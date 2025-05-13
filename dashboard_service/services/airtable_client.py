"""Airtable Client Service

This service provides functions to fetch data from Airtable for the dashboard.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add the parent directory to the path to import modules from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the airtable_sync module
from src.modules.airtable_sync import get_records, FIELD_MAPPINGS

# Load environment variables
load_dotenv()

def get_market_analysis_data():
    """Get market analysis data from Airtable.
    
    Returns:
        List of dictionaries containing market analysis records
    """
    try:
        # Get records from Airtable
        records = get_records(max_records=100)
        
        if not records:
            return []
        
        # Create a reverse mapping (Airtable field -> app field)
        reverse_mapping = {v: k for k, v in FIELD_MAPPINGS.items()}
        
        # Process records to ensure consistent field names
        processed_records = []
        for record in records:
            # Start with the record ID
            processed_record = {
                'id': record.get('id')
            }
            
            # Map Airtable field names back to application field names
            for field_name, field_value in record.items():
                if field_name == 'id':
                    continue
                    
                if field_name in reverse_mapping:
                    app_field_name = reverse_mapping[field_name]
                    processed_record[app_field_name] = field_value
                else:
                    processed_record[field_name] = field_value
            
            processed_records.append(processed_record)
        
        return processed_records
    except Exception as e:
        print(f"Error getting market analysis data: {str(e)}")
        return []

def get_market_analysis_dataframe():
    """Get market analysis data as a pandas DataFrame.
    
    Returns:
        DataFrame containing market analysis data
    """
    records = get_market_analysis_data()
    if not records:
        return pd.DataFrame()
    
    return pd.DataFrame(records)
