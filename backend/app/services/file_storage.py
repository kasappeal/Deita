"""
FileStorage: Abstracts file storage backend (MinIO/S3/local).
"""
from minio import Minio

from app.core.config import Settings


class FileStorage:

    def __init__(self, settings: Settings, client: Minio):
        self.settings = settings
        self.client = client
        self.bucket = self.settings.s3_bucket_name
        # Ensure bucket exists
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def save(self, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Save file to storage and return the object URL."""
        from io import BytesIO
        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(data),
            length=len(data),
            content_type=content_type
        )
        return self.get_url(object_name)

    def get_url(self, object_name: str) -> str:
        """Return a presigned URL for the object."""
        return self.client.presigned_get_object(self.bucket, object_name)

    def delete(self, object_name: str):
        self.client.remove_object(self.bucket, object_name)
