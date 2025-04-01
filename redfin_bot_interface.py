from motivated_seller_finder import MotivatedSellerFinder
from typing import List, Dict
import logging
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Default ZIP codes for Nashville area
DEFAULT_ZIP_CODES = [
    '37013', '37027', '37072', '37115', '37138',  # Nashville suburbs
    '37201', '37203', '37204', '37205', '37206',  # Nashville core
    '37207', '37208', '37209', '37210', '37211',  # Nashville core
    '37212', '37214', '37215', '37216', '37217',  # Nashville core
    '37218', '37219', '37220', '37221'            # Nashville core
]

def load_zip_codes() -> List[str]:
    """Load ZIP codes from config file or use defaults"""
    config_file = 'data/zip_codes.json'
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return DEFAULT_ZIP_CODES
    except Exception as e:
        logger.error(f"Error loading ZIP codes: {str(e)}")
        return DEFAULT_ZIP_CODES

def save_zip_codes(zip_codes: List[str]):
    """Save ZIP codes to config file"""
    config_file = 'data/zip_codes.json'
    os.makedirs('data', exist_ok=True)
    try:
        with open(config_file, 'w') as f:
            json.dump(zip_codes, f)
        logger.info(f"Saved {len(zip_codes)} ZIP codes to config")
    except Exception as e:
        logger.error(f"Error saving ZIP codes: {str(e)}")

def add_zip_codes(new_zip_codes: List[str]) -> List[str]:
    """Add new ZIP codes to search"""
    current_zip_codes = load_zip_codes()
    # Add new unique ZIP codes
    updated_zip_codes = list(set(current_zip_codes + new_zip_codes))
    save_zip_codes(updated_zip_codes)
    return updated_zip_codes

def remove_zip_codes(zip_codes_to_remove: List[str]) -> List[str]:
    """Remove ZIP codes from search"""
    current_zip_codes = load_zip_codes()
    # Remove specified ZIP codes
    updated_zip_codes = [z for z in current_zip_codes if z not in zip_codes_to_remove]
    save_zip_codes(updated_zip_codes)
    return updated_zip_codes

def get_motivated_sellers(zip_codes: List[str] = None, max_retries: int = 3) -> List[Dict]:
    """
    Get motivated seller data from Redfin for multiple ZIP codes
    
    Args:
        zip_codes: List of ZIP codes to search. If None, uses saved/default ZIP codes
        max_retries: Maximum number of retry attempts if search fails
        
    Returns:
        List of dictionaries containing property data
    """
    if zip_codes is None:
        zip_codes = load_zip_codes()
        
    finder = MotivatedSellerFinder()
    all_properties = []
    
    for zip_code in zip_codes:
        try:
            logger.info(f"Searching ZIP code: {zip_code}")
            properties = finder.run(zip_code)
            if properties:
                all_properties.extend(properties)
                logger.info(f"Found {len(properties)} properties in {zip_code}")
            else:
                logger.info(f"No properties found in {zip_code}")
        except Exception as e:
            logger.error(f"Error searching {zip_code}: {str(e)}")
            continue
            
    return all_properties

def get_saved_properties() -> List[Dict]:
    """
    Get previously saved properties from CSV
    
    Returns:
        List of dictionaries containing property data
    """
    import pandas as pd
    import os
    
    csv_path = 'data/motivated_sellers.csv'
    if not os.path.exists(csv_path):
        return []
        
    df = pd.read_csv(csv_path)
    return df.to_dict('records')

# Example usage
if __name__ == "__main__":
    # Initialize with default Nashville ZIP codes
    zip_codes = load_zip_codes()
    logger.info(f"Searching {len(zip_codes)} ZIP codes: {', '.join(zip_codes)}")
    
    # Get properties from all ZIP codes
    properties = get_motivated_sellers()
    if properties:
        logger.info(f"Found total of {len(properties)} motivated sellers")
        # Show sample of properties
        for prop in properties[:3]:
            logger.info(f"Sample property: {prop['address']} - ${prop['price']:,}")
    else:
        logger.warning("No properties found")
