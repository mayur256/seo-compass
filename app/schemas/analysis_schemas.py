"""Analysis-specific schemas for API responses."""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.services.competitor_service import CompetitorData
from app.services.keyword_service import KeywordData
from app.services.llm_service import PageDraft


class CompetitorResponse(BaseModel):
    """Response schema for competitor data."""
    competitors: List[CompetitorData]


class KeywordResponse(BaseModel):
    """Response schema for keyword data."""
    keywords: List[KeywordData]


class ContentDraftResponse(BaseModel):
    """Response schema for content drafts."""
    drafts: List[PageDraft]


class PartialAnalysisResponse(BaseModel):
    """Response schema for partial analysis results."""
    job_id: UUID
    section: Optional[str] = None
    competitors: Optional[List[CompetitorData]] = None
    keywords: Optional[List[KeywordData]] = None
    content_drafts: Optional[List[PageDraft]] = None


class AnalysisProgressResponse(BaseModel):
    """Response schema for analysis progress."""
    job_id: UUID
    status: str
    progress: dict
    completed_steps: List[str]
    current_step: Optional[str] = None
    estimated_completion: Optional[str] = None