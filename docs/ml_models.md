# Machine Learning Models Guide

## Overview

This guide covers the ML models used in the Real Estate AI Analysis Platform.

## Models Architecture

### 1. Property Valuation Model

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np

class PropertyValuationModel:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def preprocess_features(self, data):
        features = [
            'square_feet',
            'bedrooms',
            'bathrooms',
            'lot_size',
            'year_built',
            'days_on_market',
            'neighborhood_score',
            'school_score',
            'crime_rate',
            'median_income'
        ]
        return self.scaler.fit_transform(data[features])
```

### 2. Market Trend Predictor

```python
from sklearn.linear_model import LassoCV
from sklearn.decomposition import PCA

class MarketTrendPredictor:
    def __init__(self):
        self.model = LassoCV(
            cv=5,
            random_state=42,
            max_iter=1000
        )
        self.pca = PCA(n_components=0.95)
        
    def extract_trends(self, market_data):
        """Extract market trends using PCA."""
        transformed = self.pca.fit_transform(market_data)
        components = self.pca.components_
        return components, transformed
```

### 3. Investment Scorer

```python
class InvestmentScorer:
    def __init__(self):
        self.weights = {
            'roi_potential': 0.3,
            'risk_score': 0.2,
            'market_strength': 0.2,
            'neighborhood_growth': 0.15,
            'property_condition': 0.15
        }
        
    def calculate_score(self, metrics):
        return sum(
            metrics[key] * self.weights[key]
            for key in self.weights
        )
```

## Feature Engineering

### 1. Property Features

```python
def engineer_property_features(property_data):
    """Engineer features for property analysis."""
    features = {}
    
    # Basic features
    features['price_per_sqft'] = (
        property_data['price'] / property_data['square_feet']
    )
    
    # Age features
    features['property_age'] = (
        current_year - property_data['year_built']
    )
    
    # Location features
    features['distance_to_downtown'] = calculate_distance(
        property_data['coordinates'],
        DOWNTOWN_COORDINATES
    )
    
    # Market features
    features['price_to_rent_ratio'] = (
        property_data['price'] / 
        (property_data['estimated_rent'] * 12)
    )
    
    return features
```

### 2. Market Features

```python
def engineer_market_features(market_data):
    """Engineer features for market analysis."""
    features = {}
    
    # Trend features
    features['price_momentum'] = calculate_momentum(
        market_data['median_prices'],
        window=6  # 6 months
    )
    
    # Volatility features
    features['price_volatility'] = calculate_volatility(
        market_data['median_prices'],
        window=12  # 12 months
    )
    
    # Supply/demand features
    features['inventory_months'] = (
        market_data['active_listings'] /
        market_data['monthly_sales']
    )
    
    return features
```

## Model Training

### 1. Training Pipeline

```python
class ModelTrainingPipeline:
    def __init__(self):
        self.models = {
            'valuation': PropertyValuationModel(),
            'market': MarketTrendPredictor(),
            'investment': InvestmentScorer()
        }
        
    async def train_all(self, training_data):
        """Train all models in parallel."""
        tasks = [
            self.train_model(name, model, training_data)
            for name, model in self.models.items()
        ]
        await asyncio.gather(*tasks)
        
    async def train_model(self, name, model, data):
        """Train individual model."""
        try:
            X, y = self.prepare_data(name, data)
            model.fit(X, y)
            self.save_model(name, model)
            await self.log_metrics(name, model)
        except Exception as e:
            logger.error(f"Error training {name}: {str(e)}")
```

### 2. Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV

def tune_hyperparameters(model, X, y, param_grid):
    """Tune model hyperparameters."""
    grid_search = GridSearchCV(
        model,
        param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    grid_search.fit(X, y)
    return grid_search.best_params_
```

## Model Evaluation

### 1. Metrics Calculation

```python
def calculate_metrics(y_true, y_pred):
    """Calculate model performance metrics."""
    metrics = {
        'mse': mean_squared_error(y_true, y_pred),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
        'mape': mean_absolute_percentage_error(y_true, y_pred)
    }
    
    # Calculate custom metrics
    metrics['within_10_percent'] = np.mean(
        np.abs((y_true - y_pred) / y_true) <= 0.1
    )
    
    return metrics
```

### 2. Model Validation

```python
def validate_model(model, X_test, y_test):
    """Validate model performance."""
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = calculate_metrics(y_test, y_pred)
    
    # Check for degradation
    if metrics['r2'] < MIN_R2_SCORE:
        raise ModelPerformanceError(
            f"R2 score {metrics['r2']} below threshold"
        )
    
    return metrics
```

## Model Deployment

### 1. Model Versioning

```python
class ModelVersion:
    def __init__(self, model, version):
        self.model = model
        self.version = version
        self.created_at = datetime.utcnow()
        self.metrics = {}
        
    def save(self, path):
        """Save model version."""
        metadata = {
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'metrics': self.metrics
        }
        
        # Save model
        joblib.dump(self.model, f"{path}/model.joblib")
        
        # Save metadata
        with open(f"{path}/metadata.json", 'w') as f:
            json.dump(metadata, f)
```

### 2. Model Serving

```python
class ModelServer:
    def __init__(self):
        self.models = {}
        self.load_models()
        
    def load_models(self):
        """Load all model versions."""
        model_paths = glob.glob("models/*/")
        for path in model_paths:
            version = self.load_model_version(path)
            self.models[version.version] = version
            
    async def predict(self, data, version='latest'):
        """Make prediction using specified model version."""
        model = self.get_model(version)
        features = self.preprocess(data)
        prediction = model.predict(features)
        return self.postprocess(prediction)
```

## Model Monitoring

### 1. Performance Monitoring

```python
class ModelMonitor:
    def __init__(self):
        self.metrics_client = PrometheusClient()
        
    async def track_prediction(self, model_name, prediction, actual):
        """Track model prediction performance."""
        error = abs(prediction - actual)
        
        # Record metrics
        self.metrics_client.record_metric(
            f"{model_name}_absolute_error",
            error
        )
        
        # Check for drift
        await self.check_model_drift(model_name, error)
        
    async def check_model_drift(self, model_name, error):
        """Check for model drift."""
        recent_errors = await self.get_recent_errors(
            model_name,
            window_hours=24
        )
        
        if np.mean(recent_errors) > DRIFT_THRESHOLD:
            await self.trigger_retraining(model_name)
```

### 2. Error Analysis

```python
def analyze_errors(y_true, y_pred, features):
    """Analyze prediction errors."""
    errors = y_true - y_pred
    
    analysis = {
        'error_distribution': {
            'mean': np.mean(errors),
            'std': np.std(errors),
            'percentiles': np.percentile(
                errors,
                [25, 50, 75]
            )
        },
        'feature_correlations': {
            feature: np.corrcoef(features[feature], errors)[0, 1]
            for feature in features.columns
        }
    }
    
    return analysis
```

## Best Practices

1. **Feature Engineering**
   - Normalize numerical features
   - Handle missing values appropriately
   - Create interaction features
   - Use domain knowledge

2. **Model Training**
   - Use cross-validation
   - Monitor for overfitting
   - Implement early stopping
   - Save model checkpoints

3. **Evaluation**
   - Use multiple metrics
   - Compare against baselines
   - Test on holdout sets
   - Analyze error patterns

4. **Deployment**
   - Version control models
   - Implement A/B testing
   - Monitor performance
   - Have rollback plans

5. **Maintenance**
   - Retrain periodically
   - Update features
   - Track data drift
   - Document changes
