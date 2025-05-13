"""Base class for AI reporters."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class AIReporterBase(ABC):
    """Base class for AI-powered analysis reporters."""
    
    def __init__(self, temperature: float = 0.3):
        """
        Initialize the reporter.
        
        Args:
            temperature: AI model temperature (0-1). Lower values are more deterministic.
        """
        self.temperature = temperature
    
    @abstractmethod
    async def generate_investment_summary(self, data: Dict) -> Dict[str, str]:
        """
        Generate an investment opportunity summary.
        
        Args:
            data: Analysis data including signals and market stats
            
        Returns:
            Dict containing:
            - summary: Overall investment summary
            - pros: List of advantages
            - cons: List of risks/disadvantages
            - strategy: Recommended investment strategy
        """
        pass
    
    @abstractmethod
    async def generate_risk_report(self, data: Dict) -> Dict[str, str]:
        """
        Generate a detailed risk analysis report.
        
        Args:
            data: Analysis data including signals and market stats
            
        Returns:
            Dict containing:
            - risk_level: Overall risk assessment
            - market_risks: Market-specific risks
            - property_risks: Property-specific risks
            - mitigation: Risk mitigation strategies
        """
        pass
    
    @abstractmethod
    async def generate_neighborhood_snapshot(self, data: Dict) -> Dict[str, str]:
        """
        Generate a neighborhood analysis snapshot.
        
        Args:
            data: Analysis data including signals and market stats
            
        Returns:
            Dict containing:
            - overview: Neighborhood overview
            - demographics: Key demographic insights
            - trends: Current and projected trends
            - opportunities: Specific opportunities
        """
        pass
    
    def format_prompt(self, template: str, data: Dict) -> str:
        """Format a prompt template with data."""
        return template.format(**data)
    
    def validate_response(self, response: Dict) -> bool:
        """Validate that the response contains required fields."""
        required_fields = {
            'investment_summary': ['summary', 'pros', 'cons', 'strategy'],
            'risk_report': ['risk_level', 'market_risks', 'property_risks', 'mitigation'],
            'neighborhood_snapshot': ['overview', 'demographics', 'trends', 'opportunities']
        }
        
        for report_type, fields in required_fields.items():
            if report_type in response:
                if not all(field in response[report_type] for field in fields):
                    return False
        return True
