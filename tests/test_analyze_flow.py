import pytest
import time
from uuid import UUID
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_analyze_endpoint_creates_job():
    """Test that POST /v1/analyze creates a job successfully."""
    with patch('app.tasks.tasks.process_analysis.delay') as mock_delay:
        response = client.post(
            "/v1/analyze",
            json={"url": "https://example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "job_id" in data
        assert "status" in data
        assert data["status"] == "QUEUED"
        
        # Validate job_id is a valid UUID
        job_id = UUID(data["job_id"])
        assert isinstance(job_id, UUID)
        
        # Verify Celery task was called
        mock_delay.assert_called_once()


def test_analyze_endpoint_invalid_url():
    """Test that invalid URLs are rejected."""
    response = client.post(
        "/v1/analyze",
        json={"url": "not-a-valid-url"}
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_get_job_status_existing_job():
    """Test retrieving status of an existing job."""
    # First create a job
    with patch('app.tasks.tasks.process_analysis.delay'):
        create_response = client.post(
            "/v1/analyze",
            json={"url": "https://example.com"}
        )
        job_id = create_response.json()["job_id"]
    
    # Then get its status
    response = client.get(f"/v1/jobs/{job_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["job_id"] == job_id
    assert data["url"] == "https://example.com"
    assert data["status"] in ["QUEUED", "IN_PROGRESS", "COMPLETED", "FAILED"]
    assert "created_at" in data


def test_get_job_status_nonexistent_job():
    """Test that non-existent job returns 404."""
    fake_job_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/v1/jobs/{fake_job_id}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_get_report_completed_job():
    """Test retrieving report for a completed job."""
    # This test would require the job to actually complete
    # For now, we'll test the endpoint structure
    fake_job_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/v1/reports/{fake_job_id}")
    
    # Should return 404 since job doesn't exist
    assert response.status_code == 404


@pytest.mark.integration
def test_full_analysis_flow():
    """Integration test for the complete analysis flow."""
    # This test requires actual database and Celery worker
    # Skip in unit test environment
    pytest.skip("Integration test - requires full environment")
    
    # Create job
    response = client.post(
        "/v1/analyze",
        json={"url": "https://example.com"}
    )
    job_id = response.json()["job_id"]
    
    # Wait for processing
    time.sleep(5)
    
    # Check final status
    status_response = client.get(f"/v1/jobs/{job_id}")
    assert status_response.json()["status"] == "COMPLETED"
    
    # Get report
    report_response = client.get(f"/v1/reports/{job_id}")
    assert report_response.status_code == 200
    
    report_data = report_response.json()
    assert "competitors" in report_data
    assert "keywords" in report_data
    assert "content_drafts" in report_data