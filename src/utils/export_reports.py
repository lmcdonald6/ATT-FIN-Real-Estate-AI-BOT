#!/usr/bin/env python3
"""
Export Reports Module

This module provides functionality for exporting real estate analysis results
to various formats including PDF, CSV, and Excel.
"""

import os
import sys
import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import required libraries with fallbacks
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    logger.warning("FPDF package not installed. PDF export will be limited.")
    FPDF_AVAILABLE = False

try:
    import xlsxwriter
    EXCEL_AVAILABLE = True
except ImportError:
    logger.warning("XlsxWriter package not installed. Excel export will be limited.")
    EXCEL_AVAILABLE = False


def generate_pdf_summary(zip_code: str, summary: str, scores: dict, output_path="output") -> str:
    """
    Generate a PDF summary of real estate analysis results.
    
    Args:
        zip_code: ZIP code of the analyzed area
        summary: Text summary of the analysis
        scores: Dictionary of scores (market, reputation, etc.)
        output_path: Directory to save the PDF in
        
    Returns:
        Path to the generated PDF file
    """
    if not FPDF_AVAILABLE:
        logger.error("FPDF package not installed. Cannot generate PDF.")
        return ""
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{zip_code}_real_estate_summary_{timestamp}.pdf"
        filepath = os.path.join(output_path, filename)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add header
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(200, 10, txt=f"Real Estate Analysis for ZIP: {zip_code}", ln=True, align="C")
        pdf.ln(5)
        
        # Add timestamp
        pdf.set_font("Arial", "I", size=10)
        pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(10)
        
        # Add scores section
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="Analysis Scores", ln=True)
        pdf.ln(5)
        
        # Add scores table
        pdf.set_font("Arial", size=12)
        for label, score in scores.items():
            # Format score as integer if it's a whole number
            if isinstance(score, (int, float)):
                score_str = str(int(score)) if score == int(score) else f"{score:.1f}"
            else:
                score_str = str(score)
                
            pdf.cell(100, 10, txt=label, border=1)
            pdf.cell(100, 10, txt=score_str, border=1, ln=True)
        
        pdf.ln(10)
        
        # Add summary section
        pdf.set_font("Arial", "B", size=14)
        pdf.cell(200, 10, txt="Summary", ln=True)
        pdf.ln(5)
        
        # Add summary text
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=summary)
        
        # Add disclaimer
        pdf.ln(10)
        pdf.set_font("Arial", "I", size=10)
        pdf.set_text_color(120)
        disclaimer = "Disclaimer: This summary is for informational purposes only and does not constitute investment advice or real estate services. Always consult a licensed professional."
        pdf.multi_cell(0, 8, txt=disclaimer)
        
        # Save PDF
        pdf.output(filepath)
        logger.info(f"Generated PDF report: {filepath}")
        
        return filepath
    
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return ""


def export_to_csv(data: Dict[str, Any], output_path="output") -> str:
    """
    Export analysis results to CSV format.
    
    Args:
        data: Analysis results dictionary
        output_path: Directory to save the CSV in
        
    Returns:
        Path to the generated CSV file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_code = data.get("zip", "unknown")
        filename = f"{zip_code}_analysis_{timestamp}.csv"
        filepath = os.path.join(output_path, filename)
        
        # Flatten the data structure for CSV
        flattened_data = {}
        
        # Add basic fields
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                flattened_data[key] = value
        
        # Add investment profile if available
        if "investment_profile" in data and isinstance(data["investment_profile"], dict):
            for key, value in data["investment_profile"].items():
                flattened_data[f"investment_{key}"] = value
        
        # Add metro adjustments if available
        if "metro_adjustments" in data and isinstance(data["metro_adjustments"], dict):
            for key, value in data["metro_adjustments"].items():
                flattened_data[f"adjustment_{key}"] = value
        
        # Write to CSV
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = flattened_data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow(flattened_data)
        
        logger.info(f"Exported data to CSV: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return ""


def export_to_excel(data: Dict[str, Any], output_path="output") -> str:
    """
    Export analysis results to Excel format.
    
    Args:
        data: Analysis results dictionary
        output_path: Directory to save the Excel file in
        
    Returns:
        Path to the generated Excel file
    """
    if not EXCEL_AVAILABLE:
        logger.error("XlsxWriter package not installed. Cannot export to Excel.")
        return ""
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_code = data.get("zip", "unknown")
        filename = f"{zip_code}_analysis_{timestamp}.xlsx"
        filepath = os.path.join(output_path, filename)
        
        # Create workbook and worksheet
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet("Analysis Results")
        
        # Add header formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#4B5320',
            'border': 1
        })
        
        # Add data formats
        data_format = workbook.add_format({
            'border': 1
        })
        
        # Add numeric format
        number_format = workbook.add_format({
            'border': 1,
            'num_format': '0.0'
        })
        
        # Write basic information
        worksheet.write(0, 0, "ZIP Code", header_format)
        worksheet.write(0, 1, data.get("zip", "Unknown"), data_format)
        
        worksheet.write(1, 0, "Metro Area", header_format)
        worksheet.write(1, 1, data.get("metro", "Unknown"), data_format)
        
        worksheet.write(2, 0, "Analysis Type", header_format)
        worksheet.write(2, 1, data.get("type", "Unknown"), data_format)
        
        worksheet.write(3, 0, "Timestamp", header_format)
        worksheet.write(3, 1, data.get("timestamp", datetime.now().isoformat()), data_format)
        
        # Write scores section
        row = 5
        worksheet.write(row, 0, "Analysis Scores", header_format)
        row += 1
        
        # Write score headers
        worksheet.write(row, 0, "Metric", header_format)
        worksheet.write(row, 1, "Value", header_format)
        row += 1
        
        # Write individual scores
        for score_name in ["market_score", "reputation_score", "trend_score", "econ_score"]:
            if score_name in data:
                worksheet.write(row, 0, score_name.replace("_", " ").title(), data_format)
                worksheet.write(row, 1, data.get(score_name, 0), number_format)
                row += 1
        
        # Write investment profile if available
        if "investment_profile" in data and isinstance(data["investment_profile"], dict):
            row += 1
            worksheet.write(row, 0, "Investment Profile", header_format)
            row += 1
            
            profile = data["investment_profile"]
            worksheet.write(row, 0, "Confidence Score", data_format)
            worksheet.write(row, 1, profile.get("confidence_score", 0), number_format)
            row += 1
            
            worksheet.write(row, 0, "Rating", data_format)
            worksheet.write(row, 1, profile.get("rating", "N/A"), data_format)
            row += 1
            
            worksheet.write(row, 0, "Recommendation", data_format)
            worksheet.write(row, 1, profile.get("recommendation", "N/A"), data_format)
            row += 1
        
        # Write metro adjustments if available
        if "metro_adjustments" in data and isinstance(data["metro_adjustments"], dict):
            row += 1
            worksheet.write(row, 0, "Metro Adjustments", header_format)
            row += 1
            
            adjustments = data["metro_adjustments"]
            for key, value in adjustments.items():
                worksheet.write(row, 0, key.replace("_", " ").title(), data_format)
                worksheet.write(row, 1, value, number_format)
                row += 1
        
        # Add summary if available
        if "market_summary" in data or "buzz_summary" in data:
            row += 2
            worksheet.write(row, 0, "Summaries", header_format)
            row += 1
            
            if "market_summary" in data:
                worksheet.write(row, 0, "Market Summary", data_format)
                worksheet.write(row, 1, data.get("market_summary", ""), data_format)
                row += 1
            
            if "buzz_summary" in data:
                worksheet.write(row, 0, "Sentiment Summary", data_format)
                worksheet.write(row, 1, data.get("buzz_summary", ""), data_format)
                row += 1
        
        # Auto-fit columns
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 50)
        
        # Close workbook
        workbook.close()
        
        logger.info(f"Exported data to Excel: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        return ""


def export_analysis_result(data: Dict[str, Any], format_type: str = "pdf", output_path="output") -> str:
    """
    Export analysis results to the specified format.
    
    Args:
        data: Analysis results dictionary
        format_type: Export format ("pdf", "csv", or "excel")
        output_path: Directory to save the file in
        
    Returns:
        Path to the generated file
    """
    # Extract key information for PDF summary
    zip_code = data.get("zip", "unknown")
    
    # Build summary text
    summary_parts = []
    
    if "market_summary" in data:
        summary_parts.append(f"Market Analysis: {data['market_summary']}")
    
    if "buzz_summary" in data:
        summary_parts.append(f"Sentiment Analysis: {data['buzz_summary']}")
    
    # Add investment recommendation if available
    if "investment_profile" in data and isinstance(data["investment_profile"], dict):
        profile = data["investment_profile"]
        summary_parts.append(f"Investment Recommendation: {profile.get('recommendation', 'N/A')}")
    
    summary = "\n\n".join(summary_parts)
    
    # Build scores dictionary
    scores = {}
    
    for score_name in ["market_score", "reputation_score", "trend_score", "econ_score"]:
        if score_name in data:
            scores[score_name.replace("_", " ").title()] = data.get(score_name, 0)
    
    # Add investment confidence score if available
    if "investment_profile" in data and isinstance(data["investment_profile"], dict):
        profile = data["investment_profile"]
        scores["Investment Confidence"] = profile.get("confidence_score", 0)
        scores["Rating"] = profile.get("rating", "N/A")
    
    # Export in the specified format
    if format_type.lower() == "pdf":
        return generate_pdf_summary(zip_code, summary, scores, output_path)
    elif format_type.lower() == "csv":
        return export_to_csv(data, output_path)
    elif format_type.lower() == "excel":
        return export_to_excel(data, output_path)
    else:
        logger.error(f"Unsupported export format: {format_type}")
        return ""


if __name__ == "__main__":
    # Test functionality
    print("Export Reports Module Test")
    print("=" * 30)
    
    # Create test data
    test_data = {
        "type": "investment_analysis",
        "timestamp": datetime.now().isoformat(),
        "zip": "30318",
        "metro": "atlanta",
        "market_score": 78,
        "reputation_score": 85,
        "trend_score": 72,
        "econ_score": 69,
        "market_summary": "This area shows strong market fundamentals with steady growth.",
        "buzz_summary": "Sentiment analysis indicates positive community feedback and improving reputation.",
        "investment_profile": {
            "confidence_score": 80.3,
            "rating": "B+",
            "recommendation": "Moderate Buy"
        },
        "metro_adjustments": {
            "vacancy_penalty": 1.0,
            "crime_penalty": 2.0,
            "permit_bonus": 4.0
        }
    }
    
    # Test PDF export
    if FPDF_AVAILABLE:
        print("\nTesting PDF export...")
        pdf_path = export_analysis_result(test_data, "pdf")
        print(f"PDF exported to: {pdf_path}")
    
    # Test CSV export
    print("\nTesting CSV export...")
    csv_path = export_analysis_result(test_data, "csv")
    print(f"CSV exported to: {csv_path}")
    
    # Test Excel export
    if EXCEL_AVAILABLE:
        print("\nTesting Excel export...")
        excel_path = export_analysis_result(test_data, "excel")
        print(f"Excel exported to: {excel_path}")
