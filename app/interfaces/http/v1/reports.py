"""Report endpoints for viewing and downloading analysis results."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.base import get_db
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.services.report_service import ReportService
from app.schemas.report_schemas import ReportResponse, CompetitorOut, KeywordOut, DraftOut
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    """Dependency to get report service."""
    repository = SQLAnalysisRepository(db)
    return ReportService(repository)


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
    """Get structured analysis report.
    
    Retrieve the complete analysis report or filter by specific sections:
    - all: Complete report with all sections
    - competitors: Only competitor analysis data
    - keywords: Only keyword research data  
    - drafts: Only content draft data
    
    Args:
        job_id: UUID of the analysis job
        section: Section filter (all|competitors|keywords|drafts)
        report_service: Report service dependency
        
    Returns:
        ReportResponse with complete or filtered analysis data
        
    Raises:
        HTTPException 404: Job not found
        HTTPException 400: Job not completed
    \"\"\"\n    try:\n        # Build complete report model\n        report = await report_service.build_report_model(job_id)\n        \n        # Check if job is completed\n        if report.status != \"COMPLETED\":\n            raise HTTPException(\n                status_code=400,\n                detail=f\"Report not ready. Job status: {report.status}\"\n            )\n        \n        # Filter sections based on query parameter\n        response = ReportResponse(\n            job_id=report.job_id,\n            url=report.url,\n            status=report.status,\n            created_at=report.created_at,\n            completed_at=report.completed_at\n        )\n        \n        if section in [\"all\", \"competitors\"]:\n            response.competitors = report.competitors\n        \n        if section in [\"all\", \"keywords\"]:\n            response.keywords = report.keywords\n        \n        if section in [\"all\", \"drafts\"]:\n            response.drafts = report.drafts\n        \n        logger.info(f\"Retrieved report for job {job_id}, section: {section}\")\n        return response\n        \n    except ValueError as e:\n        logger.error(f\"Job {job_id} not found: {e}\")\n        raise HTTPException(status_code=404, detail=\"Job not found\")\n    except Exception as e:\n        logger.error(f\"Failed to retrieve report for job {job_id}: {e}\")\n        raise HTTPException(status_code=500, detail=\"Failed to retrieve report\")\n\n\n@router.get(\n    \"/{job_id}/download\",\n    summary=\"Download Report ZIP\",\n    description=\"Download complete analysis report as ZIP file with CSVs and content drafts.\",\n    response_description=\"ZIP file containing analysis data\"\n)\nasync def download_report(\n    job_id: UUID,\n    report_service: ReportService = Depends(get_report_service)\n) -> StreamingResponse:\n    \"\"\"Download complete analysis report as ZIP file.\n    \n    Generate and download a ZIP file containing:\n    - competitors.csv: Competitor analysis data\n    - keywords.csv: Keyword research data\n    - drafts/*.txt: Content draft files\n    - report_metadata.json: Report summary and metadata\n    \n    Args:\n        job_id: UUID of the analysis job\n        report_service: Report service dependency\n        \n    Returns:\n        StreamingResponse with ZIP file download\n        \n    Raises:\n        HTTPException 404: Job not found\n        HTTPException 400: Job not completed\n    \"\"\"\n    try:\n        # Build report model\n        report = await report_service.build_report_model(job_id)\n        \n        # Check if job is completed\n        if report.status != \"COMPLETED\":\n            raise HTTPException(\n                status_code=400,\n                detail=f\"Report not ready. Job status: {report.status}\"\n            )\n        \n        # Generate ZIP file\n        zip_bytes = await report_service.generate_files(report)\n        \n        # Return streaming response\n        response = await report_service.stream_zip_response(zip_bytes, job_id)\n        \n        logger.info(f\"Generated download for job {job_id}\")\n        return response\n        \n    except ValueError as e:\n        logger.error(f\"Job {job_id} not found: {e}\")\n        raise HTTPException(status_code=404, detail=\"Job not found\")\n    except Exception as e:\n        logger.error(f\"Failed to generate download for job {job_id}: {e}\")\n        raise HTTPException(status_code=500, detail=\"Failed to generate download\")