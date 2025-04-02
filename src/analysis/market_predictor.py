"""Market prediction module using advanced time series analysis."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing

class MarketPredictor:
    def __init__(self, config=None):
        self.config = config or {}
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for market prediction."""
        features = pd.DataFrame()
        
        # Price trends
        features['price_mean'] = data.groupby('period')['price'].mean()
        features['price_median'] = data.groupby('period')['price'].median()
        features['price_std'] = data.groupby('period')['price'].std()
        
        # Market activity
        features['listings_count'] = data.groupby('period').size()
        features['days_on_market'] = data.groupby('period')['days_on_market'].mean()
        
        # Price per square foot trends
        features['price_per_sqft'] = data.groupby('period')['price_per_sqft'].mean()
        
        # Create lagged features
        for lag in [1, 3, 6, 12]:  # 1, 3, 6, 12 months
            features[f'price_mean_lag_{lag}'] = features['price_mean'].shift(lag)
            features[f'listings_count_lag_{lag}'] = features['listings_count'].shift(lag)
        
        return features.dropna()
    
    def fit(self, data: pd.DataFrame) -> None:
        """Train the market prediction model."""
        features = self.prepare_features(data)
        target = features['price_mean'].shift(-1)  # Predict next month's prices
        
        # Remove last row since we don't have the target for it
        features = features[:-1]
        target = target[:-1]
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(scaled_features, target)
        
    def predict(self, data: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
        """Predict market trends for specified number of periods."""
        features = self.prepare_features(data)
        scaled_features = self.scaler.transform(features)
        
        predictions = []
        current_features = scaled_features[-1:]
        
        for _ in range(periods):
            # Predict next period
            next_price = self.model.predict(current_features)[0]
            predictions.append(next_price)
            
            # Update features for next prediction
            new_features = current_features.copy()
            new_features[0, features.columns.get_loc('price_mean')] = next_price
            current_features = new_features
        
        return pd.DataFrame({
            'period': pd.date_range(start=data['period'].max(), periods=periods+1, freq='M')[1:],
            'predicted_price': predictions
        })
    
    def analyze_seasonality(self, data: pd.DataFrame) -> dict:
        """Analyze seasonal patterns in the market."""
        # Fit Holt-Winters model
        model = ExponentialSmoothing(
            data.groupby('period')['price'].mean(),
            seasonal_periods=12,  # Monthly seasonality
            trend='add',
            seasonal='add'
        ).fit()
        
        return {
            'seasonal_factors': model.seasonal_,
            'peak_month': model.seasonal_.argmax() + 1,
            'trough_month': model.seasonal_.argmin() + 1
        }
    
    def calculate_market_strength(self, data: pd.DataFrame) -> dict:
        """Calculate market strength indicators."""
        recent_data = data[data['period'] >= data['period'].max() - pd.DateOffset(months=3)]
        
        metrics = {
            'median_price': recent_data['price'].median(),
            'price_trend': self._calculate_trend(recent_data['price']),
            'avg_days_on_market': recent_data['days_on_market'].mean(),
            'inventory_level': len(recent_data),
            'absorption_rate': self._calculate_absorption_rate(recent_data),
            'price_per_sqft': recent_data['price'].sum() / recent_data['sqft'].sum()
        }
        
        # Calculate market score (0-100)
        metrics['market_score'] = self._calculate_market_score(metrics)
        
        return metrics
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate the trend coefficient using linear regression."""
        x = np.arange(len(series))
        coeffs = np.polyfit(x, series, deg=1)
        return coeffs[0]
    
    def _calculate_absorption_rate(self, data: pd.DataFrame) -> float:
        """Calculate the market absorption rate."""
        monthly_sales = data[data['status'] == 'sold'].groupby('period').size()
        active_listings = data[data['status'] == 'active'].groupby('period').size()
        
        if len(active_listings) == 0:
            return 0
            
        return monthly_sales.mean() / active_listings.iloc[-1]
    
    def _calculate_market_score(self, metrics: dict) -> float:
        """Calculate overall market score (0-100)."""
        weights = {
            'price_trend': 0.3,
            'absorption_rate': 0.3,
            'avg_days_on_market': -0.2,  # Negative weight as lower is better
            'inventory_level': 0.2
        }
        
        # Normalize each metric to 0-1 scale
        normalized = {}
        for metric, weight in weights.items():
            value = metrics[metric]
            if metric == 'avg_days_on_market':
                # Invert days on market so lower is better
                value = 1 / (1 + value)
            normalized[metric] = value
        
        # Calculate weighted score
        score = sum(normalized[metric] * weight for metric, weight in weights.items())
        
        # Convert to 0-100 scale
        return min(max(score * 100, 0), 100)
