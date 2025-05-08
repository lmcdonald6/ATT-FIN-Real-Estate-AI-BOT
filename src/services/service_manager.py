"""
Service manager for handling independent service execution and lifecycle.
"""
import asyncio
from datetime import datetime
import logging
from typing import Dict, List, Optional, Type

from src.utils.task_orchestrator import TaskOrchestrator, Task, TaskPriority
from src.services.data_integration import DataIntegrationService
from src.analysis.market_analyzer import MarketAnalyzer

logger = logging.getLogger(__name__)

class ServiceManager:
    """Manages service lifecycle and execution"""
    
    def __init__(self):
        self.task_orchestrator = TaskOrchestrator()
        self.services: Dict[str, object] = {}
        self.service_status: Dict[str, bool] = {}
        
    async def initialize(self):
        """Initialize all services"""
        logger.info("Initializing service manager")
        
        # Initialize task orchestrator
        asyncio.create_task(self.task_orchestrator.start())
        
        # Initialize core services
        self.services['data_integration'] = DataIntegrationService()
        self.services['market_analyzer'] = MarketAnalyzer()
        
        # Mark all services as active
        for service_name in self.services:
            self.service_status[service_name] = True
            
    async def analyze_property(self, property_id: str, sources: Optional[List[str]] = None) -> str:
        """
        Analyze a property using both data integration and market analysis
        Returns a task ID that can be used to track progress
        """
        async def _analyze():
            # Fetch property data
            data_service = self.services['data_integration']
            property_data = await data_service.get_property_data(property_id, sources)
            
            if not property_data:
                raise ValueError(f"No data found for property {property_id}")
                
            # Get comparable properties
            comps = await data_service.get_comparable_properties(
                property_data,
                max_comps=15,
                max_distance_miles=5
            )
            
            # Perform market analysis
            analyzer = self.services['market_analyzer']
            analysis = analyzer.analyze_property(property_data, comps)
            
            return {
                'property_data': property_data,
                'market_analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        task = Task(
            name=f"analyze_property_{property_id}",
            func=_analyze,
            priority=TaskPriority.HIGH
        )
        
        return await self.task_orchestrator.submit_task(task)
        
    async def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Get the result of a task"""
        return self.task_orchestrator.get_task_status(task_id)
        
    def get_service_status(self) -> Dict[str, bool]:
        """Get the status of all services"""
        return self.service_status.copy()
        
    async def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.services:
            return False
            
        self.service_status[service_name] = False
        logger.info(f"Service {service_name} stopped")
        return True
        
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            return False
            
        self.service_status[service_name] = True
        logger.info(f"Service {service_name} started")
        return True
        
    async def cleanup(self):
        """Cleanup resources"""
        # Clear old completed tasks
        self.task_orchestrator.clear_completed_tasks()
        
        # Stop all services
        for service_name in self.services:
            await self.stop_service(service_name)
            
        logger.info("Service manager cleanup completed")
