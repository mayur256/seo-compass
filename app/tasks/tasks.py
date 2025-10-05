import asyncio
import time
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.infrastructure.db.base import AsyncSessionLocal
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task
def process_analysis(job_id: str, url: str) -> None:
    """Process SEO analysis for a given URL."""
    asyncio.run(_process_analysis_async(UUID(job_id), url))


async def _process_analysis_async(job_id: UUID, url: str) -> None:
    """Async implementation of analysis processing."""
    logger.info(f"Starting analysis for job {job_id}, URL: {url}")
    
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        try:
            # Update job status to IN_PROGRESS
            await repository.update_status(job_id, "IN_PROGRESS")
            logger.info(f"Job {job_id} status updated to IN_PROGRESS")
            
            # Simulate processing time (3 seconds)
            time.sleep(3)
            logger.info(f"Processing simulation completed for job {job_id}")
            
            # Add mock data to database
            await repository.add_mock_data(job_id)
            logger.info(f"Mock data added for job {job_id}")
            
            # Mark job as completed
            await repository.set_completed(job_id)
            logger.info(f"Analysis completed for job {job_id}")
                
        except Exception as e:
            logger.error(f"Analysis failed for job {job_id}: {str(e)}")
            await repository.update_status(job_id, "FAILED")
            raise