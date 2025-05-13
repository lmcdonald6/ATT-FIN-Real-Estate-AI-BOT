import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the parse_prompt function to avoid loading the full app
from app import parse_prompt, client

print("\n===== Testing Parser Only =====\n")

tests = [
    "I'm looking at a $450k condo in Atlanta, expect $2600 rent and earn $100k a year.",
    "Thinking about Chicago: buying for 350000, renting at 2000 per month, income 90000.",
    "In LA, want to pay $750k, rent 3800, salary is 150k.",
    "What about a $300k fixer-upper in Miami with $2200 rent?"  # Miami isn't in our list
]

for t in tests:
    print("Prompt:", t)
    try:
        result = parse_prompt(t)
        print("Parsed:", result)
    except Exception as e:
        print("Error:", str(e))
    print("-" * 40)
