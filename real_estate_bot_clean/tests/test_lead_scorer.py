"""
Test suite for lead scoring module.
Tests integration with hybrid data approach and API Gateway.
"""
import pytest
from datetime import datetime
from src.analysis.lead_scorer import LeadScorer, LeadScore

@pytest.fixture
def scorer():
    """Create LeadScorer instance."""
    return LeadScorer()

@pytest.fixture
def sample_property_data():
    """Create sample property data."""
    return {
        "estimated_value": 500000,
        "last_sale_price": 400000,
        "last_sale_date": "2019-01-01",
        "tax_assessment": 450000,
        "years_owned": 4,
        "equity_percentage": 0.4,
        "tax_status": "current",
        "property_condition": "fair",
        "occupancy_status": "owner_occupied"
    }

@pytest.fixture
def sample_market_data():
    """Create sample market data."""
    return {
        "median_price": 550000,
        "price_trend": 0.05,
        "days_on_market": 30,
        "inventory_level": "low",
        "market_strength": 0.8
    }

@pytest.fixture
def sample_owner_data():
    """Create sample owner data."""
    return {
        "age": 65,
        "income_level": "medium",
        "property_count": 1,
        "bankruptcy_history": False,
        "foreclosure_history": False,
        "tax_liens": False,
        "mailing_address_match": True
    }

def test_lead_scoring_complete_data(
    scorer,
    sample_property_data,
    sample_market_data,
    sample_owner_data
):
    """Test lead scoring with complete data."""
    score = scorer.score_lead(
        sample_property_data,
        sample_market_data,
        sample_owner_data
    )
    
    assert isinstance(score, LeadScore)
    assert 0 <= score.motivation_score <= 1
    assert 0 <= score.deal_probability <= 1
    assert 0 <= score.response_likelihood <= 1
    assert 0 <= score.confidence_score <= 1
    assert isinstance(score.timestamp, datetime)
    assert len(score.features_used) > 0

def test_lead_scoring_partial_data(scorer, sample_property_data):
    """Test lead scoring with partial data."""
    score = scorer.score_lead(
        sample_property_data,
        {},  # Empty market data
        {}   # Empty owner data
    )
    
    assert isinstance(score, LeadScore)
    # Should have lower confidence due to missing data
    assert score.confidence_score < 0.5
    assert len(score.features_used) < len(scorer.property_features)

def test_lead_scoring_invalid_data(scorer):
    """Test lead scoring with invalid data."""
    score = scorer.score_lead(
        {"invalid": "data"},
        {"also": "invalid"},
        {"more": "invalid"}
    )
    
    assert isinstance(score, LeadScore)
    assert score.confidence_score < 0.2
    assert len(score.features_used) == 0

def test_feature_extraction(
    scorer,
    sample_property_data,
    sample_market_data,
    sample_owner_data
):
    """Test feature extraction and normalization."""
    features, used_features = scorer._extract_features(
        sample_property_data,
        sample_market_data,
        sample_owner_data
    )
    
    assert features.shape[1] == len(used_features)
    assert all(0 <= f <= 1 for f in features.flatten())
    assert len(used_features) > 0

def test_feature_normalization(scorer):
    """Test feature value normalization."""
    # Test boolean values
    assert scorer._normalize_feature("any", True) == 1.0
    assert scorer._normalize_feature("any", False) == 0.0
    
    # Test numeric values
    assert 0 <= scorer._normalize_feature("any", 42) <= 1
    assert 0 <= scorer._normalize_feature("any", 3.14) <= 1
    
    # Test categorical values
    assert scorer._normalize_feature(
        "property_condition",
        "excellent"
    ) == 1.0
    assert scorer._normalize_feature(
        "tax_status",
        "current"
    ) == 1.0

def test_confidence_calculation(scorer):
    """Test confidence score calculation."""
    # Test with full feature set
    all_features = (
        scorer.property_features +
        scorer.market_features +
        scorer.owner_features
    )
    
    confidence = scorer._calculate_confidence(
        all_features,
        0.5,  # Neutral motivation
        0.5,  # Neutral deal probability
        0.5   # Neutral response likelihood
    )
    
    assert 0.7 <= confidence <= 1.0  # High due to full feature coverage
    
    # Test with partial feature set
    partial_features = scorer.property_features[:3]
    confidence = scorer._calculate_confidence(
        partial_features,
        0.5,
        0.5,
        0.5
    )
    
    assert confidence < 0.7  # Lower due to partial coverage

def test_prediction_methods(scorer):
    """Test individual prediction methods."""
    import numpy as np
    features = np.random.rand(1, 10)  # Random test features
    
    # Test motivation prediction
    motivation = scorer._predict_motivation(features)
    assert 0 <= motivation <= 1
    
    # Test deal probability prediction
    deal_prob = scorer._predict_deal_probability(features)
    assert 0 <= deal_prob <= 1
    
    # Test response likelihood prediction
    response = scorer._predict_response_likelihood(features)
    assert 0 <= response <= 1

def test_error_handling(scorer):
    """Test error handling and fallback scores."""
    # Test with None values
    score = scorer.score_lead(None, None, None)
    assert isinstance(score, LeadScore)
    assert score.confidence_score < 0.2
    
    # Test with empty data
    score = scorer.score_lead({}, {}, {})
    assert isinstance(score, LeadScore)
    assert score.confidence_score < 0.2
    
    # Test feature extraction with invalid data
    features, used_features = scorer._extract_features({}, {}, {})
    assert len(used_features) == 0
    assert features.shape[1] == 0

def test_integration_with_api_gateway(
    scorer,
    sample_property_data,
    sample_market_data,
    sample_owner_data
):
    """Test integration with API Gateway format."""
    # Simulate API Gateway request format
    request_data = {
        "property_data": sample_property_data,
        "market_data": sample_market_data,
        "owner_data": sample_owner_data
    }
    
    score = scorer.score_lead(
        request_data["property_data"],
        request_data["market_data"],
        request_data["owner_data"]
    )
    
    assert isinstance(score, LeadScore)
    assert score.confidence_score > 0.5  # Good confidence with complete data
    
    # Verify all components are present
    assert hasattr(score, "motivation_score")
    assert hasattr(score, "deal_probability")
    assert hasattr(score, "response_likelihood")
    assert hasattr(score, "confidence_score")
    assert hasattr(score, "timestamp")
    assert hasattr(score, "features_used")
