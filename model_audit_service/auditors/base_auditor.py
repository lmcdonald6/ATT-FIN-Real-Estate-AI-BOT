"""Base Auditor Module

This module provides a base class for AI model auditors.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAuditor(ABC):
    """Base class for AI model auditors."""
    
    def __init__(self, name: str, model_type: str):
        """Initialize the base auditor.
        
        Args:
            name: Name of the auditor
            model_type: Type of model being audited
        """
        self.name = name
        self.model_type = model_type
        self.logger = logging.getLogger(f"auditor.{name}")
        self.audit_results = {}
        
        # Create audit directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audit_results'), exist_ok=True)
    
    @abstractmethod
    def audit_model(self, model: Any, test_data: pd.DataFrame, 
                  target_column: str) -> Dict[str, Any]:
        """Audit a model for performance, bias, and other metrics.
        
        Args:
            model: Model to audit
            test_data: Test data to use for the audit
            target_column: Name of the target column
            
        Returns:
            Dictionary of audit results
        """
        pass
    
    def save_audit_results(self, audit_id: str) -> str:
        """Save audit results to a file.
        
        Args:
            audit_id: ID for the audit
            
        Returns:
            Path to the saved audit results file
        """
        if not self.audit_results:
            self.logger.warning("No audit results to save")
            return ""
        
        # Create the audit results directory if it doesn't exist
        audit_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audit_results')
        os.makedirs(audit_dir, exist_ok=True)
        
        # Add timestamp and metadata to the audit results
        results_with_metadata = {
            "audit_id": audit_id,
            "auditor_name": self.name,
            "model_type": self.model_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.audit_results
        }
        
        # Save the audit results to a file
        filename = f"{audit_id}_{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(audit_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results_with_metadata, f, indent=2, default=str)
        
        self.logger.info(f"Saved audit results to {filepath}")
        return filepath
    
    def load_audit_results(self, filepath: str) -> Dict[str, Any]:
        """Load audit results from a file.
        
        Args:
            filepath: Path to the audit results file
            
        Returns:
            Dictionary of audit results
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                audit_results = json.load(f)
            
            self.logger.info(f"Loaded audit results from {filepath}")
            return audit_results
        except Exception as e:
            self.logger.error(f"Error loading audit results from {filepath}: {str(e)}")
            return {}
    
    def compare_audit_results(self, previous_audit: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current audit results with previous audit results.
        
        Args:
            previous_audit: Previous audit results to compare with
            
        Returns:
            Dictionary of comparison results
        """
        if not self.audit_results or not previous_audit:
            self.logger.warning("Missing audit results for comparison")
            return {}
        
        # Extract the results from the previous audit
        if "results" in previous_audit:
            previous_results = previous_audit["results"]
        else:
            previous_results = previous_audit
        
        # Compare the results
        comparison = {
            "current_audit": self.audit_results,
            "previous_audit": previous_results,
            "differences": {}
        }
        
        # Compare each metric in the current audit with the previous audit
        for metric, value in self.audit_results.items():
            if metric in previous_results:
                previous_value = previous_results[metric]
                
                # Calculate the difference
                if isinstance(value, (int, float)) and isinstance(previous_value, (int, float)):
                    difference = value - previous_value
                    percent_change = (difference / previous_value) * 100 if previous_value != 0 else float('inf')
                    
                    comparison["differences"][metric] = {
                        "absolute": difference,
                        "percent": percent_change
                    }
                else:
                    comparison["differences"][metric] = {
                        "note": "Cannot calculate difference for non-numeric values"
                    }
            else:
                comparison["differences"][metric] = {
                    "note": "Metric not present in previous audit"
                }
        
        # Check for metrics in the previous audit that are not in the current audit
        for metric in previous_results:
            if metric not in self.audit_results:
                comparison["differences"][metric] = {
                    "note": "Metric not present in current audit"
                }
        
        return comparison
