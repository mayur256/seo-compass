from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.base import get_db
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.application.usecases.submit_analysis import SubmitAnalysisUseCase
from app.application.usecases.get_report import GetJobStatusUseCase, GetReportUseCase
from app.schemas.request_response import (
    AnalyzeRequest,
    AnalyzeResponse,
    JobStatusResponse,
    ReportResponse,
    CompetitorResponse,
    KeywordResponse,
    ContentDraftResponse
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse, status_code=200)
async def analyze_url(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db)
) -> AnalyzeResponse:
    """Submit URL for SEO analysis.
    
    Creates a new analysis job and enqueues it for background processing.
    
    Args:
        request: Contains the URL to analyze
        db: Database session
        
    Returns:
        AnalyzeResponse with job_id and status
        
    Raises:
        HTTPException: If URL validation fails
    """
    try:
        repository = SQLAnalysisRepository(db)
        use_case = SubmitAnalysisUseCase(repository)
        
        job_id, status = await use_case.execute(str(request.url))
        
        return AnalyzeResponse(job_id=job_id, status=status)
    except ValueError as e:
        logger.error(f"URL validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create analysis job")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> JobStatusResponse:
    """Get analysis job status.
    
    Retrieves the current status and details of an analysis job.
    
    Args:
        job_id: UUID of the analysis job
        db: Database session
        
    Returns:
        JobStatusResponse with job details and current status
        
    Raises:
        HTTPException: If job is not found
    """
    repository = SQLAnalysisRepository(db)
    use_case = GetJobStatusUseCase(repository)
    
    job = await use_case.execute(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job.id,
        url=job.url,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.get("/reports/{job_id}", response_model=ReportResponse)
async def get_report(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """Get analysis report."""
    repository = SQLAnalysisRepository(db)
    
    # Check if job exists and is completed
    job_use_case = GetJobStatusUseCase(repository)
    job = await job_use_case.execute(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail=f"Job not completed. Status: {job.status}")
    
    # Get report
    report_use_case = GetReportUseCase(repository)
    report = await report_use_case.execute(job_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(
        job_id=report.job_id,
        competitors=[
            CompetitorResponse(
                url=c.url,
                title=c.title,
                ranking_position=c.ranking_position,
                estimated_traffic=c.estimated_traffic
            )
            for c in report.competitors
        ],
        keywords=[
            KeywordResponse(
                term=k.term,
                search_volume=k.search_volume,
                difficulty=k.difficulty,
                cpc=k.cpc
            )
            for k in report.keywords
        ],
        content_drafts=[
            ContentDraftResponse(
                page_type=d.page_type,
                title=d.title,
                content=d.content,
                meta_description=d.meta_description
            )
            for d in report.content_drafts
        ]
    )