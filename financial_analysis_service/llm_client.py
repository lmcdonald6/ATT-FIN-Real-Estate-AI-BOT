"""LLM Client for Financial Analysis

This module provides an interface to interact with Large Language Models (LLMs)
for real estate financial analysis.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('llm_client')

# Load environment variables
load_dotenv()

# LLM API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

class LLMClient:
    """Client for interacting with Large Language Models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the LLM client.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: LLM model to use (defaults to environment variable)
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or DEFAULT_MODEL
        
        if not self.api_key:
            logger.warning("No API key provided. LLM functionality will be limited.")
    
    def generate_response(self, prompt: str, max_tokens: int = MAX_TOKENS, 
                         temperature: float = TEMPERATURE) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for generation
            
        Returns:
            Generated text response
        """
        if not self.api_key:
            logger.error("No API key available. Cannot generate response.")
            return "Error: No API key available. Please set OPENAI_API_KEY in your environment."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            return response_data["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return f"Error: {str(e)}"
        
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            return f"Error parsing response: {str(e)}"
    
    def load_prompt_template(self, template_name: str) -> str:
        """Load a prompt template from file.
        
        Args:
            template_name: Name of the template file (without extension)
            
        Returns:
            Template string
        """
        template_path = os.path.join(
            os.path.dirname(__file__),
            "prompt_templates",
            f"{template_name}.txt"
        )
        
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found: {template_name}")
            return ""
    
    def fill_prompt_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Fill a prompt template with variables.
        
        Args:
            template: Template string with placeholders
            variables: Dictionary of variables to fill in the template
            
        Returns:
            Filled template string
        """
        filled_template = template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            filled_template = filled_template.replace(placeholder, str(value))
        
        return filled_template
    
    def analyze_investment(self, property_data: Dict[str, Any]) -> str:
        """Analyze a real estate investment opportunity.
        
        Args:
            property_data: Dictionary containing property data
            
        Returns:
            Investment analysis text
        """
        template = self.load_prompt_template("investment_analysis")
        prompt = self.fill_prompt_template(template, property_data)
        
        return self.generate_response(prompt)
    
    def assess_risk(self, market_data: Dict[str, Any]) -> str:
        """Assess the risk of a real estate market.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Risk assessment text
        """
        template = self.load_prompt_template("risk_assessment")
        prompt = self.fill_prompt_template(template, market_data)
        
        return self.generate_response(prompt)
    
    def analyze_market_trends(self, market_data: Dict[str, Any]) -> str:
        """Analyze real estate market trends.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Market trends analysis text
        """
        template = self.load_prompt_template("market_trends")
        prompt = self.fill_prompt_template(template, market_data)
        
        return self.generate_response(prompt)
    
    def generate_investment_summary(self, property_data: Dict[str, Any], 
                                   market_data: Dict[str, Any]) -> str:
        """Generate a comprehensive investment summary.
        
        Args:
            property_data: Dictionary containing property data
            market_data: Dictionary containing market data
            
        Returns:
            Investment summary text
        """
        # Combine property and market data
        combined_data = {
            **property_data,
            "market": market_data
        }
        
        template = self.load_prompt_template("investment_summary")
        prompt = self.fill_prompt_template(template, combined_data)
        
        return self.generate_response(prompt, max_tokens=1500)
