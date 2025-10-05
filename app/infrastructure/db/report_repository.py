"""Repository for report versioning operations."""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Integer, Text, select, func, desc
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.base import Base
from app.domain.report_version import ReportVersion
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportVersionModel(Base):
    """SQLAlchemy model for report versions."""
    __tablename__ = "report_versions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(PGUUID(as_uuid=True), nullable=False)
    version = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    s3_zip_path = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ReportRepository:
    """Repository for report version operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_version(self, job_id: UUID, url: str) -> ReportVersion:
        """Create new report version."""
        # Get latest version for this URL
        latest_version = await self.get_latest_version(url)
        new_version = latest_version + 1
        
        version_id = uuid4()
        db_version = ReportVersionModel(
            id=version_id,
            job_id=job_id,
            version=new_version,
            url=url,
            status="PENDING"
        )
        
        self.session.add(db_version)
        await self.session.commit()
        await self.session.refresh(db_version)
        
        logger.info(f"Created report version {new_version} for job {job_id}")
        
        return ReportVersion(
            id=db_version.id,
            job_id=db_version.job_id,
            version=db_version.version,
            url=db_version.url,
            status=db_version.status,
            s3_zip_path=db_version.s3_zip_path,
            created_at=db_version.created_at,
            completed_at=db_version.completed_at
        )
    
    async def get_latest_version(self, url: str) -> int:
        """Get latest version number for URL."""
        result = await self.session.execute(
            select(func.max(ReportVersionModel.version))
            .where(ReportVersionModel.url == url)
        )
        max_version = result.scalar()
        return max_version or 0
    
    async def get_history(
        self, 
        url: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10, 
        offset: int = 0
    ) -> Tuple[List[ReportVersion], int]:
        """Get paginated report history."""
        query = select(ReportVersionModel)
        count_query = select(func.count(ReportVersionModel.id))
        
        if url:
            query = query.where(ReportVersionModel.url == url)
            count_query = count_query.where(ReportVersionModel.url == url)
        
        if status:
            query = query.where(ReportVersionModel.status == status)
            count_query = count_query.where(ReportVersionModel.status == status)
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(desc(ReportVersionModel.created_at))
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        db_versions = result.scalars().all()
        
        versions = [
            ReportVersion(
                id=v.id,
                job_id=v.job_id,
                version=v.version,
                url=v.url,
                status=v.status,
                s3_zip_path=v.s3_zip_path,
                created_at=v.created_at,
                completed_at=v.completed_at
            )
            for v in db_versions
        ]
        
        return versions, total
    
    async def update_status(self, version_id: UUID, status: str) -> None:
        """Update version status."""
        db_version = await self.session.get(ReportVersionModel, version_id)
        if db_version:
            db_version.status = status
            if status == "COMPLETED":
                db_version.completed_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"Updated version {version_id} status to {status}")
    
    async def update_s3_path(self, version_id: UUID, s3_path: str) -> None:
        """Update S3 path for version."""
        db_version = await self.session.get(ReportVersionModel, version_id)
        if db_version:
            db_version.s3_zip_path = s3_path
            await self.session.commit()
            logger.info(f"Updated version {version_id} S3 path to {s3_path}")
    
    async def get_by_job_id(self, job_id: UUID) -> Optional[ReportVersion]:
        """Get report version by job ID."""
        result = await self.session.execute(
            select(ReportVersionModel).where(ReportVersionModel.job_id == job_id)
        )
        db_version = result.scalar_one_or_none()
        
        if not db_version:
            return None
        
        return ReportVersion(
            id=db_version.id,
            job_id=db_version.job_id,
            version=db_version.version,
            url=db_version.url,
            status=db_version.status,
            s3_zip_path=db_version.s3_zip_path,
            created_at=db_version.created_at,
            completed_at=db_version.completed_at
        )