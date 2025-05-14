#!/usr/bin/env python3
"""
Test script for the Real Estate Intelligence API endpoints.

This script tests the API endpoints by making requests to a running API server.
Make sure to start the API server before running this script:
    python -m src.api.run_api_server
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# API base URL
API_BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    
    # Make the request
    response = requests.get(f"{API_BASE_URL}/")
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"API Name: {data.get('name')}")
        print(f"API Version: {data.get('version')}")
        print(f"API Status: {data.get('status')}")
        print(f"Available Endpoints: {', '.join(data.get('endpoints', []))}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_conversation_query():
    """Test the conversation query endpoint."""
    print("\n=== Testing Conversation Query Endpoint ===")
    
    # Prepare the request
    query = "What's the investment potential for ZIP code 90210 over the next 5 years?"
    payload = {
        "query": query,
        "context": {}
    }
    
    # Make the request
    response = requests.post(f"{API_BASE_URL}/conversation/query", json=payload)
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Query: {data.get('query')}")
        print(f"Intent: {data.get('intent')}")
        print(f"Analysis ID: {data.get('analysis_id')}")
        
        # Print a snippet of the summary
        summary = data.get('summary', '')
        if summary:
            print(f"Summary snippet: {summary[:100]}...")
        
        # Save the analysis ID for later use
        analysis_id = data.get('analysis_id')
        return analysis_id
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_market_trends():
    """Test the market trends endpoint."""
    print("\n=== Testing Market Trends Endpoint ===")
    
    # Prepare the request
    params = {
        "zip_code": "90210",
        "years_back": 5
    }
    
    # Make the request
    response = requests.get(f"{API_BASE_URL}/market/trends", params=params)
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        
        # Check if the analysis contains past layer data
        analysis = data.get('analysis', {})
        if 'layer' in analysis and analysis['layer'] == 'past':
            print("Correctly used Past layer for trends analysis")
        
        # Print time range
        time_range = analysis.get('time_range', {})
        if time_range:
            print(f"Time Range: {time_range.get('years')} years from {time_range.get('start')} to {time_range.get('end')}")
        
        # Save the analysis ID for later use
        analysis_id = data.get('analysis_id')
        return analysis_id
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_sentiment_scores():
    """Test the sentiment scores endpoint."""
    print("\n=== Testing Sentiment Scores Endpoint ===")
    
    # Prepare the request
    payload = {
        "zip_code": "90210",
        "streets": ["Main Street", "Beverly Drive"],
        "refresh": False
    }
    
    # Make the request
    response = requests.post(f"{API_BASE_URL}/sentiment/scores", json=payload)
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        
        # Check if the analysis contains present layer data
        analysis = data.get('analysis', {})
        if 'layer' in analysis and analysis['layer'] == 'present':
            print("Correctly used Present layer for sentiment analysis")
        
        # Print insights
        insights = analysis.get('insights', [])
        if insights:
            print(f"Number of insights: {len(insights)}")
            print(f"First insight: {insights[0].get('insight')}")
        
        # Save the analysis ID for later use
        analysis_id = data.get('analysis_id')
        return analysis_id
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_market_forecasts():
    """Test the market forecasts endpoint."""
    print("\n=== Testing Market Forecasts Endpoint ===")
    
    # Prepare the request
    params = {
        "zip_code": "90210",
        "months_ahead": 12,
        "investment_type": "residential"
    }
    
    # Make the request
    response = requests.get(f"{API_BASE_URL}/market/forecasts", params=params)
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        
        # Check if the analysis contains future layer data
        analysis = data.get('analysis', {})
        if 'layer' in analysis and analysis['layer'] == 'future':
            print("Correctly used Future layer for forecast analysis")
        
        # Print horizon
        if 'horizon_months' in analysis:
            print(f"Forecast Horizon: {analysis.get('horizon_months')} months")
        
        # Print insights
        insights = analysis.get('insights', [])
        if insights:
            print(f"Number of insights: {len(insights)}")
            print(f"First insight: {insights[0].get('insight')}")
        
        # Save the analysis ID for later use
        analysis_id = data.get('analysis_id')
        return analysis_id
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_discovery_opportunities():
    """Test the discovery opportunities endpoint."""
    print("\n=== Testing Discovery Opportunities Endpoint ===")
    
    # Prepare the request
    params = {
        "metro_area": "Los Angeles",
        "min_sentiment": 70.0,
        "max_price_to_income": 4.0
    }
    
    # Make the request
    response = requests.get(f"{API_BASE_URL}/discovery/opportunities", params=params)
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        
        # Print summary
        summary = data.get('summary', '')
        if summary:
            print(f"Summary snippet: {summary[:100]}...")
        
        # Save the analysis ID for later use
        analysis_id = data.get('analysis_id')
        return analysis_id
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_export_pdf(analysis_id):
    """Test the export PDF endpoint."""
    print("\n=== Testing Export PDF Endpoint ===")
    
    if not analysis_id:
        print("No analysis ID provided, skipping export test")
        return
    
    # Prepare the request
    payload = {
        "analysis_id": analysis_id,
        "format": "pdf"
    }
    
    # Make the request
    response = requests.post(f"{API_BASE_URL}/export/pdf", json=payload)
    
    # Check the response
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        print(f"Content Type: {response.headers.get('Content-Type')}")
        print(f"Content Disposition: {response.headers.get('Content-Disposition')}")
        
        # Save the PDF
        filename = f"test_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"PDF saved as {filename}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def main():
    """Run all tests."""
    print("=== Testing Real Estate Intelligence API ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Test the root endpoint
    test_root_endpoint()
    
    # Test the conversation query endpoint
    conversation_id = test_conversation_query()
    
    # Test the market trends endpoint
    trends_id = test_market_trends()
    
    # Test the sentiment scores endpoint
    sentiment_id = test_sentiment_scores()
    
    # Test the market forecasts endpoint
    forecast_id = test_market_forecasts()
    
    # Test the discovery opportunities endpoint
    discovery_id = test_discovery_opportunities()
    
    # Test the export PDF endpoint with one of the analysis IDs
    export_id = conversation_id or trends_id or sentiment_id or forecast_id or discovery_id
    test_export_pdf(export_id)
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    main()
