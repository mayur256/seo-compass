import asyncio
import time
from typing import Dict, List
from app.core.logging import get_logger

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = get_logger(__name__)


class CoreWebVitalsService:
    """Service for collecting Core Web Vitals and performance metrics using browser automation"""
    
    async def collect_metrics(self, url: str) -> Dict:
        """Collect comprehensive performance metrics"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, returning empty metrics")
            return {}
            
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Track network requests
                requests = []
                def handle_request(request):
                    requests.append({
                        'url': request.url,
                        'method': request.method,
                        'resource_type': request.resource_type
                    })
                page.on('request', handle_request)
                
                # Navigate and measure TTFB
                start_time = time.time()
                await page.goto(url, wait_until='networkidle')
                ttfb = time.time() - start_time
                
                # Get Core Web Vitals
                vitals = await page.evaluate("""
                    () => {
                        return new Promise((resolve) => {
                            const vitals = {};
                            const observer = new PerformanceObserver((list) => {
                                const entries = list.getEntries();
                                
                                entries.forEach((entry) => {
                                    if (entry.entryType === 'paint') {
                                        if (entry.name === 'first-contentful-paint') {
                                            vitals.fcp = entry.startTime;
                                        }
                                    }
                                    if (entry.entryType === 'largest-contentful-paint') {
                                        vitals.lcp = entry.startTime;
                                    }
                                    if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
                                        vitals.cls = (vitals.cls || 0) + entry.value;
                                    }
                                });
                            });
                            
                            observer.observe({entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift']});
                            
                            // Resolve after collecting metrics
                            setTimeout(() => resolve(vitals), 3000);
                        });
                    }
                """)
                
                # Analyze resources
                js_files = [r for r in requests if r['resource_type'] == 'script']
                css_files = [r for r in requests if r['resource_type'] == 'stylesheet']
                image_files = [r for r in requests if r['resource_type'] == 'image']
                
                # Check minification
                js_minified = any('.min.js' in r['url'] or 'minified' in r['url'] for r in js_files)
                css_minified = any('.min.css' in r['url'] or 'minified' in r['url'] for r in css_files)
                
                # Check modern image formats
                webp_images = sum(1 for r in image_files if 'webp' in r['url'].lower())
                
                # CDN detection
                cdn_keywords = ['cdn', 'cloudflare', 'amazonaws', 'fastly', 'cloudfront', 'akamai']
                cdn_detected = any(any(cdn in r['url'].lower() for cdn in cdn_keywords) for r in requests)
                
                # Media queries count
                media_queries = await page.evaluate("""
                    () => {
                        let count = 0;
                        try {
                            for (let sheet of document.styleSheets) {
                                for (let rule of sheet.cssRules || []) {
                                    if (rule.type === CSSRule.MEDIA_RULE) {
                                        count++;
                                    }
                                }
                            }
                        } catch (e) {}
                        return count;
                    }
                """)
                
                # JavaScript execution time
                js_execution_time = await page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('measure');
                        return entries.reduce((total, entry) => total + entry.duration, 0);
                    }
                """)
                
                await browser.close()
                
                return {
                    'http_requests': len(requests),
                    'render_blocking': len([r for r in requests if r['resource_type'] in ['script', 'stylesheet']]),
                    'js_minified': js_minified,
                    'css_minified': css_minified,
                    'webp_images': webp_images,
                    'cdn_detected': cdn_detected,
                    'media_queries': media_queries,
                    'fcp': vitals.get('fcp', 0) / 1000,  # Convert to seconds
                    'lcp': vitals.get('lcp', 0) / 1000,
                    'cls': vitals.get('cls', 0),
                    'ttfb': ttfb,
                    'js_execution_time': js_execution_time / 1000,  # Convert to seconds
                    'http2_enabled': False,  # Would need more complex detection
                }
                
        except Exception as e:
            logger.error(f"Error collecting Core Web Vitals: {e}")
            return {}