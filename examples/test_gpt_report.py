"""Test the GPT Property Report Generator"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Import after loading env vars
from modules.property_score import combined_score
from modules.gpt_report import generate_property_report

def main():
    # Test property in Atlanta
    zip_code = "30318"
    rent = 2400
    value = 330000

    print("\nAnalyzing Atlanta Property")
    print("=" * 50)
    print(f"ZIP Code: {zip_code}")
    print(f"Monthly Rent: ${rent:,}")
    print(f"Property Value: ${value:,}")
    
    # Get property analysis
    analysis = combined_score(zip_code, rent, value)
    
    # Generate report
    result = generate_property_report(analysis)
    
    if result['success']:
        print("\nInvestment Analysis Report:")
        print("=" * 30)
        print(result['report'])
        print("-" * 50)
    else:
        print(f"Error: {result['error']}")
        if 'OpenAI API error' in str(result['error']):
            print("\nNOTE: Make sure to set your OpenAI API key in the .env file:")
            print("OPENAI_API_KEY=your_actual_api_key_here")

if __name__ == "__main__":
    main()
