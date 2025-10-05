from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.schemas.analysis_schemas import PartialAnalysisResponse
from app.services.report_service import ReportService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/analyze", 
    response_model=AnalyzeResponse, 
    status_code=200,
    summary="Submit URL for SEO Analysis",
    description="Submit a URL for comprehensive SEO analysis including competitor research, keyword extraction, and content generation.",
    response_description="Analysis job created successfully"
)
async def analyze_url(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db)
) -> AnalyzeResponse:
    """Submit URL for comprehensive SEO analysis.
    
    This endpoint creates a new analysis job that will:
    - Discover top competitors via SERP analysis
    - Extract keywords using HTML parsing and TF-IDF
    - Generate SEO-optimized content drafts using AI
    
    The analysis runs asynchronously in the background. Use the returned job_id
    to check status and retrieve results.
    
    Args:
        request: Contains the URL to analyze (must be valid HTTP/HTTPS URL)
        db: Database session dependency
        
    Returns:
        AnalyzeResponse containing job_id and initial status (QUEUED)
        
    Raises:
        HTTPException 400: Invalid URL format
        HTTPException 500: Internal server error
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


@router.get(
    "/jobs/{job_id}", 
    response_model=JobStatusResponse,
    summary="Get Job Status",
    description="Retrieve the current status and details of an analysis job.",
    response_description="Job status and details"
)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> JobStatusResponse:
    """Get analysis job status and progress.
    
    Track the progress of your SEO analysis job. Status transitions:
    - QUEUED: Job is waiting to be processed
    - IN_PROGRESS: Analysis is currently running
    - COMPLETED: Analysis finished successfully
    - FAILED: Analysis encountered an error
    
    Args:
        job_id: UUID of the analysis job (returned from /analyze endpoint)
        db: Database session dependency
        
    Returns:
        JobStatusResponse with current status, timestamps, and URL
        
    Raises:
        HTTPException 404: Job not found
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


@router.get(
    "/analyze/{job_id}", 
    response_model=ReportResponse,
    summary="Get Analysis Results",
    description="Retrieve comprehensive SEO analysis results with optional section filtering.",
    response_description="Complete or filtered analysis results"
)
async def get_analysis_results(
    job_id: UUID,
    section: Optional[str] = Query(
        None, 
        description="Filter results by section",
        enum=["competitors", "keywords", "drafts"]
    ),
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """Get comprehensive SEO analysis results.
    
    Retrieve the complete analysis results or filter by specific sections:
    - competitors: Top ranking competitors with traffic estimates
    - keywords: Extracted keywords with search volume and difficulty
    - drafts: AI-generated SEO-optimized content drafts
    
    Results are available even for jobs in progress (partial data).
    
    Args:
        job_id: UUID of the analysis job
        section: Optional filter - 'competitors', 'keywords', or 'drafts'
        db: Database session dependency
        
    Returns:
        ReportResponse with complete or filtered analysis data
        
    Raises:
        HTTPException 404: Job not found
    """
    repository = SQLAnalysisRepository(db)
    
    # Check if job exists
    job_use_case = GetJobStatusUseCase(repository)
    job = await job_use_case.execute(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get report (even if job is still in progress)
    report_use_case = GetReportUseCase(repository)
    report = await report_use_case.execute(job_id)
    
    if not report:
        # Return empty response if no results yet
        return ReportResponse(
            job_id=job_id,
            competitors=[],
            keywords=[],
            content_drafts=[]
        )
    
    # Filter by section if requested
    competitors = report.competitors if section != "keywords" and section != "drafts" else []
    keywords = report.keywords if section != "competitors" and section != "drafts" else []
    content_drafts = report.content_drafts if section != "competitors" and section != "keywords" else []
    
    return ReportResponse(
        job_id=report.job_id,
        competitors=[
            CompetitorResponse(
                url=c.url,
                title=c.title,
                ranking_position=c.ranking_position,
                estimated_traffic=c.estimated_traffic
            )
            for c in competitors
        ],
        keywords=[
            KeywordResponse(
                term=k.term,
                search_volume=k.search_volume,
                difficulty=k.difficulty,
                cpc=k.cpc
            )
            for c in keywords
        ],
        content_drafts=[
            ContentDraftResponse(
                page_type=d.page_type,
                title=d.title,
                content=d.content,
                meta_description=d.meta_description
            )
            for d in content_drafts
        ]
    )


@router.get(
    "/reports/{job_id}", 
    response_model=ReportResponse,
    summary="Get Complete Report (Legacy)",
    description="Legacy endpoint for retrieving complete analysis reports.",
    response_description="Complete analysis report",
    deprecated=True
)
async def get_report(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """Get complete analysis report (legacy endpoint).
    
    **Deprecated**: Use `/analyze/{job_id}` instead for better functionality.
    
    Args:
        job_id: UUID of the analysis job
        db: Database session dependency
        
    Returns:
        ReportResponse with complete analysis results
    """
    return await get_analysis_results(job_id, None, db)