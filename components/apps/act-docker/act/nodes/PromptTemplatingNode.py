import asyncio
import re
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from act_workflow.act.node_schema import NodeSchema, NodeParameter, NodeParameterType
from act_workflow.act.nodes.base_node import BaseNode

class PromptTemplatingOperation:
    """Prompt templating and chaining operations."""
    
    # Template operations
    CREATE_TEMPLATE = "create_template"
    RENDER_TEMPLATE = "render_template"
    VALIDATE_TEMPLATE = "validate_template"
    
    # Template management
    SAVE_TEMPLATE = "save_template"
    LOAD_TEMPLATE = "load_template"
    LIST_TEMPLATES = "list_templates"
    DELETE_TEMPLATE = "delete_template"
    
    # Variable operations
    EXTRACT_VARIABLES = "extract_variables"
    SET_VARIABLES = "set_variables"
    GET_VARIABLES = "get_variables"
    VALIDATE_VARIABLES = "validate_variables"
    
    # Chaining operations
    CREATE_CHAIN = "create_chain"
    EXECUTE_CHAIN = "execute_chain"
    ADD_TO_CHAIN = "add_to_chain"
    
    # Advanced templating
    CONDITIONAL_TEMPLATE = "conditional_template"
    LOOP_TEMPLATE = "loop_template"
    INCLUDE_TEMPLATE = "include_template"
    
    # Prompt optimization
    OPTIMIZE_PROMPT = "optimize_prompt"
    ANALYZE_PROMPT = "analyze_prompt"
    GENERATE_VARIATIONS = "generate_variations"
    
    # Role-based prompts
    CREATE_SYSTEM_PROMPT = "create_system_prompt"
    CREATE_USER_PROMPT = "create_user_prompt"
    CREATE_ASSISTANT_PROMPT = "create_assistant_prompt"

@dataclass
class PromptTemplate:
    """Prompt template structure."""
    name: str
    template: str
    variables: List[str]
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    version: str = "1.0"

@dataclass
class PromptChain:
    """Chain of prompt templates."""
    name: str
    templates: List[str]
    variables: Dict[str, Any]
    description: Optional[str] = None

class PromptTemplatingNode(BaseNode):
    def __init__(self):
        schema = NodeSchema(
            name="PromptTemplating",
            version="1.0.0",
            description="Advanced prompt templating, chaining, and optimization for LLM operations",
            auth_params=[],
            parameters=[
                NodeParameter(
                    name="operation",
                    param_type=NodeParameterType.SELECT,
                    required=True,
                    description="Prompt templating operation to perform",
                    options=[
                        {"label": "Create Template", "value": "create_template"},
                        {"label": "Render Template", "value": "render_template"},
                        {"label": "Validate Template", "value": "validate_template"},
                        {"label": "Save Template", "value": "save_template"},
                        {"label": "Load Template", "value": "load_template"},
                        {"label": "List Templates", "value": "list_templates"},
                        {"label": "Delete Template", "value": "delete_template"},
                        {"label": "Extract Variables", "value": "extract_variables"},
                        {"label": "Set Variables", "value": "set_variables"},
                        {"label": "Get Variables", "value": "get_variables"},
                        {"label": "Validate Variables", "value": "validate_variables"},
                        {"label": "Create Chain", "value": "create_chain"},
                        {"label": "Execute Chain", "value": "execute_chain"},
                        {"label": "Add to Chain", "value": "add_to_chain"},
                        {"label": "Conditional Template", "value": "conditional_template"},
                        {"label": "Loop Template", "value": "loop_template"},
                        {"label": "Include Template", "value": "include_template"},
                        {"label": "Optimize Prompt", "value": "optimize_prompt"},
                        {"label": "Analyze Prompt", "value": "analyze_prompt"},
                        {"label": "Generate Variations", "value": "generate_variations"},
                        {"label": "Create System Prompt", "value": "create_system_prompt"},
                        {"label": "Create User Prompt", "value": "create_user_prompt"},
                        {"label": "Create Assistant Prompt", "value": "create_assistant_prompt"}
                    ]
                ),
                NodeParameter(
                    name="template",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Template string with variables (e.g., 'Hello {{name}}')"
                ),
                NodeParameter(
                    name="template_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of the template"
                ),
                NodeParameter(
                    name="variables",
                    param_type=NodeParameterType.JSON,
                    required=False,
                    description="Variables for template rendering as JSON object"
                ),
                NodeParameter(
                    name="variable_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of a specific variable"
                ),
                NodeParameter(
                    name="variable_value",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Value of a specific variable"
                ),
                NodeParameter(
                    name="description",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Description of the template or chain"
                ),
                NodeParameter(
                    name="category",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Template category",
                    options=[
                        {"label": "General", "value": "general"},
                        {"label": "System", "value": "system"},
                        {"label": "User", "value": "user"},
                        {"label": "Assistant", "value": "assistant"},
                        {"label": "Analysis", "value": "analysis"},
                        {"label": "Creative", "value": "creative"},
                        {"label": "Technical", "value": "technical"},
                        {"label": "Business", "value": "business"}
                    ],
                    default_value="general"
                ),
                NodeParameter(
                    name="chain_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of the prompt chain"
                ),
                NodeParameter(
                    name="templates",
                    param_type=NodeParameterType.JSON,
                    required=False,
                    description="Array of template names for chaining"
                ),
                NodeParameter(
                    name="condition",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Condition for conditional templates"
                ),
                NodeParameter(
                    name="condition_variable",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Variable to check for conditions"
                ),
                NodeParameter(
                    name="true_template",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Template to use when condition is true"
                ),
                NodeParameter(
                    name="false_template",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Template to use when condition is false"
                ),
                NodeParameter(
                    name="loop_variable",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Variable containing array for looping"
                ),
                NodeParameter(
                    name="loop_template",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Template to repeat for each loop item"
                ),
                NodeParameter(
                    name="separator",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Separator for joining loop results",
                    default_value="\n"
                ),
                NodeParameter(
                    name="include_template_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name of template to include"
                ),
                NodeParameter(
                    name="optimization_goal",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Goal for prompt optimization",
                    options=[
                        {"label": "Clarity", "value": "clarity"},
                        {"label": "Conciseness", "value": "conciseness"},
                        {"label": "Specificity", "value": "specificity"},
                        {"label": "Engagement", "value": "engagement"},
                        {"label": "Accuracy", "value": "accuracy"}
                    ],
                    default_value="clarity"
                ),
                NodeParameter(
                    name="variation_count",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Number of variations to generate",
                    default_value=3
                ),
                NodeParameter(
                    name="role_context",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Context for role-based prompts"
                ),
                NodeParameter(
                    name="expertise_level",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Expertise level for role-based prompts",
                    options=[
                        {"label": "Beginner", "value": "beginner"},
                        {"label": "Intermediate", "value": "intermediate"},
                        {"label": "Advanced", "value": "advanced"},
                        {"label": "Expert", "value": "expert"}
                    ],
                    default_value="intermediate"
                ),
                NodeParameter(
                    name="output_format",
                    param_type=NodeParameterType.SELECT,
                    required=False,
                    description="Desired output format",
                    options=[
                        {"label": "Text", "value": "text"},
                        {"label": "JSON", "value": "json"},
                        {"label": "Markdown", "value": "markdown"},
                        {"label": "HTML", "value": "html"},
                        {"label": "Bullet Points", "value": "bullets"},
                        {"label": "Numbered List", "value": "numbered"}
                    ],
                    default_value="text"
                ),
                NodeParameter(
                    name="save_to_library",
                    param_type=NodeParameterType.BOOLEAN,
                    required=False,
                    description="Save created templates to library",
                    default_value=False
                )
            ],
            icon_path="https://cdn.jsdelivr.net/gh/microsoft/vscode-icons/icons/file_type_mustache.svg"
        )
        super().__init__(schema)
        
        # Template storage (in production, this would be a database)
        self.templates: Dict[str, PromptTemplate] = {}
        self.chains: Dict[str, PromptChain] = {}
        self.variables: Dict[str, Any] = {}
        
        # Load built-in templates
        self._load_builtin_templates()

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        operation = params.get("operation")
        
        if operation == "create_template":
            return await self._create_template(params)
        elif operation == "render_template":
            return await self._render_template(params)
        elif operation == "validate_template":
            return await self._validate_template(params)
        elif operation == "save_template":
            return await self._save_template(params)
        elif operation == "load_template":
            return await self._load_template(params)
        elif operation == "list_templates":
            return await self._list_templates(params)
        elif operation == "delete_template":
            return await self._delete_template(params)
        elif operation == "extract_variables":
            return await self._extract_variables(params)
        elif operation == "set_variables":
            return await self._set_variables(params)
        elif operation == "get_variables":
            return await self._get_variables(params)
        elif operation == "validate_variables":
            return await self._validate_variables(params)
        elif operation == "create_chain":
            return await self._create_chain(params)
        elif operation == "execute_chain":
            return await self._execute_chain(params)
        elif operation == "add_to_chain":
            return await self._add_to_chain(params)
        elif operation == "conditional_template":
            return await self._conditional_template(params)
        elif operation == "loop_template":
            return await self._loop_template(params)
        elif operation == "include_template":
            return await self._include_template(params)
        elif operation == "optimize_prompt":
            return await self._optimize_prompt(params)
        elif operation == "analyze_prompt":
            return await self._analyze_prompt(params)
        elif operation == "generate_variations":
            return await self._generate_variations(params)
        elif operation == "create_system_prompt":
            return await self._create_system_prompt(params)
        elif operation == "create_user_prompt":
            return await self._create_user_prompt(params)
        elif operation == "create_assistant_prompt":
            return await self._create_assistant_prompt(params)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    async def _create_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt template."""
        template_str = params.get("template", "")
        name = params.get("template_name", f"template_{len(self.templates) + 1}")
        description = params.get("description", "")
        category = params.get("category", "general")
        
        if not template_str:
            raise ValueError("Template string is required")
        
        # Extract variables from template
        variables = self._extract_template_variables(template_str)
        
        # Create template object
        template = PromptTemplate(
            name=name,
            template=template_str,
            variables=variables,
            description=description,
            category=category,
            created_at=datetime.now().isoformat()
        )
        
        # Save if requested
        if params.get("save_to_library", False):
            self.templates[name] = template
        
        return {
            "template_name": name,
            "template": template_str,
            "variables": variables,
            "variable_count": len(variables),
            "description": description,
            "category": category,
            "created_at": template.created_at,
            "saved_to_library": params.get("save_to_library", False)
        }

    async def _render_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render a template with provided variables."""
        template_str = params.get("template")
        template_name = params.get("template_name")
        variables = params.get("variables", {})
        
        # Get template string
        if template_name and template_name in self.templates:
            template_str = self.templates[template_name].template
        elif not template_str:
            raise ValueError("Either template string or template_name is required")
        
        # Merge with stored variables
        all_variables = {**self.variables, **variables}
        
        # Render template
        rendered = self._render_template_string(template_str, all_variables)
        
        # Extract any missing variables
        missing_vars = self._find_missing_variables(template_str, all_variables)
        
        return {
            "rendered_template": rendered,
            "variables_used": all_variables,
            "missing_variables": missing_vars,
            "template_complete": len(missing_vars) == 0,
            "character_count": len(rendered),
            "word_count": len(rendered.split())
        }

    async def _validate_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template syntax and structure."""
        template_str = params.get("template", "")
        
        if not template_str:
            raise ValueError("Template string is required for validation")
        
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check for basic syntax issues
        variable_pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(variable_pattern, template_str)
        
        # Check for unclosed variables
        open_braces = template_str.count('{{')
        close_braces = template_str.count('}}')
        
        if open_braces != close_braces:
            validation_results["is_valid"] = False
            validation_results["errors"].append("Mismatched braces: unclosed variable declarations")
        
        # Check for invalid variable names
        for var in variables:
            var = var.strip()
            if not var:
                validation_results["errors"].append("Empty variable name found")
                validation_results["is_valid"] = False
            elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var):
                validation_results["warnings"].append(f"Variable '{var}' contains special characters")
        
        # Check for duplicate variables
        unique_vars = list(set(variables))
        if len(variables) != len(unique_vars):
            validation_results["warnings"].append("Duplicate variables found")
        
        # Suggestions
        if len(template_str) < 10:
            validation_results["suggestions"].append("Template seems very short - consider adding more context")
        
        if not variables:
            validation_results["warnings"].append("No variables found - this is a static template")
        
        return {
            "validation_results": validation_results,
            "variables_found": unique_vars,
            "variable_count": len(unique_vars),
            "template_length": len(template_str),
            "complexity_score": self._calculate_template_complexity(template_str)
        }

    async def _extract_variables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract variables from a template."""
        template_str = params.get("template", "")
        
        if not template_str:
            raise ValueError("Template string is required")
        
        variables = self._extract_template_variables(template_str)
        
        # Analyze variable usage
        variable_usage = {}
        for var in variables:
            count = len(re.findall(r'\{\{\s*' + re.escape(var) + r'\s*\}\}', template_str))
            variable_usage[var] = count
        
        return {
            "variables": variables,
            "variable_count": len(variables),
            "variable_usage": variable_usage,
            "most_used_variable": max(variable_usage, key=variable_usage.get) if variable_usage else None,
            "template_preview": template_str[:100] + "..." if len(template_str) > 100 else template_str
        }

    async def _create_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chain of prompt templates."""
        chain_name = params.get("chain_name", f"chain_{len(self.chains) + 1}")
        templates = params.get("templates", [])
        description = params.get("description", "")
        variables = params.get("variables", {})
        
        if not templates:
            raise ValueError("Templates array is required for chain creation")
        
        # Validate that all templates exist
        missing_templates = []
        for template_name in templates:
            if template_name not in self.templates:
                missing_templates.append(template_name)
        
        if missing_templates:
            raise ValueError(f"Templates not found: {', '.join(missing_templates)}")
        
        # Create chain
        chain = PromptChain(
            name=chain_name,
            templates=templates,
            variables=variables,
            description=description
        )
        
        self.chains[chain_name] = chain
        
        return {
            "chain_name": chain_name,
            "templates": templates,
            "template_count": len(templates),
            "variables": variables,
            "description": description,
            "created_at": datetime.now().isoformat()
        }

    async def _execute_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a prompt chain."""
        chain_name = params.get("chain_name")
        variables = params.get("variables", {})
        
        if not chain_name or chain_name not in self.chains:
            raise ValueError(f"Chain '{chain_name}' not found")
        
        chain = self.chains[chain_name]
        
        # Merge variables
        all_variables = {**chain.variables, **self.variables, **variables}
        
        # Execute each template in the chain
        results = []
        accumulated_output = ""
        
        for i, template_name in enumerate(chain.templates):
            if template_name not in self.templates:
                raise ValueError(f"Template '{template_name}' not found in chain")
            
            template = self.templates[template_name]
            
            # Add previous output as a variable for chaining
            chain_variables = {**all_variables, "previous_output": accumulated_output}
            
            rendered = self._render_template_string(template.template, chain_variables)
            
            results.append({
                "step": i + 1,
                "template_name": template_name,
                "rendered": rendered,
                "variables_used": list(template.variables)
            })
            
            accumulated_output = rendered
        
        return {
            "chain_name": chain_name,
            "execution_results": results,
            "final_output": accumulated_output,
            "steps_executed": len(results),
            "variables_used": all_variables,
            "execution_time": datetime.now().isoformat()
        }

    async def _conditional_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render template based on condition."""
        condition_variable = params.get("condition_variable", "")
        true_template = params.get("true_template", "")
        false_template = params.get("false_template", "")
        variables = params.get("variables", {})
        
        if not all([condition_variable, true_template, false_template]):
            raise ValueError("condition_variable, true_template, and false_template are required")
        
        # Merge variables
        all_variables = {**self.variables, **variables}
        
        # Evaluate condition
        condition_value = all_variables.get(condition_variable)
        condition_met = bool(condition_value)
        
        # Choose template
        chosen_template = true_template if condition_met else false_template
        
        # Render chosen template
        rendered = self._render_template_string(chosen_template, all_variables)
        
        return {
            "condition_variable": condition_variable,
            "condition_value": condition_value,
            "condition_met": condition_met,
            "template_used": "true_template" if condition_met else "false_template",
            "rendered_output": rendered,
            "variables_used": all_variables
        }

    async def _loop_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render template in a loop over array data."""
        loop_variable = params.get("loop_variable", "")
        loop_template = params.get("loop_template", "")
        separator = params.get("separator", "\n")
        variables = params.get("variables", {})
        
        if not all([loop_variable, loop_template]):
            raise ValueError("loop_variable and loop_template are required")
        
        # Merge variables
        all_variables = {**self.variables, **variables}
        
        # Get loop data
        loop_data = all_variables.get(loop_variable, [])
        
        if not isinstance(loop_data, list):
            raise ValueError(f"Loop variable '{loop_variable}' must be an array")
        
        # Render template for each item
        results = []
        for i, item in enumerate(loop_data):
            loop_vars = {
                **all_variables,
                "item": item,
                "index": i,
                "is_first": i == 0,
                "is_last": i == len(loop_data) - 1
            }
            
            rendered = self._render_template_string(loop_template, loop_vars)
            results.append(rendered)
        
        # Join results
        final_output = separator.join(results)
        
        return {
            "loop_variable": loop_variable,
            "loop_data_count": len(loop_data),
            "loop_results": results,
            "final_output": final_output,
            "separator": separator,
            "variables_used": all_variables
        }

    async def _optimize_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a prompt for better performance."""
        template_str = params.get("template", "")
        optimization_goal = params.get("optimization_goal", "clarity")
        
        if not template_str:
            raise ValueError("Template is required for optimization")
        
        original_template = template_str
        optimized_template = template_str
        
        optimizations_applied = []
        
        # Apply optimizations based on goal
        if optimization_goal == "clarity":
            optimized_template, clarity_opts = self._optimize_for_clarity(optimized_template)
            optimizations_applied.extend(clarity_opts)
        
        elif optimization_goal == "conciseness":
            optimized_template, concise_opts = self._optimize_for_conciseness(optimized_template)
            optimizations_applied.extend(concise_opts)
        
        elif optimization_goal == "specificity":
            optimized_template, specific_opts = self._optimize_for_specificity(optimized_template)
            optimizations_applied.extend(specific_opts)
        
        elif optimization_goal == "engagement":
            optimized_template, engagement_opts = self._optimize_for_engagement(optimized_template)
            optimizations_applied.extend(engagement_opts)
        
        elif optimization_goal == "accuracy":
            optimized_template, accuracy_opts = self._optimize_for_accuracy(optimized_template)
            optimizations_applied.extend(accuracy_opts)
        
        # Calculate improvement metrics
        improvement_score = self._calculate_improvement_score(original_template, optimized_template, optimization_goal)
        
        return {
            "original_template": original_template,
            "optimized_template": optimized_template,
            "optimization_goal": optimization_goal,
            "optimizations_applied": optimizations_applied,
            "improvement_score": improvement_score,
            "character_reduction": len(original_template) - len(optimized_template),
            "word_reduction": len(original_template.split()) - len(optimized_template.split())
        }

    async def _generate_variations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate variations of a prompt template."""
        template_str = params.get("template", "")
        variation_count = params.get("variation_count", 3)
        
        if not template_str:
            raise ValueError("Template is required for variation generation")
        
        variations = []
        
        for i in range(variation_count):
            variation = self._create_variation(template_str, i + 1)
            variations.append({
                "variation_number": i + 1,
                "template": variation,
                "variation_type": self._get_variation_type(i),
                "character_count": len(variation),
                "word_count": len(variation.split())
            })
        
        return {
            "original_template": template_str,
            "variations": variations,
            "variation_count": len(variations),
            "best_variation": self._select_best_variation(variations),
            "generation_method": "rule_based"
        }

    async def _create_system_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a system prompt with role and context."""
        role_context = params.get("role_context", "helpful assistant")
        expertise_level = params.get("expertise_level", "intermediate")
        output_format = params.get("output_format", "text")
        
        system_prompt = self._build_system_prompt(role_context, expertise_level, output_format)
        
        template_name = f"system_{role_context.replace(' ', '_').lower()}"
        
        # Save if requested
        if params.get("save_to_library", False):
            self.templates[template_name] = PromptTemplate(
                name=template_name,
                template=system_prompt,
                variables=self._extract_template_variables(system_prompt),
                description=f"System prompt for {role_context}",
                category="system",
                created_at=datetime.now().isoformat()
            )
        
        return {
            "system_prompt": system_prompt,
            "template_name": template_name,
            "role_context": role_context,
            "expertise_level": expertise_level,
            "output_format": output_format,
            "variables": self._extract_template_variables(system_prompt),
            "saved_to_library": params.get("save_to_library", False)
        }

    # Helper methods
    def _extract_template_variables(self, template: str) -> List[str]:
        """Extract variable names from template."""
        pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(pattern, template)
        return [var.strip() for var in variables]

    def _render_template_string(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template string with variables."""
        rendered = template
        
        for var_name, var_value in variables.items():
            pattern = r'\{\{\s*' + re.escape(var_name) + r'\s*\}\}'
            rendered = re.sub(pattern, str(var_value), rendered)
        
        return rendered

    def _find_missing_variables(self, template: str, variables: Dict[str, Any]) -> List[str]:
        """Find variables that are in template but not provided."""
        template_vars = set(self._extract_template_variables(template))
        provided_vars = set(variables.keys())
        return list(template_vars - provided_vars)

    def _calculate_template_complexity(self, template: str) -> float:
        """Calculate complexity score for template."""
        variable_count = len(self._extract_template_variables(template))
        template_length = len(template)
        
        # Simple complexity calculation
        complexity = (variable_count * 2) + (template_length / 100)
        return round(complexity, 2)

    def _optimize_for_clarity(self, template: str) -> tuple:
        """Optimize template for clarity."""
        optimized = template
        optimizations = []
        
        # Add clarity improvements
        if not optimized.endswith('.') and not optimized.endswith('?'):
            optimized += '.'
            optimizations.append("Added proper punctuation")
        
        # Replace vague terms
        vague_replacements = {
            r'\bstuff\b': 'information',
            r'\bthing\b': 'item',
            r'\bdo\b': 'perform',
        }
        
        for pattern, replacement in vague_replacements.items():
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                optimizations.append(f"Replaced vague term with '{replacement}'")
        
        return optimized, optimizations

    def _optimize_for_conciseness(self, template: str) -> tuple:
        """Optimize template for conciseness."""
        optimized = template
        optimizations = []
        
        # Remove redundant words
        redundant_patterns = [
            (r'\bplease\s+', ''),
            (r'\bkindly\s+', ''),
            (r'\bin order to\b', 'to'),
        ]
        
        for pattern, replacement in redundant_patterns:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                optimizations.append("Removed redundant words")
        
        return optimized, optimizations

    def _optimize_for_specificity(self, template: str) -> tuple:
        """Optimize template for specificity."""
        optimized = template
        optimizations = []
        
        # Add specific instructions
        if 'analyze' in optimized.lower() and 'how' not in optimized.lower():
            optimized += " Provide specific examples and reasoning."
            optimizations.append("Added specificity instruction")
        
        return optimized, optimizations

    def _optimize_for_engagement(self, template: str) -> tuple:
        """Optimize template for engagement."""
        optimized = template
        optimizations = []
        
        # Add engaging elements
        if not any(word in optimized.lower() for word in ['why', 'how', 'what']):
            optimized = "Let's explore: " + optimized
            optimizations.append("Added engaging introduction")
        
        return optimized, optimizations

    def _optimize_for_accuracy(self, template: str) -> tuple:
        """Optimize template for accuracy."""
        optimized = template
        optimizations = []
        
        # Add accuracy instructions
        if 'fact' not in optimized.lower() and 'accurate' not in optimized.lower():
            optimized += " Please ensure accuracy and cite sources if applicable."
            optimizations.append("Added accuracy requirement")
        
        return optimized, optimizations

    def _calculate_improvement_score(self, original: str, optimized: str, goal: str) -> float:
        """Calculate improvement score."""
        # Simple scoring based on goal
        if goal == "conciseness":
            return max(0, (len(original) - len(optimized)) / len(original) * 100)
        elif goal == "clarity":
            return 75.0  # Placeholder score
        else:
            return 80.0  # Default improvement score

    def _create_variation(self, template: str, variation_num: int) -> str:
        """Create a variation of the template."""
        variations = {
            1: lambda t: t.replace("Please", "Could you"),
            2: lambda t: t.replace("analyze", "examine"),
            3: lambda t: f"Task: {t}"
        }
        
        if variation_num in variations:
            return variations[variation_num](template)
        return template

    def _get_variation_type(self, index: int) -> str:
        """Get variation type description."""
        types = ["polite", "formal", "structured"]
        return types[index % len(types)]

    def _select_best_variation(self, variations: List[Dict]) -> Dict:
        """Select the best variation based on criteria."""
        # Simple selection - return the first variation
        return variations[0] if variations else {}

    def _build_system_prompt(self, role_context: str, expertise_level: str, output_format: str) -> str:
        """Build a system prompt with role and context."""
        base_prompt = f"You are a {expertise_level} {role_context}."
        
        if output_format != "text":
            base_prompt += f" Respond in {output_format} format."
        
        expertise_additions = {
            "beginner": " Explain concepts clearly and avoid jargon.",
            "intermediate": " Provide balanced detail and examples.",
            "advanced": " Include technical depth and nuanced analysis.",
            "expert": " Provide comprehensive, authoritative insights."
        }
        
        base_prompt += expertise_additions.get(expertise_level, "")
        
        return base_prompt

    def _load_builtin_templates(self):
        """Load built-in template library."""
        builtin_templates = {
            "analysis": PromptTemplate(
                name="analysis",
                template="Analyze the following {{content}} and provide insights about {{focus_area}}. Consider {{context}} in your analysis.",
                variables=["content", "focus_area", "context"],
                description="General analysis template",
                category="analysis"
            ),
            "creative_writing": PromptTemplate(
                name="creative_writing",
                template="Write a {{style}} {{content_type}} about {{topic}}. The tone should be {{tone}} and target audience is {{audience}}.",
                variables=["style", "content_type", "topic", "tone", "audience"],
                description="Creative writing template",
                category="creative"
            ),
            "question_answer": PromptTemplate(
                name="question_answer",
                template="Answer the following question: {{question}}. Provide a {{detail_level}} response with {{format}} format.",
                variables=["question", "detail_level", "format"],
                description="Question answering template",
                category="general"
            )
        }
        
        self.templates.update(builtin_templates)

    async def _save_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save a template to the library."""
        template_name = params.get("template_name")
        template_str = params.get("template")
        
        if not template_name or not template_str:
            raise ValueError("template_name and template are required")
        
        template = PromptTemplate(
            name=template_name,
            template=template_str,
            variables=self._extract_template_variables(template_str),
            description=params.get("description", ""),
            category=params.get("category", "general"),
            created_at=datetime.now().isoformat()
        )
        
        self.templates[template_name] = template
        
        return {
            "template_name": template_name,
            "saved": True,
            "variables": template.variables,
            "category": template.category
        }

    async def _load_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load a template from the library."""
        template_name = params.get("template_name")
        
        if not template_name:
            raise ValueError("template_name is required")
        
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        return {
            "template_name": template.name,
            "template": template.template,
            "variables": template.variables,
            "description": template.description,
            "category": template.category,
            "created_at": template.created_at
        }

    async def _list_templates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all templates in the library."""
        category_filter = params.get("category")
        
        templates_list = []
        for name, template in self.templates.items():
            if category_filter and template.category != category_filter:
                continue
                
            templates_list.append({
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "variable_count": len(template.variables),
                "created_at": template.created_at
            })
        
        return {
            "templates": templates_list,
            "total_count": len(templates_list),
            "category_filter": category_filter,
            "categories": list(set(t.category for t in self.templates.values()))
        }

    async def _delete_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a template from the library."""
        template_name = params.get("template_name")
        
        if not template_name:
            raise ValueError("template_name is required")
        
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        del self.templates[template_name]
        
        return {
            "template_name": template_name,
            "deleted": True,
            "remaining_templates": len(self.templates)
        }

    async def _set_variables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set global variables for templates."""
        variables = params.get("variables", {})
        variable_name = params.get("variable_name")
        variable_value = params.get("variable_value")
        
        if variable_name and variable_value is not None:
            self.variables[variable_name] = variable_value
            return {
                "variable_set": variable_name,
                "value": variable_value,
                "total_variables": len(self.variables)
            }
        elif variables:
            self.variables.update(variables)
            return {
                "variables_set": list(variables.keys()),
                "total_variables": len(self.variables)
            }
        else:
            raise ValueError("Either variables object or variable_name/variable_value pair is required")

    async def _get_variables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get global variables."""
        variable_name = params.get("variable_name")
        
        if variable_name:
            return {
                "variable_name": variable_name,
                "value": self.variables.get(variable_name),
                "exists": variable_name in self.variables
            }
        else:
            return {
                "variables": self.variables,
                "variable_count": len(self.variables)
            }

    async def _validate_variables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate variables against template requirements."""
        template_str = params.get("template")
        template_name = params.get("template_name")
        variables = params.get("variables", {})
        
        # Get template
        if template_name and template_name in self.templates:
            template_str = self.templates[template_name].template
        elif not template_str:
            raise ValueError("Either template or template_name is required")
        
        # Extract required variables
        required_vars = self._extract_template_variables(template_str)
        provided_vars = list(variables.keys())
        
        missing_vars = [var for var in required_vars if var not in provided_vars]
        extra_vars = [var for var in provided_vars if var not in required_vars]
        
        return {
            "validation_passed": len(missing_vars) == 0,
            "required_variables": required_vars,
            "provided_variables": provided_vars,
            "missing_variables": missing_vars,
            "extra_variables": extra_vars,
            "template_ready": len(missing_vars) == 0
        }

    async def _add_to_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a template to an existing chain."""
        chain_name = params.get("chain_name")
        template_name = params.get("template_name")
        
        if not chain_name or chain_name not in self.chains:
            raise ValueError(f"Chain '{chain_name}' not found")
        
        if not template_name or template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        chain = self.chains[chain_name]
        chain.templates.append(template_name)
        
        return {
            "chain_name": chain_name,
            "template_added": template_name,
            "new_template_count": len(chain.templates),
            "chain_templates": chain.templates
        }

    async def _include_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Include one template within another."""
        template_str = params.get("template", "")
        include_template_name = params.get("include_template_name")
        variables = params.get("variables", {})
        
        if not include_template_name or include_template_name not in self.templates:
            raise ValueError(f"Include template '{include_template_name}' not found")
        
        include_template = self.templates[include_template_name]
        
        # Render the include template
        include_rendered = self._render_template_string(include_template.template, variables)
        
        # Replace include directive in main template
        include_pattern = r'\{\{\s*include\s+' + re.escape(include_template_name) + r'\s*\}\}'
        final_template = re.sub(include_pattern, include_rendered, template_str)
        
        return {
            "original_template": template_str,
            "final_template": final_template,
            "included_template": include_template_name,
            "included_content": include_rendered,
            "variables_used": variables
        }

    async def _analyze_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a prompt for various characteristics."""
        template_str = params.get("template", "")
        
        if not template_str:
            raise ValueError("Template is required for analysis")
        
        # Basic metrics
        char_count = len(template_str)
        word_count = len(template_str.split())
        sentence_count = len(re.split(r'[.!?]+', template_str))
        
        # Variable analysis
        variables = self._extract_template_variables(template_str)
        
        # Complexity analysis
        complexity_score = self._calculate_template_complexity(template_str)
        
        # Content analysis
        question_words = len(re.findall(r'\b(what|how|why|when|where|which|who)\b', template_str, re.IGNORECASE))
        instruction_words = len(re.findall(r'\b(analyze|create|write|explain|describe|compare|list)\b', template_str, re.IGNORECASE))
        
        # Readability estimate (simple)
        avg_word_length = sum(len(word) for word in template_str.split()) / word_count if word_count > 0 else 0
        
        return {
            "template": template_str[:100] + "..." if len(template_str) > 100 else template_str,
            "metrics": {
                "character_count": char_count,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "average_word_length": round(avg_word_length, 2)
            },
            "variables": {
                "count": len(variables),
                "names": variables
            },
            "complexity": {
                "score": complexity_score,
                "level": "low" if complexity_score < 5 else "medium" if complexity_score < 10 else "high"
            },
            "content_analysis": {
                "question_words": question_words,
                "instruction_words": instruction_words,
                "prompt_type": "question" if question_words > instruction_words else "instruction"
            },
            "recommendations": self._get_prompt_recommendations(template_str, complexity_score)
        }

    def _get_prompt_recommendations(self, template: str, complexity: float) -> List[str]:
        """Get recommendations for improving the prompt."""
        recommendations = []
        
        if complexity < 2:
            recommendations.append("Consider adding more specific instructions or context")
        
        if len(template.split()) < 10:
            recommendations.append("Prompt might be too short - consider adding more detail")
        
        if not any(word in template.lower() for word in ['please', 'analyze', 'explain', 'describe']):
            recommendations.append("Consider adding clear action words (analyze, explain, describe)")
        
        variables = self._extract_template_variables(template)
        if not variables:
            recommendations.append("Consider adding variables to make the template reusable")
        
        return recommendations