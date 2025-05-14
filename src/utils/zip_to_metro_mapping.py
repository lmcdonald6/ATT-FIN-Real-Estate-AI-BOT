#!/usr/bin/env python3
"""
ZIP to Metro Mapping

This module provides utilities for mapping ZIP codes to metropolitan areas,
allowing for location-based routing, filtering, and grouping.

Also includes metro-based routing suggestions for the Manus Agent.
"""

import csv
import os
import logging
from typing import Dict, List, Optional, Set, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Metro-based routing suggestions for Manus Agent
MANUS_SOURCE_MAP = {
    "nyc": ["Reddit", "YouTube", "Yelp"],
    "la": ["TikTok", "YouTube", "Facebook"],
    "chicago": ["Reddit", "Yelp"],
    "atlanta": ["Twitter", "Facebook", "Reddit"],
    "sf": ["Nextdoor", "Reddit"],
    "miami": ["Instagram", "Twitter", "Facebook"],
    "dallas": ["Facebook", "Nextdoor", "Twitter"]
}

# Default path for the mapping file
DEFAULT_MAPPING_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "zip_metro_mapping.csv"
)


def load_zip_metro_mapping(filepath: str = DEFAULT_MAPPING_PATH) -> Dict[str, str]:
    """
    Load ZIP code to metropolitan area mapping from a CSV file.
    
    Args:
        filepath: Path to the CSV file containing the mapping
        
    Returns:
        Dictionary mapping ZIP codes to metropolitan areas
    """
    mapping = {}
    
    try:
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                zip_code = row["ZIP"].strip()
                metro = row["Metro"].strip().lower()
                mapping[zip_code] = metro
        
        logger.info(f"Loaded {len(mapping)} ZIP code to metro mappings from {filepath}")
    except FileNotFoundError:
        logger.warning(f"Mapping file not found: {filepath}")
    except Exception as e:
        logger.error(f"Error loading ZIP to metro mapping: {str(e)}")
    
    return mapping


def get_metro_for_zip(zip_code: str, mapping: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Get the metropolitan area for a ZIP code.
    
    Args:
        zip_code: ZIP code to look up
        mapping: Optional pre-loaded mapping dictionary
        
    Returns:
        Metropolitan area name or None if not found
    """
    if mapping is None:
        mapping = load_zip_metro_mapping()
    
    return mapping.get(zip_code)


def get_data_sources_for_zip(zip_code: str, mapping: Optional[Dict[str, str]] = None) -> List[str]:
    """
    Get recommended data sources for a ZIP code based on its metro area.
    
    Args:
        zip_code: ZIP code to look up
        mapping: Optional pre-loaded mapping dictionary
        
    Returns:
        List of recommended data sources for the ZIP code's metro area
    """
    metro = get_metro_for_zip(zip_code, mapping)
    if not metro:
        return ["Reddit"]  # Default source if metro not found
    
    return MANUS_SOURCE_MAP.get(metro, ["Reddit"])


def get_data_sources_for_metro(metro: str) -> List[str]:
    """
    Get recommended data sources for a metropolitan area.
    
    Args:
        metro: Metropolitan area name (case-insensitive)
        
    Returns:
        List of recommended data sources for the metro area
    """
    metro = metro.lower()
    return MANUS_SOURCE_MAP.get(metro, ["Reddit"])


def get_zips_in_metro(metro: str, mapping: Optional[Dict[str, str]] = None) -> List[str]:
    """
    Get all ZIP codes in a metropolitan area.
    
    Args:
        metro: Metropolitan area name (case-insensitive)
        mapping: Optional pre-loaded mapping dictionary
        
    Returns:
        List of ZIP codes in the metropolitan area
    """
    if mapping is None:
        mapping = load_zip_metro_mapping()
    
    metro = metro.lower()
    return [zip_code for zip_code, m in mapping.items() if m == metro]


def get_all_metros(mapping: Optional[Dict[str, str]] = None) -> Set[str]:
    """
    Get all metropolitan areas in the mapping.
    
    Args:
        mapping: Optional pre-loaded mapping dictionary
        
    Returns:
        Set of metropolitan area names
    """
    if mapping is None:
        mapping = load_zip_metro_mapping()
    
    return set(mapping.values())


def create_sample_mapping_file(output_path: str = DEFAULT_MAPPING_PATH) -> str:
    """
    Create a sample ZIP to metro mapping file if one doesn't exist.
    
    Args:
        output_path: Path to write the sample mapping file
        
    Returns:
        Path to the created file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Sample data mapping major ZIP codes to metros
    sample_data = [
        {"ZIP": "30318", "Metro": "atlanta"},
        {"ZIP": "30319", "Metro": "atlanta"},
        {"ZIP": "30306", "Metro": "atlanta"},
        {"ZIP": "30307", "Metro": "atlanta"},
        {"ZIP": "30308", "Metro": "atlanta"},
        {"ZIP": "11238", "Metro": "nyc"},
        {"ZIP": "11215", "Metro": "nyc"},
        {"ZIP": "11217", "Metro": "nyc"},
        {"ZIP": "11201", "Metro": "nyc"},
        {"ZIP": "11205", "Metro": "nyc"},
        {"ZIP": "94110", "Metro": "sf"},
        {"ZIP": "94103", "Metro": "sf"},
        {"ZIP": "94107", "Metro": "sf"},
        {"ZIP": "94109", "Metro": "sf"},
        {"ZIP": "94117", "Metro": "sf"},
        {"ZIP": "90210", "Metro": "la"},
        {"ZIP": "90001", "Metro": "la"},
        {"ZIP": "90025", "Metro": "la"},
        {"ZIP": "90045", "Metro": "la"},
        {"ZIP": "90064", "Metro": "la"},
        {"ZIP": "60614", "Metro": "chicago"},
        {"ZIP": "60601", "Metro": "chicago"},
        {"ZIP": "60607", "Metro": "chicago"},
        {"ZIP": "60622", "Metro": "chicago"},
        {"ZIP": "60642", "Metro": "chicago"},
        {"ZIP": "75201", "Metro": "dallas"},
        {"ZIP": "75202", "Metro": "dallas"},
        {"ZIP": "75204", "Metro": "dallas"},
        {"ZIP": "75205", "Metro": "dallas"},
        {"ZIP": "75206", "Metro": "dallas"},
        {"ZIP": "33101", "Metro": "miami"},
        {"ZIP": "33109", "Metro": "miami"},
        {"ZIP": "33122", "Metro": "miami"},
        {"ZIP": "33125", "Metro": "miami"},
        {"ZIP": "33127", "Metro": "miami"}
    ]
    
    # Write the sample data to a CSV file
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ZIP", "Metro"])
        writer.writeheader()
        writer.writerows(sample_data)
    
    logger.info(f"Created sample ZIP to metro mapping file at {output_path}")
    return output_path


def ensure_mapping_file_exists() -> str:
    """
    Ensure that the ZIP to metro mapping file exists, creating a sample if it doesn't.
    
    Returns:
        Path to the mapping file
    """
    if not os.path.exists(DEFAULT_MAPPING_PATH):
        return create_sample_mapping_file()
    return DEFAULT_MAPPING_PATH


if __name__ == "__main__":
    # Ensure the mapping file exists
    mapping_path = ensure_mapping_file_exists()
    
    # Load the mapping
    mapping = load_zip_metro_mapping(mapping_path)
    
    # Print some sample mappings
    print("\nud83dudccd Sample ZIP to Metro Mappings:")
    sample_zips = ["30318", "11238", "94110", "90210", "60614", "75201", "33101"]
    for zip_code in sample_zips:
        metro = get_metro_for_zip(zip_code, mapping)
        sources = get_data_sources_for_zip(zip_code, mapping)
        print(f"ZIP {zip_code} → Metro: {metro} → Sources: {', '.join(sources)}")
    
    # Print all metros
    metros = get_all_metros(mapping)
    print(f"\nud83cudfd9 Available Metropolitan Areas: {', '.join(sorted(metros))}")
    
    # Print all ZIPs in a metro
    metro = "atlanta"
    zips_in_metro = get_zips_in_metro(metro, mapping)
    print(f"\nud83cudfa5 ZIP Codes in {metro.title()}: {', '.join(zips_in_metro)}")
    
    # Print data sources by metro
    print("\nud83dudcf9 Data Sources by Metro:")
    for metro in sorted(metros):
        sources = get_data_sources_for_metro(metro)
        print(f"{metro.title()}: {', '.join(sources)}")
