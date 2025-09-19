"""
FileStorage: Abstracts file storage backend (AWS S3/local).
"""
from io import BytesIO

import boto3
from botocore.client import Config

from app.core.config import Settings


class FileStorage:

    def __init__(self, settings: Settings, client=None):
        self.settings = settings
        self.bucket = self.settings.s3_bucket_name

        if client:
            self.client = client
        else:
            # Create boto3 client from settings
            self.client = boto3.client(
                's3',
                endpoint_url=self.settings.s3_endpoint,
                aws_access_key_id=self.settings.s3_access_key,
                aws_secret_access_key=self.settings.s3_secret_key,
                config=Config(signature_version='s3v4'),
                # Set verify to False if using a local endpoint without proper SSL
                verify=self.settings.s3_endpoint.startswith('https://')
            )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception as e:
            # Only create if not found
            error_code = getattr(getattr(e, 'response', {}), 'get', lambda x, default=None: default)('Error', {}).get('Code') if hasattr(e, 'response') else None
            if error_code == '404' or 'Not Found' in str(e):
                self.client.create_bucket(Bucket=self.bucket)
            elif hasattr(self.client, 'exceptions') and hasattr(self.client.exceptions, 'ClientError') and isinstance(e, self.client.exceptions.ClientError):
                if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') == '404':
                    self.client.create_bucket(Bucket=self.bucket)
                else:
                    raise
            else:
                raise

    def save(self, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Save file to storage and return a presigned URL."""
        self.client.upload_fileobj(
            BytesIO(data),
            self.bucket,
            object_name,
            ExtraArgs={"ContentType": content_type}
        )
        # Return presigned URL for the uploaded object
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': object_name},
            ExpiresIn=604800  # 7 days
        )

    def get_url(self, object_name: str) -> str:
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': object_name},
            ExpiresIn=604800  # 7 days
        )

    def get_presigned_url(self, object_name: str) -> str:
        """Return a presigned URL for the object."""
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': object_name},
            ExpiresIn=60 * 10  # 10 minutes in seconds
        )

    def delete(self, object_name: str):
        self.client.delete_object(Bucket=self.bucket, Key=object_name)
