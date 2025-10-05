#!/usr/bin/env python3
"""
UUID Node for ACT Workflow System

This node provides comprehensive UUID/GUID generation and manipulation capabilities including:
- Standard UUIDs (v1, v3, v4, v5)
- Short IDs and custom formats
- Bulk generation and batch processing
- UUID validation and parsing
- Custom alphabet and encoding options
- Performance optimizations for high-volume generation

Architecture:
- Dispatch map for clean operation routing
- Multiple UUID generation strategies
- Validation and format checking
- Batch processing capabilities
- Custom encoding support
- Performance monitoring
"""

import uuid
import secrets
import string
import hashlib
import base64
import time
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Handle imports for both module and direct execution
try:
    from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Check for optional dependencies
try:
    import nanoid
    NANOID_AVAILABLE = True
except ImportError:
    NANOID_AVAILABLE = False

try:
    import shortuuid
    SHORTUUID_AVAILABLE = True
except ImportError:
    SHORTUUID_AVAILABLE = False

class UUIDOperation(str, Enum):
    """Enumeration of all supported UUID operations."""
    
    # Standard UUID Generation
    GENERATE_UUID4 = "generate_uuid4"
    GENERATE_UUID1 = "generate_uuid1"
    GENERATE_UUID3 = "generate_uuid3"
    GENERATE_UUID5 = "generate_uuid5"
    
    # Short ID Generation
    GENERATE_SHORT_ID = "generate_short_id"
    GENERATE_NANO_ID = "generate_nano_id"
    GENERATE_CUSTOM_ID = "generate_custom_id"
    
    # Bulk Generation
    GENERATE_BULK_UUIDS = "generate_bulk_uuids"
    GENERATE_BULK_SHORT_IDS = "generate_bulk_short_ids"
    
    # UUID Manipulation
    VALIDATE_UUID = "validate_uuid"
    PARSE_UUID = "parse_uuid"
    FORMAT_UUID = "format_uuid"
    CONVERT_UUID = "convert_uuid"
    
    # Custom Formats
    GENERATE_TIMESTAMP_ID = "generate_timestamp_id"
    GENERATE_SEQUENTIAL_ID = "generate_sequential_id"
    GENERATE_READABLE_ID = "generate_readable_id"
    
    # Utilities
    UUID_TO_BASE64 = "uuid_to_base64"
    BASE64_TO_UUID = "base64_to_uuid"
    UUID_TO_INT = "uuid_to_int"
    INT_TO_UUID = "int_to_uuid"

class UUIDError(Exception):
    """Custom exception for UUID operations."""
    pass

class UUIDGenerator:
    """Comprehensive UUID generation utilities."""
    
    # Custom alphabets for different ID types
    ALPHABETS = {
        'base62': string.ascii_letters + string.digits,
        'base36': string.ascii_lowercase + string.digits,
        'base32': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
        'hex': '0123456789abcdef',
        'safe': 'abcdefghijkmnopqrstuvwxyz23456789',  # No confusing chars
        'readable': 'abcdefghijkmnpqrstuvwxyz23456789'  # No 0, O, l, 1
    }
    
    def __init__(self):
        self.sequence_counter = 0
        self.last_timestamp = 0
    
    def generate_uuid4(self, count: int = 1) -> Union[str, List[str]]:
        """Generate UUID4 (random) identifiers."""
        if count == 1:
            return str(uuid.uuid4())
        return [str(uuid.uuid4()) for _ in range(count)]
    
    def generate_uuid1(self, count: int = 1) -> Union[str, List[str]]:
        """Generate UUID1 (time-based) identifiers."""
        if count == 1:
            return str(uuid.uuid1())
        return [str(uuid.uuid1()) for _ in range(count)]
    
    def generate_uuid3(self, namespace: str, name: str, count: int = 1) -> Union[str, List[str]]:
        """Generate UUID3 (name-based with MD5) identifiers."""
        # Convert namespace string to UUID if needed
        if isinstance(namespace, str):
            try:
                namespace_uuid = uuid.UUID(namespace)
            except ValueError:
                # Use predefined namespace or create one
                namespace_uuid = uuid.NAMESPACE_DNS
        else:
            namespace_uuid = namespace
        
        if count == 1:
            return str(uuid.uuid3(namespace_uuid, name))
        return [str(uuid.uuid3(namespace_uuid, f"{name}_{i}")) for i in range(count)]
    
    def generate_uuid5(self, namespace: str, name: str, count: int = 1) -> Union[str, List[str]]:
        """Generate UUID5 (name-based with SHA1) identifiers."""
        # Convert namespace string to UUID if needed
        if isinstance(namespace, str):
            try:
                namespace_uuid = uuid.UUID(namespace)
            except ValueError:
                namespace_uuid = uuid.NAMESPACE_DNS
        else:
            namespace_uuid = namespace
        
        if count == 1:
            return str(uuid.uuid5(namespace_uuid, name))
        return [str(uuid.uuid5(namespace_uuid, f"{name}_{i}")) for i in range(count)]
    
    def generate_short_id(self, length: int = 8, alphabet: str = None) -> str:
        """Generate short ID with custom alphabet."""
        if alphabet is None:
            alphabet = self.ALPHABETS['base62']
        
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_nano_id(self, length: int = 21, alphabet: str = None) -> str:
        """Generate NanoID (URL-safe unique string)."""
        if NANOID_AVAILABLE:
            if alphabet:
                return nanoid.generate(alphabet, length)
            return nanoid.generate(size=length)
        else:
            # Fallback implementation
            alphabet = alphabet or self.ALPHABETS['base62']
            return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_custom_id(self, pattern: str, replacements: Dict[str, str] = None) -> str:
        """Generate custom ID based on pattern."""
        result = pattern
        
        # Standard replacements
        standard_replacements = {
            '{uuid}': str(uuid.uuid4()),
            '{uuid_short}': str(uuid.uuid4()).replace('-', ''),
            '{timestamp}': str(int(time.time())),
            '{timestamp_ms}': str(int(time.time() * 1000)),
            '{random_hex}': secrets.token_hex(4),
            '{random_base62}': self.generate_short_id(8),
            '{date}': datetime.now().strftime('%Y%m%d'),
            '{time}': datetime.now().strftime('%H%M%S'),
            '{year}': datetime.now().strftime('%Y'),
            '{month}': datetime.now().strftime('%m'),
            '{day}': datetime.now().strftime('%d'),
        }
        
        # Add custom replacements
        if replacements:
            standard_replacements.update(replacements)
        
        # Apply replacements
        for placeholder, value in standard_replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def generate_timestamp_id(self, include_random: bool = True, length: int = 6) -> str:
        """Generate timestamp-based ID with optional random suffix."""
        timestamp = int(time.time() * 1000)  # milliseconds
        
        if include_random:
            random_suffix = self.generate_short_id(length, self.ALPHABETS['base36'])
            return f"{timestamp}_{random_suffix}"
        
        return str(timestamp)
    
    def generate_sequential_id(self, prefix: str = "", reset_on_new_timestamp: bool = True) -> str:
        """Generate sequential ID with optional prefix."""
        current_timestamp = int(time.time())
        
        if reset_on_new_timestamp and current_timestamp != self.last_timestamp:
            self.sequence_counter = 0
            self.last_timestamp = current_timestamp
        
        self.sequence_counter += 1
        
        if prefix:
            return f"{prefix}_{current_timestamp}_{self.sequence_counter:06d}"
        return f"{current_timestamp}_{self.sequence_counter:06d}"
    
    def generate_readable_id(self, word_count: int = 3, separator: str = "-") -> str:
        """Generate human-readable ID using word lists."""
        # Simple word lists - in production, use proper word lists
        adjectives = ['quick', 'lazy', 'bright', 'dark', 'small', 'large', 'happy', 'sad', 'fast', 'slow']
        nouns = ['fox', 'dog', 'cat', 'bird', 'fish', 'tree', 'rock', 'star', 'moon', 'sun']
        
        words = []
        for _ in range(word_count):
            if len(words) % 2 == 0:
                words.append(secrets.choice(adjectives))
            else:
                words.append(secrets.choice(nouns))
        
        # Add random number for uniqueness
        words.append(str(secrets.randbelow(9999)))
        
        return separator.join(words)
    
    def validate_uuid(self, uuid_string: str) -> Dict[str, Any]:
        """Validate UUID string and return information."""
        try:
            parsed_uuid = uuid.UUID(uuid_string)
            return {
                "valid": True,
                "version": parsed_uuid.version,
                "variant": parsed_uuid.variant,
                "hex": parsed_uuid.hex,
                "int": parsed_uuid.int,
                "bytes": parsed_uuid.bytes.hex(),
                "time": parsed_uuid.time if parsed_uuid.version == 1 else None,
                "clock_seq": parsed_uuid.clock_seq if parsed_uuid.version == 1 else None,
                "node": parsed_uuid.node if parsed_uuid.version == 1 else None
            }
        except ValueError as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def format_uuid(self, uuid_string: str, format_type: str = "standard") -> str:
        """Format UUID in different styles."""
        try:
            parsed_uuid = uuid.UUID(uuid_string)
            
            if format_type == "standard":
                return str(parsed_uuid)
            elif format_type == "no_dashes":
                return parsed_uuid.hex
            elif format_type == "uppercase":
                return str(parsed_uuid).upper()
            elif format_type == "braces":
                return f"{{{parsed_uuid}}}"
            elif format_type == "base64":
                return base64.urlsafe_b64encode(parsed_uuid.bytes).decode().rstrip('=')
            elif format_type == "base32":
                return base64.b32encode(parsed_uuid.bytes).decode().rstrip('=')
            else:
                raise UUIDError(f"Unknown format type: {format_type}")
                
        except ValueError as e:
            raise UUIDError(f"Invalid UUID: {str(e)}")
    
    def uuid_to_base64(self, uuid_string: str) -> str:
        """Convert UUID to base64 representation."""
        try:
            parsed_uuid = uuid.UUID(uuid_string)
            return base64.urlsafe_b64encode(parsed_uuid.bytes).decode().rstrip('=')
        except ValueError as e:
            raise UUIDError(f"Invalid UUID: {str(e)}")
    
    def base64_to_uuid(self, base64_string: str) -> str:
        """Convert base64 string back to UUID."""
        try:
            # Add padding if needed
            padding = 4 - len(base64_string) % 4
            if padding != 4:
                base64_string += '=' * padding
            
            uuid_bytes = base64.urlsafe_b64decode(base64_string)
            return str(uuid.UUID(bytes=uuid_bytes))
        except Exception as e:
            raise UUIDError(f"Invalid base64 UUID: {str(e)}")

class UUIDNode(BaseNode):
    """
    UUID/GUID generation and manipulation node for ACT workflow system.
    
    Provides comprehensive UUID operations including:
    - Standard UUID generation (v1, v3, v4, v5)
    - Short ID and custom format generation
    - Bulk generation capabilities
    - UUID validation and parsing
    - Format conversion utilities
    - Custom alphabet support
    - Performance optimizations
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        UUIDOperation.GENERATE_UUID4: {
            "required": [],
            "optional": ["count"],
            "description": "Generate UUID4 (random) identifiers"
        },
        UUIDOperation.GENERATE_UUID1: {
            "required": [],
            "optional": ["count"],
            "description": "Generate UUID1 (time-based) identifiers"
        },
        UUIDOperation.GENERATE_UUID3: {
            "required": ["namespace", "name"],
            "optional": ["count"],
            "description": "Generate UUID3 (name-based with MD5) identifiers"
        },
        UUIDOperation.GENERATE_UUID5: {
            "required": ["namespace", "name"],
            "optional": ["count"],
            "description": "Generate UUID5 (name-based with SHA1) identifiers"
        },
        UUIDOperation.GENERATE_SHORT_ID: {
            "required": [],
            "optional": ["length", "alphabet"],
            "description": "Generate short ID with custom alphabet"
        },
        UUIDOperation.GENERATE_NANO_ID: {
            "required": [],
            "optional": ["length", "alphabet"],
            "description": "Generate NanoID (URL-safe unique string)"
        },
        UUIDOperation.GENERATE_CUSTOM_ID: {
            "required": ["pattern"],
            "optional": ["replacements"],
            "description": "Generate custom ID based on pattern"
        },
        UUIDOperation.GENERATE_BULK_UUIDS: {
            "required": ["count"],
            "optional": ["type"],
            "description": "Generate multiple UUIDs in bulk"
        },
        UUIDOperation.VALIDATE_UUID: {
            "required": ["uuid_string"],
            "optional": [],
            "description": "Validate UUID string and return information"
        },
        UUIDOperation.FORMAT_UUID: {
            "required": ["uuid_string"],
            "optional": ["format_type"],
            "description": "Format UUID in different styles"
        },
        UUIDOperation.UUID_TO_BASE64: {
            "required": ["uuid_string"],
            "optional": [],
            "description": "Convert UUID to base64 representation"
        },
        UUIDOperation.BASE64_TO_UUID: {
            "required": ["base64_string"],
            "optional": [],
            "description": "Convert base64 string back to UUID"
        },
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        self.uuid_generator = UUIDGenerator()
        
        # Create operation dispatch map
        self.operation_dispatch = {
            UUIDOperation.GENERATE_UUID4: self._handle_generate_uuid4,
            UUIDOperation.GENERATE_UUID1: self._handle_generate_uuid1,
            UUIDOperation.GENERATE_UUID3: self._handle_generate_uuid3,
            UUIDOperation.GENERATE_UUID5: self._handle_generate_uuid5,
            UUIDOperation.GENERATE_SHORT_ID: self._handle_generate_short_id,
            UUIDOperation.GENERATE_NANO_ID: self._handle_generate_nano_id,
            UUIDOperation.GENERATE_CUSTOM_ID: self._handle_generate_custom_id,
            UUIDOperation.GENERATE_BULK_UUIDS: self._handle_generate_bulk_uuids,
            UUIDOperation.GENERATE_BULK_SHORT_IDS: self._handle_generate_bulk_short_ids,
            UUIDOperation.VALIDATE_UUID: self._handle_validate_uuid,
            UUIDOperation.PARSE_UUID: self._handle_parse_uuid,
            UUIDOperation.FORMAT_UUID: self._handle_format_uuid,
            UUIDOperation.CONVERT_UUID: self._handle_convert_uuid,
            UUIDOperation.GENERATE_TIMESTAMP_ID: self._handle_generate_timestamp_id,
            UUIDOperation.GENERATE_SEQUENTIAL_ID: self._handle_generate_sequential_id,
            UUIDOperation.GENERATE_READABLE_ID: self._handle_generate_readable_id,
            UUIDOperation.UUID_TO_BASE64: self._handle_uuid_to_base64,
            UUIDOperation.BASE64_TO_UUID: self._handle_base64_to_uuid,
            UUIDOperation.UUID_TO_INT: self._handle_uuid_to_int,
            UUIDOperation.INT_TO_UUID: self._handle_int_to_uuid,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the schema for UUIDNode."""
        return NodeSchema(
            name="UUIDNode",
            node_type="uuid",
            description="Comprehensive UUID/GUID generation and manipulation",
            version="1.0.0",
            parameters=[
                NodeParameter(
                    name="operation",
                    type="string",
                    description="The UUID operation to perform",
                    required=True,
                    enum=[op.value for op in UUIDOperation]
                ),
                NodeParameter(
                    name="count",
                    type="number",
                    description="Number of UUIDs to generate",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="namespace",
                    type="string",
                    description="Namespace UUID for UUID3/UUID5 generation",
                    required=False
                ),
                NodeParameter(
                    name="name",
                    type="string",
                    description="Name for UUID3/UUID5 generation",
                    required=False
                ),
                NodeParameter(
                    name="length",
                    type="number",
                    description="Length of generated ID",
                    required=False
                ),
                NodeParameter(
                    name="alphabet",
                    type="string",
                    description="Custom alphabet for ID generation",
                    required=False
                ),
                NodeParameter(
                    name="pattern",
                    type="string",
                    description="Pattern for custom ID generation",
                    required=False
                ),
                NodeParameter(
                    name="replacements",
                    type="object",
                    description="Custom replacements for pattern",
                    required=False
                ),
                NodeParameter(
                    name="uuid_string",
                    type="string",
                    description="UUID string to validate or convert",
                    required=False
                ),
                NodeParameter(
                    name="format_type",
                    type="string",
                    description="Format type for UUID formatting",
                    required=False,
                    enum=["standard", "no_dashes", "uppercase", "braces", "base64", "base32"]
                ),
                NodeParameter(
                    name="base64_string",
                    type="string",
                    description="Base64 encoded UUID string",
                    required=False
                ),
                NodeParameter(
                    name="prefix",
                    type="string",
                    description="Prefix for sequential IDs",
                    required=False
                ),
                NodeParameter(
                    name="separator",
                    type="string",
                    description="Separator for readable IDs",
                    required=False,
                    default="-"
                ),
                NodeParameter(
                    name="include_random",
                    type="boolean",
                    description="Include random component in timestamp ID",
                    required=False,
                    default=True
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "uuid": NodeParameterType.STRING,
                "uuids": NodeParameterType.ARRAY,
                "validation": NodeParameterType.OBJECT,
                "count": NodeParameterType.NUMBER,
                "timestamp": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, data: Dict[str, Any]) -> None:
        """Custom validation for UUID operations."""
        params = data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation parameter is required")
        
        if operation not in [op.value for op in UUIDOperation]:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Get operation metadata
        metadata = self.OPERATION_METADATA.get(operation, {})
        required_params = metadata.get("required", [])
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                raise ValueError(f"Required parameter '{param}' missing for operation '{operation}'")
        
        # Operation-specific validation
        if operation in [UUIDOperation.GENERATE_BULK_UUIDS, UUIDOperation.GENERATE_BULK_SHORT_IDS]:
            count = params.get("count", 1)
            if not isinstance(count, int) or count < 1:
                raise ValueError("Count must be a positive integer")
            if count > 100000:
                raise ValueError("Count cannot exceed 100,000 for performance reasons")
        
        if operation == UUIDOperation.GENERATE_SHORT_ID:
            length = params.get("length", 8)
            if not isinstance(length, int) or length < 1 or length > 128:
                raise ValueError("Length must be between 1 and 128")
        
        if operation == UUIDOperation.VALIDATE_UUID:
            uuid_string = params.get("uuid_string")
            if not uuid_string or not isinstance(uuid_string, str):
                raise ValueError("uuid_string must be a non-empty string")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a UUID operation."""
        try:
            params = data.get("params", {})
            operation = params.get("operation")
            
            self.logger.info(f"Executing UUID operation: {operation}")
            
            # Get operation handler
            handler = self.operation_dispatch.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Unsupported UUID operation: {operation}",
                    "operation": operation
                }
            
            # Execute operation
            result = await handler(params)
            
            self.logger.info(f"UUID operation {operation} completed successfully")
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except UUIDError as e:
            error_msg = f"UUID operation error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
        except Exception as e:
            error_msg = f"UUID operation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
    
    # Operation Handlers
    async def _handle_generate_uuid4(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_uuid4 operation."""
        count = params.get("count", 1)
        
        if count == 1:
            uuid_str = self.uuid_generator.generate_uuid4()
            return {
                "uuid": uuid_str,
                "count": 1,
                "type": "uuid4"
            }
        else:
            uuids = self.uuid_generator.generate_uuid4(count)
            return {
                "uuids": uuids,
                "count": count,
                "type": "uuid4"
            }
    
    async def _handle_generate_uuid1(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_uuid1 operation."""
        count = params.get("count", 1)
        
        if count == 1:
            uuid_str = self.uuid_generator.generate_uuid1()
            return {
                "uuid": uuid_str,
                "count": 1,
                "type": "uuid1"
            }
        else:
            uuids = self.uuid_generator.generate_uuid1(count)
            return {
                "uuids": uuids,
                "count": count,
                "type": "uuid1"
            }
    
    async def _handle_generate_uuid3(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_uuid3 operation."""
        namespace = params["namespace"]
        name = params["name"]
        count = params.get("count", 1)
        
        if count == 1:
            uuid_str = self.uuid_generator.generate_uuid3(namespace, name)
            return {
                "uuid": uuid_str,
                "count": 1,
                "type": "uuid3",
                "namespace": namespace,
                "name": name
            }
        else:
            uuids = self.uuid_generator.generate_uuid3(namespace, name, count)
            return {
                "uuids": uuids,
                "count": count,
                "type": "uuid3",
                "namespace": namespace,
                "name": name
            }
    
    async def _handle_generate_uuid5(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_uuid5 operation."""
        namespace = params["namespace"]
        name = params["name"]
        count = params.get("count", 1)
        
        if count == 1:
            uuid_str = self.uuid_generator.generate_uuid5(namespace, name)
            return {
                "uuid": uuid_str,
                "count": 1,
                "type": "uuid5",
                "namespace": namespace,
                "name": name
            }
        else:
            uuids = self.uuid_generator.generate_uuid5(namespace, name, count)
            return {
                "uuids": uuids,
                "count": count,
                "type": "uuid5",
                "namespace": namespace,
                "name": name
            }
    
    async def _handle_generate_short_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_short_id operation."""
        length = params.get("length", 8)
        alphabet = params.get("alphabet")
        
        short_id = self.uuid_generator.generate_short_id(length, alphabet)
        return {
            "id": short_id,
            "length": length,
            "alphabet": alphabet or "base62",
            "type": "short_id"
        }
    
    async def _handle_generate_nano_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_nano_id operation."""
        length = params.get("length", 21)
        alphabet = params.get("alphabet")
        
        nano_id = self.uuid_generator.generate_nano_id(length, alphabet)
        return {
            "id": nano_id,
            "length": length,
            "alphabet": alphabet or "default",
            "type": "nano_id",
            "nanoid_available": NANOID_AVAILABLE
        }
    
    async def _handle_generate_custom_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_custom_id operation."""
        pattern = params["pattern"]
        replacements = params.get("replacements", {})
        
        custom_id = self.uuid_generator.generate_custom_id(pattern, replacements)
        return {
            "id": custom_id,
            "pattern": pattern,
            "replacements": replacements,
            "type": "custom_id"
        }
    
    async def _handle_generate_bulk_uuids(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_bulk_uuids operation."""
        count = params["count"]
        uuid_type = params.get("type", "uuid4")
        
        start_time = time.time()
        
        if uuid_type == "uuid1":
            uuids = self.uuid_generator.generate_uuid1(count)
        elif uuid_type == "uuid4":
            uuids = self.uuid_generator.generate_uuid4(count)
        else:
            raise UUIDError(f"Unsupported UUID type for bulk generation: {uuid_type}")
        
        end_time = time.time()
        
        return {
            "uuids": uuids,
            "count": count,
            "type": uuid_type,
            "generation_time": round(end_time - start_time, 4),
            "rate": round(count / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_generate_bulk_short_ids(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_bulk_short_ids operation."""
        count = params["count"]
        length = params.get("length", 8)
        alphabet = params.get("alphabet")
        
        start_time = time.time()
        
        ids = [self.uuid_generator.generate_short_id(length, alphabet) for _ in range(count)]
        
        end_time = time.time()
        
        return {
            "ids": ids,
            "count": count,
            "length": length,
            "alphabet": alphabet or "base62",
            "generation_time": round(end_time - start_time, 4),
            "rate": round(count / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_validate_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validate_uuid operation."""
        uuid_string = params["uuid_string"]
        
        validation_result = self.uuid_generator.validate_uuid(uuid_string)
        return {
            "uuid_string": uuid_string,
            "validation": validation_result
        }
    
    async def _handle_parse_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parse_uuid operation."""
        # Same as validate_uuid for now
        return await self._handle_validate_uuid(params)
    
    async def _handle_format_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle format_uuid operation."""
        uuid_string = params["uuid_string"]
        format_type = params.get("format_type", "standard")
        
        formatted_uuid = self.uuid_generator.format_uuid(uuid_string, format_type)
        return {
            "original": uuid_string,
            "formatted": formatted_uuid,
            "format_type": format_type
        }
    
    async def _handle_convert_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle convert_uuid operation."""
        # Implementation for UUID conversion between formats
        return {"message": "convert_uuid operation not yet implemented"}
    
    async def _handle_generate_timestamp_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_timestamp_id operation."""
        include_random = params.get("include_random", True)
        length = params.get("length", 6)
        
        timestamp_id = self.uuid_generator.generate_timestamp_id(include_random, length)
        return {
            "id": timestamp_id,
            "include_random": include_random,
            "random_length": length,
            "type": "timestamp_id"
        }
    
    async def _handle_generate_sequential_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_sequential_id operation."""
        prefix = params.get("prefix", "")
        
        sequential_id = self.uuid_generator.generate_sequential_id(prefix)
        return {
            "id": sequential_id,
            "prefix": prefix,
            "type": "sequential_id"
        }
    
    async def _handle_generate_readable_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_readable_id operation."""
        word_count = params.get("word_count", 3)
        separator = params.get("separator", "-")
        
        readable_id = self.uuid_generator.generate_readable_id(word_count, separator)
        return {
            "id": readable_id,
            "word_count": word_count,
            "separator": separator,
            "type": "readable_id"
        }
    
    async def _handle_uuid_to_base64(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle uuid_to_base64 operation."""
        uuid_string = params["uuid_string"]
        
        base64_string = self.uuid_generator.uuid_to_base64(uuid_string)
        return {
            "uuid": uuid_string,
            "base64": base64_string,
            "compression_ratio": round(len(base64_string) / len(uuid_string), 2)
        }
    
    async def _handle_base64_to_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle base64_to_uuid operation."""
        base64_string = params["base64_string"]
        
        uuid_string = self.uuid_generator.base64_to_uuid(base64_string)
        return {
            "base64": base64_string,
            "uuid": uuid_string
        }
    
    async def _handle_uuid_to_int(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle uuid_to_int operation."""
        uuid_string = params["uuid_string"]
        
        try:
            parsed_uuid = uuid.UUID(uuid_string)
            return {
                "uuid": uuid_string,
                "int": parsed_uuid.int,
                "hex": parsed_uuid.hex
            }
        except ValueError as e:
            raise UUIDError(f"Invalid UUID: {str(e)}")
    
    async def _handle_int_to_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle int_to_uuid operation."""
        int_value = params["int_value"]
        
        try:
            parsed_uuid = uuid.UUID(int=int_value)
            return {
                "int": int_value,
                "uuid": str(parsed_uuid)
            }
        except ValueError as e:
            raise UUIDError(f"Invalid integer for UUID: {str(e)}")