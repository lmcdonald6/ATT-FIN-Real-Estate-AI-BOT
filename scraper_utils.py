import os
import json
from datetime import datetime, timedelta

class ScraperScheduler:
    def __init__(self, schedule_file='scraper_schedule.json'):
        self.schedule_file = schedule_file
        self.schedule = self._load_schedule()

    def _load_schedule(self):
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_schedule(self):
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f)

    def can_run(self, scraper_name):
        """Check if a scraper can run based on its last run time"""
        if scraper_name not in self.schedule:
            return True
        
        last_run = datetime.fromisoformat(self.schedule[scraper_name])
        next_run = last_run + timedelta(hours=24)
        return datetime.now() >= next_run

    def update_last_run(self, scraper_name):
        """Update the last run time for a scraper"""
        self.schedule[scraper_name] = datetime.now().isoformat()
        self._save_schedule()

    def get_wait_time(self, scraper_name):
        """Get hours and minutes until next allowed run"""
        if scraper_name not in self.schedule:
            return "Ready to run now"
        
        last_run = datetime.fromisoformat(self.schedule[scraper_name])
        next_run = last_run + timedelta(hours=24)
        wait_time = next_run - datetime.now()
        
        if wait_time.total_seconds() <= 0:
            return "Ready to run now"
        
        hours = int(wait_time.total_seconds() // 3600)
        minutes = int((wait_time.total_seconds() % 3600) // 60)
        return f"{hours} hours and {minutes} minutes"
