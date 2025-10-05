"""Report version domain entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class ReportVersion:
    """Report version entity."""
    id: UUID
    job_id: UUID
    version: int
    url: str
    status: str  # PENDING, PACKAGING, UPLOADING, COMPLETED, FAILED
    s3_zip_path: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None