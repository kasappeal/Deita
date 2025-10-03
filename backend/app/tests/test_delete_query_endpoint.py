"""
Tests for DELETE /v1/workspaces/{workspace_id}/queries/{query_id} endpoint.
"""

import uuid

from app.models.query import Query
from app.tests import APITest


class TestDeleteQueryEndpoint(APITest):
    """Tests for DELETE /v1/workspaces/{workspace_id}/queries/{query_id} endpoint."""

    def test_delete_query_success_public_orphan_workspace_no_auth(self):
        """Test successful query deletion in public orphan workspace without authentication."""
        # Create a public orphan workspace (no auth)
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Save a query without authentication
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test"
            }
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Verify query exists in database
        query_record = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert query_record is not None

        # Delete the query without authentication (should succeed)
        delete_response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}"
        )

        # Verify response
        assert delete_response.status_code == 204
        assert delete_response.content == b""

        # Verify query is deleted from database
        deleted_query = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert deleted_query is None

    def test_delete_query_success_private_workspace_owner(self):
        """Test successful query deletion in private workspace by owner."""
        user = self._create_user("owner@example.com")
        headers = self._get_auth_headers(user)

        # Create a private workspace
        workspace = self._create_workspace_via_api(user=user, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=user)

        # Save a query as the owner
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=headers
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Verify query exists in database
        query_record = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert query_record is not None

        # Delete the query as owner (should succeed)
        delete_response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=headers
        )

        # Verify response
        assert delete_response.status_code == 204
        assert delete_response.content == b""

        # Verify query is deleted from database
        deleted_query = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert deleted_query is None

    def test_delete_query_private_workspace_forbidden_no_auth(self):
        """Test query deletion forbidden in private workspace without authentication."""
        user = self._create_user("owner@example.com")
        headers = self._get_auth_headers(user)

        # Create a private workspace
        workspace = self._create_workspace_via_api(user=user, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=user)

        # Save a query as the owner
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=headers
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Try to delete without auth - should be forbidden
        delete_response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}"
        )

        assert delete_response.status_code == 403
        data = delete_response.json()
        assert "error" in data
        assert "Not authorized" in data["error"]

        # Verify query still exists in database
        query_record = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert query_record is not None

    def test_delete_query_private_workspace_forbidden_wrong_user(self):
        """Test query deletion forbidden in private workspace by non-owner."""
        owner = self._create_user("owner@example.com")
        owner_headers = self._get_auth_headers(owner)

        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a private workspace as owner
        workspace = self._create_workspace_via_api(user=owner, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as the owner
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=owner_headers
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Try to delete as different user - should be forbidden
        delete_response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=other_headers
        )

        assert delete_response.status_code == 403
        data = delete_response.json()
        assert "error" in data
        assert "Not authorized" in data["error"]

        # Verify query still exists in database
        query_record = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert query_record is not None

    def test_delete_query_not_found_wrong_query_id(self):
        """Test query deletion with non-existent query ID."""
        # Create workspace
        workspace = self._create_workspace_via_api(None, "Test Workspace", "public")
        workspace_id = workspace["id"]

        # Try to delete non-existent query
        fake_query_id = str(uuid.uuid4())
        response = self.client.delete(f"/v1/workspaces/{workspace_id}/queries/{fake_query_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "Query not found" in data["error"]
        assert fake_query_id in data["error"]  # Should include the query ID

    def test_delete_query_wrong_workspace_id(self):
        """Test query deletion with non-existent workspace ID."""
        fake_workspace_id = str(uuid.uuid4())
        fake_query_id = str(uuid.uuid4())

        response = self.client.delete(f"/v1/workspaces/{fake_workspace_id}/queries/{fake_query_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "Workspace not found" in data["error"]

    def test_delete_query_belongs_to_different_workspace(self):
        """Test query deletion where query doesn't belong to specified workspace."""
        # Create two workspaces
        workspace1 = self._create_workspace_via_api(None, "Workspace 1", "public")
        workspace2 = self._create_workspace_via_api(None, "Workspace 2", "public")

        # Upload file to workspace1
        self._create_file_via_api(workspace1["id"], "test.csv", None)

        # Save query to workspace1
        response = self.client.post(
            f"/v1/workspaces/{workspace1['id']}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test"
            }
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Try to delete query from workspace2 - should not find it
        delete_response = self.client.delete(f"/v1/workspaces/{workspace2['id']}/queries/{query_id}")

        assert delete_response.status_code == 404
        data = delete_response.json()
        assert "error" in data
        assert "Query not found" in data["error"]
        assert query_id in data["error"]  # Should include the query ID

        # Verify query still exists in workspace1
        query_record = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert query_record is not None
        assert str(query_record.workspace_id) == workspace1["id"]

    def test_delete_query_public_owned_workspace_as_owner(self):
        """Test query deletion in public owned workspace as owner."""
        owner = self._create_user("owner@example.com")
        owner_headers = self._get_auth_headers(owner)

        # Create a public workspace with owner
        workspace = self._create_workspace_via_api(user=owner, name="Public Owned", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=owner_headers
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Delete the query as owner (should succeed)
        delete_response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=owner_headers
        )

        assert delete_response.status_code == 204
        assert delete_response.content == b""

        # Verify query is deleted from database
        deleted_query = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert deleted_query is None

    def test_delete_query_public_owned_workspace_as_non_owner(self):
        """Test query deletion in public owned workspace as non-owner (should fail)."""
        owner = self._create_user("owner@example.com")
        owner_headers = self._get_auth_headers(owner)

        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a public workspace with owner
        workspace = self._create_workspace_via_api(user=owner, name="Public Owned", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=owner_headers
        )
        assert response.status_code == 201
        query_data = response.json()
        query_id = query_data["id"]

        # Try to delete the query as non-owner (should fail with 403)
        delete_response = self.client.delete(
            f"/v1/workspaces/{workspace_id}/queries/{query_id}",
            headers=other_headers
        )

        assert delete_response.status_code == 403
        data = delete_response.json()
        assert "error" in data
        assert "Not authorized" in data["error"]

        # Verify query still exists in database
        query_record = self.db.query(Query).filter(Query.id == uuid.UUID(query_id)).first()
        assert query_record is not None
