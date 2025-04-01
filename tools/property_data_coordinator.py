import logging
from typing import Dict, List, Optional
from .redfin_data_tool import RedfinDataTool
from .attom_data_tool import AttomDataTool

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PropertyDataCoordinator:
    def __init__(self):
        """Initialize the property data coordinator"""
        self.redfin_tool = RedfinDataTool()
        self.attom_tool = AttomDataTool()
        
    async def get_enriched_properties(
        self, 
        zip_code: str, 
        property_type: str = None, 
        min_beds: int = None, 
        max_price: float = None,
        enrich_count: int = 5  # Only enrich top N properties with ATTOM data
    ) -> List[Dict]:
        """
        Get property data using a cost-efficient hybrid approach:
        1. First get basic property data from Redfin (free)
        2. Then enrich only the most relevant properties with ATTOM data (paid)
        """
        logger.info(f"Starting property search for ZIP: {zip_code}")
        
        try:
            # Step 1: Get initial property list from Redfin
            redfin_properties = await self.redfin_tool.get_property_details(
                zip_code=zip_code,
                property_type=property_type,
                min_beds=min_beds,
                max_price=max_price
            )
            
            if not redfin_properties:
                logger.warning("No properties found in Redfin")
                return []
                
            logger.info(f"Found {len(redfin_properties)} properties in Redfin")
            
            # Step 2: Select top N properties to enrich with ATTOM data
            properties_to_enrich = redfin_properties[:enrich_count]
            enriched_properties = []
            
            # Step 3: Enrich selected properties with ATTOM data
            for prop in properties_to_enrich:
                try:
                    # Get detailed ATTOM data for this property
                    attom_data = await self.attom_tool.get_property_details(
                        zip_code=prop['zip_code'],
                        property_type=prop['property_type'],
                        min_beds=prop.get('bedrooms'),
                        max_price=prop.get('price')
                    )
                    
                    if attom_data:
                        # Find matching property in ATTOM data
                        matching_attom_prop = next(
                            (p for p in attom_data 
                             if p['address'] == prop['address'] and 
                             p['zip_code'] == prop['zip_code']),
                            None
                        )
                        
                        if matching_attom_prop:
                            # Merge Redfin and ATTOM data, prioritizing ATTOM for overlapping fields
                            enriched_prop = {
                                **prop,  # Base Redfin data
                                'attom_data': {  # Additional ATTOM-specific data
                                    'tax_assessment': matching_attom_prop.get('tax_assessment'),
                                    'last_sale': matching_attom_prop.get('last_sale'),
                                    'lot_size': matching_attom_prop.get('lot_size'),
                                    'zoning': matching_attom_prop.get('zoning'),
                                    'parcel_id': matching_attom_prop.get('parcel_id')
                                },
                                'data_sources': ['redfin', 'attom']
                            }
                            enriched_properties.append(enriched_prop)
                        else:
                            # If no ATTOM match, use Redfin data only
                            prop['data_sources'] = ['redfin']
                            enriched_properties.append(prop)
                            
                except Exception as e:
                    logger.error(f"Error enriching property {prop['address']}: {str(e)}")
                    # Don't let one property failure stop the entire process
                    prop['data_sources'] = ['redfin']
                    enriched_properties.append(prop)
            
            # Step 4: Add remaining Redfin-only properties
            for prop in redfin_properties[enrich_count:]:
                prop['data_sources'] = ['redfin']
                enriched_properties.append(prop)
            
            return enriched_properties
            
        except Exception as e:
            logger.error(f"Error in property data coordination: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return []

# Global coordinator instance
_coordinator = None

async def run(zip_code: str, property_type: str = None, min_beds: int = None, max_price: float = None, enrich_count: int = 5) -> List[Dict]:
    """Run the property data coordinator"""
    global _coordinator
    
    if not zip_code:
        raise ValueError("ZIP code is required")
        
    _coordinator = PropertyDataCoordinator()
    
    try:
        properties = await _coordinator.get_enriched_properties(
            zip_code=zip_code,
            property_type=property_type,
            min_beds=min_beds,
            max_price=max_price,
            enrich_count=enrich_count
        )
        return properties
        
    except Exception as e:
        logger.error(f"Error running property coordinator: {str(e)}")
        return []
    finally:
        _coordinator = None

async def stop():
    """Stop the property data coordinator"""
    global _coordinator
    if _coordinator:
        _coordinator = None
