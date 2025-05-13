"""Model Audit Service Main Module

This module provides the main entry point for the model audit service.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime

import pandas as pd
import joblib

# Import auditors
from model_audit_service.auditors.price_prediction_auditor import PricePredictionAuditor
from model_audit_service.auditors.fairness_auditor import FairnessAuditor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'audit.log'))
    ]
)
logger = logging.getLogger('model_audit_service')

class ModelAuditService:
    """Main class for the model audit service."""
    
    def __init__(self):
        """Initialize the model audit service."""
        self.logger = logging.getLogger('model_audit_service')
        self.price_prediction_auditor = PricePredictionAuditor()
        self.fairness_auditor = FairnessAuditor()
        
        # Create audit results directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'audit_results'), exist_ok=True)
    
    def audit_price_prediction_model(self, model_path: str, test_data_path: str, 
                                  target_column: str, features: List[str] = None) -> Dict[str, Any]:
        """Audit a price prediction model.
        
        Args:
            model_path: Path to the model file
            test_data_path: Path to the test data file
            target_column: Name of the target column
            features: List of feature columns to use (if None, use all columns except target)
            
        Returns:
            Dictionary of audit results
        """
        self.logger.info(f"Auditing price prediction model at {model_path}")
        
        # Load the model
        try:
            model = joblib.load(model_path)
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return {"error": f"Error loading model: {str(e)}"}
        
        # Load the test data
        try:
            if test_data_path.endswith('.csv'):
                test_data = pd.read_csv(test_data_path)
            elif test_data_path.endswith('.json'):
                test_data = pd.read_json(test_data_path)
            elif test_data_path.endswith('.parquet'):
                test_data = pd.read_parquet(test_data_path)
            else:
                self.logger.error(f"Unsupported test data format: {test_data_path}")
                return {"error": f"Unsupported test data format: {test_data_path}"}
        except Exception as e:
            self.logger.error(f"Error loading test data: {str(e)}")
            return {"error": f"Error loading test data: {str(e)}"}
        
        # Audit the model
        audit_results = self.price_prediction_auditor.audit_model(
            model=model,
            test_data=test_data,
            target_column=target_column,
            features=features
        )
        
        # Generate an audit ID
        audit_id = f"price_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save the audit results
        results_path = self.price_prediction_auditor.save_audit_results(audit_id)
        
        self.logger.info(f"Completed audit of price prediction model, results saved to {results_path}")
        return {
            "audit_id": audit_id,
            "results_path": results_path,
            "audit_results": audit_results
        }
    
    def audit_model_fairness(self, model_path: str, test_data_path: str, 
                           target_column: str, protected_attributes: List[str],
                           features: List[str] = None, threshold: float = 0.5) -> Dict[str, Any]:
        """Audit a model for fairness.
        
        Args:
            model_path: Path to the model file
            test_data_path: Path to the test data file
            target_column: Name of the target column
            protected_attributes: List of protected attribute columns
            features: List of feature columns to use (if None, use all columns except target and protected attributes)
            threshold: Decision threshold for classification models
            
        Returns:
            Dictionary of audit results
        """
        self.logger.info(f"Auditing model fairness at {model_path}")
        
        # Load the model
        try:
            model = joblib.load(model_path)
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return {"error": f"Error loading model: {str(e)}"}
        
        # Load the test data
        try:
            if test_data_path.endswith('.csv'):
                test_data = pd.read_csv(test_data_path)
            elif test_data_path.endswith('.json'):
                test_data = pd.read_json(test_data_path)
            elif test_data_path.endswith('.parquet'):
                test_data = pd.read_parquet(test_data_path)
            else:
                self.logger.error(f"Unsupported test data format: {test_data_path}")
                return {"error": f"Unsupported test data format: {test_data_path}"}
        except Exception as e:
            self.logger.error(f"Error loading test data: {str(e)}")
            return {"error": f"Error loading test data: {str(e)}"}
        
        # Audit the model for fairness
        audit_results = self.fairness_auditor.audit_model(
            model=model,
            test_data=test_data,
            target_column=target_column,
            protected_attributes=protected_attributes,
            features=features,
            threshold=threshold
        )
        
        # Generate an audit ID
        audit_id = f"fairness_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save the audit results
        results_path = self.fairness_auditor.save_audit_results(audit_id)
        
        self.logger.info(f"Completed fairness audit of model, results saved to {results_path}")
        return {
            "audit_id": audit_id,
            "results_path": results_path,
            "audit_results": audit_results
        }
    
    def compare_audit_results(self, current_audit_path: str, previous_audit_path: str) -> Dict[str, Any]:
        """Compare current audit results with previous audit results.
        
        Args:
            current_audit_path: Path to the current audit results file
            previous_audit_path: Path to the previous audit results file
            
        Returns:
            Dictionary of comparison results
        """
        self.logger.info(f"Comparing audit results: {current_audit_path} vs {previous_audit_path}")
        
        # Determine the auditor to use based on the file name
        if "price_prediction" in current_audit_path:
            auditor = self.price_prediction_auditor
        elif "fairness" in current_audit_path:
            auditor = self.fairness_auditor
        else:
            self.logger.error(f"Unknown audit type in {current_audit_path}")
            return {"error": f"Unknown audit type in {current_audit_path}"}
        
        # Load the current audit results
        current_audit = auditor.load_audit_results(current_audit_path)
        if not current_audit:
            self.logger.error(f"Error loading current audit results from {current_audit_path}")
            return {"error": f"Error loading current audit results from {current_audit_path}"}
        
        # Load the previous audit results
        previous_audit = auditor.load_audit_results(previous_audit_path)
        if not previous_audit:
            self.logger.error(f"Error loading previous audit results from {previous_audit_path}")
            return {"error": f"Error loading previous audit results from {previous_audit_path}"}
        
        # Compare the audit results
        comparison = auditor.compare_audit_results(previous_audit)
        
        # Generate a comparison ID
        comparison_id = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save the comparison results
        comparison_dir = os.path.join(os.path.dirname(__file__), 'audit_results')
        os.makedirs(comparison_dir, exist_ok=True)
        
        comparison_path = os.path.join(comparison_dir, f"{comparison_id}.json")
        with open(comparison_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, default=str)
        
        self.logger.info(f"Completed comparison of audit results, saved to {comparison_path}")
        return {
            "comparison_id": comparison_id,
            "comparison_path": comparison_path,
            "comparison_results": comparison
        }

# Command-line interface
def main():
    """Main entry point for the model audit service."""
    parser = argparse.ArgumentParser(description="Real Estate AI Model Audit Service")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Price prediction audit command
    price_parser = subparsers.add_parser("audit-price", help="Audit a price prediction model")
    price_parser.add_argument("--model", type=str, required=True, help="Path to the model file")
    price_parser.add_argument("--test-data", type=str, required=True, help="Path to the test data file")
    price_parser.add_argument("--target", type=str, required=True, help="Name of the target column")
    price_parser.add_argument("--features", type=str, nargs="+", help="List of feature columns to use")
    
    # Fairness audit command
    fairness_parser = subparsers.add_parser("audit-fairness", help="Audit a model for fairness")
    fairness_parser.add_argument("--model", type=str, required=True, help="Path to the model file")
    fairness_parser.add_argument("--test-data", type=str, required=True, help="Path to the test data file")
    fairness_parser.add_argument("--target", type=str, required=True, help="Name of the target column")
    fairness_parser.add_argument("--protected", type=str, nargs="+", required=True, help="List of protected attribute columns")
    fairness_parser.add_argument("--features", type=str, nargs="+", help="List of feature columns to use")
    fairness_parser.add_argument("--threshold", type=float, default=0.5, help="Decision threshold for classification models")
    
    # Compare audit results command
    compare_parser = subparsers.add_parser("compare", help="Compare audit results")
    compare_parser.add_argument("--current", type=str, required=True, help="Path to the current audit results file")
    compare_parser.add_argument("--previous", type=str, required=True, help="Path to the previous audit results file")
    
    args = parser.parse_args()
    
    # Create the model audit service
    service = ModelAuditService()
    
    # Run the appropriate command
    if args.command == "audit-price":
        results = service.audit_price_prediction_model(
            model_path=args.model,
            test_data_path=args.test_data,
            target_column=args.target,
            features=args.features
        )
        print(json.dumps(results, indent=2, default=str))
    
    elif args.command == "audit-fairness":
        results = service.audit_model_fairness(
            model_path=args.model,
            test_data_path=args.test_data,
            target_column=args.target,
            protected_attributes=args.protected,
            features=args.features,
            threshold=args.threshold
        )
        print(json.dumps(results, indent=2, default=str))
    
    elif args.command == "compare":
        results = service.compare_audit_results(
            current_audit_path=args.current,
            previous_audit_path=args.previous
        )
        print(json.dumps(results, indent=2, default=str))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
