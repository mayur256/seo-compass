"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create analysis_jobs table
    op.create_table(
        'analysis_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create competitors table
    op.create_table(
        'competitors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('ranking_position', sa.Integer(), nullable=False),
        sa.Column('estimated_traffic', sa.Integer(), nullable=True),
    )
    
    # Create keywords table
    op.create_table(
        'keywords',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('term', sa.String(), nullable=False),
        sa.Column('search_volume', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.Float(), nullable=False),
        sa.Column('cpc', sa.Float(), nullable=True),
    )
    
    # Create content_drafts table
    op.create_table(
        'content_drafts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('page_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('meta_description', sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('content_drafts')
    op.drop_table('keywords')
    op.drop_table('competitors')
    op.drop_table('analysis_jobs')