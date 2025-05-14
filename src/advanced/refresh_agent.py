"""
Sentiment Refresh Agent

This module provides functionality to automatically refresh neighborhood sentiment data
based on age, importance, and user activity. It implements a smart refresh strategy
that prioritizes neighborhoods that are frequently accessed or have stale data.
"""

import asyncio
import json
import logging
import os
import random
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')

# Import other components
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
if sys_path not in sys.path:
    sys.path.append(sys_path)

from src.data_collection.neighborhood_crawler import NeighborhoodCrawler
from src.analysis.sentiment_analyzer import SentimentAnalyzer


class SentimentRefreshAgent:
    """Agent that manages the automatic refresh of neighborhood sentiment data."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the sentiment refresh agent.
        
        Args:
            db_path: Path to the SQLite database with neighborhood data
        """
        self.db_path = db_path
        self.crawler = NeighborhoodCrawler(db_path)
        self.analyzer = SentimentAnalyzer(db_path)
        self._ensure_refresh_table()
    
    def _ensure_refresh_table(self):
        """
        Ensure the refresh tracking table exists in the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS refresh_tracking (
            neighborhood TEXT PRIMARY KEY,
            city TEXT,
            last_refresh TEXT,
            last_access TEXT,
            access_count INTEGER DEFAULT 0,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'idle'
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_cached_sentiment(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Get cached sentiment data for a ZIP code or neighborhood.
        
        Args:
            zip_code: The ZIP code or neighborhood name to get data for
            
        Returns:
            Dictionary with cached sentiment data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try to find by exact match
        cursor.execute('''
        SELECT n.*, s.analysis_data
        FROM neighborhood_cache n
        LEFT JOIN sentiment_analysis s ON n.neighborhood = s.neighborhood
        WHERE n.neighborhood = ? OR n.city = ?
        ''', (zip_code, zip_code))
        
        row = cursor.fetchone()
        
        # If not found, try to find by ZIP code prefix
        if not row and zip_code.isdigit():
            zip_prefix = zip_code[:3] if len(zip_code) >= 3 else zip_code
            cursor.execute('''
            SELECT n.*, s.analysis_data
            FROM neighborhood_cache n
            LEFT JOIN sentiment_analysis s ON n.neighborhood = s.neighborhood
            WHERE n.neighborhood LIKE ? OR n.city LIKE ?
            LIMIT 1
            ''', (f"{zip_prefix}%", f"{zip_prefix}%"))
            
            row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return None
        
        # Convert row to dictionary
        data = dict(row)
        
        # Parse JSON data
        if 'data' in data and data['data']:
            try:
                cached_data = json.loads(data['data'])
                data.update(cached_data)
            except json.JSONDecodeError:
                pass
        
        if 'analysis_data' in data and data['analysis_data']:
            try:
                analysis_data = json.loads(data['analysis_data'])
                data['analysis'] = analysis_data
            except json.JSONDecodeError:
                data['analysis'] = {}
        
        # Calculate age in days
        if 'last_updated' in data and data['last_updated']:
            try:
                last_updated = datetime.fromisoformat(data['last_updated'])
                data['age_days'] = (datetime.now() - last_updated).days
            except (ValueError, TypeError):
                data['age_days'] = 30
        else:
            data['age_days'] = 30
        
        # Update access tracking
        self._update_access_tracking(zip_code, data.get('city'))
        
        return data
    
    def _update_access_tracking(self, neighborhood: str, city: Optional[str] = None):
        """
        Update access tracking for a neighborhood.
        
        Args:
            neighborhood: The neighborhood name or ZIP code
            city: The city containing the neighborhood (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if neighborhood exists in tracking table
        cursor.execute('''
        SELECT access_count FROM refresh_tracking
        WHERE neighborhood = ?
        ''', (neighborhood,))
        
        row = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if row:
            # Update existing record
            cursor.execute('''
            UPDATE refresh_tracking
            SET last_access = ?, access_count = access_count + 1
            WHERE neighborhood = ?
            ''', (now, neighborhood))
        else:
            # Insert new record
            cursor.execute('''
            INSERT INTO refresh_tracking
            (neighborhood, city, last_access, access_count)
            VALUES (?, ?, ?, 1)
            ''', (neighborhood, city, now))
        
        conn.commit()
        conn.close()
    
    async def refresh_sentiment_for_zip(self, zip_code: str, city: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """
        Refresh sentiment data for a ZIP code or neighborhood.
        
        Args:
            zip_code: The ZIP code or neighborhood name to refresh
            city: The city containing the neighborhood (optional)
            force: Whether to force a refresh even if data is fresh
            
        Returns:
            Dictionary with refresh results
        """
        # Check if we need to refresh
        if not force:
            cached = self.get_cached_sentiment(zip_code)
            if cached and cached.get('age_days', 99) < 14:  # Less than 14 days old
                logger.info(f"Skipping refresh for {zip_code}, data is still fresh ({cached.get('age_days')} days old)")
                return {
                    "refreshed": False,
                    "reason": "data_fresh",
                    "neighborhood": zip_code,
                    "city": city,
                    "age_days": cached.get('age_days')
                }
        
        # Update status to refreshing
        self._update_refresh_status(zip_code, "refreshing")
        
        try:
            # Crawl for new data
            logger.info(f"Refreshing sentiment data for {zip_code}")
            posts = await self.crawler.crawl_neighborhood(zip_code, city, force_refresh=True)
            
            # Analyze the data
            analysis = self.analyzer.analyze_neighborhood(zip_code, force_refresh=True)
            
            # Extract summary and score
            summary = self.analyzer.generate_text_summary(analysis)
            score = analysis.get('overall_sentiment', {}).get('score', 0)
            
            # Update refresh tracking
            self._update_refresh_tracking(zip_code, city)
            
            logger.info(f"Successfully refreshed data for {zip_code}, score: {score:.2f}")
            
            # Update status to idle
            self._update_refresh_status(zip_code, "idle")
            
            return {
                "refreshed": True,
                "neighborhood": zip_code,
                "city": city,
                "post_count": len(posts),
                "score": score,
                "summary": summary[:200] + "..." if len(summary) > 200 else summary
            }
            
        except Exception as e:
            logger.error(f"Error refreshing data for {zip_code}: {str(e)}")
            
            # Update status to error
            self._update_refresh_status(zip_code, "error")
            
            return {
                "refreshed": False,
                "reason": "error",
                "neighborhood": zip_code,
                "city": city,
                "error": str(e)
            }
    
    def _update_refresh_status(self, neighborhood: str, status: str):
        """
        Update refresh status for a neighborhood.
        
        Args:
            neighborhood: The neighborhood name or ZIP code
            status: The refresh status (idle, refreshing, error)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE refresh_tracking
        SET status = ?
        WHERE neighborhood = ?
        ''', (status, neighborhood))
        
        conn.commit()
        conn.close()
    
    def _update_refresh_tracking(self, neighborhood: str, city: Optional[str] = None):
        """
        Update refresh tracking after a successful refresh.
        
        Args:
            neighborhood: The neighborhood name or ZIP code
            city: The city containing the neighborhood (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT OR REPLACE INTO refresh_tracking
        (neighborhood, city, last_refresh, last_access, access_count, status)
        VALUES (
            ?,
            ?,
            ?,
            (SELECT last_access FROM refresh_tracking WHERE neighborhood = ?),
            (SELECT access_count FROM refresh_tracking WHERE neighborhood = ?),
            'idle'
        )
        ''', (neighborhood, city, now, neighborhood, neighborhood))
        
        conn.commit()
        conn.close()
    
    def get_neighborhoods_to_refresh(self, limit: int = 10) -> List[Tuple[str, Optional[str]]]:
        """
        Get a list of neighborhoods that need refreshing, prioritized by age and access count.
        
        Args:
            limit: Maximum number of neighborhoods to return
            
        Returns:
            List of (neighborhood, city) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get neighborhoods from cache table that haven't been refreshed recently
        # or have high access counts
        cursor.execute('''
        SELECT n.neighborhood, n.city, 
               COALESCE(r.last_refresh, '2000-01-01') as last_refresh,
               COALESCE(r.access_count, 0) as access_count,
               COALESCE(r.status, 'idle') as status
        FROM neighborhood_cache n
        LEFT JOIN refresh_tracking r ON n.neighborhood = r.neighborhood
        WHERE r.status IS NULL OR r.status = 'idle' OR r.status = 'error'
        ORDER BY 
            CASE 
                WHEN julianday('now') - julianday(last_refresh) > 30 THEN 3  -- Very old (>30 days)
                WHEN julianday('now') - julianday(last_refresh) > 14 THEN 2  -- Old (>14 days)
                ELSE 1  -- Relatively fresh
            END DESC,
            access_count DESC
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [(row[0], row[1]) for row in rows]
    
    async def refresh_batch(self, limit: int = 5) -> Dict[str, Any]:
        """
        Refresh a batch of neighborhoods that need updating.
        
        Args:
            limit: Maximum number of neighborhoods to refresh
            
        Returns:
            Dictionary with batch refresh results
        """
        neighborhoods = self.get_neighborhoods_to_refresh(limit)
        
        if not neighborhoods:
            logger.info("No neighborhoods need refreshing")
            return {
                "refreshed": 0,
                "neighborhoods": []
            }
        
        logger.info(f"Refreshing {len(neighborhoods)} neighborhoods")
        
        results = []
        for neighborhood, city in neighborhoods:
            result = await self.refresh_sentiment_for_zip(neighborhood, city)
            results.append(result)
        
        refreshed_count = sum(1 for r in results if r.get('refreshed', False))
        
        return {
            "refreshed": refreshed_count,
            "total": len(results),
            "neighborhoods": results
        }
    
    async def start_refresh_daemon(self, interval_minutes: int = 60, batch_size: int = 5):
        """
        Start a daemon process that periodically refreshes neighborhood data.
        
        Args:
            interval_minutes: Minutes between refresh cycles
            batch_size: Number of neighborhoods to refresh in each cycle
        """
        logger.info(f"Starting refresh daemon with interval of {interval_minutes} minutes")
        
        while True:
            try:
                logger.info("Starting refresh cycle")
                result = await self.refresh_batch(batch_size)
                logger.info(f"Refresh cycle completed: {result['refreshed']}/{result['total']} neighborhoods refreshed")
            except Exception as e:
                logger.error(f"Error in refresh cycle: {str(e)}")
            
            # Wait for next cycle
            logger.info(f"Waiting {interval_minutes} minutes until next refresh cycle")
            await asyncio.sleep(interval_minutes * 60)


async def refresh_sentiment_for_zip(zip_code: str, city: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
    """
    Refresh sentiment data for a ZIP code or neighborhood.
    
    Args:
        zip_code: The ZIP code or neighborhood name to refresh
        city: The city containing the neighborhood (optional)
        force: Whether to force a refresh even if data is fresh
        
    Returns:
        Dictionary with refresh results
    """
    agent = SentimentRefreshAgent()
    return await agent.refresh_sentiment_for_zip(zip_code, city, force)


async def main():
    """
    Example usage of the sentiment refresh agent.
    """
    agent = SentimentRefreshAgent()
    
    # Example ZIP codes
    test_zips = ["30318", "11238", "94110"]
    
    for zip_code in test_zips:
        print(f"\nChecking data for ZIP {zip_code}...")
        cached = agent.get_cached_sentiment(zip_code)
        
        if cached:
            print(f"Found cached data, age: {cached.get('age_days', 'unknown')} days")
            
            if cached.get('age_days', 99) >= 14 or random.random() < 0.5:  # 50% chance to refresh for demo
                print(f"Refreshing data for ZIP {zip_code}...")
                result = await agent.refresh_sentiment_for_zip(zip_code, force=True)
                
                if result.get('refreshed', False):
                    print(f"Successfully refreshed data, score: {result.get('score', 0):.2f}")
                    print(f"Summary: {result.get('summary', '')[:100]}...")
                else:
                    print(f"Failed to refresh data: {result.get('reason')}")
            else:
                print(f"Skipping refresh, data is still fresh")
        else:
            print(f"No cached data found for ZIP {zip_code}")
            print(f"Refreshing data...")
            result = await agent.refresh_sentiment_for_zip(zip_code, force=True)
            
            if result.get('refreshed', False):
                print(f"Successfully refreshed data, score: {result.get('score', 0):.2f}")
            else:
                print(f"Failed to refresh data: {result.get('reason')}")
    
    print("\nRunning batch refresh...")
    batch_result = await agent.refresh_batch(limit=3)
    print(f"Batch refresh completed: {batch_result['refreshed']}/{batch_result['total']} neighborhoods refreshed")


if __name__ == "__main__":
    asyncio.run(main())
