from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class AuditRequest(BaseModel):
    url: HttpUrl


class SEOCheck(BaseModel):
    name: str
    status: str  # pass, fail, warning
    value: Optional[str] = None
    recommendation: Optional[str] = None


class SEOCategory(BaseModel):
    category: str
    checks: List[SEOCheck]


class SEOIssue(BaseModel):
    priority: str  # high, medium, low
    issue: str
    recommendation: str


class AuditResponse(BaseModel):
    audit_id: uuid.UUID
    status: str
    message: str


class AuditResult(BaseModel):
    url: str
    overall_score: int
    issues_to_fix: List[SEOIssue]
    common_issues: List[SEOCategory]


class ScrapedData(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = []
    h2_tags: List[str] = []
    h3_tags: List[str] = []
    canonical_tag: Optional[str] = None
    alt_missing_count: int = 0
    https: bool = False
    page_load_time: float = 0.0
    text_to_html_ratio: float = 0.0
    robots_txt_exists: bool = False
    sitemap_exists: bool = False