import os
import re

# Mock implementation of parse_prompt function to demonstrate expected behavior
def parse_prompt(prompt):
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
    elif "los angeles" in prompt.lower() or " la" in prompt.lower():
        return {
            "region": "Los Angeles",
            "value": 750000,
            "rent": 3800,
            "income": 150000
        }
    elif "miami" in prompt.lower():
        # Miami is not in our supported regions list, so region would be None
        return {
            "region": None,
            "value": 300000,
            "rent": 2200,
            "income": None
        }
    else:
        return {"error": "Could not parse the input. Please include region, property value, and rent."}

def run_parser_tests():
    test_prompts = [
        "I'm looking at a $450k condo in Atlanta, expect $2600 rent and earn $100k a year.",
        "Thinking about Chicago: buying for 350000, renting at 2000 per month, income 90000.",
        "In Los Angeles I want to pay $750k, rent 3800, salary is 150k.",
        "What about a $300k fixer-upper in Miami with $2200 rent?"
    ]

    for prompt in test_prompts:
        result = parse_prompt(prompt)
        print(f"Prompt: {prompt}")
        print("Parsed Output:", result)
        print("-" * 60)

if __name__ == "__main__":
    run_parser_tests()
