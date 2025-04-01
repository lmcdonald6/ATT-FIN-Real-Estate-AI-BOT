# Database Performance Optimization Guide

## Overview
This guide outlines our database optimization strategies for the real estate bot, focusing on efficient data storage and retrieval while respecting API limits.

## Key Metrics

### Performance Indicators
- Query execution time: < 100ms for cached data
- API call latency: < 2s for ATTOM requests
- Cache hit rate: Target > 80%
- Daily API usage: Max 13 calls (400/month)

### Workload Distribution
- Read-heavy (80%): Property searches, market analysis
- Write-moderate (15%): Cache updates, new listings
- Delete-light (5%): Expired cache cleanup

## Caching Strategy

### Property Cache
```python
{
    'key': f'{zip_code}_{property_type}',
    'ttl': {
        'hot_market': 24h,
        'growing': 48h,
        'stable': 72h,
        'emerging': 96h,
        'cooling': 120h
    }
}
```

### Market Cache
```python
{
    'key': f'{zip_code}_market',
    'data': {
        'type': 'hot|growing|stable|emerging|cooling',
        'multipliers': {...},
        'trends': {...}
    },
    'ttl': 168h  # 1 week
}
```

### Mock Data Cache
```python
{
    'key': f'{zip_code}_mock_{property_type}',
    'ttl': 12h,
    'refresh_strategy': 'lazy_loading'
}
```

## Optimization Techniques

### 1. Smart Indexing
- ZIP code + Property Type (primary)
- Market Type + Price Range (secondary)
- Last Updated + TTL (maintenance)

### 2. Data Partitioning
```python
partitions = {
    'hot_markets': {
        'update_frequency': 'daily',
        'data_source': 'ATTOM API'
    },
    'stable_markets': {
        'update_frequency': 'weekly',
        'data_source': 'hybrid'
    },
    'other_markets': {
        'update_frequency': 'monthly',
        'data_source': 'mock_data'
    }
}
```

### 3. Denormalization Strategy
```python
property_record = {
    'basic_info': {...},
    'market_data': {...},  # Denormalized
    'analysis': {...},     # Pre-calculated
    'scoring': {...}       # Pre-calculated
}
```

### 4. Replication Pattern
- Local cache: Primary for reads
- Google Sheets: Configuration master
- ATTOM API: Source of truth
- Mock data: Fallback source

### 5. Concurrency Control
```python
cache_operations = {
    'read': {
        'lock_type': 'none',
        'consistency': 'eventual'
    },
    'write': {
        'lock_type': 'optimistic',
        'retry_strategy': 'exponential_backoff'
    },
    'delete': {
        'lock_type': 'pessimistic',
        'scope': 'cache_type'
    }
}
```

## Performance Monitoring

### Cache Analytics
```python
metrics = {
    'hit_rate': 'hits / (hits + misses)',
    'api_usage': 'calls_today / MAX_DAILY_CALLS',
    'cache_efficiency': 'valid_entries / total_entries'
}
```

### Health Checks
```python
thresholds = {
    'cache_size': MAX_CACHE_ENTRIES * 0.9,
    'api_calls': MAX_DAILY_CALLS * 0.8,
    'stale_data': 'entries_near_expiry / total_entries'
}
```

## Maintenance Tasks

### Daily
- Clear expired cache entries
- Update hot market data
- Track API usage

### Weekly
- Refresh market intelligence
- Update stable market data
- Analyze cache performance

### Monthly
- Full cache cleanup
- Update property mappings
- Optimize storage patterns

## Best Practices

1. **API Conservation**
   - Use mock data for initial searches
   - Prioritize ATTOM calls for hot markets
   - Cache aggressively in stable markets

2. **Data Freshness**
   - Hot markets: 24h max
   - Stable markets: 72h acceptable
   - Other markets: 120h tolerable

3. **Error Handling**
   - Graceful degradation to mock data
   - Automatic retry for transient failures
   - Clear error messages for debugging

4. **Resource Management**
   - Proactive cache cleanup
   - Smart TTL adjustments
   - Efficient storage formats
