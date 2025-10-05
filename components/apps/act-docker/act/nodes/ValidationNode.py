#!/usr/bin/env python3
"""
Validation Node for ACT Workflow System

This node provides comprehensive data validation capabilities including:
- Type validation: string, number, boolean, array, object, null
- Format validation: email, URL, UUID, date, time, regex patterns
- Constraint validation: min/max, length, range, enum values
- Schema validation: JSON Schema, custom schemas, nested validation
- Business rules: custom validation functions, conditional rules
- Data quality: completeness, consistency, uniqueness checks
- Pattern matching: regex, wildcards, custom patterns
- Cross-field validation: dependencies, relationships, constraints
- Batch validation for multiple data items

All operations support custom error messages and detailed validation reports.
"""

import asyncio
import json
import re
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from urllib.parse import urlparse
import ipaddress

from base_node import BaseNode, NodeParameter, NodeParameterType, NodeSchema


class ValidationType(str, Enum):
    """Enumeration of all validation types."""
    
    # Type Validation
    IS_STRING = "is_string"
    IS_NUMBER = "is_number"
    IS_INTEGER = "is_integer"
    IS_FLOAT = "is_float"
    IS_BOOLEAN = "is_boolean"
    IS_ARRAY = "is_array"
    IS_OBJECT = "is_object"
    IS_NULL = "is_null"
    IS_UNDEFINED = "is_undefined"
    IS_FUNCTION = "is_function"
    
    # Format Validation
    IS_EMAIL = "is_email"
    IS_URL = "is_url"
    IS_UUID = "is_uuid"
    IS_DATE = "is_date"
    IS_TIME = "is_time"
    IS_DATETIME = "is_datetime"
    IS_IP = "is_ip"
    IS_IPV4 = "is_ipv4"
    IS_IPV6 = "is_ipv6"
    IS_MAC_ADDRESS = "is_mac_address"
    IS_PHONE = "is_phone"
    IS_CREDIT_CARD = "is_credit_card"
    IS_POSTAL_CODE = "is_postal_code"
    IS_ALPHA = "is_alpha"
    IS_ALPHANUMERIC = "is_alphanumeric"
    IS_NUMERIC = "is_numeric"
    IS_HEX = "is_hex"
    IS_BASE64 = "is_base64"
    IS_JSON = "is_json"
    IS_XML = "is_xml"
    
    # Constraint Validation
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    RANGE = "range"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    LENGTH = "length"
    PATTERN = "pattern"
    ENUM = "enum"
    NOT_EMPTY = "not_empty"
    NOT_NULL = "not_null"
    REQUIRED = "required"
    OPTIONAL = "optional"
    
    # String Validation
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    
    # Array Validation
    ARRAY_MIN_LENGTH = "array_min_length"
    ARRAY_MAX_LENGTH = "array_max_length"
    ARRAY_UNIQUE = "array_unique"
    ARRAY_CONTAINS = "array_contains"
    ARRAY_NOT_CONTAINS = "array_not_contains"
    
    # Object Validation
    HAS_PROPERTY = "has_property"
    PROPERTY_TYPE = "property_type"
    PROPERTY_VALUE = "property_value"
    
    # Comparison
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    
    # Advanced
    SCHEMA = "schema"
    CUSTOM = "custom"
    CONDITIONAL = "conditional"
    DEPENDENCIES = "dependencies"
    
    # Data Quality
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    UNIQUENESS = "uniqueness"
    ACCURACY = "accuracy"
    
    # Batch Operations
    BATCH_VALIDATE = "batch_validate"
    VALIDATE_ALL = "validate_all"
    VALIDATE_ANY = "validate_any"
    VALIDATE_NONE = "validate_none"


class ValidationRule:
    """Represents a validation rule with its parameters."""
    
    def __init__(self, type: ValidationType, value: Any = None, message: Optional[str] = None):
        self.type = type
        self.value = value
        self.message = message or f"Validation failed for {type.value}"


class ValidationResult:
    """Represents the result of a validation."""
    
    def __init__(self, valid: bool, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.valid = valid
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "valid": self.valid,
            "message": self.message,
            "details": self.details
        }


class DataValidator:
    """Processor class for data validation operations."""
    
    def __init__(self):
        # Common regex patterns
        self.patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "url": r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            "ipv4": r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            "ipv6": r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$',
            "mac": r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            "phone": r'^\+?[1-9]\d{1,14}$',  # E.164 format
            "alpha": r'^[a-zA-Z]+$',
            "alphanumeric": r'^[a-zA-Z0-9]+$',
            "numeric": r'^[0-9]+$',
            "hex": r'^[0-9a-fA-F]+$',
            "base64": r'^[A-Za-z0-9+/]*={0,2}$',
            "credit_card": r'^\d{13,19}$',
            "us_postal": r'^\d{5}(-\d{4})?$',
            "uk_postal": r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
            "ca_postal": r'^[A-Z]\d[A-Z] ?\d[A-Z]\d$'
        }
    
    # Type validation methods
    def is_string(self, data: Any) -> ValidationResult:
        """Validate if data is a string."""
        valid = isinstance(data, str)
        return ValidationResult(valid, "Value must be a string" if not valid else None)
    
    def is_number(self, data: Any) -> ValidationResult:
        """Validate if data is a number."""
        valid = isinstance(data, (int, float)) and not isinstance(data, bool)
        return ValidationResult(valid, "Value must be a number" if not valid else None)
    
    def is_integer(self, data: Any) -> ValidationResult:
        """Validate if data is an integer."""
        valid = isinstance(data, int) and not isinstance(data, bool)
        return ValidationResult(valid, "Value must be an integer" if not valid else None)
    
    def is_float(self, data: Any) -> ValidationResult:
        """Validate if data is a float."""
        valid = isinstance(data, float)
        return ValidationResult(valid, "Value must be a float" if not valid else None)
    
    def is_boolean(self, data: Any) -> ValidationResult:
        """Validate if data is a boolean."""
        valid = isinstance(data, bool)
        return ValidationResult(valid, "Value must be a boolean" if not valid else None)
    
    def is_array(self, data: Any) -> ValidationResult:
        """Validate if data is an array/list."""
        valid = isinstance(data, list)
        return ValidationResult(valid, "Value must be an array" if not valid else None)
    
    def is_object(self, data: Any) -> ValidationResult:
        """Validate if data is an object/dict."""
        valid = isinstance(data, dict)
        return ValidationResult(valid, "Value must be an object" if not valid else None)
    
    def is_null(self, data: Any) -> ValidationResult:
        """Validate if data is null/None."""
        valid = data is None
        return ValidationResult(valid, "Value must be null" if not valid else None)
    
    def is_undefined(self, data: Any) -> ValidationResult:
        """Validate if data is undefined (None in Python)."""
        valid = data is None
        return ValidationResult(valid, "Value must be undefined" if not valid else None)
    
    def is_function(self, data: Any) -> ValidationResult:
        """Validate if data is a function/callable."""
        valid = callable(data)
        return ValidationResult(valid, "Value must be a function" if not valid else None)
    
    # Format validation methods
    def is_email(self, data: Any) -> ValidationResult:
        """Validate if data is a valid email address."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["email"], data, re.IGNORECASE))
        return ValidationResult(valid, "Invalid email format" if not valid else None)
    
    def is_url(self, data: Any) -> ValidationResult:
        """Validate if data is a valid URL."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            result = urlparse(data)
            valid = all([result.scheme, result.netloc])
            return ValidationResult(valid, "Invalid URL format" if not valid else None)
        except Exception:
            return ValidationResult(False, "Invalid URL format")
    
    def is_uuid(self, data: Any) -> ValidationResult:
        """Validate if data is a valid UUID."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            uuid.UUID(data)
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid UUID format")
    
    def is_date(self, data: Any, format: Optional[str] = None) -> ValidationResult:
        """Validate if data is a valid date."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            if format:
                datetime.strptime(data, format)
            else:
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                    try:
                        datetime.strptime(data, fmt)
                        return ValidationResult(True)
                    except ValueError:
                        continue
                return ValidationResult(False, "Invalid date format")
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid date format")
    
    def is_time(self, data: Any, format: Optional[str] = None) -> ValidationResult:
        """Validate if data is a valid time."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            if format:
                datetime.strptime(data, format)
            else:
                # Try common time formats
                for fmt in ["%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"]:
                    try:
                        datetime.strptime(data, fmt)
                        return ValidationResult(True)
                    except ValueError:
                        continue
                return ValidationResult(False, "Invalid time format")
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid time format")
    
    def is_datetime(self, data: Any, format: Optional[str] = None) -> ValidationResult:
        """Validate if data is a valid datetime."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            if format:
                datetime.strptime(data, format)
            else:
                # Try ISO format first
                datetime.fromisoformat(data.replace('Z', '+00:00'))
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid datetime format")
    
    def is_ip(self, data: Any) -> ValidationResult:
        """Validate if data is a valid IP address (v4 or v6)."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            ipaddress.ip_address(data)
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid IP address")
    
    def is_ipv4(self, data: Any) -> ValidationResult:
        """Validate if data is a valid IPv4 address."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            ipaddress.IPv4Address(data)
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid IPv4 address")
    
    def is_ipv6(self, data: Any) -> ValidationResult:
        """Validate if data is a valid IPv6 address."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            ipaddress.IPv6Address(data)
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Invalid IPv6 address")
    
    def is_mac_address(self, data: Any) -> ValidationResult:
        """Validate if data is a valid MAC address."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["mac"], data))
        return ValidationResult(valid, "Invalid MAC address format" if not valid else None)
    
    def is_phone(self, data: Any) -> ValidationResult:
        """Validate if data is a valid phone number (E.164 format)."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["phone"], data))
        return ValidationResult(valid, "Invalid phone number format" if not valid else None)
    
    def is_credit_card(self, data: Any) -> ValidationResult:
        """Validate if data is a valid credit card number (basic check)."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s-]', '', data)
        
        if not re.match(self.patterns["credit_card"], cleaned):
            return ValidationResult(False, "Invalid credit card format")
        
        # Luhn algorithm check
        def luhn_check(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10 == 0
        
        valid = luhn_check(cleaned)
        return ValidationResult(valid, "Invalid credit card number" if not valid else None)
    
    def is_postal_code(self, data: Any, country: str = "US") -> ValidationResult:
        """Validate if data is a valid postal code."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        patterns = {
            "US": self.patterns["us_postal"],
            "UK": self.patterns["uk_postal"],
            "CA": self.patterns["ca_postal"]
        }
        
        pattern = patterns.get(country.upper())
        if not pattern:
            return ValidationResult(False, f"Unsupported country code: {country}")
        
        valid = bool(re.match(pattern, data, re.IGNORECASE))
        return ValidationResult(valid, f"Invalid {country} postal code format" if not valid else None)
    
    def is_alpha(self, data: Any) -> ValidationResult:
        """Validate if data contains only alphabetic characters."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["alpha"], data))
        return ValidationResult(valid, "Value must contain only alphabetic characters" if not valid else None)
    
    def is_alphanumeric(self, data: Any) -> ValidationResult:
        """Validate if data contains only alphanumeric characters."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["alphanumeric"], data))
        return ValidationResult(valid, "Value must contain only alphanumeric characters" if not valid else None)
    
    def is_numeric(self, data: Any) -> ValidationResult:
        """Validate if data contains only numeric characters."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["numeric"], data))
        return ValidationResult(valid, "Value must contain only numeric characters" if not valid else None)
    
    def is_hex(self, data: Any) -> ValidationResult:
        """Validate if data is a valid hexadecimal string."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["hex"], data))
        return ValidationResult(valid, "Value must be a valid hexadecimal string" if not valid else None)
    
    def is_base64(self, data: Any) -> ValidationResult:
        """Validate if data is a valid base64 string."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = bool(re.match(self.patterns["base64"], data))
        return ValidationResult(valid, "Value must be a valid base64 string" if not valid else None)
    
    def is_json(self, data: Any) -> ValidationResult:
        """Validate if data is valid JSON."""
        if isinstance(data, str):
            try:
                json.loads(data)
                return ValidationResult(True)
            except json.JSONDecodeError:
                return ValidationResult(False, "Invalid JSON format")
        else:
            # Check if data can be serialized to JSON
            try:
                json.dumps(data)
                return ValidationResult(True)
            except (TypeError, ValueError):
                return ValidationResult(False, "Value cannot be serialized to JSON")
    
    def is_xml(self, data: Any) -> ValidationResult:
        """Validate if data is valid XML (basic check)."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        # Basic XML validation
        import xml.etree.ElementTree as ET
        try:
            ET.fromstring(data)
            return ValidationResult(True)
        except ET.ParseError:
            return ValidationResult(False, "Invalid XML format")
    
    # Constraint validation methods
    def min_value(self, data: Any, min_val: Union[int, float]) -> ValidationResult:
        """Validate if data is greater than or equal to minimum value."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = data >= min_val
        return ValidationResult(valid, f"Value must be >= {min_val}" if not valid else None)
    
    def max_value(self, data: Any, max_val: Union[int, float]) -> ValidationResult:
        """Validate if data is less than or equal to maximum value."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = data <= max_val
        return ValidationResult(valid, f"Value must be <= {max_val}" if not valid else None)
    
    def range(self, data: Any, min_val: Union[int, float], max_val: Union[int, float]) -> ValidationResult:
        """Validate if data is within range."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = min_val <= data <= max_val
        return ValidationResult(valid, f"Value must be between {min_val} and {max_val}" if not valid else None)
    
    def min_length(self, data: Any, min_len: int) -> ValidationResult:
        """Validate if data has minimum length."""
        if not hasattr(data, '__len__'):
            return ValidationResult(False, "Value must have a length property")
        
        valid = len(data) >= min_len
        return ValidationResult(valid, f"Length must be >= {min_len}" if not valid else None)
    
    def max_length(self, data: Any, max_len: int) -> ValidationResult:
        """Validate if data has maximum length."""
        if not hasattr(data, '__len__'):
            return ValidationResult(False, "Value must have a length property")
        
        valid = len(data) <= max_len
        return ValidationResult(valid, f"Length must be <= {max_len}" if not valid else None)
    
    def length(self, data: Any, exact_len: int) -> ValidationResult:
        """Validate if data has exact length."""
        if not hasattr(data, '__len__'):
            return ValidationResult(False, "Value must have a length property")
        
        valid = len(data) == exact_len
        return ValidationResult(valid, f"Length must be exactly {exact_len}" if not valid else None)
    
    def pattern(self, data: Any, regex_pattern: str) -> ValidationResult:
        """Validate if data matches regex pattern."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        try:
            valid = bool(re.match(regex_pattern, data))
            return ValidationResult(valid, f"Value does not match pattern: {regex_pattern}" if not valid else None)
        except re.error:
            return ValidationResult(False, "Invalid regex pattern")
    
    def enum(self, data: Any, allowed_values: List[Any]) -> ValidationResult:
        """Validate if data is one of allowed values."""
        valid = data in allowed_values
        return ValidationResult(valid, f"Value must be one of: {allowed_values}" if not valid else None)
    
    def not_empty(self, data: Any) -> ValidationResult:
        """Validate if data is not empty."""
        if hasattr(data, '__len__'):
            valid = len(data) > 0
        else:
            valid = data is not None
        
        return ValidationResult(valid, "Value must not be empty" if not valid else None)
    
    def not_null(self, data: Any) -> ValidationResult:
        """Validate if data is not null."""
        valid = data is not None
        return ValidationResult(valid, "Value must not be null" if not valid else None)
    
    def required(self, data: Any) -> ValidationResult:
        """Validate if data is present (not None or empty)."""
        if data is None:
            return ValidationResult(False, "Value is required")
        
        if hasattr(data, '__len__') and len(data) == 0:
            return ValidationResult(False, "Value is required and cannot be empty")
        
        return ValidationResult(True)
    
    def optional(self, data: Any) -> ValidationResult:
        """Always returns valid (used for optional fields)."""
        return ValidationResult(True)
    
    # String validation methods
    def starts_with(self, data: Any, prefix: str) -> ValidationResult:
        """Validate if string starts with prefix."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = data.startswith(prefix)
        return ValidationResult(valid, f"Value must start with '{prefix}'" if not valid else None)
    
    def ends_with(self, data: Any, suffix: str) -> ValidationResult:
        """Validate if string ends with suffix."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = data.endswith(suffix)
        return ValidationResult(valid, f"Value must end with '{suffix}'" if not valid else None)
    
    def contains(self, data: Any, substring: str) -> ValidationResult:
        """Validate if string contains substring."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = substring in data
        return ValidationResult(valid, f"Value must contain '{substring}'" if not valid else None)
    
    def not_contains(self, data: Any, substring: str) -> ValidationResult:
        """Validate if string does not contain substring."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = substring not in data
        return ValidationResult(valid, f"Value must not contain '{substring}'" if not valid else None)
    
    def lowercase(self, data: Any) -> ValidationResult:
        """Validate if string is lowercase."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = data.islower() or not any(c.isalpha() for c in data)
        return ValidationResult(valid, "Value must be lowercase" if not valid else None)
    
    def uppercase(self, data: Any) -> ValidationResult:
        """Validate if string is uppercase."""
        if not isinstance(data, str):
            return ValidationResult(False, "Value must be a string")
        
        valid = data.isupper() or not any(c.isalpha() for c in data)
        return ValidationResult(valid, "Value must be uppercase" if not valid else None)
    
    # Array validation methods
    def array_min_length(self, data: Any, min_len: int) -> ValidationResult:
        """Validate if array has minimum length."""
        if not isinstance(data, list):
            return ValidationResult(False, "Value must be an array")
        
        valid = len(data) >= min_len
        return ValidationResult(valid, f"Array must have at least {min_len} items" if not valid else None)
    
    def array_max_length(self, data: Any, max_len: int) -> ValidationResult:
        """Validate if array has maximum length."""
        if not isinstance(data, list):
            return ValidationResult(False, "Value must be an array")
        
        valid = len(data) <= max_len
        return ValidationResult(valid, f"Array must have at most {max_len} items" if not valid else None)
    
    def array_unique(self, data: Any) -> ValidationResult:
        """Validate if array contains unique values."""
        if not isinstance(data, list):
            return ValidationResult(False, "Value must be an array")
        
        valid = len(data) == len(set(str(item) for item in data))
        return ValidationResult(valid, "Array must contain unique values" if not valid else None)
    
    def array_contains(self, data: Any, item: Any) -> ValidationResult:
        """Validate if array contains item."""
        if not isinstance(data, list):
            return ValidationResult(False, "Value must be an array")
        
        valid = item in data
        return ValidationResult(valid, f"Array must contain {item}" if not valid else None)
    
    def array_not_contains(self, data: Any, item: Any) -> ValidationResult:
        """Validate if array does not contain item."""
        if not isinstance(data, list):
            return ValidationResult(False, "Value must be an array")
        
        valid = item not in data
        return ValidationResult(valid, f"Array must not contain {item}" if not valid else None)
    
    # Object validation methods
    def has_property(self, data: Any, property_name: str) -> ValidationResult:
        """Validate if object has property."""
        if not isinstance(data, dict):
            return ValidationResult(False, "Value must be an object")
        
        valid = property_name in data
        return ValidationResult(valid, f"Object must have property '{property_name}'" if not valid else None)
    
    def property_type(self, data: Any, property_name: str, expected_type: str) -> ValidationResult:
        """Validate property type in object."""
        if not isinstance(data, dict):
            return ValidationResult(False, "Value must be an object")
        
        if property_name not in data:
            return ValidationResult(False, f"Object must have property '{property_name}'")
        
        value = data[property_name]
        type_validators = {
            "string": lambda x: isinstance(x, str),
            "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
            "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
            "float": lambda x: isinstance(x, float),
            "boolean": lambda x: isinstance(x, bool),
            "array": lambda x: isinstance(x, list),
            "object": lambda x: isinstance(x, dict),
            "null": lambda x: x is None
        }
        
        validator = type_validators.get(expected_type)
        if not validator:
            return ValidationResult(False, f"Unknown type: {expected_type}")
        
        valid = validator(value)
        return ValidationResult(valid, f"Property '{property_name}' must be of type {expected_type}" if not valid else None)
    
    def property_value(self, data: Any, property_name: str, expected_value: Any) -> ValidationResult:
        """Validate property value in object."""
        if not isinstance(data, dict):
            return ValidationResult(False, "Value must be an object")
        
        if property_name not in data:
            return ValidationResult(False, f"Object must have property '{property_name}'")
        
        valid = data[property_name] == expected_value
        return ValidationResult(valid, f"Property '{property_name}' must equal {expected_value}" if not valid else None)
    
    # Comparison methods
    def equals(self, data: Any, expected_value: Any) -> ValidationResult:
        """Validate if data equals expected value."""
        valid = data == expected_value
        return ValidationResult(valid, f"Value must equal {expected_value}" if not valid else None)
    
    def not_equals(self, data: Any, unexpected_value: Any) -> ValidationResult:
        """Validate if data does not equal unexpected value."""
        valid = data != unexpected_value
        return ValidationResult(valid, f"Value must not equal {unexpected_value}" if not valid else None)
    
    def greater_than(self, data: Any, value: Union[int, float]) -> ValidationResult:
        """Validate if data is greater than value."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = data > value
        return ValidationResult(valid, f"Value must be greater than {value}" if not valid else None)
    
    def less_than(self, data: Any, value: Union[int, float]) -> ValidationResult:
        """Validate if data is less than value."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = data < value
        return ValidationResult(valid, f"Value must be less than {value}" if not valid else None)
    
    def greater_or_equal(self, data: Any, value: Union[int, float]) -> ValidationResult:
        """Validate if data is greater than or equal to value."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = data >= value
        return ValidationResult(valid, f"Value must be greater than or equal to {value}" if not valid else None)
    
    def less_or_equal(self, data: Any, value: Union[int, float]) -> ValidationResult:
        """Validate if data is less than or equal to value."""
        if not isinstance(data, (int, float)):
            return ValidationResult(False, "Value must be a number")
        
        valid = data <= value
        return ValidationResult(valid, f"Value must be less than or equal to {value}" if not valid else None)
    
    # Advanced validation methods
    def validate_schema(self, data: Any, schema: Dict[str, Any]) -> ValidationResult:
        """Validate data against a schema."""
        errors = []
        
        # Validate required fields
        if "required" in schema:
            for field in schema["required"]:
                if not isinstance(data, dict) or field not in data:
                    errors.append(f"Required field '{field}' is missing")
        
        # Validate properties
        if "properties" in schema and isinstance(data, dict):
            for prop, prop_schema in schema["properties"].items():
                if prop in data:
                    prop_result = self._validate_property(data[prop], prop_schema)
                    if not prop_result.valid:
                        errors.append(f"{prop}: {prop_result.message}")
        
        valid = len(errors) == 0
        return ValidationResult(valid, "; ".join(errors) if errors else None, {"errors": errors})
    
    def _validate_property(self, value: Any, prop_schema: Dict[str, Any]) -> ValidationResult:
        """Validate a single property against its schema."""
        # Type validation
        if "type" in prop_schema:
            type_map = {
                "string": self.is_string,
                "number": self.is_number,
                "integer": self.is_integer,
                "boolean": self.is_boolean,
                "array": self.is_array,
                "object": self.is_object,
                "null": self.is_null
            }
            
            type_validator = type_map.get(prop_schema["type"])
            if type_validator:
                result = type_validator(value)
                if not result.valid:
                    return result
        
        # Additional constraints
        if "minimum" in prop_schema:
            result = self.min_value(value, prop_schema["minimum"])
            if not result.valid:
                return result
        
        if "maximum" in prop_schema:
            result = self.max_value(value, prop_schema["maximum"])
            if not result.valid:
                return result
        
        if "minLength" in prop_schema:
            result = self.min_length(value, prop_schema["minLength"])
            if not result.valid:
                return result
        
        if "maxLength" in prop_schema:
            result = self.max_length(value, prop_schema["maxLength"])
            if not result.valid:
                return result
        
        if "pattern" in prop_schema:
            result = self.pattern(value, prop_schema["pattern"])
            if not result.valid:
                return result
        
        if "enum" in prop_schema:
            result = self.enum(value, prop_schema["enum"])
            if not result.valid:
                return result
        
        return ValidationResult(True)
    
    def validate_custom(self, data: Any, func: Callable[[Any], bool], message: str = "Custom validation failed") -> ValidationResult:
        """Validate using custom function."""
        try:
            valid = func(data)
            return ValidationResult(valid, message if not valid else None)
        except Exception as e:
            return ValidationResult(False, f"Custom validation error: {str(e)}")
    
    def validate_conditional(self, data: Any, condition: Dict[str, Any], then_rules: List[ValidationRule], else_rules: Optional[List[ValidationRule]] = None) -> ValidationResult:
        """Validate conditionally based on condition."""
        # Evaluate condition
        condition_met = self._evaluate_condition(data, condition)
        
        # Apply appropriate rules
        rules_to_apply = then_rules if condition_met else (else_rules or [])
        
        for rule in rules_to_apply:
            result = self._apply_rule(data, rule)
            if not result.valid:
                return result
        
        return ValidationResult(True)
    
    def _evaluate_condition(self, data: Any, condition: Dict[str, Any]) -> bool:
        """Evaluate a condition."""
        if "equals" in condition:
            return data == condition["equals"]
        elif "not_equals" in condition:
            return data != condition["not_equals"]
        elif "greater_than" in condition:
            return isinstance(data, (int, float)) and data > condition["greater_than"]
        elif "less_than" in condition:
            return isinstance(data, (int, float)) and data < condition["less_than"]
        elif "contains" in condition:
            return isinstance(data, str) and condition["contains"] in data
        elif "property" in condition and "value" in condition:
            return isinstance(data, dict) and data.get(condition["property"]) == condition["value"]
        
        return False
    
    def _apply_rule(self, data: Any, rule: ValidationRule) -> ValidationResult:
        """Apply a validation rule."""
        method_name = rule.type.value
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if rule.value is not None:
                if isinstance(rule.value, dict):
                    return method(data, **rule.value)
                elif isinstance(rule.value, (list, tuple)):
                    return method(data, *rule.value)
                else:
                    return method(data, rule.value)
            else:
                return method(data)
        
        return ValidationResult(False, f"Unknown validation type: {rule.type}")
    
    def validate_dependencies(self, data: Any, dependencies: Dict[str, List[str]]) -> ValidationResult:
        """Validate field dependencies."""
        if not isinstance(data, dict):
            return ValidationResult(False, "Value must be an object for dependency validation")
        
        errors = []
        
        for field, required_fields in dependencies.items():
            if field in data:
                for required_field in required_fields:
                    if required_field not in data:
                        errors.append(f"Field '{field}' requires field '{required_field}'")
        
        valid = len(errors) == 0
        return ValidationResult(valid, "; ".join(errors) if errors else None)
    
    # Data quality methods
    def validate_completeness(self, data: Any, required_fields: List[str], threshold: float = 1.0) -> ValidationResult:
        """Validate data completeness."""
        if not isinstance(data, dict):
            return ValidationResult(False, "Value must be an object for completeness validation")
        
        present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
        completeness_ratio = present_fields / len(required_fields) if required_fields else 1.0
        
        valid = completeness_ratio >= threshold
        details = {
            "completeness_ratio": completeness_ratio,
            "present_fields": present_fields,
            "total_fields": len(required_fields),
            "missing_fields": [field for field in required_fields if field not in data or data[field] is None]
        }
        
        message = f"Data completeness {completeness_ratio:.1%} is below threshold {threshold:.1%}" if not valid else None
        return ValidationResult(valid, message, details)
    
    def validate_consistency(self, data: Any, rules: List[Dict[str, Any]]) -> ValidationResult:
        """Validate data consistency across fields."""
        if not isinstance(data, dict):
            return ValidationResult(False, "Value must be an object for consistency validation")
        
        errors = []
        
        for rule in rules:
            if "fields" in rule and len(rule["fields"]) >= 2:
                field1, field2 = rule["fields"][0], rule["fields"][1]
                if field1 in data and field2 in data:
                    if "relation" in rule:
                        if rule["relation"] == "equals" and data[field1] != data[field2]:
                            errors.append(f"Fields '{field1}' and '{field2}' must be equal")
                        elif rule["relation"] == "greater_than" and not (data[field1] > data[field2]):
                            errors.append(f"Field '{field1}' must be greater than '{field2}'")
                        elif rule["relation"] == "less_than" and not (data[field1] < data[field2]):
                            errors.append(f"Field '{field1}' must be less than '{field2}'")
        
        valid = len(errors) == 0
        return ValidationResult(valid, "; ".join(errors) if errors else None)
    
    def validate_uniqueness(self, data: List[Any], key: Optional[str] = None) -> ValidationResult:
        """Validate uniqueness in a list of items."""
        if not isinstance(data, list):
            return ValidationResult(False, "Value must be an array for uniqueness validation")
        
        if key and all(isinstance(item, dict) for item in data):
            # Check uniqueness by key
            values = [item.get(key) for item in data if key in item]
            unique_values = set(values)
            duplicates = len(values) - len(unique_values)
        else:
            # Check uniqueness of items
            try:
                unique_items = set(str(item) for item in data)
                duplicates = len(data) - len(unique_items)
            except TypeError:
                return ValidationResult(False, "Cannot check uniqueness for unhashable types")
        
        valid = duplicates == 0
        details = {
            "total_items": len(data),
            "unique_items": len(data) - duplicates,
            "duplicates": duplicates
        }
        
        message = f"Found {duplicates} duplicate items" if not valid else None
        return ValidationResult(valid, message, details)
    
    def validate_accuracy(self, data: Any, reference: Any, tolerance: float = 0.0) -> ValidationResult:
        """Validate data accuracy against reference."""
        if isinstance(data, (int, float)) and isinstance(reference, (int, float)):
            difference = abs(data - reference)
            valid = difference <= tolerance
            details = {
                "difference": difference,
                "tolerance": tolerance,
                "percentage_error": (difference / reference * 100) if reference != 0 else float('inf')
            }
            message = f"Value differs from reference by {difference}" if not valid else None
        elif isinstance(data, str) and isinstance(reference, str):
            valid = data == reference
            details = {"match": valid}
            message = "Value does not match reference" if not valid else None
        else:
            valid = data == reference
            details = {"match": valid}
            message = "Value does not match reference" if not valid else None
        
        return ValidationResult(valid, message, details)
    
    # Batch validation methods
    def batch_validate(self, data_list: List[Any], validation_type: ValidationType, **kwargs) -> Dict[str, Any]:
        """Validate multiple data items with same validation."""
        results = []
        successful = 0
        failed = 0
        
        for i, data in enumerate(data_list):
            try:
                method_name = validation_type.value
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    result = method(data, **kwargs)
                    results.append({
                        "index": i,
                        "data": data,
                        "valid": result.valid,
                        "message": result.message,
                        "details": result.details
                    })
                    
                    if result.valid:
                        successful += 1
                    else:
                        failed += 1
                else:
                    results.append({
                        "index": i,
                        "data": data,
                        "valid": False,
                        "message": f"Unknown validation type: {validation_type}",
                        "details": {}
                    })
                    failed += 1
            except Exception as e:
                results.append({
                    "index": i,
                    "data": data,
                    "valid": False,
                    "message": f"Validation error: {str(e)}",
                    "details": {}
                })
                failed += 1
        
        return {
            "results": results,
            "successful": successful,
            "failed": failed,
            "total": len(data_list),
            "success_rate": successful / len(data_list) if data_list else 0
        }
    
    def validate_all(self, data: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate that all rules pass."""
        errors = []
        
        for rule in rules:
            result = self._apply_rule(data, rule)
            if not result.valid:
                errors.append(result.message or f"Validation failed for {rule.type.value}")
        
        valid = len(errors) == 0
        return ValidationResult(valid, "; ".join(errors) if errors else None, {"failed_rules": errors})
    
    def validate_any(self, data: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate that at least one rule passes."""
        for rule in rules:
            result = self._apply_rule(data, rule)
            if result.valid:
                return ValidationResult(True)
        
        return ValidationResult(False, "None of the validation rules passed")
    
    def validate_none(self, data: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate that none of the rules pass."""
        failed_rules = []
        
        for rule in rules:
            result = self._apply_rule(data, rule)
            if result.valid:
                failed_rules.append(rule.type.value)
        
        valid = len(failed_rules) == 0
        message = f"The following rules should not pass: {', '.join(failed_rules)}" if failed_rules else None
        return ValidationResult(valid, message)


class ValidationNode(BaseNode):
    """
    Validation Node for comprehensive data validation.
    
    Provides 50+ validation operations including:
    - Type validation (string, number, boolean, array, object, etc.)
    - Format validation (email, URL, UUID, date, IP, phone, etc.)
    - Constraint validation (min/max, length, range, enum, pattern)
    - Schema validation (JSON Schema, custom schemas)
    - Business rules and custom validation
    - Data quality checks (completeness, consistency, uniqueness)
    - Cross-field validation and dependencies
    - Batch validation for multiple items
    """
    
    def __init__(self):
        super().__init__()
        self.validator = DataValidator()
    
    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            node_type="validation",
            version="1.0.0",
            description="Comprehensive data validation node with 50+ validation types for type checking, format validation, constraints, schemas, and data quality",
            parameters=[
                NodeParameter(
                    name="validation_type",
                    type=NodeParameterType.STRING,
                    description="Type of validation to perform",
                    required=True,
                    enum=[vt.value for vt in ValidationType]
                ),
                NodeParameter(
                    name="data",
                    type=NodeParameterType.ANY,
                    description="Data to validate",
                    required=True
                ),
                NodeParameter(
                    name="value",
                    type=NodeParameterType.ANY,
                    description="Comparison value or constraint",
                    required=False
                ),
                NodeParameter(
                    name="min_value",
                    type=NodeParameterType.NUMBER,
                    description="Minimum value for range validation",
                    required=False
                ),
                NodeParameter(
                    name="max_value",
                    type=NodeParameterType.NUMBER,
                    description="Maximum value for range validation",
                    required=False
                ),
                NodeParameter(
                    name="pattern",
                    type=NodeParameterType.STRING,
                    description="Regex pattern for pattern validation",
                    required=False
                ),
                NodeParameter(
                    name="format",
                    type=NodeParameterType.STRING,
                    description="Format string for date/time validation",
                    required=False
                ),
                NodeParameter(
                    name="country",
                    type=NodeParameterType.STRING,
                    description="Country code for postal code validation",
                    required=False,
                    default="US"
                ),
                NodeParameter(
                    name="allowed_values",
                    type=NodeParameterType.ARRAY,
                    description="Allowed values for enum validation",
                    required=False
                ),
                NodeParameter(
                    name="schema",
                    type=NodeParameterType.OBJECT,
                    description="Schema for schema validation",
                    required=False
                ),
                NodeParameter(
                    name="rules",
                    type=NodeParameterType.ARRAY,
                    description="List of validation rules",
                    required=False
                ),
                NodeParameter(
                    name="required_fields",
                    type=NodeParameterType.ARRAY,
                    description="Required fields for completeness validation",
                    required=False
                ),
                NodeParameter(
                    name="threshold",
                    type=NodeParameterType.NUMBER,
                    description="Threshold for completeness validation (0-1)",
                    required=False,
                    default=1.0
                ),
                NodeParameter(
                    name="dependencies",
                    type=NodeParameterType.OBJECT,
                    description="Field dependencies for dependency validation",
                    required=False
                ),
                NodeParameter(
                    name="key",
                    type=NodeParameterType.STRING,
                    description="Key for uniqueness validation in objects",
                    required=False
                ),
                NodeParameter(
                    name="reference",
                    type=NodeParameterType.ANY,
                    description="Reference value for accuracy validation",
                    required=False
                ),
                NodeParameter(
                    name="tolerance",
                    type=NodeParameterType.NUMBER,
                    description="Tolerance for accuracy validation",
                    required=False,
                    default=0.0
                ),
                NodeParameter(
                    name="data_list",
                    type=NodeParameterType.ARRAY,
                    description="List of data items for batch validation",
                    required=False
                ),
                NodeParameter(
                    name="message",
                    type=NodeParameterType.STRING,
                    description="Custom error message",
                    required=False
                ),
                NodeParameter(
                    name="property_name",
                    type=NodeParameterType.STRING,
                    description="Property name for object validation",
                    required=False
                ),
                NodeParameter(
                    name="expected_type",
                    type=NodeParameterType.STRING,
                    description="Expected type for property validation",
                    required=False
                ),
                NodeParameter(
                    name="expected_value",
                    type=NodeParameterType.ANY,
                    description="Expected value for property validation",
                    required=False
                ),
                NodeParameter(
                    name="prefix",
                    type=NodeParameterType.STRING,
                    description="Prefix for starts_with validation",
                    required=False
                ),
                NodeParameter(
                    name="suffix",
                    type=NodeParameterType.STRING,
                    description="Suffix for ends_with validation",
                    required=False
                ),
                NodeParameter(
                    name="substring",
                    type=NodeParameterType.STRING,
                    description="Substring for contains validation",
                    required=False
                ),
                NodeParameter(
                    name="min_length",
                    type=NodeParameterType.NUMBER,
                    description="Minimum length constraint",
                    required=False
                ),
                NodeParameter(
                    name="max_length",
                    type=NodeParameterType.NUMBER,
                    description="Maximum length constraint",
                    required=False
                ),
                NodeParameter(
                    name="exact_length",
                    type=NodeParameterType.NUMBER,
                    description="Exact length constraint",
                    required=False
                ),
                NodeParameter(
                    name="item",
                    type=NodeParameterType.ANY,
                    description="Item for array contains validation",
                    required=False
                ),
                NodeParameter(
                    name="condition",
                    type=NodeParameterType.OBJECT,
                    description="Condition for conditional validation",
                    required=False
                ),
                NodeParameter(
                    name="then_rules",
                    type=NodeParameterType.ARRAY,
                    description="Rules to apply if condition is met",
                    required=False
                ),
                NodeParameter(
                    name="else_rules",
                    type=NodeParameterType.ARRAY,
                    description="Rules to apply if condition is not met",
                    required=False
                ),
                NodeParameter(
                    name="custom_function",
                    type=NodeParameterType.STRING,
                    description="Custom validation function as string",
                    required=False
                )
            ],
            outputs={
                "valid": NodeParameterType.BOOLEAN,
                "message": NodeParameterType.STRING,
                "details": NodeParameterType.OBJECT
            },
            tags=["validation", "data", "quality", "schema", "type-checking"],
            author="System"
        )
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters based on validation type."""
        validation_type = params.get("validation_type")
        
        if not validation_type:
            return {"valid": False, "error": "validation_type is required"}
        
        if validation_type not in [vt.value for vt in ValidationType]:
            return {"valid": False, "error": f"Invalid validation type: {validation_type}"}
        
        # Check for required parameters based on validation type
        if validation_type.startswith("batch_"):
            if "data_list" not in params:
                return {"valid": False, "error": f"Validation type {validation_type} requires 'data_list' parameter"}
        else:
            if "data" not in params:
                return {"valid": False, "error": f"Validation type {validation_type} requires 'data' parameter"}
        
        return {"valid": True}
    
    # Operation metadata for parameter requirements
    OPERATION_METADATA = {
        # Type Validation
        ValidationType.IS_STRING: {"required": ["data"]},
        ValidationType.IS_NUMBER: {"required": ["data"]},
        ValidationType.IS_INTEGER: {"required": ["data"]},
        ValidationType.IS_FLOAT: {"required": ["data"]},
        ValidationType.IS_BOOLEAN: {"required": ["data"]},
        ValidationType.IS_ARRAY: {"required": ["data"]},
        ValidationType.IS_OBJECT: {"required": ["data"]},
        ValidationType.IS_NULL: {"required": ["data"]},
        ValidationType.IS_UNDEFINED: {"required": ["data"]},
        ValidationType.IS_FUNCTION: {"required": ["data"]},
        
        # Format Validation
        ValidationType.IS_EMAIL: {"required": ["data"]},
        ValidationType.IS_URL: {"required": ["data"]},
        ValidationType.IS_UUID: {"required": ["data"]},
        ValidationType.IS_DATE: {"required": ["data"], "optional": ["format"]},
        ValidationType.IS_TIME: {"required": ["data"], "optional": ["format"]},
        ValidationType.IS_DATETIME: {"required": ["data"], "optional": ["format"]},
        ValidationType.IS_IP: {"required": ["data"]},
        ValidationType.IS_IPV4: {"required": ["data"]},
        ValidationType.IS_IPV6: {"required": ["data"]},
        ValidationType.IS_MAC_ADDRESS: {"required": ["data"]},
        ValidationType.IS_PHONE: {"required": ["data"]},
        ValidationType.IS_CREDIT_CARD: {"required": ["data"]},
        ValidationType.IS_POSTAL_CODE: {"required": ["data"], "optional": ["country"]},
        ValidationType.IS_ALPHA: {"required": ["data"]},
        ValidationType.IS_ALPHANUMERIC: {"required": ["data"]},
        ValidationType.IS_NUMERIC: {"required": ["data"]},
        ValidationType.IS_HEX: {"required": ["data"]},
        ValidationType.IS_BASE64: {"required": ["data"]},
        ValidationType.IS_JSON: {"required": ["data"]},
        ValidationType.IS_XML: {"required": ["data"]},
        
        # Constraint Validation
        ValidationType.MIN_VALUE: {"required": ["data", "min_value"]},
        ValidationType.MAX_VALUE: {"required": ["data", "max_value"]},
        ValidationType.RANGE: {"required": ["data", "min_value", "max_value"]},
        ValidationType.MIN_LENGTH: {"required": ["data", "min_length"]},
        ValidationType.MAX_LENGTH: {"required": ["data", "max_length"]},
        ValidationType.LENGTH: {"required": ["data", "exact_length"]},
        ValidationType.PATTERN: {"required": ["data", "pattern"]},
        ValidationType.ENUM: {"required": ["data", "allowed_values"]},
        ValidationType.NOT_EMPTY: {"required": ["data"]},
        ValidationType.NOT_NULL: {"required": ["data"]},
        ValidationType.REQUIRED: {"required": ["data"]},
        ValidationType.OPTIONAL: {"required": ["data"]},
        
        # String Validation
        ValidationType.STARTS_WITH: {"required": ["data", "prefix"]},
        ValidationType.ENDS_WITH: {"required": ["data", "suffix"]},
        ValidationType.CONTAINS: {"required": ["data", "substring"]},
        ValidationType.NOT_CONTAINS: {"required": ["data", "substring"]},
        ValidationType.LOWERCASE: {"required": ["data"]},
        ValidationType.UPPERCASE: {"required": ["data"]},
        
        # Array Validation
        ValidationType.ARRAY_MIN_LENGTH: {"required": ["data", "min_length"]},
        ValidationType.ARRAY_MAX_LENGTH: {"required": ["data", "max_length"]},
        ValidationType.ARRAY_UNIQUE: {"required": ["data"]},
        ValidationType.ARRAY_CONTAINS: {"required": ["data", "item"]},
        ValidationType.ARRAY_NOT_CONTAINS: {"required": ["data", "item"]},
        
        # Object Validation
        ValidationType.HAS_PROPERTY: {"required": ["data", "property_name"]},
        ValidationType.PROPERTY_TYPE: {"required": ["data", "property_name", "expected_type"]},
        ValidationType.PROPERTY_VALUE: {"required": ["data", "property_name", "expected_value"]},
        
        # Comparison
        ValidationType.EQUALS: {"required": ["data", "expected_value"]},
        ValidationType.NOT_EQUALS: {"required": ["data", "expected_value"]},
        ValidationType.GREATER_THAN: {"required": ["data", "value"]},
        ValidationType.LESS_THAN: {"required": ["data", "value"]},
        ValidationType.GREATER_OR_EQUAL: {"required": ["data", "value"]},
        ValidationType.LESS_OR_EQUAL: {"required": ["data", "value"]},
        
        # Advanced
        ValidationType.SCHEMA: {"required": ["data", "schema"]},
        ValidationType.CUSTOM: {"required": ["data", "custom_function"], "optional": ["message"]},
        ValidationType.CONDITIONAL: {"required": ["data", "condition", "then_rules"], "optional": ["else_rules"]},
        ValidationType.DEPENDENCIES: {"required": ["data", "dependencies"]},
        
        # Data Quality
        ValidationType.COMPLETENESS: {"required": ["data", "required_fields"], "optional": ["threshold"]},
        ValidationType.CONSISTENCY: {"required": ["data", "rules"]},
        ValidationType.UNIQUENESS: {"required": ["data"], "optional": ["key"]},
        ValidationType.ACCURACY: {"required": ["data", "reference"], "optional": ["tolerance"]},
        
        # Batch Operations
        ValidationType.BATCH_VALIDATE: {"required": ["data_list", "validation_type"]},
        ValidationType.VALIDATE_ALL: {"required": ["data", "rules"]},
        ValidationType.VALIDATE_ANY: {"required": ["data", "rules"]},
        ValidationType.VALIDATE_NONE: {"required": ["data", "rules"]},
    }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation operation."""
        try:
            # Validate parameters
            validation_result = self.validate_params(params)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            validation_type = ValidationType(params["validation_type"])
            
            # Handle batch validation separately
            if validation_type == ValidationType.BATCH_VALIDATE:
                batch_type = ValidationType(params.get("validation_type", "is_string"))
                # Remove conflicting parameters
                batch_params = {k: v for k, v in params.items() if k not in ["data_list", "validation_type"]}
                result = self.validator.batch_validate(
                    params["data_list"],
                    batch_type,
                    **batch_params
                )
                
                return {
                    "status": "success",
                    "result": {
                        "valid": result["failed"] == 0,
                        "message": f"{result['successful']}/{result['total']} validations passed",
                        "details": result
                    }
                }
            
            # Get validation method
            method_name = validation_type.value
            if not hasattr(self.validator, method_name):
                return {
                    "status": "error",
                    "message": f"Validation method {method_name} not implemented",
                    "timestamp": datetime.now().isoformat()
                }
            
            method = getattr(self.validator, method_name)
            
            # Prepare arguments based on validation type
            args = []
            kwargs = {}
            
            # Add data parameter
            if "data" in params:
                args.append(params["data"])
            
            # Add other parameters based on metadata
            metadata = self.OPERATION_METADATA.get(validation_type, {})
            required_params = metadata.get("required", [])
            optional_params = metadata.get("optional", [])
            
            # Handle special parameter mappings
            param_mapping = {
                "min_value": "min_val",
                "max_value": "max_val",
                "exact_length": "exact_len",
                "min_length": "min_len",
                "max_length": "max_len",
                "pattern": "regex_pattern",
                "expected_value": "expected_value",
                "prefix": "prefix",
                "suffix": "suffix",
                "substring": "substring",
                "item": "item",
                "property_name": "property_name",
                "expected_type": "expected_type"
            }
            
            # Add required parameters
            for param in required_params:
                if param != "data" and param in params:
                    mapped_param = param_mapping.get(param, param)
                    if validation_type == ValidationType.RANGE and param in ["min_value", "max_value"]:
                        args.append(params[param])
                    elif validation_type in [ValidationType.PROPERTY_TYPE, ValidationType.PROPERTY_VALUE] and param in ["property_name", "expected_type", "expected_value"]:
                        args.append(params[param])
                    elif param in ["min_value", "max_value", "value", "exact_length", "min_length", "max_length", 
                                  "pattern", "allowed_values", "expected_value", "prefix", "suffix", "substring", 
                                  "item", "property_name"]:
                        args.append(params[param])
                    else:
                        kwargs[mapped_param] = params[param]
            
            # Add optional parameters
            for param in optional_params:
                if param in params:
                    kwargs[param] = params[param]
            
            # Handle special cases
            if validation_type == ValidationType.CUSTOM:
                # Create function from string
                try:
                    func = eval(f"lambda x: {params['custom_function']}")
                    args.append(func)
                    if "message" in params:
                        args.append(params["message"])
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Invalid custom function: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
            
            elif validation_type == ValidationType.CONDITIONAL:
                # Convert rules from dict to ValidationRule objects
                then_rules = [ValidationRule(ValidationType(r["type"]), r.get("value"), r.get("message")) 
                             for r in params.get("then_rules", [])]
                else_rules = [ValidationRule(ValidationType(r["type"]), r.get("value"), r.get("message")) 
                             for r in params.get("else_rules", [])] if "else_rules" in params else None
                
                args.extend([params["condition"], then_rules, else_rules])
            
            elif validation_type in [ValidationType.VALIDATE_ALL, ValidationType.VALIDATE_ANY, ValidationType.VALIDATE_NONE]:
                # Convert rules from dict to ValidationRule objects
                rules = [ValidationRule(ValidationType(r["type"]), r.get("value"), r.get("message")) 
                        for r in params.get("rules", [])]
                args.append(rules)
            
            # Execute validation
            result = method(*args, **kwargs)
            
            # Convert ValidationResult to dict
            if isinstance(result, ValidationResult):
                response = {
                    "status": "success",
                    "result": result.to_dict()
                }
            else:
                response = {
                    "status": "success",
                    "result": result
                }
            
            return response
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Validation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


# Register the node
from base_node import NodeRegistry
NodeRegistry.register("validation", ValidationNode)