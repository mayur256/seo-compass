from typing import List
import httpx
from app.domain.entities import ContentDraft, Keyword
from app.core.config import get_settings

settings = get_settings()


class LLMClient:
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.client = httpx.AsyncClient()
    
    async def generate_drafts(self, keywords: List[str]) -> List[ContentDraft]:
        # TODO: Implement real LLM API integration (OpenAI, etc.)
        # For now, return static example drafts
        return [
            ContentDraft(
                page_type="homepage",
                title="Welcome to Your Business",
                content="This is a sample homepage content generated based on your keywords: " + ", ".join(keywords),
                meta_description="Professional services for your business needs"
            ),
            ContentDraft(
                page_type="about",
                title="About Our Company",
                content="Learn more about our company and our mission to provide excellent services.",
                meta_description="Learn about our company history and values"
            ),
            ContentDraft(
                page_type="services",
                title="Our Services",
                content="We offer comprehensive services tailored to your business needs.",
                meta_description="Explore our range of professional services"
            )
        ]
    
    async def extract_keywords(self, url: str) -> List[Keyword]:
        # TODO: Implement keyword extraction logic
        # For now, return static example keywords
        return [
            Keyword(term="business services", search_volume=10000, difficulty=0.6, cpc=2.50),
            Keyword(term="professional consulting", search_volume=8000, difficulty=0.7, cpc=3.20),
            Keyword(term="expert solutions", search_volume=5000, difficulty=0.5, cpc=1.80),
        ]
    
    async def close(self) -> None:
        await self.client.aclose()