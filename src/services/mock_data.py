"""Mock data service for development and testing."""

import json
import os
from typing import Dict, List, Optional
import random
from datetime import datetime, timedelta

class MockDataService:
    """Provides mock data for all external API services."""
    
    def __init__(self):
        """Initialize the mock data service."""
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "demo_data")
        self.cache = {}
    
    def get_property_data(self, zipcode: str) -> Dict:
        """Mock ATTOM API property data."""
        cache_key = f"property_{zipcode}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            with open(os.path.join(self.data_dir, f"{zipcode}.json"), "r") as f:
                data = json.load(f)
                self.cache[cache_key] = data
                return data
        except FileNotFoundError:
            # Generate random data if file doesn't exist
            return self._generate_mock_property_data(zipcode)
    
    def _generate_mock_property_data(self, zipcode: str) -> Dict:
        """Generate random property data."""
        base_score = random.randint(60, 90)
        
        data = {
            "zipcode": zipcode,
            "location": {
                "city": "Sample City",
                "state": "ST",
                "lat": round(random.uniform(25, 48), 4),
                "lng": round(random.uniform(-123, -70), 4)
            },
            "signals": {
                "permits": {
                    "permit_score": round(random.uniform(max(50, base_score-20), min(100, base_score+20)), 1),
                    "residential_permits": random.randint(20, 100),
                    "commercial_permits": random.randint(5, 30),
                    "renovation_permits": random.randint(50, 200)
                },
                "demographics": {
                    "migration_score": round(random.uniform(max(50, base_score-20), min(100, base_score+20)), 1),
                    "population_growth": round(random.uniform(0.5, 5.0), 1),
                    "median_income": random.randint(45000, 150000),
                    "median_age": random.randint(25, 45),
                    "employment_rate": round(random.uniform(0.92, 0.98), 2)
                },
                "crime": {
                    "crime_score": round(random.uniform(max(50, base_score-20), min(100, base_score+20)), 1),
                    "violent_crime_rate": round(random.uniform(100, 500), 1),
                    "property_crime_rate": round(random.uniform(1000, 3000), 1),
                    "crime_trend": round(random.uniform(-10, 0), 1)
                },
                "transit": {
                    "transit_score": round(random.uniform(max(50, base_score-20), min(100, base_score+20)), 1),
                    "public_transit_stops": random.randint(10, 50),
                    "bus_lines": random.randint(2, 10),
                    "rail_lines": random.randint(0, 3),
                    "avg_commute_time": round(random.uniform(15, 45), 1)
                },
                "zoning": {
                    "zoning_score": round(random.uniform(max(50, base_score-20), min(100, base_score+20)), 1),
                    "mixed_use": round(random.uniform(10, 40), 1),
                    "development_potential": round(random.uniform(40, 80), 1),
                    "density_allowed": random.randint(20, 60),
                    "zoning_changes": [
                        {
                            "type": random.choice(["density_increase", "mixed_use", "commercial"]),
                            "date": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                            "details": "Proposed zoning change"
                        }
                    ]
                }
            },
            "market_stats": {
                "median_home_price": random.randint(200000, 1000000),
                "price_growth_1y": round(random.uniform(3, 15), 1),
                "rental_vacancy": round(random.uniform(2, 8), 1),
                "cap_rate_avg": round(random.uniform(4, 8), 1)
            },
            "opportunities": [
                {
                    "type": random.choice(["development", "renovation", "acquisition"]),
                    "description": "Investment opportunity in growing area",
                    "roi_estimate": round(random.uniform(8, 20), 1)
                }
            ]
        }
        
        # Cache the generated data
        self.cache[f"property_{zipcode}"] = data
        return data
    
    def get_market_trends(self, zipcode: str) -> Dict:
        """Mock market trend data."""
        months = 12
        base_value = random.randint(200000, 800000)
        trend = random.uniform(0.002, 0.008)  # Monthly growth rate
        
        prices = []
        for i in range(months):
            month_value = base_value * (1 + trend) ** i
            prices.append({
                "month": (datetime.now() - timedelta(months=months-i-1)).strftime("%Y-%m"),
                "median_price": round(month_value, 2),
                "inventory": random.randint(50, 200),
                "days_on_market": random.randint(20, 60)
            })
        
        return {
            "zipcode": zipcode,
            "trend_data": prices,
            "forecast": {
                "price_forecast": round(base_value * (1 + trend) ** (months + 3), 2),
                "confidence": random.uniform(0.7, 0.9),
                "factors": [
                    "Population growth",
                    "Job market expansion",
                    "Infrastructure development"
                ]
            }
        }
    
    def get_comparable_properties(self, zipcode: str, property_type: str = "residential") -> List[Dict]:
        """Mock comparable properties data."""
        base_price = random.randint(200000, 800000)
        comps = []
        
        for _ in range(random.randint(5, 10)):
            price_variation = random.uniform(0.8, 1.2)
            comps.append({
                "address": f"{random.randint(100, 999)} Sample St",
                "price": round(base_price * price_variation, 2),
                "sqft": random.randint(1500, 4000),
                "beds": random.randint(2, 5),
                "baths": random.randint(2, 4),
                "year_built": random.randint(1970, 2020),
                "days_on_market": random.randint(0, 90),
                "price_per_sqft": round(base_price * price_variation / random.randint(1500, 4000), 2)
            })
        
        return comps

mock_data_service = MockDataService()
