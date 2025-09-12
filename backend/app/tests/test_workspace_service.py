import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from app.core.config import Settings
from app.models import User, Workspace
from app.schemas import WorkspaceCreate, WorkspaceUpdate
from app.services.exceptions import (
    FileMagicTypeNotAllowed,
    FileTooLarge,
    FileTypeNotAllowed,
    WorkspaceAlreadyClaimed,
    WorkspaceNotFound,
    WorkspaceQuotaExceeded,
)
from app.services.file_storage import FileStorage
from app.services.workspace_service import WorkspaceService


class TestWorkspaceService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.db = MagicMock()
        self.file_storage = MagicMock(spec=FileStorage)
        self.settings = MagicMock(spec=Settings)
        self.settings.owned_workspace_max_file_size = 1000
        self.settings.owned_workspace_max_storage = 10000
        self.settings.orphaned_workspace_max_file_size = 500
        self.settings.orphaned_workspace_max_storage = 5000
        self.service = WorkspaceService(self.db, self.file_storage, self.settings)
        self.user = MagicMock(spec=User)
        self.user.id = 1
        self.workspace = MagicMock(spec=Workspace)
        self.workspace.id = uuid.uuid4()
        self.workspace.owner_id = self.user.id
        self.workspace.is_public = False
        self.workspace.is_private = True
        self.workspace.is_orphaned = False
        self.workspace.max_file_size = 1000
        self.workspace.max_storage = 10000
        self.workspace.storage_used = 0
        self.workspace.visibility = "private"

    def test_create_workspace_owned(self):
        data = WorkspaceCreate(name="Test", visibility="private")
        ws = self.service.create_workspace(data, self.user)
        self.db.add.assert_called()
        self.db.commit.assert_called()
        self.db.refresh.assert_called()
        assert ws is not None

    def test_create_workspace_orphaned(self):
        data = WorkspaceCreate(name="Test", visibility="public")
        ws = self.service.create_workspace(data, None)
        self.db.add.assert_called()
        self.db.commit.assert_called()
        self.db.refresh.assert_called()
        assert ws is not None

    def test_update_workspace(self):
        data = WorkspaceUpdate(name="NewName", visibility="public")
        ws = self.service.update_workspace(self.workspace, data)
        self.db.commit.assert_called()
        self.db.refresh.assert_called()
        assert ws is not None

    def test_delete_workspace(self):
        self.service.delete_workspace(self.workspace)
        self.db.delete.assert_called_with(self.workspace)
        self.db.commit.assert_called()

    def test_claim_workspace(self):
        self.workspace.is_orphaned = True
        self.service.claim_workspace(self.workspace, self.user)
        self.db.commit.assert_called()

    def test_claim_workspace_already_claimed(self):
        self.workspace.is_orphaned = False
        with pytest.raises(WorkspaceAlreadyClaimed):
            self.service.claim_workspace(self.workspace, self.user)

    def test_upload_file_valid(self):
        self.workspace.storage_used = 0
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"col1,col2\n1,2"
        self.file_storage.save.return_value = "http://url"
        with patch("app.services.workspace_service.magic.from_buffer", return_value="text/csv"):
            with patch("app.services.workspace_service.uuid.uuid4", return_value=uuid.uuid4()):
                with patch("app.services.workspace_service.FileModel", autospec=True) as FileModelMock:
                    file_record = MagicMock()
                    FileModelMock.return_value = file_record
                    result = self.service.upload_file(self.workspace, file, self.user)
                    assert result == file_record
                    self.db.add.assert_called()
                    self.db.commit.assert_called()
                    self.db.refresh.assert_called()

    def test_upload_file_too_large(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"x" * 2000
        with pytest.raises(FileTooLarge):
            self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_storage_exceeded(self):
        self.workspace.storage_used = 10000
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"x" * 10
        with pytest.raises(WorkspaceQuotaExceeded):
            self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_type_not_allowed(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.txt"
        file.content_type = "text/plain"
        file.file = MagicMock()
        file.file.read.return_value = b"abc"
        with pytest.raises(FileTypeNotAllowed):
            self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_magic_type_not_allowed(self):
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"abc"
        with patch("app.services.workspace_service.magic.from_buffer", return_value="application/pdf"):
            with pytest.raises(FileMagicTypeNotAllowed):
                self.service.upload_file(self.workspace, file, self.user)

    def test_upload_file_permission_denied(self):
        self.workspace.is_private = True
        self.workspace.owner_id = 2  # not the user
        file = MagicMock(spec=UploadFile)
        file.filename = "test.csv"
        file.content_type = "text/csv"
        file.file = MagicMock()
        file.file.read.return_value = b"abc"
        with pytest.raises(WorkspaceNotFound):
            self.service.upload_file(self.workspace, file, self.user)

