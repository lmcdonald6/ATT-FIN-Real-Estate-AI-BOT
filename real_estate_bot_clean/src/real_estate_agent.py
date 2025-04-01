"""
Real Estate AI Agent
Handles property analysis, lead scoring, and decision making.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

class RealEstateAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Query patterns for intent recognition
        self.query_patterns = {
            'value_analysis': [
                'value', 'worth', 'price', 'estimate', 'appraisal',
                'how much', 'market value', 'arv'
            ],
            'property_details': [
                'details', 'information', 'specs', 'features',
                'tell me about', 'what is', 'condition'
            ],
            'owner_info': [
                'owner', 'who owns', 'seller', 'contact',
                'owned by', 'ownership'
            ],
            'occupancy': [
                'vacant', 'occupied', 'live in', 'tenant',
                'occupancy', 'living in'
            ],
            'distressed': [
                'distressed', 'foreclosure', 'tax lien', 'motivated',
                'behind payments', 'delinquent', 'problems'
            ],
            'market': [
                'market', 'trends', 'appreciation', 'comps',
                'comparable', 'analysis'
            ],
            'investment': [
                'investment', 'roi', 'return', 'profit',
                'cash flow', 'rental', 'flip'
            ]
        }

    def analyze_query_type(self, query: str) -> str:
        """Determine the type of property query."""
        query = query.lower()
        
        # Check each pattern type
        for query_type, patterns in self.query_patterns.items():
            if any(pattern in query for pattern in patterns):
                return query_type
                
        return 'comprehensive'

    def calculate_lead_score(self, property_data: Dict) -> Dict:
        """Calculate comprehensive lead score based on multiple factors."""
        scores = {
            'financial_distress': self._calculate_financial_distress(property_data),
            'time_pressure': self._calculate_time_pressure(property_data),
            'property_condition': self._calculate_property_condition(property_data),
            'market_position': self._calculate_market_position(property_data)
        }
        
        # Calculate weighted average
        weights = {
            'financial_distress': 0.35,
            'time_pressure': 0.25,
            'property_condition': 0.20,
            'market_position': 0.20
        }
        
        overall_score = sum(score * weights[factor] 
                          for factor, score in scores.items())
        
        # Determine lead category
        if overall_score >= 80:
            category = 'Hot'
            priority = 1
        elif overall_score >= 60:
            category = 'Warm'
            priority = 2
        else:
            category = 'Cold'
            priority = 3
            
        return {
            'overall_score': round(overall_score),
            'category': category,
            'priority': priority,
            'component_scores': scores
        }

    def _calculate_financial_distress(self, data: Dict) -> float:
        """Calculate financial distress score."""
        score = 0
        indicators = data.get('distress_indicators', [])
        
        # Tax status
        if 'tax_delinquent' in indicators:
            score += 30
            
        # Mortgage status
        if 'mortgage_default' in indicators:
            score += 30
            
        # Equity position
        equity = data.get('owner_info', {}).get('estimated_equity', 0)
        if equity > 50:
            score += 20
        elif equity > 30:
            score += 10
            
        # Length of ownership
        time_owned = data.get('owner_info', {}).get('time_owned', 0)
        if time_owned > 10:
            score += 20
            
        return min(score, 100)

    def _calculate_time_pressure(self, data: Dict) -> float:
        """Calculate time pressure score."""
        score = 0
        indicators = data.get('distress_indicators', [])
        
        # Foreclosure status
        if 'pre_foreclosure' in indicators:
            score += 40
            
        # Vacancy
        if 'vacant' in indicators:
            score += 20
            
        # Market time
        days_on_market = data.get('days_on_market', 0)
        if days_on_market > 180:
            score += 20
        elif days_on_market > 90:
            score += 10
            
        # Price reductions
        price_drops = data.get('price_drops', 0)
        score += min(price_drops * 5, 20)
            
        return min(score, 100)

    def _calculate_property_condition(self, data: Dict) -> float:
        """Calculate property condition score."""
        score = 100
        details = data.get('property_details', {})
        
        # Major repairs
        major_repairs = len(details.get('repairs_needed', {}).get('major', []))
        score -= major_repairs * 15
        
        # Moderate repairs
        moderate_repairs = len(details.get('repairs_needed', {}).get('moderate', []))
        score -= moderate_repairs * 10
        
        # Minor repairs
        minor_repairs = len(details.get('repairs_needed', {}).get('minor', []))
        score -= minor_repairs * 5
        
        # Age of property
        age = datetime.now().year - details.get('year_built', datetime.now().year)
        if age > 50:
            score -= 20
        elif age > 30:
            score -= 10
            
        return max(score, 0)

    def _calculate_market_position(self, data: Dict) -> float:
        """Calculate market position score."""
        score = 50
        metrics = data.get('financial_metrics', {})
        
        # Price to ARV ratio
        current_price = data.get('price', 0)
        arv = metrics.get('arv', current_price)
        if current_price and arv:
            ratio = current_price / arv
            if ratio < 0.7:
                score += 30
            elif ratio < 0.8:
                score += 20
            elif ratio < 0.9:
                score += 10
                
        # Market trends
        market_data = data.get('market_data', {})
        appreciation = market_data.get('appreciation_rate', 0)
        if appreciation > 10:
            score += 20
        elif appreciation > 5:
            score += 10
            
        return min(score, 100)

    def recommend_next_action(self, lead_score: Dict) -> Dict:
        """Recommend next actions based on lead score."""
        score = lead_score['overall_score']
        category = lead_score['category']
        
        if category == 'Hot':
            return {
                'next_action': 'Direct Mail + Phone Call',
                'follow_up_date': (datetime.now().date() + 
                                 timedelta(days=1)).isoformat(),
                'priority': 1
            }
        elif category == 'Warm':
            return {
                'next_action': 'Direct Mail',
                'follow_up_date': (datetime.now().date() + 
                                 timedelta(days=7)).isoformat(),
                'priority': 2
            }
        else:
            return {
                'next_action': 'Add to Monthly Mailer',
                'follow_up_date': (datetime.now().date() + 
                                 timedelta(days=30)).isoformat(),
                'priority': 3
            }
