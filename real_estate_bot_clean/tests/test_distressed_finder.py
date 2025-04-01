"""
Test suite for DistressedFinder.
Tests both mock data and ATTOM-enriched scenarios.
"""
import pytest
from datetime import datetime
from src.analysis.distressed_finder import DistressedFinder

@pytest.fixture
def distressed_finder():
    """Create DistressedFinder instance for testing."""
    return DistressedFinder()

@pytest.fixture
def mock_property():
    """Create mock property data."""
    return {
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
    }

@pytest.fixture
def attom_enriched_property():
    """Create property data enriched with ATTOM data."""
    return {
        "id": "37215_2",
        "address": "456 Test Ave",
        "zip_code": "37215",
        "price": 600000,  # Under market
        "sqft": 2800,
        "property_type": "Single Family",
        "bedrooms": 3,
        "bathrooms": 2,
        "year_built": 1985,
        "days_on_market": 45,
        "status": "For Sale",
        "date": "2024-03-15",
        "attom_data": {
            "tax": {
                "is_delinquent": True,
                "amount_due": 15000
            },
            "foreclosure": {
                "status": "pre",
                "auction_date": None
            },
            "occupancy": {
                "status": "vacant",
                "last_verified": "2024-02-01"
            },
            "building": {
                "condition": "fair",
                "last_renovation": "2005"
            },
            "owner": {
                "is_out_of_state": True,
                "years_owned": 25,
                "other_properties": 4
            }
        }
    }

@pytest.fixture
def market_data():
    """Create mock market data."""
    return {
        "median_price": 900000,
        "market_strength": 0.75,
        "growth_rate": 0.08,
        "days_on_market": 35
    }

def test_analyze_property_basic(distressed_finder, mock_property):
    """Test basic property analysis with mock data."""
    result = distressed_finder.analyze_property(mock_property)
    
    assert result is not None
    assert "distress_score" in result
    assert "opportunity_level" in result
    assert "indicators" in result
    assert "recommendations" in result
    assert "confidence_score" in result
    
    # Check score ranges
    assert 0 <= result["distress_score"] <= 1
    assert 0.5 <= result["confidence_score"] <= 0.8  # Base range for mock data

def test_analyze_property_with_attom(
    distressed_finder,
    attom_enriched_property,
    market_data
):
    """Test property analysis with ATTOM-enriched data."""
    result = distressed_finder.analyze_property(
        attom_enriched_property,
        market_data
    )
    
    assert result is not None
    assert result["distress_score"] > 0.7  # Should be high due to indicators
    assert result["opportunity_level"] == "High Potential"
    assert len(result["recommendations"]) >= 3
    assert result["confidence_score"] > 0.8  # Higher due to ATTOM data

def test_feature_extraction(distressed_finder, attom_enriched_property):
    """Test feature extraction from ATTOM data."""
    features = distressed_finder._extract_features(
        attom_enriched_property,
        None
    )
    
    assert features is not None
    assert "tax_delinquent" in features
    assert features["tax_delinquent"] == 1.0
    assert "foreclosure_status" in features
    assert features["foreclosure_status"] == 0.7
    assert "vacancy_status" in features
    assert features["vacancy_status"] == 1.0

def test_mock_data_generation(distressed_finder, mock_property):
    """Test mock data generation for missing ATTOM data."""
    features = distressed_finder._extract_features(mock_property, None)
    
    assert features is not None
    assert all(0 <= features[key] <= 1 for key in features)
    assert len(features) == len(distressed_finder.indicators)

def test_market_position_analysis(
    distressed_finder,
    attom_enriched_property,
    market_data
):
    """Test market position analysis."""
    score = distressed_finder._analyze_market_position(
        attom_enriched_property,
        market_data
    )
    
    assert 0 <= score <= 1
    assert score > 0.7  # Should be high due to under-market price

def test_recommendations(distressed_finder, attom_enriched_property):
    """Test recommendation generation."""
    features = distressed_finder._extract_features(
        attom_enriched_property,
        None
    )
    score = 0.8
    
    recommendations = distressed_finder._generate_recommendations(
        features,
        score
    )
    
    assert len(recommendations) > 0
    assert any("tax" in r.lower() for r in recommendations)
    assert any("foreclosure" in r.lower() for r in recommendations)
    assert any("vacant" in r.lower() for r in recommendations)

def test_confidence_scoring(
    distressed_finder,
    mock_property,
    attom_enriched_property
):
    """Test confidence score calculation."""
    # Test with mock data
    mock_result = distressed_finder.analyze_property(mock_property)
    assert 0.5 <= mock_result["confidence_score"] <= 0.8
    
    # Test with ATTOM data
    attom_result = distressed_finder.analyze_property(
        attom_enriched_property
    )
    assert attom_result["confidence_score"] > mock_result["confidence_score"]

def test_opportunity_levels(distressed_finder):
    """Test opportunity level thresholds."""
    assert distressed_finder._get_opportunity_level(0.8) == "High Potential"
    assert distressed_finder._get_opportunity_level(0.6) == "Medium Potential"
    assert distressed_finder._get_opportunity_level(0.3) == "Low Potential"
    assert distressed_finder._get_opportunity_level(0.1) == "Not Recommended"

def test_error_handling(distressed_finder):
    """Test error handling with invalid data."""
    result = distressed_finder.analyze_property({})
    
    assert result is not None
    assert result["distress_score"] == 0.5
    assert result["opportunity_level"] == "Unknown"
    assert len(result["indicators"]) == 0
    assert result["confidence_score"] == 0.5

def test_distress_score_calculation(distressed_finder):
    """Test distress score calculation."""
    features = {
        "tax_delinquent": 1.0,
        "foreclosure_status": 0.7,
        "vacancy_status": 1.0,
        "maintenance_issues": 0.5,
        "owner_circumstances": 0.8,
        "market_position": 0.9
    }
    
    score = distressed_finder._calculate_distress_score(features)
    
    assert 0 <= score <= 1
    assert score > 0.7  # Should be high given the features
