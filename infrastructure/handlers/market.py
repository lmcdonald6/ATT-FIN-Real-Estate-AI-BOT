import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import redis
import boto3
from botocore.exceptions import ClientError

# Initialize clients
redis_client = redis.Redis(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT']),
    decode_responses=True
)

dynamodb = boto3.resource('dynamodb')
cache_table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

class MarketAnalyzer:
    def __init__(self):
        self.cache_ttl = int(os.environ.get('CACHE_TTL', 3600))
        
    async def analyze(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cost-efficient market analysis handler
        """
        try:
            # Parse request
            body = json.loads(event['body'])
            location = body.get('location')
            
            if not location:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Location is required'})
                }
                
            # Try cache first
            cached_result = await self._get_cached_result(location)
            if cached_result:
                return {
                    'statusCode': 200,
                    'body': json.dumps(cached_result)
                }
                
            # Perform analysis
            result = await self._analyze_market(location)
            
            # Cache result
            await self._cache_result(location, result)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
            
    async def _get_cached_result(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Try multiple cache layers
        """
        # Try Redis first (fastest)
        cache_key = f"market:{location}"
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
                    # Also set in Redis for next time
                    redis_client.set(
                        cache_key,
                        json.dumps(item['data']),
                        ex=self.cache_ttl
                    )
                    return item['data']
        except ClientError:
            pass
            
        return None
        
    async def _cache_result(self, location: str, result: Dict[str, Any]) -> None:
        """
        Multi-layer caching strategy
        """
        cache_key = f"market:{location}"
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
        
    async def _analyze_market(self, location: str) -> Dict[str, Any]:
        """
        Perform actual market analysis
        """
        # Get basic market data
        market_data = await self._get_market_data(location)
        
        # Only run ML if really needed
        if self._needs_detailed_analysis(market_data):
            predictions = await self._run_ml_predictions(market_data)
            market_data.update(predictions)
        
        return market_data
        
    async def _get_market_data(self, location: str) -> Dict[str, Any]:
        """
        Get basic market data (cheaper operation)
        """
        return {
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'market_indicators': {
                'price_trend': 'stable',
                'inventory_level': 'medium',
                'days_on_market': 30
            },
            'basic_stats': {
                'median_price': 350000,
                'active_listings': 150,
                'monthly_sales': 45
            }
        }
        
    def _needs_detailed_analysis(self, market_data: Dict[str, Any]) -> bool:
        """
        Determine if we need to run expensive ML
        """
        # Check if basic stats indicate significant market movement
        basic_stats = market_data['basic_stats']
        
        if basic_stats['monthly_sales'] > 100:
            return True
            
        if basic_stats['active_listings'] < 50:
            return True
            
        return False
        
    async def _run_ml_predictions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run ML predictions (more expensive operation)
        """
        return {
            'predictions': {
                'price_change_6m': 0.05,
                'price_change_12m': 0.08,
                'confidence': 0.85
            },
            'opportunities': [
                {
                    'type': 'emerging_neighborhood',
                    'score': 0.75,
                    'factors': ['new_businesses', 'transit_development']
                }
            ]
        }

# Initialize analyzer
analyzer = MarketAnalyzer()

def analyze(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for market analysis
    """
    return analyzer.analyze(event)
