"""
System monitoring module for real estate AI infrastructure.
Tracks API usage, data sources, and system health.
"""
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ApiUsage:
    calls_today: int
    calls_this_month: int
    remaining_calls: int
    last_call: datetime
    cost_per_call: float = 0.10  # ATTOM API cost per call

@dataclass
class DataSourceMetrics:
    total_requests: int
    cache_hits: int
    api_calls: int
    mock_data_used: int
    errors: int
    avg_response_time: float

class SystemMonitor:
    def __init__(self, cache_manager, sheets_manager):
        self.logger = logging.getLogger(__name__)
        self.cache = cache_manager
        self.sheets = sheets_manager
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize metrics storage
        self.monitor_dir = os.path.join(
            os.path.dirname(__file__),
            'monitoring'
        )
        os.makedirs(self.monitor_dir, exist_ok=True)
        
        # Constants
        self.MAX_MONTHLY_CALLS = 400  # ATTOM API limit
        self.ALERT_THRESHOLDS = {
            'api_usage': 0.8,  # Alert at 80% usage
            'cache_miss': 0.3,  # Alert if miss rate > 30%
            'error_rate': 0.05  # Alert if error rate > 5%
        }
        
        # Load initial state
        self._load_state()

    async def track_request(self, data_source: str, response_time: float,
                          cache_hit: bool, api_called: bool,
                          mock_data: bool, error: bool = False):
        """Track a data request."""
        try:
            metrics = self.source_metrics.get(data_source)
            if not metrics:
                metrics = DataSourceMetrics(0, 0, 0, 0, 0, 0.0)
                self.source_metrics[data_source] = metrics
            
            # Update metrics
            metrics.total_requests += 1
            metrics.cache_hits += int(cache_hit)
            metrics.api_calls += int(api_called)
            metrics.mock_data_used += int(mock_data)
            metrics.errors += int(error)
            
            # Update average response time
            metrics.avg_response_time = (
                (metrics.avg_response_time * (metrics.total_requests - 1) +
                 response_time) / metrics.total_requests
            )
            
            # Track API usage if applicable
            if api_called:
                await self._track_api_call()
            
            # Save updated metrics
            await self._save_state()
            
            # Check for alerts
            await self._check_alerts(data_source)
        except Exception as e:
            self.logger.error(f"Error tracking request: {e}")

    async def get_system_health(self) -> Dict:
        """Get comprehensive system health metrics."""
        try:
            # Get cache health
            cache_metrics = self.cache.get_health_metrics()
            
            # Calculate overall metrics
            total_requests = sum(
                m.total_requests for m in self.source_metrics.values()
            )
            total_errors = sum(
                m.errors for m in self.source_metrics.values()
            )
            
            health_metrics = {
                'api_usage': {
                    'calls_today': self.api_usage.calls_today,
                    'calls_this_month': self.api_usage.calls_this_month,
                    'remaining_calls': self.api_usage.remaining_calls,
                    'usage_percent': (
                        self.api_usage.calls_this_month /
                        self.MAX_MONTHLY_CALLS
                    ) * 100,
                    'estimated_cost': (
                        self.api_usage.calls_this_month *
                        self.api_usage.cost_per_call
                    )
                },
                'data_sources': {
                    source: {
                        'requests': metrics.total_requests,
                        'cache_hit_rate': (
                            metrics.cache_hits / metrics.total_requests
                            if metrics.total_requests > 0 else 0
                        ),
                        'mock_data_rate': (
                            metrics.mock_data_used / metrics.total_requests
                            if metrics.total_requests > 0 else 0
                        ),
                        'error_rate': (
                            metrics.errors / metrics.total_requests
                            if metrics.total_requests > 0 else 0
                        ),
                        'avg_response_time': metrics.avg_response_time
                    }
                    for source, metrics in self.source_metrics.items()
                },
                'cache': cache_metrics,
                'system': {
                    'total_requests': total_requests,
                    'error_rate': (
                        total_errors / total_requests
                        if total_requests > 0 else 0
                    ),
                    'mock_data_ratio': sum(
                        m.mock_data_used for m in self.source_metrics.values()
                    ) / total_requests if total_requests > 0 else 0
                }
            }
            
            return health_metrics
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            raise

    async def _track_api_call(self):
        """Track an API call and update usage metrics."""
        now = datetime.now()
        
        # Reset daily counter if needed
        if (not self.api_usage.last_call or
            now.date() > self.api_usage.last_call.date()):
            self.api_usage.calls_today = 0
        
        # Reset monthly counter if needed
        if (not self.api_usage.last_call or
            now.month != self.api_usage.last_call.month):
            self.api_usage.calls_this_month = 0
        
        # Update counters
        self.api_usage.calls_today += 1
        self.api_usage.calls_this_month += 1
        self.api_usage.remaining_calls = (
            self.MAX_MONTHLY_CALLS - self.api_usage.calls_this_month
        )
        self.api_usage.last_call = now
        
        # Update Google Sheets with usage data
        await self._update_usage_log()

    async def _check_alerts(self, data_source: str):
        """Check for alert conditions and log warnings."""
        metrics = self.source_metrics[data_source]
        alerts = []
        
        # Check API usage
        api_usage_percent = (
            self.api_usage.calls_this_month / self.MAX_MONTHLY_CALLS
        )
        if api_usage_percent >= self.ALERT_THRESHOLDS['api_usage']:
            alerts.append(
                f"High API usage: {api_usage_percent:.1%} of monthly limit"
            )
        
        # Check cache effectiveness
        if metrics.total_requests > 0:
            cache_miss_rate = 1 - (metrics.cache_hits / metrics.total_requests)
            if cache_miss_rate >= self.ALERT_THRESHOLDS['cache_miss']:
                alerts.append(
                    f"High cache miss rate for {data_source}: "
                    f"{cache_miss_rate:.1%}"
                )
        
        # Check error rate
        if metrics.total_requests > 0:
            error_rate = metrics.errors / metrics.total_requests
            if error_rate >= self.ALERT_THRESHOLDS['error_rate']:
                alerts.append(
                    f"High error rate for {data_source}: {error_rate:.1%}"
                )
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(alert)
        
        # Update sheets with alerts if any
        if alerts:
            await self._log_alerts(alerts)

    async def _update_usage_log(self):
        """Update API usage log in Google Sheets."""
        try:
            usage_data = {
                'timestamp': datetime.now().isoformat(),
                'calls_today': self.api_usage.calls_today,
                'calls_this_month': self.api_usage.calls_this_month,
                'remaining_calls': self.api_usage.remaining_calls,
                'estimated_cost': (
                    self.api_usage.calls_this_month *
                    self.api_usage.cost_per_call
                )
            }
            
            await self.sheets.update_usage_log(usage_data)
        except Exception as e:
            self.logger.error(f"Error updating usage log: {e}")

    async def _log_alerts(self, alerts: List[str]):
        """Log alerts to Google Sheets."""
        try:
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts
            }
            
            await self.sheets.log_alerts(alert_data)
        except Exception as e:
            self.logger.error(f"Error logging alerts: {e}")

    def _load_state(self):
        """Load monitor state from disk."""
        try:
            state_file = os.path.join(self.monitor_dir, 'monitor_state.json')
            
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # Load API usage
                api_data = state.get('api_usage', {})
                self.api_usage = ApiUsage(
                    calls_today=api_data.get('calls_today', 0),
                    calls_this_month=api_data.get('calls_this_month', 0),
                    remaining_calls=api_data.get('remaining_calls',
                                               self.MAX_MONTHLY_CALLS),
                    last_call=datetime.fromisoformat(
                        api_data.get('last_call', datetime.now().isoformat())
                    )
                )
                
                # Load source metrics
                self.source_metrics = {}
                for source, data in state.get('source_metrics', {}).items():
                    self.source_metrics[source] = DataSourceMetrics(
                        total_requests=data.get('total_requests', 0),
                        cache_hits=data.get('cache_hits', 0),
                        api_calls=data.get('api_calls', 0),
                        mock_data_used=data.get('mock_data_used', 0),
                        errors=data.get('errors', 0),
                        avg_response_time=data.get('avg_response_time', 0.0)
                    )
            else:
                # Initialize new state
                self.api_usage = ApiUsage(0, 0, self.MAX_MONTHLY_CALLS,
                                        datetime.now())
                self.source_metrics = {}
        except Exception as e:
            self.logger.error(f"Error loading monitor state: {e}")
            # Initialize new state on error
            self.api_usage = ApiUsage(0, 0, self.MAX_MONTHLY_CALLS,
                                    datetime.now())
            self.source_metrics = {}

    async def _save_state(self):
        """Save monitor state to disk."""
        try:
            state = {
                'api_usage': {
                    'calls_today': self.api_usage.calls_today,
                    'calls_this_month': self.api_usage.calls_this_month,
                    'remaining_calls': self.api_usage.remaining_calls,
                    'last_call': self.api_usage.last_call.isoformat()
                },
                'source_metrics': {
                    source: {
                        'total_requests': metrics.total_requests,
                        'cache_hits': metrics.cache_hits,
                        'api_calls': metrics.api_calls,
                        'mock_data_used': metrics.mock_data_used,
                        'errors': metrics.errors,
                        'avg_response_time': metrics.avg_response_time
                    }
                    for source, metrics in self.source_metrics.items()
                }
            }
            
            state_file = os.path.join(self.monitor_dir, 'monitor_state.json')
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving monitor state: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self._executor.shutdown(wait=False)
