#!/usr/bin/env python3
"""
Test script for the Layered Inference Architecture.

This script tests the Past, Present, and Future inference layers
as well as the InferenceLayerManager.
"""

import os
import sys
import json
from datetime import datetime

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import the inference layers
from src.inference.past_layer import PastInferenceLayer
from src.inference.present_layer import PresentInferenceLayer
from src.inference.future_layer import FutureInferenceLayer
from src.inference.inference_layer_manager import InferenceLayerManager


def test_past_layer():
    """Test the Past inference layer."""
    print("\n=== Testing Past Inference Layer ===")
    
    # Initialize the layer
    past_layer = PastInferenceLayer()
    
    # Test query
    query = "What were the historical trends for ZIP code 90210 over the past 5 years?"
    context = {
        "zip_codes": ["90210"],
        "years_back": 5
    }
    
    # Process the query
    result = past_layer.process_query(query, context)
    
    # Print the result
    print(f"Query: {query}")
    print(f"Result layer: {result.get('layer')}")
    print(f"Time range: {result.get('time_range')}")
    print(f"Number of insights: {len(result.get('insights', []))}")
    
    # Print the first insight if available
    insights = result.get("insights", [])
    if insights:
        print(f"First insight: {insights[0].get('insight')}")
    
    return result


def test_present_layer():
    """Test the Present inference layer."""
    print("\n=== Testing Present Inference Layer ===")
    
    # Initialize the layer
    present_layer = PresentInferenceLayer()
    
    # Test query
    query = "What is the current sentiment for Main Street in ZIP code 90210?"
    context = {
        "zip_codes": ["90210"],
        "streets": ["Main Street"]
    }
    
    # Process the query
    result = present_layer.process_query(query, context)
    
    # Print the result
    print(f"Query: {query}")
    print(f"Result layer: {result.get('layer')}")
    print(f"Timestamp: {result.get('timestamp')}")
    print(f"Number of insights: {len(result.get('insights', []))}")
    
    # Print the first insight if available
    insights = result.get("insights", [])
    if insights:
        print(f"First insight: {insights[0].get('insight')}")
    
    return result


def test_future_layer():
    """Test the Future inference layer."""
    print("\n=== Testing Future Inference Layer ===")
    
    # Initialize the layer
    future_layer = FutureInferenceLayer()
    
    # Test query
    query = "What is the forecast for residential real estate in ZIP code 90210 over the next 12 months?"
    context = {
        "zip_codes": ["90210"],
        "months_ahead": 12,
        "investment_type": "residential"
    }
    
    # Process the query
    result = future_layer.process_query(query, context)
    
    # Print the result
    print(f"Query: {query}")
    print(f"Result layer: {result.get('layer')}")
    print(f"Horizon months: {result.get('horizon_months')}")
    print(f"Number of insights: {len(result.get('insights', []))}")
    
    # Print the first insight if available
    insights = result.get("insights", [])
    if insights:
        print(f"First insight: {insights[0].get('insight')}")
    
    return result


def test_inference_manager():
    """Test the Inference Layer Manager."""
    print("\n=== Testing Inference Layer Manager ===")
    
    # Initialize the manager
    manager = InferenceLayerManager()
    
    # Test queries for each temporal layer
    past_query = "What were the historical trends for ZIP code 90210 over the past 5 years?"
    present_query = "What is the current sentiment for Main Street in ZIP code 90210?"
    future_query = "What is the forecast for residential real estate in ZIP code 90210 over the next 12 months?"
    combined_query = "Compare the historical, current, and future trends for ZIP code 90210."
    
    # Test the manager with each query
    for query_name, query in [
        ("Past", past_query),
        ("Present", present_query),
        ("Future", future_query),
        ("Combined", combined_query)
    ]:
        print(f"\n--- Testing {query_name} Query ---")
        print(f"Query: {query}")
        
        # Process the query
        result = manager.process_query(query)
        
        # Print the result
        if "layers_used" in result:
            print(f"Layers used: {result.get('layers_used')}")
        else:
            print(f"Layer: {result.get('layer')}")
        
        print(f"Number of insights: {len(result.get('insights', []))}")
        
        # Print the first insight if available
        insights = result.get("insights", [])
        if insights:
            print(f"First insight: {insights[0].get('insight')}")
    
    return result


def main():
    """Run all tests."""
    print("=== Testing Layered Inference Architecture ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test each layer
    past_result = test_past_layer()
    present_result = test_present_layer()
    future_result = test_future_layer()
    
    # Test the manager
    manager_result = test_inference_manager()
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    main()
