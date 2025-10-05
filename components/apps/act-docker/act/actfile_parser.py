# === File: act/actfile_parser.py ===

import configparser
import os
import re
import json
import logging
import ast
import operator
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
from functools import reduce

# Configure logger for this module
logger = logging.getLogger(__name__)

class ActfileParserError(Exception):
    """Custom exception for Actfile parsing errors."""
    pass

class PlaceholderResolutionError(Exception):
    """Custom exception for placeholder resolution errors."""
    pass

class AdvancedPlaceholderResolver:
    """
    Advanced placeholder resolver supporting:
    - Dot notation: {{node.result.field.subfield}}
    - Array access: {{node.result.array.0}}
    - Filters: {{value|length}}, {{value|default("fallback")}}
    - Conditionals: {{value if condition else default}}
    - Template blocks: {{#if condition}}content{{/if}}
    - Loops: {{#each array}}{{this.field}}{{/each}}
    """
    
    def __init__(self):
        self.static_context = {}
        self.runtime_context = {}
        self.filters = self._init_default_filters()
        self.functions = self._init_default_functions()
        
        # Regex patterns for different placeholder types
        self.patterns = {
            'simple': re.compile(r'\{\{\s*([^}]+?)\s*\}\}'),
            'parameter': re.compile(r'\{\{\s*\.Parameter\.([A-Za-z_][A-Za-z0-9_]*)\s*\}\}'),
            'env_var': re.compile(r'\$\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}'),
            'conditional_block': re.compile(r'\{\{#if\s+([^}]+?)\}\}(.*?)\{\{/if\}\}', re.DOTALL),
            'loop_block': re.compile(r'\{\{#each\s+([^}]+?)\}\}(.*?)\{\{/each\}\}', re.DOTALL),
            'else_block': re.compile(r'\{\{else\}\}'),
        }
    
    def _init_default_filters(self) -> Dict[str, Callable]:
        """Initialize default filter functions."""
        return {
            'length': lambda x: len(x) if hasattr(x, '__len__') else 0,
            'len': lambda x: len(x) if hasattr(x, '__len__') else 0,
            'upper': lambda x: str(x).upper() if x is not None else '',
            'lower': lambda x: str(x).lower() if x is not None else '',
            'capitalize': lambda x: str(x).capitalize() if x is not None else '',
            'strip': lambda x: str(x).strip() if x is not None else '',
            'default': lambda x, default_val='': x if x is not None and x != '' else default_val,
            'truncate': lambda x, length=50: str(x)[:int(length)] if x is not None else '',
            'join': lambda x, separator=',': separator.join(str(i) for i in x) if hasattr(x, '__iter__') and not isinstance(x, str) else str(x),
            'first': lambda x: x[0] if hasattr(x, '__getitem__') and len(x) > 0 else None,
            'last': lambda x: x[-1] if hasattr(x, '__getitem__') and len(x) > 0 else None,
            'sort': lambda x: sorted(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'reverse': lambda x: list(reversed(x)) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'unique': lambda x: list(dict.fromkeys(x)) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'sum': lambda x: sum(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'max': lambda x: max(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'min': lambda x: min(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'round': lambda x, digits=0: round(float(x), int(digits)) if x is not None else 0,
            'abs': lambda x: abs(float(x)) if x is not None else 0,
            'int': lambda x: int(float(x)) if x is not None else 0,
            'float': lambda x: float(x) if x is not None else 0.0,
            'str': lambda x: str(x) if x is not None else '',
            'bool': lambda x: bool(x) if x is not None else False,
            'json': lambda x: json.dumps(x) if x is not None else '{}',
        }
    
    def _init_default_functions(self) -> Dict[str, Callable]:
        """Initialize default function library."""
        return {
            'len': lambda x: len(x) if hasattr(x, '__len__') else 0,
            'max': lambda x: max(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'min': lambda x: min(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'sum': lambda x: sum(x) if hasattr(x, '__iter__') and not isinstance(x, str) else x,
            'abs': lambda x: abs(float(x)) if x is not None else 0,
            'round': lambda x, digits=0: round(float(x), int(digits)) if x is not None else 0,
            'range': lambda start, stop=None, step=1: list(range(int(start), int(stop or 0), int(step))),
            'enumerate': lambda x: list(enumerate(x)) if hasattr(x, '__iter__') and not isinstance(x, str) else [],
        }
    
    def set_static_context(self, parameters: Dict[str, Any], env_vars: Dict[str, str]):
        """Set static context for parameter and environment variable resolution."""
        self.static_context = {
            'parameters': parameters,
            'env': env_vars
        }
    
    def set_runtime_context(self, execution_context: Dict[str, Any]):
        """Set runtime context for node result resolution."""
        self.runtime_context = execution_context
    
    def resolve_static_placeholders(self, text: str) -> str:
        """Resolve static placeholders (parameters and environment variables)."""
        if not isinstance(text, str):
            return text
        
        result = text
        
        # Resolve parameter placeholders: {{.Parameter.key}}
        for match in self.patterns['parameter'].finditer(text):
            placeholder = match.group(0)
            param_key = match.group(1)
            
            if param_key in self.static_context.get('parameters', {}):
                param_value = str(self.static_context['parameters'][param_key])
                result = result.replace(placeholder, param_value)
                logger.debug(f"Resolved parameter placeholder '{placeholder}' -> '{param_value[:100]}...'")
            else:
                logger.warning(f"Parameter '{param_key}' not found in static context")
        
        # Resolve environment variable placeholders: ${ENV_VAR}
        for match in self.patterns['env_var'].finditer(result):
            placeholder = match.group(0)
            env_key = match.group(1)
            
            env_value = os.environ.get(env_key) or self.static_context.get('env', {}).get(env_key, '')
            result = result.replace(placeholder, env_value)
            logger.debug(f"Resolved env placeholder '{placeholder}' -> '{env_value[:50]}...'")
        
        return result
    
    def resolve_runtime_placeholders(self, text: str) -> str:
        """Resolve runtime placeholders (node results, conditionals, loops)."""
        if not isinstance(text, str):
            return text
        
        result = text
        
        # First pass: Resolve conditional blocks {{#if}}...{{/if}}
        result = self._resolve_conditional_blocks(result)
        
        # Second pass: Resolve loop blocks {{#each}}...{{/each}}
        result = self._resolve_loop_blocks(result)
        
        # Third pass: Resolve simple placeholders {{variable}}
        result = self._resolve_simple_placeholders(result)
        
        return result
    
    def _resolve_conditional_blocks(self, text: str) -> str:
        """Resolve {{#if condition}}content{{else}}other{{/if}} blocks."""
        result = text
        
        for match in self.patterns['conditional_block'].finditer(text):
            full_block = match.group(0)
            condition_expr = match.group(1).strip()
            content = match.group(2)
            
            try:
                # Split content on {{else}} if present
                if '{{else}}' in content:
                    if_content, else_content = re.split(r'\{\{else\}\}', content, 1)
                else:
                    if_content, else_content = content, ''
                
                # Evaluate condition
                condition_result = self._evaluate_expression(condition_expr)
                
                # Choose content based on condition
                chosen_content = if_content if condition_result else else_content
                
                # Recursively resolve placeholders in chosen content
                resolved_content = self.resolve_runtime_placeholders(chosen_content)
                
                result = result.replace(full_block, resolved_content)
                logger.debug(f"Resolved conditional block: condition='{condition_expr}' -> {condition_result}")
                
            except Exception as e:
                logger.warning(f"Error resolving conditional block '{condition_expr}': {e}")
                result = result.replace(full_block, f"[CONDITIONAL_ERROR: {e}]")
        
        return result
    
    def _resolve_loop_blocks(self, text: str) -> str:
        """Resolve {{#each array}}{{this.field}}{{/each}} blocks."""
        result = text
        
        for match in self.patterns['loop_block'].finditer(text):
            full_block = match.group(0)
            array_expr = match.group(1).strip()
            template = match.group(2)
            
            try:
                # Get the array to iterate over
                array_value = self._evaluate_expression(array_expr)
                
                if not hasattr(array_value, '__iter__') or isinstance(array_value, str):
                    array_value = [array_value]
                
                # Generate content for each item
                loop_results = []
                for index, item in enumerate(array_value):
                    # Create loop context
                    loop_context = {
                        'this': item,
                        'index': index,
                        'first': index == 0,
                        'last': index == len(array_value) - 1,
                        'length': len(array_value)
                    }
                    
                    # Temporarily add loop context to runtime context
                    original_context = self.runtime_context.copy()
                    self.runtime_context.update(loop_context)
                    
                    # Resolve template with loop context
                    item_content = self.resolve_runtime_placeholders(template)
                    loop_results.append(item_content)
                    
                    # Restore original context
                    self.runtime_context = original_context
                
                resolved_content = ''.join(loop_results)
                result = result.replace(full_block, resolved_content)
                logger.debug(f"Resolved loop block: array='{array_expr}' with {len(array_value)} items")
                
            except Exception as e:
                logger.warning(f"Error resolving loop block '{array_expr}': {e}")
                result = result.replace(full_block, f"[LOOP_ERROR: {e}]")
        
        return result
    
    def _resolve_simple_placeholders(self, text: str) -> str:
        """Resolve simple {{variable}} placeholders with dot notation and filters."""
        result = text
        
        for match in self.patterns['simple'].finditer(text):
            placeholder = match.group(0)
            expression = match.group(1).strip()
            
            # Skip if it's a template block (already processed)
            if expression.startswith('#') or expression == 'else' or expression.startswith('/'):
                continue
            
            try:
                resolved_value = self._evaluate_expression(expression)
                result = result.replace(placeholder, str(resolved_value))
                logger.debug(f"Resolved placeholder '{placeholder}' -> '{str(resolved_value)[:100]}...'")
                
            except Exception as e:
                logger.warning(f"Error resolving placeholder '{placeholder}': {e}")
                # Leave unresolved placeholders for later or mark as error
                # result = result.replace(placeholder, f"[UNRESOLVED: {expression}]")
        
        return result
    
    def _evaluate_expression(self, expression: str) -> Any:
        """Evaluate a complex expression with dot notation, filters, and conditionals."""
        try:
            # Handle conditional expressions: value if condition else default
            if ' if ' in expression and ' else ' in expression:
                return self._evaluate_conditional_expression(expression)
            
            # Handle filter chains: value|filter1|filter2(arg)
            if '|' in expression:
                return self._evaluate_filter_chain(expression)
            
            # Handle function calls: func(arg1, arg2)
            if '(' in expression and ')' in expression:
                return self._evaluate_function_call(expression)
            
            # Handle simple dot notation: node.result.field.subfield
            return self._evaluate_dot_notation(expression)
            
        except Exception as e:
            logger.warning(f"Expression evaluation failed for '{expression}': {e}")
            raise PlaceholderResolutionError(f"Cannot evaluate expression '{expression}': {e}")
    
    def _evaluate_conditional_expression(self, expression: str) -> Any:
        """Evaluate: value if condition else default"""
        try:
            # Parse the conditional expression
            match = re.match(r'(.+?)\s+if\s+(.+?)\s+else\s+(.+)', expression.strip())
            if not match:
                raise ValueError("Invalid conditional expression format")
            
            value_expr, condition_expr, default_expr = match.groups()
            
            # Evaluate condition
            condition_result = self._evaluate_expression(condition_expr.strip())
            
            # Return appropriate value based on condition
            if condition_result:
                return self._evaluate_expression(value_expr.strip())
            else:
                return self._evaluate_expression(default_expr.strip())
                
        except Exception as e:
            raise PlaceholderResolutionError(f"Conditional expression error: {e}")
    
    def _evaluate_filter_chain(self, expression: str) -> Any:
        """Evaluate: value|filter1|filter2(arg)|filter3"""
        try:
            parts = expression.split('|')
            value = self._evaluate_expression(parts[0].strip())
            
            # Apply each filter in sequence
            for filter_part in parts[1:]:
                filter_part = filter_part.strip()
                
                # Check if filter has arguments: filter(arg1, arg2)
                if '(' in filter_part and ')' in filter_part:
                    filter_name = filter_part.split('(')[0].strip()
                    args_str = filter_part[filter_part.index('(') + 1:filter_part.rindex(')')].strip()
                    
                    # Parse arguments
                    if args_str:
                        args = self._parse_function_args(args_str)
                    else:
                        args = []
                    
                    if filter_name in self.filters:
                        value = self.filters[filter_name](value, *args)
                    else:
                        logger.warning(f"Unknown filter: {filter_name}")
                        
                else:
                    # Simple filter without arguments
                    if filter_part in self.filters:
                        value = self.filters[filter_part](value)
                    else:
                        logger.warning(f"Unknown filter: {filter_part}")
            
            return value
            
        except Exception as e:
            raise PlaceholderResolutionError(f"Filter chain error: {e}")
    
    def _evaluate_function_call(self, expression: str) -> Any:
        """Evaluate: func(arg1, arg2)"""
        try:
            func_name = expression.split('(')[0].strip()
            args_str = expression[expression.index('(') + 1:expression.rindex(')')].strip()
            
            if func_name in self.functions:
                if args_str:
                    args = self._parse_function_args(args_str)
                    return self.functions[func_name](*args)
                else:
                    return self.functions[func_name]()
            else:
                # Try to evaluate as dot notation in case it's a method call
                return self._evaluate_dot_notation(expression)
                
        except Exception as e:
            raise PlaceholderResolutionError(f"Function call error: {e}")
    
    def _evaluate_dot_notation(self, expression: str) -> Any:
        """Evaluate: node.result.field.subfield or array.0.field"""
        try:
            parts = expression.split('.')
            
            # Start with the base object
            current_value = self._get_base_value(parts[0])
            
            # Navigate through the dot notation
            for part in parts[1:]:
                current_value = self._access_property(current_value, part)
            
            return current_value
            
        except Exception as e:
            raise PlaceholderResolutionError(f"Dot notation error for '{expression}': {e}")
    
    def _get_base_value(self, base_name: str) -> Any:
        """Get the base value from runtime context."""
        # Check runtime context first (node results)
        if base_name in self.runtime_context:
            return self.runtime_context[base_name]
        
        # Check static context
        if base_name in self.static_context:
            return self.static_context[base_name]
        
        # Check parameters
        if base_name in self.static_context.get('parameters', {}):
            return self.static_context['parameters'][base_name]
        
        # Check environment variables
        if base_name in self.static_context.get('env', {}):
            return self.static_context['env'][base_name]
        
        # Check if it's a literal value
        if base_name.isdigit():
            return int(base_name)
        
        if base_name.replace('.', '').isdigit():
            return float(base_name)
        
        if base_name.lower() in ('true', 'false'):
            return base_name.lower() == 'true'
        
        if base_name.lower() == 'null' or base_name.lower() == 'none':
            return None
        
        # Check for quoted strings
        if (base_name.startswith('"') and base_name.endswith('"')) or \
           (base_name.startswith("'") and base_name.endswith("'")):
            return base_name[1:-1]
        
        raise KeyError(f"Base value '{base_name}' not found in any context")
    
    def _access_property(self, obj: Any, property_name: str) -> Any:
        """Access a property of an object, handling arrays, dicts, and attributes."""
        if obj is None:
            return None
        
        # Handle array/list indices
        if property_name.isdigit():
            index = int(property_name)
            if hasattr(obj, '__getitem__'):
                try:
                    return obj[index]
                except (IndexError, KeyError):
                    return None
        
        # Handle dictionary keys
        if isinstance(obj, dict):
            return obj.get(property_name)
        
        # Handle object attributes
        if hasattr(obj, property_name):
            attr = getattr(obj, property_name)
            # If it's a method, call it with no arguments
            if callable(attr):
                try:
                    return attr()
                except TypeError:
                    return attr  # Return the method itself if it requires arguments
            return attr
        
        # Handle list methods
        if isinstance(obj, list) and property_name in ('length', 'len'):
            return len(obj)
        
        # Handle string methods
        if isinstance(obj, str) and property_name in ('length', 'len'):
            return len(obj)
        
        return None
    
    def _parse_function_args(self, args_str: str) -> List[Any]:
        """Parse function arguments from string."""
        args = []
        
        try:
            # Simple parsing - split by comma and evaluate each argument
            for arg in args_str.split(','):
                arg = arg.strip()
                
                # Try to evaluate as expression
                try:
                    value = self._evaluate_expression(arg)
                    args.append(value)
                except:
                    # Fallback to literal interpretation
                    if arg.isdigit():
                        args.append(int(arg))
                    elif arg.replace('.', '').isdigit():
                        args.append(float(arg))
                    elif arg.lower() in ('true', 'false'):
                        args.append(arg.lower() == 'true')
                    elif (arg.startswith('"') and arg.endswith('"')) or \
                         (arg.startswith("'") and arg.endswith("'")):
                        args.append(arg[1:-1])
                    else:
                        args.append(arg)
        
        except Exception as e:
            logger.warning(f"Error parsing function arguments '{args_str}': {e}")
        
        return args
    
    def add_filter(self, name: str, func: Callable):
        """Add a custom filter function."""
        self.filters[name] = func
    
    def add_function(self, name: str, func: Callable):
        """Add a custom function."""
        self.functions[name] = func


class ActfileParser:
    """
    Enhanced Actfile Parser with advanced placeholder resolution.
    Supports dot notation, filters, conditionals, loops, and more.
    """
    
    SUPPORTED_SECTIONS = [
        'workflow', 'parameters', 'nodes', 'edges',
        'dependencies', 'env', 'settings', 'configuration', 'deployment'
    ]

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.actfile_dir = self.file_path.parent
        self.parsed_data: Dict[str, Any] = {
            "parameters": {},
            "workflow": {},
            "nodes": {},
            "edges": {},
            "dependencies": {},
            "env": {},
            "settings": {},
            "configuration": {},
            "deployment": {}
        }
        
        # Initialize the advanced placeholder resolver
        self.placeholder_resolver = AdvancedPlaceholderResolver()
        
        logger.debug(f"Initialized Enhanced ActfileParser for path: {self.file_path}")

    def parse(self) -> Dict[str, Any]:
        """Parse the Actfile with enhanced placeholder resolution."""
        if not self.file_path.is_file():
            raise ActfileParserError(f"Actfile not found: {self.file_path}")

        logger.debug(f"Starting enhanced parsing of Actfile: {self.file_path}")
        
        try:
            # Read the entire file content
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Split content into logical sections
            sections = self._split_sections(content)
            logger.debug(f"Raw sections found: {list(sections.keys())}")

            # Parse each section
            self.parsed_data["parameters"] = self._parse_parameters(sections.get('parameters', ''))
            self.parsed_data["workflow"] = self._parse_key_value_section(sections.get('workflow', ''))
            self.parsed_data["nodes"] = self._parse_nodes(sections)
            self.parsed_data["edges"] = self._parse_edges(sections.get('edges', ''))
            self.parsed_data["dependencies"] = self._parse_dependencies(sections.get('dependencies', ''))
            self.parsed_data["env"] = self._parse_env(sections.get('env', ''))
            self.parsed_data["settings"] = self._parse_key_value_section(sections.get('settings', ''))
            self.parsed_data["configuration"] = self._parse_key_value_section(sections.get('configuration', ''))
            self.parsed_data["deployment"] = self._parse_key_value_section(sections.get('deployment', ''))

            # Setup placeholder resolver with static context
            self.placeholder_resolver.set_static_context(
                self.parsed_data["parameters"],
                self.parsed_data["env"]
            )

            # Replace static placeholders (parameters and env vars)
            self._replace_static_placeholders()

            # Validate the parsed data
            self._validate_parsed_data()

            logger.debug("Enhanced Actfile parsing completed successfully.")

        except ActfileParserError as e:
            logger.error(f"Actfile parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Actfile parsing: {e}", exc_info=True)
            raise ActfileParserError(f"Error parsing Actfile: {e}")

        return self.parsed_data

    def resolve_runtime_placeholders(self, text: str, execution_context: Dict[str, Any]) -> str:
        """Resolve runtime placeholders with execution context."""
        if not isinstance(text, str):
            return text
        
        # Update runtime context
        self.placeholder_resolver.set_runtime_context(execution_context)
        
        # Resolve runtime placeholders
        return self.placeholder_resolver.resolve_runtime_placeholders(text)

    def _split_sections(self, content: str) -> Dict[str, str]:
        """Split the file content into sections based on [section] headers."""
        sections = {}
        current_section_name = None
        current_section_lines = []

        for line in content.splitlines():
            stripped_line = line.strip()

            # Check for section header
            match = re.match(r'^\s*\[([^\]]+)\]\s*(?:[#;].*)?$', line)
            if match:
                # Save the previous section
                if current_section_name is not None:
                    sections[current_section_name] = "\n".join(current_section_lines)

                # Start new section
                current_section_name = match.group(1).strip()
                current_section_lines = []
                
            elif current_section_name is not None:
                # Add line to current section if it's not a comment
                if stripped_line and not stripped_line.startswith('#') and not stripped_line.startswith(';'):
                    current_section_lines.append(line)

        # Save the last section
        if current_section_name is not None:
            sections[current_section_name] = "\n".join(current_section_lines)

        return sections

    def _parse_key_value_section(self, content: str) -> Dict[str, Any]:
        """Parse key=value section with enhanced multiline support."""
        section_data = {}
        lines = content.splitlines()
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            if not stripped_line or stripped_line.startswith('#') or stripped_line.startswith(';'):
                i += 1
                continue

            if '=' in line:
                key, value_part = line.split('=', 1)
                key = key.strip()
                value_str = value_part.strip()

                # Handle Python file path reference (only for 'py' or 'python' node types)
                if key == 'path' and value_str and section_data.get('type') in ('py', 'python'):
                    if (value_str.startswith('"') and value_str.endswith('"')) or \
                       (value_str.startswith("'") and value_str.endswith("'")):
                        value_str = value_str[1:-1]
                    
                    python_file_path = self.actfile_dir / value_str
                    
                    try:
                        if python_file_path.exists() and python_file_path.is_file():
                            with open(python_file_path, 'r', encoding='utf-8') as f:
                                python_code = f.read()
                            section_data['code'] = python_code
                            logger.debug(f"Loaded Python code from file: {python_file_path}")
                        else:
                            raise ActfileParserError(f"Python file not found: {python_file_path}")
                    except Exception as e:
                        raise ActfileParserError(f"Error reading Python file {python_file_path}: {e}")
                    
                    i += 1
                    continue

                # Handle multiline code/prompt blocks
                elif key in ('code', 'prompt'):
                    if value_str == '"""' or (value_str.startswith('"""') and not value_str.endswith('"""')):
                        content_lines = []
                        
                        if value_str != '"""':
                            content_lines.append(value_str[3:])
                        
                        i += 1
                        
                        while i < len(lines):
                            content_line = lines[i]
                            if '"""' in content_line:
                                before_quotes = content_line.split('"""', 1)[0]
                                if before_quotes:
                                    content_lines.append(before_quotes)
                                i += 1
                                break
                            content_lines.append(content_line)
                            i += 1
                        
                        section_data[key] = '\n'.join(content_lines)
                        continue
                    
                    elif value_str.startswith('"""') and value_str.endswith('"""') and len(value_str) > 6:
                        section_data[key] = value_str[3:-3]
                        i += 1
                        continue
                    
                    else:
                        section_data[key] = self._parse_value(value_str)
                        i += 1
                        continue

                # Handle multiline JSON
                elif (value_str.startswith('[') and not value_str.endswith(']')) or \
                     (value_str.startswith('{') and not value_str.endswith('}')):
                    json_lines = [value_str]
                    open_bracket = value_str[0]
                    close_bracket = ']' if open_bracket == '[' else '}'
                    bracket_level = value_str.count(open_bracket) - value_str.count(close_bracket)
                    
                    i += 1
                    while bracket_level > 0 and i < len(lines):
                        json_line = lines[i]
                        json_lines.append(json_line)
                        bracket_level += json_line.count(open_bracket)
                        bracket_level -= json_line.count(close_bracket)
                        i += 1
                    
                    full_json_str = " ".join(json_lines)
                    section_data[key] = self._parse_value(full_json_str)

                else:
                    section_data[key] = self._parse_value(value_str)
                    i += 1
            else:
                i += 1
                
        return section_data

    def _parse_value(self, value_str: str) -> Any:
        """Parse value string with placeholder preservation."""
        # Preserve all types of placeholders
        if (value_str.startswith('{{') and value_str.endswith('}}')) or \
           (value_str.startswith('${') and value_str.endswith('}')):
            return value_str

        # Try parsing as JSON
        if (value_str.startswith('{') and value_str.endswith('}')) or \
           (value_str.startswith('[') and value_str.endswith(']')):
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                pass

        # Try boolean
        if value_str.lower() == 'true': 
            return True
        if value_str.lower() == 'false': 
            return False

        # Try integer
        if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
            try: 
                return int(value_str)
            except ValueError: 
                pass

        # Try float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Handle quoted strings
        if len(value_str) >= 2:
            if (value_str.startswith('"') and value_str.endswith('"')) or \
               (value_str.startswith("'") and value_str.endswith("'")):
                return value_str[1:-1]

        return value_str

    def _parse_nodes(self, sections: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Parse all [node:*] sections."""
        nodes = {}
        for section_name, content in sections.items():
            if section_name.startswith('node:'):
                parts = section_name.split(':', 1)
                if len(parts) == 2 and parts[1].strip():
                    node_name = parts[1].strip()
                    logger.debug(f"Parsing node section: [{node_name}]")
                    node_data = self._parse_key_value_section(content)
                    
                    if 'type' not in node_data:
                        raise ActfileParserError(f"Node '{node_name}' must have a 'type' field defined.")
                    
                    nodes[node_name] = node_data
                else:
                    logger.warning(f"Ignoring invalid node section header format: [{section_name}]")
        
        logger.debug(f"Parsed {len(nodes)} node definitions.")
        return nodes

    def _parse_edges(self, content: str) -> Dict[str, List[str]]:
        """Parse the [edges] section."""
        edges: Dict[str, List[str]] = {}
        
        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith(';'):
                continue

            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    source, targets_str = parts
                    source = source.strip()

                    # Remove comments
                    if '#' in source: 
                        source = source.split('#', 1)[0].strip()
                    if ';' in source: 
                        source = source.split(';', 1)[0].strip()

                    if not source:
                        continue

                    # Process targets
                    cleaned_targets = []
                    for target in targets_str.split(','):
                        target_clean = target.strip()
                        if '#' in target_clean: 
                            target_clean = target_clean.split('#', 1)[0].strip()
                        if ';' in target_clean: 
                            target_clean = target_clean.split(';', 1)[0].strip()

                        if target_clean:
                            cleaned_targets.append(target_clean)

                    if source and cleaned_targets:
                        if source in edges:
                            edges[source].extend(cleaned_targets)
                        else:
                            edges[source] = cleaned_targets
                        logger.debug(f"Parsed edge: {source} -> {cleaned_targets}")

        logger.debug(f"Parsed {sum(len(v) for v in edges.values())} edges from {len(edges)} source nodes.")
        return edges

    def _parse_dependencies(self, content: str) -> Dict[str, List[str]]:
        """Parse [dependencies] section."""
        dependencies = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith(';'): 
                continue
            
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    node_type, deps_str = parts
                    node_type = node_type.strip()
                    
                    if '#' in deps_str: 
                        deps_str = deps_str.split('#', 1)[0]
                    if ';' in deps_str: 
                        deps_str = deps_str.split(';', 1)[0]

                    deps_list = [d.strip() for d in deps_str.split(',') if d.strip()]
                    if node_type and deps_list:
                        dependencies[node_type] = deps_list
        
        return dependencies

    def _parse_env(self, content: str) -> Dict[str, str]:
        """Parse [env] section with environment variable resolution."""
        env_vars = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith(';'): 
                continue
            
            if '=' in line:
                key, value_part = line.split('=', 1)
                key = key.strip()
                
                if '#' in value_part: 
                    value_part = value_part.split('#', 1)[0]
                if ';' in value_part: 
                    value_part = value_part.split(';', 1)[0]
                
                value = value_part.strip()

                if not key: 
                    continue

                # Resolve environment variable placeholders
                final_value = value
                if value.startswith('${') and value.endswith('}'):
                    env_var_name = value[2:-1].strip()
                    if env_var_name:
                        env_value = os.environ.get(env_var_name)
                        if env_value is not None:
                            final_value = env_value
                            logger.debug(f"Resolved env var '{env_var_name}' for key '{key}'")
                        else:
                            final_value = ""
                            logger.warning(f"Environment variable '${{{env_var_name}}}' not found")

                env_vars[key] = final_value
        
        return env_vars

    def _parse_parameters(self, content: str) -> Dict[str, Any]:
        """Parse the [parameters] section."""
        logger.debug("Parsing [parameters] section...")
        params = self._parse_key_value_section(content)
        logger.debug(f"Parsed {len(params)} parameters.")
        return params

    def _replace_static_placeholders(self):
        """Replace static placeholders in the parsed data."""
        if not self.parsed_data.get('parameters') and not self.parsed_data.get('env'):
            return

        logger.debug("Starting replacement of static placeholders...")

        def replace_recursive(item: Any) -> Any:
            if isinstance(item, str):
                return self.placeholder_resolver.resolve_static_placeholders(item)
            elif isinstance(item, dict):
                return {key: replace_recursive(value) for key, value in item.items()}
            elif isinstance(item, list):
                return [replace_recursive(elem) for elem in item]
            else:
                return item

        # Apply replacement to all sections except parameters and env
        for section_key, section_value in self.parsed_data.items():
            if section_key not in ('parameters', 'env'):
                self.parsed_data[section_key] = replace_recursive(section_value)

        logger.debug("Static placeholder replacement finished.")

    def _validate_parsed_data(self):
        """Validate the parsed data structure."""
        logger.debug("Validating parsed Actfile data...")
        
        # Validate workflow section
        if 'name' not in self.parsed_data.get('workflow', {}):
            logger.warning("Workflow section missing 'name' attribute.")
        
        if 'start_node' not in self.parsed_data.get('workflow', {}):
            raise ActfileParserError("Workflow section must contain a 'start_node' attribute.")
        
        start_node = self.parsed_data['workflow']['start_node']
        if start_node not in self.parsed_data['nodes']:
            raise ActfileParserError(f"Workflow 'start_node' ('{start_node}') does not exist in node definitions.")

        # Validate edges reference existing nodes
        all_defined_nodes = set(self.parsed_data['nodes'].keys())
        edge_sources = self.parsed_data.get('edges', {})
        
        for source, targets in edge_sources.items():
            if source not in all_defined_nodes:
                raise ActfileParserError(f"Edge source node '{source}' is not defined.")
            
            for target in targets:
                if target not in all_defined_nodes:
                    raise ActfileParserError(f"Edge target node '{target}' is not defined.")

        logger.debug("Parsed data validation passed.")

    # Public accessor methods (same as before)
    def get_workflow_name(self) -> Optional[str]:
        return self.parsed_data.get('workflow', {}).get('name')

    def get_workflow_description(self) -> Optional[str]:
        return self.parsed_data.get('workflow', {}).get('description')

    def get_start_node(self) -> Optional[str]:
        return self.parsed_data.get('workflow', {}).get('start_node')

    def get_node_successors(self, node_name: str) -> List[str]:
        return list(self.parsed_data.get('edges', {}).get(node_name, []))

    def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        import copy
        return copy.deepcopy(self.parsed_data.get('nodes', {}))

    def get_node_config(self, node_name: str) -> Optional[Dict[str, Any]]:
        return self.parsed_data.get('nodes', {}).get(node_name)

    def get_env_var(self, key: str, default: Any = None) -> Any:
        return self.parsed_data.get('env', {}).get(key, default)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.parsed_data.get('settings', {}).get(key, default)

    def get_parameter(self, key: str, default: Any = None) -> Any:
        return self.parsed_data.get('parameters', {}).get(key, default)

    def to_json(self, indent: int = 2) -> str:
        try:
            return json.dumps(self.parsed_data, indent=indent)
        except TypeError as e:
            logger.error(f"Could not serialize parsed data to JSON: {e}")
            try:
                return json.dumps(self.parsed_data, indent=indent, default=str)
            except Exception as e_inner:
                return f'{{"error": "Failed to serialize parsed data: {e_inner}"}}'

    # Agent configuration methods (same as before)
    def parse_configuration_section(self):
        config = {}
        if 'configuration' in self.parsed_data:
            config_section = self.parsed_data['configuration']
            config.update({
                'agent_enabled': config_section.get('agent_enabled', False),
                'host': config_section.get('host', 'localhost'),
                'port': config_section.get('port', 8080),
                'debug': config_section.get('debug', False),
                'cors_enabled': config_section.get('cors_enabled', True),
                'auto_reload': config_section.get('auto_reload', False)
            })
        return config

    def parse_deployment_section(self):
        config = {}
        if 'deployment' in self.parsed_data:
            config_section = self.parsed_data['deployment']
            config.update({
                'environment': config_section.get('environment', 'development'),
                'workers': config_section.get('workers', 1),
                'ssl_enabled': config_section.get('ssl_enabled', False),
                'ssl_cert': config_section.get('ssl_cert'),
                'ssl_key': config_section.get('ssl_key')
            })
        return config

    def get_agent_config(self):
        config = self.parse_configuration_section()
        config.update(self.parse_deployment_section())
        return config

    def has_agent_config(self):
        return 'configuration' in self.parsed_data and \
               self.parsed_data['configuration'].get('agent_enabled', False)

    @staticmethod
    def find_actfile(start_dir: Union[str, Path] = None) -> Path:
        """Find the Actfile by searching up the directory tree."""
        possible_names = ["Actfile", "actfile", "actfile.ini", "Actfile.ini"]
        current_dir = Path(start_dir or os.getcwd()).resolve()
        
        while True:
            for name in possible_names:
                actfile_path = current_dir / name
                if actfile_path.is_file():
                    logger.debug(f"Found Actfile at: {actfile_path}")
                    return actfile_path

            if current_dir.parent == current_dir:
                break
            current_dir = current_dir.parent

        raise ActfileParserError(f"Actfile not found in '{Path(start_dir or os.getcwd())}' or parent directories.")


# Usage example for testing
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.DEBUG)
    
    # Example usage
    test_content = '''
[workflow]
name = "Test Advanced Placeholders"
start_node = TestNode

[parameters]
base_url = "https://api.example.com"
max_items = 10

[env]
API_KEY = ${API_KEY}

[node:TestNode]
type = py
code = """
def test():
    return {"items": [{"name": "item1"}, {"name": "item2"}], "count": 2}
"""
function = test

[node:ProcessNode]
type = gemini
prompt = """
Process these items: {{TestNode.result.items|length}} total items
First item: {{TestNode.result.items.0.name}}
{{#if TestNode.result.count > 1}}
Multiple items found!
{{else}}
Single item only.
{{/if}}

{{#each TestNode.result.items}}
- Item {{index}}: {{this.name}}
{{/each}}
"""

[edges]
TestNode = ProcessNode
'''
    
    print("🧪 Testing Enhanced ActfileParser...")
    
    # Create a temporary test file
    test_file = Path("/tmp/test_actfile")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Parse the file
        parser = ActfileParser(test_file)
        result = parser.parse()
        
        print("✅ Parsing successful!")
        print(f"📊 Workflow: {result['workflow']['name']}")
        print(f"🔧 Nodes: {list(result['nodes'].keys())}")
        
        # Test runtime placeholder resolution
        execution_context = {
            "TestNode": {
                "result": {
                    "items": [{"name": "item1"}, {"name": "item2"}], 
                    "count": 2
                }
            }
        }
        
        prompt = result['nodes']['ProcessNode']['prompt']
        resolved_prompt = parser.resolve_runtime_placeholders(prompt, execution_context)
        
        print("\n🔄 Runtime Resolution Test:")
        print("Original prompt:", prompt[:100] + "...")
        print("Resolved prompt:", resolved_prompt)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()