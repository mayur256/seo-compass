import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.base import get_db
from app.infrastructure.db.audit_repository import AuditRepository
from app.services.seo_scraper_service import SEOScraperService
from app.services.seo_evaluator_service import SEOEvaluatorService
from app.services.seo_report_service import SEOReportService
from app.schemas.audit_schemas import AuditRequest, AuditResponse, AuditResult
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/audit", tags=["SEO Audit"])


async def process_audit_task(audit_id: uuid.UUID, url: str):
    """Background task to process SEO audit"""
    try:
        async with get_async_session() as session:
            repository = AuditRepository(session)
            
            # Scrape website data
            async with SEOScraperService() as scraper:
                scraped_data = await scraper.scrape_url(url)
            
            # Evaluate SEO
            evaluator = SEOEvaluatorService()
            overall_score, issues_to_fix, common_issues = evaluator.evaluate(scraped_data)
            
            # Build report data
            report_service = SEOReportService()
            issues_json = {"issues_to_fix": [issue.dict() for issue in issues_to_fix]}
            recommendations_json = {"common_issues": [category.dict() for category in common_issues]}
            
            # Generate PDF
            audit_result = AuditResult(
                url=url,
                overall_score=overall_score,
                issues_to_fix=issues_to_fix,
                common_issues=common_issues
            )
            
            pdf_filename = f"seo_audit_{audit_id}.pdf"
            pdf_path = f"/tmp/reports/{pdf_filename}"
            await report_service.generate_pdf_report(audit_result, pdf_path)
            
            # Update audit with PDF path
            await repository.update_pdf_path(audit_id, pdf_path)
            
            logger.info(f"SEO audit completed for {url}")
            
    except Exception as e:
        logger.error(f"Error processing audit {audit_id}: {e}")


@router.post("/", response_model=AuditResponse)
async def create_audit(
    request: AuditRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """Start SEO audit for a URL"""
    try:
        repository = AuditRepository(session)
        
        # Create initial audit record
        audit = await repository.create_audit(
            url=str(request.url),
            overall_score=0,
            issues_json={},
            recommendations_json={}
        )
        
        # Start background processing
        background_tasks.add_task(process_audit_task, audit.id, str(request.url))
        
        return AuditResponse(
            audit_id=audit.id,
            status="processing",
            message="Audit started successfully."
        )
        
    except Exception as e:
        logger.error(f"Error creating audit: {e}")
        raise HTTPException(status_code=500, detail="Failed to start audit")


@router.get("/{audit_id}", response_model=AuditResult)
async def get_audit(
    audit_id: uuid.UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get SEO audit results"""
    repository = AuditRepository(session)
    audit = await repository.get_audit(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if not audit.issues_json or not audit.recommendations_json:
        raise HTTPException(status_code=202, detail="Audit still processing")
    
    return repository.to_audit_result(audit)


@router.get("/{audit_id}/download")
async def download_audit_pdf(
    audit_id: uuid.UUID,
    session: AsyncSession = Depends(get_db)
):
    """Download PDF report"""
    repository = AuditRepository(session)
    audit = await repository.get_audit(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if not audit.pdf_path or not os.path.exists(audit.pdf_path):
        raise HTTPException(status_code=404, detail="PDF report not available")
    
    return FileResponse(
        audit.pdf_path,
        media_type="application/pdf",
        filename=f"seo_audit_{audit_id}.pdf"
    )