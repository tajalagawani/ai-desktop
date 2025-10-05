#!/usr/bin/env python3
"""
Encode/Decode Node for ACT Workflow System

This node provides comprehensive encoding and decoding capabilities including:
- Base64 encoding/decoding (standard, URL-safe, custom)
- URL encoding/decoding (percent encoding, query parameters)
- HTML encoding/decoding (entities, attributes)
- JSON encoding/decoding (serialization, pretty printing)
- Hex encoding/decoding (binary to hex and vice versa)
- Binary operations (binary to text, text to binary)
- Custom encoding schemes and format conversions

Architecture:
- Dispatch map for clean operation routing
- Multiple encoding format support
- Bidirectional encode/decode operations
- Batch processing capabilities
- Error handling with format validation
- Performance optimization for large data
"""

import base64
import json
import html
import urllib.parse
import binascii
import codecs
import re
import zlib
import gzip
import time
from typing import Dict, Any, List, Optional, Union, Tuple
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
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

class EncodeDecodeOperation(str, Enum):
    """Enumeration of all supported encode/decode operations."""
    
    # Base64 Operations
    BASE64_ENCODE = "base64_encode"
    BASE64_DECODE = "base64_decode"
    BASE64_URL_ENCODE = "base64_url_encode"
    BASE64_URL_DECODE = "base64_url_decode"
    
    # URL Operations
    URL_ENCODE = "url_encode"
    URL_DECODE = "url_decode"
    URL_QUOTE = "url_quote"
    URL_UNQUOTE = "url_unquote"
    URL_QUOTE_PLUS = "url_quote_plus"
    URL_UNQUOTE_PLUS = "url_unquote_plus"
    
    # HTML Operations
    HTML_ENCODE = "html_encode"
    HTML_DECODE = "html_decode"
    HTML_ESCAPE = "html_escape"
    HTML_UNESCAPE = "html_unescape"
    
    # JSON Operations
    JSON_ENCODE = "json_encode"
    JSON_DECODE = "json_decode"
    JSON_PRETTY = "json_pretty"
    JSON_MINIFY = "json_minify"
    JSON_VALIDATE = "json_validate"
    
    # Hex Operations
    HEX_ENCODE = "hex_encode"
    HEX_DECODE = "hex_decode"
    BINARY_TO_HEX = "binary_to_hex"
    HEX_TO_BINARY = "hex_to_binary"
    
    # Binary Operations
    BINARY_ENCODE = "binary_encode"
    BINARY_DECODE = "binary_decode"
    TEXT_TO_BINARY = "text_to_binary"
    BINARY_TO_TEXT = "binary_to_text"
    
    # Character Encoding
    ENCODE_UTF8 = "encode_utf8"
    DECODE_UTF8 = "decode_utf8"
    ENCODE_ASCII = "encode_ascii"
    DECODE_ASCII = "decode_ascii"
    DETECT_ENCODING = "detect_encoding"
    CONVERT_ENCODING = "convert_encoding"
    
    # Compression
    GZIP_COMPRESS = "gzip_compress"
    GZIP_DECOMPRESS = "gzip_decompress"
    ZLIB_COMPRESS = "zlib_compress"
    ZLIB_DECOMPRESS = "zlib_decompress"
    
    # Advanced Operations
    BATCH_ENCODE = "batch_encode"
    BATCH_DECODE = "batch_decode"
    MULTI_ENCODE = "multi_encode"
    MULTI_DECODE = "multi_decode"
    
    # Utilities
    ENCODING_INFO = "encoding_info"
    VALIDATE_FORMAT = "validate_format"
    FORMAT_CONVERT = "format_convert"

class EncodeDecodeError(Exception):
    """Custom exception for encode/decode operations."""
    pass

class EncodingProcessor:
    """Comprehensive encoding and decoding utilities."""
    
    # Supported character encodings
    ENCODINGS = [
        'utf-8', 'utf-16', 'utf-32', 'ascii', 'latin-1', 'cp1252',
        'iso-8859-1', 'iso-8859-15', 'cp437', 'cp850', 'cp1251'
    ]
    
    def __init__(self):
        self.performance_stats = {}
    
    # Base64 Operations
    def base64_encode(self, data: Union[str, bytes], url_safe: bool = False, 
                     encoding: str = 'utf-8') -> str:
        """Encode data to Base64."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        if url_safe:
            return base64.urlsafe_b64encode(data).decode('ascii')
        else:
            return base64.b64encode(data).decode('ascii')
    
    def base64_decode(self, data: str, url_safe: bool = False, 
                     output_encoding: str = 'utf-8') -> Union[str, bytes]:
        """Decode Base64 data."""
        try:
            if url_safe:
                decoded = base64.urlsafe_b64decode(data)
            else:
                decoded = base64.b64decode(data)
            
            if output_encoding:
                return decoded.decode(output_encoding)
            else:
                return decoded
        except Exception as e:
            raise EncodeDecodeError(f"Base64 decode error: {str(e)}")
    
    # URL Operations
    def url_encode(self, data: str, quote_via: str = 'quote', 
                  safe: str = '', encoding: str = 'utf-8') -> str:
        """URL encode data."""
        if quote_via == 'quote':
            return urllib.parse.quote(data, safe=safe, encoding=encoding)
        elif quote_via == 'quote_plus':
            return urllib.parse.quote_plus(data, safe=safe, encoding=encoding)
        else:
            raise EncodeDecodeError(f"Unknown quote method: {quote_via}")
    
    def url_decode(self, data: str, quote_via: str = 'quote', 
                  encoding: str = 'utf-8') -> str:
        """URL decode data."""
        try:
            if quote_via == 'quote':
                return urllib.parse.unquote(data, encoding=encoding)
            elif quote_via == 'quote_plus':
                return urllib.parse.unquote_plus(data, encoding=encoding)
            else:
                raise EncodeDecodeError(f"Unknown unquote method: {quote_via}")
        except Exception as e:
            raise EncodeDecodeError(f"URL decode error: {str(e)}")
    
    # HTML Operations
    def html_encode(self, data: str, quote: bool = True) -> str:
        """HTML encode data."""
        return html.escape(data, quote=quote)
    
    def html_decode(self, data: str) -> str:
        """HTML decode data."""
        return html.unescape(data)
    
    # JSON Operations
    def json_encode(self, data: Any, pretty: bool = False, sort_keys: bool = False,
                   ensure_ascii: bool = False, separators: Optional[Tuple[str, str]] = None) -> str:
        """JSON encode data."""
        try:
            if pretty:
                return json.dumps(data, indent=2, sort_keys=sort_keys, 
                                ensure_ascii=ensure_ascii, separators=separators)
            else:
                return json.dumps(data, sort_keys=sort_keys, 
                                ensure_ascii=ensure_ascii, separators=separators)
        except Exception as e:
            raise EncodeDecodeError(f"JSON encode error: {str(e)}")
    
    def json_decode(self, data: str, strict: bool = True) -> Any:
        """JSON decode data."""
        try:
            if strict:
                return json.loads(data)
            else:
                # More lenient parsing
                return json.loads(data, strict=False)
        except Exception as e:
            raise EncodeDecodeError(f"JSON decode error: {str(e)}")
    
    def json_validate(self, data: str) -> Dict[str, Any]:
        """Validate JSON data."""
        try:
            parsed = json.loads(data)
            return {
                'valid': True,
                'data': parsed,
                'type': type(parsed).__name__,
                'size': len(data)
            }
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'error': str(e),
                'line': e.lineno,
                'column': e.colno,
                'position': e.pos
            }
    
    def json_pretty(self, data: str, indent: int = 2) -> str:
        """Pretty print JSON data."""
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=indent, sort_keys=True, ensure_ascii=False)
        except Exception as e:
            raise EncodeDecodeError(f"JSON pretty print error: {str(e)}")
    
    def json_minify(self, data: str) -> str:
        """Minify JSON data."""
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, separators=(',', ':'))
        except Exception as e:
            raise EncodeDecodeError(f"JSON minify error: {str(e)}")
    
    # Hex Operations
    def hex_encode(self, data: Union[str, bytes], encoding: str = 'utf-8', 
                  uppercase: bool = False, prefix: str = '') -> str:
        """Hex encode data."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        hex_str = data.hex()
        if uppercase:
            hex_str = hex_str.upper()
        
        return prefix + hex_str
    
    def hex_decode(self, data: str, output_encoding: str = 'utf-8',
                  remove_prefix: bool = True) -> Union[str, bytes]:
        """Hex decode data."""
        try:
            # Remove common prefixes
            if remove_prefix:
                data = data.replace('0x', '').replace('0X', '')
            
            # Remove whitespace and non-hex characters
            data = re.sub(r'[^0-9a-fA-F]', '', data)
            
            decoded = bytes.fromhex(data)
            
            if output_encoding:
                return decoded.decode(output_encoding)
            else:
                return decoded
        except Exception as e:
            raise EncodeDecodeError(f"Hex decode error: {str(e)}")
    
    # Binary Operations
    def text_to_binary(self, data: str, encoding: str = 'utf-8', 
                      separator: str = ' ') -> str:
        """Convert text to binary representation."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        binary_chars = []
        for byte in data:
            binary_chars.append(format(byte, '08b'))
        
        return separator.join(binary_chars)
    
    def binary_to_text(self, data: str, encoding: str = 'utf-8',
                      separator: str = ' ') -> str:
        """Convert binary representation to text."""
        try:
            # Remove separators and whitespace
            binary_str = data.replace(separator, '').replace(' ', '')
            
            # Ensure length is multiple of 8
            if len(binary_str) % 8 != 0:
                raise EncodeDecodeError("Binary string length must be multiple of 8")
            
            # Convert binary to bytes
            bytes_data = bytearray()
            for i in range(0, len(binary_str), 8):
                byte_str = binary_str[i:i+8]
                bytes_data.append(int(byte_str, 2))
            
            return bytes_data.decode(encoding)
        except Exception as e:
            raise EncodeDecodeError(f"Binary to text error: {str(e)}")
    
    # Character Encoding Operations
    def detect_encoding(self, data: bytes) -> Dict[str, Any]:
        """Detect character encoding of data."""
        if not CHARDET_AVAILABLE:
            # Fallback detection
            try:
                data.decode('utf-8')
                return {'encoding': 'utf-8', 'confidence': 0.8, 'language': ''}
            except:
                try:
                    data.decode('latin-1')
                    return {'encoding': 'latin-1', 'confidence': 0.6, 'language': ''}
                except:
                    return {'encoding': 'unknown', 'confidence': 0.0, 'language': ''}
        
        result = chardet.detect(data)
        return {
            'encoding': result['encoding'],
            'confidence': result['confidence'],
            'language': result.get('language', '')
        }
    
    def convert_encoding(self, data: Union[str, bytes], from_encoding: str,
                        to_encoding: str) -> str:
        """Convert data between character encodings."""
        try:
            if isinstance(data, str):
                # If input is string, assume it's correctly decoded
                encoded = data.encode(from_encoding)
            else:
                encoded = data
            
            # Decode with source encoding and encode with target encoding
            decoded = encoded.decode(from_encoding)
            return decoded.encode(to_encoding).decode(to_encoding)
        except Exception as e:
            raise EncodeDecodeError(f"Encoding conversion error: {str(e)}")
    
    # Compression Operations
    def gzip_compress(self, data: Union[str, bytes], encoding: str = 'utf-8',
                     level: int = 6) -> bytes:
        """Compress data using gzip."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        return gzip.compress(data, compresslevel=level)
    
    def gzip_decompress(self, data: bytes, encoding: str = 'utf-8') -> str:
        """Decompress gzip data."""
        try:
            decompressed = gzip.decompress(data)
            return decompressed.decode(encoding)
        except Exception as e:
            raise EncodeDecodeError(f"Gzip decompress error: {str(e)}")
    
    def zlib_compress(self, data: Union[str, bytes], encoding: str = 'utf-8',
                     level: int = 6) -> bytes:
        """Compress data using zlib."""
        if isinstance(data, str):
            data = data.encode(encoding)
        
        return zlib.compress(data, level)
    
    def zlib_decompress(self, data: bytes, encoding: str = 'utf-8') -> str:
        """Decompress zlib data."""
        try:
            decompressed = zlib.decompress(data)
            return decompressed.decode(encoding)
        except Exception as e:
            raise EncodeDecodeError(f"Zlib decompress error: {str(e)}")
    
    # Batch Operations
    def batch_encode(self, data_list: List[Union[str, bytes]], batch_operation: str,
                    **kwargs) -> List[Dict[str, Any]]:
        """Encode multiple data items in batch."""
        results = []
        
        for i, data in enumerate(data_list):
            try:
                if batch_operation == 'base64':
                    result = self.base64_encode(data, **kwargs)
                elif batch_operation == 'url':
                    result = self.url_encode(data, **kwargs)
                elif batch_operation == 'html':
                    result = self.html_encode(data, **kwargs)
                elif batch_operation == 'hex':
                    result = self.hex_encode(data, **kwargs)
                elif batch_operation == 'binary':
                    result = self.text_to_binary(data, **kwargs)
                else:
                    raise EncodeDecodeError(f"Unknown batch operation: {batch_operation}")
                
                results.append({
                    'index': i,
                    'status': 'success',
                    'input_length': len(data),
                    'output_length': len(result),
                    'result': result
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input_length': len(data) if data else 0,
                    'error': str(e)
                })
        
        return results
    
    def batch_decode(self, data_list: List[str], batch_operation: str,
                    **kwargs) -> List[Dict[str, Any]]:
        """Decode multiple data items in batch."""
        results = []
        
        for i, data in enumerate(data_list):
            try:
                if batch_operation == 'base64':
                    result = self.base64_decode(data, **kwargs)
                elif batch_operation == 'url':
                    result = self.url_decode(data, **kwargs)
                elif batch_operation == 'html':
                    result = self.html_decode(data, **kwargs)
                elif batch_operation == 'hex':
                    result = self.hex_decode(data, **kwargs)
                elif batch_operation == 'binary':
                    result = self.binary_to_text(data, **kwargs)
                else:
                    raise EncodeDecodeError(f"Unknown batch operation: {batch_operation}")
                
                results.append({
                    'index': i,
                    'status': 'success',
                    'input_length': len(data),
                    'output_length': len(result),
                    'result': result
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input_length': len(data) if data else 0,
                    'error': str(e)
                })
        
        return results
    
    # Utility Operations
    def validate_format(self, data: str, format_type: str) -> Dict[str, Any]:
        """Validate data format."""
        try:
            if format_type == 'base64':
                base64.b64decode(data)
                return {'valid': True, 'format': format_type}
            elif format_type == 'hex':
                bytes.fromhex(data.replace('0x', ''))
                return {'valid': True, 'format': format_type}
            elif format_type == 'json':
                json.loads(data)
                return {'valid': True, 'format': format_type}
            elif format_type == 'url':
                urllib.parse.unquote(data)
                return {'valid': True, 'format': format_type}
            else:
                return {'valid': False, 'error': f'Unknown format: {format_type}'}
        except Exception as e:
            return {'valid': False, 'error': str(e), 'format': format_type}
    
    def get_encoding_info(self, encoding: str) -> Dict[str, Any]:
        """Get information about a character encoding."""
        try:
            codec = codecs.lookup(encoding)
            return {
                'encoding': encoding,
                'available': True,
                'name': codec.name,
                'aliases': getattr(codec, 'aliases', []),
                'description': self._get_encoding_description(encoding)
            }
        except LookupError:
            return {
                'encoding': encoding,
                'available': False,
                'error': f'Unknown encoding: {encoding}'
            }
    
    def _get_encoding_description(self, encoding: str) -> str:
        """Get description for encoding."""
        descriptions = {
            'utf-8': 'UTF-8 - Universal character encoding, recommended for most use cases',
            'utf-16': 'UTF-16 - Unicode encoding using 16-bit units',
            'utf-32': 'UTF-32 - Unicode encoding using 32-bit units',
            'ascii': 'ASCII - 7-bit character encoding, limited to 128 characters',
            'latin-1': 'Latin-1 - Single-byte encoding for Western European languages',
            'cp1252': 'Windows-1252 - Windows character encoding for Western European languages',
            'iso-8859-1': 'ISO-8859-1 - Standard single-byte encoding for Western European languages'
        }
        return descriptions.get(encoding, f'Character encoding: {encoding}')

class EncodeDecodeNode(BaseNode):
    """
    Encode/Decode operations node for ACT workflow system.
    
    Provides comprehensive encoding and decoding capabilities including:
    - Base64 encoding/decoding (standard, URL-safe)
    - URL encoding/decoding (percent encoding)
    - HTML encoding/decoding (entity escaping)
    - JSON encoding/decoding (serialization)
    - Hex encoding/decoding (binary to hex)
    - Binary operations (text to binary)
    - Character encoding conversions
    - Compression operations (gzip, zlib)
    - Batch processing and validation
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        EncodeDecodeOperation.BASE64_ENCODE: {
            "required": ["data"],
            "optional": ["url_safe", "encoding"],
            "description": "Encode data to Base64 format"
        },
        EncodeDecodeOperation.BASE64_DECODE: {
            "required": ["data"],
            "optional": ["url_safe", "output_encoding"],
            "description": "Decode Base64 data"
        },
        EncodeDecodeOperation.URL_ENCODE: {
            "required": ["data"],
            "optional": ["quote_via", "safe", "encoding"],
            "description": "URL encode data (percent encoding)"
        },
        EncodeDecodeOperation.HTML_ENCODE: {
            "required": ["data"],
            "optional": ["quote"],
            "description": "HTML encode data (escape entities)"
        },
        EncodeDecodeOperation.JSON_ENCODE: {
            "required": ["data"],
            "optional": ["pretty", "sort_keys", "ensure_ascii"],
            "description": "JSON encode data (serialization)"
        },
        EncodeDecodeOperation.HEX_ENCODE: {
            "required": ["data"],
            "optional": ["encoding", "uppercase", "prefix"],
            "description": "Hex encode data"
        },
        EncodeDecodeOperation.BATCH_ENCODE: {
            "required": ["data_list", "batch_operation"],
            "optional": ["encoding", "url_safe"],
            "description": "Encode multiple data items in batch"
        },
        EncodeDecodeOperation.BATCH_DECODE: {
            "required": ["data_list", "batch_operation"],
            "optional": ["encoding", "output_encoding"],
            "description": "Decode multiple data items in batch"
        },
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        self.encoding_processor = EncodingProcessor()
        
        # Create operation dispatch map
        self.operation_dispatch = {
            EncodeDecodeOperation.BASE64_ENCODE: self._handle_base64_encode,
            EncodeDecodeOperation.BASE64_DECODE: self._handle_base64_decode,
            EncodeDecodeOperation.BASE64_URL_ENCODE: self._handle_base64_url_encode,
            EncodeDecodeOperation.BASE64_URL_DECODE: self._handle_base64_url_decode,
            EncodeDecodeOperation.URL_ENCODE: self._handle_url_encode,
            EncodeDecodeOperation.URL_DECODE: self._handle_url_decode,
            EncodeDecodeOperation.URL_QUOTE: self._handle_url_quote,
            EncodeDecodeOperation.URL_UNQUOTE: self._handle_url_unquote,
            EncodeDecodeOperation.URL_QUOTE_PLUS: self._handle_url_quote_plus,
            EncodeDecodeOperation.URL_UNQUOTE_PLUS: self._handle_url_unquote_plus,
            EncodeDecodeOperation.HTML_ENCODE: self._handle_html_encode,
            EncodeDecodeOperation.HTML_DECODE: self._handle_html_decode,
            EncodeDecodeOperation.HTML_ESCAPE: self._handle_html_escape,
            EncodeDecodeOperation.HTML_UNESCAPE: self._handle_html_unescape,
            EncodeDecodeOperation.JSON_ENCODE: self._handle_json_encode,
            EncodeDecodeOperation.JSON_DECODE: self._handle_json_decode,
            EncodeDecodeOperation.JSON_PRETTY: self._handle_json_pretty,
            EncodeDecodeOperation.JSON_MINIFY: self._handle_json_minify,
            EncodeDecodeOperation.JSON_VALIDATE: self._handle_json_validate,
            EncodeDecodeOperation.HEX_ENCODE: self._handle_hex_encode,
            EncodeDecodeOperation.HEX_DECODE: self._handle_hex_decode,
            EncodeDecodeOperation.BINARY_TO_HEX: self._handle_binary_to_hex,
            EncodeDecodeOperation.HEX_TO_BINARY: self._handle_hex_to_binary,
            EncodeDecodeOperation.BINARY_ENCODE: self._handle_binary_encode,
            EncodeDecodeOperation.BINARY_DECODE: self._handle_binary_decode,
            EncodeDecodeOperation.TEXT_TO_BINARY: self._handle_text_to_binary,
            EncodeDecodeOperation.BINARY_TO_TEXT: self._handle_binary_to_text,
            EncodeDecodeOperation.ENCODE_UTF8: self._handle_encode_utf8,
            EncodeDecodeOperation.DECODE_UTF8: self._handle_decode_utf8,
            EncodeDecodeOperation.ENCODE_ASCII: self._handle_encode_ascii,
            EncodeDecodeOperation.DECODE_ASCII: self._handle_decode_ascii,
            EncodeDecodeOperation.DETECT_ENCODING: self._handle_detect_encoding,
            EncodeDecodeOperation.CONVERT_ENCODING: self._handle_convert_encoding,
            EncodeDecodeOperation.GZIP_COMPRESS: self._handle_gzip_compress,
            EncodeDecodeOperation.GZIP_DECOMPRESS: self._handle_gzip_decompress,
            EncodeDecodeOperation.ZLIB_COMPRESS: self._handle_zlib_compress,
            EncodeDecodeOperation.ZLIB_DECOMPRESS: self._handle_zlib_decompress,
            EncodeDecodeOperation.BATCH_ENCODE: self._handle_batch_encode,
            EncodeDecodeOperation.BATCH_DECODE: self._handle_batch_decode,
            EncodeDecodeOperation.MULTI_ENCODE: self._handle_multi_encode,
            EncodeDecodeOperation.MULTI_DECODE: self._handle_multi_decode,
            EncodeDecodeOperation.ENCODING_INFO: self._handle_encoding_info,
            EncodeDecodeOperation.VALIDATE_FORMAT: self._handle_validate_format,
            EncodeDecodeOperation.FORMAT_CONVERT: self._handle_format_convert,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the schema for EncodeDecodeNode."""
        return NodeSchema(
            name="EncodeDecodeNode",
            node_type="encode_decode",
            description="Comprehensive encoding and decoding operations",
            version="1.0.0",
            parameters=[
                NodeParameter(
                    name="operation",
                    type="string",
                    description="The encode/decode operation to perform",
                    required=True,
                    enum=[op.value for op in EncodeDecodeOperation]
                ),
                NodeParameter(
                    name="data",
                    type="string",
                    description="Data to encode/decode",
                    required=False
                ),
                NodeParameter(
                    name="encoding",
                    type="string",
                    description="Character encoding to use",
                    required=False,
                    default="utf-8"
                ),
                NodeParameter(
                    name="output_encoding",
                    type="string",
                    description="Output character encoding",
                    required=False,
                    default="utf-8"
                ),
                NodeParameter(
                    name="url_safe",
                    type="boolean",
                    description="Use URL-safe Base64 encoding",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="quote_via",
                    type="string",
                    description="URL quote method",
                    required=False,
                    enum=["quote", "quote_plus"],
                    default="quote"
                ),
                NodeParameter(
                    name="safe",
                    type="string",
                    description="Characters to not encode in URL",
                    required=False,
                    default=""
                ),
                NodeParameter(
                    name="quote",
                    type="boolean",
                    description="Quote HTML attributes",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="pretty",
                    type="boolean",
                    description="Pretty print JSON",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="sort_keys",
                    type="boolean",
                    description="Sort JSON keys",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="ensure_ascii",
                    type="boolean",
                    description="Ensure ASCII-only JSON output",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="indent",
                    type="number",
                    description="JSON indentation level",
                    required=False,
                    default=2
                ),
                NodeParameter(
                    name="strict",
                    type="boolean",
                    description="Strict JSON parsing",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="uppercase",
                    type="boolean",
                    description="Use uppercase hex",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="prefix",
                    type="string",
                    description="Prefix for hex output",
                    required=False,
                    default=""
                ),
                NodeParameter(
                    name="separator",
                    type="string",
                    description="Separator for binary output",
                    required=False,
                    default=" "
                ),
                NodeParameter(
                    name="remove_prefix",
                    type="boolean",
                    description="Remove hex prefix when decoding",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="from_encoding",
                    type="string",
                    description="Source encoding for conversion",
                    required=False
                ),
                NodeParameter(
                    name="to_encoding",
                    type="string",
                    description="Target encoding for conversion",
                    required=False
                ),
                NodeParameter(
                    name="level",
                    type="number",
                    description="Compression level",
                    required=False,
                    default=6
                ),
                NodeParameter(
                    name="data_list",
                    type="array",
                    description="List of data items for batch processing",
                    required=False
                ),
                NodeParameter(
                    name="operations",
                    type="array",
                    description="List of operations for multi-processing",
                    required=False
                ),
                NodeParameter(
                    name="format_type",
                    type="string",
                    description="Format type for validation",
                    required=False,
                    enum=["base64", "hex", "json", "url"]
                ),
                NodeParameter(
                    name="batch_operation",
                    type="string",
                    description="Operation type for batch processing",
                    required=False,
                    enum=["base64", "url", "html", "hex", "binary"]
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "encoded": NodeParameterType.STRING,
                "decoded": NodeParameterType.STRING,
                "valid": NodeParameterType.BOOLEAN,
                "format": NodeParameterType.STRING,
                "encoding": NodeParameterType.STRING,
                "performance": NodeParameterType.OBJECT,
                "timestamp": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, data: Dict[str, Any]) -> None:
        """Custom validation for encode/decode operations."""
        params = data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation parameter is required")
        
        if operation not in [op.value for op in EncodeDecodeOperation]:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Get operation metadata
        metadata = self.OPERATION_METADATA.get(operation, {})
        required_params = metadata.get("required", [])
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                raise ValueError(f"Required parameter '{param}' missing for operation '{operation}'")
        
        # Operation-specific validation
        if operation == EncodeDecodeOperation.BATCH_ENCODE:
            data_list = params.get("data_list")
            if not data_list or not isinstance(data_list, list):
                raise ValueError("data_list must be a non-empty list")
            if len(data_list) > 1000:
                raise ValueError("data_list cannot exceed 1000 items for performance reasons")
        
        if operation == EncodeDecodeOperation.CONVERT_ENCODING:
            from_encoding = params.get("from_encoding")
            to_encoding = params.get("to_encoding")
            if not from_encoding or not to_encoding:
                raise ValueError("from_encoding and to_encoding are required for conversion")
        
        if operation == EncodeDecodeOperation.GZIP_COMPRESS:
            level = params.get("level", 6)
            if not isinstance(level, int) or level < 0 or level > 9:
                raise ValueError("Compression level must be between 0 and 9")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an encode/decode operation."""
        try:
            params = data.get("params", {})
            operation = params.get("operation")
            
            self.logger.info(f"Executing encode/decode operation: {operation}")
            
            # Get operation handler
            handler = self.operation_dispatch.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Unsupported encode/decode operation: {operation}",
                    "operation": operation
                }
            
            # Execute operation
            result = await handler(params)
            
            self.logger.info(f"Encode/decode operation {operation} completed successfully")
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except EncodeDecodeError as e:
            error_msg = f"Encode/decode operation error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
        except Exception as e:
            error_msg = f"Encode/decode operation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
    
    # Base64 Operations
    async def _handle_base64_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Base64 encode operation."""
        data = params["data"]
        url_safe = params.get("url_safe", False)
        encoding = params.get("encoding", "utf-8")
        
        start_time = time.time()
        encoded = self.encoding_processor.base64_encode(data, url_safe, encoding)
        end_time = time.time()
        
        return {
            "encoded": encoded,
            "url_safe": url_safe,
            "input_length": len(data),
            "output_length": len(encoded),
            "encoding": encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_base64_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Base64 decode operation."""
        data = params["data"]
        url_safe = params.get("url_safe", False)
        output_encoding = params.get("output_encoding", "utf-8")
        
        start_time = time.time()
        decoded = self.encoding_processor.base64_decode(data, url_safe, output_encoding)
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "url_safe": url_safe,
            "input_length": len(data),
            "output_length": len(decoded),
            "encoding": output_encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_base64_url_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Base64 URL-safe encode operation."""
        params["url_safe"] = True
        return await self._handle_base64_encode(params)
    
    async def _handle_base64_url_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Base64 URL-safe decode operation."""
        params["url_safe"] = True
        return await self._handle_base64_decode(params)
    
    # URL Operations
    async def _handle_url_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL encode operation."""
        data = params["data"]
        quote_via = params.get("quote_via", "quote")
        safe = params.get("safe", "")
        encoding = params.get("encoding", "utf-8")
        
        start_time = time.time()
        encoded = self.encoding_processor.url_encode(data, quote_via, safe, encoding)
        end_time = time.time()
        
        return {
            "encoded": encoded,
            "quote_via": quote_via,
            "safe": safe,
            "input_length": len(data),
            "output_length": len(encoded),
            "encoding": encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_url_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL decode operation."""
        data = params["data"]
        quote_via = params.get("quote_via", "quote")
        encoding = params.get("encoding", "utf-8")
        
        start_time = time.time()
        decoded = self.encoding_processor.url_decode(data, quote_via, encoding)
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "quote_via": quote_via,
            "input_length": len(data),
            "output_length": len(decoded),
            "encoding": encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_url_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL quote operation."""
        params["quote_via"] = "quote"
        return await self._handle_url_encode(params)
    
    async def _handle_url_unquote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL unquote operation."""
        params["quote_via"] = "quote"
        return await self._handle_url_decode(params)
    
    async def _handle_url_quote_plus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL quote plus operation."""
        params["quote_via"] = "quote_plus"
        return await self._handle_url_encode(params)
    
    async def _handle_url_unquote_plus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL unquote plus operation."""
        params["quote_via"] = "quote_plus"
        return await self._handle_url_decode(params)
    
    # HTML Operations
    async def _handle_html_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML encode operation."""
        data = params["data"]
        quote = params.get("quote", True)
        
        start_time = time.time()
        encoded = self.encoding_processor.html_encode(data, quote)
        end_time = time.time()
        
        return {
            "encoded": encoded,
            "quote": quote,
            "input_length": len(data),
            "output_length": len(encoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_html_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML decode operation."""
        data = params["data"]
        
        start_time = time.time()
        decoded = self.encoding_processor.html_decode(data)
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "input_length": len(data),
            "output_length": len(decoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_html_escape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML escape operation."""
        return await self._handle_html_encode(params)
    
    async def _handle_html_unescape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML unescape operation."""
        return await self._handle_html_decode(params)
    
    # JSON Operations
    async def _handle_json_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON encode operation."""
        data = params["data"]
        pretty = params.get("pretty", False)
        sort_keys = params.get("sort_keys", False)
        ensure_ascii = params.get("ensure_ascii", False)
        
        start_time = time.time()
        encoded = self.encoding_processor.json_encode(data, pretty, sort_keys, ensure_ascii)
        end_time = time.time()
        
        return {
            "encoded": encoded,
            "pretty": pretty,
            "sort_keys": sort_keys,
            "ensure_ascii": ensure_ascii,
            "input_type": type(data).__name__,
            "output_length": len(encoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_json_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON decode operation."""
        data = params["data"]
        strict = params.get("strict", True)
        
        start_time = time.time()
        decoded = self.encoding_processor.json_decode(data, strict)
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "strict": strict,
            "input_length": len(data),
            "output_type": type(decoded).__name__,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_json_pretty(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON pretty print operation."""
        data = params["data"]
        indent = params.get("indent", 2)
        
        start_time = time.time()
        pretty_json = self.encoding_processor.json_pretty(data, indent)
        end_time = time.time()
        
        return {
            "pretty_json": pretty_json,
            "indent": indent,
            "input_length": len(data),
            "output_length": len(pretty_json),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_json_minify(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON minify operation."""
        data = params["data"]
        
        start_time = time.time()
        minified = self.encoding_processor.json_minify(data)
        end_time = time.time()
        
        compression_ratio = round(len(minified) / len(data), 2)
        
        return {
            "minified": minified,
            "input_length": len(data),
            "output_length": len(minified),
            "compression_ratio": compression_ratio,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_json_validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON validate operation."""
        data = params["data"]
        
        start_time = time.time()
        validation_result = self.encoding_processor.json_validate(data)
        end_time = time.time()
        
        validation_result["processing_time"] = round(end_time - start_time, 4)
        return validation_result
    
    # Hex Operations
    async def _handle_hex_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hex encode operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        uppercase = params.get("uppercase", False)
        prefix = params.get("prefix", "")
        
        start_time = time.time()
        encoded = self.encoding_processor.hex_encode(data, encoding, uppercase, prefix)
        end_time = time.time()
        
        return {
            "encoded": encoded,
            "uppercase": uppercase,
            "prefix": prefix,
            "input_length": len(data),
            "output_length": len(encoded),
            "encoding": encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_hex_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hex decode operation."""
        data = params["data"]
        output_encoding = params.get("output_encoding", "utf-8")
        remove_prefix = params.get("remove_prefix", True)
        
        start_time = time.time()
        decoded = self.encoding_processor.hex_decode(data, output_encoding, remove_prefix)
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "remove_prefix": remove_prefix,
            "input_length": len(data),
            "output_length": len(decoded),
            "encoding": output_encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_binary_to_hex(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle binary to hex operation."""
        return await self._handle_hex_encode(params)
    
    async def _handle_hex_to_binary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hex to binary operation."""
        return await self._handle_hex_decode(params)
    
    # Binary Operations
    async def _handle_binary_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle binary encode operation."""
        return await self._handle_text_to_binary(params)
    
    async def _handle_binary_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle binary decode operation."""
        return await self._handle_binary_to_text(params)
    
    async def _handle_text_to_binary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text to binary operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        separator = params.get("separator", " ")
        
        start_time = time.time()
        binary = self.encoding_processor.text_to_binary(data, encoding, separator)
        end_time = time.time()
        
        return {
            "binary": binary,
            "separator": separator,
            "input_length": len(data),
            "output_length": len(binary),
            "encoding": encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_binary_to_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle binary to text operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        separator = params.get("separator", " ")
        
        start_time = time.time()
        text = self.encoding_processor.binary_to_text(data, encoding, separator)
        end_time = time.time()
        
        return {
            "text": text,
            "separator": separator,
            "input_length": len(data),
            "output_length": len(text),
            "encoding": encoding,
            "processing_time": round(end_time - start_time, 4)
        }
    
    # Character Encoding Operations
    async def _handle_encode_utf8(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UTF-8 encode operation."""
        data = params["data"]
        
        start_time = time.time()
        encoded = data.encode('utf-8')
        end_time = time.time()
        
        return {
            "encoded": encoded.hex(),
            "encoding": "utf-8",
            "input_length": len(data),
            "output_length": len(encoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_decode_utf8(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UTF-8 decode operation."""
        data = params["data"]
        
        start_time = time.time()
        if isinstance(data, str):
            # Assume hex-encoded bytes
            decoded = bytes.fromhex(data).decode('utf-8')
        else:
            decoded = data.decode('utf-8')
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "encoding": "utf-8",
            "input_length": len(data),
            "output_length": len(decoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_encode_ascii(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ASCII encode operation."""
        data = params["data"]
        
        start_time = time.time()
        encoded = data.encode('ascii')
        end_time = time.time()
        
        return {
            "encoded": encoded.hex(),
            "encoding": "ascii",
            "input_length": len(data),
            "output_length": len(encoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_decode_ascii(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ASCII decode operation."""
        data = params["data"]
        
        start_time = time.time()
        if isinstance(data, str):
            # Assume hex-encoded bytes
            decoded = bytes.fromhex(data).decode('ascii')
        else:
            decoded = data.decode('ascii')
        end_time = time.time()
        
        return {
            "decoded": decoded,
            "encoding": "ascii",
            "input_length": len(data),
            "output_length": len(decoded),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_detect_encoding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle encoding detection operation."""
        data = params["data"]
        
        # Convert to bytes if string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        start_time = time.time()
        detection_result = self.encoding_processor.detect_encoding(data)
        end_time = time.time()
        
        detection_result["processing_time"] = round(end_time - start_time, 4)
        detection_result["data_length"] = len(data)
        
        return detection_result
    
    async def _handle_convert_encoding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle encoding conversion operation."""
        data = params["data"]
        from_encoding = params["from_encoding"]
        to_encoding = params["to_encoding"]
        
        start_time = time.time()
        converted = self.encoding_processor.convert_encoding(data, from_encoding, to_encoding)
        end_time = time.time()
        
        return {
            "converted": converted,
            "from_encoding": from_encoding,
            "to_encoding": to_encoding,
            "input_length": len(data),
            "output_length": len(converted),
            "processing_time": round(end_time - start_time, 4)
        }
    
    # Compression Operations
    async def _handle_gzip_compress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gzip compression operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        level = params.get("level", 6)
        
        start_time = time.time()
        compressed = self.encoding_processor.gzip_compress(data, encoding, level)
        end_time = time.time()
        
        compression_ratio = round(len(compressed) / len(data), 2)
        
        return {
            "compressed": base64.b64encode(compressed).decode('ascii'),
            "compression_level": level,
            "input_length": len(data),
            "output_length": len(compressed),
            "compression_ratio": compression_ratio,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_gzip_decompress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gzip decompression operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        
        # Decode base64 if string
        if isinstance(data, str):
            data = base64.b64decode(data)
        
        start_time = time.time()
        decompressed = self.encoding_processor.gzip_decompress(data, encoding)
        end_time = time.time()
        
        return {
            "decompressed": decompressed,
            "input_length": len(data),
            "output_length": len(decompressed),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_zlib_compress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle zlib compression operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        level = params.get("level", 6)
        
        start_time = time.time()
        compressed = self.encoding_processor.zlib_compress(data, encoding, level)
        end_time = time.time()
        
        compression_ratio = round(len(compressed) / len(data), 2)
        
        return {
            "compressed": base64.b64encode(compressed).decode('ascii'),
            "compression_level": level,
            "input_length": len(data),
            "output_length": len(compressed),
            "compression_ratio": compression_ratio,
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_zlib_decompress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle zlib decompression operation."""
        data = params["data"]
        encoding = params.get("encoding", "utf-8")
        
        # Decode base64 if string
        if isinstance(data, str):
            data = base64.b64decode(data)
        
        start_time = time.time()
        decompressed = self.encoding_processor.zlib_decompress(data, encoding)
        end_time = time.time()
        
        return {
            "decompressed": decompressed,
            "input_length": len(data),
            "output_length": len(decompressed),
            "processing_time": round(end_time - start_time, 4)
        }
    
    # Batch Operations
    async def _handle_batch_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch encode operation."""
        data_list = params["data_list"]
        batch_operation = params["batch_operation"]
        
        # Filter out parameters already passed as positional arguments or not needed
        filtered_params = {k: v for k, v in params.items() if k not in ["data_list", "batch_operation", "operation"]}
        
        start_time = time.time()
        results = self.encoding_processor.batch_encode(data_list, batch_operation, **filtered_params)
        end_time = time.time()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(data_list),
            "successful": successful,
            "failed": failed,
            "batch_operation": batch_operation,
            "processing_time": round(end_time - start_time, 4),
            "rate": round(len(data_list) / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_batch_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch decode operation."""
        data_list = params["data_list"]
        batch_operation = params["batch_operation"]
        
        # Filter out parameters already passed as positional arguments or not needed
        filtered_params = {k: v for k, v in params.items() if k not in ["data_list", "batch_operation", "operation"]}
        
        start_time = time.time()
        results = self.encoding_processor.batch_decode(data_list, batch_operation, **filtered_params)
        end_time = time.time()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(data_list),
            "successful": successful,
            "failed": failed,
            "batch_operation": batch_operation,
            "processing_time": round(end_time - start_time, 4),
            "rate": round(len(data_list) / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_multi_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multi-encode operation."""
        data = params["data"]
        operations = params.get("operations", ["base64", "url", "html", "hex"])
        
        start_time = time.time()
        results = {}
        
        for operation in operations:
            try:
                if operation == "base64":
                    results[operation] = self.encoding_processor.base64_encode(data)
                elif operation == "url":
                    results[operation] = self.encoding_processor.url_encode(data)
                elif operation == "html":
                    results[operation] = self.encoding_processor.html_encode(data)
                elif operation == "hex":
                    results[operation] = self.encoding_processor.hex_encode(data)
                else:
                    results[operation] = f"Unknown operation: {operation}"
            except Exception as e:
                results[operation] = f"Error: {str(e)}"
        
        end_time = time.time()
        
        return {
            "results": results,
            "operations": operations,
            "input_length": len(data),
            "processing_time": round(end_time - start_time, 4)
        }
    
    async def _handle_multi_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multi-decode operation."""
        data = params["data"]
        operations = params.get("operations", ["base64", "url", "html", "hex"])
        
        start_time = time.time()
        results = {}
        
        for operation in operations:
            try:
                if operation == "base64":
                    results[operation] = self.encoding_processor.base64_decode(data)
                elif operation == "url":
                    results[operation] = self.encoding_processor.url_decode(data)
                elif operation == "html":
                    results[operation] = self.encoding_processor.html_decode(data)
                elif operation == "hex":
                    results[operation] = self.encoding_processor.hex_decode(data)
                else:
                    results[operation] = f"Unknown operation: {operation}"
            except Exception as e:
                results[operation] = f"Error: {str(e)}"
        
        end_time = time.time()
        
        return {
            "results": results,
            "operations": operations,
            "input_length": len(data),
            "processing_time": round(end_time - start_time, 4)
        }
    
    # Utility Operations
    async def _handle_encoding_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle encoding info operation."""
        encoding = params.get("encoding", "utf-8")
        
        return self.encoding_processor.get_encoding_info(encoding)
    
    async def _handle_validate_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle format validation operation."""
        data = params["data"]
        format_type = params["format_type"]
        
        start_time = time.time()
        validation_result = self.encoding_processor.validate_format(data, format_type)
        end_time = time.time()
        
        validation_result["processing_time"] = round(end_time - start_time, 4)
        return validation_result
    
    async def _handle_format_convert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle format conversion operation."""
        # Implementation for format conversion between different encoding formats
        return {"message": "format_convert operation not yet implemented"}