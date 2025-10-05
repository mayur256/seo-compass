import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.infrastructure.db.base import AsyncSessionLocal
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.infrastructure.external.serp_client import SerpClient
from app.infrastructure.external.llm_client import LLMClient
from app.domain.entities import Report
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task
def process_analysis(job_id: str, url: str) -> None:
    """Process SEO analysis for a given URL."""
    asyncio.run(_process_analysis_async(UUID(job_id), url))


async def _process_analysis_async(job_id: UUID, url: str) -> None:
    """Async implementation of analysis processing."""
    logger.info(f"Starting analysis for job {job_id}, URL: {url}")
    
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        try:
            # Update job status to IN_PROGRESS
            await repository.update_job_status(job_id, "IN_PROGRESS")
            
            # Initialize clients
            serp_client = SerpClient()
            llm_client = LLMClient()
            
            try:
                # Fetch competitors
                competitors = await serp_client.fetch_top_competitors(url)
                logger.info(f"Found {len(competitors)} competitors")
                
                # Extract keywords
                keywords = await llm_client.extract_keywords(url)
                logger.info(f"Extracted {len(keywords)} keywords")
                
                # Generate content drafts
                keyword_terms = [k.term for k in keywords]
                content_drafts = await llm_client.generate_drafts(keyword_terms)
                logger.info(f"Generated {len(content_drafts)} content drafts")
                
                # Create report
                report = Report(
                    job_id=job_id,
                    competitors=competitors,
                    keywords=keywords,
                    content_drafts=content_drafts
                )
                
                # Save report to database
                await repository.save_report(report)
                
                # Update job status to COMPLETED
                await repository.update_job_status(job_id, "COMPLETED")
                logger.info(f"Analysis completed for job {job_id}")
                
            finally:
                await serp_client.close()
                await llm_client.close()
                
        except Exception as e:
            logger.error(f"Analysis failed for job {job_id}: {str(e)}")
            await repository.update_job_status(job_id, "FAILED")
            raise