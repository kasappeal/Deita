"""
Tests for workspace cleanup service.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

from app.core.config import Settings
from app.models.file import File
from app.models.user import User
from app.models.workspace import Workspace
from app.services.email_service import EmailService
from app.services.file_storage import FileStorage
from app.services.workspace_cleanup_service import WorkspaceCleanupService


class TestWorkspaceCleanupService:
    """Tests for workspace cleanup service."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.db = MagicMock()
        self.mock_settings = Mock(spec=Settings)
        self.mock_settings.orphaned_workspace_retention_days = 15
        self.mock_settings.owned_workspace_retention_days = 30
        self.mock_settings.workspace_warning_intervals = [15, 10, 5, 3, 1]
        self.mock_settings.frontend_url = "http://localhost:3000"

        self.mock_email_service = Mock(spec=EmailService)
        self.mock_file_storage = Mock(spec=FileStorage)

        self.cleanup_service = WorkspaceCleanupService(
            db=self.db,
            settings=self.mock_settings,
            email_service=self.mock_email_service,
            file_storage=self.mock_file_storage,
        )

    def test_find_orphaned_workspaces_old_enough(self):
        """Test finding orphaned workspaces that exceed retention period."""
        old_date = datetime.now(UTC) - timedelta(days=20)
        old_orphan = Mock(spec=Workspace)
        old_orphan.id = "old-orphan-id"
        old_orphan.owner_id = None
        old_orphan.last_accessed_at = old_date

        # Mock database query
        self.db.execute.return_value.scalars.return_value.all.side_effect = [
            [old_orphan],  # orphaned workspaces
            []  # owned workspaces
        ]

        workspaces = self.cleanup_service.find_workspaces_for_deletion()

        assert len(workspaces) == 1
        assert workspaces[0].id == "old-orphan-id"

    def test_find_owned_workspaces_old_enough(self):
        """Test finding owned workspaces that exceed retention period."""
        old_date = datetime.now(UTC) - timedelta(days=35)
        old_owned = Mock(spec=Workspace)
        old_owned.id = "old-owned-id"
        old_owned.owner_id = 1
        old_owned.last_accessed_at = old_date

        # Mock database query
        self.db.execute.return_value.scalars.return_value.all.side_effect = [
            [],  # orphaned workspaces
            [old_owned]  # owned workspaces
        ]

        workspaces = self.cleanup_service.find_workspaces_for_deletion()

        assert len(workspaces) == 1
        assert workspaces[0].id == "old-owned-id"

    def test_find_workspaces_needing_warning(self):
        """Test finding workspaces that need warning emails."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"

        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"
        workspace.owner_id = 1
        workspace.last_accessed_at = datetime.now(UTC) - timedelta(days=15)

        # Mock database query
        self.db.execute.return_value.all.return_value = [(workspace, user)]

        workspaces = self.cleanup_service.find_workspaces_needing_warnings(15)

        assert len(workspaces) == 1
        assert workspaces[0][0].id == "workspace-id"
        assert workspaces[0][1].id == 1

    def test_delete_workspace_with_files(self):
        """Test deleting workspace with files."""
        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"

        file1 = Mock(spec=File)
        file1.storage_path = "path/to/file1.csv"
        file1.size = 1024 * 1024  # 1 MB

        file2 = Mock(spec=File)
        file2.storage_path = "path/to/file2.csv"
        file2.size = 2 * 1024 * 1024  # 2 MB

        # Mock database query for files
        self.db.execute.return_value.scalars.return_value.all.return_value = [file1, file2]

        file_count, storage_freed_mb = self.cleanup_service.delete_workspace(workspace)

        assert file_count == 2
        assert storage_freed_mb == 3.0
        assert self.mock_file_storage.delete.call_count == 2
        self.db.delete.assert_called_once_with(workspace)
        self.db.commit.assert_called_once()

    def test_delete_workspace_file_storage_fails(self):
        """Test that workspace deletion continues even if file storage fails."""
        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"

        file = Mock(spec=File)
        file.storage_path = "path/to/file.csv"
        file.size = 1024 * 1024

        # Mock database query for files
        self.db.execute.return_value.scalars.return_value.all.return_value = [file]

        # Make file storage fail
        self.mock_file_storage.delete.side_effect = Exception("Storage error")

        # Should not raise exception
        file_count, storage_freed_mb = self.cleanup_service.delete_workspace(workspace)

        assert file_count == 1
        self.db.delete.assert_called_once_with(workspace)

    def test_send_warning_email(self):
        """Test sending warning email."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"

        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"
        workspace.name = "Test Workspace"
        workspace.owner_id = 1
        workspace.storage_used = 5 * 1024 * 1024  # 5 MB
        workspace.last_accessed_at = datetime.now(UTC) - timedelta(days=15)

        file = Mock(spec=File)
        # Mock database query for files
        self.db.execute.return_value.scalars.return_value.all.return_value = [file]

        self.cleanup_service.send_warning_email(workspace, user, 15)

        self.mock_email_service.send_workspace_deletion_warning.assert_called_once()
        call_args = self.mock_email_service.send_workspace_deletion_warning.call_args
        assert call_args[1]["to_email"] == "test@example.com"
        assert call_args[1]["workspace_name"] == "Test Workspace"
        assert call_args[1]["days_until_deletion"] == 15
        assert call_args[1]["file_count"] == 1

    def test_send_deletion_confirmation_email(self):
        """Test sending deletion confirmation email."""
        self.cleanup_service.send_deletion_confirmation_email(
            workspace_name="Test Workspace",
            workspace_id="workspace-id",
            user_email="test@example.com",
            file_count=5,
            storage_freed_mb=10.5,
        )

        self.mock_email_service.send_workspace_deleted_notification.assert_called_once()
        call_args = self.mock_email_service.send_workspace_deleted_notification.call_args
        assert call_args[1]["to_email"] == "test@example.com"
        assert call_args[1]["workspace_name"] == "Test Workspace"
        assert call_args[1]["file_count"] == 5
        assert call_args[1]["storage_used_mb"] == 10.5

    def test_run_cleanup_warnings(self):
        """Test cleanup sends warning emails."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"

        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"
        workspace.name = "Warning Workspace"
        workspace.owner_id = 1
        workspace.storage_used = 5 * 1024 * 1024
        workspace.last_accessed_at = datetime.now(UTC) - timedelta(days=15)

        # Mock find_workspaces_needing_warnings
        self.cleanup_service.find_workspaces_needing_warnings = Mock(return_value=[(workspace, user)])

        # Mock find_workspaces_for_deletion (no deletions)
        self.cleanup_service.find_workspaces_for_deletion = Mock(return_value=[])

        # Mock database query for files
        self.db.execute.return_value.scalars.return_value.all.return_value = []

        stats = self.cleanup_service.run_cleanup()

        # Verify warning was sent for each interval
        assert stats["warnings_sent"] >= 1
        assert stats["workspaces_deleted"] == 0

    def test_run_cleanup_deletion(self):
        """Test cleanup deletes workspaces."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"

        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"
        workspace.name = "Deletion Workspace"
        workspace.owner_id = 1

        # Mock find_workspaces_needing_warnings (no warnings)
        self.cleanup_service.find_workspaces_needing_warnings = Mock(return_value=[])

        # Mock find_workspaces_for_deletion
        self.cleanup_service.find_workspaces_for_deletion = Mock(return_value=[workspace])

        # Mock db.get to return user
        self.db.get.return_value = user

        # Mock database query for files
        self.db.execute.return_value.scalars.return_value.all.return_value = []

        stats = self.cleanup_service.run_cleanup()

        assert stats["warnings_sent"] == 0
        assert stats["workspaces_deleted"] == 1
        self.mock_email_service.send_workspace_deleted_notification.assert_called_once()

    def test_run_cleanup_email_failure_continues(self):
        """Test that cleanup continues even if email sending fails."""
        workspace = Mock(spec=Workspace)
        workspace.id = "workspace-id"
        workspace.name = "Test Workspace"
        workspace.owner_id = 1

        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"

        # Mock find_workspaces_needing_warnings (no warnings)
        self.cleanup_service.find_workspaces_needing_warnings = Mock(return_value=[])

        # Mock find_workspaces_for_deletion
        self.cleanup_service.find_workspaces_for_deletion = Mock(return_value=[workspace])

        # Mock db.get to return user
        self.db.get.return_value = user

        # Mock database query for files
        self.db.execute.return_value.scalars.return_value.all.return_value = []

        # Make email service fail
        self.mock_email_service.send_workspace_deleted_notification.side_effect = Exception("Email error")

        # Should not raise exception
        stats = self.cleanup_service.run_cleanup()

        assert stats["workspaces_deleted"] == 1

