"""Tests for keyword service."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.keyword_service import KeywordService, KeywordData


@pytest.mark.asyncio
async def test_extract_keywords_success():
    """Test successful keyword extraction."""
    service = KeywordService()
    
    mock_html = """
    <html>
        <head>
            <title>Professional Business Services</title>
            <meta name="description" content="Expert consulting and business solutions">
        </head>
        <body>
            <h1>Business Consulting Services</h1>
            <p>We provide professional consulting services for businesses.</p>
            <p>Our expert team delivers business solutions and consulting expertise.</p>
        </body>
    </html>
    """
    
    with patch.object(service, '_fetch_html', return_value=mock_html):
        try:
            keywords = await service.extract_keywords("https://example.com")
            
            assert len(keywords) > 0
            assert all(isinstance(k, KeywordData) for k in keywords)
            assert all(k.search_volume > 0 for k in keywords)
            assert all(0 <= k.difficulty <= 1 for k in keywords)
            
            # Check that business-related keywords are extracted
            keyword_terms = [k.keyword for k in keywords]
            assert any("business" in term.lower() for term in keyword_terms)
            
        finally:
            await service.close()


@pytest.mark.asyncio
async def test_extract_keywords_http_failure():
    """Test keyword extraction when HTTP request fails."""
    service = KeywordService()
    
    with patch.object(service, '_fetch_html', side_effect=Exception("HTTP error")):
        try:
            keywords = await service.extract_keywords("https://example.com")
            
            # Should return mock keywords as fallback
            assert len(keywords) > 0
            assert all(isinstance(k, KeywordData) for k in keywords)
            
        finally:
            await service.close()


@pytest.mark.asyncio
async def test_analyze_keyword_frequency():
    """Test keyword frequency analysis."""
    service = KeywordService()
    
    text = "business services professional consulting business solutions expert consulting"
    
    try:
        keywords = service._analyze_keyword_frequency(text)
        
        assert len(keywords) > 0
        
        # Check that frequent words appear first
        keyword_dict = dict(keywords)
        assert "business" in keyword_dict
        assert "consulting" in keyword_dict
        
        # Business should have higher frequency than single occurrence words
        business_freq = keyword_dict.get("business", 0)
        consulting_freq = keyword_dict.get("consulting", 0)
        assert business_freq >= 2
        assert consulting_freq >= 2
        
    finally:
        await service.close()


@pytest.mark.asyncio
async def test_generate_mock_keywords():
    """Test mock keyword generation."""
    service = KeywordService()
    
    try:
        keywords = await service._generate_mock_keywords()
        
        assert len(keywords) == 8
        assert all(isinstance(k, KeywordData) for k in keywords)
        assert all(k.search_volume >= 1000 for k in keywords)
        assert all(0.2 <= k.difficulty <= 0.8 for k in keywords)
        
    finally:
        await service.close()