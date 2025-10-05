"""Report endpoints for viewing and downloading analysis results."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.base import get_db
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.services.report_service import ReportService
from app.infrastructure.db.report_repository import ReportRepository
from app.infrastructure.s3_storage import S3StorageService
from app.tasks.report_packaging_worker import package_report_task
from app.schemas.report_schemas import (
    ReportResponse, 
    CompetitorOut, 
    KeywordOut, 
    DraftOut,
    ReportVersionOut,
    ReportHistoryOut,
    PackagingStatusOut
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    """Dependency to get report service."""
    repository = SQLAnalysisRepository(db)
    return ReportService(repository)


def get_report_repository(db: AsyncSession = Depends(get_db)) -> ReportRepository:
    """Dependency to get report repository."""
    return ReportRepository(db)


def get_s3_service() -> S3StorageService:
    """Dependency to get S3 service."""
    return S3StorageService()


@router.get(
    "/{job_id}",
    response_model=ReportResponse,
    summary="Get Analysis Report",
    description="Retrieve structured analysis report with optional section filtering.",
    response_description="Complete or filtered analysis report"
)
async def get_report(
    job_id: UUID,
    section: Optional[str] = Query(
        "all",
        description="Report section to retrieve",
        enum=["all", "competitors", "keywords", "drafts"]
    ),
    report_service: ReportService = Depends(get_report_service)
) -> ReportResponse:
    """Get structured analysis report."""
    try:
        report = await report_service.build_report_model(job_id)
        
        if report.status != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail=f"Report not ready. Job status: {report.status}"
            )
        
        response = ReportResponse(
            job_id=report.job_id,
            url=report.url,
            status=report.status,
            created_at=report.created_at,
            completed_at=report.completed_at
        )
        
        if section in ["all", "competitors"]:
            response.competitors = report.competitors
        
        if section in ["all", "keywords"]:
            response.keywords = report.keywords
        
        if section in ["all", "drafts"]:
            response.drafts = report.drafts
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        logger.error(f"Failed to retrieve report for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve report")


@router.get(
    "/{job_id}/download",
    summary="Download Report ZIP",
    description="Download complete analysis report as ZIP file with CSVs and content drafts."
)
async def download_report(
    job_id: UUID,
    report_service: ReportService = Depends(get_report_service)
) -> StreamingResponse:
    """Download complete analysis report as ZIP file."""
    try:
        report = await report_service.build_report_model(job_id)
        
        if report.status != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail=f"Report not ready. Job status: {report.status}"
            )
        
        zip_bytes = await report_service.generate_files(report)
        response = await report_service.stream_zip_response(zip_bytes, job_id)
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        logger.error(f"Failed to generate download for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download")


@router.get(
    "/history",
    response_model=ReportHistoryOut,
    summary="Get Report History",
    description="Retrieve paginated history of analysis reports with optional filtering."
)
async def get_report_history(
    url: Optional[str] = Query(None, description="Filter by URL"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    page: int = Query(1, ge=1, description="Page number"),
    report_repo: ReportRepository = Depends(get_report_repository),
    s3_service: S3StorageService = Depends(get_s3_service)
) -> ReportHistoryOut:
    """Get paginated report history."""
    try:
        offset = (page - 1) * limit
        versions, total = await report_repo.get_history(
            url=url,
            status=status,
            limit=limit,
            offset=offset
        )
        
        version_outs = []
        for version in versions:
            s3_zip_url = None
            if version.status == "COMPLETED" and version.s3_zip_path:
                try:
                    s3_zip_url = await s3_service.get_presigned_url(version.s3_zip_path)
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL: {e}")
            
            version_outs.append(ReportVersionOut(
                id=version.id,
                job_id=version.job_id,
                version=version.version,
                url=version.url,
                status=version.status,
                s3_zip_url=s3_zip_url,
                created_at=version.created_at,
                completed_at=version.completed_at
            ))
        
        return ReportHistoryOut(
            data=version_outs,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve report history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve report history")


@router.get(
    "/{job_id}/packaging-status",
    response_model=PackagingStatusOut,
    summary="Get Packaging Status",
    description="Check the status of background report packaging."
)
async def get_packaging_status(
    job_id: UUID,
    report_repo: ReportRepository = Depends(get_report_repository)
) -> PackagingStatusOut:
    """Get packaging status for a job."""
    try:
        version = await report_repo.get_by_job_id(job_id)
        if not version:
            raise HTTPException(status_code=404, detail="Job not found")
        
        progress_map = {
            "PENDING": 0,
            "PACKAGING": 25,
            "UPLOADING": 75,
            "COMPLETED": 100,
            "FAILED": 0
        }
        
        return PackagingStatusOut(
            job_id=job_id,
            version_id=version.id,
            status=version.status,
            progress=progress_map.get(version.status, 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get packaging status for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get packaging status")