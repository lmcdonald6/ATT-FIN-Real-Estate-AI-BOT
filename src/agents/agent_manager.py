"""
Agent Manager for coordinating multiple specialized AI agents.
Handles agent communication, task delegation, and resource management.
"""
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Set, Type
import uuid

from src.utils.task_orchestrator import TaskOrchestrator, Task, TaskPriority
from src.services.service_manager import ServiceManager

logger = logging.getLogger(__name__)

@dataclass
class AgentCapability:
    """Represents a specific capability of an agent"""
    name: str
    description: str
    required_resources: Set[str]
    priority: int = 1

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.capabilities: List[AgentCapability] = []
        self.is_busy = False
        self.current_task: Optional[str] = None
        self.last_active = datetime.now()
        
    @abstractmethod
    async def process_task(self, task_data: Dict) -> Dict:
        """Process a task assigned to this agent"""
        pass
        
    @abstractmethod
    def can_handle_task(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        pass
        
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of agent capabilities"""
        return self.capabilities.copy()

class PropertyAnalysisAgent(BaseAgent):
    """Agent specialized in property analysis"""
    
    def __init__(self, agent_id: str, service_manager: ServiceManager):
        super().__init__(agent_id)
        self.service_manager = service_manager
        self.capabilities = [
            AgentCapability(
                name="market_analysis",
                description="Analyze property market conditions and investment potential",
                required_resources={"market_data", "property_data"},
                priority=2
            ),
            AgentCapability(
                name="comp_analysis",
                description="Analyze comparable properties and pricing trends",
                required_resources={"property_data"},
                priority=1
            )
        ]
        
    async def process_task(self, task_data: Dict) -> Dict:
        self.is_busy = True
        self.current_task = task_data.get('task_id')
        
        try:
            if task_data['type'] == 'market_analysis':
                task_id = await self.service_manager.analyze_property(
                    task_data['property_id'],
                    task_data.get('sources')
                )
                return {'task_id': task_id, 'status': 'processing'}
                
            elif task_data['type'] == 'comp_analysis':
                # Handle comp analysis specific logic
                pass
                
        finally:
            self.is_busy = False
            self.current_task = None
            self.last_active = datetime.now()
            
    def can_handle_task(self, task_type: str) -> bool:
        return task_type in {'market_analysis', 'comp_analysis'}

class DataIntegrationAgent(BaseAgent):
    """Agent specialized in data integration and validation"""
    
    def __init__(self, agent_id: str, service_manager: ServiceManager):
        super().__init__(agent_id)
        self.service_manager = service_manager
        self.capabilities = [
            AgentCapability(
                name="data_fetch",
                description="Fetch property data from multiple sources",
                required_resources={"api_access"},
                priority=2
            ),
            AgentCapability(
                name="data_validation",
                description="Validate and clean property data",
                required_resources={"validation_rules"},
                priority=1
            )
        ]
        
    async def process_task(self, task_data: Dict) -> Dict:
        self.is_busy = True
        self.current_task = task_data.get('task_id')
        
        try:
            if task_data['type'] == 'data_fetch':
                property_data = await self.service_manager.services['data_integration'].get_property_data(
                    task_data['property_id'],
                    task_data.get('sources')
                )
                return {'status': 'completed', 'data': property_data}
                
            elif task_data['type'] == 'data_validation':
                # Handle data validation specific logic
                pass
                
        finally:
            self.is_busy = False
            self.current_task = None
            self.last_active = datetime.now()
            
    def can_handle_task(self, task_type: str) -> bool:
        return task_type in {'data_fetch', 'data_validation'}

class AgentManager:
    """Manages multiple specialized agents and coordinates their activities"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.task_orchestrator = TaskOrchestrator()
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_tasks: Dict[str, List[str]] = {}
        self.lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize the agent manager and its components"""
        await self.service_manager.initialize()
        asyncio.create_task(self.task_orchestrator.start())
        
        # Create specialized agents
        self.register_agent(PropertyAnalysisAgent(str(uuid.uuid4()), self.service_manager))
        self.register_agent(DataIntegrationAgent(str(uuid.uuid4()), self.service_manager))
        
        logger.info("Agent manager initialized")
        
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
        self.agent_tasks[agent.agent_id] = []
        logger.info(f"Agent {agent.agent_id} registered with capabilities: {[c.name for c in agent.capabilities]}")
        
    async def submit_task(self, task_type: str, task_data: Dict) -> str:
        """Submit a task for processing by appropriate agent"""
        task_id = str(uuid.uuid4())
        task_data['task_id'] = task_id
        
        # Find suitable agent
        agent = await self._find_suitable_agent(task_type)
        if not agent:
            raise ValueError(f"No available agent found for task type: {task_type}")
            
        async def _execute_agent_task():
            try:
                result = await agent.process_task(task_data)
                return result
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {str(e)}")
                raise
                
        task = Task(
            name=f"{task_type}_{task_id}",
            func=_execute_agent_task,
            priority=TaskPriority.HIGH
        )
        
        await self.task_orchestrator.submit_task(task)
        self.agent_tasks[agent.agent_id].append(task_id)
        
        return task_id
        
    async def _find_suitable_agent(self, task_type: str) -> Optional[BaseAgent]:
        """Find an available agent that can handle the task"""
        async with self.lock:
            for agent in self.agents.values():
                if not agent.is_busy and agent.can_handle_task(task_type):
                    return agent
        return None
        
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get the status of a task"""
        return self.task_orchestrator.get_task_status(task_id)
        
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get the status of an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
            
        return {
            'agent_id': agent.agent_id,
            'is_busy': agent.is_busy,
            'current_task': agent.current_task,
            'last_active': agent.last_active.isoformat(),
            'capabilities': [c.name for c in agent.capabilities]
        }
        
    async def cleanup(self):
        """Cleanup resources"""
        await self.service_manager.cleanup()
        self.task_orchestrator.clear_completed_tasks()
        logger.info("Agent manager cleanup completed")
