from typing import List, Dict, Callable
from app.schemas.audit_schemas import ScrapedData, SEOCheck, SEOCategory, SEOIssue


class SEOEvaluatorService:
    def __init__(self):
        self.seo_checks = self._define_seo_checks()

    def _define_seo_checks(self) -> List[Dict]:
        return [
            {
                "name": "Title Tag",
                "category": "On-Page SEO",
                "priority": "high",
                "evaluate": lambda data: bool(data.title),
                "get_value": lambda data: f"Length: {len(data.title)} characters" if data.title else "Missing",
                "recommendation": "Add a descriptive title tag (50-60 characters)."
            },
            {
                "name": "Meta Description",
                "category": "On-Page SEO", 
                "priority": "high",
                "evaluate": lambda data: bool(data.meta_description),
                "get_value": lambda data: f"Length: {len(data.meta_description)} characters" if data.meta_description else "Missing",
                "recommendation": "Add a meta description under 160 characters."
            },
            {
                "name": "H1 Tag",
                "category": "On-Page SEO",
                "priority": "medium",
                "evaluate": lambda data: len(data.h1_tags) == 1,
                "get_value": lambda data: f"Count: {len(data.h1_tags)}",
                "recommendation": "Use exactly one H1 tag per page."
            },
            {
                "name": "HTTPS",
                "category": "Technical SEO",
                "priority": "high",
                "evaluate": lambda data: data.https,
                "get_value": lambda data: "Enabled" if data.https else "Disabled",
                "recommendation": "Enable HTTPS for security and SEO benefits."
            },
            {
                "name": "Alt Attributes",
                "category": "On-Page SEO",
                "priority": "medium",
                "evaluate": lambda data: data.alt_missing_count == 0,
                "get_value": lambda data: f"Missing: {data.alt_missing_count}",
                "recommendation": "Add alt attributes to all images for accessibility."
            },
            {
                "name": "Page Load Time",
                "category": "Technical SEO",
                "priority": "medium",
                "evaluate": lambda data: data.page_load_time < 3.0,
                "get_value": lambda data: f"{data.page_load_time:.2f}s",
                "recommendation": "Optimize page load time to under 3 seconds."
            },
            {
                "name": "Robots.txt",
                "category": "Technical SEO",
                "priority": "low",
                "evaluate": lambda data: data.robots_txt_exists,
                "get_value": lambda data: "Found" if data.robots_txt_exists else "Missing",
                "recommendation": "Create a robots.txt file to guide search engines."
            },
            {
                "name": "XML Sitemap",
                "category": "Technical SEO",
                "priority": "low",
                "evaluate": lambda data: data.sitemap_exists,
                "get_value": lambda data: "Found" if data.sitemap_exists else "Missing",
                "recommendation": "Create an XML sitemap to help search engines index your site."
            }
        ]

    def evaluate(self, scraped_data: ScrapedData) -> tuple[int, List[SEOIssue], List[SEOCategory]]:
        """Evaluate scraped data and return score, issues, and categorized checks"""
        
        # Run all checks
        check_results = []
        issues_to_fix = []
        
        for check_def in self.seo_checks:
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
            
            # Add to issues if failed
            if not passed:
                issues_to_fix.append(SEOIssue(
                    priority=check_def["priority"],
                    issue=f"{check_def['name']}: {value}",
                    recommendation=check_def["recommendation"]
                ))
        
        # Calculate overall score
        total_checks = len(check_results)
        passed_checks = sum(1 for result in check_results if result["passed"])
        overall_score = int((passed_checks / total_checks) * 100) if total_checks > 0 else 0
        
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