"""
Test suite for API Gateway implementation with hybrid data approach.
Tests integration with our hybrid data approach and protocol optimization.
"""
import pytest
from datetime import datetime
from collections import defaultdict
from src.api.gateway import APIGateway, RequestType

@pytest.fixture
async def gateway():
    """Create APIGateway instance."""
    gateway = APIGateway()
    await gateway.__aenter__()
    try:
        yield gateway
    finally:
        await gateway.__aexit__(None, None, None)

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
async def test_mock_data_primary(gateway, property_request):
    """Test mock data as primary source."""
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        property_request
    )
    assert status == 200
    assert "data" in result
    data = result["data"][0]
    assert data["source"] == "mock"
    assert data["confidence_score"] >= 0.9
    assert data["data_freshness"] == "current"

@pytest.mark.asyncio
async def test_attom_enrichment(gateway, property_request):
    """Test ATTOM API enrichment."""
    property_request["data_source"]["enrichment"]["enabled"] = True
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        property_request
    )
    assert status == 200
    data = result["data"][0]
    assert data["source"] == "hybrid"
    assert all(field in data for field in 
              property_request["data_source"]["enrichment"]["fields"])
    assert data["confidence_score"] > 0.95

@pytest.mark.asyncio
async def test_rate_limiting(gateway, property_request):
    """Test rate limiting with ATTOM API."""
    property_request["data_source"]["enrichment"]["enabled"] = True
    
    # Simulate rate limit exceeded
    gateway._rate_limiters["attom_api"] = defaultdict(int)
    gateway._rate_limiters["attom_api"][datetime.now().month] = 400
    
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        property_request
    )
    assert status == 200
    data = result["data"][0]
    # Should fallback to mock data
    assert data["source"] == "mock"
    assert "rate_limit_fallback" in result["metadata"]

"""
Tests for the enhanced API Gateway implementation.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import jwt
from src.api.gateway import (
    APIGateway,
    RequestType,
    RequestMetrics,
    RATE_LIMITS
)

@pytest.fixture
async def gateway():
    """Create API Gateway instance for testing."""
    gw = APIGateway()
    async with gw as gateway:
        # Initialize mock data source for testing
        gateway._data_source = "mock"  # Default to mock data for tests
        gateway._metrics = {}  # Reset metrics
        gateway._cache = {}   # Reset cache
        
        # Pre-populate cache with mock data following our hybrid approach
        mock_data = {
            RequestType.PROPERTY_SEARCH: {
                "data": [
                    {
                        "id": "mock_1",
                        "address": "123 Test St",
                        "price": 500000,
                        "beds": 3,
                        "baths": 2,
                        "sqft": 2000,
                        "source": "mock",
                        "confidence_score": 0.95
                    }
                ],
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            },
            RequestType.MARKET_ANALYSIS: {
                "data": {
                    "median_price": 550000,
                    "price_trend": 0.05,
                    "market_strength": 0.8,
                    "source": "mock",
                    "confidence_score": 0.9,
                    "metrics_freshness": "current"
                },
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            },
            RequestType.LEAD_SCORING: {
                "data": {
                    "score": 85,
                    "factors": ["equity", "market_strength"],
                    "source": "mock",
                    "confidence_score": 0.85,
                    "validation_status": "passed"
                },
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            },
            RequestType.DEAL_ANALYSIS: {
                "data": {
                    "roi": 0.15,
                    "arv": 600000,
                    "repair_cost": 50000,
                    "source": "mock",
                    "confidence_score": 0.88,
                    "market_validation": "verified"
                },
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            }
        }
        
        # Cache mock responses with proper TTL and compression
        for request_type, data in mock_data.items():
            cache_key = gateway._generate_cache_key(request_type, {"mock": True})
            gateway._cache[cache_key] = (datetime.now(), data)
        
        yield gateway

@pytest.fixture
def auth_token():
    """Generate valid JWT token for testing."""
    return jwt.encode(
        {"user_id": "test_user"},
        "your-secret-key",
        algorithm="HS256"
    )

@pytest.fixture
def sample_property_payload():
    """Sample property search payload."""
    return {
        "zip_code": "12345",
        "limit": 10,
        "property_type": "single_family",
        "data_source_preference": "mock"  # Explicitly request mock data for testing
    }

@pytest.fixture
def sample_market_payload():
    """Sample market analysis payload."""
    return {
        "zip_code": "12345",
        "metrics": [
            "median_price",
            "price_trend",
            "market_strength"
        ],
        "data_source_preference": "mock"  # Explicitly request mock data for testing
    }

@pytest.mark.asyncio
async def test_request_handling_success(gateway, sample_property_payload):
    """Test successful request handling."""
    async for gateway_instance in gateway:
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        
        assert status == 200
        assert "message" in response
        assert isinstance(response["message"], str)

@pytest.mark.asyncio
async def test_authentication(gateway, sample_property_payload):
    """Test authentication handling."""
    async for gateway_instance in gateway:
        # Test with invalid token
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload,
            "invalid_token"
        )
        assert status == 401
        
        # Test with valid token
        valid_token = jwt.encode(
            {"user_id": "test_user"},
            "your-secret-key",
            algorithm="HS256"
        )
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload,
            valid_token
        )
        assert status == 200

@pytest.mark.asyncio
async def test_rate_limiting(gateway, sample_property_payload):
    """Test rate limiting functionality."""
    async for gateway_instance in gateway:
        # Make requests up to limit
        for _ in range(RATE_LIMITS["property_search"]):
            response, status = await gateway_instance.handle_request(
                RequestType.PROPERTY_SEARCH,
                sample_property_payload
            )
            assert status == 200
        
        # Next request should be rate limited
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        assert status == 429
        assert "Rate limit exceeded" in response["error"]

@pytest.mark.asyncio
async def test_caching(gateway, sample_property_payload):
    """Test response caching."""
    async for gateway_instance in gateway:
        # First request
        response1, status1 = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        assert status1 == 200
        
        # Second request with same payload should hit cache
        response2, status2 = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        assert status2 == 200
        assert response1 == response2
        
        # Verify cache metrics
        metrics = gateway_instance._metrics
        cache_hits = [m for m in metrics.values() if m.cache_hit]
        assert len(cache_hits) > 0

@pytest.mark.asyncio
async def test_circuit_breaker(gateway, sample_property_payload):
    """Test circuit breaker functionality."""
    async for gateway_instance in gateway:
        # Force circuit to open by causing failures
        for _ in range(10):
            try:
                await gateway_instance._process_request(
                    RequestType.PROPERTY_SEARCH,
                    {"invalid": "payload"},  # Invalid payload to cause failure
                    "test_request"
                )
            except:
                pass
        
        # Verify circuit is open
        assert gateway_instance._is_circuit_open(RequestType.PROPERTY_SEARCH)
        
        # Wait for circuit timeout
        await asyncio.sleep(0.1)  # Reduced for testing
        
        # Verify circuit is closed after timeout
        assert not gateway_instance._is_circuit_open(RequestType.PROPERTY_SEARCH)

@pytest.mark.asyncio
async def test_request_metrics(gateway, sample_property_payload):
    """Test request metrics tracking."""
    async for gateway_instance in gateway:
        request_id = gateway_instance._generate_request_id(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        
        # Verify metrics
        metrics = gateway_instance._metrics[response["request_id"]]
        assert isinstance(metrics, RequestMetrics)
        assert metrics.request_type == RequestType.PROPERTY_SEARCH
        assert metrics.status_code == 200
        assert metrics.data_source == "mock"
        assert metrics.response_time is not None

@pytest.mark.asyncio
async def test_protocol_optimization(gateway, sample_property_payload):
    """Test protocol optimization features."""
    async for gateway_instance in gateway:
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        assert status == 200
        
        # Verify binary encoding
        assert response["encoding"] == "binary"
        
        # Verify selective field inclusion
        data = response["data"][0]
        essential_fields = {
            "property_id", "address", "price",
            "source", "confidence_score", "data_freshness"
        }
        assert all(field in data for field in essential_fields)
        
        # Verify compression for large payloads
        if len(response["data"]) > 10:
            assert response["compression"] == "enabled"
        
        # Verify request correlation
        assert "request_id" in response
        metrics = gateway_instance._metrics[response["request_id"]]
        assert metrics.response_time is not None

@pytest.mark.asyncio
async def test_error_handling(gateway, sample_property_payload):
    """Test error handling."""
    async for gateway_instance in gateway:
        # Test with invalid request type
        with pytest.raises(ValueError):
            await gateway_instance.handle_request(
                "INVALID_TYPE",  # type: ignore
                {}
            )
        
        # Test with missing required payload
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            {}  # Empty payload
        )
        assert status == 500
        assert "error" in response

@pytest.mark.asyncio
async def test_request_correlation(gateway, sample_property_payload):
    """Test request correlation and tracing."""
    async for gateway_instance in gateway:
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        
        # Verify response contains request ID
        assert "request_id" in response
        request_id = response["request_id"]
        
        # Verify metrics exist for request
        assert request_id in gateway_instance._metrics
        metrics = gateway_instance._metrics[request_id]
        assert metrics.request_type == RequestType.PROPERTY_SEARCH

@pytest.mark.asyncio
async def test_cache_expiration(gateway, sample_property_payload):
    """Test cache expiration."""
    async for gateway_instance in gateway:
        # First request
        response1, status1 = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        
        # Second request should use cache
        response2, status2 = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_payload
        )
        assert status2 == 200
        
        # Verify cache metrics
        metrics = gateway_instance._metrics
        cache_hits = [m for m in metrics.values() if m.cache_hit]
        assert len(cache_hits) > 0

@pytest.mark.asyncio
async def test_market_analysis(gateway, sample_market_payload):
    """Test market analysis integration."""
    async for gateway_instance in gateway:
        response, status = await gateway_instance.handle_request(
            RequestType.MARKET_ANALYSIS,
            sample_market_payload
        )
        assert status == 200
        assert "message" in response

@pytest.mark.asyncio
async def test_lead_scoring(gateway):
    """Test lead scoring integration."""
    async for gateway_instance in gateway:
        payload = {
            "property_data": {
                "estimated_value": 500000,
                "last_sale_date": "2020-01-01",
                "equity_percentage": 0.4
            },
            "market_data": {
                "median_price": 550000,
                "market_strength": 0.8
            },
            "owner_data": {
                "age": 65,
                "income_level": "medium"
            },
            "data_source_preference": "mock"  # Explicitly request mock data for testing
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.LEAD_SCORING,
            payload
        )
        assert status == 200
        assert "message" in response

@pytest.mark.asyncio
async def test_deal_analysis(gateway):
    """Test deal analysis integration."""
    async for gateway_instance in gateway:
        payload = {
            "property_id": "test123",
            "purchase_price": 400000,
            "repair_estimate": 50000,
            "arv": 600000,
            "data_source_preference": "mock"  # Explicitly request mock data for testing
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.DEAL_ANALYSIS,
            payload
        )
        assert status == 200
        assert "message" in response

"""
Tests for the enhanced API Gateway implementation.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import jwt
from src.api.gateway import (
    APIGateway,
    RequestType,
    RequestMetrics,
    RATE_LIMITS
)

@pytest.fixture
async def gateway():
    """Create API Gateway instance for testing."""
    gw = APIGateway()
    async with gw as gateway:
        # Initialize mock data source for testing
        gateway._data_source = "mock"  # Default to mock data for tests
        gateway._metrics = {}  # Reset metrics
        gateway._cache = {}   # Reset cache
        
        # Pre-populate cache with mock data following our hybrid approach
        mock_data = {
            RequestType.PROPERTY_SEARCH: {
                "data": [
                    {
                        "id": "mock_1",
                        "address": "123 Test St",
                        "price": 500000,
                        "beds": 3,
                        "baths": 2,
                        "sqft": 2000,
                        "source": "mock",
                        "confidence_score": 0.95
                    }
                ],
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            },
            RequestType.MARKET_ANALYSIS: {
                "data": {
                    "median_price": 550000,
                    "price_trend": 0.05,
                    "market_strength": 0.8,
                    "source": "mock",
                    "confidence_score": 0.9,
                    "metrics_freshness": "current"
                },
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            },
            RequestType.LEAD_SCORING: {
                "data": {
                    "score": 85,
                    "factors": ["equity", "market_strength"],
                    "source": "mock",
                    "confidence_score": 0.85,
                    "validation_status": "passed"
                },
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            },
            RequestType.DEAL_ANALYSIS: {
                "data": {
                    "roi": 0.15,
                    "arv": 600000,
                    "repair_cost": 50000,
                    "source": "mock",
                    "confidence_score": 0.88,
                    "market_validation": "verified"
                },
                "message": "Success",
                "request_id": "mock_request",
                "cache_status": "fresh",
                "data_source": "mock"
            }
        }
        
        # Cache mock responses with proper TTL and compression
        for request_type, data in mock_data.items():
            cache_key = gateway._generate_cache_key(request_type, {"mock": True})
            gateway._cache[cache_key] = (datetime.now(), data)
        
        yield gateway

@pytest.fixture
def auth_token():
    """Generate valid JWT token for testing."""
    return jwt.encode(
        {"user_id": "test_user"},
        "your-secret-key",
        algorithm="HS256"
    )

@pytest.fixture
def sample_property_request():
    """Sample property search request."""
    return {
        "zip_code": "37215",
        "limit": 5,
        "request_id": "test_123",
        "filters": {
            "min_price": 500000,
            "max_price": 1000000,
            "min_beds": 3,
            "min_baths": 2
        },
        "data_source_preference": "mock"  # Explicitly request mock data for testing
    }

@pytest.fixture
def sample_market_request():
    """Sample market analysis request."""
    return {
        "zip_code": "37215",
        "request_id": "test_456",
        "metrics": [
            "median_price",
            "price_trend",
            "market_strength"
        ],
        "data_source_preference": "mock"  # Explicitly request mock data for testing
    }

@pytest.mark.asyncio
async def test_property_search_request(gateway, sample_property_request):
    """Test property search request handling."""
    async for gateway_instance in gateway:
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            sample_property_request
        )
        assert status == 200
        assert "data" in response
        assert "request_id" in response

@pytest.mark.asyncio
async def test_market_analysis_request(gateway, sample_market_request):
    """Test market analysis request handling."""
    async for gateway_instance in gateway:
        response, status = await gateway_instance.handle_request(
            RequestType.MARKET_ANALYSIS,
            sample_market_request
        )
        assert status == 200
        assert "data" in response
        assert "request_id" in response

@pytest.mark.asyncio
async def test_rate_limiting(gateway):
    """Test rate limiting functionality."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        
        # Make requests up to limit
        for _ in range(RATE_LIMITS["property_search"]):
            response, status = await gateway_instance.handle_request(
                RequestType.PROPERTY_SEARCH,
                payload
            )
            assert status == 200
        
        # Next request should be rate limited
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        assert status == 429
        assert "Rate limit exceeded" in response["error"]

@pytest.mark.asyncio
async def test_parameter_validation(gateway):
    """Test parameter validation."""
    async for gateway_instance in gateway:
        # Test with missing required parameter
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            {}  # Empty payload
        )
        assert status == 500
        assert "error" in response
        assert "Missing required fields" in response["error"]

@pytest.mark.asyncio
async def test_metrics_tracking(gateway):
    """Test request metrics tracking."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        request_id = gateway_instance._generate_request_id(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        # Verify metrics
        metrics = gateway_instance._metrics[request_id]
        assert isinstance(metrics, RequestMetrics)
        assert metrics.start_time is not None
        assert metrics.end_time is not None
        assert metrics.status_code == 200
        assert metrics.error is None

@pytest.mark.asyncio
async def test_error_handling(gateway):
    """Test error handling."""
    async for gateway_instance in gateway:
        # Test with invalid request type
        with pytest.raises(ValueError):
            await gateway_instance.handle_request(
                "INVALID_TYPE",  # type: ignore
                {}
            )
        
        # Test with missing required payload
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            {}  # Empty payload
        )
        assert status == 500
        assert "error" in response

@pytest.mark.asyncio
async def test_data_source_tracking(gateway):
    """Test data source tracking."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        # Verify data source is tracked
        request_id = response["request_id"]
        metrics = gateway_instance._metrics[request_id]
        assert metrics.data_source in ["mock", "attom"]

@pytest.mark.asyncio
async def test_request_routing(gateway):
    """Test request routing."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        
        for request_type in [
            RequestType.PROPERTY_SEARCH,
            RequestType.MARKET_ANALYSIS,
            RequestType.LEAD_SCORING,
            RequestType.DEAL_ANALYSIS
        ]:
            response, status = await gateway_instance.handle_request(
                request_type,
                payload
            )
            assert status == 200

@pytest.mark.asyncio
async def test_request_handling_success(gateway):
    """Test successful request handling."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        assert status == 200
        assert "message" in response
        assert isinstance(response["message"], str)

@pytest.mark.asyncio
async def test_authentication(gateway):
    """Test authentication handling."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        auth_token = "valid_token"
        
        # Test with invalid token
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload,
            "invalid_token"
        )
        assert status == 401
        
        # Test with valid token
        valid_token = jwt.encode(
            {"user_id": "test_user"},
            "your-secret-key",
            algorithm="HS256"
        )
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload,
            valid_token
        )
        assert status == 200

@pytest.mark.asyncio
async def test_caching(gateway):
    """Test response caching."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        
        # First request
        response1, status1 = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        # Second request with same payload should hit cache
        response2, status2 = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        assert status1 == status2 == 200
        assert response1 == response2
        
        # Verify cache metrics
        metrics = gateway_instance._metrics
        cache_hits = [m for m in metrics.values() if m.cache_hit]
        assert len(cache_hits) > 0

@pytest.mark.asyncio
async def test_circuit_breaker(gateway):
    """Test circuit breaker functionality."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        
        # Simulate failures to trigger circuit breaker
        for _ in range(5):
            response, status = await gateway_instance.handle_request(
                RequestType.PROPERTY_SEARCH,
                {"invalid": "payload"}  # Invalid payload to force errors
            )
            assert status in [400, 500]  # Either validation or processing error
        
        # Next valid request should be blocked by circuit breaker
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        assert status == 503
        assert "Circuit breaker open" in response["error"]

@pytest.mark.asyncio
async def test_request_metrics(gateway):
    """Test request metrics collection."""
    async for gateway_instance in gateway:
        payload = {"zip_code": "12345"}
        request_id = gateway_instance._generate_request_id(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        assert status == 200
        assert "request_id" in response
        
        # Check metrics
        metrics = gateway_instance._metrics[response["request_id"]]
        assert metrics.request_type == RequestType.PROPERTY_SEARCH
        assert metrics.status_code == 200
        assert metrics.data_source == "mock"
        assert metrics.response_time > 0

@pytest.mark.asyncio
async def test_request_correlation(gateway):
    """Test request correlation."""
    async for gateway_instance in gateway:
        request_id = "test_correlation"
        payload = {"request_id": request_id}
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        assert status == 200
        assert response["request_id"] == request_id
        assert "test_correlation" in gateway_instance._metrics

@pytest.mark.asyncio
async def test_market_analysis(gateway):
    """Test market analysis integration."""
    async for gateway_instance in gateway:
        payload = {
            "zip_code": "12345",
            "data_source_preference": "mock",
            "metrics": [
                "median_price",
                "price_trend",
                "market_strength"
            ]
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.MARKET_ANALYSIS,
            payload
        )
        
        assert status == 200
        assert "data" in response
        assert "median_price" in response["data"]
        assert "price_trend" in response["data"]
        assert "market_strength" in response["data"]
        assert response["data"]["source"] == "mock"
        assert response["data"]["confidence_score"] > 0.8

@pytest.mark.asyncio
async def test_lead_scoring(gateway):
    """Test lead scoring integration."""
    async for gateway_instance in gateway:
        payload = {
            "data_source_preference": "mock",
            "property_data": {
                "zip_code": "12345",
                "estimated_value": 500000,
                "last_sale_date": "2020-01-01",
                "equity_percentage": 0.4
            },
            "market_data": {
                "median_price": 550000,
                "market_strength": 0.8
            },
            "owner_data": {
                "age": 65,
                "income_level": "medium"
            }
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.LEAD_SCORING,
            payload
        )
        
        assert status == 200
        assert "data" in response
        assert "score" in response["data"]
        assert "confidence_score" in response["data"]
        assert response["data"]["source"] == "mock"

@pytest.mark.asyncio
async def test_deal_analysis(gateway):
    """Test deal analysis integration."""
    async for gateway_instance in gateway:
        payload = {
            "data_source_preference": "mock",
            "zip_code": "12345",
            "property_id": "test123",
            "purchase_price": 400000,
            "repair_estimate": 50000,
            "arv": 600000
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.DEAL_ANALYSIS,
            payload
        )
        
        assert status == 200
        assert "data" in response
        assert "roi" in response["data"]
        assert "max_offer" in response["data"]
        assert "confidence_score" in response["data"]
        assert response["data"]["source"] == "mock"

@pytest.mark.asyncio
async def test_metrics_tracking(gateway):
    """Test request metrics tracking."""
    async for gateway_instance in gateway:
        payload = {
            "zip_code": "12345",
            "data_source_preference": "mock"
        }
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        # Verify metrics using response request_id
        assert "request_id" in response
        metrics = gateway_instance._metrics[response["request_id"]]
        assert isinstance(metrics, RequestMetrics)
        assert metrics.start_time is not None
        assert metrics.end_time is not None
        assert metrics.status_code == 200
        assert metrics.data_source == "mock"

@pytest.mark.asyncio
async def test_error_handling(gateway):
    """Test error handling."""
    async for gateway_instance in gateway:
        # Test with invalid payload
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            {}  # Empty payload
        )
        assert status == 400
        assert "error" in response
        assert "Missing required fields" in response["error"]
        
        # Test with invalid request type
        with pytest.raises(ValueError):
            await gateway_instance.handle_request(
                "INVALID_TYPE",  # type: ignore
                {"zip_code": "12345"}
            )

@pytest.mark.asyncio
async def test_data_source_tracking(gateway):
    """Test data source tracking."""
    async for gateway_instance in gateway:
        payload = {
            "zip_code": "12345",
            "data_source_preference": "mock"
        }
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        assert status == 200
        assert "request_id" in response
        metrics = gateway_instance._metrics[response["request_id"]]
        assert metrics.data_source == "mock"

@pytest.mark.asyncio
async def test_circuit_breaker(gateway):
    """Test circuit breaker functionality."""
    async for gateway_instance in gateway:
        # Simulate failures to trigger circuit breaker
        for _ in range(5):
            response, status = await gateway_instance.handle_request(
                RequestType.PROPERTY_SEARCH,
                {"invalid": "payload"}  # Invalid payload to force errors
            )
            assert status in [400, 500]  # Either validation or processing error
        
        # Next valid request should be blocked by circuit breaker
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            {"zip_code": "12345", "data_source_preference": "mock"}
        )
        assert status == 503
        assert "Circuit breaker open" in response["error"]

@pytest.mark.asyncio
async def test_request_metrics(gateway):
    """Test request metrics collection."""
    async for gateway_instance in gateway:
        payload = {
            "zip_code": "12345",
            "data_source_preference": "mock"
        }
        
        # Make request
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        assert status == 200
        assert "request_id" in response
        
        # Check metrics
        metrics = gateway_instance._metrics[response["request_id"]]
        assert metrics.request_type == RequestType.PROPERTY_SEARCH
        assert metrics.status_code == 200
        assert metrics.data_source == "mock"
        assert metrics.response_time > 0

@pytest.mark.asyncio
async def test_request_correlation(gateway):
    """Test request correlation."""
    async for gateway_instance in gateway:
        payload = {
            "zip_code": "12345",
            "data_source_preference": "mock",
            "request_id": "test_correlation"
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.PROPERTY_SEARCH,
            payload
        )
        
        assert status == 200
        assert response["request_id"] == "test_correlation"
        assert "test_correlation" in gateway_instance._metrics

@pytest.mark.asyncio
async def test_market_analysis(gateway):
    """Test market analysis integration."""
    async for gateway_instance in gateway:
        payload = {
            "zip_code": "12345",
            "data_source_preference": "mock",
            "metrics": [
                "median_price",
                "price_trend",
                "market_strength"
            ]
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.MARKET_ANALYSIS,
            payload
        )
        
        assert status == 200
        assert "data" in response
        assert "median_price" in response["data"]
        assert "price_trend" in response["data"]
        assert "market_strength" in response["data"]
        assert response["data"]["source"] == "mock"
        assert response["data"]["confidence_score"] > 0.8

@pytest.mark.asyncio
async def test_lead_scoring(gateway):
    """Test lead scoring integration."""
    async for gateway_instance in gateway:
        payload = {
            "data_source_preference": "mock",
            "property_data": {
                "zip_code": "12345",
                "estimated_value": 500000,
                "last_sale_date": "2020-01-01",
                "equity_percentage": 0.4
            },
            "market_data": {
                "median_price": 550000,
                "market_strength": 0.8
            },
            "owner_data": {
                "age": 65,
                "income_level": "medium"
            }
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.LEAD_SCORING,
            payload
        )
        
        assert status == 200
        assert "data" in response
        assert "score" in response["data"]
        assert "confidence_score" in response["data"]
        assert response["data"]["source"] == "mock"

@pytest.mark.asyncio
async def test_deal_analysis(gateway):
    """Test deal analysis integration."""
    async for gateway_instance in gateway:
        payload = {
            "data_source_preference": "mock",
            "zip_code": "12345",
            "property_id": "test123",
            "purchase_price": 400000,
            "repair_estimate": 50000,
            "arv": 600000
        }
        
        response, status = await gateway_instance.handle_request(
            RequestType.DEAL_ANALYSIS,
            payload
        )
        
        assert status == 200
        assert "data" in response
        assert "roi" in response["data"]
        assert "max_offer" in response["data"]
        assert "confidence_score" in response["data"]
        assert response["data"]["source"] == "mock"

"""
Test suite for API Gateway implementation.
Tests integration with our hybrid data approach and protocol optimization.
"""
import pytest
from datetime import datetime
from collections import defaultdict
from src.api.gateway import APIGateway, RequestType

@pytest.fixture
async def gateway():
    """Create APIGateway instance."""
    gateway = APIGateway()
    await gateway.__aenter__()
    try:
        yield gateway
    finally:
        await gateway.__aexit__(None, None, None)

@pytest.fixture
def sample_property_request():
    """Create sample property search request."""
    return {
        "zip_code": "37215",
        "limit": 5,
        "filters": {
            "min_price": 500000,
            "max_price": 1000000,
            "min_beds": 3,
            "min_baths": 2
        }
    }

@pytest.fixture
def sample_market_request():
    """Create sample market analysis request."""
    return {
        "zip_code": "37215",
        "metrics": [
            "median_price",
            "price_trend",
            "market_strength",
            "days_on_market",
            "inventory_level"
        ]
    }

@pytest.fixture
def sample_lead_request():
    """Create sample lead scoring request."""
    return {
        "property_data": {
            "equity_percentage": 0.75,
            "years_owned": 15,
            "tax_status": "current"
        },
        "market_data": {
            "market_strength": 0.85,
            "appreciation_rate": 0.08,
            "inventory_level": "low"
        },
        "owner_data": {
            "age": 65,
            "occupation": "retired",
            "contact_attempts": 2
        }
    }

@pytest.fixture
def sample_deal_request():
    """Create sample deal analysis request."""
    return {
        "property_id": "mock_37215_1",
        "purchase_price": 450000,
        "repair_estimate": 50000,
        "arv": 650000,
        "holding_costs": 5000,
        "closing_costs": 10000
    }

@pytest.mark.asyncio
async def test_property_search_mock_data(gateway, sample_property_request):
    """Test property search with mock data."""
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        sample_property_request
    )
    
    assert status == 200
    assert "data" in result
    assert len(result["data"]) == sample_property_request["limit"]
    
    # Verify mock data structure
    property_data = result["data"][0]
    assert all(key in property_data for key in [
        "property_id", "address", "price", "bedrooms",
        "bathrooms", "square_feet", "source"
    ])
    assert property_data["source"] == "mock"
    assert property_data["confidence_score"] > 0.9
    assert property_data["data_freshness"] == "current"

@pytest.mark.asyncio
async def test_market_analysis_mock_data(gateway, sample_market_request):
    """Test market analysis with mock data."""
    result, status = await gateway.handle_request(
        RequestType.MARKET_ANALYSIS,
        sample_market_request
    )
    
    assert status == 200
    assert "data" in result
    
    # Verify all requested metrics are present
    data = result["data"]
    for metric in sample_market_request["metrics"]:
        assert metric in data
    
    assert data["source"] == "mock"
    assert data["confidence_score"] > 0.9
    assert "price_trend" in data
    assert all(period in data["price_trend"] for period in ["1_month", "3_month", "12_month"])

@pytest.mark.asyncio
async def test_lead_scoring_mock_data(gateway, sample_lead_request):
    """Test lead scoring with mock data."""
    result, status = await gateway.handle_request(
        RequestType.LEAD_SCORING,
        sample_lead_request
    )
    
    assert status == 200
    assert "data" in result
    
    data = result["data"]
    assert "score" in data
    assert "components" in data
    assert all(component in data["components"] for component in ["equity", "market", "motivation"])
    assert data["source"] == "mock"
    assert data["confidence_score"] > 0.8
    assert "recommendation" in data

@pytest.mark.asyncio
async def test_deal_analysis_mock_data(gateway, sample_deal_request):
    """Test deal analysis with mock data."""
    result, status = await gateway.handle_request(
        RequestType.DEAL_ANALYSIS,
        sample_deal_request
    )
    
    assert status == 200
    assert "data" in result
    
    data = result["data"]
    assert all(metric in data for metric in ["roi", "equity", "max_offer"])
    assert "summary" in data
    assert data["source"] == "mock"
    assert data["confidence_score"] > 0.8
    assert "recommendation" in data

@pytest.mark.asyncio
async def test_data_source_tracking(gateway, sample_property_request):
    """Test data source tracking in metrics."""
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        sample_property_request
    )
    
    assert status == 200
    metrics = gateway._metrics[list(gateway._metrics.keys())[0]]
    
    assert metrics.data_source == "mock"  # Should start with mock
    assert metrics.cache_hit is False
    assert metrics.response_time is not None
    assert metrics.status_code == 200

@pytest.mark.asyncio
async def test_caching_behavior(gateway, sample_property_request):
    """Test caching with mock data."""
    # First request - should use mock data
    result1, status1 = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        sample_property_request
    )
    assert status1 == 200
    
    # Second request - should use cache
    result2, status2 = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        sample_property_request
    )
    assert status2 == 200
    
    # Verify cache hit in metrics
    metrics = gateway._metrics[list(gateway._metrics.keys())[1]]
    assert metrics.cache_hit is True

@pytest.mark.asyncio
async def test_error_handling(gateway):
    """Test error handling with invalid requests."""
    # Missing required fields
    invalid_property_request = {"limit": 5}  # Missing zip_code
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        invalid_property_request
    )
    assert status != 200
    assert "error" in result
    
    # Invalid market metrics
    invalid_market_request = {
        "zip_code": "37215",
        "metrics": ["invalid_metric"]
    }
    result, status = await gateway.handle_request(
        RequestType.MARKET_ANALYSIS,
        invalid_market_request
    )
    assert status != 200
    assert "error" in result

@pytest.mark.asyncio
async def test_rate_limiting(gateway, sample_property_request):
    """Test rate limiting with mock data."""
    # Set low rate limit for testing
    gateway._rate_limiters[RequestType.PROPERTY_SEARCH.value] = defaultdict(int)
    gateway._rate_limiters[RequestType.PROPERTY_SEARCH.value][datetime.now().hour] = 1
    
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        sample_property_request
    )
    assert status != 200
    assert "error" in result
    assert "Rate limit exceeded" in result["error"]

@pytest.mark.asyncio
async def test_circuit_breaker(gateway, sample_property_request):
    """Test circuit breaker with mock data."""
    # Force circuit breaker to open
    gateway._circuit_breaker_counts[RequestType.PROPERTY_SEARCH.value] = 5
    gateway._last_circuit_break[RequestType.PROPERTY_SEARCH.value] = datetime.now()
    
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        sample_property_request
    )
    assert status != 200
    assert "error" in result
    assert "Circuit breaker is open" in result["error"]

"""
Tests for API Gateway implementation.
"""
import pytest
from datetime import datetime
from collections import defaultdict
from src.api.gateway import APIGateway, RequestType

@pytest.fixture
async def gateway():
    """Create APIGateway instance."""
    gateway = APIGateway()
    await gateway.__aenter__()
    try:
        yield gateway
    finally:
        await gateway.__aexit__(None, None, None)

@pytest.fixture
def property_request():
    """Create property search request."""
    return {
        "zip_code": "37215",
        "limit": 5,
        "use_mock": True,  # Always start with mock data
        "attom_enrichment": False,  # Control ATTOM API usage
        "filters": {
            "min_price": 500000,
            "max_price": 1000000,
            "min_beds": 3,
            "min_baths": 2
        }
    }

@pytest.mark.asyncio
async def test_mock_data_primary(gateway, property_request):
    """Test mock data as primary source."""
    result, status = await gateway.handle_request(
        RequestType.PROPERTY_SEARCH,
        property_request
    )
    assert status == 200
    assert "data" in result
    data = result["data"][0]
    assert data["source"] == "mock"
    assert data["confidence_score"] >= 0.9

{{ ... }}
