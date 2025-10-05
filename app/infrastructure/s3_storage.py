"""Amazon S3 storage integration for report files."""

import asyncio
import hashlib
from typing import Optional
import aioboto3
from botocore.exceptions import ClientError
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.events import ReportEvent

settings = get_settings()
logger = get_logger(__name__)


class S3StorageService:
    """Service for S3 file operations."""
    
    def __init__(self):
        self.bucket_name = getattr(settings, 's3_bucket_name', 'seo-compass-reports')
        self.region = getattr(settings, 'aws_region', 'us-east-1')
    
    def _get_s3_key(self, url: str, job_id: str, version: int) -> str:
        """Generate S3 key for report file."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{url_hash}/{job_id}_{version}.zip"
    
    async def upload_report_zip(
        self, 
        zip_data: bytes, 
        url: str, 
        job_id: str, 
        version: int
    ) -> str:
        """Upload ZIP file to S3 with retry logic."""
        s3_key = self._get_s3_key(url, job_id, version)
        
        for attempt in range(3):
            try:
                session = aioboto3.Session()
                async with session.client('s3', region_name=self.region) as s3:
                    await s3.put_object(
                        Bucket=self.bucket_name,
                        Key=s3_key,
                        Body=zip_data,
                        ContentType='application/zip',
                        Metadata={
                            'job_id': job_id,
                            'version': str(version),
                            'url': url
                        }
                    )
                
                logger.info({
                    "event": ReportEvent.UPLOAD_SUCCESS,
                    "job_id": job_id,
                    "version": version,
                    "s3_key": s3_key,
                    "size_bytes": len(zip_data)
                })
                
                return s3_key
                
            except ClientError as e:
                wait_time = 2 ** attempt
                logger.warning(f"S3 upload attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s")
                if attempt < 2:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error({
                        "event": ReportEvent.UPLOAD_FAILED,
                        "job_id": job_id,
                        "version": version,
                        "error": str(e)
                    })
                    raise
    
    async def get_presigned_url(
        self, 
        s3_key: str, 
        expires_in: int = 604800
    ) -> str:
        """Generate presigned URL for S3 object (default 7 days)."""
        try:
            session = aioboto3.Session()
            async with session.client('s3', region_name=self.region) as s3:
                url = await s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expires_in
                )
            
            logger.info({
                "event": ReportEvent.PRESIGNED_URL_GENERATED,
                "s3_key": s3_key,
                "expires_in": expires_in
            })
            
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            raise
    
    async def delete_object(self, s3_key: str) -> None:
        """Delete object from S3."""
        try:
            session = aioboto3.Session()
            async with session.client('s3', region_name=self.region) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            logger.info(f"Deleted S3 object: {s3_key}")
            
        except ClientError as e:
            logger.error(f"Failed to delete S3 object {s3_key}: {e}")
            raise