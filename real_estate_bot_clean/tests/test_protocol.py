"""
Test suite for protocol optimization module.
Tests both mock data and ATTOM-enriched scenarios.
"""
import pytest
from datetime import datetime
from src.data.protocol import (
    ProtocolOptimizer,
    MessageType,
    Message
)

@pytest.fixture
def protocol():
    """Create ProtocolOptimizer instance."""
    return ProtocolOptimizer()

@pytest.fixture
def sample_property():
    """Create sample property data."""
    return {
        "id": "37215_1",
        "address": "123 Test St",
        "price": 800000,
        "sqft": 3000,
        "bedrooms": 4,
        "bathrooms": 3,
        "year_built": 2000,
        "property_type": "Single Family",
        "confidence_score": 0.85,
        "extra_field": "Should be removed in optimization"
    }

@pytest.fixture
def sample_market_data():
    """Create sample market analysis data."""
    return {
        "metrics": {
            "median_price": 850000,
            "price_trend": 0.05,
            "days_on_market": 30,
            "inventory_level": "Low",
            "market_strength": 0.8
        },
        "confidence_scores": {
            "price_trend": 0.9,
            "market_strength": 0.85
        }
    }

def test_encode_decode_property_request(protocol):
    """Test property request encoding and decoding."""
    # Prepare request
    zip_code = "37215"
    filters = {"min_price": 500000, "max_price": 1000000}
    
    # Encode
    encoded, compressed = protocol.optimize_property_request(
        zip_code,
        filters
    )
    
    # Decode
    message = protocol.decode_response(encoded, compressed)
    
    # Verify
    assert message.type == MessageType.PROPERTY_REQUEST
    assert message.payload["zip_code"] == zip_code
    assert message.payload["filters"] == filters
    assert isinstance(message.timestamp, datetime)
    assert len(message.request_id) > 0

def test_encode_decode_property_response(
    protocol,
    sample_property
):
    """Test property response encoding and decoding."""
    properties = [sample_property]
    request_id = "test_123"
    
    # Encode
    encoded, compressed = protocol.optimize_property_response(
        properties,
        request_id
    )
    
    # Decode
    message = protocol.decode_response(encoded, compressed)
    
    # Verify
    assert message.type == MessageType.PROPERTY_RESPONSE
    assert len(message.payload["properties"]) == 1
    prop = message.payload["properties"][0]
    assert "extra_field" not in prop  # Should be removed
    assert prop["id"] == sample_property["id"]
    assert prop["price"] == sample_property["price"]
    assert prop["confidence_score"] == sample_property["confidence_score"]

def test_encode_decode_market_request(protocol):
    """Test market request encoding and decoding."""
    zip_code = "37215"
    metrics = ["price_trend", "market_strength"]
    
    # Encode
    encoded, compressed = protocol.optimize_market_request(
        zip_code,
        metrics
    )
    
    # Decode
    message = protocol.decode_response(encoded, compressed)
    
    # Verify
    assert message.type == MessageType.MARKET_REQUEST
    assert message.payload["zip_code"] == zip_code
    assert message.payload["metrics"] == metrics

def test_encode_decode_market_response(
    protocol,
    sample_market_data
):
    """Test market response encoding and decoding."""
    request_id = "test_456"
    
    # Encode
    encoded, compressed = protocol.optimize_market_response(
        sample_market_data,
        request_id
    )
    
    # Decode
    message = protocol.decode_response(encoded, compressed)
    
    # Verify
    assert message.type == MessageType.MARKET_RESPONSE
    assert "metrics" in message.payload
    assert "confidence_scores" in message.payload
    assert message.payload["metrics"]["market_strength"] == 0.8
    assert message.payload["confidence_scores"]["price_trend"] == 0.9

def test_compression(protocol):
    """Test data compression for large payloads."""
    # Create large payload
    large_payload = {
        "data": "x" * 2000  # Exceeds compression threshold
    }
    
    # Encode with compression
    encoded, compressed = protocol.encode_request(
        MessageType.PROPERTY_REQUEST,
        large_payload,
        "test_789"
    )
    
    # Verify compression
    assert compressed
    assert len(encoded) < len(str(large_payload))
    
    # Decode compressed data
    message = protocol.decode_response(encoded, compressed)
    assert message.payload["data"] == large_payload["data"]

def test_error_handling_encode(protocol):
    """Test error handling during encoding."""
    # Create un-encodable payload
    bad_payload = {
        "data": object()  # Can't be JSON serialized
    }
    
    # Attempt encode
    encoded, compressed = protocol.encode_request(
        MessageType.PROPERTY_REQUEST,
        bad_payload,
        "test_error"
    )
    
    # Decode error message
    message = protocol.decode_response(encoded, compressed)
    assert message.type == MessageType.ERROR
    assert "error" in message.payload

def test_error_handling_decode(protocol):
    """Test error handling during decoding."""
    # Create invalid encoded data
    invalid_data = b"invalid data"
    
    # Attempt decode
    message = protocol.decode_response(invalid_data)
    
    # Verify error handling
    assert message.type == MessageType.ERROR
    assert "error" in message.payload

def test_request_id_generation(protocol):
    """Test unique request ID generation."""
    request_ids = set()
    
    # Generate multiple IDs
    for _ in range(100):
        encoded, _ = protocol.optimize_property_request("37215")
        message = protocol.decode_response(encoded)
        request_ids.add(message.request_id)
    
    # Verify uniqueness
    assert len(request_ids) == 100

def test_timestamp_handling(protocol):
    """Test timestamp handling in messages."""
    # Create and encode message
    encoded, compressed = protocol.optimize_property_request("37215")
    
    # Decode and verify timestamp
    message = protocol.decode_response(encoded, compressed)
    assert isinstance(message.timestamp, datetime)
    assert message.timestamp <= datetime.now()
