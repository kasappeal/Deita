"""
Tests for delete query API endpoint.
"""

from app.tests import APITest


class TestDeleteQuery(APITest):
    """Tests for DELETE /v1/workspaces/{workspace_id}/queries/{query_id} endpoint."""

    def _save_query_via_api(self, workspace_id: str, name: str, query: str, user=None):
        """Helper to save a query via API."""
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={"name": name, "query": query},
            headers=self._get_auth_headers(user) if user else None
        )
        assert response.status_code == 201
        return response.json()

    def test_delete_query_in_public_orphan_workspace_without_auth(self):
        """Test deleting a query in a public orphan workspace without authentication."""
        # Create a public orphan workspace (no auth)
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Save a query
        saved_query = self._save_query_via_api(workspace_id, "Test Query", "SELECT * FROM test")
        query_id = saved_query["id"]

        # Delete the query without authentication (should succeed)
        response = self.client.delete(f"/v1/workspaces/{workspace_id}/queries/{query_id}")

        assert response.status_code == 204

    def test_delete_query_in_private_workspace_as_owner(self):
        """Test deleting a query in a private workspace as the owner."""
        user = self._create_user("test@example.com")
        headers = self._get_auth_headers(user)

        # Create a private workspace
        workspace = self._create_workspace_via_api(user=user, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=user)

        # Save a query as the owner
        saved_query = self._save_query_via_api(workspace_id, "Owner Query", "SELECT * FROM data", user=user)
        query_id = saved_query["id"]

        # Delete the query as the owner (should succeed)
        response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=headers
        )

        assert response.status_code == 204

    def test_delete_query_in_private_workspace_as_non_owner(self):
        """Test deleting a query in a private workspace as non-owner (should fail)."""
        owner = self._create_user("owner@example.com")
        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a private workspace as owner
        workspace = self._create_workspace_via_api(user=owner, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file as owner
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner
        saved_query = self._save_query_via_api(workspace_id, "Owner Query", "SELECT * FROM data", user=owner)
        query_id = saved_query["id"]

        # Try to delete the query as non-owner (should fail with 403)
        response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=other_headers
        )

        assert response.status_code == 403

    def test_delete_query_in_public_owned_workspace_as_owner(self):
        """Test deleting a query in a public owned workspace as owner."""
        owner = self._create_user("owner@example.com")
        owner_headers = self._get_auth_headers(owner)

        # Create a public workspace with owner
        workspace = self._create_workspace_via_api(user=owner, name="Public Owned", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner
        saved_query = self._save_query_via_api(workspace_id, "Owner Query", "SELECT * FROM data", user=owner)
        query_id = saved_query["id"]

        # Delete the query as owner (should succeed)
        response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=owner_headers
        )

        assert response.status_code == 204

    def test_delete_query_in_public_owned_workspace_as_non_owner(self):
        """Test deleting a query in a public owned workspace as non-owner (should fail)."""
        owner = self._create_user("owner@example.com")
        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a public workspace with owner
        workspace = self._create_workspace_via_api(user=owner, name="Public Owned", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner
        saved_query = self._save_query_via_api(workspace_id, "Owner Query", "SELECT * FROM data", user=owner)
        query_id = saved_query["id"]

        # Try to delete the query as non-owner (should fail with 403)
        response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=other_headers
        )

        assert response.status_code == 403

    def test_delete_nonexistent_query(self):
        """Test deleting a non-existent query (should fail with 404)."""
        import uuid as uuid_lib

        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Try to delete a non-existent query
        nonexistent_id = str(uuid_lib.uuid4())
        response = self.client.delete(f"/v1/workspaces/{workspace_id}/queries/{nonexistent_id}")

        assert response.status_code == 404

    def test_delete_query_from_different_workspace(self):
        """Test deleting a query that belongs to a different workspace (should fail with 404)."""
        # Create two public orphan workspaces
        workspace1 = self._create_workspace_via_api(user=None, name="Workspace 1", visibility="public")
        workspace1_id = workspace1["id"]
        workspace2 = self._create_workspace_via_api(user=None, name="Workspace 2", visibility="public")
        workspace2_id = workspace2["id"]

        # Upload files and save a query in workspace 1
        self._create_file_via_api(workspace1_id, "test.csv", user=None)
        saved_query = self._save_query_via_api(workspace1_id, "Test Query", "SELECT * FROM test")
        query_id = saved_query["id"]

        # Try to delete the query from workspace 2 (should fail with 404)
        response = self.client.delete(f"/v1/workspaces/{workspace2_id}/queries/{query_id}")

        assert response.status_code == 404

    def test_delete_query_in_nonexistent_workspace(self):
        """Test deleting a query in a non-existent workspace (should fail with 404)."""
        import uuid as uuid_lib

        nonexistent_workspace_id = str(uuid_lib.uuid4())
        nonexistent_query_id = str(uuid_lib.uuid4())

        response = self.client.delete(
            f"/v1/workspaces/{nonexistent_workspace_id}/queries/{nonexistent_query_id}"
        )

        assert response.status_code == 404
