"""
Workspace management API routes.
"""
import uuid

import boto3
from botocore.client import Config
from fastapi import APIRouter, Body, Depends, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_current_user_optional
from app.core.config import get_settings
from app.core.database import get_db
from app.models import User
from app.schemas import QueryRequest, WorkspaceCreate, WorkspaceUpdate
from app.schemas import Workspace as WorkspaceSchema
from app.schemas.file import File as FileSchema
from app.schemas.query import QueryResult
from app.services.exceptions import BadQuery, WorkspaceNotFound
from app.services.file_storage import FileStorage
from app.services.query_service import QueryService
from app.services.workspace_service import WorkspaceService


def get_workspace_service(db: Session = Depends(get_db)) -> WorkspaceService:
    settings = get_settings()
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(signature_version='s3v4'),
        verify=settings.s3_endpoint.startswith('https://')
    )
    file_storage = FileStorage(settings=settings, client=s3_client)
    return WorkspaceService(db, file_storage=file_storage, settings=settings)


def get_query_service() -> QueryService:
    settings = get_settings()
    return QueryService(settings)


router = APIRouter()


@router.post("/{workspace_id}/query", status_code=status.HTTP_200_OK)
async def execute_query(
    workspace_id: uuid.UUID,
    query_request: QueryRequest,
    page: int = 1,
    count: bool = False,
    current_user: User | None = Depends(get_current_user_optional),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    query_service: QueryService = Depends(get_query_service),
):
    """
    Execute SQL query against a workspace's data.

    The query must be a SELECT or WITH statement, and a limit of 50 rows will be enforced.
    """
    try:
        # Try to get the workspace
        workspace = workspace_service.get_workspace_by_id(workspace_id)

        # Check access rights
        if not workspace.is_public and (not current_user or not workspace_service.is_owner(workspace, current_user)):
            # Return null query for private workspaces when user is not the owner
            return QueryResult(columns=[], rows=[], time=0.0)

        # Get all files in the workspace
        files = workspace_service.list_workspace_files(workspace, current_user)

        # Validate the query
        result = query_service.execute_query(query_request.query, files, page, count) # type: ignore

        # Return the sanitized query
        return result
    except WorkspaceNotFound:
        # If workspace doesn't exist, return null query
        return QueryResult(columns=[], rows=[], time=0.0)
    except BadQuery:
        return QueryResult(columns=[], rows=[], time=0.0)
    except Exception as e:
        # Log the error and return null query for other errors
        print(f"Error executing query: {str(e)}")
        return QueryResult(columns=[], rows=[], time=0.0)


@router.post("/{workspace_id}/files", status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def upload_file(
    workspace_id: uuid.UUID,
    file: UploadFile,
    overwrite: bool = Body(default=False),
    current_user: User | None = Depends(get_current_user_optional),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Upload a CSV file to a workspace with security and validation. Duplicate/overwrite logic is handled in the service."""
    workspace = service.get_workspace_by_id(workspace_id)
    file_record = service.upload_file(workspace, file, current_user, overwrite=overwrite)
    updated_workspace = service.get_workspace_by_id(workspace_id)
    return {
        "file": FileSchema.model_validate(file_record),
        "workspace": WorkspaceSchema.model_validate(updated_workspace)
    }


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



@router.get("/{workspace_id}/files", response_model=list[FileSchema])
async def list_workspace_files(
    workspace_id: uuid.UUID,
    current_user: User | None = Depends(get_current_user_optional),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """List all files in a workspace."""
    workspace = service.get_workspace_by_id(workspace_id)
    files = service.list_workspace_files(workspace, current_user)
    return files


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
