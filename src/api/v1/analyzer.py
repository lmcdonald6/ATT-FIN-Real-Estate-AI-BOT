from fastapi import APIRouter, HTTPException
from src.controllers.real_estate_controller import RealEstateController
from src.models.schemas import PropertyAnalysisRequest

router = APIRouter(prefix="/api/v1/analyze", tags=["analyzers"])
controller = RealEstateController()

@router.post("/property", 
    response_model=dict,
    summary="Analyze property investment potential",
    description="""Analyzes a property's investment potential based on location, budget, and preferences.
    
    Examples:
    ```python
    # Basic request
    {
        "zip": "60614",
        "budget": 500000,
        "preferences": {}
    }
    
    # Request with preferences
    {
        "zip": "60614",
        "budget": 500000,
        "preferences": {
            "property_type": "single_family",
            "min_bedrooms": 3,
            "max_price": 600000
        }
    }
    ```
    """)
async def analyze_property(query: PropertyAnalysisRequest):
    try:
        result = await controller.handle_property_query(query.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
