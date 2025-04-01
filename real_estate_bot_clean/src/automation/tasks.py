"""
Background task manager for real estate AI infrastructure.
Handles periodic data updates, cache maintenance, and system health checks.
"""
from typing import Dict, List, Optional, Callable
import asyncio
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import os

class TaskManager:
    def __init__(self, cache_manager, sheets_manager, market_analyzer, deal_analyzer):
        self.logger = logging.getLogger(__name__)
        self.cache = cache_manager
        self.sheets = sheets_manager
        self.market = market_analyzer
        self.deals = deal_analyzer
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Task configuration
        self.TASKS = {
            'update_hot_markets': {
                'interval': 3600,  # 1 hour
                'last_run': None,
                'enabled': True
            },
            'refresh_market_data': {
                'interval': 86400,  # 24 hours
                'last_run': None,
                'enabled': True
            },
            'cleanup_cache': {
                'interval': 43200,  # 12 hours
                'last_run': None,
                'enabled': True
            },
            'update_sheets_config': {
                'interval': 3600,  # 1 hour
                'last_run': None,
                'enabled': True
            }
        }
        
        # Market update priorities
        self.MARKET_PRIORITIES = {
            'hot': 1,      # Update every hour
            'growing': 2,  # Update every 2 hours
            'stable': 6,   # Update every 6 hours
            'cooling': 12  # Update every 12 hours
        }

    async def start(self):
        """Start background task manager."""
        self.logger.info("Starting background task manager...")
        await self._load_task_state()
        
        # Start task loops
        tasks = [
            self._run_task_loop('update_hot_markets', self._update_hot_markets),
            self._run_task_loop('refresh_market_data', self._refresh_market_data),
            self._run_task_loop('cleanup_cache', self._cleanup_cache),
            self._run_task_loop('update_sheets_config', self._update_sheets_config)
        ]
        
        await asyncio.gather(*tasks)

    async def _run_task_loop(self, task_name: str, task_func: Callable):
        """Run a task loop with proper error handling and logging."""
        while True:
            task_config = self.TASKS[task_name]
            
            if not task_config['enabled']:
                await asyncio.sleep(60)  # Check again in a minute
                continue
            
            try:
                # Check if it's time to run
                now = datetime.now()
                last_run = task_config['last_run']
                
                if (not last_run or 
                    (now - last_run).total_seconds() >= task_config['interval']):
                    self.logger.info(f"Running task: {task_name}")
                    await task_func()
                    task_config['last_run'] = now
                    await self._save_task_state()
            except Exception as e:
                self.logger.error(f"Error in task {task_name}: {e}")
            
            # Sleep until next check
            await asyncio.sleep(60)

    async def _update_hot_markets(self):
        """Update data for hot market areas."""
        try:
            # Get hot markets from sheets
            hot_markets = await self.sheets.get_hot_markets()
            
            # Update each market based on priority
            for zip_code in hot_markets:
                metrics, _ = await self.market.analyze_market(zip_code)
                market_type = self.market.get_market_type(metrics)
                
                # Check if update is needed based on market type
                last_update = self.cache.get(f"last_update_{zip_code}", 'market')
                hours_since_update = float('inf')
                
                if last_update:
                    hours_since_update = (
                        datetime.now() - last_update
                    ).total_seconds() / 3600
                
                if hours_since_update >= self.MARKET_PRIORITIES[market_type]:
                    await self._update_market_data(zip_code)
                    self.cache.set(
                        f"last_update_{zip_code}",
                        datetime.now(),
                        'market'
                    )
        except Exception as e:
            self.logger.error(f"Error updating hot markets: {e}")
            raise

    async def _refresh_market_data(self):
        """Refresh market data for all tracked areas."""
        try:
            # Get all tracked ZIP codes
            zip_codes = await self.sheets.get_tracked_markets()
            
            # Update each market
            for zip_code in zip_codes:
                await self._update_market_data(zip_code)
        except Exception as e:
            self.logger.error(f"Error refreshing market data: {e}")
            raise

    async def _update_market_data(self, zip_code: str):
        """Update market data for a specific ZIP code."""
        try:
            # Get fresh market data
            metrics, score = await self.market.analyze_market(zip_code)
            
            # Update sheets with new data
            await self.sheets.update_market_data(
                zip_code,
                {
                    'median_price': metrics.median_price,
                    'price_trend': metrics.price_trend,
                    'days_on_market': metrics.days_on_market,
                    'inventory_level': metrics.inventory_level,
                    'sales_velocity': metrics.sales_velocity,
                    'price_per_sqft': metrics.price_per_sqft,
                    'distress_ratio': metrics.distress_ratio,
                    'overall_score': score.overall_score,
                    'last_updated': datetime.now().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Error updating market data for {zip_code}: {e}")
            raise

    async def _cleanup_cache(self):
        """Clean up expired cache entries."""
        try:
            # Get cache stats before cleanup
            before_stats = self.cache.get_health_metrics()
            
            # Clear expired entries
            cleared = await self.cache.clear_expired()
            
            # Get cache stats after cleanup
            after_stats = self.cache.get_health_metrics()
            
            # Log cleanup results
            self.logger.info(
                f"Cache cleanup completed. Cleared entries: {cleared}. "
                f"Size before: {before_stats['cache_size']}, "
                f"Size after: {after_stats['cache_size']}"
            )
        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")
            raise

    async def _update_sheets_config(self):
        """Update configuration data from Google Sheets."""
        try:
            # Update market definitions
            market_config = await self.sheets.get_market_config()
            if market_config:
                self.market.MARKET_TYPES = market_config
            
            # Update deal thresholds
            deal_config = await self.sheets.get_deal_config()
            if deal_config:
                self.deals.DEAL_TYPES = deal_config
            
            # Update task intervals
            task_config = await self.sheets.get_task_config()
            if task_config:
                for task_name, config in task_config.items():
                    if task_name in self.TASKS:
                        self.TASKS[task_name].update(config)
            
            self.logger.info("Configuration updated from sheets")
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            raise

    async def _load_task_state(self):
        """Load task state from disk."""
        try:
            state_file = os.path.join(
                os.path.dirname(__file__),
                'task_state.json'
            )
            
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                for task_name, task_state in state.items():
                    if task_name in self.TASKS:
                        last_run = task_state.get('last_run')
                        if last_run:
                            self.TASKS[task_name]['last_run'] = (
                                datetime.fromisoformat(last_run)
                            )
                        self.TASKS[task_name]['enabled'] = (
                            task_state.get('enabled', True)
                        )
        except Exception as e:
            self.logger.error(f"Error loading task state: {e}")

    async def _save_task_state(self):
        """Save task state to disk."""
        try:
            state = {}
            for task_name, task_config in self.TASKS.items():
                state[task_name] = {
                    'last_run': (
                        task_config['last_run'].isoformat()
                        if task_config['last_run']
                        else None
                    ),
                    'enabled': task_config['enabled']
                }
            
            state_file = os.path.join(
                os.path.dirname(__file__),
                'task_state.json'
            )
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving task state: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self._executor.shutdown(wait=False)
