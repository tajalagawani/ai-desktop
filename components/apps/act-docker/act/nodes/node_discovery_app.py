#!/usr/bin/env python3
"""
Generic Node Discovery and Config Generation FastAPI App

Completely generic and dynamic system that discovers UniversalRequestNode-based nodes
and extracts ALL information directly from the node files themselves.

NO HARDCODED DATA - Everything is extracted dynamically from node CONFIG and OPERATIONS.

Features:
- Pure dynamic node discovery from filesystem
- CONFIG and OPERATIONS parsing from node files
- Complete metadata extraction from embedded node configurations
- Zero hardcoded mappings or vendor data
- Automatic config generation matching original node quality
- Generic endpoints that work with ANY properly structured node
"""

import ast
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

app = FastAPI(
    title="Generic Node Discovery & Config Generator",
    description="Completely generic system that discovers UniversalRequestNode-based nodes with zero hardcoded data",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class NodeInfo:
    """Information extracted dynamically from a node file"""
    name: str
    file_path: str
    class_name: str
    config: Dict[str, Any]
    operations: Dict[str, Any]

class GenericNodeDiscovery:
    """Completely generic node discovery with zero hardcoded data"""
    
    def __init__(self, nodes_directory: str = None):
        self.nodes_dir = Path(nodes_directory) if nodes_directory else Path(__file__).parent
        self.discovered_nodes: List[NodeInfo] = []
    
    def discover_nodes(self) -> List[NodeInfo]:
        """Discover all UniversalRequestNode-based nodes dynamically"""
        nodes = []
        
        for file_path in self.nodes_dir.glob("*Node.py"):
            if file_path.name in ["BaseNode.py", "UniversalRequestNode.py"]:
                continue
                
            try:
                node_info = self._analyze_node_file(file_path)
                if node_info:
                    nodes.append(node_info)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        self.discovered_nodes = nodes
        return nodes
    
    def _analyze_node_file(self, file_path: Path) -> Optional[NodeInfo]:
        """Analyze a single node file and extract ALL information dynamically"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it uses UniversalRequestNode
            if "UniversalRequestNode" not in content:
                return None
            
            # Parse the AST to extract CONFIG and OPERATIONS
            tree = ast.parse(content)
            
            class_name = None
            config = {}
            operations = {}
            
            for node in ast.walk(tree):
                # Find the main class
                if isinstance(node, ast.ClassDef) and node.name.endswith("Node"):
                    class_name = node.name
                
                # Find CONFIG assignment
                if (isinstance(node, ast.Assign) and 
                    any(isinstance(target, ast.Name) and target.id == "CONFIG" for target in node.targets)):
                    config = self._eval_ast_dict(node.value)
                
                # Find OPERATIONS assignment
                if (isinstance(node, ast.Assign) and 
                    any(isinstance(target, ast.Name) and target.id == "OPERATIONS" for target in node.targets)):
                    operations = self._eval_ast_dict(node.value)
            
            if not class_name or not config or not operations:
                return None
            
            # Extract node name from class name
            node_name = class_name.replace("Node", "").lower()
            
            return NodeInfo(
                name=node_name,
                file_path=str(file_path),
                class_name=class_name,
                config=config,
                operations=operations
            )
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _eval_ast_dict(self, node) -> Dict[str, Any]:
        """Safely evaluate an AST node to extract dictionary data"""
        try:
            # Try literal_eval first for simple cases
            return ast.literal_eval(node)
        except:
            try:
                # For more complex cases, build the dict manually
                if isinstance(node, ast.Dict):
                    result = {}
                    for key, value in zip(node.keys, node.values):
                        if isinstance(key, ast.Constant):
                            result[key.value] = self._eval_ast_value(value)
                    return result
                return {}
            except:
                return {}
    
    def _eval_ast_value(self, node) -> Any:
        """Extract value from AST node"""
        try:
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Dict):
                return self._eval_ast_dict(node)
            elif isinstance(node, ast.List):
                return [self._eval_ast_value(item) for item in node.elts]
            else:
                return str(node)
        except:
            return None

class GenericConfigGenerator:
    """Generates config files directly from node CONFIG and OPERATIONS data"""
    
    def generate_config(self, node_info: NodeInfo) -> Dict[str, Any]:
        """Generate config by extracting ALL data from the node itself"""
        
        config = node_info.config
        operations = node_info.operations
        
        # If the node has structured config with node_info, use it directly
        if "node_info" in config:
            result = {
                "node_info": config["node_info"],
                "config": config.get("api_config", config),
                "operations": self._enhance_operations(operations),
                "parameters": config.get("parameters", {}),
                "outputs": config.get("outputs", self._generate_default_outputs()),
                "error_codes": config.get("error_codes", self._generate_default_error_codes())
            }
        else:
            # For legacy nodes, generate minimal structure
            result = {
                "node_info": self._generate_basic_node_info(node_info),
                "config": config,
                "operations": self._enhance_operations(operations),
                "parameters": self._extract_parameters_from_operations(operations),
                "outputs": self._generate_default_outputs(),
                "error_codes": self._generate_default_error_codes()
            }
        
        return result
    
    def _enhance_operations(self, operations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert operations dict to enhanced list format"""
        enhanced = []
        
        for op_name, op_config in operations.items():
            enhanced_op = {
                "name": op_name,
                "display_name": op_config.get("display_name", op_name.replace("_", " ").title()),
                "description": op_config.get("description", f"Perform {op_name} operation"),
                "method": op_config.get("method", "GET"),
                "endpoint": op_config.get("endpoint", "/"),
                "group": op_config.get("group", "General"),
                "required_parameters": op_config.get("required_params", []),
                "optional_parameters": op_config.get("optional_params", []),
                "response_type": op_config.get("response_type", "object"),
                "rate_limit_cost": op_config.get("rate_limit_cost", 1),
                "cache_ttl": op_config.get("cache_ttl", 0),
                "auth": op_config.get("auth", {}),
                "examples": op_config.get("examples", [])
            }
            enhanced.append(enhanced_op)
        
        return enhanced
    
    def _generate_basic_node_info(self, node_info: NodeInfo) -> Dict[str, Any]:
        """Generate basic node info for legacy nodes"""
        return {
            "name": node_info.name,
            "display_name": node_info.class_name.replace("Node", ""),
            "description": f"{node_info.class_name} integration",
            "category": "api",
            "vendor": None,
            "version": "1.0.0",
            "author": "ACT Workflow",
            "tags": [node_info.name],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def _extract_parameters_from_operations(self, operations: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from operations for legacy nodes"""
        parameters = {}
        
        # Add common operation parameter
        parameters["operation"] = {
            "type": "string",
            "description": "The operation to perform",
            "required": True,
            "enum": list(operations.keys()),
            "group": "Operation"
        }
        
        # Extract unique parameters from all operations
        all_params = set()
        for op_config in operations.values():
            all_params.update(op_config.get("required_params", []))
            all_params.update(op_config.get("optional_params", []))
            all_params.update(op_config.get("params", []))
        
        for param in all_params:
            if param not in parameters:
                parameters[param] = {
                    "type": "string",
                    "description": f"{param.replace('_', ' ').title()} parameter",
                    "required": False,
                    "group": "General"
                }
        
        return parameters
    
    def _generate_default_outputs(self) -> Dict[str, Any]:
        """Generate default output schema"""
        return {
            "success": {
                "type": "object",
                "description": "Successful API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data"},
                    "result": {"type": "object", "description": "Operation result"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Error code"}
                }
            }
        }
    
    def _generate_default_error_codes(self) -> Dict[str, str]:
        """Generate default error codes"""
        return {
            "400": "Bad Request - Invalid parameters",
            "401": "Unauthorized - Invalid or missing authentication",
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Server error",
            "502": "Bad Gateway - Upstream server error",
            "503": "Service Unavailable - Service temporarily unavailable"
        }

# Initialize discovery and generator
discovery = GenericNodeDiscovery()
generator = GenericConfigGenerator()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Generic Node Discovery & Config Generator API",
        "version": "2.0.0",
        "description": "Completely generic system with zero hardcoded data",
        "endpoints": {
            "/discover": "Discover all UniversalRequestNode-based nodes",
            "/nodes": "List all discovered nodes",
            "/nodes/{node_name}": "Get detailed info for specific node",
            "/nodes/{node_name}/config": "Get node CONFIG dict",
            "/nodes/{node_name}/operations": "Get all operations for node",
            "/nodes/{node_name}/operations/{operation_name}": "Get specific operation details",
            "/config/{node_name}": "Generate full config file for node",
            "/config/bulk": "Generate config files for all nodes"
        }
    }

@app.post("/discover")
async def discover_nodes():
    """Discover all UniversalRequestNode-based nodes dynamically"""
    try:
        nodes = discovery.discover_nodes()
        return {
            "status": "success",
            "discovered_count": len(nodes),
            "nodes": [
                {
                    "name": n.name, 
                    "class_name": n.class_name, 
                    "operations_count": len(n.operations),
                    "has_structured_config": "node_info" in n.config
                } for n in nodes
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

@app.get("/nodes")
async def list_nodes():
    """List all discovered nodes"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    result_nodes = []
    for node in discovery.discovered_nodes:
        node_info = node.config.get("node_info", {})
        
        result_nodes.append({
            "name": node.name,
            "class_name": node.class_name,
            "display_name": node_info.get("display_name", node.class_name.replace("Node", "")),
            "description": node_info.get("description", f"{node.class_name} integration")[:100] + "...",
            "vendor": node_info.get("vendor"),
            "category": node_info.get("category", "api"),
            "operations_count": len(node.operations),
            "file_path": node.file_path,
            "has_structured_config": "node_info" in node.config
        })
    
    return {
        "status": "success",
        "nodes": result_nodes
    }

@app.get("/nodes/{node_name}")
async def get_node_details(node_name: str):
    """Get detailed information for a specific node"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    node_info = next((n for n in discovery.discovered_nodes if n.name == node_name), None)
    if not node_info:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
    
    node_meta = node_info.config.get("node_info", {})
    
    return {
        "status": "success",
        "node": {
            "name": node_info.name,
            "class_name": node_info.class_name,
            "display_name": node_meta.get("display_name", node_info.class_name.replace("Node", "")),
            "description": node_meta.get("description", f"{node_info.class_name} integration"),
            "vendor": node_meta.get("vendor"),
            "category": node_meta.get("category", "api"),
            "version": node_meta.get("version", "1.0.0"),
            "tags": node_meta.get("tags", []),
            "file_path": node_info.file_path,
            "operations_count": len(node_info.operations),
            "operations_list": list(node_info.operations.keys()),
            "config_sections": list(node_info.config.keys()),
            "has_structured_config": "node_info" in node_info.config
        }
    }

@app.get("/nodes/{node_name}/config")
async def get_node_config(node_name: str):
    """Get the raw CONFIG dictionary for a specific node"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    node_info = next((n for n in discovery.discovered_nodes if n.name == node_name), None)
    if not node_info:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
    
    return {
        "status": "success",
        "node_name": node_name,
        "config": node_info.config
    }

@app.get("/nodes/{node_name}/operations")
async def get_node_operations(node_name: str):
    """Get all operations for a specific node"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    node_info = next((n for n in discovery.discovered_nodes if n.name == node_name), None)
    if not node_info:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
    
    return {
        "status": "success",
        "node_name": node_name,
        "operations_count": len(node_info.operations),
        "operations": node_info.operations
    }

@app.get("/nodes/{node_name}/operations/{operation_name}")
async def get_specific_operation(node_name: str, operation_name: str):
    """Get details for a specific operation of a node"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    node_info = next((n for n in discovery.discovered_nodes if n.name == node_name), None)
    if not node_info:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
    
    if operation_name not in node_info.operations:
        raise HTTPException(status_code=404, detail=f"Operation '{operation_name}' not found in node '{node_name}'")
    
    operation = node_info.operations[operation_name]
    
    return {
        "status": "success",
        "node_name": node_name,
        "operation_name": operation_name,
        "operation": operation
    }

@app.get("/nodes/{node_name}/operations/{operation_name}/schema")
async def get_operation_schema(node_name: str, operation_name: str):
    """Get schema for a specific operation of a node"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    node_info = next((n for n in discovery.discovered_nodes if n.name == node_name), None)
    if not node_info:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
    
    if operation_name not in node_info.operations:
        raise HTTPException(status_code=404, detail=f"Operation '{operation_name}' not found in node '{node_name}'")
    
    operation = node_info.operations[operation_name]
    
    # Generate schema from operation definition
    schema = {
        "status": "success",
        "node_name": node_name,
        "operation_name": operation_name,
        "schema": {
            "description": operation.get("description", f"Schema for {operation_name} operation"),
            "method": operation.get("method", "GET"),
            "endpoint": operation.get("endpoint", "/"),
            "parameters": operation.get("parameters", []),
            "required_parameters": operation.get("required_parameters", []),
            "body_parameters": operation.get("body_parameters", []),
            "response_type": operation.get("response_type", "object"),
            "auth": operation.get("auth", {}),
            "examples": operation.get("examples", [])
        }
    }
    
    return schema

@app.get("/config/{node_name}")
async def generate_node_config(node_name: str):
    """Generate comprehensive config for a specific node"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    node_info = next((n for n in discovery.discovered_nodes if n.name == node_name), None)
    if not node_info:
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found")
    
    try:
        config = generator.generate_config(node_info)
        return JSONResponse(content=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config generation failed: {str(e)}")

@app.post("/config/bulk")
async def generate_all_configs(
    save_to_disk: bool = Query(True, description="Save configs to nodes_config directory")
):
    """Generate configs for all discovered nodes"""
    if not discovery.discovered_nodes:
        await discover_nodes()
    
    results = []
    
    for node_info in discovery.discovered_nodes:
        try:
            config = generator.generate_config(node_info)
            
            if save_to_disk:
                # Save to nodes_config directory
                config_dir = Path(__file__).parent / "nodes_config"
                config_dir.mkdir(exist_ok=True)
                
                config_file = config_dir / f"{node_info.name}_config.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                results.append({
                    "node": node_info.name,
                    "status": "success",
                    "file_path": str(config_file),
                    "has_structured_config": "node_info" in node_info.config
                })
            else:
                results.append({
                    "node": node_info.name,
                    "status": "success",
                    "config": config,
                    "has_structured_config": "node_info" in node_info.config
                })
                
        except Exception as e:
            results.append({
                "node": node_info.name,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "status": "success",
        "processed_count": len(results),
        "results": results
    }

if __name__ == "__main__":
    print("Starting Generic Node Discovery & Config Generator API...")
    print("Available at: http://localhost:8002")
    print("\nZero hardcoded data - everything extracted dynamically from node files!")
    print("\nEndpoints:")
    print("- POST /discover - Discover all nodes")
    print("- GET /nodes - List all discovered nodes")
    print("- GET /nodes/{node_name} - Get detailed node info")
    print("- GET /nodes/{node_name}/config - Get node CONFIG dict")
    print("- GET /nodes/{node_name}/operations - Get all operations for node")
    print("- GET /nodes/{node_name}/operations/{operation_name} - Get specific operation details")
    print("- GET /config/{node_name} - Generate full config file for node")
    print("- POST /config/bulk - Generate all config files")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)