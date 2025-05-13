"""Scheduler Module

This module provides a scheduler for running data scraping tasks periodically.
"""

import os
import time
import logging
import threading
import schedule
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scheduler')

class TaskScheduler:
    """Scheduler for data scraping tasks."""
    
    def __init__(self):
        """Initialize the task scheduler."""
        self.logger = logging.getLogger('scheduler')
        self.running = False
        self.scheduler_thread = None
        self.tasks = {}
    
    def add_task(self, name: str, task: Callable, schedule_type: str, interval: int, 
               args: Optional[List] = None, kwargs: Optional[Dict[str, Any]] = None):
        """Add a task to the scheduler.
        
        Args:
            name: Name of the task
            task: Function to run
            schedule_type: Type of schedule (daily, hourly, minutes)
            interval: Interval for the schedule
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task
        """
        self.logger.info(f"Adding task {name} to run {schedule_type} every {interval} interval")
        
        # Create a wrapper function that includes the arguments
        def task_wrapper():
            self.logger.info(f"Running task {name}")
            try:
                if args and kwargs:
                    task(*args, **kwargs)
                elif args:
                    task(*args)
                elif kwargs:
                    task(**kwargs)
                else:
                    task()
                self.logger.info(f"Task {name} completed successfully")
            except Exception as e:
                self.logger.error(f"Error running task {name}: {str(e)}")
        
        # Schedule the task based on the schedule type
        if schedule_type == "daily":
            job = schedule.every(interval).days.do(task_wrapper)
        elif schedule_type == "hourly":
            job = schedule.every(interval).hours.do(task_wrapper)
        elif schedule_type == "minutes":
            job = schedule.every(interval).minutes.do(task_wrapper)
        else:
            self.logger.error(f"Invalid schedule type: {schedule_type}")
            return
        
        # Store the task in the tasks dictionary
        self.tasks[name] = {
            "job": job,
            "schedule_type": schedule_type,
            "interval": interval,
            "last_run": None,
            "next_run": job.next_run
        }
        
        self.logger.info(f"Task {name} scheduled to run next at {job.next_run}")
    
    def remove_task(self, name: str):
        """Remove a task from the scheduler.
        
        Args:
            name: Name of the task to remove
        """
        if name in self.tasks:
            self.logger.info(f"Removing task {name} from scheduler")
            schedule.cancel_job(self.tasks[name]["job"])
            del self.tasks[name]
        else:
            self.logger.warning(f"Task {name} not found in scheduler")
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.logger.info("Starting scheduler")
        self.running = True
        
        # Create a thread for the scheduler
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.logger.info("Stopping scheduler")
        self.running = False
        
        # Wait for the scheduler thread to finish
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            self.scheduler_thread = None
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        self.logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Run pending tasks
                schedule.run_pending()
                
                # Update task information
                for name, task in self.tasks.items():
                    if task["job"].last_run:
                        self.tasks[name]["last_run"] = task["job"].last_run
                    self.tasks[name]["next_run"] = task["job"].next_run
                
                # Sleep for a short time
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(5)  # Sleep longer on error
        
        self.logger.info("Scheduler loop stopped")
    
    def get_task_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task.
        
        Args:
            name: Name of the task
            
        Returns:
            Task status dictionary or None if task not found
        """
        if name in self.tasks:
            task = self.tasks[name]
            return {
                "name": name,
                "schedule_type": task["schedule_type"],
                "interval": task["interval"],
                "last_run": task["last_run"],
                "next_run": task["next_run"]
            }
        else:
            self.logger.warning(f"Task {name} not found in scheduler")
            return None
    
    def get_all_task_status(self) -> List[Dict[str, Any]]:
        """Get the status of all tasks.
        
        Returns:
            List of task status dictionaries
        """
        return [self.get_task_status(name) for name in self.tasks.keys()]
