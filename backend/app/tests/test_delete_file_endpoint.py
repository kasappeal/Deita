"""
Tests for DELETE /v1/workspaces/{workspace_id}/files/{file_id} endpoint.
"""

import uuid
from unittest.mock import MagicMock, patch

from app.models.file import File as FileModel
from app.models.workspace import Workspace
from app.tests import APITest


class TestDeleteFileEndpoint(APITest):
    """Tests for DELETE /v1/workspaces/{workspace_id}/files/{file_id} endpoint."""

    def test_delete_file_success_public_workspace_no_auth(self):
        """Test successful file deletion in public workspace without authentication."""
        with patch('app.api.workspaces.FileStorage') as mock_file_storage_class:
            # Setup mock file storage
            mock_file_storage = MagicMock()
            mock_file_storage_class.return_value = mock_file_storage

            # Create public workspace
            workspace = self._create_workspace_via_api(None, "Public Test", "public")
            workspace_id = workspace["id"]

            # Upload a file to get a real file ID
            file_info = self._create_file_via_api(workspace_id, "test.csv", None)
            file_id = file_info["id"]

            # Get initial workspace and file state from database
            workspace_record = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            file_record = self.db.query(FileModel).filter(FileModel.id == file_id).first()
            initial_storage_used = workspace_record.storage_used
            file_size = file_record.size
            storage_path = file_record.storage_path

            # Delete the file
            response = self.client.delete(f"/v1/workspaces/{workspace_id}/files/{file_id}")

            # Verify response
            assert response.status_code == 204
            assert response.content == b""

            # Verify file is deleted from database
            deleted_file = self.db.query(FileModel).filter(FileModel.id == file_id).first()
            assert deleted_file is None

            # Verify workspace storage_used is decremented
            updated_workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            assert updated_workspace.storage_used == initial_storage_used - file_size

            # Verify file storage delete was called
            mock_file_storage.delete.assert_called_once_with(storage_path)

    def test_delete_file_success_private_workspace_owner(self):
        """Test successful file deletion in private workspace by owner."""
        with patch('app.api.workspaces.FileStorage') as mock_file_storage_class:
            # Setup mock file storage
            mock_file_storage = MagicMock()
            mock_file_storage_class.return_value = mock_file_storage

            # Create user and private workspace
            user = self._create_user('owner@example.com')
            headers = self._get_auth_headers(user)
            workspace = self._create_workspace_via_api(user, "Private Test", "private")
            workspace_id = workspace["id"]

            # Upload a file as owner
            file_info = self._create_file_via_api(workspace_id, "test.csv", user)
            file_id = file_info["id"]

            # Get initial workspace and file state from database
            workspace_record = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            file_record = self.db.query(FileModel).filter(FileModel.id == file_id).first()
            initial_storage_used = workspace_record.storage_used
            file_size = file_record.size
            storage_path = file_record.storage_path

            # Delete the file as owner
            response = self.client.delete(
                f"/v1/workspaces/{workspace_id}/files/{file_id}",
                headers=headers
            )

            # Verify response
            assert response.status_code == 204
            assert response.content == b""

            # Verify file is deleted from database
            deleted_file = self.db.query(FileModel).filter(FileModel.id == file_id).first()
            assert deleted_file is None

            # Verify workspace storage_used is decremented
            updated_workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            assert updated_workspace.storage_used == initial_storage_used - file_size

            # Verify file storage delete was called
            mock_file_storage.delete.assert_called_once_with(storage_path)

    def test_delete_file_not_found_wrong_file_id(self):
        """Test file deletion with non-existent file ID."""
        # Create workspace
        workspace = self._create_workspace_via_api(None, "Test Workspace", "public")
        workspace_id = workspace["id"]

        # Try to delete non-existent file
        fake_file_id = str(uuid.uuid4())
        response = self.client.delete(f"/v1/workspaces/{workspace_id}/files/{fake_file_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "File not found" in data["error"]
        assert fake_file_id in data["error"]  # Should include the file ID

    def test_delete_file_wrong_workspace_id(self):
        """Test file deletion with non-existent workspace ID."""
        fake_workspace_id = str(uuid.uuid4())
        fake_file_id = str(uuid.uuid4())

        response = self.client.delete(f"/v1/workspaces/{fake_workspace_id}/files/{fake_file_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "Workspace not found" in data["error"]

    def test_delete_file_private_workspace_forbidden_no_auth(self):
        """Test file deletion forbidden in private workspace without authentication."""
        # Create user and private workspace
        user = self._create_user('owner@example.com')
        workspace = self._create_workspace_via_api(user, "Private Test", "private")
        workspace_id = workspace["id"]

        # Upload a file as owner
        file_info = self._create_file_via_api(workspace_id, "test.csv", user)
        file_id = file_info["id"]

        # Try to delete without auth - should be forbidden
        response = self.client.delete(f"/v1/workspaces/{workspace_id}/files/{file_id}")

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert "Not authorized" in data["error"]

    def test_delete_file_private_workspace_forbidden_wrong_user(self):
        """Test file deletion forbidden in private workspace by non-owner."""
        # Create owner and workspace
        owner = self._create_user('owner@example.com')
        workspace = self._create_workspace_via_api(owner, "Private Test", "private")
        workspace_id = workspace["id"]

        # Upload a file as owner
        file_info = self._create_file_via_api(workspace_id, "test.csv", owner)
        file_id = file_info["id"]

        # Create another user
        other_user = self._create_user('other@example.com')
        other_headers = self._get_auth_headers(other_user)

        # Try to delete as different user - should be forbidden
        response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/files/{file_id}",
            headers=other_headers
        )

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert "Not authorized" in data["error"]

    def test_delete_file_file_belongs_to_different_workspace(self):
        """Test file deletion where file doesn't belong to specified workspace."""
        # Create two workspaces
        workspace1 = self._create_workspace_via_api(None, "Workspace 1", "public")
        workspace2 = self._create_workspace_via_api(None, "Workspace 2", "public")

        # Upload file to workspace1
        file_info = self._create_file_via_api(workspace1["id"], "test.csv", None)
        file_id = file_info["id"]

        # Try to delete file from workspace2 - should not find it
        response = self.client.delete(f"/v1/workspaces/{workspace2['id']}/files/{file_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "File not found" in data["error"]
        assert file_id in data["error"]  # Should include the file ID
