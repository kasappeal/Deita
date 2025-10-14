"""
Workspace cleanup service for automatic deletion of inactive workspaces.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.file import File
from app.models.user import User
from app.models.workspace import Workspace
from app.services.email_service import EmailService
from app.services.file_storage import FileStorage


class WorkspaceCleanupService:
    """Service for cleaning up inactive workspaces."""

    def __init__(
        self,
        db: Session,
        settings: Settings,
        email_service: EmailService,
        file_storage: FileStorage,
    ):
        """
        Initialize WorkspaceCleanupService.

        Args:
            db: Database session
            settings: Application settings
            email_service: Email service for notifications
            file_storage: File storage service for deleting files
        """
        self.db = db
        self.settings = settings
        self.email_service = email_service
        self.file_storage = file_storage

    def find_workspaces_for_deletion(self) -> list[Workspace]:
        """
        Find workspaces that should be deleted based on retention policies.

        Returns:
            List of workspaces to delete
        """
        now = datetime.now(UTC)
        workspaces_to_delete = []

        # Find orphaned workspaces (no owner)
        orphaned_cutoff = now - timedelta(days=self.settings.orphaned_workspace_retention_days)
        orphaned_workspaces = self.db.execute(
            select(Workspace).where(
                and_(
                    Workspace.owner_id.is_(None),
                    Workspace.last_accessed_at < orphaned_cutoff
                )
            )
        ).scalars().all()
        workspaces_to_delete.extend(orphaned_workspaces)

        # Find owned workspaces (with owner)
        owned_cutoff = now - timedelta(days=self.settings.owned_workspace_retention_days)
        owned_workspaces = self.db.execute(
            select(Workspace).where(
                and_(
                    Workspace.owner_id.isnot(None),
                    Workspace.last_accessed_at < owned_cutoff
                )
            )
        ).scalars().all()
        workspaces_to_delete.extend(owned_workspaces)

        return workspaces_to_delete

    def find_workspaces_needing_warnings(self, days_before_deletion: int) -> list[tuple[Workspace, User]]:
        """
        Find owned workspaces that need warning emails.

        Args:
            days_before_deletion: Number of days before deletion to warn

        Returns:
            List of tuples (workspace, owner) that need warnings
        """
        now = datetime.now(UTC)
        warning_cutoff = now - timedelta(
            days=self.settings.owned_workspace_retention_days - days_before_deletion
        )

        # Only warn for owned workspaces
        results = self.db.execute(
            select(Workspace, User).join(
                User, Workspace.owner_id == User.id
            ).where(
                and_(
                    Workspace.owner_id.isnot(None),
                    Workspace.last_accessed_at < warning_cutoff,
                    Workspace.last_accessed_at >= warning_cutoff - timedelta(days=1)
                )
            )
        ).all()

        return [(workspace, user) for workspace, user in results]

    def delete_workspace(self, workspace: Workspace) -> tuple[int, float]:
        """
        Delete workspace and all associated files.

        Args:
            workspace: Workspace to delete

        Returns:
            Tuple of (file_count, storage_freed_mb)
        """
        # Get all files in workspace
        files = self.db.execute(
            select(File).where(File.workspace_id == workspace.id)
        ).scalars().all()

        file_count = len(files)
        storage_freed = sum(f.size for f in files)
        storage_freed_mb = storage_freed / (1024 * 1024)

        # Delete files from storage
        for file in files:
            try:
                self.file_storage.delete(file.storage_path)
            except Exception:
                # Continue deletion even if file storage fails
                pass

        # Delete workspace (cascade will delete files, queries, chat messages)
        self.db.delete(workspace)
        self.db.commit()

        return file_count, storage_freed_mb

    def send_warning_email(
        self,
        workspace: Workspace,
        user: User,
        days_until_deletion: int
    ) -> None:
        """
        Send warning email to workspace owner.

        Args:
            workspace: Workspace that will be deleted
            user: Owner of the workspace
            days_until_deletion: Days until deletion
        """
        deletion_date = workspace.last_accessed_at + timedelta(
            days=self.settings.owned_workspace_retention_days
        )

        # Get file count and storage
        files = self.db.execute(
            select(File).where(File.workspace_id == workspace.id)
        ).scalars().all()

        file_count = len(files)
        storage_used_mb = workspace.storage_used / (1024 * 1024)

        # Build workspace URL
        workspace_url = f"{self.settings.frontend_url}/workspaces/{workspace.id}"

        self.email_service.send_workspace_deletion_warning(
            to_email=user.email,
            workspace_name=workspace.name,
            workspace_id=str(workspace.id),
            days_until_deletion=days_until_deletion,
            deletion_date=deletion_date.strftime("%B %d, %Y at %H:%M UTC"),
            file_count=file_count,
            storage_used_mb=storage_used_mb,
            workspace_url=workspace_url,
        )

    def send_deletion_confirmation_email(
        self,
        workspace_name: str,
        workspace_id: str,
        user_email: str,
        file_count: int,
        storage_freed_mb: float
    ) -> None:
        """
        Send deletion confirmation email to workspace owner.

        Args:
            workspace_name: Name of deleted workspace
            workspace_id: ID of deleted workspace
            user_email: Owner's email
            file_count: Number of files deleted
            storage_freed_mb: Storage freed in MB
        """
        self.email_service.send_workspace_deleted_notification(
            to_email=user_email,
            workspace_name=workspace_name,
            workspace_id=workspace_id,
            file_count=file_count,
            storage_used_mb=storage_freed_mb,
        )

    def run_cleanup(self) -> dict[str, int]:
        """
        Run complete cleanup process: send warnings and delete workspaces.

        Returns:
            Dictionary with statistics (warnings_sent, workspaces_deleted)
        """
        warnings_sent = 0
        workspaces_deleted = 0

        # Send warning emails for owned workspaces
        for days_before in self.settings.workspace_warning_intervals:
            workspaces_to_warn = self.find_workspaces_needing_warnings(days_before)
            for workspace, user in workspaces_to_warn:
                try:
                    self.send_warning_email(workspace, user, days_before)
                    warnings_sent += 1
                except Exception:
                    # Continue even if email fails
                    pass

        # Delete workspaces
        workspaces_to_delete = self.find_workspaces_for_deletion()
        for workspace in workspaces_to_delete:
            # Store owner info before deletion (if owned)
            owner_email = None
            workspace_name = workspace.name
            workspace_id = str(workspace.id)

            if workspace.owner_id:
                user = self.db.get(User, workspace.owner_id)
                if user:
                    owner_email = user.email

            # Delete workspace and files
            try:
                file_count, storage_freed_mb = self.delete_workspace(workspace)
                workspaces_deleted += 1

                # Send confirmation email if owned workspace
                if owner_email:
                    try:
                        self.send_deletion_confirmation_email(
                            workspace_name=workspace_name,
                            workspace_id=workspace_id,
                            user_email=owner_email,
                            file_count=file_count,
                            storage_freed_mb=storage_freed_mb,
                        )
                    except Exception:
                        # Continue even if email fails
                        pass
            except Exception:
                # Continue with next workspace if deletion fails
                self.db.rollback()

        return {
            "warnings_sent": warnings_sent,
            "workspaces_deleted": workspaces_deleted,
        }
