from typing import Optional
from uuid import UUID
from app.domain.entities import AnalysisJob, Report
from app.infrastructure.db.repositories import AnalysisRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class GetJobStatusUseCase:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def execute(self, job_id: UUID) -> Optional[AnalysisJob]:
        job = await self.repository.get_job(job_id)
        if job:
            logger.info(f"Retrieved job {job_id} with status: {job.status}")
        else:
            logger.warning(f"Job {job_id} not found")
        return job


class GetReportUseCase:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def execute(self, job_id: UUID) -> Optional[Report]:
        report = await self.repository.get_report(job_id)
        if report:
            logger.info(f"Retrieved report for job {job_id}")
        return report