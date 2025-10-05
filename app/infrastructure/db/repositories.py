from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities import AnalysisJob, Report, Competitor, Keyword, ContentDraft
from app.domain.types import JobStatus
from .base import AnalysisJobModel, CompetitorModel, KeywordModel, ContentDraftModel


class AnalysisRepository(ABC):
    @abstractmethod
    async def create_job(self, job: AnalysisJob) -> None:
        pass
    
    @abstractmethod
    async def get_job(self, job_id: UUID) -> Optional[AnalysisJob]:
        pass
    
    @abstractmethod
    async def update_job_status(self, job_id: UUID, status: JobStatus) -> None:
        pass
    
    @abstractmethod
    async def save_report(self, report: Report) -> None:
        pass
    
    @abstractmethod
    async def get_report(self, job_id: UUID) -> Optional[Report]:
        pass


class SQLAnalysisRepository(AnalysisRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_job(self, job: AnalysisJob) -> None:
        db_job = AnalysisJobModel(
            id=job.id,
            url=job.url,
            status=job.status,
            created_at=job.created_at,
            completed_at=job.completed_at
        )
        self.session.add(db_job)
        await self.session.commit()
    
    async def get_job(self, job_id: UUID) -> Optional[AnalysisJob]:
        result = await self.session.execute(
            select(AnalysisJobModel).where(AnalysisJobModel.id == job_id)
        )
        db_job = result.scalar_one_or_none()
        if not db_job:
            return None
        
        return AnalysisJob(
            id=db_job.id,
            url=db_job.url,
            status=db_job.status,  # type: ignore
            created_at=db_job.created_at,
            completed_at=db_job.completed_at
        )
    
    async def update_job_status(self, job_id: UUID, status: JobStatus) -> None:
        await self.session.execute(
            update(AnalysisJobModel)
            .where(AnalysisJobModel.id == job_id)
            .values(status=status)
        )
        await self.session.commit()
    
    async def save_report(self, report: Report) -> None:
        # Save competitors
        for competitor in report.competitors:
            db_competitor = CompetitorModel(
                job_id=report.job_id,
                url=competitor.url,
                title=competitor.title,
                ranking_position=competitor.ranking_position,
                estimated_traffic=competitor.estimated_traffic
            )
            self.session.add(db_competitor)
        
        # Save keywords
        for keyword in report.keywords:
            db_keyword = KeywordModel(
                job_id=report.job_id,
                term=keyword.term,
                search_volume=keyword.search_volume,
                difficulty=keyword.difficulty,
                cpc=keyword.cpc
            )
            self.session.add(db_keyword)
        
        # Save content drafts
        for draft in report.content_drafts:
            db_draft = ContentDraftModel(
                job_id=report.job_id,
                page_type=draft.page_type,
                title=draft.title,
                content=draft.content,
                meta_description=draft.meta_description
            )
            self.session.add(db_draft)
        
        await self.session.commit()
    
    async def get_report(self, job_id: UUID) -> Optional[Report]:
        # Get competitors
        competitors_result = await self.session.execute(
            select(CompetitorModel).where(CompetitorModel.job_id == job_id)
        )
        competitors = [
            Competitor(
                url=c.url,
                title=c.title,
                ranking_position=c.ranking_position,
                estimated_traffic=c.estimated_traffic
            )
            for c in competitors_result.scalars().all()
        ]
        
        # Get keywords
        keywords_result = await self.session.execute(
            select(KeywordModel).where(KeywordModel.job_id == job_id)
        )
        keywords = [
            Keyword(
                term=k.term,
                search_volume=k.search_volume,
                difficulty=k.difficulty,
                cpc=k.cpc
            )
            for k in keywords_result.scalars().all()
        ]
        
        # Get content drafts
        drafts_result = await self.session.execute(
            select(ContentDraftModel).where(ContentDraftModel.job_id == job_id)
        )
        content_drafts = [
            ContentDraft(
                page_type=d.page_type,
                title=d.title,
                content=d.content,
                meta_description=d.meta_description
            )
            for d in drafts_result.scalars().all()
        ]
        
        if not competitors and not keywords and not content_drafts:
            return None
        
        return Report(
            job_id=job_id,
            competitors=competitors,
            keywords=keywords,
            content_drafts=content_drafts
        )