"""Advanced validation rules for market analysis data."""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class MarketDataValidator:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
    def validate_market_trends(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate market trend data for anomalies and consistency."""
        errors = []
        
        # Check for price outliers
        price_outliers = self._detect_outliers(data['MedianPrice'])
        if len(price_outliers) > 0:
            errors.append({
                'error': 'price_outliers',
                'rows': price_outliers,
                'message': f"Found {len(price_outliers)} outlier prices that need review"
            })
            
        # Check for unrealistic price changes
        price_changes = data['MedianPrice'].pct_change()
        large_changes = data[abs(price_changes) > 0.2].index.tolist()
        if large_changes:
            errors.append({
                'error': 'large_price_changes',
                'rows': large_changes,
                'message': "Found sudden price changes > 20%"
            })
            
        # Validate inventory trends
        inventory_changes = data['ActiveListings'].pct_change()
        large_inventory_changes = data[abs(inventory_changes) > 0.5].index.tolist()
        if large_inventory_changes:
            errors.append({
                'error': 'inventory_anomaly',
                'rows': large_inventory_changes,
                'message': "Found sudden inventory changes > 50%"
            })
            
        return errors
    
    def validate_property_data(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate property data for consistency and completeness."""
        errors = []
        
        # Check price per square foot
        if 'price' in data.columns and 'sqft' in data.columns:
            price_per_sqft = data['price'] / data['sqft']
            sqft_outliers = self._detect_outliers(price_per_sqft)
            if len(sqft_outliers) > 0:
                errors.append({
                    'error': 'price_per_sqft_outliers',
                    'rows': sqft_outliers,
                    'message': f"Found {len(sqft_outliers)} unusual price/sqft values"
                })
                
        # Validate property features
        if 'beds' in data.columns and 'sqft' in data.columns:
            # Check for unrealistic bed/sqft ratios
            sqft_per_bed = data['sqft'] / data['beds']
            unrealistic_space = data[sqft_per_bed < 200].index.tolist()
            if unrealistic_space:
                errors.append({
                    'error': 'unrealistic_space',
                    'rows': unrealistic_space,
                    'message': "Found properties with less than 200 sqft per bedroom"
                })
                
        # Check for duplicate listings
        duplicates = self._find_potential_duplicates(data)
        if duplicates:
            errors.append({
                'error': 'potential_duplicates',
                'rows': duplicates,
                'message': "Found potentially duplicate property listings"
            })
            
        return errors
    
    def validate_investment_metrics(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate investment-related metrics."""
        errors = []
        
        if all(col in data.columns for col in ['price', 'rent_estimate']):
            # Calculate gross rent multiplier
            grm = data['price'] / (data['rent_estimate'] * 12)
            unrealistic_grm = data[
                (grm < 5) | (grm > 30)
            ].index.tolist()
            
            if unrealistic_grm:
                errors.append({
                    'error': 'unrealistic_grm',
                    'rows': unrealistic_grm,
                    'message': "Found unusual Gross Rent Multiplier values"
                })
                
        if 'cap_rate' in data.columns:
            # Validate cap rates
            unrealistic_cap = data[
                (data['cap_rate'] < 0.02) | (data['cap_rate'] > 0.2)
            ].index.tolist()
            
            if unrealistic_cap:
                errors.append({
                    'error': 'unrealistic_cap_rate',
                    'rows': unrealistic_cap,
                    'message': "Found unusual Capitalization Rate values"
                })
                
        return errors
    
    def validate_location_data(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate location-related data."""
        errors = []
        
        if all(col in data.columns for col in ['latitude', 'longitude']):
            # Check for invalid coordinates
            invalid_coords = data[
                (data['latitude'].abs() > 90) |
                (data['longitude'].abs() > 180)
            ].index.tolist()
            
            if invalid_coords:
                errors.append({
                    'error': 'invalid_coordinates',
                    'rows': invalid_coords,
                    'message': "Found invalid GPS coordinates"
                })
                
        if 'zip_code' in data.columns:
            # Validate ZIP code format
            invalid_zips = data[
                ~data['zip_code'].astype(str).str.match(r'^\d{5}(-\d{4})?$')
            ].index.tolist()
            
            if invalid_zips:
                errors.append({
                    'error': 'invalid_zip',
                    'rows': invalid_zips,
                    'message': "Found invalid ZIP code format"
                })
                
        return errors
    
    def validate_time_series(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate time series data for completeness and consistency."""
        errors = []
        
        if 'date' in data.columns:
            # Check for missing dates
            date_range = pd.date_range(
                start=data['date'].min(),
                end=data['date'].max(),
                freq='D'
            )
            missing_dates = date_range.difference(data['date'])
            
            if len(missing_dates) > 0:
                errors.append({
                    'error': 'missing_dates',
                    'dates': missing_dates.tolist(),
                    'message': f"Found {len(missing_dates)} missing dates in time series"
                })
                
            # Check for duplicate dates
            duplicate_dates = data[data['date'].duplicated()]['date'].tolist()
            if duplicate_dates:
                errors.append({
                    'error': 'duplicate_dates',
                    'dates': duplicate_dates,
                    'message': "Found duplicate date entries"
                })
                
        return errors
    
    def _detect_outliers(self, series: pd.Series) -> List[int]:
        """Detect outliers using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = series[
            (series < (Q1 - 1.5 * IQR)) |
            (series > (Q3 + 1.5 * IQR))
        ].index.tolist()
        
        return outliers
    
    def _find_potential_duplicates(self, data: pd.DataFrame) -> List[int]:
        """Find potentially duplicate property listings."""
        # Create a composite key for comparison
        if all(col in data.columns for col in ['sqft', 'beds', 'baths', 'zip_code']):
            composite_key = data.apply(
                lambda x: f"{x['sqft']}_{x['beds']}_{x['baths']}_{x['zip_code']}",
                axis=1
            )
            
            duplicates = data[composite_key.duplicated()].index.tolist()
            return duplicates
            
        return []
    
    def validate_all(self, data: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Run all validation checks."""
        return {
            'market_trends': self.validate_market_trends(data),
            'property_data': self.validate_property_data(data),
            'investment_metrics': self.validate_investment_metrics(data),
            'location_data': self.validate_location_data(data),
            'time_series': self.validate_time_series(data)
        }
