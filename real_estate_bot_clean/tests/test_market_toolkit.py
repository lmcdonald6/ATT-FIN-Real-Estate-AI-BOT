"""
Test suite for MarketToolkit.
Tests both core functionality and seasonality features.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from src.analysis.market_toolkit import MarketToolkit

@pytest.fixture
def market_toolkit():
    """Create MarketToolkit instance for testing."""
    return MarketToolkit()

@pytest.fixture
def mock_properties():
    """Create mock property data for testing."""
    return [
        {
            "id": "37215_1",
            "address": "123 Test St",
            "zip_code": "37215",
            "price": 800000,
            "sqft": 3000,
            "property_type": "Single Family",
            "bedrooms": 4,
            "bathrooms": 3,
            "year_built": 2000,
            "days_on_market": 30,
            "status": "For Sale",
            "date": "2024-03-15"
        },
        {
            "id": "37215_2",
            "address": "456 Test Ave",
            "zip_code": "37215",
            "price": 1200000,
            "sqft": 4500,
            "property_type": "Single Family",
            "bedrooms": 5,
            "bathrooms": 4,
            "year_built": 2010,
            "days_on_market": 15,
            "status": "Just Listed",
            "date": "2024-03-15"
        }
    ]

@pytest.fixture
def mock_historical_data():
    """Create mock historical data for seasonality testing."""
    data = []
    base_price = 800000
    
    for year in [2023, 2024]:
        for month in range(1, 13):
            # Add seasonal variations
            if month in [3, 4, 5]:  # Spring
                seasonal_factor = 1.08
            elif month in [6, 7, 8]:  # Summer
                seasonal_factor = 1.05
            elif month in [9, 10, 11]:  # Fall
                seasonal_factor = 0.98
            else:  # Winter
                seasonal_factor = 0.95
            
            price = base_price * seasonal_factor
            
            data.append({
                "date": f"{year}-{month:02d}-15",
                "price": price,
                "zip_code": "37215"
            })
    
    return data

def test_analyze_market_basic(market_toolkit, mock_properties):
    """Test basic market analysis functionality."""
    result = market_toolkit.analyze_market("37215", mock_properties)
    
    assert result is not None
    assert "price_analysis" in result
    assert "market_analysis" in result
    assert "trend_analysis" in result
    assert "opportunity_score" in result
    
    # Check price analysis
    price_analysis = result["price_analysis"]
    assert "median_price" in price_analysis
    assert price_analysis["median_price"] == 1000000
    
    # Check market analysis
    market_analysis = result["market_analysis"]
    assert "market_strength" in market_analysis
    assert "growth_rate" in market_analysis
    assert 0 <= market_analysis["market_strength"] <= 1

def test_analyze_seasonality(market_toolkit, mock_historical_data):
    """Test seasonality analysis."""
    result = market_toolkit.analyze_seasonality(
        "37215",
        mock_historical_data
    )
    
    assert result is not None
    assert "current_season_impact" in result
    assert "seasonal_factors" in result
    assert "peak_months" in result
    assert "slow_months" in result
    
    # Check seasonal patterns
    assert len(result["peak_months"]) > 0
    assert len(result["slow_months"]) > 0
    
    # Verify spring boost
    spring_boost = result["price_adjustments"]["spring"]
    assert spring_boost > 0
    assert spring_boost == pytest.approx(0.08)  # Belle Meade spring boost

def test_predict_property_values(market_toolkit, mock_properties):
    """Test property value predictions with seasonal adjustments."""
    market_data = market_toolkit.analyze_market(
        "37215",
        mock_properties
    )
    
    predictions = market_toolkit.predict_property_values(
        mock_properties,
        market_data["market_analysis"]
    )
    
    assert len(predictions) == len(mock_properties)
    
    for pred in predictions:
        assert "predicted_price" in pred
        assert "confidence_score" in pred
        assert "seasonal_adjustment" in pred
        assert "seasonal_price_delta" in pred
        
        # Check value ranges
        assert pred["predicted_price"] > 0
        assert 0 <= pred["confidence_score"] <= 1
        assert -0.1 <= pred["seasonal_adjustment"] <= 0.1

def test_market_phase_detection(market_toolkit, mock_properties):
    """Test market phase detection."""
    result = market_toolkit.analyze_market("37215", mock_properties)
    
    assert "market_analysis" in result
    assert "current_market_phase" in result["market_analysis"]
    
    phase = result["market_analysis"]["current_market_phase"]
    assert phase in [
        "Strong Growth Phase",
        "Moderate Growth Phase",
        "Significant Slowdown",
        "Moderate Slowdown",
        "Stable Phase"
    ]

def test_empty_data_handling(market_toolkit):
    """Test handling of empty data."""
    result = market_toolkit.analyze_market("37215", [])
    
    assert result is not None
    assert result["price_analysis"] == {}
    assert result["market_analysis"] == {}
    assert result["trend_analysis"] == {}
    assert result["opportunity_score"] == 0.5

def test_invalid_zip_code(market_toolkit, mock_properties):
    """Test handling of invalid ZIP code."""
    result = market_toolkit.analyze_market("00000", mock_properties)
    
    assert result is not None
    assert "market_analysis" in result
    
    # Should use default market characteristics
    market = result["market_analysis"]
    assert market["market_strength"] == 0.6
    assert market["growth_rate"] == 0.05

def test_seasonal_impact_calculation(market_toolkit):
    """Test seasonal impact calculations."""
    patterns = market_toolkit.seasonal_patterns["37215"]
    
    # Test spring (April)
    impact = market_toolkit._calculate_season_impact(4, patterns)
    assert impact == patterns["spring_boost"]
    
    # Test summer (July)
    impact = market_toolkit._calculate_season_impact(7, patterns)
    assert impact == patterns["summer_boost"]
    
    # Test fall (October)
    impact = market_toolkit._calculate_season_impact(10, patterns)
    assert impact == patterns["fall_boost"]
    
    # Test winter (January)
    impact = market_toolkit._calculate_season_impact(1, patterns)
    assert impact == patterns["winter_boost"]

def test_market_momentum(market_toolkit, mock_properties):
    """Test market momentum calculations."""
    result = market_toolkit.analyze_market("37215", mock_properties)
    
    assert "market_analysis" in result
    assert "market_momentum" in result["market_analysis"]
    
    momentum = result["market_analysis"]["market_momentum"]
    assert 0 <= momentum <= 1

def test_opportunity_scoring(market_toolkit, mock_properties):
    """Test opportunity scoring system."""
    market_data = market_toolkit.analyze_market(
        "37215",
        mock_properties
    )
    
    opportunities = market_toolkit.identify_opportunities(
        mock_properties,
        market_data["market_analysis"]
    )
    
    assert len(opportunities) > 0
    
    for opp in opportunities:
        assert "opportunity_score" in opp
        assert 0 <= opp["opportunity_score"] <= 100
        assert "recommendations" in opp
        assert len(opp["recommendations"]) > 0

def test_prediction_confidence(market_toolkit, mock_properties):
    """Test prediction confidence calculations."""
    # Test with mock data only
    market_data = market_toolkit.analyze_market(
        "37215",
        mock_properties
    )
    
    predictions = market_toolkit.predict_property_values(
        mock_properties,
        market_data["market_analysis"]
    )
    
    for pred in predictions:
        assert "confidence_score" in pred
        assert 0.5 <= pred["confidence_score"] <= 0.8  # Base confidence range
        
    # Test with ATTOM enriched data
    enriched_properties = mock_properties.copy()
    enriched_properties[0]["attom_data"] = {"some": "data"}
    
    predictions = market_toolkit.predict_property_values(
        enriched_properties,
        market_data["market_analysis"]
    )
    
    assert predictions[0]["confidence_score"] > predictions[1]["confidence_score"]
