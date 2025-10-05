import os
import json
import logging
import re
import asyncio
import ssl
import certifi
import inspect
from typing import Dict, Any, Optional, List, Type, Callable, Union, Set
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# -------------------------
# Custom Exceptions
# -------------------------
class NodeError(Exception):
    """Base exception for node errors."""
    pass

class NodeValidationError(NodeError):
    """Raised when node validation fails."""
    pass

class NodeExecutionError(NodeError):
    """Raised when node execution fails."""
    pass

class NodeRegistryError(NodeError):
    """Raised when there's an issue with the node registry."""
    pass

# -------------------------
# Enum & Models for Schema
# -------------------------
class NodeParameterType(str, Enum):
    """Enum defining possible parameter types for node inputs."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    SECRET = "secret"
    ANY = "any"  # Added ANY type for flexible typing

class NodeParameter(BaseModel):
    """Defines a single parameter for a node."""
    name: str
    type: NodeParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    operations: Optional[List[str]] = None  # Add this line to support operation-specific parameters



    @validator('default')
    def validate_default_value(cls, v, values):
        if v is not None:
            param_type = values.get('type')
            if param_type == NodeParameterType.STRING and not isinstance(v, str):
                raise ValueError("Default value must be a string")
            elif param_type == NodeParameterType.NUMBER and not isinstance(v, (int, float)):
                raise ValueError("Default value must be a number")
            elif param_type == NodeParameterType.BOOLEAN and not isinstance(v, bool):
                raise ValueError("Default value must be a boolean")
        return v

class NodeSchema(BaseModel):
    """Base schema definition for a node."""
    node_type: str
    version: str
    description: str
    parameters: List[NodeParameter]
    outputs: Dict[str, NodeParameterType]
    children: Optional[List["NodeSchema"]] = None  # For nested/composite nodes
    tags: Optional[List[str]] = None  # For categorizing nodes
    author: Optional[str] = None  # Node author/creator
    documentation_url: Optional[str] = None  # Link to additional documentation

    class Config:
        extra = "allow"  # Allow extra fields for future extension

# Update forward references for nested schema
NodeSchema.update_forward_refs()

# -------------------------
# Node Registry (Enhanced)
# -------------------------
class NodeRegistry:
    """
    Enhanced node registry that provides centralized registration and management
    of node classes and instances.
    """
    _registry: Dict[str, Type['BaseNode']] = {}
    _aliases: Dict[str, str] = {}  # Aliases for node types (e.g., 'http' -> 'HttpNode')
    _instances: Dict[str, 'BaseNode'] = {}  # Cached instances
    _loaded_paths: Set[str] = set()  # Track which paths have been loaded
    _hooks: Dict[str, List[Callable]] = {
        'pre_register': [],
        'post_register': [],
        'pre_instantiate': [],
        'post_instantiate': []
    }

    @classmethod
    def register(cls, node_type: str, node_class: Type['BaseNode'], aliases: List[str] = None) -> None:
        """
        Register a node class with the registry.
        
        Args:
            node_type: The primary name/type to register this node under
            node_class: The node class to register
            aliases: Optional list of alternative names for this node type
        """
        # Run pre-register hooks
        for hook in cls._hooks['pre_register']:
            hook(node_type, node_class)
            
        # Validate that the class is a subclass of BaseNode
        if not issubclass(node_class, BaseNode):
            raise NodeRegistryError(f"Cannot register {node_class.__name__}: not a subclass of BaseNode")
        
        # Get schema to verify it matches the registered type
        try:
            temp_instance = node_class()
            schema = temp_instance.get_schema()
            if schema.node_type != node_type:
                logger.warning(
                    f"Node class schema type '{schema.node_type}' doesn't match registered type '{node_type}'"
                )
        except Exception as e:
            logger.debug(f"Could not verify schema for node type '{node_type}': {e}")
        
        # Register the node type
        cls._registry[node_type] = node_class
        logger.debug(f"Registered node type: {node_type} -> {node_class.__name__}")

        # Register any aliases
        if aliases:
            for alias in aliases:
                cls._aliases[alias] = node_type
                logger.debug(f"Registered alias: {alias} -> {node_type}")
                
        # Run post-register hooks
        for hook in cls._hooks['post_register']:
            hook(node_type, node_class)

    @classmethod
    def unregister(cls, node_type: str) -> None:
        """
        Unregister a node type from the registry.
        
        Args:
            node_type: The node type to unregister
        """
        if node_type in cls._registry:
            cls._registry.pop(node_type)
            logger.info(f"Unregistered node type: {node_type}")
            
            # Remove any instances
            if node_type in cls._instances:
                cls._instances.pop(node_type)
                
            # Remove any aliases pointing to this type
            aliases_to_remove = [alias for alias, target in cls._aliases.items() if target == node_type]
            for alias in aliases_to_remove:
                cls._aliases.pop(alias)
                logger.info(f"Removed alias: {alias} -> {node_type}")
        else:
            logger.warning(f"Cannot unregister: node type '{node_type}' not found")

    @classmethod
    def get_node_class(cls, node_type: str) -> Optional[Type['BaseNode']]:
        """
        Get a node class by type name or alias.
        
        Args:
            node_type: The node type or alias to look up
            
        Returns:
            The node class or None if not found
        """
        # Check if this is an alias
        if node_type in cls._aliases:
            node_type = cls._aliases[node_type]
            
        return cls._registry.get(node_type)

    @classmethod
    def get_node_instance(cls, node_type: str, **kwargs) -> 'BaseNode':
        """
        Get a node instance by type name, creating it if needed.
        
        Args:
            node_type: The node type or alias to instantiate
            **kwargs: Arguments to pass to the node constructor
            
        Returns:
            A node instance
            
        Raises:
            NodeRegistryError: If the node type is not registered
        """
        # Run pre-instantiate hooks
        for hook in cls._hooks['pre_instantiate']:
            hook(node_type, kwargs)
            
        # Check if we have a cached instance with matching parameters
        cache_key = f"{node_type}:{hash(frozenset(kwargs.items()))}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
            
        # Get the node class
        node_class = cls.get_node_class(node_type)
        if not node_class:
            raise NodeRegistryError(f"Node type '{node_type}' is not registered")
            
        # Create a new instance
        instance = node_class(**kwargs)
        cls._instances[cache_key] = instance
        
        # Run post-instantiate hooks
        for hook in cls._hooks['post_instantiate']:
            hook(node_type, instance)
            
        return instance

    @classmethod
    def list_node_types(cls) -> List[str]:
        """Get a list of all registered node types."""
        return list(cls._registry.keys())

    @classmethod
    def list_node_aliases(cls) -> Dict[str, str]:
        """Get a dictionary of all registered aliases and their target types."""
        return cls._aliases.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered nodes and instances."""
        cls._registry.clear()
        cls._aliases.clear()
        cls._instances.clear()
        cls._loaded_paths.clear()
        logger.info("Node registry cleared")

    @classmethod
    def add_hook(cls, hook_type: str, hook_func: Callable) -> None:
        """
        Add a hook function to be called at specific points.
        
        Args:
            hook_type: One of 'pre_register', 'post_register', 'pre_instantiate', 'post_instantiate'
            hook_func: Function to call
        """
        if hook_type not in cls._hooks:
            raise NodeRegistryError(f"Unknown hook type: {hook_type}")
            
        cls._hooks[hook_type].append(hook_func)
        logger.debug(f"Added {hook_type} hook: {hook_func.__name__}")

    @classmethod
    def load_nodes_from_directory(cls, directory_path: str, recursive: bool = True) -> int:
        """
        Dynamically load and register node classes from Python files in a directory.
        
        Args:
            directory_path: Path to directory containing node modules
            recursive: Whether to recursively search subdirectories
            
        Returns:
            Number of node classes registered
        """
        import importlib.util
        import pkgutil
        from pathlib import Path
        
        # Skip if this path has already been loaded
        if directory_path in cls._loaded_paths:
            logger.debug(f"Directory already loaded: {directory_path}")
            return 0
            
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Directory does not exist: {directory_path}")
            return 0
            
        count = 0
        
        # Find all Python files in the directory
        for finder, name, is_pkg in pkgutil.iter_modules([str(directory)]):
            # Skip if it's a package and we're not doing recursive loading
            if is_pkg and not recursive:
                continue
                
            # Handle packages if recursive is True
            if is_pkg and recursive:
                pkg_path = directory / name
                pkg_count = cls.load_nodes_from_directory(str(pkg_path), recursive)
                count += pkg_count
                continue
                
            # Load regular Python files
            module_path = directory / f"{name}.py"
            if not module_path.exists():
                continue
                
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(name, module_path)
                if spec is None or spec.loader is None:
                    logger.warning(f"Could not load spec for module: {module_path}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find BaseNode subclasses in the module
                for item_name, item in inspect.getmembers(module, inspect.isclass):
                    # Skip if it's not a BaseNode subclass or is BaseNode itself
                    if not issubclass(item, BaseNode) or item is BaseNode:
                        continue
                        
                    # Try to determine the node type from the class name or schema
                    node_type = None
                    try:
                        # Create an instance to get the schema
                        temp_instance = item()
                        schema = temp_instance.get_schema()
                        node_type = schema.node_type
                    except Exception:
                        # Fall back to inferring from the class name
                        if item_name.endswith('Node'):
                            node_type = item_name[:-4].lower()  # Remove 'Node' suffix
                        else:
                            node_type = item_name.lower()
                            
                    # Register the node type
                    if node_type:
                        # Skip if already registered with same class
                        if node_type in cls._registry and cls._registry[node_type] is item:
                            continue
                            
                        cls.register(node_type, item)
                        count += 1
                    else:
                        logger.warning(f"Could not determine node type for class: {item_name}")
            
            except Exception as e:
                logger.debug(f"Error loading module {name} from {module_path}: {e}")
                
        # Mark this directory as loaded
        cls._loaded_paths.add(directory_path)
        
        logger.info(f"Loaded {count} node classes from {directory_path}")
        return count

    @classmethod
    def get_node_info(cls, node_type: str) -> Dict[str, Any]:
        """
        Get detailed information about a registered node type.
        
        Args:
            node_type: The node type to get info for
            
        Returns:
            Dictionary with node information
        """
        node_class = cls.get_node_class(node_type)
        if not node_class:
            raise NodeRegistryError(f"Node type '{node_type}' is not registered")
            
        try:
            # Create a temporary instance to get schema
            temp_instance = node_class()
            schema = temp_instance.get_schema()
            
            # Get source file and docstring
            source_file = inspect.getfile(node_class)
            docstring = inspect.getdoc(node_class) or ""
            
            # Convert schema to dict for output
            schema_dict = schema.dict()
            
            return {
                "type": node_type,
                "class_name": node_class.__name__,
                "source_file": source_file,
                "docstring": docstring,
                "schema": schema_dict,
                "is_abstract": inspect.isabstract(node_class),
                "aliases": [alias for alias, target in cls._aliases.items() if target == node_type]
            }
        except Exception as e:
            logger.error(f"Error getting info for node type '{node_type}': {e}")
            return {
                "type": node_type,
                "class_name": node_class.__name__,
                "error": str(e)
            }

# -------------------------
# Base Node Definition
# -------------------------
class BaseNode(ABC):
    """Enhanced base node with schema support and extensibility."""
    
    def __init__(self, sandbox_timeout: Optional[int] = None, dependencies: Optional[Dict[str, Any]] = None):
        logger.debug(f"Initializing {self.__class__.__name__}")
        self.sandbox_timeout = sandbox_timeout
        self.dependencies = dependencies or {}
        self._schema = self.get_schema()
        self._execution_manager = None
        self.children: List[BaseNode] = []  # For composite nodes
        self.ssl_context = self._create_ssl_context()  # Initialize SSL context using certifi

    def _create_ssl_context(self):
        """
        Creates an SSL context that uses certifi's CA bundle.
        This ensures all nodes use valid CA certificates.
        """
        context = ssl.create_default_context()
        context.load_verify_locations(certifi.where())
        return context

    @abstractmethod
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for this node."""
        pass

    def set_execution_manager(self, execution_manager: Any) -> None:
        """Set the execution manager for this node."""
        self._execution_manager = execution_manager
        logger.debug(f"Set execution manager for {self.__class__.__name__}")

    def validate_schema(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against the node's schema.
        
        Args:
            node_data: The input data to validate
            
        Returns:
            Validated and processed data dictionary
            
        Raises:
            NodeValidationError: If validation fails
        """
        validated_data = {}
        params = node_data.get("params", {})

        try:
            for param in self._schema.parameters:
                value = params.get(param.name)

                # Handle required parameters
                if param.required and value is None:
                    raise NodeValidationError(f"Missing required parameter: {param.name}")

                # Apply default value if needed
                if value is None and param.default is not None:
                    value = param.default

                # Skip if no value and not required
                if value is None and not param.required:
                    continue

                # Type validation
                self._validate_type(param, value)

                # Range validation for numbers
                if param.type == NodeParameterType.NUMBER:
                    self._validate_range(param, value)

                # Enum validation
                if param.enum is not None and value not in param.enum:
                    raise NodeValidationError(f"Parameter {param.name} must be one of: {param.enum}")

                # Pattern validation for strings
                if param.pattern is not None and param.type == NodeParameterType.STRING:
                    if not re.match(param.pattern, value):
                        raise NodeValidationError(f"Parameter {param.name} does not match required pattern")

                validated_data[param.name] = value

            # Allow node-specific custom validation
            custom_data = self.validate_custom(node_data)
            validated_data.update(custom_data)
            return validated_data

        except Exception as e:
            raise NodeValidationError(f"Schema validation error: {str(e)}")

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node-specific custom validation. Override this in subclasses if needed.
        
        Args:
            node_data: The node data to validate
            
        Returns:
            Any additional validated data
        """
        return {}

    def _validate_type(self, param: NodeParameter, value: Any) -> None:
        """
        Validate parameter type.
        
        Args:
            param: The parameter definition
            value: The value to validate
            
        Raises:
            NodeValidationError: If validation fails
        """
        if param.type == NodeParameterType.ANY:
            # ANY type accepts any value, no validation needed
            return
        elif param.type == NodeParameterType.STRING and not isinstance(value, str):
            raise NodeValidationError(f"Parameter {param.name} must be a string")
        elif param.type == NodeParameterType.NUMBER and not isinstance(value, (int, float)):
            raise NodeValidationError(f"Parameter {param.name} must be a number")
        elif param.type == NodeParameterType.BOOLEAN and not isinstance(value, bool):
            raise NodeValidationError(f"Parameter {param.name} must be a boolean")
        elif param.type == NodeParameterType.ARRAY and not isinstance(value, list):
            raise NodeValidationError(f"Parameter {param.name} must be an array")
        elif param.type == NodeParameterType.OBJECT and not isinstance(value, dict):
            raise NodeValidationError(f"Parameter {param.name} must be an object")
    
    def _validate_range(self, param: NodeParameter, value: Any) -> None:
        """
        Validate numeric range.
        
        Args:
            param: The parameter definition
            value: The value to validate
            
        Raises:
            NodeValidationError: If validation fails
        """
        if param.min_value is not None and value < param.min_value:
            raise NodeValidationError(f"Parameter {param.name} must be >= {param.min_value}")
        if param.max_value is not None and value > param.max_value:
            raise NodeValidationError(f"Parameter {param.name} must be <= {param.max_value}")

    def validate_params(self, required_params: List[str], node_data: Dict[str, Any]) -> bool:
        """
        Legacy parameter validation method for backward compatibility.
        
        Args:
            required_params: List of required parameter names
            node_data: The node data to validate
            
        Returns:
            True if validation passes
            
        Raises:
            NodeValidationError: If validation fails
        """
        missing_params = [param for param in required_params if param not in node_data.get("params", {})]
        if missing_params:
            error_message = f"Missing required parameters: {', '.join(missing_params)}"
            logger.error(error_message)
            raise NodeValidationError(error_message)
        return True

    def resolve_placeholders(self, text: str, node_data: Dict[str, Any]) -> str:
        """
        Resolve placeholders in a string using the node_data context.
        
        Args:
            text: The text containing placeholders
            node_data: The node data context
            
        Returns:
            Text with placeholders resolved
        """
        if not isinstance(text, str):
            return text
            
        pattern = re.compile(r"\{\{(.*?)\}\}")
        matches = pattern.findall(text)

        for match in matches:
            parts = match.split('.')
            value = self.fetch_value(parts, node_data)
            if value is not None:
                text = text.replace(f"{{{{{match}}}}}", str(value))
        return text

    def resolve_all_placeholders(self, data: Any, node_data: Dict[str, Any]) -> Any:
        """
        Recursively resolve all placeholders in a data structure.
        
        Args:
            data: The data structure to process
            node_data: The node data context
            
        Returns:
            Data with all placeholders resolved
        """
        if isinstance(data, str):
            return self.resolve_placeholders(data, node_data)
        elif isinstance(data, dict):
            return {k: self.resolve_all_placeholders(v, node_data) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.resolve_all_placeholders(item, node_data) for item in data]
        return data

    def fetch_value(self, path_parts: List[str], node_data: Dict[str, Any]) -> Any:
        """
        Fetch a value from the node_data using a list of keys.
        
        Args:
            path_parts: List of keys forming a path to the value
            node_data: The node data context
            
        Returns:
            The value at the specified path, or None if not found
        """
        value = node_data
        try:
            for part in path_parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        except Exception as e:
            logger.error(f"Error fetching value for path {'.'.join(path_parts)}: {e}")
            return None

    def extract_text(self, input_text: Any) -> str:
        """
        Extract actual text from input, handling JSON and other formats.
        
        Args:
            input_text: The input to extract text from
            
        Returns:
            Extracted text as a string
        """
        try:
            if isinstance(input_text, str):
                parsed = json.loads(input_text)
                if isinstance(parsed, dict):
                    return parsed.get('value', input_text)
            elif isinstance(input_text, dict):
                return input_text.get('value', str(input_text))
        except (json.JSONDecodeError, ValueError):
            pass
        return str(input_text)

    def log_safe_data(self, data: Any) -> Any:
        """
        Redact sensitive information from logs.
        
        Args:
            data: Data to make safe for logging
            
        Returns:
            Data with sensitive information redacted
        """
        if isinstance(data, dict):
            return {
                k: ('[REDACTED]' if any(sensitive in k.lower() for sensitive in ['key', 'password', 'token', 'secret']) else 
                    self.log_safe_data(v)) 
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self.log_safe_data(item) for item in data]
        return data

    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle an error and return a formatted error response.
        
        Args:
            error: The exception that occurred
            context: Optional context information
            
        Returns:
            Error response dictionary
        """
        error_message = f"Error in {context or self.__class__.__name__}: {str(error)}"
        logger.error(error_message)
        return {
            "status": "error", 
            "message": error_message,
            "error_type": error.__class__.__name__
        }

    def add_child(self, child: "BaseNode") -> None:
        """
        Add a child node for composite execution.
        
        Args:
            child: The child node to add
        """
        self.children.append(child)
        logger.debug(f"Added child {child.__class__.__name__} to {self.__class__.__name__}")

    async def execute_children(self, node_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute all child nodes asynchronously and return their results.
        
        Args:
            node_data: The node data to pass to children
            
        Returns:
            List of execution results from all children
        """
        results = []
        for child in self.children:
            try:
                result = await child.execute(node_data)
                results.append(result)
            except Exception as e:
                results.append(self.handle_error(e, f"Child {child.__class__.__name__}"))
        return results

    @abstractmethod
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node's main functionality asynchronously.
        
        Args:
            node_data: The node data for execution
            
        Returns:
            Execution result dictionary
        """
        pass
    
    def execute_sync(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node synchronously by running the async execute method in a new event loop.
        
        Args:
            node_data: The node data for execution
            
        Returns:
            Execution result dictionary
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.execute(node_data))
        finally:
            loop.close()

# -------------------------
# Example Node Implementation
# -------------------------
class ExampleNode(BaseNode):
    """Example node implementation for testing and reference."""
    
    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            node_type="example",
            version="1.0.0",
            description="Example node that processes text with placeholders",
            parameters=[
                NodeParameter(
                    name="example_param",
                    type=NodeParameterType.STRING,
                    description="Input text with optional placeholders",
                    required=True
                ),
                NodeParameter(
                    name="transform",
                    type=NodeParameterType.STRING,
                    description="Optional transformation to apply (upper, lower, title)",
                    required=False,
                    enum=["upper", "lower", "title"]
                )
            ],
            outputs={
                "processed_text": NodeParameterType.STRING,
                "metadata": NodeParameterType.OBJECT
            },
            tags=["example", "text", "utility"],
            author="System"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Extract and process input text
            input_text = self.extract_text(validated_data["example_param"])
            logger.info(f"Processing input: {input_text}")

            # Resolve placeholders using the full node_data context
            resolved_text = self.resolve_placeholders(input_text, node_data)
            logger.info(f"Resolved text: {resolved_text}")
            
            # Apply transformation if specified
            transform = validated_data.get("transform")
            if transform:
                if transform == "upper":
                    resolved_text = resolved_text.upper()
                elif transform == "lower":
                    resolved_text = resolved_text.lower()
                elif transform == "title":
                    resolved_text = resolved_text.title()
            
            # If there are child nodes, execute them asynchronously
            children_results = await self.execute_children(node_data) if self.children else []

            # Return success result along with any children outputs
            return {
                "status": "success",
                "result": {
                    "processed_text": resolved_text,
                    "metadata": {
                        "original_length": len(input_text),
                        "processed_length": len(resolved_text),
                        "timestamp": datetime.now().isoformat(),
                        "transform_applied": transform
                    },
                    "children_results": children_results
                }
            }
        except Exception as e:
            return self.handle_error(e, context="ExampleNode execution")

# -------------------------
# Helper Functions
# -------------------------
def initialize_registry(nodes_directory: str = None) -> None:
    """
    Initialize the node registry, optionally loading nodes from a directory.
    
    Args:
        nodes_directory: Optional directory to load nodes from
    """
    # Register built-in nodes
    NodeRegistry.register("example", ExampleNode, aliases=["sample"])
    
    # Load nodes from directory if specified
    if nodes_directory:
        NodeRegistry.load_nodes_from_directory(nodes_directory)

def get_node_class(node_type: str) -> Optional[Type[BaseNode]]:
    """
    Get a node class by type. This is a convenience function that wraps NodeRegistry.get_node_class.
    
    Args:
        node_type: The node type to look up
        
    Returns:
        The node class or None if not found
    """
    return NodeRegistry.get_node_class(node_type)

def create_node(node_type: str, **kwargs) -> BaseNode:
    """
    Create a node instance. This is a convenience function that wraps NodeRegistry.get_node_instance.
    
    Args:
        node_type: The node type to instantiate
        **kwargs: Arguments to pass to the node constructor
        
    Returns:
        A node instance
    """
    return NodeRegistry.get_node_instance(node_type, **kwargs)

# Ensure ExampleNode is registered
NodeRegistry.register("example", ExampleNode, aliases=["sample"])
def get_all_node_parameters_json(pretty_print: bool = False) -> str:
    """
    Fetch all node data parameters from registered nodes and return as JSON.
    
    Args:
        pretty_print: Whether to format the JSON with indentation for readability
        
    Returns:
        JSON string containing parameter information for all registered nodes
    """
    result = {}
    
    # Get all registered node types
    node_types = NodeRegistry.list_node_types()
    
    for node_type in node_types:
        try:
            # Get node class and create a temporary instance to access schema
            node_class = NodeRegistry.get_node_class(node_type)
            if not node_class:
                continue
                
            # Skip abstract classes
            if inspect.isabstract(node_class):
                continue
                
            temp_instance = node_class()
            schema = temp_instance.get_schema()
            
            # Extract parameter information
            parameters = []
            for param in schema.parameters:
                param_info = {
                    "name": param.name,
                    "type": str(param.type.value),
                    "description": param.description,
                    "required": param.required,
                }
                
                # Add optional fields if they exist
                if param.default is not None:
                    param_info["default"] = param.default
                if param.enum is not None:
                    param_info["enum"] = param.enum
                if param.min_value is not None:
                    param_info["min_value"] = param.min_value
                if param.max_value is not None:
                    param_info["max_value"] = param.max_value
                if param.pattern is not None:
                    param_info["pattern"] = param.pattern
                    
                parameters.append(param_info)
            
            # Add outputs information
            outputs = {key: str(value.value) for key, value in schema.outputs.items()}
            
            # Create the node entry
            result[node_type] = {
                "version": schema.version,
                "description": schema.description,
                "parameters": parameters,
                "outputs": outputs
            }
            
            # Add optional fields if they exist
            if schema.tags:
                result[node_type]["tags"] = schema.tags
            if schema.author:
                result[node_type]["author"] = schema.author
            if schema.documentation_url:
                result[node_type]["documentation_url"] = schema.documentation_url
                
        except Exception as e:
            # Log error but continue processing other nodes
            logger.error(f"Error fetching parameters for node type '{node_type}': {e}")
            result[node_type] = {"error": str(e)}
    
    # Convert to JSON
    indent = 2 if pretty_print else None
    return json.dumps(result, indent=indent)

def save_node_parameters_to_file(output_path: str, pretty_print: bool = True) -> None:
    """
    Save all node parameters as JSON to a file.
    
    Args:
        output_path: Path to save the JSON file
        pretty_print: Whether to format the JSON with indentation for readability
    """
    try:
        # Get the JSON data
        json_data = get_all_node_parameters_json(pretty_print)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(json_data)
            
        logger.info(f"Successfully saved node parameters to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving node parameters to file: {e}")
        raise


# -------------------------
# Main Block for Testing
# -------------------------
if __name__ == "__main__":
    from datetime import datetime
    import asyncio
    
    async def main():
        # Initialize the registry
        initialize_registry()
        
        # Create an example node via the registry
        example_node = NodeRegistry.get_node_instance("example")
        
        # Print the node schema (formatted as JSON)
        print("Node Schema:")
        print(json.dumps(example_node.get_schema().dict(), indent=2))
        
        # Test execution with sample data
        test_data = {
            "params": {
                "example_param": "Hello, {{input.user.name}}!",
                "transform": "upper"
            },
            "input": {
                "user": {
                    "name": "Taj"
                }
            }
        }
        
        print("\nExecution Result:")
        result = await example_node.execute(test_data)
        print(json.dumps(result, indent=2))
        
        # Test the registry functions
        print("\nRegistry Information:")
        print(f"Registered Node Types: {NodeRegistry.list_node_types()}")
        print(f"Registered Aliases: {NodeRegistry.list_node_aliases()}")
        
        # Get detailed info about the example node
        node_info = NodeRegistry.get_node_info("example")
        print("\nNode Information:")
        print(json.dumps(node_info, indent=2))
        
        # Test child nodes
        child_node = ExampleNode()
        child_node.add_child(ExampleNode())
        
        child_test_data = {
            "params": {
                "example_param": "This has a {{input.property}}",
                "transform": "title"
            },
            "input": {
                "property": "child node"
            }
        }
        
        print("\nChild Node Execution:")
        child_result = await child_node.execute(child_test_data)
        print(json.dumps(child_result, indent=2))
        
        # Test loading nodes from a directory
        print("\nLoading Nodes from Directory:")
        try:
            # This is just for demonstration - replace with your actual nodes directory
            nodes_dir = "./nodes"
            count = NodeRegistry.load_nodes_from_directory(nodes_dir)
            print(f"Loaded {count} nodes from {nodes_dir}")
            print(f"Updated Registry: {NodeRegistry.list_node_types()}")
        except Exception as e:
            print(f"Error loading nodes from directory: {e}")
    
    # Run the async main function
    asyncio.run(main())

    initialize_registry()
    
    # Print to console
    print(get_all_node_parameters_json(pretty_print=True))
    
    # Save to file
    save_node_parameters_to_file("node_parameters.json")