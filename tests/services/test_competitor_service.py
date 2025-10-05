"""Tests for competitor service."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.competitor_service import CompetitorService, CompetitorData


@pytest.mark.asyncio
async def test_discover_competitors_mock_data():
    """Test competitor discovery with mock data."""
    service = CompetitorService()
    
    try:
        competitors = await service.discover_competitors("https://example.com")
        
        assert len(competitors) == 5
        assert all(isinstance(c, CompetitorData) for c in competitors)
        assert all(c.rank > 0 for c in competitors)
        assert all(c.url.startswith("https://") for c in competitors)
        assert all(c.estimated_traffic > 0 for c in competitors)
        
    finally:
        await service.close()


@pytest.mark.asyncio
async def test_discover_competitors_with_api_key():
    """Test competitor discovery with API key configured."""
    with patch('app.core.config.get_settings') as mock_settings:
        mock_settings.return_value.serp_api_key = "test-api-key"
        
        service = CompetitorService()
        
        try:
            competitors = await service.discover_competitors("https://example.com")
            
            assert len(competitors) >= 1
            assert all(isinstance(c, CompetitorData) for c in competitors)
            
        finally:
            await service.close()


@pytest.mark.asyncio
async def test_discover_competitors_retry_logic():
    """Test retry logic on failure."""
    service = CompetitorService()
    
    # Mock the _generate_mock_competitors to fail twice, then succeed
    call_count = 0
    
    async def mock_generate_competitors(url):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise Exception("API failure")
        return [CompetitorData(rank=1, url="https://test.com", keyword="test", estimated_traffic=1000)]
    
    with patch.object(service, '_generate_mock_competitors', side_effect=mock_generate_competitors):
        try:
            competitors = await service.discover_competitors("https://example.com")
            assert len(competitors) == 1
            assert call_count == 3  # Failed twice, succeeded on third attempt
            
        finally:
            await service.close()


@pytest.mark.asyncio
async def test_discover_competitors_max_retries_exceeded():
    """Test behavior when max retries are exceeded."""
    service = CompetitorService()
    
    with patch.object(service, '_generate_mock_competitors', side_effect=Exception("Persistent failure")):
        try:
            with pytest.raises(Exception, match="Persistent failure"):
                await service.discover_competitors("https://example.com")
                
        finally:
            await service.close()