from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid
from app.infrastructure.db.base import Base


class SEOAudit(Base):
    __tablename__ = "seo_audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    overall_score = Column(Integer, nullable=False)
    issues_json = Column(JSON, nullable=False)
    recommendations_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    pdf_path = Column(String, nullable=True)