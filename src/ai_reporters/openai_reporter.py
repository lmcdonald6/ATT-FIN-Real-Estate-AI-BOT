"""OpenAI-powered analysis reporter."""

import os
from typing import Dict, List
import openai
from .base import AIReporterBase

class OpenAIReporter(AIReporterBase):
    """OpenAI implementation of the AI reporter."""
    
    def __init__(self, temperature: float = 0.3):
        """Initialize the OpenAI reporter."""
        super().__init__(temperature)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Load prompt templates
        self.templates = {
            "investment_summary": """Analyze the following real estate market data and provide an investment summary:
{data}

Focus on:
1. Overall investment potential
2. Key advantages
3. Potential risks
4. Recommended strategy

Use a professional, analytical tone and be specific about numbers and trends.""",

            "risk_report": """Generate a detailed risk assessment for this real estate market:
{data}

Include:
1. Overall risk level
2. Market-specific risks
3. Property-specific risks
4. Risk mitigation strategies

Be quantitative where possible and provide specific recommendations.""",

            "neighborhood_snapshot": """Create a comprehensive neighborhood analysis based on this data:
{data}

Cover:
1. Neighborhood overview
2. Key demographic insights
3. Current and projected trends
4. Specific opportunities

Focus on actionable insights and market dynamics."""
        }
    
    async def generate_investment_summary(self, data: Dict) -> Dict[str, str]:
        """Generate an investment opportunity summary using OpenAI."""
        prompt = self.format_prompt(self.templates["investment_summary"], {"data": str(data)})
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional real estate analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            # Parse the response into structured format
            content = response.choices[0].message.content
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
        """Generate a detailed risk analysis report using OpenAI."""
        prompt = self.format_prompt(self.templates["risk_report"], {"data": str(data)})
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a risk assessment specialist in real estate."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
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
        """Generate a neighborhood analysis snapshot using OpenAI."""
        prompt = self.format_prompt(self.templates["neighborhood_snapshot"], {"data": str(data)})
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a neighborhood analysis specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
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
