"""Report-specific Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class CompetitorOut(BaseModel):
    """Competitor output schema."""
    rank: int
    url: str
    keyword: str
    estimated_traffic: int


class KeywordOut(BaseModel):
    """Keyword output schema."""
    keyword: str
    search_volume: int
    difficulty: float
    cpc: Optional[float] = None


class DraftOut(BaseModel):
    """Content draft output schema."""
    page_name: str
    content: str


class ReportModel(BaseModel):
    """Complete report model."""
    job_id: UUID
    url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    competitors: List[CompetitorOut]
    keywords: List[KeywordOut]
    drafts: List[DraftOut]


class ReportResponse(BaseModel):
    """API response for report endpoint."""
    job_id: UUID
    url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    competitors: Optional[List[CompetitorOut]] = None
    keywords: Optional[List[KeywordOut]] = None
    drafts: Optional[List[DraftOut]] = None


class ReportVersionOut(BaseModel):
    """Report version output schema."""
    id: UUID
    job_id: UUID
    version: int
    url: str
    status: str
    s3_zip_url: Optional[str] = None
    created_at: Optional[datetime]
    completed_at: Optional[datetime]


class ReportHistoryOut(BaseModel):
    """Report history response schema."""
    data: List[ReportVersionOut]
    pagination: dict


class PackagingStatusOut(BaseModel):
    """Packaging status response schema."""
    job_id: UUID
    version_id: UUID
    status: str
    progress: int