__version__ = '4.8.400'

# Main components for easy importing
from .execution_manager import ExecutionManager
from .actfile_parser import ActfileParser, ActfileParserError
from .node_context import NodeContext
from .workflow_engine import WorkflowEngine
from .agent_server import AgentServer

# Expose all main components
__all__ = [
    'ExecutionManager',
    'ActfileParser',
    'ActfileParserError',
    'NodeContext',
    'WorkflowEngine',
    'AgentServer',
]