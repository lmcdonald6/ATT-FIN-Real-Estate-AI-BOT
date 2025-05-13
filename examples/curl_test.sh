#!/bin/bash

# Basic property analysis
curl -X POST http://localhost:8000/api/v1/analyze/property \
  -H "Content-Type: application/json" \
  -d '{"zip": "60614", "budget": 500000, "preferences": {}}'

# Analysis with preferences
curl -X POST http://localhost:8000/api/v1/analyze/property \
  -H "Content-Type: application/json" \
  -d '{
    "zip": "60614",
    "budget": 500000,
    "preferences": {
      "property_type": "single_family",
      "min_bedrooms": 3,
      "max_price": 600000
    }
  }'
