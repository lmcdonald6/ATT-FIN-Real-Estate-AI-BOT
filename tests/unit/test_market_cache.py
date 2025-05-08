"""Unit tests for market cache."""
import pytest
from src.cache.market_cache import MarketCache

@pytest.fixture
def market_cache(mock_redis):
    """Create market cache instance."""
    config = {
        'testing': True,
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'cache_ttl': 3600,
        'cleanup_interval': 3600,
        'compression_threshold': 10  # Small threshold for testing
    }
    return MarketCache(config)

def test_compression(market_cache):
    """Test data compression."""
    data = {'test': 'data', 'nested': {'key': 'value'}}
    compressed = market_cache._compress_data(data)
    decompressed = market_cache._decompress_data(compressed)
    assert decompressed == data

def test_cache_market_analysis(market_cache, mock_redis):
    """Test caching market analysis."""
    zip_code = 'test_zip'
    analysis_type = 'price_trends'
    params = {'timeframe': '1y'}
    data = {'values': [1, 2, 3]}
    
    market_cache.cache_market_analysis(zip_code, analysis_type, params, data)
    mock_redis.setex.assert_called_once()

def test_cache_property_data(market_cache, mock_redis):
    """Test caching property data."""
    property_id = 'test_property'
    source = 'mls'
    data = {'price': 100000, 'sqft': 2000}
    
    market_cache.cache_property_data(property_id, source, data)
    mock_redis.setex.assert_called_once()

def test_cache_stats(market_cache, mock_redis):
    """Test cache statistics."""
    mock_redis.info.return_value = {
        'used_memory': 1000000,  # 1MB
        'used_memory_peak': 2000000,
        'keyspace_hits': 100,
        'keyspace_misses': 10,
        'uptime_in_seconds': 3600
    }
    mock_redis.keys.return_value = [b'key1', b'key2']
    mock_redis.dbsize.return_value = 2
    
    stats = market_cache.get_cache_stats()
    assert isinstance(stats['memory_used_mb'], float)
    assert isinstance(stats['total_keys'], int)
    assert stats['memory_used_mb'] == 0.95367431640625  # 1MB from mock
    assert stats['total_keys'] == 2  # From mock dbsize
    assert round(stats['hit_rate'], 2) == 0.91  # From mock hits/misses

@pytest.mark.skip(reason="Cleanup test is not implemented")
def test_cleanup(market_cache):
    """Test cache cleanup."""
    pass

@pytest.mark.parametrize("property_id,metric,timeframe", [
    ('12345', 'price', '1y'),
    ('67890', 'inventory', '6m'),
    ('11111', 'sales', '3m')
])
def test_market_trends(market_cache, mock_redis, property_id, metric, timeframe):
    """Test market trends retrieval."""
    data = {'trend': 'data'}
    mock_redis.get.return_value = market_cache._compress_data(data)
    
    result = market_cache.get_market_trends(property_id, metric, timeframe)
    assert result == data
