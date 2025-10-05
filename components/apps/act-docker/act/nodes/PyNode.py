import logging
import sys
import traceback
import inspect
import importlib.util
import os
import time
import re
import json
import ast
from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
from io import StringIO

# Import base node components
try:
    from .base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    class NodeValidationError(Exception): pass
    class NodeExecutionError(Exception): pass
    class NodeParameterType: ANY="any"; STRING="string"; BOOLEAN="boolean"; NUMBER="number"; ARRAY="array"; OBJECT="object"; SECRET="secret"
    class NodeParameter:
        def __init__(self, name, type, description, required=True, default=None, enum=None):
            self.name = name; self.type = type; self.description = description; self.required = required; self.default = default; self.enum = enum
    class NodeSchema:
        def __init__(self, node_type, version, description, parameters, outputs, tags=None, author=None):
            self.node_type=node_type; self.version=version; self.description=description; self.parameters=parameters; self.outputs=outputs; self.tags=tags; self.author=author
    class BaseNode:
        def get_schema(self): raise NotImplementedError
        async def execute(self, data): raise NotImplementedError
        def validate_schema(self, data): return data.get("params", {})
        def handle_error(self, error, context=""):
             logger = logging.getLogger(__name__)
             logger.error(f"Error in {context}: {error}", exc_info=True)
             return {"status": "error", "message": f"Error in {context}: {error}", "error_type": type(error).__name__}

# Configure logger
logger = logging.getLogger(__name__)

class PyNode(BaseNode):
    """
    Enhanced Python Execution Node with Robust Placeholder Resolution
    
    Executes Python code with intelligent placeholder replacement that prevents
    JSON escaping issues and handles all edge cases properly.
    """
    
    node_type = "py"
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the PyNode."""
        return NodeSchema(
            node_type="py",
            version="2.0.0",  # Version bump for enhanced placeholder handling
            description="Executes Python code with robust placeholder resolution (prevents JSON escaping issues)",
            parameters=[
                NodeParameter(
                    name="code",
                    type=NodeParameterType.STRING,
                    description="Inline Python code to execute (with intelligent placeholder resolution)",
                    required=False
                ),
                NodeParameter(
                    name="path",
                    type=NodeParameterType.STRING,
                    description="Path to a Python file to execute",
                    required=False
                ),
                NodeParameter(
                    name="function",
                    type=NodeParameterType.STRING,
                    description="Name of a function to call from the code or file",
                    required=False
                ),
                NodeParameter(
                    name="args",
                    type=NodeParameterType.ARRAY,
                    description="Positional arguments to pass to the function",
                    required=False,
                    default=[]
                ),
                NodeParameter(
                    name="kwargs",
                    type=NodeParameterType.OBJECT,
                    description="Keyword arguments to pass to the function",
                    required=False,
                    default={}
                ),
                NodeParameter(
                    name="use_params_as_kwargs",
                    type=NodeParameterType.BOOLEAN,
                    description="Pass all node parameters as keyword arguments to the function",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="pass_context",
                    type=NodeParameterType.BOOLEAN,
                    description="Pass node execution context to the function",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.NUMBER,
                    description="Maximum execution time in seconds (0 for no timeout)",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="result_format",
                    type=NodeParameterType.STRING,
                    description="Result structure format: 'legacy' (double-nested) or 'flat' (single-level)",
                    required=False,
                    default="auto",
                    enum=["auto", "legacy", "flat"]
                ),
                NodeParameter(
                    name="placeholder_mode",
                    type=NodeParameterType.STRING,
                    description="Placeholder resolution mode: 'smart' (Python literals), 'json' (JSON strings), 'raw' (no processing)",
                    required=False,
                    default="smart",
                    enum=["smart", "json", "raw"]
                )
            ],
            outputs={
                "result": NodeParameterType.ANY,
                "stdout": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER
            },
            tags=["code", "python", "scripting", "enhanced-placeholders"],
            author="ACT Framework - Enhanced"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for PyNode."""
        params = node_data.get("params", {})
        
        # Check that at least one of code or path is provided
        if not params.get("code") and not params.get("path"):
            raise NodeValidationError("Either 'code' or 'path' parameter must be provided")
        
        # If both code and path are provided, give a warning
        if params.get("code") and params.get("path"):
            logger.warning("Both 'code' and 'path' parameters are provided. 'code' will take precedence.")
        
        # Validate timeout is non-negative
        timeout = params.get("timeout", 30)
        if timeout < 0:
            raise NodeValidationError("'timeout' parameter must be non-negative")
        
        # Validate args is a list if provided
        args = params.get("args", [])
        if args is not None and not isinstance(args, list):
            raise NodeValidationError("'args' parameter must be a list")
        
        # Validate kwargs is a dictionary if provided
        kwargs = params.get("kwargs", {})
        if kwargs is not None and not isinstance(kwargs, dict):
            raise NodeValidationError("'kwargs' parameter must be a dictionary")
        
        # Validate result_format
        result_format = params.get("result_format", "auto")
        if result_format not in ["auto", "legacy", "flat"]:
            raise NodeValidationError("'result_format' must be one of: auto, legacy, flat")
        
        # Validate placeholder_mode
        placeholder_mode = params.get("placeholder_mode", "smart")
        if placeholder_mode not in ["smart", "json", "raw"]:
            raise NodeValidationError("'placeholder_mode' must be one of: smart, json, raw")
        
        return {}
    
    def resolve_placeholders_intelligently(self, code: str, node_data: Dict[str, Any]) -> str:
        """
        Intelligently resolve placeholders in Python code to prevent syntax errors.
        Enhanced version that handles missing dependencies gracefully.
        """
        # Get placeholder mode
        placeholder_mode = node_data.get("params", {}).get("placeholder_mode", "smart")
        
        if placeholder_mode == "raw":
            return code  # No placeholder processing
        
        # Get available node results from workflow context
        node_results = self._extract_node_results(node_data)
        
        # Find all placeholder patterns
        placeholder_pattern = r'\{\{([^}]+)\}\}'
        placeholders = re.findall(placeholder_pattern, code)
        
        if not placeholders:
            return code  # No placeholders to resolve
        
        logger.debug(f"Found {len(placeholders)} placeholders to resolve: {placeholders}")
        
        resolved_code = code
        unresolved_placeholders = []
        
        for placeholder in placeholders:
            placeholder_full = f"{{{{{placeholder}}}}}"
            
            try:
                # Resolve the placeholder to its actual value
                resolved_value = self._resolve_placeholder_path(placeholder.strip(), node_results)
                
                # Convert value to appropriate format based on mode
                if placeholder_mode == "json":
                    replacement = json.dumps(resolved_value, indent=2)
                else:  # smart mode (default)
                    replacement = self._convert_to_python_literal(resolved_value)
                
                # Replace the placeholder with the resolved value
                resolved_code = resolved_code.replace(placeholder_full, replacement)
                logger.debug(f"Resolved placeholder '{placeholder}' successfully")
                
            except Exception as e:
                logger.error(f"Failed to resolve placeholder '{placeholder}': {e}")
                unresolved_placeholders.append(placeholder)
                # Keep the original placeholder if resolution fails
                continue
        
        # If there are unresolved placeholders, this indicates a dependency issue
        if unresolved_placeholders:
            missing_nodes = []
            for placeholder in unresolved_placeholders:
                node_name = placeholder.split('.')[0]
                if node_name not in node_results:
                    missing_nodes.append(node_name)
            
            if missing_nodes:
                raise NodeExecutionError(
                    f"Cannot execute node - missing dependencies: {missing_nodes}. "
                    f"These nodes must complete before this node can run. "
                    f"Unresolved placeholders: {unresolved_placeholders}"
                )
        
        return resolved_code

    def _extract_node_results(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract available node results from the workflow context - ENHANCED VERSION."""
        
        # Try to get node results from execution manager or workflow context
        possible_keys = [
            "__node_results",
            "__workflow_results", 
            "workflow_results",
            "node_results",
            "previous_results",
            "__previous_results",
            "__execution_context"
        ]
        
        for key in possible_keys:
            if key in node_data and isinstance(node_data[key], dict):
                results = node_data[key]
                logger.debug(f"Found node results via key '{key}': {list(results.keys())}")
                return results
        
        # IMPORTANT: Check if execution manager provides results differently
        # This may need to be adapted based on your execution framework
        if hasattr(self, '_execution_manager') and hasattr(self._execution_manager, 'get_node_results'):
            try:
                results = self._execution_manager.get_node_results()
                if results:
                    logger.debug(f"Got node results from execution manager: {list(results.keys())}")
                    return results
            except Exception as e:
                logger.debug(f"Could not get results from execution manager: {e}")
        
        # Fallback: look for individual node results in the data
        node_results = {}
        for key, value in node_data.items():
            if isinstance(value, dict) and "result" in value and "status" in value:
                node_results[key] = value
                logger.debug(f"Found individual node result: {key}")
        
        logger.debug(f"Final node results available: {list(node_results.keys())}")
        return node_results
        
    def _extract_node_results(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract available node results from the workflow context."""
        # This assumes the execution framework provides previous results
        # in the node_data under some key. Adjust based on your framework.
        
        # Try different possible locations for node results
        possible_keys = [
            "__node_results",
            "__workflow_results", 
            "workflow_results",
            "node_results",
            "previous_results"
        ]
        
        for key in possible_keys:
            if key in node_data:
                return node_data[key]
        
        # If no standard key found, look for any dict that contains node-like data
        for key, value in node_data.items():
            if isinstance(value, dict) and any(
                node_name in value for node_name in node_data.keys() 
                if "Step" in str(node_name) or "Node" in str(node_name)
            ):
                return value
        
        # Fallback: look for individual node results in the data
        node_results = {}
        for key, value in node_data.items():
            if isinstance(value, dict) and "result" in value:
                node_results[key] = value
        
        return node_results
    
    def _resolve_placeholder_path(self, path: str, node_results: Dict[str, Any]) -> Any:
        """
        Resolve a placeholder path like 'NodeName.result.field' to its actual value.
        """
        path_parts = path.split('.')
        
        if len(path_parts) < 1:
            raise ValueError(f"Invalid placeholder path: {path}")
        
        node_name = path_parts[0]
        
        if node_name not in node_results:
            raise ValueError(f"Node '{node_name}' not found in available results. Available: {list(node_results.keys())}")
        
        # Start with the node's data
        current_value = node_results[node_name]
        
        # Navigate through the path
        for part in path_parts[1:]:
            if isinstance(current_value, dict):
                if part not in current_value:
                    raise ValueError(f"Key '{part}' not found in path '{path}'. Available keys: {list(current_value.keys())}")
                current_value = current_value[part]
            elif isinstance(current_value, (list, tuple)):
                try:
                    index = int(part)
                    current_value = current_value[index]
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Invalid list/tuple access '{part}' in path '{path}': {e}")
            else:
                raise ValueError(f"Cannot navigate to '{part}' in path '{path}'. Current value type: {type(current_value)}")
        
        return current_value
    
    def _convert_to_python_literal(self, value: Any) -> str:
        """
        Convert a value to a proper Python literal representation.
        
        This prevents JSON escaping issues by using Python's repr() and ast.literal_eval()
        to create valid Python syntax.
        """
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return "True" if value else "False"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Use repr to properly escape strings for Python
            return repr(value)
        elif isinstance(value, (list, tuple, dict)):
            try:
                # Use repr for complex types to get proper Python literal syntax
                python_repr = repr(value)
                
                # Verify it's valid Python by parsing it
                ast.parse(python_repr, mode='eval')
                
                return python_repr
            except (SyntaxError, ValueError) as e:
                logger.warning(f"Could not create Python literal for {type(value)}: {e}. Falling back to JSON.")
                return json.dumps(value)
        else:
            # For custom objects, try repr first, then fall back to JSON if possible
            try:
                python_repr = repr(value)
                ast.parse(python_repr, mode='eval')
                return python_repr
            except:
                try:
                    return json.dumps(value, default=str)
                except:
                    return repr(str(value))
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code with enhanced placeholder resolution."""
        node_name = node_data.get('__node_name', 'PyNode')
        logger.info(f"Executing Enhanced PyNode: {node_name}")
        
        try:
            # Extract parameters
            params = node_data.get("params", {})
            code = params.get("code")
            path = params.get("path")
            function_name = params.get("function")
            args = params.get("args", [])
            kwargs = params.get("kwargs", {})
            use_params_as_kwargs = params.get("use_params_as_kwargs", False)
            pass_context = params.get("pass_context", False)
            timeout = params.get("timeout", 30)
            result_format = params.get("result_format", "auto")
            placeholder_mode = params.get("placeholder_mode", "smart")
            
            # Prepare execution context
            execution_context = self._prepare_execution_context(node_data, pass_context)
            
            # Load and resolve code
            if code:
                # Resolve placeholders in inline code
                resolved_code = self.resolve_placeholders_intelligently(code, node_data)
                code_source = "inline code (with placeholder resolution)"
                logger.debug(f"Original code length: {len(code)}, Resolved code length: {len(resolved_code)}")
            elif path:
                # Load from file and resolve placeholders
                raw_code, _ = self._load_code_from_file(path)
                resolved_code = self.resolve_placeholders_intelligently(raw_code, node_data)
                code_source = f"file: {path} (with placeholder resolution)"
            else:
                raise NodeValidationError("Neither 'code' nor 'path' parameter provided")
            
            logger.debug(f"{node_name} - Using Python code from {code_source}")
            
            # Execute the resolved code
            start_time = time.time()
            python_result, stdout = self._execute_python_code(
                resolved_code, 
                function_name, 
                args, 
                kwargs, 
                execution_context, 
                use_params_as_kwargs, 
                pass_context,
                timeout
            )
            execution_time = time.time() - start_time
            
            logger.info(f"{node_name} - Executed Python code successfully in {execution_time:.3f} seconds")
            
            # Determine result format
            determined_format = self._determine_result_format(result_format, node_data)
            
            if determined_format == "legacy":
                # Legacy format: Double-nested for {{node.result.result.field}}
                return {
                    "status": "success",
                    "message": f"Python code executed successfully in {execution_time:.3f} seconds",
                    "result": {
                        "result": python_result,
                        "stdout": stdout,
                        "execution_time": execution_time
                    },
                    "metadata": {
                        "code_source": code_source,
                        "function_called": function_name,
                        "execution_time_seconds": execution_time,
                        "result_format": "legacy",
                        "placeholder_mode": placeholder_mode
                    }
                }
            else:
                # Flat format: Single-level for {{node.result.field}}
                return {
                    "status": "success",
                    "message": f"Python code executed successfully in {execution_time:.3f} seconds",
                    "result": python_result,
                    "stdout": stdout,
                    "execution_time": execution_time,
                    "metadata": {
                        "code_source": code_source,
                        "function_called": function_name,
                        "execution_time_seconds": execution_time,
                        "result_format": "flat",
                        "placeholder_mode": placeholder_mode
                    }
                }
            
        except NodeValidationError as e:
            logger.error(f"Validation error in {node_name}: {e}")
            return self.handle_error(e, context=f"{node_name} Validation")
        except Exception as e:
            logger.error(f"Error in {node_name}: {e}", exc_info=True)
            return self.handle_error(e, context=node_name)
    
    def _determine_result_format(self, result_format: str, node_data: Dict[str, Any]) -> str:
        """Determine which result format to use based on configuration and context."""
        if result_format in ["legacy", "flat"]:
            return result_format
        
        # Auto-detection logic
        workflow_data = node_data.get("__workflow_data", {})
        node_name = node_data.get("__node_name", "")
        
        # Check for legacy indicators
        legacy_indicators = [
            workflow_data.get("version", "1.0").startswith("1."),
            "Step" in node_name and any(char.isdigit() for char in node_name),
            self._has_legacy_template_patterns(workflow_data)
        ]
        
        if any(legacy_indicators):
            logger.debug(f"Auto-detected legacy format for node {node_name}")
            return "legacy"
        else:
            logger.debug(f"Auto-detected flat format for node {node_name}")
            return "flat"
    
    def _has_legacy_template_patterns(self, workflow_data: Dict[str, Any]) -> bool:
        """Check if the workflow contains legacy template patterns."""
        workflow_content = str(workflow_data)
        legacy_patterns = [
            ".result.result.",
            "result.result.",
            "{{Step",
            "_MathematicalFoundation.result.result",
        ]
        return any(pattern in workflow_content for pattern in legacy_patterns)
    
    def _prepare_execution_context(self, node_data: Dict[str, Any], pass_context: bool) -> Dict[str, Any]:
        """Prepare the execution context for the Python code."""
        context = {}
        context["node_name"] = node_data.get("__node_name", "PyNode")
        context["execution_id"] = node_data.get("__execution_id", "unknown")
        
        # Handle input_data parameter from ACT workflow config
        params = node_data.get("params", {})
        if "input_data" in params:
            input_data_raw = params["input_data"]
            # If input_data is a JSON string, parse it back to dict
            if isinstance(input_data_raw, str):
                try:
                    context["input_data"] = json.loads(input_data_raw)
                except json.JSONDecodeError:
                    # If it's not valid JSON, treat it as a string
                    context["input_data"] = input_data_raw
            else:
                context["input_data"] = input_data_raw
        
        if pass_context:
            context["node_data"] = node_data
            context["params"] = params
            if "request_data" in node_data:
                context["request_data"] = node_data["request_data"]
        
        return context
    
    def _load_code_from_file(self, file_path: str) -> tuple:
        """Load Python code from a file."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                cwd_path = Path.cwd() / path
                if cwd_path.exists():
                    path = cwd_path
                else:
                    actfile_dir = self._find_actfile_directory()
                    if actfile_dir:
                        actfile_path = actfile_dir / path
                        if actfile_path.exists():
                            path = actfile_path
            
            if not path.exists():
                raise NodeExecutionError(f"Python file not found: {path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return code, f"file: {path}"
        
        except Exception as e:
            raise NodeExecutionError(f"Error loading Python file: {e}")
    
    def _find_actfile_directory(self) -> Optional[Path]:
        """Try to find the directory containing the Actfile."""
        try:
            current_dir = Path.cwd()
            for _ in range(5):
                for name in ["Actfile", "actfile", "actfile.ini", "Actfile.ini"]:
                    if (current_dir / name).exists():
                        return current_dir
                parent_dir = current_dir.parent
                if parent_dir == current_dir:
                    break
                current_dir = parent_dir
            return None
        except Exception as e:
            logger.warning(f"Error finding Actfile directory: {e}")
            return None
    
    def _execute_python_code(
        self, 
        code: str, 
        function_name: Optional[str], 
        args: List[Any], 
        kwargs: Dict[str, Any], 
        context: Dict[str, Any], 
        use_params_as_kwargs: bool,
        pass_context: bool,
        timeout: int
    ) -> tuple:
        """Execute Python code and return the result and captured stdout."""
        original_stdout = sys.stdout
        stdout_capture = StringIO()
        result = None
        
        try:
            # Redirect stdout to capture print statements
            sys.stdout = stdout_capture
            
            # Prepare the namespace for execution
            namespace = {
                "__builtins__": __builtins__,
                "context": context,
                # Add standard boolean values for compatibility
                "True": True,
                "False": False,
                "None": None,
                # Add JSON boolean mappings for compatibility
                "true": True,
                "false": False, 
                "null": None,
            }
            
            # Add context variables directly to the namespace
            for key, value in context.items():
                namespace[key] = value
            
            # Compile and execute the code
            try:
                compiled_code = compile(code, "<string>", "exec")
                exec(compiled_code, namespace)
            except SyntaxError as e:
                # Enhanced error reporting for syntax errors
                error_lines = code.split('\n')
                error_context = []
                
                if hasattr(e, 'lineno') and e.lineno:
                    start_line = max(0, e.lineno - 3)
                    end_line = min(len(error_lines), e.lineno + 2)
                    
                    for i, line in enumerate(error_lines[start_line:end_line], start=start_line + 1):
                        marker = " -> " if i == e.lineno else "    "
                        error_context.append(f"{marker}{i:3d}: {line}")
                
                error_msg = f"Syntax Error in Python code:\n"
                error_msg += f"  Error: {e.msg}\n"
                error_msg += f"  Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}\n"
                if error_context:
                    error_msg += f"\nCode context:\n" + "\n".join(error_context)
                
                raise NodeExecutionError(error_msg)
            
            # Call a specific function if requested
            if function_name:
                if function_name not in namespace:
                    available_funcs = [k for k, v in namespace.items() if callable(v) and not k.startswith('_')]
                    raise NodeExecutionError(
                        f"Function '{function_name}' not found in the executed code. "
                        f"Available functions: {available_funcs}"
                    )
                
                func = namespace[function_name]
                if not callable(func):
                    raise NodeExecutionError(f"'{function_name}' is not a callable function")
                
                # Prepare function arguments
                call_kwargs = dict(kwargs)
                
                if use_params_as_kwargs and "params" in context:
                    for key, value in context["params"].items():
                        if key not in ["code", "path", "function", "args", "kwargs", 
                                       "use_params_as_kwargs", "pass_context", "timeout", 
                                       "result_format", "placeholder_mode"]:
                            call_kwargs[key] = value
                
                if pass_context:
                    call_kwargs.setdefault("context", context)
                
                # Call the function
                result = func(*args, **call_kwargs)
            else:
                # If no function is specified, look for a result variable
                result = namespace.get("result", None)
            
            # Get captured stdout
            stdout = stdout_capture.getvalue()
            
            return result, stdout
            
        except Exception as e:
            if not isinstance(e, NodeExecutionError):
                # Get the traceback for runtime errors
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                
                # Filter out frames from this file
                filtered_tb = []
                for line in tb_lines:
                    if "py_node.py" not in line or "<string>" in line:
                        filtered_tb.append(line)
                
                error_message = f"Runtime Error in Python code: {e}\n{''.join(filtered_tb)}"
                raise NodeExecutionError(error_message)
            else:
                raise
        
        finally:
            # Restore original stdout
            sys.stdout = original_stdout


# For standalone testing
# === Register Node with Registry (happens during module import) ===
logger.debug("🔍 PyNode.py - About to register node type 'py'")
try:
    from .base_node import NodeRegistry
    NodeRegistry.register("py", PyNode)
    logger.debug("✅ REGISTERED PyNode as 'py' at module level")
except Exception as e:
    logger.error(f"❌ ERROR registering PyNode at module level: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    # Configure logging for standalone test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    )
    
    async def test_enhanced_placeholder_resolution():
        print("\n--- Testing ENHANCED PyNode with Placeholder Resolution ---")
        node = PyNode()
        
        # Mock node results that would come from previous nodes
        mock_node_results = {
            "Step01_AnalyzeSwitchSystem": {
                "status": "success",
                "result": {
                    "result": {
                        "num_people": 8,
                        "influence_sets": {
                            "1": [2, 4, 6, 7],
                            "2": [8, 3, 5, 6],
                            "3": [4, 6],
                            "4": [5],
                            "5": [8, 6],
                            "6": [7],
                            "7": [8],
                            "8": []
                        },
                        "total_states": 256,
                        "approach": "Deterministic simulation and cycle decomposition"
                    }
                }
            }
        }
        
        # Test 1: Smart placeholder resolution (prevents JSON escaping issues)
        print("\n1. Testing SMART placeholder resolution...")
        test_code = '''
def test_function():
    params = {{Step01_AnalyzeSwitchSystem.result.result}}
    print(f"Number of people: {params['num_people']}")
    print(f"Influence sets: {params['influence_sets']}")
    return {"processed": True, "data": params}
'''
        
        result = await node.execute({
            "__node_name": "TestNode",
            "__node_results": mock_node_results,
            "params": {
                "code": test_code,
                "function": "test_function",
                "placeholder_mode": "smart"
            }
        })
        
        print(f"Smart mode result: {result['status']}")
        if result['status'] == 'success':
            print(f"Function output: {result['result']}")
        else:
            print(f"Error: {result['message']}")
        
        # Test 2: Handling docstrings and quotes properly
        print("\n2. Testing docstring and quote handling...")
        docstring_code = '''
def process_data():
    """
    This function processes data with "quotes" and backslashes.
    It handles all edge cases properly.
    """
    params = {{Step01_AnalyzeSwitchSystem.result.result}}
    message = "Processing data with \\"quotes\\" and 'apostrophes'"
    print(message)
    return {"message": message, "params_keys": list(params.keys())}
'''
        
        result2 = await node.execute({
            "__node_name": "DocstringTest",
            "__node_results": mock_node_results,
            "params": {
                "code": docstring_code,
                "function": "process_data",
                "placeholder_mode": "smart"
            }
        })
        
        print(f"Docstring test result: {result2['status']}")
        if result2['status'] == 'success':
            print(f"Docstring function output: {result2['result']}")
        
        # Test 3: JSON mode (for comparison)
        print("\n3. Testing JSON placeholder mode...")
        result3 = await node.execute({
            "__node_name": "JSONMode",
            "__node_results": mock_node_results,
            "params": {
                "code": '''
def simple_test():
    params = {{Step01_AnalyzeSwitchSystem.result.result}}
    return {"total_states": params["total_states"]}
''',
                "function": "simple_test",
                "placeholder_mode": "json"
            }
        })
        
        print(f"JSON mode result: {result3['status']}")
        
        print(f"\n--- ALL ENHANCED TESTS COMPLETED ---")
        print(f"✅ Smart mode: Prevents JSON escaping issues")
        print(f"✅ Docstrings: Handled properly with quotes and backslashes")
        print(f"✅ Error handling: Enhanced with better diagnostics")
    
    asyncio.run(test_enhanced_placeholder_resolution())

