"""
Redfin Data Center client for accessing official market data.
Documentation: https://www.redfin.com/news/data-center/

Data provided by Redfin, a national real estate brokerage.
See https://www.redfin.com/news/data-center/ for terms of use.
"""
import logging
import aiohttp
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

class RedfinClient:
    """Client for accessing Redfin Data Center."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Official Redfin Data Center URLs with proper attribution
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; PropertyAnalyzer/1.0; +https://www.redfin.com/news/data-center/)",
            "Referer": "https://www.redfin.com/news/data-center/",
            "Accept": "text/html,application/json"
        }
        
        # Downloadable data URLs
        self.region_data_url = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv.gz"
        self.city_data_url = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/city_market_tracker.tsv.gz"
        self.county_data_url = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/county_market_tracker.tsv.gz"
        
        # Cache for market data
        self._market_data_cache = {}
        self._last_cache_update = None
        self._cache_ttl_hours = 24
    
    async def get_market_stats(self, zip_code: str) -> Optional[Dict]:
        """
        Get market statistics for a ZIP code using Redfin's official data.
        Data is updated monthly and includes key market metrics.
        """
        try:
            # Check if we need to refresh cache
            if self._should_refresh_cache():
                await self._update_market_data()
            
            # Get data from cache
            if zip_code in self._market_data_cache:
                self.logger.info(f"Using cached data for {zip_code}")
                return self._market_data_cache[zip_code]
            
            self.logger.warning(f"No data available for {zip_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market stats: {e}")
            return None
    
    def _should_refresh_cache(self) -> bool:
        """Check if market data cache needs refresh."""
        if not self._last_cache_update:
            return True
        
        hours_since_update = (datetime.now() - self._last_cache_update).total_seconds() / 3600
        return hours_since_update >= self._cache_ttl_hours
    
    async def _update_market_data(self):
        """Update market data cache from Redfin Data Center."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Get ZIP code level data
                async with session.get(self.region_data_url) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        df = pd.read_csv(
                            pd.StringIO(content),
                            sep='\t',
                            compression='gzip',
                            encoding='utf-8'
                        )
                        self._process_market_data(df)
                        self._last_cache_update = datetime.now()
                        self.logger.info("Successfully updated Redfin market data")
                    else:
                        self.logger.error(f"Error fetching region data: {resp.status}")
                
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}")
    
    def _process_market_data(self, df: pd.DataFrame):
        """Process and cache market data from Redfin."""
        try:
            # Group by region/zip and get latest data
            by_region = df.groupby('region').last().reset_index()
            
            for _, row in by_region.iterrows():
                market_stats = {
                    # Price metrics
                    "median_price": row.get('median_sale_price', 0),
                    "median_price_sqft": row.get('median_price_per_sqft', 0),
                    "avg_price_sqft": row.get('avg_price_per_sqft', 0),
                    
                    # Inventory metrics
                    "inventory": row.get('inventory', 0),
                    "new_listings": row.get('new_listings', 0),
                    "homes_sold": row.get('homes_sold', 0),
                    
                    # Market dynamics
                    "median_dom": row.get('median_dom', 0),
                    "price_drops": row.get('price_drops_share', 0),
                    "sale_to_list": row.get('sale_to_list_ratio', 0),
                    
                    # Year-over-year changes
                    "yoy_price_change": row.get('median_sale_price_yoy', 0),
                    "yoy_inventory_change": row.get('inventory_yoy', 0),
                    
                    # Metadata
                    "period": row.get('period_begin', ''),
                    "region_type": row.get('region_type', ''),
                    "last_updated": datetime.now().isoformat(),
                    "data_source": "redfin"
                }
                
                # Cache the processed data
                region = str(row.get('region', ''))
                if region:
                    self._market_data_cache[region] = market_stats
                
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
    
    def get_cached_regions(self) -> List[str]:
        """Get list of regions/ZIPs with available data."""
        return list(self._market_data_cache.keys())
