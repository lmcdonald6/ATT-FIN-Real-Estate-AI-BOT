# Performance Optimization Guide

## Overview

This guide covers performance optimization strategies for the Real Estate AI Analysis Platform.

## Caching Strategies

### 1. Redis Caching Implementation

```python
from typing import Any, Optional
import redis
import zlib
import json
from datetime import timedelta

class CacheManager:
    def __init__(
        self,
        redis_client: redis.Redis,
        compression_threshold: int = 1000
    ):
        self.redis = redis_client
        self.compression_threshold = compression_threshold
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        data = await self.redis.get(key)
        if not data:
            return None
            
        # Check if data is compressed
        if data.startswith(b'\x78\x9c'):  # zlib header
            data = zlib.decompress(data)
            
        return json.loads(data)
        
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ):
        """Set value in cache with optional TTL."""
        data = json.dumps(value)
        
        # Compress if data is large
        if len(data) > self.compression_threshold:
            data = zlib.compress(data.encode())
        
        await self.redis.set(
            key,
            data,
            ex=int(ttl.total_seconds()) if ttl else None
        )
        
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

### 2. Multi-Level Caching

```python
from functools import wraps
from typing import Callable

class MultiLevelCache:
    def __init__(
        self,
        redis_client: redis.Redis,
        local_cache_size: int = 1000
    ):
        self.redis = CacheManager(redis_client)
        self.local_cache = LRUCache(local_cache_size)
        
    async def get_multi(self, key: str) -> Optional[Any]:
        """Get from multi-level cache."""
        # Try local cache first
        value = self.local_cache.get(key)
        if value is not None:
            return value
            
        # Try Redis cache
        value = await self.redis.get(key)
        if value is not None:
            # Update local cache
            self.local_cache.set(key, value)
            return value
            
        return None
        
    def cache_decorator(
        self,
        ttl: Optional[timedelta] = None
    ) -> Callable:
        """Decorator for multi-level caching."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                key = f"{func.__name__}:{args}:{kwargs}"
                
                # Try cache
                result = await self.get_multi(key)
                if result is not None:
                    return result
                    
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.redis.set(key, result, ttl)
                self.local_cache.set(key, result)
                
                return result
            return wrapper
        return decorator
```

## Database Optimization

### 1. Query Optimization

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import asyncpg

class QueryOptimizer:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        
    async def optimize_query(self, query: str) -> str:
        """Optimize SQL query."""
        with Session(self.engine) as session:
            # Get query plan
            plan = session.execute(
                text(f"EXPLAIN ANALYZE {query}")
            ).fetchall()
            
            # Analyze plan
            if self._needs_index(plan):
                await self._create_index(query)
            
            if self._needs_materialized_view(plan):
                await self._create_materialized_view(query)
                
        return self._rewrite_query(query)
        
    def _needs_index(self, plan: list) -> bool:
        """Check if query needs index."""
        for line in plan:
            if "Seq Scan" in line[0]:
                return True
        return False
        
    async def _create_index(self, query: str):
        """Create appropriate index."""
        # Analyze query to determine index fields
        fields = self._analyze_query_fields(query)
        
        # Create index
        index_name = f"idx_{'_'.join(fields)}"
        index_sql = f"""
        CREATE INDEX IF NOT EXISTS {index_name}
        ON {self._get_table(query)} ({','.join(fields)})
        """
        
        with Session(self.engine) as session:
            session.execute(text(index_sql))
            session.commit()
```

### 2. Connection Pooling

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg

class DatabasePool:
    def __init__(
        self,
        dsn: str,
        min_size: int = 10,
        max_size: int = 100
    ):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
        
    async def initialize(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=60
        )
        
    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get connection from pool."""
        async with self.pool.acquire() as conn:
            try:
                yield conn
            except Exception:
                await conn.execute('ROLLBACK')
                raise
```

## Asynchronous Processing

### 1. Task Queue Implementation

```python
from typing import Callable, Dict, List
import asyncio
import aiojobs

class TaskQueue:
    def __init__(self, max_workers: int = 10):
        self.scheduler = None
        self.max_workers = max_workers
        self.tasks: Dict[str, List[asyncio.Task]] = {}
        
    async def initialize(self):
        """Initialize task scheduler."""
        self.scheduler = await aiojobs.create_scheduler(
            limit=self.max_workers
        )
        
    async def enqueue(
        self,
        func: Callable,
        *args,
        priority: int = 1,
        **kwargs
    ):
        """Enqueue task with priority."""
        # Create task
        task = asyncio.create_task(func(*args, **kwargs))
        
        # Store task reference
        task_id = id(task)
        self.tasks[task_id] = task
        
        # Set priority
        task.set_name(f"priority-{priority}")
        
        # Schedule task
        await self.scheduler.spawn(task)
        
        return task_id
        
    async def get_result(self, task_id: str):
        """Get task result."""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        try:
            return await task
        finally:
            del self.tasks[task_id]
```

### 2. Batch Processing

```python
from typing import List, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Batch(Generic[T]):
    items: List[T]
    size: int
    
class BatchProcessor:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.current_batch = []
        
    async def add_item(self, item: T):
        """Add item to current batch."""
        self.current_batch.append(item)
        
        if len(self.current_batch) >= self.batch_size:
            await self.process_batch()
            
    async def process_batch(self):
        """Process current batch."""
        if not self.current_batch:
            return
            
        batch = Batch(
            items=self.current_batch,
            size=len(self.current_batch)
        )
        
        try:
            await self._process_items(batch)
        finally:
            self.current_batch = []
            
    async def _process_items(self, batch: Batch[T]):
        """Process batch items in parallel."""
        tasks = [
            self._process_item(item)
            for item in batch.items
        ]
        await asyncio.gather(*tasks)
```

## Load Balancing

### 1. Service Discovery

```python
from typing import List, Dict
import aiohttp
import json

class ServiceRegistry:
    def __init__(self, consul_url: str):
        self.consul_url = consul_url
        self.services: Dict[str, List[str]] = {}
        
    async def register_service(
        self,
        name: str,
        host: str,
        port: int
    ):
        """Register service with Consul."""
        service_id = f"{name}-{host}-{port}"
        
        payload = {
            "ID": service_id,
            "Name": name,
            "Address": host,
            "Port": port,
            "Check": {
                "HTTP": f"http://{host}:{port}/health",
                "Interval": "10s"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            await session.put(
                f"{self.consul_url}/v1/agent/service/register",
                json=payload
            )
            
    async def discover_services(self, name: str) -> List[str]:
        """Discover service instances."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.consul_url}/v1/health/service/{name}"
            ) as response:
                services = await response.json()
                
        # Filter healthy instances
        healthy = [
            s for s in services
            if all(c["Status"] == "passing" for c in s["Checks"])
        ]
        
        # Update cache
        self.services[name] = [
            f"{s['Service']['Address']}:{s['Service']['Port']}"
            for s in healthy
        ]
        
        return self.services[name]
```

### 2. Load Balancer

```python
import random
from typing import List, Optional

class LoadBalancer:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.strategy = "round_robin"
        self._current_index = 0
        
    async def get_service(
        self,
        service_name: str
    ) -> Optional[str]:
        """Get service instance using load balancing."""
        instances = await self.registry.discover_services(
            service_name
        )
        
        if not instances:
            return None
            
        if self.strategy == "round_robin":
            return self._round_robin(instances)
        elif self.strategy == "random":
            return self._random(instances)
        else:
            return instances[0]
            
    def _round_robin(self, instances: List[str]) -> str:
        """Round-robin selection."""
        instance = instances[self._current_index]
        self._current_index = (
            self._current_index + 1
        ) % len(instances)
        return instance
        
    def _random(self, instances: List[str]) -> str:
        """Random selection."""
        return random.choice(instances)
```

## Performance Monitoring

### 1. Metrics Collection

```python
from dataclasses import dataclass
from datetime import datetime
import prometheus_client as prom

@dataclass
class Metrics:
    request_duration = prom.Histogram(
        'request_duration_seconds',
        'Request duration in seconds',
        ['method', 'endpoint']
    )
    
    error_count = prom.Counter(
        'error_count_total',
        'Total number of errors',
        ['type']
    )
    
    active_connections = prom.Gauge(
        'active_connections',
        'Number of active connections'
    )
    
class MetricsCollector:
    def __init__(self):
        self.metrics = Metrics()
        
    async def track_request(
        self,
        method: str,
        endpoint: str,
        duration: float
    ):
        """Track request metrics."""
        self.metrics.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
    async def track_error(self, error_type: str):
        """Track error metrics."""
        self.metrics.error_count.labels(
            type=error_type
        ).inc()
        
    async def update_connections(self, count: int):
        """Update connection count."""
        self.metrics.active_connections.set(count)
```

### 2. Performance Monitoring Middleware

```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        metrics: MetricsCollector
    ):
        super().__init__(app)
        self.metrics = metrics
        
    async def dispatch(
        self,
        request: Request,
        call_next
    ):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Track request duration
            duration = time.time() - start_time
            await self.metrics.track_request(
                method=request.method,
                endpoint=request.url.path,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            # Track error
            await self.metrics.track_error(
                error_type=type(e).__name__
            )
            raise
```

## Best Practices

1. **Caching**
   - Use multi-level caching
   - Implement cache invalidation
   - Monitor cache hit rates
   - Compress large values
   - Set appropriate TTLs

2. **Database**
   - Use connection pooling
   - Optimize queries
   - Create proper indexes
   - Use materialized views
   - Implement sharding

3. **Async Processing**
   - Use task queues
   - Implement batch processing
   - Handle backpressure
   - Monitor task completion
   - Set proper timeouts

4. **Load Balancing**
   - Implement service discovery
   - Use health checks
   - Choose appropriate strategy
   - Monitor instance health
   - Handle failover

5. **Monitoring**
   - Collect key metrics
   - Set up alerting
   - Monitor resource usage
   - Track error rates
   - Analyze performance trends
