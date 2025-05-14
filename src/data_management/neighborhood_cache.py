"""
Progressive Cache Layer for Neighborhood Data

This module provides a caching layer for neighborhood sentiment data that:
1. Stores data with configurable expiration periods
2. Handles progressive degradation (fresh → stale → generic)
3. Manages data refresh in the background
4. Provides a unified interface for the real estate analysis system
"""

import asyncio
import json
import logging
import os
import sqlite3
import threading
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import the crawler and analyzer
from src.data_collection.neighborhood_crawler import NeighborhoodCrawler
from src.analysis.sentiment_analyzer import SentimentAnalyzer

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')

# Cache configuration
DEFAULT_CACHE_EXPIRY = 30  # Days
REFRESH_THRESHOLD = 25     # Days (refresh when cache is this old)
BACKGROUND_REFRESH = True  # Whether to refresh in background


class NeighborhoodCache:
    """Progressive cache layer for neighborhood sentiment data."""
    
    def __init__(self, db_path: str = DB_PATH, 
                 cache_expiry: int = DEFAULT_CACHE_EXPIRY,
                 refresh_threshold: int = REFRESH_THRESHOLD,
                 background_refresh: bool = BACKGROUND_REFRESH):
        """
        Initialize the neighborhood cache.
        
        Args:
            db_path: Path to the SQLite database
            cache_expiry: Number of days before cache expires
            refresh_threshold: Number of days before triggering a refresh
            background_refresh: Whether to refresh in background
        """
        self.db_path = db_path
        self.cache_expiry = cache_expiry
        self.refresh_threshold = refresh_threshold
        self.background_refresh = background_refresh
        
        # Initialize components
        self.crawler = NeighborhoodCrawler(db_path)
        self.analyzer = SentimentAnalyzer(db_path)
        
        # Ensure cache table exists
        self._ensure_cache_table()
        
        # Background refresh queue
        self.refresh_queue = asyncio.Queue() if background_refresh else None
        self.refresh_thread = None
        
        # Start background refresh thread if enabled
        if background_refresh:
            self._start_background_refresh()
    
    def _ensure_cache_table(self):
        """
        Ensure the neighborhood cache table exists in the database.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS neighborhood_cache (
            neighborhood TEXT PRIMARY KEY,
            city TEXT,
            data TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            refresh_status TEXT DEFAULT 'idle'
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _start_background_refresh(self):
        """
        Start the background refresh thread.
        """
        if self.refresh_thread is not None and self.refresh_thread.is_alive():
            return
        
        def refresh_worker():
            async def worker():
                loop = asyncio.get_event_loop()
                while True:
                    try:
                        # Get the next neighborhood to refresh
                        neighborhood, city = await self.refresh_queue.get()
                        
                        # Update refresh status
                        self._update_refresh_status(neighborhood, "refreshing")
                        
                        try:
                            # Refresh the data
                            await self.refresh_neighborhood_data(neighborhood, city)
                            self._update_refresh_status(neighborhood, "idle")
                        except Exception as e:
                            logger.error(f"Error refreshing {neighborhood}: {str(e)}")
                            self._update_refresh_status(neighborhood, "error")
                        
                        # Mark task as done
                        self.refresh_queue.task_done()
                    except Exception as e:
                        logger.error(f"Error in refresh worker: {str(e)}")
            
            # Create and run the event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(worker())
        
        # Start the thread
        self.refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        self.refresh_thread.start()
        
        logger.info("Background refresh thread started")
    
    def _update_refresh_status(self, neighborhood: str, status: str):
        """
        Update the refresh status for a neighborhood.
        
        Args:
            neighborhood: The neighborhood name
            status: The refresh status (idle, refreshing, error)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE neighborhood_cache
        SET refresh_status = ?
        WHERE neighborhood = ?
        ''', (status, neighborhood))
        
        conn.commit()
        conn.close()
    
    def _queue_background_refresh(self, neighborhood: str, city: str = None):
        """
        Queue a neighborhood for background refresh.
        
        Args:
            neighborhood: The neighborhood to refresh
            city: The city containing the neighborhood (optional)
        """
        if not self.background_refresh or self.refresh_queue is None:
            return
        
        # Add to the queue
        try:
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(
                self.refresh_queue.put((neighborhood, city)),
                loop
            )
        except RuntimeError:
            # If no event loop is available, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.refresh_queue.put((neighborhood, city)))
        
        logger.info(f"Queued {neighborhood} for background refresh")
    
    async def refresh_neighborhood_data(self, neighborhood: str, city: str = None) -> Dict[str, Any]:
        """
        Refresh neighborhood data by crawling and analyzing.
        
        Args:
            neighborhood: The neighborhood to refresh
            city: The city containing the neighborhood (optional)
            
        Returns:
            Dictionary with refreshed neighborhood data
        """
        logger.info(f"Refreshing data for {neighborhood}")
        
        # Crawl for new data
        posts = await self.crawler.crawl_neighborhood(neighborhood, city, force_refresh=True)
        
        # Analyze the data
        analysis = self.analyzer.analyze_neighborhood(neighborhood, force_refresh=True)
        
        # Combine data
        data = {
            "neighborhood": neighborhood,
            "city": city,
            "post_count": len(posts),
            "analysis": analysis,
            "last_updated": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(days=self.cache_expiry)).isoformat()
        }
        
        # Cache the data
        self._cache_neighborhood_data(neighborhood, city, data)
        
        return data
    
    def _cache_neighborhood_data(self, neighborhood: str, city: str, data: Dict[str, Any]):
        """
        Cache neighborhood data in the database.
        
        Args:
            neighborhood: The neighborhood name
            city: The city containing the neighborhood
            data: The data to cache
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert data to JSON
        data_json = json.dumps(data)
        
        # Insert or replace
        cursor.execute('''
        INSERT OR REPLACE INTO neighborhood_cache
        (neighborhood, city, data, last_updated, refresh_status)
        VALUES (?, ?, ?, ?, ?)
        ''', (neighborhood, city, data_json, datetime.now().isoformat(), "idle"))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cached data for {neighborhood}")
    
    def get_cached_data(self, neighborhood: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a neighborhood.
        
        Args:
            neighborhood: The neighborhood to get data for
            
        Returns:
            Dictionary with cached data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT data, last_updated, city, refresh_status FROM neighborhood_cache
        WHERE neighborhood = ?
        ''', (neighborhood,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        data_json, last_updated, city, refresh_status = row
        data = json.loads(data_json)
        
        # Add metadata about cache status
        last_updated_dt = datetime.fromisoformat(last_updated)
        age_days = (datetime.now() - last_updated_dt).days
        
        data["cache_metadata"] = {
            "age_days": age_days,
            "is_fresh": age_days < self.refresh_threshold,
            "is_stale": self.refresh_threshold <= age_days < self.cache_expiry,
            "is_expired": age_days >= self.cache_expiry,
            "refresh_status": refresh_status
        }
        
        # Check if we should queue a refresh
        if self.background_refresh and age_days >= self.refresh_threshold and refresh_status == "idle":
            self._queue_background_refresh(neighborhood, city)
        
        return data
    
    async def get_neighborhood_data(self, neighborhood: str, city: str = None, 
                                  force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get neighborhood data with progressive caching.
        
        Args:
            neighborhood: The neighborhood to get data for
            city: The city containing the neighborhood (optional)
            force_refresh: Whether to force a refresh
            
        Returns:
            Dictionary with neighborhood data
        """
        # Check if we should use cached data
        if not force_refresh:
            cached_data = self.get_cached_data(neighborhood)
            if cached_data:
                metadata = cached_data["cache_metadata"]
                
                # If data is fresh or stale but not expired, use it
                if not metadata["is_expired"]:
                    logger.info(f"Using {'fresh' if metadata['is_fresh'] else 'stale'} cached data for {neighborhood}")
                    return cached_data
        
        # If we got here, we need to refresh the data
        try:
            return await self.refresh_neighborhood_data(neighborhood, city)
        except Exception as e:
            logger.error(f"Error refreshing data for {neighborhood}: {str(e)}")
            
            # Try to use expired cache as fallback
            cached_data = self.get_cached_data(neighborhood)
            if cached_data:
                logger.info(f"Using expired cached data for {neighborhood} as fallback")
                cached_data["cache_metadata"]["is_fallback"] = True
                return cached_data
            
            # If all else fails, return a generic response
            return self._generate_generic_data(neighborhood, city)
    
    def _generate_generic_data(self, neighborhood: str, city: str = None) -> Dict[str, Any]:
        """
        Generate generic data when no real data is available.
        
        Args:
            neighborhood: The neighborhood name
            city: The city containing the neighborhood
            
        Returns:
            Dictionary with generic neighborhood data
        """
        logger.info(f"Generating generic data for {neighborhood}")
        
        return {
            "neighborhood": neighborhood,
            "city": city,
            "post_count": 0,
            "analysis": {
                "neighborhood": neighborhood,
                "overall_sentiment": {
                    "label": "neutral",
                    "score": 0,
                    "confidence": 0,
                    "distribution": {"positive": 0.33, "neutral": 0.34, "negative": 0.33}
                },
                "aspect_sentiment": {},
                "key_themes": [],
                "sources": [],
                "analysis_date": datetime.now().isoformat()
            },
            "last_updated": datetime.now().isoformat(),
            "expiry": datetime.now().isoformat(),
            "cache_metadata": {
                "is_generic": True,
                "is_fresh": False,
                "is_stale": False,
                "is_expired": False,
                "is_fallback": True,
                "refresh_status": "error"
            }
        }
    
    async def get_multiple_neighborhoods(self, neighborhoods: List[Tuple[str, Optional[str]]]) -> Dict[str, Dict[str, Any]]:
        """
        Get data for multiple neighborhoods in parallel.
        
        Args:
            neighborhoods: List of (neighborhood, city) tuples
            
        Returns:
            Dictionary mapping neighborhood names to their data
        """
        tasks = []
        for neighborhood, city in neighborhoods:
            tasks.append(self.get_neighborhood_data(neighborhood, city))
        
        results = await asyncio.gather(*tasks)
        
        return {neighborhoods[i][0]: results[i] for i in range(len(neighborhoods))}
    
    def get_text_summary(self, neighborhood_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of neighborhood data.
        
        Args:
            neighborhood_data: The neighborhood data dictionary
            
        Returns:
            Text summary of the neighborhood data
        """
        if neighborhood_data.get("cache_metadata", {}).get("is_generic", False):
            return f"No data available for {neighborhood_data['neighborhood']}."
        
        # Use the analyzer to generate a summary
        return self.analyzer.generate_text_summary(neighborhood_data["analysis"])


async def main():
    """
    Example usage of the neighborhood cache.
    """
    cache = NeighborhoodCache()
    
    # Example neighborhoods
    neighborhoods = [
        ("Atlanta Beltline", "Atlanta"),
        ("Midtown", "Manhattan"),
        ("Mission District", "San Francisco")
    ]
    
    # Get data for a single neighborhood
    print(f"\nGetting data for {neighborhoods[0][0]}...")
    data = await cache.get_neighborhood_data(neighborhoods[0][0], neighborhoods[0][1])
    
    # Print a summary
    print("\nNeighborhood Summary:")
    print(cache.get_text_summary(data))
    
    # Get data for multiple neighborhoods
    print("\nGetting data for multiple neighborhoods...")
    multi_data = await cache.get_multiple_neighborhoods(neighborhoods)
    
    for neighborhood, data in multi_data.items():
        print(f"\n{'-'*50}")
        print(f"Neighborhood: {neighborhood}")
        print(f"Data age: {data.get('cache_metadata', {}).get('age_days', 'N/A')} days")
        print(f"Post count: {data.get('post_count', 0)}")
        
        # Print sentiment if available
        sentiment = data.get("analysis", {}).get("overall_sentiment", {})
        if sentiment:
            print(f"Sentiment: {sentiment.get('label', 'N/A')} (score: {sentiment.get('score', 0):.2f})")


if __name__ == "__main__":
    asyncio.run(main())
