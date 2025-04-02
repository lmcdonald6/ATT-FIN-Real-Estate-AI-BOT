"""Neighborhood scoring system for real estate market analysis."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Optional

class NeighborhoodScorer:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scaler = MinMaxScaler()
        
    def score_neighborhood(self, 
                         data: pd.DataFrame,
                         weights: Optional[Dict[str, float]] = None) -> Dict:
        """Calculate comprehensive neighborhood score."""
        weights = weights or {
            'market_metrics': 0.3,
            'location_metrics': 0.3,
            'demographic_metrics': 0.2,
            'investment_metrics': 0.2
        }
        
        scores = {}
        
        # Calculate individual metric scores
        scores.update(self._calculate_market_metrics(data))
        scores.update(self._calculate_location_metrics(data))
        scores.update(self._calculate_demographic_metrics(data))
        scores.update(self._calculate_investment_metrics(data))
        
        # Calculate weighted total score
        total_score = 0
        for category, weight in weights.items():
            category_scores = [v for k, v in scores.items() if k.startswith(category.split('_')[0])]
            if category_scores:
                total_score += np.mean(category_scores) * weight
        
        scores['total_score'] = min(max(total_score * 100, 0), 100)
        return scores
    
    def _calculate_market_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate market-related metrics."""
        recent_data = data[data['period'] >= data['period'].max() - pd.DateOffset(months=6)]
        
        metrics = {
            'market_price_trend': self._calculate_trend(recent_data['price']),
            'market_inventory': self._normalize_metric(len(recent_data)),
            'market_days_on_market': self._normalize_metric(recent_data['days_on_market'].mean(), inverse=True),
            'market_price_stability': self._normalize_metric(1 / recent_data['price'].std())
        }
        
        return metrics
    
    def _calculate_location_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate location-based metrics."""
        metrics = {
            'location_schools': self._normalize_metric(data['school_rating'].mean()),
            'location_crime_safety': self._normalize_metric(data['safety_score'].mean()),
            'location_amenities': self._normalize_metric(data['amenities_score'].mean()),
            'location_transportation': self._normalize_metric(data['transit_score'].mean())
        }
        
        return metrics
    
    def _calculate_demographic_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate demographic metrics."""
        metrics = {
            'demographic_income': self._normalize_metric(data['median_income'].mean()),
            'demographic_education': self._normalize_metric(data['education_score'].mean()),
            'demographic_population_growth': self._normalize_metric(data['population_growth'].mean()),
            'demographic_employment': self._normalize_metric(data['employment_rate'].mean())
        }
        
        return metrics
    
    def _calculate_investment_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate investment potential metrics."""
        metrics = {
            'investment_roi': self._normalize_metric(self._calculate_roi(data)),
            'investment_appreciation': self._normalize_metric(self._calculate_appreciation(data)),
            'investment_rental_demand': self._normalize_metric(data['rental_demand'].mean()),
            'investment_development': self._normalize_metric(data['development_score'].mean())
        }
        
        return metrics
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate trend coefficient using linear regression."""
        x = np.arange(len(series))
        coeffs = np.polyfit(x, series, deg=1)
        return self._normalize_metric(coeffs[0])
    
    def _calculate_roi(self, data: pd.DataFrame) -> float:
        """Calculate return on investment potential."""
        recent_data = data[data['period'] >= data['period'].max() - pd.DateOffset(months=12)]
        
        # Calculate potential rental income
        monthly_rent = recent_data['rental_price'].mean()
        purchase_price = recent_data['price'].mean()
        
        # Estimate annual expenses (property tax, maintenance, etc.)
        annual_expenses = purchase_price * 0.02
        
        # Calculate annual ROI
        annual_income = (monthly_rent * 12) - annual_expenses
        roi = (annual_income / purchase_price) * 100
        
        return roi
    
    def _calculate_appreciation(self, data: pd.DataFrame) -> float:
        """Calculate historical price appreciation."""
        yearly_prices = data.groupby(data['period'].dt.year)['price'].mean()
        if len(yearly_prices) < 2:
            return 0
            
        total_appreciation = (yearly_prices.iloc[-1] / yearly_prices.iloc[0]) - 1
        years = len(yearly_prices) - 1
        
        # Calculate annualized appreciation
        annual_appreciation = ((1 + total_appreciation) ** (1/years) - 1) * 100
        return annual_appreciation
    
    def _normalize_metric(self, value: float, inverse: bool = False) -> float:
        """Normalize metric to 0-1 scale."""
        if np.isnan(value):
            return 0
            
        if inverse:
            value = 1 / (1 + value)
            
        # Clip to reasonable ranges and normalize to 0-1
        return min(max(value, 0), 1)
    
    def get_neighborhood_insights(self, scores: Dict[str, float]) -> List[str]:
        """Generate insights based on neighborhood scores."""
        insights = []
        
        # Market insights
        market_scores = {k: v for k, v in scores.items() if k.startswith('market_')}
        if market_scores['market_price_trend'] > 0.7:
            insights.append("Strong price appreciation trend indicates a growing market")
        elif market_scores['market_price_trend'] < 0.3:
            insights.append("Declining price trend suggests potential investment opportunities")
            
        # Location insights
        location_scores = {k: v for k, v in scores.items() if k.startswith('location_')}
        if np.mean(list(location_scores.values())) > 0.7:
            insights.append("Excellent location with strong amenities and accessibility")
        
        # Investment insights
        investment_scores = {k: v for k, v in scores.items() if k.startswith('investment_')}
        if investment_scores['investment_roi'] > 0.7:
            insights.append("High ROI potential with strong rental demand")
        
        # Overall insight
        if scores['total_score'] > 80:
            insights.append("Premium neighborhood with excellent investment potential")
        elif scores['total_score'] > 60:
            insights.append("Good neighborhood with solid investment fundamentals")
        else:
            insights.append("Emerging neighborhood with potential for appreciation")
            
        return insights
