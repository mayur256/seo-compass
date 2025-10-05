"""Report aggregation and file generation service."""

import anyio
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi.responses import StreamingResponse
from app.core.logging import get_logger
from app.infrastructure.db.repositories import AnalysisRepository
from app.infrastructure.storage import make_csv_from_dicts, write_text_file, write_json_file, make_zip
from app.schemas.report_schemas import ReportModel, CompetitorOut, KeywordOut, DraftOut

logger = get_logger(__name__)


class ReportService:
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
    
    async def build_report_model(self, job_id: UUID) -> ReportModel:
        """Build complete report model from database."""
        logger.info(f"Building report model for job {job_id}")
        
        # Get job details
        job = await self.repository.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Get analysis results
        report_data = await self.repository.get_report(job_id)
        
        # Convert to output schemas
        competitors = []
        keywords = []
        drafts = []
        
        if report_data:
            competitors = [
                CompetitorOut(
                    rank=c.ranking_position,
                    url=c.url,
                    keyword=getattr(c, 'title', 'N/A'),  # Use title as keyword fallback
                    estimated_traffic=c.estimated_traffic or 0
                )
                for c in report_data.competitors
            ]
            
            keywords = [
                KeywordOut(
                    keyword=k.term,
                    search_volume=k.search_volume,
                    difficulty=k.difficulty,
                    cpc=k.cpc
                )
                for k in report_data.keywords
            ]
            
            drafts = [
                DraftOut(
                    page_name=d.page_type,
                    content=d.content
                )
                for d in report_data.content_drafts
            ]
        
        return ReportModel(
            job_id=job.id,
            url=job.url,
            status=job.status,
            created_at=job.created_at,
            completed_at=job.completed_at,
            competitors=competitors,
            keywords=keywords,
            drafts=drafts
        )
    
    async def generate_files(self, report: ReportModel) -> bytes:
        """Generate ZIP file with all report data."""
        logger.info(f"Generating files for report {report.job_id}")
        
        files = {}
        
        # Generate competitors CSV
        if report.competitors:
            competitors_data = [
                {
                    "rank": c.rank,
                    "url": c.url,
                    "keyword": c.keyword,
                    "estimated_traffic": c.estimated_traffic
                }
                for c in report.competitors
            ]
            competitors_csv = await anyio.to_thread.run_sync(
                make_csv_from_dicts,
                competitors_data,
                ["rank", "url", "keyword", "estimated_traffic"]
            )
            files["competitors.csv"] = competitors_csv
        
        # Generate keywords CSV
        if report.keywords:
            keywords_data = [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "difficulty": k.difficulty,
                    "cpc": k.cpc or 0
                }
                for k in report.keywords
            ]
            keywords_csv = await anyio.to_thread.run_sync(
                make_csv_from_dicts,
                keywords_data,
                ["keyword", "search_volume", "difficulty", "cpc"]
            )
            files["keywords.csv"] = keywords_csv
        
        # Generate content draft files
        for draft in report.drafts:
            filename = f"drafts/{draft.page_name}.txt"
            content_bytes = await anyio.to_thread.run_sync(
                write_text_file,
                draft.content
            )
            files[filename] = content_bytes
        
        # Generate metadata JSON
        metadata = {
            "job_id": str(report.job_id),
            "url": report.url,
            "status": report.status,
            "created_at": report.created_at.isoformat(),
            "completed_at": report.completed_at.isoformat() if report.completed_at else None,
            "counts": {
                "competitors": len(report.competitors),
                "keywords": len(report.keywords),
                "drafts": len(report.drafts)
            }
        }
        metadata_json = await anyio.to_thread.run_sync(write_json_file, metadata)
        files["report_metadata.json"] = metadata_json
        
        # Create ZIP file
        zip_bytes = await anyio.to_thread.run_sync(make_zip, files)
        logger.info(f"Generated ZIP file with {len(files)} files for job {report.job_id}")
        
        return zip_bytes
    
    async def stream_zip_response(self, report_zip: bytes, job_id: UUID) -> StreamingResponse:
        """Create streaming response for ZIP download."""
        def generate():
            yield report_zip
        
        filename = f"seo_compass_report_{job_id}.zip"
        
        return StreamingResponse(
            generate(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )