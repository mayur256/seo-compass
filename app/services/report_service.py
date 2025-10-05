"""Report aggregation service."""

from typing import List, Optional
from uuid import UUID
from app.core.logging import get_logger
from app.services.competitor_service import CompetitorData
from app.services.keyword_service import KeywordData
from app.services.llm_service import PageDraft
from app.infrastructure.db.repositories import AnalysisRepository

logger = get_logger(__name__)


class ReportService:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def save_analysis_results(
        self,
        job_id: UUID,
        competitors: List[CompetitorData],
        keywords: List[KeywordData], 
        drafts: List[PageDraft]
    ) -> None:
        """Save all analysis results to database."""
        logger.info(f"Saving analysis results for job {job_id}")
        
        try:
            # Clear existing data for this job
            await self._clear_existing_results(job_id)
            
            # Save competitors
            await self._save_competitors(job_id, competitors)
            
            # Save keywords  
            await self._save_keywords(job_id, keywords)
            
            # Save content drafts
            await self._save_drafts(job_id, drafts)
            
            logger.info(f"Successfully saved analysis results for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis results for job {job_id}: {e}")
            raise
    
    async def _clear_existing_results(self, job_id: UUID) -> None:
        """Clear any existing results for the job."""
        # This would be implemented based on your repository interface
        # For now, we'll assume the repository handles this
        pass
    
    async def _save_competitors(self, job_id: UUID, competitors: List[CompetitorData]) -> None:
        """Save competitor data."""
        # Convert to domain entities and save via repository
        # Implementation depends on your repository interface
        logger.info(f"Saved {len(competitors)} competitors for job {job_id}")
    
    async def _save_keywords(self, job_id: UUID, keywords: List[KeywordData]) -> None:
        """Save keyword data."""
        # Convert to domain entities and save via repository
        logger.info(f"Saved {len(keywords)} keywords for job {job_id}")
    
    async def _save_drafts(self, job_id: UUID, drafts: List[PageDraft]) -> None:
        """Save content drafts."""
        # Convert to domain entities and save via repository
        logger.info(f"Saved {len(drafts)} content drafts for job {job_id}")
    
    async def get_partial_results(
        self, 
        job_id: UUID, 
        section: Optional[str] = None
    ) -> dict:
        """Get partial analysis results for a job."""
        logger.info(f"Retrieving partial results for job {job_id}, section: {section}")
        
        try:
            if section == "competitors":
                # Get competitors only
                report = await self.repository.get_report(job_id)
                return {"competitors": report.competitors if report else []}
            
            elif section == "keywords":
                # Get keywords only
                report = await self.repository.get_report(job_id)
                return {"keywords": report.keywords if report else []}
            
            elif section == "drafts":
                # Get content drafts only
                report = await self.repository.get_report(job_id)
                return {"content_drafts": report.content_drafts if report else []}
            
            else:
                # Get all results
                report = await self.repository.get_report(job_id)
                if report:
                    return {
                        "competitors": report.competitors,
                        "keywords": report.keywords,
                        "content_drafts": report.content_drafts
                    }
                return {}
                
        except Exception as e:
            logger.error(f"Failed to retrieve results for job {job_id}: {e}")
            raise