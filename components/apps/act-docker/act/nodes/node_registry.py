"""
Node Registry Module for centralized management of node types.
This provides a separate module for the node registry functionality.
"""

import logging
import inspect
import importlib.util
import pkgutil
from pathlib import Path
from typing import Dict, Any, Type, List, Callable, Optional, Set, Union

logger = logging.getLogger(__name__)

# Store the singleton instance
_node_registry = None

class NodeRegistryError(Exception):
    """Raised when there's an issue with the node registry."""
    pass

class NodeRegistry:
    """
    Enhanced node registry that provides centralized registration and management
    of node classes and instances.
    """
    def __init__(self):
        self._registry: Dict[str, Type] = {}
        self._aliases: Dict[str, str] = {}  # Aliases for node types (e.g., 'http' -> 'HttpNode')
        self._instances: Dict[str, Any] = {}  # Cached instances
        self._loaded_paths: Set[str] = set()  # Track which paths have been loaded
        self._hooks: Dict[str, List[Callable]] = {
            'pre_register': [],
            'post_register': [],
            'pre_instantiate': [],
            'post_instantiate': []
        }

    def register(self, node_type: str, node_class: Type, aliases: List[str] = None) -> None:
        """
        Register a node class with the registry.
        
        Args:
            node_type: The primary name/type to register this node under
            node_class: The node class to register
            aliases: Optional list of alternative names for this node type
        """
        # Run pre-register hooks
        for hook in self._hooks['pre_register']:
            hook(node_type, node_class)
            
        # Validate that the class is a BaseNode (avoid circular imports)
        if not hasattr(node_class, 'get_schema') or not hasattr(node_class, 'execute'):
            raise NodeRegistryError(f"Cannot register {node_class.__name__}: not a valid node class")
        
        # Get schema to verify it matches the registered type
        try:
            temp_instance = node_class()
            schema = temp_instance.get_schema()
            if hasattr(schema, 'node_type') and schema.node_type != node_type:
                logger.warning(
                    f"Node class schema type '{schema.node_type}' doesn't match registered type '{node_type}'"
                )
        except Exception as e:
            logger.debug(f"Could not verify schema for node type '{node_type}': {e}")
        
        # Register the node type
        self._registry[node_type] = node_class
        logger.debug(f"Registered node type: {node_type} -> {node_class.__name__}")
        
        # Register any aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias] = node_type
                logger.debug(f"Registered alias: {alias} -> {node_type}")
                
        # Run post-register hooks
        for hook in self._hooks['post_register']:
            hook(node_type, node_class)

    def unregister(self, node_type: str) -> None:
        """
        Unregister a node type from the registry.
        
        Args:
            node_type: The node type to unregister
        """
        if node_type in self._registry:
            self._registry.pop(node_type)
            logger.debug(f"Unregistered node type: {node_type}")
            
            # Remove any instances
            if node_type in self._instances:
                self._instances.pop(node_type)
                
            # Remove any aliases pointing to this type
            aliases_to_remove = [alias for alias, target in self._aliases.items() if target == node_type]
            for alias in aliases_to_remove:
                self._aliases.pop(alias)
                logger.debug(f"Removed alias: {alias} -> {node_type}")
        else:
            logger.warning(f"Cannot unregister: node type '{node_type}' not found")

    def get_node_class(self, node_type: str) -> Optional[Type]:
        """
        Get a node class by type name or alias.
        
        Args:
            node_type: The node type or alias to look up
            
        Returns:
            The node class or None if not found
        """
        # Check if this is an alias
        if node_type in self._aliases:
            node_type = self._aliases[node_type]
            
        return self._registry.get(node_type)

    def get_node_instance(self, node_type: str, **kwargs) -> Any:
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
        for hook in self._hooks['pre_instantiate']:
            hook(node_type, kwargs)
            
        # Check if we have a cached instance with matching parameters
        cache_key = f"{node_type}:{hash(frozenset(kwargs.items() if kwargs else []))}"
        if cache_key in self._instances:
            return self._instances[cache_key]
            
        # Get the node class
        node_class = self.get_node_class(node_type)
        if not node_class:
            raise NodeRegistryError(f"Node type '{node_type}' is not registered")
            
        # Create a new instance
        instance = node_class(**kwargs)
        self._instances[cache_key] = instance
        
        # Run post-instantiate hooks
        for hook in self._hooks['post_instantiate']:
            hook(node_type, instance)
            
        return instance

    def list_node_types(self) -> List[str]:
        """Get a list of all registered node types."""
        return list(self._registry.keys())

    def list_node_aliases(self) -> Dict[str, str]:
        """Get a dictionary of all registered aliases and their target types."""
        return self._aliases.copy()

    def clear(self) -> None:
        """Clear all registered nodes and instances."""
        self._registry.clear()
        self._aliases.clear()
        self._instances.clear()
        self._loaded_paths.clear()
        logger.debug("Node registry cleared")

    def add_hook(self, hook_type: str, hook_func: Callable) -> None:
        """
        Add a hook function to be called at specific points.
        
        Args:
            hook_type: One of 'pre_register', 'post_register', 'pre_instantiate', 'post_instantiate'
            hook_func: Function to call
        """
        if hook_type not in self._hooks:
            raise NodeRegistryError(f"Unknown hook type: {hook_type}")
            
        self._hooks[hook_type].append(hook_func)
        logger.debug(f"Added {hook_type} hook: {hook_func.__name__}")

    def load_nodes_from_directory(self, directory_path: str, recursive: bool = True) -> int:
        """
        Dynamically load and register node classes from Python files in a directory.
        
        Args:
            directory_path: Path to directory containing node modules
            recursive: Whether to recursively search subdirectories
            
        Returns:
            Number of node classes registered
        """
        # Skip if this path has already been loaded
        if directory_path in self._loaded_paths:
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
                pkg_count = self.load_nodes_from_directory(str(pkg_path), recursive)
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
                    # Skip if it doesn't have the required node methods
                    if not hasattr(item, 'get_schema') or not hasattr(item, 'execute'):
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
                        if node_type in self._registry and self._registry[node_type] is item:
                            continue
                            
                        self.register(node_type, item)
                        count += 1
                    else:
                        logger.warning(f"Could not determine node type for class: {item_name}")
            
            except Exception as e:
                logger.debug(f"Error loading module {name} from {module_path}: {e}")
                
        # Mark this directory as loaded
        self._loaded_paths.add(directory_path)
        
        logger.debug(f"Loaded {count} node classes from {directory_path}")
        return count

    def get_node_info(self, node_type: str) -> Dict[str, Any]:
        """
        Get detailed information about a registered node type.
        
        Args:
            node_type: The node type to get info for
            
        Returns:
            Dictionary with node information
        """
        node_class = self.get_node_class(node_type)
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
            schema_dict = schema.dict() if hasattr(schema, 'dict') else {"error": "Schema not serializable"}
            
            return {
                "type": node_type,
                "class_name": node_class.__name__,
                "source_file": source_file,
                "docstring": docstring,
                "schema": schema_dict,
                "is_abstract": inspect.isabstract(node_class),
                "aliases": [alias for alias, target in self._aliases.items() if target == node_type]
            }
        except Exception as e:
            logger.error(f"Error getting info for node type '{node_type}': {e}")
            return {
                "type": node_type,
                "class_name": node_class.__name__,
                "error": str(e)
            }

def get_registry() -> NodeRegistry:
    """Get the singleton NodeRegistry instance."""
    global _node_registry
    if _node_registry is None:
        _node_registry = NodeRegistry()
    return _node_registry

# Make registry functions accessible at module level
def register(node_type: str, node_class: Type, aliases: List[str] = None) -> None:
    """Register a node class with the registry."""
    get_registry().register(node_type, node_class, aliases)

def unregister(node_type: str) -> None:
    """Unregister a node type from the registry."""
    get_registry().unregister(node_type)

def get_node_class(node_type: str) -> Optional[Type]:
    """Get a node class by type name or alias."""
    return get_registry().get_node_class(node_type)

def get_node_instance(node_type: str, **kwargs) -> Any:
    """Get a node instance by type name, creating it if needed."""
    return get_registry().get_node_instance(node_type, **kwargs)

def list_node_types() -> List[str]:
    """Get a list of all registered node types."""
    return get_registry().list_node_types()

def list_node_aliases() -> Dict[str, str]:
    """Get a dictionary of all registered aliases and their target types."""
    return get_registry().list_node_aliases()

def clear() -> None:
    """Clear all registered nodes and instances."""
    get_registry().clear()

def add_hook(hook_type: str, hook_func: Callable) -> None:
    """Add a hook function to be called at specific points."""
    get_registry().add_hook(hook_type, hook_func)

def load_nodes_from_directory(directory_path: str, recursive: bool = True) -> int:
    """Dynamically load and register node classes from Python files in a directory."""
    return get_registry().load_nodes_from_directory(directory_path, recursive)

def get_node_info(node_type: str) -> Dict[str, Any]:
    """Get detailed information about a registered node type."""
    return get_registry().get_node_info(node_type)

def initialize(nodes_directory: str = None) -> None:
    """
    Initialize the node registry, optionally loading nodes from a directory.
    
    Args:
        nodes_directory: Optional directory to load nodes from
    """
    # Load nodes from directory if specified
    if nodes_directory:
        load_nodes_from_directory(nodes_directory)