"""Usage and Cost Tracking for ATTOM API"""
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class UsageTracker:
    """Tracks API usage, costs, and data utilization"""
    
    def __init__(self):
        self.data_dir = "tracking"
        self.create_tracking_directory()
        
        # Define cost structure for ATTOM solutions
        self.solution_costs = {
            'property_details': {'cost_per_call': 0.05, 'daily_limit': 1000},
            'avm': {'cost_per_call': 0.10, 'daily_limit': 500},
            'foreclosure': {'cost_per_call': 0.15, 'daily_limit': 300},
            'market_trends': {'cost_per_call': 0.08, 'daily_limit': 200},
            'owner_info': {'cost_per_call': 0.12, 'daily_limit': 400}
        }
        
        # Initialize tracking files
        self.files = {
            'api_usage': 'api_usage.xlsx',
            'data_utilization': 'data_utilization.xlsx',
            'cost_analysis': 'cost_analysis.xlsx',
            'roi_metrics': 'roi_metrics.xlsx'
        }
    
    def create_tracking_directory(self):
        """Create tracking directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def track_api_call(self, solution_name: str, address: str, success: bool):
        """Track individual API call"""
        timestamp = datetime.now()
        
        df_data = {
            'timestamp': timestamp,
            'solution': solution_name,
            'address': address,
            'success': success,
            'cost': self.solution_costs.get(solution_name, {}).get('cost_per_call', 0)
        }
        
        self._update_excel('api_usage', df_data)
        self._update_daily_limits(solution_name)
    
    def track_data_usage(self, data_type: str, fields_accessed: List[str]):
        """Track how stored data is being used"""
        timestamp = datetime.now()
        
        df_data = {
            'timestamp': timestamp,
            'data_type': data_type,
            'fields_accessed': json.dumps(fields_accessed),
            'cache_hit': True  # Data was available in storage
        }
        
        self._update_excel('data_utilization', df_data)
    
    def analyze_costs(self, time_period: str = 'last_30_days') -> Dict:
        """Analyze API costs and usage patterns"""
        api_usage_path = os.path.join(self.data_dir, self.files['api_usage'])
        if not os.path.exists(api_usage_path):
            return {}
            
        df = pd.read_excel(api_usage_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by time period
        if time_period == 'last_30_days':
            cutoff_date = datetime.now() - timedelta(days=30)
            df = df[df['timestamp'] > cutoff_date]
        
        # Calculate costs by solution
        cost_analysis = df.groupby('solution').agg({
            'cost': 'sum',
            'success': 'count'
        }).reset_index()
        
        # Calculate success rate
        cost_analysis['success_rate'] = df.groupby('solution')['success'].mean()
        
        # Calculate cost per successful call
        cost_analysis['cost_per_success'] = cost_analysis['cost'] / (cost_analysis['success'] * cost_analysis['success_rate'])
        
        return cost_analysis.to_dict('records')
    
    def calculate_roi_metrics(self) -> Dict:
        """Calculate ROI metrics for data storage vs API calls"""
        api_usage_path = os.path.join(self.data_dir, self.files['api_usage'])
        data_util_path = os.path.join(self.data_dir, self.files['data_utilization'])
        
        if not (os.path.exists(api_usage_path) and os.path.exists(data_util_path)):
            return {}
            
        api_df = pd.read_excel(api_usage_path)
        util_df = pd.read_excel(data_util_path)
        
        # Calculate savings from cache hits
        total_cache_hits = len(util_df[util_df['cache_hit'] == True])
        total_api_calls = len(api_df)
        
        avg_api_cost = api_df['cost'].mean()
        estimated_savings = total_cache_hits * avg_api_cost
        
        return {
            'total_api_calls': total_api_calls,
            'total_cache_hits': total_cache_hits,
            'cache_hit_ratio': total_cache_hits / (total_api_calls + total_cache_hits),
            'estimated_savings': estimated_savings,
            'avg_api_cost': avg_api_cost
        }
    
    def get_usage_recommendations(self) -> Dict:
        """Get recommendations for optimizing API usage and costs"""
        cost_analysis = self.analyze_costs()
        roi_metrics = self.calculate_roi_metrics()
        
        recommendations = {
            'high_cost_solutions': [],
            'underutilized_solutions': [],
            'optimization_tips': []
        }
        
        # Analyze each solution's cost-effectiveness
        for solution in cost_analysis:
            if solution['cost_per_success'] > 0.15:  # High cost per successful call
                recommendations['high_cost_solutions'].append({
                    'solution': solution['solution'],
                    'current_cost': solution['cost'],
                    'suggestion': 'Consider increasing cache duration or reducing call frequency'
                })
            
            if solution['success_rate'] < 0.8:  # Low success rate
                recommendations['optimization_tips'].append({
                    'solution': solution['solution'],
                    'issue': 'Low success rate',
                    'suggestion': 'Review error patterns and improve error handling'
                })
        
        # Add caching recommendations
        if roi_metrics.get('cache_hit_ratio', 0) < 0.5:
            recommendations['optimization_tips'].append({
                'area': 'Caching Strategy',
                'issue': 'Low cache utilization',
                'suggestion': 'Increase cache duration for frequently accessed data'
            })
        
        return recommendations
    
    def _update_excel(self, tracking_type: str, new_data: Dict):
        """Update Excel tracking file"""
        file_path = os.path.join(self.data_dir, self.files[tracking_type])
        
        try:
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])
            
            df.to_excel(file_path, index=False)
            
        except Exception as e:
            logger.error(f"Error updating tracking file: {str(e)}")
    
    def _update_daily_limits(self, solution_name: str):
        """Check and update daily API limits"""
        api_usage_path = os.path.join(self.data_dir, self.files['api_usage'])
        if not os.path.exists(api_usage_path):
            return
            
        df = pd.read_excel(api_usage_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Check today's usage
        today = datetime.now().date()
        today_usage = len(df[
            (df['timestamp'].dt.date == today) & 
            (df['solution'] == solution_name)
        ])
        
        daily_limit = self.solution_costs.get(solution_name, {}).get('daily_limit', float('inf'))
        if today_usage >= daily_limit:
            logger.warning(f"Daily limit reached for {solution_name}")
            
    def generate_cost_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Generate detailed cost report"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        api_usage_path = os.path.join(self.data_dir, self.files['api_usage'])
        if not os.path.exists(api_usage_path):
            return {}
            
        df = pd.read_excel(api_usage_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by date range
        mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
        df = df[mask]
        
        # Calculate daily costs
        daily_costs = df.groupby(df['timestamp'].dt.date)['cost'].sum()
        
        # Calculate solution-specific metrics
        solution_metrics = df.groupby('solution').agg({
            'cost': 'sum',
            'success': ['count', 'mean']
        }).round(2)
        
        return {
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'total_cost': float(df['cost'].sum()),
            'total_calls': len(df),
            'daily_average_cost': float(daily_costs.mean()),
            'solution_breakdown': solution_metrics.to_dict(),
            'roi_metrics': self.calculate_roi_metrics()
        }
