"""Airtable Integration Code

This file contains the code for integrating with Airtable.
You can copy and paste these sections into your airtable_sync.py module.
"""

# ----- FIELD MAPPINGS -----
# Add this to the top of your airtable_sync.py file, after the imports

# Field mappings for Airtable
# These map your application field names to Airtable field names
FIELD_MAPPINGS = {
    "Region": "Region",
    "Final Score": "Score",
    "Market Phase": "Phase",
    "Risk Level": "Risk",
    "Trend Score": "TrendScore",
    "Economic Score": "EconomicScore",
    "PTR Ratio": "PTRRatio",
    "Cap Rate": "CapRate",
    "Monthly Sales": "MonthlySales",
    "Inventory Level": "Inventory",
    "Avg Appreciation": "AvgAppreciation",
    "Property Value": "PropertyValue",
    "Monthly Rent": "MonthlyRent",
    "Annual Income": "AnnualIncome",
    "Timestamp": "Notes",  # We'll use Notes to store timestamp if needed
}

# ----- MAP FIELDS FUNCTION -----
# Add this function to your airtable_sync.py file

def map_fields(record_data):
    """Map field names from application to Airtable field names."""
    mapped_data = {}
    for key, value in record_data.items():
        if key in FIELD_MAPPINGS:
            mapped_key = FIELD_MAPPINGS[key]
            mapped_data[mapped_key] = value
        else:
            # Keep fields that don't have a mapping
            mapped_data[key] = value
    
    return mapped_data

# ----- UPDATED SYNC_RECORD FUNCTION -----
# Replace your existing sync_record function with this one

def sync_record(record_data):
    """Sync a record with Airtable.
    
    This function will create a new record in Airtable with the provided data.
    
    Args:
        record_data: Dictionary containing the record data to be synced
        
    Returns:
        Dictionary containing the Airtable API response
    """
    if not USE_AIRTABLE:
        logger.warning("Airtable integration is disabled. Set USE_AIRTABLE=true in .env to enable.")
        return {"status": "skipped", "message": "Airtable integration is disabled"}
    
    if not API_KEY or not BASE_ID or not TABLE_IDENTIFIER:
        logger.error("Missing Airtable configuration. Check your .env file.")
        return {"status": "error", "message": "Missing Airtable configuration"}
    
    # Add timestamp to record
    record_data["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Map field names to Airtable field names
    mapped_record_data = map_fields(record_data)
    
    # Prepare data for Airtable API
    payload = {
        "fields": mapped_record_data
    }
    
    logger.info(f"Syncing record to Airtable: {record_data.get('Region', 'Unknown region')}")
    logger.debug(f"Record data: {json.dumps(mapped_record_data, indent=2)}")
    
    try:
        # Create a new record
        logger.debug(f"POST request to {BASE_URL}")
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        
        # Log response details
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        
        # Handle different status codes
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Successfully synced record to Airtable")
            return response.json()
        else:
            # Try to get error details from response
            try:
                error_data = response.json()
                logger.error(f"Error syncing record to Airtable: {error_data}")
                return {"status": "error", "message": str(error_data)}
            except ValueError:
                logger.error(f"Error syncing record to Airtable: {response.text}")
                return {"status": "error", "message": response.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception syncing record to Airtable: {str(e)}")
        
        # Try to get more details from the exception
        error_details = {}
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = {"text": e.response.text[:200]}
        
        return {"status": "error", "message": str(e), "details": error_details}

# ----- INSTRUCTIONS FOR AIRTABLE SETUP -----
"""
Airtable Setup Instructions:

1. In your Airtable base, add the following fields to the Market Analysis table:
   - Region (Single line text)
   - Score (Number)
   - Phase (Single line text)
   - Risk (Single line text)
   - TrendScore (Number)
   - EconomicScore (Number)
   - PTRRatio (Number)
   - CapRate (Number)
   - MonthlySales (Number)
   - Inventory (Single line text)
   - AvgAppreciation (Number)
   - PropertyValue (Number)
   - MonthlyRent (Number)
   - AnnualIncome (Number)
   - Notes (Long text)

2. Update your .env file with the following variables:
   AIRTABLE_API_KEY=your_api_key
   AIRTABLE_BASE_ID=app0TO0hhThd6Qzym
   AIRTABLE_TABLE_ID=tbl9U6zb4wv6SVNs0
   USE_AIRTABLE=true

3. Copy and paste the code sections above into your airtable_sync.py module.

4. Test the integration by running a simple test script.
"""
