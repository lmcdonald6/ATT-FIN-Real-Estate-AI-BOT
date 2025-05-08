import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")

def test_area_analysis():
    # Test comprehensive area analysis
    zipcode = "90210"  # Beverly Hills for testing
    response = requests.get(
        f"{BASE_URL}/api/v1/analyze/area/{zipcode}",
        params={
            "include_business": True,
            "include_demographics": True,
            "include_crime": True,
            "include_transit": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Area analysis for {zipcode}:")
    print(json.dumps(data, indent=2))

def test_property_valuation():
    # Test property valuation endpoint
    test_property = {
        "address": "123 Test St",
        "zipcode": "90210",
        "sqft": 2500,
        "bedrooms": 4,
        "bathrooms": 3,
        "year_built": 1990,
        "lot_size": 5000
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze/property/value",
        json=test_property
    )
    assert response.status_code == 200
    data = response.json()
    print("\n✓ Property valuation:")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    print(f"\nRunning API tests at {datetime.now().isoformat()}\n")
    try:
        test_health()
        test_area_analysis()
        test_property_valuation()
        print("\n✓ All tests passed successfully!")
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
