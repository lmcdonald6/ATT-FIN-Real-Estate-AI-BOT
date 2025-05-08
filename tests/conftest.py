"""Test configuration and fixtures."""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Set testing environment
os.environ['TESTING'] = 'true'

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Set environment variables for testing."""
    with patch.dict(os.environ, {
        'TESTING': 'true',
        'JWT_SECRET_KEY': 'test_secret',
        'STRIPE_API_KEY': 'test_stripe_key',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0'
    }):
        yield

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis client."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.hgetall.return_value = {}
    mock.keys.return_value = [b'key1', b'key2']
    mock.info.return_value = {
        'used_memory': 1000000,
        'used_memory_peak': 2000000,
        'keyspace_hits': 100,
        'keyspace_misses': 10,
        'uptime_in_seconds': 3600
    }
    mock.dbsize.return_value = 2
    
    # Patch Redis class
    with patch('redis.Redis', return_value=mock):
        yield mock

@pytest.fixture(autouse=True)
def mock_stripe():
    """Mock Stripe API."""
    mock = MagicMock()
    mock.Customer = MagicMock()
    mock.Charge = MagicMock()
    mock.api_key = None
    
    # Add mock to sys.modules
    sys.modules['stripe'] = mock
    yield mock
    del sys.modules['stripe']

@pytest.fixture(autouse=True)
def test_env():
    """Set test environment variables."""
    os.environ['TESTING'] = 'true'
    os.environ['jwt_secret'] = 'test_secret'
    os.environ['stripe_api_key'] = 'test_stripe_key'
    os.environ['redis_host'] = 'localhost'
    os.environ['redis_port'] = '6379'
    os.environ['redis_db'] = '0'
    yield
    # Clean up
    os.environ.pop('TESTING', None)
    os.environ.pop('jwt_secret', None)
    os.environ.pop('stripe_api_key', None)
    os.environ.pop('redis_host', None)
    os.environ.pop('redis_port', None)
    os.environ.pop('redis_db', None)

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        'testing': True,
        'jwt_secret': 'test_secret',
        'stripe_api_key': 'test_stripe_key',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'api_rate_limit': 100,
        'api_rate_window': 3600
    }
