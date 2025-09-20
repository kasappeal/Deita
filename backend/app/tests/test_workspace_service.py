import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from app.core.config import Settings
from app.models import User, Workspace
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
from app.services.workspace_service import WorkspaceService


class TestWorkspaceService:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.db = MagicMock()
        self.file_storage = MagicMock(spec=FileStorage)
        self.settings = MagicMock(spec=Settings)
        self.settings.owned_workspace_max_file_size = 1000
        self.settings.owned_workspace_max_storage = 10000
        self.settings.orphaned_workspace_max_file_size = 500
        self.settings.orphaned_workspace_max_storage = 5000
        self.service = WorkspaceService(self.db, self.file_storage, self.settings)
        self.user = MagicMock(spec=User)
        self.user.id = 1
        self.workspace = MagicMock(spec=Workspace)
        self.workspace.id = uuid.uuid4()
        self.workspace.owner_id = self.user.id
        self.workspace.is_public = False
        self.workspace.is_private = True
        self.workspace.is_orphaned = False
        self.workspace.max_file_size = 1000
        self.workspace.max_storage = 10000
        self.workspace.storage_used = 0
        self.workspace.visibility = "private"

    def test_create_workspace_owned(self):
        data = WorkspaceCreate(name="Test", visibility="private")
        ws = self.service.create_workspace(data, self.user)
        self.db.add.assert_called()
        self.db.commit.assert_called()
        self.db.refresh.assert_called()
        assert ws is not None

    def test_create_workspace_orphaned(self):
        data = WorkspaceCreate(name="Test", visibility="public")
        ws = self.service.create_workspace(data, None)
        self.db.add.assert_called()
        self.db.commit.assert_called()
        self.db.refresh.assert_called()
        assert ws is not None

    def test_update_workspace(self):
        data = WorkspaceUpdate(name="NewName", visibility="public")
        ws = self.service.update_workspace(self.workspace, data)
        self.db.commit.assert_called()
        self.db.refresh.assert_called()
        assert ws is not None

    def test_delete_workspace(self):
        self.service.delete_workspace(self.workspace)
        self.db.delete.assert_called_with(self.workspace)
        self.db.commit.assert_called()

    def test_claim_workspace(self):
        self.workspace.is_orphaned = True
        self.service.claim_workspace(self.workspace, self.user)
        self.db.commit.assert_called()

    def test_claim_workspace_already_claimed(self):
        self.workspace.is_orphaned = False
        with pytest.raises(WorkspaceAlreadyClaimed):
            self.service.claim_workspace(self.workspace, self.user)

    def test_upload_file_valid(self):
        self.workspace.storage_used = 0
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"col1,col2\n1,2"
        # Generate a valid UUID and use it in the storage path
        valid_uuid = str(uuid.uuid4())
        self.file_storage.save.return_value = f"{valid_uuid}.csv"
        with patch("app.services.workspace_service.magic.from_buffer", return_value="text/csv"):
            with patch("app.services.workspace_service.uuid.uuid4", return_value=uuid.UUID(valid_uuid)):
                with patch("app.services.workspace_service.FileModel", autospec=True) as FileModelMock:
                    file_record = MagicMock()
                    FileModelMock.return_value = file_record
                    result = self.service.upload_file(self.workspace, file, self.user)
                    assert result == file_record
                    self.db.add.assert_called()
                    self.db.commit.assert_called()
                    self.db.refresh.assert_called()

    def test_upload_file_too_large(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"x" * 2000
        with pytest.raises(FileTooLarge):
            self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_storage_exceeded(self):
        self.workspace.storage_used = 10000
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"x" * 10
        with pytest.raises(WorkspaceQuotaExceeded):
            self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_type_not_allowed(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.txt"
        file.content_type = "text/plain"
        file.file = MagicMock()
        file.file.read.return_value = b"abc"
        with pytest.raises(FileTypeNotAllowed):
            self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_magic_type_not_allowed(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"abc"
        with patch("app.services.workspace_service.magic.from_buffer", return_value="application/pdf"):
            with pytest.raises(FileTypeNotAllowed):
                self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_permission_denied(self):
        self.workspace.is_private = True
        self.workspace.owner_id = 2  # not the user
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"abc"
        with pytest.raises(WorkspaceNotFound):
            self.service.upload_file(self.workspace, file, self.user)

    def test_delete_file_success_public_workspace(self):
        """Test successful file deletion in a public workspace by any user"""
        from app.models.file import File as FileModel

        # Set up public workspace
        self.workspace.is_public = True
        self.workspace.is_private = False
        self.workspace.storage_used = 1000

        # Create mock file
        file_id = uuid.uuid4()
        file_record = MagicMock(spec=FileModel)
        file_record.id = file_id
        file_record.size = 100
        file_record.storage_path = f"{file_id}.csv"

        # Mock DB query to return the file
        self.db.query.return_value.filter.return_value.first.return_value = file_record

        # Call delete_file
        self.service.delete_file(self.workspace, file_id, None)  # No user (anonymous)

        # Verify file storage deletion was called
        self.file_storage.delete.assert_called_once_with(f"{file_id}.csv")

        # Verify workspace storage was decremented
        assert self.workspace.storage_used == 900

        # Verify file record was deleted from DB
        self.db.delete.assert_called_once_with(file_record)
        self.db.commit.assert_called()

    def test_delete_file_success_private_workspace_owner(self):
        """Test successful file deletion in a private workspace by the owner"""
        from app.models.file import File as FileModel

        # Set up private workspace
        self.workspace.is_public = False
        self.workspace.is_private = True
        self.workspace.owner_id = self.user.id
        self.workspace.storage_used = 500

        # Create mock file
        file_id = uuid.uuid4()
        file_record = MagicMock(spec=FileModel)
        file_record.id = file_id
        file_record.size = 200
        file_record.storage_path = f"{file_id}.csv"

        # Mock DB query to return the file
        self.db.query.return_value.filter.return_value.first.return_value = file_record

        # Call delete_file as owner
        self.service.delete_file(self.workspace, file_id, self.user)

        # Verify file storage deletion was called
        self.file_storage.delete.assert_called_once_with(f"{file_id}.csv")

        # Verify workspace storage was decremented
        assert self.workspace.storage_used == 300

        # Verify file record was deleted from DB
        self.db.delete.assert_called_once_with(file_record)
        self.db.commit.assert_called()

    def test_delete_file_not_found(self):
        """Test file deletion when file doesn't exist"""
        file_id = uuid.uuid4()

        # Mock DB query to return None (file not found)
        self.db.query.return_value.filter.return_value.first.return_value = None

        # Call delete_file and expect FileNotFound exception
        with pytest.raises(FileNotFound, match="File not found"):
            self.service.delete_file(self.workspace, file_id, self.user)

    def test_delete_file_private_workspace_forbidden_no_user(self):
        """Test file deletion forbidden in private workspace when no user"""
        from app.models.file import File as FileModel

        # Set up private workspace
        self.workspace.is_public = False
        self.workspace.is_private = True

        # Create mock file
        file_id = uuid.uuid4()
        file_record = MagicMock(spec=FileModel)
        file_record.id = file_id

        # Mock DB query to return the file
        self.db.query.return_value.filter.return_value.first.return_value = file_record

        # Call delete_file without user and expect forbidden
        with pytest.raises(WorkspaceForbidden, match="Not authorized to delete files in this workspace"):
            self.service.delete_file(self.workspace, file_id, None)

    def test_delete_file_private_workspace_forbidden_wrong_user(self):
        """Test file deletion forbidden in private workspace when user is not owner"""
        from app.models.file import File as FileModel

        # Set up private workspace with different owner
        self.workspace.is_public = False
        self.workspace.is_private = True
        self.workspace.owner_id = 999  # Different from self.user.id (which is 1)

        # Create mock file
        file_id = uuid.uuid4()
        file_record = MagicMock(spec=FileModel)
        file_record.id = file_id

        # Mock DB query to return the file
        self.db.query.return_value.filter.return_value.first.return_value = file_record

        # Call delete_file with wrong user and expect forbidden
        with pytest.raises(WorkspaceForbidden, match="Not authorized to delete files in this workspace"):
            self.service.delete_file(self.workspace, file_id, self.user)

