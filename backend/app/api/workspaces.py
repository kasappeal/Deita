"""
Workspace management API routes.
"""
import uuid

from fastapi import APIRouter, Depends, UploadFile, status
from minio import Minio
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_current_user_optional
from app.core.config import get_settings
from app.core.database import get_db
from app.models import User
from app.schemas import Workspace as WorkspaceSchema
from app.schemas import WorkspaceCreate, WorkspaceUpdate
from app.schemas.file import File as FileSchema
from app.services.file_storage import FileStorage
from app.services.workspace_service import WorkspaceService


def get_workspace_service(db: Session = Depends(get_db)) -> WorkspaceService:
    settings = get_settings()
    minio_client = Minio(
        settings.s3_endpoint.replace('http://', '').replace('https://', ''),
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=settings.s3_endpoint.startswith('https://'),
    )
    file_storage = FileStorage(settings=settings, client=minio_client)
    return WorkspaceService(db, file_storage=file_storage, settings=settings)


router = APIRouter()


@router.post("/{workspace_id}/files/", response_model=FileSchema, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def upload_file(
    workspace_id: uuid.UUID,
    file: UploadFile,
    current_user: User | None = Depends(get_current_user_optional),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Upload a CSV file to a workspace with security and validation."""
    workspace = service.get_workspace_by_id(workspace_id)
    file_record = service.upload_file(workspace, file, current_user)
    return FileSchema.model_validate(file_record)


@router.post("/", response_model=WorkspaceSchema, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User | None = Depends(get_current_user_optional),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Create a new workspace."""
    workspace = service.create_workspace(workspace_data, current_user)
    return workspace


@router.get("/", response_model=list[WorkspaceSchema])
async def list_workspaces(
    current_user: User | None = Depends(get_current_user_optional),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """List workspaces that belong to the authenticated user."""
    return service.list_workspaces(current_user)


@router.get("/{workspace_id}", response_model=WorkspaceSchema)
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: User | None = Depends(get_current_user_optional),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Get workspace details by ID."""
    workspace = service.get_workspace_by_id(workspace_id)
    if not service.can_access(workspace, current_user):
        from app.services.exceptions import WorkspaceNotFound
        raise WorkspaceNotFound("Workspace not found")
    # Optionally update last accessed timestamp
    service.update_last_accessed(workspace)
    return workspace



@router.put("/{workspace_id}", response_model=WorkspaceSchema)
async def update_workspace(
    workspace_id: uuid.UUID,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Update workspace by ID."""
    workspace = service.get_workspace_by_id(workspace_id)
    if not service.is_owner(workspace, current_user):
        from app.services.exceptions import WorkspaceForbidden
        raise WorkspaceForbidden("Not authorized to update this workspace")
    updated = service.update_workspace(workspace, workspace_data)
    return updated



@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Delete workspace by ID."""
    workspace = service.get_workspace_by_id(workspace_id)
    if not service.is_owner(workspace, current_user):
        from app.services.exceptions import WorkspaceForbidden
        raise WorkspaceForbidden("Not authorized to delete this workspace")
    service.delete_workspace(workspace)
    return None


@router.post("/{workspace_id}/claim", status_code=status.HTTP_204_NO_CONTENT)
async def claim_workspace(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Claim an orphan workspace."""
    workspace = service.get_workspace_by_id(workspace_id)
    service.claim_workspace(workspace, current_user)
    return None
