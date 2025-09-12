"""
Tests for the upload_file endpoint in workspace API.
"""
import io

from fastapi.testclient import TestClient

from app.core import config
from app.tests.test_workspaces import create_user, get_auth_headers


def create_workspace(client: TestClient, headers=None, name="UploadTest Workspace"):
    resp = client.post("/v1/workspaces/", json={"name": name}, headers=headers)
    assert resp.status_code == 201
    return resp.json()

class TestUploadFile:
    def test_upload_csv_file_public_workspace(self, client: TestClient):
        ws = create_workspace(client)
        ws_id = ws["id"]
        file_content = b"col1,col2\n1,2\n3,4\n"
        files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}
        resp = client.post(f"/v1/workspaces/{ws_id}/files/", files=files)
        assert resp.status_code == 201
        data = resp.json()
        assert data["filename"] == "test.csv"
        assert data["size"] == len(file_content)
        assert "uploaded_at" in data
        # Check storage_used incremented via API
        resp2 = client.get(f"/v1/workspaces/{ws_id}")
        assert resp2.status_code == 200
        ws_data = resp2.json()
        assert ws_data["storage_used"] == len(file_content)

    def test_upload_csv_file_private_workspace_owner(self, client: TestClient):
        user = create_user(client)
        headers = get_auth_headers(user["id"])
        ws = create_workspace(client, headers=headers, name="PrivateWS")
        ws_id = ws["id"]
        file_content = b"a,b\n5,6\n"
        files = {"file": ("private.csv", io.BytesIO(file_content), "text/csv")}
        resp = client.post(f"/v1/workspaces/{ws_id}/files/", files=files, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["filename"] == "private.csv"
        assert data["size"] == len(file_content)
        assert "uploaded_at" in data
        # Check storage_used incremented via API
        resp2 = client.get(f"/v1/workspaces/{ws_id}", headers=headers)
        assert resp2.status_code == 200
        ws_data = resp2.json()
        assert ws_data["storage_used"] == len(file_content)

    def test_upload_csv_file_private_workspace_not_owner(self, client: TestClient):
        user1 = create_user(client, "user1@upload.com")
        user2 = create_user(client, "user2@upload.com")
        headers1 = get_auth_headers(user1["id"])
        headers2 = get_auth_headers(user2["id"])
        ws = create_workspace(client, headers=headers1, name="PrivateWS2")
        ws_id = ws["id"]
        file_content = b"x,y\n7,8\n"
        files = {"file": ("notowner.csv", io.BytesIO(file_content), "text/csv")}
        resp = client.post(f"/v1/workspaces/{ws_id}/files/", files=files, headers=headers2)
        assert resp.status_code == 404
        assert "not found" in resp.json()["error"].lower()

    def test_upload_non_csv_file(self, client: TestClient):
        ws = create_workspace(client)
        ws_id = ws["id"]
        file_content = b"%PDF-1.4\n..."
        files = {"file": ("bad.pdf", io.BytesIO(file_content), "application/pdf")}
        resp = client.post(f"/v1/workspaces/{ws_id}/files/", files=files)
        assert resp.status_code == 400
        assert "csv" in resp.json()["error"].lower()

    def test_upload_csv_file_too_large(self, client: TestClient, monkeypatch):
        # Patch settings before workspace creation
        monkeypatch.setattr(config.get_settings(), "orphaned_workspace_max_file_size", 10)
        ws = create_workspace(client)
        ws_id = ws["id"]
        file_content = b"col1,col2\n1,2\n3,4\n"
        files = {"file": ("big.csv", io.BytesIO(file_content), "text/csv")}
        resp = client.post(f"/v1/workspaces/{ws_id}/files/", files=files)
        assert resp.status_code == 400
        assert "exceeds max size" in resp.json()["error"].lower()
