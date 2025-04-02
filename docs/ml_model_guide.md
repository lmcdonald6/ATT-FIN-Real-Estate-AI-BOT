# ML Model Development Guide

## Overview

This guide explains how to create custom ML models for the Real Estate AI System.

## Model Types

### 1. Property Valuation Models
- Price prediction
- Value analysis
- Risk assessment

### 2. Recommendation Models
- Similar properties
- Investment opportunities
- Market trends

### 3. Market Analysis Models
- Trend prediction
- Risk modeling
- Opportunity detection

## Implementation Guide

### 1. Basic Model Structure

```python
from src.core.plugin_system import ModelPlugin

class CustomModel(ModelPlugin):
    def __init__(self):
        self.model = None
        self.preprocessor = None
        
    def initialize(self, config: Dict) -> bool:
        # Load model and preprocessor
        pass
        
    def predict(self, data: Dict) -> Dict:
        # Make predictions
        pass
        
    def get_model_info(self) -> Dict:
        # Return model information
        pass
```

### 2. Feature Engineering

```python
def engineer_features(self, data: Dict) -> np.ndarray:
    features = []
    
    # Location features
    features.extend([
        data['latitude'],
        data['longitude'],
        data['distance_to_downtown']
    ])
    
    # Property features
    features.extend([
        data['square_feet'],
        data['bedrooms'],
        data['bathrooms'],
        data['year_built']
    ])
    
    # Market features
    features.extend([
        data['median_price'],
        data['price_trend'],
        data['days_on_market']
    ])
    
    return np.array(features)
```

### 3. Model Training

```python
def train_model(self, X: np.ndarray, y: np.ndarray):
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2
    )
    
    # Create model
    model = keras.Sequential([
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    # Train model
    model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32
    )
    
    return model
```

### 4. Model Evaluation

```python
def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
    predictions = self.model.predict(X_test)
    
    metrics = {
        'mse': mean_squared_error(y_test, predictions),
        'mae': mean_absolute_error(y_test, predictions),
        'r2': r2_score(y_test, predictions)
    }
    
    return metrics
```

### 5. Confidence Scoring

```python
def calculate_confidence(self, features: np.ndarray) -> float:
    # Distance from training data
    distances = cdist(features.reshape(1, -1), self.training_data)
    min_distance = np.min(distances)
    
    # Feature completeness
    completeness = np.sum(~np.isnan(features)) / len(features)
    
    # Prediction variance
    predictions = []
    for _ in range(10):
        pred = self.model(features, training=True)
        predictions.append(pred)
    variance = np.var(predictions)
    
    # Combine factors
    confidence = (
        0.4 * (1 - min_distance) +
        0.3 * completeness +
        0.3 * (1 - variance)
    )
    
    return min(0.95, confidence)
```

## Best Practices

### 1. Data Preprocessing

```python
def create_preprocessor(self):
    numeric_features = [
        'square_feet',
        'bedrooms',
        'bathrooms'
    ]
    
    categorical_features = [
        'property_type',
        'condition'
    ]
    
    # Create transformers
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant')),
        ('onehot', OneHotEncoder(drop='first'))
    ])
    
    # Combine transformers
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
        
    return preprocessor
```

### 2. Model Validation

```python
def validate_predictions(self, predictions: np.ndarray) -> bool:
    # Check for NaN values
    if np.any(np.isnan(predictions)):
        return False
        
    # Check value ranges
    if np.any(predictions < 0) or np.any(predictions > 1e7):
        return False
        
    # Check for outliers
    z_scores = np.abs(stats.zscore(predictions))
    if np.any(z_scores > 3):
        return False
        
    return True
```

### 3. Error Handling

```python
def safe_predict(self, data: Dict) -> Dict:
    try:
        # Validate input
        if not self._validate_input(data):
            raise ValueError("Invalid input data")
            
        # Preprocess data
        features = self.preprocessor.transform(data)
        
        # Make prediction
        prediction = self.model.predict(features)
        
        # Validate prediction
        if not self.validate_predictions(prediction):
            raise ValueError("Invalid prediction")
            
        # Calculate confidence
        confidence = self.calculate_confidence(features)
        
        return {
            'prediction': float(prediction[0]),
            'confidence': confidence
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            'error': str(e),
            'prediction': None,
            'confidence': 0
        }
```

## Model Configuration

### 1. Configuration Schema

```yaml
name: custom_model
version: "1.0.0"
description: "Custom ML model"
config_schema:
  type: object
  properties:
    model_type:
      type: string
      enum: ["basic", "advanced"]
    feature_engineering:
      type: object
      properties:
        use_market_features:
          type: boolean
        use_location_features:
          type: boolean
    training:
      type: object
      properties:
        batch_size:
          type: integer
        epochs:
          type: integer
```

### 2. Loading Configuration

```python
def load_config(self, config: Dict) -> bool:
    try:
        # Validate config
        jsonschema.validate(config, self.CONFIG_SCHEMA)
        
        # Set model parameters
        self.batch_size = config['training']['batch_size']
        self.epochs = config['training']['epochs']
        self.use_market = config['feature_engineering']['use_market_features']
        
        return True
        
    except Exception as e:
        logger.error(f"Config error: {str(e)}")
        return False
```

## Testing

### 1. Unit Tests

```python
def test_prediction():
    model = CustomModel()
    model.initialize(test_config)
    
    result = model.predict({
        'square_feet': 2000,
        'bedrooms': 3,
        'bathrooms': 2
    })
    
    assert 'prediction' in result
    assert 'confidence' in result
    assert result['prediction'] > 0
```

### 2. Integration Tests

```python
def test_model_pipeline():
    # Test data preprocessing
    data = load_test_data()
    features = model.preprocessor.transform(data)
    assert features.shape == expected_shape
    
    # Test prediction pipeline
    result = model.process(data)
    assert result['status'] == 'success'
    assert len(result['predictions']) == len(data)
```

## Performance Optimization

### 1. Batch Processing

```python
def batch_predict(self, data_list: List[Dict]) -> List[Dict]:
    # Create feature matrix
    features = np.vstack([
        self.engineer_features(data)
        for data in data_list
    ])
    
    # Make predictions in batch
    predictions = self.model.predict(features)
    
    # Calculate confidence scores
    confidences = [
        self.calculate_confidence(f)
        for f in features
    ]
    
    return [
        {
            'prediction': float(p),
            'confidence': float(c)
        }
        for p, c in zip(predictions, confidences)
    ]
```

### 2. Caching

```python
@lru_cache(maxsize=1000)
def get_cached_prediction(self, key: str) -> Dict:
    # Generate cache key
    cache_key = f"{key}:{self.model_version}"
    
    # Check cache
    if cache_key in self.prediction_cache:
        return self.prediction_cache[cache_key]
        
    # Make prediction
    result = self.predict(key)
    
    # Update cache
    self.prediction_cache[cache_key] = result
    
    return result
```

## Deployment

### 1. Model Versioning

```python
def save_model(self, version: str):
    # Save model artifacts
    model_path = f"models/custom_model_{version}"
    self.model.save(model_path)
    
    # Save preprocessor
    with open(f"{model_path}/preprocessor.pkl", 'wb') as f:
        pickle.dump(self.preprocessor, f)
        
    # Save metadata
    metadata = {
        'version': version,
        'features': self.feature_cols,
        'metrics': self.evaluate()
    }
    with open(f"{model_path}/metadata.json", 'w') as f:
        json.dump(metadata, f)
```

### 2. Model Loading

```python
def load_model(self, version: str):
    model_path = f"models/custom_model_{version}"
    
    # Load model
    self.model = keras.models.load_model(model_path)
    
    # Load preprocessor
    with open(f"{model_path}/preprocessor.pkl", 'rb') as f:
        self.preprocessor = pickle.load(f)
        
    # Load metadata
    with open(f"{model_path}/metadata.json", 'r') as f:
        self.metadata = json.load(f)
```

## Monitoring

### 1. Performance Metrics

```python
def log_metrics(self, prediction: Dict, actual: float):
    # Calculate error
    error = abs(prediction['prediction'] - actual)
    
    # Log metrics
    metrics = {
        'prediction_error': error,
        'confidence_score': prediction['confidence'],
        'processing_time': prediction['processing_time']
    }
    
    # Send to monitoring system
    self.metrics_client.log_metrics(metrics)
```

### 2. Error Tracking

```python
def log_error(self, error: Exception, context: Dict):
    # Log error details
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'stack_trace': traceback.format_exc(),
        'context': context
    }
    
    # Send to error tracking system
    self.error_tracker.capture_exception(error_data)
```
