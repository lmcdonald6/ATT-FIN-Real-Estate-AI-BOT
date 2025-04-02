"""Error handling and logging utilities."""
import logging
from typing import Dict, Any, Optional, Type
from functools import wraps
import traceback
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketAnalysisError(Exception):
    """Base exception for market analysis errors."""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DataValidationError(MarketAnalysisError):
    """Raised when data validation fails."""
    pass

class DataSourceError(MarketAnalysisError):
    """Raised when data source operations fail."""
    pass

class CacheError(MarketAnalysisError):
    """Raised when cache operations fail."""
    pass

class AnalysisError(MarketAnalysisError):
    """Raised when market analysis operations fail."""
    pass

def handle_errors(error_map: Dict[Type[Exception], str]):
    """Decorator for handling errors in functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_code = None
                for error_type, code in error_map.items():
                    if isinstance(e, error_type):
                        error_code = code
                        break
                
                if error_code is None:
                    error_code = 'INTERNAL_ERROR'
                
                error_details = {
                    'timestamp': datetime.now().isoformat(),
                    'error_code': error_code,
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }
                
                logger.error(
                    f"Error in {func.__name__}: {error_code}",
                    extra={'error_details': error_details}
                )
                
                raise MarketAnalysisError(
                    message=str(e),
                    error_code=error_code,
                    details=error_details
                )
        return wrapper
    return decorator

class ErrorLogger:
    """Centralized error logging."""
    
    def __init__(self):
        self.logger = logging.getLogger('error_logger')
    
    def log_error(self,
                 error: Exception,
                 context: Dict[str, Any],
                 level: str = 'error') -> None:
        """Log an error with context."""
        error_details = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error.__class__.__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        log_method = getattr(self.logger, level)
        log_method(
            f"{error_details['error_type']}: {error_details['message']}",
            extra={'error_details': error_details}
        )
    
    def log_validation_error(self,
                           errors: Dict[str, Any],
                           data_source: str) -> None:
        """Log validation errors."""
        self.logger.warning(
            f"Validation errors from {data_source}",
            extra={'validation_errors': errors}
        )
    
    def log_api_error(self,
                     endpoint: str,
                     status_code: int,
                     response: Dict[str, Any]) -> None:
        """Log API errors."""
        self.logger.error(
            f"API error at {endpoint}",
            extra={
                'status_code': status_code,
                'response': response
            }
        )
    
    def log_cache_miss(self,
                      cache_key: str,
                      context: Dict[str, Any]) -> None:
        """Log cache misses."""
        self.logger.info(
            f"Cache miss for key: {cache_key}",
            extra={'context': context}
        )

error_logger = ErrorLogger()
