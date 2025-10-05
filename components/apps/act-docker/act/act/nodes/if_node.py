from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError, NodeExecutionError; import logging, numbers; logger = logging.getLogger(__name__); class IfNode(BaseNode): # Using v1.2.0 logic
        def get_schema(self) -> NodeSchema: return NodeSchema(node_type="if", version="1.2.0", description=".", parameters=[ NodeParameter(name="value1", type=NodeParameterType.ANY, description=".", required=True), NodeParameter(name="operator", type=NodeParameterType.STRING, description=".", required=True, enum=["==", "eq", "!=", "ne", ">", "gt", "<", "lt", ">=", "ge", "<=", "le", "contains", "not contains", "starts_with", "ends_with", "is_true", "is_false", "is_empty", "is_not_empty"]), NodeParameter(name="value2", type=NodeParameterType.ANY, description=".", required=False, default=None), NodeParameter(name="case_sensitive", type=NodeParameterType.BOOLEAN, description=".", required=False, default=True) ], outputs={ "result": NodeParameterType.BOOLEAN, "value1_resolved": NodeParameterType.ANY, "value2_resolved": NodeParameterType.ANY, })
        def _check_and_convert_string(self, v): # Simplified version from IfNode v1.2.0
            if isinstance(v, str):
                if v.lower()=='true': return True;
                if v.lower()=='false': return False;
                if v.isdigit() or (v.startswith('-') and v[1:].isdigit()): return int(v)
                try: return float(v)
                except ValueError: pass
            return v
        async def execute(self, node_data: dict) -> dict:
            node_name = node_data.get('__node_name', 'if_node'); logger.debug(f"Executing IfNode: {node_name}")
            try:
                params = node_data.get("params", {}); val1 = params.get("value1"); op = params.get("operator"); val2 = params.get("value2"); case_sensitive = params.get("case_sensitive", True)
                if not op or not isinstance(op, str): raise NodeValidationError("Missing 'operator'")
                logger.info(f"{node_name} - Received: v1='{val1}'({type(val1).__name__}), op='{op}', v2='{val2}'({type(val2).__name__}), cs={case_sensitive}")
                condition_met = False; error_msg = None
                try:
                    str_val1 = str(val1); str_val2 = str(val2) if val2 is not None else None; str_val1_cmp = str_val1.lower() if not case_sensitive and isinstance(val1, str) else str_val1; str_val2_cmp = str_val2.lower() if not case_sensitive and isinstance(val2, str) and str_val2 is not None else str_val2
                    unary_ops = ["is_true", "is_false", "is_empty", "is_not_empty"]; binary_ops_req_val2 = ["==", "eq", "!=", "ne", ">", "gt", "<", "lt", ">=", "ge", "<=", "le","contains", "not contains", "starts_with", "ends_with"]
                    if op in unary_ops: conv_val1 = self._check_and_convert_string(val1); logger.debug(f"{node_name} - Unary op '{op}' using: '{conv_val1}' ({type(conv_val1).__name__})"); condition_met = bool(conv_val1) if op=="is_true" else (not bool(conv_val1) if op=="is_false" else (conv_val1 is None or (hasattr(conv_val1, '__len__') and len(conv_val1) == 0)) if op=="is_empty" else (conv_val1 is not None and (not hasattr(conv_val1, '__len__') or len(conv_val1) > 0)))
                    elif op in binary_ops_req_val2:
                        if val2 is None: raise ValueError(f"Operator '{op}' requires value2")
                        elif op in ["==", "eq"]: condition_met = (str_val1_cmp == str_val2_cmp) if not case_sensitive and isinstance(val1, str) and isinstance(val2, str) else (val1 == val2)
                        elif op in ["!=", "ne"]: condition_met = (str_val1_cmp != str_val2_cmp) if not case_sensitive and isinstance(val1, str) and isinstance(val2, str) else (val1 != val2)
                        elif op in [">", "gt", "<", "lt", ">=", "ge", "<=", "le"]:
                             try: condition_met = (val1 > val2) if op in [">","gt"] else (val1 < val2) if op in ["<","lt"] else (val1 >= val2) if op in [">=","ge"] else (val1 <= val2)
                             except TypeError: logger.debug(f"{node_name} - TypeError on direct numeric compare, attempting conversion..."); conv_val1 = self._check_and_convert_string(val1); conv_val2 = self._check_and_convert_string(val2); logger.debug(f"{node_name} - Converted for fallback: '{conv_val1}'({type(conv_val1).__name__}), '{conv_val2}'({type(conv_val2).__name__})");
                             if isinstance(conv_val1, numbers.Number) and isinstance(conv_val2, numbers.Number): condition_met = (conv_val1 > conv_val2) if op in [">","gt"] else (conv_val1 < conv_val2) if op in ["<","lt"] else (conv_val1 >= conv_val2) if op in [">=","ge"] else (conv_val1 <= conv_val2)
                             else: raise TypeError(f"Numeric compare failed after conversion: {type(val1).__name__} vs {type(val2).__name__}")
                        elif op == "contains": container = str_val1_cmp if isinstance(val1, str) and not case_sensitive else val1; item = str_val2_cmp if isinstance(val1, str) and isinstance(val2, str) and not case_sensitive else val2; condition_met = item in container if isinstance(container,(str,list,tuple,dict)) else False
                        elif op == "starts_with": condition_met = str_val1_cmp.startswith(str_val2_cmp) if isinstance(val1, str) and isinstance(val2, str) else False
                        elif op == "ends_with": condition_met = str_val1_cmp.endswith(str_val2_cmp) if isinstance(val1, str) and isinstance(val2, str) else False
                    else: error_msg = f"Unsupported operator: {op}"
                    if error_msg: raise NodeExecutionError(error_msg)
                except TypeError as e: return self.handle_error(NodeExecutionError(f"Type error on compare for '{op}': {e}. Comparing '{val1}'({type(val1).__name__}) and '{val2}'({type(val2).__name__})"), context=f"{node_name} Comparison")
                except ValueError as e: return self.handle_error(NodeExecutionError(str(e)), context=f"{node_name} Setup")
                except NodeExecutionError as e: return self.handle_error(e, context=f"{node_name} Logic")
                except Exception as e: return self.handle_error(e, context=f"{node_name} Comparison")
                logger.info(f"{node_name} - Condition '{op}' evaluated to: {condition_met}")
                return {"status": "success", "result": {"result": condition_met, "value1_resolved": val1, "value2_resolved": val2}, "message": f"Condition evaluated to {condition_met}"}
            except NodeValidationError as e: return self.handle_error(e, context=f"{node_name} Validation")
            except Exception as e: return self.handle_error(e, context=f"{node_name} Execute")