"""
Tests for workspace API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.auth import create_access_token
from app.core.config import get_settings
from app.models import User, Workspace

settings = get_settings()


def create_user(client: TestClient, email: str = "test@example.com") -> dict:
    """Create a user for testing and return the user data."""
    # Since we don't have user creation endpoint, we'll mock directly in DB
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    user = User(
        email=email,
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "email": user.email}


def get_auth_headers(user_id: int) -> dict:
    """Get authorization headers for a user."""
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


class TestCreateWorkspace:
    """Tests for POST /v1/workspaces endpoint."""
    
    def test_create_workspace_without_auth(self, client: TestClient):
        """Test creating a workspace without authentication."""
        response = client.post(
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
    
    def test_create_workspace_with_auth_default_visibility(self, client: TestClient):
        """Test creating a workspace with authentication (default private visibility)."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        response = client.post(
            "/v1/workspaces/",
            json={"name": "Private Workspace"},
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Private Workspace"
        assert data["visibility"] == "private"
    
    def test_create_workspace_with_auth_explicit_public(self, client: TestClient):
        """Test creating a public workspace with authentication."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        response = client.post(
            "/v1/workspaces/",
            json={"name": "Public Workspace", "visibility": "public"},
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Public Workspace"
        assert data["visibility"] == "public"
    
    def test_create_workspace_without_auth_ignores_visibility(self, client: TestClient):
        """Test that visibility parameter is ignored when not authenticated."""
        response = client.post(
            "/v1/workspaces/",
            json={"name": "Test Workspace", "visibility": "private"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["visibility"] == "public"  # Should be public regardless


class TestListWorkspaces:
    """Tests for GET /v1/workspaces endpoint."""
    
    def test_list_workspaces_without_auth(self, client: TestClient):
        """Test listing workspaces without authentication returns empty list."""
        response = client.get("/v1/workspaces/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_workspaces_with_auth_empty(self, client: TestClient):
        """Test listing workspaces with authentication but no workspaces."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        response = client.get("/v1/workspaces/", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_workspaces_with_auth_has_workspaces(self, client: TestClient):
        """Test listing workspaces with authentication and existing workspaces."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create some workspaces
        client.post("/v1/workspaces/", json={"name": "Workspace 1"}, headers=headers)
        client.post("/v1/workspaces/", json={"name": "Workspace 2"}, headers=headers)
        
        response = client.get("/v1/workspaces/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["Workspace 1", "Workspace 2"]
        assert data[1]["name"] in ["Workspace 1", "Workspace 2"]


class TestGetWorkspace:
    """Tests for GET /v1/workspaces/{id} endpoint."""
    
    def test_get_nonexistent_workspace(self, client: TestClient):
        """Test getting a non-existent workspace."""
        fake_id = uuid.uuid4()
        response = client.get(f"/v1/workspaces/{fake_id}")
        
        assert response.status_code == 404
    
    def test_get_public_workspace_without_auth(self, client: TestClient):
        """Test getting a public workspace without authentication."""
        # Create public workspace
        response = client.post("/v1/workspaces/", json={"name": "Public Workspace"})
        workspace_id = response.json()["id"]
        
        response = client.get(f"/v1/workspaces/{workspace_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Public Workspace"
        assert data["visibility"] == "public"
    
    def test_get_private_workspace_without_auth(self, client: TestClient):
        """Test getting a private workspace without authentication returns 404."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create private workspace
        response = client.post("/v1/workspaces/", json={"name": "Private Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Try to access without auth
        response = client.get(f"/v1/workspaces/{workspace_id}")
        
        assert response.status_code == 404
    
    def test_get_private_workspace_as_owner(self, client: TestClient):
        """Test getting a private workspace as the owner."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create private workspace
        response = client.post("/v1/workspaces/", json={"name": "Private Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Access as owner
        response = client.get(f"/v1/workspaces/{workspace_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Private Workspace"
        assert data["visibility"] == "private"
    
    def test_get_private_workspace_as_different_user(self, client: TestClient):
        """Test getting a private workspace as a different user returns 404."""
        user1 = create_user(client, "user1@example.com")
        user2 = create_user(client, "user2@example.com")
        headers1 = get_auth_headers(user1["id"])
        headers2 = get_auth_headers(user2["id"])
        
        # Create private workspace with user1
        response = client.post("/v1/workspaces/", json={"name": "Private Workspace"}, headers=headers1)
        workspace_id = response.json()["id"]
        
        # Try to access as user2
        response = client.get(f"/v1/workspaces/{workspace_id}", headers=headers2)
        
        assert response.status_code == 404


class TestUpdateWorkspace:
    """Tests for PUT /v1/workspaces/{id} endpoint."""
    
    def test_update_nonexistent_workspace(self, client: TestClient):
        """Test updating a non-existent workspace."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        fake_id = uuid.uuid4()
        
        response = client.put(
            f"/v1/workspaces/{fake_id}",
            json={"name": "Updated Name"},
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_update_orphan_workspace(self, client: TestClient):
        """Test updating an orphan workspace returns 403."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create an orphan workspace (no auth)
        response = client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]
        
        # Try to update as authenticated user
        response = client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Name"},
            headers=headers
        )
        
        assert response.status_code == 403
    
    def test_update_workspace_without_auth(self, client: TestClient):
        """Test updating workspace without authentication returns 403."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create workspace
        response = client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Try to update without auth
        response = client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == 403
    
    def test_update_workspace_as_different_user(self, client: TestClient):
        """Test updating workspace as different user returns 403."""
        user1 = create_user(client, "user1@example.com")
        user2 = create_user(client, "user2@example.com")
        headers1 = get_auth_headers(user1["id"])
        headers2 = get_auth_headers(user2["id"])
        
        # Create workspace with user1
        response = client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers1)
        workspace_id = response.json()["id"]
        
        # Try to update as user2
        response = client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Name"},
            headers=headers2
        )
        
        assert response.status_code == 403
    
    def test_update_workspace_as_owner(self, client: TestClient):
        """Test updating workspace as owner succeeds."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create workspace
        response = client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Update workspace
        response = client.put(
            f"/v1/workspaces/{workspace_id}",
            json={"name": "Updated Workspace", "visibility": "public"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Workspace"
        assert data["visibility"] == "public"


class TestDeleteWorkspace:
    """Tests for DELETE /v1/workspaces/{id} endpoint."""
    
    def test_delete_nonexistent_workspace(self, client: TestClient):
        """Test deleting a non-existent workspace."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        fake_id = uuid.uuid4()
        
        response = client.delete(f"/v1/workspaces/{fake_id}", headers=headers)
        
        assert response.status_code == 404
    
    def test_delete_orphan_workspace(self, client: TestClient):
        """Test deleting an orphan workspace returns 403."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create an orphan workspace
        response = client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]
        
        # Try to delete as authenticated user
        response = client.delete(f"/v1/workspaces/{workspace_id}", headers=headers)
        
        assert response.status_code == 403
    
    def test_delete_workspace_without_auth(self, client: TestClient):
        """Test deleting workspace without authentication returns 403."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create workspace
        response = client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Try to delete without auth
        response = client.delete(f"/v1/workspaces/{workspace_id}")
        
        assert response.status_code == 403
    
    def test_delete_workspace_as_owner(self, client: TestClient):
        """Test deleting workspace as owner succeeds."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create workspace
        response = client.post("/v1/workspaces/", json={"name": "Test Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Delete workspace
        response = client.delete(f"/v1/workspaces/{workspace_id}", headers=headers)
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/v1/workspaces/{workspace_id}", headers=headers)
        assert response.status_code == 404


class TestClaimWorkspace:
    """Tests for POST /v1/workspaces/{id}/claim endpoint."""
    
    def test_claim_workspace_without_auth(self, client: TestClient):
        """Test claiming workspace without authentication returns 401."""
        # Create orphan workspace
        response = client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]
        
        # Try to claim without auth
        response = client.post(f"/v1/workspaces/{workspace_id}/claim")
        
        assert response.status_code == 401
    
    def test_claim_nonexistent_workspace(self, client: TestClient):
        """Test claiming a non-existent workspace returns 404."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        fake_id = uuid.uuid4()
        
        response = client.post(f"/v1/workspaces/{fake_id}/claim", headers=headers)
        
        assert response.status_code == 404
    
    def test_claim_owned_workspace(self, client: TestClient):
        """Test claiming a workspace that already has an owner returns 403."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create owned workspace
        response = client.post("/v1/workspaces/", json={"name": "Owned Workspace"}, headers=headers)
        workspace_id = response.json()["id"]
        
        # Try to claim owned workspace
        response = client.post(f"/v1/workspaces/{workspace_id}/claim", headers=headers)
        
        assert response.status_code == 403
    
    def test_claim_orphan_workspace_success(self, client: TestClient):
        """Test successfully claiming an orphan workspace."""
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        
        # Create orphan workspace
        response = client.post("/v1/workspaces/", json={"name": "Orphan Workspace"})
        workspace_id = response.json()["id"]
        
        # Verify it's public and orphan
        response = client.get(f"/v1/workspaces/{workspace_id}")
        assert response.status_code == 200
        assert response.json()["visibility"] == "public"
        
        # Claim the workspace
        response = client.post(f"/v1/workspaces/{workspace_id}/claim", headers=headers)
        assert response.status_code == 204
        
        # Verify it's now private and owned
        response = client.get(f"/v1/workspaces/{workspace_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["visibility"] == "private"
        
        # Verify it appears in owner's workspace list
        response = client.get("/v1/workspaces/", headers=headers)
        assert response.status_code == 200
        workspaces = response.json()
        workspace_ids = [w["id"] for w in workspaces]
        assert workspace_id in workspace_ids