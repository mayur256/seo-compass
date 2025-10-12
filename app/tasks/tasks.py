import asyncio
from uuid import UUID
from app.tasks.celery_app import celery_app
from app.infrastructure.db.base import AsyncSessionLocal
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.services.competitor_service import CompetitorService
from app.services.keyword_service import KeywordService
from app.services.llm_service import LLMService
from app.services.report_service import ReportService

from app.core.logging import get_logger

logger = get_logger(__name__)

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_analysis(self, job_id: str, url: str) -> None:
    """Process SEO analysis for a given URL."""
    try:
        asyncio.run(_process_analysis_async(UUID(job_id), url))
    except Exception as e:
        logger.error(f"Analysis task failed for job {job_id}: {e}")
        raise


async def _process_analysis_async(job_id: UUID, url: str) -> None:
    """Async implementation of analysis processing pipeline."""
    logger.info(f"Starting analysis pipeline for job {job_id}, URL: {url}")
    
    # Initialize services
    competitor_service = CompetitorService()
    keyword_service = KeywordService()
    llm_service = LLMService()
    
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        report_service = ReportService(repository)
        
        try:
            # Update job status to IN_PROGRESS
            await repository.update_status(job_id, "IN_PROGRESS")
            logger.info(f"Job {job_id} status updated to IN_PROGRESS")
            
            # Step 1: Competitor Discovery
            logger.info(f"Step 1: Discovering competitors for {url}")
            competitors = await competitor_service.discover_competitors(url)
            logger.info(f"Found {len(competitors)} competitors")
            
            # Step 2: Keyword Extraction
            logger.info(f"Step 2: Extracting keywords from {url}")
            keywords = await keyword_service.extract_keywords(url)
            logger.info(f"Extracted {len(keywords)} keywords")
            
            # Step 3: Content Generation
            logger.info(f"Step 3: Generating content drafts")
            content_drafts = await llm_service.generate_content_drafts(keywords, competitors)
            logger.info(f"Generated {len(content_drafts)} content drafts")
            
            # Step 4: Save Results
            logger.info(f"Step 4: Saving analysis results")
            await repository.add_mock_data(job_id)
            
            # Step 5: Create report version and trigger packaging
            from app.infrastructure.db.report_repository import ReportRepository
            from app.tasks.report_packaging_worker import package_report_task
            
            report_repo = ReportRepository(session)
            job = await repository.get_job(job_id)
            
            if job:
                # Create report version
                version = await report_repo.create_version(job_id, job.url)
                logger.info(f"Created report version {version.version} for job {job_id}")
                
                # Trigger background packaging
                package_report_task.delay(str(job_id), str(version.id))
                logger.info(f"Triggered packaging task for version {version.id}")
            
            # Mark job as completed
            await repository.set_completed(job_id)
            logger.info(f"Analysis pipeline completed successfully for job {job_id}")
                
        except Exception as e:
            logger.error(f"Analysis pipeline failed for job {job_id}: {str(e)}")
            await repository.update_status(job_id, "FAILED")
            raise
        
        finally:
            # Clean up services
            await competitor_service.close()
            await keyword_service.close()
            await llm_service.close()