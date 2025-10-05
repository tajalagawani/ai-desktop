"""
FunctionCallingNode - Function calling integration for LLM workflows.
Handles function definitions, parameter validation, execution management, and response formatting.
"""

import json
import inspect
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import importlib
import sys

from .base_node import BaseNode, NodeResult, NodeSchema, NodeParameter, NodeParameterType
from ..utils.validation import NodeValidationError

class FunctionCallingOperation:
    DEFINE_FUNCTION = "define_function"
    CALL_FUNCTION = "call_function"
    VALIDATE_PARAMETERS = "validate_parameters"
    GET_FUNCTION_SCHEMA = "get_function_schema"
    LIST_FUNCTIONS = "list_functions"
    PARSE_FUNCTION_CALL = "parse_function_call"
    FORMAT_FUNCTION_RESPONSE = "format_function_response"
    EXECUTE_BATCH_CALLS = "execute_batch_calls"
    VALIDATE_FUNCTION_DEFINITION = "validate_function_definition"
    GENERATE_FUNCTION_DOCS = "generate_function_docs"
    MAP_PARAMETERS = "map_parameters"
    HANDLE_FUNCTION_ERROR = "handle_function_error"
    CREATE_FUNCTION_WRAPPER = "create_function_wrapper"
    SIMULATE_FUNCTION_CALL = "simulate_function_call"
    TRACK_FUNCTION_USAGE = "track_function_usage"
    COMPOSE_FUNCTION_CHAIN = "compose_function_chain"
    VALIDATE_RETURN_TYPE = "validate_return_type"
    CREATE_FUNCTION_LIBRARY = "create_function_library"
    OPTIMIZE_FUNCTION_CALLS = "optimize_function_calls"
    HANDLE_ASYNC_FUNCTIONS = "handle_async_functions"

class FunctionCallingNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.name = "FunctionCallingNode"
        self.description = "Function calling integration for LLM workflows"
        self.version = "1.0.0"
        self.icon_path = "⚙️"
        self.function_registry = {}
        self.call_history = []
        self.function_usage_stats = {}

    async def execute(self, operation: str, params: Dict[str, Any]) -> NodeResult:
        try:
            operation_map = {
                FunctionCallingOperation.DEFINE_FUNCTION: self._define_function,
                FunctionCallingOperation.CALL_FUNCTION: self._call_function,
                FunctionCallingOperation.VALIDATE_PARAMETERS: self._validate_parameters,
                FunctionCallingOperation.GET_FUNCTION_SCHEMA: self._get_function_schema,
                FunctionCallingOperation.LIST_FUNCTIONS: self._list_functions,
                FunctionCallingOperation.PARSE_FUNCTION_CALL: self._parse_function_call,
                FunctionCallingOperation.FORMAT_FUNCTION_RESPONSE: self._format_function_response,
                FunctionCallingOperation.EXECUTE_BATCH_CALLS: self._execute_batch_calls,
                FunctionCallingOperation.VALIDATE_FUNCTION_DEFINITION: self._validate_function_definition,
                FunctionCallingOperation.GENERATE_FUNCTION_DOCS: self._generate_function_docs,
                FunctionCallingOperation.MAP_PARAMETERS: self._map_parameters,
                FunctionCallingOperation.HANDLE_FUNCTION_ERROR: self._handle_function_error,
                FunctionCallingOperation.CREATE_FUNCTION_WRAPPER: self._create_function_wrapper,
                FunctionCallingOperation.SIMULATE_FUNCTION_CALL: self._simulate_function_call,
                FunctionCallingOperation.TRACK_FUNCTION_USAGE: self._track_function_usage,
                FunctionCallingOperation.COMPOSE_FUNCTION_CHAIN: self._compose_function_chain,
                FunctionCallingOperation.VALIDATE_RETURN_TYPE: self._validate_return_type,
                FunctionCallingOperation.CREATE_FUNCTION_LIBRARY: self._create_function_library,
                FunctionCallingOperation.OPTIMIZE_FUNCTION_CALLS: self._optimize_function_calls,
                FunctionCallingOperation.HANDLE_ASYNC_FUNCTIONS: self._handle_async_functions,
            }

            if operation not in operation_map:
                return self._create_error_result(f"Unknown operation: {operation}")

            self._validate_params(operation, params)
            result = await operation_map[operation](params)
            
            return self._create_success_result(result, f"Function calling operation '{operation}' completed")
            
        except Exception as e:
            return self._create_error_result(f"Function calling error: {str(e)}")

    async def _define_function(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Define a new function for calling."""
        function_name = params["function_name"]
        function_definition = params["function_definition"]
        function_type = params.get("function_type", "python")  # python, external, api
        
        function_info = {
            "name": function_name,
            "definition": function_definition,
            "type": function_type,
            "created_at": datetime.now().isoformat(),
            "call_count": 0,
            "parameters": self._extract_function_parameters(function_definition),
            "return_type": self._extract_return_type(function_definition),
            "description": self._extract_function_description(function_definition)
        }
        
        # Validate function definition
        validation_result = await self._validate_function_definition({"function_definition": function_definition})
        if not validation_result["is_valid"]:
            raise NodeValidationError(f"Invalid function definition: {validation_result['errors']}")
        
        self.function_registry[function_name] = function_info
        
        # Initialize usage stats
        self.function_usage_stats[function_name] = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_execution_time": 0,
            "last_called": None
        }
        
        return {
            "function_name": function_name,
            "function_info": function_info,
            "registry_size": len(self.function_registry)
        }

    async def _call_function(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call."""
        function_name = params["function_name"]
        function_args = params.get("function_args", {})
        timeout = params.get("timeout", 30)
        track_usage = params.get("track_usage", True)
        
        start_time = datetime.now()
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found in registry")
        
        function_info = self.function_registry[function_name]
        
        try:
            # Validate parameters
            validation_result = await self._validate_parameters({
                "function_name": function_name,
                "parameters": function_args
            })
            
            if not validation_result["is_valid"]:
                raise NodeValidationError(f"Parameter validation failed: {validation_result['errors']}")
            
            # Execute function based on type
            if function_info["type"] == "python":
                result = await self._execute_python_function(function_info, function_args, timeout)
            elif function_info["type"] == "external":
                result = await self._execute_external_function(function_info, function_args, timeout)
            elif function_info["type"] == "api":
                result = await self._execute_api_function(function_info, function_args, timeout)
            else:
                raise NodeValidationError(f"Unknown function type: {function_info['type']}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Track usage
            if track_usage:
                await self._track_function_usage({
                    "function_name": function_name,
                    "execution_time": execution_time,
                    "success": True
                })
            
            # Log call history
            self.call_history.append({
                "function_name": function_name,
                "arguments": function_args,
                "result": result,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat(),
                "success": True
            })
            
            return {
                "function_name": function_name,
                "result": result,
                "execution_time": execution_time,
                "success": True,
                "call_id": len(self.call_history)
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if track_usage:
                await self._track_function_usage({
                    "function_name": function_name,
                    "execution_time": execution_time,
                    "success": False
                })
            
            self.call_history.append({
                "function_name": function_name,
                "arguments": function_args,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": start_time.isoformat(),
                "success": False
            })
            
            raise

    async def _validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate function parameters against schema."""
        function_name = params["function_name"]
        parameters = params["parameters"]
        
        if function_name not in self.function_registry:
            return {
                "is_valid": False,
                "errors": [f"Function '{function_name}' not found"]
            }
        
        function_info = self.function_registry[function_name]
        function_params = function_info["parameters"]
        
        errors = []
        warnings = []
        
        # Check required parameters
        for param_name, param_info in function_params.items():
            if param_info.get("required", False) and param_name not in parameters:
                errors.append(f"Required parameter '{param_name}' is missing")
        
        # Check parameter types
        for param_name, param_value in parameters.items():
            if param_name in function_params:
                expected_type = function_params[param_name].get("type")
                if expected_type:
                    if not self._validate_parameter_type(param_value, expected_type):
                        errors.append(f"Parameter '{param_name}' should be of type {expected_type}")
            else:
                warnings.append(f"Unknown parameter '{param_name}'")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validated_parameters": parameters
        }

    async def _get_function_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get OpenAI-compatible function schema."""
        function_name = params["function_name"]
        include_examples = params.get("include_examples", False)
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found")
        
        function_info = self.function_registry[function_name]
        
        schema = {
            "name": function_name,
            "description": function_info.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # Build parameter schema
        for param_name, param_info in function_info["parameters"].items():
            schema["parameters"]["properties"][param_name] = {
                "type": param_info.get("type", "string"),
                "description": param_info.get("description", "")
            }
            
            if param_info.get("enum"):
                schema["parameters"]["properties"][param_name]["enum"] = param_info["enum"]
            
            if param_info.get("required", False):
                schema["parameters"]["required"].append(param_name)
        
        if include_examples:
            schema["examples"] = self._generate_function_examples(function_info)
        
        return {
            "function_name": function_name,
            "schema": schema,
            "openai_format": True
        }

    async def _list_functions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available functions."""
        include_stats = params.get("include_stats", False)
        function_type_filter = params.get("function_type_filter")
        
        functions = []
        
        for function_name, function_info in self.function_registry.items():
            if function_type_filter and function_info["type"] != function_type_filter:
                continue
            
            function_data = {
                "name": function_name,
                "description": function_info.get("description", ""),
                "type": function_info["type"],
                "parameter_count": len(function_info["parameters"]),
                "created_at": function_info["created_at"]
            }
            
            if include_stats and function_name in self.function_usage_stats:
                function_data["usage_stats"] = self.function_usage_stats[function_name]
            
            functions.append(function_data)
        
        return {
            "functions": functions,
            "total_count": len(functions),
            "types": list(set(f["type"] for f in functions))
        }

    async def _parse_function_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse function call from LLM response."""
        text = params["text"]
        format_type = params.get("format_type", "auto")  # auto, openai, anthropic, json
        
        function_calls = []
        
        if format_type in ["auto", "openai"]:
            # Parse OpenAI function call format
            openai_calls = self._parse_openai_function_calls(text)
            function_calls.extend(openai_calls)
        
        if format_type in ["auto", "json"]:
            # Parse JSON function calls
            json_calls = self._parse_json_function_calls(text)
            function_calls.extend(json_calls)
        
        if format_type in ["auto", "anthropic"]:
            # Parse Anthropic function call format
            anthropic_calls = self._parse_anthropic_function_calls(text)
            function_calls.extend(anthropic_calls)
        
        # Validate parsed calls
        validated_calls = []
        for call in function_calls:
            validation = await self._validate_parameters({
                "function_name": call["function_name"],
                "parameters": call["arguments"]
            })
            
            validated_calls.append({
                **call,
                "is_valid": validation["is_valid"],
                "validation_errors": validation.get("errors", [])
            })
        
        return {
            "function_calls": validated_calls,
            "call_count": len(validated_calls),
            "valid_calls": sum(1 for call in validated_calls if call["is_valid"])
        }

    async def _format_function_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Format function response for LLM consumption."""
        function_name = params["function_name"]
        result = params["result"]
        format_type = params.get("format_type", "json")  # json, text, openai
        include_metadata = params.get("include_metadata", True)
        
        formatted_response = {}
        
        if format_type == "json":
            formatted_response = {
                "function_name": function_name,
                "result": result,
                "status": "success"
            }
            
            if include_metadata:
                formatted_response["metadata"] = {
                    "timestamp": datetime.now().isoformat(),
                    "execution_info": self._get_last_execution_info(function_name)
                }
        
        elif format_type == "text":
            result_text = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            formatted_response = {
                "text": f"Function '{function_name}' returned: {result_text}",
                "function_name": function_name,
                "result": result
            }
        
        elif format_type == "openai":
            formatted_response = {
                "role": "function",
                "name": function_name,
                "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            }
        
        return {
            "formatted_response": formatted_response,
            "format_type": format_type,
            "function_name": function_name
        }

    async def _execute_batch_calls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple function calls in batch."""
        function_calls = params["function_calls"]
        parallel_execution = params.get("parallel_execution", False)
        fail_fast = params.get("fail_fast", False)
        max_workers = params.get("max_workers", 5)
        
        results = []
        
        if parallel_execution:
            # Execute calls in parallel
            semaphore = asyncio.Semaphore(max_workers)
            
            async def execute_with_semaphore(call):
                async with semaphore:
                    try:
                        return await self._call_function({
                            "function_name": call["function_name"],
                            "function_args": call.get("arguments", {}),
                            "track_usage": False  # Track separately for batch
                        })
                    except Exception as e:
                        return {
                            "function_name": call["function_name"],
                            "error": str(e),
                            "success": False
                        }
            
            tasks = [execute_with_semaphore(call) for call in function_calls]
            results = await asyncio.gather(*tasks, return_exceptions=not fail_fast)
        
        else:
            # Execute calls sequentially
            for call in function_calls:
                try:
                    result = await self._call_function({
                        "function_name": call["function_name"],
                        "function_args": call.get("arguments", {}),
                        "track_usage": False
                    })
                    results.append(result)
                    
                except Exception as e:
                    error_result = {
                        "function_name": call["function_name"],
                        "error": str(e),
                        "success": False
                    }
                    results.append(error_result)
                    
                    if fail_fast:
                        break
        
        # Update batch usage stats
        successful_calls = sum(1 for r in results if r.get("success", False))
        
        return {
            "batch_results": results,
            "total_calls": len(function_calls),
            "successful_calls": successful_calls,
            "failed_calls": len(function_calls) - successful_calls,
            "execution_mode": "parallel" if parallel_execution else "sequential"
        }

    async def _validate_function_definition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate function definition syntax and structure."""
        function_definition = params["function_definition"]
        
        errors = []
        warnings = []
        
        try:
            # Try to parse as Python code
            parsed = compile(function_definition, '<string>', 'exec')
            
            # Extract function info
            namespace = {}
            exec(parsed, namespace)
            
            # Find functions in namespace
            functions = {name: obj for name, obj in namespace.items() 
                        if callable(obj) and not name.startswith('_')}
            
            if not functions:
                errors.append("No callable functions found in definition")
            else:
                # Validate each function
                for func_name, func in functions.items():
                    sig = inspect.signature(func)
                    
                    # Check for proper annotations
                    if not func.__doc__:
                        warnings.append(f"Function '{func_name}' missing docstring")
                    
                    # Check parameter annotations
                    for param_name, param in sig.parameters.items():
                        if param.annotation == inspect.Parameter.empty:
                            warnings.append(f"Parameter '{param_name}' in '{func_name}' missing type annotation")
                    
                    # Check return annotation
                    if sig.return_annotation == inspect.Signature.empty:
                        warnings.append(f"Function '{func_name}' missing return type annotation")
        
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
        except Exception as e:
            errors.append(f"Compilation error: {e}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "function_definition": function_definition
        }

    async def _generate_function_docs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for functions."""
        function_name = params.get("function_name")
        include_examples = params.get("include_examples", True)
        format_type = params.get("format_type", "markdown")  # markdown, json, openapi
        
        if function_name:
            functions_to_document = [function_name]
        else:
            functions_to_document = list(self.function_registry.keys())
        
        documentation = {}
        
        for func_name in functions_to_document:
            if func_name not in self.function_registry:
                continue
            
            function_info = self.function_registry[func_name]
            
            if format_type == "markdown":
                doc = self._generate_markdown_docs(func_name, function_info, include_examples)
            elif format_type == "json":
                doc = self._generate_json_docs(func_name, function_info, include_examples)
            elif format_type == "openapi":
                doc = self._generate_openapi_docs(func_name, function_info)
            else:
                doc = str(function_info)
            
            documentation[func_name] = doc
        
        return {
            "documentation": documentation,
            "format_type": format_type,
            "function_count": len(documentation)
        }

    async def _map_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map input parameters to function parameter schema."""
        function_name = params["function_name"]
        input_data = params["input_data"]
        mapping_rules = params.get("mapping_rules", {})
        auto_mapping = params.get("auto_mapping", True)
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found")
        
        function_params = self.function_registry[function_name]["parameters"]
        mapped_params = {}
        unmapped_data = {}
        
        # Apply explicit mapping rules
        for input_key, function_param in mapping_rules.items():
            if input_key in input_data and function_param in function_params:
                mapped_params[function_param] = input_data[input_key]
            elif input_key in input_data:
                unmapped_data[input_key] = input_data[input_key]
        
        # Auto-mapping for remaining data
        if auto_mapping:
            for input_key, input_value in input_data.items():
                if input_key not in [k for k in mapping_rules.keys()]:
                    # Try exact match
                    if input_key in function_params:
                        mapped_params[input_key] = input_value
                    # Try case-insensitive match
                    else:
                        matching_params = [p for p in function_params.keys() 
                                         if p.lower() == input_key.lower()]
                        if matching_params:
                            mapped_params[matching_params[0]] = input_value
                        else:
                            unmapped_data[input_key] = input_value
        
        # Validate mapped parameters
        validation = await self._validate_parameters({
            "function_name": function_name,
            "parameters": mapped_params
        })
        
        return {
            "mapped_parameters": mapped_params,
            "unmapped_data": unmapped_data,
            "mapping_success": validation["is_valid"],
            "validation_errors": validation.get("errors", []),
            "mapping_coverage": len(mapped_params) / len(function_params) if function_params else 0
        }

    async def _handle_function_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle and categorize function execution errors."""
        error = params["error"]
        function_name = params.get("function_name")
        context = params.get("context", {})
        
        error_info = {
            "error_message": str(error),
            "error_type": type(error).__name__,
            "function_name": function_name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Categorize error
        error_category = self._categorize_error(error)
        error_info["category"] = error_category
        
        # Generate suggestions
        suggestions = self._generate_error_suggestions(error, error_category, function_name)
        error_info["suggestions"] = suggestions
        
        # Check if error is recoverable
        error_info["recoverable"] = self._is_error_recoverable(error, error_category)
        
        return error_info

    async def _create_function_wrapper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a wrapper function with additional functionality."""
        function_name = params["function_name"]
        wrapper_type = params.get("wrapper_type", "logging")  # logging, retry, timeout, validation
        wrapper_config = params.get("wrapper_config", {})
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found")
        
        original_function = self.function_registry[function_name]
        
        # Create wrapper based on type
        if wrapper_type == "logging":
            wrapper = self._create_logging_wrapper(original_function, wrapper_config)
        elif wrapper_type == "retry":
            wrapper = self._create_retry_wrapper(original_function, wrapper_config)
        elif wrapper_type == "timeout":
            wrapper = self._create_timeout_wrapper(original_function, wrapper_config)
        elif wrapper_type == "validation":
            wrapper = self._create_validation_wrapper(original_function, wrapper_config)
        else:
            raise NodeValidationError(f"Unknown wrapper type: {wrapper_type}")
        
        # Register wrapped function
        wrapped_name = f"{function_name}_wrapped"
        self.function_registry[wrapped_name] = wrapper
        
        return {
            "original_function": function_name,
            "wrapped_function": wrapped_name,
            "wrapper_type": wrapper_type,
            "wrapper_config": wrapper_config
        }

    async def _simulate_function_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate function call without actual execution."""
        function_name = params["function_name"]
        function_args = params.get("function_args", {})
        simulation_mode = params.get("simulation_mode", "mock")  # mock, dry_run, estimate
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found")
        
        function_info = self.function_registry[function_name]
        
        # Validate parameters
        validation = await self._validate_parameters({
            "function_name": function_name,
            "parameters": function_args
        })
        
        simulation_result = {
            "function_name": function_name,
            "arguments": function_args,
            "simulation_mode": simulation_mode,
            "would_execute": validation["is_valid"],
            "validation_result": validation
        }
        
        if simulation_mode == "mock":
            # Generate mock result based on return type
            mock_result = self._generate_mock_result(function_info)
            simulation_result["mock_result"] = mock_result
        
        elif simulation_mode == "estimate":
            # Estimate execution time and resources
            estimates = self._estimate_execution_metrics(function_info, function_args)
            simulation_result["estimates"] = estimates
        
        return simulation_result

    async def _track_function_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track function usage statistics."""
        function_name = params["function_name"]
        execution_time = params.get("execution_time", 0)
        success = params.get("success", True)
        
        if function_name not in self.function_usage_stats:
            self.function_usage_stats[function_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "average_execution_time": 0,
                "last_called": None
            }
        
        stats = self.function_usage_stats[function_name]
        
        # Update counters
        stats["total_calls"] += 1
        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
        
        # Update average execution time
        if execution_time > 0:
            current_avg = stats["average_execution_time"]
            new_avg = ((current_avg * (stats["total_calls"] - 1)) + execution_time) / stats["total_calls"]
            stats["average_execution_time"] = new_avg
        
        stats["last_called"] = datetime.now().isoformat()
        
        return {
            "function_name": function_name,
            "updated_stats": stats,
            "tracking_enabled": True
        }

    async def _compose_function_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a chain of function calls."""
        function_chain = params["function_chain"]  # List of function calls
        chain_mode = params.get("chain_mode", "sequential")  # sequential, parallel, conditional
        error_handling = params.get("error_handling", "stop")  # stop, continue, retry
        
        chain_results = []
        chain_context = {}
        
        for i, call_spec in enumerate(function_chain):
            function_name = call_spec["function_name"]
            function_args = call_spec.get("arguments", {})
            
            # Substitute variables from previous results
            if "variable_mapping" in call_spec:
                function_args = self._substitute_chain_variables(
                    function_args, 
                    call_spec["variable_mapping"], 
                    chain_context
                )
            
            try:
                if chain_mode == "conditional" and "condition" in call_spec:
                    # Evaluate condition
                    if not self._evaluate_chain_condition(call_spec["condition"], chain_context):
                        chain_results.append({
                            "step": i,
                            "function_name": function_name,
                            "skipped": True,
                            "reason": "condition not met"
                        })
                        continue
                
                # Execute function
                result = await self._call_function({
                    "function_name": function_name,
                    "function_args": function_args
                })
                
                chain_results.append({
                    "step": i,
                    "function_name": function_name,
                    "result": result,
                    "success": True
                })
                
                # Update chain context
                chain_context[f"step_{i}_result"] = result["result"]
                chain_context[function_name] = result["result"]
                
            except Exception as e:
                error_result = {
                    "step": i,
                    "function_name": function_name,
                    "error": str(e),
                    "success": False
                }
                
                chain_results.append(error_result)
                
                if error_handling == "stop":
                    break
                elif error_handling == "retry":
                    # Could implement retry logic here
                    pass
        
        return {
            "chain_results": chain_results,
            "chain_context": chain_context,
            "total_steps": len(function_chain),
            "executed_steps": len(chain_results),
            "successful_steps": sum(1 for r in chain_results if r.get("success", False))
        }

    async def _validate_return_type(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate function return value against expected type."""
        function_name = params["function_name"]
        return_value = params["return_value"]
        expected_type = params.get("expected_type")
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found")
        
        function_info = self.function_registry[function_name]
        expected_return_type = expected_type or function_info.get("return_type")
        
        validation_result = {
            "function_name": function_name,
            "return_value": return_value,
            "expected_type": expected_return_type,
            "actual_type": type(return_value).__name__,
            "is_valid": True,
            "errors": []
        }
        
        if expected_return_type:
            if not self._validate_type_match(return_value, expected_return_type):
                validation_result["is_valid"] = False
                validation_result["errors"].append(
                    f"Return type mismatch: expected {expected_return_type}, got {type(return_value).__name__}"
                )
        
        return validation_result

    async def _create_function_library(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a function library with multiple related functions."""
        library_name = params["library_name"]
        functions = params["functions"]  # List of function definitions
        library_description = params.get("description", "")
        
        library_info = {
            "name": library_name,
            "description": library_description,
            "functions": {},
            "created_at": datetime.now().isoformat()
        }
        
        # Define all functions in the library
        for func_def in functions:
            result = await self._define_function(func_def)
            library_info["functions"][func_def["function_name"]] = result["function_info"]
        
        return {
            "library_name": library_name,
            "library_info": library_info,
            "function_count": len(library_info["functions"])
        }

    async def _optimize_function_calls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize function call patterns and performance."""
        optimization_type = params.get("optimization_type", "performance")  # performance, caching, batching
        analysis_period = params.get("analysis_period", "all")  # recent, all
        
        optimization_results = {}
        
        if optimization_type in ["performance", "all"]:
            # Analyze performance patterns
            performance_analysis = self._analyze_performance_patterns()
            optimization_results["performance"] = performance_analysis
        
        if optimization_type in ["caching", "all"]:
            # Identify cacheable functions
            caching_analysis = self._analyze_caching_opportunities()
            optimization_results["caching"] = caching_analysis
        
        if optimization_type in ["batching", "all"]:
            # Identify batch opportunities
            batching_analysis = self._analyze_batching_opportunities()
            optimization_results["batching"] = batching_analysis
        
        return {
            "optimization_results": optimization_results,
            "optimization_type": optimization_type,
            "recommendations": self._generate_optimization_recommendations(optimization_results)
        }

    async def _handle_async_functions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle asynchronous function execution."""
        function_name = params["function_name"]
        function_args = params.get("function_args", {})
        execution_mode = params.get("execution_mode", "await")  # await, background, callback
        callback_url = params.get("callback_url")
        
        if function_name not in self.function_registry:
            raise NodeValidationError(f"Function '{function_name}' not found")
        
        if execution_mode == "await":
            # Standard async execution
            result = await self._call_function({
                "function_name": function_name,
                "function_args": function_args
            })
            return result
        
        elif execution_mode == "background":
            # Execute in background
            task_id = f"task_{datetime.now().timestamp()}"
            
            # Create background task (simplified)
            async def background_execution():
                try:
                    result = await self._call_function({
                        "function_name": function_name,
                        "function_args": function_args
                    })
                    return result
                except Exception as e:
                    return {"error": str(e), "success": False}
            
            # Start background task
            task = asyncio.create_task(background_execution())
            
            return {
                "task_id": task_id,
                "status": "running",
                "execution_mode": "background",
                "function_name": function_name
            }
        
        elif execution_mode == "callback":
            # Execute with callback
            if not callback_url:
                raise NodeValidationError("Callback URL required for callback mode")
            
            # Execute and send callback (simplified)
            result = await self._call_function({
                "function_name": function_name,
                "function_args": function_args
            })
            
            # Here you would typically send HTTP POST to callback_url
            # For now, just return the result with callback info
            return {
                "result": result,
                "callback_url": callback_url,
                "execution_mode": "callback",
                "callback_sent": True  # Would be actual status
            }

    # Helper methods
    def _extract_function_parameters(self, function_definition):
        """Extract parameters from function definition."""
        try:
            namespace = {}
            exec(function_definition, namespace)
            
            # Find the first function
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    sig = inspect.signature(obj)
                    params = {}
                    
                    for param_name, param in sig.parameters.items():
                        param_info = {
                            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                            "required": param.default == inspect.Parameter.empty,
                            "default": param.default if param.default != inspect.Parameter.empty else None
                        }
                        params[param_name] = param_info
                    
                    return params
                    
        except Exception:
            pass
        
        return {}

    def _extract_return_type(self, function_definition):
        """Extract return type from function definition."""
        try:
            namespace = {}
            exec(function_definition, namespace)
            
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    sig = inspect.signature(obj)
                    return str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "any"
                    
        except Exception:
            pass
        
        return "any"

    def _extract_function_description(self, function_definition):
        """Extract docstring from function definition."""
        try:
            namespace = {}
            exec(function_definition, namespace)
            
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    return obj.__doc__ or ""
                    
        except Exception:
            pass
        
        return ""

    def _validate_parameter_type(self, value, expected_type):
        """Validate parameter type."""
        type_mapping = {
            "str": str,
            "string": str,
            "int": int,
            "integer": int,
            "float": float,
            "bool": bool,
            "boolean": bool,
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict
        }
        
        expected_type_lower = expected_type.lower()
        if expected_type_lower in type_mapping:
            return isinstance(value, type_mapping[expected_type_lower])
        
        return True  # Unknown types pass validation

    def _validate_type_match(self, value, expected_type):
        """Check if value matches expected type."""
        return self._validate_parameter_type(value, expected_type)

    async def _execute_python_function(self, function_info, args, timeout):
        """Execute Python function."""
        # This is a simplified implementation
        # In practice, you'd want proper sandboxing
        
        namespace = {}
        exec(function_info["definition"], namespace)
        
        # Find the function
        for name, obj in namespace.items():
            if callable(obj) and not name.startswith('_'):
                if asyncio.iscoroutinefunction(obj):
                    return await asyncio.wait_for(obj(**args), timeout=timeout)
                else:
                    return obj(**args)
        
        raise ValueError("No callable function found")

    async def _execute_external_function(self, function_info, args, timeout):
        """Execute external function (subprocess, etc.)."""
        # Placeholder for external function execution
        raise NotImplementedError("External function execution not implemented")

    async def _execute_api_function(self, function_info, args, timeout):
        """Execute API function call."""
        # Placeholder for API function calls
        raise NotImplementedError("API function execution not implemented")

    def _parse_openai_function_calls(self, text):
        """Parse OpenAI format function calls."""
        import re
        import json
        
        calls = []
        # Look for function call patterns
        pattern = r'function_call.*?"name":\s*"([^"]+)".*?"arguments":\s*"([^"]*)"'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                function_name = match.group(1)
                args_str = match.group(2)
                arguments = json.loads(args_str) if args_str else {}
                
                calls.append({
                    "function_name": function_name,
                    "arguments": arguments,
                    "format": "openai"
                })
            except:
                continue
        
        return calls

    def _parse_json_function_calls(self, text):
        """Parse JSON format function calls."""
        import re
        import json
        
        calls = []
        # Look for JSON objects with function_name and arguments
        json_pattern = r'\{[^{}]*"function_name"[^{}]*\}'
        matches = re.finditer(json_pattern, text)
        
        for match in matches:
            try:
                call_obj = json.loads(match.group(0))
                if "function_name" in call_obj:
                    calls.append({
                        "function_name": call_obj["function_name"],
                        "arguments": call_obj.get("arguments", {}),
                        "format": "json"
                    })
            except:
                continue
        
        return calls

    def _parse_anthropic_function_calls(self, text):
        """Parse Anthropic format function calls."""
        # Placeholder for Anthropic-specific parsing
        return []

    def _get_last_execution_info(self, function_name):
        """Get last execution info for function."""
        for call in reversed(self.call_history):
            if call["function_name"] == function_name:
                return {
                    "execution_time": call.get("execution_time"),
                    "timestamp": call.get("timestamp"),
                    "success": call.get("success")
                }
        return None

    def _generate_function_examples(self, function_info):
        """Generate example function calls."""
        examples = []
        params = function_info["parameters"]
        
        if params:
            example_args = {}
            for param_name, param_info in params.items():
                if param_info.get("required", False):
                    # Generate example value based on type
                    param_type = param_info.get("type", "string")
                    if param_type in ["string", "str"]:
                        example_args[param_name] = f"example_{param_name}"
                    elif param_type in ["integer", "int"]:
                        example_args[param_name] = 42
                    elif param_type in ["boolean", "bool"]:
                        example_args[param_name] = True
                    else:
                        example_args[param_name] = f"example_{param_name}"
            
            examples.append({
                "description": "Basic example",
                "arguments": example_args
            })
        
        return examples

    def _generate_markdown_docs(self, func_name, function_info, include_examples):
        """Generate markdown documentation."""
        doc = f"# {func_name}\n\n"
        doc += f"{function_info.get('description', 'No description available')}\n\n"
        
        doc += "## Parameters\n\n"
        for param_name, param_info in function_info["parameters"].items():
            required = "**Required**" if param_info.get("required") else "Optional"
            doc += f"- `{param_name}` ({param_info.get('type', 'any')}) - {required}\n"
        
        if include_examples:
            examples = self._generate_function_examples(function_info)
            if examples:
                doc += "\n## Examples\n\n"
                for example in examples:
                    doc += f"```json\n{json.dumps(example['arguments'], indent=2)}\n```\n\n"
        
        return doc

    def _generate_json_docs(self, func_name, function_info, include_examples):
        """Generate JSON documentation."""
        doc = {
            "name": func_name,
            "description": function_info.get("description", ""),
            "parameters": function_info["parameters"],
            "return_type": function_info.get("return_type", "any")
        }
        
        if include_examples:
            doc["examples"] = self._generate_function_examples(function_info)
        
        return doc

    def _generate_openapi_docs(self, func_name, function_info):
        """Generate OpenAPI documentation."""
        # Simplified OpenAPI schema
        return {
            "operationId": func_name,
            "summary": function_info.get("description", ""),
            "parameters": [
                {
                    "name": param_name,
                    "in": "query",
                    "required": param_info.get("required", False),
                    "schema": {"type": param_info.get("type", "string")}
                }
                for param_name, param_info in function_info["parameters"].items()
            ]
        }

    def _categorize_error(self, error):
        """Categorize error type."""
        error_type = type(error).__name__
        
        if error_type in ["TypeError", "AttributeError"]:
            return "type_error"
        elif error_type in ["ValueError", "KeyError"]:
            return "parameter_error"
        elif error_type in ["TimeoutError", "asyncio.TimeoutError"]:
            return "timeout_error"
        elif error_type in ["ConnectionError", "HTTPError"]:
            return "network_error"
        else:
            return "unknown_error"

    def _generate_error_suggestions(self, error, category, function_name):
        """Generate suggestions for error resolution."""
        suggestions = []
        
        if category == "parameter_error":
            suggestions.append("Check parameter names and types")
            suggestions.append("Verify required parameters are provided")
        elif category == "timeout_error":
            suggestions.append("Increase timeout value")
            suggestions.append("Check function performance")
        elif category == "network_error":
            suggestions.append("Check network connectivity")
            suggestions.append("Verify API endpoints")
        
        return suggestions

    def _is_error_recoverable(self, error, category):
        """Check if error is recoverable."""
        recoverable_categories = ["timeout_error", "network_error"]
        return category in recoverable_categories

    def _create_logging_wrapper(self, function_info, config):
        """Create logging wrapper for function."""
        # Simplified wrapper creation
        wrapped_info = function_info.copy()
        wrapped_info["wrapper"] = {"type": "logging", "config": config}
        return wrapped_info

    def _create_retry_wrapper(self, function_info, config):
        """Create retry wrapper for function."""
        wrapped_info = function_info.copy()
        wrapped_info["wrapper"] = {"type": "retry", "config": config}
        return wrapped_info

    def _create_timeout_wrapper(self, function_info, config):
        """Create timeout wrapper for function."""
        wrapped_info = function_info.copy()
        wrapped_info["wrapper"] = {"type": "timeout", "config": config}
        return wrapped_info

    def _create_validation_wrapper(self, function_info, config):
        """Create validation wrapper for function."""
        wrapped_info = function_info.copy()
        wrapped_info["wrapper"] = {"type": "validation", "config": config}
        return wrapped_info

    def _generate_mock_result(self, function_info):
        """Generate mock result based on function return type."""
        return_type = function_info.get("return_type", "any")
        
        if return_type in ["string", "str"]:
            return "mock_string_result"
        elif return_type in ["integer", "int"]:
            return 42
        elif return_type in ["boolean", "bool"]:
            return True
        elif return_type in ["list", "array"]:
            return ["mock", "list", "result"]
        elif return_type in ["dict", "object"]:
            return {"mock": "object", "result": True}
        else:
            return "mock_result"

    def _estimate_execution_metrics(self, function_info, args):
        """Estimate execution metrics."""
        # Simplified estimation
        return {
            "estimated_time": "< 1 second",
            "memory_usage": "low",
            "complexity": "O(1)"
        }

    def _substitute_chain_variables(self, args, mapping, context):
        """Substitute variables in function arguments."""
        substituted = {}
        
        for key, value in args.items():
            if isinstance(value, str) and value.startswith("$"):
                var_name = value[1:]
                if var_name in context:
                    substituted[key] = context[var_name]
                else:
                    substituted[key] = value
            else:
                substituted[key] = value
        
        return substituted

    def _evaluate_chain_condition(self, condition, context):
        """Evaluate chain condition."""
        # Simplified condition evaluation
        # In practice, you'd want a proper expression evaluator
        try:
            return eval(condition, {"context": context})
        except:
            return True

    def _analyze_performance_patterns(self):
        """Analyze performance patterns from usage stats."""
        patterns = {}
        
        for func_name, stats in self.function_usage_stats.items():
            patterns[func_name] = {
                "average_time": stats["average_execution_time"],
                "call_frequency": stats["total_calls"],
                "success_rate": stats["successful_calls"] / max(stats["total_calls"], 1)
            }
        
        return patterns

    def _analyze_caching_opportunities(self):
        """Analyze caching opportunities."""
        opportunities = {}
        
        for func_name, info in self.function_registry.items():
            # Simple heuristic: functions with no side effects are cacheable
            if "read" in func_name.lower() or "get" in func_name.lower():
                opportunities[func_name] = {"cacheable": True, "reason": "read operation"}
            else:
                opportunities[func_name] = {"cacheable": False, "reason": "potential side effects"}
        
        return opportunities

    def _analyze_batching_opportunities(self):
        """Analyze batching opportunities."""
        opportunities = {}
        
        # Look for functions that are called frequently in sequence
        recent_calls = self.call_history[-100:]  # Last 100 calls
        function_sequences = {}
        
        for i in range(len(recent_calls) - 1):
            current_func = recent_calls[i]["function_name"]
            next_func = recent_calls[i + 1]["function_name"]
            
            if current_func == next_func:
                if current_func not in function_sequences:
                    function_sequences[current_func] = 0
                function_sequences[current_func] += 1
        
        for func_name, count in function_sequences.items():
            if count > 5:  # Threshold for batching opportunity
                opportunities[func_name] = {
                    "batchable": True,
                    "sequence_count": count,
                    "potential_savings": f"{count * 0.1:.2f}s"
                }
        
        return opportunities

    def _generate_optimization_recommendations(self, analysis):
        """Generate optimization recommendations."""
        recommendations = []
        
        # Performance recommendations
        if "performance" in analysis:
            for func_name, metrics in analysis["performance"].items():
                if metrics["average_time"] > 5:  # > 5 seconds
                    recommendations.append({
                        "type": "performance",
                        "function": func_name,
                        "issue": "slow execution",
                        "recommendation": "Consider optimizing function implementation"
                    })
        
        # Caching recommendations
        if "caching" in analysis:
            for func_name, cache_info in analysis["caching"].items():
                if cache_info["cacheable"]:
                    recommendations.append({
                        "type": "caching",
                        "function": func_name,
                        "recommendation": "Enable caching for this function"
                    })
        
        return recommendations

    def _validate_params(self, operation: str, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        required_params = {
            FunctionCallingOperation.DEFINE_FUNCTION: ["function_name", "function_definition"],
            FunctionCallingOperation.CALL_FUNCTION: ["function_name"],
            FunctionCallingOperation.VALIDATE_PARAMETERS: ["function_name", "parameters"],
            FunctionCallingOperation.GET_FUNCTION_SCHEMA: ["function_name"],
            FunctionCallingOperation.LIST_FUNCTIONS: [],
            FunctionCallingOperation.PARSE_FUNCTION_CALL: ["text"],
            FunctionCallingOperation.FORMAT_FUNCTION_RESPONSE: ["function_name", "result"],
            FunctionCallingOperation.EXECUTE_BATCH_CALLS: ["function_calls"],
            FunctionCallingOperation.VALIDATE_FUNCTION_DEFINITION: ["function_definition"],
            FunctionCallingOperation.GENERATE_FUNCTION_DOCS: [],
            FunctionCallingOperation.MAP_PARAMETERS: ["function_name", "input_data"],
            FunctionCallingOperation.HANDLE_FUNCTION_ERROR: ["error"],
            FunctionCallingOperation.CREATE_FUNCTION_WRAPPER: ["function_name"],
            FunctionCallingOperation.SIMULATE_FUNCTION_CALL: ["function_name"],
            FunctionCallingOperation.TRACK_FUNCTION_USAGE: ["function_name"],
            FunctionCallingOperation.COMPOSE_FUNCTION_CHAIN: ["function_chain"],
            FunctionCallingOperation.VALIDATE_RETURN_TYPE: ["function_name", "return_value"],
            FunctionCallingOperation.CREATE_FUNCTION_LIBRARY: ["library_name", "functions"],
            FunctionCallingOperation.OPTIMIZE_FUNCTION_CALLS: [],
            FunctionCallingOperation.HANDLE_ASYNC_FUNCTIONS: ["function_name"],
        }

        if operation in required_params:
            for param in required_params[operation]:
                if param not in params:
                    raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="FunctionCallingNode",
            description="Function calling integration for LLM workflows",
            version="1.0.0",
            icon_path="⚙️",
            auth_params=[],
            parameters=[
                NodeParameter(
                    name="function_name",
                    param_type=NodeParameterType.STRING,
                    required=True,
                    description="Name of the function to define or call"
                ),
                NodeParameter(
                    name="function_definition",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Python code defining the function"
                ),
                NodeParameter(
                    name="function_args",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Arguments to pass to the function"
                ),
                NodeParameter(
                    name="function_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of function: python, external, api"
                ),
                NodeParameter(
                    name="timeout",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Execution timeout in seconds"
                ),
                NodeParameter(
                    name="parameters",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Function parameters for validation"
                ),
                NodeParameter(
                    name="text",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Text containing function calls to parse"
                ),
                NodeParameter(
                    name="format_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Format type: json, text, openai, anthropic"
                ),
                NodeParameter(
                    name="result",
                    param_type=NodeParameterType.ANY,
                    required=False,
                    description="Function result to format"
                ),
                NodeParameter(
                    name="function_calls",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Array of function calls for batch execution"
                ),
                NodeParameter(
                    name="parallel_execution",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Execute batch calls in parallel"
                ),
                NodeParameter(
                    name="include_examples",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Include examples in documentation"
                ),
                NodeParameter(
                    name="input_data",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Input data to map to function parameters"
                ),
                NodeParameter(
                    name="mapping_rules",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Explicit parameter mapping rules"
                ),
                NodeParameter(
                    name="wrapper_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of wrapper: logging, retry, timeout, validation"
                ),
                NodeParameter(
                    name="simulation_mode",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Simulation mode: mock, dry_run, estimate"
                ),
                NodeParameter(
                    name="function_chain",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Chain of function calls to compose"
                ),
                NodeParameter(
                    name="chain_mode",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Chain execution mode: sequential, parallel, conditional"
                ),
                NodeParameter(
                    name="return_value",
                    param_type=NodeParameterType.ANY,
                    required=False,
                    description="Return value to validate against expected type"
                ),
                NodeParameter(
                    name="expected_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Expected return type for validation"
                ),
                NodeParameter(
                    name="library_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of the function library to create"
                ),
                NodeParameter(
                    name="functions",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Array of function definitions for library"
                ),
                NodeParameter(
                    name="optimization_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of optimization: performance, caching, batching"
                ),
                NodeParameter(
                    name="execution_mode",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Async execution mode: await, background, callback"
                )
            ]
        )