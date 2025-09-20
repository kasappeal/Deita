"""
WorkspaceService: Encapsulates business logic for workspace and file operations.
"""
import csv
import io
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import magic
from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import User, Workspace
from app.models.file import File as FileModel
from app.schemas import WorkspaceCreate, WorkspaceUpdate
from app.services.exceptions import (
    FileNotFound,
    FileTooLarge,
    FileTypeNotAllowed,
    WorkspaceAlreadyClaimed,
    WorkspaceForbidden,
    WorkspaceNotFound,
    WorkspaceQuotaExceeded,
)
from app.services.file_storage import FileStorage


class WorkspaceService:

    def is_owner(self, workspace: Workspace, user: User | None) -> bool:
        """Return True if the user is the owner of the workspace."""
        return bool(user is not None and workspace.owner_id == user.id)

    def __init__(self, db: Session, file_storage: FileStorage, settings: Settings):
        self.db = db
        self.settings = settings
        self.file_storage = file_storage

    def update_last_accessed(self, workspace: Workspace):
        if hasattr(workspace, "last_accessed_at"):
            try:
                workspace.__dict__["last_accessed_at"] = datetime.now(UTC)
            except Exception:
                pass
            self.db.commit()
            self.db.refresh(workspace)

    def list_workspaces(self, user: User | None):
        if not user:
            return []
        return self.db.query(Workspace).filter(Workspace.owner_id == user.id).all()

    def get_workspace_by_id(self, workspace_id: uuid.UUID) -> Workspace:
        workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise WorkspaceNotFound("Workspace not found")
        return workspace

    def can_access(self, workspace: Workspace, user: User | None) -> bool:
        if workspace.is_public:
            return True
        if workspace.is_private:
            return user and workspace.owner_id == user.id
        return False

    def can_modify(self, workspace: Workspace, user: User | None) -> bool:
        return not workspace.is_orphaned and user and workspace.owner_id == user.id

    def create_workspace(self, data: WorkspaceCreate, user: User | None) -> Workspace:
        from app.models.workspace import Workspace
        if user is None:
            visibility = Workspace.VISIBILITY_PUBLIC
            owner_id = None
            max_file_size = self.settings.orphaned_workspace_max_file_size
            max_storage = self.settings.orphaned_workspace_max_storage
        else:
            visibility = data.visibility or Workspace.VISIBILITY_PRIVATE
            owner_id = user.id
            max_file_size = self.settings.owned_workspace_max_file_size
            max_storage = self.settings.owned_workspace_max_storage
        workspace = Workspace(
            name=data.name,
            owner_id=owner_id,
            visibility=visibility,
            max_file_size=max_file_size,
            max_storage=max_storage,
        )
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def update_workspace(self, workspace: Workspace, data: WorkspaceUpdate) -> Workspace:
        if data.name is not None:
            workspace.name = data.name # type: ignore
        if data.visibility is not None:
            workspace.visibility = data.visibility # type: ignore
        workspace.last_accessed_at = datetime.now(UTC) # type: ignore
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def delete_workspace(self, workspace: Workspace):
        self.db.delete(workspace)
        self.db.commit()

    def claim_workspace(self, workspace: Workspace, user: User):
        if not workspace.is_orphaned:
            raise WorkspaceAlreadyClaimed("Workspace already has an owner")
        workspace.owner_id = user.id # type: ignore
        workspace.last_accessed_at = datetime.now(UTC) # type: ignore
        workspace.max_file_size = self.settings.owned_workspace_max_file_size # type: ignore
        workspace.max_storage = self.settings.owned_workspace_max_storage # type: ignore
        self.db.commit()

    def get_workspace_storage(self, workspace_id: uuid.UUID) -> int:
        total = self.db.query(func.coalesce(func.sum(FileModel.size), 0)).filter(FileModel.workspace_id == workspace_id).scalar() or 0
        return total

    def list_workspace_files(self, workspace: Workspace, user: User | None) -> list[FileModel]:
        """List all files in a workspace, respecting access permissions."""
        # For public workspaces, anyone can see the files
        if workspace.is_public:
            return self.db.query(FileModel).filter(FileModel.workspace_id == workspace.id).all()

        # For private workspaces, only the owner can see files
        if workspace.is_private:
            if user and workspace.owner_id == user.id:
                return self.db.query(FileModel).filter(FileModel.workspace_id == workspace.id).all()
            else:
                # Return empty list if no auth user or user is not the owner
                return []

        # Fallback to empty list for any other case
        return []

    def upload_file(self, workspace: Workspace, file: UploadFile, user: User | None) -> FileModel:
        self._validate_file_permissions(workspace, user)
        contents = file.file.read()
        file_size = len(contents)
        self._validate_file_size(workspace, file_size)
        # Ensure workspace.id is a UUID, not a SQLAlchemy column
        self._validate_workspace_storage(workspace, file_size)
        filename = file.filename or ""
        mime_type = file.content_type or ""

        # Validate file type and extract CSV metadata
        self._validate_file_type(filename, mime_type, contents)
        csv_metadata = self._extract_csv_metadata(contents)

        storage_path = self._save_file_to_storage(contents)
        file_record = self._create_file_record(workspace, filename, storage_path, file_size, csv_metadata)

        # Increment workspace.storage_used and persist
        workspace.storage_used += file_size # type: ignore
        self.db.commit()
        self.db.refresh(workspace)
        return file_record

    def _validate_file_permissions(self, workspace: Workspace, user: User | None):
        if not self.can_access(workspace, user):
            raise WorkspaceNotFound("Workspace not found")
        if workspace.visibility == "private" and not self.can_modify(workspace, user): # type: ignore
            raise WorkspaceForbidden("Not authorized to upload to this workspace")

    def _validate_file_size(self, workspace: Workspace, file_size: int):
        if file_size > workspace.max_file_size: # type: ignore
            raise FileTooLarge(f"File exceeds max size ({workspace.max_file_size} bytes)")

    def _validate_workspace_storage(self, workspace: Workspace, file_size: int):
        if workspace.storage_used + file_size > workspace.max_storage: # type: ignore
            raise WorkspaceQuotaExceeded(f"Workspace storage limit ({workspace.max_storage} bytes) exceeded")

    def _validate_file_type(self, filename: str, mime_type: str, contents: bytes):
        ext = os.path.splitext(filename)[1].lower()
        if ext != ".csv":
            raise FileTypeNotAllowed("Only CSV files are allowed")
        if mime_type not in ["text/csv", "application/csv", "text/plain"]:
            raise FileTypeNotAllowed("Only CSV files are allowed")
        magic_type = magic.from_buffer(contents, mime=True)
        if magic_type not in ["text/csv", "application/csv", "text/plain"]:
            raise FileTypeNotAllowed("Only CSV files are allowed")

    def _extract_csv_metadata(self, contents: bytes) -> dict[str, Any]:
        """
        Extract metadata from a CSV file including delimiter, quotechar, and headers.
        Raises FileTypeNotAllowed if the file cannot be parsed as a valid CSV.
        """
        try:
            # Try to detect the CSV dialect and extract headers
            csv_text = contents.decode("utf-8")
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(csv_text[:min(10000, len(csv_text))])

            # Parse the CSV with the detected dialect
            f = io.StringIO(csv_text)
            reader = csv.reader(f, dialect)
            headers = next(reader, [])

            # Check if we have valid headers
            if not headers:
                raise FileTypeNotAllowed("CSV file has no headers")

            # Return metadata
            return {
                "delimiter": dialect.delimiter,
                "quotechar": dialect.quotechar,
                "headers": headers,
                "has_header": sniffer.has_header(csv_text[:min(10000, len(csv_text))])
            }
        except (csv.Error, UnicodeDecodeError) as e:
            raise FileTypeNotAllowed(f"Invalid CSV file: {str(e)}") from e

    def _save_file_to_storage(self, contents: bytes) -> str:
        object_name = f"{uuid.uuid4()}.csv"
        url = self.file_storage.save(object_name, contents, content_type="text/csv")
        return url

    def _get_name_without_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[0]

    def _create_file_record(self, workspace: Workspace, filename: str, storage_path: str, file_size: int, metadata: dict[str, Any] | None = None) -> FileModel:
        id_str = storage_path.split("/")[-1].split(".")[-2]
        id = uuid.UUID(id_str) if not isinstance(id_str, uuid.UUID) else id_str
        file_record = FileModel(
            id=id,
            workspace_id=workspace.id,
            table_name=self._get_name_without_extension(filename),
            filename=filename,
            storage_path=storage_path,
            size=file_size,
            csv_metadata=metadata
        )
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        return file_record

    def delete_file(self, workspace: Workspace, file_id: uuid.UUID, user: User | None) -> None:
        """Delete a file from a workspace, respecting access permissions."""
        # Get the file and verify it belongs to the workspace
        file_record = self.db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.workspace_id == workspace.id
        ).first()

        if not file_record:
            raise FileNotFound("File not found")

        # Check permissions based on workspace visibility
        if workspace.is_public:
            # For public workspaces, anyone can delete files
            pass
        elif workspace.is_private:
            # For private workspaces, only owner can delete files
            if not user or workspace.owner_id != user.id:
                raise WorkspaceForbidden("Not authorized to delete files in this workspace")
        else:
            # For any other case, deny access
            raise WorkspaceForbidden("Not authorized to delete files in this workspace")

        # Delete file from storage
        self.file_storage.delete(file_record.storage_path)

        # Update workspace storage_used
        workspace.storage_used -= file_record.size  # type: ignore

        # Delete file record from database
        self.db.delete(file_record)
        self.db.commit()
