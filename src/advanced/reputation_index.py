"""
Neighborhood Reputation Index

This module calculates a comprehensive reputation index for neighborhoods
based on sentiment analysis, data freshness, and content richness.

It provides a standardized 0-100 score that can be used for comparison
across different neighborhoods and regions.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')


class ReputationIndex:
    """Calculates and manages neighborhood reputation indices."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the reputation index calculator.
        
        Args:
            db_path: Path to the SQLite database with neighborhood data
        """
        self.db_path = db_path
        self._ensure_index_table()
    
    def _ensure_index_table(self):
        """
        Ensure the reputation index table exists in the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reputation_index (
            zip_code TEXT PRIMARY KEY,
            neighborhood TEXT,
            city TEXT,
            index_score REAL,
            data_volume INTEGER,
            data_freshness INTEGER,
            sentiment_score REAL,
            last_updated TEXT,
            metadata TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_cached_sentiment(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Get cached sentiment data for a ZIP code.
        
        Args:
            zip_code: The ZIP code to get data for
            
        Returns:
            Dictionary with cached sentiment data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First try to find by exact ZIP code match
        cursor.execute('''
        SELECT * FROM neighborhood_cache
        WHERE neighborhood = ? OR city = ?
        ''', (zip_code, zip_code))
        
        row = cursor.fetchone()
        
        if not row:
            # Try to find by ZIP code prefix (first 3 digits)
            zip_prefix = zip_code[:3] if len(zip_code) >= 3 else zip_code
            cursor.execute('''
            SELECT * FROM neighborhood_cache
            WHERE neighborhood LIKE ? OR city LIKE ?
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
                data['parsed_data'] = json.loads(data['data'])
            except json.JSONDecodeError:
                data['parsed_data'] = {}
        
        # Calculate age in days
        if 'last_updated' in data and data['last_updated']:
            try:
                last_updated = datetime.fromisoformat(data['last_updated'])
                data['age_days'] = (datetime.now() - last_updated).days
            except (ValueError, TypeError):
                data['age_days'] = 30  # Default to 30 days if date parsing fails
        else:
            data['age_days'] = 30
        
        # Get post count
        cursor = conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM neighborhood_posts
        WHERE neighborhood = ? OR neighborhood LIKE ?
        ''', (zip_code, f"{zip_prefix}%"))
        
        post_count = cursor.fetchone()[0]
        data['posts'] = post_count
        
        # Get average sentiment score
        cursor.execute('''
        SELECT data FROM sentiment_analysis
        WHERE neighborhood = ? OR neighborhood LIKE ?
        ''', (zip_code, f"{zip_prefix}%"))
        
        row = cursor.fetchone()
        if row and row[0]:
            try:
                sentiment_data = json.loads(row[0])
                overall_sentiment = sentiment_data.get('overall_sentiment', {})
                data['avg_score'] = overall_sentiment.get('score', 0) * 50 + 50  # Convert from [-1,1] to [0,100]
            except (json.JSONDecodeError, KeyError):
                data['avg_score'] = 50  # Default to neutral if parsing fails
        else:
            data['avg_score'] = 50
        
        # Get summary if available
        cursor.execute('''
        SELECT analysis_data FROM sentiment_analysis
        WHERE neighborhood = ? OR neighborhood LIKE ?
        ''', (zip_code, f"{zip_prefix}%"))
        
        row = cursor.fetchone()
        if row and row[0]:
            try:
                analysis_data = json.loads(row[0])
                data['summary'] = analysis_data.get('summary', '')
            except json.JSONDecodeError:
                data['summary'] = ''
        else:
            data['summary'] = ''
        
        return data
    
    def compute_reputation_index(self, zip_code: str) -> Dict[str, Any]:
        """
        Compute a reputation index for a ZIP code.
        
        Args:
            zip_code: The ZIP code to compute index for
            
        Returns:
            Dictionary with reputation index data
        """
        # Get cached sentiment data
        cached = self.get_cached_sentiment(zip_code)
        
        if not cached:
            logger.warning(f"No data available for ZIP code {zip_code}")
            return {
                "zip": zip_code,
                "score": 0,
                "message": "No data available",
                "age": None,
                "volume": 0,
                "summary": None
            }
        
        # Calculate freshness penalty (0-30 days old)
        age_days = cached.get('age_days', 30)
        freshness_penalty = max(0, min(30, age_days)) * 0.5  # 0.5 points per day of age
        
        # Calculate volume bonus (0-20 points)
        post_count = cached.get('posts', 0)
        volume_bonus = min(20, post_count * 0.5)  # 0.5 points per post, max 20
        
        # Get base sentiment score (0-100)
        base_score = cached.get('avg_score', 50)
        
        # Calculate final score
        score = max(0, min(100, base_score + volume_bonus - freshness_penalty))
        
        # Get neighborhood and city
        neighborhood = cached.get('neighborhood', zip_code)
        city = cached.get('city', '')
        
        # Get summary
        summary = cached.get('summary', '')
        
        # Create result
        result = {
            "zip": zip_code,
            "neighborhood": neighborhood,
            "city": city,
            "score": round(score, 1),
            "age": age_days,
            "volume": post_count,
            "summary": summary,
            "components": {
                "base_score": round(base_score, 1),
                "volume_bonus": round(volume_bonus, 1),
                "freshness_penalty": round(freshness_penalty, 1)
            }
        }
        
        # Store in database
        self._store_index(result)
        
        return result
    
    def _store_index(self, index_data: Dict[str, Any]):
        """
        Store reputation index data in the database.
        
        Args:
            index_data: Dictionary with index data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO reputation_index
        (zip_code, neighborhood, city, index_score, data_volume, data_freshness, 
         sentiment_score, last_updated, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            index_data['zip'],
            index_data.get('neighborhood', index_data['zip']),
            index_data.get('city', ''),
            index_data['score'],
            index_data['volume'],
            index_data['age'],
            index_data['components']['base_score'],
            datetime.now().isoformat(),
            json.dumps(index_data['components'])
        ))
        
        conn.commit()
        conn.close()
    
    def get_stored_index(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Get stored reputation index for a ZIP code.
        
        Args:
            zip_code: The ZIP code to get index for
            
        Returns:
            Dictionary with reputation index or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM reputation_index
        WHERE zip_code = ?
        ''', (zip_code,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Convert row to dictionary
        result = dict(row)
        
        # Parse metadata JSON
        if 'metadata' in result and result['metadata']:
            try:
                result['components'] = json.loads(result['metadata'])
                del result['metadata']
            except json.JSONDecodeError:
                result['components'] = {}
        
        # Calculate age of index
        if 'last_updated' in result and result['last_updated']:
            try:
                last_updated = datetime.fromisoformat(result['last_updated'])
                result['index_age_days'] = (datetime.now() - last_updated).days
            except (ValueError, TypeError):
                result['index_age_days'] = 0
        
        return result
    
    def compare_neighborhoods(self, zip_codes: List[str]) -> Dict[str, Any]:
        """
        Compare reputation indices for multiple ZIP codes.
        
        Args:
            zip_codes: List of ZIP codes to compare
            
        Returns:
            Dictionary with comparison results
        """
        results = []
        
        for zip_code in zip_codes:
            # Check if we have a stored index
            stored = self.get_stored_index(zip_code)
            
            # If stored index is recent (less than 7 days old), use it
            if stored and stored.get('index_age_days', 99) < 7:
                results.append(stored)
            else:
                # Otherwise compute a new index
                index = self.compute_reputation_index(zip_code)
                results.append(index)
        
        # Sort by score (descending)
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Calculate average score
        avg_score = sum(r.get('score', 0) for r in results) / len(results) if results else 0
        
        return {
            "neighborhoods": results,
            "count": len(results),
            "average_score": round(avg_score, 1),
            "top_neighborhood": results[0] if results else None,
            "comparison_date": datetime.now().isoformat()
        }


def compute_reputation_index(zip_code: str) -> Dict[str, Any]:
    """
    Compute a reputation index for a ZIP code.
    
    Args:
        zip_code: The ZIP code to compute index for
        
    Returns:
        Dictionary with reputation index data
    """
    index = ReputationIndex()
    return index.compute_reputation_index(zip_code)


if __name__ == "__main__":
    # Example usage
    test_zips = ["30318", "11238", "94110"]
    
    index = ReputationIndex()
    
    print("\nComputing Individual Reputation Indices:")
    for zip_code in test_zips:
        result = index.compute_reputation_index(zip_code)
        print(f"\nZIP {zip_code}: Score {result['score']}/100")
        print(f"Components: Base={result['components']['base_score']}, Volume Bonus={result['components']['volume_bonus']}, Freshness Penalty={result['components']['freshness_penalty']}")
    
    print("\nComparing Neighborhoods:")
    comparison = index.compare_neighborhoods(test_zips)
    print(f"Average Score: {comparison['average_score']}/100")
    print(f"Top Neighborhood: {comparison['top_neighborhood']['zip']} with score {comparison['top_neighborhood']['score']}/100")
