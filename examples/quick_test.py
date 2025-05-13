import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Mock implementation for testing without API calls
def parse_prompt_mock(prompt):
    """Parse natural language input (mock implementation simulating GPT-4)"""
    print("Note: Using mock implementation due to API quota limitations")
    
    # Mock implementation that simulates what GPT-4 would return
    if "atlanta" in prompt.lower():
        return {
            "region": "Atlanta",
            "value": 450000,
            "rent": 2600,
            "income": 100000
        }
    elif "chicago" in prompt.lower():
        return {
            "region": "Chicago",
            "value": 350000,
            "rent": 2000,
            "income": 90000
        }
    elif "los angeles" in prompt.lower() or "la" in prompt.lower():
        return {
            "region": "Los Angeles",
            "value": 750000,
            "rent": 3800,
            "income": 150000
        }
    elif "miami" in prompt.lower():
        # Miami is not in our supported regions list, but we'll return it for testing
        return {
            "region": "Miami",
            "value": 300000,
            "rent": 2200,
            "income": None
        }
    else:
        return {"error": "Could not parse the input. Please include region, property value, and rent."}

# Use the mock implementation for testing
parse_prompt = parse_prompt_mock

if __name__ == "__main__":
    prompts = [
        "I'm buying a $450k condo in Atlanta, rent $2600, income is $100k.",
        "Thinking about Chicago: pay 350000, rent at 2000, salary 90000.",
        "In LA, want to pay $750k, rent 3800, I earn 150k a year.",
        "What about Miami for $300k and rent 2200?"
    ]
    for p in prompts:
        print(p, "->", parse_prompt(p))
