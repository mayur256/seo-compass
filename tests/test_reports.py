"""Tests for report endpoints and functionality."""

import io
import json
import zipfile
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.domain.entities import AnalysisJob, Report, Competitor, Keyword, ContentDraft
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_completed_job():
    """Mock completed analysis job."""
    job_id = uuid4()
    return AnalysisJob(
        id=job_id,
        url=\"https://example.com\",
        status=\"COMPLETED\",
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )


@pytest.fixture
def mock_report_data(mock_completed_job):
    \"\"\"Mock report data with competitors, keywords, and drafts.\"\"\"
    return Report(
        job_id=mock_completed_job.id,
        competitors=[
            Competitor(
                url=\"https://competitor1.com\",
                title=\"Competitor 1\",
                ranking_position=1,
                estimated_traffic=50000
            ),
            Competitor(
                url=\"https://competitor2.com\",
                title=\"Competitor 2\",
                ranking_position=2,
                estimated_traffic=35000
            )
        ],
        keywords=[
            Keyword(term=\"business services\", search_volume=10000, difficulty=0.6, cpc=2.50),
            Keyword(term=\"professional consulting\", search_volume=8000, difficulty=0.7, cpc=3.20),
            Keyword(term=\"expert solutions\", search_volume=5000, difficulty=0.5, cpc=1.80)
        ],
        content_drafts=[
            ContentDraft(
                page_type=\"home\",
                title=\"Homepage\",
                content=\"# Welcome to Your Business\\n\\nProfessional services...\",
                meta_description=\"Professional services\"
            ),
            ContentDraft(
                page_type=\"services\",
                title=\"Our Services\",
                content=\"# Our Services\\n\\nWe offer comprehensive...\",
                meta_description=\"Our services\"
            ),
            ContentDraft(
                page_type=\"about\",
                title=\"About Us\",
                content=\"# About Our Company\\n\\nLearn more about...\",
                meta_description=\"About us\"
            )
        ]
    )


def test_get_report_all_sections(mock_completed_job, mock_report_data):
    \"\"\"Test getting complete report with all sections.\"\"\"
    with patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_job', return_value=mock_completed_job), \\\n         patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_report', return_value=mock_report_data):\n        \n        response = client.get(f\"/v1/reports/{mock_completed_job.id}\")\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        # Check job metadata\n        assert data[\"job_id\"] == str(mock_completed_job.id)\n        assert data[\"url\"] == \"https://example.com\"\n        assert data[\"status\"] == \"COMPLETED\"\n        \n        # Check all sections are present\n        assert \"competitors\" in data\n        assert \"keywords\" in data\n        assert \"drafts\" in data\n        \n        # Check data counts\n        assert len(data[\"competitors\"]) == 2\n        assert len(data[\"keywords\"]) == 3\n        assert len(data[\"drafts\"]) == 3\n        \n        # Check competitor data structure\n        competitor = data[\"competitors\"][0]\n        assert \"rank\" in competitor\n        assert \"url\" in competitor\n        assert \"keyword\" in competitor\n        assert \"estimated_traffic\" in competitor\n        \n        # Check keyword data structure\n        keyword = data[\"keywords\"][0]\n        assert \"keyword\" in keyword\n        assert \"search_volume\" in keyword\n        assert \"difficulty\" in keyword\n        assert \"cpc\" in keyword\n        \n        # Check draft data structure\n        draft = data[\"drafts\"][0]\n        assert \"page_name\" in draft\n        assert \"content\" in draft


def test_get_report_section_keywords(mock_completed_job, mock_report_data):
    \"\"\"Test getting report with keywords section only.\"\"\"
    with patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_job', return_value=mock_completed_job), \\\n         patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_report', return_value=mock_report_data):\n        \n        response = client.get(f\"/v1/reports/{mock_completed_job.id}?section=keywords\")\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        # Check job metadata is present\n        assert data[\"job_id\"] == str(mock_completed_job.id)\n        assert data[\"status\"] == \"COMPLETED\"\n        \n        # Check only keywords section is present\n        assert \"keywords\" in data\n        assert data[\"competitors\"] is None\n        assert data[\"drafts\"] is None\n        \n        # Check keywords data\n        assert len(data[\"keywords\"]) == 3\n        assert data[\"keywords\"][0][\"keyword\"] == \"business services\"


def test_get_report_job_not_found():
    \"\"\"Test getting report for non-existent job.\"\"\"
    fake_job_id = uuid4()\n    \n    with patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_job', return_value=None):\n        response = client.get(f\"/v1/reports/{fake_job_id}\")\n        \n        assert response.status_code == 404\n        assert response.json()[\"detail\"] == \"Job not found\"


def test_get_report_job_not_completed():
    \"\"\"Test getting report for incomplete job.\"\"\"
    job_id = uuid4()\n    incomplete_job = AnalysisJob(\n        id=job_id,\n        url=\"https://example.com\",\n        status=\"IN_PROGRESS\",\n        created_at=datetime.utcnow()\n    )\n    \n    with patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_job', return_value=incomplete_job):\n        response = client.get(f\"/v1/reports/{job_id}\")\n        \n        assert response.status_code == 400\n        assert \"Report not ready\" in response.json()[\"detail\"]\n        assert \"IN_PROGRESS\" in response.json()[\"detail\"]


def test_download_zip_contains_files(mock_completed_job, mock_report_data):
    \"\"\"Test downloading ZIP file and validating contents.\"\"\"
    with patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_job', return_value=mock_completed_job), \\\n         patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_report', return_value=mock_report_data):\n        \n        response = client.get(f\"/v1/reports/{mock_completed_job.id}/download\")\n        \n        assert response.status_code == 200\n        assert response.headers[\"content-type\"] == \"application/zip\"\n        assert \"attachment\" in response.headers[\"content-disposition\"]\n        assert f\"seo_compass_report_{mock_completed_job.id}.zip\" in response.headers[\"content-disposition\"]\n        \n        # Read ZIP contents\n        zip_bytes = response.content\n        zip_file = zipfile.ZipFile(io.BytesIO(zip_bytes))\n        \n        # Check expected files are present\n        file_list = zip_file.namelist()\n        assert \"competitors.csv\" in file_list\n        assert \"keywords.csv\" in file_list\n        assert \"drafts/home.txt\" in file_list\n        assert \"drafts/services.txt\" in file_list\n        assert \"drafts/about.txt\" in file_list\n        assert \"report_metadata.json\" in file_list\n        \n        # Check competitors CSV content\n        competitors_csv = zip_file.read(\"competitors.csv\").decode('utf-8')\n        assert \"rank,url,keyword,estimated_traffic\" in competitors_csv\n        assert \"competitor1.com\" in competitors_csv\n        \n        # Check keywords CSV content\n        keywords_csv = zip_file.read(\"keywords.csv\").decode('utf-8')\n        assert \"keyword,search_volume,difficulty,cpc\" in keywords_csv\n        assert \"business services\" in keywords_csv\n        \n        # Check draft content\n        home_content = zip_file.read(\"drafts/home.txt\").decode('utf-8')\n        assert \"Welcome to Your Business\" in home_content\n        \n        # Check metadata JSON\n        metadata_json = zip_file.read(\"report_metadata.json\").decode('utf-8')\n        metadata = json.loads(metadata_json)\n        assert metadata[\"job_id\"] == str(mock_completed_job.id)\n        assert metadata[\"url\"] == \"https://example.com\"\n        assert metadata[\"counts\"][\"competitors\"] == 2\n        assert metadata[\"counts\"][\"keywords\"] == 3\n        assert metadata[\"counts\"][\"drafts\"] == 3


def test_download_zip_job_not_completed():
    \"\"\"Test downloading ZIP for incomplete job.\"\"\"
    job_id = uuid4()\n    incomplete_job = AnalysisJob(\n        id=job_id,\n        url=\"https://example.com\",\n        status=\"QUEUED\",\n        created_at=datetime.utcnow()\n    )\n    \n    with patch('app.infrastructure.db.repositories.SQLAnalysisRepository.get_job', return_value=incomplete_job):\n        response = client.get(f\"/v1/reports/{job_id}/download\")\n        \n        assert response.status_code == 400\n        assert \"Report not ready\" in response.json()[\"detail\"]