"""Market opportunity detection system using advanced analytics and ML."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple

class OpportunityDetector:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
    def find_opportunities(self,
                         market_data: pd.DataFrame,
                         property_data: pd.DataFrame,
                         min_confidence: float = 0.7) -> List[Dict]:
        """Find potential investment opportunities in the market."""
        # Prepare market indicators
        market_indicators = self._calculate_market_indicators(market_data)
        
        # Find undervalued properties
        undervalued = self._detect_undervalued_properties(property_data, market_data)
        
        # Identify emerging areas
        emerging_areas = self._identify_emerging_areas(market_data)
        
        # Find properties in emerging areas
        opportunities = self._match_opportunities(
            undervalued,
            emerging_areas,
            market_indicators,
            min_confidence
        )
        
        return opportunities
    
    def _calculate_market_indicators(self, market_data: pd.DataFrame) -> Dict:
        """Calculate key market indicators."""
        recent_data = market_data[
            market_data['period'] >= market_data['period'].max() - pd.DateOffset(months=6)
        ]
        
        indicators = {
            'price_momentum': self._calculate_momentum(recent_data, 'price'),
            'volume_momentum': self._calculate_momentum(recent_data, 'volume'),
            'inventory_change': self._calculate_inventory_change(recent_data),
            'price_volatility': self._calculate_volatility(recent_data, 'price'),
            'market_efficiency': self._calculate_market_efficiency(recent_data)
        }
        
        return indicators
    
    def _detect_undervalued_properties(self,
                                     property_data: pd.DataFrame,
                                     market_data: pd.DataFrame) -> pd.DataFrame:
        """Detect potentially undervalued properties using anomaly detection."""
        # Prepare features for anomaly detection
        features = self._prepare_property_features(property_data, market_data)
        
        # Fit and predict anomalies
        self.anomaly_detector.fit(features)
        anomaly_scores = self.anomaly_detector.score_samples(features)
        
        # Filter properties with low prices relative to their features
        property_data['anomaly_score'] = anomaly_scores
        undervalued = property_data[anomaly_scores < np.percentile(anomaly_scores, 20)].copy()
        
        # Calculate potential value
        undervalued['potential_value'] = self._estimate_potential_value(
            undervalued,
            market_data
        )
        
        return undervalued
    
    def _identify_emerging_areas(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Identify areas showing signs of emergence or gentrification."""
        areas = pd.DataFrame()
        
        for zip_code in market_data['zip_code'].unique():
            area_data = market_data[market_data['zip_code'] == zip_code]
            
            # Calculate area metrics
            metrics = {
                'zip_code': zip_code,
                'price_growth': self._calculate_price_growth(area_data),
                'sales_velocity': self._calculate_sales_velocity(area_data),
                'renovation_activity': self._calculate_renovation_activity(area_data),
                'demographic_score': self._calculate_demographic_score(area_data)
            }
            
            areas = pd.concat([areas, pd.DataFrame([metrics])], ignore_index=True)
            
        # Calculate emergence score
        weights = {
            'price_growth': 0.3,
            'sales_velocity': 0.25,
            'renovation_activity': 0.25,
            'demographic_score': 0.2
        }
        
        for metric, weight in weights.items():
            areas[metric] = self._normalize_series(areas[metric])
            areas[f'{metric}_weighted'] = areas[metric] * weight
            
        areas['emergence_score'] = areas[[f'{m}_weighted' for m in weights.keys()]].sum(axis=1)
        
        return areas.sort_values('emergence_score', ascending=False)
    
    def _match_opportunities(self,
                           undervalued: pd.DataFrame,
                           emerging_areas: pd.DataFrame,
                           market_indicators: Dict,
                           min_confidence: float) -> List[Dict]:
        """Match undervalued properties with emerging areas."""
        opportunities = []
        
        for _, property_data in undervalued.iterrows():
            area_data = emerging_areas[
                emerging_areas['zip_code'] == property_data['zip_code']
            ].iloc[0]
            
            # Calculate opportunity score
            opportunity_score = self._calculate_opportunity_score(
                property_data,
                area_data,
                market_indicators
            )
            
            if opportunity_score >= min_confidence:
                opportunities.append({
                    'property_id': property_data['property_id'],
                    'address': property_data['address'],
                    'price': property_data['price'],
                    'potential_value': property_data['potential_value'],
                    'upside_percentage': (
                        (property_data['potential_value'] - property_data['price'])
                        / property_data['price'] * 100
                    ),
                    'opportunity_score': opportunity_score,
                    'area_emergence_score': area_data['emergence_score'],
                    'key_factors': self._identify_key_factors(
                        property_data,
                        area_data,
                        market_indicators
                    )
                })
                
        return sorted(
            opportunities,
            key=lambda x: x['opportunity_score'],
            reverse=True
        )
    
    def _prepare_property_features(self,
                                 property_data: pd.DataFrame,
                                 market_data: pd.DataFrame) -> np.ndarray:
        """Prepare property features for anomaly detection."""
        features = pd.DataFrame()
        
        # Basic property features
        for feature in ['sqft', 'beds', 'baths', 'lot_size', 'age']:
            if feature in property_data.columns:
                features[feature] = property_data[feature]
                
        # Price per square foot
        features['price_per_sqft'] = property_data['price'] / property_data['sqft']
        
        # Location value indicators
        zip_metrics = market_data.groupby('zip_code').agg({
            'price': 'median',
            'days_on_market': 'mean'
        })
        
        features['area_price_ratio'] = property_data.apply(
            lambda x: x['price'] / zip_metrics.loc[x['zip_code'], 'price'],
            axis=1
        )
        
        return self.scaler.fit_transform(features)
    
    def _calculate_momentum(self,
                          data: pd.DataFrame,
                          column: str,
                          periods: int = 3) -> float:
        """Calculate price momentum using exponential moving averages."""
        values = data.groupby('period')[column].mean()
        if len(values) < periods:
            return 0
            
        ema_short = values.ewm(span=periods).mean()
        ema_long = values.ewm(span=periods*2).mean()
        
        return (ema_short.iloc[-1] / ema_long.iloc[-1] - 1) * 100
    
    def _calculate_inventory_change(self, data: pd.DataFrame) -> float:
        """Calculate change in inventory levels."""
        monthly_inventory = data[data['status'] == 'active'].groupby('period').size()
        if len(monthly_inventory) < 2:
            return 0
            
        return (monthly_inventory.iloc[-1] / monthly_inventory.iloc[0] - 1) * 100
    
    def _calculate_volatility(self,
                            data: pd.DataFrame,
                            column: str) -> float:
        """Calculate price volatility."""
        values = data.groupby('period')[column].mean()
        return values.std() / values.mean() * 100
    
    def _calculate_market_efficiency(self, data: pd.DataFrame) -> float:
        """Calculate market efficiency ratio."""
        sold_price = data[data['status'] == 'sold']['price'].median()
        list_price = data[data['status'] == 'active']['price'].median()
        
        if not list_price:
            return 0
            
        return sold_price / list_price
    
    def _calculate_price_growth(self, data: pd.DataFrame) -> float:
        """Calculate price growth rate."""
        yearly_prices = data.groupby(
            data['period'].dt.year
        )['price'].median()
        
        if len(yearly_prices) < 2:
            return 0
            
        return (yearly_prices.iloc[-1] / yearly_prices.iloc[0] - 1) * 100
    
    def _calculate_sales_velocity(self, data: pd.DataFrame) -> float:
        """Calculate sales velocity trend."""
        monthly_sales = data[data['status'] == 'sold'].groupby('period').size()
        if len(monthly_sales) < 2:
            return 0
            
        return (monthly_sales.iloc[-1] / monthly_sales.iloc[0] - 1) * 100
    
    def _calculate_renovation_activity(self, data: pd.DataFrame) -> float:
        """Calculate renovation activity level."""
        if 'renovation_year' not in data.columns:
            return 0
            
        recent_renovations = data[
            data['renovation_year'] >= data['period'].max().year - 2
        ]
        
        return len(recent_renovations) / len(data) * 100
    
    def _calculate_demographic_score(self, data: pd.DataFrame) -> float:
        """Calculate demographic improvement score."""
        metrics = []
        
        if 'median_income' in data.columns:
            income_growth = (
                data.groupby('period')['median_income'].mean().pct_change()
            ).mean()
            metrics.append(income_growth)
            
        if 'education_level' in data.columns:
            education_growth = (
                data.groupby('period')['education_level'].mean().pct_change()
            ).mean()
            metrics.append(education_growth)
            
        return np.mean(metrics) if metrics else 0
    
    def _estimate_potential_value(self,
                                properties: pd.DataFrame,
                                market_data: pd.DataFrame) -> pd.Series:
        """Estimate potential value of properties."""
        # Calculate median price per sqft for each zip code
        zip_metrics = market_data.groupby('zip_code').agg({
            'price': lambda x: np.percentile(x, 75),
            'sqft': 'median'
        })
        zip_metrics['price_per_sqft'] = zip_metrics['price'] / zip_metrics['sqft']
        
        # Estimate potential value
        potential_values = properties.apply(
            lambda x: x['sqft'] * zip_metrics.loc[x['zip_code'], 'price_per_sqft'],
            axis=1
        )
        
        return potential_values
    
    def _calculate_opportunity_score(self,
                                  property_data: pd.Series,
                                  area_data: pd.Series,
                                  market_indicators: Dict) -> float:
        """Calculate overall opportunity score."""
        scores = []
        
        # Property value score
        value_gap = (property_data['potential_value'] - property_data['price']) / property_data['price']
        scores.append(min(value_gap * 2, 1))  # Cap at 1
        
        # Area emergence score
        scores.append(area_data['emergence_score'])
        
        # Market momentum score
        momentum_score = (
            market_indicators['price_momentum'] / 100 +
            market_indicators['volume_momentum'] / 100
        ) / 2
        scores.append(max(min(momentum_score, 1), 0))
        
        return np.mean(scores) * 100
    
    def _identify_key_factors(self,
                            property_data: pd.Series,
                            area_data: pd.Series,
                            market_indicators: Dict) -> List[str]:
        """Identify key factors contributing to the opportunity."""
        factors = []
        
        # Value factors
        value_gap = (property_data['potential_value'] - property_data['price']) / property_data['price']
        if value_gap > 0.2:
            factors.append(f"Potentially undervalued by {value_gap:.1%}")
            
        # Area factors
        if area_data['emergence_score'] > 0.7:
            factors.append("Located in rapidly emerging area")
        if area_data['price_growth'] > 0.1:
            factors.append(f"Strong price appreciation ({area_data['price_growth']:.1f}%)")
            
        # Market factors
        if market_indicators['price_momentum'] > 5:
            factors.append("Positive market momentum")
        if market_indicators['inventory_change'] < -10:
            factors.append("Decreasing inventory levels")
            
        return factors
    
    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """Normalize series to 0-1 range."""
        if len(series) == 0:
            return series
            
        return (series - series.min()) / (series.max() - series.min() + 1e-10)
