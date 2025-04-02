"""Data schemas and validation rules for market analysis data."""
from typing import Dict, List, Any, Callable
import re
from datetime import datetime

# Validation functions
def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, str(phone)))

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))

def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(str(date_str), '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
    return bool(re.match(pattern, str(url)))

def validate_address(address: str) -> bool:
    """Validate address format."""
    return bool(re.match(r'^[A-Za-z0-9\s,.-]+$', str(address)))

# Enhanced validation rules
VALIDATION_RULES = {
    'price_rules': {
        'min_value': 1000,
        'max_value': 100000000,
        'validator': lambda x: isinstance(x, (int, float)) and 1000 <= x <= 100000000
    },
    'sqft_rules': {
        'min_value': 100,
        'max_value': 100000,
        'validator': lambda x: isinstance(x, (int, float)) and 100 <= x <= 100000
    },
    'year_rules': {
        'min_value': 1800,
        'max_value': datetime.now().year,
        'validator': lambda x: isinstance(x, (int)) and 1800 <= x <= datetime.now().year
    },
    'coordinate_rules': {
        'lat_range': (-90, 90),
        'lon_range': (-180, 180),
        'validator': lambda x, is_lat: isinstance(x, (int, float)) and 
                                     ((-90 <= x <= 90) if is_lat else (-180 <= x <= 180))
    }
}

# Enhanced schema definitions
REDFIN_SCHEMA = {
    'required_columns': {
        'Price': {
            'type': float,
            'validator': VALIDATION_RULES['price_rules']['validator'],
            'error_msg': 'Price must be between $1,000 and $100,000,000'
        },
        'Square Feet': {
            'type': float,
            'validator': VALIDATION_RULES['sqft_rules']['validator'],
            'error_msg': 'Square footage must be between 100 and 100,000'
        },
        'Beds': {
            'type': int,
            'validator': lambda x: isinstance(x, int) and 0 <= x <= 20,
            'error_msg': 'Bedrooms must be between 0 and 20'
        },
        'Baths': {
            'type': float,
            'validator': lambda x: isinstance(x, (int, float)) and 0 <= x <= 20,
            'error_msg': 'Bathrooms must be between 0 and 20'
        },
        'Location': {
            'type': str,
            'validator': validate_address,
            'error_msg': 'Invalid address format'
        },
        'Zip': {
            'type': str,
            'validator': lambda x: bool(re.match(r'^\d{5}(-\d{4})?$', str(x))),
            'error_msg': 'Invalid ZIP code format (12345 or 12345-6789)'
        },
        'Year Built': {
            'type': int,
            'validator': VALIDATION_RULES['year_rules']['validator'],
            'error_msg': f'Year must be between 1800 and {datetime.now().year}'
        },
        'Days on Market': {
            'type': int,
            'validator': lambda x: isinstance(x, int) and x >= 0,
            'error_msg': 'Days on Market must be non-negative'
        },
        'Status': {
            'type': str,
            'validator': lambda x: str(x).lower() in ['active', 'pending', 'sold', 'off market'],
            'error_msg': 'Status must be: Active, Pending, Sold, or Off Market'
        }
    },
    'optional_columns': {
        'Lot Size': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x > 0),
            'error_msg': 'Lot Size must be positive'
        },
        'Last Sale Date': {
            'type': str,
            'validator': lambda x: x is None or validate_date(x),
            'error_msg': 'Invalid date format (YYYY-MM-DD)'
        },
        'Last Sale Price': {
            'type': float,
            'validator': lambda x: x is None or VALIDATION_RULES['price_rules']['validator'](x),
            'error_msg': 'Last Sale Price must be between $1,000 and $100,000,000'
        },
        'Property Type': {
            'type': str,
            'validator': lambda x: x is None or str(x).lower() in [
                'single family', 'multi family', 'condo', 'townhouse', 'land', 'other'
            ],
            'error_msg': 'Invalid Property Type'
        },
        'HOA': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
            'error_msg': 'HOA fees must be non-negative'
        },
        'School District': {
            'type': str,
            'validator': lambda x: x is None or isinstance(x, str),
            'error_msg': 'Invalid School District'
        }
    }
}

ATTOM_SCHEMA = {
    'required_columns': {
        'propertyId': {
            'type': str,
            'validator': lambda x: bool(x),
            'error_msg': 'Property ID is required'
        },
        'address': {
            'type': str,
            'validator': validate_address,
            'error_msg': 'Invalid address format'
        },
        'zipCode': {
            'type': str,
            'validator': lambda x: bool(re.match(r'^\d{5}(-\d{4})?$', str(x))),
            'error_msg': 'Invalid ZIP code format'
        },
        'latitude': {
            'type': float,
            'validator': lambda x: VALIDATION_RULES['coordinate_rules']['validator'](x, True),
            'error_msg': 'Invalid latitude (-90 to 90)'
        },
        'longitude': {
            'type': float,
            'validator': lambda x: VALIDATION_RULES['coordinate_rules']['validator'](x, False),
            'error_msg': 'Invalid longitude (-180 to 180)'
        },
        'yearBuilt': {
            'type': int,
            'validator': VALIDATION_RULES['year_rules']['validator'],
            'error_msg': f'Year must be between 1800 and {datetime.now().year}'
        }
    },
    'optional_columns': {
        'lotSizeSquareFeet': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x > 0),
            'error_msg': 'Lot size must be positive'
        },
        'lastSalePrice': {
            'type': float,
            'validator': lambda x: x is None or VALIDATION_RULES['price_rules']['validator'](x),
            'error_msg': 'Invalid sale price range'
        },
        'lastSaleDate': {
            'type': str,
            'validator': lambda x: x is None or validate_date(x),
            'error_msg': 'Invalid date format (YYYY-MM-DD)'
        },
        'zoning': {
            'type': str,
            'validator': lambda x: x is None or isinstance(x, str),
            'error_msg': 'Invalid zoning information'
        },
        'taxAssessment': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
            'error_msg': 'Tax assessment must be non-negative'
        },
        'floodZone': {
            'type': str,
            'validator': lambda x: x is None or str(x).upper() in ['A', 'AE', 'X', 'OTHER'],
            'error_msg': 'Invalid flood zone designation'
        }
    }
}

MARKET_DATA_SCHEMA = {
    'required_columns': {
        'Date': {
            'type': str,
            'validator': validate_date,
            'error_msg': 'Invalid date format (YYYY-MM-DD)'
        },
        'MedianPrice': {
            'type': float,
            'validator': VALIDATION_RULES['price_rules']['validator'],
            'error_msg': 'Invalid median price range'
        },
        'AvgDOM': {
            'type': float,
            'validator': lambda x: isinstance(x, (int, float)) and x >= 0,
            'error_msg': 'Average Days on Market must be non-negative'
        },
        'ActiveListings': {
            'type': int,
            'validator': lambda x: isinstance(x, int) and x >= 0,
            'error_msg': 'Active listings must be non-negative'
        },
        'SoldListings': {
            'type': int,
            'validator': lambda x: isinstance(x, int) and x >= 0,
            'error_msg': 'Sold listings must be non-negative'
        }
    },
    'optional_columns': {
        'MedianIncome': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
            'error_msg': 'Median income must be non-negative'
        },
        'SchoolRating': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and 0 <= x <= 10),
            'error_msg': 'School rating must be between 0 and 10'
        },
        'CrimeRate': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
            'error_msg': 'Crime rate must be non-negative'
        },
        'PricePerSqFt': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x > 0),
            'error_msg': 'Price per square foot must be positive'
        },
        'InventoryMonths': {
            'type': float,
            'validator': lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
            'error_msg': 'Inventory months must be non-negative'
        },
        'MarketType': {
            'type': str,
            'validator': lambda x: x is None or str(x).lower() in [
                'buyer\'s market', 'seller\'s market', 'balanced'
            ],
            'error_msg': 'Invalid market type'
        }
    }
}

# Template definitions for Excel files
EXCEL_TEMPLATES = {
    'redfin': {
        'sheet_name': 'Redfin Data',
        'columns': list(REDFIN_SCHEMA['required_columns'].keys()) + 
                  list(REDFIN_SCHEMA['optional_columns'].keys()),
        'sample_data': [
            {
                'Price': 300000,
                'Square Feet': 1500,
                'Beds': 3,
                'Baths': 2,
                'Location': '123 Main St',
                'Zip': '12345',
                'Year Built': 2000,
                'Days on Market': 30,
                'Status': 'Active'
            }
        ]
    },
    'attom': {
        'sheet_name': 'ATTOM Data',
        'columns': list(ATTOM_SCHEMA['required_columns'].keys()) + 
                  list(ATTOM_SCHEMA['optional_columns'].keys()),
        'sample_data': [
            {
                'propertyId': 'ABC123',
                'address': '123 Main St',
                'zipCode': '12345',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'yearBuilt': 2000
            }
        ]
    },
    'market': {
        'sheet_name': 'Market Data',
        'columns': list(MARKET_DATA_SCHEMA['required_columns'].keys()) + 
                  list(MARKET_DATA_SCHEMA['optional_columns'].keys()),
        'sample_data': [
            {
                'Date': '2025-01-01',
                'MedianPrice': 350000,
                'AvgDOM': 45,
                'ActiveListings': 100,
                'SoldListings': 50
            }
        ]
    }
}

def validate_schema(data: Dict, schema_type: str) -> List[Dict[str, Any]]:
    """Validate data against schema with detailed error reporting."""
    errors = []
    schema = globals().get(f'{schema_type.upper()}_SCHEMA')
    
    if not schema:
        return [{'error': 'schema_error', 'message': f"Invalid schema type: {schema_type}"}]
        
    # Check required columns
    for col, specs in schema['required_columns'].items():
        if col not in data.columns:
            errors.append({
                'error': 'missing_column',
                'column': col,
                'message': f"Missing required column: {col}"
            })
        else:
            # Check data type
            try:
                data[col].astype(specs['type'])
            except:
                errors.append({
                    'error': 'type_error',
                    'column': col,
                    'message': f"Invalid data type for {col}. Expected {specs['type'].__name__}"
                })
            
            # Apply validation rules
            invalid_mask = ~data[col].apply(specs['validator'])
            invalid_rows = data[invalid_mask].index.tolist()
            if invalid_rows:
                errors.append({
                    'error': 'validation_error',
                    'column': col,
                    'rows': invalid_rows,
                    'message': f"{specs['error_msg']} (Rows: {invalid_rows})"
                })
                
    # Check optional columns
    for col, specs in schema['optional_columns'].items():
        if col in data.columns:
            # Check data type for non-null values
            non_null = data[col].dropna()
            try:
                non_null.astype(specs['type'])
            except:
                errors.append({
                    'error': 'type_error',
                    'column': col,
                    'message': f"Invalid data type for {col}. Expected {specs['type'].__name__}"
                })
            
            # Apply validation rules
            invalid_mask = ~data[col].apply(lambda x: x is None or specs['validator'](x))
            invalid_rows = data[invalid_mask].index.tolist()
            if invalid_rows:
                errors.append({
                    'error': 'validation_error',
                    'column': col,
                    'rows': invalid_rows,
                    'message': f"{specs['error_msg']} (Rows: {invalid_rows})"
                })
                
    return errors
