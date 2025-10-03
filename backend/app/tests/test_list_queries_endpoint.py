"""
Tests for list queries API endpoint.
"""

from app.tests import APITest


class TestListQueries(APITest):
    """Tests for GET /v1/workspaces/{workspace_id}/queries endpoint."""

    def test_list_queries_in_public_orphan_workspace_without_auth(self):
        """Test listing queries in a public orphan workspace without authentication."""
        # Create a public orphan workspace (no auth)
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Save a couple of queries
        response1 = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Query 1",
                "query": "SELECT * FROM test"
            }
        )
        assert response1.status_code == 201

        response2 = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Query 2",
                "query": "SELECT COUNT(*) FROM test"
            }
        )
        assert response2.status_code == 201

        # List queries without authentication (should succeed)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        # Check that all expected fields are present
        for query in data:
            assert "id" in query
            assert "name" in query
            assert "query" in query
            assert "created_at" in query

        # Check specific query details
        query_names = [q["name"] for q in data]
        assert "Query 1" in query_names
        assert "Query 2" in query_names

    def test_list_queries_in_private_workspace_as_owner(self):
        """Test listing queries in a private workspace as the owner."""
        user = self._create_user("test@example.com")
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

        # List queries as the owner (should succeed)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Owner Query"
        assert data[0]["query"] == "SELECT * FROM data"

    def test_list_queries_in_private_workspace_as_non_owner(self):
        """Test listing queries in a private workspace as non-owner (should fail)."""
        owner = self._create_user("owner@example.com")
        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a private workspace as owner
        workspace = self._create_workspace_via_api(user=owner, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file as owner
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner
        owner_headers = self._get_auth_headers(owner)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=owner_headers
        )
        assert response.status_code == 201

        # Try to list queries as non-owner (should fail with 403)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries", headers=other_headers)

        assert response.status_code == 403

    def test_list_queries_in_private_workspace_without_auth(self):
        """Test listing queries in a private workspace without authentication (should fail)."""
        owner = self._create_user("owner@example.com")
        owner_headers = self._get_auth_headers(owner)

        # Create a private workspace as owner
        workspace = self._create_workspace_via_api(user=owner, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file as owner
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

        # Try to list queries without authentication (should fail with 403)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries")

        assert response.status_code == 403

    def test_list_queries_in_public_owned_workspace_without_auth(self):
        """Test listing queries in a public owned workspace without authentication."""
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

        # List queries without authentication (should succeed - it's public)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Owner Query"

    def test_list_queries_in_nonexistent_workspace(self):
        """Test listing queries in a non-existent workspace (should fail with 404)."""
        import uuid
        nonexistent_id = str(uuid.uuid4())

        response = self.client.get(f"/v1/workspaces/{nonexistent_id}/queries")

        assert response.status_code == 404

    def test_list_queries_empty_workspace(self):
        """Test listing queries in a workspace with no saved queries."""
        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Empty Workspace", visibility="public")
        workspace_id = workspace["id"]

        # List queries (should return empty list)
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_queries_response_format(self):
        """Test that the response format matches the expected schema."""
        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Test Workspace", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Save a query
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test"
            }
        )
        assert response.status_code == 201
        saved_query = response.json()

        # List queries
        response = self.client.get(f"/v1/workspaces/{workspace_id}/queries")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        query_data = data[0]

        # Check all required fields are present
        required_fields = ["id", "name", "query", "created_at"]
        for field in required_fields:
            assert field in query_data, f"Missing required field: {field}"

        # Check field types and values
        assert isinstance(query_data["id"], str)
        assert isinstance(query_data["name"], str)
        assert isinstance(query_data["query"], str)
        assert isinstance(query_data["created_at"], str)

        # Check specific values
        assert query_data["id"] == saved_query["id"]
        assert query_data["name"] == "Test Query"
        assert query_data["query"] == "SELECT * FROM test"
