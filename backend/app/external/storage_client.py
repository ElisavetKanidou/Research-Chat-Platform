"""
Storage Client (app/external/storage_client.py)
"""
import boto3
from typing import Optional, BinaryIO
import logging
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)


class StorageClient:
    """Cloud storage client (AWS S3 compatible)"""

    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.AWS_S3_BUCKET
        else:
            self.s3_client = None
            logger.warning("AWS credentials not configured, using local storage")

    async def upload_file(
            self,
            file_content: bytes,
            file_key: str,
            content_type: str = "application/octet-stream",
            metadata: Optional[dict] = None
    ) -> str:
        """Upload file to cloud storage"""

        if not self.s3_client:
            # Fallback to local storage
            return self._save_to_local(file_content, file_key)

        try:
            extra_args = {
                'ContentType': content_type,
                'Metadata': metadata or {}
            }

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                **extra_args
            )

            # Return public URL
            return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise ExternalServiceException("S3", f"Upload failed: {str(e)}")

    async def download_file(self, file_key: str) -> bytes:
        """Download file from cloud storage"""

        if not self.s3_client:
            return self._load_from_local(file_key)

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()

        except Exception as e:
            logger.error(f"Failed to download from S3: {e}")
            raise ExternalServiceException("S3", f"Download failed: {str(e)}")

    async def delete_file(self, file_key: str) -> bool:
        """Delete file from cloud storage"""

        if not self.s3_client:
            return self._delete_from_local(file_key)

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True

        except Exception as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False

    async def generate_presigned_url(
            self,
            file_key: str,
            expiration: int = 3600,
            method: str = "get_object"
    ) -> str:
        """Generate presigned URL for direct access"""

        if not self.s3_client:
            # Return local file URL
            return f"/files/{file_key}"

        try:
            url = self.s3_client.generate_presigned_url(
                method,
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url

        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise ExternalServiceException("S3", f"Presigned URL generation failed: {str(e)}")

    def _save_to_local(self, file_content: bytes, file_key: str) -> str:
        """Save file to local storage as fallback"""
        local_path = Path("uploads") / file_key
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(file_content)

        return f"/uploads/{file_key}"

    def _load_from_local(self, file_key: str) -> bytes:
        """Load file from local storage"""
        local_path = Path("uploads") / file_key

        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {file_key}")

        with open(local_path, 'rb') as f:
            return f.read()

    def _delete_from_local(self, file_key: str) -> bool:
        """Delete file from local storage"""
        local_path = Path("uploads") / file_key

        try:
            if local_path.exists():
                local_path.unlink()
            return True
        except Exception:
            return False


# Create client instance
storage_client = StorageClient()
