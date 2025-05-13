"""CSV Export Utility

This module provides functionality to export market analysis data to CSV format
with proper error handling, data validation, and formatting options.
"""

import csv
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVExportError(Exception):
    """Custom exception for CSV export errors"""
    pass

def format_value(value: Any) -> str:
    """Format values for CSV export"""
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, (list, dict)):
        return str(value).replace(",", ";")
    return str(value)

def validate_data(data: List[Dict[str, Any]]) -> None:
    """Validate data structure before export"""
    if not isinstance(data, list):
        raise CSVExportError("Input must be a list of dictionaries")
    if not data:
        raise CSVExportError("No data to export")
    if not all(isinstance(item, dict) for item in data):
        raise CSVExportError("All items must be dictionaries")
    if not all(data[0].keys() == item.keys() for item in data):
        raise CSVExportError("All dictionaries must have the same keys")

def export_to_csv(
    data: List[Dict[str, Any]], 
    filepath: str = "export/market_analysis.csv",
    append: bool = False,
    timestamp: bool = True
) -> Optional[str]:
    """
    Export market analysis data to CSV format.
    
    Args:
        data: List of dictionaries containing market analysis results
        filepath: Target CSV file path
        append: If True, append to existing file
        timestamp: If True, add timestamp to filename
        
    Returns:
        Path to the exported CSV file or None if export fails
        
    Raises:
        CSVExportError: If export fails due to validation or I/O errors
    """
    try:
        # Validate input data
        validate_data(data)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Add timestamp to filename if requested
        if timestamp:
            base, ext = os.path.splitext(filepath)
            filepath = f"{base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        # Get fieldnames from first item
        fieldnames = list(data[0].keys())
        
        # Determine file mode
        mode = "a" if append and os.path.exists(filepath) else "w"
        write_header = mode == "w" or not os.path.exists(filepath)
        
        # Format data for export
        formatted_data = []
        for item in data:
            formatted_item = {
                key: format_value(value)
                for key, value in item.items()
            }
            formatted_data.append(formatted_item)
        
        # Write to CSV
        with open(filepath, mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(formatted_data)
        
        logger.info(f"Successfully exported {len(data)} rows to {filepath}")
        return filepath
        
    except CSVExportError as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise CSVExportError(f"Failed to export data: {str(e)}")

def export_batch_to_csv(
    data_batches: Dict[str, List[Dict[str, Any]]],
    base_dir: str = "export",
    timestamp: bool = True
) -> Dict[str, str]:
    """
    Export multiple batches of market analysis data to separate CSV files.
    
    Args:
        data_batches: Dictionary mapping batch names to data lists
        base_dir: Base directory for export files
        timestamp: If True, add timestamp to filenames
        
    Returns:
        Dictionary mapping batch names to exported file paths
    """
    results = {}
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S") if timestamp else ""
    
    for batch_name, batch_data in data_batches.items():
        try:
            # Create sanitized filename
            safe_name = "".join(c if c.isalnum() else "_" for c in batch_name)
            filename = f"{safe_name}_{timestamp_str}.csv" if timestamp else f"{safe_name}.csv"
            filepath = os.path.join(base_dir, filename)
            
            # Export batch
            exported_path = export_to_csv(
                data=batch_data,
                filepath=filepath,
                timestamp=False  # Already included in filename
            )
            results[batch_name] = exported_path
            
        except Exception as e:
            logger.error(f"Failed to export batch '{batch_name}': {str(e)}")
            results[batch_name] = str(e)
    
    return results
