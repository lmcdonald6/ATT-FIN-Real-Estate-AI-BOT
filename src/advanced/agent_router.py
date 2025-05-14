"""
Manus Agent Router

This module provides intelligent routing of data collection tasks to the most
appropriate sources based on region characteristics, data quality, and availability.

It implements a strategy pattern to select the optimal data source for each
neighborhood or ZIP code, maximizing data quality and coverage.
"""

import json
import logging
import os
import random
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')

# Region-specific data sources
REGION_SOURCES = {
    # Major metro areas with specialized sources
    "nyc": ["Reddit", "StreetEasy", "NYTimes", "Nextdoor"],
    "la": ["Reddit", "YouTube", "LAist", "Nextdoor"],
    "sf": ["Reddit", "SFGate", "Nextdoor", "Medium"],
    "chicago": ["Reddit", "ChicagoTribune", "Nextdoor", "BlockClub"],
    "boston": ["Reddit", "BostonGlobe", "Nextdoor", "UniversalHub"],
    "dc": ["Reddit", "WashingtonPost", "Nextdoor", "DCist"],
    "atl": ["Reddit", "AJC", "Twitter", "Nextdoor"],
    "miami": ["Reddit", "MiamiHerald", "Twitter", "Nextdoor"],
    "dallas": ["Reddit", "DallasMorningNews", "Nextdoor"],
    "houston": ["Reddit", "HoustonChronicle", "Nextdoor"],
    
    # Default sources for other regions
    "default": ["Reddit", "Twitter", "Nextdoor", "LocalNews"]
}

# ZIP code prefixes for major metro areas
ZIP_REGIONS = {
    "100": "nyc",  # Manhattan
    "101": "nyc",  # Manhattan
    "102": "nyc",  # Manhattan
    "103": "nyc",  # Staten Island
    "104": "nyc",  # Bronx
    "112": "nyc",  # Brooklyn
    "113": "nyc",  # Queens
    "114": "nyc",  # Queens
    "116": "nyc",  # Queens
    "900": "la",   # Los Angeles
    "902": "la",   # Los Angeles
    "913": "la",   # Los Angeles County
    "917": "la",   # Industry
    "940": "sf",   # San Francisco
    "941": "sf",   # San Francisco
    "943": "sf",   # San Mateo
    "945": "sf",   # Oakland
    "946": "sf",   # Oakland
    "606": "chicago",  # Chicago
    "607": "chicago",  # Chicago
    "021": "boston",   # Boston
    "022": "boston",   # Boston
    "200": "dc",       # Washington DC
    "202": "dc",       # Washington DC
    "203": "dc",       # Washington DC
    "303": "atl",      # Atlanta
    "311": "atl",      # Atlanta
    "331": "miami",    # Miami
    "332": "miami",    # Miami
    "752": "dallas",   # Dallas
    "753": "dallas",   # Dallas
    "770": "houston",  # Houston
    "772": "houston",  # Houston
}


class DataSourceStrategy:
    """Base class for data source selection strategies."""
    
    def select_source(self, zip_code: str, region: str) -> str:
        """
        Select a data source for the given ZIP code and region.
        
        Args:
            zip_code: The ZIP code to select a source for
            region: The region the ZIP code belongs to
            
        Returns:
            Name of the selected data source
        """
        raise NotImplementedError("Subclasses must implement select_source")


class RandomSourceStrategy(DataSourceStrategy):
    """Strategy that randomly selects a source from the available options."""
    
    def select_source(self, zip_code: str, region: str) -> str:
        """
        Randomly select a data source from the available options for the region.
        
        Args:
            zip_code: The ZIP code to select a source for
            region: The region the ZIP code belongs to
            
        Returns:
            Name of the selected data source
        """
        sources = REGION_SOURCES.get(region, REGION_SOURCES["default"])
        return random.choice(sources)


class PrimarySourceStrategy(DataSourceStrategy):
    """Strategy that selects the primary (first) source for a region."""
    
    def select_source(self, zip_code: str, region: str) -> str:
        """
        Select the primary (first) data source for the region.
        
        Args:
            zip_code: The ZIP code to select a source for
            region: The region the ZIP code belongs to
            
        Returns:
            Name of the selected data source
        """
        sources = REGION_SOURCES.get(region, REGION_SOURCES["default"])
        return sources[0] if sources else "Reddit"  # Default to Reddit if no sources


class SuccessRateStrategy(DataSourceStrategy):
    """Strategy that selects the source with the highest success rate for the region."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the success rate strategy.
        
        Args:
            db_path: Path to the SQLite database with source tracking data
        """
        self.db_path = db_path
        self._ensure_source_tracking_table()
    
    def _ensure_source_tracking_table(self):
        """
        Ensure the source tracking table exists in the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS source_tracking (
            region TEXT,
            source TEXT,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            last_success TEXT,
            last_failure TEXT,
            PRIMARY KEY (region, source)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def select_source(self, zip_code: str, region: str) -> str:
        """
        Select the data source with the highest success rate for the region.
        
        Args:
            zip_code: The ZIP code to select a source for
            region: The region the ZIP code belongs to
            
        Returns:
            Name of the selected data source
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get available sources for the region
        sources = REGION_SOURCES.get(region, REGION_SOURCES["default"])
        
        # Get success rates for each source
        source_rates = {}
        for source in sources:
            cursor.execute('''
            SELECT success_count, failure_count FROM source_tracking
            WHERE region = ? AND source = ?
            ''', (region, source))
            
            row = cursor.fetchone()
            
            if row:
                success_count, failure_count = row
                total = success_count + failure_count
                if total > 0:
                    source_rates[source] = success_count / total
                else:
                    source_rates[source] = 0.5  # Default to 50% if no data
            else:
                source_rates[source] = 0.5  # Default to 50% if no data
        
        conn.close()
        
        # Select the source with the highest success rate
        if not source_rates:
            return "Reddit"  # Default to Reddit if no sources
        
        return max(source_rates.items(), key=lambda x: x[1])[0]
    
    def update_source_success(self, region: str, source: str, success: bool):
        """
        Update the success/failure count for a source in a region.
        
        Args:
            region: The region
            source: The data source
            success: Whether the source was successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        if success:
            cursor.execute('''
            INSERT INTO source_tracking (region, source, success_count, failure_count, last_success)
            VALUES (?, ?, 1, 0, ?)
            ON CONFLICT(region, source) DO UPDATE SET
                success_count = success_count + 1,
                last_success = ?
            ''', (region, source, now, now))
        else:
            cursor.execute('''
            INSERT INTO source_tracking (region, source, success_count, failure_count, last_failure)
            VALUES (?, ?, 0, 1, ?)
            ON CONFLICT(region, source) DO UPDATE SET
                failure_count = failure_count + 1,
                last_failure = ?
            ''', (region, source, now, now))
        
        conn.commit()
        conn.close()


class ManusAgentRouter:
    """Router that selects the optimal data source for each neighborhood or ZIP code."""
    
    def __init__(self, db_path: str = DB_PATH, strategy: str = "success_rate"):
        """
        Initialize the Manus agent router.
        
        Args:
            db_path: Path to the SQLite database
            strategy: The strategy to use for source selection
                      ("random", "primary", or "success_rate")
        """
        self.db_path = db_path
        self.strategy_name = strategy
        
        # Initialize the appropriate strategy
        if strategy == "random":
            self.strategy = RandomSourceStrategy()
        elif strategy == "primary":
            self.strategy = PrimarySourceStrategy()
        elif strategy == "success_rate":
            self.strategy = SuccessRateStrategy(db_path)
        else:
            logger.warning(f"Unknown strategy '{strategy}', defaulting to success_rate")
            self.strategy = SuccessRateStrategy(db_path)
    
    def get_region_for_zip(self, zip_code: str) -> str:
        """
        Determine the region for a ZIP code.
        
        Args:
            zip_code: The ZIP code to get the region for
            
        Returns:
            Region name
        """
        # Clean up ZIP code
        zip_code = zip_code.strip().replace("-", "")[:5]
        
        # Try to match by first 3 digits
        if len(zip_code) >= 3:
            prefix = zip_code[:3]
            if prefix in ZIP_REGIONS:
                return ZIP_REGIONS[prefix]
        
        # If no match, return default
        return "default"
    
    def choose_agent_source(self, zip_code: str) -> str:
        """
        Choose the optimal data source for a ZIP code.
        
        Args:
            zip_code: The ZIP code to choose a source for
            
        Returns:
            Name of the selected data source
        """
        # Determine the region for the ZIP code
        region = self.get_region_for_zip(zip_code)
        
        # Use the strategy to select a source
        source = self.strategy.select_source(zip_code, region)
        
        logger.info(f"Selected source '{source}' for ZIP {zip_code} (region: {region}) using {self.strategy_name} strategy")
        
        return source
    
    def report_source_result(self, zip_code: str, source: str, success: bool):
        """
        Report the result of using a data source for a ZIP code.
        
        Args:
            zip_code: The ZIP code the source was used for
            source: The data source that was used
            success: Whether the source was successful
        """
        # Only track results if using success rate strategy
        if isinstance(self.strategy, SuccessRateStrategy):
            region = self.get_region_for_zip(zip_code)
            self.strategy.update_source_success(region, source, success)
            
            logger.info(f"Reported {success and 'success' or 'failure'} for source '{source}' in region '{region}'")
    
    def get_all_sources_for_zip(self, zip_code: str) -> List[str]:
        """
        Get all available data sources for a ZIP code, in priority order.
        
        Args:
            zip_code: The ZIP code to get sources for
            
        Returns:
            List of data source names
        """
        region = self.get_region_for_zip(zip_code)
        return REGION_SOURCES.get(region, REGION_SOURCES["default"])


def choose_agent_source(zip_code: str) -> str:
    """
    Choose the optimal data source for a ZIP code.
    
    Args:
        zip_code: The ZIP code to choose a source for
        
    Returns:
        Name of the selected data source
    """
    router = ManusAgentRouter()
    return router.choose_agent_source(zip_code)


if __name__ == "__main__":
    # Example usage
    router = ManusAgentRouter()
    
    test_zips = ["10001", "90210", "94107", "60601", "30318", "33139", "75201", "77002", "12345"]
    
    print("Testing Manus Agent Router:")
    for zip_code in test_zips:
        source = router.choose_agent_source(zip_code)
        region = router.get_region_for_zip(zip_code)
        all_sources = router.get_all_sources_for_zip(zip_code)
        
        print(f"\nZIP: {zip_code} (Region: {region})")
        print(f"Selected source: {source}")
        print(f"All available sources: {', '.join(all_sources)}")
        
        # Simulate some successes and failures to test tracking
        if random.random() < 0.7:  # 70% success rate
            router.report_source_result(zip_code, source, True)
            print(f"Reported SUCCESS for {source}")
        else:
            router.report_source_result(zip_code, source, False)
            print(f"Reported FAILURE for {source}")
