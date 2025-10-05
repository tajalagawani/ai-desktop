import asyncio
import aiohttp
import json
import boto3
from typing import Dict, Any, List, Optional
from base_node import NodeSchema, NodeParameter, NodeParameterType, BaseNode

class AwsNode(BaseNode):
    def __init__(self):
        schema = NodeSchema(
            name="AWS",
            version="1.0.0",
            description="Amazon Web Services integration supporting multiple AWS services",
            auth_params=[
                NodeParameter(
                    name="access_key_id",
                    param_type=NodeParameterType.STRING,
                    required=True,
                    description="AWS Access Key ID"
                ),
                NodeParameter(
                    name="secret_access_key",
                    param_type=NodeParameterType.STRING,
                    required=True,
                    description="AWS Secret Access Key"
                ),
                NodeParameter(
                    name="region",
                    param_type=NodeParameterType.SELECT,
                    required=True,
                    description="AWS Region",
                    options=[
                        {"label": "US East (N. Virginia)", "value": "us-east-1"},
                        {"label": "US East (Ohio)", "value": "us-east-2"},
                        {"label": "US West (N. California)", "value": "us-west-1"},
                        {"label": "US West (Oregon)", "value": "us-west-2"},
                        {"label": "Africa (Cape Town)", "value": "af-south-1"},
                        {"label": "Asia Pacific (Hong Kong)", "value": "ap-east-1"},
                        {"label": "Asia Pacific (Mumbai)", "value": "ap-south-1"},
                        {"label": "Asia Pacific (Seoul)", "value": "ap-northeast-2"},
                        {"label": "Asia Pacific (Singapore)", "value": "ap-southeast-1"},
                        {"label": "Asia Pacific (Sydney)", "value": "ap-southeast-2"},
                        {"label": "Asia Pacific (Tokyo)", "value": "ap-northeast-1"},
                        {"label": "Canada (Central)", "value": "ca-central-1"},
                        {"label": "Europe (Frankfurt)", "value": "eu-central-1"},
                        {"label": "Europe (Ireland)", "value": "eu-west-1"},
                        {"label": "Europe (London)", "value": "eu-west-2"},
                        {"label": "Europe (Paris)", "value": "eu-west-3"},
                        {"label": "Europe (Stockholm)", "value": "eu-north-1"},
                        {"label": "Middle East (Bahrain)", "value": "me-south-1"},
                        {"label": "South America (São Paulo)", "value": "sa-east-1"}
                    ]
                )
            ],
            parameters=[
                NodeParameter(
                    name="service",
                    param_type=NodeParameterType.SELECT,
                    required=True,
                    description="AWS Service to use",
                    options=[
                        {"label": "S3 - Simple Storage Service", "value": "s3"},
                        {"label": "EC2 - Elastic Compute Cloud", "value": "ec2"},
                        {"label": "Lambda - Serverless Functions", "value": "lambda"},
                        {"label": "DynamoDB - NoSQL Database", "value": "dynamodb"},
                        {"label": "SQS - Simple Queue Service", "value": "sqs"},
                        {"label": "SNS - Simple Notification Service", "value": "sns"},
                        {"label": "CloudWatch - Monitoring", "value": "cloudwatch"},
                        {"label": "IAM - Identity Access Management", "value": "iam"},
                        {"label": "SES - Simple Email Service", "value": "ses"},
                        {"label": "RDS - Relational Database Service", "value": "rds"},
                        {"label": "CloudFormation - Infrastructure as Code", "value": "cloudformation"},
                        {"label": "ECS - Elastic Container Service", "value": "ecs"},
                        {"label": "Route 53 - DNS Service", "value": "route53"},
                        {"label": "Secrets Manager", "value": "secretsmanager"},
                        {"label": "SSM - Systems Manager", "value": "ssm"}
                    ]
                ),
                NodeParameter(
                    name="operation",
                    param_type=NodeParameterType.SELECT,
                    required=True,
                    description="Operation to perform",
                    options=[
                        # S3 Operations
                        {"label": "S3: List Buckets", "value": "s3_list_buckets"},
                        {"label": "S3: Create Bucket", "value": "s3_create_bucket"},
                        {"label": "S3: Delete Bucket", "value": "s3_delete_bucket"},
                        {"label": "S3: List Objects", "value": "s3_list_objects"},
                        {"label": "S3: Upload Object", "value": "s3_upload_object"},
                        {"label": "S3: Download Object", "value": "s3_download_object"},
                        {"label": "S3: Delete Object", "value": "s3_delete_object"},
                        {"label": "S3: Copy Object", "value": "s3_copy_object"},
                        {"label": "S3: Get Object Metadata", "value": "s3_get_object_metadata"},
                        # EC2 Operations
                        {"label": "EC2: List Instances", "value": "ec2_list_instances"},
                        {"label": "EC2: Start Instance", "value": "ec2_start_instance"},
                        {"label": "EC2: Stop Instance", "value": "ec2_stop_instance"},
                        {"label": "EC2: Reboot Instance", "value": "ec2_reboot_instance"},
                        {"label": "EC2: Terminate Instance", "value": "ec2_terminate_instance"},
                        {"label": "EC2: Create Instance", "value": "ec2_create_instance"},
                        {"label": "EC2: List Images", "value": "ec2_list_images"},
                        {"label": "EC2: List Security Groups", "value": "ec2_list_security_groups"},
                        # Lambda Operations
                        {"label": "Lambda: List Functions", "value": "lambda_list_functions"},
                        {"label": "Lambda: Invoke Function", "value": "lambda_invoke_function"},
                        {"label": "Lambda: Create Function", "value": "lambda_create_function"},
                        {"label": "Lambda: Update Function", "value": "lambda_update_function"},
                        {"label": "Lambda: Delete Function", "value": "lambda_delete_function"},
                        # DynamoDB Operations
                        {"label": "DynamoDB: List Tables", "value": "dynamodb_list_tables"},
                        {"label": "DynamoDB: Create Table", "value": "dynamodb_create_table"},
                        {"label": "DynamoDB: Delete Table", "value": "dynamodb_delete_table"},
                        {"label": "DynamoDB: Get Item", "value": "dynamodb_get_item"},
                        {"label": "DynamoDB: Put Item", "value": "dynamodb_put_item"},
                        {"label": "DynamoDB: Update Item", "value": "dynamodb_update_item"},
                        {"label": "DynamoDB: Delete Item", "value": "dynamodb_delete_item"},
                        {"label": "DynamoDB: Query", "value": "dynamodb_query"},
                        {"label": "DynamoDB: Scan", "value": "dynamodb_scan"},
                        # SQS Operations
                        {"label": "SQS: List Queues", "value": "sqs_list_queues"},
                        {"label": "SQS: Create Queue", "value": "sqs_create_queue"},
                        {"label": "SQS: Delete Queue", "value": "sqs_delete_queue"},
                        {"label": "SQS: Send Message", "value": "sqs_send_message"},
                        {"label": "SQS: Receive Messages", "value": "sqs_receive_messages"},
                        {"label": "SQS: Delete Message", "value": "sqs_delete_message"},
                        # SNS Operations
                        {"label": "SNS: List Topics", "value": "sns_list_topics"},
                        {"label": "SNS: Create Topic", "value": "sns_create_topic"},
                        {"label": "SNS: Delete Topic", "value": "sns_delete_topic"},
                        {"label": "SNS: Publish Message", "value": "sns_publish_message"},
                        {"label": "SNS: Subscribe", "value": "sns_subscribe"},
                        {"label": "SNS: Unsubscribe", "value": "sns_unsubscribe"},
                        # CloudWatch Operations
                        {"label": "CloudWatch: List Metrics", "value": "cloudwatch_list_metrics"},
                        {"label": "CloudWatch: Get Metric Statistics", "value": "cloudwatch_get_metric_statistics"},
                        {"label": "CloudWatch: Put Metric Data", "value": "cloudwatch_put_metric_data"},
                        {"label": "CloudWatch: List Alarms", "value": "cloudwatch_list_alarms"},
                        {"label": "CloudWatch: Create Alarm", "value": "cloudwatch_create_alarm"},
                        # IAM Operations
                        {"label": "IAM: List Users", "value": "iam_list_users"},
                        {"label": "IAM: Create User", "value": "iam_create_user"},
                        {"label": "IAM: Delete User", "value": "iam_delete_user"},
                        {"label": "IAM: List Roles", "value": "iam_list_roles"},
                        {"label": "IAM: List Policies", "value": "iam_list_policies"},
                        # SES Operations
                        {"label": "SES: Send Email", "value": "ses_send_email"},
                        {"label": "SES: List Identities", "value": "ses_list_identities"},
                        {"label": "SES: Verify Email", "value": "ses_verify_email"}
                    ]
                ),
                # Common Parameters
                NodeParameter(
                    name="bucket_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="S3 bucket name"
                ),
                NodeParameter(
                    name="object_key",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="S3 object key/path"
                ),
                NodeParameter(
                    name="content",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Content for upload operations"
                ),
                NodeParameter(
                    name="instance_id",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="EC2 instance ID"
                ),
                NodeParameter(
                    name="function_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Lambda function name"
                ),
                NodeParameter(
                    name="table_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="DynamoDB table name"
                ),
                NodeParameter(
                    name="queue_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="SQS queue name"
                ),
                NodeParameter(
                    name="queue_url",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="SQS queue URL"
                ),
                NodeParameter(
                    name="topic_arn",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="SNS topic ARN"
                ),
                NodeParameter(
                    name="message",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Message content"
                ),
                NodeParameter(
                    name="subject",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Email subject or message subject"
                ),
                NodeParameter(
                    name="email_to",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Email recipient"
                ),
                NodeParameter(
                    name="email_from",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Email sender"
                ),
                NodeParameter(
                    name="payload",
                    param_type=NodeParameterType.JSON,
                    required=False,
                    description="JSON payload for various operations"
                ),
                NodeParameter(
                    name="parameters",
                    param_type=NodeParameterType.JSON,
                    required=False,
                    description="Additional parameters as JSON"
                ),
                NodeParameter(
                    name="max_results",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Maximum number of results to return",
                    default_value=100
                ),
                NodeParameter(
                    name="prefix",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Prefix filter for listing operations"
                )
            ],
            icon_path="https://cdn.jsdelivr.net/gh/n8n-io/n8n/packages/nodes-base/nodes/Aws/aws.svg"
        )
        super().__init__(schema)

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        access_key_id = params.get("access_key_id")
        secret_access_key = params.get("secret_access_key")
        region = params.get("region")
        service = params.get("service")
        operation = params.get("operation")
        
        if not all([access_key_id, secret_access_key, region]):
            raise ValueError("AWS credentials and region are required")
        
        # Configure boto3 session
        session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        
        # Route to appropriate service handler
        if service == "s3" or operation.startswith("s3_"):
            return await self._handle_s3_operations(session, operation, params)
        elif service == "ec2" or operation.startswith("ec2_"):
            return await self._handle_ec2_operations(session, operation, params)
        elif service == "lambda" or operation.startswith("lambda_"):
            return await self._handle_lambda_operations(session, operation, params)
        elif service == "dynamodb" or operation.startswith("dynamodb_"):
            return await self._handle_dynamodb_operations(session, operation, params)
        elif service == "sqs" or operation.startswith("sqs_"):
            return await self._handle_sqs_operations(session, operation, params)
        elif service == "sns" or operation.startswith("sns_"):
            return await self._handle_sns_operations(session, operation, params)
        elif service == "cloudwatch" or operation.startswith("cloudwatch_"):
            return await self._handle_cloudwatch_operations(session, operation, params)
        elif service == "iam" or operation.startswith("iam_"):
            return await self._handle_iam_operations(session, operation, params)
        elif service == "ses" or operation.startswith("ses_"):
            return await self._handle_ses_operations(session, operation, params)
        else:
            raise ValueError(f"Unsupported service: {service}")

    async def _handle_s3_operations(self, session, operation, params):
        s3_client = session.client('s3')
        
        try:
            if operation == "s3_list_buckets":
                response = s3_client.list_buckets()
                return {"buckets": response.get('Buckets', [])}
                
            elif operation == "s3_create_bucket":
                bucket_name = params.get("bucket_name")
                if not bucket_name:
                    raise ValueError("Bucket name is required")
                    
                create_config = {}
                if session.region_name != 'us-east-1':
                    create_config['LocationConstraint'] = session.region_name
                    
                response = s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration=create_config
                )
                return {"bucket_created": bucket_name, "location": response.get('Location')}
                
            elif operation == "s3_delete_bucket":
                bucket_name = params.get("bucket_name")
                if not bucket_name:
                    raise ValueError("Bucket name is required")
                    
                s3_client.delete_bucket(Bucket=bucket_name)
                return {"success": True, "message": f"Bucket {bucket_name} deleted"}
                
            elif operation == "s3_list_objects":
                bucket_name = params.get("bucket_name")
                if not bucket_name:
                    raise ValueError("Bucket name is required")
                    
                prefix = params.get("prefix", "")
                max_results = params.get("max_results", 100)
                
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    MaxKeys=max_results
                )
                return {
                    "objects": response.get('Contents', []),
                    "total_count": response.get('KeyCount', 0)
                }
                
            elif operation == "s3_upload_object":
                bucket_name = params.get("bucket_name")
                object_key = params.get("object_key")
                content = params.get("content")
                
                if not all([bucket_name, object_key, content]):
                    raise ValueError("Bucket name, object key, and content are required")
                    
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=content.encode('utf-8') if isinstance(content, str) else content
                )
                return {"success": True, "message": f"Object {object_key} uploaded to {bucket_name}"}
                
            elif operation == "s3_download_object":
                bucket_name = params.get("bucket_name")
                object_key = params.get("object_key")
                
                if not all([bucket_name, object_key]):
                    raise ValueError("Bucket name and object key are required")
                    
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                content = response['Body'].read()
                
                return {
                    "content": content.decode('utf-8') if isinstance(content, bytes) else content,
                    "metadata": response.get('Metadata', {}),
                    "content_type": response.get('ContentType')
                }
                
            elif operation == "s3_delete_object":
                bucket_name = params.get("bucket_name")
                object_key = params.get("object_key")
                
                if not all([bucket_name, object_key]):
                    raise ValueError("Bucket name and object key are required")
                    
                s3_client.delete_object(Bucket=bucket_name, Key=object_key)
                return {"success": True, "message": f"Object {object_key} deleted from {bucket_name}"}
                
            elif operation == "s3_copy_object":
                source_bucket = params.get("source_bucket")
                source_key = params.get("source_key")
                dest_bucket = params.get("bucket_name")
                dest_key = params.get("object_key")
                
                if not all([source_bucket, source_key, dest_bucket, dest_key]):
                    raise ValueError("Source and destination bucket/key are required")
                    
                copy_source = {'Bucket': source_bucket, 'Key': source_key}
                s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=dest_bucket,
                    Key=dest_key
                )
                return {"success": True, "message": f"Object copied from {source_bucket}/{source_key} to {dest_bucket}/{dest_key}"}
                
            elif operation == "s3_get_object_metadata":
                bucket_name = params.get("bucket_name")
                object_key = params.get("object_key")
                
                if not all([bucket_name, object_key]):
                    raise ValueError("Bucket name and object key are required")
                    
                response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
                return {
                    "metadata": response.get('Metadata', {}),
                    "content_type": response.get('ContentType'),
                    "content_length": response.get('ContentLength'),
                    "last_modified": response.get('LastModified').isoformat() if response.get('LastModified') else None
                }
                
        except Exception as e:
            raise Exception(f"S3 operation failed: {str(e)}")

    async def _handle_ec2_operations(self, session, operation, params):
        ec2_client = session.client('ec2')
        
        try:
            if operation == "ec2_list_instances":
                response = ec2_client.describe_instances()
                instances = []
                for reservation in response.get('Reservations', []):
                    instances.extend(reservation.get('Instances', []))
                return {"instances": instances}
                
            elif operation == "ec2_start_instance":
                instance_id = params.get("instance_id")
                if not instance_id:
                    raise ValueError("Instance ID is required")
                    
                response = ec2_client.start_instances(InstanceIds=[instance_id])
                return {"starting_instances": response.get('StartingInstances', [])}
                
            elif operation == "ec2_stop_instance":
                instance_id = params.get("instance_id")
                if not instance_id:
                    raise ValueError("Instance ID is required")
                    
                response = ec2_client.stop_instances(InstanceIds=[instance_id])
                return {"stopping_instances": response.get('StoppingInstances', [])}
                
            elif operation == "ec2_reboot_instance":
                instance_id = params.get("instance_id")
                if not instance_id:
                    raise ValueError("Instance ID is required")
                    
                ec2_client.reboot_instances(InstanceIds=[instance_id])
                return {"success": True, "message": f"Instance {instance_id} rebooted"}
                
            elif operation == "ec2_terminate_instance":
                instance_id = params.get("instance_id")
                if not instance_id:
                    raise ValueError("Instance ID is required")
                    
                response = ec2_client.terminate_instances(InstanceIds=[instance_id])
                return {"terminating_instances": response.get('TerminatingInstances', [])}
                
            elif operation == "ec2_create_instance":
                parameters = params.get("parameters", {})
                if not parameters.get("ImageId"):
                    raise ValueError("ImageId is required in parameters")
                    
                response = ec2_client.run_instances(**parameters)
                return {"instances": response.get('Instances', [])}
                
            elif operation == "ec2_list_images":
                response = ec2_client.describe_images(Owners=['self'])
                return {"images": response.get('Images', [])}
                
            elif operation == "ec2_list_security_groups":
                response = ec2_client.describe_security_groups()
                return {"security_groups": response.get('SecurityGroups', [])}
                
        except Exception as e:
            raise Exception(f"EC2 operation failed: {str(e)}")

    async def _handle_lambda_operations(self, session, operation, params):
        lambda_client = session.client('lambda')
        
        try:
            if operation == "lambda_list_functions":
                response = lambda_client.list_functions()
                return {"functions": response.get('Functions', [])}
                
            elif operation == "lambda_invoke_function":
                function_name = params.get("function_name")
                payload = params.get("payload", {})
                
                if not function_name:
                    raise ValueError("Function name is required")
                    
                response = lambda_client.invoke(
                    FunctionName=function_name,
                    Payload=json.dumps(payload)
                )
                
                response_payload = response['Payload'].read()
                return {
                    "status_code": response.get('StatusCode'),
                    "payload": json.loads(response_payload) if response_payload else None
                }
                
            elif operation == "lambda_create_function":
                parameters = params.get("parameters", {})
                if not parameters.get("FunctionName"):
                    raise ValueError("FunctionName is required in parameters")
                    
                response = lambda_client.create_function(**parameters)
                return {"function": response}
                
            elif operation == "lambda_update_function":
                function_name = params.get("function_name")
                parameters = params.get("parameters", {})
                
                if not function_name:
                    raise ValueError("Function name is required")
                    
                response = lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    **parameters
                )
                return {"function": response}
                
            elif operation == "lambda_delete_function":
                function_name = params.get("function_name")
                if not function_name:
                    raise ValueError("Function name is required")
                    
                lambda_client.delete_function(FunctionName=function_name)
                return {"success": True, "message": f"Function {function_name} deleted"}
                
        except Exception as e:
            raise Exception(f"Lambda operation failed: {str(e)}")

    async def _handle_dynamodb_operations(self, session, operation, params):
        dynamodb_client = session.client('dynamodb')
        
        try:
            if operation == "dynamodb_list_tables":
                response = dynamodb_client.list_tables()
                return {"tables": response.get('TableNames', [])}
                
            elif operation == "dynamodb_create_table":
                parameters = params.get("parameters", {})
                if not parameters.get("TableName"):
                    raise ValueError("TableName is required in parameters")
                    
                response = dynamodb_client.create_table(**parameters)
                return {"table": response.get('TableDescription')}
                
            elif operation == "dynamodb_delete_table":
                table_name = params.get("table_name")
                if not table_name:
                    raise ValueError("Table name is required")
                    
                response = dynamodb_client.delete_table(TableName=table_name)
                return {"table": response.get('TableDescription')}
                
            elif operation == "dynamodb_get_item":
                table_name = params.get("table_name")
                key = params.get("payload", {})
                
                if not all([table_name, key]):
                    raise ValueError("Table name and key are required")
                    
                response = dynamodb_client.get_item(
                    TableName=table_name,
                    Key=key
                )
                return {"item": response.get('Item')}
                
            elif operation == "dynamodb_put_item":
                table_name = params.get("table_name")
                item = params.get("payload", {})
                
                if not all([table_name, item]):
                    raise ValueError("Table name and item are required")
                    
                response = dynamodb_client.put_item(
                    TableName=table_name,
                    Item=item
                )
                return {"success": True, "attributes": response.get('Attributes')}
                
            elif operation == "dynamodb_update_item":
                table_name = params.get("table_name")
                parameters = params.get("parameters", {})
                
                if not table_name:
                    raise ValueError("Table name is required")
                    
                response = dynamodb_client.update_item(
                    TableName=table_name,
                    **parameters
                )
                return {"attributes": response.get('Attributes')}
                
            elif operation == "dynamodb_delete_item":
                table_name = params.get("table_name")
                key = params.get("payload", {})
                
                if not all([table_name, key]):
                    raise ValueError("Table name and key are required")
                    
                response = dynamodb_client.delete_item(
                    TableName=table_name,
                    Key=key
                )
                return {"success": True, "attributes": response.get('Attributes')}
                
            elif operation == "dynamodb_query":
                table_name = params.get("table_name")
                parameters = params.get("parameters", {})
                
                if not table_name:
                    raise ValueError("Table name is required")
                    
                response = dynamodb_client.query(
                    TableName=table_name,
                    **parameters
                )
                return {
                    "items": response.get('Items', []),
                    "count": response.get('Count', 0)
                }
                
            elif operation == "dynamodb_scan":
                table_name = params.get("table_name")
                parameters = params.get("parameters", {})
                
                if not table_name:
                    raise ValueError("Table name is required")
                    
                response = dynamodb_client.scan(
                    TableName=table_name,
                    **parameters
                )
                return {
                    "items": response.get('Items', []),
                    "count": response.get('Count', 0)
                }
                
        except Exception as e:
            raise Exception(f"DynamoDB operation failed: {str(e)}")

    async def _handle_sqs_operations(self, session, operation, params):
        sqs_client = session.client('sqs')
        
        try:
            if operation == "sqs_list_queues":
                response = sqs_client.list_queues()
                return {"queues": response.get('QueueUrls', [])}
                
            elif operation == "sqs_create_queue":
                queue_name = params.get("queue_name")
                if not queue_name:
                    raise ValueError("Queue name is required")
                    
                response = sqs_client.create_queue(QueueName=queue_name)
                return {"queue_url": response.get('QueueUrl')}
                
            elif operation == "sqs_delete_queue":
                queue_url = params.get("queue_url")
                if not queue_url:
                    raise ValueError("Queue URL is required")
                    
                sqs_client.delete_queue(QueueUrl=queue_url)
                return {"success": True, "message": "Queue deleted"}
                
            elif operation == "sqs_send_message":
                queue_url = params.get("queue_url")
                message = params.get("message")
                
                if not all([queue_url, message]):
                    raise ValueError("Queue URL and message are required")
                    
                response = sqs_client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message
                )
                return {"message_id": response.get('MessageId')}
                
            elif operation == "sqs_receive_messages":
                queue_url = params.get("queue_url")
                max_results = params.get("max_results", 10)
                
                if not queue_url:
                    raise ValueError("Queue URL is required")
                    
                response = sqs_client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=min(max_results, 10)
                )
                return {"messages": response.get('Messages', [])}
                
            elif operation == "sqs_delete_message":
                queue_url = params.get("queue_url")
                receipt_handle = params.get("receipt_handle")
                
                if not all([queue_url, receipt_handle]):
                    raise ValueError("Queue URL and receipt handle are required")
                    
                sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )
                return {"success": True, "message": "Message deleted"}
                
        except Exception as e:
            raise Exception(f"SQS operation failed: {str(e)}")

    async def _handle_sns_operations(self, session, operation, params):
        sns_client = session.client('sns')
        
        try:
            if operation == "sns_list_topics":
                response = sns_client.list_topics()
                return {"topics": response.get('Topics', [])}
                
            elif operation == "sns_create_topic":
                topic_name = params.get("topic_name")
                if not topic_name:
                    raise ValueError("Topic name is required")
                    
                response = sns_client.create_topic(Name=topic_name)
                return {"topic_arn": response.get('TopicArn')}
                
            elif operation == "sns_delete_topic":
                topic_arn = params.get("topic_arn")
                if not topic_arn:
                    raise ValueError("Topic ARN is required")
                    
                sns_client.delete_topic(TopicArn=topic_arn)
                return {"success": True, "message": "Topic deleted"}
                
            elif operation == "sns_publish_message":
                topic_arn = params.get("topic_arn")
                message = params.get("message")
                subject = params.get("subject")
                
                if not all([topic_arn, message]):
                    raise ValueError("Topic ARN and message are required")
                    
                publish_params = {
                    "TopicArn": topic_arn,
                    "Message": message
                }
                if subject:
                    publish_params["Subject"] = subject
                    
                response = sns_client.publish(**publish_params)
                return {"message_id": response.get('MessageId')}
                
            elif operation == "sns_subscribe":
                topic_arn = params.get("topic_arn")
                protocol = params.get("protocol", "email")
                endpoint = params.get("endpoint")
                
                if not all([topic_arn, endpoint]):
                    raise ValueError("Topic ARN and endpoint are required")
                    
                response = sns_client.subscribe(
                    TopicArn=topic_arn,
                    Protocol=protocol,
                    Endpoint=endpoint
                )
                return {"subscription_arn": response.get('SubscriptionArn')}
                
            elif operation == "sns_unsubscribe":
                subscription_arn = params.get("subscription_arn")
                if not subscription_arn:
                    raise ValueError("Subscription ARN is required")
                    
                sns_client.unsubscribe(SubscriptionArn=subscription_arn)
                return {"success": True, "message": "Unsubscribed"}
                
        except Exception as e:
            raise Exception(f"SNS operation failed: {str(e)}")

    async def _handle_cloudwatch_operations(self, session, operation, params):
        cloudwatch_client = session.client('cloudwatch')
        
        try:
            if operation == "cloudwatch_list_metrics":
                namespace = params.get("namespace")
                list_params = {}
                if namespace:
                    list_params["Namespace"] = namespace
                    
                response = cloudwatch_client.list_metrics(**list_params)
                return {"metrics": response.get('Metrics', [])}
                
            elif operation == "cloudwatch_get_metric_statistics":
                parameters = params.get("parameters", {})
                if not all(k in parameters for k in ["Namespace", "MetricName", "StartTime", "EndTime", "Period", "Statistics"]):
                    raise ValueError("Required parameters: Namespace, MetricName, StartTime, EndTime, Period, Statistics")
                    
                response = cloudwatch_client.get_metric_statistics(**parameters)
                return {"datapoints": response.get('Datapoints', [])}
                
            elif operation == "cloudwatch_put_metric_data":
                namespace = params.get("namespace")
                metric_data = params.get("payload", [])
                
                if not all([namespace, metric_data]):
                    raise ValueError("Namespace and metric data are required")
                    
                cloudwatch_client.put_metric_data(
                    Namespace=namespace,
                    MetricData=metric_data
                )
                return {"success": True, "message": "Metric data sent"}
                
            elif operation == "cloudwatch_list_alarms":
                response = cloudwatch_client.describe_alarms()
                return {"alarms": response.get('MetricAlarms', [])}
                
            elif operation == "cloudwatch_create_alarm":
                parameters = params.get("parameters", {})
                if not parameters.get("AlarmName"):
                    raise ValueError("AlarmName is required in parameters")
                    
                cloudwatch_client.put_metric_alarm(**parameters)
                return {"success": True, "message": "Alarm created"}
                
        except Exception as e:
            raise Exception(f"CloudWatch operation failed: {str(e)}")

    async def _handle_iam_operations(self, session, operation, params):
        iam_client = session.client('iam')
        
        try:
            if operation == "iam_list_users":
                response = iam_client.list_users()
                return {"users": response.get('Users', [])}
                
            elif operation == "iam_create_user":
                user_name = params.get("user_name")
                if not user_name:
                    raise ValueError("User name is required")
                    
                response = iam_client.create_user(UserName=user_name)
                return {"user": response.get('User')}
                
            elif operation == "iam_delete_user":
                user_name = params.get("user_name")
                if not user_name:
                    raise ValueError("User name is required")
                    
                iam_client.delete_user(UserName=user_name)
                return {"success": True, "message": f"User {user_name} deleted"}
                
            elif operation == "iam_list_roles":
                response = iam_client.list_roles()
                return {"roles": response.get('Roles', [])}
                
            elif operation == "iam_list_policies":
                response = iam_client.list_policies(Scope='Local')
                return {"policies": response.get('Policies', [])}
                
        except Exception as e:
            raise Exception(f"IAM operation failed: {str(e)}")

    async def _handle_ses_operations(self, session, operation, params):
        ses_client = session.client('ses')
        
        try:
            if operation == "ses_send_email":
                email_from = params.get("email_from")
                email_to = params.get("email_to")
                subject = params.get("subject")
                message = params.get("message")
                
                if not all([email_from, email_to, subject, message]):
                    raise ValueError("From, To, Subject, and Message are required")
                    
                response = ses_client.send_email(
                    Source=email_from,
                    Destination={'ToAddresses': [email_to]},
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {'Text': {'Data': message}}
                    }
                )
                return {"message_id": response.get('MessageId')}
                
            elif operation == "ses_list_identities":
                response = ses_client.list_identities()
                return {"identities": response.get('Identities', [])}
                
            elif operation == "ses_verify_email":
                email = params.get("email_to")
                if not email:
                    raise ValueError("Email address is required")
                    
                ses_client.verify_email_identity(EmailAddress=email)
                return {"success": True, "message": f"Verification email sent to {email}"}
                
        except Exception as e:
            raise Exception(f"SES operation failed: {str(e)}")