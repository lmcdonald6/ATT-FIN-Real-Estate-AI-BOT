"""Anthropic Claude-powered analysis reporter."""

import os
from typing import Dict, List
import anthropic
from .base import AIReporterBase

class ClaudeReporter(AIReporterBase):
    """Claude implementation of the AI reporter."""
    
    def __init__(self, temperature: float = 0.3):
        """Initialize the Claude reporter."""
        super().__init__(temperature)
        self.client = anthropic.Client(api_key=os.getenv("CLAUDE_API_KEY"))
        
        # Load prompt templates
        self.templates = {
            "investment_summary": """Analyze this real estate market data as an expert analyst:
{data}

Provide a structured analysis with these sections:
1. Executive Summary: Brief overview of investment potential
2. Key Advantages: List specific positive factors
3. Risk Factors: List potential concerns
4. Investment Strategy: Specific recommendations

Format the response in clear sections. Be quantitative and specific.""",

            "risk_report": """As a risk assessment specialist, analyze this real estate market data:
{data}

Provide a detailed risk analysis with:
1. Risk Level Assessment: Overall evaluation
2. Market Risk Factors: Specific market-related risks
3. Property Risk Factors: Property-specific concerns
4. Mitigation Strategies: Actionable recommendations

Use data-driven insights and specific examples.""",

            "neighborhood_snapshot": """Create a detailed neighborhood analysis using this data:
{data}

Structure the analysis with:
1. Neighborhood Overview: Key characteristics
2. Demographic Profile: Population trends and characteristics
3. Market Trends: Current and projected developments
4. Investment Opportunities: Specific actionable opportunities

Focus on concrete details and market dynamics."""
        }
    
    async def generate_investment_summary(self, data: Dict) -> Dict[str, str]:
        """Generate an investment opportunity summary using Claude."""
        prompt = self.format_prompt(self.templates["investment_summary"], {"data": str(data)})
        
        try:
            response = await self.client.messages.create(
                model="claude-2",
                max_tokens=1000,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            sections = content.split("\n\n")
            
            return {
                "summary": sections[0].strip(),
                "pros": self._extract_list(sections[1]) if len(sections) > 1 else [],
                "cons": self._extract_list(sections[2]) if len(sections) > 2 else [],
                "strategy": sections[3].strip() if len(sections) > 3 else "No strategy provided"
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "pros": [],
                "cons": [],
                "strategy": "Error occurred"
            }
    
    async def generate_risk_report(self, data: Dict) -> Dict[str, str]:
        """Generate a detailed risk analysis report using Claude."""
        prompt = self.format_prompt(self.templates["risk_report"], {"data": str(data)})
        
        try:
            response = await self.client.messages.create(
                model="claude-2",
                max_tokens=1000,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            sections = content.split("\n\n")
            
            return {
                "risk_level": sections[0].strip(),
                "market_risks": self._extract_list(sections[1]) if len(sections) > 1 else [],
                "property_risks": self._extract_list(sections[2]) if len(sections) > 2 else [],
                "mitigation": sections[3].strip() if len(sections) > 3 else "No mitigation strategies provided"
            }
            
        except Exception as e:
            return {
                "risk_level": "Error",
                "market_risks": [],
                "property_risks": [],
                "mitigation": f"Error generating risk report: {str(e)}"
            }
    
    async def generate_neighborhood_snapshot(self, data: Dict) -> Dict[str, str]:
        """Generate a neighborhood analysis snapshot using Claude."""
        prompt = self.format_prompt(self.templates["neighborhood_snapshot"], {"data": str(data)})
        
        try:
            response = await self.client.messages.create(
                model="claude-2",
                max_tokens=1000,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            sections = content.split("\n\n")
            
            return {
                "overview": sections[0].strip(),
                "demographics": sections[1].strip() if len(sections) > 1 else "No demographic data",
                "trends": self._extract_list(sections[2]) if len(sections) > 2 else [],
                "opportunities": self._extract_list(sections[3]) if len(sections) > 3 else []
            }
            
        except Exception as e:
            return {
                "overview": f"Error generating snapshot: {str(e)}",
                "demographics": "Error",
                "trends": [],
                "opportunities": []
            }
    
    def _extract_list(self, text: str) -> List[str]:
        """Extract a list from bullet points or numbered items."""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "• ", "* ", "1.", "2.", "3.")):
                items.append(line[2:].strip())
        return items if items else [text]
