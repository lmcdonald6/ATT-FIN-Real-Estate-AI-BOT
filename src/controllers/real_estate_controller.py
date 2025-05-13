import logging
from src.modules.data_sources import (
    get_property_data,
    get_crime_score,
    get_permit_activity,
    get_zoning_data,
    get_rent_vs_value_score,
    get_market_trend_score
)
from src.modules.gpt_reporter import generate_summary

class RealEstateController:
    def __init__(self):
        logging.info("Controller initialized")

    async def handle_property_query(self, query: dict) -> dict:
        try:
            zip_code = query.get('zip')
            if not zip_code:
                raise ValueError("ZIP code is required")
                
            budget = query.get('budget')
            if not budget or budget <= 0:
                raise ValueError("Valid budget is required")
                
            preferences = query.get('preferences', {})

            results = await self.analyze_neighborhood_potential(zip_code, budget, preferences)
            summary = generate_summary(results)

            return {
                "raw_analysis": results,
                "gpt_summary": summary
            }
        except Exception as e:
            logging.error(f"Property analysis failed: {str(e)}")
            raise

    async def analyze_neighborhood_potential(self, zip_code: str, budget: float, preferences: dict) -> dict:
        property_data = await get_property_data(zip_code)
        crime = await get_crime_score(zip_code)
        permits = await get_permit_activity(zip_code)
        zoning = await get_zoning_data(zip_code)
        rent_value = await get_rent_vs_value_score(zip_code)
        trend = await get_market_trend_score(zip_code)

        return {
            "property_data": property_data,
            "crime_score": crime,
            "permit_activity": permits,
            "zoning_info": zoning,
            "rent_vs_value": rent_value,
            "market_trend": trend
        }
