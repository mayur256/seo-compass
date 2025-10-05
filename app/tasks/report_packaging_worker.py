"""Celery worker for background report packaging."""

import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.infrastructure.db.base import AsyncSessionLocal
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.infrastructure.db.report_repository import ReportRepository
from app.infrastructure.s3_storage import S3StorageService
from app.services.report_service import ReportService
from app.core.logging import get_logger
from app.core.events import ReportEvent

logger = get_logger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def package_report_task(self, job_id: str, version_id: str) -> None:
    """Package and upload report to S3."""
    try:
        asyncio.run(_package_report_async(UUID(job_id), UUID(version_id)))
    except Exception as e:
        logger.error(f"Report packaging failed for job {job_id}: {e}")
        raise


async def _package_report_async(job_id: UUID, version_id: UUID) -> None:
    """Async implementation of report packaging."""
    logger.info({
        "event": ReportEvent.PACKAGING_STARTED,
        "job_id": str(job_id),
        "version_id": str(version_id)
    })
    
    async with AsyncSessionLocal() as session:
        analysis_repo = SQLAnalysisRepository(session)
        report_repo = ReportRepository(session)
        report_service = ReportService(analysis_repo)
        s3_service = S3StorageService()
        
        try:
            # Update status to PACKAGING
            await report_repo.update_status(version_id, "PACKAGING")
            
            # Get report version details
            version = await report_repo.get_by_job_id(job_id)
            if not version:
                raise ValueError(f"Report version not found for job {job_id}")
            
            # Build report model
            report = await report_service.build_report_model(job_id)
            
            # Generate ZIP file
            zip_bytes = await report_service.generate_files(report)
            
            # Update status to UPLOADING
            await report_repo.update_status(version_id, "UPLOADING")
            
            # Upload to S3
            s3_key = await s3_service.upload_report_zip(
                zip_bytes, 
                version.url, 
                str(job_id), 
                version.version
            )
            
            # Update version with S3 path and mark completed
            await report_repo.update_s3_path(version_id, s3_key)
            await report_repo.update_status(version_id, "COMPLETED")
            
            logger.info({
                "event": ReportEvent.PACKAGING_COMPLETED,
                "job_id": str(job_id),
                "version_id": str(version_id),
                "s3_key": s3_key
            })
            
        except Exception as e:
            # Mark as failed
            await report_repo.update_status(version_id, "FAILED")
            logger.error({
                "event": "packaging_failed",
                "job_id": str(job_id),
                "version_id": str(version_id),
                "error": str(e)
            })
            raise