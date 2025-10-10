"""
Utility functions for workspace API operations.
"""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, Workspace
from app.schemas import Workspace as WorkspaceSchema


def get_workspace_or_404(db: Session, workspace_id: uuid.UUID) -> Workspace:
    """Get workspace by ID or raise 404."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    return workspace


def can_access_workspace(workspace: Workspace, current_user: User | None) -> bool:
    """Check if user can access workspace based on visibility and ownership."""
    # Public workspaces can be accessed by anyone
    if workspace.visibility == "public":
        return True

    # Private workspaces can only be accessed by the owner
    if workspace.visibility == "private":
        if not current_user:
            return False
        return workspace.owner_id == current_user.id

    return False


def can_modify_workspace(workspace: Workspace, current_user: User | None) -> bool:
    """Check if user can modify workspace."""
    # Orphan workspaces cannot be modified
    if workspace.owner_id is None:
        return False

    # Only the owner can modify the workspace
    if not current_user:
        return False

    return workspace.owner_id == current_user.id


def update_last_accessed(db: Session, workspace: Workspace):
    """Update workspace last_accessed_at timestamp."""
    workspace.last_accessed_at = datetime.now(UTC)
    db.commit()


def build_workspace_schema(ws, user):
    owner_id = getattr(ws, "owner_id", None)
    user_id = getattr(user, "id", None) if user else None
    is_orphan = owner_id is None
    is_yours = (owner_id is not None and user_id is not None and owner_id == user_id)
    ws_dict = ws.__dict__.copy() if hasattr(ws, "__dict__") else dict(ws)
    ws_dict["is_orphan"] = is_orphan
    ws_dict["is_yours"] = is_yours
    return WorkspaceSchema(**ws_dict)  # noqa: F821
