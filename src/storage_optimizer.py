"""Storage Optimizer for ATTOM Data"""
from typing import Dict, List, Set
import pandas as pd
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StorageOptimizer:
    """Optimizes data storage based on usage patterns and importance"""
    
    def __init__(self):
        self.essential_data_types = {
            'property_basic': {
                'fields': {'market_value', 'beds', 'baths', 'sqft', 'assessed_value'},
                'solution': 'Property Details',
                'priority': 1
            },
            'ownership': {
                'fields': {'owner_name', 'occupancy_status', 'mailing_address'},
                'solution': 'Owner Info',
                'priority': 1
            },
            'distressed': {
                'fields': {'foreclosure_status', 'tax_status', 'liens'},
                'solution': 'Foreclosure',
                'priority': 1
            }
        }
        
        self.optional_data_types = {
            'property_advanced': {
                'fields': {'construction_type', 'roof_type', 'foundation_type'},
                'solution': 'Building Characteristics',
                'priority': 3
            },
            'market_detailed': {
                'fields': {'price_history', 'market_trends', 'comparable_sales'},
                'solution': 'Market Analysis',
                'priority': 2
            },
            'neighborhood': {
                'fields': {'school_ratings', 'crime_stats', 'demographics'},
                'solution': 'Area Info',
                'priority': 3
            }
        }
        
        self.usage_stats = {}
        self.storage_limits = {
            'max_properties': 1000,
            'max_days_stored': 90,
            'max_file_size_mb': 100
        }
    
    def analyze_data_requirements(self, query_history: List[Dict]) -> Set[str]:
        """Analyze query patterns to determine required ATTOM solutions"""
        required_solutions = set()
        
        # Count query types
        query_counts = {}
        for query in query_history:
            query_type = query.get('type', '')
            query_counts[query_type] = query_counts.get(query_type, 0) + 1
        
        # Add essential solutions
        for data_type in self.essential_data_types.values():
            required_solutions.add(data_type['solution'])
        
        # Add frequently used optional solutions
        total_queries = sum(query_counts.values())
        for query_type, count in query_counts.items():
            usage_ratio = count / total_queries
            if usage_ratio > 0.2:  # If used in more than 20% of queries
                if query_type in self.optional_data_types:
                    required_solutions.add(self.optional_data_types[query_type]['solution'])
        
        return required_solutions
    
    def optimize_storage(self, data_dir: str):
        """Optimize data storage based on usage and limits"""
        for file_name in os.listdir(data_dir):
            if not file_name.endswith('.xlsx'):
                continue
                
            file_path = os.path.join(data_dir, file_name)
            df = pd.read_excel(file_path)
            
            # Remove old data
            df['last_updated'] = pd.to_datetime(df['last_updated'])
            cutoff_date = datetime.now() - timedelta(days=self.storage_limits['max_days_stored'])
            df = df[df['last_updated'] > cutoff_date]
            
            # Keep only most recent properties if exceeding limit
            if len(df) > self.storage_limits['max_properties']:
                df = df.sort_values('last_updated', ascending=False)
                df = df.head(self.storage_limits['max_properties'])
            
            # Save optimized data
            df.to_excel(file_path, index=False)
    
    def get_storage_recommendations(self) -> Dict:
        """Get recommendations for data storage optimization"""
        return {
            "essential_solutions": [
                {
                    "name": "Property Details",
                    "purpose": "Core property information needed for all analyses",
                    "storage_impact": "Low - Basic fields only",
                    "update_frequency": "30 days"
                },
                {
                    "name": "Owner Info",
                    "purpose": "Essential for lead generation and contact",
                    "storage_impact": "Low - Contact details only",
                    "update_frequency": "90 days"
                },
                {
                    "name": "Foreclosure",
                    "purpose": "Critical for distressed property identification",
                    "storage_impact": "Low - Status fields only",
                    "update_frequency": "7 days"
                }
            ],
            "recommended_optional": [
                {
                    "name": "Market Analysis",
                    "purpose": "Valuable for pricing and trends",
                    "storage_impact": "Medium - Store aggregated data only",
                    "update_frequency": "14 days"
                }
            ],
            "storage_guidelines": {
                "max_properties": self.storage_limits['max_properties'],
                "retention_period": self.storage_limits['max_days_stored'],
                "file_size_limit_mb": self.storage_limits['max_file_size_mb']
            }
        }
    
    def track_query_usage(self, query_type: str, fields_accessed: List[str]):
        """Track usage patterns of different data types"""
        timestamp = datetime.now()
        if query_type not in self.usage_stats:
            self.usage_stats[query_type] = []
        
        self.usage_stats[query_type].append({
            'timestamp': timestamp,
            'fields': fields_accessed
        })
    
    def get_usage_analysis(self) -> Dict:
        """Analyze data usage patterns"""
        analysis = {}
        
        for query_type, stats in self.usage_stats.items():
            total_queries = len(stats)
            field_usage = {}
            
            for stat in stats:
                for field in stat['fields']:
                    field_usage[field] = field_usage.get(field, 0) + 1
            
            analysis[query_type] = {
                'total_queries': total_queries,
                'field_usage': {
                    field: count/total_queries 
                    for field, count in field_usage.items()
                }
            }
        
        return analysis
