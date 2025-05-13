"""Financial Analysis Service

This module provides financial analysis services for real estate investments.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
import logging

# Add the parent directory to the path to import modules from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the llm_client module
from financial_analysis_service.llm_client import LLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('analysis_service')

class FinancialAnalysisService:
    """Service for financial analysis of real estate investments."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the financial analysis service.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: LLM model to use (defaults to environment variable)
        """
        self.llm_client = LLMClient(api_key, model)
    
    def analyze_investment(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a real estate investment opportunity.
        
        Args:
            property_data: Dictionary containing property data
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing investment for property: {property_data.get('address', 'Unknown')}")
        
        # Validate required fields
        required_fields = ['address', 'price', 'monthly_rent']
        missing_fields = [field for field in required_fields if field not in property_data]
        
        if missing_fields:
            logger.error(f"Missing required fields for investment analysis: {missing_fields}")
            return {
                "status": "error",
                "message": f"Missing required fields: {missing_fields}"
            }
        
        # Calculate basic financial metrics if not provided
        if 'cap_rate' not in property_data and 'price' in property_data and 'annual_income' in property_data:
            annual_income = property_data['annual_income']
            price = property_data['price']
            property_data['cap_rate'] = round((annual_income / price) * 100, 2)
        
        if 'annual_income' not in property_data and 'monthly_rent' in property_data:
            property_data['annual_income'] = property_data['monthly_rent'] * 12
        
        if 'ptr_ratio' not in property_data and 'price' in property_data and 'monthly_rent' in property_data:
            price = property_data['price']
            monthly_rent = property_data['monthly_rent']
            property_data['ptr_ratio'] = round(price / (monthly_rent * 12), 2)
        
        # Generate analysis using LLM
        analysis_text = self.llm_client.analyze_investment(property_data)
        
        return {
            "status": "success",
            "property": property_data,
            "analysis": analysis_text
        }
    
    def assess_risk(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the risk of a real estate market.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Dictionary containing risk assessment results
        """
        logger.info(f"Assessing risk for market: {market_data.get('region', 'Unknown')}")
        
        # Validate required fields
        required_fields = ['region', 'market_phase']
        missing_fields = [field for field in required_fields if field not in market_data]
        
        if missing_fields:
            logger.error(f"Missing required fields for risk assessment: {missing_fields}")
            return {
                "status": "error",
                "message": f"Missing required fields: {missing_fields}"
            }
        
        # Generate risk assessment using LLM
        assessment_text = self.llm_client.assess_risk(market_data)
        
        return {
            "status": "success",
            "market": market_data,
            "assessment": assessment_text
        }
    
    def analyze_market_trends(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze real estate market trends.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Dictionary containing market trends analysis results
        """
        logger.info(f"Analyzing market trends for: {market_data.get('region', 'Unknown')}")
        
        # Validate required fields
        required_fields = ['region', 'market_phase']
        missing_fields = [field for field in required_fields if field not in market_data]
        
        if missing_fields:
            logger.error(f"Missing required fields for market trends analysis: {missing_fields}")
            return {
                "status": "error",
                "message": f"Missing required fields: {missing_fields}"
            }
        
        # Generate market trends analysis using LLM
        trends_text = self.llm_client.analyze_market_trends(market_data)
        
        return {
            "status": "success",
            "market": market_data,
            "analysis": trends_text
        }
    
    def generate_investment_summary(self, property_data: Dict[str, Any], 
                                  market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive investment summary.
        
        Args:
            property_data: Dictionary containing property data
            market_data: Dictionary containing market data
            
        Returns:
            Dictionary containing investment summary results
        """
        logger.info(f"Generating investment summary for property: {property_data.get('address', 'Unknown')}")
        
        # Validate required fields for property
        property_required_fields = ['address', 'price', 'monthly_rent']
        property_missing_fields = [field for field in property_required_fields if field not in property_data]
        
        if property_missing_fields:
            logger.error(f"Missing required property fields for investment summary: {property_missing_fields}")
            return {
                "status": "error",
                "message": f"Missing required property fields: {property_missing_fields}"
            }
        
        # Validate required fields for market
        market_required_fields = ['region', 'market_phase']
        market_missing_fields = [field for field in market_required_fields if field not in market_data]
        
        if market_missing_fields:
            logger.error(f"Missing required market fields for investment summary: {market_missing_fields}")
            return {
                "status": "error",
                "message": f"Missing required market fields: {market_missing_fields}"
            }
        
        # Generate investment summary using LLM
        summary_text = self.llm_client.generate_investment_summary(property_data, market_data)
        
        return {
            "status": "success",
            "property": property_data,
            "market": market_data,
            "summary": summary_text
        }
