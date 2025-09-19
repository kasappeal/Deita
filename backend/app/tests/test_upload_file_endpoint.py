"""
Tests for the upload_file endpoint in workspace API.
"""
import io

from app.core import config
from app.tests import APITest


class TestUploadFile(APITest):

    def test_upload_csv_file_public_workspace(self):
        ws = self._create_workspace_via_api()
        ws_id = ws["id"]
        file_content = b"col1,col2\n1,2\n3,4\n"
        files = {"file": ("test.csv", io.BytesIO(file_content), "text/csv")}
        resp = self.client.post(f"/v1/workspaces/{ws_id}/files/", files=files)
        assert resp.status_code == 201
        data = resp.json()
        # Access file data from the nested structure
        file_data = data["file"]
        assert file_data["filename"] == "test.csv"
        assert file_data["size"] == len(file_content)
        assert "uploaded_at" in file_data
        # Check workspace data from the response directly
        ws_data = data["workspace"]
        assert ws_data["storage_used"] == len(file_content)

    def test_upload_csv_file_private_workspace_owner(self):
        user = self._create_user('test@example.com')
        headers = self._get_auth_headers(user)
        ws = self._create_workspace_via_api(user, name="PrivateWS")
        ws_id = ws["id"]
        file_content = b"a,b\n5,6\n"
        files = {"file": ("private.csv", io.BytesIO(file_content), "text/csv")}
        resp = self.client.post(f"/v1/workspaces/{ws_id}/files/", files=files, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        # Access file data from the nested structure
        file_data = data["file"]
        assert file_data["filename"] == "private.csv"
        assert file_data["size"] == len(file_content)
        assert "uploaded_at" in file_data
        # Check workspace data from the response directly
        ws_data = data["workspace"]
        assert ws_data["storage_used"] == len(file_content)

    def test_upload_csv_file_private_workspace_not_owner(self):
        user1 = self._create_user('test1@example.com')
        user2 = self._create_user('test2@example.com')
        headers2 = self._get_auth_headers(user2)
        ws = self._create_workspace_via_api(user1, name="PrivateWS2", visibility="private")
        ws_id = ws["id"]
        file_content = b"x,y\n7,8\n"
        files = {"file": ("notowner.csv", io.BytesIO(file_content), "text/csv")}
        resp = self.client.post(f"/v1/workspaces/{ws_id}/files/", files=files, headers=headers2)
        assert resp.status_code == 404
        assert "not found" in resp.json()["error"].lower()

    def test_upload_non_csv_file(self):
        ws = self._create_workspace_via_api()
        ws_id = ws["id"]
        file_content = b"%PDF-1.4\n..."
        files = {"file": ("bad.pdf", io.BytesIO(file_content), "application/pdf")}
        resp = self.client.post(f"/v1/workspaces/{ws_id}/files/", files=files)
        assert resp.status_code == 400
        assert "csv" in resp.json()["error"].lower()

    def test_upload_csv_file_too_large(self, monkeypatch):
        # Patch settings before workspace creation
        monkeypatch.setattr(config.get_settings(), "orphaned_workspace_max_file_size", 10)
        ws = self._create_workspace_via_api()
        ws_id = ws["id"]
        file_content = b"col1,col2\n1,2\n3,4\n"
        files = {"file": ("big.csv", io.BytesIO(file_content), "text/csv")}
        resp = self.client.post(f"/v1/workspaces/{ws_id}/files/", files=files)
        assert resp.status_code == 400
        assert "exceeds max size" in resp.json()["error"].lower()
