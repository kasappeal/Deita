"""
Test cases for workspace API endpoints and functionality.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.models import Workspace, WorkspaceUsage


class TestWorkspaceAPI:
    """Test workspace API endpoints."""

    def test_create_orphan_workspace(self, client: TestClient):
        """Test creating an orphan workspace."""
        data = {
            "name": "Test Orphan Workspace",
            "description": "Test description",
        }
        
        response = client.post("/v1/workspaces/orphan", json=data)
        assert response.status_code == 201
        
        workspace = response.json()
        assert workspace["name"] == data["name"]
        assert workspace["description"] == data["description"]
        assert workspace["is_orphan"] is True
        assert workspace["is_public"] is True
        assert workspace["owner_id"] is None
        assert workspace["storage_quota_bytes"] == 52428800  # 50MB

    def test_list_workspaces(self, client: TestClient):
        """Test listing workspaces."""
        # First create a workspace
        client.post("/v1/workspaces/orphan", json={
            "name": "Test Workspace",
            "description": "Test description",
        })
        
        response = client.get("/v1/workspaces")
        assert response.status_code == 200
        
        data = response.json()
        assert "workspaces" in data
        assert data["total"] >= 1
        assert data["page"] == 1
        assert data["size"] == 20

    def test_list_workspaces_with_pagination(self, client: TestClient):
        """Test workspace listing with pagination."""
        response = client.get("/v1/workspaces?page=1&size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5

    def test_list_workspaces_with_search(self, client: TestClient):
        """Test workspace listing with search filter."""
        # Create a workspace with specific name
        client.post("/v1/workspaces/orphan", json={
            "name": "Analytics Project",
            "description": "Data analytics workspace",
        })
        
        response = client.get("/v1/workspaces?search=Analytics")
        assert response.status_code == 200
        
        data = response.json()
        workspaces = data["workspaces"]
        if workspaces:
            assert "Analytics" in workspaces[0]["name"]

    def test_validate_workspace_name(self, client: TestClient):
        """Test workspace name validation."""
        # Test available name
        response = client.post("/v1/workspaces/validate-name", json={
            "name": "Unique Workspace Name"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["available"] is True
        assert "available" in data["message"]

    def test_get_workspace_templates(self, client: TestClient):
        """Test getting workspace templates."""
        response = client.get("/v1/workspaces/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) > 0

    def test_create_workspace_without_auth_should_fail(self, client: TestClient):
        """Test that creating owned workspace without auth fails."""
        data = {
            "name": "Test Owned Workspace",
            "description": "Test description",
            "is_public": True,
        }
        
        response = client.post("/v1/workspaces", json=data)
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_workspace_name_validation_edge_cases(self, client: TestClient):
        """Test workspace name validation with edge cases."""
        # Test empty name
        response = client.post("/v1/workspaces/validate-name", json={"name": ""})
        assert response.status_code == 422  # Validation error
        
        # Test very long name
        long_name = "a" * 101  # Exceeds 100 character limit
        response = client.post("/v1/workspaces/validate-name", json={"name": long_name})
        assert response.status_code == 422  # Validation error

    def test_orphan_workspace_creation_data_integrity(self, client: TestClient):
        """Test that orphan workspace creation maintains data integrity."""
        data = {
            "name": "Integrity Test Workspace",
            "description": "Testing data integrity",
        }
        
        response = client.post("/v1/workspaces/orphan", json=data)
        assert response.status_code == 201
        
        workspace = response.json()
        
        # Check all expected fields are present and have correct types
        assert isinstance(workspace["id"], str)
        assert isinstance(workspace["created_at"], str)
        assert isinstance(workspace["updated_at"], str)
        assert workspace["expires_at"] is not None  # Should have expiration
        assert workspace["settings"] == {}  # Should be empty dict

    def test_workspace_listing_filters(self, client: TestClient):
        """Test workspace listing with various filters."""
        # Create some test workspaces
        client.post("/v1/workspaces/orphan", json={
            "name": "Public Orphan",
            "description": "Public orphan workspace",
        })
        
        # Test orphan filter
        response = client.get("/v1/workspaces?is_orphan=true")
        assert response.status_code == 200
        
        data = response.json()
        for workspace in data["workspaces"]:
            assert workspace["is_orphan"] is True

        # Test public filter
        response = client.get("/v1/workspaces?is_public=true")
        assert response.status_code == 200
        
        data = response.json()
        for workspace in data["workspaces"]:
            assert workspace["is_public"] is True


class TestWorkspaceBusinessLogic:
    """Test workspace business logic and service layer."""

    def test_orphan_workspace_has_expiration(self, client: TestClient):
        """Test that orphan workspaces have expiration dates."""
        response = client.post("/v1/workspaces/orphan", json={
            "name": "Expiring Workspace",
            "description": "Should expire in 30 days",
        })
        
        workspace = response.json()
        assert workspace["expires_at"] is not None
        
        # Parse the expiration date and verify it's in the future
        from datetime import datetime
        expires_at = datetime.fromisoformat(workspace["expires_at"].replace("Z", "+00:00"))
        now = datetime.now(expires_at.tzinfo)
        assert expires_at > now

    def test_workspace_storage_quota_defaults(self, client: TestClient):
        """Test that workspaces have appropriate storage quota defaults."""
        # Orphan workspace should have 50MB quota
        response = client.post("/v1/workspaces/orphan", json={
            "name": "Quota Test Workspace",
        })
        
        workspace = response.json()
        assert workspace["storage_quota_bytes"] == 52428800  # 50MB

    def test_workspace_response_schema(self, client: TestClient):
        """Test that workspace responses match expected schema."""
        response = client.post("/v1/workspaces/orphan", json={
            "name": "Schema Test",
            "description": "Testing response schema",
        })
        
        workspace = response.json()
        required_fields = [
            "id", "name", "description", "owner_id", "is_public", "is_orphan",
            "storage_quota_bytes", "settings", "created_at", "updated_at", "expires_at"
        ]
        
        for field in required_fields:
            assert field in workspace, f"Missing required field: {field}"