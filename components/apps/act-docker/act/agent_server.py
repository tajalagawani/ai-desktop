# act/agent_server.py - Complete Agent Server with Robust Parameter Handling
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os # For environment variable access
import re # For more robust placeholder resolution

logger = logging.getLogger(__name__)

class AgentServer:
    """Complete Agent Server with Dynamic Route Discovery and Workflow Execution."""

    def __init__(self, execution_manager, config: Dict[str, Any], deployment: Dict[str, Any]):
        self.execution_manager = execution_manager
        self.config = config # Agent server's own config (host, port, etc.)
        self.deployment = deployment # Deployment specific config
        self.app: Optional[Flask] = None
        self.dynamic_routes: Dict[str, Dict[str, Any]] = {}
        self.agent_status: str = "initializing"
        self.aci_nodes: List[Dict[str, Any]] = [] # List of ACI node definitions from Actfile
        self.edges: Dict[str, List[str]] = {}    # Workflow edges: {source_node_id: [target_node_id, ...]}
        self.all_nodes: Dict[str, Dict[str, Any]] = {} # All node definitions from Actfile: {node_id: node_config}
        self.resolved_parameters: Dict[str, Any] = {} # Globally resolved parameters from Actfile [parameters]

        self._initialize_resolved_parameters() # Must be called first
        self._discover_all_components() # Depends on resolved_parameters for some node configs

    def _initialize_resolved_parameters(self):
        """
        Initializes self.resolved_parameters from the Actfile's [parameters] section.
        This method MUST accurately reflect how the main ExecutionManager resolves
        parameters, including environment variable substitution (e.g., ${ENV_VAR}).
        """
        logger.debug("AgentServer: Initializing resolved parameters...")
        try:
            # Prioritize getting parameters from the execution_manager if it has a dedicated method
            if hasattr(self.execution_manager, 'get_global_resolved_parameters'): # Ideal custom method
                self.resolved_parameters = self.execution_manager.get_global_resolved_parameters()
                logger.debug(f"AgentServer: Loaded resolved parameters via get_global_resolved_parameters(): {list(self.resolved_parameters.keys())}")
            elif hasattr(self.execution_manager, 'actfile_parser') and \
                 hasattr(self.execution_manager.actfile_parser, 'get_resolved_parameters'):
                self.resolved_parameters = self.execution_manager.actfile_parser.get_resolved_parameters()
                logger.debug(f"AgentServer: Loaded resolved parameters from actfile_parser.get_resolved_parameters(): {list(self.resolved_parameters.keys())}")
            elif hasattr(self.execution_manager, 'resolved_parameters'): # If ExecutionManager stores them directly
                self.resolved_parameters = self.execution_manager.resolved_parameters
                logger.debug(f"AgentServer: Loaded resolved parameters directly from ExecutionManager.resolved_parameters: {list(self.resolved_parameters.keys())}")
            elif hasattr(self.execution_manager, 'actfile_parser') and \
                 hasattr(self.execution_manager.actfile_parser, 'parsed_data'):
                # Fallback: Manually resolve from raw [parameters] in parsed_data
                logger.warning("AgentServer: Attempting fallback for parameter resolution. This only handles ${ENV_VAR} directly.")
                raw_params = self.execution_manager.actfile_parser.parsed_data.get('parameters', {})
                temp_resolved_params = {}
                for key, value_template in raw_params.items():
                    if isinstance(value_template, str) and value_template.startswith("${") and value_template.endswith("}"):
                        env_var_name = value_template[2:-1]
                        env_val = os.getenv(env_var_name)
                        if env_val is not None:
                            temp_resolved_params[key] = env_val
                            logger.debug(f"AgentServer: Resolved global param '{key}' from env var '{env_var_name}'.")
                        else:
                            temp_resolved_params[key] = value_template # Keep placeholder if env var not found
                            logger.warning(f"AgentServer: Env var '{env_var_name}' for global param '{key}' not found. Using literal placeholder.")
                    else:
                        temp_resolved_params[key] = value_template # Value is not an env var placeholder
                self.resolved_parameters = temp_resolved_params
                logger.debug(f"AgentServer: Fallback parameter resolution complete. Resolved: {list(self.resolved_parameters.keys())}")
            else:
                logger.error("AgentServer: CRITICAL - Could not obtain global parameters. Placeholder {{.Parameter.xxx}} resolution will fail.")
            
            # Log final resolved parameters for verification
            if self.resolved_parameters:
                logger.debug(f"AgentServer: Final initialized global parameters: {json.dumps(self.resolved_parameters,default=str,indent=2)}")
            else:
                logger.warning("AgentServer: No global parameters were resolved or found.")

        except Exception as e:
            logger.error(f"AgentServer: Error initializing resolved parameters: {e}", exc_info=True)

    def _discover_all_components(self):
        """Discover all workflow nodes, edges, and ACI route definitions."""
        try:
            self._discover_nodes()
            self._discover_edges()
            self._discover_aci_nodes() # Depends on self.all_nodes
            logger.debug(f"🔍 Discovery complete: {len(self.all_nodes)} nodes, {len(self.aci_nodes)} ACI routes, {len(self.edges)} edges.")
        except Exception as e:
            logger.error(f"Error during component discovery: {e}", exc_info=True)

    def _discover_nodes(self):
        """Discover all node configurations from the Actfile."""
        try:
            if hasattr(self.execution_manager, 'actfile_parser'):
                parser = self.execution_manager.actfile_parser
                if hasattr(parser, 'get_all_nodes'): # Ideal method
                    self.all_nodes = parser.get_all_nodes() or {}
                elif hasattr(parser, 'parsed_data'): # Fallback to raw parsed data
                    parsed_data = parser.parsed_data
                    temp_nodes = {}
                    for section_name, section_data in parsed_data.items():
                        if section_name.startswith('node:'):
                            node_id = section_name.replace('node:', '')
                            temp_nodes[node_id] = dict(section_data) # Ensure it's a dict
                    self.all_nodes = temp_nodes
                logger.debug(f"📋 Discovered {len(self.all_nodes)} total nodes from Actfile.")
            else:
                logger.warning("Node discovery skipped: execution_manager missing 'actfile_parser'.")
        except Exception as e:
            logger.error(f"Error discovering nodes: {e}", exc_info=True)

    def _discover_edges(self):
        """Discover workflow edge configurations from the Actfile."""
        try:
            if hasattr(self.execution_manager, 'actfile_parser') and \
               hasattr(self.execution_manager.actfile_parser, 'parsed_data'):
                parsed_data = self.execution_manager.actfile_parser.parsed_data
                if 'edges' in parsed_data:
                    edges_data = parsed_data['edges'] # Should be a dict from parser
                    temp_edges = {}
                    for source_node, targets in edges_data.items():
                        if isinstance(targets, str): # Handle single target string
                            # If targets can be comma-separated string "nodeA,nodeB"
                            temp_edges[source_node] = [t.strip() for t in targets.split(',') if t.strip()]
                        elif isinstance(targets, list): # Handle list of targets
                            temp_edges[source_node] = [str(t).strip() for t in targets if str(t).strip()]
                        else: # Handle other types by converting to string list
                            temp_edges[source_node] = [str(targets).strip()] if str(targets).strip() else []
                        logger.debug(f"🔗 Discovered Edge: {source_node} → {temp_edges[source_node]}")
                    self.edges = temp_edges
                    logger.debug(f"🔗 Discovered {len(self.edges)} edge definitions.")
            else:
                logger.warning("Edge discovery skipped: no parsed_data or 'edges' section.")
        except Exception as e:
            logger.error(f"Error discovering edges: {e}", exc_info=True)

    def _discover_aci_nodes(self):
        """Discover ACI nodes intended for API route creation from all_nodes."""
        if not self.all_nodes:
            logger.warning("ACI node discovery skipped: no nodes loaded into self.all_nodes.")
            return
        try:
            temp_aci_nodes: List[Dict[str, Any]] = []
            for node_id, node_config in self.all_nodes.items():
                if isinstance(node_config, dict) and node_config.get('type') == 'aci':
                    # 'params' might be a sub-dict or parameters might be at root of node_config
                    node_params_block = node_config.get('params', {}) # Params sub-dictionary
                    
                    # Get operation from root of node_config or from its 'params' block
                    operation = node_config.get('operation') or node_params_block.get('operation')
                    
                    if operation == 'add_route':
                        route_path = node_config.get('route_path') or node_params_block.get('route_path')
                        methods_raw = node_config.get('methods') or node_params_block.get('methods', ['GET'])
                        handler_name = node_config.get('handler') or node_params_block.get('handler') # Logical name
                        
                        # Normalize methods to list of uppercase strings
                        methods_list: List[str] = []
                        if isinstance(methods_raw, str):
                            # Try parsing as JSON list string, then comma-separated, then single item
                            if methods_raw.startswith('[') and methods_raw.endswith(']'):
                                try: methods_list = [str(m).strip().upper() for m in json.loads(methods_raw)]
                                except json.JSONDecodeError: methods_list = [m.strip().upper() for m in methods_raw.split(',') if m.strip()]
                            else:
                                methods_list = [m.strip().upper() for m in methods_raw.split(',') if m.strip()]
                        elif isinstance(methods_raw, list):
                            methods_list = [str(m).strip().upper() for m in methods_raw if str(m).strip()]
                        
                        if not methods_list: methods_list = ['GET'] # Default if parsing failed or empty

                        if route_path and handler_name:
                            temp_aci_nodes.append({
                                'node_id': node_id, # The ID of this ACI node definition
                                'route_path': str(route_path),
                                'methods': methods_list,
                                'handler': str(handler_name),
                                'description': str(node_config.get('description', '')),
                                'node_config_original': dict(node_config), # Store original for _prepare_node_data
                                'auth_required': node_config.get('auth_required', False) or node_params_block.get('auth_required', False),
                                'rate_limit': node_config.get('rate_limit') or node_params_block.get('rate_limit')
                            })
                            logger.debug(f"✅ DISCOVERED ACI Add_Route: {methods_list} {route_path} -> Handler: {handler_name} (ACI Node ID: {node_id})")
                        else:
                            logger.warning(f"⚠️ ACI add_route node '{node_id}' missing route_path or handler name.")
            self.aci_nodes = temp_aci_nodes
            logger.debug(f"🔎 ACI route discovery complete. Found {len(self.aci_nodes)} route definitions.")
        except Exception as e:
            logger.error(f"Error discovering ACI (add_route) nodes: {e}", exc_info=True)

    def _resolve_placeholder(self, value_template: Any, resolution_context: Dict[str, Any]) -> Any:
        """
        Resolves placeholders in a string value_template.
        - {{.Parameter.global_param_name}}
        - {{request_data.key_from_http_request}}
        - {{PreviousNodeID.result.key_from_output}} (or .data.key)
        """
        if not isinstance(value_template, str) or "{{" not in value_template:
            return value_template # Not a string or no placeholders

        # Regex to find {{ placeholder_expression }}
        placeholder_pattern = re.compile(r"\{\{\s*(.*?)\s*\}\}")

        def replace_match(match):
            expression = match.group(1).strip()
            keys = expression.split('.')
            current_value: Any = None
            
            # 1. Try {{.Parameter.xxx}} - Global parameters
            if keys[0] == "" and len(keys) > 1 and keys[1] == "Parameter":
                param_name = '.'.join(keys[2:])
                if param_name in self.resolved_parameters:
                    logger.debug(f"Resolving global param placeholder '{{{{.{expression}}}}}' to value for '{param_name}'.")
                    return self.resolved_parameters[param_name]
                else:
                    logger.warning(f"Global parameter '{param_name}' not found for placeholder '{{{{.{expression}}}}}'.")
                    return match.group(0) # Return original placeholder string

            # 2. Try other contexts (request_data, previous node outputs stored in resolution_context)
            # resolution_context might contain {'request_data': {...}, 'NodeA_ID': {'result':{...}, 'data':{...}}}
            source_key = keys[0]
            if source_key in resolution_context:
                current_value = resolution_context[source_key]
                path_keys_to_traverse = keys[1:]
            else: # If not a known context key, it might be an implicit node ID
                if source_key in self.all_nodes and source_key in resolution_context: # Check if it's a node ID with data
                     current_value = resolution_context[source_key]
                     path_keys_to_traverse = keys[1:] # e.g. for {{NodeID.result.value}}
                else:
                    logger.warning(f"Top-level key '{source_key}' for placeholder '{{{{{expression}}}}}' not in resolution_context or not a known node with prior output.")
                    return match.group(0)

            # Traverse the path (e.g., result.data_item[0].name)
            for key_part in path_keys_to_traverse:
                # Handle list indexing like "items[0]"
                list_idx_match = re.fullmatch(r"(\w+)\[(\d+)\]", key_part)
                if list_idx_match:
                    item_key, idx_str = list_idx_match.groups()
                    idx = int(idx_str)
                    if isinstance(current_value, dict) and item_key in current_value and isinstance(current_value[item_key], list):
                        if 0 <= idx < len(current_value[item_key]):
                            current_value = current_value[item_key][idx]
                            continue
                        else: logger.warning(f"Index {idx} out of bounds for list '{item_key}' in placeholder '{{{{{expression}}}}}'."); return match.group(0)
                    else: logger.warning(f"Cannot apply index '{key_part}' to non-list or missing key in placeholder '{{{{{expression}}}}}'."); return match.group(0)
                
                # Handle direct dict key or object attribute
                if isinstance(current_value, dict) and key_part in current_value:
                    current_value = current_value[key_part]
                elif hasattr(current_value, key_part) and not key_part.startswith('_'): # Avoid private attrs
                    current_value = getattr(current_value, key_part)
                else:
                    logger.warning(f"Key/attribute '{key_part}' not found in path for placeholder '{{{{{expression}}}}}'. Current object type: {type(current_value)}")
                    return match.group(0)
            
            # If the resolved value is complex (dict/list), for simple string templates, often stringified.
            # If the whole template was just one placeholder, return the native type.
            if isinstance(current_value, (dict, list)) and match.group(0) != value_template: # Part of a larger string
                 return json.dumps(current_value, default=str)
            return current_value if current_value is not None else "" # Avoid returning None in strings

        # Check if the entire string is a single placeholder
        single_placeholder_match = placeholder_pattern.fullmatch(value_template)
        if single_placeholder_match:
            # If so, try to return the native type of the resolved value
            resolved_single = replace_match(single_placeholder_match)
            # Check if it actually resolved to something other than the original placeholder string
            if resolved_single != single_placeholder_match.group(0) or not isinstance(resolved_single, str):
                return resolved_single
            else: # It resolved to a string that happened to be the same as the placeholder (e.g. key not found)
                return resolved_single # Which is the original placeholder string in this case

        # Otherwise, substitute all occurrences in the string
        return placeholder_pattern.sub(replace_match, value_template)


    def _prepare_node_data(self, node_id_to_execute: str, original_node_config: Dict[str, Any],
                           http_request_data: Dict[str, Any], http_method: str,
                           prior_workflow_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares the input data dictionary for a node executor.
        Resolves placeholders in the node's configuration using global parameters,
        HTTP request data, and outputs from prior nodes in the ACI chain.
        """
        logger.debug(f"Preparing data for node '{node_id_to_execute}'. Original config: {original_node_config}")

        # Context for placeholder resolution:
        # 1. Outputs from prior nodes in this ACI-triggered workflow chain.
        # 2. HTTP request data (URL params, query params, body) under 'request_data' key.
        # 3. Global parameters are handled by {{.Parameter.xxx}} pattern in _resolve_placeholder.
        resolution_context = prior_workflow_outputs.copy() # e.g., {'PreviousNodeID': {'result': ..., 'data': ...}}
        resolution_context['request_data'] = http_request_data # e.g., {'workflow_id_from_url': 'abc', 'name': 'test'}

        # Build the 'params' dictionary for the node executor
        # by resolving placeholders in the original_node_config values.
        # original_node_config is from self.all_nodes[node_id_to_execute]
        resolved_params_for_executor: Dict[str, Any] = {}
        for key, value_template in original_node_config.items():
            # Skip metadata keys that are not part of 'params' for the executor
            if key in ["type", "label", "description", "node_id", "handler"]: # These are for AgentServer/Actfile
                continue
            
            # Special handling for 'parameters' if it's a list (often for SQL %s)
            if key == "parameters" and isinstance(value_template, list):
                resolved_list = []
                for item_template in value_template:
                    resolved_list.append(self._resolve_placeholder(str(item_template), resolution_context))
                resolved_params_for_executor[key] = resolved_list
                logger.debug(f"Node '{node_id_to_execute}': Resolved list parameter '{key}' to: {resolved_list}")
            else: # Standard key-value parameter
                resolved_params_for_executor[key] = self._resolve_placeholder(value_template, resolution_context)
        
        # Ensure 'connection_string' for 'neon' nodes is the actual DSN
        node_type = original_node_config.get("type")
        if node_type == "neon":
            current_cs = resolved_params_for_executor.get("connection_string")
            # If current_cs is still a placeholder {{.Parameter.connection_string}} or similar,
            # _resolve_placeholder should have handled it using self.resolved_parameters.
            # We log to confirm it's a valid DSN.
            if isinstance(current_cs, str) and ("${" in current_cs or "{{" in current_cs):
                logger.error(f"Node '{node_id_to_execute}' (neon): connection_string '{current_cs}' appears unresolved after placeholder substitution. This indicates an issue with global parameter setup or _resolve_placeholder logic for {{.Parameter...}}. Check self.resolved_parameters.")
                # As a last resort, if all resolution failed for connection_string, try direct env var.
                # This is a patch; the resolution should ideally happen cleanly via placeholders.
                fallback_dsn = os.getenv("NEON_CONNECTION_STRING")
                if fallback_dsn:
                    logger.warning(f"Node '{node_id_to_execute}': Forcing connection_string to direct NEON_CONNECTION_STRING env var value due to prior resolution failure.")
                    resolved_params_for_executor["connection_string"] = fallback_dsn
                else:
                    logger.error(f"Node '{node_id_to_execute}': NEON_CONNECTION_STRING env var also not found for fallback. Connection will fail.")
            elif not current_cs:
                 logger.error(f"Node '{node_id_to_execute}' (neon): connection_string is missing or None after resolution.")


        # Convention-based SQL 'parameters' list construction for Neon 'execute_query' with POST
        if node_type == "neon" and \
           resolved_params_for_executor.get("operation") == "execute_query" and \
           http_method == "POST":
            
            # If 'parameters' was not explicitly defined as a list in Actfile (e.g. from Solution 1)
            if not isinstance(resolved_params_for_executor.get("parameters"), list):
                parameters_order_str = original_node_config.get("parameters_order") # e.g., "key1,key2"
                if parameters_order_str:
                    expected_keys_in_order = [k.strip() for k in parameters_order_str.split(',')]
                    constructed_sql_params = []
                    all_keys_found = True
                    post_body = http_request_data # Assuming http_request_data IS the parsed POST body for POST requests
                    
                    for key_from_order in expected_keys_in_order:
                        if key_from_order in post_body:
                            constructed_sql_params.append(post_body[key_from_order])
                        else:
                            logger.warning(f"Node '{node_id_to_execute}': Expected key '{key_from_order}' (from 'parameters_order') not found in POST body {list(post_body.keys())} for SQL parameters.")
                            all_keys_found = False
                            break
                    if all_keys_found:
                        resolved_params_for_executor["parameters"] = constructed_sql_params
                        logger.debug(f"Node '{node_id_to_execute}': Constructed SQL 'parameters' from POST body using 'parameters_order': {constructed_sql_params}")
                    else:
                        logger.error(f"Node '{node_id_to_execute}': Failed to construct all SQL 'parameters' using 'parameters_order'. Setting to empty list.")
                        resolved_params_for_executor["parameters"] = []
                else:
                    logger.warning(f"Node '{node_id_to_execute}' (neon, POST, execute_query): No 'parameters_order' in Actfile and 'parameters' not a list. SQL parameters likely incorrect.")
                    if "parameters" not in resolved_params_for_executor: resolved_params_for_executor["parameters"] = []


        # For GET requests (like FetchContentForAPI) ensure 'parameters' is set if URL param exists
        elif node_type == "neon" and \
             resolved_params_for_executor.get("operation") == "execute_query" and \
             http_method == "GET":
            if not isinstance(resolved_params_for_executor.get("parameters"), list): # If not set by Actfile list template
                # Check for specific known URL parameters for this node
                # This is still a bit specific, ideally node declares its param needs
                if "workflow_id_from_url" in http_request_data and node_id_to_execute == "FetchContentForAPI":
                     resolved_params_for_executor["parameters"] = [http_request_data["workflow_id_from_url"]]
                     logger.debug(f"Node '{node_id_to_execute}': Set SQL 'parameters' from URL param: {[http_request_data['workflow_id_from_url']]}")
                elif "parameters" not in resolved_params_for_executor: # Default if nothing else
                    resolved_params_for_executor["parameters"] = []


        # Final structure expected by node executors
        final_node_input_data = {
            "type": original_node_config.get("type"),
            "label": original_node_config.get("label"),
            "description": original_node_config.get("description"),
            "params": resolved_params_for_executor # This dict contains all resolved config values
        }
        
        # Add http_method, timestamp, and full request data to params for context if nodes need it
        final_node_input_data["params"]["_http_method_"] = http_method # Use a distinct key
        final_node_input_data["params"]["_timestamp_"] = datetime.utcnow().isoformat()
        final_node_input_data["params"]["_request_data_full_"] = http_request_data

        logger.critical(f"AGENT_SERVER PREPARE FOR '{node_id_to_execute}': FINAL 'connection_string' in params: '{final_node_input_data['params'].get('connection_string')}'")
        logger.critical(f"AGENT_SERVER PREPARE FOR '{node_id_to_execute}': FINAL 'parameters' for SQL in params: {final_node_input_data['params'].get('parameters')} (type: {type(final_node_input_data['params'].get('parameters'))})")
        logger.critical(f"AGENT_SERVER PREPARE FOR '{node_id_to_execute}': FINAL 'operation' in params: '{final_node_input_data['params'].get('operation')}'")
        logger.critical(f"AGENT_SERVER PREPARE FOR '{node_id_to_execute}': ALL PARAMS KEYS: {list(final_node_input_data['params'].keys())}")
        # logger.debug(f"Full final prepared data for node '{node_id_to_execute}': {json.dumps(final_node_input_data, indent=2, default=str)}")
        return final_node_input_data

    def _execute_node(self, node_id: str, node_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a specific node using its registered executor."""
        node_type = node_input_data.get('type')
        logger.debug(f"Attempting to execute node: '{node_id}' (Type: {node_type})")
        # logger.debug(f"Node input data for execution of '{node_id}': {json.dumps(node_input_data, indent=2, default=str)}")

        try:
            if hasattr(self.execution_manager, 'node_executors') and \
               node_type in self.execution_manager.node_executors:
                executor = self.execution_manager.node_executors[node_type]
                
                if asyncio.iscoroutinefunction(executor.execute):
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                           logger.warning(f"Event loop was closed for async node {node_id}. Creating new loop.")
                           loop = asyncio.new_event_loop()
                           asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(executor.execute(node_input_data))
                    except RuntimeError as e: # "There is no current event loop in thread..."
                         logger.warning(f"RuntimeError with event loop for async node {node_id} ('{e}'). Trying new loop for this execution.")
                         new_loop = asyncio.new_event_loop()
                         try:
                             result = new_loop.run_until_complete(executor.execute(node_input_data))
                         finally:
                             new_loop.close() # Close the temporary loop
                else: # Synchronous executor
                    result = executor.execute(node_input_data)
                
                logger.debug(f"Node '{node_id}' execution result status: {result.get('status')}")
                # logger.debug(f"Full result from '{node_id}': {json.dumps(result, indent=2, default=str)}")
                return result
            else:
                logger.error(f"No executor found for node type: '{node_type}' (Node ID: '{node_id}')")
                return { "status": "error", "message": f"No executor found for node type: {node_type}" }
        except Exception as e:
            logger.error(f"Exception during execution of node '{node_id}' (Type: {node_type}): {str(e)}", exc_info=True)
            return { "status": "error", "message": f"Exception in node execution: {str(e)}" }

    def _execute_aci_workflow(self, aci_node_definition: Dict[str, Any],
                            http_request_data: Dict[str, Any], http_method: str) -> Dict[str, Any]:
        """
        Executes the COMPLETE sequence of workflow nodes connected to an ACI 'add_route' node.
        This method now properly follows the workflow chain through all connected nodes,
        not just the immediate targets.
        
        aci_node_definition: The configuration of the ACI node that defined the route.
        http_request_data: Combined data from URL parameters, query strings, and request body.
        http_method: The HTTP method of the incoming request (GET, POST, etc.).
        """
        aci_node_id = aci_node_definition['node_id']
        
        # Get the starting nodes connected to the ACI route
        starting_target_node_ids = self.edges.get(aci_node_id, [])

        if not starting_target_node_ids:
            logger.debug(f"ACI Route '{aci_node_definition.get('route_path')}' (ACI Node ID: {aci_node_id}) triggered, but no downstream workflow nodes are connected.")
            return {
                "status": "success_no_op",
                "message": f"ACI Route '{aci_node_definition.get('handler')}' handled. No workflow nodes connected to ACI node '{aci_node_id}'.",
                "data": { "request_method": http_method, "request_data_received": http_request_data },
                "workflow_executed": []
            }

        logger.debug(f"🔄 Executing ACI-triggered workflow for ACI Node ID '{aci_node_id}'. Starting nodes: {starting_target_node_ids}")
        
        # Tracking for the complete workflow execution
        executed_nodes_trace: List[Dict[str, Any]] = []
        current_aci_flow_outputs: Dict[str, Any] = {}  # Accumulates outputs from all executed nodes
        final_api_response_payload: Any = None
        overall_execution_success = True
        
        # Queue of nodes to execute - starts with immediate targets, then expands
        nodes_to_execute_queue = list(starting_target_node_ids)
        executed_node_ids = set()  # Prevent infinite loops in case of circular dependencies
        max_execution_depth = 50   # Safety limit to prevent runaway execution
        current_depth = 0
        
        # Execute nodes in workflow order, following the edges
        while nodes_to_execute_queue and current_depth < max_execution_depth:
            current_depth += 1
            current_batch_nodes = list(nodes_to_execute_queue)
            nodes_to_execute_queue.clear()
            next_batch_nodes = []
            
            logger.debug(f"🔄 Workflow Depth {current_depth}: Executing batch of {len(current_batch_nodes)} nodes: {current_batch_nodes}")
            
            for target_node_id in current_batch_nodes:
                # Skip if already executed (prevents loops)
                if target_node_id in executed_node_ids:
                    logger.debug(f"⏭️ Skipping already executed node: {target_node_id}")
                    continue
                    
                # Get node configuration
                original_target_node_config = self.all_nodes.get(target_node_id)
                if not original_target_node_config:
                    logger.warning(f"⚠️ Config for target node '{target_node_id}' not found in self.all_nodes.")
                    executed_nodes_trace.append({ 
                        "node_id": target_node_id, 
                        "status": "error_config_not_found",
                        "depth": current_depth
                    })
                    overall_execution_success = False
                    continue
                
                # Prepare input data for this node using all previous outputs
                try:
                    node_input_data = self._prepare_node_data(
                        target_node_id, 
                        original_target_node_config,
                        http_request_data, 
                        http_method, 
                        current_aci_flow_outputs
                    )
                except Exception as e:
                    logger.error(f"❌ Error preparing data for node '{target_node_id}': {e}")
                    executed_nodes_trace.append({
                        "node_id": target_node_id,
                        "type": original_target_node_config.get('type'),
                        "status": "error_data_preparation",
                        "error": str(e),
                        "depth": current_depth
                    })
                    overall_execution_success = False
                    continue
                
                # Execute the node
                logger.debug(f"🚀 Executing node '{target_node_id}' (Type: {original_target_node_config.get('type')}) at depth {current_depth}")
                node_execution_result = self._execute_node(target_node_id, node_input_data)
                
                # Track execution
                executed_node_ids.add(target_node_id)
                execution_trace_entry = {
                    "node_id": target_node_id,
                    "type": original_target_node_config.get('type'),
                    "status": node_execution_result.get('status'),
                    "depth": current_depth,
                    "execution_time": node_execution_result.get('execution_time', 0)
                }
                
                # Add error details if execution failed
                if node_execution_result.get('status') != 'success':
                    execution_trace_entry["error"] = node_execution_result.get('message', 'Unknown error')
                    overall_execution_success = False
                    logger.error(f"❌ Node '{target_node_id}' execution failed: {node_execution_result.get('message')}")
                else:
                    logger.debug(f"✅ Node '{target_node_id}' executed successfully")
                
                executed_nodes_trace.append(execution_trace_entry)
                
                # Store this node's result for use by subsequent nodes
                current_aci_flow_outputs[target_node_id] = node_execution_result
                
                # Update the final API response payload
                # Priority: 'result' from py nodes, then 'data' from db nodes, then 'result_text' from AI nodes
                if node_execution_result.get('status') == 'success':
                    if 'result' in node_execution_result and node_execution_result['result'] is not None:
                        final_api_response_payload = node_execution_result['result']
                        logger.debug(f"📝 Updated final payload from node '{target_node_id}' 'result' field")
                    elif 'data' in node_execution_result and node_execution_result['data'] is not None:
                        final_api_response_payload = node_execution_result['data']
                        logger.debug(f"📝 Updated final payload from node '{target_node_id}' 'data' field")
                    elif 'result_text' in node_execution_result and node_execution_result['result_text'] is not None:
                        # For AI nodes that return text
                        if not final_api_response_payload or not isinstance(final_api_response_payload, dict):
                            final_api_response_payload = {}
                        if isinstance(final_api_response_payload, dict):
                            final_api_response_payload['ai_explanation'] = node_execution_result['result_text']
                        logger.debug(f"📝 Added AI explanation from node '{target_node_id}' to final payload")
                
                # Find the next nodes to execute (following the workflow edges)
                if node_execution_result.get('status') == 'success':
                    next_connected_nodes = self.edges.get(target_node_id, [])
                    if next_connected_nodes:
                        logger.debug(f"🔗 Node '{target_node_id}' connects to: {next_connected_nodes}")
                        # Add to next batch, avoiding duplicates
                        for next_node in next_connected_nodes:
                            if next_node not in executed_node_ids and next_node not in next_batch_nodes:
                                next_batch_nodes.append(next_node)
                    else:
                        logger.debug(f"🏁 Node '{target_node_id}' has no outgoing connections (workflow end)")
                else:
                    # If node failed, we might still want to continue with other nodes in current batch
                    # but don't add failed node's targets to the queue
                    logger.warning(f"⚠️ Not following edges from failed node '{target_node_id}'")
            
            # Add next batch to the execution queue
            if next_batch_nodes:
                nodes_to_execute_queue.extend(next_batch_nodes)
                logger.debug(f"📋 Next batch queued: {next_batch_nodes}")
            else:
                logger.debug(f"🏁 Workflow execution complete - no more nodes to execute")
                break
        
        # Check for execution depth limit
        if current_depth >= max_execution_depth:
            logger.error(f"⚠️ Workflow execution stopped: reached maximum depth limit of {max_execution_depth}")
            overall_execution_success = False
        
        # Determine final execution status
        if overall_execution_success and executed_nodes_trace:
            final_execution_status = "success"
        elif any(n.get('status') == 'success' for n in executed_nodes_trace) and final_api_response_payload is not None:
            final_execution_status = "partial_success"
        elif executed_nodes_trace:
            final_execution_status = "error"
        else:
            final_execution_status = "error_no_nodes_executed"
        
        # Execution statistics
        total_nodes_executed = len(executed_nodes_trace)
        successful_nodes = len([n for n in executed_nodes_trace if n.get('status') == 'success'])
        total_execution_time = sum(n.get('execution_time', 0) for n in executed_nodes_trace)
        
        logger.debug(f"📊 Workflow execution summary:")
        logger.debug(f"   • Total nodes executed: {total_nodes_executed}")
        logger.debug(f"   • Successful nodes: {successful_nodes}")
        logger.debug(f"   • Execution depth reached: {current_depth}")
        logger.debug(f"   • Total execution time: {total_execution_time:.3f}s")
        logger.debug(f"   • Final status: {final_execution_status}")
        
        return {
            "status": final_execution_status,
            "message": f"ACI Workflow for '{aci_node_definition.get('handler')}' (ACI Node ID: {aci_node_id}) processed. Executed {successful_nodes}/{total_nodes_executed} nodes successfully.",
            "payload": final_api_response_payload,  # This becomes the HTTP response body
            "execution_time": total_execution_time,
            "workflow_execution_trace": executed_nodes_trace,
            "execution_statistics": {
                "total_nodes_executed": total_nodes_executed,
                "successful_nodes": successful_nodes,
                "failed_nodes": total_nodes_executed - successful_nodes,
                "execution_depth": current_depth,
                "total_execution_time": total_execution_time
            },
            # Additional debug info
            "debug_info": {
                "starting_nodes": starting_target_node_ids,
                "final_executed_nodes": list(executed_node_ids),
                "workflow_edges_used": {node_id: self.edges.get(node_id, []) for node_id in executed_node_ids}
            } if logger.isEnabledFor(logging.DEBUG) else None
        }

    def create_app(self) -> Flask:
        """Creates and configures the Flask application with all routes."""
        app = Flask(__name__)
        if self.config.get("cors_enabled", True):
            CORS(app) # Enable CORS for all routes if configured
        
        # Register standard/fixed routes
        self._add_health_routes(app)
        self._add_admin_routes(app)
        self._add_api_routes(app) # General API info routes
        self._add_aci_base_routes(app) # Informational ACI routes

        # Dynamically register routes defined by ACI 'add_route' nodes
        self._auto_register_aci_routes(app)
        
        self.app = app
        self.agent_status = "ready"
        logger.debug("Flask app created and all routes (standard and dynamic ACI) registered.")
        return app

    def _auto_register_aci_routes(self, app: Flask):
        """
        Discovers ACI nodes with 'operation: add_route' in the Actfile
        and registers them as dynamic Flask routes.
        """
        if not self.aci_nodes: # self.aci_nodes is populated by _discover_aci_nodes
            logger.debug("No ACI 'add_route' definitions found in Actfile. No dynamic API routes to register.")
            return

        logger.debug(f"🔧 Attempting to register {len(self.aci_nodes)} ACI-defined Flask routes...")
        for aci_node_definition_from_discovery in self.aci_nodes:
            try:
                route_path = aci_node_definition_from_discovery['route_path']
                methods = aci_node_definition_from_discovery['methods'] # Should be list of uppercase strings
                handler_name_logical = aci_node_definition_from_discovery['handler'] # For logging/display
                aci_node_id_in_actfile = aci_node_definition_from_discovery['node_id']

                # Closure to capture current aci_node_definition_from_discovery for each route's view function
                def create_flask_view_function(current_aci_node_def_captured):
                    # This function becomes the view_func for Flask's app.add_url_rule
                    def dynamic_aci_flask_handler(*args, **flask_url_kwargs):
                        # flask_url_kwargs contains URL parameters like <string:workflow_id_from_url>
                        # args would be for non-keyword URL parameters (less common with Flask named params)
                        
                        logger.debug(f"ACI Route Hit: {request.method} {request.path}. URL Params: {flask_url_kwargs}")
                        
                        # Combine all incoming HTTP data sources
                        combined_http_data: Dict[str, Any] = {}
                        combined_http_data.update(dict(request.args))  # Query string parameters
                        combined_http_data.update(flask_url_kwargs)   # URL path parameters
                        
                        # Handle request body for relevant methods
                        if request.method in ['POST', 'PUT', 'PATCH']:
                            content_type = request.headers.get('Content-Type', '').lower()
                            if 'application/json' in content_type:
                                try: combined_http_data.update(request.get_json(silent=True) or {})
                                except Exception as e: logger.warning(f"Could not parse JSON request body for {request.path}: {e}")
                            elif 'application/x-www-form-urlencoded' in content_type:
                                try: combined_http_data.update(dict(request.form))
                                except Exception as e: logger.warning(f"Could not parse form data for {request.path}: {e}")
                            # Add handling for other content types like multipart/form-data if needed
                        
                        logger.debug(f"Combined HTTP data for ACI handler: {combined_http_data}")

                        # Execute the ACI-triggered workflow chain
                        # Pass the definition of the ACI node itself, and the combined HTTP data
                        execution_result = self._execute_aci_workflow(
                            current_aci_node_def_captured, # The ACI node's own config (route_path, handler name, etc.)
                            combined_http_data,            # Data from the HTTP request
                            request.method                 # The HTTP method used
                        )
                        
                        # Determine HTTP status code for the Flask response
                        response_http_status = 200
                        if execution_result.get("status", "").startswith("error"): response_http_status = 500
                        elif execution_result.get("status") == "partial_failure": response_http_status = 207 # Multi-Status
                        elif execution_result.get("status") == "success_no_op": response_http_status = 200 # Or 204 No Content if no body

                        # Return a structured JSON response from Flask
                        return jsonify({
                            "agent_name": self.config.get("agent_name", "ACT_Agent"),
                            "route_handler_name": current_aci_node_def_captured.get('handler'),
                            "aci_node_id_defining_route": current_aci_node_def_captured.get('node_id'),
                            "request_timestamp": datetime.utcnow().isoformat(),
                            "execution_outcome": execution_result.get("status"),
                            "message": execution_result.get("message"),
                            "payload": execution_result.get("payload"), # The main data from the workflow
                            "workflow_execution_trace": execution_result.get("workflow_executed")
                        }), response_http_status
                    
                    # Set a unique name for the Flask endpoint function for clarity in Flask's internals
                    dynamic_aci_flask_handler.__name__ = f"aci_view_{aci_node_id_in_actfile}_{'_'.join(methods).lower()}"
                    return dynamic_aci_flask_handler

                # Create the specific view function for this route using the closure
                flask_view_function = create_flask_view_function(aci_node_definition_from_discovery)
                
                # Register the URL rule with Flask
                app.add_url_rule(
                    route_path,
                    endpoint=f"aci_dynamic_endpoint_{aci_node_id_in_actfile}", # Must be unique for Flask
                    view_func=flask_view_function,
                    methods=methods # e.g., ["GET", "POST"]
                )
                
                # Store info about this dynamically registered route for admin/display
                self.dynamic_routes[f"{'_'.join(methods)} {route_path}"] = { # Use a more unique key
                    "methods": methods, "handler_name": handler_name_logical, 
                    "aci_node_id": aci_node_id_in_actfile,
                    "description": aci_node_definition_from_discovery.get('description', ''),
                    "connected_workflow_nodes": self.edges.get(aci_node_id_in_actfile, []),
                    "auth_required": aci_node_definition_from_discovery.get('auth_required', False),
                    "rate_limit": aci_node_definition_from_discovery.get('rate_limit')
                }
                logger.debug(f"✅ Flask Route REGISTERED: {methods} {route_path} (ACI Node ID: {aci_node_id_in_actfile}, Handler Name: {handler_name_logical})")
            except Exception as e:
                logger.error(f"❌ FAILED to register ACI-defined Flask route for '{aci_node_definition_from_discovery.get('route_path')}': {e}", exc_info=True)

        logger.debug(f"✅ Successfully registered {len(self.dynamic_routes)} Flask routes from ACI definitions")

    # --- Standard Informational Routes ---
    def _add_health_routes(self, app: Flask):
        @app.route('/health', methods=['GET'])
        @app.route('/', methods=['GET']) # Root as health check
        def health_check_route():
            return jsonify({
                "agent_name": self.config.get("agent_name", "ACT_Agent"),
                "status": self.agent_status,
                "version": self.config.get("agent_version", "dev"),
                "timestamp": datetime.utcnow().isoformat(),
                "active_dynamic_routes": len(self.dynamic_routes)
            })

    def _add_admin_routes(self, app: Flask):
        # (Admin dashboard HTML and JSON routes - kept same as your provided code for brevity here)
        # Ensure this HTML is secure if exposed, or protect this route.
        @app.route('/admin/dashboard')
        def admin_dashboard():
            routes_html = ""
            sorted_routes = sorted(self.dynamic_routes.items())

            for route_key, route_info in sorted_routes: # route_key is "METHOD /path"
                route_path_display = route_key # Use the more descriptive key
                methods_str = ", ".join(route_info.get("methods", ["N/A"]))
                connected_nodes_list = route_info.get("connected_workflow_nodes", []) # Corrected key
                connected_nodes = ", ".join(connected_nodes_list) if connected_nodes_list else "<em>None</em>"
                auth_badge = "🔒 Auth" if route_info.get("auth_required") else "🔓 Open"
                rate_limit_val = route_info.get("rate_limit")
                rate_limit = f"⏱️ {rate_limit_val}" if rate_limit_val else ""
                
                routes_html += f"""
                <tr>
                    <td><code>{route_path_display}</code></td>
                    <td><span class="methods">{methods_str}</span></td>
                    <td>{route_info.get("handler_name", "N/A")} (ACI Node: {route_info.get("aci_node_id","N/A")})</td>
                    <td>{connected_nodes}</td>
                    <td>{route_info.get("description", "")}</td>
                    <td>{auth_badge} {rate_limit}</td>
                </tr>
                """
            # (Rest of the HTML for dashboard)
            return f"""
            <!DOCTYPE html><html><head><title>{self.config.get("agent_name", "ACT Agent")} Dashboard</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; background-color: #f9f9f9; color: #333; }}
                h1, h2 {{ color: #1a73e8; }} h1 small {{ font-size: 0.5em; color: #5f6368; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); background-color: white; }}
                th, td {{ border: 1px solid #ddd; padding: 10px 12px; text-align: left; }}
                th {{ background-color: #e3f2fd; color: #1a73e8; font-weight: 600; }}
                tr:nth-child(even) {{ background-color: #f2f5f8; }}
                .methods {{ background-color: #d1eaff; color: #004085; padding: 3px 7px; border-radius: 4px; font-size: 0.9em; white-space: nowrap; }}
                .status-ready {{ color: #2e7d32; font-weight: bold; }}
                .stats {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 25px 0; }}
                .stat-box {{ background: white; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #1a73e8; }}
                .stat-box strong {{ display: block; margin-bottom: 5px; color: #5f6368; }}
                code {{ background-color: #e8eaed; padding: 2px 5px; border-radius: 3px; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;}}
                pre {{ background-color: #f1f3f4; padding: 15px; border-radius: 4px; overflow-x: auto; border: 1px solid #dadce0; }}
            </style></head><body>
                <h1>🤖 {self.config.get("agent_name", "ACT Agent")} Dashboard <small>v{self.config.get("agent_version", "dev")}</small></h1>
                <div class="stats">
                    <div class="stat-box"><strong>Status:</strong> <span class="status-ready">{self.agent_status}</span></div>
                    <div class="stat-box"><strong>Flask Routes:</strong> {len(self.dynamic_routes)}</div>
                    <div class="stat-box"><strong>Total Nodes:</strong> {len(self.all_nodes)}</div>
                    <div class="stat-box"><strong>Workflow Edges:</strong> {len(self.edges)}</div>
                </div>
                <h2>🛣️ Dynamically Registered API Routes</h2><table>
                <tr><th>Route Path (Method)</th><th>Methods</th><th>Handler (ACI Node)</th><th>Connected Workflow Nodes</th><th>Description</th><th>Security</th></tr>{routes_html}</table>
                <h2>🔗 Workflow Edge Definitions</h2><pre>{json.dumps(self.edges, indent=2)}</pre>
                <h2>📋 All Discovered Nodes</h2><pre>{json.dumps(self.all_nodes, indent=2, default=str)}</pre>
            </body></html>
            """

        @app.route('/admin/nodes')
        def admin_nodes_json():
             return jsonify({
                "total_nodes": len(self.all_nodes),
                "nodes": self.all_nodes,
            })

        @app.route('/admin/edges')
        def admin_edges_json():
            return jsonify({ "total_edge_definitions": len(self.edges), "edges": self.edges })

    def _add_api_routes(self, app: Flask): # General info about the agent's API capabilities
        @app.route('/api/status')
        def api_status_route():
            return jsonify({
                "agent_name": self.config.get("agent_name"), "status": self.agent_status,
                "version": self.config.get("agent_version"), "timestamp": datetime.utcnow().isoformat(),
                "dynamic_routes_count": len(self.dynamic_routes),
                "dynamic_routes_summary": {
                    k: { "methods": v["methods"], "handler": v["handler_name"], "aci_node": v["aci_node_id"], "connects_to": v["connected_workflow_nodes"]}
                    for k,v in self.dynamic_routes.items()
                }
            })

    def _add_aci_base_routes(self, app: Flask): # Info about ACI specifically
        @app.route('/aci/info')
        def aci_info_route():
            return jsonify({
                "message": "Agent Communication Interface (ACI) Route Information",
                "total_aci_add_route_definitions": len(self.aci_nodes), # From _discover_aci_nodes
                "registered_flask_routes_from_aci": len(self.dynamic_routes),
                "routes_details": self.dynamic_routes # Info about routes created by _auto_register_aci_routes
            })

        # === New Production API Endpoints ===

        @app.route('/api/info')
        def api_info():
            """Get Docker image and server information"""
            import platform
            return jsonify({
                "name": self.config.get("agent_name", "ACT Server"),
                "version": self.config.get("agent_version", "1.0.0"),
                "mode": self._get_server_mode(),
                "host": self.config.get("host", "0.0.0.0"),
                "port": self.config.get("port", 9999),
                "environment": self.deployment.get("environment", "development"),
                "platform": platform.system(),
                "python_version": platform.python_version()
            })

        @app.route('/api/status')
        def api_status():
            """Get current server status"""
            return jsonify({
                "status": self.agent_status,
                "mode": self._get_server_mode(),
                "uptime": getattr(self, 'start_time', None),
                "flow_loaded": hasattr(self.execution_manager, 'workflow_data'),
                "total_nodes": len(self.all_nodes),
                "total_routes": len(self.dynamic_routes),
                "aci_nodes": len(self.aci_nodes)
            })

        @app.route('/api/nodes')
        def api_nodes():
            """Get all loaded nodes"""
            return jsonify({
                "total": len(self.all_nodes),
                "nodes": list(self.all_nodes.keys()),
                "details": self.all_nodes
            })

        @app.route('/api/routes')
        def api_routes():
            """Get all active routes (agent mode)"""
            return jsonify({
                "total": len(self.dynamic_routes),
                "routes": self.dynamic_routes
            })

        @app.route('/execute', methods=['POST'])
        def execute_workflow():
            """Execute entire workflow manually"""
            try:
                data = request.get_json() or {}

                # Check if we have a miniact executor
                if hasattr(self, 'miniact_executor'):
                    result = self.miniact_executor.execute_from_start(data)
                    return jsonify(result)
                else:
                    # Fallback to direct execution
                    result = self.execution_manager.execute_workflow(initial_input=data)
                    return jsonify({"status": "success", "result": result})

            except Exception as e:
                logger.error(f"Workflow execution failed: {e}", exc_info=True)
                return jsonify({"status": "error", "error": str(e)}), 500

        @app.route('/execute/node/<node_id>', methods=['POST'])
        def execute_node(node_id):
            """Execute specific node manually"""
            try:
                data = request.get_json() or {}

                # Check if we have a miniact executor
                if hasattr(self, 'miniact_executor'):
                    result = self.miniact_executor.execute_node(node_id, data)
                    return jsonify(result)
                else:
                    return jsonify({"status": "error", "error": "MiniACT executor not available"}), 400

            except Exception as e:
                logger.error(f"Node execution failed: {e}", exc_info=True)
                return jsonify({"status": "error", "error": str(e)}), 500

        @app.route('/reload', methods=['POST'])
        def reload_flow():
            """Force reload of flow file"""
            try:
                if hasattr(self, 'flow_watcher'):
                    self.flow_watcher.force_reload()
                    return jsonify({"status": "success", "message": "Reload triggered"})
                else:
                    return jsonify({"status": "error", "error": "Hot reload not enabled"}), 400
            except Exception as e:
                logger.error(f"Reload failed: {e}", exc_info=True)
                return jsonify({"status": "error", "error": str(e)}), 500

    def _get_server_mode(self) -> str:
        """Determine if server is in Agent or MiniACT mode"""
        if len(self.aci_nodes) > 0 or len(self.dynamic_routes) > 0:
            return "agent"
        return "miniact"

    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
        """Initializes and starts the Flask web server."""
        if not self.app:
            self.create_app() # This calls all the _add_..._routes and _auto_register_aci_routes

        # Determine final run configuration, allowing overrides from method args
        final_host = host if host is not None else self.config.get("host", "0.0.0.0")
        final_port = port if port is not None else self.config.get("port", 8080)
        # Flask debug mode; for production, this should be False.
        final_debug = debug if debug is not None else self.config.get("debug", True) 

        logger.debug(f"🤖 Starting {self.config.get('agent_name', 'ACT Agent')} v{self.config.get('agent_version', 'dev')}...")
        logger.debug(f"🌍 Flask server will listen on http://{final_host}:{final_port}")
        logger.debug(f"🛠️ Debug mode: {'ON' if final_debug else 'OFF'}")
        logger.debug(f"🔗 CORS enabled: {'Yes' if self.config.get('cors_enabled', True) else 'No'}")
        
        logger.debug(f"🚀 {len(self.dynamic_routes)} dynamic API routes registered from Actfile ACI definitions.")
        logger.debug(f"🔗 {len(self.edges)} workflow edge definitions loaded.")
        logger.debug(f"📋 {len(self.all_nodes)} total nodes discovered in Actfile.")

        if self.dynamic_routes:
            logger.debug("--- Registered Dynamic API Routes ---")
            for route_key, route_info in self.dynamic_routes.items():
                # route_key is like "GET /api/content/<...>"
                methods_str = ", ".join(route_info["methods"])
                path_only = route_key.split(" ", 1)[1] if " " in route_key else route_key
                connected_str = ", ".join(route_info.get("connected_workflow_nodes", [])) or "None"
                logger.debug(f"  ➡️ {methods_str} http://{final_host}:{final_port}{path_only}")
                logger.debug(f"     Handler: {route_info['handler_name']} (ACI Node: {route_info['aci_node_id']}) → Triggers: [{connected_str}]")
        else:
            logger.warning("No dynamic API routes were registered. Check Actfile for ACI 'add_route' nodes.")

        logger.debug(f"📍 Server ready at http://{final_host}:{final_port} | Dashboard: /admin/dashboard | Health: /health | API: /api/status")

        # Suppress werkzeug INFO logs
        import logging as std_logging
        werkzeug_logger = std_logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(std_logging.WARNING)

        try:
            # Note: Flask's built-in server is for development. For production, use a WSGI server like Gunicorn or uWSGI.
            self.app.run(host=final_host, port=final_port, debug=final_debug, use_reloader=final_debug) # use_reloader only if debug
        except Exception as e:
            logger.error(f"FATAL: Failed to start Flask web server: {e}", exc_info=True)

# --- Example Usage (for standalone testing or as a script entry point) ---
if __name__ == '__main__':
    # This example demonstrates how AgentServer could be instantiated and run.
    # It requires a mock or real ExecutionManager and node executors.

    # Basic console logging setup
    logging.basicConfig(
        level=logging.INFO, # Set to DEBUG for more verbose output
        format='%(asctime)s - %(name)s - [%(levelname)s] - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    )

    # --- Mocking ExecutionManager and ActfileParser for standalone run ---
    class MockActfileParser:
        def __init__(self, actfile_path):
            self.actfile_path = actfile_path
            self.parsed_data = self._load_and_parse_actfile() # Implement this based on your INI format
            self.resolved_params_cache = None # To cache resolved [parameters]

        def _load_and_parse_actfile(self):
            # Replace with your actual INI parsing logic that handles your Actfile format
            # This example uses configparser but might need adjustments for list values or duplicate keys.
            import configparser
            config = configparser.ConfigParser(interpolation=None, allow_no_value=True, strict=False)
            # Make it read sections with duplicate keys as lists if needed, or handle manually
            # For 'edges', if a source has multiple targets defined on separate lines, default configparser might only take the last.
            # Your real parser should handle this. This mock is simplified.
            
            try: 
                if not os.path.exists(self.actfile_path):
                    logger.error(f"MockActfileParser: Actfile not found at '{self.actfile_path}'")
                    return {}
                config.read(self.actfile_path)
            except Exception as e:
                logger.error(f"MockActfileParser: Error reading Actfile '{self.actfile_path}': {e}")
                return {}

            data: Dict[str, Any] = {}
            for section in config.sections():
                data[section] = dict(config.items(section))
                # Special handling for 'parameters' list in Actfile if INI format is tricky
                if section.startswith("node:"):
                    node_conf = data[section]
                    if 'parameters' in node_conf and isinstance(node_conf['parameters'], str):
                        # Attempt to parse a string like '["{{a}}", "{{b}}"]' into a list
                        # This is fragile; ideally, the parser handles list structures better from INI.
                        val_str = node_conf['parameters']
                        if val_str.startswith('[') and val_str.endswith(']'):
                            try: data[section]['parameters'] = json.loads(val_str.replace("'", "\"")) # Basic attempt
                            except json.JSONDecodeError: logger.warning(f"Could not JSON parse 'parameters' string for {section}: {val_str}")
            return data

        def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
            return {k.replace('node:', ''): v for k, v in self.parsed_data.items() if k.startswith('node:') and isinstance(v, dict)}

        def get_resolved_parameters(self) -> Dict[str, Any]: # From [parameters] section
            if self.resolved_params_cache is None:
                self.resolved_params_cache = {}
                raw_global_params = self.parsed_data.get('parameters', {})
                if isinstance(raw_global_params, dict):
                    for key, value_template in raw_global_params.items():
                        if isinstance(value_template, str) and value_template.startswith("${") and value_template.endswith("}"):
                            env_var_name = value_template[2:-1]
                            env_val = os.getenv(env_var_name)
                            self.resolved_params_cache[key] = env_val if env_val is not None else value_template
                        else:
                            self.resolved_params_cache[key] = value_template
            return self.resolved_params_cache or {}

    class MockExecutionManager:
        def __init__(self, actfile_path_for_parser):
            self.node_executors: Dict[str, Any] = {} # MUST be populated with actual node executor instances
            self.actfile_parser = MockActfileParser(actfile_path_for_parser)
            # Ensure global parameters are resolved early for AgentServer to use
            self.resolved_parameters = self.actfile_parser.get_resolved_parameters()
            
        def get_global_resolved_parameters(self): # Method for AgentServer to call
             return self.resolved_parameters


    # --- Node Executor Registration (CRITICAL FOR OPERATION) ---
    # You MUST define and register your node executor classes here.
    class DummyNeonExecutor: # Replace with your actual NeonNode class or instance
        async def execute(self, node_input_data: Dict[str, Any]) -> Dict[str, Any]:
            params = node_input_data.get('params', {})
            label = node_input_data.get('label', 'UnknownNeonNode')
            logger.debug(f"DummyNeonExecutor ('{label}'): Received input: {json.dumps(params, default=str, indent=2)}")
            
            # Check connection string
            cs = params.get('connection_string')
            if not cs or "${" in cs or "{{" in cs: # Check for unresolved placeholders
                logger.error(f"DummyNeonExecutor ('{label}'): Invalid or unresolved connection string: '{cs}'")
                return {"status": "error", "message": f"Invalid/unresolved connection string: {cs}"}

            op = params.get('operation')
            sql_params = params.get('parameters') # List for %s
            
            if op == "execute_query" and params.get('query','').startswith("SELECT id, workflow_id FROM content_pipeline.generated_content WHERE workflow_id = %s"):
                wf_id = sql_params[0] if sql_params and len(sql_params) > 0 else "unknown_wf_id"
                logger.debug(f"DummyNeonExecutor ('{label}'): Simulating SELECT for workflow_id: {wf_id}")
                return {"status": "success", "data": [{"id": 1, "workflow_id": wf_id, "content_type": "api_get_simulated", "content_text": "Simulated content for GET API"}], "rows_affected": 1}
            
            elif op == "execute_query" and params.get('query','').startswith("INSERT INTO content_pipeline.generated_content"):
                logger.debug(f"DummyNeonExecutor ('{label}'): Simulating INSERT with params: {sql_params}")
                if sql_params and len(sql_params) == 3: # workflow_id, content_type, content_text
                    return {"status": "success", "data": [{"id": "new_id_123", "workflow_id": sql_params[0], "content_type": sql_params[1], "created_at": datetime.utcnow().isoformat()}], "rows_affected": 1}
                else: return {"status": "error", "message": "Dummy INSERT requires 3 parameters."}
            
            logger.warning(f"DummyNeonExecutor ('{label}'): Unhandled operation '{op}' or query.")
            return {"status": "success", "message": f"Dummy Neon operation '{op}' completed (unspecific)."}

    # --- Script Execution ---
    # Ensure environment variables are set if your Actfile [parameters] use them
    if not os.getenv("NEON_CONNECTION_STRING") and not os.getenv("GEMINI_API_KEY"):
        logger.warning("NEON_CONNECTION_STRING or GEMINI_API_KEY environment variables are not set. "
                       "The Actfile might rely on these if not hardcoded in [parameters].")
    
    # Path to your Actfile (e.g., 'flow', 'my_workflow.act')
    actfile_to_run = 'flow' 
    if not os.path.exists(actfile_to_run):
        logger.error(f"Actfile '{actfile_to_run}' not found. Please ensure it's in the correct path.")
        exit(1)
        
    # Instantiate the mock execution manager (replace with your actual one)
    execution_manager_instance = MockExecutionManager(actfile_path_for_parser=actfile_to_run)
    
    # !!!! REGISTER YOUR NODE EXECUTORS HERE !!!!
    execution_manager_instance.node_executors['neon'] = DummyNeonExecutor() 
    # Add other executors:
    # execution_manager_instance.node_executors['generate_uuid'] = YourActualGenerateUUIDExecutor()
    # execution_manager_instance.node_executors['data'] = YourActualDataNodeExecutor()
    # execution_manager_instance.node_executors['gemini'] = YourActualGeminiExecutor()
    # execution_manager_instance.node_executors['log_message'] = YourActualLogMessageExecutor()
    # ... and so on for all node types used in ACI-triggered flows.

    # Agent Server Configuration (can also come from a config file)
    agent_config = {
        "agent_name": "MyContentAgent", 
        "agent_version": "1.1.0",
        "host": "0.0.0.0", 
        "port": 8080, 
        "debug": True, # Flask debug mode (set to False in production)
        "cors_enabled": True
    }
    deployment_config = {"environment": "development"} # Example

    server = AgentServer(execution_manager_instance, agent_config, deployment_config)
    server.run() # This will start the Flask server