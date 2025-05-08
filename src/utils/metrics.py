from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Callable

# Define metrics
API_REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status']
)

API_LATENCY = Histogram(
    'api_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

ANALYZER_EXECUTION_TIME = Histogram(
    'analyzer_execution_time_seconds',
    'Time taken by analyzers',
    ['analyzer_type', 'operation']
)

PREDICTION_CONFIDENCE = Gauge(
    'prediction_confidence',
    'Confidence score of predictions',
    ['analyzer_type', 'prediction_type']
)

def track_analyzer_metrics(analyzer_type: str, operation: str):
    """Decorator to track analyzer metrics."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                
                # Record execution time
                ANALYZER_EXECUTION_TIME.labels(
                    analyzer_type=analyzer_type,
                    operation=operation
                ).observe(time.time() - start_time)
                
                # Record confidence if available
                if isinstance(result, dict) and 'confidence' in result:
                    PREDICTION_CONFIDENCE.labels(
                        analyzer_type=analyzer_type,
                        prediction_type=operation
                    ).set(result['confidence'])
                
                return result
            except Exception as e:
                # Record failed execution
                API_REQUEST_COUNT.labels(
                    endpoint=f"{analyzer_type}/{operation}",
                    method="GET",
                    status="error"
                ).inc()
                raise
            
        return wrapper
    return decorator
