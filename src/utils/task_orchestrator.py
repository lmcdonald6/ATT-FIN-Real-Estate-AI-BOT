"""
Task orchestrator for managing independent process execution.
Handles task queuing, scheduling, and execution with proper error handling.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Optional, Union
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class TaskResult:
    """Container for task execution results"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0

class Task:
    """Represents a task to be executed"""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        timeout: Optional[float] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.retries = 0
        self.max_retries = 3

class TaskOrchestrator:
    """Manages task execution and scheduling"""
    
    def __init__(self, max_workers: int = None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.lock = asyncio.Lock()
        self.event_loop = asyncio.get_event_loop()
        
    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution"""
        async with self.lock:
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda x: x.priority.value, reverse=True)
            logger.info(f"Task {task.name} ({task.id}) submitted with priority {task.priority}")
            return task.id
            
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a single task"""
        start_time = datetime.now()
        task.started_at = start_time
        task.status = TaskStatus.RUNNING
        
        try:
            if task.timeout:
                result = await asyncio.wait_for(
                    self.event_loop.run_in_executor(
                        self.executor,
                        task.func,
                        *task.args,
                        **task.kwargs
                    ),
                    timeout=task.timeout
                )
            else:
                result = await self.event_loop.run_in_executor(
                    self.executor,
                    task.func,
                    *task.args,
                    **task.kwargs
                )
                
            execution_time = (datetime.now() - start_time).total_seconds()
            return TaskResult(True, result=result, execution_time=execution_time)
            
        except asyncio.TimeoutError:
            logger.error(f"Task {task.name} ({task.id}) timed out after {task.timeout} seconds")
            return TaskResult(False, error=TimeoutError(f"Task timed out after {task.timeout} seconds"))
            
        except Exception as e:
            logger.error(f"Task {task.name} ({task.id}) failed: {str(e)}")
            return TaskResult(False, error=e)
            
    async def process_tasks(self):
        """Process tasks from the queue"""
        while True:
            if not self.task_queue:
                await asyncio.sleep(0.1)
                continue
                
            async with self.lock:
                task = self.task_queue.pop(0)
                self.running_tasks[task.id] = task
                
            try:
                result = await self.execute_task(task)
                task.completed_at = datetime.now()
                
                if result.success:
                    task.status = TaskStatus.COMPLETED
                    task.result = result.result
                else:
                    if task.retries < task.max_retries:
                        task.retries += 1
                        task.status = TaskStatus.PENDING
                        await self.submit_task(task)
                        logger.warning(f"Task {task.name} ({task.id}) failed, retrying ({task.retries}/{task.max_retries})")
                        continue
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = result.error
                        
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = e
                logger.error(f"Error processing task {task.name} ({task.id}): {str(e)}")
                
            finally:
                del self.running_tasks[task.id]
                self.completed_tasks[task.id] = task
                
    async def start(self):
        """Start the task orchestrator"""
        logger.info("Starting task orchestrator")
        await self.process_tasks()
        
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get the current status of a task"""
        task = (
            self.running_tasks.get(task_id) or
            self.completed_tasks.get(task_id)
        )
        
        if not task:
            return None
            
        return {
            'id': task.id,
            'name': task.name,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'result': task.result if task.status == TaskStatus.COMPLETED else None,
            'error': str(task.error) if task.error else None,
            'retries': task.retries
        }
        
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        async with self.lock:
            # Check pending tasks
            for i, task in enumerate(self.task_queue):
                if task.id == task_id:
                    task.status = TaskStatus.CANCELLED
                    self.completed_tasks[task_id] = task
                    del self.task_queue[i]
                    logger.info(f"Task {task.name} ({task_id}) cancelled")
                    return True
                    
            # Check running tasks
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                self.completed_tasks[task_id] = task
                del self.running_tasks[task_id]
                logger.info(f"Task {task.name} ({task_id}) cancelled")
                return True
                
        return False
        
    def clear_completed_tasks(self, age_hours: int = 24):
        """Clear completed tasks older than specified hours"""
        current_time = datetime.now()
        to_remove = []
        
        for task_id, task in self.completed_tasks.items():
            if task.completed_at:
                age = (current_time - task.completed_at).total_seconds() / 3600
                if age > age_hours:
                    to_remove.append(task_id)
                    
        for task_id in to_remove:
            del self.completed_tasks[task_id]
            
        logger.info(f"Cleared {len(to_remove)} completed tasks older than {age_hours} hours")
