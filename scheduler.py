import schedule
import time
from datetime import datetime, timedelta
import logging
import os
from real_estate_data_api import RealEstateDataAPI
from dotenv import load_dotenv
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from real_estate_controller import RealEstateController
from firebase_manager import FirebaseManager
from config.config import UPDATE_SCHEDULE, THRESHOLDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollectionScheduler:
    def __init__(self):
        """Initialize the Data Collection Scheduler"""
        load_dotenv()
        self.api = RealEstateDataAPI()
        self.setup_folders()
        self.load_target_zipcodes()
        
    def setup_folders(self):
        """Create necessary folders"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/market_stats', exist_ok=True)
        os.makedirs('data/property_data', exist_ok=True)
        os.makedirs('data/owner_data', exist_ok=True)
        
    def load_target_zipcodes(self):
        """Load or create target ZIP codes file"""
        self.zipcode_file = 'data/target_zipcodes.json'
        if os.path.exists(self.zipcode_file):
            with open(self.zipcode_file, 'r') as f:
                self.zipcodes = json.load(f)
        else:
            # Default to Nashville area ZIP codes
            self.zipcodes = {
                'primary': ['37218', '37208', '37207', '37206'],
                'secondary': ['37209', '37211', '37214', '37217']
            }
            self.save_target_zipcodes()
            
    def save_target_zipcodes(self):
        """Save target ZIP codes"""
        with open(self.zipcode_file, 'w') as f:
            json.dump(self.zipcodes, f, indent=2)
            
    def collect_market_data(self):
        """Collect market statistics for all target areas"""
        logger.info("Starting market data collection")
        for zipcode in self.zipcodes['primary'] + self.zipcodes['secondary']:
            try:
                stats = self.api.get_market_stats(zipcode)
                logger.info(f"Collected market stats for {zipcode}")
            except Exception as e:
                logger.error(f"Error collecting market stats for {zipcode}: {str(e)}")
                
    def collect_distressed_properties(self):
        """Collect distressed property data"""
        logger.info("Starting distressed property collection")
        for zipcode in self.zipcodes['primary']:
            try:
                properties = self.api.get_distressed_properties(zipcode)
                logger.info(f"Collected distressed properties for {zipcode}")
            except Exception as e:
                logger.error(f"Error collecting distressed properties for {zipcode}: {str(e)}")
                
    def bulk_property_search(self):
        """Perform bulk property search in target areas"""
        logger.info("Starting bulk property search")
        max_price = int(os.getenv('MAX_PRICE', 400000))
        property_type = os.getenv('DEFAULT_PROPERTY_TYPE', 'SFR')
        
        for zipcode in self.zipcodes['primary']:
            try:
                results = self.api.bulk_property_search(
                    zipcode=zipcode,
                    property_type=property_type,
                    max_price=max_price
                )
                logger.info(f"Completed bulk search for {zipcode}")
            except Exception as e:
                logger.error(f"Error in bulk search for {zipcode}: {str(e)}")
                
    def run_daily_collection(self):
        """Run daily data collection tasks"""
        logger.info("Starting daily data collection")
        
        try:
            # Collect market data first
            self.collect_market_data()
            
            # Then look for distressed properties
            self.collect_distressed_properties()
            
            # Finally do bulk property search
            self.bulk_property_search()
            
            logger.info("Daily collection completed successfully")
        except Exception as e:
            logger.error(f"Error in daily collection: {str(e)}")
            
    def run_hourly_collection(self):
        """Run hourly data collection tasks"""
        logger.info("Starting hourly data collection")
        
        try:
            # Focus on primary ZIP codes for more frequent updates
            for zipcode in self.zipcodes['primary']:
                stats = self.api.get_market_stats(zipcode)
                logger.info(f"Updated market stats for {zipcode}")
        except Exception as e:
            logger.error(f"Error in hourly collection: {str(e)}")

class DataUpdateScheduler:
    """Manages scheduled data updates and caching"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.controller = RealEstateController()
        self.firebase = FirebaseManager()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self._setup_schedules()
    
    def _setup_schedules(self):
        """Set up all scheduled tasks"""
        # Update high-demand areas daily
        self.scheduler.add_job(
            self._update_high_demand_areas,
            CronTrigger(hour=1),  # Run at 1 AM
            name='high_demand_update'
        )
        
        # Update market stats weekly
        self.scheduler.add_job(
            self._update_market_stats,
            CronTrigger(day_of_week='mon', hour=2),  # Run Mondays at 2 AM
            name='market_stats_update'
        )
        
        # Clean expired cache daily
        self.scheduler.add_job(
            self._clean_expired_cache,
            CronTrigger(hour=3),  # Run at 3 AM
            name='cache_cleanup'
        )
        
        # Track API usage hourly
        self.scheduler.add_job(
            self._track_api_usage,
            'interval',
            hours=1,
            name='api_usage_tracking'
        )
    
    async def _update_high_demand_areas(self):
        """Update data for high-demand ZIP codes"""
        try:
            hot_zips = self.firebase.get_high_demand_zips(10)
            for zip_code in hot_zips:
                # Check search frequency
                metrics = self._get_zip_metrics(zip_code)
                if metrics['weekly_searches'] >= THRESHOLDS['high_demand_area']:
                    await self._update_zip_data(zip_code)
                    
        except Exception as e:
            logging.error(f"Error updating high-demand areas: {e}")
    
    async def _update_market_stats(self):
        """Update market statistics for all tracked areas"""
        try:
            active_zips = self._get_active_zip_codes()
            for zip_code in active_zips:
                request = {
                    'type': 'market_analysis',
                    'zip_code': zip_code
                }
                await self.controller.handle_property_query(request)
                
        except Exception as e:
            logging.error(f"Error updating market stats: {e}")
    
    def _clean_expired_cache(self):
        """Remove expired cache entries"""
        try:
            # Get configuration
            cache_duration = timedelta(days=UPDATE_SCHEDULE['property_details'] // 24)
            cutoff = datetime.now() - cache_duration
            
            # Clean different data types
            self._clean_expired_properties(cutoff)
            self._clean_expired_market_data(cutoff)
            self._clean_expired_queries(cutoff)
            
        except Exception as e:
            logging.error(f"Error cleaning cache: {e}")
    
    def _track_api_usage(self):
        """Track and analyze API usage patterns"""
        try:
            usage_stats = {
                'property_details': self._count_api_calls('property_details'),
                'market_analysis': self._count_api_calls('market_analysis'),
                'owner_info': self._count_api_calls('owner_info'),
                'total_cost': self._calculate_api_costs()
            }
            
            self.firebase.update_api_stats(usage_stats)
            
            # Alert if approaching limits
            self._check_usage_limits(usage_stats)
            
        except Exception as e:
            logging.error(f"Error tracking API usage: {e}")
    
    async def _update_zip_data(self, zip_code: str):
        """Update all data for a specific ZIP code"""
        requests = [
            {'type': 'property_analysis', 'zip_code': zip_code},
            {'type': 'market_trends', 'zip_code': zip_code},
            {'type': 'distressed_property', 'zip_code': zip_code}
        ]
        
        for request in requests:
            try:
                await self.controller.handle_property_query(request)
            except Exception as e:
                logging.error(f"Error updating {request['type']} for {zip_code}: {e}")
    
    def _get_zip_metrics(self, zip_code: str) -> Dict:
        """Get usage metrics for a ZIP code"""
        return {
            'daily_searches': self._count_daily_searches(zip_code),
            'weekly_searches': self._count_weekly_searches(zip_code),
            'last_update': self._get_last_update(zip_code)
        }
    
    def _get_active_zip_codes(self) -> List[str]:
        """Get list of actively monitored ZIP codes"""
        week_ago = datetime.now() - timedelta(days=7)
        active = self.firebase.db.collection('search_metrics').where(
            'last_search', '>', week_ago
        ).stream()
        return [doc.id for doc in active]
    
    def _clean_expired_properties(self, cutoff: datetime):
        """Clean expired property data"""
        expired = self.firebase.db.collection('properties').where(
            'last_updated', '<', cutoff
        ).stream()
        
        batch = self.firebase.db.batch()
        for doc in expired:
            batch.delete(doc.reference)
        batch.commit()
    
    def _clean_expired_market_data(self, cutoff: datetime):
        """Clean expired market analysis data"""
        expired = self.firebase.db.collection('market_data').where(
            'timestamp', '<', cutoff
        ).stream()
        
        batch = self.firebase.db.batch()
        for doc in expired:
            batch.delete(doc.reference)
        batch.commit()
    
    def _clean_expired_queries(self, cutoff: datetime):
        """Clean expired query cache"""
        expired = self.firebase.db.collection('query_cache').where(
            'timestamp', '<', cutoff
        ).stream()
        
        batch = self.firebase.db.batch()
        for doc in expired:
            batch.delete(doc.reference)
        batch.commit()
    
    def _count_api_calls(self, endpoint_type: str) -> int:
        """Count API calls for a specific endpoint"""
        today = datetime.now().strftime('%Y-%m-%d')
        doc = self.firebase.db.collection('api_usage').document(today).get()
        
        if not doc.exists:
            return 0
            
        data = doc.to_dict()
        return data.get(endpoint_type, 0)
    
    def _calculate_api_costs(self) -> float:
        """Calculate current API usage costs"""
        usage = self._get_current_usage()
        
        cost = 0.0
        # Add base subscription cost
        cost += 250  # Basic tier
        
        # Add overage costs
        if usage['reports'] > 400:
            cost += (usage['reports'] - 400) * 0.63
        if usage['csv'] > 400:
            cost += (usage['csv'] - 400) * 0.15
            
        return cost
    
    def _check_usage_limits(self, usage_stats: Dict):
        """Check if approaching usage limits"""
        if usage_stats['property_details'] > 350:  # 87.5% of limit
            logging.warning("Approaching property details API limit")
        if usage_stats['total_cost'] > 400:  # $400 threshold
            logging.warning("Approaching monthly API cost threshold")
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logging.info("Data update scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logging.info("Data update scheduler stopped")

def main():
    """Main scheduler function"""
    data_collection_scheduler = DataCollectionScheduler()
    data_update_scheduler = DataUpdateScheduler()
    
    # Schedule data collection
    schedule.every().day.at("00:00").do(data_collection_scheduler.run_daily_collection)
    schedule.every(4).hours.do(data_collection_scheduler.run_hourly_collection)
    
    # Run initial collection immediately
    data_collection_scheduler.run_daily_collection()
    
    logger.info("Scheduler started successfully")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
    
    data_update_scheduler.start()

if __name__ == "__main__":
    main()
