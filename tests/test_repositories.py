import pytest
from uuid import uuid4
from app.infrastructure.db.repositories import SQLAnalysisRepository
from app.infrastructure.db.base import AsyncSessionLocal


@pytest.mark.asyncio
async def test_create_job():
    """Test job creation in repository."""
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        url = "https://example.com"
        job = await repository.create_job(url)
        
        assert job.url == url
        assert job.status == "QUEUED"
        assert job.id is not None
        assert job.created_at is not None


@pytest.mark.asyncio
async def test_get_job():
    """Test job retrieval from repository."""
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        # Create a job first
        url = "https://example.com"
        created_job = await repository.create_job(url)
        
        # Retrieve it
        retrieved_job = await repository.get_job(created_job.id)
        
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id
        assert retrieved_job.url == url
        assert retrieved_job.status == "QUEUED"


@pytest.mark.asyncio
async def test_update_status():
    """Test job status update."""
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        # Create a job
        job = await repository.create_job("https://example.com")
        
        # Update status
        await repository.update_status(job.id, "IN_PROGRESS")
        
        # Verify update
        updated_job = await repository.get_job(job.id)
        assert updated_job.status == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_add_mock_data():
    """Test adding mock data to job."""
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        # Create a job
        job = await repository.create_job("https://example.com")
        
        # Add mock data
        await repository.add_mock_data(job.id)
        
        # Verify data was added by getting report
        report = await repository.get_report(job.id)
        
        assert report is not None
        assert len(report.competitors) == 3
        assert len(report.keywords) == 3
        assert len(report.content_drafts) == 3


@pytest.mark.asyncio
async def test_set_completed():
    """Test marking job as completed."""
    async with AsyncSessionLocal() as session:
        repository = SQLAnalysisRepository(session)
        
        # Create a job
        job = await repository.create_job("https://example.com")
        
        # Mark as completed
        await repository.set_completed(job.id)
        
        # Verify completion
        completed_job = await repository.get_job(job.id)
        assert completed_job.status == "COMPLETED"
        assert completed_job.completed_at is not None