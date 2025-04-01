"""
Market analyzer for property data generation and analysis.
Uses historical trends and market dynamics.
"""
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class MarketAnalyzer:
    """
    Analyzes market trends and generates realistic property data.
    Uses historical patterns and market dynamics.
    """
    
    def __init__(self):
        # Market characteristics by ZIP
        self.market_data = {
            # Nashville Markets
            "37215": {  # Belle Meade/Green Hills
                "price_range": (600000, 1200000),
                "price_trend": 0.08,  # 8% annual appreciation
                "inventory_trend": -0.05,  # Declining inventory
                "dom_range": (15, 45),
                "property_mix": {
                    "Single Family": 0.65,
                    "Townhouse": 0.20,
                    "Condo": 0.15
                },
                "lot_sizes": (0.25, 1.0),  # Acres
                "year_built_range": (1950, 2024)
            },
            "37203": {  # Downtown/Midtown
                "price_range": (400000, 800000),
                "price_trend": 0.06,
                "inventory_trend": 0.02,
                "dom_range": (20, 60),
                "property_mix": {
                    "Condo": 0.45,
                    "Townhouse": 0.35,
                    "Single Family": 0.20
                },
                "lot_sizes": (0.1, 0.3),
                "year_built_range": (1960, 2024)
            },
            # Atlanta Markets
            "30305": {  # Buckhead
                "price_range": (500000, 1000000),
                "price_trend": 0.07,
                "inventory_trend": -0.03,
                "dom_range": (20, 50),
                "property_mix": {
                    "Single Family": 0.55,
                    "Condo": 0.30,
                    "Townhouse": 0.15
                },
                "lot_sizes": (0.2, 0.8),
                "year_built_range": (1955, 2024)
            },
            "30308": {  # Midtown
                "price_range": (300000, 600000),
                "price_trend": 0.05,
                "inventory_trend": 0.04,
                "dom_range": (25, 65),
                "property_mix": {
                    "Condo": 0.50,
                    "Townhouse": 0.30,
                    "Single Family": 0.20
                },
                "lot_sizes": (0.1, 0.25),
                "year_built_range": (1965, 2024)
            },
            # Dallas Markets
            "75225": {  # Highland Park
                "price_range": (800000, 1600000),
                "price_trend": 0.09,
                "inventory_trend": -0.06,
                "dom_range": (10, 40),
                "property_mix": {
                    "Single Family": 0.75,
                    "Townhouse": 0.15,
                    "Condo": 0.10
                },
                "lot_sizes": (0.3, 1.2),
                "year_built_range": (1945, 2024)
            },
            "75201": {  # Downtown
                "price_range": (400000, 800000),
                "price_trend": 0.06,
                "inventory_trend": 0.03,
                "dom_range": (20, 55),
                "property_mix": {
                    "Condo": 0.55,
                    "Townhouse": 0.35,
                    "Single Family": 0.10
                },
                "lot_sizes": (0.1, 0.3),
                "year_built_range": (1970, 2024)
            }
        }
        
        # Seasonal adjustments (monthly factors)
        self.seasonal_factors = {
            1: 0.95,   # January
            2: 0.97,   # February
            3: 1.00,   # March
            4: 1.02,   # April
            5: 1.03,   # May
            6: 1.04,   # June
            7: 1.03,   # July
            8: 1.02,   # August
            9: 1.00,   # September
            10: 0.98,  # October
            11: 0.96,  # November
            12: 0.94   # December
        }
    
    def get_market_stats(self, zip_code: str) -> Dict:
        """Get market statistics for a ZIP code."""
        market = self.market_data.get(zip_code, {})
        if not market:
            return self._get_default_market_stats()
        
        current_month = datetime.now().month
        seasonal_factor = self.seasonal_factors[current_month]
        
        min_price, max_price = market["price_range"]
        median_price = (min_price + max_price) / 2
        
        return {
            "median_price": median_price * seasonal_factor,
            "price_trend": market["price_trend"],
            "inventory_trend": market["inventory_trend"],
            "median_dom": sum(market["dom_range"]) / 2,
            "property_mix": market["property_mix"],
            "lot_sizes": market["lot_sizes"],
            "year_built_range": market["year_built_range"]
        }
    
    def generate_property_attributes(
        self,
        zip_code: str,
        property_type: str = None
    ) -> Dict:
        """Generate realistic property attributes based on market."""
        market = self.market_data.get(zip_code, {})
        if not market:
            return self._generate_default_attributes()
        
        # Get or select property type
        if not property_type:
            property_type = self._weighted_choice(market["property_mix"])
        
        # Base price range
        min_price, max_price = market["price_range"]
        
        # Apply property type adjustments
        if property_type == "Condo":
            min_price *= 0.8
            max_price *= 0.9
        elif property_type == "Townhouse":
            min_price *= 0.85
            max_price *= 0.95
        
        # Generate attributes
        price = self._random_range(min_price, max_price)
        sqft = self._calculate_sqft(price, property_type, zip_code)
        
        return {
            "price": round(price, -3),  # Round to nearest thousand
            "sqft": round(sqft, -2),    # Round to nearest hundred
            "bedrooms": self._get_bedrooms(sqft, property_type),
            "bathrooms": self._get_bathrooms(sqft, property_type),
            "year_built": self._random_range(*market["year_built_range"]),
            "lot_size": self._random_range(*market["lot_sizes"]),
            "days_on_market": self._random_range(*market["dom_range"]),
            "property_type": property_type
        }
    
    def _calculate_sqft(
        self,
        price: float,
        property_type: str,
        zip_code: str
    ) -> float:
        """Calculate square footage based on price and property type."""
        # Base price per sqft
        base_ppsf = {
            "37215": 300, "37203": 350,  # Nashville
            "30305": 275, "30308": 325,  # Atlanta
            "75225": 350, "75201": 375   # Dallas
        }.get(zip_code, 250)
        
        # Adjust for property type
        type_factors = {
            "Single Family": 1.0,
            "Townhouse": 1.1,
            "Condo": 1.2
        }
        
        adjusted_ppsf = base_ppsf * type_factors[property_type]
        return price / adjusted_ppsf
    
    def _get_bedrooms(self, sqft: float, property_type: str) -> int:
        """Calculate bedrooms based on square footage."""
        if property_type == "Condo":
            base = max(1, int(sqft / 800))
        else:
            base = max(2, int(sqft / 1000))
        return min(6, base)  # Cap at 6 bedrooms
    
    def _get_bathrooms(self, sqft: float, property_type: str) -> int:
        """Calculate bathrooms based on square footage."""
        if property_type == "Condo":
            base = max(1, int(sqft / 1000))
        else:
            base = max(2, int(sqft / 1200))
        return min(5, base)  # Cap at 5 bathrooms
    
    def _random_range(
        self,
        min_val: float,
        max_val: float,
        distribution: str = "normal"
    ) -> float:
        """Generate random number with specified distribution."""
        if distribution == "normal":
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6  # 99.7% within range
            value = np.random.normal(mean, std)
            return max(min_val, min(max_val, value))
        else:
            return np.random.uniform(min_val, max_val)
    
    def _weighted_choice(self, options: Dict[str, float]) -> str:
        """Choose random item with weights."""
        items = list(options.keys())
        weights = list(options.values())
        return np.random.choice(items, p=weights)
    
    def _get_default_market_stats(self) -> Dict:
        """Get default market statistics."""
        return {
            "median_price": 300000,
            "price_trend": 0.05,
            "inventory_trend": 0.0,
            "median_dom": 45,
            "property_mix": {
                "Single Family": 0.6,
                "Townhouse": 0.25,
                "Condo": 0.15
            },
            "lot_sizes": (0.1, 0.5),
            "year_built_range": (1970, 2024)
        }
    
    def _generate_default_attributes(self) -> Dict:
        """Generate default property attributes."""
        price = self._random_range(200000, 400000)
        sqft = price / 200
        
        return {
            "price": round(price, -3),
            "sqft": round(sqft, -2),
            "bedrooms": 3,
            "bathrooms": 2,
            "year_built": 1990,
            "lot_size": 0.25,
            "days_on_market": 30,
            "property_type": "Single Family"
        }
