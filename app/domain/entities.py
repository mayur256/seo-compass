from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from .types import JobStatus


@dataclass
class AnalysisJob:
    id: UUID
    url: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None


@dataclass
class Competitor:
    url: str
    title: str
    ranking_position: int
    estimated_traffic: Optional[int] = None


@dataclass
class Keyword:
    term: str
    search_volume: int
    difficulty: float
    cpc: Optional[float] = None


@dataclass
class ContentDraft:
    page_type: str  # "homepage", "about", "services"
    title: str
    content: str
    meta_description: str


@dataclass
class Report:
    job_id: UUID
    competitors: list[Competitor]
    keywords: list[Keyword]
    content_drafts: list[ContentDraft]