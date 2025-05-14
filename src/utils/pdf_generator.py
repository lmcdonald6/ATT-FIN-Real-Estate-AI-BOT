#!/usr/bin/env python3
"""
PDF Generator

This module provides functionality for generating PDF reports
for real estate analysis results.
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_pdf_summary(zip_code: str, summary: str, scores: Dict[str, Any], output_path: Optional[str] = "output") -> str:
    """
    Generate a PDF summary of real estate analysis results.
    
    Args:
        zip_code: The ZIP code analyzed
        summary: Text summary of the analysis
        scores: Dictionary of scores (market, reputation, etc.)
        output_path: Directory to save the PDF
        
    Returns:
        Path to the generated PDF file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Create filename and filepath
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{zip_code}_real_estate_summary_{timestamp}.pdf"
    filepath = os.path.join(output_path, filename)
    
    try:
        # Import reportlab components here to avoid import errors
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        
        # Filepath was already created above
        
        # Create canvas
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, f"Real Estate Summary for ZIP: {zip_code}")
        
        # Add timestamp
        c.setFont("Helvetica", 10)
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawString(72, height - 90, f"Generated: {timestamp_str}")
        
        # Add scores
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, height - 120, "Analysis Scores:")
        
        c.setFont("Helvetica", 12)
        y = height - 140
        for label, score in scores.items():
            # Format the label for display
            display_label = label.replace("_", " ").title()
            
            # Format the score
            if isinstance(score, (int, float)):
                display_score = f"{score:.1f}" if isinstance(score, float) else str(score)
            else:
                display_score = str(score)
            
            c.drawString(72, y, f"{display_label}: {display_score}")
            y -= 18
        
        # Add summary
        c.setFont("Helvetica-Bold", 12)
        y -= 24
        c.drawString(72, y, "Analysis Summary:")
        
        # Add summary text
        c.setFont("Helvetica", 11)
        y -= 24
        text = c.beginText(72, y)
        text.setLeading(16)  # Line spacing
        
        # Split summary into lines and add to text object
        for line in summary.split("\n"):
            text.textLine(line)
        
        c.drawText(text)
        
        # Add disclaimer
        y = text.getY() - 30
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(72, y, "Disclaimer: This summary is for informational purposes only.")
        c.drawString(72, y - 12, "It does not constitute investment advice or legal recommendation.")
        
        # Add footer with page number
        c.setFont("Helvetica", 9)
        c.drawString(width / 2 - 40, 30, f"Page 1 of 1")
        
        # Save the PDF
        c.save()
        
        logger.info(f"Generated PDF report: {filepath}")
        return filepath
        
    except ImportError as e:
        logger.error(f"ReportLab import error: {e}")
        # Fallback to text file if PDF generation fails
        try:
            text_filename = f"{zip_code}_real_estate_summary_{timestamp}.txt"
            text_filepath = os.path.join(output_path, text_filename)
            
            with open(text_filepath, 'w') as f:
                f.write(f"REAL ESTATE SUMMARY FOR ZIP: {zip_code}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("ANALYSIS SCORES:\n")
                for label, score in scores.items():
                    display_label = label.replace("_", " ").title()
                    f.write(f"{display_label}: {score}\n")
                f.write("\nANALYSIS SUMMARY:\n")
                f.write(summary)
                f.write("\n\nDisclaimer: This summary is for informational purposes only.")
                f.write("\nIt does not constitute investment advice or legal recommendation.")
            
            logger.info(f"Generated text report as PDF fallback: {text_filepath}")
            return text_filepath
        except Exception as fallback_error:
            logger.error(f"Error generating fallback text file: {fallback_error}")
            return ""
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        # Attempt to create a fallback text file
        try:
            text_filename = f"{zip_code}_real_estate_summary_{timestamp}.txt"
            text_filepath = os.path.join(output_path, text_filename)
            
            with open(text_filepath, 'w') as f:
                f.write(f"REAL ESTATE SUMMARY FOR ZIP: {zip_code}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("ANALYSIS SCORES:\n")
                for label, score in scores.items():
                    display_label = label.replace("_", " ").title()
                    f.write(f"{display_label}: {score}\n")
                f.write("\nANALYSIS SUMMARY:\n")
                f.write(summary)
                f.write("\n\nDisclaimer: This summary is for informational purposes only.")
                f.write("\nIt does not constitute investment advice or legal recommendation.")
            
            logger.info(f"Generated text report as PDF fallback: {text_filepath}")
            return text_filepath
        except Exception as fallback_error:
            logger.error(f"Error generating fallback text file: {fallback_error}")
            return ""


# Example usage
if __name__ == "__main__":
    example_summary = "This ZIP code shows strong rental potential and low risk, with a solid reputation and favorable economic outlook."
    example_scores = {
        "Market Score": 78,
        "Reputation Score": 85,
        "Trend Score": 72,
        "Econ Score": 69,
        "Investment Confidence": 80.3
    }
    pdf_path = generate_pdf_summary("30318", example_summary, example_scores)
    print(f"PDF generated at: {pdf_path}")
