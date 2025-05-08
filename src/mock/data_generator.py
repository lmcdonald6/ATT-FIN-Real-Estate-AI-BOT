import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class MockDataGenerator:
    def __init__(self):
        self.zip_codes = ['90210', '90211', '90212', '90025', '90024']
        self.street_names = ['Main St', 'Oak Ave', 'Maple Dr', 'Beverly Dr', 'Wilshire Blvd']
        self.cities = ['Beverly Hills', 'Los Angeles', 'Santa Monica', 'West Hollywood']
        self.property_types = ['Single Family', 'Multi Family', 'Condo', 'Townhouse']
        self.property_features = [
            'Pool', 'Garden', 'Garage', 'Renovated Kitchen', 'Solar Panels', 
            'Smart Home', 'Security System', 'Central AC', 'Fireplace', 'View'
        ]
        self.deal_types = ['Fix and Flip', 'Buy and Hold', 'Wholesale', 'BRRRR']
        
    def generate_property(self, property_id: str, scenario: str = 'normal') -> Dict:
        """Generate a single property with realistic data based on scenario"""
        sqft = random.randint(1000, 4000)
        
        # Adjust price per sqft based on scenario
        if scenario == 'distressed':
            price_per_sqft = random.uniform(200, 400)
            condition = 'Poor'
            days_on_market = random.randint(90, 180)
        elif scenario == 'luxury':
            price_per_sqft = random.uniform(800, 2000)
            condition = 'Excellent'
            days_on_market = random.randint(30, 90)
        else:  # normal
            price_per_sqft = random.uniform(400, 800)
            condition = random.choice(['Good', 'Fair', 'Excellent'])
            days_on_market = random.randint(15, 60)
            
        price = int(sqft * price_per_sqft)
        features = random.sample(self.property_features, random.randint(3, 6))
        
        return {
            "property_id": property_id,
            "address": f"{random.randint(100, 999)} {random.choice(self.street_names)}",
            "city": random.choice(self.cities),
            "state": "CA",
            "zip_code": random.choice(self.zip_codes),
            "price": price,
            "beds": random.randint(2, 6),
            "baths": random.randint(2, 5),
            "square_feet": sqft,
            "property_type": random.choice(self.property_types),
            "year_built": random.randint(1950, 2020),
            "lot_size": sqft * random.uniform(1.2, 2.5),
            "condition": condition,
            "features": features,
            "days_on_market": days_on_market,
            "price_history": self._generate_price_history(price),
            "tax_history": self._generate_tax_history(price),
            "lead_score": self._calculate_lead_score({
                "condition": condition,
                "days_on_market": days_on_market,
                "price": price,
                "market_avg": price * 1.1  # Simulated market average
            }),
            "recommended_strategy": self._recommend_strategy(scenario),
            "estimated_rehab": self._estimate_rehab_cost(condition, sqft),
            "zoning": random.choice(['R1', 'R2', 'R3', 'C1']),
            "last_sold": {
                "date": (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d'),
                "price": int(price * random.uniform(0.7, 0.9))
            }
        }
    
    def _generate_price_history(self, current_price: float) -> List[Dict]:
        """Generate price history for a property"""
        history = []
        price = current_price
        dates = []
        current_date = datetime.now()
        
        # Generate 3-5 historical price points
        for i in range(random.randint(3, 5)):
            date = current_date - timedelta(days=random.randint(i*365, (i+1)*365))
            dates.append(date)
            # Historical prices generally decrease as we go back in time
            price = price * random.uniform(0.85, 0.95)
            history.append({
                "date": date.strftime('%Y-%m-%d'),
                "price": int(price),
                "event": random.choice(['Listed', 'Sold', 'Price Reduced', 'Relisted'])
            })
            
        return sorted(history, key=lambda x: x['date'])
    
    def _generate_tax_history(self, current_price: float) -> List[Dict]:
        """Generate property tax history"""
        history = []
        assessed_value = current_price * 0.8  # Typically assessed value is lower than market value
        tax_rate = random.uniform(0.01, 0.015)  # 1-1.5% tax rate
        
        for year in range(datetime.now().year - 3, datetime.now().year + 1):
            history.append({
                "year": year,
                "assessed_value": int(assessed_value),
                "tax_amount": int(assessed_value * tax_rate)
            })
            assessed_value *= 1.02  # 2% annual increase
            
        return history
    
    def _calculate_lead_score(self, factors: Dict) -> float:
        """Calculate lead score based on various factors"""
        score = 7.0  # Base score
        
        # Adjust for condition
        condition_scores = {'Poor': 2.0, 'Fair': 1.0, 'Good': 0, 'Excellent': -1.0}
        score += condition_scores.get(factors['condition'], 0)
        
        # Adjust for days on market
        if factors['days_on_market'] > 90:
            score += 1.5
        elif factors['days_on_market'] > 60:
            score += 1.0
        
        # Adjust for price vs market
        price_ratio = factors['price'] / factors['market_avg']
        if price_ratio < 0.8:
            score += 2.0
        elif price_ratio < 0.9:
            score += 1.0
            
        return round(min(max(score, 1.0), 10.0), 1)  # Ensure score is between 1.0 and 10.0
    
    def _recommend_strategy(self, scenario: str) -> Dict:
        """Recommend investment strategy based on property scenario"""
        strategies = []
        
        if scenario == 'distressed':
            strategies = [
                {'type': 'Fix and Flip', 'confidence': random.uniform(0.8, 0.95)},
                {'type': 'Wholesale', 'confidence': random.uniform(0.7, 0.9)},
                {'type': 'BRRRR', 'confidence': random.uniform(0.6, 0.8)}
            ]
        elif scenario == 'luxury':
            strategies = [
                {'type': 'Buy and Hold', 'confidence': random.uniform(0.7, 0.9)},
                {'type': 'Fix and Flip', 'confidence': random.uniform(0.5, 0.7)},
                {'type': 'Wholesale', 'confidence': random.uniform(0.3, 0.5)}
            ]
        else:
            strategies = [
                {'type': random.choice(self.deal_types), 'confidence': random.uniform(0.6, 0.9)}
                for _ in range(3)
            ]
            
        return sorted(strategies, key=lambda x: x['confidence'], reverse=True)
    
    def _estimate_rehab_cost(self, condition: str, sqft: float) -> Dict:
        """Estimate rehabilitation costs based on property condition"""
        base_cost_per_sqft = {
            'Poor': random.uniform(80, 120),
            'Fair': random.uniform(40, 80),
            'Good': random.uniform(20, 40),
            'Excellent': random.uniform(5, 20)
        }
        
        base_cost = sqft * base_cost_per_sqft[condition]
        
        return {
            "total": int(base_cost),
            "breakdown": {
                "kitchen": int(base_cost * random.uniform(0.2, 0.3)),
                "bathrooms": int(base_cost * random.uniform(0.15, 0.25)),
                "flooring": int(base_cost * random.uniform(0.1, 0.2)),
                "electrical": int(base_cost * random.uniform(0.05, 0.15)),
                "plumbing": int(base_cost * random.uniform(0.05, 0.15)),
                "exterior": int(base_cost * random.uniform(0.1, 0.2)),
                "other": int(base_cost * random.uniform(0.05, 0.15))
            },
            "timeline": {
                "estimated_weeks": random.randint(4, 12),
                "complexity": random.choice(['Low', 'Medium', 'High'])
            }
        }
    
    def search_properties(self, criteria: Dict) -> List[Dict]:
        """Search properties based on criteria"""
        num_results = random.randint(3, 8)
        properties = []
        
        # Determine scenario based on criteria
        scenario = self._determine_scenario(criteria)
        
        for i in range(num_results):
            property_data = self.generate_property(str(i + 1), scenario)
            if self._matches_criteria(property_data, criteria):
                properties.append(property_data)
        
        return properties
    
    def _determine_scenario(self, criteria: Dict) -> str:
        """Determine property scenario based on search criteria"""
        if criteria.get('price_max') and criteria['price_max'] > 2000000:
            return 'luxury'
        elif criteria.get('condition') == 'Poor' or criteria.get('deal_type') in ['Fix and Flip', 'Wholesale']:
            return 'distressed'
        return 'normal'
    
    def _matches_criteria(self, property_data: Dict, criteria: Dict) -> bool:
        """Check if property matches search criteria"""
        if criteria.get('location'):
            if criteria['location'] not in [property_data['zip_code'], property_data['city']]:
                return False
                
        if criteria.get('property_type') and criteria['property_type'] != 'Any':
            if property_data['property_type'] != criteria['property_type']:
                return False
                
        if criteria.get('price_min') and property_data['price'] < criteria['price_min']:
            return False
            
        if criteria.get('price_max') and property_data['price'] > criteria['price_max']:
            return False
            
        if criteria.get('beds_min') and property_data['beds'] < criteria['beds_min']:
            return False
            
        if criteria.get('baths_min') and property_data['baths'] < criteria['baths_min']:
            return False
            
        if criteria.get('sqft_min') and property_data['square_feet'] < criteria['sqft_min']:
            return False
            
        if criteria.get('year_built_min') and property_data['year_built'] < criteria['year_built_min']:
            return False
            
        return True
    
    def generate_market_trends(self, zip_code: str) -> Dict:
        """Generate market trends for a specific area"""
        # Base price for the area
        base_price = random.uniform(700000, 1500000)
        
        # Generate dates and prices with an upward trend and some volatility
        dates = []
        prices = []
        inventory = []
        dom_trend = []  # Days on Market trend
        current_price = base_price
        current_inventory = random.randint(20, 50)
        current_dom = random.randint(30, 60)
        
        for i in range(180, 0, -30):  # 6 months of data
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Add some randomness to the price trend
            change = random.uniform(-0.02, 0.04)  # -2% to +4%
            current_price *= (1 + change)
            prices.append(int(current_price))
            
            # Update inventory
            inventory_change = random.randint(-5, 5)
            current_inventory = max(10, current_inventory + inventory_change)
            inventory.append(current_inventory)
            
            # Update Days on Market
            dom_change = random.randint(-5, 5)
            current_dom = max(15, current_dom + dom_change)
            dom_trend.append(current_dom)
        
        return {
            "dates": dates,
            "prices": prices,
            "market_stats": self._generate_market_stats(),
            "metrics": {
                "median_price": int(np.median(prices)),
                "price_per_sqft": int(current_price / 2000),
                "days_on_market": current_dom,
                "inventory": current_inventory,
                "price_trends": {
                    "1_month": round((prices[-1] - prices[-2]) / prices[-2] * 100, 1),
                    "3_month": round((prices[-1] - prices[-4]) / prices[-4] * 100, 1),
                    "6_month": round((prices[-1] - prices[0]) / prices[0] * 100, 1)
                }
            },
            "historical_data": {
                "inventory": inventory,
                "days_on_market": dom_trend
            },
            "forecast": self._generate_market_forecast(prices[-1])
        }
    
    def _generate_market_forecast(self, current_price: float) -> Dict:
        """Generate market forecast for next 12 months"""
        scenarios = {
            "conservative": {
                "price": int(current_price * 1.02),
                "confidence": 0.8
            },
            "moderate": {
                "price": int(current_price * 1.05),
                "confidence": 0.6
            },
            "aggressive": {
                "price": int(current_price * 1.08),
                "confidence": 0.4
            }
        }
        
        return {
            "scenarios": scenarios,
            "factors": [
                {"name": "Interest Rates", "impact": random.choice(['Positive', 'Negative', 'Neutral'])},
                {"name": "Local Economy", "impact": random.choice(['Positive', 'Negative', 'Neutral'])},
                {"name": "Housing Supply", "impact": random.choice(['Positive', 'Negative', 'Neutral'])},
                {"name": "Population Growth", "impact": random.choice(['Positive', 'Negative', 'Neutral'])}
            ]
        }
    
    def analyze_property(self, property_id: str) -> Dict:
        """Generate detailed analysis for a property"""
        # Determine scenario based on property ID
        scenario = 'distressed' if int(property_id) % 3 == 0 else 'normal'
        property_data = self.generate_property(property_id, scenario)
        purchase_price = property_data['price']
        
        # Generate ROI analysis
        rehab_data = self._estimate_rehab_cost(property_data['condition'], property_data['square_feet'])
        repair_cost = rehab_data['total']
        arv = purchase_price * random.uniform(1.2, 1.4)
        selling_costs = arv * 0.08
        holding_costs = purchase_price * random.uniform(0.01, 0.03)
        total_costs = purchase_price + repair_cost + selling_costs + holding_costs
        potential_profit = arv - total_costs
        roi_percentage = (potential_profit / total_costs) * 100
        
        # Generate comps
        comps = self._generate_comps(property_data)
        
        return {
            "property_details": property_data,
            "market_analysis": self.generate_market_trends(property_data['zip_code']),
            "roi_analysis": {
                "purchase_price": int(purchase_price),
                "repair_cost": int(repair_cost),
                "arv": int(arv),
                "selling_costs": int(selling_costs),
                "holding_costs": int(holding_costs),
                "total_costs": int(total_costs),
                "potential_profit": int(potential_profit),
                "roi_percentage": round(roi_percentage, 2),
                "rehab_details": rehab_data
            },
            "comps": comps,
            "risk_factors": self._generate_risk_factors(),
            "opportunity_score": round(random.uniform(60, 95), 1),
            "deal_analysis": {
                "recommended_strategies": self._recommend_strategy(scenario),
                "negotiation_range": {
                    "minimum": int(purchase_price * 0.9),
                    "target": int(purchase_price * 0.95),
                    "maximum": int(purchase_price)
                },
                "timeline": {
                    "acquisition": random.randint(30, 60),
                    "renovation": rehab_data['timeline']['estimated_weeks'] * 7,
                    "sale": random.randint(45, 90)
                }
            }
        }
