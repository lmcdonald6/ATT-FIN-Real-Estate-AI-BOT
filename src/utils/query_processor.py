"""Process natural language queries for property searches"""
import re
from typing import Dict, Optional, List

class QueryProcessor:
    """Parse natural language queries into structured filters"""
    def __init__(self):
        # Price-related keywords
        self.price_keywords = {
            'under': 'max',
            'below': 'max',
            'less than': 'max',
            'up to': 'max',
            'over': 'min',
            'above': 'min',
            'more than': 'min',
            'at least': 'min'
        }
        
        # Property types mapping
        self.property_types = {
            'house': 'Single Family',
            'home': 'Single Family',
            'single family': 'Single Family',
            'condo': 'Condo',
            'condominium': 'Condo',
            'townhouse': 'Townhouse',
            'townhome': 'Townhouse',
            'duplex': 'Multi-Family',
            'triplex': 'Multi-Family',
            'multi-family': 'Multi-Family',
            'multifamily': 'Multi-Family',
            'multi family': 'Multi-Family'
        }
        
        # Area type indicators
        self.area_indicators = {
            'luxury': 'luxury',
            'high-end': 'luxury',
            'upscale': 'luxury',
            'downtown': 'urban',
            'city': 'urban',
            'suburban': 'suburban',
            'residential': 'suburban',
            'rural': 'rural',
            'country': 'rural'
        }
        
        # Location mappings
        self.location_data = {
            'manhattan': {
                'state': 'NY',
                'zip_codes': ['10001', '10011', '10016', '10019'],
                'area_type': 'urban'
            },
            'silicon valley': {
                'state': 'CA',
                'zip_codes': ['94025', '94301', '95014'],
                'area_type': 'suburban'
            },
            'green hills': {
                'state': 'TN',
                'zip_codes': ['37215'],
                'area_type': 'suburban'
            },
            'miami': {
                'state': 'FL',
                'zip_codes': ['33101', '33129', '33130'],
                'area_type': 'urban'
            },
            'austin': {
                'state': 'TX',
                'zip_codes': ['78701', '78702', '78703'],
                'area_type': 'urban'
            },
            'dallas': {
                'state': 'TX',
                'zip_codes': ['75201', '75202', '75204'],
                'area_type': 'urban'
            },
            'houston': {
                'state': 'TX',
                'zip_codes': ['77002', '77003', '77004'],
                'area_type': 'urban'
            },
            'orlando': {
                'state': 'FL',
                'zip_codes': ['32801', '32803', '32804'],
                'area_type': 'suburban'
            }
        }
    
    def parse_query(self, query: str) -> Dict:
        """Parse natural language query into search parameters"""
        query = query.lower().strip()
        
        # Extract location
        location_info = self._extract_location(query)
        if not location_info:
            return {'error': 'Location not found in query'}
        
        # Extract price constraints
        price_range = self._extract_price(query)
        
        # Extract property type
        property_type = self._extract_property_type(query)
        
        # Extract minimum bedrooms
        min_beds = self._extract_bedrooms(query)
        
        # Extract area type
        area_type = self._extract_area_type(query)
        
        # Build search parameters
        params = {
            'state': location_info['state'],
            'zip_codes': location_info['zip_codes'],
            'area_type': area_type or location_info['area_type']
        }
        
        if property_type:
            params['property_type'] = property_type
        
        if min_beds:
            params['min_beds'] = min_beds
            
        if price_range.get('min'):
            params['min_price'] = price_range['min']
        if price_range.get('max'):
            params['max_price'] = price_range['max']
        
        return params
    
    def _extract_location(self, query: str) -> Optional[Dict]:
        """Extract location information from query"""
        for location, data in self.location_data.items():
            if location in query:
                return data
        return None
    
    def _extract_price(self, query: str) -> Dict:
        """Extract price constraints from query"""
        price_range = {}
        
        # Find all numbers in the query
        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(?:k|m|million|thousand)?', query)
        
        for num in numbers:
            # Convert number to float
            value = float(num)
            
            # Check for k/m multipliers
            if 'million' in query or 'm' in query:
                value *= 1_000_000
            elif 'thousand' in query or 'k' in query:
                value *= 1_000
            
            # Determine if it's a min or max based on context
            for keyword, type_ in self.price_keywords.items():
                if keyword in query:
                    price_range[type_] = value
                    break
        
        return price_range
    
    def _extract_property_type(self, query: str) -> Optional[str]:
        """Extract property type from query"""
        for keyword, type_ in self.property_types.items():
            if keyword in query:
                return type_
        return None
    
    def _extract_bedrooms(self, query: str) -> Optional[int]:
        """Extract minimum number of bedrooms from query"""
        bed_match = re.search(r'(\d+)\s*(?:bed|bedroom|br)', query)
        if bed_match:
            return int(bed_match.group(1))
        return None
    
    def _extract_area_type(self, query: str) -> Optional[str]:
        """Extract area type from query"""
        for indicator, area_type in self.area_indicators.items():
            if indicator in query:
                return area_type
        return None
