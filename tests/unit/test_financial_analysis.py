"""Unit tests for the Financial Analysis Service."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the module to test
sys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
import sys
sys.path.append(sys_path)

from financial_analysis_service.api import app
from financial_analysis_service.analysis_service import (
    FinancialAnalysisService,
    InvestmentAnalysis,
    RiskAssessment,
    MarketTrendAnalysis
)

# Test client
@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)

# Mock LLM client
@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    with patch('financial_analysis_service.llm_client.LLMClient') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

# Mock financial analysis service
@pytest.fixture
def mock_financial_analysis_service():
    """Create a mock financial analysis service."""
    with patch('financial_analysis_service.api.FinancialAnalysisService') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service

class TestFinancialAnalysisAPI:
    """Test suite for the Financial Analysis API."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    def test_investment_analysis(self, client, mock_financial_analysis_service):
        """Test investment analysis endpoint."""
        # Mock the investment analysis response
        mock_financial_analysis_service.analyze_investment.return_value = {
            "roi": 8.5,
            "cash_flow": 1200,
            "cap_rate": 6.2,
            "recommendation": "This property shows good potential for investment."
        }
        
        # Test data
        test_data = {
            "property_id": "123",
            "purchase_price": 300000,
            "estimated_rent": 2500,
            "estimated_expenses": 800,
            "location": "Austin, TX"
        }
        
        # Make request
        response = client.post('/analysis/investment', json=test_data)
        
        # Check response
        assert response.status_code == 200
        assert response.json()['roi'] == 8.5
        assert response.json()['cash_flow'] == 1200
        assert response.json()['cap_rate'] == 6.2
        assert "good potential" in response.json()['recommendation']
        
        # Check that the service was called with the correct data
        mock_financial_analysis_service.analyze_investment.assert_called_once_with(
            property_id="123",
            purchase_price=300000,
            estimated_rent=2500,
            estimated_expenses=800,
            location="Austin, TX"
        )
    
    def test_risk_assessment(self, client, mock_financial_analysis_service):
        """Test risk assessment endpoint."""
        # Mock the risk assessment response
        mock_financial_analysis_service.assess_risk.return_value = {
            "risk_score": 65,
            "market_volatility": "medium",
            "liquidity_risk": "low",
            "assessment": "The property has a moderate risk profile."
        }
        
        # Test data
        test_data = {
            "property_id": "123",
            "location": "Austin, TX",
            "property_type": "single_family",
            "market_trends": ["growing", "stable_employment"]
        }
        
        # Make request
        response = client.post('/analysis/risk', json=test_data)
        
        # Check response
        assert response.status_code == 200
        assert response.json()['risk_score'] == 65
        assert response.json()['market_volatility'] == "medium"
        assert response.json()['liquidity_risk'] == "low"
        assert "moderate risk" in response.json()['assessment']
        
        # Check that the service was called with the correct data
        mock_financial_analysis_service.assess_risk.assert_called_once_with(
            property_id="123",
            location="Austin, TX",
            property_type="single_family",
            market_trends=["growing", "stable_employment"]
        )
    
    def test_market_trends(self, client, mock_financial_analysis_service):
        """Test market trends endpoint."""
        # Mock the market trends response
        mock_financial_analysis_service.analyze_market_trends.return_value = {
            "price_trend": "increasing",
            "demand": "high",
            "supply": "limited",
            "forecast": "The market is expected to grow by 5% in the next year."
        }
        
        # Test data
        test_data = {
            "location": "Austin, TX",
            "property_type": "single_family",
            "time_period": "1y"
        }
        
        # Make request
        response = client.post('/analysis/market_trends', json=test_data)
        
        # Check response
        assert response.status_code == 200
        assert response.json()['price_trend'] == "increasing"
        assert response.json()['demand'] == "high"
        assert response.json()['supply'] == "limited"
        assert "grow by 5%" in response.json()['forecast']
        
        # Check that the service was called with the correct data
        mock_financial_analysis_service.analyze_market_trends.assert_called_once_with(
            location="Austin, TX",
            property_type="single_family",
            time_period="1y"
        )

class TestFinancialAnalysisService:
    """Test suite for the Financial Analysis Service."""
    
    def test_investment_analysis(self, mock_llm_client):
        """Test investment analysis."""
        # Mock the LLM response
        mock_llm_client.get_completion.return_value = json.dumps({
            "roi": 8.5,
            "cash_flow": 1200,
            "cap_rate": 6.2,
            "recommendation": "This property shows good potential for investment."
        })
        
        # Create service instance
        service = FinancialAnalysisService(llm_client=mock_llm_client)
        
        # Call the method
        result = service.analyze_investment(
            property_id="123",
            purchase_price=300000,
            estimated_rent=2500,
            estimated_expenses=800,
            location="Austin, TX"
        )
        
        # Check result
        assert result['roi'] == 8.5
        assert result['cash_flow'] == 1200
        assert result['cap_rate'] == 6.2
        assert "good potential" in result['recommendation']
        
        # Check that the LLM client was called
        mock_llm_client.get_completion.assert_called_once()
    
    def test_risk_assessment(self, mock_llm_client):
        """Test risk assessment."""
        # Mock the LLM response
        mock_llm_client.get_completion.return_value = json.dumps({
            "risk_score": 65,
            "market_volatility": "medium",
            "liquidity_risk": "low",
            "assessment": "The property has a moderate risk profile."
        })
        
        # Create service instance
        service = FinancialAnalysisService(llm_client=mock_llm_client)
        
        # Call the method
        result = service.assess_risk(
            property_id="123",
            location="Austin, TX",
            property_type="single_family",
            market_trends=["growing", "stable_employment"]
        )
        
        # Check result
        assert result['risk_score'] == 65
        assert result['market_volatility'] == "medium"
        assert result['liquidity_risk'] == "low"
        assert "moderate risk" in result['assessment']
        
        # Check that the LLM client was called
        mock_llm_client.get_completion.assert_called_once()
    
    def test_market_trends(self, mock_llm_client):
        """Test market trends analysis."""
        # Mock the LLM response
        mock_llm_client.get_completion.return_value = json.dumps({
            "price_trend": "increasing",
            "demand": "high",
            "supply": "limited",
            "forecast": "The market is expected to grow by 5% in the next year."
        })
        
        # Create service instance
        service = FinancialAnalysisService(llm_client=mock_llm_client)
        
        # Call the method
        result = service.analyze_market_trends(
            location="Austin, TX",
            property_type="single_family",
            time_period="1y"
        )
        
        # Check result
        assert result['price_trend'] == "increasing"
        assert result['demand'] == "high"
        assert result['supply'] == "limited"
        assert "grow by 5%" in result['forecast']
        
        # Check that the LLM client was called
        mock_llm_client.get_completion.assert_called_once()

if __name__ == "__main__":
    pytest.main()
