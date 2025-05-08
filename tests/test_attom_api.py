import requests
import json
import logging
from dotenv import load_dotenv
import os
from typing import Dict
import aiohttp
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealEstateDataAPI:
    def __init__(self):
        """Initialize ATTOM API client"""
        load_dotenv()
        self.api_key = os.getenv('ATTOM_API_KEY')
        self.base_url = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0'
        self.headers = {
            'apikey': self.api_key,
            'Accept': 'application/json'
        }

    def get_property_details(self, zipcode: str, property_type: str = None, min_beds: int = None, max_price: int = None):
        """Get property details from ATTOM"""
        endpoint = f"{self.base_url}/property/basicprofile"
        params = {
            'postalcode': zipcode,
            'pagesize': 10,
            'propertytype': property_type if property_type else 'SFR'
        }
        if min_beds:
            params['minbeds'] = min_beds
        if max_price:
            params['maxprice'] = max_price
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()

    def get_market_stats(self, zipcode: str):
        """Get market statistics from ATTOM"""
        endpoint = f"{self.base_url}/avm/snapshot"
        params = {
            'postalcode': zipcode
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()

    def get_foreclosure_data(self, zipcode: str):
        """Get foreclosure data from ATTOM"""
        endpoint = f"{self.base_url}/property/foreclosure"
        params = {
            'postalcode': zipcode
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json()

def display_property_analysis(property_data: Dict):
    """Display comprehensive property analysis with lead scoring"""
    print("\n" + "=" * 80)
    
    # Display property address
    address = property_data.get('address', {})
    print(f"Property: {address.get('oneLine', 'N/A')}")
    print("=" * 80 + "\n")
    
    # Display lead scores
    lead_score = property_data.get('lead_score', {})
    scores = lead_score.get('scores', {})
    print("LEAD SCORES")
    print("-" * 40)
    print(f"Total Score: {scores.get('total', 0):.1f}/100")
    print(f"Financial Distress: {scores.get('financial_distress', 0)}/100")
    print(f"Property Condition: {scores.get('property_condition', 0)}/100")
    print(f"Market Position: {scores.get('market_position', 0)}/100")
    print(f"Timing Factors: {scores.get('timing', 0)}/100\n")
    
    # Display basic information
    summary = property_data.get('summary', {})
    building = property_data.get('building', {})
    rooms = building.get('rooms', {})
    size = building.get('size', {})
    
    print("BASIC INFORMATION")
    print("-" * 40)
    print(f"Type: {summary.get('propertyType', 'N/A')}")
    print(f"Year Built: {summary.get('yearBuilt', 'N/A')}")
    print(f"Beds: {rooms.get('beds', 'N/A')}")
    print(f"Baths: {rooms.get('bathsTotal', 'N/A')}")
    print(f"Square Feet: {size.get('universalSize', 'N/A')}\n")
    
    # Display financial information
    assessment = property_data.get('assessment', {})
    tax = assessment.get('tax', {})
    assessed = assessment.get('assessed', {})
    avm = property_data.get('avm', {}).get('amount', {})
    
    print("FINANCIAL INFORMATION")
    print("-" * 40)
    print(f"Estimated Value: ${avm.get('value', 0):,.0f}")
    print(f"Tax Amount: ${tax.get('taxAmt', 0):,.0f}")
    print(f"Assessed Value: ${assessed.get('assdTtlValue', 0):,.0f}")
    print(f"Tax Delinquent: {tax.get('taxDelinquent', 'N')}\n")
    
    # Display analysis and insights
    insights = lead_score.get('insights', {})
    print("ANALYSIS & INSIGHTS")
    print("-" * 40)
    print(f"Summary: {insights.get('summary', 'N/A')}")
    print(f"Property Condition: {insights.get('property_condition', 'N/A')}")
    print(f"Financial Situation: {insights.get('financial_situation', 'N/A')}")
    print(f"Market Position: {insights.get('market_position', 'N/A')}")
    print(f"Timing Factors: {insights.get('timing', 'N/A')}\n")
    
    # Display recommendations
    print("RECOMMENDED ACTIONS")
    print("-" * 40)
    print(f"{insights.get('recommendation', 'No recommendations available')}\n")

def main():
    """Test ATTOM API integration with lead scoring"""
    api = RealEstateDataAPI()
    
    # Test property details with lead scoring
    logger.info("Testing property details with lead scoring...")
    zipcode = "37208"  # Example ZIP code in Nashville, TN
    
    response = api.get_property_details(zipcode)
    if 'property' in response:
        for prop in response['property']:
            display_property_analysis(prop)
    print(f"\nProperty Data Response:\n{json.dumps(response, indent=2)}")
    
    # Test market stats
    logger.info("\nTesting market stats...")
    market_stats = api.get_market_stats(zipcode)
    print(f"\nMarket Stats Response:\n{json.dumps(market_stats, indent=2)}")
    
    # Test foreclosure data
    logger.info("\nTesting foreclosure data...")
    foreclosure_data = api.get_foreclosure_data(zipcode)
    print(f"\nForeclosure Data Response:\n{json.dumps(foreclosure_data, indent=2)}")

async def test_attom_api():
    api_key = "e5bb16c669ddbe7c803b7779fba4acd7"
    base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
    
    # Test endpoints
    endpoints = [
        '/property/basicprofile',  # Basic property info
        '/property/address',       # Property by ZIP
        '/property/snapshot'       # Property snapshot
    ]
    
    headers = {
        'APIKey': api_key,
        'Accept': 'application/json'
    }
    
    params = {
        'postalcode': '37208',
        'pagesize': '1'
    }
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            logger.info(f"\nTesting endpoint: {url}")
            
            try:
                async with session.get(url, headers=headers, params=params, ssl=True) as response:
                    logger.info(f"Status: {response.status}")
                    logger.info(f"Headers: {dict(response.headers)}")
                    
                    text = await response.text()
                    logger.info(f"Response: {text[:500]}...")
                    
            except Exception as e:
                logger.error(f"Error testing {endpoint}: {str(e)}")

async def test_api_endpoints():
    """Test various ATTOM API endpoints to validate connectivity"""
    attom = RealEstateDataAPI()
    test_zip = "90210"  # Beverly Hills for testing
    
    logger.info("=== Starting ATTOM API Tests ===")
    
    try:
        # Test 1: Basic Property Search
        logger.info("\nTest 1: Basic Property Search")
        properties = await asyncio.to_thread(attom.get_property_details, test_zip)
        logger.info(f"Found {len(properties['property'])} properties in {test_zip}")
        if properties['property']:
            logger.info("Sample property data:")
            logger.info(properties['property'][0])
        
        # Test 2: Filtered Property Search
        logger.info("\nTest 2: Filtered Property Search")
        filtered_properties = await asyncio.to_thread(attom.get_property_details, test_zip)
        logger.info(f"Found {len(filtered_properties['property'])} properties matching filters")
        if filtered_properties['property']:
            logger.info("Sample filtered property:")
            logger.info(filtered_properties['property'][0])
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.debug("Exception details:", exc_info=True)
    
    logger.info("\n=== ATTOM API Tests Complete ===")

import asyncio
import logging
from tools.attom_data_tool import AttomDataTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_property_query():
    """Test a specific property query with filters"""
    attom = AttomDataTool()
    
    # Test parameters
    zip_code = "37215"  # Green Hills/Forest Hills area
    property_type = "SFR"  # Single Family Residence
    min_beds = 4  # Larger homes
    max_price = 1500000  # Luxury segment
    
    logger.info("=== Testing Property Query ===")
    logger.info(f"Searching in ZIP: {zip_code}")
    logger.info(f"Filters: {property_type}, {min_beds}+ beds, under ${max_price:,}")
    
    try:
        properties = await attom.get_property_details(
            zip_code=zip_code,
            property_type=property_type,
            min_beds=min_beds,
            max_price=max_price
        )
        
        if properties:
            logger.info(f"\nFound {len(properties)} matching properties")
            
            if len(properties) > 0:
                logger.info("\nSample Properties:")
                for i, prop in enumerate(properties[:5], 1):  # Show up to 5 properties
                    logger.info(f"\nProperty {i}:")
                    logger.info(f"Address: {prop['address']}")
                    logger.info(f"City: {prop['city']}, {prop['state']} {prop['zip_code']}")
                    if prop.get('price'):
                        logger.info(f"Price: ${prop['price']:,}")
                    logger.info(f"Beds: {prop['bedrooms']}")
                    logger.info(f"Square Feet: {prop['square_feet']}")
                    logger.info(f"Year Built: {prop['year_built']}")
                    
                    last_sale = prop.get('last_sale', {})
                    if last_sale and last_sale.get('price') and last_sale.get('date'):
                        logger.info(f"Last Sale: ${last_sale['price']:,} on {last_sale['date']}")
            else:
                logger.info("No properties found matching the criteria")
        else:
            logger.info("No response received from the API")
        
    except Exception as e:
        logger.error(f"Query test failed: {str(e)}")
        logger.debug("Exception details:", exc_info=True)
    
    logger.info("\n=== Property Query Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_property_query())
