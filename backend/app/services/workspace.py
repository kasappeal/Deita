"""
Core workspace service for business logic and operations.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import secrets
import string

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models import Workspace, WorkspaceUsage, WorkspaceAuditLog
from app.schemas.workspace import (
    CreateWorkspaceRequest,
    CreateOrphanWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceFilters,
    WorkspaceResponse,
    WorkspaceListResponse,
)


class WorkspaceService:
    """Service for workspace operations and business logic."""

    def __init__(self, db: Session):
        self.db = db

    async def create_workspace(
        self,
        user_id: UUID,
        data: CreateWorkspaceRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Workspace:
        """Create a new owned workspace for a registered user."""
        # Set storage quota based on user type (200MB for registered users)
        storage_quota = 209715200  # 200MB
        
        # Create workspace
        workspace = Workspace(
            name=data.name,
            description=data.description,
            owner_id=user_id,
            is_public=data.is_public,
            is_orphan=False,
            storage_quota_bytes=storage_quota,
            settings={},
        )
        
        try:
            self.db.add(workspace)
            self.db.flush()  # Get the workspace ID
            
            # Create usage record
            usage = WorkspaceUsage(workspace_id=workspace.id)
            self.db.add(usage)
            
            # Create audit log entry
            await self._log_action(
                workspace_id=workspace.id,
                user_id=user_id,
                action="create",
                resource_type="workspace",
                resource_id=str(workspace.id),
                details={"name": data.name, "is_public": data.is_public},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            self.db.commit()
            self.db.refresh(workspace)
            return workspace
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Workspace creation failed due to constraint violation")

    async def create_orphan_workspace(
        self,
        data: CreateOrphanWorkspaceRequest,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Workspace:
        """Create a new orphan workspace for anonymous users."""
        # Set expiration to 30 days from now for orphan workspaces
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Create workspace
        workspace = Workspace(
            name=data.name,
            description=data.description,
            owner_id=None,
            is_public=True,
            is_orphan=True,
            storage_quota_bytes=52428800,  # 50MB for orphan workspaces
            settings={"session_id": session_id},
            expires_at=expires_at,
        )
        
        try:
            self.db.add(workspace)
            self.db.flush()
            
            # Create usage record
            usage = WorkspaceUsage(workspace_id=workspace.id)
            self.db.add(usage)
            
            # Create audit log entry
            await self._log_action(
                workspace_id=workspace.id,
                user_id=None,
                action="create_orphan",
                resource_type="workspace",
                resource_id=str(workspace.id),
                details={"name": data.name, "session_id": session_id},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            self.db.commit()
            self.db.refresh(workspace)
            return workspace
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Orphan workspace creation failed")

    async def claim_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Workspace:
        """Claim an orphan workspace for a registered user."""
        workspace = self.db.query(Workspace).filter(
            and_(
                Workspace.id == workspace_id,
                Workspace.is_orphan == True,
                Workspace.settings["session_id"].as_string() == session_id,
            )
        ).first()
        
        if not workspace:
            raise ValueError("Workspace not found or cannot be claimed")
        
        # Update workspace to be owned
        workspace.owner_id = user_id
        workspace.is_orphan = False
        workspace.expires_at = None  # Remove expiration
        workspace.storage_quota_bytes = 209715200  # Upgrade to 200MB
        
        # Update settings to remove session_id
        settings = workspace.settings.copy()
        settings.pop("session_id", None)
        workspace.settings = settings
        
        # Create audit log entry
        await self._log_action(
            workspace_id=workspace_id,
            user_id=user_id,
            action="claim",
            resource_type="workspace",
            resource_id=str(workspace_id),
            details={"session_id": session_id},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    async def get_workspace(self, workspace_id: UUID, user_id: Optional[UUID] = None) -> Optional[Workspace]:
        """Get workspace by ID with access control."""
        query = self.db.query(Workspace).options(
            joinedload(Workspace.usage),
            joinedload(Workspace.audit_logs)
        )
        
        if user_id:
            # Authenticated user can see their own workspaces or public ones
            query = query.filter(
                and_(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == user_id,
                        Workspace.is_public == True
                    )
                )
            )
        else:
            # Anonymous users can only see public workspaces
            query = query.filter(
                and_(
                    Workspace.id == workspace_id,
                    Workspace.is_public == True
                )
            )
        
        return query.first()

    async def list_workspaces(
        self,
        user_id: Optional[UUID] = None,
        filters: Optional[WorkspaceFilters] = None,
        page: int = 1,
        size: int = 20,
    ) -> WorkspaceListResponse:
        """List workspaces with pagination and filtering."""
        query = self.db.query(Workspace).options(joinedload(Workspace.usage))
        
        # Apply user-based filtering
        if user_id:
            # Authenticated user can see their own workspaces or public ones
            query = query.filter(
                or_(
                    Workspace.owner_id == user_id,
                    Workspace.is_public == True
                )
            )
        else:
            # Anonymous users can only see public workspaces
            query = query.filter(Workspace.is_public == True)
        
        # Apply filters
        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Workspace.name.ilike(search_term),
                        Workspace.description.ilike(search_term),
                    )
                )
            
            if filters.is_public is not None:
                query = query.filter(Workspace.is_public == filters.is_public)
            
            if filters.is_orphan is not None:
                query = query.filter(Workspace.is_orphan == filters.is_orphan)
            
            if filters.owner_id is not None:
                query = query.filter(Workspace.owner_id == filters.owner_id)
            
            if filters.created_after:
                query = query.filter(Workspace.created_at >= filters.created_after)
            
            if filters.created_before:
                query = query.filter(Workspace.created_at <= filters.created_before)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * size
        workspaces = query.order_by(desc(Workspace.updated_at)).offset(offset).limit(size).all()
        
        return WorkspaceListResponse(
            workspaces=[WorkspaceResponse.model_validate(w) for w in workspaces],
            total=total,
            page=page,
            size=size,
            has_more=offset + size < total,
        )

    async def update_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        data: UpdateWorkspaceRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Workspace:
        """Update workspace metadata."""
        workspace = self.db.query(Workspace).filter(
            and_(
                Workspace.id == workspace_id,
                Workspace.owner_id == user_id
            )
        ).first()
        
        if not workspace:
            raise ValueError("Workspace not found or access denied")
        
        # Update fields
        update_details = {}
        if data.name is not None:
            workspace.name = data.name
            update_details["name"] = data.name
        
        if data.description is not None:
            workspace.description = data.description
            update_details["description"] = data.description
        
        # Create audit log entry
        await self._log_action(
            workspace_id=workspace_id,
            user_id=user_id,
            action="update",
            resource_type="workspace",
            resource_id=str(workspace_id),
            details=update_details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    async def delete_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Delete workspace and all associated data."""
        workspace = self.db.query(Workspace).filter(
            and_(
                Workspace.id == workspace_id,
                Workspace.owner_id == user_id
            )
        ).first()
        
        if not workspace:
            raise ValueError("Workspace not found or access denied")
        
        # Create audit log entry before deletion
        await self._log_action(
            workspace_id=workspace_id,
            user_id=user_id,
            action="delete",
            resource_type="workspace",
            resource_id=str(workspace_id),
            details={"name": workspace.name},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        # Delete workspace (cascades to related records)
        self.db.delete(workspace)
        self.db.commit()
        return True

    async def validate_workspace_name(self, name: str, user_id: Optional[UUID] = None) -> tuple[bool, str]:
        """Validate if workspace name is available for the user."""
        # Check if name is already used by the same user
        if user_id:
            existing = self.db.query(Workspace).filter(
                and_(
                    Workspace.name == name,
                    Workspace.owner_id == user_id
                )
            ).first()
        else:
            # For anonymous users, check within recent orphan workspaces
            cutoff_date = datetime.utcnow() - timedelta(hours=24)
            existing = self.db.query(Workspace).filter(
                and_(
                    Workspace.name == name,
                    Workspace.is_orphan == True,
                    Workspace.created_at > cutoff_date
                )
            ).first()
        
        if existing:
            return False, "Workspace name is already in use"
        
        return True, "Workspace name is available"

    async def _log_action(
        self,
        workspace_id: UUID,
        user_id: Optional[UUID],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Create an audit log entry."""
        log_entry = WorkspaceAuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log_entry)


class WorkspaceCleanupService:
    """Service for workspace cleanup and lifecycle management."""

    def __init__(self, db: Session):
        self.db = db

    async def cleanup_expired_workspaces(self) -> int:
        """Clean up expired orphan workspaces."""
        cutoff_date = datetime.utcnow()
        
        expired_workspaces = self.db.query(Workspace).filter(
            and_(
                Workspace.is_orphan == True,
                Workspace.expires_at <= cutoff_date
            )
        ).all()
        
        count = 0
        for workspace in expired_workspaces:
            # Log deletion
            log_entry = WorkspaceAuditLog(
                workspace_id=workspace.id,
                user_id=None,
                action="auto_delete",
                resource_type="workspace",
                resource_id=str(workspace.id),
                details={"reason": "expired", "expires_at": workspace.expires_at.isoformat()},
            )
            self.db.add(log_entry)
            
            # Delete workspace
            self.db.delete(workspace)
            count += 1
        
        self.db.commit()
        return count

    async def cleanup_inactive_owned_workspaces(self, days_inactive: int = 60) -> int:
        """Clean up inactive owned workspaces after specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        # Find workspaces that haven't been accessed
        inactive_workspaces = self.db.query(Workspace).join(WorkspaceUsage).filter(
            and_(
                Workspace.is_orphan == False,
                WorkspaceUsage.last_accessed_at <= cutoff_date
            )
        ).all()
        
        count = 0
        for workspace in inactive_workspaces:
            # Log deletion
            log_entry = WorkspaceAuditLog(
                workspace_id=workspace.id,
                user_id=workspace.owner_id,
                action="auto_delete",
                resource_type="workspace",
                resource_id=str(workspace.id),
                details={"reason": "inactive", "last_accessed": workspace.usage.last_accessed_at.isoformat()},
            )
            self.db.add(log_entry)
            
            # Delete workspace
            self.db.delete(workspace)
            count += 1
        
        self.db.commit()
        return count

    async def send_expiration_warnings(self) -> int:
        """Send warnings for workspaces expiring soon."""
        # Warn 7 days before expiration
        warning_date = datetime.utcnow() + timedelta(days=7)
        
        expiring_workspaces = self.db.query(Workspace).filter(
            and_(
                Workspace.is_orphan == True,
                Workspace.expires_at <= warning_date,
                Workspace.expires_at > datetime.utcnow()
            )
        ).all()
        
        # In a real implementation, you would send emails here
        # For now, just log the warning
        count = 0
        for workspace in expiring_workspaces:
            log_entry = WorkspaceAuditLog(
                workspace_id=workspace.id,
                user_id=None,
                action="expiration_warning",
                resource_type="workspace",
                resource_id=str(workspace.id),
                details={"expires_at": workspace.expires_at.isoformat()},
            )
            self.db.add(log_entry)
            count += 1
        
        self.db.commit()
        return count