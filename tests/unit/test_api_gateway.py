"""Unit tests for API Gateway."""
import os
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api_gateway.gateway import APIGateway

# Set testing environment
os.environ['TESTING'] = 'true'
os.environ['jwt_secret'] = 'test_secret'
os.environ['stripe_api_key'] = 'test_stripe_key'

@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    with patch('redis.Redis') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def api_gateway(mock_redis):
    """Create API Gateway instance with mocked dependencies."""
    config = {
        'testing': True,
        'jwt_secret': 'test_secret',
        'stripe_api_key': 'test_stripe_key',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'api_rate_limit': 100,
        'api_rate_window': 3600
    }
    with patch('stripe.api_key') as mock_stripe:
        return APIGateway(config)

@pytest.fixture
def test_client(api_gateway):
    """Create test client."""
    return TestClient(api_gateway.app)

class TestAPIGateway:
    """Test suite for API Gateway."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get('/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        assert 'timestamp' in response.json()
    
    def test_validate_api_key_valid(self, api_gateway, mock_redis):
        """Test API key validation with valid key."""
        mock_redis.hgetall.return_value = {b'created': b'2024-01-01'}
        assert api_gateway._validate_api_key('valid_key') is True
        mock_redis.hset.assert_called_once()
    
    def test_validate_api_key_invalid(self, api_gateway, mock_redis):
        """Test API key validation with invalid key."""
        mock_redis.hgetall.return_value = {}
        assert api_gateway._validate_api_key('invalid_key') is False
    
    def test_create_jwt_token(self, api_gateway):
        """Test JWT token creation."""
        token = api_gateway._create_jwt_token('test_key')
        payload = jwt.decode(token, 'test_secret', algorithms=['HS256'])
        assert payload['sub'] == 'test_key'
        assert 'exp' in payload
    
    def test_check_rate_limit_first_request(self, api_gateway, mock_redis):
        """Test rate limiting for first request."""
        mock_redis.get.return_value = None
        assert api_gateway._check_rate_limit('test_key') is True
        mock_redis.setex.assert_called_once()
    
    def test_check_rate_limit_under_limit(self, api_gateway, mock_redis):
        """Test rate limiting under the limit."""
        mock_redis.get.return_value = b'50'
        assert api_gateway._check_rate_limit('test_key') is True
        mock_redis.incr.assert_called_once()
    
    def test_check_rate_limit_exceeded(self, api_gateway, mock_redis):
        """Test rate limiting when limit exceeded."""
        mock_redis.get.return_value = b'100'
        assert api_gateway._check_rate_limit('test_key') is False
    
    def test_track_usage(self, api_gateway, mock_redis):
        """Test usage tracking."""
        api_gateway.track_usage('test_key', '/test')
        mock_redis.hincrby.assert_called_once()
        mock_redis.expire.assert_called_once()
    
    def test_get_usage_stats(self, api_gateway, mock_redis):
        """Test getting usage statistics."""
        mock_redis.keys.return_value = [b'usage:test_key:2024-04-03']
        mock_redis.hgetall.return_value = {b'/test': b'10'}
        
        stats = api_gateway.get_usage_stats('test_key')
        assert stats['total_requests'] == 10
        assert stats['endpoints']['/test'] == 10
        assert '2024-04-03' in stats['daily_usage']
    
    def test_create_token_endpoint_valid(self, test_client, mock_redis):
        """Test token creation endpoint with valid API key."""
        mock_redis.hgetall.return_value = {b'created': b'2024-01-01'}
        response = test_client.post(
            '/auth/token',
            headers={'X-API-Key': 'valid_key'}
        )
        assert response.status_code == 200
        assert 'access_token' in response.json()
        assert response.json()['token_type'] == 'bearer'
    
    def test_create_token_endpoint_invalid(self, test_client, mock_redis):
        """Test token creation endpoint with invalid API key."""
        mock_redis.hgetall.return_value = {}
        response = test_client.post(
            '/auth/token',
            headers={'X-API-Key': 'invalid_key'}
        )
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid API key'
