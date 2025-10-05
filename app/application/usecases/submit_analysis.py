from uuid import UUID
from urllib.parse import urlparse
from app.infrastructure.db.repositories import AnalysisRepository
from app.tasks.tasks import process_analysis
from app.core.logging import get_logger

logger = get_logger(__name__)


class SubmitAnalysisUseCase:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def execute(self, url: str) -> tuple[UUID, str]:
        # Validate URL
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid URL format")
        
        # Create job in database
        job = await self.repository.create_job(url)
        logger.info(f"Created analysis job {job.id} for URL: {url}")
        
        # Enqueue Celery task
        process_analysis.delay(str(job.id), url)
        logger.info(f"Enqueued analysis task for job {job.id}")
        
        return job.id, job.status