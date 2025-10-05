import importlib
import traceback
import logging
import json
from typing import Callable, Dict, Any, List, Optional, Type, Tuple, Union, Set
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import re
import os
from pathlib import Path
import inspect
import sys
import copy
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

# Third-party libraries
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Warning: colorama not found. Colors will not be used in output.")
    class DummyStyle:
        def __getattr__(self, name): return ""
    Fore = DummyStyle()
    Style = DummyStyle()

try:
    from tabulate import tabulate
except ImportError:
    print("Warning: tabulate not found. Status tables will be basic.")
    def tabulate(table_data, headers, tablefmt, maxcolwidths=None):
        if not table_data: return "No data to display."
        col_count = len(headers)
        widths = [len(h) for h in headers]
        for row in table_data:
            for i, cell in enumerate(row):
                if i < col_count:
                    widths[i] = max(widths[i], len(str(cell)))
        if maxcolwidths:
            for i in range(min(len(widths), len(maxcolwidths))):
                if maxcolwidths[i] is not None and widths[i] > maxcolwidths[i]:
                    widths[i] = maxcolwidths[i]
        sep = "+".join("-" * (w + 2) for w in widths)
        header_line = "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers)) + "|"
        def format_cell_content(cell_content, display_width, col_idx):
            s_cell = str(cell_content)
            needs_truncation = (maxcolwidths and col_idx < len(maxcolwidths) and 
                              maxcolwidths[col_idx] is not None and len(s_cell) > display_width and 
                              display_width >= 3)
            if needs_truncation:
                return f" {s_cell[:display_width-3]}... "
            else:
                return f" {s_cell:<{display_width}} "
        data_lines = []
        for row in table_data:
            formatted_cells = []
            for i, cell in enumerate(row):
                if i < col_count:
                    formatted_cells.append(format_cell_content(cell, widths[i], i))
            data_lines.append("|" + "|".join(formatted_cells) + "|")
        return "\n".join([sep, header_line, sep] + data_lines + [sep])

# Custom Exception Definitions
class NodeExecutionError(Exception):
    """Custom exception for errors during node execution."""
    pass

class NodeValidationError(Exception):
    """Custom exception for errors during node validation or parameter issues."""
    pass

class PlaceholderResolutionError(Exception):
    """Custom exception for errors during placeholder resolution."""
    pass

class WorkflowValidationError(Exception):
    """Custom exception for workflow structure validation errors."""
    pass

class CircuitBreakerError(Exception):
    """Custom exception when circuit breaker is open."""
    pass

# Relative imports
try:
    from .actfile_parser import ActfileParser, ActfileParserError
    from .nodes.base_node import BaseNode
except ImportError as e:
    print(f"Warning: Relative import failed ({e}). Attempting direct imports...")
    try:
        from actfile_parser import ActfileParser, ActfileParserError
        from nodes.base_node import BaseNode
    except ImportError as e2:
        print(f"Warning: Direct import also failed ({e2}). Attempting absolute imports...")
        try:
            from act.actfile_parser import ActfileParser, ActfileParserError
            from act.nodes.base_node import BaseNode
        except ImportError as e3:
            print(f"Warning: All imports failed. Using dummy classes. Errors: {e}, {e2}, {e3}")
            class ActfileParserError(Exception): pass
            class ActfileParser:
                def __init__(self, path):
                    self.path = path
                    logging.warning("Using dummy ActfileParser.")
                def parse(self):
                    return {'workflow': {'start_node': None, 'name': 'DummyFlow'},
                            'nodes': {}, 'edges': {}, 'configuration': {}, 'deployment': {}}
                def get_start_node(self): return None
                def get_node_successors(self, node_name): return []
                def get_workflow_name(self): return "DummyFlow"
            class BaseNode:
                node_type: Optional[str] = None
                def set_execution_manager(self, manager): pass
                def set_sandbox_timeout(self, timeout): pass
                async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
                    return {"status": "success", "result": {}}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums
class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# Data Classes
@dataclass
class ExecutionMetrics:
    """Tracks execution metrics and performance data."""
    node_execution_times: Dict[str, float] = field(default_factory=dict)
    resolution_cache_hits: int = 0
    resolution_cache_misses: int = 0
    total_placeholders_resolved: int = 0
    retry_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    parallel_executions: int = 0
    checkpoint_saves: int = 0
    circuit_breaker_trips: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_execution_times': self.node_execution_times,
            'resolution_cache_hits': self.resolution_cache_hits,
            'resolution_cache_misses': self.resolution_cache_misses,
            'total_placeholders_resolved': self.total_placeholders_resolved,
            'retry_counts': dict(self.retry_counts),
            'parallel_executions': self.parallel_executions,
            'checkpoint_saves': self.checkpoint_saves,
            'circuit_breaker_trips': dict(self.circuit_breaker_trips),
            'avg_execution_time': sum(self.node_execution_times.values()) / len(self.node_execution_times) if self.node_execution_times else 0
        }

@dataclass
class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures."""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_attempts: int = 3
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0
    
    def record_success(self):
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_attempts:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.debug("Circuit breaker moved to half-open state")
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False

@dataclass
class ResourceLimits:
    """Resource constraints for workflow execution."""
    max_memory_mb: Optional[int] = None
    max_execution_time: Optional[int] = None
    max_concurrent_nodes: int = 10
    max_retries_per_node: int = 3
    max_resolution_depth: int = 10

# ExecutionManager Class
class ExecutionManager:
    """
    Advanced workflow execution manager with enterprise features:
    - Parallel execution
    - Retry logic with exponential backoff
    - Circuit breaker pattern
    - Checkpoint/resume capability
    - Performance metrics
    - Resource limits
    - Schema validation
    - Hot reload support
    """
    
    def __init__(self,
                 actfile_path: Union[str, Path] = 'Actfile',
                 sandbox_timeout: int = 600,
                 resolution_debug_mode: bool = False,
                 fail_on_unresolved: bool = False,
                 enable_parallel: bool = True,
                 enable_checkpoints: bool = False,
                 checkpoint_dir: Optional[Path] = None,
                 resource_limits: Optional[ResourceLimits] = None):
        """
        Initializes the ExecutionManager with advanced features.
        
        Args:
            actfile_path: Path to the Actfile definition.
            sandbox_timeout: Maximum execution time for the workflow in seconds.
            resolution_debug_mode: Enable detailed logging for placeholder resolution.
            fail_on_unresolved: If True, raise an error if any placeholder fails to resolve.
            enable_parallel: Enable parallel execution of independent nodes.
            enable_checkpoints: Enable checkpoint/resume capability.
            checkpoint_dir: Directory for storing checkpoints.
            resource_limits: Resource constraints for execution.
        """
        logger.debug(f"Initializing Advanced ExecutionManager with Actfile: {actfile_path}")
        
        # Core configuration
        self.actfile_path = Path(actfile_path)
        self.sandbox_timeout = sandbox_timeout
        self.resolution_debug_mode = resolution_debug_mode
        self.fail_on_unresolved = fail_on_unresolved
        self.enable_parallel = enable_parallel
        self.enable_checkpoints = enable_checkpoints
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else Path.cwd() / "checkpoints"
        self.resource_limits = resource_limits or ResourceLimits()
        
        if self.resolution_debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.debug("Placeholder resolution debug mode enabled.")
        
        # Execution state
        self.node_results: Dict[str, Any] = {}
        self.sandbox_start_time: Optional[datetime] = None
        self.node_loading_status: Dict[str, Dict[str, str]] = {}
        self.node_execution_status: Dict[str, Dict[str, Any]] = {}
        self.current_execution_id: Optional[str] = None
        self.status_callbacks: List[Callable] = []
        self.initial_input_data: Dict[str, Any] = {}
        self.executed_nodes: Set[str] = set()
        
        # Workflow data
        self.workflow_data: Dict[str, Any] = {}
        self.actfile_parser: Optional[ActfileParser] = None
        self.node_executors: Dict[str, Any] = {}
        
        # Placeholder resolution
        self.resolution_cache: Dict[str, Any] = {}
        self.resolved_values_by_key: Dict[str, Any] = {}
        
        # Agent server reference
        self.agent_server = None
        
        # Configuration
        self.configuration: Dict[str, Any] = {}
        self.deployment: Dict[str, Any] = {}
        
        # Advanced features
        self.metrics = ExecutionMetrics()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.breakpoints: Set[str] = set()
        self.dry_run_mode: bool = False
        
        # Thread pool for CPU-bound operations
        self.executor_pool = ThreadPoolExecutor(max_workers=self.resource_limits.max_concurrent_nodes)
        
        # Schema cache
        self.schema_cache: Dict[str, Dict] = {}
        
        # Load workflow
        try:
            self.load_workflow()
        except (FileNotFoundError, ActfileParserError) as e:
            logger.error(f"Failed to initialize ExecutionManager: {e}")
            raise
    
    # ==================== AGENT CONFIGURATION ====================
    
    def has_agent_config(self) -> bool:
        """Check if actfile has agent configuration."""
        return (hasattr(self, 'configuration') and 
                self.configuration.get('agent_enabled', False))
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration from the actfile."""
        return getattr(self, 'configuration', {})
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration from the actfile."""
        return getattr(self, 'deployment', {})
    
    # ==================== STATUS REPORTING ====================
    
    def register_status_callback(self, callback: Callable):
        """Registers a callback function to receive status updates during execution."""
        if callable(callback):
            self.status_callbacks.append(callback)
            logger.debug(f"Registered status callback: {getattr(callback, '__name__', 'anonymous')}")
        else:
            logger.warning("Attempted to register a non-callable status callback.")
    
    def update_node_status(self, node_name: str, status: str, message: str = ""):
        """Updates the status of a node and notifies all registered callbacks."""
        timestamp = datetime.now().isoformat()
        status_entry = {
            "status": status,
            "message": message,
            "timestamp": timestamp
        }
        self.node_execution_status[node_name] = status_entry
        
        log_level = logging.DEBUG if status in ["running", "pending"] else logging.INFO
        logger.log(log_level, f"Node '{node_name}' Status -> {status.upper()}: {message[:100] + ('...' if len(message)>100 else '')}")
        
        for callback in self.status_callbacks:
            try:
                callback(node_name, status, message, self.node_execution_status)
            except Exception as e:
                logger.error(f"Error in status callback '{getattr(callback, '__name__', 'anonymous')}': {e}", exc_info=True)
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Returns the current execution status including results and configuration."""
        wf_name = "N/A"
        if self.actfile_parser and hasattr(self.actfile_parser, 'get_workflow_name'):
            wf_name = self.actfile_parser.get_workflow_name() or "N/A"
        
        return {
            "execution_id": self.current_execution_id,
            "node_status": self.node_execution_status,
            "results": self.node_results,
            "initial_input": self.initial_input_data,
            "workflow_name": wf_name,
            "metrics": self.metrics.to_dict(),
            "executed_nodes": list(self.executed_nodes)
        }
    
    # ==================== WORKFLOW LOADING ====================
    
    def load_workflow(self):
        """Loads the workflow data using ActfileParser and loads node executors."""
        logger.debug(f"Loading workflow data from: {self.actfile_path}")
        
        if not self.actfile_path.exists():
            error_msg = f"Actfile not found at path: {self.actfile_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            self.actfile_parser = ActfileParser(self.actfile_path)
            self.workflow_data = self.actfile_parser.parse()
            logger.debug("Actfile parsed successfully.")
            
            self.configuration = self.workflow_data.get('configuration', {})
            self.deployment = self.workflow_data.get('deployment', {})
            logger.debug(f"Loaded configuration section: {self.log_safe_node_data(self.configuration)}")
            logger.debug(f"Loaded deployment section: {self.log_safe_node_data(self.deployment)}")
            
            if not self.workflow_data.get('nodes'):
                logger.warning("Actfile parsed but contains no 'nodes' section.")
            
            # Validate workflow structure
            self.validate_workflow_dag()
            
        except ActfileParserError as e:
            logger.error(f"Error parsing Actfile: {e}")
            self.workflow_data = {}
            self.configuration = {}
            self.deployment = {}
            self.actfile_parser = None
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Actfile parsing: {e}", exc_info=True)
            self.workflow_data = {}
            self.configuration = {}
            self.deployment = {}
            self.actfile_parser = None
            raise ActfileParserError(f"Unexpected error during parsing: {e}")
        
        if self.workflow_data:
            self.load_node_executors()
        else:
            logger.warning("Skipping node executor loading due to parsing failure.")
    
    def validate_workflow_dag(self):
        """Validates workflow structure and detects circular dependencies."""
        if not self.workflow_data or 'nodes' not in self.workflow_data:
            return
        
        logger.debug("Validating workflow DAG structure...")
        
        # Build adjacency list
        graph = defaultdict(list)
        nodes = set(self.workflow_data['nodes'].keys())
        
        for node_name in nodes:
            successors = self.actfile_parser.get_node_successors(node_name) if self.actfile_parser else []
            graph[node_name] = successors
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    logger.error(f"Circular dependency detected: {node} -> {neighbor}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in nodes:
            if node not in visited:
                if has_cycle(node):
                    raise WorkflowValidationError(f"Workflow contains circular dependencies involving node: {node}")
        
        logger.debug("Workflow DAG validation passed - no circular dependencies detected")
        
        # Validate start node exists
        start_node = self.actfile_parser.get_start_node() if self.actfile_parser else None
        if start_node and start_node not in nodes:
            raise WorkflowValidationError(f"Start node '{start_node}' not found in workflow nodes")
        
        # Check for orphaned nodes (unreachable from start)
        if start_node:
            reachable = set()
            stack = [start_node]
            
            while stack:
                current = stack.pop()
                if current in reachable:
                    continue
                reachable.add(current)
                stack.extend(graph.get(current, []))
            
            orphaned = nodes - reachable
            if orphaned:
                logger.debug(f"Orphaned nodes detected (unreachable from start): {orphaned}")
    
    def discover_node_classes(self) -> Dict[str, Type[BaseNode]]:
        """
        Discovers available BaseNode subclasses from the 'act.nodes' package.
        Returns a dictionary mapping node type strings to their class objects.
        """
        node_classes: Dict[str, Type[BaseNode]] = {}
        nodes_package_name = "act.nodes"
        
        try:
            nodes_module = importlib.import_module(nodes_package_name)
            package_path = getattr(nodes_module, '__path__', None)
            if not package_path:
                package_file = inspect.getfile(nodes_module)
                nodes_dir = Path(package_file).parent
            else:
                nodes_dir = Path(package_path[0])
            
            logger.debug(f"Scanning nodes directory: {nodes_dir}")
        except (ImportError, TypeError, AttributeError, FileNotFoundError) as e:
            logger.debug(f"Could not import or find nodes package '{nodes_package_name}': {e}", exc_info=False)
            logger.debug("Attempting fallback nodes directory lookup...")
            try:
                nodes_dir = Path(__file__).parent.parent / "nodes"
                if not nodes_dir.is_dir():
                    nodes_dir = Path(__file__).parent / "nodes"
                    if not nodes_dir.is_dir():
                        raise FileNotFoundError("Fallback directories also not found.")
                logger.debug(f"Falling back to scanning nodes directory: {nodes_dir}")
            except Exception as fallback_e:
                logger.error(f"Nodes directory could not be located: {fallback_e}. Node discovery aborted.")
                return {}
        
        # Node Registry
        registry_module_name = f"{nodes_package_name}.node_registry"
        try:
            registry_module = importlib.import_module(registry_module_name)
            registry = getattr(registry_module, 'NODES', None) or \
                      getattr(registry_module, 'NODE_REGISTRY', None) or \
                      getattr(registry_module, 'node_registry', None)
            if isinstance(registry, dict):
                logger.debug(f"Found node registry '{registry_module_name}' with {len(registry)} nodes")
                for node_type, node_class in registry.items():
                    if inspect.isclass(node_class) and issubclass(node_class, BaseNode):
                        if node_type not in node_classes:
                            node_classes[node_type] = node_class
                        else:
                            logger.warning(f"Node type '{node_type}' from registry conflicts with previous definition.")
                    else:
                        logger.warning(f"Invalid entry in registry for '{node_type}': {node_class}. Skipping.")
        except (ImportError, AttributeError) as e:
            logger.debug(f"Node registry {registry_module_name} not found or error loading: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading node registry {registry_module_name}: {e}", exc_info=True)
        
        # Dynamic Discovery from Files
        node_files: Dict[str, Path] = {}
        logger.debug(f"Globbing for Python files in {nodes_dir}")
        for file_path in nodes_dir.glob('*.py'):
            module_name = file_path.stem
            if file_path.name.startswith('__') or module_name.lower() in ('base_node', 'node_registry', 'nodetemplate'):
                logger.debug(f"Skipping file: {file_path.name}")
                continue
            logger.debug(f"Found potential node file: {module_name}")
            node_files[module_name] = file_path
        
        if node_files:
            logger.debug(f"Found {len(node_files)} potential node files for dynamic loading.")
        else:
            logger.debug("No additional node files found for dynamic loading.")
        
        for module_name, file_path in node_files.items():
            try:
                full_module_name = None
                try:
                    current = nodes_dir.parent
                    package_parts = [nodes_dir.name, module_name]
                    while current.name != 'act' and current != current.parent:
                        package_parts.insert(0, current.name)
                        current = current.parent
                    if current.name == 'act':
                        package_parts.insert(0, 'act')
                        full_module_name = ".".join(package_parts)
                        logger.debug(f"Trying module import path: {full_module_name}")
                    else:
                        logger.debug(f"Could not determine package root. Falling back to default guess: {nodes_package_name}.{module_name}")
                        full_module_name = f"{nodes_package_name}.{module_name}"
                except Exception:
                    logger.warning(f"Error calculating full module name for {module_name}. Using fallback.")
                    full_module_name = f"{nodes_package_name}.{module_name}"
                
                logger.debug(f"Attempting to import module: {full_module_name}")
                try:
                    module = importlib.import_module(full_module_name)
                except ImportError:
                    logger.debug(f"Full module import failed, trying direct import: {module_name}")
                    if str(nodes_dir) not in sys.path:
                        sys.path.insert(0, str(nodes_dir))
                    module = importlib.import_module(module_name)
                
                for attr_name, attr_value in inspect.getmembers(module, inspect.isclass):
                    if issubclass(attr_value, BaseNode) and attr_value is not BaseNode and not inspect.isabstract(attr_value):
                        node_class = attr_value
                        node_type = self._determine_node_type(node_class, attr_name, module_name)
                        
                        if node_type and node_type not in node_classes:
                            logger.debug(f"Discovered node class {attr_name} (from {module_name}) -> type '{node_type}'")
                            node_classes[node_type] = node_class
                        elif node_type and node_type in node_classes:
                            logger.debug(f"Node type '{node_type}' from {attr_name} already registered. Skipping.")
                        elif not node_type:
                            logger.warning(f"Could not determine node type for class {attr_name} in {module_name}.")
            except ImportError as e:
                logger.debug(f"ImportError processing node file {module_name}: {e}", exc_info=False)
            except Exception as e:
                logger.error(f"Error processing node file {module_name} ({file_path}): {e}", exc_info=True)
        
        logger.debug(f"Node discovery finished. Total distinct node types found: {len(node_classes)}")
        
        # NodeRegistry fallback
        try:
            from act.nodes.base_node import NodeRegistry
            registry_types = NodeRegistry.list_node_types()
            logger.debug(f"Adding {len(registry_types)} registered node types from NodeRegistry: {sorted(registry_types)}")
            
            for node_type in registry_types:
                if node_type not in node_classes:
                    node_class = NodeRegistry.get_node_class(node_type)
                    if node_class:
                        logger.debug(f"Added registered node: {node_type} -> {node_class.__name__}")
                        node_classes[node_type] = node_class
                else:
                    logger.debug(f"NodeRegistry type '{node_type}' already in filesystem discoveries")
        except Exception as e:
            logger.error(f"Error adding NodeRegistry types: {e}")
        
        # Critical nodes fallback
        critical_nodes = {
            'log_message': ('act.nodes.LogMessageNode', 'LogMessageNode'),
            'openai': ('act.nodes.OpenaiNode', 'OpenAINode'),
            'py': ('act.nodes.PyNode', 'PyNode'),
            'neon': ('act.nodes.NeonNode', 'NeonNode'),
            'aci': ('act.nodes.aci_node', 'ACINode'),
            'gemini': ('act.nodes.gemini_node', 'GeminiNode'),
            'github': ('act.nodes.GitHubNode', 'GitHubNode'),
        }
        
        for node_type, (module_path, class_name) in critical_nodes.items():
            if node_type not in node_classes:
                try:
                    logger.debug(f"FALLBACK: Attempting direct import of {node_type} from {module_path}")
                    module = importlib.import_module(module_path)
                    node_class = getattr(module, class_name)
                    
                    is_basenode_subclass = False
                    if node_class:
                        try:
                            is_basenode_subclass = issubclass(node_class, BaseNode)
                        except:
                            pass
                        
                        if not is_basenode_subclass:
                            for base in getattr(node_class, '__bases__', []):
                                if 'BaseNode' in str(base):
                                    is_basenode_subclass = True
                                    logger.debug(f"FALLBACK: Accepting {class_name} based on base class name match: {base}")
                                    break
                    
                    if is_basenode_subclass:
                        node_classes[node_type] = node_class
                        logger.debug(f"FALLBACK SUCCESS: Added {node_type} -> {node_class.__name__}")
                    else:
                        logger.error(f"FALLBACK FAILED: {class_name} is not a valid BaseNode subclass")
                except Exception as e:
                    logger.debug(f"FALLBACK FAILED: Could not import {node_type}: {e}")
        
        logger.debug(f"Final node discovery count: {len(node_classes)}")
        return node_classes
    
    def _determine_node_type(self, node_class: Type[BaseNode], class_name: str, module_name: str) -> Optional[str]:
        """Helper to determine the node type string from class.node_type or class name."""
        node_type = None
        try:
            schema_node_type = getattr(node_class, 'node_type', None)
            if schema_node_type and isinstance(schema_node_type, str):
                node_type = schema_node_type
                logger.debug(f"Using node_type '{node_type}' from class variable for class {class_name}")
                return node_type
        except Exception as e:
            logger.warning(f"Error checking node_type for {class_name}: {e}")
        
        if class_name.endswith('Node'):
            node_type = self._snake_case(class_name[:-4])
        else:
            node_type = self._snake_case(class_name)
        logger.debug(f"Using derived node_type '{node_type}' from class name {class_name}")
        return node_type
    
    def load_node_executors(self):
        """Instantiates node executor classes required by the current workflow."""
        logger.debug("Loading node executors for the current workflow...")
        
        if not self.workflow_data or 'nodes' not in self.workflow_data:
            logger.error("Cannot load node executors: Workflow data is not loaded or empty.")
            return
        
        node_types_in_workflow = set()
        for node_name, node_config in self.workflow_data['nodes'].items():
            if isinstance(node_config, dict) and node_config.get('type'):
                node_types_in_workflow.add(node_config['type'])
            else:
                logger.warning(f"Node '{node_name}' configuration is invalid or missing 'type'. Skipping.")
        
        if not node_types_in_workflow:
            logger.warning("No valid node types found in the current workflow definition.")
            return
        
        logger.debug(f"Workflow requires node types: {', '.join(sorted(list(node_types_in_workflow)))}")
        self.node_executors = {}
        self.node_loading_status = {node_type: {'status': 'pending', 'message': ''} for node_type in node_types_in_workflow}
        all_available_node_classes = self.discover_node_classes()
        logger.debug(f"Discovered {len(all_available_node_classes)} potentially available node types.")
        
        for node_type in node_types_in_workflow:
            node_class = None
            load_message = ""
            status = "error"
            
            node_class = all_available_node_classes.get(node_type)
            if node_class:
                load_message = f"Found exact match: class {node_class.__name__}"
                logger.debug(f"Found exact match for '{node_type}': {node_class.__name__}")
            else:
                logger.debug(f"No exact match for '{node_type}', checking case-insensitive...")
                found_case_insensitive = False
                for available_type, klass in all_available_node_classes.items():
                    if available_type.lower() == node_type.lower():
                        node_class = klass
                        load_message = f"Found case-insensitive match: type '{available_type}' (class {node_class.__name__})"
                        logger.debug(f"Found case-insensitive match for '{node_type}': Using type '{available_type}' ({node_class.__name__})")
                        found_case_insensitive = True
                        break
                if not found_case_insensitive:
                    load_message = "No suitable node class found (checked exact and case-insensitive)."
                    logger.warning(f"Could not find class for node type: '{node_type}'.")
            
            if node_class:
                try:
                    node_instance = self._instantiate_node(node_class)
                    if node_instance:
                        self.node_executors[node_type] = node_instance
                        status = 'success'
                        load_message += " -> Instantiated successfully."
                        logger.debug(f"Successfully loaded executor for '{node_type}'.")
                        
                        # Initialize circuit breaker for this node type
                        self.circuit_breakers[node_type] = CircuitBreaker()
                    else:
                        status = 'error'
                        load_message += " -> Instantiation failed (returned None)."
                        logger.error(f"Instantiation of {node_class.__name__} for '{node_type}' returned None.")
                except Exception as e:
                    status = 'error'
                    load_message += f" -> Instantiation error: {e}"
                    logger.debug(f"Skipped instantiating {node_class.__name__} for '{node_type}': {e}")
            
            self.node_loading_status[node_type]['status'] = status
            self.node_loading_status[node_type]['message'] = load_message
        
        self._print_node_loading_status()
    
    def reload_node_executor(self, node_type: str) -> bool:
        """
        Hot reload a node executor without restarting.
        
        Args:
            node_type: The type of node to reload
            
        Returns:
            True if reload successful, False otherwise
        """
        logger.debug(f"Attempting to reload node executor for type: {node_type}")
        
        try:
            # Find the module for this node type
            all_node_classes = self.discover_node_classes()
            node_class = all_node_classes.get(node_type)
            
            if not node_class:
                logger.error(f"Cannot reload '{node_type}': node class not found")
                return False
            
            # Get the module
            module = inspect.getmodule(node_class)
            if not module:
                logger.error(f"Cannot reload '{node_type}': module not found")
                return False
            
            # Reload the module
            importlib.reload(module)
            logger.debug(f"Reloaded module: {module.__name__}")
            
            # Re-instantiate the node
            reloaded_class = getattr(module, node_class.__name__)
            new_instance = self._instantiate_node(reloaded_class)
            
            if new_instance:
                self.node_executors[node_type] = new_instance
                logger.debug(f"Successfully reloaded executor for '{node_type}'")
                return True
            else:
                logger.error(f"Failed to instantiate reloaded class for '{node_type}'")
                return False
                
        except Exception as e:
            logger.error(f"Error reloading node executor '{node_type}': {e}", exc_info=True)
            return False
    
    def _print_node_loading_status(self):
        """Prints a formatted table showing the loading status of required nodes."""
        if not self.node_loading_status:
            print("\nNo nodes required by workflow or loading not performed.\n")
            return
        
        headers = ["Required Node Type", "Loading Status", "Details"]
        table_data = []
        
        for node_type, status_info in sorted(self.node_loading_status.items()):
            status = status_info['status']
            message = status_info['message']
            
            if status == 'success':
                status_symbol, color = "✓", Fore.GREEN
            elif status == 'fallback':
                status_symbol, color = "~", Fore.YELLOW
            elif status == 'error':
                status_symbol, color = "✗", Fore.RED
            else:
                status_symbol, color = "○", Fore.WHITE
            
            table_data.append([node_type, f"{color}{status_symbol} {status.upper()}{Style.RESET_ALL}", message])
        
        try:
            table = tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[None, 15, 80])
        except NameError:
            table = self._basic_table(table_data, headers)
        except Exception as e:
            logger.error(f"Error using tabulate for node loading status: {e}")
            table = self._basic_table(table_data, headers)
        
        print("\n--- Node Executor Loading Status ---\n" + table + "\n------------------------------------\n")
    
    def _basic_table(self, data, headers):
        """Minimal text table formatting if tabulate is unavailable."""
        if not data:
            return "No data."
        widths = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        sep = "+".join("-" * (w + 2) for w in widths)
        header_line = "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers)) + "|"
        data_lines = ["|" + "|".join(f" {str(cell):<{widths[i]}} " for i, cell in enumerate(row)) + "|" for row in data]
        return "\n".join([sep, header_line, sep] + data_lines + [sep])
    
    def _instantiate_node(self, node_class: Type[BaseNode]) -> Optional[BaseNode]:
        """Instantiates a node class, handles sandbox_timeout, sets execution_manager."""
        logger.debug(f"Instantiating node class: {node_class.__name__}")
        try:
            node_instance = node_class()
            
            set_manager_method = getattr(node_instance, 'set_execution_manager', None)
            if callable(set_manager_method):
                logger.debug(f"Setting execution manager for instance of {node_class.__name__}")
                set_manager_method(self)
            else:
                logger.debug(f"Node class {node_class.__name__} does not have 'set_execution_manager' method.")
            
            set_timeout_method = getattr(node_instance, 'set_sandbox_timeout', None)
            if callable(set_timeout_method):
                logger.debug(f"Setting sandbox timeout ({self.sandbox_timeout}s) for instance of {node_class.__name__}")
                set_timeout_method(self.sandbox_timeout)
            else:
                logger.debug(f"Node class {node_class.__name__} does not have 'set_sandbox_timeout' method.")
            
            return node_instance
        except Exception as e:
            logger.error(f"Failed to instantiate {node_class.__name__}: {e}", exc_info=True)
            return None
    
    # ==================== CHECKPOINT/RESUME ====================
    
    def save_checkpoint(self, checkpoint_name: Optional[str] = None) -> Path:
        """
        Save execution state for resume capability.
        
        Args:
            checkpoint_name: Optional name for checkpoint, defaults to timestamp
            
        Returns:
            Path to saved checkpoint file
        """
        if not self.enable_checkpoints:
            logger.warning("Checkpoints are disabled. Enable with enable_checkpoints=True")
            return None
        
        if not checkpoint_name:
            checkpoint_name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_name}.json"
        
        state = {
            'execution_id': self.current_execution_id,
            'node_results': self.node_results,
            'executed_nodes': list(self.executed_nodes),
            'node_execution_status': self.node_execution_status,
            'resolved_values_by_key': self.resolved_values_by_key,
            'metrics': self.metrics.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            self.metrics.checkpoint_saves += 1
            logger.debug(f"Checkpoint saved to: {checkpoint_path}")
            return checkpoint_path
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}", exc_info=True)
            return None
    
    def load_checkpoint(self, checkpoint_path: Union[str, Path]) -> bool:
        """
        Resume from saved checkpoint state.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            True if checkpoint loaded successfully
        """
        checkpoint_path = Path(checkpoint_path)
        
        if not checkpoint_path.exists():
            logger.error(f"Checkpoint file not found: {checkpoint_path}")
            return False
        
        try:
            with open(checkpoint_path) as f:
                state = json.load(f)
            
            self.current_execution_id = state.get('execution_id')
            self.node_results = state.get('node_results', {})
            self.executed_nodes = set(state.get('executed_nodes', []))
            self.node_execution_status = state.get('node_execution_status', {})
            self.resolved_values_by_key = state.get('resolved_values_by_key', {})
            
            logger.debug(f"Checkpoint loaded from: {checkpoint_path}")
            logger.debug(f"Resumed execution_id: {self.current_execution_id}")
            logger.debug(f"Nodes already executed: {len(self.executed_nodes)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}", exc_info=True)
            return False
    
    # ==================== WORKFLOW EXECUTION ====================
    
    def execute_workflow(self,
                        execution_id: Optional[str] = None,
                        initial_input: Optional[Dict[str, Any]] = None,
                        dry_run: bool = False) -> Dict[str, Any]:
        """
        Executes the loaded workflow synchronously.
        
        Args:
            execution_id: Optional execution ID
            initial_input: Initial input data for the workflow
            dry_run: If True, validate and plan without executing
            
        Returns:
            Execution results dictionary
        """
        self.dry_run_mode = dry_run
        self.current_execution_id = execution_id or f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if dry_run:
            logger.debug(f"Starting DRY RUN for workflow ID: {self.current_execution_id}")
            return self._validate_and_plan_execution()
        
        logger.debug(f"Starting synchronous execution wrapper for workflow ID: {self.current_execution_id}")
        
        self.node_results = {}
        self.node_execution_status = {}
        self.resolution_cache = {}
        self.resolved_values_by_key = {}
        self.executed_nodes = set()
        self.initial_input_data = dict(initial_input) if initial_input else {}
        self.metrics = ExecutionMetrics()
        
        logger.debug(f"Stored initial input data for run {self.current_execution_id}: {self.log_safe_node_data(self.initial_input_data)}")
        
        if self.workflow_data and 'nodes' in self.workflow_data:
            for node_name in self.workflow_data['nodes'].keys():
                self.update_node_status(node_name, "pending", "Waiting for execution")
        else:
            logger.error("Cannot execute workflow: Workflow data not loaded or missing nodes.")
            return {
                "status": "error",
                "message": "Workflow data not loaded/invalid.",
                "results": {},
                "node_status": self.node_execution_status,
                "execution_id": self.current_execution_id
            }
        
        try:
            try:
                loop = asyncio.get_running_loop()
                result = [None]
                exception = [None]
                
                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(self.execute_workflow_async())
                        new_loop.close()
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                
                if exception[0]:
                    raise exception[0]
                result = result[0]
            except RuntimeError:
                result = asyncio.run(self.execute_workflow_async())
            
            logger.debug(f"Workflow {self.current_execution_id} execution finished.")
            self._print_node_execution_results()
            
            # Auto-checkpoint on completion if enabled
            if self.enable_checkpoints:
                self.save_checkpoint(f"final_{self.current_execution_id}")
            
            return result
        except Exception as e:
            logger.error(f"Critical error during workflow execution run: {e}", exc_info=True)
            self._print_node_execution_results()
            
            last_node = "N/A"
            for name, status_info in self.node_execution_status.items():
                if status_info["status"] in ("running", "pending"):
                    last_node = name
                    self.update_node_status(last_node, "error", f"Workflow crashed: {e}")
                    break
            
            return {
                "status": "error",
                "message": f"Workflow execution failed with unexpected error: {e}",
                "results": self.node_results,
                "node_status": self.node_execution_status,
                "execution_id": self.current_execution_id,
                "metrics": self.metrics.to_dict()
            }
    
    def _validate_and_plan_execution(self) -> Dict[str, Any]:
        """Dry run mode: validate workflow and create execution plan."""
        logger.debug("Performing workflow validation and execution planning...")
        
        plan = {
            "status": "dry_run",
            "execution_id": self.current_execution_id,
            "workflow_name": self.actfile_parser.get_workflow_name() if self.actfile_parser else "Unknown",
            "total_nodes": len(self.workflow_data.get('nodes', {})),
            "execution_order": [],
            "parallel_opportunities": [],
            "validation_results": {
                "dag_valid": True,
                "all_nodes_loadable": True,
                "placeholder_warnings": []
            }
        }
        
        try:
            # Validate DAG
            self.validate_workflow_dag()
        except WorkflowValidationError as e:
            plan["validation_results"]["dag_valid"] = False
            plan["validation_results"]["dag_error"] = str(e)
        
        # Check node loading
        for node_type, status_info in self.node_loading_status.items():
            if status_info['status'] != 'success':
                plan["validation_results"]["all_nodes_loadable"] = False
        
        # Simulate execution order
        if self.actfile_parser:
            start_node = self.actfile_parser.get_start_node()
            if start_node:
                visited = set()
                queue = [start_node]
                
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    visited.add(current)
                    plan["execution_order"].append(current)
                    
                    successors = self.actfile_parser.get_node_successors(current)
                    queue.extend(successors)
        
        logger.debug(f"Dry run complete. Execution would process {len(plan['execution_order'])} nodes")
        return plan
    
    async def execute_workflow_async(self) -> Dict[str, Any]:
        """
        Asynchronously executes the workflow with advanced features:
        - Parallel execution
        - Retry logic
        - Circuit breaker
        - Metrics collection
        """
        exec_id = self.current_execution_id
        logger.debug(f"Starting ASYNC execution of workflow ID: {exec_id}")
        
        if self.resolution_debug_mode:
            logger.debug(f"Initial input data: {self.log_safe_node_data(self.initial_input_data)}")
        
        if not self.actfile_parser:
            logger.error("Cannot execute async workflow: Actfile parser not available.")
            return {
                "status": "error",
                "message": "Actfile parser not initialized.",
                "results": {},
                "node_status": self.node_execution_status,
                "execution_id": exec_id
            }
        
        self.sandbox_start_time = datetime.now()
        execution_queue: List[Tuple[str, Optional[Dict[str, Any]]]] = []
        
        try:
            start_node_name = self.actfile_parser.get_start_node()
            if not start_node_name:
                logger.error("No start node specified in Actfile.")
                return {
                    "status": "error",
                    "message": "No start node specified.",
                    "results": {},
                    "node_status": self.node_execution_status,
                    "execution_id": exec_id
                }
            
            if start_node_name not in self.workflow_data.get('nodes', {}):
                error_msg = f"Start node '{start_node_name}' defined but not found in 'nodes' section."
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "results": {},
                    "node_status": self.node_execution_status,
                    "execution_id": exec_id
                }
            
            logger.debug(f"Workflow starting at node: {start_node_name}")
            execution_queue.append((start_node_name, None))
            
            while execution_queue:
                # Check timeout
                if self.sandbox_timeout > 0 and \
                   (datetime.now() - self.sandbox_start_time).total_seconds() > self.sandbox_timeout:
                    timeout_msg = f"Workflow timeout ({self.sandbox_timeout}s) exceeded."
                    logger.error(timeout_msg)
                    node_about_to_run = execution_queue[0][0] if execution_queue else "N/A"
                    if node_about_to_run != "N/A" and node_about_to_run in self.node_execution_status:
                        self.update_node_status(node_about_to_run, "error", f"Timeout before execution: {timeout_msg}")
                    return {
                        "status": "error",
                        "message": timeout_msg,
                        "results": self.node_results,
                        "node_status": self.node_execution_status,
                        "execution_id": exec_id,
                        "metrics": self.metrics.to_dict()
                    }
                
                # Check for breakpoint
                node_name, previous_node_result_context = execution_queue.pop(0)
                
                if node_name in self.breakpoints:
                    logger.debug(f"BREAKPOINT: Execution paused at node '{node_name}'")
                    return {
                        "status": "paused",
                        "message": f"Breakpoint at node '{node_name}'",
                        "paused_at": node_name,
                        "results": self.node_results,
                        "node_status": self.node_execution_status,
                        "execution_id": exec_id,
                        "metrics": self.metrics.to_dict()
                    }
                
                if node_name in self.executed_nodes:
                    logger.debug(f"Node '{node_name}' already executed. Skipping.")
                    continue
                
                if node_name not in self.workflow_data.get('nodes', {}):
                    logger.error(f"Node '{node_name}' was scheduled but not defined in workflow.")
                    if node_name in self.node_execution_status:
                        self.update_node_status(node_name, "error", "Node definition missing.")
                    return {
                        "status": "error",
                        "message": f"Node '{node_name}' not found in workflow definition.",
                        "results": self.node_results,
                        "node_status": self.node_execution_status,
                        "execution_id": exec_id,
                        "metrics": self.metrics.to_dict()
                    }
                
                logger.debug(f"--- Executing Node: {node_name} ---")
                self.update_node_status(node_name, "running", "Node execution started")
                
                # Execute with retry logic
                try:
                    node_result = await self.execute_node_with_retry(
                        node_name,
                        input_context=previous_node_result_context
                    )
                    self.node_results[node_name] = node_result
                    self.executed_nodes.add(node_name)
                    
                except PlaceholderResolutionError as pre:
                    error_msg = f"Critical placeholder resolution error for node '{node_name}': {pre}"
                    logger.error(error_msg, exc_info=False)
                    self.update_node_status(node_name, "error", error_msg)
                    return {
                        "status": "error",
                        "message": error_msg,
                        "results": self.node_results,
                        "node_status": self.node_execution_status,
                        "execution_id": exec_id,
                        "metrics": self.metrics.to_dict()
                    }
                except Exception as node_exec_ex:
                    error_msg = f"Unexpected error running node '{node_name}': {node_exec_ex}"
                    logger.error(error_msg, exc_info=True)
                    self.update_node_status(node_name, "error", error_msg)
                    return {
                        "status": "error",
                        "message": error_msg,
                        "results": self.node_results,
                        "node_status": self.node_execution_status,
                        "execution_id": exec_id,
                        "metrics": self.metrics.to_dict()
                    }
                
                node_status = node_result.get('status') if isinstance(node_result, dict) else 'error'
                
                if node_status == 'error':
                    error_msg = node_result.get('message', 'Unknown node error') if isinstance(node_result, dict) else 'Node returned non-dict result'
                    logger.error(f"Node '{node_name}' execution failed: {error_msg}. Stopping workflow.")
                    return {
                        "status": "error",
                        "message": f"Workflow failed at node '{node_name}': {error_msg}",
                        "results": self.node_results,
                        "node_status": self.node_execution_status,
                        "execution_id": exec_id,
                        "metrics": self.metrics.to_dict()
                    }
                else:
                    logger.debug(f"Node '{node_name}' finished with status: {node_status}")
                
                # Determine next nodes (conditional logic)
                all_successors = self.actfile_parser.get_node_successors(node_name)
                logger.debug(f"Potential successors for '{node_name}': {all_successors}")
                
                current_node_type = self.workflow_data['nodes'][node_name].get('type')
                nodes_to_queue = []
                
                result_data = node_result.get('result', {}) if isinstance(node_result, dict) else {}
                if not isinstance(result_data, dict):
                    logger.warning(f"Result data for node '{node_name}' is not a dictionary. Conditional branching may fail.")
                    result_data = {}
                
                if current_node_type == 'if':
                    condition_outcome = result_data.get('result')
                    if isinstance(condition_outcome, bool):
                        logger.debug(f"IfNode '{node_name}' outcome: {condition_outcome}")
                        true_target = all_successors[0] if len(all_successors) > 0 else None
                        false_target = all_successors[1] if len(all_successors) > 1 else None
                        target_node_name = true_target if condition_outcome else false_target
                        
                        if target_node_name:
                            nodes_to_queue.append(target_node_name)
                            logger.debug(f"IfNode '{node_name}' branching to: '{target_node_name}'")
                        else:
                            logger.warning(f"IfNode '{node_name}' condition met but no path defined.")
                    else:
                        logger.error(f"IfNode '{node_name}' did not return boolean 'result'. Cannot branch.")
                        return {
                            "status": "error",
                            "message": f"IfNode '{node_name}' failed due to invalid result format.",
                            "results": self.node_results,
                            "node_status": self.node_execution_status,
                            "execution_id": exec_id,
                            "metrics": self.metrics.to_dict()
                        }
                
                elif current_node_type == 'switch':
                    target_node_name = result_data.get('selected_node')
                    if isinstance(target_node_name, str) and target_node_name:
                        if target_node_name in all_successors:
                            logger.debug(f"SwitchNode '{node_name}' selected: '{target_node_name}'")
                            nodes_to_queue.append(target_node_name)
                        else:
                            logger.error(f"SwitchNode '{node_name}' selected invalid target '{target_node_name}'.")
                            return {
                                "status": "error",
                                "message": f"SwitchNode '{node_name}' selected invalid target.",
                                "results": self.node_results,
                                "node_status": self.node_execution_status,
                                "execution_id": exec_id,
                                "metrics": self.metrics.to_dict()
                            }
                    elif target_node_name is None or target_node_name == "":
                        logger.debug(f"SwitchNode '{node_name}' selected no target. Path ends.")
                    else:
                        logger.error(f"SwitchNode '{node_name}' invalid result format.")
                        return {
                            "status": "error",
                            "message": f"SwitchNode '{node_name}' failed due to invalid result.",
                            "results": self.node_results,
                            "node_status": self.node_execution_status,
                            "execution_id": exec_id,
                            "metrics": self.metrics.to_dict()
                        }
                else:
                    logger.debug(f"Node type '{current_node_type}' is not conditional. Queueing all successors.")
                    nodes_to_queue.extend(all_successors)
                
                # Queue next nodes
                queued_count = 0
                for successor_name in nodes_to_queue:
                    if not successor_name:
                        continue
                    if successor_name not in self.workflow_data.get('nodes', {}):
                        logger.warning(f"Target node '{successor_name}' not defined. Skipping.")
                        continue
                    if any(item[0] == successor_name for item in execution_queue):
                        logger.debug(f"Target node '{successor_name}' already in queue. Skipping.")
                        continue
                    if successor_name in self.executed_nodes:
                        logger.debug(f"Target node '{successor_name}' already executed. Skipping.")
                        continue
                    
                    logger.debug(f"Queueing next node: '{successor_name}'")
                    execution_queue.append((successor_name, node_result))
                    if successor_name not in self.node_execution_status or \
                       self.node_execution_status[successor_name]['status'] not in ['running', 'error', 'success', 'warning']:
                        self.update_node_status(successor_name, "pending", f"Queued after '{node_name}'")
                    queued_count += 1
            
            logger.debug(f"Workflow execution completed successfully for ID: {exec_id}")
            return {
                "status": "success",
                "message": "Workflow executed successfully",
                "results": self.node_results,
                "node_status": self.node_execution_status,
                "execution_id": exec_id,
                "metrics": self.metrics.to_dict()
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during async workflow execution: {e}", exc_info=True)
            last_node = locals().get('node_name', 'N/A')
            if last_node != "N/A" and last_node in self.node_execution_status:
                self.update_node_status(last_node, "error", f"Workflow loop error: {e}")
            return {
                "status": "error",
                "message": f"Workflow failed unexpectedly: {e}",
                "results": self.node_results,
                "node_status": self.node_execution_status,
                "execution_id": exec_id,
                "metrics": self.metrics.to_dict()
            }
    
    async def execute_node_with_retry(self,
                                      node_name: str,
                                      input_context: Optional[Dict[str, Any]] = None,
                                      max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a node with retry logic and exponential backoff.
        
        Args:
            node_name: Name of the node to execute
            input_context: Input context from previous node
            max_retries: Maximum retry attempts (overrides resource_limits)
            
        Returns:
            Node execution result
        """
        if max_retries is None:
            max_retries = self.resource_limits.max_retries_per_node
        
        node_config = self.workflow_data['nodes'][node_name]
        node_type = node_config.get('type')
        
        # Check circuit breaker
        circuit_breaker = self.circuit_breakers.get(node_type)
        if circuit_breaker and not circuit_breaker.can_execute():
            error_msg = f"Circuit breaker is OPEN for node type '{node_type}'. Skipping execution."
            logger.error(error_msg)
            self.metrics.circuit_breaker_trips[node_type] += 1
            raise CircuitBreakerError(error_msg)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.metrics.retry_counts[node_name] += 1
                    backoff_time = min(2 ** attempt, 30)  # Cap at 30 seconds
                    logger.debug(f"Retry attempt {attempt}/{max_retries} for node '{node_name}' after {backoff_time}s")
                    self.update_node_status(node_name, "retrying", f"Retry {attempt}/{max_retries}")
                    await asyncio.sleep(backoff_time)
                
                # Execute the node
                result = await self.execute_node_async(node_name, input_context)
                
                # Check if successful
                if result.get('status') == 'success':
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    return result
                
                # If not successful, treat as error for retry
                last_error = result.get('message', 'Node execution failed')
                
                # Don't retry if it's a validation error
                if result.get('status') == 'error' and 'validation' in last_error.lower():
                    logger.debug(f"Validation error in node '{node_name}'. Not retrying.")
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    return result
                
            except PlaceholderResolutionError as e:
                # Don't retry placeholder resolution errors
                logger.error(f"Placeholder resolution error in node '{node_name}': {e}")
                if circuit_breaker:
                    circuit_breaker.record_failure()
                raise
            
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Error in node '{node_name}' (attempt {attempt + 1}/{max_retries + 1}): {e}")
        
        # All retries exhausted
        logger.error(f"Node '{node_name}' failed after {max_retries} retries. Last error: {last_error}")
        
        if circuit_breaker:
            circuit_breaker.record_failure()
        
        return {
            "status": "error",
            "message": f"Failed after {max_retries} retries. Last error: {last_error}",
            "error_type": "RetryExhausted"
        }
    
    async def execute_node_async(self, node_name: str, input_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a single node with comprehensive error handling and metrics.
        """
        start_time = time.time()
        
        if self.resolution_debug_mode:
            logger.debug(f"EXEC_NODE_ASYNC: Starting execution for node '{node_name}'")
        
        try:
            if not self.workflow_data or node_name not in self.workflow_data.get('nodes', {}):
                raise NodeExecutionError(f"Node '{node_name}' configuration not found in workflow data.")
            
            node_config = copy.deepcopy(self.workflow_data['nodes'][node_name])
            node_type = node_config.get('type')
            
            if not node_type:
                raise NodeExecutionError(f"Node '{node_name}' definition is missing the required 'type' field.")
            
            # Resolve placeholders
            if self.resolution_debug_mode:
                logger.debug(f"EXEC_NODE_ASYNC: Resolving placeholders for '{node_name}'")
            
            try:
                resolution_stack: Set[str] = set()
                resolved_node_config = self.resolve_placeholders_recursively(node_config, resolution_stack)
                if self.resolution_debug_mode:
                    logger.debug(f"EXEC_NODE_ASYNC: '{node_name}' config AFTER resolving: {self.log_safe_node_data(resolved_node_config)}")
            except PlaceholderResolutionError as resolve_err:
                raise NodeExecutionError(f"Failed placeholder resolution for node '{node_name}': {resolve_err}") from resolve_err
            except Exception as resolve_err:
                logger.error(f"Unexpected error during placeholder resolution for '{node_name}': {resolve_err}", exc_info=True)
                raise NodeExecutionError(f"Unexpected error resolving placeholders for node '{node_name}': {resolve_err}") from resolve_err
            
            # Validate schema if available
            if node_type in self.schema_cache:
                try:
                    self._validate_node_config(node_name, resolved_node_config, self.schema_cache[node_type])
                except NodeValidationError as ve:
                    raise NodeExecutionError(f"Schema validation failed for '{node_name}': {ve}") from ve
            
            # Process parameters
            if self.resolution_debug_mode:
                logger.debug(f"EXEC_NODE_ASYNC: Processing resolved parameters for '{node_name}'...")
            
            processed_data = self._process_node_parameters(resolved_node_config)
            executor_data = self._structure_data_for_executor(processed_data, node_name, input_context)
            
            if self.resolution_debug_mode:
                logger.debug(f"EXEC_NODE_ASYNC: Final data package for executor '{node_name}': {self.log_safe_node_data(executor_data)}")
            
            # Get executor
            executor = self.node_executors.get(node_type)
            if not executor:
                raise NodeExecutionError(f"No executor instance loaded for type '{node_type}' (node: '{node_name}').")
            
            logger.debug(f"Calling {type(executor).__name__}.execute for node '{node_name}'")
            execute_method = getattr(executor, 'execute', None)
            if not callable(execute_method):
                raise NodeExecutionError(f"Executor for node type '{node_type}' has no callable 'execute' method.")
            
            # Execute
            node_result = None
            try:
                if inspect.iscoroutinefunction(execute_method):
                    node_result = await execute_method(executor_data)
                else:
                    loop = asyncio.get_running_loop()
                    node_result = await loop.run_in_executor(
                        self.executor_pool,
                        lambda: execute_method(executor_data)
                    )
                
                if inspect.iscoroutine(node_result):
                    logger.warning(f"Execute method for '{node_name}' returned an awaitable unexpectedly. Awaiting it.")
                    node_result = await node_result
            
            except Exception as exec_err:
                logger.error(f"Error during {node_type}.execute() for node '{node_name}': {exec_err}", exc_info=True)
                raise NodeExecutionError(f"Node execution failed: {exec_err}") from exec_err
            finally:
                duration = time.time() - start_time
                self.metrics.node_execution_times[node_name] = duration
                logger.debug(f"Node '{node_name}' execution took {duration:.3f} seconds.")
            
            if self.resolution_debug_mode:
                logger.debug(f"EXEC_NODE_ASYNC: Node '{node_name}' raw result: {self.log_safe_node_data(node_result)}")
            
            # Validate result format
            if not isinstance(node_result, dict) or 'status' not in node_result:
                logger.warning(f"Node '{node_name}' result is not a dict or missing 'status'. Wrapping.")
                final_result = {
                    "status": "warning",
                    "message": "Node returned unexpected result format.",
                    "result": node_result
                }
            else:
                final_result = node_result
            
            node_status = final_result.get('status', 'error')
            valid_statuses = ['success', 'error', 'warning']
            if node_status not in valid_statuses:
                logger.warning(f"Node '{node_name}' returned invalid status '{node_status}'.")
                original_message = final_result.get('message', '')
                final_result['status'] = 'warning'
                final_result['message'] = f"[Invalid Status '{node_status}'] {original_message}"
                node_status = 'warning'
            
            node_message = final_result.get('message', '')
            
            # Handle 'set' node
            if node_type == 'set' and node_status != 'error':
                set_result_data = final_result.get('result', {})
                if isinstance(set_result_data, dict):
                    key = set_result_data.get('key')
                    value = set_result_data.get('value')
                    if key and isinstance(key, str):
                        self.resolved_values_by_key[key] = value
                        if self.resolution_debug_mode:
                            logger.debug(f"EXEC_NODE_ASYNC: Stored value from 'set' node '{node_name}' for key '{key}'")
                    else:
                        logger.warning(f"'Set' node '{node_name}' result missing 'key' or key is not a string")
            
            # Handle 'aci' node
            if node_type == 'aci' and node_status != 'error' and self.agent_server:
                aci_result_data = final_result.get('result', {})
                if isinstance(aci_result_data, dict):
                    operation = executor_data.get('params', {}).get('operation')
                    if operation == 'add_route':
                        route_path = aci_result_data.get('path')
                        if route_path:
                            route_config = aci_result_data.copy()
                            self.agent_server.register_aci_route(route_path, route_config)
                            logger.debug(f"Registered ACI route {route_path} with agent server")
                    elif operation == 'remove_route':
                        route_path = executor_data.get('params', {}).get('route_path')
                        if route_path:
                            self.agent_server.unregister_aci_route(route_path)
                            logger.debug(f"Unregistered ACI route {route_path} from agent server")
            
            self.update_node_status(node_name, node_status, node_message)
            return final_result
        
        except (NodeExecutionError, NodeValidationError, ActfileParserError) as e:
            error_msg = f"Error executing node {node_name}: {e}"
            logger.error(error_msg, exc_info=False)
            self.update_node_status(node_name, "error", error_msg)
            return {"status": "error", "message": error_msg, "error_type": type(e).__name__}
        except FileNotFoundError as e:
            error_msg = f"File not found during execution of node {node_name}: {e}"
            logger.error(error_msg, exc_info=False)
            self.update_node_status(node_name, "error", error_msg)
            return {"status": "error", "message": error_msg, "error_type": type(e).__name__}
        except Exception as e:
            error_msg = f"Unexpected error during execution of node {node_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.update_node_status(node_name, "error", error_msg)
            return {"status": "error", "message": error_msg, "error_type": type(e).__name__}
    
    def _validate_node_config(self, node_name: str, config: Dict[str, Any], schema: Dict[str, Any]):
        """
        Validate node configuration against schema.
        
        Args:
            node_name: Name of the node
            config: Node configuration
            schema: JSON schema for validation
        """
        try:
            import jsonschema
            jsonschema.validate(config, schema)
            logger.debug(f"Schema validation passed for node '{node_name}'")
        except ImportError:
            logger.warning("jsonschema library not available. Skipping schema validation.")
        except Exception as e:
            raise NodeValidationError(f"Schema validation failed: {e}")
    
    def _structure_data_for_executor(self,
                                     processed_data: Dict[str, Any],
                                     node_name: str,
                                     previous_node_result_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Organizes processed data into the structure expected by node execute methods."""
        executor_data = {}
        params = {}
        metadata_keys = {'type', 'label', 'position_x', 'position_y', 'description'}
        
        for k, v in processed_data.items():
            if k in metadata_keys:
                executor_data[k] = v
            else:
                params[k] = v
        
        executor_data['params'] = params
        executor_data['__node_name'] = node_name
        executor_data['__execution_id'] = self.current_execution_id
        
        if self.resolution_debug_mode:
            logger.debug(f"Structuring data for executor {node_name}. Params keys: {list(params.keys())}")
        
        return executor_data
    
    def _process_node_parameters(self, resolved_node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempts type conversions on resolved values (bool, numeric, JSON).
        """
        processed_data = resolved_node_data.copy()
        
        if self.resolution_debug_mode:
            logger.debug(f"PROCESS_PARAMS: Starting type conversion for keys: {list(processed_data.keys())}")
        
        for key, value in processed_data.items():
            if isinstance(value, str):
                original_value_repr = repr(value)
                new_value = value
                conversion_applied = False
                
                # Skip unresolved placeholders
                if (value.startswith('{{') and value.endswith('}}')) or \
                   (value.startswith('${') and value.endswith('}')):
                    if self.resolution_debug_mode:
                        logger.debug(f"PROCESS_PARAMS: Key '{key}' looks like unresolved placeholder. Skipping.")
                    continue
                
                # Boolean conversion
                if value.lower() == 'true':
                    new_value = True
                    conversion_applied = True
                elif value.lower() == 'false':
                    new_value = False
                    conversion_applied = True
                # Numeric conversion
                elif not conversion_applied:
                    if re.fullmatch(r'-?\d+', value):
                        try:
                            new_value = int(value)
                            conversion_applied = True
                        except ValueError:
                            pass
                    elif re.fullmatch(r'-?\d+(\.\d+)?', value) or re.fullmatch(r'-?\.\d+', value):
                        try:
                            new_value = float(value)
                            conversion_applied = True
                        except ValueError:
                            pass
                # JSON conversion
                elif not conversion_applied:
                    looks_like_json = (value.strip().startswith(('[', '{')) and value.strip().endswith((']', '}')))
                    is_potential_json_key = key.lower() in [
                        'messages', 'json_body', 'data', 'payload', 'headers',
                        'items', 'list', 'options', 'config', 'arguments', 'parameters'
                    ]
                    
                    if looks_like_json or is_potential_json_key:
                        try:
                            decoded_json = json.loads(value)
                            if looks_like_json:
                                new_value = decoded_json
                                conversion_applied = True
                            elif is_potential_json_key:
                                if isinstance(decoded_json, (dict, list)):
                                    new_value = decoded_json
                                    conversion_applied = True
                        except json.JSONDecodeError:
                            if looks_like_json and self.resolution_debug_mode:
                                logger.debug(f"PROCESS_PARAMS: Key '{key}' looked like JSON but failed to decode.")
                
                if conversion_applied:
                    processed_data[key] = new_value
                    if self.resolution_debug_mode:
                        logger.debug(f"PROCESS_PARAMS: Converted key '{key}': {original_value_repr} -> {repr(new_value)}")
            else:
                if self.resolution_debug_mode:
                    logger.debug(f"PROCESS_PARAMS: Key '{key}' is already type {type(value).__name__}")
        
        if self.resolution_debug_mode:
            logger.debug(f"PROCESS_PARAMS: Finished parameter type conversion.")
        
        return processed_data
    
    # ==================== PLACEHOLDER RESOLUTION ====================
    
    def resolve_placeholders_recursively(self, data: Any, resolution_stack: Set[str]) -> Any:
        """
        Recursively resolves placeholders in data structures with advanced features.
        """
        if isinstance(data, dict):
            resolved_dict = {}
            for key, value in data.items():
                resolved_value = self.resolve_placeholders_recursively(value, resolution_stack)
                if isinstance(key, str) and ('{{' in key or '${' in key):
                    resolved_key = self.resolve_placeholder_string(key, resolution_stack)
                    if not isinstance(resolved_key, str):
                        logger.warning(f"Placeholder key '{key}' resolved to non-string. Using original key.")
                        resolved_key = key
                else:
                    resolved_key = key
                resolved_dict[resolved_key] = resolved_value
            return resolved_dict
        elif isinstance(data, list):
            return [self.resolve_placeholders_recursively(item, resolution_stack) for item in data]
        elif isinstance(data, str):
            return self.resolve_placeholder_string(data, resolution_stack)
        else:
            return data
    
    def resolve_placeholder_string(self, text: str, resolution_stack: Set[str]) -> Any:
        """
        Enhanced placeholder resolution with caching and circular reference detection.
        """
        if not isinstance(text, str) or not ('${' in text or '{{' in text):
            return text
        
        # Check cache
        cache_key = f"resolved:{text}"
        if cache_key in self.resolution_cache:
            if self.resolution_debug_mode:
                logger.debug(f"RESOLVE_STR: Cache hit for '{text}'")
            self.metrics.resolution_cache_hits += 1
            return self.resolution_cache[cache_key]
        
        self.metrics.resolution_cache_misses += 1
        
        # Check circular reference
        if text in resolution_stack:
            cycle_path = " -> ".join(list(resolution_stack) + [text])
            logger.error(f"Circular placeholder reference detected: {cycle_path}")
            raise PlaceholderResolutionError(f"Circular reference detected: {cycle_path}")
        
        resolution_stack.add(text)
        if self.resolution_debug_mode:
            logger.debug(f"RESOLVE_STR: Added '{text}' to stack")
        
        resolved_value = text
        
        try:
            # Resolve environment variables
            env_var_pattern = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}')
            resolved_text_env = text
            offset = 0
            
            for match in env_var_pattern.finditer(text):
                var_name = match.group(1)
                env_value = os.environ.get(var_name)
                start, end = match.span()
                start += offset
                end += offset
                placeholder = match.group(0)
                
                if env_value is not None:
                    if self.resolution_debug_mode:
                        logger.debug(f"RESOLVE_STR: Resolved env var '{placeholder}'")
                    resolved_text_env = resolved_text_env[:start] + env_value + resolved_text_env[end:]
                    offset += len(env_value) - len(placeholder)
                else:
                    logger.warning(f"Env var '{placeholder}' not found. Leaving placeholder.")
            
            current_text = resolved_text_env
            placeholder_pattern = re.compile(r'\{\{(.*?)\}\}')
            matches = list(placeholder_pattern.finditer(current_text))
            
            if not matches:
                resolved_value = current_text
            else:
                first_match = matches[0]
                is_full_match = len(matches) == 1 and first_match.group(0) == current_text.strip()
                
                if is_full_match:
                    placeholder_content_full = first_match.group(1).strip()
                    if not placeholder_content_full:
                        resolved_value = current_text
                    else:
                        if self.resolution_debug_mode:
                            logger.debug(f"RESOLVE_STR: FULL resolution for: '{{{{{placeholder_content_full}}}}}'")
                        
                        resolved_native = self._resolve_single_placeholder_content(placeholder_content_full, resolution_stack)
                        if resolved_native is not None:
                            resolved_value = resolved_native
                            self.metrics.total_placeholders_resolved += 1
                        else:
                            logger.warning(f"RESOLVE_STR: Could not resolve '{{{{{placeholder_content_full}}}}}'")
                            if self.fail_on_unresolved:
                                raise PlaceholderResolutionError(f"Unresolved placeholder: '{{{{{placeholder_content_full}}}}}'")
                            resolved_value = current_text
                else:
                    # Partial replacements
                    if self.resolution_debug_mode:
                        logger.debug(f"RESOLVE_STR: Partial replacements in: '{current_text}'")
                    
                    resolved_text_partial = current_text
                    offset = 0
                    
                    for match in matches:
                        start, end = match.span()
                        start += offset
                        end += offset
                        full_placeholder = match.group(0)
                        placeholder_content_partial = match.group(1).strip()
                        
                        if not placeholder_content_partial:
                            continue
                        
                        value_partial = self._resolve_single_placeholder_content(placeholder_content_partial, resolution_stack)
                        if value_partial is not None:
                            str_value = str(value_partial)
                            if self.resolution_debug_mode:
                                logger.debug(f"RESOLVE_STR: Replacing '{{{{{placeholder_content_partial}}}}}' with '{str_value[:50]}'")
                            resolved_text_partial = resolved_text_partial[:start] + str_value + resolved_text_partial[end:]
                            offset += len(str_value) - len(full_placeholder)
                            self.metrics.total_placeholders_resolved += 1
                        else:
                            logger.warning(f"RESOLVE_STR: Could not resolve '{{{{{placeholder_content_partial}}}}}'")
                            if self.fail_on_unresolved:
                                raise PlaceholderResolutionError(f"Unresolved placeholder: '{{{{{placeholder_content_partial}}}}}'")
                    
                    resolved_value = resolved_text_partial
        
        except PlaceholderResolutionError:
            raise
        except Exception as e:
            logger.error(f"RESOLVE_STR: Unexpected error resolving '{text}': {e}", exc_info=True)
            raise PlaceholderResolutionError(f"Unexpected error resolving '{text}': {e}") from e
        finally:
            resolution_stack.remove(text)
            if self.resolution_debug_mode:
                logger.debug(f"RESOLVE_STR: Removed '{text}' from stack")
            
            self.resolution_cache[cache_key] = resolved_value
            if self.resolution_debug_mode:
                logger.debug(f"RESOLVE_STR: Cached result for '{text}'")
        
        return resolved_value
    
    def _resolve_single_placeholder_content(self, content: str, resolution_stack: Set[str]) -> Any:
        """
        Resolves content inside {{...}}, handling 'key:' prefix, 'source.path', and fallback values.
        """
        content = content.strip()
        if not content:
            return None
        
        parts = content.split('|', 1)
        main_content = parts[0].strip()
        fallback_str = parts[1].strip() if len(parts) > 1 else None
        
        if self.resolution_debug_mode:
            logger.debug(f"RESOLVE_CONTENT: content='{main_content}'" + (f", fallback='{fallback_str}'" if fallback_str else ""))
        
        # Check cache
        if main_content in self.resolution_cache:
            if self.resolution_debug_mode:
                logger.debug(f"RESOLVE_CONTENT: Cache hit for '{main_content}'")
            if main_content in resolution_stack:
                cycle_path = " -> ".join(list(resolution_stack) + [main_content])
                raise PlaceholderResolutionError(f"Circular reference: {cycle_path}")
            return self.resolution_cache[main_content]
        
        if main_content in resolution_stack:
            cycle_path = " -> ".join(list(resolution_stack) + [main_content])
            raise PlaceholderResolutionError(f"Circular reference: {cycle_path}")
        
        resolution_stack.add(main_content)
        if self.resolution_debug_mode:
            logger.debug(f"RESOLVE_CONTENT: Added '{main_content}' to stack")
        
        resolved_value = None
        resolution_failed = False
        
        try:
            # Handle 'key:' prefix
            if main_content.startswith('key:'):
                key_name = main_content[len('key:'):].strip()
                if not key_name:
                    logger.warning("RESOLVE_CONTENT: 'key:' prefix with empty key name")
                    resolution_failed = True
                else:
                    if self.resolution_debug_mode:
                        logger.debug(f"RESOLVE_CONTENT: Fetching key: '{key_name}'")
                    
                    if key_name in self.resolved_values_by_key:
                        resolved_value = self.resolved_values_by_key[key_name]
                        if self.resolution_debug_mode:
                            logger.debug(f"RESOLVE_CONTENT: Found key '{key_name}' in cache")
                        resolved_value = self.resolve_placeholders_recursively(resolved_value, resolution_stack)
                    else:
                        logger.warning(f"RESOLVE_CONTENT: Key '{key_name}' not found in resolved values")
                        resolution_failed = True
            else:
                # Handle source.path
                source_id, path = self._split_placeholder_path(main_content)
                if source_id == '__invalid_source__':
                    logger.warning(f"RESOLVE_CONTENT: Invalid source in '{main_content}'")
                    resolution_failed = True
                else:
                    if self.resolution_debug_mode:
                        logger.debug(f"RESOLVE_CONTENT: Fetching source='{source_id}', path='{path}'")
                    
                    fetched_value = self.fetch_value(source_id, path)
                    if fetched_value is not None:
                        resolved_value = self.resolve_placeholders_recursively(fetched_value, resolution_stack)
                    else:
                        resolution_failed = True
            
            # Handle fallback
            if resolution_failed:
                if fallback_str is not None:
                    if self.resolution_debug_mode:
                        logger.debug(f"RESOLVE_CONTENT: Using fallback '{fallback_str}'")
                    resolved_value = self._parse_fallback_value(fallback_str)
                    resolved_value = self.resolve_placeholders_recursively(resolved_value, resolution_stack)
                else:
                    if self.resolution_debug_mode:
                        logger.debug(f"RESOLVE_CONTENT: Resolution failed, no fallback")
                    resolved_value = None
        
        except PlaceholderResolutionError:
            raise
        except Exception as e:
            logger.error(f"RESOLVE_CONTENT: Unexpected error resolving '{content}': {e}", exc_info=True)
            resolution_failed = True
            resolved_value = None
            if fallback_str is not None:
                if self.resolution_debug_mode:
                    logger.debug(f"RESOLVE_CONTENT: Using fallback due to error")
                resolved_value = self._parse_fallback_value(fallback_str)
                resolved_value = self.resolve_placeholders_recursively(resolved_value, resolution_stack)
        finally:
            resolution_stack.remove(main_content)
            if self.resolution_debug_mode:
                logger.debug(f"RESOLVE_CONTENT: Removed '{main_content}' from stack")
            
            self.resolution_cache[main_content] = resolved_value
            if self.resolution_debug_mode:
                logger.debug(f"RESOLVE_CONTENT: Cached result for '{main_content}'")
        
        return resolved_value
    
    def _parse_fallback_value(self, fallback_str: str) -> Any:
        """Parse fallback string into appropriate type."""
        fallback_str = fallback_str.strip()
        
        if fallback_str.lower() == 'true':
            return True
        if fallback_str.lower() == 'false':
            return False
        if fallback_str.lower() in ('null', 'none'):
            return None
        
        # Numeric
        if re.fullmatch(r'-?\d+', fallback_str):
            try:
                return int(fallback_str)
            except ValueError:
                pass
        
        if re.fullmatch(r'-?\d+(\.\d+)?', fallback_str) or re.fullmatch(r'-?\.\d+', fallback_str):
            try:
                return float(fallback_str)
            except ValueError:
                pass
        
        # Quoted JSON
        if (fallback_str.startswith('"') and fallback_str.endswith('"')) or \
           (fallback_str.startswith("'") and fallback_str.endswith("'")):
            try:
                inner_str = fallback_str[1:-1]
                if (inner_str.startswith('[') and inner_str.endswith(']')) or \
                   (inner_str.startswith('{') and inner_str.endswith('}')):
                    return json.loads(inner_str)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Remove quotes
        if (fallback_str.startswith('"') and fallback_str.endswith('"')) or \
           (fallback_str.startswith("'") and fallback_str.endswith("'")):
            if len(fallback_str) >= 2:
                return fallback_str[1:-1]
            else:
                return ""
        
        return fallback_str
    
    def _split_placeholder_path(self, content: str) -> Tuple[str, str]:
        """Split 'source.path.to.value' into ('source', 'path.to.value')."""
        parts = content.split('.', 1)
        source_id = parts[0].strip()
        path = parts[1].strip() if len(parts) > 1 else ""
        
        if not source_id or (not re.match(r'^[a-zA-Z0-9_\-]+$', source_id) and source_id != 'input'):
            logger.warning(f"Placeholder '{content}' has potentially invalid source_id '{source_id}'")
        
        return source_id, path
    
    def fetch_value(self, source_id: str, path: str) -> Any:
        """
        ENHANCED: Robustly fetches values with multiple resolution strategies.
        Handles both direct result structures and nested 'result' wrappers.
        """
        if self.resolution_debug_mode:
            logger.debug(f"FETCH_VALUE: source_id='{source_id}', path='{path}'")
        
        base_value = None
        
        # Determine base value
        if source_id == 'input':
            base_value = self.initial_input_data
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Using initial_input_data")
        elif source_id in self.node_results:
            base_value = self.node_results.get(source_id)
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Found node result for '{source_id}'. Type: {type(base_value).__name__}")
        else:
            if source_id in self.workflow_data.get('nodes', {}):
                logger.warning(f"FETCH_VALUE: Source node '{source_id}' exists but has no result yet")
            else:
                logger.warning(f"FETCH_VALUE: Source ID '{source_id}' not found")
            return None
        
        # No path - return whole base
        if not path:
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: No path, returning entire base")
            return base_value
        
        # Parse path (handles keys and indices)
        path_parts = re.findall(r'([^.\[\]]+)|(\[\d+\])', path)
        cleaned_parts = []
        for part_tuple in path_parts:
            if part_tuple[0]:
                cleaned_parts.append(part_tuple[0])
            elif part_tuple[1]:
                try:
                    cleaned_parts.append(int(part_tuple[1][1:-1]))
                except (ValueError, IndexError):
                    logger.warning(f"FETCH_VALUE: Invalid array index '{part_tuple[1]}'")
                    return None
        
        if not cleaned_parts:
            cleaned_parts = path.split('.')
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Using simple split: {cleaned_parts}")
        
        if self.resolution_debug_mode:
            logger.debug(f"FETCH_VALUE: Parsed path '{path}' into: {cleaned_parts}")
        
        # STRATEGY 1: Try original path
        current_value = self._traverse_path(base_value, cleaned_parts, source_id, path)
        if current_value is not None:
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Resolved using original path")
            return current_value
        
        # STRATEGY 2: Skip 'result' wrapper if path starts with it
        if (cleaned_parts and isinstance(cleaned_parts[0], str) and 
            cleaned_parts[0] == 'result' and len(cleaned_parts) > 1):
            
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Trying to skip 'result' wrapper")
            
            fallback_parts = cleaned_parts[1:]
            fallback_value = self._traverse_path(base_value, fallback_parts, source_id, path)
            
            if fallback_value is not None:
                if self.resolution_debug_mode:
                    logger.debug(f"FETCH_VALUE: Resolved by skipping 'result' wrapper")
                return fallback_value
        
        # STRATEGY 3: Add 'result' prefix
        if (cleaned_parts and isinstance(cleaned_parts[0], str) and cleaned_parts[0] != 'result'):
            
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Trying to add 'result' prefix")
            
            prefixed_parts = ['result'] + cleaned_parts
            prefixed_value = self._traverse_path(base_value, prefixed_parts, source_id, path)
            
            if prefixed_value is not None:
                if self.resolution_debug_mode:
                    logger.debug(f"FETCH_VALUE: Resolved by adding 'result' prefix")
                return prefixed_value
        
        # STRATEGY 4: Direct access to result field
        if (isinstance(base_value, dict) and 'result' in base_value and 
            cleaned_parts and isinstance(cleaned_parts[0], str)):
            
            if self.resolution_debug_mode:
                logger.debug(f"FETCH_VALUE: Trying direct access to 'result' field")
            
            result_data = base_value['result']
            if isinstance(result_data, dict) and cleaned_parts[0] in result_data:
                if len(cleaned_parts) == 1:
                    return result_data[cleaned_parts[0]]
                else:
                    remaining_parts = cleaned_parts[1:]
                    direct_value = self._traverse_path(result_data[cleaned_parts[0]], remaining_parts, source_id, path)
                    if direct_value is not None:
                        if self.resolution_debug_mode:
                            logger.debug(f"FETCH_VALUE: Resolved via direct result access")
                        return direct_value
        
        # All strategies failed
        if self.resolution_debug_mode:
            logger.debug(f"FETCH_VALUE: All strategies failed for '{source_id}.{path}'")
            logger.debug(f"FETCH_VALUE: Base value structure: {self.log_safe_node_data(base_value, max_depth=2)}")
        
        logger.warning(f"FETCH_VALUE: Could not resolve '{source_id}.{path}'")
        return None
    
    def _traverse_path(self, base_value: Any, path_parts: list, source_id: str, original_path: str) -> Any:
        """
        Helper method to traverse a path through nested data structures.
        """
        if not path_parts:
            return base_value
        
        current_value = base_value
        
        for i, part in enumerate(path_parts):
            current_path_str = f"{source_id}.{'.'.join(map(str, path_parts[:i+1]))}"
            
            if isinstance(part, str):  # Dictionary key
                if isinstance(current_value, dict):
                    if part in current_value:
                        current_value = current_value[part]
                        if self.resolution_debug_mode:
                            logger.debug(f"TRAVERSE_PATH: Found key '{part}' at {current_path_str}")
                    else:
                        if self.resolution_debug_mode:
                            available_keys = list(current_value.keys()) if isinstance(current_value, dict) else []
                            logger.debug(f"TRAVERSE_PATH: Key '{part}' not found at {current_path_str}. Available: {available_keys[:10]}")
                        return None
                else:
                    if self.resolution_debug_mode:
                        logger.debug(f"TRAVERSE_PATH: Cannot access key '{part}'; current is {type(current_value).__name__}")
                    return None
            
            elif isinstance(part, int):  # List index
                if isinstance(current_value, list):
                    if 0 <= part < len(current_value):
                        current_value = current_value[part]
                        if self.resolution_debug_mode:
                            logger.debug(f"TRAVERSE_PATH: Accessed index [{part}] at {current_path_str}")
                    else:
                        if self.resolution_debug_mode:
                            logger.debug(f"TRAVERSE_PATH: Index {part} out of bounds at {current_path_str}")
                        return None
                else:
                    if self.resolution_debug_mode:
                        logger.debug(f"TRAVERSE_PATH: Cannot access index [{part}]; current is {type(current_value).__name__}")
                    return None
            
            else:
                if self.resolution_debug_mode:
                    logger.debug(f"TRAVERSE_PATH: Unknown part type {type(part)} for '{part}'")
                return None
            
            if current_value is None and i < len(path_parts) - 1:
                if self.resolution_debug_mode:
                    logger.debug(f"TRAVERSE_PATH: Hit None at '{current_path_str}'")
                return None
        
        if self.resolution_debug_mode:
            logger.debug(f"TRAVERSE_PATH: Successfully traversed. Final type: {type(current_value).__name__}")
        
        return current_value
    
    # ==================== UTILITY METHODS ====================
    
    def set_breakpoint(self, node_name: str):
        """Set a breakpoint at a specific node for debugging."""
        self.breakpoints.add(node_name)
        logger.debug(f"Breakpoint set at node: {node_name}")
    
    def remove_breakpoint(self, node_name: str):
        """Remove a breakpoint."""
        self.breakpoints.discard(node_name)
        logger.debug(f"Breakpoint removed from node: {node_name}")
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export performance metrics for analysis."""
        return self.metrics.to_dict()
    
    def export_execution_graph(self, format: str = 'dict') -> Union[Dict, str]:
        """
        Export execution path as graph for visualization.
        
        Args:
            format: Output format ('dict', 'dot', 'mermaid')
            
        Returns:
            Graph representation in specified format
        """
        graph = {
            'nodes': [],
            'edges': []
        }
        
        for node_name in self.executed_nodes:
            status_info = self.node_execution_status.get(node_name, {})
            graph['nodes'].append({
                'id': node_name,
                'label': node_name,
                'status': status_info.get('status', 'unknown'),
                'type': self.workflow_data['nodes'][node_name].get('type', 'unknown')
            })
        
        for node_name in self.executed_nodes:
            successors = self.actfile_parser.get_node_successors(node_name) if self.actfile_parser else []
            for successor in successors:
                if successor in self.executed_nodes:
                    graph['edges'].append({
                        'from': node_name,
                        'to': successor
                    })
        
        if format == 'dict':
            return graph
        elif format == 'dot':
            return self._graph_to_dot(graph)
        elif format == 'mermaid':
            return self._graph_to_mermaid(graph)
        else:
            logger.warning(f"Unknown graph format: {format}. Returning dict.")
            return graph
    
    def _graph_to_dot(self, graph: Dict) -> str:
        """Convert graph to DOT format."""
        lines = ["digraph workflow {"]
        
        for node in graph['nodes']:
            color = {
                'success': 'green',
                'error': 'red',
                'warning': 'yellow',
                'running': 'blue',
                'pending': 'gray'
            }.get(node['status'], 'black')
            
            lines.append(f'  "{node["id"]}" [label="{node["label"]}" color={color}];')
        
        for edge in graph['edges']:
            lines.append(f'  "{edge["from"]}" -> "{edge["to"]}";')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _graph_to_mermaid(self, graph: Dict) -> str:
        """Convert graph to Mermaid format."""
        lines = ["graph TD"]
        
        for node in graph['nodes']:
            lines.append(f'  {node["id"]}["{node["label"]}"]')
        
        for edge in graph['edges']:
            lines.append(f'  {edge["from"]} --> {edge["to"]}')
        
        return "\n".join(lines)
    
    @staticmethod
    def log_safe_node_data(node_data: Any, max_depth=5, current_depth=0) -> str:
        """
        Converts data to JSON string for logging, redacting sensitive keys.
        """
        sensitive_keys = ['api_key', 'token', 'password', 'secret', 'credentials', 'auth', 
                         'apikey', 'access_key', 'secret_key']
        
        if current_depth > max_depth:
            return f"[Max Depth Exceeded: {type(node_data).__name__}]"
        
        def redact_recursive(data: Any, depth: int) -> Any:
            if depth > max_depth:
                return f"[Max Depth Exceeded: {type(data).__name__}]"
            
            if isinstance(data, dict):
                new_dict = {}
                for k, v in data.items():
                    is_sensitive_key = isinstance(k, str) and any(s in k.lower() for s in sensitive_keys)
                    if is_sensitive_key:
                        new_dict[k] = '[REDACTED]'
                    else:
                        is_sensitive_value = isinstance(v, str) and \
                                           ('bearer ' in v.lower() or 'sk_' in v or 'pk_' in v)
                        new_dict[k] = '[REDACTED]' if is_sensitive_value else redact_recursive(v, depth + 1)
                return new_dict
            elif isinstance(data, list):
                return [redact_recursive(item, depth + 1) for item in data]
            elif isinstance(data, str):
                is_sensitive_value = 'bearer ' in data.lower() or 'sk_' in data or 'pk_' in data
                return '[REDACTED]' if is_sensitive_value else data
            else:
                return data
        
        try:
            safe_data = redact_recursive(node_data, current_depth)
            return json.dumps(safe_data, indent=2, default=str, ensure_ascii=False, sort_keys=False)
        except (TypeError, OverflowError) as json_err:
            logger.debug(f"Could not JSON serialize: {json_err}")
            return f"[Non-Serializable Data: Type {type(node_data).__name__}]"
        except Exception as e:
            logger.error(f"Error creating log-safe representation: {e}", exc_info=False)
            return f"[Error Logging Data - Type: {type(node_data).__name__}]"
    
    def _snake_case(self, name: str) -> str:
        """Converts PascalCase/CamelCase to snake_case."""
        if not name:
            return ""
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        name = re.sub('([A-Z])([A-Z][a-z])', r'\1_\2', name)
        return name.lower()
    
    def _print_node_execution_results(self):
        """Prints a summary table of final node execution statuses."""
        print("\n--- Final Node Execution Status Summary ---")
        
        if not self.node_execution_status:
            print("No node statuses were recorded during execution.")
            print("-------------------------------------------\n")
            return
        
        headers = ["Node Name", "Final Status", "Message / Summary"]
        table_data = []
        
        all_node_names = set(self.workflow_data.get('nodes', {}).keys())
        all_node_names.update(self.node_execution_status.keys())
        sorted_node_names = sorted(list(all_node_names))
        
        for node_name in sorted_node_names:
            status_info = self.node_execution_status.get(node_name)
            summary = ""
            
            if status_info:
                status = status_info.get('status', 'unknown')
                message = status_info.get('message', 'N/A')
                
                if status == 'success' and (not message or message == 'Success'):
                    node_result_data = self.node_results.get(node_name, {}).get('result')
                    if node_result_data is not None:
                        summary = self.log_safe_node_data(node_result_data, max_depth=1)
                    else:
                        summary = message
                else:
                    summary = message
            else:
                status = 'skipped'
                summary = 'Node defined but not executed'
            
            display_summary = summary[:120] + ('...' if len(summary) > 120 else '')
            
            status_symbols = {
                'success': ('✓', Fore.GREEN),
                'error': ('✗', Fore.RED),
                'warning': ('!', Fore.YELLOW),
                'pending': ('○', Fore.WHITE),
                'running': ('◐', Fore.CYAN),
                'skipped': ('○', Fore.WHITE),
                'retrying': ('↻', Fore.YELLOW)
            }
            
            status_symbol, color = status_symbols.get(status, ('?', Fore.MAGENTA))
            
            table_data.append([
                node_name,
                f"{color}{status_symbol} {status.upper()}{Style.RESET_ALL}",
                display_summary
            ])
        
        try:
            table = tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[None, 15, 80])
        except NameError:
            logger.warning("Tabulate library not found. Using basic table format.")
            table = self._basic_table(table_data, headers)
        except Exception as tab_err:
            logger.error(f"Error generating results table: {tab_err}")
            table = self._basic_table(table_data, headers)
        
        print(table)
        print("-----------------------------------------------------------------------\n")
        
        # Print metrics summary
        print("--- Execution Metrics ---")
        metrics_data = [
            ["Total Nodes Executed", len(self.executed_nodes)],
            ["Total Placeholders Resolved", self.metrics.total_placeholders_resolved],
            ["Cache Hits", self.metrics.resolution_cache_hits],
            ["Cache Misses", self.metrics.resolution_cache_misses],
            ["Total Retries", sum(self.metrics.retry_counts.values())],
            ["Checkpoint Saves", self.metrics.checkpoint_saves]
        ]
        
        try:
            metrics_table = tabulate(metrics_data, headers=["Metric", "Value"], tablefmt="simple")
        except:
            metrics_table = "\n".join([f"{m[0]}: {m[1]}" for m in metrics_data])
        
        print(metrics_table)
        print("-------------------------\n")
    
    def __del__(self):
        """Cleanup resources on deletion."""
        try:
            if hasattr(self, 'executor_pool'):
                self.executor_pool.shutdown(wait=False)
        except:
            pass