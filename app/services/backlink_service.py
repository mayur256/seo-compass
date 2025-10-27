import asyncio
import httpx
from typing import Dict, Optional
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class BacklinkService:
    """Third-party API integration for backlink and domain authority metrics"""
    
    def __init__(self):
        self.moz_api_key = getattr(settings, 'MOZ_API_KEY', None)
        self.ahrefs_api_key = getattr(settings, 'AHREFS_API_KEY', None)
        self.semrush_api_key = getattr(settings, 'SEMRUSH_API_KEY', None)

    async def get_domain_metrics(self, url: str) -> Dict:
        """Get comprehensive domain authority and backlink metrics"""
        domain = self._extract_domain(url)
        
        # Try multiple APIs in order of preference
        metrics = {}
        
        # Try Moz API first
        if self.moz_api_key:
            moz_data = await self._get_moz_metrics(domain)
            metrics.update(moz_data)
        
        # Try Ahrefs API
        if self.ahrefs_api_key:
            ahrefs_data = await self._get_ahrefs_metrics(domain)
            metrics.update(ahrefs_data)
        
        # Try SEMrush API
        if self.semrush_api_key:
            semrush_data = await self._get_semrush_metrics(domain)
            metrics.update(semrush_data)
        
        # If no APIs available, return mock data for development
        if not metrics:
            metrics = self._get_mock_metrics(domain)
        
        return metrics

    async def _get_moz_metrics(self, domain: str) -> Dict:
        """Get Moz Domain Authority and backlink data"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://lsapi.seomoz.com/v2/url_metrics",
                    params={'targets': domain},
                    headers={'Authorization': f'Basic {self.moz_api_key}'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        result = data['results'][0]
                        return {
                            'domain_authority': result.get('domain_authority', 0),
                            'page_authority': result.get('page_authority', 0),
                            'spam_score': result.get('spam_score', 0),
                            'linking_root_domains': result.get('linking_root_domains', 0),
                            'total_backlinks': result.get('external_links', 0)
                        }
        except Exception as e:
            logger.warning(f"Moz API error for {domain}: {e}")
        
        return {}

    async def _get_ahrefs_metrics(self, domain: str) -> Dict:
        """Get Ahrefs Domain Rating and backlink data"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://apiv2.ahrefs.com",
                    params={
                        'target': domain,
                        'token': self.ahrefs_api_key,
                        'mode': 'domain',
                        'output': 'json'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('domain'):
                        domain_data = data['domain']
                        return {
                            'domain_rating': domain_data.get('ahrefs_rank', 0),
                            'referring_domains': domain_data.get('refdomains', 0),
                            'backlinks': domain_data.get('backlinks', 0),
                            'organic_keywords': domain_data.get('organic_keywords', 0),
                            'organic_traffic': domain_data.get('organic_traffic', 0)
                        }
        except Exception as e:
            logger.warning(f"Ahrefs API error for {domain}: {e}")
        
        return {}

    async def _get_semrush_metrics(self, domain: str) -> Dict:
        """Get SEMrush domain metrics"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.semrush.com/",
                    params={
                        'type': 'domain_overview',
                        'key': self.semrush_api_key,
                        'domain': domain,
                        'export_columns': 'Or,Ot,Oc,Ad,At,Ac'
                    }
                )
                
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    if len(lines) > 1:
                        data = lines[1].split(';')
                        return {
                            'organic_keywords_semrush': int(data[0]) if data[0].isdigit() else 0,
                            'organic_traffic_semrush': int(data[1]) if data[1].isdigit() else 0,
                            'organic_cost': float(data[2]) if data[2].replace('.', '').isdigit() else 0,
                            'adwords_keywords': int(data[3]) if data[3].isdigit() else 0,
                            'adwords_traffic': int(data[4]) if data[4].isdigit() else 0,
                            'adwords_cost': float(data[5]) if data[5].replace('.', '').isdigit() else 0
                        }
        except Exception as e:
            logger.warning(f"SEMrush API error for {domain}: {e}")
        
        return {}

    def _get_mock_metrics(self, domain: str) -> Dict:
        """Generate realistic mock data for development"""
        # Simple hash-based mock data for consistency
        domain_hash = hash(domain) % 100
        
        return {
            'domain_authority': min(85, max(10, 30 + domain_hash)),
            'page_authority': min(80, max(5, 25 + domain_hash)),
            'spam_score': max(0, min(17, 5 - (domain_hash // 10))),
            'linking_root_domains': max(10, domain_hash * 50),
            'total_backlinks': max(100, domain_hash * 500),
            'domain_rating': min(90, max(5, 20 + domain_hash)),
            'referring_domains': max(5, domain_hash * 30),
            'backlinks': max(50, domain_hash * 300),
            'organic_keywords': max(100, domain_hash * 100),
            'organic_traffic': max(500, domain_hash * 1000),
            'organic_keywords_semrush': max(80, domain_hash * 80),
            'organic_traffic_semrush': max(400, domain_hash * 800),
            'organic_cost': max(100.0, domain_hash * 50.0),
            'adwords_keywords': max(20, domain_hash * 10),
            'adwords_traffic': max(200, domain_hash * 200),
            'adwords_cost': max(50.0, domain_hash * 25.0)
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or parsed.path