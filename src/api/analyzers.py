from fastapi import APIRouter, HTTPException
from typing import Dict, Optional

from ..analyzers.business_permits import BusinessPermitAnalyzer
from ..analyzers.demographics import DemographicAnalyzer
from ..analyzers.crime_stats import CrimeStatsAnalyzer
from ..analyzers.transit import TransitAnalyzer

router = APIRouter(prefix="/api/v1/analyze")

# Initialize analyzers
business_analyzer = BusinessPermitAnalyzer()
demographic_analyzer = DemographicAnalyzer()
crime_analyzer = CrimeStatsAnalyzer()
transit_analyzer = TransitAnalyzer()

@router.get("/area/{zipcode}")
async def analyze_area(
    zipcode: str,
    include_business: bool = True,
    include_demographics: bool = True,
    include_crime: bool = True,
    include_transit: bool = True
) -> Dict:
    """
    Comprehensive area analysis endpoint.
    """
    results = {}
    
    if include_business:
        results["business"] = {
            "recent_changes": await business_analyzer.get_recent_changes(zipcode),
            "density": await business_analyzer.analyze_business_density(zipcode),
            "growth_prediction": await business_analyzer.predict_business_growth(zipcode)
        }
    
    if include_demographics:
        results["demographics"] = {
            "migration": await demographic_analyzer.get_migration_patterns(zipcode),
            "population": await demographic_analyzer.analyze_population_trends(zipcode),
            "predictions": await demographic_analyzer.predict_demographic_changes(zipcode)
        }
    
    if include_crime:
        results["crime"] = {
            "trends": await crime_analyzer.get_trend_analysis(zipcode),
            "safety_score": await crime_analyzer.analyze_safety_score(zipcode),
            "predictions": await crime_analyzer.predict_safety_trends(zipcode)
        }
    
    if include_transit:
        results["transit"] = {
            "development": await transit_analyzer.get_development_plans(zipcode),
            "accessibility": await transit_analyzer.analyze_transit_score(zipcode),
            "predictions": await transit_analyzer.predict_transit_changes(zipcode)
        }
    
    return results

@router.get("/business/{zipcode}")
async def analyze_business(zipcode: str) -> Dict:
    """
    Business-focused analysis endpoint.
    """
    return {
        "recent_changes": await business_analyzer.get_recent_changes(zipcode),
        "density": await business_analyzer.analyze_business_density(zipcode),
        "growth_prediction": await business_analyzer.predict_business_growth(zipcode)
    }

@router.get("/demographics/{zipcode}")
async def analyze_demographics(zipcode: str) -> Dict:
    """
    Demographics-focused analysis endpoint.
    """
    return {
        "migration": await demographic_analyzer.get_migration_patterns(zipcode),
        "population": await demographic_analyzer.analyze_population_trends(zipcode),
        "predictions": await demographic_analyzer.predict_demographic_changes(zipcode)
    }

@router.get("/crime/{zipcode}")
async def analyze_crime(zipcode: str) -> Dict:
    """
    Crime and safety-focused analysis endpoint.
    """
    return {
        "trends": await crime_analyzer.get_trend_analysis(zipcode),
        "safety_score": await crime_analyzer.analyze_safety_score(zipcode),
        "predictions": await crime_analyzer.predict_safety_trends(zipcode)
    }

@router.get("/transit/{zipcode}")
async def analyze_transit(zipcode: str) -> Dict:
    """
    Transit-focused analysis endpoint.
    """
    return {
        "development": await transit_analyzer.get_development_plans(zipcode),
        "accessibility": await transit_analyzer.analyze_transit_score(zipcode),
        "predictions": await transit_analyzer.predict_transit_changes(zipcode)
    }
