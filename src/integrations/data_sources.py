"""Data integration module for Redfin and ATTOM data sources."""
import pandas as pd
import requests
from typing import Dict, List, Optional
import openpyxl
from pathlib import Path

class DataSourceIntegrator:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.cache = {}
        
    def load_redfin_data(self, excel_path: str) -> pd.DataFrame:
        """Load Redfin data from Excel file."""
        try:
            df = pd.read_excel(excel_path)
            
            # Standardize column names
            column_mapping = {
                'Price': 'price',
                'Square Feet': 'sqft',
                'Beds': 'beds',
                'Baths': 'baths',
                'Location': 'address',
                'Zip': 'zip_code',
                'Year Built': 'year_built',
                'Days on Market': 'days_on_market',
                'Status': 'status'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Add calculated fields
            df['age'] = 2025 - df['year_built']
            df['price_per_sqft'] = df['price'] / df['sqft']
            
            return df
            
        except Exception as e:
            print(f"Error loading Redfin data: {e}")
            return pd.DataFrame()
    
    def load_attom_data(self, excel_path: str) -> pd.DataFrame:
        """Load ATTOM data from Excel file."""
        try:
            df = pd.read_excel(excel_path)
            
            # Standardize column names
            column_mapping = {
                'propertyId': 'property_id',
                'address': 'address',
                'zipCode': 'zip_code',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'lotSizeSquareFeet': 'lot_size',
                'yearBuilt': 'year_built',
                'lastSalePrice': 'last_sale_price',
                'lastSaleDate': 'last_sale_date'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Add calculated fields
            df['age'] = 2025 - df['year_built']
            
            return df
            
        except Exception as e:
            print(f"Error loading ATTOM data: {e}")
            return pd.DataFrame()
    
    def merge_data_sources(self,
                          redfin_data: pd.DataFrame,
                          attom_data: pd.DataFrame) -> pd.DataFrame:
        """Merge Redfin and ATTOM data based on address matching."""
        try:
            # Standardize addresses for matching
            redfin_data['address_clean'] = redfin_data['address'].str.lower().str.strip()
            attom_data['address_clean'] = attom_data['address'].str.lower().str.strip()
            
            # Merge datasets
            merged = pd.merge(
                redfin_data,
                attom_data,
                on='address_clean',
                how='left',
                suffixes=('', '_attom')
            )
            
            # Clean up duplicate columns
            for col in merged.columns:
                if col.endswith('_attom'):
                    base_col = col[:-6]
                    # Fill missing values from ATTOM data
                    merged[base_col] = merged[base_col].fillna(merged[col])
                    merged = merged.drop(columns=[col])
                    
            return merged.drop(columns=['address_clean'])
            
        except Exception as e:
            print(f"Error merging data sources: {e}")
            return pd.DataFrame()
    
    def load_market_data(self, market_excel_path: str) -> pd.DataFrame:
        """Load market analysis data from Excel file."""
        try:
            df = pd.read_excel(market_excel_path)
            
            # Standardize column names
            column_mapping = {
                'Date': 'period',
                'MedianPrice': 'median_price',
                'AvgDOM': 'avg_days_on_market',
                'ActiveListings': 'active_listings',
                'SoldListings': 'sold_listings',
                'MedianIncome': 'median_income',
                'SchoolRating': 'school_rating',
                'CrimeRate': 'crime_rate'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Convert date to datetime
            df['period'] = pd.to_datetime(df['period'])
            
            return df
            
        except Exception as e:
            print(f"Error loading market data: {e}")
            return pd.DataFrame()
    
    def export_to_excel(self,
                       data: pd.DataFrame,
                       output_path: str,
                       sheet_name: str = 'Analysis') -> None:
        """Export analysis results to Excel file."""
        try:
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write data
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(data.columns):
                    max_length = max(
                        data[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[
                        openpyxl.utils.get_column_letter(idx + 1)
                    ].width = max_length + 2
                    
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
    
    def validate_data(self, df: pd.DataFrame, source: str) -> List[str]:
        """Validate data quality and completeness."""
        issues = []
        
        # Check for missing values
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                issues.append(f"{source}: {count} missing values in {col}")
                
        # Check for data types
        if source == 'redfin':
            if not pd.api.types.is_numeric_dtype(df['price']):
                issues.append(f"{source}: Price column is not numeric")
            if not pd.api.types.is_numeric_dtype(df['sqft']):
                issues.append(f"{source}: Square Feet column is not numeric")
                
        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"{source}: Found {duplicates} duplicate records")
            
        return issues
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data."""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Fill numeric missing values with median
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
            
        # Fill categorical missing values with mode
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0])
            
        # Remove outliers (optional)
        if self.config.get('remove_outliers', False):
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                df = df[
                    (df[col] >= Q1 - 1.5 * IQR) &
                    (df[col] <= Q3 + 1.5 * IQR)
                ]
                
        return df
