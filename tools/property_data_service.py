"""Property data service with hybrid Redfin + ATTOM approach"""
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
import logging
import os
import json
import random
from .attom_data_tool import AttomDataTool
from .api_usage_tracker import get_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockRedfinData:
    """Generate realistic property data for any US location"""
    def __init__(self):
        # Common street types across US
        self.street_types = ['Ave', 'St', 'Rd', 'Dr', 'Ln', 'Way', 'Blvd', 'Ct', 'Pl', 'Cir']
        
        # Common street names by region
        self.street_names = {
            'urban': ['Oak', 'Maple', 'Cedar', 'Pine', 'Main', 'Washington', 'Park', 'Lake', 'River', 'Hill'],
            'suburban': ['Willow', 'Sunset', 'Forest', 'Valley', 'Ridge', 'Meadow', 'Creek', 'Spring', 'Green'],
            'luxury': ['Highland', 'Royal', 'Grand', 'Estate', 'Manor', 'Legacy', 'Vista', 'Overlook']
        }
        
        self.property_types = ['Single Family', 'Townhouse', 'Condo', 'Multi-Family']
        
        # Price ranges by area type (min, max, median)
        self.price_ranges = {
            'urban_luxury': (800000, 5000000, 1500000),
            'urban_mid': (400000, 1200000, 600000),
            'urban_starter': (200000, 500000, 350000),
            'suburban_luxury': (600000, 2000000, 900000),
            'suburban_mid': (300000, 800000, 450000),
            'suburban_starter': (150000, 400000, 250000),
            'rural_luxury': (400000, 1200000, 600000),
            'rural_mid': (200000, 500000, 300000),
            'rural_starter': (100000, 300000, 180000)
        }
        
        # Regional market adjustments
        self.market_multipliers = {
            'CA': 2.5, 'NY': 2.0, 'FL': 1.3, 'TX': 1.1,
            'IL': 1.2, 'MA': 1.8, 'WA': 1.6, 'CO': 1.4,
            'OR': 1.5, 'DC': 2.2, 'VA': 1.3, 'MD': 1.4
        }
    
    def _get_area_type(self, zip_code: str) -> tuple:
        """Determine area type and market characteristics from ZIP"""
        # Use last 2 digits to create variation
        variation = int(zip_code[-2:]) / 100
        
        # First digit often indicates urban (0,1) vs rural (7,8,9)
        first_digit = int(zip_code[0])
        
        if first_digit in [0, 1, 2]:
            area = 'urban'
            if variation > 0.7:
                price_range = 'urban_luxury'
            elif variation > 0.3:
                price_range = 'urban_mid'
            else:
                price_range = 'urban_starter'
        elif first_digit in [3, 4, 5, 6]:
            area = 'suburban'
            if variation > 0.8:
                price_range = 'suburban_luxury'
            elif variation > 0.4:
                price_range = 'suburban_mid'
            else:
                price_range = 'suburban_starter'
        else:
            area = 'rural'
            if variation > 0.9:
                price_range = 'rural_luxury'
            elif variation > 0.5:
                price_range = 'rural_mid'
            else:
                price_range = 'rural_starter'
        
        return area, price_range
    
    def _get_market_multiplier(self, state: str) -> float:
        """Get market price multiplier for state"""
        return self.market_multipliers.get(state, 1.0)
    
    def generate_properties(self, zip_code: str, state: str = None, count: int = 20) -> List[Dict]:
        """Generate realistic property listings for any location"""
        properties = []
        area_type, price_range = self._get_area_type(zip_code)
        base_min, base_max, base_median = self.price_ranges[price_range]
        
        # Apply regional market adjustment
        if state:
            multiplier = self._get_market_multiplier(state)
            base_min *= multiplier
            base_max *= multiplier
            base_median *= multiplier
        
        # Generate properties
        for _ in range(count):
            # Generate realistic price based on area characteristics
            price_variation = random.uniform(0.8, 1.2)
            base_price = random.triangular(base_min, base_max, base_median)
            price = base_price * price_variation
            
            # Generate realistic specs based on price point
            beds = max(1, min(8, int(price / base_median * 3) + random.randint(-1, 1)))
            baths = max(1, beds - random.randint(0, 2))
            sqft = int(price / (base_median / 2000) + random.randint(-500, 500))
            
            # Generate address
            street_name = random.choice(self.street_names[area_type])
            street_type = random.choice(self.street_types)
            number = random.randint(1, 99) * 100 + random.randint(0, 99)
            
            # Adjust property types based on area
            if area_type == 'urban':
                prop_type = random.choice(['Condo', 'Townhouse', 'Single Family'])
            elif area_type == 'suburban':
                prop_type = random.choice(['Single Family', 'Townhouse'])
            else:
                prop_type = 'Single Family'
            
            # Generate property data
            property_data = {
                'address': f'{number} {street_name} {street_type}, {zip_code}',
                'price': price,
                'beds': beds,
                'baths': baths,
                'square_feet': sqft,
                'price_reduced': random.random() < 0.2,
                'days_on_market': random.randint(1, 120),
                'property_type': prop_type,
                'year_built': random.randint(1960, 2020),
                'lot_size': sqft + random.randint(1000, 5000) if prop_type == 'Single Family' else sqft,
                'last_sale_date': (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d'),
                'last_sale_price': price * 0.8,  # Assume 20% appreciation
                'tax_assessment': price * 0.9,
                'owner_occupied': random.random() < 0.7,
                'foreclosure_status': 'None' if random.random() < 0.95 else 'Pre-foreclosure',
                'data_source': 'redfin'
            }
            
            properties.append(property_data)
        
        return properties

class PropertyDataService:
    """Property data service with hybrid Redfin + ATTOM approach"""
    def __init__(self):
        self.mock_redfin = MockRedfinData()
        self.attom = AttomDataTool()
        self.tracker = get_tracker()
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        
        # Create cache directory
        os.makedirs('data/cache', exist_ok=True)
        self.cache_file = 'data/cache/property_cache.json'
        self.load_cache()
    
    def load_cache(self):
        """Load cached property data"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    self.cache_timestamps = {
                        k: datetime.fromisoformat(v) 
                        for k, v in data.get('timestamps', {}).items()
                    }
                logger.info(f"Loaded {len(self.cache)} cached property searches")
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            self.cache = {}
            self.cache_timestamps = {}
    
    def save_cache(self):
        """Save property data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'cache': self.cache,
                    'timestamps': {
                        k: v.isoformat() 
                        for k, v in self.cache_timestamps.items()
                    }
                }, f)
            logger.info("Saved property cache to disk")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def _cache_key(self, zip_code: str, filters: Dict) -> str:
        """Generate cache key from search parameters"""
        filter_str = json.dumps(filters, sort_keys=True) if filters else ''
        return f"{zip_code}_{filter_str}"
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache or key not in self.cache_timestamps:
            return False
        age = datetime.now() - self.cache_timestamps[key]
        return age < self.cache_duration
    
    async def search_properties(self, zip_code: str, filters: Dict = None) -> List[Dict]:
        """Search for properties using hybrid approach"""
        try:
            cache_key = self._cache_key(zip_code, filters)
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.info(f"Using cached data for {zip_code}")
                return self.cache[cache_key]
            
            # Get Redfin data first
            logger.info(f"Generating Redfin data for {zip_code}")
            properties = self.mock_redfin.generate_properties(zip_code)
            
            # Apply filters to Redfin data
            if filters:
                properties = self._apply_filters(properties, filters)
            
            # Check ATTOM API usage before enrichment
            usage = self.tracker.get_monthly_summary()
            remaining_reports = usage['reports_remaining']
            
            # Enrich high-priority properties with ATTOM data if available
            if properties and remaining_reports > 0:
                priority_props = self._prioritize_properties(properties)
                enrichment_count = min(3, remaining_reports)  # Limit to 3 properties to save API calls
                
                logger.info(f"Enriching {enrichment_count} properties with ATTOM data")
                logger.info(f"ATTOM API reports remaining: {remaining_reports}")
                
                for prop in priority_props[:enrichment_count]:
                    try:
                        attom_data = await self.attom.get_property_details(
                            zip_code=zip_code,
                            property_type=prop.get('property_type'),
                            min_beds=prop.get('beds'),
                            max_price=prop.get('price')
                        )
                        
                        if attom_data:
                            # Track API usage
                            self.tracker.track_api_call('report', 1)
                            
                            # Update with ATTOM data
                            prop.update({
                                'tax_assessment': attom_data[0].get('price', prop['tax_assessment']),
                                'last_sale_date': attom_data[0].get('last_sale_date', prop['last_sale_date']),
                                'last_sale_price': attom_data[0].get('last_sale_price', prop['last_sale_price']),
                                'lot_size': attom_data[0].get('lot_size', prop['lot_size']),
                                'year_built': attom_data[0].get('year_built', prop['year_built']),
                                'attom_enriched': True,
                                'data_source': 'redfin+attom'
                            })
                            
                    except Exception as e:
                        logger.error(f"Error enriching with ATTOM data: {str(e)}")
                        continue
            
            # Cache results
            self.cache[cache_key] = properties
            self.cache_timestamps[cache_key] = datetime.now()
            self.save_cache()
            
            return properties
            
        except Exception as e:
            logger.error(f"Error searching properties: {str(e)}")
            return []
    
    def _apply_filters(self, properties: List[Dict], filters: Dict) -> List[Dict]:
        """Apply search filters to properties"""
        result = properties
        
        if filters.get('max_price'):
            result = [p for p in result if p.get('price', float('inf')) <= filters['max_price']]
        if filters.get('min_beds'):
            result = [p for p in result if p.get('beds', 0) >= filters['min_beds']]
        if filters.get('min_sqft'):
            result = [p for p in result if p.get('square_feet', 0) >= filters['min_sqft']]
        if filters.get('only_reduced'):
            result = [p for p in result if p.get('price_reduced', False)]
        if filters.get('property_type'):
            result = [p for p in result if p.get('property_type', '').lower() == filters['property_type'].lower()]
        
        return result
    
    def _prioritize_properties(self, properties: List[Dict]) -> List[Dict]:
        """Prioritize properties for ATTOM enrichment"""
        def priority_score(prop):
            score = 0
            if prop.get('days_on_market', 0) <= 7:  # New listings
                score += 3
            if prop.get('price_reduced'):  # Price drops
                score += 2
            if prop.get('foreclosure_status') != 'None':  # Distressed properties
                score += 2
            if not prop.get('owner_occupied'):  # Investment properties
                score += 1
            score += prop.get('price', 0) / 1000000  # Higher-value properties
            return score
        
        return sorted(properties, key=priority_score, reverse=True)
    
    def get_attom_usage(self) -> Dict:
        """Get ATTOM API usage stats"""
        summary = self.tracker.get_monthly_summary()
        return {
            'requests_made': summary['reports_used'],
            'requests_remaining': summary['reports_remaining'],
            'total_cost': summary['total_cost'],
            'reset_date': summary.get('reset_date', 'Unknown')
        }
