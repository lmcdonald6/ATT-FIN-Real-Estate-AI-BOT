#!/usr/bin/env python3
"""
Simple Export Module

This module provides basic export functionality for real estate analysis results
without relying on complex PDF libraries.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def export_to_text_file(data: Dict[str, Any], output_path: str = "output") -> str:
    """
    Export analysis data to a simple text file.
    
    Args:
        data: Dictionary containing analysis data
        output_path: Directory to save the file
        
    Returns:
        Path to the generated file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Extract key information
        zip_code = data.get("zip", "unknown")
        summary = data.get("summary", "No summary available")
        scores = data.get("scores", {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        filename = f"{zip_code}_analysis_{timestamp}.txt"
        filepath = os.path.join(output_path, filename)
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"REAL ESTATE ANALYSIS FOR ZIP CODE: {zip_code}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("ANALYSIS SCORES:\n")
            f.write("-" * 40 + "\n")
            for label, score in scores.items():
                f.write(f"{label}: {score}\n")
            
            f.write("\nANALYSIS SUMMARY:\n")
            f.write("-" * 40 + "\n")
            f.write(summary)
            
            f.write("\n\n" + "-" * 40 + "\n")
            f.write("Disclaimer: This analysis is for informational purposes only.\n")
            f.write("It does not constitute investment advice or legal recommendation.\n")
        
        logger.info(f"Exported analysis to text file: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error exporting to text file: {e}")
        return ""


def export_to_json_file(data: Dict[str, Any], output_path: str = "output") -> str:
    """
    Export analysis data to a JSON file.
    
    Args:
        data: Dictionary containing analysis data
        output_path: Directory to save the file
        
    Returns:
        Path to the generated file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Extract key information
        zip_code = data.get("zip", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        filename = f"{zip_code}_analysis_{timestamp}.json"
        filepath = os.path.join(output_path, filename)
        
        # Add export metadata
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "export_format": "json",
            **data
        }
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported analysis to JSON file: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error exporting to JSON file: {e}")
        return ""


def export_to_csv_file(data: Dict[str, Any], output_path: str = "output") -> str:
    """
    Export analysis data to a CSV file.
    
    Args:
        data: Dictionary containing analysis data
        output_path: Directory to save the file
        
    Returns:
        Path to the generated file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Extract key information
        zip_code = data.get("zip", "unknown")
        scores = data.get("scores", {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        filename = f"{zip_code}_analysis_{timestamp}.csv"
        filepath = os.path.join(output_path, filename)
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            # Write header
            f.write("Metric,Score\n")
            
            # Write scores
            for label, score in scores.items():
                f.write(f"{label},{score}\n")
            
            # Write summary as a note
            summary = data.get("summary", "No summary available")
            f.write(f"\nSummary,\"{summary.replace('"', '""')}\"\n")
        
        logger.info(f"Exported analysis to CSV file: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error exporting to CSV file: {e}")
        return ""


def simple_export(data: Dict[str, Any], format_type: str = "text", output_path: str = "output") -> str:
    """
    Export analysis data to the specified format using simple export functions.
    
    Args:
        data: Dictionary containing analysis data
        format_type: Export format ("text", "json", "csv", or "pdf")
        output_path: Directory to save the file
        
    Returns:
        Path to the generated file
    """
    format_type = format_type.lower()
    
    if format_type == "text" or format_type == "pdf":  # Use text as fallback for PDF
        return export_to_text_file(data, output_path)
    elif format_type == "json":
        return export_to_json_file(data, output_path)
    elif format_type == "csv":
        return export_to_csv_file(data, output_path)
    else:
        logger.warning(f"Unsupported format: {format_type}. Falling back to text format.")
        return export_to_text_file(data, output_path)


# Example usage
if __name__ == "__main__":
    # Test data
    test_data = {
        "zip": "90210",
        "summary": "This ZIP code shows strong rental potential and low risk, with a solid reputation and favorable economic outlook.",
        "scores": {
            "Market Score": 78,
            "Reputation Score": 85,
            "Trend Score": 72,
            "Econ Score": 69,
            "Investment Confidence": 80.3
        }
    }
    
    # Test exports
    text_path = simple_export(test_data, "text")
    json_path = simple_export(test_data, "json")
    csv_path = simple_export(test_data, "csv")
    
    print(f"Text export: {text_path}")
    print(f"JSON export: {json_path}")
    print(f"CSV export: {csv_path}")
