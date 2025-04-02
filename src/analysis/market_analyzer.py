"""
Market analysis module for real estate properties.
Provides advanced analytics and market insights.
"""
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyzes real estate market data and provides insights"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.svd = TruncatedSVD(n_components=5)
        
    def analyze_property(self, property_data: Dict, comps: List[Dict]) -> Dict:
        """
        Analyze a property in the context of its market comps
        
        Args:
            property_data: Property data dictionary
            comps: List of comparable properties
            
        Returns:
            Dictionary containing market analysis results
        """
        try:
            if not property_data.get('price'):
                raise ValueError("Property price is required for analysis")
                
            # Handle no comps case
            if not comps:
                logger.warning("No comparable properties available for analysis")
                return {
                    'market_position': {
                        'price_percentiles': {},
                        'market_segment': self._determine_market_segment(property_data['price']),
                        'competition_level': 'Low',
                        'price_volatility': 'Unknown'
                    },
                    'price_trends': {
                        'appreciation_rate': 0.0,
                        'price_momentum': 'unknown',
                        'seasonality': 'insufficient_data'
                    },
                    'investment_metrics': self._calculate_investment_metrics(
                        property_data,
                        property_data['price'],  # Use property's own price as market average
                        0.0  # No appreciation rate without comps
                    ),
                    'recommendations': self._generate_recommendations(
                        property_data,
                        {'market_segment': self._determine_market_segment(property_data['price']),
                         'competition_level': 'Low',
                         'price_volatility': 'Unknown'},
                        {'price_to_market_ratio': 1.0,
                         'monthly_cashflow': 0.0,
                         'annual_roi': 0.0}
                    ),
                    'timestamp': datetime.now().isoformat()
                }
                
            # Extract key metrics
            metrics = self._extract_metrics(property_data, comps)
            
            # Calculate market position
            market_position = self._calculate_market_position(metrics)
            
            # Analyze price trends
            price_trends = self._analyze_price_trends(comps)
            
            # Calculate investment metrics
            investment_metrics = self._calculate_investment_metrics(
                property_data,
                metrics['market_avg_price'],
                price_trends['appreciation_rate']
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                property_data,
                market_position,
                investment_metrics
            )
            
            return {
                'market_position': market_position,
                'price_trends': price_trends,
                'investment_metrics': investment_metrics,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing property: {str(e)}")
            raise
            
    def _extract_metrics(self, property_data: Dict, comps: List[Dict]) -> Dict:
        """Extract and calculate key market metrics"""
        if not comps:
            return {
                'market_avg_price': property_data['price'],
                'market_median_price': property_data['price'],
                'price_std': 0,
                'avg_price_per_sqft': property_data['price'] / property_data['square_feet'],
                'median_price_per_sqft': property_data['price'] / property_data['square_feet'],
                'num_comps': 0,
                'price_range': {
                    'min': property_data['price'],
                    'max': property_data['price']
                }
            }
            
        comp_prices = [comp['price'] for comp in comps]
        comp_sqft = [comp['square_feet'] for comp in comps]
        comp_price_per_sqft = [p/s for p, s in zip(comp_prices, comp_sqft)]
        
        return {
            'market_avg_price': np.mean(comp_prices),
            'market_median_price': np.median(comp_prices),
            'price_std': np.std(comp_prices),
            'avg_price_per_sqft': np.mean(comp_price_per_sqft),
            'median_price_per_sqft': np.median(comp_price_per_sqft),
            'num_comps': len(comps),
            'price_range': {
                'min': min(comp_prices),
                'max': max(comp_prices)
            }
        }
        
    def _calculate_market_position(self, metrics: Dict) -> Dict:
        """Calculate property's position in the market"""
        percentiles = [10, 25, 50, 75, 90]
        price_percentiles = {
            f'percentile_{p}': np.percentile([metrics['market_avg_price']], p)
            for p in percentiles
        }
        
        return {
            'price_percentiles': price_percentiles,
            'market_segment': self._determine_market_segment(metrics['market_avg_price']),
            'competition_level': self._assess_competition_level(metrics['num_comps']),
            'price_volatility': self._calculate_price_volatility(metrics['price_std'])
        }
        
    def _analyze_price_trends(self, comps: List[Dict]) -> Dict:
        """Analyze historical price trends"""
        if not comps:
            return {
                'appreciation_rate': 0.0,
                'price_momentum': 'unknown',
                'seasonality': 'insufficient_data'
            }
            
        # Extract historical prices and dates
        historical_data = []
        for comp in comps:
            if 'price_history' in comp:
                for entry in comp['price_history']:
                    historical_data.append({
                        'date': pd.to_datetime(entry['date']),
                        'price': entry['price']
                    })
                    
        if not historical_data:
            return {
                'appreciation_rate': 0.0,
                'price_momentum': 'stable',
                'seasonality': 'unknown'
            }
            
        # Create time series
        df = pd.DataFrame(historical_data)
        df = df.sort_values('date')
        
        # Calculate metrics
        total_days = (df['date'].max() - df['date'].min()).days
        if total_days > 0:
            price_change = (df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0]
            annual_appreciation = (price_change / total_days) * 365
        else:
            annual_appreciation = 0.0
            
        return {
            'appreciation_rate': annual_appreciation,
            'price_momentum': self._calculate_price_momentum(df),
            'seasonality': self._analyze_seasonality(df)
        }
        
    def _calculate_investment_metrics(
        self,
        property_data: Dict,
        market_avg_price: float,
        appreciation_rate: float
    ) -> Dict:
        """Calculate investment-related metrics"""
        price = float(property_data.get('price', 0))
        if price == 0:
            raise ValueError("Property price is required for investment analysis")
            
        sqft = float(property_data.get('square_feet', 0))
        if sqft == 0:
            sqft = price / 200  # Rough estimate based on $200/sqft
            
        estimated_rent = self._estimate_monthly_rent(sqft, market_avg_price)
        
        # Calculate metrics
        price_to_market_ratio = price / market_avg_price if market_avg_price > 0 else 1.0
        gross_rent_multiplier = price / (estimated_rent * 12) if estimated_rent > 0 else 0
        
        # Estimate costs
        annual_taxes = float(property_data.get('tax_info', {}).get('tax_amount', price * 0.015))
        annual_insurance = price * 0.005  # Estimated at 0.5% of property value
        annual_maintenance = sqft * 2  # $2 per sqft per year
        
        # Calculate cash flow
        monthly_mortgage = self._calculate_mortgage_payment(price * 0.8, 0.06, 30)
        monthly_expenses = (annual_taxes + annual_insurance + annual_maintenance) / 12
        monthly_cashflow = estimated_rent - monthly_mortgage - monthly_expenses
        
        # Calculate ROI
        down_payment = price * 0.2
        monthly_equity_buildup = self._calculate_equity_buildup(price * 0.8, 0.06, 30)
        annual_appreciation_value = price * appreciation_rate
        
        total_annual_return = (monthly_cashflow * 12) + (monthly_equity_buildup * 12) + annual_appreciation_value
        roi = (total_annual_return / down_payment) * 100 if down_payment > 0 else 0
        
        return {
            'price_to_market_ratio': price_to_market_ratio,
            'estimated_monthly_rent': estimated_rent,
            'gross_rent_multiplier': gross_rent_multiplier,
            'monthly_cashflow': monthly_cashflow,
            'annual_roi': roi,
            'cap_rate': ((estimated_rent * 12) - (monthly_expenses * 12)) / price * 100,
            'cost_analysis': {
                'monthly_mortgage': monthly_mortgage,
                'monthly_taxes': annual_taxes / 12,
                'monthly_insurance': annual_insurance / 12,
                'monthly_maintenance': annual_maintenance / 12
            }
        }
        
    def _generate_recommendations(
        self,
        property_data: Dict,
        market_position: Dict,
        investment_metrics: Dict
    ) -> List[Dict]:
        """Generate investment recommendations"""
        recommendations = []
        
        # Analyze deal type potential
        if investment_metrics['monthly_cashflow'] > 0:
            recommendations.append({
                'type': 'Buy and Hold',
                'confidence': min(0.9, 0.5 + (investment_metrics['annual_roi'] / 100)),
                'reason': 'Positive cash flow with good ROI potential'
            })
            
        if investment_metrics['price_to_market_ratio'] < 0.9:
            recommendations.append({
                'type': 'Fix and Flip',
                'confidence': min(0.9, 0.7 + (0.9 - investment_metrics['price_to_market_ratio'])),
                'reason': 'Property is priced below market value'
            })
            
        if investment_metrics['price_to_market_ratio'] < 0.85:
            recommendations.append({
                'type': 'Wholesale',
                'confidence': min(0.9, 0.6 + (0.85 - investment_metrics['price_to_market_ratio'])),
                'reason': 'Significant equity potential'
            })
            
        # If no recommendations were generated, add a conservative one
        if not recommendations:
            recommendations.append({
                'type': 'Further Analysis Required',
                'confidence': 0.5,
                'reason': 'Insufficient market data for strong recommendations'
            })
            
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations
        
    def _determine_market_segment(self, price: float) -> str:
        """Determine the market segment based on price"""
        if price < 200000:
            return 'Entry Level'
        elif price < 500000:
            return 'Mid Market'
        elif price < 1000000:
            return 'High End'
        else:
            return 'Luxury'
            
    def _assess_competition_level(self, num_comps: int) -> str:
        """Assess market competition level"""
        if num_comps < 5:
            return 'Low'
        elif num_comps < 15:
            return 'Moderate'
        else:
            return 'High'
            
    def _calculate_price_volatility(self, price_std: float) -> str:
        """Calculate price volatility level"""
        if price_std == 0:
            return 'Unknown'
        elif price_std < 10000:
            return 'Low'
        elif price_std < 50000:
            return 'Moderate'
        else:
            return 'High'
            
    def _calculate_price_momentum(self, df: pd.DataFrame) -> str:
        """Calculate price momentum"""
        if len(df) < 2:
            return 'stable'
            
        recent_prices = df.sort_values('date').tail(3)
        price_changes = recent_prices['price'].pct_change()
        avg_change = price_changes.mean()
        
        if avg_change > 0.05:
            return 'strong_up'
        elif avg_change > 0.02:
            return 'up'
        elif avg_change < -0.05:
            return 'strong_down'
        elif avg_change < -0.02:
            return 'down'
        else:
            return 'stable'
            
    def _analyze_seasonality(self, df: pd.DataFrame) -> str:
        """Analyze price seasonality"""
        if len(df) < 12:
            return 'insufficient_data'
            
        df['month'] = df['date'].dt.month
        monthly_avg = df.groupby('month')['price'].mean()
        
        if len(monthly_avg) < 12:
            return 'insufficient_data'
            
        max_month = monthly_avg.idxmax()
        min_month = monthly_avg.idxmin()
        
        if max_month in [6, 7, 8]:
            return 'summer_peak'
        elif max_month in [3, 4, 5]:
            return 'spring_peak'
        elif min_month in [12, 1, 2]:
            return 'winter_low'
        else:
            return 'no_clear_pattern'
            
    def _estimate_monthly_rent(self, sqft: float, market_price: float) -> float:
        """Estimate monthly rent based on property characteristics"""
        # Simple estimation using the 1% rule as a baseline
        baseline = market_price * 0.01
        
        # Adjust based on square footage
        sqft_factor = min(max(sqft / 1500, 0.8), 1.2)
        
        return baseline * sqft_factor
        
    def _calculate_mortgage_payment(self, principal: float, rate: float, years: int) -> float:
        """Calculate monthly mortgage payment"""
        monthly_rate = rate / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return principal / num_payments
            
        return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
    def _calculate_equity_buildup(self, principal: float, rate: float, years: int) -> float:
        """Calculate monthly equity buildup"""
        monthly_rate = rate / 12
        num_payments = years * 12
        monthly_payment = self._calculate_mortgage_payment(principal, rate, years)
        
        # First month's principal payment
        if monthly_rate == 0:
            return monthly_payment
            
        interest_payment = principal * monthly_rate
        return monthly_payment - interest_payment
