import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from app.schemas.audit_schemas import AuditResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class SEOReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#1f2937')
        ))

    def build_json_report(self, url: str, overall_score: int, issues_to_fix: list, common_issues: list) -> Dict[str, Any]:
        """Build structured JSON report"""
        return {
            "url": url,
            "overall_score": overall_score,
            "issues_to_fix": [issue.dict() for issue in issues_to_fix],
            "common_issues": [category.dict() for category in common_issues]
        }

    async def generate_pdf_report(self, audit_result: AuditResult, output_path: str) -> str:
        """Generate PDF report from audit results"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title
            story.append(Paragraph("SEO Compass - Audit Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # URL and Score
            story.append(Paragraph(f"<b>Website:</b> {audit_result.url}", self.styles['Normal']))
            story.append(Spacer(1, 10))
            
            score_color = self._get_score_color(audit_result.overall_score)
            story.append(Paragraph(
                f"<b>Overall SEO Score:</b> <font color='{score_color}'>{audit_result.overall_score}/100</font>",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 20))
            
            # Issues to Fix Section
            if audit_result.issues_to_fix:
                story.append(Paragraph("Issues to Fix", self.styles['SectionHeader']))
                
                issues_data = [['Priority', 'Issue', 'Recommendation']]
                for issue in audit_result.issues_to_fix:
                    issues_data.append([
                        issue.priority.upper(),
                        issue.issue,
                        issue.recommendation
                    ])
                
                issues_table = Table(issues_data, colWidths=[1*inch, 2.5*inch, 3*inch])
                issues_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                story.append(issues_table)
                story.append(Spacer(1, 20))
            
            # Common Issues Section
            story.append(Paragraph("SEO Checklist", self.styles['SectionHeader']))
            
            for category in audit_result.common_issues:
                story.append(Paragraph(f"<b>{category.category}</b>", self.styles['Heading3']))
                
                checks_data = [['Check', 'Status', 'Details']]
                for check in category.checks:
                    status_symbol = "✓" if check.status == "pass" else "✗"
                    status_color = "green" if check.status == "pass" else "red"
                    
                    checks_data.append([
                        check.name,
                        f"<font color='{status_color}'>{status_symbol} {check.status.upper()}</font>",
                        check.value or check.recommendation or ""
                    ])
                
                checks_table = Table(checks_data, colWidths=[2*inch, 1.5*inch, 3*inch])
                checks_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(checks_table)
                story.append(Spacer(1, 15))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise

    def _get_score_color(self, score: int) -> str:
        """Get color based on score"""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "orange"
        else:
            return "red"