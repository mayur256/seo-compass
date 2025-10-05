"""Tests for LLM service."""

import pytest
from unittest.mock import patch
from app.services.llm_service import LLMService, PageDraft
from app.services.keyword_service import KeywordData
from app.services.competitor_service import CompetitorData


@pytest.mark.asyncio
async def test_generate_content_drafts():
    """Test content draft generation."""
    service = LLMService()
    
    keywords = [
        KeywordData(keyword="business services", search_volume=10000, difficulty=0.6),
        KeywordData(keyword="professional consulting", search_volume=8000, difficulty=0.7),
        KeywordData(keyword="expert solutions", search_volume=5000, difficulty=0.5),
    ]
    
    competitors = [
        CompetitorData(rank=1, url="https://competitor1.com", keyword="business", estimated_traffic=50000),
        CompetitorData(rank=2, url="https://competitor2.com", keyword="consulting", estimated_traffic=35000),
    ]
    
    try:
        drafts = await service.generate_content_drafts(keywords, competitors)
        
        assert len(drafts) == 3
        assert all(isinstance(d, PageDraft) for d in drafts)
        
        page_names = [d.page_name for d in drafts]
        assert "home" in page_names
        assert "services" in page_names
        assert "about" in page_names
        
        # Check that content contains keywords
        for draft in drafts:
            assert len(draft.content) > 100  # Substantial content
            assert "business services" in draft.content.lower()
            
    finally:
        await service.close()


@pytest.mark.asyncio
async def test_generate_content_with_api_key():
    """Test content generation with API key configured."""
    with patch('app.core.config.get_settings') as mock_settings:
        mock_settings.return_value.llm_api_key = "test-api-key"
        
        service = LLMService()
        
        keywords = [KeywordData(keyword="test keyword", search_volume=1000, difficulty=0.5)]
        competitors = []
        
        try:
            drafts = await service.generate_content_drafts(keywords, competitors)
            
            assert len(drafts) >= 1
            assert all(isinstance(d, PageDraft) for d in drafts)
            
        finally:
            await service.close()


def test_generate_homepage_content():
    """Test homepage content generation."""
    service = LLMService()
    
    keywords = ["business services", "professional consulting", "expert solutions"]
    
    try:
        content = service._generate_homepage_content(keywords)
        
        assert len(content) > 200
        assert "business services" in content.lower()
        assert "#" in content  # Has markdown headers
        assert "##" in content  # Has subheaders
        
    finally:
        pass  # No async cleanup needed for this test


def test_generate_services_content():
    """Test services page content generation."""
    service = LLMService()
    
    keywords = ["consulting", "strategy", "optimization", "analysis"]
    
    try:
        content = service._generate_services_content(keywords)
        
        assert len(content) > 300
        assert "# Our Professional Services" in content
        assert "consulting" in content.lower()
        assert "strategy" in content.lower()
        
        # Check that it has numbered services
        assert "## 1." in content
        assert "## 2." in content
        
    finally:
        pass


def test_generate_about_content():
    """Test about page content generation."""
    service = LLMService()
    
    keywords = ["business solutions"]
    
    try:
        content = service._generate_about_content(keywords)
        
        assert len(content) > 300
        assert "# About Our Company" in content
        assert "business solutions" in content.lower()
        assert "mission" in content.lower()
        assert "values" in content.lower()
        
    finally:
        pass