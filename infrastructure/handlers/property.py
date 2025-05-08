import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import redis
import boto3
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Initialize clients
redis_client = redis.Redis(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT']),
    decode_responses=True
)

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cache_table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

class PropertyValuator:
    def __init__(self):
        self.cache_ttl = int(os.environ.get('CACHE_TTL', 3600))
        self.light_model = None
        self.heavy_model = None
        self.scaler = None
        
    async def valuate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cost-efficient property valuation handler
        """
        try:
            # Parse request
            body = json.loads(event['body'])
            property_data = body.get('property')
            
            if not property_data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Property data is required'})
                }
                
            # Try cache first
            cache_key = self._generate_cache_key(property_data)
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return {
                    'statusCode': 200,
                    'body': json.dumps(cached_result)
                }
                
            # Perform valuation
            result = await self._valuate_property(property_data)
            
            # Cache result
            await self._cache_result(cache_key, result)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
            
    def _generate_cache_key(self, property_data: Dict[str, Any]) -> str:
        """
        Generate cache key based on property attributes
        """
        key_parts = [
            property_data.get('address', ''),
            property_data.get('zipcode', ''),
            property_data.get('last_sale_date', ''),
            str(property_data.get('sqft', 0))
        ]
        return f"property:{'|'.join(key_parts)}"
        
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Multi-layer caching strategy
        """
        # Try Redis first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
            
        # Try DynamoDB next
        try:
            response = cache_table.get_item(
                Key={'id': cache_key}
            )
            if 'Item' in response:
                item = response['Item']
                if item['expires'] > datetime.now().timestamp():
                    # Set in Redis for next time
                    redis_client.set(
                        cache_key,
                        json.dumps(item['data']),
                        ex=self.cache_ttl
                    )
                    return item['data']
        except Exception:
            pass
            
        return None
        
    async def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        Multi-layer caching implementation
        """
        expires = int((datetime.now() + timedelta(seconds=self.cache_ttl)).timestamp())
        
        # Cache in Redis
        redis_client.set(
            cache_key,
            json.dumps(result),
            ex=self.cache_ttl
        )
        
        # Cache in DynamoDB
        cache_table.put_item(
            Item={
                'id': cache_key,
                'data': result,
                'expires': expires
            }
        )
        
    async def _valuate_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Smart property valuation with cost optimization
        """
        # Get basic property metrics
        basic_metrics = await self._calculate_basic_metrics(property_data)
        
        # Determine if we need detailed analysis
        if self._needs_detailed_analysis(basic_metrics):
            # Load heavy model if needed
            detailed_analysis = await self._run_detailed_analysis(property_data)
            basic_metrics.update(detailed_analysis)
        
        return basic_metrics
        
    async def _calculate_basic_metrics(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate basic property metrics (cheaper operation)
        """
        # Load light model if not loaded
        if not self.light_model:
            self.light_model = await self._load_light_model()
            
        features = self._extract_basic_features(property_data)
        prediction = self.light_model.predict([features])[0]
        
        return {
            'estimated_value': float(prediction),
            'confidence': 0.85,
            'last_updated': datetime.now().isoformat(),
            'basic_metrics': {
                'price_per_sqft': prediction / property_data.get('sqft', 1),
                'market_days_estimate': 30,
                'value_trend': 'stable'
            }
        }
        
    def _needs_detailed_analysis(self, basic_metrics: Dict[str, Any]) -> bool:
        """
        Determine if property needs expensive detailed analysis
        """
        # Check if property value is high enough to warrant detailed analysis
        if basic_metrics['estimated_value'] > 1000000:
            return True
            
        # Check if property is in a volatile market
        if basic_metrics['basic_metrics']['market_days_estimate'] < 15:
            return True
            
        return False
        
    async def _run_detailed_analysis(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run detailed property analysis (more expensive operation)
        """
        # Load heavy model if needed
        if not self.heavy_model:
            self.heavy_model = await self._load_heavy_model()
            
        features = self._extract_detailed_features(property_data)
        prediction = self.heavy_model.predict([features])[0]
        
        return {
            'detailed_analysis': {
                'refined_value': float(prediction),
                'confidence': 0.95,
                'value_factors': [
                    {
                        'factor': 'location_score',
                        'impact': 0.4,
                        'description': 'Prime location with good schools'
                    },
                    {
                        'factor': 'market_momentum',
                        'impact': 0.3,
                        'description': 'Strong market growth'
                    }
                ],
                'comparable_properties': await self._find_comparables(property_data)
            }
        }
        
    async def _load_light_model(self) -> RandomForestRegressor:
        """
        Load lightweight model for basic predictions
        """
        model = RandomForestRegressor(
            n_estimators=50,  # Fewer trees for faster prediction
            max_depth=10,
            random_state=42
        )
        # In practice, load pre-trained model from S3
        return model
        
    async def _load_heavy_model(self) -> RandomForestRegressor:
        """
        Load comprehensive model for detailed analysis
        """
        model = RandomForestRegressor(
            n_estimators=200,  # More trees for higher accuracy
            max_depth=20,
            random_state=42
        )
        # In practice, load pre-trained model from S3
        return model
        
    def _extract_basic_features(self, property_data: Dict[str, Any]) -> List[float]:
        """
        Extract basic features for light model
        """
        return [
            float(property_data.get('sqft', 0)),
            float(property_data.get('bedrooms', 0)),
            float(property_data.get('bathrooms', 0)),
            float(property_data.get('lot_size', 0))
        ]
        
    def _extract_detailed_features(self, property_data: Dict[str, Any]) -> List[float]:
        """
        Extract comprehensive features for heavy model
        """
        basic_features = self._extract_basic_features(property_data)
        return basic_features + [
            float(property_data.get('year_built', 1900)),
            float(property_data.get('last_sale_price', 0)),
            float(property_data.get('school_rating', 0)),
            float(property_data.get('crime_rate', 0))
        ]
        
    async def _find_comparables(self, property_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find comparable properties
        """
        # In practice, query database for similar properties
        return [
            {
                'address': '123 Similar St',
                'sale_price': 350000,
                'sale_date': '2024-01-15',
                'similarity_score': 0.92
            },
            {
                'address': '456 Nearby Ave',
                'sale_price': 375000,
                'sale_date': '2024-02-01',
                'similarity_score': 0.88
            }
        ]

# Initialize valuator
valuator = PropertyValuator()

def valuate(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for property valuation
    """
    return valuator.valuate(event)
