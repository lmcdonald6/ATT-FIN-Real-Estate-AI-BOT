#!/usr/bin/env python3
"""
Test PDF Export Functionality

This script tests the PDF export functionality of the Real Estate Intelligence Core.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import PDF generator
try:
    from src.utils.pdf_generator import generate_pdf_summary
    logger.info("Successfully imported PDF generator")
except ImportError as e:
    logger.error(f"Error importing PDF generator: {e}")
    sys.exit(1)

# Import simple export
try:
    from src.utils.simple_export import simple_export
    logger.info("Successfully imported simple export")
except ImportError as e:
    logger.error(f"Error importing simple export: {e}")
    sys.exit(1)


def test_pdf_generator():
    """Test the PDF generator directly."""
    print("\n=== Testing PDF Generator ===\n")
    
    # Test data
    zip_code = "90210"
    summary = "Beverly Hills (90210) is a highly desirable residential area with luxury properties. The market has shown stability with moderate growth over the past year. Current sentiment is positive, with high demand and limited inventory keeping prices elevated."
    scores = {
        "Market Score": 85,
        "Reputation Score": 92,
        "Trend Score": 78,
        "Economic Score": 88
    }
    
    # Create output directory
    output_dir = os.path.join(sys_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Generate PDF
        pdf_path = generate_pdf_summary(zip_code, summary, scores, output_dir)
        
        # Check if PDF was generated successfully
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"PDF generated successfully: {pdf_path}")
            print(f"File size: {file_size} bytes")
            return pdf_path
        else:
            print("PDF generation failed")
            return None
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        print(f"PDF generation error: {e}")
        return None


def test_simple_export_pdf():
    """Test the simple export function for PDF format."""
    print("\n=== Testing Simple Export (PDF) ===\n")
    
    # Test data
    export_data = {
        "zip": "90210",
        "query": "What is the current market analysis for Beverly Hills?",
        "timestamp": datetime.now().isoformat(),
        "summary": "Beverly Hills (90210) is a highly desirable residential area with luxury properties. The market has shown stability with moderate growth over the past year. Current sentiment is positive, with high demand and limited inventory keeping prices elevated.",
        "scores": {
            "Market Score": 85,
            "Reputation Score": 92,
            "Trend Score": 78,
            "Economic Score": 88
        }
    }
    
    # Create output directory
    output_dir = os.path.join(sys_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Export to PDF
        pdf_path = simple_export(export_data, "pdf", output_dir)
        
        # Check if PDF was exported successfully
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"PDF exported successfully: {pdf_path}")
            print(f"File size: {file_size} bytes")
            return pdf_path
        else:
            print("PDF export failed")
            return None
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        print(f"PDF export error: {e}")
        return None


def main():
    """Run all PDF export tests."""
    print("=== Testing PDF Export Functionality ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test PDF generator
    pdf_generator_path = test_pdf_generator()
    
    # Test simple export PDF
    simple_export_path = test_simple_export_pdf()
    
    # Summary
    print("\n=== Test Summary ===\n")
    print(f"PDF Generator Test: {'PASSED' if pdf_generator_path else 'FAILED'}")
    print(f"Simple Export PDF Test: {'PASSED' if simple_export_path else 'FAILED'}")
    
    print("\n=== All Tests Completed ===\n")


if __name__ == "__main__":
    main()
