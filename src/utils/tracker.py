from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

class UsageTracker:
    """Track API usage and costs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tracking_data = {}
        self.api_costs = {
            'property_details': 0.05,
            'owner_info': 0.03,
            'market_data': 0.04,
            'foreclosure': 0.06,
            'liens': 0.04,
            'tax': 0.03
        }
        self._init_tracking_file()
    
    def _init_tracking_file(self):
        """Initialize tracking file"""
        self.tracking_file = Path(__file__).parent.parent.parent / 'data' / 'usage_tracking.xlsx'
        self.tracking_file.parent.mkdir(exist_ok=True)
        
        if not self.tracking_file.exists():
            self._create_tracking_structure()
    
    def _create_tracking_structure(self):
        """Create tracking file structure"""
        sheets = {
            'api_usage': [
                'timestamp', 'endpoint', 'address', 'success',
                'response_time', 'cost', 'data_source'
            ],
            'daily_summary': [
                'date', 'total_requests', 'success_rate',
                'total_cost', 'avg_response_time'
            ],
            'endpoint_stats': [
                'endpoint', 'total_calls', 'success_rate',
                'avg_cost', 'avg_response_time'
            ]
        }
        
        with pd.ExcelWriter(self.tracking_file) as writer:
            for sheet, columns in sheets.items():
                pd.DataFrame(columns=columns).to_excel(
                    writer, sheet_name=sheet, index=False
                )
    
    def start_tracking(self, address: str) -> None:
        """Start tracking API usage for an address"""
        self.tracking_data[address] = {
            'start_time': datetime.now(),
            'endpoints': [],
            'success': True,
            'total_cost': 0
        }
    
    def track_api_call(self, address: str, endpoint: str, 
                      success: bool, data_source: str) -> None:
        """Track individual API call"""
        if address not in self.tracking_data:
            self.start_tracking(address)
        
        tracking = self.tracking_data[address]
        end_time = datetime.now()
        response_time = (end_time - tracking['start_time']).total_seconds()
        cost = self.api_costs.get(endpoint, 0)
        
        if not success:
            tracking['success'] = False
        
        tracking['total_cost'] += cost
        tracking['endpoints'].append({
            'endpoint': endpoint,
            'success': success,
            'response_time': response_time,
            'cost': cost,
            'data_source': data_source
        })
        
        # Store in Excel
        self._store_api_call(
            timestamp=end_time,
            endpoint=endpoint,
            address=address,
            success=success,
            response_time=response_time,
            cost=cost,
            data_source=data_source
        )
    
    def complete_tracking(self, address: str, success: bool) -> None:
        """Complete tracking for an address"""
        if address in self.tracking_data:
            tracking = self.tracking_data[address]
            tracking['end_time'] = datetime.now()
            tracking['success'] &= success
            
            # Update daily summary
            self._update_daily_summary()
            # Update endpoint statistics
            self._update_endpoint_stats()
            
            del self.tracking_data[address]
    
    def _store_api_call(self, timestamp: datetime, endpoint: str,
                       address: str, success: bool, response_time: float,
                       cost: float, data_source: str) -> None:
        """Store API call in tracking file"""
        try:
            df = pd.DataFrame([{
                'timestamp': timestamp,
                'endpoint': endpoint,
                'address': address,
                'success': success,
                'response_time': response_time,
                'cost': cost,
                'data_source': data_source
            }])
            
            with pd.ExcelWriter(
                self.tracking_file, mode='a', if_sheet_exists='overlay'
            ) as writer:
                df.to_excel(
                    writer, sheet_name='api_usage',
                    header=False, index=False
                )
        except Exception as e:
            self.logger.error(f"Error storing API call: {str(e)}")
    
    def _update_daily_summary(self) -> None:
        """Update daily usage summary"""
        try:
            today = datetime.now().date()
            
            # Read existing data
            df = pd.read_excel(self.tracking_file, sheet_name='api_usage')
            
            # Filter today's data
            today_data = df[df['timestamp'].dt.date == today]
            
            summary = {
                'date': today,
                'total_requests': len(today_data),
                'success_rate': today_data['success'].mean() * 100,
                'total_cost': today_data['cost'].sum(),
                'avg_response_time': today_data['response_time'].mean()
            }
            
            # Update summary sheet
            summary_df = pd.DataFrame([summary])
            with pd.ExcelWriter(
                self.tracking_file, mode='a', if_sheet_exists='overlay'
            ) as writer:
                summary_df.to_excel(
                    writer, sheet_name='daily_summary',
                    header=False, index=False
                )
        except Exception as e:
            self.logger.error(f"Error updating daily summary: {str(e)}")
    
    def _update_endpoint_stats(self) -> None:
        """Update endpoint statistics"""
        try:
            # Read existing data
            df = pd.read_excel(self.tracking_file, sheet_name='api_usage')
            
            # Group by endpoint
            endpoint_stats = df.groupby('endpoint').agg({
                'endpoint': 'count',
                'success': 'mean',
                'cost': 'mean',
                'response_time': 'mean'
            }).rename(columns={
                'endpoint': 'total_calls',
                'success': 'success_rate',
                'cost': 'avg_cost',
                'response_time': 'avg_response_time'
            }).reset_index()
            
            # Update stats sheet
            with pd.ExcelWriter(
                self.tracking_file, mode='a', if_sheet_exists='replace'
            ) as writer:
                endpoint_stats.to_excel(
                    writer, sheet_name='endpoint_stats',
                    index=False
                )
        except Exception as e:
            self.logger.error(f"Error updating endpoint stats: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        try:
            # Read data
            usage_df = pd.read_excel(self.tracking_file, sheet_name='api_usage')
            daily_df = pd.read_excel(self.tracking_file, sheet_name='daily_summary')
            endpoint_df = pd.read_excel(self.tracking_file, sheet_name='endpoint_stats')
            
            # Calculate time periods
            now = datetime.now()
            today = now.date()
            month_start = today.replace(day=1)
            
            # Daily stats
            today_data = usage_df[usage_df['timestamp'].dt.date == today]
            daily_stats = {
                'requests': len(today_data),
                'success_rate': f"{today_data['success'].mean()*100:.1f}%",
                'cost': f"${today_data['cost'].sum():.2f}"
            }
            
            # Monthly stats
            month_data = usage_df[usage_df['timestamp'].dt.date >= month_start]
            monthly_stats = {
                'requests': len(month_data),
                'success_rate': f"{month_data['success'].mean()*100:.1f}%",
                'cost': f"${month_data['cost'].sum():.2f}"
            }
            
            # Endpoint stats
            endpoint_stats = endpoint_df.to_dict('records')
            
            # Cost optimization
            cost_saved = self._calculate_cost_savings(usage_df)
            
            return {
                'daily': daily_stats,
                'monthly': monthly_stats,
                'endpoints': endpoint_stats,
                'cost_optimization': {
                    'total_saved': f"${cost_saved:.2f}",
                    'optimization_rate': f"{(cost_saved / (cost_saved + usage_df['cost'].sum()))*100:.1f}%"
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {str(e)}")
            return {}
    
    def _calculate_cost_savings(self, df: pd.DataFrame) -> float:
        """Calculate cost savings from data prioritization"""
        try:
            # Calculate potential cost if all data came from paid APIs
            potential_cost = sum(
                len(df[df['endpoint'] == endpoint]) * cost
                for endpoint, cost in self.api_costs.items()
            )
            
            # Actual cost
            actual_cost = df['cost'].sum()
            
            return potential_cost - actual_cost
        except Exception as e:
            self.logger.error(f"Error calculating cost savings: {str(e)}")
            return 0.0
    
    def get_usage_alerts(self) -> List[Dict]:
        """Get usage alerts and recommendations"""
        alerts = []
        
        try:
            # Read data
            df = pd.read_excel(self.tracking_file, sheet_name='api_usage')
            daily_df = pd.read_excel(self.tracking_file, sheet_name='daily_summary')
            
            # Check for high costs
            today_cost = df[
                df['timestamp'].dt.date == datetime.now().date()
            ]['cost'].sum()
            
            if today_cost > 50:  # $50 daily threshold
                alerts.append({
                    'level': 'warning',
                    'message': f"High daily API cost: ${today_cost:.2f}",
                    'recommendation': "Consider implementing more aggressive caching"
                })
            
            # Check for low success rates
            success_rate = df['success'].mean() * 100
            if success_rate < 90:  # 90% success threshold
                alerts.append({
                    'level': 'warning',
                    'message': f"Low API success rate: {success_rate:.1f}%",
                    'recommendation': "Review error patterns and adjust retry logic"
                })
            
            # Check for response time issues
            avg_response = df['response_time'].mean()
            if avg_response > 2:  # 2 second threshold
                alerts.append({
                    'level': 'info',
                    'message': f"High average response time: {avg_response:.1f}s",
                    'recommendation': "Consider implementing response time optimization"
                })
            
            # Check for cost optimization opportunities
            redfin_usage = len(df[df['data_source'] == 'redfin'])
            attom_usage = len(df[df['data_source'] == 'attom'])
            
            if attom_usage > redfin_usage:
                alerts.append({
                    'level': 'info',
                    'message': "High paid API usage ratio",
                    'recommendation': "Increase usage of free data sources"
                })
            
        except Exception as e:
            self.logger.error(f"Error getting usage alerts: {str(e)}")
            alerts.append({
                'level': 'error',
                'message': f"Error analyzing usage patterns: {str(e)}",
                'recommendation': "Check tracking file integrity"
            })
        
        return alerts
