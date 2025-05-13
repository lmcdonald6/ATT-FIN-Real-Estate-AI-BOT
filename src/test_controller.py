import asyncio
from src.controllers.real_estate_controller import RealEstateController

async def main():
    controller = RealEstateController()
    zip_code = "60614"
    budget = 500000
    preferences = {}

    result = await controller.handle_property_query({
        "zip": zip_code,
        "budget": budget,
        "preferences": preferences
    })

    print("GPT Summary:", result["gpt_summary"]["summary"])
    print("Raw Data:", result["raw_analysis"])

if __name__ == "__main__":
    asyncio.run(main())
