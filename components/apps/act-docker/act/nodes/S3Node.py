"""
S3 Node - Comprehensive AWS S3 integration for cloud storage operations
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports all major S3 operations including bucket management, object operations,
permissions, encryption, versioning, lifecycle, and advanced features.
"""

import logging
import asyncio
import json
import base64
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import io

try:
    import boto3
    from boto3 import client, resource
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    from botocore.client import Config
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

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

# Configure logging with proper masking
logger = logging.getLogger(__name__)

class S3Operation:
    """All available S3 operations."""
    
    # Bucket Operations
    CREATE_BUCKET = "create_bucket"
    DELETE_BUCKET = "delete_bucket"
    LIST_BUCKETS = "list_buckets"
    HEAD_BUCKET = "head_bucket"
    GET_BUCKET_LOCATION = "get_bucket_location"
    
    # Bucket Configuration
    PUT_BUCKET_POLICY = "put_bucket_policy"
    GET_BUCKET_POLICY = "get_bucket_policy"
    DELETE_BUCKET_POLICY = "delete_bucket_policy"
    PUT_BUCKET_ACL = "put_bucket_acl"
    GET_BUCKET_ACL = "get_bucket_acl"
    PUT_BUCKET_CORS = "put_bucket_cors"
    GET_BUCKET_CORS = "get_bucket_cors"
    DELETE_BUCKET_CORS = "delete_bucket_cors"
    PUT_BUCKET_ENCRYPTION = "put_bucket_encryption"
    GET_BUCKET_ENCRYPTION = "get_bucket_encryption"
    DELETE_BUCKET_ENCRYPTION = "delete_bucket_encryption"
    PUT_BUCKET_VERSIONING = "put_bucket_versioning"
    GET_BUCKET_VERSIONING = "get_bucket_versioning"
    PUT_BUCKET_LIFECYCLE = "put_bucket_lifecycle"
    GET_BUCKET_LIFECYCLE = "get_bucket_lifecycle"
    DELETE_BUCKET_LIFECYCLE = "delete_bucket_lifecycle"
    PUT_BUCKET_NOTIFICATION = "put_bucket_notification"
    GET_BUCKET_NOTIFICATION = "get_bucket_notification"
    PUT_BUCKET_WEBSITE = "put_bucket_website"
    GET_BUCKET_WEBSITE = "get_bucket_website"
    DELETE_BUCKET_WEBSITE = "delete_bucket_website"
    
    # Object Operations
    PUT_OBJECT = "put_object"
    GET_OBJECT = "get_object"
    DELETE_OBJECT = "delete_object"
    DELETE_OBJECTS = "delete_objects"
    COPY_OBJECT = "copy_object"
    HEAD_OBJECT = "head_object"
    LIST_OBJECTS_V2 = "list_objects_v2"
    LIST_OBJECT_VERSIONS = "list_object_versions"
    
    # Object ACL Operations
    PUT_OBJECT_ACL = "put_object_acl"
    GET_OBJECT_ACL = "get_object_acl"
    
    # Object Tagging
    PUT_OBJECT_TAGGING = "put_object_tagging"
    GET_OBJECT_TAGGING = "get_object_tagging"
    DELETE_OBJECT_TAGGING = "delete_object_tagging"
    
    # Multipart Upload Operations
    CREATE_MULTIPART_UPLOAD = "create_multipart_upload"
    UPLOAD_PART = "upload_part"
    COMPLETE_MULTIPART_UPLOAD = "complete_multipart_upload"
    ABORT_MULTIPART_UPLOAD = "abort_multipart_upload"
    LIST_MULTIPART_UPLOADS = "list_multipart_uploads"
    LIST_PARTS = "list_parts"
    UPLOAD_PART_COPY = "upload_part_copy"
    
    # Advanced Operations
    RESTORE_OBJECT = "restore_object"
    SELECT_OBJECT_CONTENT = "select_object_content"
    GENERATE_PRESIGNED_URL = "generate_presigned_url"
    GENERATE_PRESIGNED_POST = "generate_presigned_post"
    
    # File Transfer Operations (Convenience)
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    
    # Batch Operations
    PUT_BUCKET_INTELLIGENT_TIERING = "put_bucket_intelligent_tiering"
    GET_BUCKET_INTELLIGENT_TIERING = "get_bucket_intelligent_tiering"
    DELETE_BUCKET_INTELLIGENT_TIERING = "delete_bucket_intelligent_tiering"
    
    # Public Access Block
    PUT_PUBLIC_ACCESS_BLOCK = "put_public_access_block"
    GET_PUBLIC_ACCESS_BLOCK = "get_public_access_block"
    DELETE_PUBLIC_ACCESS_BLOCK = "delete_public_access_block"
    
    # Object Lock
    PUT_OBJECT_LOCK_CONFIGURATION = "put_object_lock_configuration"
    GET_OBJECT_LOCK_CONFIGURATION = "get_object_lock_configuration"
    PUT_OBJECT_RETENTION = "put_object_retention"
    GET_OBJECT_RETENTION = "get_object_retention"
    PUT_OBJECT_LEGAL_HOLD = "put_object_legal_hold"
    GET_OBJECT_LEGAL_HOLD = "get_object_legal_hold"


class S3ClientWrapper:
    """Unified S3 client wrapper that handles sync/async operations."""
    
    def __init__(self, client):
        self.client = client
        self.is_async = False  # Boto3 is synchronous
    
    async def maybe_await(self, result):
        """Helper to handle both sync and async results."""
        if self.is_async and asyncio.iscoroutine(result):
            return await result
        return result
    
    # Bucket operations
    async def create_bucket(self, bucket_name: str, **kwargs) -> Dict[str, Any]:
        """Create a new S3 bucket."""
        return await self.maybe_await(self.client.create_bucket(Bucket=bucket_name, **kwargs))
    
    async def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Delete an S3 bucket."""
        return await self.maybe_await(self.client.delete_bucket(Bucket=bucket_name))
    
    async def list_buckets(self) -> Dict[str, Any]:
        """List all S3 buckets."""
        return await self.maybe_await(self.client.list_buckets())
    
    async def head_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Check if bucket exists and you have permission to access it."""
        return await self.maybe_await(self.client.head_bucket(Bucket=bucket_name))
    
    async def get_bucket_location(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket location."""
        return await self.maybe_await(self.client.get_bucket_location(Bucket=bucket_name))
    
    # Bucket configuration operations
    async def put_bucket_policy(self, bucket_name: str, policy: str) -> Dict[str, Any]:
        """Apply bucket policy."""
        return await self.maybe_await(self.client.put_bucket_policy(Bucket=bucket_name, Policy=policy))
    
    async def get_bucket_policy(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket policy."""
        return await self.maybe_await(self.client.get_bucket_policy(Bucket=bucket_name))
    
    async def delete_bucket_policy(self, bucket_name: str) -> Dict[str, Any]:
        """Delete bucket policy."""
        return await self.maybe_await(self.client.delete_bucket_policy(Bucket=bucket_name))
    
    async def put_bucket_acl(self, bucket_name: str, acl: str = None, **kwargs) -> Dict[str, Any]:
        """Set bucket ACL."""
        params = {"Bucket": bucket_name}
        if acl:
            params["ACL"] = acl
        params.update(kwargs)
        return await self.maybe_await(self.client.put_bucket_acl(**params))
    
    async def get_bucket_acl(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket ACL."""
        return await self.maybe_await(self.client.get_bucket_acl(Bucket=bucket_name))
    
    async def put_bucket_encryption(self, bucket_name: str, encryption_config: Dict[str, Any]) -> Dict[str, Any]:
        """Set bucket encryption."""
        return await self.maybe_await(self.client.put_bucket_encryption(
            Bucket=bucket_name, 
            ServerSideEncryptionConfiguration=encryption_config
        ))
    
    async def get_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket encryption."""
        return await self.maybe_await(self.client.get_bucket_encryption(Bucket=bucket_name))
    
    async def delete_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Delete bucket encryption."""
        return await self.maybe_await(self.client.delete_bucket_encryption(Bucket=bucket_name))
    
    async def put_bucket_versioning(self, bucket_name: str, versioning_config: Dict[str, Any]) -> Dict[str, Any]:
        """Set bucket versioning."""
        return await self.maybe_await(self.client.put_bucket_versioning(
            Bucket=bucket_name, 
            VersioningConfiguration=versioning_config
        ))
    
    async def get_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket versioning."""
        return await self.maybe_await(self.client.get_bucket_versioning(Bucket=bucket_name))
    
    # Object operations
    async def put_object(self, bucket_name: str, key: str, body: Any = None, **kwargs) -> Dict[str, Any]:
        """Upload object to S3."""
        params = {"Bucket": bucket_name, "Key": key}
        if body is not None:
            params["Body"] = body
        params.update(kwargs)
        return await self.maybe_await(self.client.put_object(**params))
    
    async def get_object(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Download object from S3."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.get_object(**params))
    
    async def delete_object(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Delete object from S3."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.delete_object(**params))
    
    async def delete_objects(self, bucket_name: str, delete_config: Dict[str, Any]) -> Dict[str, Any]:
        """Delete multiple objects from S3."""
        return await self.maybe_await(self.client.delete_objects(
            Bucket=bucket_name, 
            Delete=delete_config
        ))
    
    async def copy_object(self, copy_source: Dict[str, str], bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Copy object within S3."""
        params = {"CopySource": copy_source, "Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.copy_object(**params))
    
    async def head_object(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Get object metadata."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.head_object(**params))
    
    async def list_objects_v2(self, bucket_name: str, **kwargs) -> Dict[str, Any]:
        """List objects in bucket."""
        params = {"Bucket": bucket_name}
        params.update(kwargs)
        return await self.maybe_await(self.client.list_objects_v2(**params))
    
    async def list_object_versions(self, bucket_name: str, **kwargs) -> Dict[str, Any]:
        """List object versions."""
        params = {"Bucket": bucket_name}
        params.update(kwargs)
        return await self.maybe_await(self.client.list_object_versions(**params))
    
    # Object ACL operations
    async def put_object_acl(self, bucket_name: str, key: str, acl: str = None, **kwargs) -> Dict[str, Any]:
        """Set object ACL."""
        params = {"Bucket": bucket_name, "Key": key}
        if acl:
            params["ACL"] = acl
        params.update(kwargs)
        return await self.maybe_await(self.client.put_object_acl(**params))
    
    async def get_object_acl(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Get object ACL."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.get_object_acl(**params))
    
    # Object tagging
    async def put_object_tagging(self, bucket_name: str, key: str, tagging: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Set object tags."""
        params = {"Bucket": bucket_name, "Key": key, "Tagging": tagging}
        params.update(kwargs)
        return await self.maybe_await(self.client.put_object_tagging(**params))
    
    async def get_object_tagging(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Get object tags."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.get_object_tagging(**params))
    
    async def delete_object_tagging(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Delete object tags."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.delete_object_tagging(**params))
    
    # Multipart upload operations
    async def create_multipart_upload(self, bucket_name: str, key: str, **kwargs) -> Dict[str, Any]:
        """Create multipart upload."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.create_multipart_upload(**params))
    
    async def upload_part(self, bucket_name: str, key: str, part_number: int, upload_id: str, body: Any, **kwargs) -> Dict[str, Any]:
        """Upload part for multipart upload."""
        params = {
            "Bucket": bucket_name, 
            "Key": key, 
            "PartNumber": part_number, 
            "UploadId": upload_id, 
            "Body": body
        }
        params.update(kwargs)
        return await self.maybe_await(self.client.upload_part(**params))
    
    async def complete_multipart_upload(self, bucket_name: str, key: str, upload_id: str, parts: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Complete multipart upload."""
        params = {
            "Bucket": bucket_name, 
            "Key": key, 
            "UploadId": upload_id, 
            "MultipartUpload": {"Parts": parts}
        }
        params.update(kwargs)
        return await self.maybe_await(self.client.complete_multipart_upload(**params))
    
    async def abort_multipart_upload(self, bucket_name: str, key: str, upload_id: str, **kwargs) -> Dict[str, Any]:
        """Abort multipart upload."""
        params = {"Bucket": bucket_name, "Key": key, "UploadId": upload_id}
        params.update(kwargs)
        return await self.maybe_await(self.client.abort_multipart_upload(**params))
    
    async def list_multipart_uploads(self, bucket_name: str, **kwargs) -> Dict[str, Any]:
        """List multipart uploads."""
        params = {"Bucket": bucket_name}
        params.update(kwargs)
        return await self.maybe_await(self.client.list_multipart_uploads(**params))
    
    async def list_parts(self, bucket_name: str, key: str, upload_id: str, **kwargs) -> Dict[str, Any]:
        """List parts of multipart upload."""
        params = {"Bucket": bucket_name, "Key": key, "UploadId": upload_id}
        params.update(kwargs)
        return await self.maybe_await(self.client.list_parts(**params))
    
    # Advanced operations
    async def restore_object(self, bucket_name: str, key: str, restore_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Restore object from Glacier."""
        params = {"Bucket": bucket_name, "Key": key, "RestoreRequest": restore_request}
        params.update(kwargs)
        return await self.maybe_await(self.client.restore_object(**params))
    
    async def select_object_content(self, bucket_name: str, key: str, expression: str, input_serialization: Dict[str, Any], output_serialization: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Select content from object using SQL."""
        params = {
            "Bucket": bucket_name, 
            "Key": key, 
            "Expression": expression,
            "InputSerialization": input_serialization,
            "OutputSerialization": output_serialization,
            "ExpressionType": "SQL"
        }
        params.update(kwargs)
        return await self.maybe_await(self.client.select_object_content(**params))
    
    async def generate_presigned_url(self, method: str, bucket_name: str, key: str = None, expires_in: int = 3600, **kwargs) -> str:
        """Generate presigned URL."""
        params = {"Bucket": bucket_name}
        if key:
            params["Key"] = key
        params.update(kwargs)
        return await self.maybe_await(self.client.generate_presigned_url(method, Params=params, ExpiresIn=expires_in))
    
    async def generate_presigned_post(self, bucket_name: str, key: str, expires_in: int = 3600, **kwargs) -> Dict[str, Any]:
        """Generate presigned POST."""
        params = {"Bucket": bucket_name, "Key": key}
        params.update(kwargs)
        return await self.maybe_await(self.client.generate_presigned_post(params, ExpiresIn=expires_in))
    
    # File transfer operations
    async def upload_file(self, filename: str, bucket_name: str, key: str, **kwargs) -> None:
        """Upload file to S3."""
        return await self.maybe_await(self.client.upload_file(filename, bucket_name, key, **kwargs))
    
    async def download_file(self, bucket_name: str, key: str, filename: str, **kwargs) -> None:
        """Download file from S3."""
        return await self.maybe_await(self.client.download_file(bucket_name, key, filename, **kwargs))
    
    # Public access block
    async def put_public_access_block(self, bucket_name: str, public_access_block_config: Dict[str, Any]) -> Dict[str, Any]:
        """Set public access block configuration."""
        return await self.maybe_await(self.client.put_public_access_block(
            Bucket=bucket_name, 
            PublicAccessBlockConfiguration=public_access_block_config
        ))
    
    async def get_public_access_block(self, bucket_name: str) -> Dict[str, Any]:
        """Get public access block configuration."""
        return await self.maybe_await(self.client.get_public_access_block(Bucket=bucket_name))
    
    async def delete_public_access_block(self, bucket_name: str) -> Dict[str, Any]:
        """Delete public access block configuration."""
        return await self.maybe_await(self.client.delete_public_access_block(Bucket=bucket_name))


class OperationMetadata:
    """Metadata for operation validation and parameter requirements."""
    
    def __init__(self, required_params: List[str], optional_params: List[str] = None, 
                 handler: Optional[Callable] = None):
        self.required_params = required_params
        self.optional_params = optional_params or []
        self.handler = handler


class S3Node(BaseNode):
    """
    Comprehensive S3 integration node supporting all major cloud storage operations.
    Handles bucket management, object operations, permissions, encryption, versioning,
    lifecycle, and advanced S3 features.
    """
    
    # Operation metadata table - programmatic validation generation
    OPERATION_METADATA = {
        # Bucket operations
        S3Operation.CREATE_BUCKET: OperationMetadata(["bucket_name"]),
        S3Operation.DELETE_BUCKET: OperationMetadata(["bucket_name"]),
        S3Operation.LIST_BUCKETS: OperationMetadata([]),
        S3Operation.HEAD_BUCKET: OperationMetadata(["bucket_name"]),
        S3Operation.GET_BUCKET_LOCATION: OperationMetadata(["bucket_name"]),
        
        # Bucket configuration
        S3Operation.PUT_BUCKET_POLICY: OperationMetadata(["bucket_name", "policy"]),
        S3Operation.GET_BUCKET_POLICY: OperationMetadata(["bucket_name"]),
        S3Operation.DELETE_BUCKET_POLICY: OperationMetadata(["bucket_name"]),
        S3Operation.PUT_BUCKET_ACL: OperationMetadata(["bucket_name"]),
        S3Operation.GET_BUCKET_ACL: OperationMetadata(["bucket_name"]),
        S3Operation.PUT_BUCKET_ENCRYPTION: OperationMetadata(["bucket_name", "encryption_config"]),
        S3Operation.GET_BUCKET_ENCRYPTION: OperationMetadata(["bucket_name"]),
        S3Operation.DELETE_BUCKET_ENCRYPTION: OperationMetadata(["bucket_name"]),
        S3Operation.PUT_BUCKET_VERSIONING: OperationMetadata(["bucket_name", "versioning_config"]),
        S3Operation.GET_BUCKET_VERSIONING: OperationMetadata(["bucket_name"]),
        
        # Object operations
        S3Operation.PUT_OBJECT: OperationMetadata(["bucket_name", "key"]),
        S3Operation.GET_OBJECT: OperationMetadata(["bucket_name", "key"]),
        S3Operation.DELETE_OBJECT: OperationMetadata(["bucket_name", "key"]),
        S3Operation.DELETE_OBJECTS: OperationMetadata(["bucket_name", "delete_config"]),
        S3Operation.COPY_OBJECT: OperationMetadata(["copy_source", "bucket_name", "key"]),
        S3Operation.HEAD_OBJECT: OperationMetadata(["bucket_name", "key"]),
        S3Operation.LIST_OBJECTS_V2: OperationMetadata(["bucket_name"]),
        S3Operation.LIST_OBJECT_VERSIONS: OperationMetadata(["bucket_name"]),
        
        # Object ACL
        S3Operation.PUT_OBJECT_ACL: OperationMetadata(["bucket_name", "key"]),
        S3Operation.GET_OBJECT_ACL: OperationMetadata(["bucket_name", "key"]),
        
        # Object tagging
        S3Operation.PUT_OBJECT_TAGGING: OperationMetadata(["bucket_name", "key", "tagging"]),
        S3Operation.GET_OBJECT_TAGGING: OperationMetadata(["bucket_name", "key"]),
        S3Operation.DELETE_OBJECT_TAGGING: OperationMetadata(["bucket_name", "key"]),
        
        # Multipart upload
        S3Operation.CREATE_MULTIPART_UPLOAD: OperationMetadata(["bucket_name", "key"]),
        S3Operation.UPLOAD_PART: OperationMetadata(["bucket_name", "key", "part_number", "upload_id", "body"]),
        S3Operation.COMPLETE_MULTIPART_UPLOAD: OperationMetadata(["bucket_name", "key", "upload_id", "parts"]),
        S3Operation.ABORT_MULTIPART_UPLOAD: OperationMetadata(["bucket_name", "key", "upload_id"]),
        S3Operation.LIST_MULTIPART_UPLOADS: OperationMetadata(["bucket_name"]),
        S3Operation.LIST_PARTS: OperationMetadata(["bucket_name", "key", "upload_id"]),
        
        # Advanced operations
        S3Operation.RESTORE_OBJECT: OperationMetadata(["bucket_name", "key", "restore_request"]),
        S3Operation.SELECT_OBJECT_CONTENT: OperationMetadata(["bucket_name", "key", "expression", "input_serialization", "output_serialization"]),
        S3Operation.GENERATE_PRESIGNED_URL: OperationMetadata(["method", "bucket_name"]),
        S3Operation.GENERATE_PRESIGNED_POST: OperationMetadata(["bucket_name", "key"]),
        
        # File transfer
        S3Operation.UPLOAD_FILE: OperationMetadata(["filename", "bucket_name", "key"]),
        S3Operation.DOWNLOAD_FILE: OperationMetadata(["bucket_name", "key", "filename"]),
        
        # Public access block
        S3Operation.PUT_PUBLIC_ACCESS_BLOCK: OperationMetadata(["bucket_name", "public_access_block_config"]),
        S3Operation.GET_PUBLIC_ACCESS_BLOCK: OperationMetadata(["bucket_name"]),
        S3Operation.DELETE_PUBLIC_ACCESS_BLOCK: OperationMetadata(["bucket_name"]),
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create dispatch map for operations
        self.operation_dispatch = {
            # Bucket operations
            S3Operation.CREATE_BUCKET: self._handle_create_bucket,
            S3Operation.DELETE_BUCKET: self._handle_delete_bucket,
            S3Operation.LIST_BUCKETS: self._handle_list_buckets,
            S3Operation.HEAD_BUCKET: self._handle_head_bucket,
            S3Operation.GET_BUCKET_LOCATION: self._handle_get_bucket_location,
            
            # Bucket configuration
            S3Operation.PUT_BUCKET_POLICY: self._handle_put_bucket_policy,
            S3Operation.GET_BUCKET_POLICY: self._handle_get_bucket_policy,
            S3Operation.DELETE_BUCKET_POLICY: self._handle_delete_bucket_policy,
            S3Operation.PUT_BUCKET_ACL: self._handle_put_bucket_acl,
            S3Operation.GET_BUCKET_ACL: self._handle_get_bucket_acl,
            S3Operation.PUT_BUCKET_ENCRYPTION: self._handle_put_bucket_encryption,
            S3Operation.GET_BUCKET_ENCRYPTION: self._handle_get_bucket_encryption,
            S3Operation.DELETE_BUCKET_ENCRYPTION: self._handle_delete_bucket_encryption,
            S3Operation.PUT_BUCKET_VERSIONING: self._handle_put_bucket_versioning,
            S3Operation.GET_BUCKET_VERSIONING: self._handle_get_bucket_versioning,
            
            # Object operations
            S3Operation.PUT_OBJECT: self._handle_put_object,
            S3Operation.GET_OBJECT: self._handle_get_object,
            S3Operation.DELETE_OBJECT: self._handle_delete_object,
            S3Operation.DELETE_OBJECTS: self._handle_delete_objects,
            S3Operation.COPY_OBJECT: self._handle_copy_object,
            S3Operation.HEAD_OBJECT: self._handle_head_object,
            S3Operation.LIST_OBJECTS_V2: self._handle_list_objects_v2,
            S3Operation.LIST_OBJECT_VERSIONS: self._handle_list_object_versions,
            
            # Object ACL
            S3Operation.PUT_OBJECT_ACL: self._handle_put_object_acl,
            S3Operation.GET_OBJECT_ACL: self._handle_get_object_acl,
            
            # Object tagging
            S3Operation.PUT_OBJECT_TAGGING: self._handle_put_object_tagging,
            S3Operation.GET_OBJECT_TAGGING: self._handle_get_object_tagging,
            S3Operation.DELETE_OBJECT_TAGGING: self._handle_delete_object_tagging,
            
            # Multipart upload
            S3Operation.CREATE_MULTIPART_UPLOAD: self._handle_create_multipart_upload,
            S3Operation.UPLOAD_PART: self._handle_upload_part,
            S3Operation.COMPLETE_MULTIPART_UPLOAD: self._handle_complete_multipart_upload,
            S3Operation.ABORT_MULTIPART_UPLOAD: self._handle_abort_multipart_upload,
            S3Operation.LIST_MULTIPART_UPLOADS: self._handle_list_multipart_uploads,
            S3Operation.LIST_PARTS: self._handle_list_parts,
            
            # Advanced operations
            S3Operation.RESTORE_OBJECT: self._handle_restore_object,
            S3Operation.SELECT_OBJECT_CONTENT: self._handle_select_object_content,
            S3Operation.GENERATE_PRESIGNED_URL: self._handle_generate_presigned_url,
            S3Operation.GENERATE_PRESIGNED_POST: self._handle_generate_presigned_post,
            
            # File transfer
            S3Operation.UPLOAD_FILE: self._handle_upload_file,
            S3Operation.DOWNLOAD_FILE: self._handle_download_file,
            
            # Public access block
            S3Operation.PUT_PUBLIC_ACCESS_BLOCK: self._handle_put_public_access_block,
            S3Operation.GET_PUBLIC_ACCESS_BLOCK: self._handle_get_public_access_block,
            S3Operation.DELETE_PUBLIC_ACCESS_BLOCK: self._handle_delete_public_access_block,
        }
    
    def get_schema(self) -> NodeSchema:
        """Generate schema with all parameters from operation metadata."""
        # Common parameters for all operations
        base_params = [
            ("operation", NodeParameterType.STRING, "S3 operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("aws_access_key_id", NodeParameterType.STRING, "AWS Access Key ID", False),
            ("aws_secret_access_key", NodeParameterType.STRING, "AWS Secret Access Key", False),
            ("aws_session_token", NodeParameterType.STRING, "AWS Session Token (for temporary credentials)", False),
            ("region_name", NodeParameterType.STRING, "AWS region name (e.g., us-east-1)", False),
            ("endpoint_url", NodeParameterType.STRING, "Custom S3 endpoint URL", False),
            ("use_ssl", NodeParameterType.BOOLEAN, "Use SSL for connections", False, None, True),
        ]
        
        # Operation-specific parameters
        operation_params = [
            # Bucket parameters
            ("bucket_name", NodeParameterType.STRING, "S3 bucket name", False),
            ("location_constraint", NodeParameterType.STRING, "Bucket location constraint", False),
            
            # Object parameters
            ("key", NodeParameterType.STRING, "S3 object key", False),
            ("body", NodeParameterType.STRING, "Object body/content (string or base64)", False),
            ("content_type", NodeParameterType.STRING, "Content type of the object", False),
            ("content_encoding", NodeParameterType.STRING, "Content encoding of the object", False),
            ("metadata", NodeParameterType.OBJECT, "Object metadata (key-value pairs)", False),
            
            # File transfer parameters
            ("filename", NodeParameterType.STRING, "Local filename for upload/download", False),
            
            # Copying parameters
            ("copy_source", NodeParameterType.OBJECT, "Copy source object (bucket and key)", False),
            
            # Versioning parameters
            ("version_id", NodeParameterType.STRING, "Object version ID", False),
            
            # Encryption parameters
            ("server_side_encryption", NodeParameterType.STRING, "Server-side encryption", False, ["AES256", "aws:kms"]),
            ("sse_kms_key_id", NodeParameterType.STRING, "KMS key ID for encryption", False),
            ("sse_customer_algorithm", NodeParameterType.STRING, "Customer encryption algorithm", False),
            ("sse_customer_key", NodeParameterType.STRING, "Customer encryption key", False),
            ("sse_customer_key_md5", NodeParameterType.STRING, "Customer encryption key MD5", False),
            
            # ACL parameters
            ("acl", NodeParameterType.STRING, "Canned ACL", False, ["private", "public-read", "public-read-write", "authenticated-read", "aws-exec-read", "bucket-owner-read", "bucket-owner-full-control"]),
            ("grant_full_control", NodeParameterType.STRING, "Grant full control", False),
            ("grant_read", NodeParameterType.STRING, "Grant read access", False),
            ("grant_read_acp", NodeParameterType.STRING, "Grant read ACP", False),
            ("grant_write", NodeParameterType.STRING, "Grant write access", False),
            ("grant_write_acp", NodeParameterType.STRING, "Grant write ACP", False),
            
            # Policy parameters
            ("policy", NodeParameterType.STRING, "Bucket policy (JSON string)", False),
            
            # Configuration parameters
            ("encryption_config", NodeParameterType.OBJECT, "Encryption configuration", False),
            ("versioning_config", NodeParameterType.OBJECT, "Versioning configuration", False),
            ("cors_config", NodeParameterType.OBJECT, "CORS configuration", False),
            ("lifecycle_config", NodeParameterType.OBJECT, "Lifecycle configuration", False),
            ("public_access_block_config", NodeParameterType.OBJECT, "Public access block configuration", False),
            
            # Tagging parameters
            ("tagging", NodeParameterType.OBJECT, "Object tagging", False),
            
            # Multipart upload parameters
            ("upload_id", NodeParameterType.STRING, "Multipart upload ID", False),
            ("part_number", NodeParameterType.NUMBER, "Part number for multipart upload", False),
            ("parts", NodeParameterType.ARRAY, "List of parts for multipart upload completion", False),
            
            # Restore parameters
            ("restore_request", NodeParameterType.OBJECT, "Restore request configuration", False),
            
            # Select content parameters
            ("expression", NodeParameterType.STRING, "SQL expression for select content", False),
            ("input_serialization", NodeParameterType.OBJECT, "Input serialization for select content", False),
            ("output_serialization", NodeParameterType.OBJECT, "Output serialization for select content", False),
            
            # Presigned URL parameters
            ("method", NodeParameterType.STRING, "HTTP method for presigned URL", False, ["GET", "PUT", "POST", "DELETE"]),
            ("expires_in", NodeParameterType.NUMBER, "Expiration time in seconds for presigned URL", False, None, 3600),
            
            # Listing parameters
            ("prefix", NodeParameterType.STRING, "Object key prefix for listing", False),
            ("delimiter", NodeParameterType.STRING, "Delimiter for listing", False),
            ("max_keys", NodeParameterType.NUMBER, "Maximum number of keys to return", False),
            ("continuation_token", NodeParameterType.STRING, "Continuation token for pagination", False),
            ("start_after", NodeParameterType.STRING, "Start listing after this key", False),
            
            # Delete parameters
            ("delete_config", NodeParameterType.OBJECT, "Delete configuration for multiple objects", False),
            
            # Storage class parameters
            ("storage_class", NodeParameterType.STRING, "Storage class", False, ["STANDARD", "REDUCED_REDUNDANCY", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING", "GLACIER", "DEEP_ARCHIVE", "OUTPOSTS", "GLACIER_IR"]),
            
            # Request payer parameters
            ("request_payer", NodeParameterType.STRING, "Request payer", False, ["Requester"]),
            
            # Conditional parameters
            ("if_match", NodeParameterType.STRING, "If-Match condition", False),
            ("if_none_match", NodeParameterType.STRING, "If-None-Match condition", False),
            ("if_modified_since", NodeParameterType.STRING, "If-Modified-Since condition", False),
            ("if_unmodified_since", NodeParameterType.STRING, "If-Unmodified-Since condition", False),
            
            # Range parameters
            ("range", NodeParameterType.STRING, "Byte range for partial object retrieval", False),
        ]
        
        # Build parameters dict
        parameters = {}
        for param_def in base_params + operation_params:
            name = param_def[0]
            param_type = param_def[1]
            description = param_def[2]
            required = param_def[3]
            enum = param_def[4] if len(param_def) > 4 else None
            default = param_def[5] if len(param_def) > 5 else None
            
            param_kwargs = {
                "name": name,
                "type": param_type,
                "description": description,
                "required": required
            }
            
            if enum:
                param_kwargs["enum"] = enum
            if default is not None:
                param_kwargs["default"] = default
            
            parameters[name] = NodeParameter(**param_kwargs)
        
        return NodeSchema(
            node_type="s3",
            version="1.0.0",
            description="Comprehensive AWS S3 integration supporting all major cloud storage operations including bucket management, object operations, permissions, encryption, versioning, lifecycle, and advanced features",
            parameters=list(parameters.values()),
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "start_time": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER,
                "inputs": NodeParameterType.OBJECT,
                "raw_result": NodeParameterType.ANY,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "aws_error": NodeParameterType.STRING,
                "connection_info": NodeParameterType.OBJECT,
                "bucket_name": NodeParameterType.STRING,
                "key": NodeParameterType.STRING,
                "version_id": NodeParameterType.STRING,
                "etag": NodeParameterType.STRING,
                "upload_id": NodeParameterType.STRING,
                "location": NodeParameterType.STRING,
                "presigned_url": NodeParameterType.STRING,
                "content_length": NodeParameterType.NUMBER,
                "last_modified": NodeParameterType.STRING,
                "storage_class": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate S3-specific parameters using operation metadata."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Basic validation
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata.required_params:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Additional validation for specific operations
        if operation in [S3Operation.PUT_BUCKET_POLICY, S3Operation.PUT_BUCKET_ENCRYPTION, S3Operation.PUT_BUCKET_VERSIONING]:
            if operation == S3Operation.PUT_BUCKET_POLICY and "policy" in params:
                try:
                    # Validate that policy is valid JSON
                    json.loads(params["policy"])
                except json.JSONDecodeError:
                    raise NodeValidationError("Policy must be valid JSON")
        
        if operation in [S3Operation.PUT_OBJECT] and "body" in params:
            body = params["body"]
            if isinstance(body, str):
                # Check if it's base64 encoded
                try:
                    base64.b64decode(body)
                except Exception:
                    # It's regular text, which is fine
                    pass
        
        if operation in [S3Operation.COPY_OBJECT] and "copy_source" in params:
            copy_source = params["copy_source"]
            if not isinstance(copy_source, dict) or "Bucket" not in copy_source or "Key" not in copy_source:
                raise NodeValidationError("copy_source must be a dict with 'Bucket' and 'Key' fields")
        
        return node_data
    
    @asynccontextmanager
    async def _get_s3_client(self, params: Dict[str, Any]):
        """Context manager for S3 client with proper connection lifecycle."""
        aws_access_key_id = params.get("aws_access_key_id")
        aws_secret_access_key = params.get("aws_secret_access_key")
        aws_session_token = params.get("aws_session_token")
        region_name = params.get("region_name")
        endpoint_url = params.get("endpoint_url")
        use_ssl = params.get("use_ssl", True)
        
        # Build client configuration
        config_kwargs = {}
        if use_ssl is False:
            config_kwargs["use_ssl"] = False
        
        config = Config(**config_kwargs) if config_kwargs else None
        
        # Build session parameters
        session_kwargs = {}
        if aws_access_key_id:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if aws_session_token:
            session_kwargs["aws_session_token"] = aws_session_token
        if region_name:
            session_kwargs["region_name"] = region_name
        
        client = None
        try:
            # Create session if we have explicit credentials
            if session_kwargs:
                session = boto3.Session(**session_kwargs)
                client = session.client("s3", endpoint_url=endpoint_url, config=config)
            else:
                # Use default credential chain
                client = boto3.client("s3", region_name=region_name, endpoint_url=endpoint_url, config=config)
            
            s3_client = S3ClientWrapper(client)
            yield s3_client
        finally:
            # boto3 client doesn't need explicit closing
            pass
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked_data = data.copy()
        
        # Mask sensitive fields
        sensitive_fields = ["aws_secret_access_key", "aws_session_token", "sse_customer_key", "policy"]
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = "***MASKED***"
        
        return masked_data
    
    def _create_standard_response(self, operation: str, start_time: datetime, 
                                 params: Dict[str, Any], result: Any, 
                                 error: Optional[str] = None, 
                                 aws_error: Optional[str] = None) -> Dict[str, Any]:
        """Create standardized response shape."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "status": "success" if error is None else "error",
            "operation": operation,
            "start_time": start_time.isoformat(),
            "execution_time": execution_time,
            "inputs": self._mask_sensitive_data(params),
            "raw_result": result,
            "result": result,
        }
        
        if error:
            response["error"] = error
        
        if aws_error:
            response["aws_error"] = aws_error
        
        # Add connection info (without sensitive data)
        response["connection_info"] = {
            "region_name": params.get("region_name"),
            "endpoint_url": params.get("endpoint_url"),
            "use_ssl": params.get("use_ssl", True),
        }
        
        return response
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the S3 operation using dispatch map."""
        start_time = datetime.now()
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Get handler from dispatch map
        handler = self.operation_dispatch.get(operation)
        if not handler:
            return self._create_standard_response(
                operation, start_time, params, None,
                error=f"Unknown operation: {operation}"
            )
        
        try:
            # Create S3 client with proper connection lifecycle
            async with self._get_s3_client(params) as s3_client:
                # Call the handler
                result = await handler(s3_client, params)
                
                return self._create_standard_response(
                    operation, start_time, params, result
                )
        
        except (BotoCoreError, ClientError, NoCredentialsError) as e:
            error_type = type(e).__name__
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), aws_error=error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in operation {operation}: {e}")
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), aws_error=type(e).__name__
            )
    
    # Bucket operation handlers
    async def _handle_create_bucket(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_BUCKET operation."""
        bucket_kwargs = {}
        if params.get("location_constraint"):
            bucket_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": params["location_constraint"]}
        if params.get("acl"):
            bucket_kwargs["ACL"] = params["acl"]
        
        return await s3_client.create_bucket(params["bucket_name"], **bucket_kwargs)
    
    async def _handle_delete_bucket(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_BUCKET operation."""
        return await s3_client.delete_bucket(params["bucket_name"])
    
    async def _handle_list_buckets(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LIST_BUCKETS operation."""
        return await s3_client.list_buckets()
    
    async def _handle_head_bucket(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HEAD_BUCKET operation."""
        return await s3_client.head_bucket(params["bucket_name"])
    
    async def _handle_get_bucket_location(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_BUCKET_LOCATION operation."""
        return await s3_client.get_bucket_location(params["bucket_name"])
    
    # Bucket configuration handlers
    async def _handle_put_bucket_policy(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_BUCKET_POLICY operation."""
        return await s3_client.put_bucket_policy(params["bucket_name"], params["policy"])
    
    async def _handle_get_bucket_policy(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_BUCKET_POLICY operation."""
        return await s3_client.get_bucket_policy(params["bucket_name"])
    
    async def _handle_delete_bucket_policy(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_BUCKET_POLICY operation."""
        return await s3_client.delete_bucket_policy(params["bucket_name"])
    
    async def _handle_put_bucket_acl(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_BUCKET_ACL operation."""
        acl_kwargs = {}
        if params.get("acl"):
            acl_kwargs["acl"] = params["acl"]
        for field in ["grant_full_control", "grant_read", "grant_read_acp", "grant_write", "grant_write_acp"]:
            if params.get(field):
                acl_kwargs[field.replace("_", "")] = params[field]
        
        return await s3_client.put_bucket_acl(params["bucket_name"], **acl_kwargs)
    
    async def _handle_get_bucket_acl(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_BUCKET_ACL operation."""
        return await s3_client.get_bucket_acl(params["bucket_name"])
    
    async def _handle_put_bucket_encryption(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_BUCKET_ENCRYPTION operation."""
        return await s3_client.put_bucket_encryption(params["bucket_name"], params["encryption_config"])
    
    async def _handle_get_bucket_encryption(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_BUCKET_ENCRYPTION operation."""
        return await s3_client.get_bucket_encryption(params["bucket_name"])
    
    async def _handle_delete_bucket_encryption(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_BUCKET_ENCRYPTION operation."""
        return await s3_client.delete_bucket_encryption(params["bucket_name"])
    
    async def _handle_put_bucket_versioning(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_BUCKET_VERSIONING operation."""
        return await s3_client.put_bucket_versioning(params["bucket_name"], params["versioning_config"])
    
    async def _handle_get_bucket_versioning(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_BUCKET_VERSIONING operation."""
        return await s3_client.get_bucket_versioning(params["bucket_name"])
    
    # Object operation handlers
    async def _handle_put_object(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_OBJECT operation."""
        object_kwargs = {}
        
        # Handle body
        if params.get("body"):
            body = params["body"]
            if isinstance(body, str):
                try:
                    # Try to decode as base64
                    decoded_body = base64.b64decode(body)
                    object_kwargs["body"] = decoded_body
                except Exception:
                    # Use as regular text
                    object_kwargs["body"] = body
            else:
                object_kwargs["body"] = body
        
        # Add optional parameters
        optional_fields = [
            "content_type", "content_encoding", "metadata", "storage_class",
            "server_side_encryption", "sse_kms_key_id", "sse_customer_algorithm",
            "sse_customer_key", "sse_customer_key_md5", "acl"
        ]
        
        for field in optional_fields:
            if params.get(field):
                boto_field = field.replace("_", "").title().replace("Sse", "SSE").replace("Acl", "ACL")
                if field == "content_type":
                    boto_field = "ContentType"
                elif field == "content_encoding":
                    boto_field = "ContentEncoding"
                elif field == "metadata":
                    boto_field = "Metadata"
                elif field == "storage_class":
                    boto_field = "StorageClass"
                elif field == "server_side_encryption":
                    boto_field = "ServerSideEncryption"
                elif field == "sse_kms_key_id":
                    boto_field = "SSEKMSKeyId"
                elif field == "sse_customer_algorithm":
                    boto_field = "SSECustomerAlgorithm"
                elif field == "sse_customer_key":
                    boto_field = "SSECustomerKey"
                elif field == "sse_customer_key_md5":
                    boto_field = "SSECustomerKeyMD5"
                elif field == "acl":
                    boto_field = "ACL"
                
                object_kwargs[boto_field] = params[field]
        
        return await s3_client.put_object(params["bucket_name"], params["key"], **object_kwargs)
    
    async def _handle_get_object(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_OBJECT operation."""
        object_kwargs = {}
        
        optional_fields = ["version_id", "range", "if_match", "if_none_match", "if_modified_since", "if_unmodified_since"]
        for field in optional_fields:
            if params.get(field):
                boto_field = field.replace("_", "").title()
                if field == "version_id":
                    boto_field = "VersionId"
                elif field == "range":
                    boto_field = "Range"
                elif field == "if_match":
                    boto_field = "IfMatch"
                elif field == "if_none_match":
                    boto_field = "IfNoneMatch"
                elif field == "if_modified_since":
                    boto_field = "IfModifiedSince"
                elif field == "if_unmodified_since":
                    boto_field = "IfUnmodifiedSince"
                
                object_kwargs[boto_field] = params[field]
        
        return await s3_client.get_object(params["bucket_name"], params["key"], **object_kwargs)
    
    async def _handle_delete_object(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_OBJECT operation."""
        delete_kwargs = {}
        if params.get("version_id"):
            delete_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.delete_object(params["bucket_name"], params["key"], **delete_kwargs)
    
    async def _handle_delete_objects(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_OBJECTS operation."""
        return await s3_client.delete_objects(params["bucket_name"], params["delete_config"])
    
    async def _handle_copy_object(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COPY_OBJECT operation."""
        copy_kwargs = {}
        optional_fields = ["metadata", "storage_class", "server_side_encryption", "acl"]
        for field in optional_fields:
            if params.get(field):
                copy_kwargs[field] = params[field]
        
        return await s3_client.copy_object(params["copy_source"], params["bucket_name"], params["key"], **copy_kwargs)
    
    async def _handle_head_object(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HEAD_OBJECT operation."""
        head_kwargs = {}
        if params.get("version_id"):
            head_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.head_object(params["bucket_name"], params["key"], **head_kwargs)
    
    async def _handle_list_objects_v2(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LIST_OBJECTS_V2 operation."""
        list_kwargs = {}
        optional_fields = ["prefix", "delimiter", "max_keys", "continuation_token", "start_after"]
        for field in optional_fields:
            if params.get(field):
                boto_field = field.replace("_", "").title()
                if field == "max_keys":
                    boto_field = "MaxKeys"
                elif field == "continuation_token":
                    boto_field = "ContinuationToken"
                elif field == "start_after":
                    boto_field = "StartAfter"
                
                list_kwargs[boto_field] = params[field]
        
        return await s3_client.list_objects_v2(params["bucket_name"], **list_kwargs)
    
    async def _handle_list_object_versions(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LIST_OBJECT_VERSIONS operation."""
        list_kwargs = {}
        optional_fields = ["prefix", "delimiter", "max_keys"]
        for field in optional_fields:
            if params.get(field):
                list_kwargs[field.title()] = params[field]
        
        return await s3_client.list_object_versions(params["bucket_name"], **list_kwargs)
    
    # Object ACL handlers
    async def _handle_put_object_acl(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_OBJECT_ACL operation."""
        acl_kwargs = {}
        if params.get("acl"):
            acl_kwargs["acl"] = params["acl"]
        if params.get("version_id"):
            acl_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.put_object_acl(params["bucket_name"], params["key"], **acl_kwargs)
    
    async def _handle_get_object_acl(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_OBJECT_ACL operation."""
        acl_kwargs = {}
        if params.get("version_id"):
            acl_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.get_object_acl(params["bucket_name"], params["key"], **acl_kwargs)
    
    # Object tagging handlers
    async def _handle_put_object_tagging(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_OBJECT_TAGGING operation."""
        tagging_kwargs = {}
        if params.get("version_id"):
            tagging_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.put_object_tagging(params["bucket_name"], params["key"], params["tagging"], **tagging_kwargs)
    
    async def _handle_get_object_tagging(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_OBJECT_TAGGING operation."""
        tagging_kwargs = {}
        if params.get("version_id"):
            tagging_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.get_object_tagging(params["bucket_name"], params["key"], **tagging_kwargs)
    
    async def _handle_delete_object_tagging(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_OBJECT_TAGGING operation."""
        tagging_kwargs = {}
        if params.get("version_id"):
            tagging_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.delete_object_tagging(params["bucket_name"], params["key"], **tagging_kwargs)
    
    # Multipart upload handlers
    async def _handle_create_multipart_upload(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_MULTIPART_UPLOAD operation."""
        upload_kwargs = {}
        optional_fields = ["content_type", "metadata", "storage_class", "server_side_encryption", "acl"]
        for field in optional_fields:
            if params.get(field):
                upload_kwargs[field] = params[field]
        
        return await s3_client.create_multipart_upload(params["bucket_name"], params["key"], **upload_kwargs)
    
    async def _handle_upload_part(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UPLOAD_PART operation."""
        body = params["body"]
        if isinstance(body, str):
            try:
                body = base64.b64decode(body)
            except Exception:
                body = body.encode('utf-8')
        
        return await s3_client.upload_part(
            params["bucket_name"], 
            params["key"], 
            params["part_number"], 
            params["upload_id"], 
            body
        )
    
    async def _handle_complete_multipart_upload(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COMPLETE_MULTIPART_UPLOAD operation."""
        return await s3_client.complete_multipart_upload(
            params["bucket_name"], 
            params["key"], 
            params["upload_id"], 
            params["parts"]
        )
    
    async def _handle_abort_multipart_upload(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ABORT_MULTIPART_UPLOAD operation."""
        return await s3_client.abort_multipart_upload(params["bucket_name"], params["key"], params["upload_id"])
    
    async def _handle_list_multipart_uploads(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LIST_MULTIPART_UPLOADS operation."""
        list_kwargs = {}
        optional_fields = ["prefix", "delimiter", "max_uploads"]
        for field in optional_fields:
            if params.get(field):
                list_kwargs[field] = params[field]
        
        return await s3_client.list_multipart_uploads(params["bucket_name"], **list_kwargs)
    
    async def _handle_list_parts(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LIST_PARTS operation."""
        list_kwargs = {}
        if params.get("max_parts"):
            list_kwargs["max_parts"] = params["max_parts"]
        
        return await s3_client.list_parts(params["bucket_name"], params["key"], params["upload_id"], **list_kwargs)
    
    # Advanced operation handlers
    async def _handle_restore_object(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RESTORE_OBJECT operation."""
        restore_kwargs = {}
        if params.get("version_id"):
            restore_kwargs["VersionId"] = params["version_id"]
        
        return await s3_client.restore_object(params["bucket_name"], params["key"], params["restore_request"], **restore_kwargs)
    
    async def _handle_select_object_content(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SELECT_OBJECT_CONTENT operation."""
        return await s3_client.select_object_content(
            params["bucket_name"], 
            params["key"], 
            params["expression"],
            params["input_serialization"],
            params["output_serialization"]
        )
    
    async def _handle_generate_presigned_url(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> str:
        """Handle GENERATE_PRESIGNED_URL operation."""
        expires_in = params.get("expires_in", 3600)
        key = params.get("key")
        
        return await s3_client.generate_presigned_url(
            params["method"], 
            params["bucket_name"], 
            key=key,
            expires_in=expires_in
        )
    
    async def _handle_generate_presigned_post(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GENERATE_PRESIGNED_POST operation."""
        expires_in = params.get("expires_in", 3600)
        
        return await s3_client.generate_presigned_post(params["bucket_name"], params["key"], expires_in=expires_in)
    
    # File transfer handlers
    async def _handle_upload_file(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> None:
        """Handle UPLOAD_FILE operation."""
        upload_kwargs = {}
        optional_fields = ["extra_args", "callback", "config"]
        for field in optional_fields:
            if params.get(field):
                upload_kwargs[field] = params[field]
        
        return await s3_client.upload_file(params["filename"], params["bucket_name"], params["key"], **upload_kwargs)
    
    async def _handle_download_file(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> None:
        """Handle DOWNLOAD_FILE operation."""
        download_kwargs = {}
        optional_fields = ["extra_args", "callback", "config"]
        for field in optional_fields:
            if params.get(field):
                download_kwargs[field] = params[field]
        
        return await s3_client.download_file(params["bucket_name"], params["key"], params["filename"], **download_kwargs)
    
    # Public access block handlers
    async def _handle_put_public_access_block(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_PUBLIC_ACCESS_BLOCK operation."""
        return await s3_client.put_public_access_block(params["bucket_name"], params["public_access_block_config"])
    
    async def _handle_get_public_access_block(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_PUBLIC_ACCESS_BLOCK operation."""
        return await s3_client.get_public_access_block(params["bucket_name"])
    
    async def _handle_delete_public_access_block(self, s3_client: S3ClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DELETE_PUBLIC_ACCESS_BLOCK operation."""
        return await s3_client.delete_public_access_block(params["bucket_name"])