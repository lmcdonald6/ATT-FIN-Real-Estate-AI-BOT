"""
Simple performance monitor for the real estate bot's hybrid data system.
Tracks ATTOM API usage (400/month limit) and cache effectiveness.
"""
import sys
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data.cache import Cache

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = Cache()
        
        # Setup monitoring directory
        self.monitor_dir = project_root / 'monitoring'
        self.monitor_dir.mkdir(exist_ok=True)
        
        # Initialize metrics storage
        self.metrics_file = self.monitor_dir / 'performance_metrics.json'
        self.metrics_history = self._load_metrics_history()

    async def run_health_check(self):
        """Run comprehensive health check and return metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cache': self.cache.get_health_metrics(),
            'system': self._get_system_metrics()
        }
        
        # Save metrics
        self.metrics_history.append(metrics)
        self._save_metrics_history()
        
        # Print summary
        self._print_summary(metrics)
        
        return metrics

    def _get_system_metrics(self):
        """Get system-level performance metrics."""
        cache_dir = project_root / 'src' / 'data' / 'cache'
        cache_size = 0
        cache_files = 0
        
        if cache_dir.exists():
            cache_size = sum(f.stat().st_size for f in cache_dir.glob('**/*') if f.is_file())
            cache_files = len(list(cache_dir.glob('**/*')))
        
        return {
            'cache_size_mb': cache_size / (1024 * 1024),
            'cache_files': cache_files
        }

    def _print_summary(self, metrics):
        """Print a human-readable summary of current metrics."""
        cache_metrics = metrics['cache']
        api_usage = cache_metrics['api_usage']['attom']
        
        print("\n=== Real Estate Bot Performance Summary ===")
        print(f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}")
        
        print("\nAPI Usage:")
        print(f"- Today's Usage: {api_usage['usage_percent']:.1f}%")
        print(f"- Remaining Calls: {api_usage['remaining_calls']}")
        
        print("\nCache Performance:")
        for cache_type, perf in cache_metrics['cache_performance'].items():
            print(f"\n{cache_type.title()} Cache:")
            print(f"- Hit Rate: {perf['hit_rate']:.1%}")
            print(f"- Avg Latency: {perf['avg_latency_ms']:.2f}ms")
            print(f"- Size: {perf['size']} entries")
            print(f"- Utilization: {perf['utilization']:.1%}")
        
        if cache_metrics.get('warnings'):
            print("\nWarnings:")
            for warning in cache_metrics['warnings']:
                print(f"- {warning}")

    def _load_metrics_history(self):
        """Load historical metrics from file."""
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text())
            except Exception as e:
                self.logger.error(f"Error loading metrics history: {e}")
                return []
        return []

    def _save_metrics_history(self):
        """Save metrics history to file."""
        try:
            # Keep last 30 days of metrics
            cutoff = datetime.now() - timedelta(days=30)
            self.metrics_history = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m['timestamp']) >= cutoff
            ]
            
            self.metrics_file.write_text(json.dumps(self.metrics_history, indent=2))
        except Exception as e:
            self.logger.error(f"Error saving metrics history: {e}")

async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    monitor = PerformanceMonitor()
    
    # Run health check
    await monitor.run_health_check()

if __name__ == '__main__':
    asyncio.run(main())
