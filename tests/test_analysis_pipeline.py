"""Integration tests for the analysis pipeline."""

import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from app.tasks.tasks import _process_analysis_async
from app.infrastructure.db.repositories import SQLAnalysisRepository


@pytest.mark.asyncio
async def test_analysis_pipeline_success():
    """Test successful analysis pipeline execution."""
    job_id = uuid4()
    url = "https://example.com"
    
    # Mock all external services
    with patch('app.services.competitor_service.CompetitorService') as mock_competitor_service, \
         patch('app.services.keyword_service.KeywordService') as mock_keyword_service, \
         patch('app.services.llm_service.LLMService') as mock_llm_service, \
         patch('app.infrastructure.db.base.AsyncSessionLocal') as mock_session:
        
        # Setup mocks
        mock_competitor_instance = AsyncMock()
        mock_keyword_instance = AsyncMock()
        mock_llm_instance = AsyncMock()
        
        mock_competitor_service.return_value = mock_competitor_instance
        mock_keyword_service.return_value = mock_keyword_instance
        mock_llm_service.return_value = mock_llm_instance
        
        # Mock service responses
        mock_competitor_instance.discover_competitors.return_value = []
        mock_keyword_instance.extract_keywords.return_value = []
        mock_llm_instance.generate_content_drafts.return_value = []
        
        # Mock repository
        mock_repository = AsyncMock()
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        
        with patch('app.infrastructure.db.repositories.SQLAnalysisRepository', return_value=mock_repository):
            # Run the pipeline
            await _process_analysis_async(job_id, url)
            
            # Verify all steps were called
            mock_repository.update_status.assert_any_call(job_id, "IN_PROGRESS")
            mock_repository.set_completed.assert_called_once_with(job_id)
            mock_competitor_instance.discover_competitors.assert_called_once_with(url)
            mock_keyword_instance.extract_keywords.assert_called_once_with(url)
            mock_llm_instance.generate_content_drafts.assert_called_once()


@pytest.mark.asyncio
async def test_analysis_pipeline_failure():
    """Test analysis pipeline failure handling."""
    job_id = uuid4()
    url = "https://example.com"
    
    with patch('app.services.competitor_service.CompetitorService') as mock_competitor_service, \
         patch('app.infrastructure.db.base.AsyncSessionLocal') as mock_session:
        
        # Setup competitor service to fail
        mock_competitor_instance = AsyncMock()
        mock_competitor_service.return_value = mock_competitor_instance
        mock_competitor_instance.discover_competitors.side_effect = Exception("Service failure")
        
        # Mock repository
        mock_repository = AsyncMock()
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        
        with patch('app.infrastructure.db.repositories.SQLAnalysisRepository', return_value=mock_repository):
            # Run the pipeline and expect failure
            with pytest.raises(Exception, match="Service failure"):
                await _process_analysis_async(job_id, url)
            
            # Verify failure was handled
            mock_repository.update_status.assert_any_call(job_id, "FAILED")


@pytest.mark.asyncio
async def test_analysis_pipeline_service_cleanup():
    """Test that services are properly cleaned up."""
    job_id = uuid4()
    url = "https://example.com"
    
    with patch('app.services.competitor_service.CompetitorService') as mock_competitor_service, \
         patch('app.services.keyword_service.KeywordService') as mock_keyword_service, \
         patch('app.services.llm_service.LLMService') as mock_llm_service, \
         patch('app.infrastructure.db.base.AsyncSessionLocal') as mock_session:
        
        # Setup mocks
        mock_competitor_instance = AsyncMock()
        mock_keyword_instance = AsyncMock()
        mock_llm_instance = AsyncMock()
        
        mock_competitor_service.return_value = mock_competitor_instance
        mock_keyword_service.return_value = mock_keyword_instance
        mock_llm_service.return_value = mock_llm_instance
        
        # Mock service responses
        mock_competitor_instance.discover_competitors.return_value = []
        mock_keyword_instance.extract_keywords.return_value = []
        mock_llm_instance.generate_content_drafts.return_value = []
        
        # Mock repository
        mock_repository = AsyncMock()
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        
        with patch('app.infrastructure.db.repositories.SQLAnalysisRepository', return_value=mock_repository):
            await _process_analysis_async(job_id, url)
            
            # Verify cleanup was called
            mock_competitor_instance.close.assert_called_once()
            mock_keyword_instance.close.assert_called_once()
            mock_llm_instance.close.assert_called_once()