from typing import List, Dict, Optional, Any
import pandas as pd
import logging
import json
import os
import importlib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/ai_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIAutomationController:
    def __init__(self):
        """Initialize the AI Automation Controller"""
        self.setup_folders()
        self.active_tasks = {}
        self.available_tools = self._discover_tools()
        
    def setup_folders(self):
        """Create necessary folders"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/sessions', exist_ok=True)
        os.makedirs('tools', exist_ok=True)
        
    def _discover_tools(self) -> Dict[str, Any]:
        """Discover available automation tools"""
        tools = {}
        tools_dir = 'tools'
        
        if not os.path.exists(tools_dir):
            return tools
            
        for file in os.listdir(tools_dir):
            if file.endswith('.py') and not file.startswith('__'):
                tool_name = file[:-3]  # Remove .py extension
                try:
                    module = importlib.import_module(f'tools.{tool_name}')
                    if hasattr(module, 'get_tool_info'):
                        tools[tool_name] = {
                            'module': module,
                            'info': module.get_tool_info()
                        }
                        logger.info(f"Loaded tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Error loading tool {tool_name}: {str(e)}")
                    
        return tools
        
    def start_session(self, session_name: str, tool_name: str) -> str:
        """Start a new automation session"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
            
        session_id = f"{tool_name}_{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_tasks[session_id] = {
            'id': session_id,
            'name': session_name,
            'tool': tool_name,
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        self._save_session(session_id)
        logger.info(f"Started {tool_name} session: {session_name}")
        return session_id
        
    def stop_session(self, session_id: str) -> Dict:
        """Stop an active automation session"""
        if session_id not in self.active_tasks:
            raise ValueError(f"Session '{session_id}' not found")
            
        session = self.active_tasks[session_id]
        tool_name = session['tool']
        
        if tool_name in self.available_tools:
            try:
                tool = self.available_tools[tool_name]['module']
                if hasattr(tool, 'stop'):
                    tool.stop()
            except Exception as e:
                logger.error(f"Error stopping {tool_name}: {str(e)}")
                
        session['end_time'] = datetime.now().isoformat()
        session['status'] = 'completed'
        self._save_session(session_id)
        
        session_summary = session.copy()
        del self.active_tasks[session_id]
        
        logger.info(f"Stopped session: {session_id}")
        return session_summary
        
    def run_tool(self, tool_name: str, session_name: str, **kwargs) -> Dict:
        """Run a specific automation tool"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
            
        session_id = self.start_session(session_name, tool_name)
        
        try:
            tool = self.available_tools[tool_name]['module']
            if not hasattr(tool, 'run'):
                raise ValueError(f"Tool '{tool_name}' does not have a run method")
                
            results = tool.run(**kwargs)
            
            # Save results if they exist
            if results and isinstance(results, (list, dict)):
                self._save_results(results, session_id)
                
            session_summary = self.stop_session(session_id)
            
            return {
                'success': True,
                'results': results,
                'session': session_summary
            }
            
        except Exception as e:
            logger.error(f"Error running {tool_name}: {str(e)}")
            if session_id in self.active_tasks:
                self.stop_session(session_id)
            return {
                'success': False,
                'error': str(e)
            }
            
    def get_session_results(self, session_id: str) -> Optional[Dict]:
        """Get results from a specific session"""
        try:
            session_file = f"data/sessions/{session_id}.json"
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None
            
    def list_available_tools(self) -> Dict[str, Dict]:
        """List all available automation tools"""
        return {name: info['info'] for name, info in self.available_tools.items()}
        
    def _save_session(self, session_id: str):
        """Save session data"""
        if session_id in self.active_tasks:
            session_file = f"data/sessions/{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(self.active_tasks[session_id], f)
                
    def _save_results(self, results: Any, session_id: str):
        """Save tool results"""
        try:
            if isinstance(results, list):
                df = pd.DataFrame(results)
                output_file = f"data/results_{session_id}.csv"
                df.to_csv(output_file, index=False)
                logger.info(f"Saved results to {output_file}")
            elif isinstance(results, dict):
                output_file = f"data/results_{session_id}.json"
                with open(output_file, 'w') as f:
                    json.dump(results, f)
                logger.info(f"Saved results to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

# Example usage
if __name__ == "__main__":
    controller = AIAutomationController()
    
    # List available tools
    tools = controller.list_available_tools()
    print("Available automation tools:")
    for name, info in tools.items():
        print(f"- {name}: {info['description']}")
        
    # Example: Run Redfin scraper
    try:
        results = controller.run_tool(
            tool_name='redfin_scraper',
            session_name='Multi_State_Search',
            zip_codes=['90210', '10001', '60601']  # Beverly Hills, Manhattan, Chicago
        )
        
        if results['success']:
            print(f"Search completed successfully!")
            print(f"Session ID: {results['session']['id']}")
            print(f"Found {len(results['results'])} properties")
        else:
            print(f"Search failed: {results['error']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
