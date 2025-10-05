"""
DynamoDB Node - Performs AWS DynamoDB operations using boto3 SDK with comprehensive options and error handling.
"""

import logging
import json
import time
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
import boto3
from botocore.exceptions import ClientError

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

# Configure logging
logger = logging.getLogger(__name__)

class DynamoDBOperationType:
    """DynamoDB operation types."""
    CREATE_TABLE = "create_table"
    DELETE_TABLE = "delete_table"
    LIST_TABLES = "list_tables"
    DESCRIBE_TABLE = "describe_table"
    PUT_ITEM = "put_item"
    GET_ITEM = "get_item"
    UPDATE_ITEM = "update_item"
    DELETE_ITEM = "delete_item"
    QUERY = "query"
    SCAN = "scan"
    BATCH_WRITE = "batch_write"
    BATCH_GET = "batch_get"
    TRANSACT_WRITE = "transact_write"
    TRANSACT_GET = "transact_get"

class DynamoDBNode(BaseNode):
    """
    Node for interacting with AWS DynamoDB.
    Provides functionality for all common DynamoDB operations with comprehensive error handling.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.dynamodb_client = None
        self.dynamodb_resource = None
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the DynamoDB node."""
        return NodeSchema(
            node_type="dynamodb",
            version="1.0.0",
            description="Interacts with AWS DynamoDB using boto3 SDK",
            parameters=[
                # AWS Connection parameters
                NodeParameter(
                    name="region_name",
                    type=NodeParameterType.STRING,
                    description="AWS region name",
                    required=False,
                    default="us-east-1"
                ),
                NodeParameter(
                    name="aws_access_key_id",
                    type=NodeParameterType.STRING,
                    description="AWS access key ID",
                    required=False,
                ),
                NodeParameter(
                    name="aws_secret_access_key",
                    type=NodeParameterType.STRING,
                    description="AWS secret access key",
                    required=False,
                ),
                NodeParameter(
                    name="endpoint_url",
                    type=NodeParameterType.STRING,
                    description="Custom endpoint URL (e.g., for local DynamoDB)",
                    required=False,
                ),
                
                # Operation parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="DynamoDB operation to perform",
                    required=True,
                    enum=[
                        DynamoDBOperationType.CREATE_TABLE,
                        DynamoDBOperationType.DELETE_TABLE,
                        DynamoDBOperationType.LIST_TABLES,
                        DynamoDBOperationType.DESCRIBE_TABLE,
                        DynamoDBOperationType.PUT_ITEM,
                        DynamoDBOperationType.GET_ITEM,
                        DynamoDBOperationType.UPDATE_ITEM,
                        DynamoDBOperationType.DELETE_ITEM,
                        DynamoDBOperationType.QUERY,
                        DynamoDBOperationType.SCAN,
                        DynamoDBOperationType.BATCH_WRITE,
                        DynamoDBOperationType.BATCH_GET,
                        DynamoDBOperationType.TRANSACT_WRITE,
                        DynamoDBOperationType.TRANSACT_GET
                    ]
                ),
                NodeParameter(
                    name="table_name",
                    type=NodeParameterType.STRING,
                    description="Name of the DynamoDB table",
                    required=False,
                ),
                
                # Table definition parameters (for CREATE_TABLE)
                NodeParameter(
                    name="key_schema",
                    type=NodeParameterType.ARRAY,
                    description="Key schema for the table",
                    required=False,
                ),
                NodeParameter(
                    name="attribute_definitions",
                    type=NodeParameterType.ARRAY,
                    description="Attribute definitions for the table",
                    required=False,
                ),
                NodeParameter(
                    name="provisioned_throughput",
                    type=NodeParameterType.OBJECT,
                    description="Provisioned throughput for the table",
                    required=False,
                ),
                NodeParameter(
                    name="billing_mode",
                    type=NodeParameterType.STRING,
                    description="Billing mode (PROVISIONED or PAY_PER_REQUEST)",
                    required=False,
                    default="PAY_PER_REQUEST",
                    enum=["PROVISIONED", "PAY_PER_REQUEST"]
                ),
                
                # Item operation parameters
                NodeParameter(
                    name="item",
                    type=NodeParameterType.OBJECT,
                    description="Item to put, get, update, or delete",
                    required=False,
                ),
                NodeParameter(
                    name="key",
                    type=NodeParameterType.OBJECT,
                    description="Key to identify an item",
                    required=False,
                ),
                NodeParameter(
                    name="update_expression",
                    type=NodeParameterType.STRING,
                    description="Update expression for UPDATE_ITEM operation",
                    required=False,
                ),
                NodeParameter(
                    name="expression_attribute_names",
                    type=NodeParameterType.OBJECT,
                    description="Expression attribute names for operations",
                    required=False,
                ),
                NodeParameter(
                    name="expression_attribute_values",
                    type=NodeParameterType.OBJECT,
                    description="Expression attribute values for operations",
                    required=False,
                ),
                NodeParameter(
                    name="condition_expression",
                    type=NodeParameterType.STRING,
                    description="Condition expression for operations",
                    required=False,
                ),
                
                # Query and Scan parameters
                NodeParameter(
                    name="key_condition_expression",
                    type=NodeParameterType.STRING,
                    description="Key condition expression for QUERY operation",
                    required=False,
                ),
                NodeParameter(
                    name="filter_expression",
                    type=NodeParameterType.STRING,
                    description="Filter expression for QUERY or SCAN operations",
                    required=False,
                ),
                NodeParameter(
                    name="index_name",
                    type=NodeParameterType.STRING,
                    description="Name of the index to query",
                    required=False,
                ),
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of items to retrieve",
                    required=False,
                ),
                NodeParameter(
                    name="scan_index_forward",
                    type=NodeParameterType.BOOLEAN,
                    description="Direction for index traversal",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="consistent_read",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use consistent read",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="exclusive_start_key",
                    type=NodeParameterType.OBJECT,
                    description="Key to start with for pagination",
                    required=False,
                ),
                
                # Batch operations parameters
                NodeParameter(
                    name="batch_items",
                    type=NodeParameterType.ARRAY,
                    description="Items for batch operations",
                    required=False,
                ),
                
                # Transaction operations parameters
                NodeParameter(
                    name="transact_items",
                    type=NodeParameterType.ARRAY,
                    description="Items for transactional operations",
                    required=False,
                ),
                
                # General options
                NodeParameter(
                    name="return_values",
                    type=NodeParameterType.STRING,
                    description="Return values option for write operations",
                    required=False,
                    default="NONE",
                    enum=["NONE", "ALL_OLD", "UPDATED_OLD", "ALL_NEW", "UPDATED_NEW"]
                ),
                NodeParameter(
                    name="return_consumed_capacity",
                    type=NodeParameterType.STRING,
                    description="Whether to return consumed capacity",
                    required=False,
                    default="NONE",
                    enum=["NONE", "TOTAL", "INDEXES"]
                ),
                NodeParameter(
                    name="return_item_collection_metrics",
                    type=NodeParameterType.STRING,
                    description="Whether to return item collection metrics",
                    required=False,
                    default="NONE",
                    enum=["NONE", "SIZE"]
                ),
                
                # Wait parameters
                NodeParameter(
                    name="wait_for_active",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to wait for table to become active",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="wait_timeout",
                    type=NodeParameterType.NUMBER,
                    description="Timeout in seconds for wait operations",
                    required=False,
                    default=300
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "consumed_capacity": NodeParameterType.OBJECT,
                "item_collection_metrics": NodeParameterType.OBJECT,
                "count": NodeParameterType.NUMBER,
                "scanned_count": NodeParameterType.NUMBER,
                "last_evaluated_key": NodeParameterType.OBJECT,
            },
            
            # Add metadata
            tags=["aws", "dynamodb", "database", "nosql"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for DynamoDB parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Validate table name for operations that require it
        if operation != DynamoDBOperationType.LIST_TABLES:
            if not params.get("table_name"):
                raise NodeValidationError("Table name is required for this operation")
        
        # Validate create table parameters
        if operation == DynamoDBOperationType.CREATE_TABLE:
            if not params.get("key_schema"):
                raise NodeValidationError("Key schema is required for CREATE_TABLE operation")
            if not params.get("attribute_definitions"):
                raise NodeValidationError("Attribute definitions are required for CREATE_TABLE operation")
            
            # Validate provisioned throughput if billing mode is PROVISIONED
            if params.get("billing_mode") == "PROVISIONED" and not params.get("provisioned_throughput"):
                raise NodeValidationError("Provisioned throughput is required when billing mode is PROVISIONED")
        
        # Validate parameters for item operations
        if operation in [DynamoDBOperationType.PUT_ITEM]:
            if not params.get("item"):
                raise NodeValidationError("Item is required for PUT_ITEM operation")
        
        if operation in [DynamoDBOperationType.GET_ITEM, DynamoDBOperationType.DELETE_ITEM]:
            if not params.get("key"):
                raise NodeValidationError("Key is required for this operation")
        
        if operation == DynamoDBOperationType.UPDATE_ITEM:
            if not params.get("key"):
                raise NodeValidationError("Key is required for UPDATE_ITEM operation")
            if not params.get("update_expression"):
                raise NodeValidationError("Update expression is required for UPDATE_ITEM operation")
        
        # Validate query parameters
        if operation == DynamoDBOperationType.QUERY:
            if not params.get("key_condition_expression"):
                raise NodeValidationError("Key condition expression is required for QUERY operation")
        
        # Validate batch operations
        if operation in [DynamoDBOperationType.BATCH_WRITE, DynamoDBOperationType.BATCH_GET]:
            if not params.get("batch_items"):
                raise NodeValidationError("Batch items are required for batch operations")
        
        # Validate transaction operations
        if operation in [DynamoDBOperationType.TRANSACT_WRITE, DynamoDBOperationType.TRANSACT_GET]:
            if not params.get("transact_items"):
                raise NodeValidationError("Transaction items are required for transaction operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the DynamoDB node operation."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            params = validated_data.copy()
            
            # Initialize DynamoDB client and resource if not already initialized
            self._initialize_boto3_clients(params)
            
            # Get operation type
            operation = params.get("operation")
            
            # Execute the appropriate operation based on the operation type
            if operation == DynamoDBOperationType.CREATE_TABLE:
                return await self.operation_create_table(params)
            elif operation == DynamoDBOperationType.DELETE_TABLE:
                return await self.operation_delete_table(params)
            elif operation == DynamoDBOperationType.LIST_TABLES:
                return await self.operation_list_tables(params)
            elif operation == DynamoDBOperationType.DESCRIBE_TABLE:
                return await self.operation_describe_table(params)
            elif operation == DynamoDBOperationType.PUT_ITEM:
                return await self.operation_put_item(params)
            elif operation == DynamoDBOperationType.GET_ITEM:
                return await self.operation_get_item(params)
            elif operation == DynamoDBOperationType.UPDATE_ITEM:
                return await self.operation_update_item(params)
            elif operation == DynamoDBOperationType.DELETE_ITEM:
                return await self.operation_delete_item(params)
            elif operation == DynamoDBOperationType.QUERY:
                return await self.operation_query(params)
            elif operation == DynamoDBOperationType.SCAN:
                return await self.operation_scan(params)
            elif operation == DynamoDBOperationType.BATCH_WRITE:
                return await self.operation_batch_write(params)
            elif operation == DynamoDBOperationType.BATCH_GET:
                return await self.operation_batch_get(params)
            elif operation == DynamoDBOperationType.TRANSACT_WRITE:
                return await self.operation_transact_write(params)
            elif operation == DynamoDBOperationType.TRANSACT_GET:
                return await self.operation_transact_get(params)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            error_message = f"Error in DynamoDB node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "data": None,
                "error": error_message,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": 0,
                "scanned_count": 0,
                "last_evaluated_key": None
            }
    
    def _initialize_boto3_clients(self, params: Dict[str, Any]) -> None:
        """
        Initialize boto3 clients for DynamoDB.
        
        Args:
            params: Parameters including AWS credentials and region
        """
        # Extract AWS connection parameters
        region_name = params.get("region_name", "us-east-1")
        aws_access_key_id = params.get("aws_access_key_id")
        aws_secret_access_key = params.get("aws_secret_access_key")
        endpoint_url = params.get("endpoint_url")
        
        # Create client kwargs
        client_kwargs = {
            "region_name": region_name
        }
        
        # Add credentials if provided
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs.update({
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key
            })
        
        # Add endpoint URL if provided (for local DynamoDB)
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url
        
        # Create client and resource
        self.dynamodb_client = boto3.client("dynamodb", **client_kwargs)
        self.dynamodb_resource = boto3.resource("dynamodb", **client_kwargs)
    
    async def operation_create_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a DynamoDB table.
        
        Args:
            params: Parameters for creating the table
            
        Returns:
            Operation result
        """
        table_name = params["table_name"]
        key_schema = params["key_schema"]
        attribute_definitions = params["attribute_definitions"]
        billing_mode = params.get("billing_mode", "PAY_PER_REQUEST")
        wait_for_active = params.get("wait_for_active", True)
        wait_timeout = params.get("wait_timeout", 300)
        
        create_params = {
            "TableName": table_name,
            "KeySchema": key_schema,
            "AttributeDefinitions": attribute_definitions,
            "BillingMode": billing_mode
        }
        
        # Add provisioned throughput if billing mode is PROVISIONED
        if billing_mode == "PROVISIONED":
            provisioned_throughput = params.get("provisioned_throughput", {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            })
            create_params["ProvisionedThroughput"] = provisioned_throughput
        
        try:
            # Create the table
            response = self.dynamodb_client.create_table(**create_params)
            
            # Wait for the table to become active if requested
            if wait_for_active:
                waiter = self.dynamodb_client.get_waiter('table_exists')
                waiter.wait(
                    TableName=table_name,
                    WaiterConfig={
                        'Delay': 5,
                        'MaxAttempts': wait_timeout // 5
                    }
                )
            
            return {
                "status": "success",
                "data": response.get("TableDescription"),
                "error": None,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
        except ClientError as e:
            error_message = str(e)
            if "ResourceInUseException" in error_message:
                error_message = f"Table {table_name} already exists"
            
            return {
                "status": "error",
                "data": None,
                "error": error_message,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_delete_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a DynamoDB table.
        
        Args:
            params: Parameters for deleting the table
            
        Returns:
            Operation result
        """
        table_name = params["table_name"]
        wait_for_delete = params.get("wait_for_active", True)
        wait_timeout = params.get("wait_timeout", 300)
        
        try:
            # Delete the table
            response = self.dynamodb_client.delete_table(TableName=table_name)
            
            # Wait for the table to be deleted if requested
            if wait_for_delete:
                waiter = self.dynamodb_client.get_waiter('table_not_exists')
                waiter.wait(
                    TableName=table_name,
                    WaiterConfig={
                        'Delay': 5,
                        'MaxAttempts': wait_timeout // 5
                    }
                )
            
            return {
                "status": "success",
                "data": response.get("TableDescription"),
                "error": None,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
        except ClientError as e:
            error_message = str(e)
            if "ResourceNotFoundException" in error_message:
                error_message = f"Table {table_name} does not exist"
            
            return {
                "status": "error",
                "data": None,
                "error": error_message,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_list_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List DynamoDB tables.
        
        Args:
            params: Parameters for listing tables
            
        Returns:
            Operation result with list of tables
        """
        limit = params.get("limit")
        exclusive_start_table_name = params.get("exclusive_start_key")
        
        list_params = {}
        if limit:
            list_params["Limit"] = limit
        if exclusive_start_table_name:
            list_params["ExclusiveStartTableName"] = exclusive_start_table_name
        
        try:
            response = self.dynamodb_client.list_tables(**list_params)
            
            return {
                "status": "success",
                "data": {
                    "TableNames": response.get("TableNames", []),
                    "LastEvaluatedTableName": response.get("LastEvaluatedTableName")
                },
                "error": None,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": len(response.get("TableNames", [])),
                "scanned_count": None,
                "last_evaluated_key": response.get("LastEvaluatedTableName")
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_describe_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describe a DynamoDB table.
        
        Args:
            params: Parameters for describing the table
            
        Returns:
            Operation result with table details
        """
        table_name = params["table_name"]
        try:
            response = self.dynamodb_client.describe_table(TableName=table_name)
            return {
                "status": "success",
                "data": response.get("Table"),
                "error": None,
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_put_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Put an item into a DynamoDB table.
        
        Args:
            params: Parameters for putting an item
            
        Returns:
            Operation result
        """
        table_name = params["table_name"]
        item = params["item"]
        
        try:
            table = self.dynamodb_resource.Table(table_name)
            response = table.put_item(Item=item)
            return {
                "status": "success",
                "data": response,
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": response.get("ItemCollectionMetrics"),
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_get_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get an item from a DynamoDB table.
        
        Args:
            params: Parameters for getting an item
            
        Returns:
            Operation result with the retrieved item
        """
        table_name = params["table_name"]
        key = params["key"]
        
        try:
            table = self.dynamodb_resource.Table(table_name)
            response = table.get_item(Key=key)
            return {
                "status": "success",
                "data": response.get("Item"),
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_update_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an item in a DynamoDB table.
        
        Args:
            params: Parameters for updating the item
            
        Returns:
            Operation result with updated attributes
        """
        table_name = params["table_name"]
        key = params["key"]
        update_expression = params["update_expression"]
        expr_attr_values = params["expression_attribute_values"]
        expr_attr_names = params.get("expression_attribute_names")
        
        try:
            table = self.dynamodb_resource.Table(table_name)
            kwargs = {
                "Key": key,
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expr_attr_values,
                "ReturnValues": params.get("return_values", "NONE")
            }
            if expr_attr_names:
                kwargs["ExpressionAttributeNames"] = expr_attr_names
            
            response = table.update_item(**kwargs)
            return {
                "status": "success",
                "data": response.get("Attributes"),
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": response.get("ItemCollectionMetrics"),
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_delete_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete an item from a DynamoDB table.
        
        Args:
            params: Parameters for deleting the item
            
        Returns:
            Operation result
        """
        table_name = params["table_name"]
        key = params["key"]
        
        try:
            table = self.dynamodb_resource.Table(table_name)
            response = table.delete_item(Key=key, ReturnValues=params.get("return_values", "NONE"))
            return {
                "status": "success",
                "data": response,
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": response.get("ItemCollectionMetrics"),
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query items from a DynamoDB table.
        
        Args:
            params: Parameters for querying items
            
        Returns:
            Operation result with queried items
        """
        table_name = params["table_name"]
        key_condition_expression = params["key_condition_expression"]
        filter_expression = params.get("filter_expression")
        index_name = params.get("index_name")
        expression_attribute_names = params.get("expression_attribute_names")
        expression_attribute_values = params.get("expression_attribute_values")
        projection_expression = params.get("projection_expression")
        consistent_read = params.get("consistent_read", False)
        scan_index_forward = params.get("scan_index_forward", True)
        limit = params.get("limit")
        exclusive_start_key = params.get("exclusive_start_key")
        return_consumed_capacity = params.get("return_consumed_capacity", "NONE")
        
        query_params = {
            "TableName": table_name,
            "KeyConditionExpression": key_condition_expression,
            "ConsistentRead": consistent_read,
            "ScanIndexForward": scan_index_forward,
            "ReturnConsumedCapacity": return_consumed_capacity
        }
        
        # Add optional parameters if provided
        if filter_expression:
            query_params["FilterExpression"] = filter_expression
        if index_name:
            query_params["IndexName"] = index_name
        if expression_attribute_names:
            query_params["ExpressionAttributeNames"] = expression_attribute_names
        if expression_attribute_values:
            query_params["ExpressionAttributeValues"] = expression_attribute_values
        if projection_expression:
            query_params["ProjectionExpression"] = projection_expression
        if limit:
            query_params["Limit"] = limit
        if exclusive_start_key:
            query_params["ExclusiveStartKey"] = exclusive_start_key
        
        try:
            response = self.dynamodb_client.query(**query_params)
            
            return {
                "status": "success",
                "data": {
                    "Items": response.get("Items", []),
                    "Count": response.get("Count", 0),
                    "ScannedCount": response.get("ScannedCount", 0),
                    "LastEvaluatedKey": response.get("LastEvaluatedKey")
                },
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": None,
                "count": response.get("Count", 0),
                "scanned_count": response.get("ScannedCount", 0),
                "last_evaluated_key": response.get("LastEvaluatedKey")
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_scan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan items from a DynamoDB table.
        
        Args:
            params: Parameters for scanning items
            
        Returns:
            Operation result with scanned items
        """
        table_name = params["table_name"]
        filter_expression = params.get("filter_expression")
        index_name = params.get("index_name")
        expression_attribute_names = params.get("expression_attribute_names")
        expression_attribute_values = params.get("expression_attribute_values")
        projection_expression = params.get("projection_expression")
        consistent_read = params.get("consistent_read", False)
        limit = params.get("limit")
        exclusive_start_key = params.get("exclusive_start_key")
        return_consumed_capacity = params.get("return_consumed_capacity", "NONE")
        
        scan_params = {
            "TableName": table_name,
            "ConsistentRead": consistent_read,
            "ReturnConsumedCapacity": return_consumed_capacity
        }
        
        # Add optional parameters if provided
        if filter_expression:
            scan_params["FilterExpression"] = filter_expression
        if index_name:
            scan_params["IndexName"] = index_name
        if expression_attribute_names:
            scan_params["ExpressionAttributeNames"] = expression_attribute_names
        if expression_attribute_values:
            scan_params["ExpressionAttributeValues"] = expression_attribute_values
        if projection_expression:
            scan_params["ProjectionExpression"] = projection_expression
        if limit:
            scan_params["Limit"] = limit
        if exclusive_start_key:
            scan_params["ExclusiveStartKey"] = exclusive_start_key
        
        try:
            response = self.dynamodb_client.scan(**scan_params)
            
            return {
                "status": "success",
                "data": {
                    "Items": response.get("Items", []),
                    "Count": response.get("Count", 0),
                    "ScannedCount": response.get("ScannedCount", 0),
                    "LastEvaluatedKey": response.get("LastEvaluatedKey")
                },
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": None,
                "count": response.get("Count", 0),
                "scanned_count": response.get("ScannedCount", 0),
                "last_evaluated_key": response.get("LastEvaluatedKey")
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_batch_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a batch write operation.
        
        Args:
            params: Parameters for batch write
            
        Returns:
            Operation result
        """
        table_name = params["table_name"]
        batch_items = params["batch_items"]
        return_consumed_capacity = params.get("return_consumed_capacity", "NONE")
        return_item_collection_metrics = params.get("return_item_collection_metrics", "NONE")
        
        # Prepare request items
        request_items = {
            table_name: []
        }
        
        # Add put or delete requests
        for item in batch_items:
            if "Item" in item:
                request_items[table_name].append({
                    "PutRequest": {
                        "Item": item["Item"]
                    }
                })
            elif "Key" in item:
                request_items[table_name].append({
                    "DeleteRequest": {
                        "Key": item["Key"]
                    }
                })
        
        batch_params = {
            "RequestItems": request_items,
            "ReturnConsumedCapacity": return_consumed_capacity,
            "ReturnItemCollectionMetrics": return_item_collection_metrics
        }
        
        try:
            response = self.dynamodb_client.batch_write_item(**batch_params)
            
            # Check if there are unprocessed items
            unprocessed_items = response.get("UnprocessedItems", {})
            status = "success" if not unprocessed_items else "partial_success"
            
            return {
                "status": status,
                "data": {
                    "UnprocessedItems": unprocessed_items
                },
                "error": None if status == "success" else "Some items were not processed",
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": response.get("ItemCollectionMetrics"),
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_batch_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a batch get operation.
        
        Args:
            params: Parameters for batch get
            
        Returns:
            Operation result with retrieved items
        """
        table_name = params["table_name"]
        batch_items = params["batch_items"]
        consistent_read = params.get("consistent_read", False)
        projection_expression = params.get("projection_expression")
        expression_attribute_names = params.get("expression_attribute_names")
        return_consumed_capacity = params.get("return_consumed_capacity", "NONE")
        
        # Prepare request items
        request_items = {
            table_name: {
                "Keys": [item["Key"] for item in batch_items],
                "ConsistentRead": consistent_read
            }
        }
        
        # Add optional parameters if provided
        if projection_expression:
            request_items[table_name]["ProjectionExpression"] = projection_expression
        if expression_attribute_names:
            request_items[table_name]["ExpressionAttributeNames"] = expression_attribute_names
        
        batch_params = {
            "RequestItems": request_items,
            "ReturnConsumedCapacity": return_consumed_capacity
        }
        
        try:
            response = self.dynamodb_client.batch_get_item(**batch_params)
            
            # Check if there are unprocessed keys
            unprocessed_keys = response.get("UnprocessedKeys", {})
            status = "success" if not unprocessed_keys else "partial_success"
            
            return {
                "status": status,
                "data": {
                    "Responses": response.get("Responses", {}),
                    "UnprocessedKeys": unprocessed_keys
                },
                "error": None if status == "success" else "Some keys were not processed",
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": None,
                "count": len(response.get("Responses", {}).get(table_name, [])),
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
    async def operation_transact_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a transactional write operation.
        
        Args:
            params: Parameters for transactional write
            
        Returns:
            Operation result
        """
        transact_items = params["transact_items"]
        return_consumed_capacity = params.get("return_consumed_capacity", "NONE")
        return_item_collection_metrics = params.get("return_item_collection_metrics", "NONE")
        client_request_token = params.get("client_request_token", str(uuid.uuid4()))
        
        transact_params = {
            "TransactItems": transact_items,
            "ReturnConsumedCapacity": return_consumed_capacity,
            "ReturnItemCollectionMetrics": return_item_collection_metrics,
            "ClientRequestToken": client_request_token
        }
        
        try:
            response = self.dynamodb_client.transact_write_items(**transact_params)
            
            return {
                "status": "success",
                "data": response,
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": response.get("ItemCollectionMetrics"),
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def operation_transact_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a transactional get operation.
        
        Args:
            params: Parameters for transactional get
            
        Returns:
            Operation result with retrieved items
        """
        transact_items = params["transact_items"]
        return_consumed_capacity = params.get("return_consumed_capacity", "NONE")
        
        transact_params = {
            "TransactItems": transact_items,
            "ReturnConsumedCapacity": return_consumed_capacity
        }
        
        try:
            response = self.dynamodb_client.transact_get_items(**transact_params)
            
            return {
                "status": "success",
                "data": {
                    "Responses": response.get("Responses", [])
                },
                "error": None,
                "consumed_capacity": response.get("ConsumedCapacity"),
                "item_collection_metrics": None,
                "count": len(response.get("Responses", [])),
                "scanned_count": None,
                "last_evaluated_key": None
            }
            
        except ClientError as e:
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "consumed_capacity": None,
                "item_collection_metrics": None,
                "count": None,
                "scanned_count": None,
                "last_evaluated_key": None
            }
    
    async def close(self):
        """Close resources used by this node."""
        # No need to close anything for DynamoDB as boto3 manages connections
        pass

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("dynamodb", DynamoDBNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register DynamoDBNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")

# Main test suite for DynamoDBNode
if __name__ == "__main__":
    # Configure logging for testing
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== DynamoDBNode Test Suite ===")
        
        # Create an instance of the DynamoDBNode
        node = DynamoDBNode()
        
        # Use local DynamoDB for testing
        local_params = {
            "endpoint_url": "http://localhost:8000",  # Default local DynamoDB port
            "region_name": "us-east-1",
            "aws_access_key_id": "dummy",
            "aws_secret_access_key": "dummy"
        }
        
        # Test cases
        test_cases = [
            {
                "name": "List Tables",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.LIST_TABLES
                },
                "expected_status": "success"
            },
            {
                "name": "Create Table",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.CREATE_TABLE,
                    "table_name": "TestTable",
                    "key_schema": [
                        {"AttributeName": "id", "KeyType": "HASH"},
                        {"AttributeName": "sort_key", "KeyType": "RANGE"}
                    ],
                    "attribute_definitions": [
                        {"AttributeName": "id", "AttributeType": "S"},
                        {"AttributeName": "sort_key", "AttributeType": "S"}
                    ],
                    "billing_mode": "PAY_PER_REQUEST"
                },
                "expected_status": "success"
            },
            {
                "name": "Describe Table",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.DESCRIBE_TABLE,
                    "table_name": "TestTable"
                },
                "expected_status": "success",
                "validation": lambda result: result["data"]["TableName"] == "TestTable"
            },
            {
                "name": "Put Item",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.PUT_ITEM,
                    "table_name": "TestTable",
                    "item": {
                        "id": {"S": "user1"},
                        "sort_key": {"S": "profile"},
                        "name": {"S": "John Doe"},
                        "email": {"S": "john@example.com"},
                        "age": {"N": "30"}
                    }
                },
                "expected_status": "success"
            },
            {
                "name": "Get Item",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.GET_ITEM,
                    "table_name": "TestTable",
                    "key": {
                        "id": {"S": "user1"},
                        "sort_key": {"S": "profile"}
                    }
                },
                "expected_status": "success",
                "validation": lambda result: result["data"]["name"]["S"] == "John Doe"
            },
            {
                "name": "Update Item",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.UPDATE_ITEM,
                    "table_name": "TestTable",
                    "key": {
                        "id": {"S": "user1"},
                        "sort_key": {"S": "profile"}
                    },
                    "update_expression": "SET #nm = :new_name, age = :new_age",
                    "expression_attribute_names": {
                        "#nm": "name"
                    },
                    "expression_attribute_values": {
                        ":new_name": {"S": "Jane Doe"},
                        ":new_age": {"N": "31"}
                    },
                    "return_values": "ALL_NEW"
                },
                "expected_status": "success",
                "validation": lambda result: result["data"]["name"]["S"] == "Jane Doe"
            },
            {
                "name": "Query Items",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.QUERY,
                    "table_name": "TestTable",
                    "key_condition_expression": "id = :id_val",
                    "expression_attribute_values": {
                        ":id_val": {"S": "user1"}
                    }
                },
                "expected_status": "success",
                "validation": lambda result: result["count"] > 0
            },
            {
                "name": "Scan Items",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.SCAN,
                    "table_name": "TestTable"
                },
                "expected_status": "success",
                "validation": lambda result: result["count"] > 0
            },
            {
                "name": "Delete Item",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.DELETE_ITEM,
                    "table_name": "TestTable",
                    "key": {
                        "id": {"S": "user1"},
                        "sort_key": {"S": "profile"}
                    },
                    "return_values": "ALL_OLD"
                },
                "expected_status": "success",
                "validation": lambda result: result["data"] is not None
            },
            {
                "name": "Delete Table",
                "params": {
                    **local_params,
                    "operation": DynamoDBOperationType.DELETE_TABLE,
                    "table_name": "TestTable"
                },
                "expected_status": "success"
            }
        ]
        
        # Run all test cases
        total_tests = len(test_cases)
        passed_tests = 0
        
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            
            try:
                # Prepare node data
                node_data = {
                    "params": test_case["params"]
                }
                
                # Execute the node
                result = await node.execute(node_data)
                
                # Check if the result status matches expected status
                if result["status"] == test_case["expected_status"]:
                    # Run additional validation if provided
                    if "validation" in test_case:
                        validation_func = test_case["validation"]
                        if validation_func(result):
                            print(f"✅ PASS: {test_case['name']} - Status: {result['status']} - Validation passed")
                            passed_tests += 1
                        else:
                            print(f"❌ FAIL: {test_case['name']} - Validation failed")
                            print(f"Response: {result}")
                    else:
                        print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                        passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        # Additional manual tests for specific scenarios
        print("\n=== Manual Test: Batch Operations ===")
        
        # Create a test table for batch operations
        await node.execute({
            "params": {
                **local_params,
                "operation": DynamoDBOperationType.CREATE_TABLE,
                "table_name": "BatchTestTable",
                "key_schema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ],
                "attribute_definitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "billing_mode": "PAY_PER_REQUEST"
            }
        })
        
        # Test batch write operation
        batch_write_result = await node.execute({
            "params": {
                **local_params,
                "operation": DynamoDBOperationType.BATCH_WRITE,
                "table_name": "BatchTestTable",
                "batch_items": [
                    {
                        "Item": {
                            "id": {"S": "item1"},
                            "data": {"S": "value1"}
                        }
                    },
                    {
                        "Item": {
                            "id": {"S": "item2"},
                            "data": {"S": "value2"}
                        }
                    },
                    {
                        "Item": {
                            "id": {"S": "item3"},
                            "data": {"S": "value3"}
                        }
                    }
                ]
            }
        })
        
        print(f"Batch Write Result: Status={batch_write_result['status']}")
        
        # Test batch get operation
        batch_get_result = await node.execute({
            "params": {
                **local_params,
                "operation": DynamoDBOperationType.BATCH_GET,
                "table_name": "BatchTestTable",
                "batch_items": [
                    {"Key": {"id": {"S": "item1"}}},
                    {"Key": {"id": {"S": "item2"}}},
                    {"Key": {"id": {"S": "item3"}}}
                ]
            }
        })
        
        print(f"Batch Get Result: Status={batch_get_result['status']}, Items Count={batch_get_result['count']}")
        
        # Clean up batch test table
        await node.execute({
            "params": {
                **local_params,
                "operation": DynamoDBOperationType.DELETE_TABLE,
                "table_name": "BatchTestTable"
            }
        })
        
        print("\n=== Additional Test: Error Handling ===")
        
        # Test with non-existent table
        error_result = await node.execute({
            "params": {
                **local_params,
                "operation": DynamoDBOperationType.GET_ITEM,
                "table_name": "NonExistentTable",
                "key": {
                    "id": {"S": "test"}
                }
            }
        })
        
        print(f"Error Handling Test: Status={error_result['status']}, Error={error_result['error']}")
        
        # Try to close the node
        await node.close()
        print("\nAll tests completed!")
    
    asyncio.run(run_tests())
