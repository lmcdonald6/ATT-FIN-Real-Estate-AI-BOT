import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.property_score import combined_score

def test_property_scoring():
    print("\nProperty Investment Score Test")
    print("=" * 50)
    
    # Test scenarios
    scenarios = [
        {
            "name": "Chicago Luxury Condo",
            "zip": "60614",
            "rent": 3500,
            "value": 550000
        },
        {
            "name": "LA Multi-Family",
            "zip": "90011",
            "rent": 4200,
            "value": 650000
        },
        {
            "name": "Atlanta Single Family",
            "zip": "30318",
            "rent": 2800,
            "value": 380000
        },
        {
            "name": "Unknown Market Property",
            "zip": "99999",
            "rent": 2000,
            "value": 300000
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
        
        print(f"ZIP Code: {result['zip']}")
        print(f"Combined Score: {result['combined_score']}/100")
        print(f"Overall Rating: {result['overall_rating']}")
        
        print("\nRental Analysis:")
        print(f"- Ratio: {result['rent_analysis']['ratio']*100:.1f}%")
        print(f"- Score: {result['rent_analysis']['score']}/100")
        print(f"- Note: {result['rent_analysis']['note']}")
        
        print("\nAppreciation Analysis:")
        print(f"- Rate: {result['appreciation_analysis']['rate']}")
        print(f"- Score: {result['appreciation_analysis']['score']}/100")
        print(f"- Note: {result['appreciation_analysis']['note']}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_property_scoring()
