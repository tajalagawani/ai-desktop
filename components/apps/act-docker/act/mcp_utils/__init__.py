"""
ACT MCP Utilities

Integration layer for Model Context Protocol (MCP) tools.
Provides signature management, catalog syncing, and execution utilities.

Usage:
    from act.mcp_utils import SignatureManager, sync_catalog, execute_single_node
    from act.mcp_utils import execute_flow, list_node_operations

Author: ACT Team
License: MIT
"""

from .signature_manager import SignatureManager
from .catalog_sync import sync_catalog, get_node_info, list_all_nodes, parse_node_file
from .single_node_executor import SingleNodeExecutor, execute_single_node
from .execute_flow import execute_flow
from .list_operations import (
    list_node_operations,
    list_all_operations,
    search_operations,
    get_operation_details
)
from .logger import MCPLogger, get_logger, LogLevel

__all__ = [
    # Signature management
    'SignatureManager',

    # Catalog syncing
    'sync_catalog',
    'get_node_info',
    'list_all_nodes',
    'parse_node_file',

    # Execution
    'SingleNodeExecutor',
    'execute_single_node',
    'execute_flow',

    # Operations listing
    'list_node_operations',
    'list_all_operations',
    'search_operations',
    'get_operation_details',

    # Logging
    'MCPLogger',
    'get_logger',
    'LogLevel'
]

__version__ = '1.0.0'
