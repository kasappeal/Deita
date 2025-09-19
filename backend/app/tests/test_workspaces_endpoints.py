"""
Tests for workspace API endpoints.
"""

import uuid

from app.tests import APITest


class TestCreateWorkspace(APITest):
    """Tests for POST /v1/workspaces endpoint."""

    def test_create_workspace_without_auth(self):
        """Test creating a workspace without authentication."""
        response = self.client.post(
            "/v1/workspaces/",
            json={"name": "Test Workspace"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert data["visibility"] == "public"
        assert "id" in data
        assert "created_at" in data
        assert "last_accessed_at" in data

    def test_create_workspace_with_auth_default_visibility(self):
        """Test creating a workspace with authentication (default private visibility)."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        response = self.client.post(
            "/v1/workspaces/",
            json={"name": "Private Workspace"},
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Private Workspace"
        assert data["visibility"] == "private"

    def test_create_workspace_with_auth_explicit_public(self):
        """Test creating a public workspace with authentication."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        response = self.client.post(
            "/v1/workspaces/",
            json={"name": "Public Workspace", "visibility": "public"},
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Public Workspace"
        assert data["visibility"] == "public"

    def test_create_workspace_without_auth_ignores_visibility(self):
        """Test that visibility parameter is ignored when not authenticated."""
        response = self.client.post(
            "/v1/workspaces/",
            json={"name": "Test Workspace", "visibility": "private"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["visibility"] == "public"  # Should be public regardless


class TestListWorkspaces(APITest):
    """Tests for GET /v1/workspaces endpoint."""

    def test_list_workspaces_without_auth(self):
        """Test listing workspaces without authentication returns empty list."""
        response = self.client.get("/v1/workspaces/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_workspaces_with_auth_empty(self):
        """Test listing workspaces with authentication but no workspaces."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        response = self.client.get("/v1/workspaces/", headers=headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_workspaces_with_auth_has_workspaces(self):
        """Test listing workspaces with authentication and existing workspaces."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create some workspaces
        self.client.post("/v1/workspaces/", json={"name": "Workspace 1"}, headers=headers)
        self.client.post("/v1/workspaces/", json={"name": "Workspace 2"}, headers=headers)

        response = self.client.get("/v1/workspaces/", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["Workspace 1", "Workspace 2"]
        assert data[1]["name"] in ["Workspace 1", "Workspace 2"]

    def test_list_workspaces_user_isolation(self):
        """Test that users only see their own workspaces."""
        # Create first user and their workspace
        user = self._create_user('user1@example.com')
        headers1 = self._get_auth_headers(user)
        self.client.post("/v1/workspaces/", json={"name": "User1 Workspace"}, headers=headers1)

        # Create second user and their workspace
        user = self._create_user('user2@example.com')
        headers2 = self._get_auth_headers(user)
        self.client.post("/v1/workspaces/", json={"name": "User2 Workspace"}, headers=headers2)

        # Check that user1 only sees their own workspace
        response1 = self.client.get("/v1/workspaces/", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 1
        assert data1[0]["name"] == "User1 Workspace"

        # Check that user2 only sees their own workspace
        response2 = self.client.get("/v1/workspaces/", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["name"] == "User2 Workspace"


class TestGetWorkspace(APITest):
    """Tests for GET /v1/workspaces/{id} endpoint."""

    def test_get_nonexistent_workspace(self):
        """Test getting a non-existent workspace."""
        fake_id = uuid.uuid4()
        response = self.client.get(f"/v1/workspaces/{fake_id}")

        assert response.status_code == 404

    def test_get_public_workspace_without_auth(self):
        """Test getting a public workspace without authentication."""
        # Create public workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Public Workspace"})
        workspace_id = response.json()["id"]

        response = self.client.get(f"/v1/workspaces/{workspace_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Public Workspace"
        assert data["visibility"] == "public"

    def test_get_private_workspace_without_auth(self):
        """Test getting a private workspace without authentication returns 404."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create private workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Private Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Try to access without auth
        response = self.client.get(f"/v1/workspaces/{workspace_id}")

        assert response.status_code == 404

    def test_get_private_workspace_as_owner(self):
        """Test getting a private workspace as the owner."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create private workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Private Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Access as owner
        response = self.client.get(f"/v1/workspaces/{workspace_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Private Workspace"
        assert data["visibility"] == "private"

    def test_get_private_workspace_as_different_user(self):
        """Test getting a private workspace as a different user returns 404."""
        user1 = self._create_user('test1@example.com')
        headers1 = self._get_auth_headers(user1)
        user2 = self._create_user('test2@example.com')
        headers2 = self._get_auth_headers(user2)

        # Create private workspace with user1
        response = self.client.post("/v1/workspaces/", json={"name": "Private Workspace"}, headers=headers1)
        workspace_id = response.json()["id"]

        # Try to access as user2
        response = self.client.get(f"/v1/workspaces/{workspace_id}", headers=headers2)

        assert response.status_code == 404


class TestUpdateWorkspace(APITest):
    """Tests for PUT /v1/workspaces/{id} endpoint."""

    def test_update_nonexistent_workspace(self):
        """Test updating a non-existent workspace."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)
        fake_id = uuid.uuid4()

        response = self.client.put(
            f"/v1/workspaces/{fake_id}",
            json={"name": "Updated Name"},
            headers=headers
        )

        assert response.status_code == 404

    def test_update_orphan_workspace(self):
        """Test updating an orphan workspace returns 403."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create an orphan workspace (no auth)
        response = self.client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]

        # Try to update as authenticated user
        response = self.client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Name"},
            headers=headers
        )

        assert response.status_code == 403

    def test_update_workspace_without_auth(self):
        """Test updating workspace without authentication returns 403."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Try to update without auth
        response = self.client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Name"}
        )

        assert response.status_code == 401

    def test_update_workspace_as_different_user(self):
        """Test updating workspace as different user returns 403."""
        user1 = self._create_user('test1@example.com')
        headers1 = self._get_auth_headers(user1)
        user2 = self._create_user('test2@example.com')
        headers2 = self._get_auth_headers(user2)

        # Create workspace with user1
        response = self.client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers1)
        workspace_id = response.json()["id"]

        # Try to update as user2
        response = self.client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Name"},
            headers=headers2
        )

        assert response.status_code == 403

    def test_update_workspace_as_owner(self):
        """Test updating workspace as owner succeeds."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Update workspace
        response = self.client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Workspace", "visibility": "public"},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Workspace"
        assert data["visibility"] == "public"


class TestDeleteWorkspace(APITest):
    """Tests for DELETE /v1/workspaces/{id} endpoint."""

    def test_delete_nonexistent_workspace(self):
        """Test deleting a non-existent workspace."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)
        fake_id = uuid.uuid4()

        response = self.client.delete(f"/v1/workspaces/{fake_id}", headers=headers)

        assert response.status_code == 404

    def test_delete_orphan_workspace(self):
        """Test deleting an orphan workspace returns 403."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create an orphan workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]

        # Try to delete as authenticated user
        response = self.client.delete(f"/v1/workspaces/{workspace_id}", headers=headers)

        assert response.status_code == 403

    def test_delete_workspace_without_auth(self):
        """Test deleting workspace without authentication returns 403."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Try to delete without auth
        response = self.client.delete(f"/v1/workspaces/{workspace_id}")

        assert response.status_code == 401

    def test_delete_workspace_as_owner(self):
        """Test deleting workspace as owner succeeds."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Delete workspace
        response = self.client.delete(f"/v1/workspaces/{workspace_id}", headers=headers)

        assert response.status_code == 204

        # Verify it's deleted
        response = self.client.get(f"/v1/workspaces/{workspace_id}", headers=headers)
        assert response.status_code == 404


class TestClaimWorkspace(APITest):
    """Tests for POST /v1/workspaces/{id}/claim endpoint."""

    def test_claim_workspace_without_auth(self):
        """Test claiming workspace without authentication returns 401."""
        # Create orphan workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]

        # Try to claim without auth
        response = self.client.post(f"/v1/workspaces/{workspace_id}/claim")

        assert response.status_code == 401

    def test_claim_nonexistent_workspace(self):
        """Test claiming a non-existent workspace returns 404."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)
        fake_id = uuid.uuid4()

        response = self.client.post(f"/v1/workspaces/{fake_id}/claim", headers=headers)

        assert response.status_code == 404

    def test_claim_owned_workspace(self):
        """Test claiming a workspace that already has an owner returns 403."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create owned workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Owned Workspace"}, headers=headers)
        workspace_id = response.json()["id"]

        # Try to claim owned workspace
        response = self.client.post(f"/v1/workspaces/{workspace_id}/claim", headers=headers)

        assert response.status_code == 403

    def test_claim_orphan_workspace_success(self):
        """Test successfully claiming an orphan workspace."""
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)

        # Create orphan workspace
        response = self.client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]

        # Verify it's public and orphan
        response = self.client.get(f"/v1/workspaces/{workspace_id}")
        assert response.status_code == 200
        assert response.json()["visibility"] == "public"

        # Claim the workspace
        response = self.client.post(f"/v1/workspaces/{workspace_id}/claim", headers=headers)
        assert response.status_code == 204

        # Verify it's now owned but visibility preserved
        response = self.client.get(f"/v1/workspaces/{workspace_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["visibility"] == "public"  # Visibility preserved as requested

        # Verify it appears in owner's workspace list
        response = self.client.get("/v1/workspaces/", headers=headers)
        assert response.status_code == 200
        workspaces = response.json()
        workspace_ids = [w["id"] for w in workspaces]
        assert workspace_id in workspace_ids
