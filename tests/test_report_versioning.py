"""Tests for report versioning and S3 integration."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime
from app.infrastructure.db.report_repository import ReportRepository
from app.infrastructure.s3_storage import S3StorageService
from app.domain.report_version import ReportVersion
from app.tasks.report_packaging_worker import _package_report_async


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def report_repo(mock_session):
    """Report repository fixture."""
    return ReportRepository(mock_session)


@pytest.fixture
def s3_service():
    """S3 service fixture."""
    return S3StorageService()


@pytest.mark.asyncio
async def test_create_version_increments_correctly(report_repo):
    """Test that version numbers increment correctly."""
    job_id = uuid4()
    url = "https://example.com"
    
    # Mock get_latest_version to return 2
    with patch.object(report_repo, 'get_latest_version', return_value=2):
        # Mock database operations
        report_repo.session.add = MagicMock()
        report_repo.session.commit = AsyncMock()
        report_repo.session.refresh = AsyncMock()
        
        # Mock the created version
        mock_version = MagicMock()
        mock_version.id = uuid4()
        mock_version.job_id = job_id
        mock_version.version = 3
        mock_version.url = url
        mock_version.status = "PENDING"
        mock_version.s3_zip_path = None
        mock_version.created_at = datetime.utcnow()
        mock_version.completed_at = None
        
        # Mock session.refresh to set the mock_version
        async def mock_refresh(obj):
            for attr, value in vars(mock_version).items():
                setattr(obj, attr, value)
        
        report_repo.session.refresh.side_effect = mock_refresh
        
        version = await report_repo.create_version(job_id, url)
        
        assert version.version == 3
        assert version.job_id == job_id
        assert version.url == url
        assert version.status == "PENDING"


@pytest.mark.asyncio
async def test_get_history_pagination(report_repo):
    """Test report history pagination."""
    # Mock database query results
    mock_versions = [
        MagicMock(
            id=uuid4(),
            job_id=uuid4(),
            version=i,
            url=f"https://example{i}.com",
            status="COMPLETED",
            s3_zip_path=f"path/to/file{i}.zip",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        for i in range(1, 6)
    ]
    
    # Mock session execute for both count and data queries
    count_result = MagicMock()
    count_result.scalar.return_value = 25
    
    data_result = MagicMock()
    data_result.scalars.return_value.all.return_value = mock_versions
    
    report_repo.session.execute = AsyncMock(side_effect=[count_result, data_result])
    
    versions, total = await report_repo.get_history(limit=5, offset=0)
    
    assert len(versions) == 5
    assert total == 25
    assert all(isinstance(v, ReportVersion) for v in versions)


@pytest.mark.asyncio
async def test_s3_upload_with_retry():
    """Test S3 upload with retry logic."""
    s3_service = S3StorageService()
    
    # Mock successful upload on second attempt
    mock_s3_client = AsyncMock()
    mock_s3_client.put_object = AsyncMock()
    
    # First call fails, second succeeds
    mock_s3_client.put_object.side_effect = [
        Exception("Network error"),
        None  # Success
    ]
    
    mock_session = AsyncMock()
    mock_session.client.return_value.__aenter__.return_value = mock_s3_client
    
    with patch('aioboto3.Session', return_value=mock_session):
        s3_key = await s3_service.upload_report_zip(
            b"test zip data",
            "https://example.com",
            "job123",
            1
        )
        
        assert s3_key is not None
        assert mock_s3_client.put_object.call_count == 2


@pytest.mark.asyncio
async def test_presigned_url_generation():
    """Test presigned URL generation."""
    s3_service = S3StorageService()
    
    mock_s3_client = AsyncMock()
    mock_s3_client.generate_presigned_url = AsyncMock(
        return_value="https://s3.amazonaws.com/bucket/key?signature=abc123"
    )
    
    mock_session = AsyncMock()
    mock_session.client.return_value.__aenter__.return_value = mock_s3_client
    
    with patch('aioboto3.Session', return_value=mock_session):
        url = await s3_service.get_presigned_url("test/key.zip")
        
        assert url.startswith("https://s3.amazonaws.com")
        assert "signature=" in url


@pytest.mark.asyncio
async def test_packaging_task_workflow():
    """Test complete packaging task workflow."""
    job_id = uuid4()
    version_id = uuid4()
    
    # Mock all dependencies
    with patch('app.tasks.report_packaging_worker.AsyncSessionLocal') as mock_session_local, \
         patch('app.tasks.report_packaging_worker.SQLAnalysisRepository') as mock_analysis_repo, \
         patch('app.tasks.report_packaging_worker.ReportRepository') as mock_report_repo, \
         patch('app.tasks.report_packaging_worker.ReportService') as mock_report_service, \
         patch('app.tasks.report_packaging_worker.S3StorageService') as mock_s3_service:
        
        # Setup mocks
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        
        mock_version = ReportVersion(
            id=version_id,
            job_id=job_id,
            version=1,
            url="https://example.com",
            status="PENDING"
        )
        
        mock_report_repo_instance = AsyncMock()
        mock_report_repo_instance.get_by_job_id.return_value = mock_version
        mock_report_repo_instance.update_status = AsyncMock()
        mock_report_repo_instance.update_s3_path = AsyncMock()
        mock_report_repo.return_value = mock_report_repo_instance
        
        mock_report_service_instance = AsyncMock()
        mock_report_service_instance.build_report_model.return_value = MagicMock()
        mock_report_service_instance.generate_files.return_value = b"zip data"
        mock_report_service.return_value = mock_report_service_instance
        
        mock_s3_service_instance = AsyncMock()
        mock_s3_service_instance.upload_report_zip.return_value = "s3/key/path.zip"
        mock_s3_service.return_value = mock_s3_service_instance
        
        # Run the packaging task
        await _package_report_async(job_id, version_id)
        
        # Verify workflow steps
        mock_report_repo_instance.update_status.assert_any_call(version_id, "PACKAGING")
        mock_report_repo_instance.update_status.assert_any_call(version_id, "UPLOADING")
        mock_report_repo_instance.update_status.assert_any_call(version_id, "COMPLETED")
        mock_report_repo_instance.update_s3_path.assert_called_once_with(version_id, "s3/key/path.zip")


@pytest.mark.asyncio
async def test_packaging_task_failure_handling():
    """Test packaging task failure handling."""
    job_id = uuid4()
    version_id = uuid4()
    
    with patch('app.tasks.report_packaging_worker.AsyncSessionLocal') as mock_session_local, \
         patch('app.tasks.report_packaging_worker.ReportRepository') as mock_report_repo:
        
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        
        mock_report_repo_instance = AsyncMock()
        mock_report_repo_instance.get_by_job_id.side_effect = Exception("Database error")
        mock_report_repo_instance.update_status = AsyncMock()
        mock_report_repo.return_value = mock_report_repo_instance
        
        # Run the packaging task and expect failure
        with pytest.raises(Exception, match="Database error"):
            await _package_report_async(job_id, version_id)
        
        # Verify failure was recorded
        mock_report_repo_instance.update_status.assert_called_with(version_id, "FAILED")


def test_report_history_api_endpoint():
    """Test report history API endpoint."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Mock the dependencies
    with patch('app.interfaces.http.v1.reports.get_report_repository') as mock_get_repo, \
         patch('app.interfaces.http.v1.reports.get_s3_service') as mock_get_s3:
        
        mock_repo = AsyncMock()
        mock_repo.get_history.return_value = ([], 0)
        mock_get_repo.return_value = mock_repo
        
        mock_s3 = AsyncMock()
        mock_get_s3.return_value = mock_s3
        
        response = client.get("/v1/reports/history?limit=10&page=1")
        
        # Should return 200 with empty results
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert data["pagination"]["total"] == 0