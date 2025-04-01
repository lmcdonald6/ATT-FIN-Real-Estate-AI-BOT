"""
Market analysis module for real estate data.
Provides market statistics and trends for property analysis.
"""
import logging
from typing import Dict, Optional
from datetime import datetime

class MarketAnalyzer:
    """Analyzes real estate market data and provides insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Market data by ZIP code
        self._market_data = {
            # Nashville affluent areas
            "37215": {  # Green Hills/Forest Hills
                "median_price": 850000,
                "price_per_sqft": 375,
                "dom_90th_percentile": 90,
                "market_type": "affluent",
                "last_updated": datetime.now().isoformat()
            },
            "37205": {  # Belle Meade/West End
                "median_price": 925000,
                "price_per_sqft": 400,
                "dom_90th_percentile": 85,
                "market_type": "affluent",
                "last_updated": datetime.now().isoformat()
            },
            "37027": {  # Brentwood
                "median_price": 875000,
                "price_per_sqft": 350,
                "dom_90th_percentile": 95,
                "market_type": "affluent",
                "last_updated": datetime.now().isoformat()
            },
            
            # Urban/trendy areas
            "37203": {  # The Gulch/Midtown
                "median_price": 550000,
                "price_per_sqft": 425,
                "dom_90th_percentile": 75,
                "market_type": "urban",
                "last_updated": datetime.now().isoformat()
            },
            "37206": {  # East Nashville
                "median_price": 475000,
                "price_per_sqft": 325,
                "dom_90th_percentile": 80,
                "market_type": "urban",
                "last_updated": datetime.now().isoformat()
            },
            "37208": {  # Germantown/North Nashville
                "median_price": 425000,
                "price_per_sqft": 300,
                "dom_90th_percentile": 85,
                "market_type": "urban",
                "last_updated": datetime.now().isoformat()
            },
            
            # Standard areas
            "37210": {  # South Nashville
                "median_price": 350000,
                "price_per_sqft": 250,
                "dom_90th_percentile": 100,
                "market_type": "standard",
                "last_updated": datetime.now().isoformat()
            },
            "37211": {  # South Nashville/Antioch
                "median_price": 325000,
                "price_per_sqft": 225,
                "dom_90th_percentile": 105,
                "market_type": "standard",
                "last_updated": datetime.now().isoformat()
            },
            "37217": {  # Airport Area
                "median_price": 300000,
                "price_per_sqft": 200,
                "dom_90th_percentile": 110,
                "market_type": "standard",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # Default market stats for unknown areas
        self._default_stats = {
            "median_price": 350000,
            "price_per_sqft": 250,
            "dom_90th_percentile": 100,
            "market_type": "standard",
            "last_updated": datetime.now().isoformat()
        }
    
    def get_market_stats(self, zip_code: str) -> Dict:
        """
        Get market statistics for a given ZIP code.
        Returns default stats if ZIP code not found.
        """
        try:
            return self._market_data.get(zip_code, self._default_stats)
        except Exception as e:
            self.logger.error(f"Error getting market stats: {e}")
            return self._default_stats.copy()
    
    def get_market_type(self, zip_code: str) -> str:
        """Get the market type for a ZIP code."""
        return self.get_market_stats(zip_code)["market_type"]
    
    def get_price_per_sqft(self, zip_code: str) -> float:
        """Get the average price per square foot for a ZIP code."""
        return self.get_market_stats(zip_code)["price_per_sqft"]
    
    def get_median_price(self, zip_code: str) -> int:
        """Get the median home price for a ZIP code."""
        return self.get_market_stats(zip_code)["median_price"]
    
    def get_dom_90th(self, zip_code: str) -> int:
        """Get the 90th percentile days on market for a ZIP code."""
        return self.get_market_stats(zip_code)["dom_90th_percentile"]
