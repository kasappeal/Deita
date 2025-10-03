"""
Tests for saved queries API endpoints.
"""

import uuid

from app.tests import APITest


class TestSaveQuery(APITest):
    """Tests for POST /v1/workspaces/:id/queries endpoint."""

    def test_save_query_in_public_workspace_without_auth(self):
        """Test saving a query in a public workspace without authentication."""
        # Create a public workspace
        workspace = self._create_workspace_via_api(name="Test Workspace", visibility="public")
        
        # Save a query
        response = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test_table LIMIT 10"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Query"
        assert data["query"] == "SELECT * FROM test_table LIMIT 10"
        assert "id" in data
        assert "created_at" in data

    def test_save_query_in_private_workspace_with_auth(self):
        """Test saving a query in a private workspace with authentication."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)
        
        # Create a private workspace
        workspace = self._create_workspace_via_api(user, name="Private Workspace", visibility="private")
        
        # Save a query
        response = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "name": "Private Query",
                "query": "SELECT COUNT(*) FROM users"
            },
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Private Query"
        assert data["query"] == "SELECT COUNT(*) FROM users"

    def test_save_query_in_private_workspace_without_auth(self):
        """Test saving a query in a private workspace without authentication should fail."""
        user = self._create_user('test@example.com')
        
        # Create a private workspace
        workspace = self._create_workspace_via_api(user, name="Private Workspace", visibility="private")
        
        # Try to save a query without auth
        response = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "name": "Unauthorized Query",
                "query": "SELECT * FROM secret_data"
            }
        )

        assert response.status_code == 403

    def test_save_duplicate_query_name(self):
        """Test saving a query with a duplicate name should fail."""
        # Create a public workspace
        workspace = self._create_workspace_via_api(name="Test Workspace", visibility="public")
        
        # Save a query
        response1 = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "name": "Duplicate Query",
                "query": "SELECT * FROM table1"
            }
        )
        assert response1.status_code == 201
        
        # Try to save another query with the same name
        response2 = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "name": "Duplicate Query",
                "query": "SELECT * FROM table2"
            }
        )
        assert response2.status_code == 400

    def test_save_query_with_invalid_data(self):
        """Test saving a query with invalid data should fail."""
        # Create a public workspace
        workspace = self._create_workspace_via_api(name="Test Workspace", visibility="public")
        
        # Try to save a query without name
        response = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "query": "SELECT * FROM test"
            }
        )
        assert response.status_code == 422

        # Try to save a query without query text
        response = self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={
                "name": "Test Query"
            }
        )
        assert response.status_code == 422

    def test_save_query_in_nonexistent_workspace(self):
        """Test saving a query in a non-existent workspace should fail."""
        fake_workspace_id = str(uuid.uuid4())
        
        response = self.client.post(
            f"/v1/workspaces/{fake_workspace_id}/queries",
            json={
                "name": "Test Query",
                "query": "SELECT * FROM test"
            }
        )
        
        assert response.status_code == 404


class TestListSavedQueries(APITest):
    """Tests for GET /v1/workspaces/:id/queries endpoint."""

    def test_list_queries_in_public_workspace(self):
        """Test listing queries in a public workspace."""
        # Create a public workspace
        workspace = self._create_workspace_via_api(name="Test Workspace", visibility="public")
        
        # Save some queries
        self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={"name": "Query 1", "query": "SELECT 1"}
        )
        self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={"name": "Query 2", "query": "SELECT 2"}
        )
        
        # List queries
        response = self.client.get(f"/v1/workspaces/{workspace['id']}/queries")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        # Queries should be ordered by created_at descending
        assert data[0]["name"] == "Query 2"
        assert data[1]["name"] == "Query 1"

    def test_list_queries_in_private_workspace_with_auth(self):
        """Test listing queries in a private workspace with authentication."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)
        
        # Create a private workspace
        workspace = self._create_workspace_via_api(user, name="Private Workspace", visibility="private")
        
        # Save a query
        self.client.post(
            f"/v1/workspaces/{workspace['id']}/queries",
            json={"name": "Private Query", "query": "SELECT * FROM users"},
            headers=headers
        )
        
        # List queries
        response = self.client.get(
            f"/v1/workspaces/{workspace['id']}/queries",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Private Query"

    def test_list_queries_in_private_workspace_without_auth(self):
        """Test listing queries in a private workspace without authentication should fail."""
        user = self._create_user('test@example.com')
        
        # Create a private workspace
        workspace = self._create_workspace_via_api(user, name="Private Workspace", visibility="private")
        
        # Try to list queries without auth
        response = self.client.get(f"/v1/workspaces/{workspace['id']}/queries")
        
        assert response.status_code == 404

    def test_list_queries_empty_workspace(self):
        """Test listing queries in a workspace with no saved queries."""
        # Create a public workspace
        workspace = self._create_workspace_via_api(name="Empty Workspace", visibility="public")
        
        # List queries
        response = self.client.get(f"/v1/workspaces/{workspace['id']}/queries")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_queries_in_nonexistent_workspace(self):
        """Test listing queries in a non-existent workspace should fail."""
        fake_workspace_id = str(uuid.uuid4())
        
        response = self.client.get(f"/v1/workspaces/{fake_workspace_id}/queries")
        
        assert response.status_code == 404
