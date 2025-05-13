"""Report Generator Module

This module generates visual reports from model audit results.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('report_generator')

class ReportGenerator:
    """Class for generating visual reports from model audit results."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.logger = logging.getLogger('report_generator')
        
        # Create reports directory if it doesn't exist
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_price_prediction_report(self, audit_results_path: str) -> str:
        """Generate a report for price prediction audit results.
        
        Args:
            audit_results_path: Path to the audit results file
            
        Returns:
            Path to the generated report
        """
        self.logger.info(f"Generating price prediction report from {audit_results_path}")
        
        # Load the audit results
        try:
            with open(audit_results_path, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading audit results: {str(e)}")
            return ""
        
        # Extract the results
        if "results" in audit_data:
            results = audit_data["results"]
        else:
            results = audit_data
        
        # Create a report directory
        report_id = f"price_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_dir = os.path.join(self.reports_dir, report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate performance metrics visualization
        if "performance_metrics" in results:
            self._plot_performance_metrics(results["performance_metrics"], report_dir)
        
        # Generate bias metrics visualization
        if "bias_metrics" in results:
            self._plot_bias_metrics(results["bias_metrics"], report_dir)
        
        # Generate feature importance visualization
        if "feature_importance" in results:
            self._plot_feature_importance(results["feature_importance"], report_dir)
        
        # Generate prediction distribution visualization
        if "prediction_distribution" in results:
            self._plot_prediction_distribution(results["prediction_distribution"], report_dir)
        
        # Generate outlier metrics visualization
        if "outlier_metrics" in results:
            self._plot_outlier_metrics(results["outlier_metrics"], report_dir)
        
        # Generate an HTML report
        html_path = self._generate_html_report(results, report_dir, "Price Prediction Model Audit Report")
        
        self.logger.info(f"Generated price prediction report at {html_path}")
        return html_path
    
    def generate_fairness_report(self, audit_results_path: str) -> str:
        """Generate a report for fairness audit results.
        
        Args:
            audit_results_path: Path to the audit results file
            
        Returns:
            Path to the generated report
        """
        self.logger.info(f"Generating fairness report from {audit_results_path}")
        
        # Load the audit results
        try:
            with open(audit_results_path, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading audit results: {str(e)}")
            return ""
        
        # Extract the results
        if "results" in audit_data:
            results = audit_data["results"]
        else:
            results = audit_data
        
        # Create a report directory
        report_id = f"fairness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_dir = os.path.join(self.reports_dir, report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate fairness metrics visualization
        if "fairness_by_attribute" in results:
            self._plot_fairness_by_attribute(results["fairness_by_attribute"], report_dir)
        
        # Generate overall fairness visualization
        if "overall_fairness" in results:
            self._plot_overall_fairness(results["overall_fairness"], report_dir)
        
        # Generate an HTML report
        html_path = self._generate_html_report(results, report_dir, "Model Fairness Audit Report")
        
        self.logger.info(f"Generated fairness report at {html_path}")
        return html_path
    
    def generate_comparison_report(self, comparison_results_path: str) -> str:
        """Generate a report for audit comparison results.
        
        Args:
            comparison_results_path: Path to the comparison results file
            
        Returns:
            Path to the generated report
        """
        self.logger.info(f"Generating comparison report from {comparison_results_path}")
        
        # Load the comparison results
        try:
            with open(comparison_results_path, "r", encoding="utf-8") as f:
                comparison_data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading comparison results: {str(e)}")
            return ""
        
        # Create a report directory
        report_id = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_dir = os.path.join(self.reports_dir, report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate comparison visualization
        self._plot_comparison_results(comparison_data, report_dir)
        
        # Generate an HTML report
        html_path = self._generate_html_report(comparison_data, report_dir, "Model Audit Comparison Report")
        
        self.logger.info(f"Generated comparison report at {html_path}")
        return html_path
    
    def _plot_performance_metrics(self, performance_metrics: Dict[str, float], report_dir: str):
        """Plot performance metrics.
        
        Args:
            performance_metrics: Dictionary of performance metrics
            report_dir: Directory to save the plot
        """
        plt.figure(figsize=(10, 6))
        
        # Create a bar chart of performance metrics
        metrics = list(performance_metrics.keys())
        values = list(performance_metrics.values())
        
        sns.barplot(x=metrics, y=values)
        plt.xticks(rotation=45, ha="right")
        plt.title("Model Performance Metrics")
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(report_dir, "performance_metrics.png"))
        plt.close()
    
    def _plot_bias_metrics(self, bias_metrics: Dict[str, Any], report_dir: str):
        """Plot bias metrics.
        
        Args:
            bias_metrics: Dictionary of bias metrics
            report_dir: Directory to save the plot
        """
        # Plot price range bias
        if "price_range_bias" in bias_metrics:
            plt.figure(figsize=(12, 6))
            
            price_ranges = list(bias_metrics["price_range_bias"].keys())
            mean_errors = [data["mean_error"] for data in bias_metrics["price_range_bias"].values()]
            
            sns.barplot(x=price_ranges, y=mean_errors)
            plt.title("Mean Error by Price Range")
            plt.xlabel("Price Range")
            plt.ylabel("Mean Error")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(os.path.join(report_dir, "price_range_bias.png"))
            plt.close()
    
    def _plot_feature_importance(self, feature_importance: Dict[str, float], report_dir: str):
        """Plot feature importance.
        
        Args:
            feature_importance: Dictionary of feature importance
            report_dir: Directory to save the plot
        """
        # Skip if there's an error or note
        if "error" in feature_importance or "note" in feature_importance:
            return
        
        plt.figure(figsize=(10, 6))
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        features = [item[0] for item in sorted_features]
        importance = [item[1] for item in sorted_features]
        
        sns.barplot(x=importance, y=features)
        plt.title("Feature Importance")
        plt.xlabel("Importance")
        plt.ylabel("Feature")
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(report_dir, "feature_importance.png"))
        plt.close()
    
    def _plot_prediction_distribution(self, prediction_distribution: Dict[str, Any], report_dir: str):
        """Plot prediction distribution.
        
        Args:
            prediction_distribution: Dictionary of prediction distribution metrics
            report_dir: Directory to save the plot
        """
        plt.figure(figsize=(12, 6))
        
        # Create a histogram of true and predicted values
        true_dist = prediction_distribution["true_distribution"]
        pred_dist = prediction_distribution["pred_distribution"]
        
        # Plot the distribution comparison
        plt.subplot(1, 2, 1)
        plt.bar(["Mean", "Median", "Std Dev"], 
               [true_dist["mean"], true_dist["median"], true_dist["std"]], 
               alpha=0.5, label="True")
        plt.bar(["Mean", "Median", "Std Dev"], 
               [pred_dist["mean"], pred_dist["median"], pred_dist["std"]], 
               alpha=0.5, label="Predicted")
        plt.legend()
        plt.title("Distribution Comparison")
        
        # Plot the percentile comparison
        plt.subplot(1, 2, 2)
        percentiles = list(true_dist["percentiles"].keys())
        true_percentiles = list(true_dist["percentiles"].values())
        pred_percentiles = list(pred_dist["percentiles"].values())
        
        plt.plot(percentiles, true_percentiles, marker='o', label="True")
        plt.plot(percentiles, pred_percentiles, marker='o', label="Predicted")
        plt.legend()
        plt.title("Percentile Comparison")
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(report_dir, "prediction_distribution.png"))
        plt.close()
    
    def _plot_outlier_metrics(self, outlier_metrics: Dict[str, Any], report_dir: str):
        """Plot outlier metrics.
        
        Args:
            outlier_metrics: Dictionary of outlier metrics
            report_dir: Directory to save the plot
        """
        plt.figure(figsize=(8, 6))
        
        # Create a pie chart of outliers vs non-outliers
        labels = ["Outliers", "Non-Outliers"]
        sizes = [outlier_metrics["num_outliers"], 100 - outlier_metrics["outlier_percentage"]]
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title("Outliers in Predictions")
        
        # Save the plot
        plt.savefig(os.path.join(report_dir, "outlier_metrics.png"))
        plt.close()
    
    def _plot_fairness_by_attribute(self, fairness_by_attribute: Dict[str, Dict[str, Any]], report_dir: str):
        """Plot fairness metrics by attribute.
        
        Args:
            fairness_by_attribute: Dictionary of fairness metrics by attribute
            report_dir: Directory to save the plot
        """
        for attribute, metrics in fairness_by_attribute.items():
            if "value_metrics" in metrics:
                plt.figure(figsize=(12, 6))
                
                # Get the values and a relevant metric
                values = list(metrics["value_metrics"].keys())
                
                # Try to find a relevant metric
                if "positive_rate" in next(iter(metrics["value_metrics"].values())):
                    # Classification
                    metric_name = "positive_rate"
                    metric_values = [data[metric_name] for data in metrics["value_metrics"].values()]
                    title = f"Positive Rate by {attribute}"
                elif "mean_prediction" in next(iter(metrics["value_metrics"].values())):
                    # Regression
                    metric_name = "mean_prediction"
                    metric_values = [data[metric_name] for data in metrics["value_metrics"].values()]
                    title = f"Mean Prediction by {attribute}"
                else:
                    continue
                
                sns.barplot(x=values, y=metric_values)
                plt.title(title)
                plt.xlabel(attribute)
                plt.ylabel(metric_name.replace("_", " ").title())
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                
                # Save the plot
                plt.savefig(os.path.join(report_dir, f"fairness_{attribute}.png"))
                plt.close()
    
    def _plot_overall_fairness(self, overall_fairness: Dict[str, Any], report_dir: str):
        """Plot overall fairness metrics.
        
        Args:
            overall_fairness: Dictionary of overall fairness metrics
            report_dir: Directory to save the plot
        """
        if "fairness_scores" in overall_fairness:
            plt.figure(figsize=(10, 6))
            
            # Get the metrics and scores
            metrics = list(overall_fairness["fairness_scores"].keys())
            scores = [data["score"] for data in overall_fairness["fairness_scores"].values()]
            
            sns.barplot(x=metrics, y=scores)
            plt.title("Fairness Scores by Metric")
            plt.xlabel("Metric")
            plt.ylabel("Fairness Score (0-100)")
            plt.xticks(rotation=45, ha="right")
            plt.axhline(y=80, color='r', linestyle='--', label="Good Fairness Threshold")
            plt.legend()
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(os.path.join(report_dir, "overall_fairness.png"))
            plt.close()
            
            # Create a gauge chart for the overall fairness score
            plt.figure(figsize=(8, 8))
            
            overall_score = overall_fairness["overall_fairness_score"]
            
            # Create a gauge chart using a half donut
            size = 0.3
            vals = [overall_score, 100 - overall_score]
            
            cmap = plt.get_cmap("RdYlGn")
            colors = [cmap(overall_score / 100.0), "#f0f0f0"]
            
            plt.pie(vals, radius=1, colors=colors, wedgeprops=dict(width=size, edgecolor='w'))
            
            # Add a circle in the center to make it look like a gauge
            circle = plt.Circle((0, 0), 0.7, color='white')
            plt.gcf().gca().add_artist(circle)
            
            # Add the score text in the center
            plt.text(0, 0, f"{overall_score:.1f}", ha='center', va='center', fontsize=36)
            plt.text(0, -0.2, "Overall Fairness Score", ha='center', va='center', fontsize=12)
            
            plt.title("Overall Fairness Score")
            plt.axis('equal')
            
            # Save the plot
            plt.savefig(os.path.join(report_dir, "fairness_gauge.png"))
            plt.close()
    
    def _plot_comparison_results(self, comparison_data: Dict[str, Any], report_dir: str):
        """Plot comparison results.
        
        Args:
            comparison_data: Dictionary of comparison results
            report_dir: Directory to save the plot
        """
        if "differences" in comparison_data:
            plt.figure(figsize=(12, 6))
            
            # Get the metrics and differences
            metrics = []
            differences = []
            
            for metric, diff_data in comparison_data["differences"].items():
                if "absolute" in diff_data:
                    metrics.append(metric)
                    differences.append(diff_data["absolute"])
            
            # Sort by absolute difference
            sorted_indices = sorted(range(len(differences)), key=lambda i: abs(differences[i]), reverse=True)
            sorted_metrics = [metrics[i] for i in sorted_indices]
            sorted_differences = [differences[i] for i in sorted_indices]
            
            # Use different colors for positive and negative differences
            colors = ['g' if d >= 0 else 'r' for d in sorted_differences]
            
            plt.barh(sorted_metrics, sorted_differences, color=colors)
            plt.axvline(x=0, color='black', linestyle='-')
            plt.title("Metric Differences (Current - Previous)")
            plt.xlabel("Difference")
            plt.ylabel("Metric")
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(os.path.join(report_dir, "comparison_differences.png"))
            plt.close()
    
    def _generate_html_report(self, data: Dict[str, Any], report_dir: str, title: str) -> str:
        """Generate an HTML report.
        
        Args:
            data: Data to include in the report
            report_dir: Directory to save the report
            title: Title of the report
            
        Returns:
            Path to the generated HTML report
        """
        # Get the list of images in the report directory
        images = [f for f in os.listdir(report_dir) if f.endswith(".png")]
        
        # Create the HTML content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333366; }}
        h2 {{ color: #666699; }}
        .image-container {{ margin: 20px 0; }}
        .image-container img {{ max-width: 100%; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
        
        # Add images to the report
        if images:
            html_content += "\n    <h2>Visualizations</h2>\n"
            for image in images:
                image_title = image.replace(".png", "").replace("_", " ").title()
                html_content += f"""    <div class="image-container">
        <h3>{image_title}</h3>
        <img src="{image}" alt="{image_title}">
    </div>
"""
        
        # Add data tables to the report
        html_content += "\n    <h2>Detailed Results</h2>\n"
        
        # Convert the data to a formatted HTML table
        html_content += self._data_to_html_table(data)
        
        # Close the HTML content
        html_content += "\n</body>\n</html>"
        
        # Write the HTML content to a file
        html_path = os.path.join(report_dir, "report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return html_path
    
    def _data_to_html_table(self, data: Dict[str, Any], level: int = 0) -> str:
        """Convert data to an HTML table.
        
        Args:
            data: Data to convert
            level: Nesting level
            
        Returns:
            HTML table representation of the data
        """
        html = ""
        
        if isinstance(data, dict):
            # Create a table for the dictionary
            html += "<table>\n"
            html += "<tr><th>Key</th><th>Value</th></tr>\n"
            
            for key, value in data.items():
                html += "<tr>"
                html += f"<td>{key}</td>"
                
                if isinstance(value, (dict, list)) and level < 2:
                    # Recursively convert nested dictionaries and lists
                    html += f"<td>{self._data_to_html_table(value, level + 1)}</td>"
                else:
                    # Format the value as a string
                    if isinstance(value, (int, float)):
                        formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                    else:
                        formatted_value = str(value)
                    
                    html += f"<td>{formatted_value}</td>"
                
                html += "</tr>\n"
            
            html += "</table>\n"
        
        elif isinstance(data, list):
            # Create a list representation
            if level < 2 and len(data) > 0 and isinstance(data[0], dict):
                # Create a table for a list of dictionaries
                if all(isinstance(item, dict) for item in data):
                    # Get all unique keys
                    keys = set()
                    for item in data:
                        keys.update(item.keys())
                    
                    # Create the table header
                    html += "<table>\n"
                    html += "<tr>"
                    for key in keys:
                        html += f"<th>{key}</th>"
                    html += "</tr>\n"
                    
                    # Create the table rows
                    for item in data:
                        html += "<tr>"
                        for key in keys:
                            value = item.get(key, "")
                            
                            if isinstance(value, (int, float)):
                                formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                            else:
                                formatted_value = str(value)
                            
                            html += f"<td>{formatted_value}</td>"
                        
                        html += "</tr>\n"
                    
                    html += "</table>\n"
                else:
                    # Create a simple list representation
                    html += "<ul>\n"
                    for item in data:
                        html += f"<li>{self._data_to_html_table(item, level + 1)}</li>\n"
                    html += "</ul>\n"
            else:
                # Create a simple list representation
                html += "<ul>\n"
                for item in data[:10]:  # Limit to 10 items
                    html += f"<li>{item}</li>\n"
                
                if len(data) > 10:
                    html += f"<li>... and {len(data) - 10} more items</li>\n"
                
                html += "</ul>\n"
        
        else:
            # Return the value as a string
            if isinstance(data, (int, float)):
                html = f"{data:.4f}" if isinstance(data, float) else str(data)
            else:
                html = str(data)
        
        return html
