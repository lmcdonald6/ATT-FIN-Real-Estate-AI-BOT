"""Investment opportunity ranking system."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple

class InvestmentRanker:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scaler = StandardScaler()
        
    def rank_opportunities(self,
                         properties: pd.DataFrame,
                         market_data: pd.DataFrame,
                         criteria: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """Rank investment opportunities based on multiple criteria."""
        criteria = criteria or {
            'roi_potential': 0.3,
            'risk_level': 0.2,
            'market_strength': 0.2,
            'property_condition': 0.15,
            'location_score': 0.15
        }
        
        # Calculate scores for each criterion
        scores = pd.DataFrame(index=properties.index)
        
        scores['roi_score'] = self._calculate_roi_scores(properties, market_data)
        scores['risk_score'] = self._calculate_risk_scores(properties, market_data)
        scores['market_score'] = self._calculate_market_scores(properties, market_data)
        scores['condition_score'] = self._calculate_condition_scores(properties)
        scores['location_score'] = self._calculate_location_scores(properties, market_data)
        
        # Calculate weighted total score
        for criterion, weight in criteria.items():
            criterion_name = f"{criterion.split('_')[0]}_score"
            scores[criterion_name] = scores[criterion_name] * weight
            
        scores['total_score'] = scores.sum(axis=1)
        
        # Rank properties
        scores['rank'] = scores['total_score'].rank(ascending=False)
        
        # Add property details
        result = pd.concat([
            properties[['address', 'price', 'sqft', 'beds', 'baths']],
            scores[['total_score', 'rank']],
            scores.drop(['total_score', 'rank'], axis=1)
        ], axis=1)
        
        return result.sort_values('rank')
    
    def _calculate_roi_scores(self,
                            properties: pd.DataFrame,
                            market_data: pd.DataFrame) -> pd.Series:
        """Calculate ROI potential scores."""
        # Calculate potential monthly rent
        rent_estimates = self._estimate_rental_prices(properties, market_data)
        
        # Calculate annual ROI
        annual_income = rent_estimates * 12
        expenses = properties['price'] * 0.02  # Estimated annual expenses
        roi = (annual_income - expenses) / properties['price'] * 100
        
        return self._normalize_series(roi)
    
    def _calculate_risk_scores(self,
                             properties: pd.DataFrame,
                             market_data: pd.DataFrame) -> pd.Series:
        """Calculate risk level scores."""
        risk_factors = pd.Series(index=properties.index, dtype=float)
        
        # Market volatility risk
        price_volatility = market_data.groupby('zip_code')['price'].std() / market_data.groupby('zip_code')['price'].mean()
        risk_factors += price_volatility[properties['zip_code']].values
        
        # Property condition risk
        risk_factors += (properties['age'] / 100)  # Age risk
        risk_factors += (1 - properties['condition_score'])  # Condition risk
        
        # Market liquidity risk
        days_on_market = market_data.groupby('zip_code')['days_on_market'].mean()
        risk_factors += days_on_market[properties['zip_code']].values / 365
        
        return 1 - self._normalize_series(risk_factors)  # Invert so higher is better
    
    def _calculate_market_scores(self,
                               properties: pd.DataFrame,
                               market_data: pd.DataFrame) -> pd.Series:
        """Calculate market strength scores."""
        market_scores = pd.Series(index=properties.index, dtype=float)
        
        # Price trends
        price_trends = self._calculate_price_trends(market_data)
        market_scores += price_trends[properties['zip_code']].values
        
        # Supply-demand metrics
        inventory_levels = market_data.groupby('zip_code').size()
        absorption_rates = self._calculate_absorption_rates(market_data)
        
        market_scores += absorption_rates[properties['zip_code']].values
        market_scores -= self._normalize_series(inventory_levels[properties['zip_code']].values)
        
        return self._normalize_series(market_scores)
    
    def _calculate_condition_scores(self, properties: pd.DataFrame) -> pd.Series:
        """Calculate property condition scores."""
        condition_scores = pd.Series(index=properties.index, dtype=float)
        
        # Base condition score
        condition_scores += properties['condition_score']
        
        # Age factor
        age_factor = 1 - (properties['age'] / properties['age'].max())
        condition_scores += age_factor
        
        # Recent renovations
        if 'renovation_year' in properties.columns:
            renovation_age = 2024 - properties['renovation_year']
            renovation_factor = 1 - (renovation_age / renovation_age.max())
            condition_scores += renovation_factor
            
        return self._normalize_series(condition_scores)
    
    def _calculate_location_scores(self,
                                 properties: pd.DataFrame,
                                 market_data: pd.DataFrame) -> pd.Series:
        """Calculate location quality scores."""
        location_scores = pd.Series(index=properties.index, dtype=float)
        
        # School ratings
        if 'school_rating' in properties.columns:
            location_scores += properties['school_rating'] / 10
            
        # Crime rates (inverse)
        if 'crime_rate' in properties.columns:
            location_scores += 1 - (properties['crime_rate'] / properties['crime_rate'].max())
            
        # Amenities score
        if 'amenities_score' in properties.columns:
            location_scores += properties['amenities_score']
            
        # Median income of area
        median_income = market_data.groupby('zip_code')['median_income'].mean()
        location_scores += self._normalize_series(median_income[properties['zip_code']].values)
        
        return self._normalize_series(location_scores)
    
    def _estimate_rental_prices(self,
                              properties: pd.DataFrame,
                              market_data: pd.DataFrame) -> pd.Series:
        """Estimate potential rental prices."""
        # Calculate average rent per sqft by zip code
        rent_per_sqft = market_data.groupby('zip_code')['rental_price'].mean() / \
                       market_data.groupby('zip_code')['sqft'].mean()
                       
        # Estimate rent based on property size and location
        estimated_rent = properties['sqft'] * rent_per_sqft[properties['zip_code']].values
        
        # Adjust for property features
        if 'condition_score' in properties.columns:
            estimated_rent *= (1 + (properties['condition_score'] - 0.5) * 0.2)
            
        return estimated_rent
    
    def _calculate_price_trends(self, market_data: pd.DataFrame) -> pd.Series:
        """Calculate price trends by zip code."""
        trends = pd.Series(dtype=float)
        
        for zip_code in market_data['zip_code'].unique():
            zip_data = market_data[market_data['zip_code'] == zip_code]
            prices = zip_data.groupby('period')['price'].mean()
            
            if len(prices) > 1:
                x = np.arange(len(prices))
                slope = np.polyfit(x, prices, deg=1)[0]
                trends[zip_code] = slope / prices.mean()  # Normalize by average price
            else:
                trends[zip_code] = 0
                
        return self._normalize_series(trends)
    
    def _calculate_absorption_rates(self, market_data: pd.DataFrame) -> pd.Series:
        """Calculate absorption rates by zip code."""
        absorption_rates = pd.Series(dtype=float)
        
        for zip_code in market_data['zip_code'].unique():
            zip_data = market_data[market_data['zip_code'] == zip_code]
            
            monthly_sales = zip_data[zip_data['status'] == 'sold'].groupby('period').size()
            active_listings = zip_data[zip_data['status'] == 'active'].groupby('period').size()
            
            if len(active_listings) > 0:
                absorption_rates[zip_code] = monthly_sales.mean() / active_listings.iloc[-1]
            else:
                absorption_rates[zip_code] = 0
                
        return self._normalize_series(absorption_rates)
    
    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """Normalize series to 0-1 range."""
        if len(series) == 0:
            return series
            
        return (series - series.min()) / (series.max() - series.min() + 1e-10)
    
    def get_investment_insights(self, ranked_properties: pd.DataFrame) -> List[Dict]:
        """Generate insights for top-ranked investment opportunities."""
        insights = []
        
        for _, property_data in ranked_properties.head().iterrows():
            property_insights = {
                'address': property_data['address'],
                'rank': int(property_data['rank']),
                'total_score': round(property_data['total_score'], 2),
                'strengths': [],
                'considerations': []
            }
            
            # Analyze scores
            if property_data['roi_score'] > 0.7:
                property_insights['strengths'].append("High ROI potential")
            elif property_data['roi_score'] < 0.3:
                property_insights['considerations'].append("Limited ROI potential")
                
            if property_data['risk_score'] > 0.7:
                property_insights['strengths'].append("Low risk investment")
            elif property_data['risk_score'] < 0.3:
                property_insights['considerations'].append("Higher risk profile")
                
            if property_data['market_score'] > 0.7:
                property_insights['strengths'].append("Strong market conditions")
            elif property_data['market_score'] < 0.3:
                property_insights['considerations'].append("Challenging market conditions")
                
            insights.append(property_insights)
            
        return insights
