"""
Tests for save query API endpoint.
"""

from app.tests import APITest


class TestSaveQuery(APITest):
    """Tests for POST /v1/workspaces/{workspace_id}/queries endpoint."""

    def test_save_query_in_public_orphan_workspace_without_auth(self):
        """Test saving a query in a public orphan workspace without authentication."""
        # Create a public orphan workspace (no auth)
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Try to save a query without authentication (should succeed)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Query"
        assert data["query"] == "SELECT * FROM test"
        assert "id" in data
        assert "created_at" in data

    def test_save_query_in_private_workspace_as_owner(self):
        """Test saving a query in a private workspace as the owner."""
        user = self._create_user("test@example.com")
        headers = self._get_auth_headers(user)

        # Create a private workspace
        workspace = self._create_workspace_via_api(user=user, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=user)

        # Try to save a query as the owner (should succeed)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Owner Query"
        assert data["query"] == "SELECT * FROM data"

    def test_save_query_in_private_workspace_as_non_owner(self):
        """Test saving a query in a private workspace as non-owner (should fail)."""
        owner = self._create_user("owner@example.com")
        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a private workspace as owner
        workspace = self._create_workspace_via_api(user=owner, name="Private Workspace", visibility="private")
        workspace_id = workspace["id"]

        # Upload a CSV file as owner
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Try to save a query as non-owner (should fail with 403)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Non-owner Query",
                "query": "SELECT * FROM data"
            },
            headers=other_headers
        )

        assert response.status_code == 403

    def test_save_query_in_public_owned_workspace_as_owner(self):
        """Test saving a query in a public owned workspace as owner."""
        owner = self._create_user("owner@example.com")
        owner_headers = self._get_auth_headers(owner)

        # Create a public workspace with owner
        workspace = self._create_workspace_via_api(user=owner, name="Public Owned", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Save a query as owner (should succeed)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Owner Query",
                "query": "SELECT * FROM data"
            },
            headers=owner_headers
        )

        assert response.status_code == 201

    def test_save_query_in_public_owned_workspace_as_non_owner(self):
        """Test saving a query in a public owned workspace as non-owner (should fail)."""
        owner = self._create_user("owner@example.com")
        other_user = self._create_user("other@example.com")
        other_headers = self._get_auth_headers(other_user)

        # Create a public workspace with owner
        workspace = self._create_workspace_via_api(user=owner, name="Public Owned", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "data.csv", user=owner)

        # Try to save a query as non-owner (should fail with 403)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Non-owner Query",
                "query": "SELECT * FROM data"
            },
            headers=other_headers
        )

        assert response.status_code == 403

    def test_save_query_with_invalid_sql(self):
        """Test saving a query with invalid SQL (should fail with 400)."""
        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Try to save a query with invalid SQL
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Invalid Query",
                "query": "SELECT * FROM nonexistent_table"
            }
        )

        assert response.status_code == 400

    def test_save_query_with_disallowed_expression(self):
        """Test saving a query with disallowed SQL expression (should fail with 400)."""
        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Upload a CSV file
        self._create_file_via_api(workspace_id, "test.csv", user=None)

        # Try to save a query with disallowed expression (INSERT)
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Insert Query",
                "query": "INSERT INTO test VALUES (1, 2, 3)"
            }
        )

        assert response.status_code == 400

    def test_save_query_with_missing_name(self):
        """Test saving a query without a name (should fail with 422)."""
        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Try to save a query without name
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "query": "SELECT * FROM test"
            }
        )

        assert response.status_code == 422

    def test_save_query_with_missing_query(self):
        """Test saving a query without SQL query text (should fail with 422)."""
        # Create a public orphan workspace
        workspace = self._create_workspace_via_api(user=None, name="Public Orphan", visibility="public")
        workspace_id = workspace["id"]

        # Try to save a query without query text
        response = self.client.post(
            f"/v1/workspaces/{workspace_id}/queries",
            json={
                "name": "Missing Query"
            }
        )

        assert response.status_code == 422

    def test_save_query_in_nonexistent_workspace(self):
        """Test saving a query in a non-existent workspace (should fail with 404)."""
        import uuid
        nonexistent_id = str(uuid.uuid4())

        response = self.client.post(
            f"/v1/workspaces/{nonexistent_id}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test"
            }
        )

        assert response.status_code == 404
