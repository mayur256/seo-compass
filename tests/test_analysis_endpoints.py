"""Tests for analysis endpoints with section filtering."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_analysis_results_with_section_filter():
    """Test analysis results endpoint with section filtering."""
    # First create a job
    with patch('app.tasks.tasks.process_analysis.delay'):
        create_response = client.post(
            "/v1/analyze",
            json={"url": "https://example.com"}
        )
        job_id = create_response.json()["job_id"]
    
    # Test section filtering
    test_cases = [
        ("competitors", "competitors"),
        ("keywords", "keywords"), 
        ("drafts", "content_drafts"),
        (None, "all")  # No section filter
    ]
    
    for section, expected_content in test_cases:
        params = {"section": section} if section else {}
        response = client.get(f"/v1/analyze/{job_id}", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "job_id" in data
        assert "competitors" in data
        assert "keywords" in data
        assert "content_drafts" in data


def test_get_analysis_results_nonexistent_job():
    """Test analysis results for non-existent job."""
    fake_job_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/v1/analyze/{fake_job_id}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_get_analysis_results_empty_report():
    """Test analysis results when no data is available yet."""
    # This would test the case where job exists but no analysis results yet
    # Implementation depends on your repository mock setup
    pass


def test_legacy_reports_endpoint():
    """Test that legacy reports endpoint still works."""
    # First create a job
    with patch('app.tasks.tasks.process_analysis.delay'):
        create_response = client.post(
            "/v1/analyze",
            json={"url": "https://example.com"}
        )
        job_id = create_response.json()["job_id"]
    
    # Test legacy endpoint
    response = client.get(f"/v1/reports/{job_id}")
    
    # Should work the same as the new endpoint
    assert response.status_code == 200
    data = response.json()
    
    assert "job_id" in data
    assert "competitors" in data
    assert "keywords" in data
    assert "content_drafts" in data


def test_analyze_endpoint_with_invalid_section():
    """Test analysis endpoint with invalid section parameter."""
    with patch('app.tasks.tasks.process_analysis.delay'):
        create_response = client.post(
            "/v1/analyze",
            json={"url": "https://example.com"}
        )
        job_id = create_response.json()["job_id"]
    
    # Test with invalid section
    response = client.get(f"/v1/analyze/{job_id}", params={"section": "invalid"})
    
    # Should still return 200 but with all sections
    assert response.status_code == 200
    data = response.json()
    
    assert "competitors" in data
    assert "keywords" in data
    assert "content_drafts" in data