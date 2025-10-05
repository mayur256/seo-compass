from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.domain.entities import AnalysisJob, Report, Competitor, Keyword, ContentDraft
from app.domain.types import JobStatus
from .base import AnalysisJobModel, CompetitorModel, KeywordModel, ContentDraftModel


class AnalysisRepository(ABC):
    @abstractmethod
    async def create_job(self, url: str) -> AnalysisJob:
        pass
    
    @abstractmethod
    async def get_job(self, job_id: UUID) -> Optional[AnalysisJob]:
        pass
    
    @abstractmethod
    async def update_status(self, job_id: UUID, status: JobStatus) -> None:
        pass
    
    @abstractmethod
    async def set_completed(self, job_id: UUID) -> None:
        pass
    
    @abstractmethod
    async def add_mock_data(self, job_id: UUID) -> None:
        pass
    
    @abstractmethod
    async def get_report(self, job_id: UUID) -> Optional[Report]:
        pass


class SQLAnalysisRepository(AnalysisRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_job(self, url: str) -> AnalysisJob:
        job_id = uuid4()
        created_at = datetime.utcnow()
        
        db_job = AnalysisJobModel(
            id=job_id,
            url=url,
            status="QUEUED",
            created_at=created_at
        )
        self.session.add(db_job)
        await self.session.commit()
        
        return AnalysisJob(
            id=job_id,
            url=url,
            status="QUEUED",
            created_at=created_at
        )
    
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
    
    async def update_status(self, job_id: UUID, status: JobStatus) -> None:
        await self.session.execute(
            update(AnalysisJobModel)
            .where(AnalysisJobModel.id == job_id)
            .values(status=status)
        )
        await self.session.commit()
    
    async def set_completed(self, job_id: UUID) -> None:
        await self.session.execute(
            update(AnalysisJobModel)
            .where(AnalysisJobModel.id == job_id)
            .values(status="COMPLETED", completed_at=func.now())
        )
        await self.session.commit()
    
    async def add_mock_data(self, job_id: UUID) -> None:
        # Add mock competitors
        competitors = [
            CompetitorModel(
                job_id=job_id,
                url="https://competitor1.com",
                title="Top Competitor 1",
                ranking_position=1,
                estimated_traffic=50000
            ),
            CompetitorModel(
                job_id=job_id,
                url="https://competitor2.com",
                title="Top Competitor 2",
                ranking_position=2,
                estimated_traffic=35000
            ),
            CompetitorModel(
                job_id=job_id,
                url="https://competitor3.com",
                title="Top Competitor 3",
                ranking_position=3,
                estimated_traffic=25000
            )
        ]
        
        # Add mock keywords
        keywords = [
            KeywordModel(
                job_id=job_id,
                term="business services",
                search_volume=10000,
                difficulty=0.6,
                cpc=2.50
            ),
            KeywordModel(
                job_id=job_id,
                term="professional consulting",
                search_volume=8000,
                difficulty=0.7,
                cpc=3.20
            ),
            KeywordModel(
                job_id=job_id,
                term="expert solutions",
                search_volume=5000,
                difficulty=0.5,
                cpc=1.80
            )
        ]
        
        # Add mock content drafts
        drafts = [
            ContentDraftModel(
                job_id=job_id,
                page_type="homepage",
                title="Welcome to Your Business",
                content="Professional homepage content optimized for your target keywords.",
                meta_description="Professional services for your business needs"
            ),
            ContentDraftModel(
                job_id=job_id,
                page_type="about",
                title="About Our Company",
                content="Learn more about our company and our mission to provide excellent services.",
                meta_description="Learn about our company history and values"
            ),
            ContentDraftModel(
                job_id=job_id,
                page_type="services",
                title="Our Services",
                content="We offer comprehensive services tailored to your business needs.",
                meta_description="Explore our range of professional services"
            )
        ]
        
        for item in competitors + keywords + drafts:
            self.session.add(item)
        
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
        
        if not competitors and not keywords and not content_drafts:
            return None
        
        return Report(
            job_id=job_id,
            competitors=competitors,
            keywords=keywords,
            content_drafts=content_drafts
        )