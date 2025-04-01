"""Generate realistic mock property data based on location"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MockRedfinData:
    """Generate realistic property data matching Redfin's structure"""
    def __init__(self):
        # Market multipliers by state (relative to base prices)
        self.state_multipliers = {
            'CA': 2.5,  # California premium
            'NY': 2.3,  # New York premium
            'FL': 1.4,  # Florida premium
            'TX': 1.3,  # Texas premium
            'TN': 1.0,  # Nashville baseline
        }
        
        # Area type multipliers
        self.area_multipliers = {
            'urban': 1.4,
            'suburban': 1.0,
            'rural': 0.7,
            'luxury': 2.0
        }
        
        # Base price ranges by property type (will be adjusted by multipliers)
        self.base_prices = {
            'Single Family': {
                'min': 300000,
                'max': 800000
            },
            'Townhouse': {
                'min': 250000,
                'max': 600000
            },
            'Condo': {
                'min': 200000,
                'max': 500000
            },
            'Multi-Family': {
                'min': 400000,
                'max': 1000000
            }
        }
        
        # Common street names by area type
        self.street_names = {
            'urban': ['Main', 'Broadway', 'Market', 'Park', 'Downtown'],
            'suburban': ['Oak', 'Maple', 'Cedar', 'Willow', 'Pleasant'],
            'luxury': ['Highland', 'Grand', 'Royal', 'Estate', 'Manor'],
            'rural': ['County Line', 'Ridge', 'Valley', 'Mountain', 'Lake']
        }
        
        self.street_types = ['St', 'Ave', 'Blvd', 'Dr', 'Ln', 'Way', 'Circle']
        
        # Property features by type
        self.property_features = {
            'Single Family': {
                'beds': (3, 5),
                'baths': (2, 4),
                'sqft': (1800, 3500)
            },
            'Townhouse': {
                'beds': (2, 4),
                'baths': (2, 3),
                'sqft': (1500, 2500)
            },
            'Condo': {
                'beds': (1, 3),
                'baths': (1, 2),
                'sqft': (800, 2000)
            },
            'Multi-Family': {
                'beds': (4, 8),
                'baths': (3, 6),
                'sqft': (2500, 5000)
            }
        }
    
    def get_properties(
        self,
        zip_code: str,
        state: str,
        property_type: Optional[str] = None,
        min_beds: Optional[int] = None,
        max_price: Optional[float] = None,
        area_type: Optional[str] = None
    ) -> List[Dict]:
        """Generate realistic property listings for a location"""
        try:
            # Determine area type if not provided
            if not area_type:
                area_type = self._determine_area_type(zip_code)
            
            # Get price multipliers
            state_mult = self.state_multipliers.get(state, 1.0)
            area_mult = self.area_multipliers.get(area_type, 1.0)
            total_mult = state_mult * area_mult
            
            # Generate 5-10 properties
            num_properties = random.randint(5, 10)
            properties = []
            
            for _ in range(num_properties):
                # Select property type if not specified
                prop_type = property_type or self._select_property_type(area_type)
                
                # Generate property details
                prop = self._generate_property(
                    zip_code=zip_code,
                    property_type=prop_type,
                    price_multiplier=total_mult,
                    area_type=area_type
                )
                
                # Apply filters
                if self._matches_filters(prop, min_beds, max_price):
                    properties.append(prop)
            
            return properties
            
        except Exception as e:
            print(f"Error generating mock data: {str(e)}")
            return []
    
    def _determine_area_type(self, zip_code: str) -> str:
        """Determine area type based on ZIP code patterns"""
        # Simple heuristic for MVP
        if zip_code.startswith(('100', '101', '102')):  # NYC
            return 'urban'
        elif zip_code.startswith(('940', '941')):  # SF Bay Area
            return 'urban'
        elif zip_code.startswith(('372')):  # Nashville area
            return 'suburban'
        elif zip_code.startswith(('331', '332')):  # Miami area
            return 'urban'
        else:
            return 'suburban'  # Default to suburban
    
    def _select_property_type(self, area_type: str) -> str:
        """Select appropriate property type for area"""
        if area_type == 'urban':
            weights = [0.2, 0.3, 0.4, 0.1]  # More condos/townhouses
        elif area_type == 'suburban':
            weights = [0.6, 0.2, 0.1, 0.1]  # More single family
        elif area_type == 'luxury':
            weights = [0.7, 0.1, 0.1, 0.1]  # Mostly single family
        else:  # rural
            weights = [0.8, 0.1, 0.0, 0.1]  # Almost all single family
        
        return random.choices(
            list(self.base_prices.keys()),
            weights=weights
        )[0]
    
    def _generate_property(
        self,
        zip_code: str,
        property_type: str,
        price_multiplier: float,
        area_type: str
    ) -> Dict:
        """Generate a single property listing"""
        # Get base price range and apply multiplier
        price_range = self.base_prices[property_type]
        min_price = price_range['min'] * price_multiplier
        max_price = price_range['max'] * price_multiplier
        
        # Get property features
        features = self.property_features[property_type]
        beds = random.randint(*features['beds'])
        baths = random.randint(*features['baths'])
        sqft = random.randint(*features['sqft'])
        
        # Calculate price based on features
        base_price = random.uniform(min_price, max_price)
        price_adjustments = {
            'beds': 50000,  # Per bedroom above base
            'baths': 25000,  # Per bathroom above base
            'sqft': 100     # Per sq ft above base
        }
        
        # Adjust price based on features
        price = base_price
        price += (beds - features['beds'][0]) * price_adjustments['beds']
        price += (baths - features['baths'][0]) * price_adjustments['baths']
        price += (sqft - features['sqft'][0]) * price_adjustments['sqft']
        
        # Generate address
        street_number = random.randint(1, 9999)
        street_name = random.choice(self.street_names[area_type])
        street_type = random.choice(self.street_types)
        
        # Random dates within last 30 days
        list_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        return {
            'address': f"{street_number} {street_name} {street_type}",
            'zip_code': zip_code,
            'price': round(price, 2),
            'beds': beds,
            'baths': baths,
            'square_feet': sqft,
            'property_type': property_type,
            'year_built': random.randint(1960, 2023),
            'days_on_market': random.randint(0, 60),
            'price_reduced': random.random() < 0.2,  # 20% chance of price reduction
            'list_date': list_date.isoformat(),
            'data_source': 'redfin_mock'
        }
    
    def _matches_filters(
        self,
        property_data: Dict,
        min_beds: Optional[int],
        max_price: Optional[float]
    ) -> bool:
        """Check if property matches search filters"""
        if min_beds and property_data['beds'] < min_beds:
            return False
        if max_price and property_data['price'] > max_price:
            return False
        return True
