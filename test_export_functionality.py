#!/usr/bin/env python3
"""
Test script for the Real Estate Intelligence API export functionality.

This script tests the export endpoints by making requests to a running API server.
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

def test_conversation_and_export():
    """Test the conversation query endpoint and then export the results."""
    print("\n=== Testing Conversation Query and Export ===")
    
    # Prepare the request
    query = "What's the investment potential for ZIP code 90210 over the next 5 years?"
    payload = {
        "query": query,
        "context": {}
    }
    
    # Make the request
    print(f"Making request to /conversation/query with query: {query}")
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
        
        # Save the analysis ID for export
        analysis_id = data.get('analysis_id')
        if analysis_id:
            print(f"\nExporting analysis {analysis_id} to PDF...")
            test_export_pdf(analysis_id)
        else:
            print("No analysis ID found in response")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_export_pdf(analysis_id):
    """Test the export PDF endpoint."""
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
        
        # Check if the file exists and has content
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            print(f"Successfully created PDF file with {os.path.getsize(filename)} bytes")
        else:
            print(f"Error: PDF file is empty or does not exist")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def main():
    """Run the export functionality test."""
    print("=== Testing Real Estate Intelligence API Export Functionality ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Test conversation query and export
    test_conversation_and_export()
    
    print("\n=== Test Completed ===")


if __name__ == "__main__":
    main()
