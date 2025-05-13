"""Configuration for mock data services."""

# Mock API keys - these will be replaced with real ones later
API_KEYS = {
    "openai": "mock-openai-key",
    "anthropic": "mock-anthropic-key",
    "attom": "mock-attom-key",
    "housecanary": "mock-housecanary-key",
    "zillow": "mock-zillow-key",
    "google_maps": "mock-google-maps-key",
    "walkscore": "mock-walkscore-key"
}

# Email for API services
API_EMAIL = "upwardhomeservices1@gmail.com"

# Mock service settings
MOCK_DATA_SETTINGS = {
    "cache_duration": 3600,  # Cache duration in seconds
    "demo_zipcodes": [
        "90210",  # Beverly Hills
        "10001",  # Manhattan
        "60601",  # Chicago Loop
        "98101",  # Seattle Downtown
        "33139"   # Miami Beach
    ],
    "refresh_interval": 300  # Data refresh interval in seconds
}

# Feature flags
FEATURES = {
    "use_mock_data": True,
    "enable_caching": True,
    "enable_ai_analysis": True,
    "enable_market_trends": True,
    "enable_comparable_search": True
}
