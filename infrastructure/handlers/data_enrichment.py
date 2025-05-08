import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import boto3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class DataEnrichmentService:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.historical_bucket = os.environ.get('HISTORICAL_DATA_BUCKET')
        self.trends_table = self.dynamodb.Table(os.environ.get('TRENDS_TABLE'))
        
    async def enrich_and_store(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich incoming property data and store for historical analysis
        """
        try:
            # Parse incoming data
            properties = json.loads(event['body'])
            
            # Enrich data
            enriched_data = await self._enrich_properties(properties)
            
            # Store historical data
            await self._store_historical_data(enriched_data)
            
            # Update market trends
            await self._update_market_trends(enriched_data)
            
            # Generate insights
            insights = await self._generate_insights(enriched_data)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'enriched_count': len(enriched_data),
                    'insights': insights,
                    'timestamp': datetime.now().isoformat()
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
            
    async def _enrich_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich property data with derived features
        """
        enriched = []
        for prop in properties:
            # Calculate price per sqft
            if prop.get('price') and prop.get('sqft'):
                prop['price_per_sqft'] = prop['price'] / prop['sqft']
                
            # Calculate days on market
            if prop.get('list_date'):
                list_date = datetime.fromisoformat(prop['list_date'])
                prop['days_on_market'] = (datetime.now() - list_date).days
                
            # Add market momentum score
            prop['market_momentum'] = await self._calculate_momentum(prop)
            
            # Add neighborhood score
            prop['neighborhood_score'] = await self._calculate_neighborhood_score(prop)
            
            # Add investment potential score
            prop['investment_potential'] = await self._calculate_investment_potential(prop)
            
            enriched.append(prop)
            
        return enriched
        
    async def _store_historical_data(self, properties: List[Dict[str, Any]]) -> None:
        """
        Store enriched data for historical analysis
        """
        # Group by ZIP code
        by_zip = {}
        for prop in properties:
            zip_code = prop.get('zip_code')
            if zip_code:
                if zip_code not in by_zip:
                    by_zip[zip_code] = []
                by_zip[zip_code].append(prop)
                
        # Store in S3 by ZIP and date
        date_str = datetime.now().strftime('%Y-%m-%d')
        for zip_code, zip_properties in by_zip.items():
            key = f"{zip_code}/{date_str}.json"
            self.s3.put_object(
                Bucket=self.historical_bucket,
                Key=key,
                Body=json.dumps(zip_properties)
            )
            
    async def _update_market_trends(self, properties: List[Dict[str, Any]]) -> None:
        """
        Update market trends analysis
        """
        # Group by ZIP code
        by_zip = {}
        for prop in properties:
            zip_code = prop.get('zip_code')
            if zip_code:
                if zip_code not in by_zip:
                    by_zip[zip_code] = []
                by_zip[zip_code].append(prop)
                
        # Calculate trends for each ZIP
        for zip_code, zip_properties in by_zip.items():
            trends = {
                'zip_code': zip_code,
                'median_price': np.median([p['price'] for p in zip_properties if 'price' in p]),
                'median_price_sqft': np.median([p['price_per_sqft'] for p in zip_properties if 'price_per_sqft' in p]),
                'avg_days_market': np.mean([p['days_on_market'] for p in zip_properties if 'days_on_market' in p]),
                'inventory_count': len(zip_properties),
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in DynamoDB
            self.trends_table.put_item(Item=trends)
            
    async def _generate_insights(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate market insights from enriched data
        """
        df = pd.DataFrame(properties)
        
        insights = {
            'hot_zips': await self._find_hot_zip_codes(df),
            'price_trends': await self._analyze_price_trends(df),
            'investment_opportunities': await self._find_investment_opportunities(df),
            'market_shifts': await self._detect_market_shifts(df)
        }
        
        return insights
        
    async def _calculate_momentum(self, property_data: Dict[str, Any]) -> float:
        """
        Calculate market momentum score
        """
        factors = [
            property_data.get('days_on_market', 30),  # Lower is better
            property_data.get('price_change', 0),     # Higher is better
            property_data.get('view_count', 0)        # Higher is better
        ]
        
        # Normalize and weight factors
        weights = [-0.4, 0.3, 0.3]  # Negative weight for days_on_market
        normalized = [f/100 if i == 0 else f/1000 if i == 1 else f/1000 for i, f in enumerate(factors)]
        
        return sum(n * w for n, w in zip(normalized, weights))
        
    async def _calculate_neighborhood_score(self, property_data: Dict[str, Any]) -> float:
        """
        Calculate neighborhood score
        """
        factors = [
            property_data.get('school_rating', 5),     # 1-10
            property_data.get('crime_rate', 50),       # Lower is better
            property_data.get('amenities_count', 10),  # Higher is better
            property_data.get('transit_score', 50)     # 0-100
        ]
        
        weights = [0.3, -0.2, 0.25, 0.25]  # Negative weight for crime_rate
        normalized = [f/10 if i == 0 else (100-f)/100 if i == 1 else f/20 if i == 2 else f/100 
                     for i, f in enumerate(factors)]
        
        return sum(n * w for n, w in zip(normalized, weights))
        
    async def _calculate_investment_potential(self, property_data: Dict[str, Any]) -> float:
        """
        Calculate investment potential score
        """
        factors = [
            property_data.get('price_per_sqft', 200),    # Lower is better
            property_data.get('market_momentum', 0),     # Higher is better
            property_data.get('neighborhood_score', 0.5), # Higher is better
            property_data.get('rental_demand', 50)       # Higher is better
        ]
        
        weights = [-0.3, 0.3, 0.2, 0.2]  # Negative weight for price_per_sqft
        normalized = [(1000-f)/1000 if i == 0 else f if i == 1 else f if i == 2 else f/100 
                     for i, f in enumerate(factors)]
        
        return sum(n * w for n, w in zip(normalized, weights))
        
    async def _find_hot_zip_codes(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify hot ZIP codes based on multiple factors
        """
        hot_zips = []
        for zip_code in df['zip_code'].unique():
            zip_df = df[df['zip_code'] == zip_code]
            
            score = (
                zip_df['market_momentum'].mean() * 0.4 +
                zip_df['neighborhood_score'].mean() * 0.3 +
                zip_df['investment_potential'].mean() * 0.3
            )
            
            if score > 0.7:  # Threshold for "hot" ZIP codes
                hot_zips.append({
                    'zip_code': zip_code,
                    'score': float(score),
                    'avg_price': float(zip_df['price'].mean()),
                    'inventory': len(zip_df)
                })
                
        return sorted(hot_zips, key=lambda x: x['score'], reverse=True)
        
    async def _analyze_price_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze price trends and patterns
        """
        trends = {
            'overall_trend': {
                'median_price': float(df['price'].median()),
                'median_price_sqft': float(df['price_per_sqft'].median()),
                'price_momentum': float(df['market_momentum'].mean())
            },
            'by_property_type': {},
            'by_zip': {}
        }
        
        # Analyze by property type
        for prop_type in df['property_type'].unique():
            type_df = df[df['property_type'] == prop_type]
            trends['by_property_type'][prop_type] = {
                'median_price': float(type_df['price'].median()),
                'inventory': len(type_df)
            }
            
        # Analyze by ZIP
        for zip_code in df['zip_code'].unique():
            zip_df = df[df['zip_code'] == zip_code]
            trends['by_zip'][zip_code] = {
                'median_price': float(zip_df['price'].median()),
                'inventory': len(zip_df)
            }
            
        return trends
        
    async def _find_investment_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify specific investment opportunities
        """
        opportunities = []
        
        # Find properties with high potential
        high_potential = df[df['investment_potential'] > 0.8]
        for _, prop in high_potential.iterrows():
            opportunities.append({
                'property_id': prop['id'],
                'address': prop['address'],
                'price': float(prop['price']),
                'investment_score': float(prop['investment_potential']),
                'key_factors': [
                    'high_momentum' if prop['market_momentum'] > 0.7 else None,
                    'good_location' if prop['neighborhood_score'] > 0.7 else None,
                    'undervalued' if prop['price_per_sqft'] < df['price_per_sqft'].median() else None
                ]
            })
            
        return sorted(opportunities, key=lambda x: x['investment_score'], reverse=True)
        
    async def _detect_market_shifts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect significant market shifts and patterns
        """
        shifts = {
            'price_shifts': {},
            'inventory_changes': {},
            'demand_patterns': {}
        }
        
        # Analyze price shifts by ZIP
        for zip_code in df['zip_code'].unique():
            zip_df = df[df['zip_code'] == zip_code]
            current_median = zip_df['price'].median()
            
            # Compare with historical data (last month)
            historical = await self._get_historical_data(zip_code, days=30)
            if historical:
                price_change = (current_median - historical['median_price']) / historical['median_price']
                if abs(price_change) > 0.05:  # 5% threshold
                    shifts['price_shifts'][zip_code] = {
                        'change': float(price_change),
                        'current_median': float(current_median),
                        'previous_median': float(historical['median_price'])
                    }
                    
        return shifts
        
    async def _get_historical_data(self, zip_code: str, days: int) -> Optional[Dict[str, Any]]:
        """
        Get historical data for comparison
        """
        date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        try:
            response = self.s3.get_object(
                Bucket=self.historical_bucket,
                Key=f"{zip_code}/{date}.json"
            )
            return json.loads(response['Body'].read())
        except:
            return None

# Initialize service
enrichment_service = DataEnrichmentService()

def enrich_and_store(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for data enrichment and storage
    """
    return enrichment_service.enrich_and_store(event)
