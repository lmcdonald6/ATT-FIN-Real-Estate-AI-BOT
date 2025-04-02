"""
Data integration service for real estate property data.
Handles integration with external data sources and data validation.
"""
from typing import Dict, List, Optional, Union
import requests
import json
import logging
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DataSourceConfig:
    """Configuration for external data sources"""
    def __init__(self, api_key: str, base_url: str, rate_limit: int = 100):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit = rate_limit  # requests per minute
        
class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch_property(self, property_id: str) -> Dict:
        """Fetch property data by ID"""
        pass
        
    @abstractmethod
    def search_properties(self, criteria: Dict) -> List[Dict]:
        """Search for properties based on criteria"""
        pass
        
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """Validate property data"""
        pass
        
class MLSDataSource(DataSource):
    """Integration with MLS (Multiple Listing Service) data"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        })
        
    def fetch_property(self, property_id: str) -> Dict:
        """Fetch property data from MLS"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/properties/{property_id}"
            )
            response.raise_for_status()
            data = response.json()
            
            if self.validate_data(data):
                return self._normalize_data(data)
            else:
                raise ValueError("Invalid property data received from MLS")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching property from MLS: {str(e)}")
            raise
            
    def search_properties(self, criteria: Dict) -> List[Dict]:
        """Search for properties in MLS"""
        try:
            response = self.session.post(
                f"{self.config.base_url}/properties/search",
                json=criteria
            )
            response.raise_for_status()
            properties = response.json()
            
            validated_properties = []
            for prop in properties:
                if self.validate_data(prop):
                    validated_properties.append(self._normalize_data(prop))
                    
            return validated_properties
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching properties in MLS: {str(e)}")
            raise
            
    def validate_data(self, data: Dict) -> bool:
        """Validate MLS property data"""
        required_fields = [
            'property_id', 'address', 'price', 'bedrooms',
            'bathrooms', 'square_feet', 'property_type'
        ]
        
        return all(
            field in data and data[field] is not None
            for field in required_fields
        )
        
    def _normalize_data(self, data: Dict) -> Dict:
        """Normalize MLS data to standard format"""
        return {
            'property_id': data.get('property_id'),
            'address': {
                'street': data.get('address', {}).get('street'),
                'city': data.get('address', {}).get('city'),
                'state': data.get('address', {}).get('state'),
                'zip': data.get('address', {}).get('zip')
            },
            'price': float(data.get('price', 0)),
            'bedrooms': int(data.get('bedrooms', 0)),
            'bathrooms': float(data.get('bathrooms', 0)),
            'square_feet': float(data.get('square_feet', 0)),
            'property_type': data.get('property_type'),
            'year_built': int(data.get('year_built', 0)),
            'lot_size': float(data.get('lot_size', 0)),
            'features': data.get('features', []),
            'last_updated': datetime.now().isoformat()
        }
        
class PublicRecordsDataSource(DataSource):
    """Integration with public records data"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': config.api_key,
            'Content-Type': 'application/json'
        })
        
    def fetch_property(self, property_id: str) -> Dict:
        """Fetch property data from public records"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/properties/{property_id}"
            )
            response.raise_for_status()
            data = response.json()
            
            if self.validate_data(data):
                return self._normalize_data(data)
            else:
                raise ValueError("Invalid property data from public records")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching property from public records: {str(e)}")
            raise
            
    def search_properties(self, criteria: Dict) -> List[Dict]:
        """Search for properties in public records"""
        try:
            response = self.session.post(
                f"{self.config.base_url}/properties/search",
                json=criteria
            )
            response.raise_for_status()
            properties = response.json()
            
            validated_properties = []
            for prop in properties:
                if self.validate_data(prop):
                    validated_properties.append(self._normalize_data(prop))
                    
            return validated_properties
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching public records: {str(e)}")
            raise
            
    def validate_data(self, data: Dict) -> bool:
        """Validate public records property data"""
        required_fields = [
            'parcel_id', 'address', 'assessed_value',
            'tax_year', 'owner_info'
        ]
        
        return all(
            field in data and data[field] is not None
            for field in required_fields
        )
        
    def _normalize_data(self, data: Dict) -> Dict:
        """Normalize public records data to standard format"""
        return {
            'parcel_id': data.get('parcel_id'),
            'address': {
                'street': data.get('address', {}).get('street'),
                'city': data.get('address', {}).get('city'),
                'state': data.get('address', {}).get('state'),
                'zip': data.get('address', {}).get('zip')
            },
            'tax_info': {
                'assessed_value': float(data.get('assessed_value', 0)),
                'tax_year': int(data.get('tax_year', 0)),
                'tax_amount': float(data.get('tax_amount', 0))
            },
            'ownership': {
                'owner_name': data.get('owner_info', {}).get('name'),
                'owner_type': data.get('owner_info', {}).get('type'),
                'purchase_date': data.get('owner_info', {}).get('purchase_date'),
                'purchase_price': float(data.get('owner_info', {}).get('purchase_price', 0))
            },
            'last_updated': datetime.now().isoformat()
        }
        
class DataIntegrationService:
    """Service for integrating data from multiple sources"""
    
    def __init__(self):
        self.data_sources: Dict[str, DataSource] = {}
        
    def add_data_source(self, name: str, source: DataSource):
        """Add a new data source"""
        self.data_sources[name] = source
        
    def get_property_data(self, property_id: str, sources: Optional[List[str]] = None) -> Dict:
        """Get property data from specified sources"""
        if not sources:
            sources = list(self.data_sources.keys())
            
        property_data = {}
        errors = []
        
        for source_name in sources:
            if source_name not in self.data_sources:
                logger.warning(f"Data source '{source_name}' not found")
                continue
                
            try:
                source_data = self.data_sources[source_name].fetch_property(property_id)
                property_data[source_name] = source_data
            except Exception as e:
                logger.error(f"Error fetching data from {source_name}: {str(e)}")
                errors.append({
                    'source': source_name,
                    'error': str(e)
                })
                
        return {
            'property_id': property_id,
            'data': property_data,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
        
    def search_properties(self, criteria: Dict, sources: Optional[List[str]] = None) -> Dict:
        """Search for properties across multiple sources"""
        if not sources:
            sources = list(self.data_sources.keys())
            
        results = {}
        errors = []
        
        for source_name in sources:
            if source_name not in self.data_sources:
                logger.warning(f"Data source '{source_name}' not found")
                continue
                
            try:
                source_results = self.data_sources[source_name].search_properties(criteria)
                results[source_name] = source_results
            except Exception as e:
                logger.error(f"Error searching in {source_name}: {str(e)}")
                errors.append({
                    'source': source_name,
                    'error': str(e)
                })
                
        return {
            'criteria': criteria,
            'results': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
