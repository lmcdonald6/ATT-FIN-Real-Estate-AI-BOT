import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

@dataclass
class MarketInsight:
    trend: str
    confidence: float
    impact: str
    action_items: List[str]

@dataclass
class OpportunityScore:
    score: float
    factors: Dict[str, float]
    recommendations: List[str]

class SmartInsightsEngine:
    def __init__(self):
        self.market_patterns = {}
        self.opportunity_weights = {
            'price_to_market': 0.3,
            'location_growth': 0.2,
            'property_condition': 0.15,
            'rental_demand': 0.15,
            'renovation_potential': 0.1,
            'market_timing': 0.1
        }
        
    def analyze_market_patterns(self, historical_data: pd.DataFrame) -> List[MarketInsight]:
        """Analyze market patterns and identify trends"""
        insights = []
        
        # Price trend analysis
        price_trends = self._analyze_price_trends(historical_data)
        if price_trends:
            insights.append(price_trends)
        
        # Seasonal patterns
        seasonal = self._analyze_seasonal_patterns(historical_data)
        if seasonal:
            insights.append(seasonal)
        
        # Market velocity
        velocity = self._analyze_market_velocity(historical_data)
        if velocity:
            insights.append(velocity)
        
        return insights
    
    def calculate_opportunity_score(self, property_data: Dict, market_data: Dict) -> OpportunityScore:
        """Calculate comprehensive opportunity score"""
        scores = {}
        
        # Price to market ratio
        market_price = market_data.get('median_price', 0)
        if market_price > 0:
            price_ratio = property_data.get('price', 0) / market_price
            scores['price_to_market'] = self._normalize_score(1 - price_ratio)
        
        # Location growth potential
        growth_rate = market_data.get('annual_growth_rate', 0)
        scores['location_growth'] = self._normalize_score(growth_rate)
        
        # Property condition and renovation potential
        condition_score = self._evaluate_condition(property_data.get('condition', ''))
        scores['property_condition'] = condition_score
        
        # Rental demand
        rental_score = self._evaluate_rental_potential(property_data, market_data)
        scores['rental_demand'] = rental_score
        
        # Calculate weighted score
        final_score = sum(scores[k] * self.opportunity_weights[k] for k in scores)
        
        return OpportunityScore(
            score=final_score,
            factors=scores,
            recommendations=self._generate_recommendations(scores)
        )
    
    def identify_market_clusters(self, properties: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify market clusters and opportunities"""
        if not properties:
            return {}
            
        # Extract features for clustering
        features = []
        for prop in properties:
            features.append([
                prop.get('price', 0),
                prop.get('square_feet', 0),
                prop.get('year_built', 2000),
                prop.get('last_sold', {}).get('price', 0)
            ])
            
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Group properties by cluster
        clustered_properties = {
            'undervalued': [],
            'fair_value': [],
            'premium': []
        }
        
        for idx, cluster in enumerate(clusters):
            property_with_cluster = properties[idx].copy()
            property_with_cluster['cluster_type'] = list(clustered_properties.keys())[cluster]
            clustered_properties[list(clustered_properties.keys())[cluster]].append(property_with_cluster)
            
        return clustered_properties
    
    def generate_investment_strategy(self, property_data: Dict, market_data: Dict, investor_profile: Dict) -> Dict:
        """Generate personalized investment strategy"""
        strategy = {
            'recommended_approach': [],
            'risk_factors': [],
            'timeline': {},
            'financial_projections': {}
        }
        
        # Analyze property potential
        potential = self._analyze_property_potential(property_data, market_data)
        
        # Match with investor profile
        strategy['recommended_approach'] = self._match_investor_strategy(potential, investor_profile)
        
        # Risk assessment
        strategy['risk_factors'] = self._assess_risks(property_data, market_data)
        
        # Timeline projection
        strategy['timeline'] = self._project_timeline(strategy['recommended_approach'])
        
        # Financial projections
        strategy['financial_projections'] = self._project_financials(
            property_data,
            market_data,
            strategy['recommended_approach']
        )
        
        return strategy
    
    def _analyze_price_trends(self, data: pd.DataFrame) -> Optional[MarketInsight]:
        """Analyze price trends in the market"""
        if data.empty:
            return None
            
        try:
            # Calculate price trend
            price_changes = data['price'].pct_change()
            trend_strength = abs(price_changes.mean())
            trend_direction = 'upward' if price_changes.mean() > 0 else 'downward'
            
            return MarketInsight(
                trend=f"{trend_direction} price trend",
                confidence=min(trend_strength * 100, 95),
                impact='high' if trend_strength > 0.05 else 'medium',
                action_items=[
                    f"Consider {'buying' if trend_direction == 'upward' else 'selling'} soon",
                    "Monitor price changes weekly",
                    "Review comparable properties"
                ]
            )
        except:
            return None
    
    def _analyze_seasonal_patterns(self, data: pd.DataFrame) -> Optional[MarketInsight]:
        """Analyze seasonal patterns in the market"""
        if data.empty:
            return None
            
        try:
            # Group by month and calculate average prices
            data['month'] = pd.to_datetime(data['date']).dt.month
            monthly_avg = data.groupby('month')['price'].mean()
            
            # Find peak and trough months
            peak_month = monthly_avg.idxmax()
            trough_month = monthly_avg.idxmin()
            
            return MarketInsight(
                trend=f"Seasonal pattern identified",
                confidence=85.0,
                impact='medium',
                action_items=[
                    f"Best time to sell: Month {peak_month}",
                    f"Best time to buy: Month {trough_month}",
                    "Plan renovations during off-peak seasons"
                ]
            )
        except:
            return None
    
    def _analyze_market_velocity(self, data: pd.DataFrame) -> Optional[MarketInsight]:
        """Analyze market velocity (days on market)"""
        if data.empty:
            return None
            
        try:
            avg_dom = data['days_on_market'].mean()
            dom_trend = 'fast' if avg_dom < 30 else 'moderate' if avg_dom < 60 else 'slow'
            
            return MarketInsight(
                trend=f"{dom_trend} market velocity",
                confidence=90.0,
                impact='high' if dom_trend == 'fast' else 'medium',
                action_items=[
                    "Prepare for quick decisions" if dom_trend == 'fast' else "Take time to analyze deals",
                    "Have financing ready" if dom_trend == 'fast' else "Negotiate more aggressively",
                    "Monitor competition closely"
                ]
            )
        except:
            return None
    
    def _normalize_score(self, value: float) -> float:
        """Normalize score to 0-1 range"""
        return max(0, min(1, value))
    
    def _evaluate_condition(self, condition: str) -> float:
        """Evaluate property condition"""
        condition_scores = {
            'excellent': 1.0,
            'good': 0.8,
            'fair': 0.6,
            'poor': 0.4,
            'very poor': 0.2
        }
        return condition_scores.get(condition.lower(), 0.5)
    
    def _evaluate_rental_potential(self, property_data: Dict, market_data: Dict) -> float:
        """Evaluate rental potential"""
        try:
            # Calculate potential monthly rent
            sqft = property_data.get('square_feet', 0)
            beds = property_data.get('beds', 0)
            market_rent = market_data.get('avg_rent_per_sqft', 0) * sqft
            
            # Calculate potential ROI
            price = property_data.get('price', 0)
            if price > 0:
                annual_roi = (market_rent * 12) / price
                return self._normalize_score(annual_roi * 10)  # Normalize to 0-1
            return 0.5
        except:
            return 0.5
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if scores.get('price_to_market', 0) > 0.7:
            recommendations.append("Consider making an offer soon - property appears undervalued")
            
        if scores.get('location_growth', 0) > 0.7:
            recommendations.append("Strong growth potential in this location")
            
        if scores.get('rental_demand', 0) > 0.7:
            recommendations.append("Good candidate for rental investment")
            
        if scores.get('property_condition', 0) < 0.4:
            recommendations.append("Major renovation may be required - factor this into your offer")
            
        return recommendations
    
    def _analyze_property_potential(self, property_data: Dict, market_data: Dict) -> Dict:
        """Analyze property potential"""
        return {
            'flip_potential': self._calculate_flip_potential(property_data, market_data),
            'rental_potential': self._calculate_rental_potential(property_data, market_data),
            'development_potential': self._calculate_development_potential(property_data, market_data)
        }
    
    def _match_investor_strategy(self, potential: Dict, investor_profile: Dict) -> List[Dict]:
        """Match property potential with investor profile"""
        strategies = []
        
        risk_tolerance = investor_profile.get('risk_tolerance', 'medium')
        investment_horizon = investor_profile.get('investment_horizon', 'medium')
        
        # Add strategies based on potential and investor profile
        if potential['flip_potential'] > 0.7 and risk_tolerance in ['high', 'medium']:
            strategies.append({
                'type': 'Fix and Flip',
                'confidence': potential['flip_potential'] * 100,
                'timeline': '6-12 months'
            })
            
        if potential['rental_potential'] > 0.7 and investment_horizon in ['long', 'medium']:
            strategies.append({
                'type': 'Buy and Hold',
                'confidence': potential['rental_potential'] * 100,
                'timeline': '5+ years'
            })
            
        if potential['development_potential'] > 0.8 and risk_tolerance == 'high':
            strategies.append({
                'type': 'Development',
                'confidence': potential['development_potential'] * 100,
                'timeline': '1-2 years'
            })
            
        return sorted(strategies, key=lambda x: x['confidence'], reverse=True)
    
    def _calculate_flip_potential(self, property_data: Dict, market_data: Dict) -> float:
        """Calculate flip potential"""
        try:
            # Factors affecting flip potential
            price_ratio = property_data.get('price', 0) / market_data.get('median_price', 1)
            condition_score = self._evaluate_condition(property_data.get('condition', ''))
            market_growth = market_data.get('annual_growth_rate', 0)
            
            # Weight the factors
            weighted_score = (
                (1 - price_ratio) * 0.4 +
                (1 - condition_score) * 0.3 +
                market_growth * 0.3
            )
            
            return self._normalize_score(weighted_score)
        except:
            return 0.5
    
    def _calculate_rental_potential(self, property_data: Dict, market_data: Dict) -> float:
        """Calculate rental potential"""
        try:
            # Calculate potential monthly rent
            sqft = property_data.get('square_feet', 0)
            market_rent = market_data.get('avg_rent_per_sqft', 0) * sqft
            
            # Calculate potential ROI
            price = property_data.get('price', 0)
            if price > 0:
                annual_roi = (market_rent * 12) / price
                return self._normalize_score(annual_roi * 10)
            return 0.5
        except:
            return 0.5
    
    def _calculate_development_potential(self, property_data: Dict, market_data: Dict) -> float:
        """Calculate development potential"""
        try:
            # Factors affecting development potential
            lot_size = property_data.get('lot_size', 0)
            zoning = property_data.get('zoning', '')
            location_score = market_data.get('location_score', 0.5)
            
            # Weight the factors
            weighted_score = (
                (lot_size / 10000) * 0.4 +  # Normalize lot size
                (1 if zoning in ['R2', 'R3', 'C1'] else 0.5) * 0.3 +
                location_score * 0.3
            )
            
            return self._normalize_score(weighted_score)
        except:
            return 0.5
    
    def _assess_risks(self, property_data: Dict, market_data: Dict) -> List[Dict]:
        """Assess investment risks"""
        risks = []
        
        # Price risk
        if property_data.get('price', 0) > market_data.get('median_price', 0) * 1.1:
            risks.append({
                'type': 'Price',
                'level': 'High',
                'description': 'Property may be overpriced for the market'
            })
            
        # Market risk
        if market_data.get('market_stability', 0.5) < 0.4:
            risks.append({
                'type': 'Market',
                'level': 'Medium',
                'description': 'Market shows signs of instability'
            })
            
        # Property risk
        age = datetime.now().year - property_data.get('year_built', datetime.now().year)
        if age > 30:
            risks.append({
                'type': 'Property',
                'level': 'Medium',
                'description': 'Older property may require significant maintenance'
            })
            
        return risks
    
    def _project_timeline(self, strategies: List[Dict]) -> Dict:
        """Project investment timeline"""
        timeline = {}
        
        for strategy in strategies:
            if strategy['type'] == 'Fix and Flip':
                timeline['acquisition'] = '1-2 months'
                timeline['renovation'] = '3-4 months'
                timeline['sale'] = '1-2 months'
            elif strategy['type'] == 'Buy and Hold':
                timeline['acquisition'] = '1-2 months'
                timeline['stabilization'] = '2-3 months'
                timeline['cash flow'] = 'Ongoing'
            elif strategy['type'] == 'Development':
                timeline['acquisition'] = '2-3 months'
                timeline['planning'] = '3-4 months'
                timeline['construction'] = '8-12 months'
                timeline['sale'] = '2-3 months'
                
        return timeline
    
    def _project_financials(self, property_data: Dict, market_data: Dict, strategies: List[Dict]) -> Dict:
        """Project financial outcomes"""
        financials = {}
        
        for strategy in strategies:
            if strategy['type'] == 'Fix and Flip':
                financials['flip'] = self._project_flip_financials(property_data, market_data)
            elif strategy['type'] == 'Buy and Hold':
                financials['rental'] = self._project_rental_financials(property_data, market_data)
            elif strategy['type'] == 'Development':
                financials['development'] = self._project_development_financials(property_data, market_data)
                
        return financials
    
    def _project_flip_financials(self, property_data: Dict, market_data: Dict) -> Dict:
        """Project flip financials"""
        purchase_price = property_data.get('price', 0)
        sqft = property_data.get('square_feet', 0)
        condition = property_data.get('condition', 'fair')
        
        # Estimate renovation costs
        renovation_cost = self._estimate_renovation_cost(sqft, condition)
        
        # Estimate ARV
        arv = self._estimate_arv(purchase_price, renovation_cost, condition)
        
        # Calculate holding costs
        holding_costs = purchase_price * 0.02  # Estimate 2% for 6 months
        
        return {
            'purchase_price': purchase_price,
            'renovation_cost': renovation_cost,
            'holding_costs': holding_costs,
            'estimated_arv': arv,
            'potential_profit': arv - (purchase_price + renovation_cost + holding_costs),
            'roi': ((arv - (purchase_price + renovation_cost + holding_costs)) / 
                   (purchase_price + renovation_cost + holding_costs)) * 100
        }
    
    def _project_rental_financials(self, property_data: Dict, market_data: Dict) -> Dict:
        """Project rental financials"""
        purchase_price = property_data.get('price', 0)
        sqft = property_data.get('square_feet', 0)
        
        # Estimate monthly rent
        monthly_rent = sqft * market_data.get('avg_rent_per_sqft', 0)
        
        # Estimate expenses
        annual_expenses = {
            'property_tax': purchase_price * 0.015,
            'insurance': purchase_price * 0.005,
            'maintenance': monthly_rent * 0.1 * 12,
            'vacancy': monthly_rent * 0.08 * 12,
            'management': monthly_rent * 0.1 * 12
        }
        
        total_expenses = sum(annual_expenses.values())
        annual_noi = (monthly_rent * 12) - total_expenses
        
        return {
            'monthly_rent': monthly_rent,
            'annual_gross_income': monthly_rent * 12,
            'annual_expenses': annual_expenses,
            'annual_noi': annual_noi,
            'cap_rate': (annual_noi / purchase_price) * 100,
            'cash_on_cash_return': ((annual_noi - (purchase_price * 0.05)) / (purchase_price * 0.2)) * 100
        }
    
    def _project_development_financials(self, property_data: Dict, market_data: Dict) -> Dict:
        """Project development financials"""
        land_value = property_data.get('price', 0)
        lot_size = property_data.get('lot_size', 0)
        
        # Estimate construction costs
        construction_cost_per_sqft = 150  # Example value
        buildable_sqft = lot_size * 0.5  # Assume 50% lot coverage
        total_construction_cost = buildable_sqft * construction_cost_per_sqft
        
        # Estimate completed value
        price_per_sqft = market_data.get('avg_price_per_sqft', 0)
        completed_value = buildable_sqft * price_per_sqft
        
        # Calculate other costs
        soft_costs = total_construction_cost * 0.2  # 20% of construction costs
        financing_costs = (land_value + total_construction_cost) * 0.06  # 6% interest for 1 year
        
        total_costs = land_value + total_construction_cost + soft_costs + financing_costs
        
        return {
            'land_value': land_value,
            'construction_cost': total_construction_cost,
            'soft_costs': soft_costs,
            'financing_costs': financing_costs,
            'total_costs': total_costs,
            'completed_value': completed_value,
            'potential_profit': completed_value - total_costs,
            'roi': ((completed_value - total_costs) / total_costs) * 100
        }
    
    def _estimate_renovation_cost(self, sqft: float, condition: str) -> float:
        """Estimate renovation costs based on property condition"""
        base_cost_per_sqft = {
            'excellent': 10,
            'good': 20,
            'fair': 40,
            'poor': 60,
            'very poor': 80
        }
        
        base_cost = sqft * base_cost_per_sqft.get(condition.lower(), 40)
        return base_cost
    
    def _estimate_arv(self, purchase_price: float, renovation_cost: float, condition: str) -> float:
        """Estimate After Repair Value"""
        condition_multiplier = {
            'excellent': 1.1,
            'good': 1.2,
            'fair': 1.3,
            'poor': 1.4,
            'very poor': 1.5
        }
        
        multiplier = condition_multiplier.get(condition.lower(), 1.3)
        return (purchase_price + renovation_cost) * multiplier
