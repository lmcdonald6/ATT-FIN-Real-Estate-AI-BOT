"""
Property matching utilities for data enrichment prioritization.
"""
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime

class PropertyMatcher:
    """
    Matches and scores properties for data enrichment.
    Prioritizes properties based on investment potential.
    """
    
    def __init__(self):
        # Scoring weights
        self.weights = {
            "price": 0.3,           # Higher price = higher priority
            "location": 0.25,       # Prime locations
            "property_type": 0.15,  # Certain types more valuable
            "age": 0.15,           # Newer properties
            "size": 0.15           # Larger properties
        }
        
        # Location scoring (example prime areas)
        self.prime_zips = {
            "37215": 1.0,  # Nashville Luxury
            "37203": 0.9,  # Nashville Urban
            "30305": 1.0,  # Atlanta Luxury
            "30308": 0.9,  # Atlanta Urban
            "75225": 1.0,  # Dallas Luxury
            "75201": 0.9   # Dallas Urban
        }
        
        # Property type scoring
        self.type_scores = {
            "Single Family": 1.0,
            "Multi Family": 0.9,
            "Townhouse": 0.8,
            "Condo": 0.7,
            "Land": 0.6
        }
    
    def score_property(self, property_data: Dict) -> float:
        """
        Score a property based on investment potential.
        Higher scores = higher priority for enrichment.
        """
        scores = {}
        
        # Price score (normalized to 0-1 range)
        price = float(property_data.get("price", 0))
        scores["price"] = min(price / 1_000_000, 1.0)  # Cap at $1M
        
        # Location score
        zip_code = property_data.get("zip_code", "")
        scores["location"] = self.prime_zips.get(zip_code, 0.5)
        
        # Property type score
        prop_type = property_data.get("property_type", "")
        scores["property_type"] = self.type_scores.get(prop_type, 0.5)
        
        # Age score (newer = higher score)
        year_built = int(property_data.get("year_built", 1900))
        current_year = datetime.now().year
        age_score = 1.0 - ((current_year - year_built) / 100)
        scores["age"] = max(0, min(1, age_score))
        
        # Size score (normalized to 0-1 range)
        sqft = float(property_data.get("sqft", 0))
        scores["size"] = min(sqft / 5000, 1.0)  # Cap at 5000 sqft
        
        # Calculate weighted score
        final_score = sum(
            scores[metric] * weight 
            for metric, weight in self.weights.items()
        )
        
        return round(final_score, 3)
    
    def prioritize_properties(
        self,
        properties: List[Dict],
        limit: int = None
    ) -> List[Tuple[Dict, float]]:
        """
        Score and sort properties by enrichment priority.
        Returns: List of (property, score) tuples.
        """
        # Score all properties
        scored_properties = [
            (prop, self.score_property(prop))
            for prop in properties
        ]
        
        # Sort by score (highest first)
        scored_properties.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N if limit specified
        if limit:
            return scored_properties[:limit]
        return scored_properties
    
    def find_similar_properties(
        self,
        target: Dict,
        candidates: List[Dict],
        threshold: float = 0.8
    ) -> List[Tuple[Dict, float]]:
        """
        Find properties similar to target property.
        Returns: List of (property, similarity_score) tuples.
        """
        similar_properties = []
        
        for candidate in candidates:
            similarity = self._calculate_similarity(target, candidate)
            if similarity >= threshold:
                similar_properties.append((candidate, similarity))
        
        # Sort by similarity (highest first)
        similar_properties.sort(key=lambda x: x[1], reverse=True)
        return similar_properties
    
    def _calculate_similarity(
        self,
        prop1: Dict,
        prop2: Dict
    ) -> float:
        """Calculate similarity score between two properties."""
        scores = []
        
        # Price similarity (within 20%)
        price1 = float(prop1.get("price", 0))
        price2 = float(prop2.get("price", 0))
        if price1 and price2:
            price_diff = abs(price1 - price2) / max(price1, price2)
            scores.append(1.0 - min(price_diff, 1.0))
        
        # Location similarity (same zip = 1.0)
        zip1 = prop1.get("zip_code", "")
        zip2 = prop2.get("zip_code", "")
        scores.append(1.0 if zip1 == zip2 else 0.0)
        
        # Property type similarity
        type1 = prop1.get("property_type", "")
        type2 = prop2.get("property_type", "")
        scores.append(1.0 if type1 == type2 else 0.0)
        
        # Size similarity (within 20%)
        sqft1 = float(prop1.get("sqft", 0))
        sqft2 = float(prop2.get("sqft", 0))
        if sqft1 and sqft2:
            size_diff = abs(sqft1 - sqft2) / max(sqft1, sqft2)
            scores.append(1.0 - min(size_diff, 1.0))
        
        # Return average similarity score
        return round(sum(scores) / len(scores), 3) if scores else 0.0
