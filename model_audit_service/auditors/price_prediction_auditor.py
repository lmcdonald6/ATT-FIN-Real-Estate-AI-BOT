"""Price Prediction Auditor Module

This module provides an auditor for real estate price prediction models.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from model_audit_service.auditors.base_auditor import BaseAuditor

class PricePredictionAuditor(BaseAuditor):
    """Auditor for real estate price prediction models."""
    
    def __init__(self):
        """Initialize the price prediction auditor."""
        super().__init__(name="price_prediction_auditor", model_type="regression")
    
    def audit_model(self, model: Any, test_data: pd.DataFrame, 
                  target_column: str, features: List[str] = None) -> Dict[str, Any]:
        """Audit a price prediction model for performance, bias, and other metrics.
        
        Args:
            model: Model to audit
            test_data: Test data to use for the audit
            target_column: Name of the target column
            features: List of feature columns to use (if None, use all columns except target)
            
        Returns:
            Dictionary of audit results
        """
        self.logger.info(f"Auditing price prediction model with {len(test_data)} test samples")
        
        # Make a copy of the test data to avoid modifying the original
        test_df = test_data.copy()
        
        # Determine the features to use
        if features is None:
            features = [col for col in test_df.columns if col != target_column]
        
        # Get the actual target values
        y_true = test_df[target_column].values
        
        # Get the feature values
        X_test = test_df[features]
        
        # Make predictions
        try:
            y_pred = model.predict(X_test)
        except Exception as e:
            self.logger.error(f"Error making predictions: {str(e)}")
            return {"error": str(e)}
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(y_true, y_pred)
        
        # Check for bias in predictions
        bias_metrics = self._check_for_bias(test_df, y_true, y_pred, features)
        
        # Check for feature importance
        feature_importance = self._check_feature_importance(model, features)
        
        # Check for prediction distribution
        prediction_distribution = self._check_prediction_distribution(y_true, y_pred)
        
        # Check for outliers in predictions
        outlier_metrics = self._check_for_outliers(y_true, y_pred)
        
        # Combine all metrics
        self.audit_results = {
            "performance_metrics": performance_metrics,
            "bias_metrics": bias_metrics,
            "feature_importance": feature_importance,
            "prediction_distribution": prediction_distribution,
            "outlier_metrics": outlier_metrics
        }
        
        self.logger.info(f"Completed audit of price prediction model")
        return self.audit_results
    
    def _calculate_performance_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics for the model.
        
        Args:
            y_true: True target values
            y_pred: Predicted target values
            
        Returns:
            Dictionary of performance metrics
        """
        # Calculate regression metrics
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        # Calculate mean absolute percentage error (MAPE)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        # Calculate median absolute error
        median_ae = np.median(np.abs(y_true - y_pred))
        
        return {
            "mean_absolute_error": mae,
            "mean_squared_error": mse,
            "root_mean_squared_error": rmse,
            "r2_score": r2,
            "mean_absolute_percentage_error": mape,
            "median_absolute_error": median_ae
        }
    
    def _check_for_bias(self, test_df: pd.DataFrame, y_true: np.ndarray, 
                       y_pred: np.ndarray, features: List[str]) -> Dict[str, Any]:
        """Check for bias in the model predictions.
        
        Args:
            test_df: Test data DataFrame
            y_true: True target values
            y_pred: Predicted target values
            features: List of feature columns
            
        Returns:
            Dictionary of bias metrics
        """
        bias_metrics = {}
        
        # Calculate prediction errors
        errors = y_true - y_pred
        
        # Check for bias by price range
        price_ranges = [
            (0, 100000),
            (100000, 250000),
            (250000, 500000),
            (500000, 1000000),
            (1000000, float('inf'))
        ]
        
        price_range_bias = {}
        for lower, upper in price_ranges:
            mask = (y_true >= lower) & (y_true < upper)
            if np.sum(mask) > 0:
                range_errors = errors[mask]
                price_range_bias[f"{lower}-{upper}"] = {
                    "count": int(np.sum(mask)),
                    "mean_error": float(np.mean(range_errors)),
                    "median_error": float(np.median(range_errors)),
                    "mean_absolute_error": float(np.mean(np.abs(range_errors))),
                    "mean_percentage_error": float(np.mean(range_errors / y_true[mask]) * 100)
                }
        
        bias_metrics["price_range_bias"] = price_range_bias
        
        # Check for bias by location (if available)
        location_columns = [col for col in test_df.columns if any(loc_type in col.lower() for loc_type in 
                                                              ["city", "state", "zip", "location", "region"])]
        
        location_bias = {}
        for col in location_columns:
            if col in test_df.columns:
                location_bias[col] = {}
                for location in test_df[col].unique():
                    mask = test_df[col] == location
                    if np.sum(mask) > 5:  # Only include locations with enough samples
                        loc_errors = errors[mask]
                        location_bias[col][str(location)] = {
                            "count": int(np.sum(mask)),
                            "mean_error": float(np.mean(loc_errors)),
                            "median_error": float(np.median(loc_errors)),
                            "mean_absolute_error": float(np.mean(np.abs(loc_errors))),
                            "mean_percentage_error": float(np.mean(loc_errors / y_true[mask]) * 100)
                        }
        
        bias_metrics["location_bias"] = location_bias
        
        # Check for bias by property type (if available)
        property_type_columns = [col for col in test_df.columns if any(prop_type in col.lower() for prop_type in 
                                                                   ["type", "property", "home", "house", "condo"])]
        
        property_type_bias = {}
        for col in property_type_columns:
            if col in test_df.columns:
                property_type_bias[col] = {}
                for prop_type in test_df[col].unique():
                    mask = test_df[col] == prop_type
                    if np.sum(mask) > 5:  # Only include property types with enough samples
                        type_errors = errors[mask]
                        property_type_bias[col][str(prop_type)] = {
                            "count": int(np.sum(mask)),
                            "mean_error": float(np.mean(type_errors)),
                            "median_error": float(np.median(type_errors)),
                            "mean_absolute_error": float(np.mean(np.abs(type_errors))),
                            "mean_percentage_error": float(np.mean(type_errors / y_true[mask]) * 100)
                        }
        
        bias_metrics["property_type_bias"] = property_type_bias
        
        return bias_metrics
    
    def _check_feature_importance(self, model: Any, features: List[str]) -> Dict[str, float]:
        """Check the importance of each feature in the model.
        
        Args:
            model: Model to check
            features: List of feature columns
            
        Returns:
            Dictionary of feature importance
        """
        feature_importance = {}
        
        # Try to get feature importance from the model
        try:
            if hasattr(model, "feature_importances_"):
                # For tree-based models
                importances = model.feature_importances_
                for feature, importance in zip(features, importances):
                    feature_importance[feature] = float(importance)
            elif hasattr(model, "coef_"):
                # For linear models
                coefficients = model.coef_
                if len(coefficients.shape) > 1:
                    coefficients = coefficients[0]  # Take the first set of coefficients
                for feature, coef in zip(features, coefficients):
                    feature_importance[feature] = float(abs(coef))
            else:
                # For models without built-in feature importance
                feature_importance = {"note": "Model does not provide feature importance"}
        except Exception as e:
            self.logger.warning(f"Error getting feature importance: {str(e)}")
            feature_importance = {"error": str(e)}
        
        return feature_importance
    
    def _check_prediction_distribution(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Check the distribution of predictions compared to actual values.
        
        Args:
            y_true: True target values
            y_pred: Predicted target values
            
        Returns:
            Dictionary of prediction distribution metrics
        """
        # Calculate basic statistics
        true_mean = float(np.mean(y_true))
        true_median = float(np.median(y_true))
        true_std = float(np.std(y_true))
        true_min = float(np.min(y_true))
        true_max = float(np.max(y_true))
        
        pred_mean = float(np.mean(y_pred))
        pred_median = float(np.median(y_pred))
        pred_std = float(np.std(y_pred))
        pred_min = float(np.min(y_pred))
        pred_max = float(np.max(y_pred))
        
        # Calculate percentiles
        true_percentiles = {
            "10th": float(np.percentile(y_true, 10)),
            "25th": float(np.percentile(y_true, 25)),
            "50th": float(np.percentile(y_true, 50)),
            "75th": float(np.percentile(y_true, 75)),
            "90th": float(np.percentile(y_true, 90))
        }
        
        pred_percentiles = {
            "10th": float(np.percentile(y_pred, 10)),
            "25th": float(np.percentile(y_pred, 25)),
            "50th": float(np.percentile(y_pred, 50)),
            "75th": float(np.percentile(y_pred, 75)),
            "90th": float(np.percentile(y_pred, 90))
        }
        
        # Calculate the difference between predicted and actual distributions
        distribution_diff = {
            "mean_diff": pred_mean - true_mean,
            "median_diff": pred_median - true_median,
            "std_diff": pred_std - true_std,
            "range_diff": (pred_max - pred_min) - (true_max - true_min),
            "percentile_diffs": {
                percentile: pred_percentiles[percentile] - true_percentiles[percentile]
                for percentile in true_percentiles
            }
        }
        
        return {
            "true_distribution": {
                "mean": true_mean,
                "median": true_median,
                "std": true_std,
                "min": true_min,
                "max": true_max,
                "percentiles": true_percentiles
            },
            "pred_distribution": {
                "mean": pred_mean,
                "median": pred_median,
                "std": pred_std,
                "min": pred_min,
                "max": pred_max,
                "percentiles": pred_percentiles
            },
            "distribution_diff": distribution_diff
        }
    
    def _check_for_outliers(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Check for outliers in the predictions.
        
        Args:
            y_true: True target values
            y_pred: Predicted target values
            
        Returns:
            Dictionary of outlier metrics
        """
        # Calculate prediction errors
        errors = y_true - y_pred
        abs_errors = np.abs(errors)
        
        # Calculate error statistics
        mean_error = float(np.mean(errors))
        median_error = float(np.median(errors))
        std_error = float(np.std(errors))
        
        # Define outliers as predictions with errors more than 2 standard deviations from the mean
        outlier_threshold = 2 * std_error
        outlier_mask = abs_errors > outlier_threshold
        
        # Count the number of outliers
        num_outliers = int(np.sum(outlier_mask))
        outlier_percentage = float(num_outliers / len(y_true) * 100)
        
        # Get the indices of the outliers
        outlier_indices = np.where(outlier_mask)[0].tolist()
        
        # Get the true and predicted values for the outliers
        outlier_true = y_true[outlier_mask].tolist()
        outlier_pred = y_pred[outlier_mask].tolist()
        outlier_errors = errors[outlier_mask].tolist()
        
        # Calculate the mean and median error for the outliers
        outlier_mean_error = float(np.mean(outlier_errors)) if num_outliers > 0 else 0
        outlier_median_error = float(np.median(outlier_errors)) if num_outliers > 0 else 0
        
        return {
            "num_outliers": num_outliers,
            "outlier_percentage": outlier_percentage,
            "outlier_threshold": float(outlier_threshold),
            "outlier_mean_error": outlier_mean_error,
            "outlier_median_error": outlier_median_error,
            "outlier_samples": [
                {
                    "index": int(idx),
                    "true_value": float(true),
                    "pred_value": float(pred),
                    "error": float(error)
                }
                for idx, true, pred, error in zip(
                    outlier_indices[:10],  # Limit to 10 samples
                    outlier_true[:10],
                    outlier_pred[:10],
                    outlier_errors[:10]
                )
            ] if num_outliers > 0 else []
        }
