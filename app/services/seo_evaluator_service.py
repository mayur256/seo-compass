from typing import List, Dict
from app.schemas.audit_schemas import ScrapedData, SEOCheck, SEOCategory, SEOIssue


class SEOEvaluatorService:
    def __init__(self):
        self.seo_checks = self._define_comprehensive_seo_checks()

    def _define_comprehensive_seo_checks(self) -> List[Dict]:
        return [
            # On-Page SEO
            {
                "name": "Meta Title Tag",
                "category": "On-Page SEO",
                "priority": "high",
                "evaluate": lambda data: bool(data.title) and 30 <= len(data.title) <= 60,
                "get_value": lambda data: f"Length: {len(data.title)} chars" if data.title else "Missing",
                "recommendation": "Add a descriptive title tag (30-60 characters)."
            },
            {
                "name": "Meta Description Tag",
                "category": "On-Page SEO",
                "priority": "high",
                "evaluate": lambda data: bool(data.meta_description) and 120 <= len(data.meta_description) <= 160,
                "get_value": lambda data: f"Length: {len(data.meta_description)} chars" if data.meta_description else "Missing",
                "recommendation": "Add a meta description (120-160 characters)."
            },
            {
                "name": "H1 Tag Usage",
                "category": "On-Page SEO",
                "priority": "high",
                "evaluate": lambda data: len(data.h1_tags) == 1,
                "get_value": lambda data: f"Count: {len(data.h1_tags)}",
                "recommendation": "Use exactly one H1 tag per page."
            },
            {
                "name": "Heading Structure (H1-H6)",
                "category": "On-Page SEO",
                "priority": "medium",
                "evaluate": lambda data: len(data.h1_tags) + len(data.h2_tags) + len(data.h3_tags) > 0,
                "get_value": lambda data: f"H1:{len(data.h1_tags)} H2:{len(data.h2_tags)} H3:{len(data.h3_tags)}",
                "recommendation": "Use proper heading hierarchy (H1-H6) for content structure."
            },
            {
                "name": "Image Alt Attributes",
                "category": "On-Page SEO",
                "priority": "medium",
                "evaluate": lambda data: data.alt_missing_count == 0,
                "get_value": lambda data: f"Missing: {data.alt_missing_count}",
                "recommendation": "Add alt attributes to all images for accessibility and SEO."
            },
            {
                "name": "Keyword Density",
                "category": "On-Page SEO",
                "priority": "medium",
                "evaluate": lambda data: len(data.most_common_keywords) > 0,
                "get_value": lambda data: f"Keywords found: {len(data.most_common_keywords)}",
                "recommendation": "Optimize keyword usage and density (2-3% recommended)."
            },
            
            # Technical SEO
            {
                "name": "HTTPS Implementation",
                "category": "Technical SEO",
                "priority": "high",
                "evaluate": lambda data: data.https and data.ssl_valid,
                "get_value": lambda data: "Valid SSL" if data.https and data.ssl_valid else "Missing/Invalid",
                "recommendation": "Implement valid HTTPS with proper SSL certificate."
            },
            {
                "name": "Canonical Tag",
                "category": "Technical SEO",
                "priority": "high",
                "evaluate": lambda data: bool(data.canonical_tag),
                "get_value": lambda data: "Present" if data.canonical_tag else "Missing",
                "recommendation": "Add canonical tag to prevent duplicate content issues."
            },
            {
                "name": "Robots.txt File",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: data.robots_txt_exists,
                "get_value": lambda data: "Found" if data.robots_txt_exists else "Missing",
                "recommendation": "Create robots.txt file to guide search engine crawling."
            },
            {
                "name": "XML Sitemap",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: data.sitemap_exists,
                "get_value": lambda data: "Found" if data.sitemap_exists else "Missing",
                "recommendation": "Create XML sitemap to help search engines index your site."
            },
            {
                "name": "Charset Declaration",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: bool(data.charset),
                "get_value": lambda data: data.charset or "Missing",
                "recommendation": "Declare character encoding (UTF-8 recommended)."
            },
            {
                "name": "Favicon Presence",
                "category": "Technical SEO",
                "priority": "low",
                "evaluate": lambda data: data.favicon_exists,
                "get_value": lambda data: "Present" if data.favicon_exists else "Missing",
                "recommendation": "Add favicon for better user experience and branding."
            },
            {
                "name": "Noindex Meta Tag",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: not data.noindex,
                "get_value": lambda data: "Present (blocking indexing)" if data.noindex else "Not present",
                "recommendation": "Remove noindex tag if you want the page indexed."
            },
            {
                "name": "Structured Data",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: data.structured_data_count > 0,
                "get_value": lambda data: f"Count: {data.structured_data_count}",
                "recommendation": "Add structured data (Schema.org) for rich snippets."
            },
            {
                "name": "Deprecated HTML Tags",
                "category": "Technical SEO",
                "priority": "low",
                "evaluate": lambda data: data.deprecated_tags_count == 0,
                "get_value": lambda data: f"Count: {data.deprecated_tags_count}",
                "recommendation": "Remove deprecated HTML tags for modern standards compliance."
            },
            
            # Social Media Meta Tags
            {
                "name": "Open Graph Meta Tags",
                "category": "Social Media SEO",
                "priority": "medium",
                "evaluate": lambda data: bool(data.og_title) and bool(data.og_description),
                "get_value": lambda data: "Complete" if data.og_title and data.og_description else "Incomplete",
                "recommendation": "Add Open Graph tags for better social media sharing."
            },
            {
                "name": "Twitter Card Meta Tags",
                "category": "Social Media SEO",
                "priority": "medium",
                "evaluate": lambda data: bool(data.twitter_card),
                "get_value": lambda data: data.twitter_card or "Missing",
                "recommendation": "Add Twitter Card tags for optimized Twitter sharing."
            },
            
            # Performance & Speed
            {
                "name": "Page Load Time",
                "category": "Performance",
                "priority": "high",
                "evaluate": lambda data: data.page_load_time < 3.0,
                "get_value": lambda data: f"{data.page_load_time:.2f}s",
                "recommendation": "Optimize page load time to under 3 seconds."
            },
            {
                "name": "HTML Page Size",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.html_size < 100000,  # 100KB
                "get_value": lambda data: f"{data.html_size / 1024:.1f}KB",
                "recommendation": "Keep HTML size under 100KB for faster loading."
            },
            {
                "name": "DOM Size",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.dom_size < 1500,
                "get_value": lambda data: f"{data.dom_size} nodes",
                "recommendation": "Keep DOM size under 1500 nodes for better performance."
            },
            {
                "name": "HTTP Requests",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.http_requests < 50,
                "get_value": lambda data: f"{data.http_requests} requests",
                "recommendation": "Minimize HTTP requests (under 50 recommended)."
            },
            {
                "name": "GZIP Compression",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.gzip_enabled,
                "get_value": lambda data: "Enabled" if data.gzip_enabled else "Disabled",
                "recommendation": "Enable GZIP compression to reduce file sizes."
            },
            
            # Security
            {
                "name": "HSTS Header",
                "category": "Security",
                "priority": "medium",
                "evaluate": lambda data: data.hsts_header,
                "get_value": lambda data: "Present" if data.hsts_header else "Missing",
                "recommendation": "Add HSTS header for enhanced security."
            },
            {
                "name": "Mixed Content Check",
                "category": "Security",
                "priority": "high",
                "evaluate": lambda data: data.mixed_content_count == 0,
                "get_value": lambda data: f"Issues: {data.mixed_content_count}",
                "recommendation": "Fix mixed content issues (HTTP resources on HTTPS pages)."
            },
            {
                "name": "Unsafe Cross-Origin Links",
                "category": "Security",
                "priority": "medium",
                "evaluate": lambda data: data.unsafe_links_count == 0,
                "get_value": lambda data: f"Unsafe links: {data.unsafe_links_count}",
                "recommendation": "Add rel='noopener noreferrer' to external links with target='_blank'."
            },
            
            # Mobile Usability
            {
                "name": "Meta Viewport Tag",
                "category": "Mobile Usability",
                "priority": "high",
                "evaluate": lambda data: data.viewport_tag,
                "get_value": lambda data: "Present" if data.viewport_tag else "Missing",
                "recommendation": "Add viewport meta tag for mobile responsiveness."
            },
            
            # Additional Files
            {
                "name": "Custom 404 Error Page",
                "category": "User Experience",
                "priority": "medium",
                "evaluate": lambda data: data.custom_404_exists,
                "get_value": lambda data: "Present" if data.custom_404_exists else "Missing",
                "recommendation": "Create custom 404 error page for better user experience."
            },
            {
                "name": "Ads.txt File",
                "category": "Monetization",
                "priority": "low",
                "evaluate": lambda data: data.ads_txt_exists,
                "get_value": lambda data: "Present" if data.ads_txt_exists else "Missing",
                "recommendation": "Add ads.txt file if using programmatic advertising."
            },
            {
                "name": "Time To First Byte (TTFB)",
                "category": "Core Web Vitals",
                "priority": "high",
                "evaluate": lambda data: data.page_load_time < 0.8,
                "get_value": lambda data: f"{data.page_load_time:.3f}s",
                "recommendation": "Optimize TTFB to under 800ms."
            },
            {
                "name": "JavaScript Minification",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.js_minified,
                "get_value": lambda data: "Minified" if data.js_minified else "Not minified",
                "recommendation": "Minify JavaScript files."
            },
            {
                "name": "CSS Minification",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.css_minified,
                "get_value": lambda data: "Minified" if data.css_minified else "Not minified",
                "recommendation": "Minify CSS files."
            },
            {
                "name": "Modern Image Formats",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.webp_images > 0,
                "get_value": lambda data: f"WebP: {data.webp_images}",
                "recommendation": "Use WebP format for images."
            },
            {
                "name": "First Contentful Paint (FCP)",
                "category": "Core Web Vitals",
                "priority": "high",
                "evaluate": lambda data: data.fcp < 1.8,
                "get_value": lambda data: f"{data.fcp:.2f}s",
                "recommendation": "Optimize FCP to under 1.8 seconds."
            },
            {
                "name": "Cumulative Layout Shift (CLS)",
                "category": "Core Web Vitals",
                "priority": "high",
                "evaluate": lambda data: data.cls < 0.1,
                "get_value": lambda data: f"{data.cls:.3f}",
                "recommendation": "Keep CLS under 0.1 for good user experience."
            },
            {
                "name": "Render-Blocking Resources",
                "category": "Performance",
                "priority": "high",
                "evaluate": lambda data: data.render_blocking < 5,
                "get_value": lambda data: f"{data.render_blocking} resources",
                "recommendation": "Minimize render-blocking CSS and JavaScript."
            },
            {
                "name": "JavaScript Execution Time",
                "category": "Performance",
                "priority": "medium",
                "evaluate": lambda data: data.js_execution_time < 2.0,
                "get_value": lambda data: f"{data.js_execution_time:.2f}s",
                "recommendation": "Optimize JavaScript execution time."
            }
        ]

    def evaluate(self, scraped_data: ScrapedData) -> tuple[int, List[SEOIssue], List[SEOCategory]]:
        """Evaluate scraped data and return score, issues, and categorized checks"""
        
        check_results = []
        issues_to_fix = []
        
        for check_def in self.seo_checks:
            try:
                passed = check_def["evaluate"](scraped_data)
                status = "pass" if passed else "fail"
                value = check_def["get_value"](scraped_data)
                
                seo_check = SEOCheck(
                    name=check_def["name"],
                    status=status,
                    value=value,
                    recommendation=check_def["recommendation"] if not passed else None
                )
                
                check_results.append({
                    "check": seo_check,
                    "category": check_def["category"],
                    "priority": check_def["priority"],
                    "passed": passed
                })
                
                if not passed:
                    issues_to_fix.append(SEOIssue(
                        priority=check_def["priority"],
                        issue=f"{check_def['name']}: {value}",
                        recommendation=check_def["recommendation"]
                    ))
            except Exception:
                # Skip checks that fail due to missing data
                continue
        
        # Calculate weighted score
        total_weight = 0
        passed_weight = 0
        weight_map = {"high": 3, "medium": 2, "low": 1}
        
        for result in check_results:
            weight = weight_map.get(result["priority"], 1)
            total_weight += weight
            if result["passed"]:
                passed_weight += weight
        
        overall_score = int((passed_weight / total_weight) * 100) if total_weight > 0 else 0
        
        # Group checks by category
        categories = {}
        for result in check_results:
            cat_name = result["category"]
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(result["check"])
        
        common_issues = [
            SEOCategory(category=cat_name, checks=checks)
            for cat_name, checks in categories.items()
        ]
        
        # Sort issues by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        issues_to_fix.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return overall_score, issues_to_fix, common_issues