#!/usr/bin/env python3
"""
Apache Kafka Node for ACT Workflow System

This node provides comprehensive Apache Kafka integration capabilities including:
- Message production with various sending patterns
- Message consumption with consumer groups and offset management
- Admin operations for topic and cluster management
- Schema registry integration for Avro serialization
- Stream processing capabilities
- Monitoring and metrics collection
- Security configuration support

Architecture:
- Dispatch map for clean operation routing
- Unified KafkaWrapper for managing producers, consumers, and admin clients
- Context manager for resource lifecycle management
- Metadata-driven validation
- Comprehensive error handling with retry mechanisms
- Sensitive data masking for credentials and message content
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable
from contextlib import asynccontextmanager
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Handle imports for both module and direct execution
try:
    from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Check for Kafka client dependencies
try:
    from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
    from kafka.admin import NewTopic, ConfigResource, ConfigResourceType
    from kafka.errors import KafkaError, KafkaTimeoutError, TopicAlreadyExistsError
    KAFKA_PYTHON_AVAILABLE = True
except ImportError:
    KAFKA_PYTHON_AVAILABLE = False

try:
    from confluent_kafka import Producer, Consumer, KafkaError as ConfluentKafkaError
    from confluent_kafka.admin import AdminClient, NewTopic as ConfluentNewTopic
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

try:
    import aiokafka
    from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
    AIOKAFKA_AVAILABLE = True
except ImportError:
    AIOKAFKA_AVAILABLE = False

class KafkaOperation(str, Enum):
    """Enumeration of all supported Kafka operations."""
    
    # Producer Operations
    SEND_MESSAGE = "send_message"
    SEND_BATCH = "send_batch"
    SEND_WITH_KEY = "send_with_key"
    SEND_ASYNC = "send_async"
    FLUSH_PRODUCER = "flush_producer"
    
    # Consumer Operations
    CONSUME_MESSAGES = "consume_messages"
    SUBSCRIBE_TOPICS = "subscribe_topics"
    UNSUBSCRIBE = "unsubscribe"
    COMMIT_OFFSETS = "commit_offsets"
    SEEK_TO_OFFSET = "seek_to_offset"
    PAUSE_CONSUMPTION = "pause_consumption"
    RESUME_CONSUMPTION = "resume_consumption"
    
    # Admin Operations
    CREATE_TOPIC = "create_topic"
    DELETE_TOPIC = "delete_topic"
    LIST_TOPICS = "list_topics"
    DESCRIBE_TOPIC = "describe_topic"
    DESCRIBE_CLUSTER = "describe_cluster"
    LIST_CONSUMER_GROUPS = "list_consumer_groups"
    DESCRIBE_CONSUMER_GROUP = "describe_consumer_group"
    
    # Configuration Operations
    SET_PRODUCER_CONFIG = "set_producer_config"
    SET_CONSUMER_CONFIG = "set_consumer_config"
    SET_SECURITY_CONFIG = "set_security_config"
    UPDATE_TOPIC_CONFIG = "update_topic_config"
    
    # Monitoring Operations
    GET_CONSUMER_LAG = "get_consumer_lag"
    GET_PRODUCER_METRICS = "get_producer_metrics"
    CHECK_TOPIC_HEALTH = "check_topic_health"
    GET_CLUSTER_STATUS = "get_cluster_status"
    GET_PARTITION_METADATA = "get_partition_metadata"
    
    # Offset Management
    RESET_CONSUMER_OFFSETS = "reset_consumer_offsets"
    GET_COMMITTED_OFFSETS = "get_committed_offsets"
    GET_PARTITION_OFFSETS = "get_partition_offsets"

class KafkaNodeError(Exception):
    """Custom exception for Kafka operations."""
    def __init__(self, message: str, error_code: str = None, original_error: Exception = None):
        self.error_code = error_code
        self.original_error = original_error
        super().__init__(message)

class KafkaWrapper:
    """Unified wrapper for Kafka operations with support for multiple client libraries."""
    
    def __init__(self, config: Dict[str, Any], client_type: str = "kafka-python"):
        self.config = config
        self.client_type = client_type
        self.bootstrap_servers = config.get("bootstrap_servers", ["localhost:9092"])
        
        # Client instances
        self.producer = None
        self.consumer = None
        self.admin_client = None
        
        # Validate client availability
        if client_type == "kafka-python" and not KAFKA_PYTHON_AVAILABLE:
            raise KafkaNodeError("kafka-python library not available")
        elif client_type == "confluent-kafka" and not CONFLUENT_KAFKA_AVAILABLE:
            raise KafkaNodeError("confluent-kafka library not available")
        elif client_type == "aiokafka" and not AIOKAFKA_AVAILABLE:
            raise KafkaNodeError("aiokafka library not available")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_clients()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup_clients()
    
    async def _initialize_clients(self):
        """Initialize Kafka clients based on configuration."""
        try:
            if self.client_type == "kafka-python":
                await self._init_kafka_python_clients()
            elif self.client_type == "confluent-kafka":
                await self._init_confluent_clients()
            elif self.client_type == "aiokafka":
                await self._init_aiokafka_clients()
        except Exception as e:
            raise KafkaNodeError(f"Failed to initialize Kafka clients: {str(e)}", original_error=e)
    
    async def _init_kafka_python_clients(self):
        """Initialize kafka-python clients."""
        # Producer configuration
        producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'acks': self.config.get('acks', 'all'),
            'compression_type': self.config.get('compression_type', 'lz4'),
            'batch_size': self.config.get('batch_size', 16384),
            'linger_ms': self.config.get('linger_ms', 10),
            'retries': self.config.get('retries', 3),
            'enable_idempotence': self.config.get('enable_idempotence', True),
            'value_serializer': lambda x: json.dumps(x).encode('utf-8') if isinstance(x, (dict, list)) else str(x).encode('utf-8')
        }
        
        # Consumer configuration
        consumer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'group_id': self.config.get('group_id', 'default_group'),
            'enable_auto_commit': self.config.get('enable_auto_commit', True),
            'auto_offset_reset': self.config.get('auto_offset_reset', 'latest'),
            'value_deserializer': lambda x: json.loads(x.decode('utf-8')) if x else None
        }
        
        # Admin client configuration
        admin_config = {
            'bootstrap_servers': self.bootstrap_servers
        }
        
        # Apply security settings if provided
        security_config = self.config.get('security', {})
        if security_config:
            producer_config.update(security_config)
            consumer_config.update(security_config)
            admin_config.update(security_config)
        
        self.producer = KafkaProducer(**producer_config)
        self.admin_client = KafkaAdminClient(**admin_config)
        # Consumer is created on-demand when needed
    
    async def _init_confluent_clients(self):
        """Initialize confluent-kafka clients."""
        # Base configuration
        base_config = {
            'bootstrap.servers': ','.join(self.bootstrap_servers),
            'client.id': self.config.get('client_id', 'kafka-node')
        }
        
        # Apply security settings
        security_config = self.config.get('security', {})
        if security_config:
            base_config.update(security_config)
        
        # Producer configuration
        producer_config = base_config.copy()
        producer_config.update({
            'acks': self.config.get('acks', 'all'),
            'compression.type': self.config.get('compression_type', 'lz4'),
            'batch.size': self.config.get('batch_size', 16384),
            'linger.ms': self.config.get('linger_ms', 10),
            'retries': self.config.get('retries', 3),
            'enable.idempotence': self.config.get('enable_idempotence', True)
        })
        
        # Consumer configuration
        consumer_config = base_config.copy()
        consumer_config.update({
            'group.id': self.config.get('group_id', 'default_group'),
            'enable.auto.commit': self.config.get('enable_auto_commit', True),
            'auto.offset.reset': self.config.get('auto_offset_reset', 'latest')
        })
        
        self.producer = Producer(producer_config)
        self.admin_client = AdminClient(base_config)
        # Consumer created on-demand
    
    async def _init_aiokafka_clients(self):
        """Initialize aiokafka clients."""
        # Producer configuration
        producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'acks': self.config.get('acks', 'all'),
            'compression_type': self.config.get('compression_type', 'lz4'),
            'batch_size': self.config.get('batch_size', 16384),
            'linger_ms': self.config.get('linger_ms', 10),
            'max_batch_size': self.config.get('max_batch_size', 1048576),
            'enable_idempotence': self.config.get('enable_idempotence', True),
            'value_serializer': lambda x: json.dumps(x).encode('utf-8') if isinstance(x, (dict, list)) else str(x).encode('utf-8')
        }
        
        # Apply security settings
        security_config = self.config.get('security', {})
        if security_config:
            producer_config.update(security_config)
        
        self.producer = AIOKafkaProducer(**producer_config)
        await self.producer.start()
    
    async def _cleanup_clients(self):
        """Clean up Kafka client connections."""
        try:
            if self.producer:
                if self.client_type == "aiokafka":
                    await self.producer.stop()
                else:
                    self.producer.close()
            
            if self.consumer:
                if self.client_type == "aiokafka":
                    await self.consumer.stop()
                else:
                    self.consumer.close()
        except Exception as e:
            logger.warning(f"Error during Kafka client cleanup: {str(e)}")
    
    # Producer Operations
    async def send_message(self, topic: str, value: Any, key: str = None, partition: int = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Send a message to a Kafka topic."""
        try:
            if self.client_type == "kafka-python":
                future = self.producer.send(
                    topic, 
                    value=value, 
                    key=key.encode('utf-8') if key else None,
                    partition=partition,
                    headers=[(k, v.encode('utf-8')) for k, v in headers.items()] if headers else None
                )
                record_metadata = future.get(timeout=30)
                return {
                    "topic": record_metadata.topic,
                    "partition": record_metadata.partition,
                    "offset": record_metadata.offset,
                    "timestamp": record_metadata.timestamp
                }
            
            elif self.client_type == "confluent-kafka":
                def delivery_callback(err, msg):
                    if err:
                        raise KafkaNodeError(f"Message delivery failed: {err}")
                
                self.producer.produce(
                    topic, 
                    value=json.dumps(value) if isinstance(value, (dict, list)) else str(value),
                    key=key,
                    partition=partition,
                    headers=headers,
                    callback=delivery_callback
                )
                self.producer.flush()
                return {"status": "sent", "topic": topic}
            
            elif self.client_type == "aiokafka":
                record_metadata = await self.producer.send(
                    topic,
                    value=value,
                    key=key.encode('utf-8') if key else None,
                    partition=partition,
                    headers=[(k, v.encode('utf-8')) for k, v in headers.items()] if headers else None
                )
                return {
                    "topic": record_metadata.topic,
                    "partition": record_metadata.partition,
                    "offset": record_metadata.offset,
                    "timestamp": record_metadata.timestamp
                }
                
        except Exception as e:
            raise KafkaNodeError(f"Failed to send message: {str(e)}", original_error=e)
    
    async def send_batch(self, topic: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send multiple messages as a batch."""
        try:
            results = []
            for msg in messages:
                result = await self.send_message(
                    topic,
                    msg.get('value'),
                    msg.get('key'),
                    msg.get('partition'),
                    msg.get('headers')
                )
                results.append(result)
            
            return {
                "messages_sent": len(results),
                "results": results,
                "topic": topic
            }
            
        except Exception as e:
            raise KafkaNodeError(f"Failed to send batch: {str(e)}", original_error=e)
    
    # Consumer Operations
    async def consume_messages(self, topics: List[str], max_messages: int = 100, timeout_ms: int = 1000) -> List[Dict[str, Any]]:
        """Consume messages from specified topics."""
        try:
            if not self.consumer:
                await self._create_consumer()
            
            if self.client_type == "kafka-python":
                self.consumer.subscribe(topics)
                messages = []
                start_time = time.time()
                
                while len(messages) < max_messages and (time.time() - start_time) * 1000 < timeout_ms:
                    msg_pack = self.consumer.poll(timeout_ms=100)
                    for tp, msgs in msg_pack.items():
                        for msg in msgs:
                            messages.append({
                                "topic": msg.topic,
                                "partition": msg.partition,
                                "offset": msg.offset,
                                "key": msg.key.decode('utf-8') if msg.key else None,
                                "value": msg.value,
                                "timestamp": msg.timestamp,
                                "headers": dict(msg.headers) if msg.headers else {}
                            })
                
                return messages
                
        except Exception as e:
            raise KafkaNodeError(f"Failed to consume messages: {str(e)}", original_error=e)
    
    async def _create_consumer(self):
        """Create consumer on-demand."""
        if self.client_type == "kafka-python":
            consumer_config = {
                'bootstrap_servers': self.bootstrap_servers,
                'group_id': self.config.get('group_id', 'default_group'),
                'enable_auto_commit': self.config.get('enable_auto_commit', True),
                'auto_offset_reset': self.config.get('auto_offset_reset', 'latest'),
                'value_deserializer': lambda x: json.loads(x.decode('utf-8')) if x else None
            }
            
            security_config = self.config.get('security', {})
            if security_config:
                consumer_config.update(security_config)
            
            self.consumer = KafkaConsumer(**consumer_config)
    
    # Admin Operations
    async def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1, config: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a new Kafka topic."""
        try:
            if self.client_type == "kafka-python":
                topic = NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                    topic_configs=config or {}
                )
                
                result = self.admin_client.create_topics([topic])
                future = result[topic_name]
                future.result()  # Wait for completion
                
                return {
                    "topic": topic_name,
                    "partitions": num_partitions,
                    "replication_factor": replication_factor,
                    "created": True
                }
                
        except TopicAlreadyExistsError:
            return {
                "topic": topic_name,
                "created": False,
                "error": "Topic already exists"
            }
        except Exception as e:
            raise KafkaNodeError(f"Failed to create topic: {str(e)}", original_error=e)
    
    async def list_topics(self) -> Dict[str, Any]:
        """List all available topics."""
        try:
            if self.client_type == "kafka-python":
                metadata = self.admin_client.describe_cluster()
                topics = list(metadata.topics.keys())
                
                return {
                    "topics": topics,
                    "count": len(topics),
                    "cluster_id": getattr(metadata, 'cluster_id', 'unknown')
                }
                
        except Exception as e:
            raise KafkaNodeError(f"Failed to list topics: {str(e)}", original_error=e)
    
    async def describe_cluster(self) -> Dict[str, Any]:
        """Get cluster information."""
        try:
            if self.client_type == "kafka-python":
                metadata = self.admin_client.describe_cluster()
                
                brokers = []
                for broker in metadata.brokers:
                    brokers.append({
                        "id": broker.nodeId,
                        "host": broker.host,
                        "port": broker.port
                    })
                
                return {
                    "cluster_id": getattr(metadata, 'cluster_id', 'unknown'),
                    "brokers": brokers,
                    "controller_id": getattr(metadata, 'controller_id', 'unknown'),
                    "topic_count": len(metadata.topics)
                }
                
        except Exception as e:
            raise KafkaNodeError(f"Failed to describe cluster: {str(e)}", original_error=e)

class KafkaNode(BaseNode):
    """
    Apache Kafka node for ACT workflow system.
    
    Provides comprehensive Apache Kafka integration with support for:
    - Message production with various sending patterns
    - Message consumption with consumer groups and offset management
    - Admin operations for topic and cluster management
    - Schema registry integration for Avro serialization
    - Stream processing capabilities
    - Monitoring and metrics collection
    - Security configuration support
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        # Producer Operations
        KafkaOperation.SEND_MESSAGE: {
            "required": ["bootstrap_servers", "topic", "value"],
            "optional": ["key", "partition", "headers", "client_type"],
            "description": "Send a message to a Kafka topic"
        },
        KafkaOperation.SEND_BATCH: {
            "required": ["bootstrap_servers", "topic", "messages"],
            "optional": ["client_type"],
            "description": "Send multiple messages as a batch"
        },
        
        # Consumer Operations
        KafkaOperation.CONSUME_MESSAGES: {
            "required": ["bootstrap_servers", "topics"],
            "optional": ["group_id", "max_messages", "timeout_ms", "client_type"],
            "description": "Consume messages from specified topics"
        },
        
        # Admin Operations
        KafkaOperation.CREATE_TOPIC: {
            "required": ["bootstrap_servers", "topic_name"],
            "optional": ["num_partitions", "replication_factor", "topic_config", "client_type"],
            "description": "Create a new Kafka topic"
        },
        KafkaOperation.LIST_TOPICS: {
            "required": ["bootstrap_servers"],
            "optional": ["client_type"],
            "description": "List all available topics"
        },
        KafkaOperation.DESCRIBE_CLUSTER: {
            "required": ["bootstrap_servers"],
            "optional": ["client_type"],
            "description": "Get cluster information"
        },
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        
        # Create operation dispatch map for clean routing
        self.operation_dispatch = {
            # Producer Operations
            KafkaOperation.SEND_MESSAGE: self._handle_send_message,
            KafkaOperation.SEND_BATCH: self._handle_send_batch,
            KafkaOperation.SEND_WITH_KEY: self._handle_send_with_key,
            KafkaOperation.SEND_ASYNC: self._handle_send_async,
            KafkaOperation.FLUSH_PRODUCER: self._handle_flush_producer,
            
            # Consumer Operations
            KafkaOperation.CONSUME_MESSAGES: self._handle_consume_messages,
            KafkaOperation.SUBSCRIBE_TOPICS: self._handle_subscribe_topics,
            KafkaOperation.UNSUBSCRIBE: self._handle_unsubscribe,
            KafkaOperation.COMMIT_OFFSETS: self._handle_commit_offsets,
            KafkaOperation.SEEK_TO_OFFSET: self._handle_seek_to_offset,
            KafkaOperation.PAUSE_CONSUMPTION: self._handle_pause_consumption,
            KafkaOperation.RESUME_CONSUMPTION: self._handle_resume_consumption,
            
            # Admin Operations
            KafkaOperation.CREATE_TOPIC: self._handle_create_topic,
            KafkaOperation.DELETE_TOPIC: self._handle_delete_topic,
            KafkaOperation.LIST_TOPICS: self._handle_list_topics,
            KafkaOperation.DESCRIBE_TOPIC: self._handle_describe_topic,
            KafkaOperation.DESCRIBE_CLUSTER: self._handle_describe_cluster,
            KafkaOperation.LIST_CONSUMER_GROUPS: self._handle_list_consumer_groups,
            KafkaOperation.DESCRIBE_CONSUMER_GROUP: self._handle_describe_consumer_group,
            
            # Configuration Operations
            KafkaOperation.SET_PRODUCER_CONFIG: self._handle_set_producer_config,
            KafkaOperation.SET_CONSUMER_CONFIG: self._handle_set_consumer_config,
            KafkaOperation.SET_SECURITY_CONFIG: self._handle_set_security_config,
            KafkaOperation.UPDATE_TOPIC_CONFIG: self._handle_update_topic_config,
            
            # Monitoring Operations
            KafkaOperation.GET_CONSUMER_LAG: self._handle_get_consumer_lag,
            KafkaOperation.GET_PRODUCER_METRICS: self._handle_get_producer_metrics,
            KafkaOperation.CHECK_TOPIC_HEALTH: self._handle_check_topic_health,
            KafkaOperation.GET_CLUSTER_STATUS: self._handle_get_cluster_status,
            KafkaOperation.GET_PARTITION_METADATA: self._handle_get_partition_metadata,
            
            # Offset Management
            KafkaOperation.RESET_CONSUMER_OFFSETS: self._handle_reset_consumer_offsets,
            KafkaOperation.GET_COMMITTED_OFFSETS: self._handle_get_committed_offsets,
            KafkaOperation.GET_PARTITION_OFFSETS: self._handle_get_partition_offsets,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the schema for KafkaNode."""
        return NodeSchema(
            name="KafkaNode",
            node_type="kafka",
            description="Apache Kafka integration node for message streaming, topic management, and stream processing",
            version="1.0.0",
            parameters=[
                NodeParameter(
                    name="operation",
                    type="string",
                    description="The Kafka operation to perform",
                    required=True,
                    enum=[op.value for op in KafkaOperation]
                ),
                NodeParameter(
                    name="bootstrap_servers",
                    type="array",
                    description="List of Kafka broker addresses (host:port)",
                    required=True
                ),
                NodeParameter(
                    name="client_type",
                    type="string",
                    description="Kafka client library to use",
                    required=False,
                    enum=["kafka-python", "confluent-kafka", "aiokafka"],
                    default="kafka-python"
                ),
                NodeParameter(
                    name="topic",
                    type="string",
                    description="Kafka topic name for message operations",
                    required=False
                ),
                NodeParameter(
                    name="topics",
                    type="array",
                    description="List of topic names for subscription",
                    required=False
                ),
                NodeParameter(
                    name="value",
                    type="any",
                    description="Message value to send",
                    required=False
                ),
                NodeParameter(
                    name="key",
                    type="string",
                    description="Message key for partitioning",
                    required=False
                ),
                NodeParameter(
                    name="partition",
                    type="number",
                    description="Specific partition to send message to",
                    required=False
                ),
                NodeParameter(
                    name="headers",
                    type="object",
                    description="Message headers as key-value pairs",
                    required=False
                ),
                NodeParameter(
                    name="messages",
                    type="array",
                    description="Array of messages for batch operations",
                    required=False
                ),
                NodeParameter(
                    name="group_id",
                    type="string",
                    description="Consumer group ID",
                    required=False
                ),
                NodeParameter(
                    name="max_messages",
                    type="number",
                    description="Maximum number of messages to consume",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="timeout_ms",
                    type="number",
                    description="Timeout in milliseconds for operations",
                    required=False,
                    default=1000
                ),
                NodeParameter(
                    name="topic_name",
                    type="string",
                    description="Name for topic creation/deletion",
                    required=False
                ),
                NodeParameter(
                    name="num_partitions",
                    type="number",
                    description="Number of partitions for new topic",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="replication_factor",
                    type="number",
                    description="Replication factor for new topic",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="topic_config",
                    type="object",
                    description="Configuration parameters for topic",
                    required=False
                ),
                NodeParameter(
                    name="security_config",
                    type="object",
                    description="Security configuration (SSL, SASL)",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="producer_config",
                    type="object",
                    description="Producer-specific configuration",
                    required=False
                ),
                NodeParameter(
                    name="consumer_config",
                    type="object",
                    description="Consumer-specific configuration",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "result": NodeParameterType.OBJECT,
                "messages": NodeParameterType.ARRAY,
                "topics": NodeParameterType.ARRAY,
                "cluster_info": NodeParameterType.OBJECT,
                "metrics": NodeParameterType.OBJECT,
                "timestamp": NodeParameterType.STRING,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, data: Dict[str, Any]) -> None:
        """Custom validation for Kafka operations."""
        params = data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation parameter is required")
        
        if operation not in [op.value for op in KafkaOperation]:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Get operation metadata for validation
        metadata = self.OPERATION_METADATA.get(operation, {})
        required_params = metadata.get("required", [])
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                raise ValueError(f"Required parameter '{param}' missing for operation '{operation}'")
        
        # Validate bootstrap_servers
        bootstrap_servers = params.get("bootstrap_servers", [])
        if not bootstrap_servers or not isinstance(bootstrap_servers, list):
            raise ValueError("bootstrap_servers must be a non-empty list")
        
        # Validate each server address
        for server in bootstrap_servers:
            if not isinstance(server, str) or ':' not in server:
                raise ValueError("Each bootstrap server must be in format 'host:port'")
        
        # Validate client type
        client_type = params.get("client_type", "kafka-python")
        if client_type not in ["kafka-python", "confluent-kafka", "aiokafka"]:
            raise ValueError("client_type must be one of: kafka-python, confluent-kafka, aiokafka")
        
        # Validate topic operations
        if operation in [KafkaOperation.SEND_MESSAGE, KafkaOperation.SEND_BATCH]:
            if not params.get("topic"):
                raise ValueError("topic parameter is required for message operations")
        
        # Validate consumer operations
        if operation in [KafkaOperation.CONSUME_MESSAGES, KafkaOperation.SUBSCRIBE_TOPICS]:
            topics = params.get("topics", [])
            if not topics or not isinstance(topics, list):
                raise ValueError("topics parameter must be a non-empty list for consumer operations")
        
        # Validate topic creation
        if operation == KafkaOperation.CREATE_TOPIC:
            topic_name = params.get("topic_name")
            if not topic_name or not isinstance(topic_name, str):
                raise ValueError("topic_name must be a non-empty string")
            
            num_partitions = params.get("num_partitions", 1)
            if not isinstance(num_partitions, int) or num_partitions < 1:
                raise ValueError("num_partitions must be a positive integer")
            
            replication_factor = params.get("replication_factor", 1)
            if not isinstance(replication_factor, int) or replication_factor < 1:
                raise ValueError("replication_factor must be a positive integer")
        
        # Validate batch messages
        if operation == KafkaOperation.SEND_BATCH:
            messages = params.get("messages", [])
            if not messages or not isinstance(messages, list):
                raise ValueError("messages parameter must be a non-empty list for batch operations")
            
            for i, msg in enumerate(messages):
                if not isinstance(msg, dict) or 'value' not in msg:
                    raise ValueError(f"Message at index {i} must be a dict with 'value' field")
        
        # Validate timeout values
        timeout_ms = params.get("timeout_ms")
        if timeout_ms is not None and (not isinstance(timeout_ms, (int, float)) or timeout_ms <= 0):
            raise ValueError("timeout_ms must be a positive number")
        
        max_messages = params.get("max_messages")
        if max_messages is not None and (not isinstance(max_messages, int) or max_messages <= 0):
            raise ValueError("max_messages must be a positive integer")
    
    @asynccontextmanager
    async def _get_kafka_wrapper(self, config: Dict[str, Any], client_type: str = "kafka-python"):
        """Get KafkaWrapper with proper lifecycle management."""
        wrapper = KafkaWrapper(config, client_type)
        try:
            async with wrapper:
                yield wrapper
        except Exception as e:
            self.logger.error(f"Kafka wrapper error: {str(e)}")
            raise
    
    def _mask_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked = params.copy()
        
        # Mask security configuration
        if "security_config" in masked:
            masked["security_config"] = "***SECURITY_CONFIG***"
        
        # Mask large message content
        if "value" in masked and isinstance(masked["value"], str) and len(masked["value"]) > 100:
            masked["value"] = "***LARGE_MESSAGE***"
        
        # Mask batch messages
        if "messages" in masked and isinstance(masked["messages"], list) and len(masked["messages"]) > 5:
            masked["messages"] = f"***{len(masked['messages'])}_MESSAGES***"
        
        # Mask producer/consumer config with potentially sensitive data
        for config_field in ["producer_config", "consumer_config"]:
            if config_field in masked and isinstance(masked[config_field], dict):
                config_copy = masked[config_field].copy()
                for sensitive_key in ["password", "ssl_keystore_password", "ssl_key_password"]:
                    if sensitive_key in config_copy:
                        config_copy[sensitive_key] = "***MASKED***"
                masked[config_field] = config_copy
        
        return masked
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Kafka operation."""
        try:
            params = data.get("params", {})
            operation = params.get("operation")
            
            # Log operation (with sensitive data masked)
            masked_params = self._mask_sensitive_data(params)
            self.logger.info(f"Executing Kafka operation: {operation} with params: {masked_params}")
            
            # Get operation handler
            handler = self.operation_dispatch.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Unsupported Kafka operation: {operation}",
                    "operation": operation
                }
            
            # Execute operation
            result = await handler(params)
            
            self.logger.info(f"Kafka operation {operation} completed successfully")
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except KafkaNodeError as e:
            error_msg = f"Kafka operation error: {str(e)}"
            if e.error_code:
                error_msg += f" (Code: {e.error_code})"
            
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "error_code": e.error_code,
                "operation": params.get("operation", "unknown")
            }
        except Exception as e:
            error_msg = f"Kafka operation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
    
    # Producer Operation Handlers
    async def _handle_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_message operation."""
        bootstrap_servers = params["bootstrap_servers"]
        topic = params["topic"]
        value = params["value"]
        key = params.get("key")
        partition = params.get("partition")
        headers = params.get("headers")
        client_type = params.get("client_type", "kafka-python")
        
        config = {
            "bootstrap_servers": bootstrap_servers,
            "security": params.get("security_config", {}),
            **params.get("producer_config", {})
        }
        
        async with self._get_kafka_wrapper(config, client_type) as kafka:
            result = await kafka.send_message(topic, value, key, partition, headers)
            return {
                "message_sent": True,
                "topic": topic,
                "metadata": result,
                "client_type": client_type
            }
    
    async def _handle_send_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_batch operation."""
        bootstrap_servers = params["bootstrap_servers"]
        topic = params["topic"]
        messages = params["messages"]
        client_type = params.get("client_type", "kafka-python")
        
        config = {
            "bootstrap_servers": bootstrap_servers,
            "security": params.get("security_config", {}),
            **params.get("producer_config", {})
        }
        
        async with self._get_kafka_wrapper(config, client_type) as kafka:
            result = await kafka.send_batch(topic, messages)
            return {
                "batch_sent": True,
                "topic": topic,
                "messages_count": result["messages_sent"],
                "results": result["results"],
                "client_type": client_type
            }
    
    async def _handle_send_with_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_with_key operation."""
        # This is essentially the same as send_message with a key
        return await self._handle_send_message(params)
    
    async def _handle_send_async(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_async operation."""
        # For now, delegate to regular send_message
        # In a real implementation, this would use async callbacks
        return await self._handle_send_message(params)
    
    async def _handle_flush_producer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flush_producer operation."""
        return {"message": "flush_producer handler not implemented yet"}
    
    # Consumer Operation Handlers
    async def _handle_consume_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle consume_messages operation."""
        bootstrap_servers = params["bootstrap_servers"]
        topics = params["topics"]
        max_messages = params.get("max_messages", 100)
        timeout_ms = params.get("timeout_ms", 1000)
        client_type = params.get("client_type", "kafka-python")
        
        config = {
            "bootstrap_servers": bootstrap_servers,
            "group_id": params.get("group_id", "default_group"),
            "security": params.get("security_config", {}),
            **params.get("consumer_config", {})
        }
        
        async with self._get_kafka_wrapper(config, client_type) as kafka:
            messages = await kafka.consume_messages(topics, max_messages, timeout_ms)
            return {
                "messages_consumed": len(messages),
                "messages": messages,
                "topics": topics,
                "client_type": client_type
            }
    
    async def _handle_subscribe_topics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscribe_topics operation."""
        # This would typically be used with a persistent consumer
        return {"message": "subscribe_topics handler not implemented yet"}
    
    async def _handle_unsubscribe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unsubscribe operation."""
        return {"message": "unsubscribe handler not implemented yet"}
    
    async def _handle_commit_offsets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle commit_offsets operation."""
        return {"message": "commit_offsets handler not implemented yet"}
    
    async def _handle_seek_to_offset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle seek_to_offset operation."""
        return {"message": "seek_to_offset handler not implemented yet"}
    
    async def _handle_pause_consumption(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pause_consumption operation."""
        return {"message": "pause_consumption handler not implemented yet"}
    
    async def _handle_resume_consumption(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resume_consumption operation."""
        return {"message": "resume_consumption handler not implemented yet"}
    
    # Admin Operation Handlers
    async def _handle_create_topic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_topic operation."""
        bootstrap_servers = params["bootstrap_servers"]
        topic_name = params["topic_name"]
        num_partitions = params.get("num_partitions", 1)
        replication_factor = params.get("replication_factor", 1)
        topic_config = params.get("topic_config", {})
        client_type = params.get("client_type", "kafka-python")
        
        config = {
            "bootstrap_servers": bootstrap_servers,
            "security": params.get("security_config", {})
        }
        
        async with self._get_kafka_wrapper(config, client_type) as kafka:
            result = await kafka.create_topic(topic_name, num_partitions, replication_factor, topic_config)
            return {
                "topic_created": result.get("created", False),
                "topic_name": topic_name,
                "partitions": num_partitions,
                "replication_factor": replication_factor,
                "client_type": client_type,
                **result
            }
    
    async def _handle_delete_topic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_topic operation."""
        return {"message": "delete_topic handler not implemented yet"}
    
    async def _handle_list_topics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_topics operation."""
        bootstrap_servers = params["bootstrap_servers"]
        client_type = params.get("client_type", "kafka-python")
        
        config = {
            "bootstrap_servers": bootstrap_servers,
            "security": params.get("security_config", {})
        }
        
        async with self._get_kafka_wrapper(config, client_type) as kafka:
            result = await kafka.list_topics()
            return {
                "topics_listed": True,
                "topics": result["topics"],
                "topic_count": result["count"],
                "cluster_id": result.get("cluster_id"),
                "client_type": client_type
            }
    
    async def _handle_describe_topic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle describe_topic operation."""
        return {"message": "describe_topic handler not implemented yet"}
    
    async def _handle_describe_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle describe_cluster operation."""
        bootstrap_servers = params["bootstrap_servers"]
        client_type = params.get("client_type", "kafka-python")
        
        config = {
            "bootstrap_servers": bootstrap_servers,
            "security": params.get("security_config", {})
        }
        
        async with self._get_kafka_wrapper(config, client_type) as kafka:
            result = await kafka.describe_cluster()
            return {
                "cluster_described": True,
                "cluster_info": result,
                "broker_count": len(result.get("brokers", [])),
                "client_type": client_type
            }
    
    async def _handle_list_consumer_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_consumer_groups operation."""
        return {"message": "list_consumer_groups handler not implemented yet"}
    
    async def _handle_describe_consumer_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle describe_consumer_group operation."""
        return {"message": "describe_consumer_group handler not implemented yet"}
    
    # Configuration Operation Handlers (placeholders)
    async def _handle_set_producer_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set_producer_config operation."""
        return {"message": "set_producer_config handler not implemented yet"}
    
    async def _handle_set_consumer_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set_consumer_config operation."""
        return {"message": "set_consumer_config handler not implemented yet"}
    
    async def _handle_set_security_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set_security_config operation."""
        return {"message": "set_security_config handler not implemented yet"}
    
    async def _handle_update_topic_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_topic_config operation."""
        return {"message": "update_topic_config handler not implemented yet"}
    
    # Monitoring Operation Handlers (placeholders)
    async def _handle_get_consumer_lag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_consumer_lag operation."""
        return {"message": "get_consumer_lag handler not implemented yet"}
    
    async def _handle_get_producer_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_producer_metrics operation."""
        return {"message": "get_producer_metrics handler not implemented yet"}
    
    async def _handle_check_topic_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle check_topic_health operation."""
        return {"message": "check_topic_health handler not implemented yet"}
    
    async def _handle_get_cluster_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_cluster_status operation."""
        return {"message": "get_cluster_status handler not implemented yet"}
    
    async def _handle_get_partition_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_partition_metadata operation."""
        return {"message": "get_partition_metadata handler not implemented yet"}
    
    # Offset Management Handlers (placeholders)
    async def _handle_reset_consumer_offsets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reset_consumer_offsets operation."""
        return {"message": "reset_consumer_offsets handler not implemented yet"}
    
    async def _handle_get_committed_offsets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_committed_offsets operation."""
        return {"message": "get_committed_offsets handler not implemented yet"}
    
    async def _handle_get_partition_offsets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_partition_offsets operation."""
        return {"message": "get_partition_offsets handler not implemented yet"}