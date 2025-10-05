# === File: act/nodes/aci_node.py ===

import logging
import json
import asyncio
from typing import Dict, Any, Optional
from aiohttp import web
import uuid
import threading
import queue

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
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

# --- Node Logger ---
logger = logging.getLogger(__name__)

# --- Global server instance ---
_server = None
_server_thread = None
_request_queues = {}
_response_queues = {}

class ACINode(BaseNode):
    node_type = "aci"
    """
    Agent Communication Interface (ACI) Node
    
    Provides HTTP server capabilities for workflows, enabling them to receive
    and respond to HTTP requests. Can be used as a start node to trigger
    workflow execution from external API calls.
    """

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the ACINode."""
        return NodeSchema(
            node_type="aci",
            version="1.0.0",
            description="Agent Communication Interface node for receiving and responding to HTTP requests",
            parameters=[
                NodeParameter(
                    name="mode",
                    type=NodeParameterType.STRING,
                    description="Mode of operation: 'server' to start the server, 'request' to handle a request",
                    required=True,
                    enum=["server", "request", "response"]
                ),
                NodeParameter(
                    name="host",
                    type=NodeParameterType.STRING,
                    description="Host to bind the server to (for server mode)",
                    required=False,
                    default="0.0.0.0"
                ),
                NodeParameter(
                    name="port",
                    type=NodeParameterType.NUMBER,
                    description="Port to bind the server to (for server mode)",
                    required=False,
                    default=8080
                ),
                NodeParameter(
                    name="endpoint",
                    type=NodeParameterType.STRING,
                    description="API endpoint to listen on (for server mode)",
                    required=False,
                    default="/api/agent"
                ),
                NodeParameter(
                    name="allowed_methods",
                    type=NodeParameterType.ARRAY,
                    description="HTTP methods to allow (for server mode)",
                    required=False,
                    default=["GET", "POST", "PUT", "DELETE"]
                ),
                NodeParameter(
                    name="request_id",
                    type=NodeParameterType.STRING,
                    description="ID of the request to handle (for request mode)",
                    required=False,
                    default=None
                ),
                NodeParameter(
                    name="response_data",
                    type=NodeParameterType.OBJECT,
                    description="Data to send back in the response (for response mode)",
                    required=False,
                    default=None
                ),
                NodeParameter(
                    name="response_status",
                    type=NodeParameterType.NUMBER,
                    description="HTTP status code to send (for response mode)",
                    required=False,
                    default=200
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.NUMBER,
                    description="Timeout in seconds for waiting for requests (for request mode)",
                    required=False,
                    default=30
                )
            ],
            outputs={
                "request_id": NodeParameterType.STRING,
                "request_method": NodeParameterType.STRING,
                "request_path": NodeParameterType.STRING,
                "request_query": NodeParameterType.OBJECT,
                "request_headers": NodeParameterType.OBJECT,
                "request_body": NodeParameterType.ANY,
                "response_sent": NodeParameterType.BOOLEAN,
                "server_running": NodeParameterType.BOOLEAN
            },
            tags=["api", "http", "server", "interface", "agent"],
            author="ACT Framework"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the ACI operation with the provided data."""
        node_name = node_data.get('__node_name', 'ACINode')
        logger.debug(f"Executing ACINode: {node_name}")

        try:
            # Extract parameters
            params = node_data.get("params", {})
            mode = params.get("mode")
            
            if not mode:
                raise NodeValidationError("No mode specified. Required parameter 'mode' is missing.")
            
            logger.debug(f"{node_name} - Executing in mode: {mode}")
            
            # Execute the appropriate mode
            if mode == "server":
                return await self._start_server(params, node_name)
            elif mode == "request":
                return await self._handle_request(params, node_name)
            elif mode == "response":
                return await self._send_response(params, node_name)
            else:
                raise NodeValidationError(f"Invalid mode: {mode}")
                
        except Exception as e:
            logger.error(f"Error in {node_name}: {str(e)}", exc_info=True)
            return self.handle_error(e, context=node_name)

    async def _start_server(self, params: Dict[str, Any], node_name: str) -> Dict[str, Any]:
        """Start the HTTP server to listen for requests."""
        global _server, _server_thread
        
        # Get server parameters
        host = params.get("host", "0.0.0.0")
        port = params.get("port", 8080)
        endpoint = params.get("endpoint", "/api/agent")
        allowed_methods = params.get("allowed_methods", ["GET", "POST", "PUT", "DELETE"])
        
        # Check if server is already running
        if _server is not None:
            logger.info(f"{node_name} - Server is already running on {host}:{port}")
            return {
                "status": "success",
                "message": f"Server is already running on {host}:{port}",
                "result": {
                    "server_running": True,
                    "host": host,
                    "port": port,
                    "endpoint": endpoint
                }
            }
        
        # Define HTTP handler
        async def handle_request(request):
            # Generate a unique ID for this request
            request_id = str(uuid.uuid4())
            
            # Extract request data
            method = request.method
            path = request.path
            query = dict(request.query)
            headers = dict(request.headers)
            
            # Get request body if available
            body = None
            if request.content_type == 'application/json':
                try:
                    body = await request.json()
                except:
                    body = None
            elif request.content_type and request.content_type.startswith('multipart/form-data'):
                body = {}
                multipart = await request.multipart()
                while True:
                    field = await multipart.next()
                    if field is None:
                        break
                    
                    value = await field.read()
                    if field.content_type and field.content_type.startswith('text/'):
                        value = value.decode('utf-8')
                    
                    body[field.name] = value
            elif request.content_type and request.content_type.startswith('application/x-www-form-urlencoded'):
                form = await request.post()
                body = {k: v for k, v in form.items()}
            else:
                try:
                    body_text = await request.text()
                    body = body_text
                except:
                    body = None
            
            # Create request data package
            request_data = {
                "request_id": request_id,
                "request_method": method,
                "request_path": path,
                "request_query": query,
                "request_headers": headers,
                "request_body": body,
                "request_time": time.time()
            }
            
            # Create queues for this request if they don't exist
            if request_id not in _request_queues:
                _request_queues[request_id] = queue.Queue()
            if request_id not in _response_queues:
                _response_queues[request_id] = queue.Queue()
            
            # Put request in the queue
            _request_queues[request_id].put(request_data)
            
            # Wait for response
            try:
                response_data = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: _response_queues[request_id].get(timeout=60)
                )
                
                # Clean up queues
                del _request_queues[request_id]
                del _response_queues[request_id]
                
                # Return response
                return web.json_response(
                    data=response_data.get("data", {}),
                    status=response_data.get("status", 200),
                    headers=response_data.get("headers", {})
                )
            except queue.Empty:
                # Timeout waiting for response
                logger.error(f"Timeout waiting for response to request {request_id}")
                return web.json_response(
                    data={"error": "Timeout waiting for response"},
                    status=504  # Gateway Timeout
                )
        
        # Create the aiohttp server
        app = web.Application()
        
        # Register routes for the specified endpoint
        for method in allowed_methods:
            if method == "GET":
                app.router.add_get(endpoint, handle_request)
            elif method == "POST":
                app.router.add_post(endpoint, handle_request)
            elif method == "PUT":
                app.router.add_put(endpoint, handle_request)
            elif method == "DELETE":
                app.router.add_delete(endpoint, handle_request)
            elif method == "PATCH":
                app.router.add_patch(endpoint, handle_request)
        
        # Function to run the server in a separate thread
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            runner = web.AppRunner(app)
            loop.run_until_complete(runner.setup())
            site = web.TCPSite(runner, host, port)
            loop.run_until_complete(site.start())
            logger.info(f"Server started on {host}:{port}")
            loop.run_forever()
        
        # Start the server in a separate thread
        _server_thread = threading.Thread(target=run_server, daemon=True)
        _server_thread.start()
        _server = app
        
        logger.info(f"{node_name} - Started server on {host}:{port} with endpoint {endpoint}")
        
        return {
            "status": "success",
            "message": f"Server started successfully on {host}:{port}",
            "result": {
                "server_running": True,
                "host": host,
                "port": port,
                "endpoint": endpoint
            }
        }

    async def _handle_request(self, params: Dict[str, Any], node_name: str) -> Dict[str, Any]:
        """Wait for and retrieve an incoming request."""
        # Get request parameters
        request_id = params.get("request_id")
        timeout = params.get("timeout", 30)
        
        # If request_id is provided, check for that specific request
        if request_id:
            if request_id not in _request_queues:
                raise NodeExecutionError(f"No request found with ID: {request_id}")
            
            try:
                # Try to get the request non-blocking (it should already be there)
                request_data = _request_queues[request_id].get_nowait()
            except queue.Empty:
                raise NodeExecutionError(f"Request with ID {request_id} was registered but is no longer available")
        else:
            # No specific request ID, so look for any new request
            # Create a list of all request queues
            queue_items = list(_request_queues.items())
            
            if not queue_items:
                # No requests are waiting
                return {
                    "status": "success",
                    "message": "No requests available",
                    "result": {
                        "request_available": False
                    }
                }
            
            # Try each queue until we find a request or run out of queues
            request_data = None
            found_request_id = None
            
            for rid, req_queue in queue_items:
                try:
                    request_data = req_queue.get_nowait()
                    found_request_id = rid
                    break
                except queue.Empty:
                    continue
            
            if not request_data:
                # No requests are available in any queue
                return {
                    "status": "success",
                    "message": "No requests available",
                    "result": {
                        "request_available": False
                    }
                }
            
            request_id = found_request_id
        
        logger.debug(f"{node_name} - Handling request with ID: {request_id}")
        
        return {
            "status": "success",
            "message": f"Retrieved request with ID: {request_id}",
            "result": {
                "request_available": True,
                "request_id": request_id,
                "request_method": request_data.get("request_method"),
                "request_path": request_data.get("request_path"),
                "request_query": request_data.get("request_query"),
                "request_headers": request_data.get("request_headers"),
                "request_body": request_data.get("request_body")
            }
        }

    async def _send_response(self, params: Dict[str, Any], node_name: str) -> Dict[str, Any]:
        """Send a response to a previously handled request."""
        # Get response parameters
        request_id = params.get("request_id")
        response_data = params.get("response_data", {})
        response_status = params.get("response_status", 200)
        
        if not request_id:
            raise NodeValidationError("No request ID specified. Required parameter 'request_id' is missing.")
        
        if request_id not in _response_queues:
            raise NodeExecutionError(f"No response queue found for request ID: {request_id}")
        
        # Prepare response package
        response_package = {
            "data": response_data,
            "status": response_status,
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
        # Put response in the queue
        _response_queues[request_id].put(response_package)
        
        logger.debug(f"{node_name} - Sent response for request with ID: {request_id}")
        
        return {
            "status": "success",
            "message": f"Response sent for request with ID: {request_id}",
            "result": {
                "response_sent": True,
                "request_id": request_id,
                "response_status": response_status
            }
        }

# For standalone testing
if __name__ == "__main__":
    import time
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    )
    
    async def test_aci():
        print("\n--- Testing ACINode ---")
        node = ACINode()
        
        # Start the server
        print("\n1. Starting server...")
        server_result = await node.execute({
            "__node_name": "TestACI",
            "params": {
                "mode": "server",
                "host": "localhost",
                "port": 8080,
                "endpoint": "/api/test"
            }
        })
        print(f"Server Result: {server_result}")
        
        # Give the server time to start
        print("\nServer started. Please send a request to http://localhost:8080/api/test")
        print("Waiting for incoming requests...")
        
        # Continuously poll for requests
        while True:
            # Handle any incoming request
            request_result = await node.execute({
                "__node_name": "TestACI",
                "params": {
                    "mode": "request",
                    "timeout": 1  # Short timeout for polling
                }
            })
            
            if request_result.get("result", {}).get("request_available", False):
                # Got a request, process it
                print(f"\nRequest received: {request_result}")
                
                # Send a response
                request_id = request_result.get("result", {}).get("request_id")
                response_result = await node.execute({
                    "__node_name": "TestACI",
                    "params": {
                        "mode": "response",
                        "request_id": request_id,
                        "response_data": {
                            "message": "Hello from ACI Node!",
                            "timestamp": time.time(),
                            "your_request": request_result.get("result", {}).get("request_body")
                        },
                        "response_status": 200
                    }
                })
                print(f"Response sent: {response_result}")
                break
            
            # Wait a bit before polling again
            await asyncio.sleep(0.5)
    
    asyncio.run(test_aci())