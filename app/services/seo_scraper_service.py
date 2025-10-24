import asyncio
import time
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.schemas.audit_schemas import ScrapedData
from app.core.logging import get_logger

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
        """Scrape SEO-related data from a URL"""
        try:
            start_time = time.time()
            response = await self.client.get(str(url))
            page_load_time = time.time() - start_time
            
            if response.status_code != 200:
                logger.warning(f"Non-200 status code {response.status_code} for {url}")
                return ScrapedData(https=url.startswith('https://'))

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract SEO data
            title = self._extract_title(soup)
            meta_description = self._extract_meta_description(soup)
            h1_tags = self._extract_headings(soup, 'h1')
            h2_tags = self._extract_headings(soup, 'h2')
            h3_tags = self._extract_headings(soup, 'h3')
            canonical_tag = self._extract_canonical(soup)
            alt_missing_count = self._count_missing_alt_tags(soup)
            text_to_html_ratio = self._calculate_text_ratio(soup, response.text)
            
            # Check external resources
            robots_txt_exists = await self._check_robots_txt(url)
            sitemap_exists = await self._check_sitemap(url)
            
            return ScrapedData(
                title=title,
                meta_description=meta_description,
                h1_tags=h1_tags,
                h2_tags=h2_tags,
                h3_tags=h3_tags,
                canonical_tag=canonical_tag,
                alt_missing_count=alt_missing_count,
                https=url.startswith('https://'),
                page_load_time=page_load_time,
                text_to_html_ratio=text_to_html_ratio,
                robots_txt_exists=robots_txt_exists,
                sitemap_exists=sitemap_exists
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

    def _extract_headings(self, soup: BeautifulSoup, tag: str) -> list[str]:
        headings = soup.find_all(tag)
        return [h.get_text().strip() for h in headings if h.get_text().strip()]

    def _extract_canonical(self, soup: BeautifulSoup) -> Optional[str]:
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href') if canonical else None

    def _count_missing_alt_tags(self, soup: BeautifulSoup) -> int:
        images = soup.find_all('img')
        return sum(1 for img in images if not img.get('alt'))

    def _calculate_text_ratio(self, soup: BeautifulSoup, html: str) -> float:
        text_content = soup.get_text()
        text_length = len(text_content.strip())
        html_length = len(html)
        return (text_length / html_length * 100) if html_length > 0 else 0.0

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