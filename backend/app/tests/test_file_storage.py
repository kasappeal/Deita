from unittest.mock import MagicMock

import pytest
from minio import Minio

from app.core.config import Settings
from app.services.file_storage import FileStorage


class TestFileStorage:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.settings = MagicMock(spec=Settings)
        self.settings.s3_bucket_name = "test-bucket"
        self.minio_client = MagicMock(spec=Minio)
        self.minio_client.bucket_exists.return_value = True
        self.file_storage = FileStorage(settings=self.settings, client=self.minio_client)

    def test_init_creates_bucket_if_not_exists(self):
        client = MagicMock(spec=Minio)
        client.bucket_exists.return_value = False
        FileStorage(settings=self.settings, client=client)
        client.make_bucket.assert_called_once_with(self.settings.s3_bucket_name)

    def test_save_calls_put_object_and_returns_url(self):
        self.minio_client.put_object.return_value = None
        self.minio_client.presigned_get_object.return_value = "http://url"
        data = b"abc"
        url = self.file_storage.save("obj.csv", data, content_type="text/csv")
        self.minio_client.put_object.assert_called_once()
        self.minio_client.presigned_get_object.assert_called_once_with(self.file_storage.bucket, "obj.csv")
        assert url == "http://url"

    def test_get_url_returns_presigned_url(self):
        self.minio_client.presigned_get_object.return_value = "http://url"
        url = self.file_storage.get_url("obj.csv")
        self.minio_client.presigned_get_object.assert_called_once_with(self.file_storage.bucket, "obj.csv")
        assert url == "http://url"

    def test_delete_calls_remove_object(self):
        self.file_storage.delete("obj.csv")
        self.minio_client.remove_object.assert_called_once_with(self.file_storage.bucket, "obj.csv")
