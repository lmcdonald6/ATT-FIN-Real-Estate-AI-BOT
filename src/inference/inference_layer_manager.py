#!/usr/bin/env python3
"""
Inference Layer Manager

This module implements the Inference Layer Manager for the
Real Estate Intelligence Core (REIC), coordinating between
Past, Present, and Future temporal inference layers.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union, Type
import re

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import inference layers
from src.inference.base_layer import InferenceLayer
from src.inference.past_layer import PastInferenceLayer
from src.inference.present_layer import PresentInferenceLayer
from src.inference.future_layer import FutureInferenceLayer


class InferenceLayerManager:
    """
    Manager for coordinating between temporal inference layers.
    
    This class is responsible for:
    1. Determining which layer(s) are relevant for a query
    2. Routing queries to the appropriate layer(s)
    3. Combining results from multiple layers when needed
    4. Providing a unified interface to the orchestrator
    """
    
    def __init__(self):
        """
        Initialize the Inference Layer Manager with all temporal layers.
        """
        logger.info("Initializing Inference Layer Manager")
        
        # Initialize all layers
        self.past_layer = PastInferenceLayer()
        self.present_layer = PresentInferenceLayer()
        self.future_layer = FutureInferenceLayer()
        
        # Store layers in a dictionary for easy access
        self.layers = {
            "past": self.past_layer,
            "present": self.present_layer,
            "future": self.future_layer
        }
        
        logger.info("Inference Layer Manager initialized with all temporal layers")
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query using the appropriate inference layer(s).
        
        Args:
            query: The user query to process
            context: Additional context for the query (optional)
            
        Returns:
            Dictionary with the processed results
        """
        if context is None:
            context = {}
        
        logger.info(f"Processing query: {query}")
        
        # Determine which layers are relevant for this query
        relevant_layers = self._determine_relevant_layers(query)
        logger.info(f"Relevant layers for query: {', '.join(relevant_layers)}")
        
        # If no layers are relevant, default to present
        if not relevant_layers:
            logger.info("No relevant layers found, defaulting to present layer")
            relevant_layers = ["present"]
        
        # Extract entities from query to enhance context
        enhanced_context = self._extract_entities(query, context)
        
        # Process query with each relevant layer
        layer_results = {}
        for layer_name in relevant_layers:
            layer = self.layers[layer_name]
            layer_results[layer_name] = layer.process_query(query, enhanced_context)
        
        # Combine results if multiple layers were used
        if len(layer_results) > 1:
            combined_result = self._combine_layer_results(layer_results, query)
            return combined_result
        else:
            # Return the single layer result
            return list(layer_results.values())[0]
    
    def _determine_relevant_layers(self, query: str) -> List[str]:
        """
        Determine which layers are relevant for the given query.
        
        Args:
            query: The user query to check
            
        Returns:
            List of relevant layer names
        """
        relevant_layers = []
        
        # Check each layer for relevance
        for layer_name, layer in self.layers.items():
            if layer.is_relevant_for_query(query):
                relevant_layers.append(layer_name)
        
        return relevant_layers
    
    def _extract_entities(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities from the query to enhance context.
        
        Args:
            query: The user query to process
            context: Existing context dictionary
            
        Returns:
            Enhanced context dictionary
        """
        # Create a copy of the context to avoid modifying the original
        enhanced_context = context.copy()
        
        # Extract ZIP codes if not already in context
        if "zip_codes" not in enhanced_context or not enhanced_context["zip_codes"]:
            zip_codes = self._extract_zip_codes(query)
            if zip_codes:
                enhanced_context["zip_codes"] = zip_codes
        
        # Extract streets if not already in context
        if "streets" not in enhanced_context or not enhanced_context["streets"]:
            streets = self._extract_streets(query)
            if streets:
                enhanced_context["streets"] = streets
        
        # Extract time frame if not already in context
        if "years_back" not in enhanced_context and "months_ahead" not in enhanced_context:
            years_back, months_ahead = self._extract_time_frame(query)
            if years_back is not None:
                enhanced_context["years_back"] = years_back
            if months_ahead is not None:
                enhanced_context["months_ahead"] = months_ahead
        
        # Extract investment type if not already in context
        if "investment_type" not in enhanced_context:
            investment_type = self._extract_investment_type(query)
            if investment_type:
                enhanced_context["investment_type"] = investment_type
        
        return enhanced_context
    
    def _extract_zip_codes(self, query: str) -> List[str]:
        """
        Extract ZIP codes from the query.
        
        Args:
            query: The user query to process
            
        Returns:
            List of ZIP codes
        """
        # Look for 5-digit ZIP codes
        zip_pattern = r'\b(\d{5})\b'
        zip_codes = re.findall(zip_pattern, query)
        
        # Also look for ZIP codes mentioned as "ZIP: 12345" or similar
        zip_label_pattern = r'\b[Zz][Ii][Pp]\s*(?:code)?\s*:?\s*(\d{5})\b'
        labeled_zips = re.findall(zip_label_pattern, query)
        
        # Combine and deduplicate
        all_zips = list(set(zip_codes + labeled_zips))
        
        return all_zips
    
    def _extract_streets(self, query: str) -> List[str]:
        """
        Extract street names from the query.
        
        Args:
            query: The user query to process
            
        Returns:
            List of street names
        """
        # This is a simplified approach - in a real system, you would use NER or a more
        # sophisticated approach to extract street names
        
        # Look for common street suffixes
        street_suffixes = ["Street", "St", "Avenue", "Ave", "Road", "Rd", "Boulevard", "Blvd", 
                          "Lane", "Ln", "Drive", "Dr", "Court", "Ct", "Place", "Pl", "Way"]
        
        # Create pattern to match "<Word> <Suffix>"
        suffix_pattern = "|".join([s + "\\b" for s in street_suffixes])
        street_pattern = r'\b([A-Z][a-z]+ (?:' + suffix_pattern + '))'
        
        # Find all matches
        streets = re.findall(street_pattern, query)
        
        return streets
    
    def _extract_time_frame(self, query: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extract time frame from the query.
        
        Args:
            query: The user query to process
            
        Returns:
            Tuple of (years_back, months_ahead)
        """
        years_back = None
        months_ahead = None
        
        # Look for past time references
        past_patterns = [
            r'\b(\d+)\s+years?\s+(?:ago|back|history|historical|past)\b',
            r'\bpast\s+(\d+)\s+years?\b',
            r'\bover\s+(?:the\s+)?(?:last|past)\s+(\d+)\s+years?\b'
        ]
        
        for pattern in past_patterns:
            matches = re.findall(pattern, query.lower())
            if matches:
                try:
                    years_back = int(matches[0])
                    break
                except (ValueError, IndexError):
                    pass
        
        # Look for future time references
        future_patterns = [
            r'\b(?:next|coming|following|future)\s+(\d+)\s+months?\b',
            r'\b(\d+)\s+months?\s+(?:ahead|forward|future|forecast|projection)\b',
            r'\b(?:next|coming|following|future)\s+(\d+)\s+years?\b',
            r'\b(\d+)\s+years?\s+(?:ahead|forward|future|forecast|projection)\b'
        ]
        
        for pattern in future_patterns:
            matches = re.findall(pattern, query.lower())
            if matches:
                try:
                    value = int(matches[0])
                    if "year" in pattern:
                        months_ahead = value * 12
                    else:
                        months_ahead = value
                    break
                except (ValueError, IndexError):
                    pass
        
        return years_back, months_ahead
    
    def _extract_investment_type(self, query: str) -> Optional[str]:
        """
        Extract investment type from the query.
        
        Args:
            query: The user query to process
            
        Returns:
            Investment type string or None
        """
        # Define investment types to look for
        investment_types = {
            "residential": ["residential", "housing", "homes", "apartments", "condos"],
            "commercial": ["commercial", "office", "retail", "shopping", "business"],
            "industrial": ["industrial", "warehouse", "manufacturing", "factory"],
            "mixed-use": ["mixed-use", "mixed use", "multi-use"],
            "land": ["land", "vacant", "undeveloped", "lot"]
        }
        
        query_lower = query.lower()
        
        # Check for each investment type
        for inv_type, keywords in investment_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return inv_type
        
        # Default to residential if no specific type is found
        return None
    
    def _combine_layer_results(self, layer_results: Dict[str, Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Combine results from multiple layers into a unified response.
        
        Args:
            layer_results: Dictionary of layer results keyed by layer name
            query: The original user query
            
        Returns:
            Combined result dictionary
        """
        # Create base combined result
        combined_result = {
            "query": query,
            "layers_used": list(layer_results.keys()),
            "temporal_analysis": {}
        }
        
        # Extract and combine insights from all layers
        all_insights = []
        for layer_name, result in layer_results.items():
            # Add layer-specific results to temporal_analysis
            combined_result["temporal_analysis"][layer_name] = result
            
            # Extract insights
            insights = result.get("insights", [])
            for insight in insights:
                insight["layer"] = layer_name
                all_insights.append(insight)
        
        # Add combined insights
        combined_result["insights"] = all_insights
        
        # Extract ZIP codes from results
        zip_codes = set()
        for layer_name, result in layer_results.items():
            results_by_zip = result.get("results", {})
            zip_codes.update(results_by_zip.keys())
        
        combined_result["zip_codes"] = list(zip_codes)
        
        # Generate a summary that spans all temporal layers
        combined_result["summary"] = self._generate_cross_temporal_summary(layer_results, zip_codes)
        
        return combined_result
    
    def _generate_cross_temporal_summary(self, layer_results: Dict[str, Dict[str, Any]], zip_codes: set) -> str:
        """
        Generate a summary that spans all temporal layers.
        
        Args:
            layer_results: Dictionary of layer results keyed by layer name
            zip_codes: Set of ZIP codes in the results
            
        Returns:
            Summary string
        """
        # This would be more sophisticated in a real implementation
        # For now, we'll create a simple summary
        
        layers_used = list(layer_results.keys())
        layers_str = ", ".join(layers_used)
        zips_str = ", ".join(zip_codes)
        
        summary = f"Analysis across {layers_str} temporal layers for ZIP code(s) {zips_str}.\n\n"
        
        # Add layer-specific summaries
        for layer_name in sorted(layer_results.keys()):
            result = layer_results[layer_name]
            
            # Extract a representative summary from the layer
            layer_summary = ""
            
            if layer_name == "past":
                time_range = result.get("time_range", {})
                years = time_range.get("years", "unknown")
                layer_summary = f"Historical analysis over {years} years shows "
            elif layer_name == "present":
                layer_summary = "Current market conditions indicate "
            elif layer_name == "future":
                horizon = result.get("horizon_months", "unknown")
                layer_summary = f"Future projections over {horizon} months suggest "
            
            # Add insights from this layer
            insights = result.get("insights", [])
            if insights:
                # Take the first 2 insights
                for i, insight in enumerate(insights[:2]):
                    if i > 0:
                        layer_summary += " Additionally, "
                    layer_summary += insight.get("insight", "").lower()
                layer_summary += "."
            else:
                layer_summary += "insufficient data for detailed insights."
            
            summary += f"{layer_name.capitalize()} Layer: {layer_summary}\n\n"
        
        return summary
