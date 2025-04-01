"""Cache Scheduler for Real Estate AI Bot"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from firebase_manager import FirebaseManager

logger = logging.getLogger(__name__)

class CacheScheduler:
    """Manages scheduled cache operations and updates"""
    
    def __init__(self, firebase_manager: FirebaseManager):
        self.firebase = firebase_manager
        self.running = False
        self.schedules = {
            'market_data': timedelta(hours=24),    # Daily market data updates
            'property_data': timedelta(days=7),    # Weekly property updates
            'cleanup': timedelta(hours=3),         # Cleanup every 3 hours
            'metrics': timedelta(minutes=30)       # Update metrics every 30 minutes
        }
        self.last_run = {}
        
    async def start(self):
        """Start the cache scheduler"""
        self.running = True
        await self._run_scheduler()
        
    async def stop(self):
        """Stop the cache scheduler"""
        self.running = False
        
    async def _run_scheduler(self):
        """Run scheduled tasks"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check and run each scheduled task
                for task_name, interval in self.schedules.items():
                    last_run = self.last_run.get(task_name)
                    if not last_run or (current_time - last_run) >= interval:
                        await self._run_task(task_name)
                        self.last_run[task_name] = current_time
                
                # Wait for next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
                
    async def _run_task(self, task_name: str):
        """Run a specific scheduled task"""
        try:
            if task_name == 'cleanup':
                self.firebase.cleanup_expired_cache()
                logger.info("Completed cache cleanup")
                
            elif task_name == 'market_data':
                await self._update_market_data()
                logger.info("Updated market data cache")
                
            elif task_name == 'property_data':
                await self._update_property_data()
                logger.info("Updated property data cache")
                
            elif task_name == 'metrics':
                await self._update_cache_metrics()
                logger.info("Updated cache metrics")
                
        except Exception as e:
            logger.error(f"Task {task_name} failed: {str(e)}")
            
    async def _update_market_data(self):
        """Update cached market data for high-demand areas"""
        high_demand_zips = self.firebase.get_high_demand_zips(10)
        for zip_code in high_demand_zips:
            query = {
                'type': 'market_trends',
                'parameters': {'zip_code': zip_code},
                'timestamp': datetime.now().isoformat()
            }
            # Force cache refresh for market data
            self.firebase.get_cached_response(query)
            
    async def _update_property_data(self):
        """Update cached property data"""
        # Get properties needing update
        properties = self.firebase.get_properties_for_update()
        for property_data in properties:
            query = {
                'type': 'property_analysis',
                'parameters': {
                    'address': property_data.get('address'),
                    'zip_code': property_data.get('zip_code')
                },
                'timestamp': datetime.now().isoformat()
            }
            # Force cache refresh
            self.firebase.get_cached_response(query)
            
    async def _update_cache_metrics(self):
        """Update cache performance metrics"""
        metrics = {
            'total_size': await self._get_cache_size(),
            'hit_rate': await self._calculate_hit_rate(),
            'query_types': await self._get_query_type_stats()
        }
        
        self.firebase.update_cache_metrics(metrics)
        
    async def _get_cache_size(self) -> int:
        """Get total size of cached data"""
        # Implementation depends on Firebase storage metrics
        return 0
        
    async def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        metrics = self.firebase.get_cache_metrics()
        hits = metrics.get('hit_count', 0)
        total = hits + metrics.get('miss_count', 0)
        return hits / total if total > 0 else 0
        
    async def _get_query_type_stats(self) -> Dict:
        """Get statistics for different query types"""
        return {
            'property_analysis': await self._get_type_stats('property_analysis'),
            'market_trends': await self._get_type_stats('market_trends'),
            'investment_strategy': await self._get_type_stats('investment_strategy')
        }
        
    async def _get_type_stats(self, query_type: str) -> Dict:
        """Get statistics for a specific query type"""
        return {
            'count': self.firebase.get_query_type_count(query_type),
            'avg_response_time': self.firebase.get_avg_response_time(query_type)
        }
