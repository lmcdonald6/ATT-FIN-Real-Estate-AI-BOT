import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import parse_prompt

print("\n===== Testing Parser =====\n")

tests = [
    "I'm looking at a $450k condo in Atlanta, expect $2600 rent and earn $100k a year.",
    "Thinking about Chicago: buying for 350000, renting at 2000 per month, income 90000.",
    "In LA, want to pay $750k, rent 3800, salary is 150k.",
    "What about a $300k fixer-upper in Miami with $2200 rent?"  # Miami isn't in our list
]

for t in tests:
    print("Prompt:", t)
    print("Parsed:", parse_prompt(t))
    print("-" * 40)


print("\n===== Testing Full Analysis =====\n")

from modules.analyze_market import analyze_market
from modules.market_export_formatter import format_market_export

prompt = "I'm thinking of purchasing a $600k home in Chicago, rent it for 2700/month, and my income is 110000."
print("Prompt:", prompt)
parsed = parse_prompt(prompt)
print("Parsed:", parsed)

if parsed and not isinstance(parsed, tuple) and "error" not in parsed and all(k in parsed and parsed[k] is not None for k in ("region","value","rent")):
    income = parsed.get("income", 85000)  # Default income if not provided
    result = analyze_market(parsed["region"], parsed["rent"], parsed["value"], income)
    if hasattr(result, "__dict__"):
        export = format_market_export(result.__dict__)
        print("\nAnalysis Results:")
        for key, value in export.items():
            print(f"{key}: {value}")
    else:
        print("\nAnalysis Results:", result)
else:
    print("\nParsing incomplete or error:", parsed)
