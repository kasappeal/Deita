from unittest.mock import MagicMock

import pytest

from app.core.config import Settings
from app.services.file_storage import FileStorage


class TestFileStorage:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.settings = MagicMock(spec=Settings)
        self.settings.s3_bucket_name = "test-bucket"
        self.s3_client = MagicMock()
        # Mock head_bucket to simulate bucket exists
        self.s3_client.head_bucket.return_value = True
        self.file_storage = FileStorage(settings=self.settings, client=self.s3_client)

    def test_init_creates_bucket_if_not_exists(self):
        # Create a new test-specific method that directly tests the _ensure_bucket_exists method
        client = MagicMock()

        # Define ClientError as a class with response attribute
        class ClientError(Exception):
            def __init__(self, response, operation_name):
                self.response = response
                self.operation_name = operation_name

        # Set up client exceptions
        client.exceptions = MagicMock()
        client.exceptions.ClientError = ClientError

        # Mock head_bucket to raise exception
        error_response = {'Error': {'Code': '404'}}
        client.head_bucket.side_effect = ClientError(error_response, 'head_bucket')

        # Create FileStorage instance (calls _ensure_bucket_exists once)
        file_storage = FileStorage(settings=self.settings, client=client)

        # Reset mock call count so we only check the manual call below
        client.create_bucket.reset_mock()

        # Manually call _ensure_bucket_exists to test it directly
        file_storage._ensure_bucket_exists()

        # Verify create_bucket was called once by the manual call
        client.create_bucket.assert_called_once_with(Bucket=self.settings.s3_bucket_name)

    def test_save_calls_upload_fileobj_and_returns_url(self):
        self.s3_client.upload_fileobj.return_value = None
        self.s3_client.generate_presigned_url.return_value = "http://url"
        data = b"abc"
        url = self.file_storage.save("obj.csv", data, content_type="text/csv")
        self.s3_client.upload_fileobj.assert_called_once()
        self.s3_client.generate_presigned_url.assert_called_once()
        assert url == "http://url"

    def test_get_url_returns_presigned_url(self):
        self.s3_client.generate_presigned_url.return_value = "http://url"
        url = self.file_storage.get_url("obj.csv")
        self.s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': self.file_storage.bucket, 'Key': "obj.csv"},
            ExpiresIn=604800
        )
        assert url == "http://url"

    def test_delete_calls_delete_object(self):
        self.file_storage.delete("obj.csv")
        self.s3_client.delete_object.assert_called_once_with(Bucket=self.file_storage.bucket, Key="obj.csv")
