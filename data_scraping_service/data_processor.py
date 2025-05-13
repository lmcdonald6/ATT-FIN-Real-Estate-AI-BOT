"""Data Processor Module

This module provides functions to process, clean, and transform scraped real estate data.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_processor')

class DataProcessor:
    """Processor for real estate data."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = logging.getLogger('data_processor')
    
    def clean_property_data(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and standardize property data.
        
        Args:
            properties: List of property data dictionaries
            
        Returns:
            Cleaned property data
        """
        self.logger.info(f"Cleaning {len(properties)} properties")
        
        cleaned_properties = []
        
        for property_data in properties:
            # Create a copy of the property data
            cleaned_property = property_data.copy()
            
            # Clean price
            if "price" in cleaned_property:
                cleaned_property["price"] = self._clean_price(cleaned_property["price"])
            
            # Clean square footage
            if "square_footage" in cleaned_property:
                cleaned_property["square_footage"] = self._clean_numeric(cleaned_property["square_footage"])
            
            # Clean lot size
            if "lot_size" in cleaned_property:
                cleaned_property["lot_size"] = self._clean_numeric(cleaned_property["lot_size"])
            
            # Clean bedrooms
            if "bedrooms" in cleaned_property:
                cleaned_property["bedrooms"] = self._clean_numeric(cleaned_property["bedrooms"])
            
            # Clean bathrooms
            if "bathrooms" in cleaned_property:
                cleaned_property["bathrooms"] = self._clean_numeric(cleaned_property["bathrooms"])
            
            # Clean year built
            if "year_built" in cleaned_property:
                cleaned_property["year_built"] = self._clean_numeric(cleaned_property["year_built"])
            
            # Add timestamp
            cleaned_property["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add to cleaned properties
            cleaned_properties.append(cleaned_property)
        
        self.logger.info(f"Cleaned {len(cleaned_properties)} properties")
        return cleaned_properties
    
    def clean_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize market data.
        
        Args:
            market_data: Market data dictionary
            
        Returns:
            Cleaned market data
        """
        self.logger.info(f"Cleaning market data for {market_data.get('location', 'Unknown')}")
        
        # Create a copy of the market data
        cleaned_market = market_data.copy()
        
        # Clean median listing price
        if "median_listing_price" in cleaned_market:
            cleaned_market["median_listing_price"] = self._clean_price(cleaned_market["median_listing_price"])
        
        # Clean median sold price
        if "median_sold_price" in cleaned_market:
            cleaned_market["median_sold_price"] = self._clean_price(cleaned_market["median_sold_price"])
        
        # Clean median rent price
        if "median_rent_price" in cleaned_market:
            cleaned_market["median_rent_price"] = self._clean_price(cleaned_market["median_rent_price"])
        
        # Clean median price per sqft
        if "median_price_per_sqft" in cleaned_market:
            cleaned_market["median_price_per_sqft"] = self._clean_price(cleaned_market["median_price_per_sqft"])
        
        # Clean median days on market
        if "median_days_on_market" in cleaned_market:
            cleaned_market["median_days_on_market"] = self._clean_numeric(cleaned_market["median_days_on_market"])
        
        # Add timestamp
        cleaned_market["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return cleaned_market
    
    def merge_property_data(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge property data from different sources based on address.
        
        Args:
            properties: List of property data dictionaries
            
        Returns:
            Merged property data
        """
        self.logger.info(f"Merging {len(properties)} properties")
        
        # Create a DataFrame from the properties
        df = pd.DataFrame(properties)
        
        # If there's no address column, we can't merge
        if "address" not in df.columns:
            self.logger.warning("No address column found, cannot merge properties")
            return properties
        
        # Standardize addresses for better matching
        df["standardized_address"] = df["address"].apply(self._standardize_address)
        
        # Group by standardized address
        grouped = df.groupby("standardized_address")
        
        # Merge properties with the same standardized address
        merged_properties = []
        
        for address, group in grouped:
            if len(group) == 1:
                # Only one property with this address, no need to merge
                merged_properties.append(group.iloc[0].to_dict())
            else:
                # Multiple properties with this address, merge them
                merged_property = {}
                
                # Iterate through all columns
                for column in group.columns:
                    if column == "standardized_address":
                        continue
                    
                    # Get unique non-null values for this column
                    values = group[column].dropna().unique()
                    
                    if len(values) == 0:
                        # No non-null values
                        merged_property[column] = None
                    elif len(values) == 1:
                        # Only one unique value
                        merged_property[column] = values[0]
                    else:
                        # Multiple unique values, use the one from the most recent source
                        # Assuming the most recent source is the one with the latest timestamp
                        if "timestamp" in group.columns and "source" in group.columns:
                            latest_source = group.loc[group["timestamp"].idxmax(), "source"]
                            latest_value = group.loc[group["source"] == latest_source, column].iloc[0]
                            merged_property[column] = latest_value
                        else:
                            # No timestamp or source column, use the first value
                            merged_property[column] = values[0]
                
                merged_properties.append(merged_property)
        
        self.logger.info(f"Merged into {len(merged_properties)} properties")
        return merged_properties
    
    def calculate_derived_metrics(self, properties: List[Dict[str, Any]], 
                                 market_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Calculate derived metrics for properties.
        
        Args:
            properties: List of property data dictionaries
            market_data: Optional market data dictionary
            
        Returns:
            Properties with derived metrics
        """
        self.logger.info(f"Calculating derived metrics for {len(properties)} properties")
        
        properties_with_metrics = []
        
        for property_data in properties:
            # Create a copy of the property data
            property_with_metrics = property_data.copy()
            
            # Calculate price per square foot
            if "price" in property_with_metrics and "square_footage" in property_with_metrics:
                price = property_with_metrics["price"]
                square_footage = property_with_metrics["square_footage"]
                
                if price is not None and square_footage is not None and square_footage > 0:
                    property_with_metrics["price_per_sqft"] = round(price / square_footage, 2)
            
            # Calculate cap rate if we have price and rent
            if "price" in property_with_metrics and "monthly_rent" in property_with_metrics:
                price = property_with_metrics["price"]
                monthly_rent = property_with_metrics["monthly_rent"]
                
                if price is not None and monthly_rent is not None and price > 0:
                    # Assume 50% expense ratio for a rough estimate
                    annual_rent = monthly_rent * 12
                    net_operating_income = annual_rent * 0.5
                    property_with_metrics["cap_rate"] = round((net_operating_income / price) * 100, 2)
            
            # Calculate price-to-rent ratio if we have price and rent
            if "price" in property_with_metrics and "monthly_rent" in property_with_metrics:
                price = property_with_metrics["price"]
                monthly_rent = property_with_metrics["monthly_rent"]
                
                if price is not None and monthly_rent is not None and monthly_rent > 0:
                    property_with_metrics["price_to_rent_ratio"] = round(price / (monthly_rent * 12), 2)
            
            # Compare to market averages if we have market data
            if market_data is not None:
                # Compare price to median listing price
                if "price" in property_with_metrics and "median_listing_price" in market_data:
                    price = property_with_metrics["price"]
                    median_price = market_data["median_listing_price"]
                    
                    if price is not None and median_price is not None and median_price > 0:
                        property_with_metrics["price_to_median_ratio"] = round(price / median_price, 2)
                
                # Compare price per square foot to median
                if "price_per_sqft" in property_with_metrics and "median_price_per_sqft" in market_data:
                    price_per_sqft = property_with_metrics["price_per_sqft"]
                    median_price_per_sqft = market_data["median_price_per_sqft"]
                    
                    if price_per_sqft is not None and median_price_per_sqft is not None and median_price_per_sqft > 0:
                        property_with_metrics["price_per_sqft_to_median_ratio"] = round(price_per_sqft / median_price_per_sqft, 2)
            
            properties_with_metrics.append(property_with_metrics)
        
        return properties_with_metrics
    
    def convert_to_airtable_format(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert property data to Airtable format.
        
        Args:
            properties: List of property data dictionaries
            
        Returns:
            Property data in Airtable format
        """
        self.logger.info(f"Converting {len(properties)} properties to Airtable format")
        
        airtable_properties = []
        
        for property_data in properties:
            # Create a new dictionary for Airtable
            airtable_property = {
                "Region": property_data.get("city", "") or property_data.get("location", ""),
                "Property Value": property_data.get("price", 0),
                "Monthly Rent": property_data.get("monthly_rent", 0),
                "Cap Rate": property_data.get("cap_rate", 0),
                "PTR Ratio": property_data.get("price_to_rent_ratio", 0),
                "Risk Level": self._calculate_risk_level(property_data),
                "Market Phase": self._calculate_market_phase(property_data),
                "Avg Appreciation": property_data.get("appreciation_rate", 0),
                "Address": property_data.get("address", ""),
                "Bedrooms": property_data.get("bedrooms", 0),
                "Bathrooms": property_data.get("bathrooms", 0),
                "Square Footage": property_data.get("square_footage", 0),
                "Year Built": property_data.get("year_built", 0),
                "Property Type": property_data.get("property_type", ""),
                "URL": property_data.get("url", ""),
                "Source": property_data.get("source", "")
            }
            
            # Add to airtable properties
            airtable_properties.append(airtable_property)
        
        return airtable_properties
    
    def _clean_price(self, price: Any) -> Optional[float]:
        """Clean and convert price to a float.
        
        Args:
            price: Price value to clean
            
        Returns:
            Cleaned price as a float or None if invalid
        """
        if price is None:
            return None
        
        # Convert to string
        price_str = str(price)
        
        # Remove non-numeric characters except decimal point
        price_str = re.sub(r'[^\d.]', '', price_str)
        
        # Convert to float
        try:
            return float(price_str)
        except ValueError:
            return None
    
    def _clean_numeric(self, value: Any) -> Optional[float]:
        """Clean and convert a numeric value to a float.
        
        Args:
            value: Numeric value to clean
            
        Returns:
            Cleaned value as a float or None if invalid
        """
        if value is None:
            return None
        
        # Convert to string
        value_str = str(value)
        
        # Remove non-numeric characters except decimal point
        value_str = re.sub(r'[^\d.]', '', value_str)
        
        # Convert to float
        try:
            return float(value_str)
        except ValueError:
            return None
    
    def _standardize_address(self, address: str) -> str:
        """Standardize an address for better matching.
        
        Args:
            address: Address to standardize
            
        Returns:
            Standardized address
        """
        if not address:
            return ""
        
        # Convert to lowercase
        address = address.lower()
        
        # Remove common address prefixes and suffixes
        address = re.sub(r'\b(street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|place|pl|court|ct|way|circle|cir|terrace|ter|highway|hwy)\b', '', address)
        
        # Remove apartment/unit numbers
        address = re.sub(r'\b(apt|unit|suite|ste|#)\s*[\w-]+', '', address)
        
        # Remove punctuation and extra whitespace
        address = re.sub(r'[^\w\s]', '', address)
        address = re.sub(r'\s+', ' ', address).strip()
        
        return address
    
    def _calculate_risk_level(self, property_data: Dict[str, Any]) -> str:
        """Calculate risk level for a property.
        
        Args:
            property_data: Property data dictionary
            
        Returns:
            Risk level (Low, Moderate, High, Very High)
        """
        # This is a simplified risk calculation
        # In a real implementation, this would be more sophisticated
        
        risk_score = 0
        
        # Price-to-rent ratio factor
        ptr_ratio = property_data.get("price_to_rent_ratio", 0)
        if ptr_ratio > 0:
            if ptr_ratio < 15:
                risk_score += 0
            elif ptr_ratio < 20:
                risk_score += 1
            elif ptr_ratio < 25:
                risk_score += 2
            else:
                risk_score += 3
        
        # Cap rate factor
        cap_rate = property_data.get("cap_rate", 0)
        if cap_rate > 0:
            if cap_rate > 8:
                risk_score += 0
            elif cap_rate > 6:
                risk_score += 1
            elif cap_rate > 4:
                risk_score += 2
            else:
                risk_score += 3
        
        # Property age factor
        year_built = property_data.get("year_built", 0)
        if year_built > 0:
            age = datetime.now().year - year_built
            if age < 10:
                risk_score += 0
            elif age < 30:
                risk_score += 1
            elif age < 50:
                risk_score += 2
            else:
                risk_score += 3
        
        # Determine risk level based on score
        if risk_score <= 2:
            return "Low"
        elif risk_score <= 4:
            return "Moderate"
        elif risk_score <= 6:
            return "High"
        else:
            return "Very High"
    
    def _calculate_market_phase(self, property_data: Dict[str, Any]) -> str:
        """Calculate market phase for a property.
        
        Args:
            property_data: Property data dictionary
            
        Returns:
            Market phase (Growth, Peak, Decline, Recovery)
        """
        # This is a simplified market phase calculation
        # In a real implementation, this would be more sophisticated
        
        # Check if we have appreciation rate
        appreciation_rate = property_data.get("appreciation_rate", None)
        if appreciation_rate is not None:
            if appreciation_rate > 10:
                return "Growth"
            elif appreciation_rate > 5:
                return "Peak"
            elif appreciation_rate > 0:
                return "Recovery"
            else:
                return "Decline"
        
        # Check if we have days on market trend
        days_on_market_trend = property_data.get("days_on_market_trend", None)
        if days_on_market_trend is not None:
            if days_on_market_trend < -10:
                return "Growth"
            elif days_on_market_trend < 0:
                return "Peak"
            elif days_on_market_trend < 10:
                return "Decline"
            else:
                return "Recovery"
        
        # Default to "Unknown" if we don't have enough data
        return "Unknown"
