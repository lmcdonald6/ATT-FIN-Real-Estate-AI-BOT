import sys
import os
import json
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.property_score import combined_score

def format_result(result: Dict[str, Any]) -> str:
    """Format the result for clean output"""
    return json.dumps(result, indent=2)

def test_combined_scoring():
    print("\nCombined Property Score Test")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Chicago Property",
            "zip": "60614",
            "rent": 3000,
            "value": 480000  # 7.5% yield
        },
        {
            "name": "LA Property",
            "zip": "90011",
            "rent": 2200,
            "value": 395000  # 6.7% yield
        },
        {
            "name": "Atlanta Property",
            "zip": "30318",
            "rent": 2400,
            "value": 330000  # 8.7% yield
        }
    ]

    for scenario in scenarios:
        print(f"\nAnalyzing: {scenario['name']}")
        print("-" * 30)
        
        result = combined_score(
            scenario["zip"],
            scenario["rent"],
            scenario["value"]
        )
        
        # Calculate annual yield for reference
        annual_yield = (scenario["rent"] * 12 / scenario["value"]) * 100
        
        print(f"ZIP Code: {result['zip']}")
        print(f"Monthly Rent: ${scenario['rent']:,}")
        print(f"Property Value: ${scenario['value']:,}")
        print(f"Annual Yield: {annual_yield:.1f}%")
        print(f"\nOverall Score: {result['combined_score']}/100")
        print(f"Rating: {result['overall_rating']}")
        
        print(f"\nRisk Analysis:")
        print(f"Vacancy Rate: {result['risk_analysis']['vacancy_rate']}")
        print(f"Tax Burden: {result['risk_analysis']['tax_burden']}")
        print(f"Crime Index: {result['risk_analysis']['crime_index']} per 1000")
        print(f"Price Volatility: {result['risk_analysis']['price_volatility']}")
        
        if result['risk_analysis']['score_penalty'] != 0:
            print(f"\nRisk Penalties: {result['risk_analysis']['score_penalty']} points total")
            if result['risk_analysis']['details']['high_vacancy']:
                print("- High vacancy rate (-10 points)")
            if result['risk_analysis']['details']['high_tax']:
                print("- High tax burden (-5 points)")
            if result['risk_analysis']['details']['high_crime']:
                print("- High crime rate (-4 to -8 points)")
            if result['risk_analysis']['details']['high_volatility']:
                print("- High price volatility (-3 to -7 points)")
        
        print(f"\nDetailed Analysis:")
        print(f"Rental Score: {result['rent_analysis']['score']}/100")
        print(f"- {result['rent_analysis']['note']}")
        print(f"\nAppreciation Score: {result['appreciation_analysis']['score']}/100")
        print(f"- {result['appreciation_analysis']['note']}")
        print(f"- Historical Rate: {result['appreciation_analysis']['rate']}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_combined_scoring()
