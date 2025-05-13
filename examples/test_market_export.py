"""Test the Market Export Formatter"""

import os
import sys
import json
from pprint import pprint

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from modules.analyze_market import analyze_market
from modules.market_export_formatter import format_market_export

def test_market_export():
    # Test cases
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
    
    print("\nMarket Analysis Export Test")
    print("=" * 80)
    
    for case in test_cases:
        print(f"\nProcessing: {case['region']}")
        print("-" * 50)
        
        # Get market analysis
        analysis = analyze_market(**case)
        
        # Format for export
        export_data = format_market_export({
            "region": analysis.region,
            "final_score": analysis.final_score,
            "market_phase": analysis.market_phase,
            "risk_level": analysis.risk_level,
            "trend_score": analysis.trend_score,
            "economic_score": analysis.economic_score,
            "investment_score": analysis.investment_score,
            "key_metrics": analysis.key_metrics,
            "opportunities": analysis.opportunities,
            "risks": analysis.risks,
            "gpt_summary": analysis.gpt_summary,
            "error": analysis.error
        })
        
        # Pretty print the export data
        print("\nExport Data:")
        for key, value in export_data.items():
            if isinstance(value, (list, dict)):
                print(f"\n{key}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"  - {item}")
                else:
                    for k, v in value.items():
                        print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
        
        # Save to JSON file
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, f"{case['region'].lower()}_market_analysis.json")
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"\nSaved to: {json_path}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_market_export()
