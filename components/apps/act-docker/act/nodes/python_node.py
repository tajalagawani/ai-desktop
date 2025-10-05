import logging
import json
import asyncio
import time
import os
import importlib.util
import sys
from typing import Dict, Any, List, Optional, Union, Callable
import tempfile
import traceback

# Import the base node classes
try:
    from .base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class PythonOperationType:
    """Python operation types (string constants)."""
    EXECUTE_CODE = "execute_code"
    EXECUTE_FILE = "execute_file"
    EXECUTE_FUNCTION = "execute_function"

class PythonNode(BaseNode):
    """
    Node for executing Python code with various options.
    Supports inline code, external files, and function execution.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Python node."""
        return NodeSchema(
            node_type="python",
            version="1.0.0",
            description="Execute Python code in various modes",
            parameters=[
                # Core parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Type of Python operation to perform",
                    required=True,
                    enum=[
                        PythonOperationType.EXECUTE_CODE,
                        PythonOperationType.EXECUTE_FILE,
                        PythonOperationType.EXECUTE_FUNCTION
                    ]
                ),
                
                # Inline code execution
                NodeParameter(
                    name="code",
                    type=NodeParameterType.STRING,
                    description="Python code to execute (for execute_code operation)",
                    required=False
                ),
                
                # File execution
                NodeParameter(
                    name="file_path",
                    type=NodeParameterType.STRING,
                    description="Path to Python file (for execute_file operation)",
                    required=False
                ),
                
                # Function execution
                NodeParameter(
                    name="module_path",
                    type=NodeParameterType.STRING,
                    description="Path to Python module containing the function (for execute_function operation)",
                    required=False
                ),
                NodeParameter(
                    name="function_name",
                    type=NodeParameterType.STRING,
                    description="Name of function to execute (for execute_function operation)",
                    required=False
                ),
                
                # Common parameters
                NodeParameter(
                    name="input_data",
                    type=NodeParameterType.ANY,
                    description="Input data to pass to the Python code",
                    required=False
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.NUMBER,
                    description="Execution timeout in seconds",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="requirements",
                    type=NodeParameterType.ARRAY,
                    description="List of Python package requirements",
                    required=False,
                    default=[]
                ),
                NodeParameter(
                    name="environment_variables",
                    type=NodeParameterType.OBJECT,
                    description="Environment variables to set for execution",
                    required=False,
                    default={}
                ),
                NodeParameter(
                    name="memory_limit",
                    type=NodeParameterType.NUMBER,
                    description="Memory limit in MB (0 for no limit)",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="capture_stdout",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to capture standard output",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="capture_stderr",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to capture standard error",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="working_directory",
                    type=NodeParameterType.STRING,
                    description="Working directory for execution",
                    required=False
                )
            ],
            
            # Define outputs
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "stdout": NodeParameterType.STRING,
                "stderr": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER,
                "error": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["python", "code", "execution", "scripting"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Validate based on operation
        if operation == PythonOperationType.EXECUTE_CODE:
            if not params.get("code"):
                raise NodeValidationError("Python code is required for execute_code operation")
                
        elif operation == PythonOperationType.EXECUTE_FILE:
            if not params.get("file_path"):
                raise NodeValidationError("File path is required for execute_file operation")
            
            file_path = params.get("file_path")
            if not os.path.exists(file_path):
                raise NodeValidationError(f"Python file not found: {file_path}")
                
        elif operation == PythonOperationType.EXECUTE_FUNCTION:
            if not params.get("module_path"):
                raise NodeValidationError("Module path is required for execute_function operation")
                
            if not params.get("function_name"):
                raise NodeValidationError("Function name is required for execute_function operation")
            
            module_path = params.get("module_path")
            if not os.path.exists(module_path) and not module_path.startswith("package:"):
                raise NodeValidationError(f"Module file not found: {module_path}")
        
        # Validate timeout
        timeout = params.get("timeout", 30)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise NodeValidationError("Timeout must be a positive number")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Python node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Set up environment variables if provided
            env_vars = validated_data.get("environment_variables", {})
            original_env = {}
            try:
                # Save original environment values
                for key, value in env_vars.items():
                    if key in os.environ:
                        original_env[key] = os.environ[key]
                    os.environ[key] = str(value)
                
                # Execute the appropriate operation
                if operation == PythonOperationType.EXECUTE_CODE:
                    return await self._operation_execute_code(validated_data)
                elif operation == PythonOperationType.EXECUTE_FILE:
                    return await self._operation_execute_file(validated_data)
                elif operation == PythonOperationType.EXECUTE_FUNCTION:
                    return await self._operation_execute_function(validated_data)
                else:
                    error_message = f"Unknown operation: {operation}"
                    logger.error(error_message)
                    return self._error_response(error_message)
            finally:
                # Restore original environment variables
                for key in env_vars:
                    if key in original_env:
                        os.environ[key] = original_env[key]
                    else:
                        del os.environ[key]
                
        except Exception as e:
            error_message = f"Error in Python node: {str(e)}"
            logger.error(error_message, exc_info=True)
            return self._error_response(error_message)
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate a standard error response."""
        return {
            "status": "error",
            "result": None,
            "stdout": "",
            "stderr": "",
            "execution_time": 0,
            "error": error_message
        }
    
    async def _operation_execute_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute inline Python code.
        
        Args:
            params: Parameters including the code to execute
            
        Returns:
            Execution results
        """
        code = params.get("code", "")
        input_data = params.get("input_data")
        timeout = params.get("timeout", 30)
        capture_stdout = params.get("capture_stdout", True)
        capture_stderr = params.get("capture_stderr", True)
        working_dir = params.get("working_directory")
        
        # Create a temporary file to execute the code
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
            # Write the code to the file
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Create a namespace for execution
            namespace = {'input_data': input_data, 'result': None}
            
            # Modify the code to capture the result
            modified_code = code + "\n\n# Added by PythonNode\nresult = locals().get('result', None)"
            
            # Execute the code and capture output
            return await self._execute_python_file_with_capture(
                temp_file_path, 
                namespace, 
                timeout,
                capture_stdout,
                capture_stderr,
                working_dir,
                modified_code
            )
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
    
    async def _operation_execute_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Python file.
        
        Args:
            params: Parameters including the file path
            
        Returns:
            Execution results
        """
        file_path = params.get("file_path", "")
        input_data = params.get("input_data")
        timeout = params.get("timeout", 30)
        capture_stdout = params.get("capture_stdout", True)
        capture_stderr = params.get("capture_stderr", True)
        working_dir = params.get("working_directory")
        
        # Create a namespace for execution
        namespace = {'input_data': input_data, 'result': None}
        
        # Execute the file and capture output
        return await self._execute_python_file_with_capture(
            file_path, 
            namespace, 
            timeout,
            capture_stdout,
            capture_stderr,
            working_dir
        )
    
    async def _operation_execute_function(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function from a Python module.
        
        Args:
            params: Parameters including the module path and function name
            
        Returns:
            Execution results
        """
        module_path = params.get("module_path", "")
        function_name = params.get("function_name", "")
        input_data = params.get("input_data")
        timeout = params.get("timeout", 30)
        capture_stdout = params.get("capture_stdout", True)
        capture_stderr = params.get("capture_stderr", True)
        working_dir = params.get("working_directory")
        
        start_time = time.time()
        stdout_capture = ""
        stderr_capture = ""
        
        # Check if module path is a package path
        if module_path.startswith("package:"):
            # Import from an installed package
            package_path = module_path[len("package:"):]
            try:
                module = importlib.import_module(package_path)
            except ImportError as e:
                return self._error_response(f"Failed to import module {package_path}: {str(e)}")
        else:
            # Import from a file path
            try:
                # Get the absolute path
                module_abs_path = os.path.abspath(module_path)
                
                # Check if the file exists
                if not os.path.exists(module_abs_path):
                    return self._error_response(f"Module file not found: {module_abs_path}")
                
                # Load the module from the file
                module_name = os.path.splitext(os.path.basename(module_abs_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, module_abs_path)
                if spec is None:
                    return self._error_response(f"Failed to create module spec for {module_abs_path}")
                
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            except Exception as e:
                return self._error_response(f"Failed to load module {module_path}: {str(e)}")
        
        # Check if the function exists in the module
        if not hasattr(module, function_name):
            return self._error_response(f"Function {function_name} not found in module {module_path}")
        
        # Get the function
        function = getattr(module, function_name)
        if not callable(function):
            return self._error_response(f"{function_name} is not a callable function in module {module_path}")
        
        # Set up working directory if provided
        original_dir = None
        if working_dir:
            if not os.path.exists(working_dir):
                return self._error_response(f"Working directory not found: {working_dir}")
            original_dir = os.getcwd()
            os.chdir(working_dir)
        
        try:
            # Set up stdout/stderr capturing
            if capture_stdout or capture_stderr:
                import io
                import contextlib
                
                stdout_io = io.StringIO() if capture_stdout else None
                stderr_io = io.StringIO() if capture_stderr else None
                
                with contextlib.redirect_stdout(stdout_io), contextlib.redirect_stderr(stderr_io):
                    # Execute the function with a timeout
                    try:
                        if input_data is not None:
                            if isinstance(input_data, dict):
                                result = await asyncio.wait_for(
                                    asyncio.to_thread(lambda: function(**input_data)), 
                                    timeout
                                )
                            else:
                                result = await asyncio.wait_for(
                                    asyncio.to_thread(lambda: function(input_data)), 
                                    timeout
                                )
                        else:
                            result = await asyncio.wait_for(
                                asyncio.to_thread(lambda: function()), 
                                timeout
                            )
                    except asyncio.TimeoutError:
                        return self._error_response(f"Function execution timed out after {timeout} seconds")
                
                # Collect captured output
                if stdout_io:
                    stdout_capture = stdout_io.getvalue()
                if stderr_io:
                    stderr_capture = stderr_io.getvalue()
            else:
                # Execute without capturing output
                try:
                    if input_data is not None:
                        if isinstance(input_data, dict):
                            result = await asyncio.wait_for(
                                asyncio.to_thread(lambda: function(**input_data)), 
                                timeout
                            )
                        else:
                            result = await asyncio.wait_for(
                                asyncio.to_thread(lambda: function(input_data)), 
                                timeout
                            )
                    else:
                        result = await asyncio.wait_for(
                            asyncio.to_thread(lambda: function()), 
                            timeout
                        )
                except asyncio.TimeoutError:
                    return self._error_response(f"Function execution timed out after {timeout} seconds")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "stdout": stdout_capture,
                "stderr": stderr_capture,
                "execution_time": execution_time,
                "error": None
            }
        except Exception as e:
            error_message = f"Function execution error: {str(e)}"
            logger.error(error_message, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "stdout": stdout_capture,
                "stderr": stderr_capture,
                "execution_time": time.time() - start_time,
                "error": f"{error_message}\n\n{traceback.format_exc()}"
            }
        finally:
            # Restore original working directory if changed
            if original_dir:
                os.chdir(original_dir)
    
    async def _execute_python_file_with_capture(
        self, 
        file_path: str, 
        namespace: Dict[str, Any], 
        timeout: int,
        capture_stdout: bool,
        capture_stderr: bool,
        working_dir: Optional[str] = None,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a Python file with output capturing.
        
        Args:
            file_path: Path to the Python file
            namespace: Namespace for execution
            timeout: Execution timeout in seconds
            capture_stdout: Whether to capture stdout
            capture_stderr: Whether to capture stderr
            working_dir: Working directory for execution
            code: Optional code string to execute instead of file content
            
        Returns:
            Execution results
        """
        start_time = time.time()
        stdout_capture = ""
        stderr_capture = ""
        
        # Set up working directory if provided
        original_dir = None
        if working_dir:
            if not os.path.exists(working_dir):
                return self._error_response(f"Working directory not found: {working_dir}")
            original_dir = os.getcwd()
            os.chdir(working_dir)
        
        try:
            # Set up stdout/stderr capturing
            if capture_stdout or capture_stderr:
                import io
                import contextlib
                
                stdout_io = io.StringIO() if capture_stdout else None
                stderr_io = io.StringIO() if capture_stderr else None
                
                with contextlib.redirect_stdout(stdout_io), contextlib.redirect_stderr(stderr_io):
                    # Execute the code with a timeout
                    try:
                        if code:
                            # Execute the provided code string
                            exec_result = await asyncio.wait_for(
                                asyncio.to_thread(lambda: exec(code, namespace)), 
                                timeout
                            )
                        else:
                            # Execute the file
                            with open(file_path, 'r') as f:
                                file_code = f.read()
                            exec_result = await asyncio.wait_for(
                                asyncio.to_thread(lambda: exec(file_code, namespace)), 
                                timeout
                            )
                    except asyncio.TimeoutError:
                        return self._error_response(f"Code execution timed out after {timeout} seconds")
                
                # Collect captured output
                if stdout_io:
                    stdout_capture = stdout_io.getvalue()
                if stderr_io:
                    stderr_capture = stderr_io.getvalue()
            else:
                # Execute without capturing output
                try:
                    if code:
                        # Execute the provided code string
                        exec_result = await asyncio.wait_for(
                            asyncio.to_thread(lambda: exec(code, namespace)), 
                            timeout
                        )
                    else:
                        # Execute the file
                        with open(file_path, 'r') as f:
                            file_code = f.read()
                        exec_result = await asyncio.wait_for(
                            asyncio.to_thread(lambda: exec(file_code, namespace)), 
                            timeout
                        )
                except asyncio.TimeoutError:
                    return self._error_response(f"Code execution timed out after {timeout} seconds")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Get the result from the namespace
            result = namespace.get('result')
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "stdout": stdout_capture,
                "stderr": stderr_capture,
                "execution_time": execution_time,
                "error": None
            }
        except Exception as e:
            error_message = f"Code execution error: {str(e)}"
            logger.error(error_message, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "stdout": stdout_capture,
                "stderr": stderr_capture,
                "execution_time": time.time() - start_time,
                "error": f"{error_message}\n\n{traceback.format_exc()}"
            }
        finally:
            # Restore original working directory if changed
            if original_dir:
                os.chdir(original_dir)

# Register with NodeRegistry
try:
    from .base_node import NodeRegistry
    NodeRegistry.register("python", PythonNode)
    logger.debug("Registered node type: python")
except Exception as e:
    logger.error(f"Error registering Python node: {str(e)}")