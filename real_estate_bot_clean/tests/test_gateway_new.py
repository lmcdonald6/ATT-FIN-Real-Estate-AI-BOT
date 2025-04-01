"""Tests for the API Gateway following our hybrid data approach."""
import pytest
import asyncio
from datetime import datetime
from collections import defaultdict
from src.api.gateway import APIGateway, RequestType

@pytest.fixture
def gateway():
    """Create APIGateway instance."""
    return APIGateway()

@pytest.fixture
def property_request():
    """Create property search request with hybrid data configuration."""
    return {
        "request_id": "test_123",
        "zip_code": "37215",
        "limit": 5,
        "data_source": {
            "primary": "mock",  # Always start with mock data
            "enrichment": {
                "enabled": False,  # Control ATTOM API usage
                "fields": ["tax_data", "sales_history", "valuation"]
            }
        },
        "filters": {
            "min_price": 500000,
            "max_price": 1000000,
            "min_beds": 3,
            "min_baths": 2
        }
    }

@pytest.mark.asyncio
async def test_mock_data_primary(gateway: APIGateway, property_request):
    """Test mock data as primary source."""
    async with gateway:
        result, status = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            property_request
        )
        assert status == 200
        data = result["data"][0]
        assert data["source"] == "mock"
        assert data["confidence_score"] >= 0.9
        assert "encoding" in result
        assert result["encoding"] == "binary"

@pytest.mark.asyncio
async def test_attom_enrichment(gateway: APIGateway, property_request):
    """Test ATTOM API enrichment."""
    async with gateway:
        request = property_request.copy()
        request["data_source"]["enrichment"].update({
            "enabled": True,
            "fields": ["tax_data", "sales_history", "valuation"]
        })

        result, status = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            request
        )
        assert status == 200
        data = result["data"][0]
        
        # Verify hybrid approach
        assert data["source"] == "hybrid"
        assert "confidence_score" in data
        assert data["confidence_score"] >= 0.8  # Base expectation for hybrid data
        
        # Verify data enrichment
        assert "tax_data" in data
        assert "sales_history" in data
        assert "valuation" in data
        
        # Verify ATTOM usage tracking
        assert "attom_usage" in result["metadata"]
        usage = result["metadata"]["attom_usage"]
        assert "total_calls" in usage
        assert "remaining" in usage

@pytest.mark.asyncio
async def test_rate_limiting(gateway: APIGateway, property_request):
    """Test ATTOM API rate limiting."""
    async with gateway:
        # Set rate limit to max (400 reports/month)
        gateway.rate_limiters["attom_api"][datetime.now().month] = 400
        
        request = property_request.copy()
        request["data_source"]["enrichment"]["enabled"] = True
        
        result, status = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            request
        )
        assert status == 200
        data = result["data"][0]
        assert data["source"] == "mock"  # Should fallback to mock
        assert "rate_limit_fallback" in result["metadata"]

@pytest.mark.asyncio
async def test_caching(gateway: APIGateway, property_request):
    """Test caching behavior."""
    async with gateway:
        # First request
        result1, status1 = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            property_request
        )
        assert status1 == 200
        
        # Second request should use cache (24-hour TTL)
        result2, status2 = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            property_request
        )
        assert status2 == 200
        assert result2["metadata"]["cache_hit"] is True
        assert result2["data"][0]["data_freshness"] == "cached"

@pytest.mark.asyncio
async def test_protocol_optimization(gateway: APIGateway, property_request):
    """Test protocol optimization features."""
    async with gateway:
        result, status = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            property_request
        )
        assert status == 200
        # Binary encoding for efficient transfer
        assert "encoding" in result
        assert result["encoding"] == "binary"
        # Compression for large payloads
        assert "compression" in result["metadata"]
        # Request/Response correlation
        assert "request_correlation_id" in result["metadata"]

@pytest.mark.asyncio
async def test_error_handling(gateway: APIGateway, property_request):
    """Test error handling."""
    async with gateway:
        # Test with invalid zip code
        request = property_request.copy()
        request["zip_code"] = "invalid"
        
        result, status = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            request
        )
        assert status == 400
        assert "error" in result
        assert "validation_errors" in result
        assert "zip_code" in result["validation_errors"]

@pytest.mark.asyncio
async def test_attom_comprehensive_data(gateway: APIGateway, property_request):
    """Test comprehensive ATTOM data collection."""
    async with gateway:
        request = property_request.copy()
        request["data_source"]["enrichment"].update({
            "enabled": True,
            "fields": [
                "tax_data",
                "title_data",
                "foreclosure",
                "sales_history"
            ]
        })

        result, status = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            request
        )
        assert status == 200
        data = result["data"][0]

        # Verify all requested data is present with correct field mapping
        assert "tax_data" in data
        assert "title_data" in data
        assert "foreclosure" in data
        assert "sales_history" in data

        # Verify data structure
        assert "assessed_value" in data["tax_data"]
        assert "ownership_type" in data["title_data"]
        assert "status" in data["foreclosure"]
        assert "transactions" in data["sales_history"]

        # Check metadata
        assert "attom_endpoints_used" in result["metadata"]
        used_endpoints = result["metadata"]["attom_endpoints_used"]
        assert len(used_endpoints) == 5  # property + 4 enrichment endpoints

        # Verify hybrid approach with complete data
        assert data["source"] == "hybrid"
        assert "confidence_score" in data
        assert data["confidence_score"] >= 0.85  # Higher expectation for comprehensive data

@pytest.mark.asyncio
async def test_attom_rate_limit_distribution(gateway: APIGateway, property_request):
    """Test ATTOM API rate limit across endpoints."""
    async with gateway:
        request = property_request.copy()
        request["data_source"]["enrichment"].update({
            "enabled": True,
            "fields": ["tax_data", "title_data"]
        })

        # Make multiple requests with unique addresses
        for i in range(5):
            request["address"] = f"123{i} Main St"  # Make each request unique
            result, status = await gateway.handle_request(
                RequestType.PROPERTY_SEARCH,
                request
            )
            assert status == 200
            
            # Verify ATTOM usage tracking
            assert "attom_usage" in result["metadata"]
            usage = result["metadata"]["attom_usage"]
            assert usage["total_calls"] == i + 1  # Count should increment for unique requests
            assert usage["remaining"] == 400 - (i + 1)

        # Check rate limit counters - should match unique requests
        current_month = datetime.now().month
        total_calls = gateway.rate_limiters[RequestType.ATTOM_API.value][current_month]
        assert total_calls == 5  # One call per unique request

@pytest.mark.asyncio
async def test_attom_data_caching(gateway: APIGateway, property_request):
    """Test caching of ATTOM API responses."""
    async with gateway:
        request = property_request.copy()
        request["data_source"]["enrichment"].update({
            "enabled": True,
            "fields": ["tax_data"]
        })

        # First request
        result1, status1 = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            request
        )
        assert status1 == 200
        assert result1["data"][0]["source"] == "hybrid"
        
        # Second request should use cache
        result2, status2 = await gateway.handle_request(
            RequestType.PROPERTY_SEARCH,
            request
        )
        assert status2 == 200
        
        # Verify cache usage
        assert result2["metadata"]["cache_hit"] is True
        assert "data_freshness" in result2["data"][0]
        
        # Verify rate limit wasn't incremented for cached response
        current_month = datetime.now().month
        assert gateway.rate_limiters[RequestType.ATTOM_API.value][current_month] == 1  # Only from first request
