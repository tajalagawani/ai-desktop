import os
import importlib.util
import inspect
from flask import Flask, jsonify, request
from flask_cors import CORS  # For handling Cross-Origin Resource Sharing
import logging
import sys

# Add the nodes directory to the Python path - auto-detect based on current file location
nodes_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(nodes_dir)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("node_api.log")],
)

# Dictionary to store node classes and instances
nodes = {}


def make_serializable(obj):
    """Convert objects to JSON serializable format."""
    # Handle NodeParameter objects specifically
    if hasattr(obj, 'name') and hasattr(obj, 'type') and hasattr(obj, 'description'):
        result = {
            'name': obj.name,
            'type': obj.type.value if hasattr(obj.type, 'value') else str(obj.type),
            'description': obj.description,
            'required': getattr(obj, 'required', False),
        }
        # Add optional attributes if they exist
        if hasattr(obj, 'default') and obj.default is not None:
            result['default'] = make_serializable(obj.default)
        if hasattr(obj, 'enum') and obj.enum is not None:
            result['enum'] = obj.enum
        return result
    elif hasattr(obj, "__dict__"):
        return {
            k: make_serializable(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif hasattr(obj, "value") and not callable(obj.value):
        return obj.value
    else:
        # Try to convert to string or return as is if primitive type
        try:
            return (
                str(obj)
                if not isinstance(obj, (int, float, bool, str, type(None)))
                else obj
            )
        except:
            return str(type(obj))


def load_node_modules():
    """Dynamically load all Node classes from the nodes directory."""
    node_files = [f for f in os.listdir(nodes_dir) if f.endswith("Node.py") and f != "NodeTemplate.py"]

    for file in node_files:
        try:
            # Get the module name
            module_name = file[:-3]  # Remove .py extension

            # Load the module
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(nodes_dir, file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find node class in module
            for name, obj in inspect.getmembers(module):
                # Look for classes that have "Node" in their name and aren't base classes
                if (
                    inspect.isclass(obj)
                    and "Node" in name
                    and name != "BaseNode"
                    and name != "NodeRegistry"
                ):

                    # Try to instantiate the node
                    try:
                        node_instance = obj()
                        # Check if the class has get_schema method
                        if hasattr(node_instance, "get_schema"):
                            # Store the node class and instance
                            node_type = name.lower().replace("node", "")
                            nodes[node_type] = {"class": obj, "instance": node_instance}
                            logging.debug(f"Loaded node: {name}")
                    except Exception as e:
                        # Silently skip nodes that fail to instantiate (usually due to missing schema)
                        logging.debug(f"Skipped {name}: {str(e)}")

        except Exception as e:
            logging.debug(f"Error loading module {file}: {str(e)}")

    logging.info(f"Loaded {len(nodes)} node types")


@app.route("/api/nodes", methods=["GET"])
def get_all_nodes():
    """Return a list of all available nodes."""
    result = {}
    for node_type, node_data in nodes.items():
        try:
            schema = node_data["instance"].get_schema()
            result[node_type] = {
                "node_type": schema.node_type,
                "version": schema.version,
                "description": schema.description,
            }
        except Exception as e:
            result[node_type] = {"error": str(e)}

    return jsonify(result)


@app.route("/api/nodes/<node_type>", methods=["GET"])
def get_node_schema(node_type):
    """Return the complete schema for a specific node type."""
    if node_type not in nodes:
        return jsonify({"error": f"Node type {node_type} not found"}), 404

    try:
        schema = nodes[node_type]["instance"].get_schema()
        # Convert schema to dict for JSON serialization
        schema_dict = make_serializable(schema)
        return jsonify(schema_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/nodes/<node_type>/operations", methods=["GET"])
def get_node_operations(node_type):
    """Return all available operations for a specific node type."""
    if node_type not in nodes:
        return jsonify({"error": f"Node type {node_type} not found"}), 404

    try:
        node_instance = nodes[node_type]["instance"]
        operations = []

        # Method 1: Check for OpenAI-style operation parameters
        if hasattr(node_instance, "_operation_parameters"):
            operations = list(node_instance._operation_parameters.keys())

        # Method 2: Look for operation methods
        if not operations:
            for name, method in inspect.getmembers(node_instance, inspect.ismethod):
                if name.startswith("_operation_"):
                    operations.append(name[11:])  # Remove '_operation_' prefix

        # Method 3: Check schema for operation enum
        if not operations:
            schema = node_instance.get_schema()
            for param in schema.parameters:
                if param.name == "operation" and hasattr(param, "enum"):
                    operations = param.enum

        # Method 4: Check for an Operation class in the module
        if not operations:
            module = inspect.getmodule(node_instance.__class__)
            for name, obj in inspect.getmembers(module):
                if name.endswith("Operation") and inspect.isclass(obj):
                    # Extract operations from class attributes
                    for attr_name, attr_value in inspect.getmembers(obj):
                        if not attr_name.startswith("_") and isinstance(
                            attr_value, str
                        ):
                            operations.append(attr_value)

        # Add details if available
        operation_details = {}
        for op in operations:
            operation_details[op] = {
                "name": op,
                "description": f"Execute {op} operation",
                "endpoint": f"/api/nodes/{node_type}/operations/{op}",
            }

        return jsonify(
            {
                "node_type": node_type,
                "operations_count": len(operations),
                "operations": operation_details,
            }
        )
    except Exception as e:
        logging.error(f"Error getting operations for {node_type}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/nodes/<node_type>/operations/<operation>", methods=["GET"])
def get_operation_parameters(node_type, operation):
    """Return the parameters required for a specific operation."""
    if node_type not in nodes:
        return jsonify({"error": f"Node type {node_type} not found"}), 404

    try:
        node_instance = nodes[node_type]["instance"]

        # Method 1: Use get_operation_parameters if available
        if hasattr(node_instance, "get_operation_parameters"):
            params = node_instance.get_operation_parameters(operation)
            return jsonify(
                {"node_type": node_type, "operation": operation, "parameters": params}
            )

        # Method 2: Check _operation_parameters dictionary
        if hasattr(node_instance, "_operation_parameters"):
            param_names = node_instance._operation_parameters.get(operation.lower(), [])
            schema = node_instance.get_schema()
            all_params = schema.parameters

            # Filter parameters based on operation
            filtered_params = []
            for param in all_params:
                if param.name in param_names:
                    filtered_params.append(make_serializable(param))

            return jsonify(
                {
                    "node_type": node_type,
                    "operation": operation,
                    "parameters": filtered_params,
                }
            )

        # Method 3: For other nodes (fallback)
        schema = node_instance.get_schema()
        # Convert all parameters to serializable format
        all_params = [make_serializable(param) for param in schema.parameters]

        # As a fallback, return all parameters with a note
        return jsonify(
            {
                "node_type": node_type,
                "operation": operation,
                "note": "Operation-specific parameter filtering not available, showing all parameters",
                "parameters": all_params,
            }
        )
    except Exception as e:
        logging.error(f"Error getting parameters for {node_type}/{operation}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/execute/<node_type>", methods=["POST"])
def execute_node(node_type):
    """Execute a node with given parameters."""
    if node_type not in nodes:
        return jsonify({"error": f"Node type {node_type} not found"}), 404

    try:
        node_instance = nodes[node_type]["instance"]
        node_data = request.json

        # Check if the execute method is sync or async
        if inspect.iscoroutinefunction(node_instance.execute):
            # For async nodes, you'll need to run this in an event loop
            import asyncio

            result = asyncio.run(node_instance.execute(node_data))
        else:
            # For sync nodes
            result = node_instance.execute(node_data)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Load all node modules when the app starts
load_node_modules()


@app.route("/api/docs", methods=["GET"])
def get_api_docs():
    """Return API documentation in OpenAPI format."""
    swagger_doc = {
        "openapi": "3.0.0",
        "info": {
            "title": "Node API",
            "description": "API for interacting with workflow nodes",
            "version": "1.0.0",
        },
        "servers": [{"url": "/api", "description": "Node API Server"}],
        "paths": {
            "/nodes": {
                "get": {
                    "summary": "Get all nodes",
                    "description": "Returns a list of all available nodes",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        }
                    },
                }
            },
            "/nodes/{node_type}": {
                "get": {
                    "summary": "Get node schema",
                    "description": "Returns the schema for a specific node type",
                    "parameters": [
                        {
                            "name": "node_type",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        }
                    },
                }
            },
            "/nodes/{node_type}/operations": {
                "get": {
                    "summary": "Get node operations",
                    "description": "Returns all operations for a node type",
                    "parameters": [
                        {
                            "name": "node_type",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "Successful response"}},
                }
            },
            "/nodes/{node_type}/operations/{operation}": {
                "get": {
                    "summary": "Get operation parameters",
                    "description": "Returns parameters for a specific operation",
                    "parameters": [
                        {
                            "name": "node_type",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "operation",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {"200": {"description": "Successful response"}},
                }
            },
            "/execute/{node_type}": {
                "post": {
                    "summary": "Execute node",
                    "description": "Execute a node with the provided parameters",
                    "parameters": [
                        {
                            "name": "node_type",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "description": "Node parameters",
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                    "responses": {"200": {"description": "Successful response"}},
                }
            },
        },
    }

    return jsonify(swagger_doc)


@app.route("/", methods=["GET"])
def index():
    """Return a simple welcome page with links to API docs."""
    return """
    <html>
        <head>
            <title>Node API Server</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
                h1 { color: #333; }
                a { color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .endpoint { background: #f4f4f4; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
                code { background: #e0e0e0; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Node API Server</h1>
            <p>Welcome to the Node API Server. Use the following endpoints to interact with the API:</p>
            
            <div class="endpoint">
                <h3>View API Documentation</h3>
                <p><a href="/api/docs">/api/docs</a></p>
            </div>
            
            <div class="endpoint">
                <h3>List All Nodes</h3>
                <p><a href="/api/nodes">/api/nodes</a></p>
            </div>
            
            <p>For specific node operations, use the following pattern:</p>
            <code>/api/nodes/{node_type}</code><br>
            <code>/api/nodes/{node_type}/operations</code><br>
            <code>/api/nodes/{node_type}/operations/{operation}</code>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5088)
