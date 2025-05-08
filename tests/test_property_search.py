import asyncio
import logging
from tools.property_data_coordinator import PropertyDataCoordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_hybrid_property_search():
    """Test the hybrid property search approach (Redfin + ATTOM)"""
    coordinator = PropertyDataCoordinator()
    
    # Test parameters
    zip_code = "37215"  # Green Hills/Forest Hills area
    property_type = "SFR"  # Single Family Residence
    min_beds = 4  # Larger homes
    max_price = 1500000  # Luxury segment
    enrich_count = 3  # Only get ATTOM data for top 3 properties
    
    logger.info("=== Testing Hybrid Property Search ===")
    logger.info(f"Searching in ZIP: {zip_code}")
    logger.info(f"Filters: {property_type}, {min_beds}+ beds, under ${max_price:,}")
    logger.info(f"Will enrich top {enrich_count} properties with ATTOM data")
    
    try:
        properties = await coordinator.get_enriched_properties(
            zip_code=zip_code,
            property_type=property_type,
            min_beds=min_beds,
            max_price=max_price,
            enrich_count=enrich_count
        )
        
        if properties:
            logger.info(f"\nFound {len(properties)} total properties")
            enriched_count = sum(1 for p in properties if 'attom' in p.get('data_sources', []))
            logger.info(f"Properties with ATTOM data: {enriched_count}")
            logger.info(f"Properties with Redfin data only: {len(properties) - enriched_count}")
            
            if len(properties) > 0:
                logger.info("\nSample Properties:")
                for i, prop in enumerate(properties[:5], 1):
                    logger.info(f"\nProperty {i}:")
                    logger.info(f"Address: {prop['address']}")
                    logger.info(f"City: {prop['city']}, {prop['state']} {prop['zip_code']}")
                    logger.info(f"Price: ${prop['price']:,}" if prop.get('price') else "Price: N/A")
                    logger.info(f"Beds: {prop['bedrooms']}")
                    logger.info(f"Square Feet: {prop['square_feet']}")
                    logger.info(f"Year Built: {prop['year_built']}")
                    logger.info(f"Data Sources: {', '.join(prop.get('data_sources', []))}")
                    
                    # Show additional ATTOM data if available
                    if 'attom_data' in prop:
                        logger.info("\nAdditional ATTOM Data:")
                        attom_data = prop['attom_data']
                        if attom_data.get('tax_assessment'):
                            logger.info(f"Tax Assessment: ${attom_data['tax_assessment']:,}")
                        if attom_data.get('lot_size'):
                            logger.info(f"Lot Size: {attom_data['lot_size']} acres")
                        if attom_data.get('zoning'):
                            logger.info(f"Zoning: {attom_data['zoning']}")
            else:
                logger.info("No properties found matching the criteria")
        else:
            logger.info("No response received from either data source")
        
    except Exception as e:
        logger.error(f"Search test failed: {str(e)}")
        logger.debug("Exception details:", exc_info=True)
    
    logger.info("\n=== Hybrid Property Search Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_hybrid_property_search())
