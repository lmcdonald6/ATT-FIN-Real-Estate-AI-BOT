"""
Rate limiter for API calls with time-based quotas.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    """
    Rate limiter for managing API quotas over time periods.
    Tracks usage and enforces limits.
    """
    
    def __init__(self, limit: int, period: timedelta):
        """
        Initialize rate limiter.
        
        Args:
            limit: Maximum number of calls allowed in period
            period: Time period for the limit (e.g. timedelta(days=30))
        """
        self.limit = limit
        self.period = period
        self.calls = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """
        Try to acquire permission for an API call.
        Returns True if call is allowed, False if limit reached.
        """
        async with self._lock:
            now = datetime.now()
            cutoff = now - self.period
            
            # Remove expired calls
            self.calls = [t for t in self.calls if t > cutoff]
            
            # Check if under limit
            if len(self.calls) < self.limit:
                self.calls.append(now)
                return True
            
            return False
    
    def get_remaining(self) -> int:
        """Get remaining calls in current period."""
        now = datetime.now()
        cutoff = now - self.period
        valid_calls = [t for t in self.calls if t > cutoff]
        return max(0, self.limit - len(valid_calls))
    
    def get_reset_time(self) -> Optional[datetime]:
        """Get time when next call will be available."""
        if not self.calls:
            return None
        
        oldest_call = min(self.calls)
        return oldest_call + self.period
