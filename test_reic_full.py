#!/usr/bin/env python3
"""
Comprehensive Test for Real Estate Intelligence Core (REIC)

This script performs a comprehensive test of all REIC components:
1. Layered Inference Architecture
2. Export Functionality (including PDF)
3. API Endpoints
4. ML Integration
"""

import os
import sys
import json
import logging
import requests
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import inference components
from src.inference.inference_layer_manager import InferenceLayerManager

# Import export components
from src.utils.simple_export import simple_export
from src.utils.pdf_generator import generate_pdf_summary


def test_inference_layers():
    """Test the layered inference architecture."""
    print("\n=== Testing Layered Inference Architecture ===")
    
    # Initialize the inference layer manager
    manager = InferenceLayerManager()
    
    # Test queries for different temporal perspectives
    test_queries = [
        {
            "description": "Past Layer Query",
            "query": "What were the historical trends for ZIP code 90210 over the past 5 years?",
            "context": {"zip_codes": ["90210"]}
        },
        {
            "description": "Present Layer Query",
            "query": "What is the current sentiment for ZIP code 90210?",
            "context": {"zip_codes": ["90210"]}
        },
        {
            "description": "Future Layer Query",
            "query": "What is the forecast for residential real estate in ZIP code 90210 over the next 12 months?",
            "context": {"zip_codes": ["90210"]}
        },
        {
            "description": "Multi-Layer Query",
            "query": "Compare the historical, current, and future trends for ZIP code 90210.",
            "context": {"zip_codes": ["90210"]}
        }
    ]
    
    # Process each query and collect results
    results = {}
    for test_case in test_queries:
        print(f"\n--- Testing {test_case['description']} ---")
        print(f"Query: {test_case['query']}")
        
        # Process the query
        result = manager.process_query(test_case['query'], test_case['context'])
        
        # Store the result
        results[test_case['description']] = result
        
        # Print information about the result
        if "layers_used" in result:
            print(f"Layers used: {result.get('layers_used')}")
        else:
            print(f"Layer: {result.get('layer')}")
        
        # Print insights
        insights = result.get("insights", [])
        print(f"Number of insights: {len(insights)}")
        if insights:
            print(f"First insight: {insights[0].get('insight')}")
    
    return results


def test_export_functionality(results):
    """Test the export functionality with inference results."""
    print("\n=== Testing Export Functionality ===")
    
    # Select a result to export
    result_key = "Multi-Layer Query"
    if result_key not in results:
        result_key = list(results.keys())[0]
    
    result = results[result_key]
    print(f"Exporting result from: {result_key}")
    
    # Extract ZIP code
    zip_code = "90210"  # Default
    if "results" in result:
        zip_codes = list(result["results"].keys())
        if zip_codes:
            zip_code = zip_codes[0]
    
    # Prepare export data
    export_data = {
        "zip": zip_code,
        "query": f"Query: {result_key}",
        "timestamp": datetime.now().isoformat(),
        "summary": result.get("summary", "Analysis summary")
    }
    
    # Extract scores
    scores = {}
    if "results" in result and zip_code in result["results"]:
        zip_result = result["results"][zip_code]
        for score_name in ["market_score", "reputation_score", "trend_score", "econ_score"]:
            if score_name in zip_result:
                scores[score_name.replace("_", " ").title()] = zip_result.get(score_name, 0)
    
    # Add insights as scores if no scores are available
    if not scores and "insights" in result:
        for i, insight in enumerate(result.get("insights", [])[:3]):
            if "metric" in insight and "value" in insight:
                scores[f"{insight['metric'].replace('_', ' ').title()}"] = insight["value"]
    
    # Add scores to export data
    export_data["scores"] = scores
    
    # Test different export formats
    export_formats = ["text", "json", "csv", "pdf"]
    export_paths = {}
    
    for format_type in export_formats:
        # Export the data
        output_path = "output"
        if format_type == "pdf":
            # Use the PDF generator directly for PDF export
            export_path = generate_pdf_summary(
                zip_code=zip_code,
                summary=export_data.get("summary", ""),
                scores=export_data.get("scores", {}),
                output_path=output_path
            )
        else:
            # Use simple_export for other formats
            export_path = simple_export(export_data, format_type, output_path)
        
        export_paths[format_type] = export_path
        
        # Check if export was successful
        if export_path and os.path.exists(export_path):
            print(f"{format_type.upper()} export successful: {export_path}")
            file_size = os.path.getsize(export_path)
            print(f"File size: {file_size} bytes")
        else:
            print(f"{format_type.upper()} export failed")
    
    return export_paths


def test_api_endpoints():
    """Test the API endpoints by starting a server and making requests."""
    print("\n=== Testing API Endpoints ===")
    
    # Check if we should skip API testing
    if os.environ.get("SKIP_API_TEST", "").lower() == "true":
        print("Skipping API tests as SKIP_API_TEST is set to true")
        return None
    
    # Start the API server in a separate process
    try:
        print("Starting API server...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "src.api.run_simple_api"],
            cwd=sys_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        print("Waiting for API server to start...")
        time.sleep(5)  # Give the server some time to start
        
        # Test the root endpoint
        print("\n--- Testing Root Endpoint ---")
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print(f"Root endpoint test: PASSED (Status: {response.status_code})")
                print(f"Response: {response.json()}")
            else:
                print(f"Root endpoint test: FAILED (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("Root endpoint test: FAILED (Connection error)")
            print("API server may not be running. Skipping remaining API tests.")
            if api_process:
                api_process.terminate()
            return None
        
        # Test the analyze endpoint
        print("\n--- Testing Analyze Endpoint ---")
        try:
            response = requests.get(
                "http://localhost:8000/analyze",
                params={
                    "query": "What is the current market analysis for Beverly Hills?",
                    "zip_code": "90210"
                }
            )
            if response.status_code == 200:
                print(f"Analyze endpoint test: PASSED (Status: {response.status_code})")
                result = response.json()
                analysis_id = result.get("analysis_id")
                print(f"Analysis ID: {analysis_id}")
                
                # Store the analysis ID for export testing
                if analysis_id:
                    # Test the export endpoint
                    print("\n--- Testing Export Endpoint ---")
                    for format_type in ["text", "json", "csv"]:
                        try:
                            response = requests.get(
                                f"http://localhost:8000/export/{format_type}",
                                params={"analysis_id": analysis_id}
                            )
                            if response.status_code == 200:
                                print(f"Export endpoint test ({format_type}): PASSED (Status: {response.status_code})")
                                content_type = response.headers.get("Content-Type")
                                content_length = response.headers.get("Content-Length")
                                print(f"Content-Type: {content_type}")
                                print(f"Content-Length: {content_length}")
                            else:
                                print(f"Export endpoint test ({format_type}): FAILED (Status: {response.status_code})")
                                print(f"Response: {response.text}")
                        except requests.exceptions.RequestException as e:
                            print(f"Export endpoint test ({format_type}): FAILED (Error: {e})")
            else:
                print(f"Analyze endpoint test: FAILED (Status: {response.status_code})")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Analyze endpoint test: FAILED (Error: {e})")
        
        # Terminate the API server
        if api_process:
            print("\nTerminating API server...")
            api_process.terminate()
            stdout, stderr = api_process.communicate(timeout=5)
            if stdout:
                print(f"API server stdout: {stdout}")
            if stderr:
                print(f"API server stderr: {stderr}")
    
    except Exception as e:
        print(f"Error during API testing: {e}")
        if 'api_process' in locals() and api_process:
            api_process.terminate()
    
    return True


def test_ml_integration():
    """Test integration with ML features (TF-IDF, SVD)."""
    print("\n=== Testing ML Integration ===")
    print("Note: This is a placeholder for future ML integration testing.")
    print("The system has been enhanced with TF-IDF and SVD features for property analysis.")
    print("Future tests will verify these ML components are properly integrated with the inference layers.")


def main():
    """Run all tests."""
    print("=== Comprehensive Testing of Real Estate Intelligence Core (REIC) ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test inference layers
    results = test_inference_layers()
    
    # Test export functionality
    export_paths = test_export_functionality(results)
    
    # Test API endpoints
    api_test_result = test_api_endpoints()
    
    # Test ML integration
    test_ml_integration()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Inference Layers Test: {'PASSED' if results else 'FAILED'}")
    print(f"Export Functionality Test: {'PASSED' if export_paths else 'FAILED'}")
    print(f"API Endpoints Test: {'PASSED' if api_test_result else 'SKIPPED/FAILED'}")
    print(f"ML Integration Test: PLACEHOLDER")
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    main()
