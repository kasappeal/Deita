"""
Workspace management API routes.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.utils import (
    can_access_workspace,
    can_modify_workspace,
    get_workspace_or_404,
    update_last_accessed,
)
from app.core.auth import get_current_user, get_current_user_optional
from app.core.database import get_db
from app.models import User, Workspace
from app.schemas import Workspace as WorkspaceSchema
from app.schemas import WorkspaceCreate, WorkspaceUpdate

router = APIRouter()


@router.post("/", response_model=WorkspaceSchema, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    """Create a new workspace."""

    # Determine visibility based on authentication
    if current_user is None:
        # No authentication provided - create public workspace without owner
        visibility = "public"
        owner_id = None
    else:
        # Authentication provided - set default visibility to private unless specified
        visibility = workspace_data.visibility or "private"
        owner_id = current_user.id

    workspace = Workspace(
        name=workspace_data.name,
        owner_id=owner_id,
        visibility=visibility
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return workspace


@router.get("/", response_model=list[WorkspaceSchema])
async def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    """List workspaces that belong to the authenticated user."""

    if not current_user:
        # Return empty list for unauthenticated users
        return []

    workspaces = db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceSchema)
async def get_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    """Get workspace details by ID."""

    workspace = get_workspace_or_404(db, workspace_id)

    if not can_access_workspace(workspace, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Update last accessed timestamp
    update_last_accessed(db, workspace)

    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceSchema)
async def update_workspace(
    workspace_id: uuid.UUID,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    """Update workspace by ID."""

    workspace = get_workspace_or_404(db, workspace_id)

    # Check if workspace is orphan
    if workspace.owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify orphan workspace"
        )

    if not can_modify_workspace(workspace, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this workspace"
        )

    # Update fields if provided
    if workspace_data.name is not None:
        workspace.name = workspace_data.name

    if workspace_data.visibility is not None:
        workspace.visibility = workspace_data.visibility

    # Update last accessed timestamp
    workspace.last_accessed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(workspace)

    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    """Delete workspace by ID."""

    workspace = get_workspace_or_404(db, workspace_id)

    # Check if workspace is orphan
    if workspace.owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete orphan workspace"
        )

    if not can_modify_workspace(workspace, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this workspace"
        )

    # TODO: Implement background tasks for file deletion
    # For now, just delete the workspace record
    db.delete(workspace)
    db.commit()

    return None


@router.post("/{workspace_id}/claim", status_code=status.HTTP_204_NO_CONTENT)
async def claim_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Claim an orphan workspace."""

    workspace = get_workspace_or_404(db, workspace_id)

    # Only orphan workspaces can be claimed
    if workspace.owner_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workspace already has an owner"
        )

    # Assign current user as owner but preserve visibility
    workspace.owner_id = current_user.id
    workspace.last_accessed_at = datetime.now(timezone.utc)

    db.commit()

    return None
