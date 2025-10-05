#!/usr/bin/env python3
"""
MiniACT Executor - Workflow execution for flows without HTTP routes
Executes workflows from start node when no ACI routes are defined
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MiniACTExecutor:
    """
    Executes ACT workflows without HTTP routes.
    Used when flow file contains workflow logic but no ACI route definitions.
    """

    def __init__(self, execution_manager):
        self.execution_manager = execution_manager
        self.last_execution: Optional[Dict[str, Any]] = None
        self.execution_count = 0

    def execute_from_start(self, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute workflow from the start node.

        Args:
            initial_data: Optional initial data to pass to workflow

        Returns:
            Execution result dictionary
        """
        try:
            start_time = datetime.now()
            self.execution_count += 1

            logger.info(f"🚀 MiniACT Execution #{self.execution_count} starting...")

            # Execute the workflow
            result = self.execution_manager.execute_workflow(initial_input=initial_data)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            execution_info = {
                "execution_id": self.execution_count,
                "status": "success",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "result": result
            }

            self.last_execution = execution_info
            logger.info(f"✅ MiniACT Execution #{self.execution_count} completed in {duration:.2f}s")

            return execution_info

        except Exception as e:
            logger.error(f"❌ MiniACT Execution #{self.execution_count} failed: {e}", exc_info=True)

            execution_info = {
                "execution_id": self.execution_count,
                "status": "error",
                "start_time": start_time.isoformat() if 'start_time' in locals() else None,
                "error": str(e),
                "error_type": type(e).__name__
            }

            self.last_execution = execution_info
            return execution_info

    def execute_node(self, node_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a specific node manually.

        Args:
            node_id: The ID of the node to execute
            input_data: Input data for the node

        Returns:
            Node execution result
        """
        try:
            logger.info(f"🎯 Executing node: {node_id}")

            # Get the node executor
            if node_id not in self.execution_manager.node_executors:
                raise ValueError(f"Node not found: {node_id}")

            node_executor = self.execution_manager.node_executors[node_id]

            # Execute the node
            if asyncio.iscoroutinefunction(node_executor.execute):
                # Async execution
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(node_executor.execute(input_data or {}))
            else:
                # Sync execution
                result = node_executor.execute(input_data or {})

            logger.info(f"✅ Node {node_id} executed successfully")

            return {
                "status": "success",
                "node_id": node_id,
                "result": result
            }

        except Exception as e:
            logger.error(f"❌ Node {node_id} execution failed: {e}", exc_info=True)

            return {
                "status": "error",
                "node_id": node_id,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def get_status(self) -> Dict[str, Any]:
        """Get executor status"""
        return {
            "mode": "miniact",
            "execution_count": self.execution_count,
            "last_execution": self.last_execution,
            "available_nodes": list(self.execution_manager.node_executors.keys()) if hasattr(self.execution_manager, 'node_executors') else []
        }

    def auto_execute_on_load(self) -> bool:
        """
        Automatically execute workflow when flow is loaded (if configured).

        Returns:
            True if auto-execution is enabled
        """
        # Check if flow has auto_execute setting
        config = self.execution_manager.get_agent_config() if hasattr(self.execution_manager, 'get_agent_config') else {}
        auto_execute = config.get('auto_execute', False)

        if auto_execute:
            logger.info("⚡ Auto-execute enabled - running workflow on load")
            self.execute_from_start()
            return True

        logger.debug("Auto-execute disabled - workflow ready for manual execution")
        return False
