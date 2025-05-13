"""Test the CSV Export Utility"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from modules.analyze_market import analyze_market
from modules.market_export_formatter import format_market_export
from utils.export_to_csv import export_to_csv, export_batch_to_csv, CSVExportError

def test_csv_export():
    # Test data
    test_cases = [
        {
            "region": "Atlanta",
            "rent": 2400,
            "value": 330000,
            "income": 85000
        },
        {
            "region": "Chicago",
            "rent": 2200,
            "value": 290000,
            "income": 95000
        },
        {
            "region": "Los Angeles",
            "rent": 3800,
            "value": 750000,
            "income": 150000
        }
    ]
    
    print("\nCSV Export Test")
    print("=" * 80)
    
    # Get market analysis results
    analysis_results = []
    for case in test_cases:
        analysis = analyze_market(**case)
        export_data = format_market_export(analysis.__dict__)
        analysis_results.append(export_data)
    
    # Test single file export
    try:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        filepath = os.path.join(output_dir, "market_analysis.csv")
        
        result = export_to_csv(
            data=analysis_results,
            filepath=filepath,
            timestamp=True
        )
        print(f"\nSingle file export successful: {result}")
        
    except CSVExportError as e:
        print(f"\nSingle file export failed: {str(e)}")
    
    # Test batch export
    try:
        # Group data by risk level
        risk_groups = {}
        for result in analysis_results:
            risk_level = result.get("risk_level", "unknown").lower()
            if risk_level not in risk_groups:
                risk_groups[risk_level] = []
            risk_groups[risk_level].append(result)
        
        # Export each risk group
        batch_results = export_batch_to_csv(
            data_batches=risk_groups,
            base_dir=output_dir,
            timestamp=True
        )
        
        print("\nBatch export results:")
        for group, path in batch_results.items():
            print(f"- {group}: {path}")
            
    except Exception as e:
        print(f"\nBatch export failed: {str(e)}")
    
    print("\nTesting error handling:")
    
    # Test empty data
    try:
        export_to_csv([], filepath="test_empty.csv")
    except CSVExportError as e:
        print(f"Empty data test: {str(e)}")
    
    # Test invalid data structure
    try:
        export_to_csv([1, 2, 3], filepath="test_invalid.csv")
    except CSVExportError as e:
        print(f"Invalid data test: {str(e)}")
    
    # Test inconsistent keys
    try:
        invalid_data = [
            {"a": 1, "b": 2},
            {"b": 2, "c": 3}
        ]
        export_to_csv(invalid_data, filepath="test_keys.csv")
    except CSVExportError as e:
        print(f"Inconsistent keys test: {str(e)}")

if __name__ == "__main__":
    test_csv_export()
