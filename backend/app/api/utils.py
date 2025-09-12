"""
Utility functions for workspace API operations.
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, Workspace


def get_workspace_or_404(db: Session, workspace_id: uuid.UUID) -> Workspace:
    """Get workspace by ID or raise 404."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    return workspace


def can_access_workspace(workspace: Workspace, current_user: Optional[User]) -> bool:
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


def can_modify_workspace(workspace: Workspace, current_user: Optional[User]) -> bool:
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
    workspace.last_accessed_at = datetime.utcnow()
    db.commit()