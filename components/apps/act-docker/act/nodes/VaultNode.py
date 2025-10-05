"""
HashiCorp Vault Node - Comprehensive integration with HashiCorp Vault API
Provides access to all Vault operations including secrets management, authentication, policies, and encryption services.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from urllib.parse import urlencode

# Import HTTP client for API calls
import aiohttp
import certifi

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .base_node import (
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

class VaultOperation:
    """Operations available on HashiCorp Vault API."""
    
    # Authentication Operations
    GET_TOKEN = "get_token"
    RENEW_TOKEN = "renew_token"
    REVOKE_TOKEN = "revoke_token"
    LIST_AUTH_METHODS = "list_auth_methods"
    ENABLE_AUTH_METHOD = "enable_auth_method"
    DISABLE_AUTH_METHOD = "disable_auth_method"
    
    # KV Secrets Operations
    READ_SECRET = "read_secret"
    WRITE_SECRET = "write_secret"
    DELETE_SECRET = "delete_secret"
    LIST_SECRETS = "list_secrets"
    READ_SECRET_METADATA = "read_secret_metadata"
    DESTROY_SECRET_VERSION = "destroy_secret_version"
    UNDELETE_SECRET_VERSION = "undelete_secret_version"
    PATCH_SECRET = "patch_secret"
    
    # Database Secrets Operations
    CONFIGURE_DATABASE = "configure_database"
    CREATE_DATABASE_ROLE = "create_database_role"
    GENERATE_DATABASE_CREDENTIALS = "generate_database_credentials"
    ROTATE_ROOT_CREDENTIALS = "rotate_root_credentials"
    ROTATE_STATIC_CREDENTIALS = "rotate_static_credentials"
    LIST_DATABASE_CONNECTIONS = "list_database_connections"
    LIST_DATABASE_ROLES = "list_database_roles"
    
    # Transit Encryption Operations
    CREATE_ENCRYPTION_KEY = "create_encryption_key"
    ENCRYPT_DATA = "encrypt_data"
    DECRYPT_DATA = "decrypt_data"
    SIGN_DATA = "sign_data"
    VERIFY_SIGNATURE = "verify_signature"
    GENERATE_HASH = "generate_hash"
    GENERATE_HMAC = "generate_hmac"
    GENERATE_RANDOM = "generate_random"
    ROTATE_ENCRYPTION_KEY = "rotate_encryption_key"
    LIST_ENCRYPTION_KEYS = "list_encryption_keys"
    
    # PKI Operations
    GENERATE_ROOT_CA = "generate_root_ca"
    GENERATE_INTERMEDIATE_CA = "generate_intermediate_ca"
    GENERATE_CERTIFICATE = "generate_certificate"
    REVOKE_CERTIFICATE = "revoke_certificate"
    SIGN_CSR = "sign_csr"
    LIST_CERTIFICATES = "list_certificates"
    READ_CA_CERTIFICATE = "read_ca_certificate"
    READ_CRL = "read_crl"
    
    # AWS Secrets Operations
    CONFIGURE_AWS_ROOT = "configure_aws_root"
    CREATE_AWS_ROLE = "create_aws_role"
    GENERATE_AWS_CREDENTIALS = "generate_aws_credentials"
    ROTATE_AWS_ROOT = "rotate_aws_root"
    LIST_AWS_ROLES = "list_aws_roles"
    
    # Policy Operations
    CREATE_POLICY = "create_policy"
    READ_POLICY = "read_policy"
    UPDATE_POLICY = "update_policy"
    DELETE_POLICY = "delete_policy"
    LIST_POLICIES = "list_policies"
    
    # System Operations
    GET_SEAL_STATUS = "get_seal_status"
    UNSEAL_VAULT = "unseal_vault"
    SEAL_VAULT = "seal_vault"
    GET_HEALTH = "get_health"
    LIST_MOUNTS = "list_mounts"
    ENABLE_SECRETS_ENGINE = "enable_secrets_engine"
    DISABLE_SECRETS_ENGINE = "disable_secrets_engine"
    TUNE_MOUNT = "tune_mount"
    LIST_LEASES = "list_leases"
    RENEW_LEASE = "renew_lease"
    REVOKE_LEASE = "revoke_lease"
    
    # Audit Operations
    LIST_AUDIT_DEVICES = "list_audit_devices"
    ENABLE_AUDIT_DEVICE = "enable_audit_device"
    DISABLE_AUDIT_DEVICE = "disable_audit_device"

class VaultNode(BaseNode):
    """
    Node for interacting with HashiCorp Vault API.
    Provides comprehensive functionality for secrets management, authentication, encryption, and PKI operations.
    """
    
    BASE_URL = "http://127.0.0.1:8200/v1"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Vault node."""
        return NodeSchema(
            node_type="vault",
            version="1.0.0",
            description="Comprehensive integration with HashiCorp Vault API for secrets management, authentication, encryption, and PKI operations",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Vault API",
                    required=True,
                    enum=[
                        VaultOperation.GET_TOKEN,
                        VaultOperation.RENEW_TOKEN,
                        VaultOperation.REVOKE_TOKEN,
                        VaultOperation.LIST_AUTH_METHODS,
                        VaultOperation.ENABLE_AUTH_METHOD,
                        VaultOperation.DISABLE_AUTH_METHOD,
                        VaultOperation.READ_SECRET,
                        VaultOperation.WRITE_SECRET,
                        VaultOperation.DELETE_SECRET,
                        VaultOperation.LIST_SECRETS,
                        VaultOperation.READ_SECRET_METADATA,
                        VaultOperation.DESTROY_SECRET_VERSION,
                        VaultOperation.UNDELETE_SECRET_VERSION,
                        VaultOperation.PATCH_SECRET,
                        VaultOperation.CONFIGURE_DATABASE,
                        VaultOperation.CREATE_DATABASE_ROLE,
                        VaultOperation.GENERATE_DATABASE_CREDENTIALS,
                        VaultOperation.ROTATE_ROOT_CREDENTIALS,
                        VaultOperation.ROTATE_STATIC_CREDENTIALS,
                        VaultOperation.LIST_DATABASE_CONNECTIONS,
                        VaultOperation.LIST_DATABASE_ROLES,
                        VaultOperation.CREATE_ENCRYPTION_KEY,
                        VaultOperation.ENCRYPT_DATA,
                        VaultOperation.DECRYPT_DATA,
                        VaultOperation.SIGN_DATA,
                        VaultOperation.VERIFY_SIGNATURE,
                        VaultOperation.GENERATE_HASH,
                        VaultOperation.GENERATE_HMAC,
                        VaultOperation.GENERATE_RANDOM,
                        VaultOperation.ROTATE_ENCRYPTION_KEY,
                        VaultOperation.LIST_ENCRYPTION_KEYS,
                        VaultOperation.GENERATE_ROOT_CA,
                        VaultOperation.GENERATE_INTERMEDIATE_CA,
                        VaultOperation.GENERATE_CERTIFICATE,
                        VaultOperation.REVOKE_CERTIFICATE,
                        VaultOperation.SIGN_CSR,
                        VaultOperation.LIST_CERTIFICATES,
                        VaultOperation.READ_CA_CERTIFICATE,
                        VaultOperation.READ_CRL,
                        VaultOperation.CONFIGURE_AWS_ROOT,
                        VaultOperation.CREATE_AWS_ROLE,
                        VaultOperation.GENERATE_AWS_CREDENTIALS,
                        VaultOperation.ROTATE_AWS_ROOT,
                        VaultOperation.LIST_AWS_ROLES,
                        VaultOperation.CREATE_POLICY,
                        VaultOperation.READ_POLICY,
                        VaultOperation.UPDATE_POLICY,
                        VaultOperation.DELETE_POLICY,
                        VaultOperation.LIST_POLICIES,
                        VaultOperation.GET_SEAL_STATUS,
                        VaultOperation.UNSEAL_VAULT,
                        VaultOperation.SEAL_VAULT,
                        VaultOperation.GET_HEALTH,
                        VaultOperation.LIST_MOUNTS,
                        VaultOperation.ENABLE_SECRETS_ENGINE,
                        VaultOperation.DISABLE_SECRETS_ENGINE,
                        VaultOperation.TUNE_MOUNT,
                        VaultOperation.LIST_LEASES,
                        VaultOperation.RENEW_LEASE,
                        VaultOperation.REVOKE_LEASE,
                        VaultOperation.LIST_AUDIT_DEVICES,
                        VaultOperation.ENABLE_AUDIT_DEVICE,
                        VaultOperation.DISABLE_AUDIT_DEVICE
                    ]
                ),
                NodeParameter(
                    name="vault_token",
                    type=NodeParameterType.SECRET,
                    description="Vault authentication token",
                    required=False
                ),
                NodeParameter(
                    name="vault_url",
                    type=NodeParameterType.STRING,
                    description="Vault server URL (default: http://127.0.0.1:8200)",
                    required=False,
                    default="http://127.0.0.1:8200"
                ),
                NodeParameter(
                    name="mount_path",
                    type=NodeParameterType.STRING,
                    description="Mount path for secrets engine or auth method",
                    required=False
                ),
                NodeParameter(
                    name="secret_path",
                    type=NodeParameterType.STRING,
                    description="Path to the secret within the mount",
                    required=False
                ),
                NodeParameter(
                    name="secret_data",
                    type=NodeParameterType.OBJECT,
                    description="Secret data to write or update",
                    required=False
                ),
                NodeParameter(
                    name="key_name",
                    type=NodeParameterType.STRING,
                    description="Name of encryption key or certificate",
                    required=False
                ),
                NodeParameter(
                    name="plaintext",
                    type=NodeParameterType.STRING,
                    description="Plaintext data to encrypt (base64 encoded)",
                    required=False
                ),
                NodeParameter(
                    name="ciphertext",
                    type=NodeParameterType.STRING,
                    description="Ciphertext data to decrypt",
                    required=False
                ),
                NodeParameter(
                    name="signature",
                    type=NodeParameterType.STRING,
                    description="Signature to verify",
                    required=False
                ),
                NodeParameter(
                    name="hash_algorithm",
                    type=NodeParameterType.STRING,
                    description="Hash algorithm (sha2-256, sha2-512, etc.)",
                    required=False,
                    default="sha2-256"
                ),
                NodeParameter(
                    name="policy_name",
                    type=NodeParameterType.STRING,
                    description="Name of the policy",
                    required=False
                ),
                NodeParameter(
                    name="policy_rules",
                    type=NodeParameterType.STRING,
                    description="Policy rules in HCL format",
                    required=False
                ),
                NodeParameter(
                    name="role_name",
                    type=NodeParameterType.STRING,
                    description="Name of the role",
                    required=False
                ),
                NodeParameter(
                    name="connection_name",
                    type=NodeParameterType.STRING,
                    description="Name of database connection",
                    required=False
                ),
                NodeParameter(
                    name="database_config",
                    type=NodeParameterType.OBJECT,
                    description="Database connection configuration",
                    required=False
                ),
                NodeParameter(
                    name="role_config",
                    type=NodeParameterType.OBJECT,
                    description="Role configuration parameters",
                    required=False
                ),
                NodeParameter(
                    name="engine_type",
                    type=NodeParameterType.STRING,
                    description="Type of secrets engine to enable",
                    required=False
                ),
                NodeParameter(
                    name="engine_config",
                    type=NodeParameterType.OBJECT,
                    description="Secrets engine configuration",
                    required=False
                ),
                NodeParameter(
                    name="lease_id",
                    type=NodeParameterType.STRING,
                    description="Lease ID for lease operations",
                    required=False
                ),
                NodeParameter(
                    name="unseal_key",
                    type=NodeParameterType.SECRET,
                    description="Unseal key for Vault",
                    required=False
                ),
                NodeParameter(
                    name="common_name",
                    type=NodeParameterType.STRING,
                    description="Common name for certificate generation",
                    required=False
                ),
                NodeParameter(
                    name="alt_names",
                    type=NodeParameterType.ARRAY,
                    description="Alternative names for certificate",
                    required=False
                ),
                NodeParameter(
                    name="ttl",
                    type=NodeParameterType.STRING,
                    description="Time to live for generated secrets/certificates",
                    required=False
                ),
                NodeParameter(
                    name="csr",
                    type=NodeParameterType.STRING,
                    description="Certificate Signing Request",
                    required=False
                ),
                NodeParameter(
                    name="aws_config",
                    type=NodeParameterType.OBJECT,
                    description="AWS configuration for AWS secrets engine",
                    required=False
                ),
                NodeParameter(
                    name="increment",
                    type=NodeParameterType.NUMBER,
                    description="Increment value for token/lease renewal",
                    required=False
                ),
                NodeParameter(
                    name="version",
                    type=NodeParameterType.NUMBER,
                    description="Version number for secret operations",
                    required=False
                ),
                NodeParameter(
                    name="format",
                    type=NodeParameterType.STRING,
                    description="Format for certificates (pem, der, pem_bundle)",
                    required=False,
                    default="pem"
                ),
                NodeParameter(
                    name="serial_number",
                    type=NodeParameterType.STRING,
                    description="Serial number for certificate revocation",
                    required=False
                ),
                NodeParameter(
                    name="audit_type",
                    type=NodeParameterType.STRING,
                    description="Type of audit device (file, syslog, etc.)",
                    required=False
                ),
                NodeParameter(
                    name="audit_options",
                    type=NodeParameterType.OBJECT,
                    description="Audit device configuration options",
                    required=False
                ),
                NodeParameter(
                    name="bytes",
                    type=NodeParameterType.NUMBER,
                    description="Number of random bytes to generate",
                    required=False,
                    default=32
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "token": NodeParameterType.STRING,
                "lease_id": NodeParameterType.STRING,
                "lease_duration": NodeParameterType.NUMBER,
                "renewable": NodeParameterType.BOOLEAN,
                "secret_data": NodeParameterType.OBJECT,
                "encrypted_data": NodeParameterType.STRING,
                "decrypted_data": NodeParameterType.STRING,
                "signature": NodeParameterType.STRING,
                "verification_result": NodeParameterType.BOOLEAN,
                "hash": NodeParameterType.STRING,
                "hmac": NodeParameterType.STRING,
                "random_bytes": NodeParameterType.STRING,
                "certificate": NodeParameterType.STRING,
                "private_key": NodeParameterType.STRING,
                "ca_chain": NodeParameterType.ARRAY,
                "serial_number": NodeParameterType.STRING,
                "aws_credentials": NodeParameterType.OBJECT,
                "policy_rules": NodeParameterType.STRING,
                "seal_status": NodeParameterType.OBJECT,
                "health_status": NodeParameterType.OBJECT,
                "mount_info": NodeParameterType.OBJECT,
                "auth_methods": NodeParameterType.OBJECT,
                "policies": NodeParameterType.ARRAY,
                "roles": NodeParameterType.ARRAY,
                "connections": NodeParameterType.ARRAY,
                "keys": NodeParameterType.ARRAY,
                "certificates": NodeParameterType.ARRAY,
                "leases": NodeParameterType.ARRAY,
                "audit_devices": NodeParameterType.OBJECT,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["vault", "hashicorp", "secrets", "encryption", "pki", "authentication", "security"],
            author="System",
            documentation_url="https://developer.hashicorp.com/vault/api-docs"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Most operations require a token except health check and seal status
        if operation not in [VaultOperation.GET_HEALTH, VaultOperation.GET_SEAL_STATUS, VaultOperation.UNSEAL_VAULT]:
            if not params.get("vault_token"):
                raise NodeValidationError("Vault token is required for authenticated operations")
                
        # Validate operation-specific requirements
        if operation in [VaultOperation.READ_SECRET, VaultOperation.WRITE_SECRET, VaultOperation.DELETE_SECRET,
                        VaultOperation.READ_SECRET_METADATA, VaultOperation.DESTROY_SECRET_VERSION,
                        VaultOperation.UNDELETE_SECRET_VERSION, VaultOperation.PATCH_SECRET]:
            if not params.get("secret_path"):
                raise NodeValidationError("Secret path is required for secret operations")
                
        elif operation in [VaultOperation.WRITE_SECRET, VaultOperation.PATCH_SECRET]:
            if not params.get("secret_data"):
                raise NodeValidationError("Secret data is required for write/patch operations")
                
        elif operation in [VaultOperation.CREATE_ENCRYPTION_KEY, VaultOperation.ENCRYPT_DATA, VaultOperation.DECRYPT_DATA,
                          VaultOperation.SIGN_DATA, VaultOperation.VERIFY_SIGNATURE, VaultOperation.GENERATE_HASH,
                          VaultOperation.GENERATE_HMAC, VaultOperation.ROTATE_ENCRYPTION_KEY]:
            if not params.get("key_name"):
                raise NodeValidationError("Key name is required for transit operations")
                
        elif operation == VaultOperation.ENCRYPT_DATA:
            if not params.get("plaintext"):
                raise NodeValidationError("Plaintext is required for encryption")
                
        elif operation == VaultOperation.DECRYPT_DATA:
            if not params.get("ciphertext"):
                raise NodeValidationError("Ciphertext is required for decryption")
                
        elif operation == VaultOperation.VERIFY_SIGNATURE:
            if not params.get("signature"):
                raise NodeValidationError("Signature is required for verification")
                
        elif operation in [VaultOperation.CREATE_POLICY, VaultOperation.UPDATE_POLICY]:
            if not params.get("policy_name") or not params.get("policy_rules"):
                raise NodeValidationError("Policy name and rules are required")
                
        elif operation in [VaultOperation.READ_POLICY, VaultOperation.DELETE_POLICY]:
            if not params.get("policy_name"):
                raise NodeValidationError("Policy name is required")
                
        elif operation in [VaultOperation.CONFIGURE_DATABASE, VaultOperation.CREATE_DATABASE_ROLE]:
            if not params.get("connection_name"):
                raise NodeValidationError("Connection name is required for database operations")
                
        elif operation == VaultOperation.GENERATE_CERTIFICATE:
            if not params.get("common_name"):
                raise NodeValidationError("Common name is required for certificate generation")
                
        elif operation == VaultOperation.UNSEAL_VAULT:
            if not params.get("unseal_key"):
                raise NodeValidationError("Unseal key is required for unsealing")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Vault node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == VaultOperation.GET_TOKEN:
                return await self._operation_get_token(validated_data)
            elif operation == VaultOperation.RENEW_TOKEN:
                return await self._operation_renew_token(validated_data)
            elif operation == VaultOperation.REVOKE_TOKEN:
                return await self._operation_revoke_token(validated_data)
            elif operation == VaultOperation.LIST_AUTH_METHODS:
                return await self._operation_list_auth_methods(validated_data)
            elif operation == VaultOperation.ENABLE_AUTH_METHOD:
                return await self._operation_enable_auth_method(validated_data)
            elif operation == VaultOperation.DISABLE_AUTH_METHOD:
                return await self._operation_disable_auth_method(validated_data)
            elif operation == VaultOperation.READ_SECRET:
                return await self._operation_read_secret(validated_data)
            elif operation == VaultOperation.WRITE_SECRET:
                return await self._operation_write_secret(validated_data)
            elif operation == VaultOperation.DELETE_SECRET:
                return await self._operation_delete_secret(validated_data)
            elif operation == VaultOperation.LIST_SECRETS:
                return await self._operation_list_secrets(validated_data)
            elif operation == VaultOperation.READ_SECRET_METADATA:
                return await self._operation_read_secret_metadata(validated_data)
            elif operation == VaultOperation.DESTROY_SECRET_VERSION:
                return await self._operation_destroy_secret_version(validated_data)
            elif operation == VaultOperation.UNDELETE_SECRET_VERSION:
                return await self._operation_undelete_secret_version(validated_data)
            elif operation == VaultOperation.PATCH_SECRET:
                return await self._operation_patch_secret(validated_data)
            elif operation == VaultOperation.CONFIGURE_DATABASE:
                return await self._operation_configure_database(validated_data)
            elif operation == VaultOperation.CREATE_DATABASE_ROLE:
                return await self._operation_create_database_role(validated_data)
            elif operation == VaultOperation.GENERATE_DATABASE_CREDENTIALS:
                return await self._operation_generate_database_credentials(validated_data)
            elif operation == VaultOperation.ROTATE_ROOT_CREDENTIALS:
                return await self._operation_rotate_root_credentials(validated_data)
            elif operation == VaultOperation.ROTATE_STATIC_CREDENTIALS:
                return await self._operation_rotate_static_credentials(validated_data)
            elif operation == VaultOperation.LIST_DATABASE_CONNECTIONS:
                return await self._operation_list_database_connections(validated_data)
            elif operation == VaultOperation.LIST_DATABASE_ROLES:
                return await self._operation_list_database_roles(validated_data)
            elif operation == VaultOperation.CREATE_ENCRYPTION_KEY:
                return await self._operation_create_encryption_key(validated_data)
            elif operation == VaultOperation.ENCRYPT_DATA:
                return await self._operation_encrypt_data(validated_data)
            elif operation == VaultOperation.DECRYPT_DATA:
                return await self._operation_decrypt_data(validated_data)
            elif operation == VaultOperation.SIGN_DATA:
                return await self._operation_sign_data(validated_data)
            elif operation == VaultOperation.VERIFY_SIGNATURE:
                return await self._operation_verify_signature(validated_data)
            elif operation == VaultOperation.GENERATE_HASH:
                return await self._operation_generate_hash(validated_data)
            elif operation == VaultOperation.GENERATE_HMAC:
                return await self._operation_generate_hmac(validated_data)
            elif operation == VaultOperation.GENERATE_RANDOM:
                return await self._operation_generate_random(validated_data)
            elif operation == VaultOperation.ROTATE_ENCRYPTION_KEY:
                return await self._operation_rotate_encryption_key(validated_data)
            elif operation == VaultOperation.LIST_ENCRYPTION_KEYS:
                return await self._operation_list_encryption_keys(validated_data)
            elif operation == VaultOperation.GENERATE_ROOT_CA:
                return await self._operation_generate_root_ca(validated_data)
            elif operation == VaultOperation.GENERATE_INTERMEDIATE_CA:
                return await self._operation_generate_intermediate_ca(validated_data)
            elif operation == VaultOperation.GENERATE_CERTIFICATE:
                return await self._operation_generate_certificate(validated_data)
            elif operation == VaultOperation.REVOKE_CERTIFICATE:
                return await self._operation_revoke_certificate(validated_data)
            elif operation == VaultOperation.SIGN_CSR:
                return await self._operation_sign_csr(validated_data)
            elif operation == VaultOperation.LIST_CERTIFICATES:
                return await self._operation_list_certificates(validated_data)
            elif operation == VaultOperation.READ_CA_CERTIFICATE:
                return await self._operation_read_ca_certificate(validated_data)
            elif operation == VaultOperation.READ_CRL:
                return await self._operation_read_crl(validated_data)
            elif operation == VaultOperation.CONFIGURE_AWS_ROOT:
                return await self._operation_configure_aws_root(validated_data)
            elif operation == VaultOperation.CREATE_AWS_ROLE:
                return await self._operation_create_aws_role(validated_data)
            elif operation == VaultOperation.GENERATE_AWS_CREDENTIALS:
                return await self._operation_generate_aws_credentials(validated_data)
            elif operation == VaultOperation.ROTATE_AWS_ROOT:
                return await self._operation_rotate_aws_root(validated_data)
            elif operation == VaultOperation.LIST_AWS_ROLES:
                return await self._operation_list_aws_roles(validated_data)
            elif operation == VaultOperation.CREATE_POLICY:
                return await self._operation_create_policy(validated_data)
            elif operation == VaultOperation.READ_POLICY:
                return await self._operation_read_policy(validated_data)
            elif operation == VaultOperation.UPDATE_POLICY:
                return await self._operation_update_policy(validated_data)
            elif operation == VaultOperation.DELETE_POLICY:
                return await self._operation_delete_policy(validated_data)
            elif operation == VaultOperation.LIST_POLICIES:
                return await self._operation_list_policies(validated_data)
            elif operation == VaultOperation.GET_SEAL_STATUS:
                return await self._operation_get_seal_status(validated_data)
            elif operation == VaultOperation.UNSEAL_VAULT:
                return await self._operation_unseal_vault(validated_data)
            elif operation == VaultOperation.SEAL_VAULT:
                return await self._operation_seal_vault(validated_data)
            elif operation == VaultOperation.GET_HEALTH:
                return await self._operation_get_health(validated_data)
            elif operation == VaultOperation.LIST_MOUNTS:
                return await self._operation_list_mounts(validated_data)
            elif operation == VaultOperation.ENABLE_SECRETS_ENGINE:
                return await self._operation_enable_secrets_engine(validated_data)
            elif operation == VaultOperation.DISABLE_SECRETS_ENGINE:
                return await self._operation_disable_secrets_engine(validated_data)
            elif operation == VaultOperation.TUNE_MOUNT:
                return await self._operation_tune_mount(validated_data)
            elif operation == VaultOperation.LIST_LEASES:
                return await self._operation_list_leases(validated_data)
            elif operation == VaultOperation.RENEW_LEASE:
                return await self._operation_renew_lease(validated_data)
            elif operation == VaultOperation.REVOKE_LEASE:
                return await self._operation_revoke_lease(validated_data)
            elif operation == VaultOperation.LIST_AUDIT_DEVICES:
                return await self._operation_list_audit_devices(validated_data)
            elif operation == VaultOperation.ENABLE_AUDIT_DEVICE:
                return await self._operation_enable_audit_device(validated_data)
            elif operation == VaultOperation.DISABLE_AUDIT_DEVICE:
                return await self._operation_disable_audit_device(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "status_code": None,
                    "response_headers": None
                }
                
        except Exception as e:
            error_message = f"Error in Vault node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "status_code": None,
                "response_headers": None
            }
        finally:
            # Clean up session
            await self._cleanup_session()
    
    async def _init_session(self):
        """Initialize HTTP session."""
        if not self.session:
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
    
    async def _cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Vault API."""
        vault_url = params.get("vault_url", self.BASE_URL)
        url = f"{vault_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add token header if provided
        if params.get("vault_token"):
            headers["X-Vault-Token"] = params.get("vault_token")
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Vault API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Authentication Operations
    # -------------------------
    
    async def _operation_get_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get token information."""
        result = await self._make_request("GET", "auth/token/lookup-self", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["token"] = data.get("id", "")
            result["lease_duration"] = data.get("ttl", 0)
            result["renewable"] = data.get("renewable", False)
        
        return result
    
    async def _operation_renew_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Renew a token."""
        request_data = {}
        if params.get("increment"):
            request_data["increment"] = params.get("increment")
        
        result = await self._make_request("POST", "auth/token/renew-self", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            auth_data = result["result"].get("auth", {})
            result["token"] = auth_data.get("client_token", "")
            result["lease_duration"] = auth_data.get("lease_duration", 0)
            result["renewable"] = auth_data.get("renewable", False)
        
        return result
    
    async def _operation_revoke_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Revoke a token."""
        return await self._make_request("POST", "auth/token/revoke-self", params)
    
    async def _operation_list_auth_methods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List authentication methods."""
        result = await self._make_request("GET", "sys/auth", params)
        
        if result["status"] == "success" and result["result"]:
            result["auth_methods"] = result["result"].get("data", {})
        
        return result
    
    async def _operation_enable_auth_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable an authentication method."""
        mount_path = params.get("mount_path", "")
        engine_type = params.get("engine_type", "")
        config = params.get("engine_config", {})
        
        request_data = {
            "type": engine_type,
            **config
        }
        
        return await self._make_request("POST", f"sys/auth/{mount_path}", params, request_data)
    
    async def _operation_disable_auth_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable an authentication method."""
        mount_path = params.get("mount_path", "")
        return await self._make_request("DELETE", f"sys/auth/{mount_path}", params)
    
    # -------------------------
    # KV Secrets Operations
    # -------------------------
    
    async def _operation_read_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a secret from KV store."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        version = params.get("version")
        
        endpoint = f"{mount_path}/data/{secret_path}"
        if version:
            endpoint += f"?version={version}"
        
        result = await self._make_request("GET", endpoint, params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["secret_data"] = data.get("data", {})
            metadata = data.get("metadata", {})
            result["version"] = metadata.get("version")
            result["created_time"] = metadata.get("created_time")
        
        return result
    
    async def _operation_write_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write a secret to KV store."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        secret_data = params.get("secret_data", {})
        
        request_data = {
            "data": secret_data
        }
        
        result = await self._make_request("POST", f"{mount_path}/data/{secret_path}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["version"] = data.get("version")
            result["created_time"] = data.get("created_time")
        
        return result
    
    async def _operation_delete_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a secret from KV store."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        versions = params.get("versions", [])
        
        if versions:
            request_data = {"versions": versions}
            return await self._make_request("POST", f"{mount_path}/delete/{secret_path}", params, request_data)
        else:
            return await self._make_request("DELETE", f"{mount_path}/metadata/{secret_path}", params)
    
    async def _operation_list_secrets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List secrets in a path."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        
        result = await self._make_request("LIST", f"{mount_path}/metadata/{secret_path}", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["keys"] = data.get("keys", [])
        
        return result
    
    async def _operation_read_secret_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read secret metadata."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        
        return await self._make_request("GET", f"{mount_path}/metadata/{secret_path}", params)
    
    async def _operation_destroy_secret_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Destroy a secret version."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        versions = params.get("versions", [])
        
        request_data = {"versions": versions}
        return await self._make_request("POST", f"{mount_path}/destroy/{secret_path}", params, request_data)
    
    async def _operation_undelete_secret_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Undelete a secret version."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        versions = params.get("versions", [])
        
        request_data = {"versions": versions}
        return await self._make_request("POST", f"{mount_path}/undelete/{secret_path}", params, request_data)
    
    async def _operation_patch_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patch a secret (partial update)."""
        mount_path = params.get("mount_path", "secret")
        secret_path = params.get("secret_path", "")
        secret_data = params.get("secret_data", {})
        
        request_data = {
            "data": secret_data
        }
        
        return await self._make_request("PATCH", f"{mount_path}/data/{secret_path}", params, request_data)
    
    # -------------------------
    # Database Operations
    # -------------------------
    
    async def _operation_configure_database(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure a database connection."""
        mount_path = params.get("mount_path", "database")
        connection_name = params.get("connection_name", "")
        database_config = params.get("database_config", {})
        
        return await self._make_request("POST", f"{mount_path}/config/{connection_name}", params, database_config)
    
    async def _operation_create_database_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a database role."""
        mount_path = params.get("mount_path", "database")
        role_name = params.get("role_name", "")
        role_config = params.get("role_config", {})
        
        return await self._make_request("POST", f"{mount_path}/roles/{role_name}", params, role_config)
    
    async def _operation_generate_database_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database credentials."""
        mount_path = params.get("mount_path", "database")
        role_name = params.get("role_name", "")
        
        result = await self._make_request("GET", f"{mount_path}/creds/{role_name}", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["username"] = data.get("username", "")
            result["password"] = data.get("password", "")
            result["lease_id"] = result["result"].get("lease_id", "")
            result["lease_duration"] = result["result"].get("lease_duration", 0)
            result["renewable"] = result["result"].get("renewable", False)
        
        return result
    
    async def _operation_rotate_root_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate root credentials."""
        mount_path = params.get("mount_path", "database")
        connection_name = params.get("connection_name", "")
        
        return await self._make_request("POST", f"{mount_path}/rotate-root/{connection_name}", params)
    
    async def _operation_rotate_static_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate static credentials."""
        mount_path = params.get("mount_path", "database")
        role_name = params.get("role_name", "")
        
        return await self._make_request("POST", f"{mount_path}/rotate-role/{role_name}", params)
    
    async def _operation_list_database_connections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List database connections."""
        mount_path = params.get("mount_path", "database")
        
        result = await self._make_request("LIST", f"{mount_path}/config", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["connections"] = data.get("keys", [])
        
        return result
    
    async def _operation_list_database_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List database roles."""
        mount_path = params.get("mount_path", "database")
        
        result = await self._make_request("LIST", f"{mount_path}/roles", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["roles"] = data.get("keys", [])
        
        return result
    
    # -------------------------
    # Transit Encryption Operations
    # -------------------------
    
    async def _operation_create_encryption_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an encryption key."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        key_config = params.get("role_config", {})
        
        return await self._make_request("POST", f"{mount_path}/keys/{key_name}", params, key_config)
    
    async def _operation_encrypt_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt data."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        plaintext = params.get("plaintext", "")
        
        request_data = {
            "plaintext": plaintext
        }
        
        result = await self._make_request("POST", f"{mount_path}/encrypt/{key_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["encrypted_data"] = data.get("ciphertext", "")
        
        return result
    
    async def _operation_decrypt_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt data."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        ciphertext = params.get("ciphertext", "")
        
        request_data = {
            "ciphertext": ciphertext
        }
        
        result = await self._make_request("POST", f"{mount_path}/decrypt/{key_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["decrypted_data"] = data.get("plaintext", "")
        
        return result
    
    async def _operation_sign_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sign data."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        plaintext = params.get("plaintext", "")
        hash_algorithm = params.get("hash_algorithm", "sha2-256")
        
        request_data = {
            "input": plaintext,
            "hash_algorithm": hash_algorithm
        }
        
        result = await self._make_request("POST", f"{mount_path}/sign/{key_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["signature"] = data.get("signature", "")
        
        return result
    
    async def _operation_verify_signature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a signature."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        plaintext = params.get("plaintext", "")
        signature = params.get("signature", "")
        hash_algorithm = params.get("hash_algorithm", "sha2-256")
        
        request_data = {
            "input": plaintext,
            "signature": signature,
            "hash_algorithm": hash_algorithm
        }
        
        result = await self._make_request("POST", f"{mount_path}/verify/{key_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["verification_result"] = data.get("valid", False)
        
        return result
    
    async def _operation_generate_hash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a hash."""
        mount_path = params.get("mount_path", "transit")
        plaintext = params.get("plaintext", "")
        hash_algorithm = params.get("hash_algorithm", "sha2-256")
        
        request_data = {
            "input": plaintext,
            "algorithm": hash_algorithm
        }
        
        result = await self._make_request("POST", f"{mount_path}/hash", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["hash"] = data.get("sum", "")
        
        return result
    
    async def _operation_generate_hmac(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an HMAC."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        plaintext = params.get("plaintext", "")
        hash_algorithm = params.get("hash_algorithm", "sha2-256")
        
        request_data = {
            "input": plaintext,
            "algorithm": hash_algorithm
        }
        
        result = await self._make_request("POST", f"{mount_path}/hmac/{key_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["hmac"] = data.get("hmac", "")
        
        return result
    
    async def _operation_generate_random(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate random bytes."""
        mount_path = params.get("mount_path", "transit")
        num_bytes = params.get("bytes", 32)
        
        result = await self._make_request("POST", f"{mount_path}/random/{num_bytes}", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["random_bytes"] = data.get("random_bytes", "")
        
        return result
    
    async def _operation_rotate_encryption_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate an encryption key."""
        mount_path = params.get("mount_path", "transit")
        key_name = params.get("key_name", "")
        
        return await self._make_request("POST", f"{mount_path}/keys/{key_name}/rotate", params)
    
    async def _operation_list_encryption_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List encryption keys."""
        mount_path = params.get("mount_path", "transit")
        
        result = await self._make_request("LIST", f"{mount_path}/keys", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["keys"] = data.get("keys", [])
        
        return result
    
    # -------------------------
    # PKI Operations
    # -------------------------
    
    async def _operation_generate_root_ca(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a root CA certificate."""
        mount_path = params.get("mount_path", "pki")
        common_name = params.get("common_name", "")
        ttl = params.get("ttl", "8760h")
        
        request_data = {
            "common_name": common_name,
            "ttl": ttl
        }
        
        result = await self._make_request("POST", f"{mount_path}/root/generate/internal", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["certificate"] = data.get("certificate", "")
            result["private_key"] = data.get("private_key", "")
            result["serial_number"] = data.get("serial_number", "")
        
        return result
    
    async def _operation_generate_intermediate_ca(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an intermediate CA certificate."""
        mount_path = params.get("mount_path", "pki")
        common_name = params.get("common_name", "")
        
        request_data = {
            "common_name": common_name
        }
        
        result = await self._make_request("POST", f"{mount_path}/intermediate/generate/internal", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["csr"] = data.get("csr", "")
            result["private_key"] = data.get("private_key", "")
        
        return result
    
    async def _operation_generate_certificate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a certificate."""
        mount_path = params.get("mount_path", "pki")
        role_name = params.get("role_name", "")
        common_name = params.get("common_name", "")
        alt_names = params.get("alt_names", [])
        ttl = params.get("ttl", "24h")
        
        request_data = {
            "common_name": common_name,
            "ttl": ttl
        }
        
        if alt_names:
            request_data["alt_names"] = ",".join(alt_names)
        
        result = await self._make_request("POST", f"{mount_path}/issue/{role_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["certificate"] = data.get("certificate", "")
            result["private_key"] = data.get("private_key", "")
            result["ca_chain"] = data.get("ca_chain", [])
            result["serial_number"] = data.get("serial_number", "")
        
        return result
    
    async def _operation_revoke_certificate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Revoke a certificate."""
        mount_path = params.get("mount_path", "pki")
        serial_number = params.get("serial_number", "")
        
        request_data = {
            "serial_number": serial_number
        }
        
        return await self._make_request("POST", f"{mount_path}/revoke", params, request_data)
    
    async def _operation_sign_csr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sign a CSR."""
        mount_path = params.get("mount_path", "pki")
        role_name = params.get("role_name", "")
        csr = params.get("csr", "")
        common_name = params.get("common_name", "")
        ttl = params.get("ttl", "24h")
        
        request_data = {
            "csr": csr,
            "common_name": common_name,
            "ttl": ttl
        }
        
        result = await self._make_request("POST", f"{mount_path}/sign/{role_name}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["certificate"] = data.get("certificate", "")
            result["ca_chain"] = data.get("ca_chain", [])
            result["serial_number"] = data.get("serial_number", "")
        
        return result
    
    async def _operation_list_certificates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List certificates."""
        mount_path = params.get("mount_path", "pki")
        
        result = await self._make_request("LIST", f"{mount_path}/certs", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["certificates"] = data.get("keys", [])
        
        return result
    
    async def _operation_read_ca_certificate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read CA certificate."""
        mount_path = params.get("mount_path", "pki")
        
        result = await self._make_request("GET", f"{mount_path}/ca/pem", params)
        
        if result["status"] == "success":
            result["certificate"] = result["result"]
        
        return result
    
    async def _operation_read_crl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read certificate revocation list."""
        mount_path = params.get("mount_path", "pki")
        
        return await self._make_request("GET", f"{mount_path}/crl/pem", params)
    
    # -------------------------
    # AWS Operations
    # -------------------------
    
    async def _operation_configure_aws_root(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure AWS root credentials."""
        mount_path = params.get("mount_path", "aws")
        aws_config = params.get("aws_config", {})
        
        return await self._make_request("POST", f"{mount_path}/config/root", params, aws_config)
    
    async def _operation_create_aws_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an AWS role."""
        mount_path = params.get("mount_path", "aws")
        role_name = params.get("role_name", "")
        role_config = params.get("role_config", {})
        
        return await self._make_request("POST", f"{mount_path}/roles/{role_name}", params, role_config)
    
    async def _operation_generate_aws_credentials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AWS credentials."""
        mount_path = params.get("mount_path", "aws")
        role_name = params.get("role_name", "")
        
        result = await self._make_request("GET", f"{mount_path}/creds/{role_name}", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["aws_credentials"] = {
                "access_key": data.get("access_key", ""),
                "secret_key": data.get("secret_key", ""),
                "security_token": data.get("security_token", "")
            }
            result["lease_id"] = result["result"].get("lease_id", "")
            result["lease_duration"] = result["result"].get("lease_duration", 0)
            result["renewable"] = result["result"].get("renewable", False)
        
        return result
    
    async def _operation_rotate_aws_root(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate AWS root credentials."""
        mount_path = params.get("mount_path", "aws")
        
        return await self._make_request("POST", f"{mount_path}/config/rotate-root", params)
    
    async def _operation_list_aws_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List AWS roles."""
        mount_path = params.get("mount_path", "aws")
        
        result = await self._make_request("LIST", f"{mount_path}/roles", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["roles"] = data.get("keys", [])
        
        return result
    
    # -------------------------
    # Policy Operations
    # -------------------------
    
    async def _operation_create_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a policy."""
        policy_name = params.get("policy_name", "")
        policy_rules = params.get("policy_rules", "")
        
        request_data = {
            "policy": policy_rules
        }
        
        return await self._make_request("PUT", f"sys/policies/acl/{policy_name}", params, request_data)
    
    async def _operation_read_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a policy."""
        policy_name = params.get("policy_name", "")
        
        result = await self._make_request("GET", f"sys/policies/acl/{policy_name}", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["policy_rules"] = data.get("policy", "")
        
        return result
    
    async def _operation_update_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a policy."""
        return await self._operation_create_policy(params)
    
    async def _operation_delete_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a policy."""
        policy_name = params.get("policy_name", "")
        
        return await self._make_request("DELETE", f"sys/policies/acl/{policy_name}", params)
    
    async def _operation_list_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List policies."""
        result = await self._make_request("LIST", "sys/policies/acl", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["policies"] = data.get("keys", [])
        
        return result
    
    # -------------------------
    # System Operations
    # -------------------------
    
    async def _operation_get_seal_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Vault seal status."""
        result = await self._make_request("GET", "sys/seal-status", params)
        
        if result["status"] == "success" and result["result"]:
            result["seal_status"] = result["result"]
        
        return result
    
    async def _operation_unseal_vault(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unseal Vault."""
        unseal_key = params.get("unseal_key", "")
        
        request_data = {
            "key": unseal_key
        }
        
        result = await self._make_request("POST", "sys/unseal", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            result["seal_status"] = result["result"]
        
        return result
    
    async def _operation_seal_vault(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Seal Vault."""
        result = await self._make_request("POST", "sys/seal", params)
        
        if result["status"] == "success" and result["result"]:
            result["seal_status"] = result["result"]
        
        return result
    
    async def _operation_get_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Vault health status."""
        result = await self._make_request("GET", "sys/health", params)
        
        if result["status"] == "success" and result["result"]:
            result["health_status"] = result["result"]
        
        return result
    
    async def _operation_list_mounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List secret engine mounts."""
        result = await self._make_request("GET", "sys/mounts", params)
        
        if result["status"] == "success" and result["result"]:
            result["mount_info"] = result["result"]
        
        return result
    
    async def _operation_enable_secrets_engine(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable a secrets engine."""
        mount_path = params.get("mount_path", "")
        engine_type = params.get("engine_type", "")
        engine_config = params.get("engine_config", {})
        
        request_data = {
            "type": engine_type,
            **engine_config
        }
        
        return await self._make_request("POST", f"sys/mounts/{mount_path}", params, request_data)
    
    async def _operation_disable_secrets_engine(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a secrets engine."""
        mount_path = params.get("mount_path", "")
        
        return await self._make_request("DELETE", f"sys/mounts/{mount_path}", params)
    
    async def _operation_tune_mount(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tune a mount."""
        mount_path = params.get("mount_path", "")
        engine_config = params.get("engine_config", {})
        
        return await self._make_request("POST", f"sys/mounts/{mount_path}/tune", params, engine_config)
    
    async def _operation_list_leases(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List leases."""
        prefix = params.get("secret_path", "")
        
        result = await self._make_request("LIST", f"sys/leases/lookup/{prefix}", params)
        
        if result["status"] == "success" and result["result"]:
            data = result["result"].get("data", {})
            result["leases"] = data.get("keys", [])
        
        return result
    
    async def _operation_renew_lease(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Renew a lease."""
        lease_id = params.get("lease_id", "")
        increment = params.get("increment")
        
        request_data = {
            "lease_id": lease_id
        }
        
        if increment:
            request_data["increment"] = increment
        
        result = await self._make_request("POST", "sys/leases/renew", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            result["lease_id"] = result["result"].get("lease_id", "")
            result["lease_duration"] = result["result"].get("lease_duration", 0)
            result["renewable"] = result["result"].get("renewable", False)
        
        return result
    
    async def _operation_revoke_lease(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Revoke a lease."""
        lease_id = params.get("lease_id", "")
        
        request_data = {
            "lease_id": lease_id
        }
        
        return await self._make_request("POST", "sys/leases/revoke", params, request_data)
    
    async def _operation_list_audit_devices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List audit devices."""
        result = await self._make_request("GET", "sys/audit", params)
        
        if result["status"] == "success" and result["result"]:
            result["audit_devices"] = result["result"]
        
        return result
    
    async def _operation_enable_audit_device(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable an audit device."""
        mount_path = params.get("mount_path", "")
        audit_type = params.get("audit_type", "")
        audit_options = params.get("audit_options", {})
        
        request_data = {
            "type": audit_type,
            "options": audit_options
        }
        
        return await self._make_request("POST", f"sys/audit/{mount_path}", params, request_data)
    
    async def _operation_disable_audit_device(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable an audit device."""
        mount_path = params.get("mount_path", "")
        
        return await self._make_request("DELETE", f"sys/audit/{mount_path}", params)


# Utility functions for common Vault operations
class VaultHelpers:
    """Helper functions for common Vault operations."""
    
    @staticmethod
    def create_kv_policy(mount: str, path: str, capabilities: List[str]) -> str:
        """Create a KV policy string."""
        return f'''
path "{mount}/data/{path}" {{
  capabilities = {json.dumps(capabilities)}
}}

path "{mount}/metadata/{path}" {{
  capabilities = ["list"]
}}
        '''.strip()
    
    @staticmethod
    def create_database_policy(mount: str, role: str) -> str:
        """Create a database policy string."""
        return f'''
path "{mount}/creds/{role}" {{
  capabilities = ["read"]
}}
        '''.strip()
    
    @staticmethod
    def create_transit_policy(mount: str, key: str, operations: List[str]) -> str:
        """Create a transit policy string."""
        policies = []
        for op in operations:
            policies.append(f'''
path "{mount}/{op}/{key}" {{
  capabilities = ["create", "update"]
}}
            '''.strip())
        return '\n\n'.join(policies)
    
    @staticmethod
    def create_pki_policy(mount: str, role: str) -> str:
        """Create a PKI policy string."""
        return f'''
path "{mount}/issue/{role}" {{
  capabilities = ["create", "update"]
}}

path "{mount}/sign/{role}" {{
  capabilities = ["create", "update"]
}}
        '''.strip()
    
    @staticmethod
    def encode_base64(data: str) -> str:
        """Encode string to base64."""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decode_base64(data: str) -> str:
        """Decode base64 to string."""
        return base64.b64decode(data).decode()
    
    @staticmethod
    def format_ttl(hours: int) -> str:
        """Format TTL in hours to string."""
        return f"{hours}h"
    
    @staticmethod
    def parse_lease_duration(duration: int) -> Dict[str, int]:
        """Parse lease duration in seconds to human readable format."""
        days = duration // 86400
        hours = (duration % 86400) // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": duration
        }


# Main test function for Vault Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== HashiCorp Vault Node Test Suite ===")
        
        # Get Vault token from environment or user input
        vault_token = os.environ.get("VAULT_TOKEN")
        vault_url = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
        
        if not vault_token:
            print("Vault token not found in environment variables")
            print("Please set VAULT_TOKEN")
            print("Or provide it when prompted...")
            vault_token = input("Enter Vault token: ")
        
        if not vault_token:
            print("Vault token is required for testing")
            return
        
        # Create an instance of the Vault Node
        node = VaultNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Get Health Status",
                "params": {
                    "operation": VaultOperation.GET_HEALTH,
                    "vault_url": vault_url
                },
                "expected_status": "success"
            },
            {
                "name": "Get Seal Status",
                "params": {
                    "operation": VaultOperation.GET_SEAL_STATUS,
                    "vault_url": vault_url
                },
                "expected_status": "success"
            },
            {
                "name": "List Policies",
                "params": {
                    "operation": VaultOperation.LIST_POLICIES,
                    "vault_token": vault_token,
                    "vault_url": vault_url
                },
                "expected_status": "success"
            }
        ]
        
        # Run test cases
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
                    print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                    if result.get("health_status"):
                        print(f"Health: {result['health_status'].get('initialized', 'unknown')}")
                    if result.get("seal_status"):
                        print(f"Sealed: {result['seal_status'].get('sealed', 'unknown')}")
                    if result.get("policies"):
                        print(f"Policies found: {len(result.get('policies', []))}")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("vault", VaultNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register VaultNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")