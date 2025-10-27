import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.base import get_db
from app.infrastructure.db.audit_repository import AuditRepository
from app.services.seo_scraper_service import SEOScraperService
from app.services.seo_evaluator_service import SEOEvaluatorService
from app.services.seo_report_service import SEOReportService
from app.schemas.audit_schemas import AuditRequest, AuditResult
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/audit", tags=["SEO Audit"])


@router.post("/", response_model=AuditResult)
async def create_audit(
    request: AuditRequest,
    session: AsyncSession = Depends(get_db)
):
    """Perform complete SEO audit for a URL"""
    try:
        # Scrape website data
        async with SEOScraperService() as scraper:
            scraped_data = await scraper.scrape_url(str(request.url))
        
        # Evaluate SEO
        evaluator = SEOEvaluatorService()
        overall_score, issues_to_fix, common_issues = evaluator.evaluate(scraped_data)
        
        # Build report data
        issues_json = {"issues_to_fix": [issue.dict() for issue in issues_to_fix]}
        recommendations_json = {"common_issues": [category.dict() for category in common_issues]}
        
        # Generate PDF
        audit_result = AuditResult(
            url=str(request.url),
            overall_score=overall_score,
            issues_to_fix=issues_to_fix,
            common_issues=common_issues
        )
        
        report_service = SEOReportService()
        audit_id = uuid.uuid4()
        pdf_filename = f"seo_audit_{audit_id}.pdf"
        pdf_path = f"/tmp/reports/{pdf_filename}"
        await report_service.generate_pdf_report(audit_result, pdf_path)
        
        # Save to database
        repository = AuditRepository(session)
        await repository.create_audit(
            url=str(request.url),
            overall_score=overall_score,
            issues_json=issues_json,
            recommendations_json=recommendations_json,
            pdf_path=pdf_path
        )
        
        logger.info(f"SEO audit completed for {request.url}")
        return audit_result
        
    except Exception as e:
        logger.error(f"Error creating audit: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete audit")


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