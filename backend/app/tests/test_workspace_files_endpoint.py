"""
Tests for workspace files API endpoint.
"""

import uuid

from app.tests import APITest


class TestListWorkspaceFiles(APITest):
    """Tests for GET /v1/workspaces/{workspace_id}/files/ endpoint."""

    def test_list_files_public_workspace_no_auth(self):
        """Test listing files in a public workspace without authentication."""
        # Create a public workspace
        workspace = self._create_workspace_via_api()
        workspace_id = workspace["id"]

        # Create some files in the workspace
        file1 = self._create_file_via_api(workspace_id, "data1.csv")
        file2 = self._create_file_via_api(workspace_id, "data2.csv")

        # Request files without authentication
        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        # Check that all expected fields are present
        for file_data in data:
            assert "id" in file_data
            assert "table_name" in file_data
            assert "filename" in file_data
            assert "size" in file_data
            assert "uploaded_at" in file_data

        # Check specific file data
        file_ids = [f["id"] for f in data]
        assert file1["id"] in file_ids
        assert file2["id"] in file_ids

    def test_list_files_public_workspace_with_auth(self):
        """Test listing files in a public workspace with authentication."""
        # Create a user and a public workspace
        user = self._create_user('test@example.com')
        workspace = self._create_workspace_via_api(user, visibility="public")
        workspace_id = workspace["id"]

        # Create a file
        file1 = self._create_file_via_api(workspace_id, "data.csv")

        # Request files with authentication
        headers = self._get_auth_headers(user)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == file1["id"]
        assert data[0]["table_name"] == file1["table_name"]

    def test_list_files_private_workspace_as_owner(self):
        """Test listing files in a private workspace as the owner."""
        # Create a user and a private workspace
        user = self._create_user('test@example.com')
        workspace = self._create_workspace_via_api(user, visibility="private")
        workspace_id = workspace["id"]

        # Create a file
        file1 = self._create_file_via_api(workspace_id, "private_data.csv", user)

        # Request files as the owner
        headers = self._get_auth_headers(user)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == file1["id"]
        assert data[0]["table_name"] == "private_data"

    def test_list_files_private_workspace_no_auth(self):
        """Test listing files in a private workspace without authentication."""
        # Create a user and a private workspace
        user = self._create_user('test@example.com')
        workspace = self._create_workspace_via_api(user, visibility="private")
        workspace_id = workspace["id"]

        # Create a file
        self._create_file_via_api(workspace_id, "private_data.csv", user)

        # Request files without authentication
        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list

    def test_list_files_private_workspace_as_other_user(self):
        """Test listing files in a private workspace as a different user."""
        # Create owner and other user
        owner = self._create_user("owner@example.com")

        # Create a private workspace owned by owner
        workspace = self._create_workspace_via_api(owner, visibility="private")
        workspace_id = workspace["id"]

        # Create a file
        self._create_file_via_api(workspace_id, "private_data.csv", owner)

        # Request files as the other user
        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list

    def test_list_files_nonexistent_workspace(self):
        """Test listing files for a nonexistent workspace."""
        fake_workspace_id = str(uuid.uuid4())

        response = self.client.get(f"/v1/workspaces/{fake_workspace_id}/files/")

        assert response.status_code == 404

    def test_list_files_empty_workspace(self):
        """Test listing files in an empty workspace."""
        workspace = self._create_workspace_via_api()
        workspace_id = workspace["id"]

        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_files_response_format(self):
        """Test that the response format matches the expected schema."""
        workspace = self._create_workspace_via_api(visibility="public")
        workspace_id = workspace["id"]

        self._create_file_via_api(workspace_id, "test_table.csv")

        response = self.client.get(f"/v1/workspaces/{workspace_id}/files/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        file_data = data[0]

        # Check all required fields are present
        required_fields = ["id", "table_name", "filename", "size", "uploaded_at"]
        for field in required_fields:
            assert field in file_data, f"Missing required field: {field}"

        # Check field types and values
        assert isinstance(file_data["id"], str)
        assert isinstance(file_data["table_name"], str)
        assert isinstance(file_data["filename"], str)
        assert isinstance(file_data["size"], int)
        assert isinstance(file_data["uploaded_at"], str)

        # Check specific values
        assert file_data["filename"] == "test_table.csv"
        assert file_data["table_name"] == "test_table"
        assert file_data["size"] == 35

    def test_list_files_only_from_requested_workspace(self):
        """Test that only files from the requested workspace are returned, not from other workspaces."""
        # Create three public workspaces with different numbers of files
        workspace1 = self._create_workspace_via_api(name="Workspace 1", visibility="public")
        workspace2 = self._create_workspace_via_api(name="Workspace 2", visibility="public")
        workspace3 = self._create_workspace_via_api(name="Workspace 3", visibility="public")

        workspace1_id = workspace1["id"]
        workspace2_id = workspace2["id"]
        workspace3_id = workspace3["id"]

        # Create 2 files in workspace1
        file1_ws1 = self._create_file_via_api(workspace1_id, "data1_ws1.csv")
        file2_ws1 = self._create_file_via_api(workspace1_id, "data2_ws1.csv")

        # Create 3 files in workspace2
        file1_ws2 = self._create_file_via_api(workspace2_id, "data1_ws2.csv")
        file2_ws2 = self._create_file_via_api(workspace2_id, "data2_ws2.csv")
        file3_ws2 = self._create_file_via_api(workspace2_id, "data3_ws2.csv")

        # Create 1 file in workspace3
        file1_ws3 = self._create_file_via_api(workspace3_id, "data1_ws3.csv")

        # Test workspace1 - should return only its 2 files
        response1 = self.client.get(f"/v1/workspaces/{workspace1_id}/files/")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 2

        # Verify only workspace1 files are returned
        file_ids_ws1 = [f["id"] for f in data1]
        assert file1_ws1["id"] in file_ids_ws1
        assert file2_ws1["id"] in file_ids_ws1
        # Ensure no files from other workspaces
        assert file1_ws2["id"] not in file_ids_ws1
        assert file1_ws3["id"] not in file_ids_ws1

        # Test workspace2 - should return only its 3 files
        response2 = self.client.get(f"/v1/workspaces/{workspace2_id}/files/")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 3

        # Verify only workspace2 files are returned
        file_ids_ws2 = [f["id"] for f in data2]
        assert file1_ws2["id"] in file_ids_ws2
        assert file2_ws2["id"] in file_ids_ws2
        assert file3_ws2["id"] in file_ids_ws2
        # Ensure no files from other workspaces
        assert file1_ws1["id"] not in file_ids_ws2
        assert file1_ws3["id"] not in file_ids_ws2

        # Test workspace3 - should return only its 1 file
        response3 = self.client.get(f"/v1/workspaces/{workspace3_id}/files/")
        assert response3.status_code == 200
        data3 = response3.json()
        assert len(data3) == 1

        # Verify only workspace3 file is returned
        file_ids_ws3 = [f["id"] for f in data3]
        assert file1_ws3["id"] in file_ids_ws3
        # Ensure no files from other workspaces
        assert file1_ws1["id"] not in file_ids_ws3
        assert file1_ws2["id"] not in file_ids_ws3
