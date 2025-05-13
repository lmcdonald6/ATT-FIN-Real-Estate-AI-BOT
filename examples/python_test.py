import requests
import json

def test_property_analysis():
    # Basic analysis
    data = {
        "zip": "60614",
        "budget": 500000,
        "preferences": {}
    }
    response = requests.post(
        "http://localhost:8000/api/v1/analyze/property",
        json=data
    )
    print("\nBasic Analysis:")
    print(json.dumps(response.json(), indent=2))

    # Analysis with preferences
    data_with_prefs = {
        "zip": "60614",
        "budget": 500000,
        "preferences": {
            "property_type": "single_family",
            "min_bedrooms": 3,
            "max_price": 600000
        }
    }
    response = requests.post(
        "http://localhost:8000/api/v1/analyze/property",
        json=data_with_prefs
    )
    print("\nAnalysis with Preferences:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_property_analysis()
