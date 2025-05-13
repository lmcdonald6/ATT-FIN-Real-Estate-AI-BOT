"""Test the Market Analysis Integration"""

import os
import sys
from pprint import pprint

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from modules.analyze_market import analyze_market

def test_market_analysis():
    # Test cases with different scenarios
    test_cases = [
        {
            "region": "Atlanta",
            "rent": 2400,
            "value": 330000,
            "income": 85000
        },
        {
            "region": "Chicago",
            "rent": 2200,
            "value": 290000,
            "income": 95000
        },
        {
            "region": "Los Angeles",
            "rent": 3800,
            "value": 750000,
            "income": 150000
        },
        {
            "region": "NonExistentCity",
            "rent": 2000,
            "value": 300000,
            "income": 80000
        }
    ]
    
    print("\nComprehensive Market Analysis")
    print("=" * 80)
    
    for case in test_cases:
        print(f"\nAnalyzing: {case['region']}")
        print(f"Property: ${case['value']:,} | Rent: ${case['rent']}/mo | Income: ${case['income']:,}/yr")
        print("-" * 60)
        
        result = analyze_market(**case)
        
        if result.error:
            print(f"Error: {result.error}")
            print("-" * 80)
            continue
            
        print(f"Market Phase: {result.market_phase}")
        print(f"Risk Level: {result.risk_level}")
        print("\nScores:")
        print(f"- Overall Investment Score: {result.final_score}/100")
        print(f"- Market Trend Score: {result.trend_score}/100")
        print(f"- Economic Score: {result.economic_score}/100")
        
        print("\nKey Metrics:")
        for metric, value in result.key_metrics.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"- {metric.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"- {metric.replace('_', ' ').title()}: {value:,}")
        
        if result.opportunities:
            print("\nOpportunities:")
            for opp in result.opportunities:
                print(f"+ {opp}")
                
        if result.risks:
            print("\nRisks:")
            for risk in result.risks:
                print(f"- {risk}")
        
        if result.gpt_summary:
            print("\nGPT Analysis:")
            print(result.gpt_summary)
        
        print("=" * 80)

if __name__ == "__main__":
    test_market_analysis()
