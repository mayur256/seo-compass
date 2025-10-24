from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from app.infrastructure.db.seo_audit_model import SEOAudit
from app.schemas.audit_schemas import AuditResult


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_audit(
        self, 
        url: str, 
        overall_score: int, 
        issues_json: dict, 
        recommendations_json: dict,
        pdf_path: Optional[str] = None
    ) -> SEOAudit:
        """Create a new SEO audit record"""
        audit = SEOAudit(
            url=url,
            overall_score=overall_score,
            issues_json=issues_json,
            recommendations_json=recommendations_json,
            pdf_path=pdf_path
        )
        
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(audit)
        return audit

    async def get_audit(self, audit_id: uuid.UUID) -> Optional[SEOAudit]:
        """Get audit by ID"""
        result = await self.session.execute(
            select(SEOAudit).where(SEOAudit.id == audit_id)
        )
        return result.scalar_one_or_none()

    async def update_pdf_path(self, audit_id: uuid.UUID, pdf_path: str) -> bool:
        """Update PDF path for an audit"""
        audit = await self.get_audit(audit_id)
        if audit:
            audit.pdf_path = pdf_path
            await self.session.commit()
            return True
        return False

    def to_audit_result(self, audit: SEOAudit) -> AuditResult:
        """Convert database model to response schema"""
        return AuditResult(
            url=audit.url,
            overall_score=audit.overall_score,
            issues_to_fix=audit.issues_json.get("issues_to_fix", []),
            common_issues=audit.recommendations_json.get("common_issues", [])
        )