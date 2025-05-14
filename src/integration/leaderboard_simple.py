#!/usr/bin/env python3
"""
Simple Leaderboard Generator

Generates leaderboards of top neighborhoods based on various metrics
and exports them to CSV files.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any

from src.integration.combine_market_and_sentiment import combine_analysis


def generate_leaderboard(zip_list: List[str], sort_key: str = "reputation_score", 
                       top_n: int = 10, export_path: str = None) -> List[Dict[str, Any]]:
    """
    Generate a leaderboard of top neighborhoods based on a specified metric.
    
    Args:
        zip_list: List of ZIP codes to analyze
        sort_key: Metric to sort by (e.g., "reputation_score", "market_score")
        top_n: Number of top results to include
        export_path: Path to export CSV file (optional)
        
    Returns:
        List of top neighborhoods
    """
    # Create default export path if not provided
    if not export_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure output directory exists
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        os.makedirs(output_dir, exist_ok=True)
        export_path = os.path.join(output_dir, f"leaderboard_{sort_key}_{timestamp}.csv")
    
    # Analyze all ZIP codes
    print(f"\nud83dudcca Analyzing {len(zip_list)} ZIP codes...")
    results = [combine_analysis(z) for z in zip_list]
    
    # Sort by the specified key
    ranked = sorted(results, key=lambda r: r.get(sort_key, 0), reverse=True)
    top = ranked[:top_n]

    # Display results
    print(f"\nud83cudfc6 Top {top_n} ZIPs by {sort_key.replace('_', ' ').title()}\n")
    for idx, r in enumerate(top):
        print(f"{idx+1}. {r['zip']} → {sort_key.title()}: {r.get(sort_key)}")

    # Export to CSV
    with open(export_path, "w", newline="") as f:
        # Filter out keys that start with underscore (internal data)
        fieldnames = [k for k in top[0].keys() if not k.startswith('_')]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write only the visible fields (not starting with underscore)
        for row in top:
            filtered_row = {k: v for k, v in row.items() if not k.startswith('_')}
            writer.writerow(filtered_row)

    print(f"\nud83dudcc4 Leaderboard saved to {export_path}")
    return top


def generate_multiple_leaderboards(zip_list: List[str], metrics: List[str] = None, 
                                 top_n: int = 10) -> Dict[str, str]:
    """
    Generate multiple leaderboards for different metrics.
    
    Args:
        zip_list: List of ZIP codes to analyze
        metrics: List of metrics to generate leaderboards for
        top_n: Number of top results to include in each leaderboard
        
    Returns:
        Dictionary mapping metrics to export paths
    """
    if metrics is None:
        metrics = ["reputation_score", "market_score", "investment_score"]
    
    export_paths = {}
    
    for metric in metrics:
        print(f"\nud83dudcc8 Generating leaderboard for {metric.replace('_', ' ').title()}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        os.makedirs(output_dir, exist_ok=True)
        export_path = os.path.join(output_dir, f"leaderboard_{metric}_{timestamp}.csv")
        
        generate_leaderboard(zip_list, sort_key=metric, top_n=top_n, export_path=export_path)
        export_paths[metric] = export_path
    
    return export_paths


if __name__ == "__main__":
    # Example ZIP codes
    zips = ["30318", "11238", "90210", "33101", "60614", "75201"]
    
    # Generate leaderboard for reputation score
    generate_leaderboard(zips)
    
    # Uncomment to generate multiple leaderboards
    # generate_multiple_leaderboards(zips)
