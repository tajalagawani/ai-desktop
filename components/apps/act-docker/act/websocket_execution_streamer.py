"""
WebSocket Execution Streamer for ACT Workflows
Provides real-time streaming of workflow execution progress via WebSocket
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)

class WebSocketExecutionStreamer:
    """
    Streams workflow execution progress via WebSocket in real-time.
    Integrates with ExecutionManager's status callback system.
    """
    
    def __init__(self, websocket):
        self.websocket = websocket
        self.execution_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.node_start_times: Dict[str, datetime] = {}
        self.execution_manager = None
        
    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send a structured message via WebSocket"""
        message = {
            "type": message_type,
            "execution_id": self.execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        try:
            await self.websocket.send(json.dumps(message, default=str))
            logger.debug(f"Sent WebSocket message: {message_type}")
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
    
    def _send_message_sync(self, message_type: str, data: Dict[str, Any]):
        """Synchronous message sender for eventlet compatibility"""
        message = {
            "type": message_type,
            "execution_id": self.execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        try:
            # For eventlet/socketio compatibility
            if hasattr(self.websocket, 'send'):
                self.websocket.send(json.dumps(message, default=str))
            else:
                logger.debug(f"Cannot send message - websocket has no send method")
        except Exception as e:
            logger.error(f"Failed to send sync WebSocket message: {e}")
    
    def status_callback(self, node_name: str, status: str, message: str, all_statuses: Dict[str, Any]):
        """Callback function for ExecutionManager status updates"""
        
        # Track node execution times
        if status == "running":
            self.node_start_times[node_name] = datetime.now()
        
        execution_time = 0.0
        if node_name in self.node_start_times and status in ["success", "error", "warning"]:
            execution_time = (datetime.now() - self.node_start_times[node_name]).total_seconds()
        
        # Get node result if available
        node_result = None
        if self.execution_manager and hasattr(self.execution_manager, 'node_results'):
            node_result = self.execution_manager.node_results.get(node_name)
        
        # Prepare data for WebSocket
        data = {
            "node_name": node_name,
            "status": status,
            "message": message,
            "execution_time": execution_time,
            "result": node_result
        }
        
        # Send async (need to handle in event loop) 
        try:
            # Try to create task in current loop
            asyncio.create_task(self.send_message("node_status", data))
        except RuntimeError:
            # If no event loop, schedule for later (for eventlet compatibility)
            import eventlet
            eventlet.spawn(self._send_message_sync, "node_status", data)
    
    async def execute_workflow_from_file(self, actfile_path: str, initial_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a complete workflow from an Actfile with WebSocket streaming"""
        
        try:
            # Import here to avoid circular imports
            from .execution_manager import ExecutionManager
            
            self.execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self.start_time = datetime.now()
            
            await self.send_message("execution_start", {
                "actfile_path": actfile_path,
                "initial_input": initial_input,
                "execution_mode": "workflow"
            })
            
            # Create execution manager
            self.execution_manager = ExecutionManager(
                actfile_path=actfile_path,
                resolution_debug_mode=False,
                fail_on_unresolved=False
            )
            
            # Register our callback for status updates
            self.execution_manager.register_status_callback(self.status_callback)
            
            # Execute workflow
            result = self.execution_manager.execute_workflow(
                execution_id=self.execution_id,
                initial_input=initial_input or {}
            )
            
            # Calculate total execution time
            total_time = (datetime.now() - self.start_time).total_seconds()
            
            await self.send_message("execution_complete", {
                "result": result,
                "total_execution_time": total_time,
                "nodes_executed": len(self.execution_manager.node_results),
                "final_status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error during workflow execution: {e}", exc_info=True)
            await self.send_message("error", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "execution_phase": "workflow_execution"
            })
            return {"status": "error", "message": str(e)}
    
    async def execute_workflow_from_content(self, actfile_content: str, initial_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute workflow from Actfile content string with WebSocket streaming"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.actfile', delete=False) as temp_file:
            temp_file.write(actfile_content)
            temp_file_path = temp_file.name
        
        try:
            result = await self.execute_workflow_from_file(temp_file_path, initial_input)
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    async def execute_single_node(self, node_config: Dict[str, Any], initial_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a single node with WebSocket streaming"""
        
        try:
            from .execution_manager import ExecutionManager
            
            self.execution_id = f"node_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self.start_time = datetime.now()
            
            await self.send_message("execution_start", {
                "node_config": node_config,
                "initial_input": initial_input,
                "execution_mode": "single_node"
            })
            
            # Create a minimal workflow with just this node
            node_name = node_config.get('name', 'SingleNode')
            node_type = node_config.get('type', 'unknown')
            
            # Create temporary Actfile content
            actfile_content = f"""
[workflow]
name = "Single Node Execution"
start_node = {node_name}

[node:{node_name}]
type = {node_type}
"""
            
            # Add all node parameters
            for key, value in node_config.items():
                if key not in ['name', 'type']:
                    if isinstance(value, str):
                        actfile_content += f"{key} = {value}\n"
                    else:
                        actfile_content += f"{key} = {json.dumps(value, default=str)}\n"
            
            # Execute the single-node workflow
            result = await self.execute_workflow_from_content(actfile_content, initial_input)
            
            return result
            
        except Exception as e:
            logger.error(f"Error during single node execution: {e}", exc_info=True)
            await self.send_message("error", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "execution_phase": "single_node_execution"
            })
            return {"status": "error", "message": str(e)}

class ExecutionModeDetector:
    """Detects whether an Actfile is for server mode or execution mode"""
    
    @staticmethod
    def detect_mode(actfile_path: str) -> str:
        """
        Detect execution mode from Actfile
        Returns: 'server' if has agent config, 'execution' otherwise
        """
        try:
            from .execution_manager import ExecutionManager
            
            em = ExecutionManager(actfile_path)
            
            if em.has_agent_config():
                return "server"
            else:
                return "execution"
                
        except Exception as e:
            logger.error(f"Error detecting execution mode: {e}")
            return "execution"  # Default to execution mode
    
    @staticmethod
    def detect_mode_from_content(actfile_content: str) -> str:
        """Detect execution mode from Actfile content string"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.actfile', delete=False) as temp_file:
            temp_file.write(actfile_content)
            temp_file_path = temp_file.name
        
        try:
            return ExecutionModeDetector.detect_mode(temp_file_path)
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

# Helper function for creating execution streamers
async def create_execution_streamer(websocket) -> WebSocketExecutionStreamer:
    """Factory function to create a WebSocket execution streamer"""
    return WebSocketExecutionStreamer(websocket)