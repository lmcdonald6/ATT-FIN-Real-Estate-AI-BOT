#!/usr/bin/env python3
"""
Base Inference Layer

This module defines the base interface for all temporal inference layers
(Past, Present, Future) in the Real Estate Intelligence Core (REIC).
"""

import os
import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)


class InferenceLayer(ABC):
    """
    Abstract base class for all inference layers.
    Defines the common interface that all temporal layers must implement.
    """
    
    def __init__(self, name: str):
        """
        Initialize the inference layer.
        
        Args:
            name: Name of the inference layer
        """
        self.name = name
        logger.info(f"Initializing {name} inference layer")
    
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query using this inference layer.
        
        Args:
            query: The user query to process
            context: Additional context for the query
            
        Returns:
            Dictionary with the processed results
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this layer provides.
        
        Returns:
            List of capability strings
        """
        pass
    
    def is_relevant_for_query(self, query: str) -> bool:
        """
        Determine if this layer is relevant for the given query.
        
        Args:
            query: The user query to check
            
        Returns:
            True if this layer is relevant, False otherwise
        """
        # Default implementation checks if any capability keywords are in the query
        capabilities = self.get_capabilities()
        query_lower = query.lower()
        
        for capability in capabilities:
            if capability.lower() in query_lower:
                return True
        
        return False
    
    def __str__(self) -> str:
        return f"{self.name} Inference Layer"
    
    def __repr__(self) -> str:
        return f"<{self.name}InferenceLayer>"
