#!/usr/bin/env python3
"""
Sanitization Node for ACT Workflow System

This node provides comprehensive data sanitization capabilities including:
- Input validation and sanitization
- HTML/XML sanitization
- SQL injection prevention
- XSS protection
- Path traversal prevention
- Email and URL validation
- File type validation
- Content filtering
- Data masking and anonymization
- Security policy enforcement
"""

import re
import html
import urllib.parse
import time
import hashlib
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import mimetypes

try:
    from base_node import BaseNode
except ImportError:
    # Try to import BaseNode from the current directory
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from base_node import BaseNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SanitizationError(Exception):
    """Custom exception for sanitization errors."""
    pass

class SanitizationOperation(str, Enum):
    """Enumeration of all sanitization operations."""
    
    # Input Validation
    VALIDATE_EMAIL = "validate_email"
    VALIDATE_URL = "validate_url"
    VALIDATE_PHONE = "validate_phone"
    VALIDATE_IP = "validate_ip"
    VALIDATE_DOMAIN = "validate_domain"
    VALIDATE_FILE_TYPE = "validate_file_type"
    VALIDATE_JSON = "validate_json"
    VALIDATE_XML = "validate_xml"
    
    # HTML/XML Sanitization
    SANITIZE_HTML = "sanitize_html"
    STRIP_HTML = "strip_html"
    ESCAPE_HTML = "escape_html"
    UNESCAPE_HTML = "unescape_html"
    SANITIZE_XML = "sanitize_xml"
    
    # Security Sanitization
    PREVENT_XSS = "prevent_xss"
    PREVENT_SQL_INJECTION = "prevent_sql_injection"
    PREVENT_PATH_TRAVERSAL = "prevent_path_traversal"
    SANITIZE_FILENAME = "sanitize_filename"
    VALIDATE_CSRF_TOKEN = "validate_csrf_token"
    
    # Content Filtering
    FILTER_PROFANITY = "filter_profanity"
    FILTER_SENSITIVE_DATA = "filter_sensitive_data"
    REMOVE_METADATA = "remove_metadata"
    WHITELIST_CHARS = "whitelist_chars"
    BLACKLIST_CHARS = "blacklist_chars"
    
    # Data Masking
    MASK_EMAIL = "mask_email"
    MASK_PHONE = "mask_phone"
    MASK_CREDIT_CARD = "mask_credit_card"
    MASK_SSN = "mask_ssn"
    MASK_CUSTOM = "mask_custom"
    
    # Encoding/Decoding
    URL_ENCODE = "url_encode"
    URL_DECODE = "url_decode"
    BASE64_ENCODE = "base64_encode"
    BASE64_DECODE = "base64_decode"
    
    # Advanced Operations
    NORMALIZE_UNICODE = "normalize_unicode"
    CLEAN_WHITESPACE = "clean_whitespace"
    EXTRACT_SAFE_TEXT = "extract_safe_text"
    BATCH_SANITIZE = "batch_sanitize"
    POLICY_ENFORCE = "policy_enforce"

class SanitizationProcessor:
    """Core sanitization processing engine."""
    
    def __init__(self):
        # Regex patterns for validation
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.url_pattern = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$')
        self.phone_pattern = re.compile(r'^[\+]?[1-9]?[\d\-\(\)\s]{8,20}$')
        self.ip_pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        self.domain_pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')
        
        # XSS prevention patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
            r'(\b(?:OR|AND)\b\s+\d+\s*=\s*\d+)',
            r'(\b(?:OR|AND)\b\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
            r'(--|#|/\*|\*/)',
            r'(;|\||&)',
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'%252e%252e%252f',
            r'%252e%252e%255c',
        ]
        
        # Common profanity list (basic implementation)
        self.profanity_list = [
            'badword1', 'badword2', 'profanity1', 'profanity2'
        ]
        
        # Sensitive data patterns
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.credit_card_pattern = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
        self.phone_sensitive_pattern = re.compile(r'\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b')
    
    # Validation Operations
    def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate email address format."""
        is_valid = bool(self.email_pattern.match(email))
        return {
            'valid': is_valid,
            'email': email,
            'domain': email.split('@')[1] if '@' in email else None
        }
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL format and structure."""
        is_valid = bool(self.url_pattern.match(url))
        parsed = urllib.parse.urlparse(url) if is_valid else None
        
        return {
            'valid': is_valid,
            'url': url,
            'scheme': parsed.scheme if parsed else None,
            'domain': parsed.netloc if parsed else None,
            'path': parsed.path if parsed else None,
            'query': parsed.query if parsed else None
        }
    
    def validate_phone(self, phone: str) -> Dict[str, Any]:
        """Validate phone number format."""
        is_valid = bool(self.phone_pattern.match(phone))
        return {
            'valid': is_valid,
            'phone': phone,
            'normalized': re.sub(r'[^\d+]', '', phone) if is_valid else None
        }
    
    def validate_ip(self, ip: str) -> Dict[str, Any]:
        """Validate IP address format."""
        is_valid = bool(self.ip_pattern.match(ip))
        return {
            'valid': is_valid,
            'ip': ip,
            'type': 'ipv4' if is_valid else None
        }
    
    def validate_domain(self, domain: str) -> Dict[str, Any]:
        """Validate domain name format."""
        is_valid = bool(self.domain_pattern.match(domain))
        return {
            'valid': is_valid,
            'domain': domain,
            'tld': domain.split('.')[-1] if is_valid else None
        }
    
    def validate_file_type(self, filename: str, allowed_types: List[str]) -> Dict[str, Any]:
        """Validate file type against allowed types."""
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(filename)
        
        is_valid = extension in [f'.{t}' if not t.startswith('.') else t for t in allowed_types]
        
        return {
            'valid': is_valid,
            'filename': filename,
            'extension': extension,
            'mime_type': mime_type,
            'allowed_types': allowed_types
        }
    
    def validate_json(self, json_str: str) -> Dict[str, Any]:
        """Validate JSON format."""
        import json
        try:
            data = json.loads(json_str)
            return {
                'valid': True,
                'data': data,
                'type': type(data).__name__
            }
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'error': str(e),
                'data': None
            }
    
    def validate_xml(self, xml_str: str) -> Dict[str, Any]:
        """Validate XML format."""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_str)
            return {
                'valid': True,
                'root_tag': root.tag,
                'children_count': len(root)
            }
        except ET.ParseError as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    # HTML/XML Sanitization
    def sanitize_html(self, html_content: str, allowed_tags: List[str] = None) -> str:
        """Sanitize HTML content by removing dangerous elements."""
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'i', 'b', 'span', 'div']
        
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove dangerous attributes
        html_content = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove javascript: links
        html_content = re.sub(r'javascript:', '', html_content, flags=re.IGNORECASE)
        
        # Filter allowed tags (basic implementation)
        if allowed_tags:
            # This is a simplified approach - in production, use a proper HTML sanitizer like bleach
            tag_pattern = r'</?([a-zA-Z]+)[^>]*>'
            def tag_filter(match):
                tag = match.group(1).lower()
                return match.group(0) if tag in allowed_tags else ''
            html_content = re.sub(tag_pattern, tag_filter, html_content)
        
        return html_content
    
    def strip_html(self, html_content: str) -> str:
        """Strip all HTML tags from content."""
        return re.sub(r'<[^>]+>', '', html_content)
    
    def escape_html(self, content: str) -> str:
        """Escape HTML special characters."""
        return html.escape(content, quote=True)
    
    def unescape_html(self, content: str) -> str:
        """Unescape HTML entities."""
        return html.unescape(content)
    
    def sanitize_xml(self, xml_content: str) -> str:
        """Sanitize XML content by removing potentially dangerous elements."""
        # Remove CDATA sections that might contain scripts
        xml_content = re.sub(r'<!\[CDATA\[.*?\]\]>', '', xml_content, flags=re.DOTALL)
        
        # Remove processing instructions
        xml_content = re.sub(r'<\?.*?\?>', '', xml_content, flags=re.DOTALL)
        
        # Remove comments
        xml_content = re.sub(r'<!--.*?-->', '', xml_content, flags=re.DOTALL)
        
        return xml_content
    
    # Security Sanitization
    def prevent_xss(self, content: str) -> str:
        """Prevent XSS attacks by removing/escaping dangerous patterns."""
        for pattern in self.xss_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Escape remaining HTML
        content = self.escape_html(content)
        
        return content
    
    def prevent_sql_injection(self, content: str) -> str:
        """Prevent SQL injection by escaping dangerous patterns."""
        for pattern in self.sql_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Escape single quotes
        content = content.replace("'", "''")
        
        return content
    
    def prevent_path_traversal(self, path: str) -> str:
        """Prevent path traversal attacks."""
        for pattern in self.path_traversal_patterns:
            path = re.sub(pattern, '', path, flags=re.IGNORECASE)
        
        # Normalize path
        path = str(Path(path).resolve())
        
        return path
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing dangerous characters."""
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename
    
    def validate_csrf_token(self, token: str, expected_token: str) -> bool:
        """Validate CSRF token."""
        return token == expected_token
    
    # Content Filtering
    def filter_profanity(self, content: str, replacement: str = '***') -> str:
        """Filter profanity from content."""
        for word in self.profanity_list:
            content = re.sub(rf'\b{re.escape(word)}\b', replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def filter_sensitive_data(self, content: str) -> str:
        """Filter sensitive data patterns."""
        # Mask SSN
        content = self.ssn_pattern.sub('XXX-XX-XXXX', content)
        
        # Mask credit card
        content = self.credit_card_pattern.sub('XXXX-XXXX-XXXX-XXXX', content)
        
        # Mask phone numbers
        content = self.phone_sensitive_pattern.sub('XXX-XXX-XXXX', content)
        
        return content
    
    def remove_metadata(self, content: str) -> str:
        """Remove metadata and comments."""
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Remove XML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        return content
    
    def whitelist_chars(self, content: str, allowed_chars: str) -> str:
        """Keep only whitelisted characters."""
        return ''.join(c for c in content if c in allowed_chars)
    
    def blacklist_chars(self, content: str, forbidden_chars: str) -> str:
        """Remove blacklisted characters."""
        return ''.join(c for c in content if c not in forbidden_chars)
    
    # Data Masking
    def mask_email(self, email: str, mask_char: str = '*') -> str:
        """Mask email address."""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            return email
        
        masked_local = local[0] + mask_char * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"
    
    def mask_phone(self, phone: str, mask_char: str = '*') -> str:
        """Mask phone number."""
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) < 4:
            return phone
        
        masked = digits[:3] + mask_char * (len(digits) - 6) + digits[-3:]
        return re.sub(r'\d', lambda m: masked[0] if masked else m.group(), phone, count=1)
    
    def mask_credit_card(self, card_number: str, mask_char: str = '*') -> str:
        """Mask credit card number."""
        digits = re.sub(r'[^\d]', '', card_number)
        if len(digits) < 8:
            return card_number
        
        masked = digits[:4] + mask_char * (len(digits) - 8) + digits[-4:]
        return re.sub(r'\d+', masked, card_number)
    
    def mask_ssn(self, ssn: str, mask_char: str = '*') -> str:
        """Mask Social Security Number."""
        return re.sub(r'\d{3}-\d{2}-\d{4}', f'{mask_char*3}-{mask_char*2}-{mask_char*4}', ssn)
    
    def mask_custom(self, content: str, pattern: str, replacement: str) -> str:
        """Apply custom masking pattern."""
        return re.sub(pattern, replacement, content)
    
    # Encoding/Decoding
    def url_encode(self, content: str) -> str:
        """URL encode content."""
        return urllib.parse.quote(content, safe='')
    
    def url_decode(self, content: str) -> str:
        """URL decode content."""
        return urllib.parse.unquote(content)
    
    def base64_encode(self, content: str) -> str:
        """Base64 encode content."""
        import base64
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    def base64_decode(self, content: str) -> str:
        """Base64 decode content."""
        import base64
        try:
            return base64.b64decode(content).decode('utf-8')
        except Exception:
            return content
    
    # Advanced Operations
    def normalize_unicode(self, content: str, form: str = 'NFC') -> str:
        """Normalize Unicode content."""
        import unicodedata
        return unicodedata.normalize(form, content)
    
    def clean_whitespace(self, content: str) -> str:
        """Clean and normalize whitespace."""
        # Replace multiple whitespace with single space
        content = re.sub(r'\s+', ' ', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def extract_safe_text(self, content: str) -> str:
        """Extract only safe text characters."""
        # Keep only alphanumeric, basic punctuation, and whitespace
        return re.sub(r'[^\w\s\.\,\!\?\-\(\)\[\]\{\}]', '', content)
    
    def batch_sanitize(self, items: List[str], operation: str, **kwargs) -> List[Dict[str, Any]]:
        """Batch sanitize multiple items."""
        results = []
        
        for i, item in enumerate(items):
            try:
                if operation == 'sanitize_html':
                    result = self.sanitize_html(item, kwargs.get('allowed_tags'))
                elif operation == 'prevent_xss':
                    result = self.prevent_xss(item)
                elif operation == 'filter_profanity':
                    result = self.filter_profanity(item, kwargs.get('replacement', '***'))
                elif operation == 'mask_email':
                    result = self.mask_email(item, kwargs.get('mask_char', '*'))
                elif operation == 'clean_whitespace':
                    result = self.clean_whitespace(item)
                else:
                    raise SanitizationError(f"Unknown batch operation: {operation}")
                
                results.append({
                    'index': i,
                    'status': 'success',
                    'input': item,
                    'result': result,
                    'operation': operation
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input': item,
                    'error': str(e),
                    'operation': operation
                })
        
        return results
    
    def policy_enforce(self, content: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce sanitization policy."""
        result = content
        violations = []
        
        # Check maximum length
        if 'max_length' in policy and len(content) > policy['max_length']:
            violations.append(f"Content exceeds maximum length of {policy['max_length']}")
            result = result[:policy['max_length']]
        
        # Check forbidden patterns
        if 'forbidden_patterns' in policy:
            for pattern in policy['forbidden_patterns']:
                if re.search(pattern, result):
                    violations.append(f"Content contains forbidden pattern: {pattern}")
                    result = re.sub(pattern, '', result)
        
        # Check required patterns
        if 'required_patterns' in policy:
            for pattern in policy['required_patterns']:
                if not re.search(pattern, result):
                    violations.append(f"Content missing required pattern: {pattern}")
        
        # Apply automatic sanitization if enabled
        if policy.get('auto_sanitize', False):
            result = self.prevent_xss(result)
            result = self.clean_whitespace(result)
        
        return {
            'sanitized_content': result,
            'violations': violations,
            'compliant': len(violations) == 0,
            'original_length': len(content),
            'final_length': len(result)
        }

class SanitizationNode(BaseNode):
    """
    Sanitization node for ACT workflow system.
    
    Provides comprehensive data sanitization capabilities including:
    - Input validation and sanitization
    - HTML/XML sanitization
    - Security protection (XSS, SQL injection, path traversal)
    - Content filtering and data masking
    - Encoding/decoding operations
    - Policy enforcement
    """
    
    def __init__(self):
        super().__init__()
        self.processor = SanitizationProcessor()
        
        # Dispatch map for operations
        self.dispatch_map = {
            # Validation operations
            SanitizationOperation.VALIDATE_EMAIL: self._handle_validate_email,
            SanitizationOperation.VALIDATE_URL: self._handle_validate_url,
            SanitizationOperation.VALIDATE_PHONE: self._handle_validate_phone,
            SanitizationOperation.VALIDATE_IP: self._handle_validate_ip,
            SanitizationOperation.VALIDATE_DOMAIN: self._handle_validate_domain,
            SanitizationOperation.VALIDATE_FILE_TYPE: self._handle_validate_file_type,
            SanitizationOperation.VALIDATE_JSON: self._handle_validate_json,
            SanitizationOperation.VALIDATE_XML: self._handle_validate_xml,
            
            # HTML/XML sanitization
            SanitizationOperation.SANITIZE_HTML: self._handle_sanitize_html,
            SanitizationOperation.STRIP_HTML: self._handle_strip_html,
            SanitizationOperation.ESCAPE_HTML: self._handle_escape_html,
            SanitizationOperation.UNESCAPE_HTML: self._handle_unescape_html,
            SanitizationOperation.SANITIZE_XML: self._handle_sanitize_xml,
            
            # Security sanitization
            SanitizationOperation.PREVENT_XSS: self._handle_prevent_xss,
            SanitizationOperation.PREVENT_SQL_INJECTION: self._handle_prevent_sql_injection,
            SanitizationOperation.PREVENT_PATH_TRAVERSAL: self._handle_prevent_path_traversal,
            SanitizationOperation.SANITIZE_FILENAME: self._handle_sanitize_filename,
            SanitizationOperation.VALIDATE_CSRF_TOKEN: self._handle_validate_csrf_token,
            
            # Content filtering
            SanitizationOperation.FILTER_PROFANITY: self._handle_filter_profanity,
            SanitizationOperation.FILTER_SENSITIVE_DATA: self._handle_filter_sensitive_data,
            SanitizationOperation.REMOVE_METADATA: self._handle_remove_metadata,
            SanitizationOperation.WHITELIST_CHARS: self._handle_whitelist_chars,
            SanitizationOperation.BLACKLIST_CHARS: self._handle_blacklist_chars,
            
            # Data masking
            SanitizationOperation.MASK_EMAIL: self._handle_mask_email,
            SanitizationOperation.MASK_PHONE: self._handle_mask_phone,
            SanitizationOperation.MASK_CREDIT_CARD: self._handle_mask_credit_card,
            SanitizationOperation.MASK_SSN: self._handle_mask_ssn,
            SanitizationOperation.MASK_CUSTOM: self._handle_mask_custom,
            
            # Encoding/decoding
            SanitizationOperation.URL_ENCODE: self._handle_url_encode,
            SanitizationOperation.URL_DECODE: self._handle_url_decode,
            SanitizationOperation.BASE64_ENCODE: self._handle_base64_encode,
            SanitizationOperation.BASE64_DECODE: self._handle_base64_decode,
            
            # Advanced operations
            SanitizationOperation.NORMALIZE_UNICODE: self._handle_normalize_unicode,
            SanitizationOperation.CLEAN_WHITESPACE: self._handle_clean_whitespace,
            SanitizationOperation.EXTRACT_SAFE_TEXT: self._handle_extract_safe_text,
            SanitizationOperation.BATCH_SANITIZE: self._handle_batch_sanitize,
            SanitizationOperation.POLICY_ENFORCE: self._handle_policy_enforce,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for sanitization operations."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in SanitizationOperation],
                    "description": "Sanitization operation to perform"
                },
                "content": {
                    "type": "string",
                    "description": "Content to sanitize"
                },
                "email": {
                    "type": "string",
                    "description": "Email address to validate"
                },
                "url": {
                    "type": "string",
                    "description": "URL to validate"
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number to validate"
                },
                "ip": {
                    "type": "string",
                    "description": "IP address to validate"
                },
                "domain": {
                    "type": "string",
                    "description": "Domain name to validate"
                },
                "filename": {
                    "type": "string",
                    "description": "Filename to validate or sanitize"
                },
                "allowed_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allowed file types"
                },
                "json_str": {
                    "type": "string",
                    "description": "JSON string to validate"
                },
                "xml_str": {
                    "type": "string",
                    "description": "XML string to validate"
                },
                "allowed_tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allowed HTML tags"
                },
                "token": {
                    "type": "string",
                    "description": "CSRF token to validate"
                },
                "expected_token": {
                    "type": "string",
                    "description": "Expected CSRF token"
                },
                "replacement": {
                    "type": "string",
                    "description": "Replacement text for filtering"
                },
                "allowed_chars": {
                    "type": "string",
                    "description": "Characters to whitelist"
                },
                "forbidden_chars": {
                    "type": "string",
                    "description": "Characters to blacklist"
                },
                "mask_char": {
                    "type": "string",
                    "description": "Character to use for masking"
                },
                "pattern": {
                    "type": "string",
                    "description": "Custom regex pattern"
                },
                "form": {
                    "type": "string",
                    "description": "Unicode normalization form"
                },
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Items for batch processing"
                },
                "batch_operation": {
                    "type": "string",
                    "description": "Operation to apply to all items"
                },
                "policy": {
                    "type": "object",
                    "description": "Sanitization policy configuration"
                }
            },
            "required": ["operation"],
            "additionalProperties": True
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sanitization operation."""
        try:
            operation = SanitizationOperation(params["operation"])
            
            logger.info(f"Executing sanitization operation: {operation}")
            
            # Get operation handler
            handler = self.dispatch_map.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Operation {operation} not implemented"
                }
            
            # Execute operation
            start_time = time.time()
            result = await handler(params)
            end_time = time.time()
            
            logger.info(f"Sanitization operation {operation} completed successfully")
            
            return {
                "status": "success",
                "operation": operation.value,
                "result": result,
                "processing_time": round(end_time - start_time, 4),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sanitization operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"Sanitization operation error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    # Validation handlers
    async def _handle_validate_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email validation."""
        email = params["email"]
        return self.processor.validate_email(email)
    
    async def _handle_validate_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL validation."""
        url = params["url"]
        return self.processor.validate_url(url)
    
    async def _handle_validate_phone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phone validation."""
        phone = params["phone"]
        return self.processor.validate_phone(phone)
    
    async def _handle_validate_ip(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IP validation."""
        ip = params["ip"]
        return self.processor.validate_ip(ip)
    
    async def _handle_validate_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle domain validation."""
        domain = params["domain"]
        return self.processor.validate_domain(domain)
    
    async def _handle_validate_file_type(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file type validation."""
        filename = params["filename"]
        allowed_types = params.get("allowed_types", [])
        return self.processor.validate_file_type(filename, allowed_types)
    
    async def _handle_validate_json(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON validation."""
        json_str = params["json_str"]
        return self.processor.validate_json(json_str)
    
    async def _handle_validate_xml(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle XML validation."""
        xml_str = params["xml_str"]
        return self.processor.validate_xml(xml_str)
    
    # HTML/XML sanitization handlers
    async def _handle_sanitize_html(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML sanitization."""
        content = params["content"]
        allowed_tags = params.get("allowed_tags")
        result = self.processor.sanitize_html(content, allowed_tags)
        
        return {
            "sanitized_content": result,
            "original_length": len(content),
            "final_length": len(result),
            "allowed_tags": allowed_tags
        }
    
    async def _handle_strip_html(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML stripping."""
        content = params["content"]
        result = self.processor.strip_html(content)
        
        return {
            "stripped_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_escape_html(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML escaping."""
        content = params["content"]
        result = self.processor.escape_html(content)
        
        return {
            "escaped_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_unescape_html(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML unescaping."""
        content = params["content"]
        result = self.processor.unescape_html(content)
        
        return {
            "unescaped_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_sanitize_xml(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle XML sanitization."""
        content = params["content"]
        result = self.processor.sanitize_xml(content)
        
        return {
            "sanitized_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    # Security sanitization handlers
    async def _handle_prevent_xss(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle XSS prevention."""
        content = params["content"]
        result = self.processor.prevent_xss(content)
        
        return {
            "sanitized_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_prevent_sql_injection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SQL injection prevention."""
        content = params["content"]
        result = self.processor.prevent_sql_injection(content)
        
        return {
            "sanitized_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_prevent_path_traversal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle path traversal prevention."""
        content = params["content"]
        result = self.processor.prevent_path_traversal(content)
        
        return {
            "sanitized_path": result,
            "original_path": content
        }
    
    async def _handle_sanitize_filename(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filename sanitization."""
        filename = params["filename"]
        result = self.processor.sanitize_filename(filename)
        
        return {
            "sanitized_filename": result,
            "original_filename": filename
        }
    
    async def _handle_validate_csrf_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CSRF token validation."""
        token = params["token"]
        expected_token = params["expected_token"]
        result = self.processor.validate_csrf_token(token, expected_token)
        
        return {
            "valid": result,
            "token": token
        }
    
    # Content filtering handlers
    async def _handle_filter_profanity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle profanity filtering."""
        content = params["content"]
        replacement = params.get("replacement", "***")
        result = self.processor.filter_profanity(content, replacement)
        
        return {
            "filtered_content": result,
            "original_length": len(content),
            "final_length": len(result),
            "replacement": replacement
        }
    
    async def _handle_filter_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sensitive data filtering."""
        content = params["content"]
        result = self.processor.filter_sensitive_data(content)
        
        return {
            "filtered_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_remove_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle metadata removal."""
        content = params["content"]
        result = self.processor.remove_metadata(content)
        
        return {
            "cleaned_content": result,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_whitelist_chars(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle character whitelisting."""
        content = params["content"]
        allowed_chars = params["allowed_chars"]
        result = self.processor.whitelist_chars(content, allowed_chars)
        
        return {
            "filtered_content": result,
            "original_length": len(content),
            "final_length": len(result),
            "allowed_chars": allowed_chars
        }
    
    async def _handle_blacklist_chars(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle character blacklisting."""
        content = params["content"]
        forbidden_chars = params["forbidden_chars"]
        result = self.processor.blacklist_chars(content, forbidden_chars)
        
        return {
            "filtered_content": result,
            "original_length": len(content),
            "final_length": len(result),
            "forbidden_chars": forbidden_chars
        }
    
    # Data masking handlers
    async def _handle_mask_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email masking."""
        email = params.get("email") or params.get("content")
        mask_char = params.get("mask_char", "*")
        result = self.processor.mask_email(email, mask_char)
        
        return {
            "masked_email": result,
            "original_email": email,
            "mask_char": mask_char
        }
    
    async def _handle_mask_phone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phone masking."""
        phone = params.get("phone") or params.get("content")
        mask_char = params.get("mask_char", "*")
        result = self.processor.mask_phone(phone, mask_char)
        
        return {
            "masked_phone": result,
            "original_phone": phone,
            "mask_char": mask_char
        }
    
    async def _handle_mask_credit_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle credit card masking."""
        card_number = params.get("card_number") or params.get("content")
        mask_char = params.get("mask_char", "*")
        result = self.processor.mask_credit_card(card_number, mask_char)
        
        return {
            "masked_card": result,
            "original_card": card_number,
            "mask_char": mask_char
        }
    
    async def _handle_mask_ssn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SSN masking."""
        ssn = params.get("ssn") or params.get("content")
        mask_char = params.get("mask_char", "*")
        result = self.processor.mask_ssn(ssn, mask_char)
        
        return {
            "masked_ssn": result,
            "original_ssn": ssn,
            "mask_char": mask_char
        }
    
    async def _handle_mask_custom(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle custom masking."""
        content = params["content"]
        pattern = params["pattern"]
        replacement = params["replacement"]
        result = self.processor.mask_custom(content, pattern, replacement)
        
        return {
            "masked_content": result,
            "original_content": content,
            "pattern": pattern,
            "replacement": replacement
        }
    
    # Encoding/decoding handlers
    async def _handle_url_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL encoding."""
        content = params["content"]
        result = self.processor.url_encode(content)
        
        return {
            "encoded_content": result,
            "original_content": content
        }
    
    async def _handle_url_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL decoding."""
        content = params["content"]
        result = self.processor.url_decode(content)
        
        return {
            "decoded_content": result,
            "original_content": content
        }
    
    async def _handle_base64_encode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Base64 encoding."""
        content = params["content"]
        result = self.processor.base64_encode(content)
        
        return {
            "encoded_content": result,
            "original_content": content
        }
    
    async def _handle_base64_decode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Base64 decoding."""
        content = params["content"]
        result = self.processor.base64_decode(content)
        
        return {
            "decoded_content": result,
            "original_content": content
        }
    
    # Advanced operation handlers
    async def _handle_normalize_unicode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Unicode normalization."""
        content = params["content"]
        form = params.get("form", "NFC")
        result = self.processor.normalize_unicode(content, form)
        
        return {
            "normalized_content": result,
            "original_content": content,
            "form": form
        }
    
    async def _handle_clean_whitespace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle whitespace cleaning."""
        content = params["content"]
        result = self.processor.clean_whitespace(content)
        
        return {
            "cleaned_content": result,
            "original_content": content,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_extract_safe_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle safe text extraction."""
        content = params["content"]
        result = self.processor.extract_safe_text(content)
        
        return {
            "safe_text": result,
            "original_content": content,
            "original_length": len(content),
            "final_length": len(result)
        }
    
    async def _handle_batch_sanitize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch sanitization."""
        items = params["items"]
        batch_operation = params["batch_operation"]
        
        # Filter out parameters already passed
        filtered_params = {k: v for k, v in params.items() if k not in ["items", "batch_operation", "operation"]}
        
        results = self.processor.batch_sanitize(items, batch_operation, **filtered_params)
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(items),
            "successful": successful,
            "failed": failed,
            "batch_operation": batch_operation
        }
    
    async def _handle_policy_enforce(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle policy enforcement."""
        content = params["content"]
        policy = params["policy"]
        
        return self.processor.policy_enforce(content, policy)