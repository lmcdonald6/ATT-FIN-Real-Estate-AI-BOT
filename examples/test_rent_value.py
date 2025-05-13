from src.modules.rent_value_calc import rent_value_score

def test_rent_value_calculator():
    # Test cases
    scenarios = [
        {
            "name": "High Yield Property",
            "rent": 3000,
            "value": 350000  # 10.3% yield
        },
        {
            "name": "Good Yield Property",
            "rent": 2500,
            "value": 400000  # 7.5% yield
        },
        {
            "name": "Average Yield Property",
            "rent": 2000,
            "value": 450000  # 5.3% yield
        },
        {
            "name": "Low Yield Property",
            "rent": 1500,
            "value": 500000  # 3.6% yield
        }
    ]

    print("\nRent-to-Value Analysis Test")
    print("=" * 50)
    
    for scenario in scenarios:
        result = rent_value_score(scenario["rent"], scenario["value"])
        print(f"\n{scenario['name']}:")
        print(f"Monthly Rent: ${scenario['rent']}")
        print(f"Property Value: ${scenario['value']}")
        print(f"Annual Yield: {result['ratio']*100:.1f}%")
        print(f"Score: {result['score']}/100")
        print(f"Analysis: {result['note']}")

if __name__ == "__main__":
    test_rent_value_calculator()
