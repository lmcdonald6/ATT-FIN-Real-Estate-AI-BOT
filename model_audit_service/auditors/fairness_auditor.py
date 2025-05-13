"""Fairness Auditor Module

This module provides an auditor for checking fairness in real estate AI models.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from model_audit_service.auditors.base_auditor import BaseAuditor

class FairnessAuditor(BaseAuditor):
    """Auditor for checking fairness in real estate AI models."""
    
    def __init__(self):
        """Initialize the fairness auditor."""
        super().__init__(name="fairness_auditor", model_type="any")
    
    def audit_model(self, model: Any, test_data: pd.DataFrame, 
                  target_column: str, protected_attributes: List[str],
                  features: List[str] = None, threshold: float = 0.5) -> Dict[str, Any]:
        """Audit a model for fairness across protected attributes.
        
        Args:
            model: Model to audit
            test_data: Test data to use for the audit
            target_column: Name of the target column
            protected_attributes: List of protected attribute columns
            features: List of feature columns to use (if None, use all columns except target)
            threshold: Decision threshold for classification models
            
        Returns:
            Dictionary of audit results
        """
        self.logger.info(f"Auditing model for fairness with {len(test_data)} test samples")
        
        # Make a copy of the test data to avoid modifying the original
        test_df = test_data.copy()
        
        # Determine the features to use
        if features is None:
            features = [col for col in test_df.columns if col != target_column and col not in protected_attributes]
        
        # Get the actual target values
        y_true = test_df[target_column].values
        
        # Get the feature values
        X_test = test_df[features]
        
        # Make predictions
        try:
            # Check if the model has a predict_proba method (for classification)
            if hasattr(model, 'predict_proba'):
                y_pred_proba = model.predict_proba(X_test)
                if y_pred_proba.shape[1] == 2:  # Binary classification
                    y_pred_proba = y_pred_proba[:, 1]  # Probability of the positive class
                else:  # Multi-class classification
                    y_pred_proba = np.max(y_pred_proba, axis=1)  # Probability of the predicted class
                
                # Apply threshold for binary decisions
                y_pred = (y_pred_proba >= threshold).astype(int)
            else:  # Regression or direct prediction
                y_pred = model.predict(X_test)
                y_pred_proba = None
        except Exception as e:
            self.logger.error(f"Error making predictions: {str(e)}")
            return {"error": str(e)}
        
        # Check for fairness across protected attributes
        fairness_metrics = {}
        for attribute in protected_attributes:
            if attribute in test_df.columns:
                fairness_metrics[attribute] = self._check_attribute_fairness(
                    test_df, attribute, y_true, y_pred, y_pred_proba
                )
        
        # Calculate overall fairness metrics
        overall_fairness = self._calculate_overall_fairness(fairness_metrics)
        
        # Combine all metrics
        self.audit_results = {
            "fairness_by_attribute": fairness_metrics,
            "overall_fairness": overall_fairness
        }
        
        self.logger.info(f"Completed fairness audit of model")
        return self.audit_results
    
    def _check_attribute_fairness(self, test_df: pd.DataFrame, attribute: str, 
                                y_true: np.ndarray, y_pred: np.ndarray, 
                                y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Check fairness for a specific protected attribute.
        
        Args:
            test_df: Test data DataFrame
            attribute: Protected attribute to check
            y_true: True target values
            y_pred: Predicted target values
            y_pred_proba: Predicted probabilities (optional)
            
        Returns:
            Dictionary of fairness metrics for the attribute
        """
        attribute_metrics = {}
        
        # Get unique values for the attribute
        unique_values = test_df[attribute].unique()
        
        # Calculate metrics for each value of the attribute
        value_metrics = {}
        for value in unique_values:
            # Get the mask for this attribute value
            mask = test_df[attribute] == value
            if np.sum(mask) < 5:  # Skip if there are too few samples
                continue
            
            # Get the true and predicted values for this attribute value
            value_y_true = y_true[mask]
            value_y_pred = y_pred[mask]
            
            # Calculate metrics based on the type of model
            if np.array_equal(np.unique(y_true), np.array([0, 1])) or np.array_equal(np.unique(y_true), np.array([0., 1.])):
                # Binary classification
                metrics = self._calculate_binary_classification_metrics(value_y_true, value_y_pred)
                
                # Add demographic parity if we have probabilities
                if y_pred_proba is not None:
                    value_y_pred_proba = y_pred_proba[mask]
                    metrics["mean_prediction"] = float(np.mean(value_y_pred_proba))
            else:
                # Regression
                metrics = self._calculate_regression_metrics(value_y_true, value_y_pred)
            
            # Add the metrics for this value
            value_metrics[str(value)] = {
                "count": int(np.sum(mask)),
                **metrics
            }
        
        # Calculate disparities between different values of the attribute
        disparities = self._calculate_disparities(value_metrics)
        
        return {
            "value_metrics": value_metrics,
            "disparities": disparities
        }
    
    def _calculate_binary_classification_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate metrics for binary classification.
        
        Args:
            y_true: True target values
            y_pred: Predicted target values
            
        Returns:
            Dictionary of classification metrics
        """
        # Calculate confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        
        # Calculate metrics
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate fairness-specific metrics
        positive_rate = (tp + fp) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0  # Rate of positive predictions
        true_positive_rate = recall  # Same as recall
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "specificity": float(specificity),
            "f1_score": float(f1_score),
            "positive_rate": float(positive_rate),
            "true_positive_rate": float(true_positive_rate),
            "false_positive_rate": float(false_positive_rate)
        }
    
    def _calculate_regression_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate metrics for regression.
        
        Args:
            y_true: True target values
            y_pred: Predicted target values
            
        Returns:
            Dictionary of regression metrics
        """
        # Calculate errors
        errors = y_true - y_pred
        abs_errors = np.abs(errors)
        squared_errors = errors ** 2
        
        # Calculate metrics
        mae = float(np.mean(abs_errors))
        mse = float(np.mean(squared_errors))
        rmse = float(np.sqrt(mse))
        
        # Calculate mean prediction
        mean_prediction = float(np.mean(y_pred))
        
        # Calculate mean true value
        mean_true = float(np.mean(y_true))
        
        # Calculate mean error
        mean_error = float(np.mean(errors))
        
        return {
            "mean_absolute_error": mae,
            "mean_squared_error": mse,
            "root_mean_squared_error": rmse,
            "mean_prediction": mean_prediction,
            "mean_true": mean_true,
            "mean_error": mean_error
        }
    
    def _calculate_disparities(self, value_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate disparities between different values of an attribute.
        
        Args:
            value_metrics: Metrics for each value of the attribute
            
        Returns:
            Dictionary of disparities
        """
        disparities = {}
        
        # Get the list of values
        values = list(value_metrics.keys())
        
        # Skip if there are fewer than 2 values
        if len(values) < 2:
            return {"note": "Not enough values to calculate disparities"}
        
        # Determine the type of metrics (classification or regression)
        first_value = values[0]
        first_metrics = value_metrics[first_value]
        is_classification = "positive_rate" in first_metrics
        
        # Calculate disparities for each pair of values
        for i, value1 in enumerate(values):
            for j, value2 in enumerate(values):
                if i < j:  # Only compare each pair once
                    metrics1 = value_metrics[value1]
                    metrics2 = value_metrics[value2]
                    
                    # Calculate disparities based on the type of metrics
                    if is_classification:
                        # Classification disparities
                        disparities[f"{value1}_vs_{value2}"] = {
                            "accuracy_disparity": metrics1["accuracy"] - metrics2["accuracy"],
                            "precision_disparity": metrics1["precision"] - metrics2["precision"],
                            "recall_disparity": metrics1["recall"] - metrics2["recall"],
                            "specificity_disparity": metrics1["specificity"] - metrics2["specificity"],
                            "f1_score_disparity": metrics1["f1_score"] - metrics2["f1_score"],
                            "positive_rate_disparity": metrics1["positive_rate"] - metrics2["positive_rate"],
                            "true_positive_rate_disparity": metrics1["true_positive_rate"] - metrics2["true_positive_rate"],
                            "false_positive_rate_disparity": metrics1["false_positive_rate"] - metrics2["false_positive_rate"]
                        }
                    else:
                        # Regression disparities
                        disparities[f"{value1}_vs_{value2}"] = {
                            "mae_disparity": metrics1["mean_absolute_error"] - metrics2["mean_absolute_error"],
                            "mse_disparity": metrics1["mean_squared_error"] - metrics2["mean_squared_error"],
                            "rmse_disparity": metrics1["root_mean_squared_error"] - metrics2["root_mean_squared_error"],
                            "mean_prediction_disparity": metrics1["mean_prediction"] - metrics2["mean_prediction"],
                            "mean_true_disparity": metrics1["mean_true"] - metrics2["mean_true"],
                            "mean_error_disparity": metrics1["mean_error"] - metrics2["mean_error"]
                        }
        
        return disparities
    
    def _calculate_overall_fairness(self, fairness_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall fairness metrics across all protected attributes.
        
        Args:
            fairness_metrics: Fairness metrics for each protected attribute
            
        Returns:
            Dictionary of overall fairness metrics
        """
        overall_fairness = {}
        
        # Calculate the maximum disparities across all attributes
        max_disparities = {}
        
        for attribute, metrics in fairness_metrics.items():
            disparities = metrics.get("disparities", {})
            
            # Skip if there are no disparities
            if not disparities or isinstance(disparities, dict) and "note" in disparities:
                continue
            
            # Iterate through all disparity pairs
            for pair, pair_disparities in disparities.items():
                for metric, value in pair_disparities.items():
                    # Update the maximum disparity for this metric
                    if metric not in max_disparities or abs(value) > abs(max_disparities[metric]["value"]):
                        max_disparities[metric] = {
                            "value": value,
                            "attribute": attribute,
                            "pair": pair
                        }
        
        # Calculate fairness scores (0-100) based on disparities
        fairness_scores = {}
        
        # Define thresholds for different metrics
        thresholds = {
            "accuracy_disparity": 0.1,
            "precision_disparity": 0.1,
            "recall_disparity": 0.1,
            "specificity_disparity": 0.1,
            "f1_score_disparity": 0.1,
            "positive_rate_disparity": 0.1,
            "true_positive_rate_disparity": 0.1,
            "false_positive_rate_disparity": 0.1,
            "mae_disparity": 0.2,
            "mse_disparity": 0.3,
            "rmse_disparity": 0.2,
            "mean_prediction_disparity": 0.2,
            "mean_true_disparity": 0.2,
            "mean_error_disparity": 0.2
        }
        
        # Calculate fairness scores
        for metric, disparity in max_disparities.items():
            threshold = thresholds.get(metric, 0.1)
            value = disparity["value"]
            
            # Calculate score (100 = perfect fairness, 0 = max unfairness)
            score = max(0, 100 * (1 - abs(value) / threshold))
            score = min(100, score)  # Cap at 100
            
            fairness_scores[metric] = {
                "score": float(score),
                "max_disparity": disparity
            }
        
        # Calculate overall fairness score (average of all scores)
        if fairness_scores:
            overall_score = np.mean([score_data["score"] for score_data in fairness_scores.values()])
        else:
            overall_score = 100  # Perfect fairness if no disparities
        
        return {
            "max_disparities": max_disparities,
            "fairness_scores": fairness_scores,
            "overall_fairness_score": float(overall_score)
        }
