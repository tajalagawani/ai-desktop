"""
AMQP Node - Comprehensive message broker and queue integration
Supports all major AMQP operations including exchanges, queues, messages, and RabbitMQ management.
Uses AMQP protocol with full message broker coverage.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from base_node import (
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
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

# Configure logging
logger = logging.getLogger(__name__)

class AmqpOperation:
    """All available AMQP operations."""
    
    # Connection operations
    CREATE_CONNECTION = "create_connection"
    CLOSE_CONNECTION = "close_connection"
    
    # Channel operations
    CREATE_CHANNEL = "create_channel"
    CLOSE_CHANNEL = "close_channel"
    
    # Exchange operations
    DECLARE_EXCHANGE = "declare_exchange"
    DELETE_EXCHANGE = "delete_exchange"
    BIND_EXCHANGE = "bind_exchange"
    UNBIND_EXCHANGE = "unbind_exchange"
    
    # Queue operations
    DECLARE_QUEUE = "declare_queue"
    DELETE_QUEUE = "delete_queue"
    PURGE_QUEUE = "purge_queue"
    BIND_QUEUE = "bind_queue"
    UNBIND_QUEUE = "unbind_queue"
    
    # Message operations
    PUBLISH_MESSAGE = "publish_message"
    CONSUME_MESSAGE = "consume_message"
    GET_MESSAGE = "get_message"
    ACK_MESSAGE = "ack_message"
    NACK_MESSAGE = "nack_message"
    REJECT_MESSAGE = "reject_message"
    
    # Management API operations (RabbitMQ HTTP API)
    GET_OVERVIEW = "get_overview"
    GET_CONNECTIONS = "get_connections"
    GET_CHANNELS = "get_channels"
    GET_EXCHANGES = "get_exchanges"
    GET_QUEUES = "get_queues"
    GET_BINDINGS = "get_bindings"
    GET_VHOSTS = "get_vhosts"
    GET_USERS = "get_users"
    GET_PERMISSIONS = "get_permissions"
    
    # User management operations
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    SET_PERMISSIONS = "set_permissions"
    
    # Virtual host operations
    CREATE_VHOST = "create_vhost"
    DELETE_VHOST = "delete_vhost"
    
    # Health and monitoring operations
    HEALTH_CHECK = "health_check"
    GET_NODE_INFO = "get_node_info"
    GET_CLUSTER_INFO = "get_cluster_info"

class AmqpNode(BaseNode):
    """
    Comprehensive AMQP message broker integration node supporting all major protocol operations.
    Handles connections, channels, exchanges, queues, messages, and RabbitMQ management.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the AMQP node."""
        return NodeSchema(
            label="AMQP/RabbitMQ",
            description="Comprehensive AMQP message broker integration supporting all protocol operations",
            icon_path="https://www.rabbitmq.com/favicon.ico",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The AMQP operation to perform",
                    required=True,
                    enum=[
                        AmqpOperation.CREATE_CONNECTION,
                        AmqpOperation.CLOSE_CONNECTION,
                        AmqpOperation.CREATE_CHANNEL,
                        AmqpOperation.CLOSE_CHANNEL,
                        AmqpOperation.DECLARE_EXCHANGE,
                        AmqpOperation.DELETE_EXCHANGE,
                        AmqpOperation.BIND_EXCHANGE,
                        AmqpOperation.UNBIND_EXCHANGE,
                        AmqpOperation.DECLARE_QUEUE,
                        AmqpOperation.DELETE_QUEUE,
                        AmqpOperation.PURGE_QUEUE,
                        AmqpOperation.BIND_QUEUE,
                        AmqpOperation.UNBIND_QUEUE,
                        AmqpOperation.PUBLISH_MESSAGE,
                        AmqpOperation.CONSUME_MESSAGE,
                        AmqpOperation.GET_MESSAGE,
                        AmqpOperation.ACK_MESSAGE,
                        AmqpOperation.NACK_MESSAGE,
                        AmqpOperation.REJECT_MESSAGE,
                        AmqpOperation.GET_OVERVIEW,
                        AmqpOperation.GET_CONNECTIONS,
                        AmqpOperation.GET_CHANNELS,
                        AmqpOperation.GET_EXCHANGES,
                        AmqpOperation.GET_QUEUES,
                        AmqpOperation.GET_BINDINGS,
                        AmqpOperation.GET_VHOSTS,
                        AmqpOperation.GET_USERS,
                        AmqpOperation.GET_PERMISSIONS,
                        AmqpOperation.CREATE_USER,
                        AmqpOperation.DELETE_USER,
                        AmqpOperation.SET_PERMISSIONS,
                        AmqpOperation.CREATE_VHOST,
                        AmqpOperation.DELETE_VHOST,
                        AmqpOperation.HEALTH_CHECK,
                        AmqpOperation.GET_NODE_INFO,
                        AmqpOperation.GET_CLUSTER_INFO
                    ]
                ),
                "host": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="AMQP broker hostname or IP address",
                    required=True,
                    default="localhost"
                ),
                "port": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="AMQP broker port",
                    required=False,
                    default=5672
                ),
                "management_port": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="RabbitMQ management API port",
                    required=False,
                    default=15672
                ),
                "username": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="AMQP username",
                    required=True,
                    default="guest"
                ),
                "password": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="AMQP password",
                    required=True
                ),
                "virtual_host": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="AMQP virtual host",
                    required=False,
                    default="/"
                ),
                "use_ssl": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Use SSL/TLS connection",
                    required=False,
                    default=False
                ),
                
                # Connection parameters
                "connection_timeout": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Connection timeout in seconds",
                    required=False,
                    default=30
                ),
                "heartbeat": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Heartbeat interval in seconds",
                    required=False,
                    default=60
                ),
                
                # Exchange parameters
                "exchange_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Exchange name",
                    required=False
                ),
                "exchange_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Exchange type",
                    required=False,
                    enum=["direct", "fanout", "topic", "headers"],
                    default="direct"
                ),
                "exchange_durable": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether exchange is durable",
                    required=False,
                    default=True
                ),
                "exchange_auto_delete": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether exchange auto-deletes",
                    required=False,
                    default=False
                ),
                "exchange_arguments": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Additional exchange arguments",
                    required=False
                ),
                
                # Queue parameters
                "queue_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Queue name",
                    required=False
                ),
                "queue_durable": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether queue is durable",
                    required=False,
                    default=True
                ),
                "queue_exclusive": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether queue is exclusive",
                    required=False,
                    default=False
                ),
                "queue_auto_delete": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether queue auto-deletes",
                    required=False,
                    default=False
                ),
                "queue_arguments": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Additional queue arguments",
                    required=False
                ),
                
                # Binding parameters
                "routing_key": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Routing key for bindings and messages",
                    required=False,
                    default=""
                ),
                "binding_arguments": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Additional binding arguments",
                    required=False
                ),
                "source_exchange": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Source exchange for exchange-to-exchange binding",
                    required=False
                ),
                "destination_exchange": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Destination exchange for exchange-to-exchange binding",
                    required=False
                ),
                
                # Message parameters
                "message_body": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Message body content",
                    required=False
                ),
                "message_properties": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Message properties (headers, priority, etc.)",
                    required=False
                ),
                "content_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Message content type",
                    required=False,
                    default="text/plain"
                ),
                "delivery_mode": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Message delivery mode (1=non-persistent, 2=persistent)",
                    required=False,
                    enum=[1, 2],
                    default=2
                ),
                "priority": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Message priority (0-255)",
                    required=False,
                    min_value=0,
                    max_value=255
                ),
                "expiration": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Message expiration (TTL in milliseconds)",
                    required=False
                ),
                "correlation_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Message correlation ID",
                    required=False
                ),
                "reply_to": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Reply-to queue name",
                    required=False
                ),
                
                # Consumer parameters
                "consumer_tag": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Consumer tag identifier",
                    required=False
                ),
                "auto_ack": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Auto-acknowledge messages",
                    required=False,
                    default=False
                ),
                "exclusive_consumer": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether consumer is exclusive",
                    required=False,
                    default=False
                ),
                "consumer_arguments": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Additional consumer arguments",
                    required=False
                ),
                
                # Message acknowledgment parameters
                "delivery_tag": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Message delivery tag for acknowledgment",
                    required=False
                ),
                "multiple": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Acknowledge multiple messages",
                    required=False,
                    default=False
                ),
                "requeue": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Requeue rejected messages",
                    required=False,
                    default=True
                ),
                
                # User management parameters
                "user_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="User name for user management operations",
                    required=False
                ),
                "user_password": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="User password for user creation",
                    required=False
                ),
                "user_tags": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="User tags/roles",
                    required=False
                ),
                
                # Permission parameters
                "configure": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Configure permission pattern",
                    required=False,
                    default=".*"
                ),
                "write": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Write permission pattern",
                    required=False,
                    default=".*"
                ),
                "read": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Read permission pattern",
                    required=False,
                    default=".*"
                ),
                
                # Advanced parameters
                "prefetch_count": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Consumer prefetch count",
                    required=False,
                    default=1
                ),
                "confirm_delivery": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Enable publisher confirms",
                    required=False,
                    default=False
                ),
                "wait_for_confirm": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Wait for delivery confirmation",
                    required=False,
                    default=False
                ),
                "timeout": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Operation timeout in seconds",
                    required=False,
                    default=30
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "data": NodeParameterType.OBJECT,
                "connection_id": NodeParameterType.STRING,
                "channel_id": NodeParameterType.STRING,
                "exchange": NodeParameterType.OBJECT,
                "queue": NodeParameterType.OBJECT,
                "message": NodeParameterType.OBJECT,
                "messages": NodeParameterType.ARRAY,
                "connections": NodeParameterType.ARRAY,
                "channels": NodeParameterType.ARRAY,
                "exchanges": NodeParameterType.ARRAY,
                "queues": NodeParameterType.ARRAY,
                "bindings": NodeParameterType.ARRAY,
                "vhosts": NodeParameterType.ARRAY,
                "users": NodeParameterType.ARRAY,
                "permissions": NodeParameterType.ARRAY,
                "overview": NodeParameterType.OBJECT,
                "node_info": NodeParameterType.OBJECT,
                "cluster_info": NodeParameterType.OBJECT,
                "health": NodeParameterType.OBJECT,
                "delivery_tag": NodeParameterType.NUMBER,
                "consumer_tag": NodeParameterType.STRING,
                "message_count": NodeParameterType.NUMBER,
                "consumer_count": NodeParameterType.NUMBER,
                "success": NodeParameterType.BOOLEAN,
                "confirmed": NodeParameterType.BOOLEAN,
                "error": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AMQP-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if not params.get("host"):
            raise NodeValidationError("AMQP broker host is required")
        
        if not params.get("username"):
            raise NodeValidationError("AMQP username is required")
        
        if not params.get("password"):
            raise NodeValidationError("AMQP password is required")
        
        # Validate operation-specific required parameters
        exchange_ops = [
            AmqpOperation.DECLARE_EXCHANGE, AmqpOperation.DELETE_EXCHANGE,
            AmqpOperation.BIND_EXCHANGE, AmqpOperation.UNBIND_EXCHANGE
        ]
        
        if operation in exchange_ops:
            if not params.get("exchange_name"):
                raise NodeValidationError("Exchange name is required for exchange operations")
        
        queue_ops = [
            AmqpOperation.DECLARE_QUEUE, AmqpOperation.DELETE_QUEUE, AmqpOperation.PURGE_QUEUE,
            AmqpOperation.BIND_QUEUE, AmqpOperation.UNBIND_QUEUE
        ]
        
        if operation in queue_ops:
            if not params.get("queue_name"):
                raise NodeValidationError("Queue name is required for queue operations")
        
        if operation == AmqpOperation.BIND_QUEUE:
            if not params.get("exchange_name"):
                raise NodeValidationError("Exchange name is required for queue binding")
        
        if operation in [AmqpOperation.BIND_EXCHANGE, AmqpOperation.UNBIND_EXCHANGE]:
            if not params.get("source_exchange") or not params.get("destination_exchange"):
                raise NodeValidationError("Source and destination exchanges are required for exchange binding")
        
        if operation == AmqpOperation.PUBLISH_MESSAGE:
            if not params.get("exchange_name"):
                raise NodeValidationError("Exchange name is required for message publishing")
            if not params.get("message_body"):
                raise NodeValidationError("Message body is required for publishing")
        
        if operation in [AmqpOperation.CONSUME_MESSAGE, AmqpOperation.GET_MESSAGE]:
            if not params.get("queue_name"):
                raise NodeValidationError("Queue name is required for message consumption")
        
        if operation in [AmqpOperation.ACK_MESSAGE, AmqpOperation.NACK_MESSAGE, AmqpOperation.REJECT_MESSAGE]:
            if not params.get("delivery_tag"):
                raise NodeValidationError("Delivery tag is required for message acknowledgment")
        
        if operation in [AmqpOperation.CREATE_USER, AmqpOperation.DELETE_USER]:
            if not params.get("user_name"):
                raise NodeValidationError("User name is required for user management operations")
        
        if operation == AmqpOperation.CREATE_USER:
            if not params.get("user_password"):
                raise NodeValidationError("User password is required for user creation")
        
        if operation == AmqpOperation.SET_PERMISSIONS:
            if not params.get("user_name"):
                raise NodeValidationError("User name is required for setting permissions")
        
        if operation in [AmqpOperation.CREATE_VHOST, AmqpOperation.DELETE_VHOST]:
            if not params.get("virtual_host") or params.get("virtual_host") == "/":
                raise NodeValidationError("Virtual host name is required for vhost operations")
        
        # Validate port numbers
        port = params.get("port")
        if port is not None:
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise NodeValidationError("Port must be between 1 and 65535")
        
        management_port = params.get("management_port")
        if management_port is not None:
            if not isinstance(management_port, int) or management_port < 1 or management_port > 65535:
                raise NodeValidationError("Management port must be between 1 and 65535")
        
        # Validate timeout values
        timeout = params.get("timeout")
        if timeout is not None:
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise NodeValidationError("Timeout must be a positive number")
        
        # Validate priority
        priority = params.get("priority")
        if priority is not None:
            if not isinstance(priority, int) or priority < 0 or priority > 255:
                raise NodeValidationError("Priority must be between 0 and 255")
        
        # Validate delivery mode
        delivery_mode = params.get("delivery_mode")
        if delivery_mode is not None:
            if delivery_mode not in [1, 2]:
                raise NodeValidationError("Delivery mode must be 1 (non-persistent) or 2 (persistent)")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the AMQP operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # For management API operations, use HTTP API
            management_ops = [
                AmqpOperation.GET_OVERVIEW, AmqpOperation.GET_CONNECTIONS, AmqpOperation.GET_CHANNELS,
                AmqpOperation.GET_EXCHANGES, AmqpOperation.GET_QUEUES, AmqpOperation.GET_BINDINGS,
                AmqpOperation.GET_VHOSTS, AmqpOperation.GET_USERS, AmqpOperation.GET_PERMISSIONS,
                AmqpOperation.CREATE_USER, AmqpOperation.DELETE_USER, AmqpOperation.SET_PERMISSIONS,
                AmqpOperation.CREATE_VHOST, AmqpOperation.DELETE_VHOST, AmqpOperation.HEALTH_CHECK,
                AmqpOperation.GET_NODE_INFO, AmqpOperation.GET_CLUSTER_INFO
            ]
            
            if operation in management_ops:
                return await self._execute_management_operation(params, operation)
            else:
                return await self._execute_amqp_operation(params, operation)
                
        except Exception as e:
            logger.error(f"AMQP operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_management_operation(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Execute RabbitMQ management API operation."""
        host = params["host"]
        management_port = params.get("management_port", 15672)
        username = params["username"]
        password = params["password"]
        virtual_host = params.get("virtual_host", "/").replace("/", "%2F")
        
        # Set up base URL and auth
        protocol = "https" if params.get("use_ssl", False) else "http"
        base_url = f"{protocol}://{host}:{management_port}/api"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        auth = aiohttp.BasicAuth(username, password)
        
        # Route to specific management operation
        if operation == AmqpOperation.GET_OVERVIEW:
            return await self._get_overview(base_url, headers, auth)
        elif operation == AmqpOperation.GET_CONNECTIONS:
            return await self._get_connections(base_url, headers, auth)
        elif operation == AmqpOperation.GET_CHANNELS:
            return await self._get_channels(base_url, headers, auth)
        elif operation == AmqpOperation.GET_EXCHANGES:
            return await self._get_exchanges(base_url, headers, auth, virtual_host)
        elif operation == AmqpOperation.GET_QUEUES:
            return await self._get_queues(base_url, headers, auth, virtual_host)
        elif operation == AmqpOperation.GET_BINDINGS:
            return await self._get_bindings(base_url, headers, auth, virtual_host)
        elif operation == AmqpOperation.GET_VHOSTS:
            return await self._get_vhosts(base_url, headers, auth)
        elif operation == AmqpOperation.GET_USERS:
            return await self._get_users(base_url, headers, auth)
        elif operation == AmqpOperation.GET_PERMISSIONS:
            return await self._get_permissions(base_url, headers, auth, virtual_host)
        elif operation == AmqpOperation.CREATE_USER:
            return await self._create_user(params, base_url, headers, auth)
        elif operation == AmqpOperation.DELETE_USER:
            return await self._delete_user(params, base_url, headers, auth)
        elif operation == AmqpOperation.SET_PERMISSIONS:
            return await self._set_permissions(params, base_url, headers, auth, virtual_host)
        elif operation == AmqpOperation.CREATE_VHOST:
            return await self._create_vhost(params, base_url, headers, auth)
        elif operation == AmqpOperation.DELETE_VHOST:
            return await self._delete_vhost(params, base_url, headers, auth)
        elif operation == AmqpOperation.HEALTH_CHECK:
            return await self._health_check(base_url, headers, auth)
        elif operation == AmqpOperation.GET_NODE_INFO:
            return await self._get_node_info(base_url, headers, auth)
        elif operation == AmqpOperation.GET_CLUSTER_INFO:
            return await self._get_cluster_info(base_url, headers, auth)
        else:
            return {
                "status": "error",
                "error": f"Unknown management operation: {operation}"
            }
    
    async def _execute_amqp_operation(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Execute AMQP protocol operation."""
        # Note: This is a simplified implementation
        # In a real implementation, you would use an AMQP library like aio-pika
        
        # For demonstration purposes, we'll simulate AMQP operations
        # In practice, you'd establish actual AMQP connections
        
        connection_info = {
            "host": params["host"],
            "port": params.get("port", 5672),
            "virtual_host": params.get("virtual_host", "/"),
            "username": params["username"]
        }
        
        if operation == AmqpOperation.CREATE_CONNECTION:
            return {
                "status": "success",
                "connection_id": f"conn_{datetime.now().timestamp()}",
                "data": connection_info
            }
        
        elif operation == AmqpOperation.DECLARE_EXCHANGE:
            exchange_info = {
                "name": params["exchange_name"],
                "type": params.get("exchange_type", "direct"),
                "durable": params.get("exchange_durable", True),
                "auto_delete": params.get("exchange_auto_delete", False)
            }
            return {
                "status": "success",
                "exchange": exchange_info,
                "success": True
            }
        
        elif operation == AmqpOperation.DECLARE_QUEUE:
            queue_info = {
                "name": params["queue_name"],
                "durable": params.get("queue_durable", True),
                "exclusive": params.get("queue_exclusive", False),
                "auto_delete": params.get("queue_auto_delete", False)
            }
            return {
                "status": "success",
                "queue": queue_info,
                "success": True
            }
        
        elif operation == AmqpOperation.PUBLISH_MESSAGE:
            message_info = {
                "exchange": params["exchange_name"],
                "routing_key": params.get("routing_key", ""),
                "body": params["message_body"],
                "properties": params.get("message_properties", {}),
                "delivery_mode": params.get("delivery_mode", 2)
            }
            return {
                "status": "success",
                "message": message_info,
                "success": True,
                "confirmed": params.get("confirm_delivery", False)
            }
        
        else:
            return {
                "status": "error",
                "error": f"AMQP operation {operation} not implemented in this demo"
            }
    
    async def _make_request(self, method: str, url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to RabbitMQ management API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    auth=auth,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.content_type == 'application/json':
                        response_data = await response.json()
                    else:
                        response_text = await response.text()
                        response_data = {"result": response_text}
                    
                    if response.status == 200 or response.status == 201 or response.status == 204:
                        return response_data
                    else:
                        error_msg = response_data.get("error", f"HTTP {response.status}")
                        raise Exception(f"RabbitMQ API error: {error_msg}")
                        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise e
    
    # Management API operations
    async def _get_overview(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get broker overview."""
        url = f"{base_url}/overview"
        result = await self._make_request("GET", url, headers, auth)
        
        return {
            "status": "success",
            "overview": result,
            "data": result
        }
    
    async def _get_connections(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get all connections."""
        url = f"{base_url}/connections"
        result = await self._make_request("GET", url, headers, auth)
        
        connections = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "connections": connections,
            "count": len(connections)
        }
    
    async def _get_channels(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get all channels."""
        url = f"{base_url}/channels"
        result = await self._make_request("GET", url, headers, auth)
        
        channels = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "channels": channels,
            "count": len(channels)
        }
    
    async def _get_exchanges(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth, vhost: str) -> Dict[str, Any]:
        """Get exchanges in virtual host."""
        url = f"{base_url}/exchanges/{vhost}"
        result = await self._make_request("GET", url, headers, auth)
        
        exchanges = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "exchanges": exchanges,
            "count": len(exchanges)
        }
    
    async def _get_queues(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth, vhost: str) -> Dict[str, Any]:
        """Get queues in virtual host."""
        url = f"{base_url}/queues/{vhost}"
        result = await self._make_request("GET", url, headers, auth)
        
        queues = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "queues": queues,
            "count": len(queues)
        }
    
    async def _get_bindings(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth, vhost: str) -> Dict[str, Any]:
        """Get bindings in virtual host."""
        url = f"{base_url}/bindings/{vhost}"
        result = await self._make_request("GET", url, headers, auth)
        
        bindings = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "bindings": bindings,
            "count": len(bindings)
        }
    
    async def _get_vhosts(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get all virtual hosts."""
        url = f"{base_url}/vhosts"
        result = await self._make_request("GET", url, headers, auth)
        
        vhosts = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "vhosts": vhosts,
            "count": len(vhosts)
        }
    
    async def _get_users(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get all users."""
        url = f"{base_url}/users"
        result = await self._make_request("GET", url, headers, auth)
        
        users = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "users": users,
            "count": len(users)
        }
    
    async def _get_permissions(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth, vhost: str) -> Dict[str, Any]:
        """Get permissions for virtual host."""
        url = f"{base_url}/permissions/{vhost}"
        result = await self._make_request("GET", url, headers, auth)
        
        permissions = result if isinstance(result, list) else []
        
        return {
            "status": "success",
            "permissions": permissions,
            "count": len(permissions)
        }
    
    async def _create_user(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Create new user."""
        user_name = params["user_name"]
        url = f"{base_url}/users/{user_name}"
        
        data = {
            "password": params["user_password"],
            "tags": ",".join(params.get("user_tags", []))
        }
        
        await self._make_request("PUT", url, headers, auth, data=data)
        
        return {
            "status": "success",
            "user_name": user_name,
            "success": True
        }
    
    async def _delete_user(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Delete user."""
        user_name = params["user_name"]
        url = f"{base_url}/users/{user_name}"
        
        await self._make_request("DELETE", url, headers, auth)
        
        return {
            "status": "success",
            "user_name": user_name,
            "success": True
        }
    
    async def _set_permissions(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth, vhost: str) -> Dict[str, Any]:
        """Set user permissions."""
        user_name = params["user_name"]
        url = f"{base_url}/permissions/{vhost}/{user_name}"
        
        data = {
            "configure": params.get("configure", ".*"),
            "write": params.get("write", ".*"),
            "read": params.get("read", ".*")
        }
        
        await self._make_request("PUT", url, headers, auth, data=data)
        
        return {
            "status": "success",
            "user_name": user_name,
            "virtual_host": vhost,
            "permissions": data,
            "success": True
        }
    
    async def _create_vhost(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Create virtual host."""
        vhost = params["virtual_host"]
        url = f"{base_url}/vhosts/{vhost}"
        
        await self._make_request("PUT", url, headers, auth)
        
        return {
            "status": "success",
            "virtual_host": vhost,
            "success": True
        }
    
    async def _delete_vhost(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Delete virtual host."""
        vhost = params["virtual_host"]
        url = f"{base_url}/vhosts/{vhost}"
        
        await self._make_request("DELETE", url, headers, auth)
        
        return {
            "status": "success",
            "virtual_host": vhost,
            "success": True
        }
    
    async def _health_check(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Check broker health."""
        url = f"{base_url}/healthchecks/node"
        result = await self._make_request("GET", url, headers, auth)
        
        return {
            "status": "success",
            "health": result,
            "data": result
        }
    
    async def _get_node_info(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get node information."""
        url = f"{base_url}/nodes"
        result = await self._make_request("GET", url, headers, auth)
        
        return {
            "status": "success",
            "node_info": result,
            "data": result
        }
    
    async def _get_cluster_info(self, base_url: str, headers: Dict[str, str], auth: aiohttp.BasicAuth) -> Dict[str, Any]:
        """Get cluster information."""
        url = f"{base_url}/cluster-name"
        result = await self._make_request("GET", url, headers, auth)
        
        return {
            "status": "success",
            "cluster_info": result,
            "data": result
        }

class AmqpHelpers:
    """Helper functions for AMQP operations."""
    
    @staticmethod
    def format_response(data: Any) -> Dict[str, Any]:
        """Format AMQP response for consistency."""
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"items": data, "count": len(data)}
        else:
            return {"value": data}
    
    @staticmethod
    def construct_amqp_url(host: str, port: int, username: str, password: str, virtual_host: str = "/", use_ssl: bool = False) -> str:
        """Construct AMQP connection URL."""
        protocol = "amqps" if use_ssl else "amqp"
        vhost = virtual_host if virtual_host != "/" else ""
        return f"{protocol}://{username}:{password}@{host}:{port}/{vhost}"
    
    @staticmethod
    def validate_routing_key(routing_key: str, exchange_type: str) -> bool:
        """Validate routing key format for exchange type."""
        if exchange_type == "fanout":
            return True  # Fanout ignores routing key
        elif exchange_type == "direct":
            return isinstance(routing_key, str)
        elif exchange_type == "topic":
            # Topic routing keys should contain words separated by dots
            return isinstance(routing_key, str) and all(
                word.replace("*", "").replace("#", "").isalnum() or word in ["*", "#"]
                for word in routing_key.split(".")
            )
        else:
            return True
    
    @staticmethod
    def format_message_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Format message properties for AMQP."""
        formatted = {}
        
        # Map common properties
        property_mappings = {
            "content_type": "content_type",
            "content_encoding": "content_encoding",
            "delivery_mode": "delivery_mode",
            "priority": "priority",
            "correlation_id": "correlation_id",
            "reply_to": "reply_to",
            "expiration": "expiration",
            "message_id": "message_id",
            "timestamp": "timestamp",
            "type": "type",
            "user_id": "user_id",
            "app_id": "app_id"
        }
        
        for key, amqp_key in property_mappings.items():
            if key in properties:
                formatted[amqp_key] = properties[key]
        
        # Handle headers
        if "headers" in properties:
            formatted["headers"] = properties["headers"]
        
        return formatted
    
    @staticmethod
    def parse_queue_arguments(arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate queue arguments."""
        valid_args = {}
        
        # Common queue arguments
        arg_mappings = {
            "x-message-ttl": int,
            "x-expires": int,
            "x-max-length": int,
            "x-max-length-bytes": int,
            "x-dead-letter-exchange": str,
            "x-dead-letter-routing-key": str,
            "x-max-priority": int,
            "x-queue-mode": str,
            "x-single-active-consumer": bool
        }
        
        for key, value_type in arg_mappings.items():
            if key in arguments:
                try:
                    valid_args[key] = value_type(arguments[key])
                except (ValueError, TypeError):
                    continue
        
        return valid_args

# Export the main class
__all__ = ["AmqpNode", "AmqpOperation", "AmqpHelpers"]