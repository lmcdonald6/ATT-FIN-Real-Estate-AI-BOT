"""Data Manager for Real Estate Bot"""
import pandas as pd
from typing import Dict, List
import os
from datetime import datetime, timedelta
import logging
from attom_api import AttomAPI

logger = logging.getLogger(__name__)

class DataManager:
    """Manages data storage and retrieval for real estate data"""
    
    def __init__(self):
        self.attom = AttomAPI()
        self.data_dir = "data"
        self.create_data_directory()
        
        # Define Excel files for different data types
        self.files = {
            'property_details': 'property_details.xlsx',
            'market_trends': 'market_trends.xlsx',
            'owner_info': 'owner_info.xlsx',
            'lead_scores': 'lead_scores.xlsx'
        }
        
        # Cache expiration times (in days)
        self.cache_expiry = {
            'property_details': 30,  # Property details valid for 30 days
            'market_trends': 7,      # Market trends update weekly
            'owner_info': 90,        # Owner info valid for 90 days
            'lead_scores': 14        # Lead scores update bi-weekly
        }
    
    def create_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_file_path(self, data_type: str) -> str:
        """Get full path for a data file"""
        return os.path.join(self.data_dir, self.files[data_type])
    
    def is_data_fresh(self, data_type: str, address: str) -> bool:
        """Check if stored data is still fresh"""
        file_path = self.get_file_path(data_type)
        if not os.path.exists(file_path):
            return False
            
        try:
            df = pd.read_excel(file_path)
            if address not in df['address'].values:
                return False
                
            last_updated = pd.to_datetime(
                df.loc[df['address'] == address, 'last_updated'].iloc[0]
            )
            expiry_days = self.cache_expiry[data_type]
            return datetime.now() - last_updated < timedelta(days=expiry_days)
            
        except Exception as e:
            logger.error(f"Error checking data freshness: {str(e)}")
            return False
    
    def store_property_details(self, address: str, zipcode: str):
        """Store property details in Excel"""
        data = self.attom.get_property_details(address, zipcode)
        if not data:
            return
            
        df_data = {
            'address': address,
            'zipcode': zipcode,
            'last_updated': datetime.now(),
            'beds': data.get('building', {}).get('beds'),
            'baths': data.get('building', {}).get('baths'),
            'sqft': data.get('building', {}).get('size'),
            'value': data.get('assessment', {}).get('value'),
            'year_built': data.get('summary', {}).get('yearBuilt'),
            'lot_size': data.get('lot', {}).get('size'),
            'property_type': data.get('summary', {}).get('proptype'),
            'zoning': data.get('building', {}).get('zoning')
        }
        
        self._update_excel('property_details', df_data)
    
    def store_market_trends(self, zipcode: str):
        """Store market trends in Excel"""
        data = self.attom.get_market_trends(zipcode)
        if not data:
            return
            
        df_data = {
            'zipcode': zipcode,
            'last_updated': datetime.now(),
            'median_price': data.get('summary', {}).get('medianPrice'),
            'price_trend': data.get('summary', {}).get('priceChange'),
            'days_on_market': data.get('summary', {}).get('daysOnMarket'),
            'price_per_sqft': data.get('summary', {}).get('pricePerSqft'),
            'inventory': data.get('summary', {}).get('inventory'),
            'sales_count': data.get('summary', {}).get('salesCount')
        }
        
        self._update_excel('market_trends', df_data)
    
    def store_owner_info(self, address: str, zipcode: str):
        """Store owner information in Excel"""
        data = self.attom.get_owner_info(address, zipcode)
        if not data:
            return
            
        df_data = {
            'address': address,
            'zipcode': zipcode,
            'last_updated': datetime.now(),
            'owner_name': data.get('owner', {}).get('name'),
            'ownership_length': data.get('owner', {}).get('lengthOfResidence'),
            'occupancy_status': data.get('owner', {}).get('occupancyStatus'),
            'mailing_address': data.get('owner', {}).get('mailingAddress'),
            'tax_delinquent': data.get('owner', {}).get('taxDelinquent'),
            'other_properties': len(data.get('owner', {}).get('otherProperties', []))
        }
        
        self._update_excel('owner_info', df_data)
    
    def store_lead_score(self, address: str, zipcode: str, score_data: Dict):
        """Store lead scoring data in Excel"""
        df_data = {
            'address': address,
            'zipcode': zipcode,
            'last_updated': datetime.now(),
            'total_score': score_data['total_score'],
            'financial_score': score_data['components']['financial_distress'],
            'time_pressure': score_data['components']['time_pressure'],
            'property_condition': score_data['components']['property_condition'],
            'market_position': score_data['components']['market_position'],
            'status': score_data['status'],
            'recommended_action': score_data['recommended_action'],
            'motivation_factors': '; '.join(score_data['motivation_factors'])
        }
        
        self._update_excel('lead_scores', df_data)
    
    def _update_excel(self, data_type: str, new_data: Dict):
        """Update Excel file with new data"""
        file_path = self.get_file_path(data_type)
        
        try:
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                
                # Update existing record or append new one
                if 'address' in new_data and new_data['address'] in df['address'].values:
                    idx = df[df['address'] == new_data['address']].index[0]
                    for key, value in new_data.items():
                        df.at[idx, key] = value
                else:
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])
            
            df.to_excel(file_path, index=False)
            logger.info(f"Successfully updated {data_type} data")
            
        except Exception as e:
            logger.error(f"Error updating Excel file: {str(e)}")
    
    def get_property_data(self, address: str, zipcode: str) -> Dict:
        """Get property data from Excel or ATTOM API"""
        if not self.is_data_fresh('property_details', address):
            self.store_property_details(address, zipcode)
        
        file_path = self.get_file_path('property_details')
        df = pd.read_excel(file_path)
        return df[df['address'] == address].to_dict('records')[0]
    
    def get_market_data(self, zipcode: str) -> Dict:
        """Get market data from Excel or ATTOM API"""
        if not self.is_data_fresh('market_trends', zipcode):
            self.store_market_trends(zipcode)
        
        file_path = self.get_file_path('market_trends')
        df = pd.read_excel(file_path)
        return df[df['zipcode'] == zipcode].to_dict('records')[0]
    
    def get_owner_data(self, address: str, zipcode: str) -> Dict:
        """Get owner data from Excel or ATTOM API"""
        if not self.is_data_fresh('owner_info', address):
            self.store_owner_info(address, zipcode)
        
        file_path = self.get_file_path('owner_info')
        df = pd.read_excel(file_path)
        return df[df['address'] == address].to_dict('records')[0]
    
    def get_lead_score(self, address: str, zipcode: str) -> Dict:
        """Get lead score from Excel"""
        file_path = self.get_file_path('lead_scores')
        if not os.path.exists(file_path):
            return None
            
        df = pd.read_excel(file_path)
        if address not in df['address'].values:
            return None
            
        return df[df['address'] == address].to_dict('records')[0]
