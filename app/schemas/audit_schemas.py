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
    # Basic SEO
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = []
    h2_tags: List[str] = []
    h3_tags: List[str] = []
    h4_tags: List[str] = []
    h5_tags: List[str] = []
    h6_tags: List[str] = []
    canonical_tag: Optional[str] = None
    alt_missing_count: int = 0
    https: bool = False
    page_load_time: float = 0.0
    text_to_html_ratio: float = 0.0
    robots_txt_exists: bool = False
    sitemap_exists: bool = False
    
    # Meta tags
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_card: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    
    # Technical
    charset: Optional[str] = None
    viewport_tag: bool = False
    favicon_exists: bool = False
    noindex: bool = False
    nofollow: bool = False
    meta_refresh: Optional[str] = None
    structured_data_count: int = 0
    deprecated_tags_count: int = 0
    
    # Performance
    html_size: int = 0
    dom_size: int = 0
    http_requests: int = 0
    gzip_enabled: bool = False
    js_minified: bool = False
    css_minified: bool = False
    webp_images: int = 0
    http2_enabled: bool = False
    cdn_detected: bool = False
    media_queries: int = 0
    render_blocking: int = 0
    js_execution_time: float = 0.0
    
    # Core Web Vitals
    fcp: float = 0.0  # First Contentful Paint
    lcp: float = 0.0  # Largest Contentful Paint
    cls: float = 0.0  # Cumulative Layout Shift
    ttfb: float = 0.0  # Time To First Byte
    
    # Security
    ssl_valid: bool = False
    hsts_header: bool = False
    mixed_content_count: int = 0
    unsafe_links_count: int = 0
    
    # Keywords
    keyword_density: Dict[str, float] = {}
    most_common_keywords: List[str] = []
    
    # Files
    ads_txt_exists: bool = False
    custom_404_exists: bool = False