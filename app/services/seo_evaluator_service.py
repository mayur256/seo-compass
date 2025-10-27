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
            },
            
            # DNS & Email Security
            {
                "name": "SPF Record",
                "category": "Email Security",
                "priority": "medium",
                "evaluate": lambda data: data.spf_record,
                "get_value": lambda data: "Present" if data.spf_record else "Missing",
                "recommendation": "Add SPF record to prevent email spoofing."
            },
            {
                "name": "DMARC Record",
                "category": "Email Security",
                "priority": "medium",
                "evaluate": lambda data: data.dmarc_record,
                "get_value": lambda data: "Present" if data.dmarc_record else "Missing",
                "recommendation": "Add DMARC record for email authentication."
            },
            {
                "name": "MX Records",
                "category": "Email Security",
                "priority": "low",
                "evaluate": lambda data: data.mx_records,
                "get_value": lambda data: "Configured" if data.mx_records else "Not configured",
                "recommendation": "Configure MX records for email delivery."
            },
            {
                "name": "IPv6 Support",
                "category": "Technical SEO",
                "priority": "low",
                "evaluate": lambda data: data.ipv6_support,
                "get_value": lambda data: "Supported" if data.ipv6_support else "Not supported",
                "recommendation": "Add AAAA records for IPv6 support."
            },
            {
                "name": "Domain Verification",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: data.has_verification,
                "get_value": lambda data: "Verified" if data.has_verification else "Not verified",
                "recommendation": "Add domain verification records for search engines."
            },
            {
                "name": "Plaintext Emails",
                "category": "Security",
                "priority": "low",
                "evaluate": lambda data: data.plaintext_emails == 0,
                "get_value": lambda data: f"Exposed: {data.plaintext_emails}",
                "recommendation": "Avoid exposing email addresses to prevent spam."
            },
            
            # Third-party API Metrics (Authority & Backlinks)
            {
                "name": "Domain Authority",
                "category": "Authority",
                "priority": "high",
                "evaluate": lambda data: max(data.domain_authority, data.domain_rating) >= 40,
                "get_value": lambda data: f"DA: {data.domain_authority}, DR: {data.domain_rating}",
                "recommendation": "Build quality backlinks to improve domain authority."
            },
            {
                "name": "Spam Score",
                "category": "Authority",
                "priority": "medium",
                "evaluate": lambda data: data.spam_score <= 5,
                "get_value": lambda data: f"{data.spam_score}%",
                "recommendation": "Monitor and disavow toxic backlinks to reduce spam score."
            },
            {
                "name": "Backlink Profile",
                "category": "Backlinks",
                "priority": "high",
                "evaluate": lambda data: max(data.linking_root_domains, data.referring_domains) >= 20,
                "get_value": lambda data: f"Domains: {max(data.linking_root_domains, data.referring_domains)}, Links: {max(data.total_backlinks, data.backlinks)}",
                "recommendation": "Focus on acquiring backlinks from diverse, high-quality domains."
            },
            {
                "name": "Organic Visibility",
                "category": "Organic Search",
                "priority": "high",
                "evaluate": lambda data: max(data.organic_keywords, data.organic_keywords_semrush) >= 100,
                "get_value": lambda data: f"Keywords: {max(data.organic_keywords, data.organic_keywords_semrush)}, Traffic: {max(data.organic_traffic, data.organic_traffic_semrush)}",
                "recommendation": "Expand keyword targeting and improve content optimization."
            },
            {
                "name": "Link Diversity",
                "category": "Backlinks",
                "priority": "medium",
                "evaluate": lambda data: self._check_link_diversity_ratio(data),
                "get_value": lambda data: f"Ratio: {self._get_link_diversity_ratio(data):.1f}",
                "recommendation": "Maintain healthy link diversity (2-10 links per domain)."
            },
            {
                "name": "Traffic Quality",
                "category": "Organic Search",
                "priority": "medium",
                "evaluate": lambda data: data.organic_cost > 0 and (data.organic_cost / max(data.organic_traffic, data.organic_traffic_semrush, 1)) >= 0.5,
                "get_value": lambda data: f"Value: ${(data.organic_cost / max(data.organic_traffic, data.organic_traffic_semrush, 1)):.2f}/visit" if data.organic_cost > 0 else "No data",
                "recommendation": "Target higher commercial value keywords."
            },
            {
                "name": "Competitive Position",
                "category": "Competition",
                "priority": "medium",
                "evaluate": lambda data: max(data.domain_authority, data.domain_rating) >= 30 and max(data.organic_keywords, data.organic_keywords_semrush) >= 100,
                "get_value": lambda data: "Strong" if max(data.domain_authority, data.domain_rating) >= 60 else "Moderate" if max(data.domain_authority, data.domain_rating) >= 30 else "Weak",
                "recommendation": "Improve authority and keyword coverage to compete effectively."
            },
            {
                "name": "Paid Search Presence",
                "category": "Paid Search",
                "priority": "low",
                "evaluate": lambda data: data.adwords_keywords > 0,
                "get_value": lambda data: f"Keywords: {data.adwords_keywords}, Traffic: {data.adwords_traffic}" if data.adwords_keywords > 0 else "No activity",
                "recommendation": "Consider paid search advertising for competitive keywords."
            },
            
            # Image Analysis & Optimization
            {
                "name": "Image Alt Text Coverage",
                "category": "Image SEO",
                "priority": "high",
                "evaluate": lambda data: data.total_images == 0 or data.images_without_alt == 0,
                "get_value": lambda data: f"{data.images_without_alt}/{data.total_images} missing alt text",
                "recommendation": "Add descriptive alt text to all images for accessibility and SEO."
            },
            {
                "name": "Image Format Optimization",
                "category": "Image SEO",
                "priority": "medium",
                "evaluate": lambda data: data.total_images == 0 or data.unoptimized_formats <= data.total_images * 0.3,
                "get_value": lambda data: f"{data.unoptimized_formats}/{data.total_images} need format optimization",
                "recommendation": "Convert images to WebP format for better compression."
            },
            {
                "name": "Image Size Optimization",
                "category": "Image SEO",
                "priority": "high",
                "evaluate": lambda data: data.oversized_images == 0,
                "get_value": lambda data: f"{data.oversized_images} oversized images (>500KB)",
                "recommendation": "Compress large images to improve page load speed."
            },
            {
                "name": "Lazy Loading Implementation",
                "category": "Image SEO",
                "priority": "medium",
                "evaluate": lambda data: data.total_images == 0 or data.missing_lazy_loading <= data.total_images * 0.5,
                "get_value": lambda data: f"{data.missing_lazy_loading}/{data.total_images} missing lazy loading",
                "recommendation": "Implement lazy loading for images below the fold."
            },
            {
                "name": "Image Dimensions Specified",
                "category": "Image SEO",
                "priority": "medium",
                "evaluate": lambda data: data.total_images == 0 or data.images_without_dimensions == 0,
                "get_value": lambda data: f"{data.images_without_dimensions}/{data.total_images} missing dimensions",
                "recommendation": "Specify width and height attributes to prevent layout shift."
            },
            {
                "name": "Broken Images Check",
                "category": "Image SEO",
                "priority": "high",
                "evaluate": lambda data: data.broken_images == 0,
                "get_value": lambda data: f"{data.broken_images} broken images",
                "recommendation": "Fix or remove broken image links."
            },
            {
                "name": "Alt Text Uniqueness",
                "category": "Image SEO",
                "priority": "low",
                "evaluate": lambda data: data.duplicate_alt_texts == 0,
                "get_value": lambda data: f"{data.duplicate_alt_texts} duplicate alt texts",
                "recommendation": "Use unique, descriptive alt text for each image."
            },
            {
                "name": "Image Compression Potential",
                "category": "Image SEO",
                "priority": "medium",
                "evaluate": lambda data: data.compression_savings_kb <= 500,
                "get_value": lambda data: f"{data.compression_savings_kb}KB potential savings",
                "recommendation": "Compress images to reduce page load time and bandwidth usage."
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
    
    def _check_link_diversity_ratio(self, data: ScrapedData) -> bool:
        """Check if link diversity ratio is healthy (2-10 links per domain)"""
        referring_domains = max(data.linking_root_domains, data.referring_domains)
        if referring_domains == 0:
            return False
        
        total_links = max(data.total_backlinks, data.backlinks)
        ratio = total_links / referring_domains
        return 2 <= ratio <= 10
    
    def _get_link_diversity_ratio(self, data: ScrapedData) -> float:
        """Get link diversity ratio for display"""
        referring_domains = max(data.linking_root_domains, data.referring_domains)
        if referring_domains == 0:
            return 0.0
        
        total_links = max(data.total_backlinks, data.backlinks)
        return total_links / referring_domains