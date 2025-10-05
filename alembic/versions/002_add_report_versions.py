"""Add report versions table

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_versions table
    op.create_table(
        'report_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('s3_zip_path', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for performance
    op.create_index('idx_report_versions_url', 'report_versions', ['url'])
    op.create_index('idx_report_versions_job_id', 'report_versions', ['job_id'])
    op.create_index('idx_report_versions_created_at', 'report_versions', ['created_at'])


def downgrade() -> None:
    op.drop_table('report_versions')