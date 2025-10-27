import asyncio
import httpx
import base64
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ImageAnalysisService:
    """Computer vision and image optimization analysis"""
    
    def __init__(self):
        self.google_vision_api_key = getattr(settings, 'GOOGLE_VISION_API_KEY', None)
        self.azure_vision_api_key = getattr(settings, 'AZURE_VISION_API_KEY', None)
        self.azure_vision_endpoint = getattr(settings, 'AZURE_VISION_ENDPOINT', None)
        self.tinify_api_key = getattr(settings, 'TINIFY_API_KEY', None)

    async def analyze_page_images(self, url: str, soup, client: httpx.AsyncClient) -> Dict:
        """Analyze all images on the page for SEO optimization"""
        images = soup.find_all('img')
        
        metrics = {
            'total_images': len(images),
            'images_without_alt': 0,
            'images_without_title': 0,
            'oversized_images': 0,
            'unoptimized_formats': 0,
            'missing_lazy_loading': 0,
            'images_without_dimensions': 0,
            'broken_images': 0,
            'duplicate_alt_texts': 0,
            'ai_generated_alt_suggestions': 0,
            'compression_savings_kb': 0,
            'webp_conversion_candidates': 0
        }
        
        if not images:
            return metrics
        
        # Analyze each image
        alt_texts = []
        processed_images = 0
        
        for img in images[:10]:  # Limit to first 10 images for performance
            img_analysis = await self._analyze_single_image(img, url, client)
            
            # Update metrics
            if not img_analysis.get('has_alt'):
                metrics['images_without_alt'] += 1
            if not img_analysis.get('has_title'):
                metrics['images_without_title'] += 1
            if img_analysis.get('is_oversized'):
                metrics['oversized_images'] += 1
            if img_analysis.get('needs_format_optimization'):
                metrics['unoptimized_formats'] += 1
            if not img_analysis.get('has_lazy_loading'):
                metrics['missing_lazy_loading'] += 1
            if not img_analysis.get('has_dimensions'):
                metrics['images_without_dimensions'] += 1
            if img_analysis.get('is_broken'):
                metrics['broken_images'] += 1
            if img_analysis.get('webp_candidate'):
                metrics['webp_conversion_candidates'] += 1
            
            metrics['compression_savings_kb'] += img_analysis.get('compression_savings', 0)
            
            # Collect alt texts for duplicate detection
            alt_text = img_analysis.get('alt_text', '').strip()
            if alt_text:
                alt_texts.append(alt_text)
            
            processed_images += 1
        
        # Check for duplicate alt texts
        if alt_texts:
            unique_alts = set(alt_texts)
            metrics['duplicate_alt_texts'] = len(alt_texts) - len(unique_alts)
        
        # AI-generated alt text suggestions for images without alt
        if self.google_vision_api_key or self.azure_vision_api_key:
            metrics['ai_generated_alt_suggestions'] = min(metrics['images_without_alt'], 5)
        
        return metrics

    async def _analyze_single_image(self, img, base_url: str, client: httpx.AsyncClient) -> Dict:
        """Analyze individual image for SEO factors"""
        analysis = {
            'has_alt': bool(img.get('alt', '').strip()),
            'has_title': bool(img.get('title', '').strip()),
            'has_lazy_loading': bool(img.get('loading') == 'lazy'),
            'has_dimensions': bool(img.get('width') and img.get('height')),
            'alt_text': img.get('alt', ''),
            'is_broken': False,
            'is_oversized': False,
            'needs_format_optimization': False,
            'webp_candidate': False,
            'compression_savings': 0
        }
        
        # Get image URL
        img_src = img.get('src', '')
        if not img_src:
            return analysis
        
        # Convert relative URLs to absolute
        if img_src.startswith('//'):
            img_src = 'https:' + img_src
        elif img_src.startswith('/'):
            img_src = urljoin(base_url, img_src)
        elif not img_src.startswith(('http://', 'https://')):
            img_src = urljoin(base_url, img_src)
        
        try:
            # Check if image is accessible
            response = await client.head(img_src, timeout=5.0)
            
            if response.status_code != 200:
                analysis['is_broken'] = True
                return analysis
            
            # Analyze image properties from headers
            content_length = response.headers.get('content-length')
            content_type = response.headers.get('content-type', '')
            
            if content_length:
                size_kb = int(content_length) / 1024
                
                # Check if oversized (>500KB)
                if size_kb > 500:
                    analysis['is_oversized'] = True
                
                # Estimate compression savings (30% average)
                analysis['compression_savings'] = int(size_kb * 0.3)
            
            # Check format optimization
            if content_type in ['image/jpeg', 'image/png', 'image/gif']:
                analysis['needs_format_optimization'] = True
                analysis['webp_candidate'] = True
            
        except Exception as e:
            logger.debug(f"Error analyzing image {img_src}: {e}")
            analysis['is_broken'] = True
        
        return analysis

    async def generate_alt_text_suggestions(self, img_urls: List[str]) -> List[str]:
        """Generate AI-powered alt text suggestions"""
        suggestions = []
        
        for img_url in img_urls[:5]:  # Limit to 5 images
            try:
                if self.google_vision_api_key:
                    suggestion = await self._get_google_vision_description(img_url)
                elif self.azure_vision_api_key:
                    suggestion = await self._get_azure_vision_description(img_url)
                else:
                    suggestion = self._generate_mock_alt_text(img_url)
                
                if suggestion:
                    suggestions.append(suggestion)
                    
            except Exception as e:
                logger.debug(f"Error generating alt text for {img_url}: {e}")
        
        return suggestions

    async def _get_google_vision_description(self, img_url: str) -> Optional[str]:
        """Get image description from Google Vision API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Download image
                img_response = await client.get(img_url)
                if img_response.status_code != 200:
                    return None
                
                # Encode image to base64
                img_base64 = base64.b64encode(img_response.content).decode()
                
                # Call Vision API
                response = await client.post(
                    f"https://vision.googleapis.com/v1/images:annotate?key={self.google_vision_api_key}",
                    json={
                        "requests": [{
                            "image": {"content": img_base64},
                            "features": [{"type": "LABEL_DETECTION", "maxResults": 5}]
                        }]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    responses = data.get('responses', [])
                    if responses and 'labelAnnotations' in responses[0]:
                        labels = [label['description'] for label in responses[0]['labelAnnotations']]
                        return f"Image showing {', '.join(labels[:3])}"
                
        except Exception as e:
            logger.warning(f"Google Vision API error: {e}")
        
        return None

    async def _get_azure_vision_description(self, img_url: str) -> Optional[str]:
        """Get image description from Azure Computer Vision"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.azure_vision_endpoint}/vision/v3.2/describe",
                    headers={
                        'Ocp-Apim-Subscription-Key': self.azure_vision_api_key,
                        'Content-Type': 'application/json'
                    },
                    json={'url': img_url},
                    params={'maxCandidates': 1}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    descriptions = data.get('description', {}).get('captions', [])
                    if descriptions:
                        return descriptions[0]['text'].capitalize()
                
        except Exception as e:
            logger.warning(f"Azure Vision API error: {e}")
        
        return None

    def _generate_mock_alt_text(self, img_url: str) -> str:
        """Generate mock alt text based on image URL"""
        filename = img_url.split('/')[-1].split('?')[0]
        name_part = filename.split('.')[0]
        
        # Simple heuristics based on filename
        if any(word in name_part.lower() for word in ['logo', 'brand']):
            return f"Company logo"
        elif any(word in name_part.lower() for word in ['hero', 'banner', 'header']):
            return f"Hero banner image"
        elif any(word in name_part.lower() for word in ['product', 'item']):
            return f"Product image"
        elif any(word in name_part.lower() for word in ['team', 'person', 'staff']):
            return f"Team member photo"
        else:
            return f"Image: {name_part.replace('-', ' ').replace('_', ' ').title()}"

    def _get_mock_image_metrics(self, total_images: int) -> Dict:
        """Generate realistic mock image analysis data"""
        if total_images == 0:
            return {
                'total_images': 0,
                'images_without_alt': 0,
                'images_without_title': 0,
                'oversized_images': 0,
                'unoptimized_formats': 0,
                'missing_lazy_loading': 0,
                'images_without_dimensions': 0,
                'broken_images': 0,
                'duplicate_alt_texts': 0,
                'ai_generated_alt_suggestions': 0,
                'compression_savings_kb': 0,
                'webp_conversion_candidates': 0
            }
        
        # Realistic percentages for common issues
        return {
            'total_images': total_images,
            'images_without_alt': max(0, int(total_images * 0.3)),  # 30% missing alt
            'images_without_title': max(0, int(total_images * 0.7)),  # 70% missing title
            'oversized_images': max(0, int(total_images * 0.2)),  # 20% oversized
            'unoptimized_formats': max(0, int(total_images * 0.6)),  # 60% not WebP
            'missing_lazy_loading': max(0, int(total_images * 0.8)),  # 80% no lazy loading
            'images_without_dimensions': max(0, int(total_images * 0.4)),  # 40% no dimensions
            'broken_images': max(0, int(total_images * 0.05)),  # 5% broken
            'duplicate_alt_texts': max(0, int(total_images * 0.1)),  # 10% duplicates
            'ai_generated_alt_suggestions': min(5, max(0, int(total_images * 0.3))),
            'compression_savings_kb': max(0, int(total_images * 150)),  # 150KB avg savings per image
            'webp_conversion_candidates': max(0, int(total_images * 0.6))
        }