import asyncio
import time
import re
import json
from typing import Optional, Dict, List
from collections import Counter
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.schemas.audit_schemas import ScrapedData
from app.core.logging import get_logger
from app.services.core_web_vitals_service import CoreWebVitalsService

logger = get_logger(__name__)


class SEOScraperService:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={'User-Agent': 'SEO-Compass-Bot/1.0'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def scrape_url(self, url: str) -> ScrapedData:
        """Comprehensive SEO data scraping"""
        try:
            start_time = time.time()
            response = await self.client.get(str(url))
            page_load_time = time.time() - start_time
            
            # Get Core Web Vitals
            cwv_service = CoreWebVitalsService()
            core_web_vitals = await cwv_service.collect_metrics(url)
            
            if response.status_code != 200:
                logger.warning(f"Non-200 status code {response.status_code} for {url}")
                return ScrapedData(https=url.startswith('https://'))

            soup = BeautifulSoup(response.text, 'html.parser')
            html_content = response.text
            
            # Basic SEO data
            title = self._extract_title(soup)
            meta_description = self._extract_meta_description(soup)
            
            # Heading tags
            h1_tags = self._extract_headings(soup, 'h1')
            h2_tags = self._extract_headings(soup, 'h2')
            h3_tags = self._extract_headings(soup, 'h3')
            h4_tags = self._extract_headings(soup, 'h4')
            h5_tags = self._extract_headings(soup, 'h5')
            h6_tags = self._extract_headings(soup, 'h6')
            
            # Meta tags
            canonical_tag = self._extract_canonical(soup)
            og_title = self._extract_meta_property(soup, 'og:title')
            og_description = self._extract_meta_property(soup, 'og:description')
            og_image = self._extract_meta_property(soup, 'og:image')
            twitter_card = self._extract_meta_name(soup, 'twitter:card')
            twitter_title = self._extract_meta_name(soup, 'twitter:title')
            twitter_description = self._extract_meta_name(soup, 'twitter:description')
            
            # Technical elements
            charset = self._extract_charset(soup)
            viewport_tag = self._check_viewport(soup)
            noindex = self._check_noindex(soup)
            nofollow = self._check_nofollow(soup)
            meta_refresh = self._extract_meta_refresh(soup)
            
            # Images and media
            alt_missing_count = self._count_missing_alt_tags(soup)
            
            # Performance metrics
            html_size = len(html_content)
            dom_size = len(soup.find_all())
            text_to_html_ratio = self._calculate_text_ratio(soup, html_content)
            
            # Browser-based metrics
            http_requests = core_web_vitals.get('http_requests', 0)
            render_blocking = core_web_vitals.get('render_blocking', 0)
            js_minified = core_web_vitals.get('js_minified', False)
            css_minified = core_web_vitals.get('css_minified', False)
            webp_images = core_web_vitals.get('webp_images', 0)
            http2_enabled = core_web_vitals.get('http2_enabled', False)
            cdn_detected = core_web_vitals.get('cdn_detected', False)
            media_queries = core_web_vitals.get('media_queries', 0)
            fcp = core_web_vitals.get('fcp', 0)
            lcp = core_web_vitals.get('lcp', 0)
            cls = core_web_vitals.get('cls', 0)
            ttfb = core_web_vitals.get('ttfb', page_load_time)
            
            # Keywords analysis
            keyword_data = self._analyze_keywords(soup)
            
            # Structured data
            structured_data_count = self._count_structured_data(soup)
            
            # Deprecated tags
            deprecated_tags_count = self._count_deprecated_tags(soup)
            
            # Security checks
            mixed_content_count = self._count_mixed_content(soup, url)
            unsafe_links_count = self._count_unsafe_links(soup)
            
            # External checks
            robots_txt_exists = await self._check_robots_txt(url)
            sitemap_exists = await self._check_sitemap(url)
            favicon_exists = await self._check_favicon(url)
            ads_txt_exists = await self._check_ads_txt(url)
            custom_404_exists = await self._check_custom_404(url)
            
            # Headers and compression
            gzip_enabled = self._check_gzip_compression(response)
            hsts_header = self._check_hsts_header(response)
            
            # SSL validation
            ssl_valid = await self._validate_ssl(url)
            
            return ScrapedData(
                # Basic SEO
                title=title,
                meta_description=meta_description,
                h1_tags=h1_tags,
                h2_tags=h2_tags,
                h3_tags=h3_tags,
                h4_tags=h4_tags,
                h5_tags=h5_tags,
                h6_tags=h6_tags,
                canonical_tag=canonical_tag,
                alt_missing_count=alt_missing_count,
                https=url.startswith('https://'),
                page_load_time=page_load_time,
                text_to_html_ratio=text_to_html_ratio,
                robots_txt_exists=robots_txt_exists,
                sitemap_exists=sitemap_exists,
                
                # Meta tags
                og_title=og_title,
                og_description=og_description,
                og_image=og_image,
                twitter_card=twitter_card,
                twitter_title=twitter_title,
                twitter_description=twitter_description,
                
                # Technical
                charset=charset,
                viewport_tag=viewport_tag,
                favicon_exists=favicon_exists,
                noindex=noindex,
                nofollow=nofollow,
                meta_refresh=meta_refresh,
                structured_data_count=structured_data_count,
                deprecated_tags_count=deprecated_tags_count,
                
                # Performance
                html_size=html_size,
                dom_size=dom_size,
                http_requests=http_requests,
                gzip_enabled=gzip_enabled,
                js_minified=core_web_vitals.get('js_minified', False),
                css_minified=core_web_vitals.get('css_minified', False),
                webp_images=core_web_vitals.get('webp_images', 0),
                http2_enabled=core_web_vitals.get('http2_enabled', False),
                cdn_detected=core_web_vitals.get('cdn_detected', False),
                media_queries=core_web_vitals.get('media_queries', 0),
                render_blocking=core_web_vitals.get('render_blocking', 0),
                js_execution_time=core_web_vitals.get('js_execution_time', 0.0),
                
                # Core Web Vitals
                fcp=core_web_vitals.get('fcp', 0.0),
                lcp=core_web_vitals.get('lcp', 0.0),
                cls=core_web_vitals.get('cls', 0.0),
                ttfb=core_web_vitals.get('ttfb', page_load_time),
                
                # Security
                ssl_valid=ssl_valid,
                hsts_header=hsts_header,
                mixed_content_count=mixed_content_count,
                unsafe_links_count=unsafe_links_count,
                
                # Keywords
                keyword_density=keyword_data['density'],
                most_common_keywords=keyword_data['common'],
                
                # Files
                ads_txt_exists=ads_txt_exists,
                custom_404_exists=custom_404_exists
            )
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ScrapedData(https=url.startswith('https://'))

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None

    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else None

    def _extract_meta_property(self, soup: BeautifulSoup, property_name: str) -> Optional[str]:
        meta_tag = soup.find('meta', attrs={'property': property_name})
        return meta_tag.get('content', '').strip() if meta_tag else None

    def _extract_meta_name(self, soup: BeautifulSoup, name: str) -> Optional[str]:
        meta_tag = soup.find('meta', attrs={'name': name})
        return meta_tag.get('content', '').strip() if meta_tag else None

    def _extract_headings(self, soup: BeautifulSoup, tag: str) -> List[str]:
        headings = soup.find_all(tag)
        return [h.get_text().strip() for h in headings if h.get_text().strip()]

    def _extract_canonical(self, soup: BeautifulSoup) -> Optional[str]:
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href') if canonical else None

    def _extract_charset(self, soup: BeautifulSoup) -> Optional[str]:
        charset_tag = soup.find('meta', attrs={'charset': True})
        if charset_tag:
            return charset_tag.get('charset')
        
        http_equiv = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
        if http_equiv and 'content' in http_equiv.attrs:
            content = http_equiv['content']
            match = re.search(r'charset=([^;]+)', content)
            return match.group(1) if match else None
        return None

    def _check_viewport(self, soup: BeautifulSoup) -> bool:
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        return bool(viewport)

    def _check_noindex(self, soup: BeautifulSoup) -> bool:
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta and 'content' in robots_meta.attrs:
            return 'noindex' in robots_meta['content'].lower()
        return False

    def _check_nofollow(self, soup: BeautifulSoup) -> bool:
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta and 'content' in robots_meta.attrs:
            return 'nofollow' in robots_meta['content'].lower()
        return False

    def _extract_meta_refresh(self, soup: BeautifulSoup) -> Optional[str]:
        refresh_tag = soup.find('meta', attrs={'http-equiv': 'refresh'})
        return refresh_tag.get('content') if refresh_tag else None

    def _count_missing_alt_tags(self, soup: BeautifulSoup) -> int:
        images = soup.find_all('img')
        return sum(1 for img in images if not img.get('alt'))

    def _calculate_text_ratio(self, soup: BeautifulSoup, html: str) -> float:
        text_content = soup.get_text()
        text_length = len(text_content.strip())
        html_length = len(html)
        return (text_length / html_length * 100) if html_length > 0 else 0.0

    def _analyze_keywords(self, soup: BeautifulSoup) -> Dict:
        text_content = soup.get_text().lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_content)
        
        # Filter common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        filtered_words = [word for word in words if word not in stop_words]
        
        word_count = Counter(filtered_words)
        total_words = len(filtered_words)
        
        # Calculate density for top words
        density = {}
        most_common = []
        
        for word, count in word_count.most_common(10):
            density[word] = (count / total_words) * 100 if total_words > 0 else 0
            most_common.append(word)
        
        return {'density': density, 'common': most_common}

    def _count_structured_data(self, soup: BeautifulSoup) -> int:
        json_ld = soup.find_all('script', type='application/ld+json')
        microdata = soup.find_all(attrs={'itemscope': True})
        return len(json_ld) + len(microdata)

    def _count_deprecated_tags(self, soup: BeautifulSoup) -> int:
        deprecated_tags = ['center', 'font', 'marquee', 'blink', 'big', 'tt', 'strike']
        count = 0
        for tag in deprecated_tags:
            count += len(soup.find_all(tag))
        return count

    def _count_mixed_content(self, soup: BeautifulSoup, url: str) -> int:
        if not url.startswith('https://'):
            return 0
        
        count = 0
        # Check images, scripts, stylesheets, etc.
        for tag in soup.find_all(['img', 'script', 'link', 'iframe']):
            src = tag.get('src') or tag.get('href')
            if src and src.startswith('http://'):
                count += 1
        return count

    def _count_unsafe_links(self, soup: BeautifulSoup) -> int:
        count = 0
        for link in soup.find_all('a', target='_blank'):
            rel = link.get('rel', [])
            if isinstance(rel, str):
                rel = rel.split()
            if 'noopener' not in rel or 'noreferrer' not in rel:
                count += 1
        return count

    def _check_gzip_compression(self, response: httpx.Response) -> bool:
        return 'gzip' in response.headers.get('content-encoding', '').lower()

    def _check_hsts_header(self, response: httpx.Response) -> bool:
        return 'strict-transport-security' in response.headers

    async def _validate_ssl(self, url: str) -> bool:
        if not url.startswith('https://'):
            return False
        try:
            # Basic SSL validation - in production, use more comprehensive checks
            response = await self.client.get(url)
            return response.status_code < 400
        except:
            return False

    async def _check_robots_txt(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            response = await self.client.get(robots_url)
            return response.status_code == 200
        except:
            return False

    async def _check_sitemap(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            sitemap_url = f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml"
            response = await self.client.get(sitemap_url)
            return response.status_code == 200
        except:
            return False

    async def _check_favicon(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
            response = await self.client.get(favicon_url)
            return response.status_code == 200
        except:
            return False

    async def _check_ads_txt(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            ads_txt_url = f"{parsed_url.scheme}://{parsed_url.netloc}/ads.txt"
            response = await self.client.get(ads_txt_url)
            return response.status_code == 200
        except:
            return False

    async def _check_custom_404(self, url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            test_404_url = f"{parsed_url.scheme}://{parsed_url.netloc}/nonexistent-page-test-404"
            response = await self.client.get(test_404_url)
            # Custom 404 should return 404 status with content
            return response.status_code == 404 and len(response.text) > 100
        except:
            return False