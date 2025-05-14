#!/usr/bin/env python3
"""
Leaderboard Generator

This module generates leaderboards of top neighborhoods based on various metrics
such as investment score, sentiment score, or market performance.
"""

import asyncio
import csv
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our components
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
if sys_path not in sys.path:
    sys.path.append(sys_path)

from src.integration.combine_market_and_sentiment import combined_analysis, batch_analysis
from src.utils.export_to_csv import export_to_csv


class LeaderboardGenerator:
    """Class for generating neighborhood leaderboards based on various metrics."""
    
    def __init__(self):
        """
        Initialize the leaderboard generator.
        """
        self.results_cache = {}
    
    async def analyze_zip_codes(self, zip_codes: List[str], force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze a list of ZIP codes to generate leaderboard data.
        
        Args:
            zip_codes: List of ZIP codes to analyze
            force_refresh: Whether to force a refresh of sentiment data
            
        Returns:
            List of analysis results
        """
        logger.info(f"Analyzing {len(zip_codes)} ZIP codes for leaderboard generation")
        
        # Use batch analysis to get results for all ZIP codes
        results = await batch_analysis(zip_codes, force_refresh)
        
        # Cache the results
        for result in results:
            zip_code = result.get("zip_code")
            if zip_code:
                self.results_cache[zip_code] = result
        
        return results
    
    def generate_leaderboard(self, results: List[Dict[str, Any]], metric: str = "investment", 
                           top_n: int = 10, ascending: bool = False) -> List[Dict[str, Any]]:
        """
        Generate a leaderboard from analysis results.
        
        Args:
            results: List of analysis results
            metric: Metric to sort by ("investment", "market", "sentiment")
            top_n: Number of top results to include
            ascending: Whether to sort in ascending order
            
        Returns:
            List of top neighborhoods
        """
        # Define key functions for different metrics
        if metric == "investment":
            key_func = lambda x: x.get("investment", {}).get("score", 0)
        elif metric == "market":
            key_func = lambda x: x.get("market", {}).get("market_score", 0)
        elif metric == "sentiment":
            key_func = lambda x: x.get("sentiment", {}).get("reputation", {}).get("overall_score", 0) * 100
        elif metric == "price":
            key_func = lambda x: x.get("market", {}).get("median_price", 0)
        elif metric == "growth":
            key_func = lambda x: x.get("market", {}).get("price_growth_1yr", 0)
        elif metric == "yield":
            key_func = lambda x: x.get("market", {}).get("rental_yield", 0)
        else:
            logger.warning(f"Unknown metric: {metric}, defaulting to investment score")
            key_func = lambda x: x.get("investment", {}).get("score", 0)
        
        # Sort the results
        sorted_results = sorted(results, key=key_func, reverse=not ascending)
        
        # Take the top N results
        top_results = sorted_results[:top_n]
        
        # Format the leaderboard
        leaderboard = []
        for i, result in enumerate(top_results):
            entry = {
                "rank": i + 1,
                "zip_code": result.get("zip_code"),
                "investment_score": result.get("investment", {}).get("score", 0),
                "investment_rating": result.get("investment", {}).get("rating", "N/A"),
                "market_score": result.get("market", {}).get("market_score", 0),
                "sentiment_score": result.get("sentiment", {}).get("reputation", {}).get("overall_score", 0) * 100,
                "median_price": result.get("market", {}).get("median_price", 0),
                "price_growth": result.get("market", {}).get("price_growth_1yr", 0),
                "rental_yield": result.get("market", {}).get("rental_yield", 0),
                "recommendation": result.get("investment", {}).get("recommendation", "N/A")
            }
            leaderboard.append(entry)
        
        return leaderboard
    
    def export_leaderboard_to_csv(self, leaderboard: List[Dict[str, Any]], 
                                filename: Optional[str] = None, 
                                metric: str = "investment") -> str:
        """
        Export a leaderboard to a CSV file.
        
        Args:
            leaderboard: Leaderboard data to export
            filename: Output filename (optional)
            metric: Metric used for the leaderboard
            
        Returns:
            Path to the exported CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"neighborhood_leaderboard_{metric}_{timestamp}.csv"
        
        # Ensure the output directory exists
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        
        # Define CSV headers
        headers = [
            "Rank", "ZIP Code", "Investment Score", "Rating", "Market Score", 
            "Sentiment Score", "Median Price", "Price Growth (1yr)", 
            "Rental Yield", "Recommendation"
        ]
        
        # Write to CSV
        with open(output_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for entry in leaderboard:
                writer.writerow({
                    "Rank": entry["rank"],
                    "ZIP Code": entry["zip_code"],
                    "Investment Score": f"{entry['investment_score']:.1f}",
                    "Rating": entry["investment_rating"],
                    "Market Score": f"{entry['market_score']:.1f}",
                    "Sentiment Score": f"{entry['sentiment_score']:.1f}",
                    "Median Price": f"${entry['median_price']:,}",
                    "Price Growth (1yr)": f"{entry['price_growth']:.1%}",
                    "Rental Yield": f"{entry['rental_yield']:.1%}",
                    "Recommendation": entry["recommendation"]
                })
        
        logger.info(f"Exported leaderboard to {output_path}")
        return output_path
    
    def generate_html_report(self, leaderboard: List[Dict[str, Any]], 
                           title: str = "Neighborhood Investment Leaderboard",
                           metric: str = "investment") -> str:
        """
        Generate an HTML report for a leaderboard.
        
        Args:
            leaderboard: Leaderboard data
            title: Report title
            metric: Metric used for the leaderboard
            
        Returns:
            HTML content as a string
        """
        # Start HTML content
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1 {{ color: #333; }}
                .timestamp {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f8f8; color: #333; font-weight: bold; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .rank {{ font-weight: bold; width: 50px; }}
                .score {{ font-weight: bold; }}
                .good {{ color: #28a745; }}
                .neutral {{ color: #ffc107; }}
                .bad {{ color: #dc3545; }}
                .recommendation {{ font-weight: bold; }}
                .strong-buy {{ color: #28a745; }}
                .buy {{ color: #5cb85c; }}
                .hold {{ color: #ffc107; }}
                .neutral-rec {{ color: #6c757d; }}
                .avoid {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="timestamp">Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</div>
            
            <table>
                <thead>
                    <tr>
                        <th class="rank">Rank</th>
                        <th>ZIP Code</th>
                        <th>Investment Score</th>
                        <th>Rating</th>
                        <th>Market Score</th>
                        <th>Sentiment Score</th>
                        <th>Median Price</th>
                        <th>Price Growth (1yr)</th>
                        <th>Rental Yield</th>
                        <th>Recommendation</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add rows for each leaderboard entry
        for entry in leaderboard:
            # Determine CSS classes based on scores
            investment_class = "good" if entry["investment_score"] >= 70 else "neutral" if entry["investment_score"] >= 50 else "bad"
            market_class = "good" if entry["market_score"] >= 70 else "neutral" if entry["market_score"] >= 50 else "bad"
            sentiment_class = "good" if entry["sentiment_score"] >= 70 else "neutral" if entry["sentiment_score"] >= 50 else "bad"
            
            # Determine recommendation class
            rec = entry["recommendation"]
            rec_class = "strong-buy" if rec == "Strong Buy" else \
                       "buy" if rec == "Buy" else \
                       "hold" if rec == "Hold" else \
                       "neutral-rec" if rec == "Neutral" else "avoid"
            
            html += f"""
                    <tr>
                        <td class="rank">{entry['rank']}</td>
                        <td>{entry['zip_code']}</td>
                        <td class="score {investment_class}">{entry['investment_score']:.1f}</td>
                        <td>{entry['investment_rating']}</td>
                        <td class="score {market_class}">{entry['market_score']:.1f}</td>
                        <td class="score {sentiment_class}">{entry['sentiment_score']:.1f}</td>
                        <td>${entry['median_price']:,}</td>
                        <td>{entry['price_growth']:.1%}</td>
                        <td>{entry['rental_yield']:.1%}</td>
                        <td class="recommendation {rec_class}">{rec}</td>
                    </tr>
            """
        
        # Close HTML
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def export_html_report(self, leaderboard: List[Dict[str, Any]], 
                         filename: Optional[str] = None,
                         title: str = "Neighborhood Investment Leaderboard",
                         metric: str = "investment") -> str:
        """
        Export a leaderboard to an HTML file.
        
        Args:
            leaderboard: Leaderboard data
            filename: Output filename (optional)
            title: Report title
            metric: Metric used for the leaderboard
            
        Returns:
            Path to the exported HTML file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"neighborhood_leaderboard_{metric}_{timestamp}.html"
        
        # Ensure the output directory exists
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        
        # Generate HTML content
        html_content = self.generate_html_report(leaderboard, title, metric)
        
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Exported HTML report to {output_path}")
        return output_path


async def generate_leaderboard(zip_codes: List[str], metric: str = "investment", 
                             top_n: int = 10, force_refresh: bool = False,
                             export_format: str = "both") -> Dict[str, Any]:
    """
    Generate a neighborhood leaderboard and export it to CSV and/or HTML.
    
    Args:
        zip_codes: List of ZIP codes to analyze
        metric: Metric to sort by ("investment", "market", "sentiment", "price", "growth", "yield")
        top_n: Number of top results to include
        force_refresh: Whether to force a refresh of sentiment data
        export_format: Export format ("csv", "html", or "both")
        
    Returns:
        Dictionary with leaderboard results and export paths
    """
    generator = LeaderboardGenerator()
    
    # Analyze ZIP codes
    results = await generator.analyze_zip_codes(zip_codes, force_refresh)
    
    # Generate leaderboard
    leaderboard = generator.generate_leaderboard(results, metric, top_n)
    
    # Export results
    exports = {}
    
    if export_format in ["csv", "both"]:
        csv_path = generator.export_leaderboard_to_csv(leaderboard, metric=metric)
        exports["csv"] = csv_path
    
    if export_format in ["html", "both"]:
        title = f"Top {top_n} Neighborhoods by {metric.title()} Score"
        html_path = generator.export_html_report(leaderboard, title=title, metric=metric)
        exports["html"] = html_path
    
    return {
        "leaderboard": leaderboard,
        "metric": metric,
        "top_n": top_n,
        "total_analyzed": len(results),
        "exports": exports
    }


async def main():
    """
    Example usage of the leaderboard generator.
    """
    # Example ZIP codes (expand this list for real usage)
    test_zips = [
        "30318", "30319", "30306", "30307", "30308", "30309", "30310", "30311", "30312", "30313",  # Atlanta
        "11238", "11215", "11217", "11201", "11205", "11216", "11221", "11222", "11211", "11206",  # Brooklyn
        "94110", "94103", "94107", "94109", "94117", "94114", "94133", "94115", "94118", "94121"   # San Francisco
    ]
    
    print("\nud83cudfc6 Generating Neighborhood Leaderboards")
    
    # Generate investment score leaderboard
    print("\nud83dudcb0 Top Neighborhoods by Investment Score")
    investment_result = await generate_leaderboard(test_zips, "investment", 10)
    
    for entry in investment_result["leaderboard"]:
        print(f"{entry['rank']}. ZIP {entry['zip_code']} - Score: {entry['investment_score']:.1f} ({entry['investment_rating']}) - {entry['recommendation']}")
    
    # Generate sentiment score leaderboard
    print("\nud83dude00 Top Neighborhoods by Sentiment Score")
    sentiment_result = await generate_leaderboard(test_zips, "sentiment", 5)
    
    for entry in sentiment_result["leaderboard"]:
        print(f"{entry['rank']}. ZIP {entry['zip_code']} - Score: {entry['sentiment_score']:.1f} - {entry['recommendation']}")
    
    # Generate rental yield leaderboard
    print("\nud83dudcb6 Top Neighborhoods by Rental Yield")
    yield_result = await generate_leaderboard(test_zips, "yield", 5)
    
    for entry in yield_result["leaderboard"]:
        print(f"{entry['rank']}. ZIP {entry['zip_code']} - Yield: {entry['rental_yield']:.1%} - Price: ${entry['median_price']:,}")
    
    print("\nu2705 Leaderboard generation complete!")
    print(f"CSV exports: {investment_result['exports'].get('csv')}")
    print(f"HTML exports: {investment_result['exports'].get('html')}")


if __name__ == "__main__":
    asyncio.run(main())
