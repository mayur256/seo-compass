import uuid
from datetime import datetime
from app.domain.entities import AnalysisJob
from app.infrastructure.db.repositories import AnalysisRepository
from app.tasks.tasks import process_analysis


class SubmitAnalysisUseCase:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def execute(self, url: str) -> uuid.UUID:
        job_id = uuid.uuid4()
        job = AnalysisJob(
            id=job_id,
            url=url,
            status="QUEUED",
            created_at=datetime.utcnow()
        )
        
        await self.repository.create_job(job)
        
        # Enqueue Celery task
        process_analysis.delay(str(job_id), url)
        
        return job_id