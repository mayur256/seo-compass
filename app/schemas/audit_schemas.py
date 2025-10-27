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
    
    # DNS & Email Security
    spf_record: bool = False
    dmarc_record: bool = False
    mx_records: bool = False
    ipv6_support: bool = False
    has_verification: bool = False
    plaintext_emails: int = 0
    
    # Third-party API Metrics (Backlinks & Authority)
    domain_authority: int = 0
    page_authority: int = 0
    spam_score: int = 0
    linking_root_domains: int = 0
    total_backlinks: int = 0
    domain_rating: int = 0
    referring_domains: int = 0
    backlinks: int = 0
    organic_keywords: int = 0
    organic_traffic: int = 0
    organic_keywords_semrush: int = 0
    organic_traffic_semrush: int = 0
    organic_cost: float = 0.0
    adwords_keywords: int = 0
    adwords_traffic: int = 0
    adwords_cost: float = 0.0
    
    # Performance Monitoring APIs
    mobile_performance_score: int = 0
    mobile_accessibility_score: int = 0
    mobile_best_practices_score: int = 0
    mobile_seo_score: int = 0
    desktop_performance_score: int = 0
    desktop_accessibility_score: int = 0
    desktop_best_practices_score: int = 0
    desktop_seo_score: int = 0
    mobile_fcp: float = 0.0
    mobile_lcp: float = 0.0
    mobile_cls: float = 0.0
    desktop_fcp: float = 0.0
    desktop_lcp: float = 0.0
    desktop_cls: float = 0.0
    gtmetrix_grade: str = ""
    gtmetrix_performance_score: int = 0
    gtmetrix_structure_score: int = 0
    gtmetrix_page_load_time: float = 0.0
    gtmetrix_page_size: int = 0
    gtmetrix_requests: int = 0
    pingdom_response_time: float = 0.0
    pingdom_performance_grade: int = 0
    pingdom_page_size: int = 0
    pingdom_requests: int = 0
    wpt_load_time: float = 0.0
    wpt_first_byte: float = 0.0
    wpt_start_render: float = 0.0
    wpt_speed_index: float = 0.0
    wpt_bytes_in: int = 0
    wpt_requests: int = 0
    
    # Image Analysis & Optimization
    total_images: int = 0
    images_without_alt: int = 0
    images_without_title: int = 0
    oversized_images: int = 0
    unoptimized_formats: int = 0
    missing_lazy_loading: int = 0
    images_without_dimensions: int = 0
    broken_images: int = 0
    duplicate_alt_texts: int = 0
    ai_generated_alt_suggestions: int = 0
    compression_savings_kb: int = 0
    webp_conversion_candidates: int = 0
    
    # Keywords
    keyword_density: Dict[str, float] = {}
    most_common_keywords: List[str] = []
    
    # Files
    ads_txt_exists: bool = False
    custom_404_exists: bool = False