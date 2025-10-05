from typing import AsyncGenerator
from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


class AnalysisJobModel(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class CompetitorModel(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    ranking_position = Column(Integer, nullable=False)
    estimated_traffic = Column(Integer, nullable=True)


class KeywordModel(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    term = Column(String, nullable=False)
    search_volume = Column(Integer, nullable=False)
    difficulty = Column(Float, nullable=False)
    cpc = Column(Float, nullable=True)


class ContentDraftModel(Base):
    __tablename__ = "content_drafts"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    page_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    meta_description = Column(String, nullable=False)


engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()