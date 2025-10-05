from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl
from app.domain.types import JobStatus


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class AnalyzeResponse(BaseModel):
    job_id: UUID
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: UUID
    url: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None


class CompetitorResponse(BaseModel):
    url: str
    title: str
    ranking_position: int
    estimated_traffic: Optional[int] = None


class KeywordResponse(BaseModel):
    term: str
    search_volume: int
    difficulty: float
    cpc: Optional[float] = None


class ContentDraftResponse(BaseModel):
    page_type: str
    title: str
    content: str
    meta_description: str


class ReportResponse(BaseModel):
    job_id: UUID
    competitors: list[CompetitorResponse]
    keywords: list[KeywordResponse]
    content_drafts: list[ContentDraftResponse]