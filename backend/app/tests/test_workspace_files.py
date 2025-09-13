"""
Tests for workspace files API endpoint.
"""

import uuid

from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.core.config import get_settings
from app.models import User, Workspace
from app.models.file import File

settings = get_settings()


def create_user(client: TestClient, email: str = "test@example.com") -> dict:
    """Create a user for testing and return the user data."""
    from app.tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    user = User(email=email, full_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "email": user.email}


def create_workspace(
    client: TestClient, name: str = "Test Workspace", visibility: str = "public", user_id: int = None
) -> dict:
    """Create a workspace for testing and return the workspace data."""
    from app.tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    workspace = Workspace(
        name=name,
        visibility=visibility,
        owner_id=user_id,
        max_file_size=1024 * 1024,  # 1MB
        max_storage=10 * 1024 * 1024,  # 10MB
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    db.close()
    return {"id": str(workspace.id), "name": workspace.name, "visibility": workspace.visibility}


def create_file(client: TestClient, workspace_id: str, filename: str = "test.csv") -> dict:
    """Create a file for testing and return the file data."""
    from app.tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    file_obj = File(
        workspace_id=uuid.UUID(workspace_id),
        table_name=filename.replace(".csv", ""),
        filename=filename,
        storage_path=f"test-storage-path/{filename}",
        size=1024,
    )
    db.add(file_obj)
    db.commit()
    db.refresh(file_obj)
    db.close()
    return {
        "id": str(file_obj.id),
        "table_name": file_obj.table_name,
        "filename": file_obj.filename,
        "size": file_obj.size,
        "uploaded_at": file_obj.uploaded_at.isoformat(),
    }


def get_auth_headers(user_id: int) -> dict:
    """Get authorization headers for a user."""
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


class TestListWorkspaceFiles:
    """Tests for GET /v1/workspaces/{workspace_id}/files endpoint."""

    def test_list_files_public_workspace_no_auth(self, client: TestClient):
        """Test listing files in a public workspace without authentication."""
        # Create a public workspace
        workspace = create_workspace(client, visibility="public")
        workspace_id = workspace["id"]

        # Create some files in the workspace
        file1 = create_file(client, workspace_id, "data1.csv")
        file2 = create_file(client, workspace_id, "data2.csv")

        # Request files without authentication
        response = client.get(f"/v1/workspaces/{workspace_id}/files")

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

    def test_list_files_public_workspace_with_auth(self, client: TestClient):
        """Test listing files in a public workspace with authentication."""
        # Create a user and a public workspace
        user = create_user(client)
        workspace = create_workspace(client, visibility="public", user_id=user["id"])
        workspace_id = workspace["id"]

        # Create a file
        file1 = create_file(client, workspace_id, "data.csv")

        # Request files with authentication
        headers = get_auth_headers(user["id"])
        response = client.get(f"/v1/workspaces/{workspace_id}/files", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == file1["id"]
        assert data[0]["table_name"] == file1["table_name"]

    def test_list_files_private_workspace_as_owner(self, client: TestClient):
        """Test listing files in a private workspace as the owner."""
        # Create a user and a private workspace
        user = create_user(client)
        workspace = create_workspace(client, visibility="private", user_id=user["id"])
        workspace_id = workspace["id"]

        # Create a file
        file1 = create_file(client, workspace_id, "private_data.csv")

        # Request files as the owner
        headers = get_auth_headers(user["id"])
        response = client.get(f"/v1/workspaces/{workspace_id}/files", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == file1["id"]
        assert data[0]["table_name"] == "private_data"

    def test_list_files_private_workspace_no_auth(self, client: TestClient):
        """Test listing files in a private workspace without authentication."""
        # Create a user and a private workspace
        user = create_user(client)
        workspace = create_workspace(client, visibility="private", user_id=user["id"])
        workspace_id = workspace["id"]

        # Create a file
        create_file(client, workspace_id, "private_data.csv")

        # Request files without authentication
        response = client.get(f"/v1/workspaces/{workspace_id}/files")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list

    def test_list_files_private_workspace_as_other_user(self, client: TestClient):
        """Test listing files in a private workspace as a different user."""
        # Create owner and other user
        owner = create_user(client, "owner@example.com")
        other_user = create_user(client, "other@example.com")

        # Create a private workspace owned by owner
        workspace = create_workspace(client, visibility="private", user_id=owner["id"])
        workspace_id = workspace["id"]

        # Create a file
        create_file(client, workspace_id, "private_data.csv")

        # Request files as the other user
        headers = get_auth_headers(other_user["id"])
        response = client.get(f"/v1/workspaces/{workspace_id}/files")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list

    def test_list_files_nonexistent_workspace(self, client: TestClient):
        """Test listing files for a nonexistent workspace."""
        fake_workspace_id = str(uuid.uuid4())

        response = client.get(f"/v1/workspaces/{fake_workspace_id}/files")

        assert response.status_code == 404

    def test_list_files_empty_workspace(self, client: TestClient):
        """Test listing files in an empty workspace."""
        workspace = create_workspace(client, visibility="public")
        workspace_id = workspace["id"]

        response = client.get(f"/v1/workspaces/{workspace_id}/files")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_files_response_format(self, client: TestClient):
        """Test that the response format matches the expected schema."""
        workspace = create_workspace(client, visibility="public")
        workspace_id = workspace["id"]

        file1 = create_file(client, workspace_id, "test_table.csv")

        response = client.get(f"/v1/workspaces/{workspace_id}/files")

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
        assert file_data["size"] == 1024