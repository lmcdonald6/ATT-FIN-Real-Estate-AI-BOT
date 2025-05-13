"""🤖 GPT-4 Property Report Generator Module"""

import os
from typing import Dict, Optional
from pydantic import BaseModel, Field
from openai import OpenAI, OpenAIError

class PropertyData(BaseModel):
    """Validate property data structure"""
    zip: str
    rent_analysis: Dict[str, str | float] = Field(..., description="Rental analysis data")
    appreciation_analysis: Dict[str, str | float] = Field(..., description="Appreciation analysis data")
    risk_analysis: Dict[str, str | float] = Field(..., description="Risk analysis data")
    final_score: float = Field(..., ge=0, le=100)

def generate_property_report(data: Dict) -> Dict[str, str | bool | None]:
    """Generate a property investment report using GPT-4"""
    try:
        # Validate input data
        PropertyData(**data)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        client = OpenAI(api_key=api_key)
        
        # Build the prompt
        prompt = f"""
        You're a real estate investment analyst. Based on the following data, write a 3-paragraph investor report that includes:
        1. Property summary and rental potential
        2. Market outlook and appreciation potential
        3. Risk assessment and final recommendation

        PROPERTY DATA:
        - Location: ZIP {data['zip']}
        - Rental Analysis:
          * Score: {data['rent_analysis']['score']}/100
          * Assessment: {data['rent_analysis']['note']}
        - Market Analysis:
          * Appreciation Score: {data['appreciation_analysis']['score']}/100
          * Trend: {data['appreciation_analysis']['note']}

        RISK FACTORS:
        - Vacancy Rate: {data['risk_analysis']['vacancy_rate']}%
        - Tax Burden: {data['risk_analysis']['tax_burden']}%
        - Overall Risk Score: {data['risk_analysis'].get('score_penalty', 0)} points

        INVESTMENT RATING:
        Final Score: {data['final_score']}/100

        Write a professional analysis focused on actionable insights. Be clear and confident but acknowledge both opportunities and risks.
        """

        # Generate report
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "system",
                "content": "You are an experienced real estate investment analyst specializing in market analysis and risk assessment."
            }, {
                "role": "user",
                "content": prompt
            }],
            max_tokens=800,
            temperature=0.7
        )

        return {
            "success": True,
            "report": response.choices[0].message.content,
            "error": None
        }

    except OpenAIError as e:
        return {
            "success": False,
            "report": None,
            "error": f"OpenAI API error: {str(e)}"
        }
    except ValueError as e:
        return {
            "success": False,
            "report": None,
            "error": f"Data validation error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "report": None,
            "error": f"Unexpected error: {str(e)}"
        }
