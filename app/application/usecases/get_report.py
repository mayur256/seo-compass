from typing import Optional
from uuid import UUID
from app.domain.entities import AnalysisJob, Report
from app.infrastructure.db.repositories import AnalysisRepository


class GetJobStatusUseCase:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def execute(self, job_id: UUID) -> Optional[AnalysisJob]:
        return await self.repository.get_job(job_id)


class GetReportUseCase:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def execute(self, job_id: UUID) -> Optional[Report]:
        return await self.repository.get_report(job_id)