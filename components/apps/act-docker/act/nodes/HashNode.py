#!/usr/bin/env python3
"""
Hash Node for ACT Workflow System

This node provides comprehensive hashing and checksum capabilities including:
- Standard hash algorithms (MD5, SHA1, SHA256, SHA512)
- Secure password hashing (bcrypt, scrypt, pbkdf2)
- File integrity checking (CRC32, checksums)
- Custom hash functions and HMAC
- Hash verification and comparison
- Performance optimization for large data

Architecture:
- Dispatch map for clean operation routing
- Multiple hash algorithm support
- Secure password hashing with salt
- File and data integrity verification
- Batch processing capabilities
- Performance monitoring
"""

import hashlib
import hmac
import zlib
import base64
import secrets
import time
import os
from typing import Dict, Any, List, Optional, Union, BinaryIO
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
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import scrypt
    SCRYPT_AVAILABLE = True
except ImportError:
    SCRYPT_AVAILABLE = False

try:
    import argon2
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

class HashOperation(str, Enum):
    """Enumeration of all supported hash operations."""
    
    # Standard Hash Algorithms
    MD5 = "md5"
    SHA1 = "sha1"
    SHA224 = "sha224"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA3_224 = "sha3_224"
    SHA3_256 = "sha3_256"
    SHA3_384 = "sha3_384"
    SHA3_512 = "sha3_512"
    
    # Password Hashing
    BCRYPT = "bcrypt"
    SCRYPT = "scrypt"
    PBKDF2 = "pbkdf2"
    ARGON2 = "argon2"
    
    # HMAC Operations
    HMAC_MD5 = "hmac_md5"
    HMAC_SHA1 = "hmac_sha1"
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA512 = "hmac_sha512"
    
    # File Operations
    FILE_MD5 = "file_md5"
    FILE_SHA256 = "file_sha256"
    FILE_CHECKSUM = "file_checksum"
    
    # Checksums
    CRC32 = "crc32"
    ADLER32 = "adler32"
    
    # Verification
    VERIFY_HASH = "verify_hash"
    VERIFY_PASSWORD = "verify_password"
    COMPARE_HASHES = "compare_hashes"
    
    # Batch Operations
    BATCH_HASH = "batch_hash"
    MULTI_HASH = "multi_hash"
    
    # Utilities
    HASH_INFO = "hash_info"
    GENERATE_SALT = "generate_salt"
    STRENGTH_CHECK = "strength_check"

class HashError(Exception):
    """Custom exception for hash operations."""
    pass

class HashGenerator:
    """Comprehensive hash generation utilities."""
    
    # Available hash algorithms
    ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha224': hashlib.sha224,
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'sha3_224': hashlib.sha3_224,
        'sha3_256': hashlib.sha3_256,
        'sha3_384': hashlib.sha3_384,
        'sha3_512': hashlib.sha3_512,
    }
    
    def __init__(self):
        self.performance_stats = {}
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256', 
                  encoding: str = 'utf-8', output_format: str = 'hex') -> str:
        """Generate hash for data using specified algorithm."""
        if algorithm not in self.ALGORITHMS:
            raise HashError(f"Unsupported hash algorithm: {algorithm}")
        
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode(encoding)
        
        # Generate hash
        hash_obj = self.ALGORITHMS[algorithm]()
        hash_obj.update(data)
        
        # Return in requested format
        if output_format == 'hex':
            return hash_obj.hexdigest()
        elif output_format == 'base64':
            return base64.b64encode(hash_obj.digest()).decode()
        elif output_format == 'bytes':
            return hash_obj.digest()
        else:
            raise HashError(f"Unsupported output format: {output_format}")
    
    def hash_file(self, file_path: str, algorithm: str = 'sha256', 
                  chunk_size: int = 8192) -> Dict[str, Any]:
        """Generate hash for a file."""
        if not os.path.exists(file_path):
            raise HashError(f"File not found: {file_path}")
        
        if algorithm not in self.ALGORITHMS:
            raise HashError(f"Unsupported hash algorithm: {algorithm}")
        
        hash_obj = self.ALGORITHMS[algorithm]()
        file_size = os.path.getsize(file_path)
        bytes_processed = 0
        
        start_time = time.time()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
                bytes_processed += len(chunk)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            'file_path': file_path,
            'algorithm': algorithm,
            'hash': hash_obj.hexdigest(),
            'file_size': file_size,
            'bytes_processed': bytes_processed,
            'processing_time': round(processing_time, 4),
            'throughput_mb_s': round((file_size / 1024 / 1024) / processing_time, 2) if processing_time > 0 else 0
        }
    
    def generate_hmac(self, data: Union[str, bytes], key: Union[str, bytes], 
                      algorithm: str = 'sha256', encoding: str = 'utf-8') -> str:
        """Generate HMAC for data with key."""
        # Convert strings to bytes if needed
        if isinstance(data, str):
            data = data.encode(encoding)
        if isinstance(key, str):
            key = key.encode(encoding)
        
        # Map algorithm names to hashlib functions
        algorithm_map = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        if algorithm not in algorithm_map:
            raise HashError(f"Unsupported HMAC algorithm: {algorithm}")
        
        return hmac.new(key, data, algorithm_map[algorithm]).hexdigest()
    
    def hash_password_bcrypt(self, password: str, rounds: int = 12) -> str:
        """Hash password using bcrypt."""
        if not BCRYPT_AVAILABLE:
            raise HashError("bcrypt library not available")
        
        # Convert string to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode('utf-8')
    
    def verify_password_bcrypt(self, password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash."""
        if not BCRYPT_AVAILABLE:
            raise HashError("bcrypt library not available")
        
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
    def hash_password_pbkdf2(self, password: str, salt: Optional[bytes] = None, 
                            iterations: int = 100000, algorithm: str = 'sha256') -> Dict[str, Any]:
        """Hash password using PBKDF2."""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Convert string to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate hash
        hashed = hashlib.pbkdf2_hmac(algorithm, password_bytes, salt, iterations)
        
        return {
            'hash': base64.b64encode(hashed).decode(),
            'salt': base64.b64encode(salt).decode(),
            'iterations': iterations,
            'algorithm': algorithm
        }
    
    def verify_password_pbkdf2(self, password: str, stored_hash: str, salt: str, 
                               iterations: int = 100000, algorithm: str = 'sha256') -> bool:
        """Verify password against PBKDF2 hash."""
        try:
            password_bytes = password.encode('utf-8')
            salt_bytes = base64.b64decode(salt)
            stored_hash_bytes = base64.b64decode(stored_hash)
            
            computed_hash = hashlib.pbkdf2_hmac(algorithm, password_bytes, salt_bytes, iterations)
            
            return hmac.compare_digest(computed_hash, stored_hash_bytes)
        except Exception:
            return False
    
    def calculate_crc32(self, data: Union[str, bytes], encoding: str = 'utf-8') -> int:
        """Calculate CRC32 checksum."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        return zlib.crc32(data) & 0xffffffff
    
    def calculate_adler32(self, data: Union[str, bytes], encoding: str = 'utf-8') -> int:
        """Calculate Adler32 checksum."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        return zlib.adler32(data) & 0xffffffff
    
    def batch_hash(self, data_list: List[Union[str, bytes]], algorithm: str = 'sha256') -> List[Dict[str, Any]]:
        """Hash multiple data items in batch."""
        results = []
        
        for i, data in enumerate(data_list):
            try:
                hash_result = self.hash_data(data, algorithm)
                results.append({
                    'index': i,
                    'data_length': len(data),
                    'hash': hash_result,
                    'algorithm': algorithm,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'data_length': len(data) if data else 0,
                    'hash': None,
                    'algorithm': algorithm,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def multi_hash(self, data: Union[str, bytes], algorithms: List[str]) -> Dict[str, str]:
        """Generate multiple hashes for the same data."""
        results = {}
        
        for algorithm in algorithms:
            try:
                results[algorithm] = self.hash_data(data, algorithm)
            except Exception as e:
                results[algorithm] = f"Error: {str(e)}"
        
        return results
    
    def verify_hash(self, data: Union[str, bytes], expected_hash: str, 
                    algorithm: str = 'sha256') -> Dict[str, Any]:
        """Verify data against expected hash."""
        try:
            computed_hash = self.hash_data(data, algorithm)
            is_valid = hmac.compare_digest(computed_hash, expected_hash)
            
            return {
                'valid': is_valid,
                'expected': expected_hash,
                'computed': computed_hash,
                'algorithm': algorithm,
                'data_length': len(data)
            }
        except Exception as e:
            return {
                'valid': False,
                'expected': expected_hash,
                'computed': None,
                'algorithm': algorithm,
                'error': str(e)
            }
    
    def compare_hashes(self, hash1: str, hash2: str) -> Dict[str, Any]:
        """Compare two hashes safely."""
        try:
            are_equal = hmac.compare_digest(hash1, hash2)
            return {
                'equal': are_equal,
                'hash1': hash1,
                'hash2': hash2,
                'hash1_length': len(hash1),
                'hash2_length': len(hash2)
            }
        except Exception as e:
            return {
                'equal': False,
                'hash1': hash1,
                'hash2': hash2,
                'error': str(e)
            }
    
    def generate_salt(self, length: int = 32, output_format: str = 'hex') -> str:
        """Generate cryptographically secure salt."""
        salt_bytes = secrets.token_bytes(length)
        
        if output_format == 'hex':
            return salt_bytes.hex()
        elif output_format == 'base64':
            return base64.b64encode(salt_bytes).decode()
        elif output_format == 'bytes':
            return salt_bytes
        else:
            raise HashError(f"Unsupported salt format: {output_format}")
    
    def get_hash_info(self, algorithm: str) -> Dict[str, Any]:
        """Get information about a hash algorithm."""
        if algorithm not in self.ALGORITHMS:
            return {
                'algorithm': algorithm,
                'available': False,
                'error': f"Unsupported algorithm: {algorithm}"
            }
        
        hash_obj = self.ALGORITHMS[algorithm]()
        
        return {
            'algorithm': algorithm,
            'available': True,
            'digest_size': hash_obj.digest_size,
            'block_size': hash_obj.block_size,
            'name': hash_obj.name,
            'description': self._get_algorithm_description(algorithm)
        }
    
    def _get_algorithm_description(self, algorithm: str) -> str:
        """Get description for hash algorithm."""
        descriptions = {
            'md5': 'MD5 - Fast but cryptographically broken, use only for non-security purposes',
            'sha1': 'SHA-1 - Deprecated for security, use SHA-2 or SHA-3 instead',
            'sha224': 'SHA-224 - Part of SHA-2 family, produces 224-bit hash',
            'sha256': 'SHA-256 - Most common secure hash, produces 256-bit hash',
            'sha384': 'SHA-384 - Part of SHA-2 family, produces 384-bit hash',
            'sha512': 'SHA-512 - Strong hash function, produces 512-bit hash',
            'sha3_224': 'SHA3-224 - Part of SHA-3 family, produces 224-bit hash',
            'sha3_256': 'SHA3-256 - Part of SHA-3 family, produces 256-bit hash',
            'sha3_384': 'SHA3-384 - Part of SHA-3 family, produces 384-bit hash',
            'sha3_512': 'SHA3-512 - Part of SHA-3 family, produces 512-bit hash'
        }
        return descriptions.get(algorithm, f"Hash algorithm: {algorithm}")

class HashNode(BaseNode):
    """
    Hash generation and verification node for ACT workflow system.
    
    Provides comprehensive hashing capabilities including:
    - Standard hash algorithms (MD5, SHA1, SHA256, SHA512)
    - Secure password hashing (bcrypt, scrypt, pbkdf2)
    - File integrity checking (CRC32, checksums)
    - HMAC generation and verification
    - Batch processing and performance optimization
    - Hash comparison and verification
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        HashOperation.MD5: {
            "required": ["data"],
            "optional": ["encoding", "output_format"],
            "description": "Generate MD5 hash (not secure, use for non-security purposes)"
        },
        HashOperation.SHA256: {
            "required": ["data"],
            "optional": ["encoding", "output_format"],
            "description": "Generate SHA-256 hash (recommended for security)"
        },
        HashOperation.SHA512: {
            "required": ["data"],
            "optional": ["encoding", "output_format"],
            "description": "Generate SHA-512 hash (strong security)"
        },
        HashOperation.BCRYPT: {
            "required": ["password"],
            "optional": ["rounds"],
            "description": "Hash password using bcrypt (recommended for passwords)"
        },
        HashOperation.HMAC_SHA256: {
            "required": ["data", "key"],
            "optional": ["encoding"],
            "description": "Generate HMAC-SHA256 for authenticated hashing"
        },
        HashOperation.FILE_SHA256: {
            "required": ["file_path"],
            "optional": ["chunk_size"],
            "description": "Generate SHA-256 hash for file"
        },
        HashOperation.VERIFY_PASSWORD: {
            "required": ["password", "hashed"],
            "optional": ["hash_type"],
            "description": "Verify password against stored hash"
        },
        HashOperation.BATCH_HASH: {
            "required": ["data_list"],
            "optional": ["algorithm"],
            "description": "Hash multiple data items in batch"
        },
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        self.hash_generator = HashGenerator()
        
        # Create operation dispatch map
        self.operation_dispatch = {
            HashOperation.MD5: self._handle_md5,
            HashOperation.SHA1: self._handle_sha1,
            HashOperation.SHA224: self._handle_sha224,
            HashOperation.SHA256: self._handle_sha256,
            HashOperation.SHA384: self._handle_sha384,
            HashOperation.SHA512: self._handle_sha512,
            HashOperation.SHA3_224: self._handle_sha3_224,
            HashOperation.SHA3_256: self._handle_sha3_256,
            HashOperation.SHA3_384: self._handle_sha3_384,
            HashOperation.SHA3_512: self._handle_sha3_512,
            HashOperation.BCRYPT: self._handle_bcrypt,
            HashOperation.SCRYPT: self._handle_scrypt,
            HashOperation.PBKDF2: self._handle_pbkdf2,
            HashOperation.ARGON2: self._handle_argon2,
            HashOperation.HMAC_MD5: self._handle_hmac_md5,
            HashOperation.HMAC_SHA1: self._handle_hmac_sha1,
            HashOperation.HMAC_SHA256: self._handle_hmac_sha256,
            HashOperation.HMAC_SHA512: self._handle_hmac_sha512,
            HashOperation.FILE_MD5: self._handle_file_md5,
            HashOperation.FILE_SHA256: self._handle_file_sha256,
            HashOperation.FILE_CHECKSUM: self._handle_file_checksum,
            HashOperation.CRC32: self._handle_crc32,
            HashOperation.ADLER32: self._handle_adler32,
            HashOperation.VERIFY_HASH: self._handle_verify_hash,
            HashOperation.VERIFY_PASSWORD: self._handle_verify_password,
            HashOperation.COMPARE_HASHES: self._handle_compare_hashes,
            HashOperation.BATCH_HASH: self._handle_batch_hash,
            HashOperation.MULTI_HASH: self._handle_multi_hash,
            HashOperation.HASH_INFO: self._handle_hash_info,
            HashOperation.GENERATE_SALT: self._handle_generate_salt,
            HashOperation.STRENGTH_CHECK: self._handle_strength_check,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the schema for HashNode."""
        return NodeSchema(
            name="HashNode",
            node_type="hash",
            description="Comprehensive hash generation and verification",
            version="1.0.0",
            parameters=[
                NodeParameter(
                    name="operation",
                    type="string",
                    description="The hash operation to perform",
                    required=True,
                    enum=[op.value for op in HashOperation]
                ),
                NodeParameter(
                    name="data",
                    type="string",
                    description="Data to hash",
                    required=False
                ),
                NodeParameter(
                    name="password",
                    type="string",
                    description="Password to hash",
                    required=False
                ),
                NodeParameter(
                    name="key",
                    type="string",
                    description="Key for HMAC operations",
                    required=False
                ),
                NodeParameter(
                    name="file_path",
                    type="string",
                    description="Path to file for hashing",
                    required=False
                ),
                NodeParameter(
                    name="algorithm",
                    type="string",
                    description="Hash algorithm to use",
                    required=False,
                    enum=["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_224", "sha3_256", "sha3_384", "sha3_512"]
                ),
                NodeParameter(
                    name="encoding",
                    type="string",
                    description="Text encoding for string data",
                    required=False,
                    default="utf-8"
                ),
                NodeParameter(
                    name="output_format",
                    type="string",
                    description="Output format for hash",
                    required=False,
                    enum=["hex", "base64", "bytes"],
                    default="hex"
                ),
                NodeParameter(
                    name="rounds",
                    type="number",
                    description="Number of rounds for bcrypt",
                    required=False,
                    default=12
                ),
                NodeParameter(
                    name="iterations",
                    type="number",
                    description="Number of iterations for PBKDF2",
                    required=False,
                    default=100000
                ),
                NodeParameter(
                    name="salt",
                    type="string",
                    description="Salt for password hashing",
                    required=False
                ),
                NodeParameter(
                    name="chunk_size",
                    type="number",
                    description="Chunk size for file processing",
                    required=False,
                    default=8192
                ),
                NodeParameter(
                    name="expected_hash",
                    type="string",
                    description="Expected hash for verification",
                    required=False
                ),
                NodeParameter(
                    name="hashed",
                    type="string",
                    description="Stored hash for password verification",
                    required=False
                ),
                NodeParameter(
                    name="hash1",
                    type="string",
                    description="First hash for comparison",
                    required=False
                ),
                NodeParameter(
                    name="hash2",
                    type="string",
                    description="Second hash for comparison",
                    required=False
                ),
                NodeParameter(
                    name="data_list",
                    type="array",
                    description="List of data items for batch processing",
                    required=False
                ),
                NodeParameter(
                    name="algorithms",
                    type="array",
                    description="List of algorithms for multi-hash",
                    required=False
                ),
                NodeParameter(
                    name="length",
                    type="number",
                    description="Length for salt generation",
                    required=False,
                    default=32
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "hash": NodeParameterType.STRING,
                "hashes": NodeParameterType.OBJECT,
                "valid": NodeParameterType.BOOLEAN,
                "algorithm": NodeParameterType.STRING,
                "performance": NodeParameterType.OBJECT,
                "timestamp": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, data: Dict[str, Any]) -> None:
        """Custom validation for hash operations."""
        params = data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation parameter is required")
        
        if operation not in [op.value for op in HashOperation]:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Get operation metadata
        metadata = self.OPERATION_METADATA.get(operation, {})
        required_params = metadata.get("required", [])
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                raise ValueError(f"Required parameter '{param}' missing for operation '{operation}'")
        
        # Operation-specific validation
        if operation == HashOperation.BCRYPT:
            if not BCRYPT_AVAILABLE:
                raise ValueError("bcrypt library not available")
            
            rounds = params.get("rounds", 12)
            if not isinstance(rounds, int) or rounds < 4 or rounds > 31:
                raise ValueError("bcrypt rounds must be between 4 and 31")
        
        if operation == HashOperation.PBKDF2:
            iterations = params.get("iterations", 100000)
            if not isinstance(iterations, int) or iterations < 1000:
                raise ValueError("PBKDF2 iterations must be at least 1000")
        
        if operation in [HashOperation.FILE_MD5, HashOperation.FILE_SHA256, HashOperation.FILE_CHECKSUM]:
            file_path = params.get("file_path")
            if not file_path or not isinstance(file_path, str):
                raise ValueError("file_path must be a non-empty string")
        
        if operation == HashOperation.BATCH_HASH:
            data_list = params.get("data_list")
            if not data_list or not isinstance(data_list, list):
                raise ValueError("data_list must be a non-empty list")
            if len(data_list) > 1000:
                raise ValueError("data_list cannot exceed 1000 items for performance reasons")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a hash operation."""
        try:
            params = data.get("params", {})
            operation = params.get("operation")
            
            self.logger.info(f"Executing hash operation: {operation}")
            
            # Get operation handler
            handler = self.operation_dispatch.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Unsupported hash operation: {operation}",
                    "operation": operation
                }
            
            # Execute operation
            result = await handler(params)
            
            self.logger.info(f"Hash operation {operation} completed successfully")
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except HashError as e:
            error_msg = f"Hash operation error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
        except Exception as e:
            error_msg = f"Hash operation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
    
    # Standard Hash Operations
    async def _handle_md5(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MD5 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "md5", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "md5",
            "data_length": len(data),
            "output_format": output_format,
            "warning": "MD5 is cryptographically broken, use for non-security purposes only"
        }
    
    async def _handle_sha1(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA-1 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha1", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha1",
            "data_length": len(data),
            "output_format": output_format,
            "warning": "SHA-1 is deprecated for security, use SHA-2 or SHA-3 instead"
        }
    
    async def _handle_sha224(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA-224 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha224", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha224",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha256(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA-256 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha256", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha256",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha384(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA-384 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha384", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha384",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha512(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA-512 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha512", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha512",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha3_224(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA3-224 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha3_224", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha3_224",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha3_256(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA3-256 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha3_256", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha3_256",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha3_384(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA3-384 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha3_384", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha3_384",
            "data_length": len(data),
            "output_format": output_format
        }
    
    async def _handle_sha3_512(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SHA3-512 hash operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        output_format = params.get("output_format", "hex")
        
        hash_result = self.hash_generator.hash_data(data, "sha3_512", encoding, output_format)
        return {
            "hash": hash_result,
            "algorithm": "sha3_512",
            "data_length": len(data),
            "output_format": output_format
        }
    
    # Password Hashing Operations
    async def _handle_bcrypt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bcrypt password hashing."""
        password = params["password"]
        rounds = params.get("rounds", 12)
        
        start_time = time.time()
        hashed = self.hash_generator.hash_password_bcrypt(password, rounds)
        end_time = time.time()
        
        return {
            "hash": hashed,
            "algorithm": "bcrypt",
            "rounds": rounds,
            "hashing_time": round(end_time - start_time, 4),
            "password_length": len(password),
            "hash_length": len(hashed)
        }
    
    async def _handle_scrypt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scrypt password hashing."""
        if not SCRYPT_AVAILABLE:
            raise HashError("scrypt library not available")
        
        # Implementation would go here
        return {"message": "scrypt operation not yet implemented"}
    
    async def _handle_pbkdf2(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PBKDF2 password hashing."""
        password = params["password"]
        salt = params.get("salt")
        iterations = params.get("iterations", 100000)
        algorithm = params.get("algorithm", "sha256")
        
        if salt:
            salt_bytes = base64.b64decode(salt)
        else:
            salt_bytes = None
        
        start_time = time.time()
        result = self.hash_generator.hash_password_pbkdf2(password, salt_bytes, iterations, algorithm)
        end_time = time.time()
        
        result["hashing_time"] = round(end_time - start_time, 4)
        result["password_length"] = len(password)
        
        return result
    
    async def _handle_argon2(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Argon2 password hashing."""
        if not ARGON2_AVAILABLE:
            raise HashError("argon2 library not available")
        
        # Implementation would go here
        return {"message": "argon2 operation not yet implemented"}
    
    # HMAC Operations
    async def _handle_hmac_md5(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HMAC-MD5 operation."""
        data = params["data"]
        key = params["key"]
        encoding = params.get("encoding", "utf-8")
        
        hmac_result = self.hash_generator.generate_hmac(data, key, "md5", encoding)
        return {
            "hmac": hmac_result,
            "algorithm": "hmac_md5",
            "data_length": len(data),
            "key_length": len(key),
            "warning": "HMAC-MD5 is not recommended for security purposes"
        }
    
    async def _handle_hmac_sha1(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HMAC-SHA1 operation."""
        data = params["data"]
        key = params["key"]
        encoding = params.get("encoding", "utf-8")
        
        hmac_result = self.hash_generator.generate_hmac(data, key, "sha1", encoding)
        return {
            "hmac": hmac_result,
            "algorithm": "hmac_sha1",
            "data_length": len(data),
            "key_length": len(key),
            "warning": "HMAC-SHA1 is deprecated for security purposes"
        }
    
    async def _handle_hmac_sha256(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HMAC-SHA256 operation."""
        data = params["data"]
        key = params["key"]
        encoding = params.get("encoding", "utf-8")
        
        hmac_result = self.hash_generator.generate_hmac(data, key, "sha256", encoding)
        return {
            "hmac": hmac_result,
            "algorithm": "hmac_sha256",
            "data_length": len(data),
            "key_length": len(key)
        }
    
    async def _handle_hmac_sha512(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HMAC-SHA512 operation."""
        data = params["data"]
        key = params["key"]
        encoding = params.get("encoding", "utf-8")
        
        hmac_result = self.hash_generator.generate_hmac(data, key, "sha512", encoding)
        return {
            "hmac": hmac_result,
            "algorithm": "hmac_sha512",
            "data_length": len(data),
            "key_length": len(key)
        }
    
    # File Operations
    async def _handle_file_md5(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file MD5 operation."""
        file_path = params["file_path"]
        chunk_size = params.get("chunk_size", 8192)
        
        result = self.hash_generator.hash_file(file_path, "md5", chunk_size)
        result["warning"] = "MD5 is cryptographically broken, use for non-security purposes only"
        return result
    
    async def _handle_file_sha256(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file SHA-256 operation."""
        file_path = params["file_path"]
        chunk_size = params.get("chunk_size", 8192)
        
        return self.hash_generator.hash_file(file_path, "sha256", chunk_size)
    
    async def _handle_file_checksum(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file checksum operation."""
        file_path = params["file_path"]
        algorithm = params.get("algorithm", "sha256")
        chunk_size = params.get("chunk_size", 8192)
        
        return self.hash_generator.hash_file(file_path, algorithm, chunk_size)
    
    # Checksum Operations
    async def _handle_crc32(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CRC32 checksum operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        
        crc32_result = self.hash_generator.calculate_crc32(data, encoding)
        return {
            "crc32": crc32_result,
            "crc32_hex": f"{crc32_result:08x}",
            "algorithm": "crc32",
            "data_length": len(data)
        }
    
    async def _handle_adler32(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Adler32 checksum operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        
        adler32_result = self.hash_generator.calculate_adler32(data, encoding)
        return {
            "adler32": adler32_result,
            "adler32_hex": f"{adler32_result:08x}",
            "algorithm": "adler32",
            "data_length": len(data)
        }
    
    # Verification Operations
    async def _handle_verify_hash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hash verification operation."""
        data = params["data"]
        expected_hash = params["expected_hash"]
        algorithm = params.get("algorithm", "sha256")
        
        return self.hash_generator.verify_hash(data, expected_hash, algorithm)
    
    async def _handle_verify_password(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle password verification operation."""
        password = params["password"]
        hashed = params["hashed"]
        hash_type = params.get("hash_type", "bcrypt")
        
        start_time = time.time()
        
        if hash_type == "bcrypt":
            is_valid = self.hash_generator.verify_password_bcrypt(password, hashed)
        elif hash_type == "pbkdf2":
            salt = params.get("salt")
            iterations = params.get("iterations", 100000)
            algorithm = params.get("algorithm", "sha256")
            is_valid = self.hash_generator.verify_password_pbkdf2(password, hashed, salt, iterations, algorithm)
        else:
            raise HashError(f"Unsupported hash type for verification: {hash_type}")
        
        end_time = time.time()
        
        return {
            "valid": is_valid,
            "hash_type": hash_type,
            "verification_time": round(end_time - start_time, 4),
            "password_length": len(password),
            "hash_length": len(hashed)
        }
    
    async def _handle_compare_hashes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hash comparison operation."""
        hash1 = params["hash1"]
        hash2 = params["hash2"]
        
        return self.hash_generator.compare_hashes(hash1, hash2)
    
    # Batch Operations
    async def _handle_batch_hash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch hash operation."""
        data_list = params["data_list"]
        algorithm = params.get("algorithm", "sha256")
        
        start_time = time.time()
        results = self.hash_generator.batch_hash(data_list, algorithm)
        end_time = time.time()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(data_list),
            "successful": successful,
            "failed": failed,
            "algorithm": algorithm,
            "processing_time": round(end_time - start_time, 4),
            "rate": round(len(data_list) / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_multi_hash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multi-hash operation."""
        data = params["data"]
        algorithms = params.get("algorithms", ["md5", "sha1", "sha256", "sha512"])
        
        start_time = time.time()
        results = self.hash_generator.multi_hash(data, algorithms)
        end_time = time.time()
        
        return {
            "hashes": results,
            "data_length": len(data),
            "algorithms_used": algorithms,
            "processing_time": round(end_time - start_time, 4)
        }
    
    # Utility Operations
    async def _handle_hash_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hash info operation."""
        algorithm = params.get("algorithm", "sha256")
        
        return self.hash_generator.get_hash_info(algorithm)
    
    async def _handle_generate_salt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle salt generation operation."""
        length = params.get("length", 32)
        output_format = params.get("output_format", "hex")
        
        salt = self.hash_generator.generate_salt(length, output_format)
        return {
            "salt": salt,
            "length": length,
            "output_format": output_format,
            "entropy_bits": length * 8
        }
    
    async def _handle_strength_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hash strength check operation."""
        algorithm = params.get("algorithm", "sha256")
        
        # Simple strength assessment
        strength_ratings = {
            "md5": {"rating": "weak", "score": 1, "recommendation": "Do not use for security"},
            "sha1": {"rating": "weak", "score": 2, "recommendation": "Deprecated, use SHA-2 or SHA-3"},
            "sha224": {"rating": "good", "score": 7, "recommendation": "Good for most applications"},
            "sha256": {"rating": "strong", "score": 9, "recommendation": "Recommended for security"},
            "sha384": {"rating": "strong", "score": 9, "recommendation": "Strong security"},
            "sha512": {"rating": "strong", "score": 10, "recommendation": "Excellent security"},
            "sha3_224": {"rating": "strong", "score": 8, "recommendation": "Modern and secure"},
            "sha3_256": {"rating": "strong", "score": 9, "recommendation": "Modern and secure"},
            "sha3_384": {"rating": "strong", "score": 9, "recommendation": "Modern and secure"},
            "sha3_512": {"rating": "strong", "score": 10, "recommendation": "Excellent modern security"},
        }
        
        return {
            "algorithm": algorithm,
            "strength": strength_ratings.get(algorithm, {"rating": "unknown", "score": 0, "recommendation": "Unknown algorithm"}),
            "available_algorithms": list(strength_ratings.keys())
        }