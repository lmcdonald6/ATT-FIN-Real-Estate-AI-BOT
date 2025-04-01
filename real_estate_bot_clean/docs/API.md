# Real Estate AI Bot API Documentation

## Query Types and Response Formats

### 1. Property Value Analysis
```python
Query: "what is the value of 123 Main St Bessemer?"

Response:
{
    'status': 'success',
    'response': [
        "Value Analysis:",
        "Current Valuation:",
        "- Estimated Value: $275,000",
        "- Confidence Score: 85%",
        ...
    ]
}
```

### 2. Property Details
```python
Query: "show me property details for 456 Oak Ave"

Response:
{
    'status': 'success',
    'response': [
        "Property Details:",
        "Basic Information:",
        "- 3 Bedrooms",
        "- 2 Bathrooms",
        ...
    ]
}
```

### 3. Owner Information
```python
Query: "who owns 123 Main St?"

Response:
{
    'status': 'success',
    'response': [
        "Owner Analysis:",
        "Owner Profile:",
        "- Current Owner: John Smith",
        "- Ownership Length: 8 years",
        ...
    ]
}
```

### 4. Occupancy Status
```python
Query: "is 123 Main St vacant?"

Response:
{
    'status': 'success',
    'response': [
        "Occupancy Analysis:",
        "Current Status:",
        "- Status: Occupied",
        "- Type: Owner-Occupied",
        ...
    ]
}
```

### 5. Distressed Property Analysis
```python
Query: "find distressed properties with high equity in Bessemer"

Response:
{
    'status': 'success',
    'response': [
        "Distressed Property Analysis:",
        "Property Status:",
        "- Pre-foreclosure Stage",
        "- Days in Default: 120",
        ...
    ]
}
```

### 6. Market Analysis
```python
Query: "show me market trends for Bessemer"

Response:
{
    'status': 'success',
    'response': [
        "Market Analysis Report:",
        "Price Trends & Velocity:",
        "- Median Price: $265,000",
        "- YoY Change: +6.2%",
        ...
    ]
}
```

### 7. Investment Analysis
```python
Query: "what's the maximum offer for 123 Main St?"

Response:
{
    'status': 'success',
    'response': [
        "Investment Analysis:",
        "Purchase Analysis:",
        "- Current Ask: $275,000",
        "- ARV: $325,000",
        ...
    ]
}
```

## Lead Scoring System

The bot uses a sophisticated lead scoring system with the following components:

1. Score Components (0-100):
   - Financial Distress Score (30%)
   - Time Pressure Score (25%)
   - Property Condition Score (25%)
   - Market Position Score (20%)

2. Lead Categories:
   - Hot Lead: Score >= 80
   - Warm Lead: Score 60-79
   - Cold Lead: Score < 60

## Error Handling

The bot returns error responses in the following format:
```python
{
    'status': 'error',
    'message': 'Detailed error message'
}
```

Common error types:
1. Invalid address format
2. API connectivity issues
3. Unrecognized query type
4. Missing required parameters
