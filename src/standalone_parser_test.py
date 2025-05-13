import os
import sys
import re

# Mock implementation for testing without OpenAI API
def parse_prompt_mock(prompt):
    """Mock implementation of parse_prompt that uses regex patterns"""
    try:
        # Extract region (look for common city names)
        region_match = re.search(r'(?i)(atlanta|chicago|los angeles|LA|miami)', prompt)
        region = region_match.group(1).title() if region_match else None
        if region and region.lower() == "la":
            region = "Los Angeles"
        
        # Extract property value (look for dollar amounts with k or mil)
        value_match = re.search(r'\$?(\d+(?:\.\d+)?)\s*(?:k|K|thousand|mil|M|million)?', prompt)
        value = None
        if value_match:
            value_str = value_match.group(1)
            # Check if there's a k or million indicator near the number
            value_context = prompt[max(0, value_match.start()-5):min(len(prompt), value_match.end()+5)]
            multiplier = 1000 if any(k in value_context.lower() for k in ['k', 'thousand']) else 1000000 if any(m in value_context.lower() for m in ['m', 'mil', 'million']) else 1
            value = float(value_str) * multiplier
        
        # Extract rent (look for monthly rent indicators)
        rent_match = re.search(r'rent.*?\$?(\d+(?:\.\d+)?)\s*(?:k|K)?|(\d+(?:\.\d+)?)\s*(?:k|K)?\s*(?:rent|month)', prompt)
        rent = None
        if rent_match:
            rent_str = rent_match.group(1) or rent_match.group(2)
            # Check if there's a k indicator near the rent number
            rent_context = prompt[max(0, rent_match.start()-5):min(len(prompt), rent_match.end()+5)]
            multiplier = 1000 if any(k in rent_context.lower() for k in ['k', 'thousand']) else 1
            rent = float(rent_str) * multiplier
        
        # Extract income (look for salary/income indicators)
        income_match = re.search(r'(?:make|earn|income|salary).*?\$?(\d+(?:\.\d+)?)\s*(?:k|K|thousand|mil|M|million)?', prompt)
        income = None
        if income_match:
            income_str = income_match.group(1)
            # Check if there's a k or million indicator near the income number
            income_context = prompt[max(0, income_match.start()-5):min(len(prompt), income_match.end()+10)]
            multiplier = 1000 if any(k in income_context.lower() for k in ['k', 'thousand']) else 1000000 if any(m in income_context.lower() for m in ['m', 'mil', 'million']) else 1
            income = float(income_str) * multiplier
        
        # Return as dictionary (simulating GPT-4 output)
        return {
            "region": region,
            "value": value,
            "rent": rent,
            "income": income
        }
    except Exception as e:
        return {"error": str(e)}

# Use the mock implementation for testing
parse_prompt = parse_prompt_mock

# Test cases
print("\n===== Testing Parser Only =====\n")

tests = [
    "I'm looking at a $450k condo in Atlanta, expect $2600 rent and earn $100k a year.",
    "Thinking about Chicago: buying for 350000, renting at 2000 per month, income 90000.",
    "In LA, want to pay $750k, rent 3800, salary is 150k.",
    "What about a $300k fixer-upper in Miami with $2200 rent?"  # Miami isn't in our list
]

for t in tests:
    print("\nPrompt:", t)
    try:
        result = parse_prompt(t)
        print("Parsed:", result)
    except Exception as e:
        print("Error:", str(e))
    print("-" * 40)
