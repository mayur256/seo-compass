from typing import List
import httpx
from app.domain.entities import Competitor
from app.core.config import get_settings

settings = get_settings()


class SerpClient:
    def __init__(self):
        self.api_key = settings.serp_api_key
        self.client = httpx.AsyncClient()
    
    async def fetch_top_competitors(self, url: str) -> List[Competitor]:
        # TODO: Implement real SERP API integration
        # For now, return static example data
        return [
            Competitor(
                url="https://competitor1.com",
                title="Top Competitor 1",
                ranking_position=1,
                estimated_traffic=50000
            ),
            Competitor(
                url="https://competitor2.com",
                title="Top Competitor 2",
                ranking_position=2,
                estimated_traffic=35000
            ),
            Competitor(
                url="https://competitor3.com",
                title="Top Competitor 3",
                ranking_position=3,
                estimated_traffic=25000
            )
        ]
    
    async def close(self) -> None:
        await self.client.aclose()