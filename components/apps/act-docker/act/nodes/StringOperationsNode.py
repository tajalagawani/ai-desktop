#!/usr/bin/env python3
"""
String Operations Node for ACT Workflow System

This node provides comprehensive string manipulation capabilities including:
- Basic operations (split, join, replace, substring)
- Case transformations (upper, lower, title, camel case)
- String validation and formatting
- Regular expressions (find, replace, split, extract)
- Text processing (trim, pad, truncate, wrap)
- String analysis (length, character counts, statistics)
- Template operations (format, interpolate)
- Advanced operations (similarity, fuzzy matching, transliteration)
"""

import re
import time
import unicodedata
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple
from difflib import SequenceMatcher
import logging

from base_node import BaseNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StringOperationsError(Exception):
    """Custom exception for string operations errors."""
    pass

class StringOperation(str, Enum):
    """Enumeration of all string operations."""
    
    # Basic Operations
    SPLIT = "split"
    JOIN = "join"
    REPLACE = "replace"
    SUBSTRING = "substring"
    CONCAT = "concat"
    REPEAT = "repeat"
    REVERSE = "reverse"
    SLICE = "slice"
    
    # Case Transformations
    UPPER = "upper"
    LOWER = "lower"
    TITLE = "title"
    CAPITALIZE = "capitalize"
    SWAPCASE = "swapcase"
    CAMEL_CASE = "camel_case"
    SNAKE_CASE = "snake_case"
    KEBAB_CASE = "kebab_case"
    PASCAL_CASE = "pascal_case"
    
    # Trimming and Padding
    TRIM = "trim"
    LTRIM = "ltrim"
    RTRIM = "rtrim"
    PAD_LEFT = "pad_left"
    PAD_RIGHT = "pad_right"
    PAD_CENTER = "pad_center"
    
    # Regular Expressions
    REGEX_FIND = "regex_find"
    REGEX_REPLACE = "regex_replace"
    REGEX_SPLIT = "regex_split"
    REGEX_EXTRACT = "regex_extract"
    REGEX_MATCH = "regex_match"
    REGEX_TEST = "regex_test"
    
    # String Analysis
    LENGTH = "length"
    COUNT = "count"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    INDEX_OF = "index_of"
    LAST_INDEX_OF = "last_index_of"
    
    # Formatting
    FORMAT = "format"
    TEMPLATE = "template"
    INTERPOLATE = "interpolate"
    TRUNCATE = "truncate"
    WRAP = "wrap"
    INDENT = "indent"
    DEDENT = "dedent"
    
    # Validation
    IS_ALPHA = "is_alpha"
    IS_NUMERIC = "is_numeric"
    IS_ALPHANUMERIC = "is_alphanumeric"
    IS_EMAIL = "is_email"
    IS_URL = "is_url"
    IS_PHONE = "is_phone"
    IS_EMPTY = "is_empty"
    IS_BLANK = "is_blank"
    
    # Advanced Operations
    SIMILARITY = "similarity"
    LEVENSHTEIN = "levenshtein"
    SOUNDEX = "soundex"
    NORMALIZE = "normalize"
    TRANSLITERATE = "transliterate"
    
    # Batch Operations
    BATCH_PROCESS = "batch_process"
    MULTI_REPLACE = "multi_replace"
    CHAIN_OPERATIONS = "chain_operations"

class StringProcessor:
    """Core string processing engine."""
    
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.url_pattern = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$')
        self.phone_pattern = re.compile(r'^[\+]?[1-9]?[\d\-\(\)\s]{8,20}$')
        
    # Basic Operations
    def split(self, text: str, separator: str = " ", max_split: int = -1) -> List[str]:
        """Split string by separator."""
        if max_split == -1:
            return text.split(separator)
        return text.split(separator, max_split)
    
    def join(self, items: List[str], separator: str = " ") -> str:
        """Join list of strings with separator."""
        return separator.join(str(item) for item in items)
    
    def replace(self, text: str, old: str, new: str, count: int = -1) -> str:
        """Replace occurrences of old with new."""
        if count == -1:
            return text.replace(old, new)
        return text.replace(old, new, count)
    
    def substring(self, text: str, start: int, end: Optional[int] = None) -> str:
        """Extract substring from start to end."""
        if end is None:
            return text[start:]
        return text[start:end]
    
    def concat(self, *args: str) -> str:
        """Concatenate multiple strings."""
        return ''.join(str(arg) for arg in args)
    
    def repeat(self, text: str, count: int) -> str:
        """Repeat string count times."""
        return text * count
    
    def reverse(self, text: str) -> str:
        """Reverse string."""
        return text[::-1]
    
    def slice(self, text: str, start: int, end: Optional[int] = None, step: int = 1) -> str:
        """Slice string with start, end, and step."""
        return text[start:end:step]
    
    # Case Transformations
    def upper(self, text: str) -> str:
        """Convert to uppercase."""
        return text.upper()
    
    def lower(self, text: str) -> str:
        """Convert to lowercase."""
        return text.lower()
    
    def title(self, text: str) -> str:
        """Convert to title case."""
        return text.title()
    
    def capitalize(self, text: str) -> str:
        """Capitalize first letter."""
        return text.capitalize()
    
    def swapcase(self, text: str) -> str:
        """Swap case of all characters."""
        return text.swapcase()
    
    def camel_case(self, text: str) -> str:
        """Convert to camelCase."""
        words = re.split(r'[\s_-]+', text.lower())
        if not words:
            return text
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def snake_case(self, text: str) -> str:
        """Convert to snake_case."""
        # Handle camelCase and PascalCase
        text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
        # Replace spaces, hyphens, and other separators with underscores
        text = re.sub(r'[\s\-]+', '_', text)
        return text.lower()
    
    def kebab_case(self, text: str) -> str:
        """Convert to kebab-case."""
        # Handle camelCase and PascalCase
        text = re.sub(r'([a-z])([A-Z])', r'\1-\2', text)
        # Replace spaces, underscores, and other separators with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        return text.lower()
    
    def pascal_case(self, text: str) -> str:
        """Convert to PascalCase."""
        words = re.split(r'[\s_-]+', text.lower())
        return ''.join(word.capitalize() for word in words)
    
    # Trimming and Padding
    def trim(self, text: str, chars: Optional[str] = None) -> str:
        """Trim whitespace or specified characters from both ends."""
        return text.strip(chars)
    
    def ltrim(self, text: str, chars: Optional[str] = None) -> str:
        """Trim whitespace or specified characters from left."""
        return text.lstrip(chars)
    
    def rtrim(self, text: str, chars: Optional[str] = None) -> str:
        """Trim whitespace or specified characters from right."""
        return text.rstrip(chars)
    
    def pad_left(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad string to width with fill_char on the left."""
        return text.rjust(width, fill_char)
    
    def pad_right(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad string to width with fill_char on the right."""
        return text.ljust(width, fill_char)
    
    def pad_center(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad string to width with fill_char centered."""
        return text.center(width, fill_char)
    
    # Regular Expressions
    def regex_find(self, text: str, pattern: str, flags: int = 0) -> List[str]:
        """Find all matches of regex pattern."""
        try:
            return re.findall(pattern, text, flags)
        except re.error as e:
            raise StringOperationsError(f"Invalid regex pattern: {e}")
    
    def regex_replace(self, text: str, pattern: str, replacement: str, flags: int = 0) -> str:
        """Replace regex pattern with replacement."""
        try:
            return re.sub(pattern, replacement, text, flags=flags)
        except re.error as e:
            raise StringOperationsError(f"Invalid regex pattern: {e}")
    
    def regex_split(self, text: str, pattern: str, flags: int = 0) -> List[str]:
        """Split string by regex pattern."""
        try:
            return re.split(pattern, text, flags=flags)
        except re.error as e:
            raise StringOperationsError(f"Invalid regex pattern: {e}")
    
    def regex_extract(self, text: str, pattern: str, group: int = 0, flags: int = 0) -> Optional[str]:
        """Extract specific group from regex match."""
        try:
            match = re.search(pattern, text, flags)
            return match.group(group) if match else None
        except re.error as e:
            raise StringOperationsError(f"Invalid regex pattern: {e}")
    
    def regex_match(self, text: str, pattern: str, flags: int = 0) -> bool:
        """Test if string matches regex pattern."""
        try:
            return bool(re.match(pattern, text, flags))
        except re.error as e:
            raise StringOperationsError(f"Invalid regex pattern: {e}")
    
    def regex_test(self, text: str, pattern: str, flags: int = 0) -> bool:
        """Test if string contains regex pattern."""
        try:
            return bool(re.search(pattern, text, flags))
        except re.error as e:
            raise StringOperationsError(f"Invalid regex pattern: {e}")
    
    # String Analysis
    def length(self, text: str) -> int:
        """Get string length."""
        return len(text)
    
    def count(self, text: str, substring: str, start: int = 0, end: Optional[int] = None) -> int:
        """Count occurrences of substring."""
        if end is None:
            return text.count(substring, start)
        return text.count(substring, start, end)
    
    def starts_with(self, text: str, prefix: str, start: int = 0, end: Optional[int] = None) -> bool:
        """Check if string starts with prefix."""
        if end is None:
            return text.startswith(prefix, start)
        return text.startswith(prefix, start, end)
    
    def ends_with(self, text: str, suffix: str, start: int = 0, end: Optional[int] = None) -> bool:
        """Check if string ends with suffix."""
        if end is None:
            return text.endswith(suffix, start)
        return text.endswith(suffix, start, end)
    
    def contains(self, text: str, substring: str) -> bool:
        """Check if string contains substring."""
        return substring in text
    
    def index_of(self, text: str, substring: str, start: int = 0, end: Optional[int] = None) -> int:
        """Find index of first occurrence of substring."""
        try:
            if end is None:
                return text.index(substring, start)
            return text.index(substring, start, end)
        except ValueError:
            return -1
    
    def last_index_of(self, text: str, substring: str, start: int = 0, end: Optional[int] = None) -> int:
        """Find index of last occurrence of substring."""
        try:
            if end is None:
                return text.rindex(substring, start)
            return text.rindex(substring, start, end)
        except ValueError:
            return -1
    
    # Formatting
    def format(self, template: str, *args: Any, **kwargs: Any) -> str:
        """Format string with positional and keyword arguments."""
        return template.format(*args, **kwargs)
    
    def template(self, template: str, variables: Dict[str, Any]) -> str:
        """Process template with variables."""
        import string
        return string.Template(template).safe_substitute(variables)
    
    def interpolate(self, template: str, variables: Dict[str, Any]) -> str:
        """Interpolate variables into template using f-string style."""
        # Simple variable interpolation
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def truncate(self, text: str, length: int, suffix: str = "...") -> str:
        """Truncate string to length with suffix."""
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix
    
    def wrap(self, text: str, width: int, break_long_words: bool = True) -> List[str]:
        """Wrap text to specified width."""
        import textwrap
        return textwrap.wrap(text, width=width, break_long_words=break_long_words)
    
    def indent(self, text: str, prefix: str = "    ") -> str:
        """Indent all lines with prefix."""
        import textwrap
        return textwrap.indent(text, prefix)
    
    def dedent(self, text: str) -> str:
        """Remove common leading whitespace."""
        import textwrap
        return textwrap.dedent(text)
    
    # Validation
    def is_alpha(self, text: str) -> bool:
        """Check if string contains only alphabetic characters."""
        return text.isalpha()
    
    def is_numeric(self, text: str) -> bool:
        """Check if string contains only numeric characters."""
        return text.isnumeric()
    
    def is_alphanumeric(self, text: str) -> bool:
        """Check if string contains only alphanumeric characters."""
        return text.isalnum()
    
    def is_email(self, text: str) -> bool:
        """Check if string is a valid email address."""
        return bool(self.email_pattern.match(text))
    
    def is_url(self, text: str) -> bool:
        """Check if string is a valid URL."""
        return bool(self.url_pattern.match(text))
    
    def is_phone(self, text: str) -> bool:
        """Check if string is a valid phone number."""
        return bool(self.phone_pattern.match(text))
    
    def is_empty(self, text: str) -> bool:
        """Check if string is empty."""
        return len(text) == 0
    
    def is_blank(self, text: str) -> bool:
        """Check if string is blank (empty or whitespace only)."""
        return len(text.strip()) == 0
    
    # Advanced Operations
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings (0-1)."""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def levenshtein(self, text1: str, text2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(text1) < len(text2):
            return self.levenshtein(text2, text1)
        
        if len(text2) == 0:
            return len(text1)
        
        previous_row = list(range(len(text2) + 1))
        for i, c1 in enumerate(text1):
            current_row = [i + 1]
            for j, c2 in enumerate(text2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def soundex(self, text: str) -> str:
        """Generate Soundex code for string."""
        if not text:
            return "0000"
        
        text = text.upper()
        soundex_code = text[0]
        
        # Soundex mapping
        mapping = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }
        
        for char in text[1:]:
            if char in mapping:
                code = mapping[char]
                if code != soundex_code[-1]:
                    soundex_code += code
        
        # Pad or truncate to 4 characters
        soundex_code = soundex_code[:4].ljust(4, '0')
        return soundex_code
    
    def normalize(self, text: str, form: str = 'NFC') -> str:
        """Normalize Unicode text."""
        return unicodedata.normalize(form, text)
    
    def transliterate(self, text: str, remove_accents: bool = True) -> str:
        """Transliterate text to ASCII."""
        if remove_accents:
            # Remove accents and diacritics
            normalized = unicodedata.normalize('NFD', text)
            ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
            return ascii_text
        return text
    
    # Batch Operations
    def batch_process(self, texts: List[str], operation: str, **kwargs) -> List[Dict[str, Any]]:
        """Process multiple texts with same operation."""
        results = []
        
        for i, text in enumerate(texts):
            try:
                if operation == 'upper':
                    result = self.upper(text)
                elif operation == 'lower':
                    result = self.lower(text)
                elif operation == 'trim':
                    result = self.trim(text, kwargs.get('chars'))
                elif operation == 'split':
                    result = self.split(text, kwargs.get('separator', ' '))
                elif operation == 'replace':
                    result = self.replace(text, kwargs.get('old', ''), kwargs.get('new', ''))
                elif operation == 'substring':
                    result = self.substring(text, kwargs.get('start', 0), kwargs.get('end'))
                elif operation == 'regex_find':
                    result = self.regex_find(text, kwargs.get('pattern', ''))
                elif operation == 'truncate':
                    result = self.truncate(text, kwargs.get('length', 100), kwargs.get('suffix', '...'))
                else:
                    raise StringOperationsError(f"Unknown batch operation: {operation}")
                
                results.append({
                    'index': i,
                    'status': 'success',
                    'input': text,
                    'result': result,
                    'input_length': len(text)
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input': text,
                    'error': str(e),
                    'input_length': len(text)
                })
        
        return results
    
    def multi_replace(self, text: str, replacements: Dict[str, str]) -> str:
        """Replace multiple patterns in single pass."""
        import re
        
        def replace_func(match):
            return replacements[match.group(0)]
        
        pattern = '|'.join(map(re.escape, replacements.keys()))
        return re.sub(pattern, replace_func, text)
    
    def chain_operations(self, text: str, operations: List[Dict[str, Any]]) -> str:
        """Chain multiple operations on text."""
        result = text
        
        for operation in operations:
            op_type = operation.get('operation')
            params = operation.get('params', {})
            
            if op_type == 'upper':
                result = self.upper(result)
            elif op_type == 'lower':
                result = self.lower(result)
            elif op_type == 'trim':
                result = self.trim(result, params.get('chars'))
            elif op_type == 'replace':
                result = self.replace(result, params.get('old', ''), params.get('new', ''))
            elif op_type == 'substring':
                result = self.substring(result, params.get('start', 0), params.get('end'))
            elif op_type == 'split':
                result = self.split(result, params.get('separator', ' '))
            elif op_type == 'join':
                if isinstance(result, list):
                    result = self.join(result, params.get('separator', ' '))
            # Add more operations as needed
        
        return result

class StringOperationsNode(BaseNode):
    """
    String Operations node for ACT workflow system.
    
    Provides comprehensive string manipulation capabilities including:
    - Basic operations (split, join, replace, substring)
    - Case transformations (upper, lower, camel case)
    - Regular expressions and pattern matching
    - String validation and analysis
    - Text formatting and processing
    - Advanced operations (similarity, transliteration)
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        StringOperation.SPLIT: {
            "required": ["text"],
            "optional": ["separator", "max_split"],
            "description": "Split string by separator"
        },
        StringOperation.JOIN: {
            "required": ["items"],
            "optional": ["separator"],
            "description": "Join list of strings with separator"
        },
        StringOperation.REPLACE: {
            "required": ["text", "old", "new"],
            "optional": ["count"],
            "description": "Replace occurrences of old with new"
        },
        StringOperation.REGEX_FIND: {
            "required": ["text", "pattern"],
            "optional": ["flags"],
            "description": "Find all matches of regex pattern"
        },
        StringOperation.BATCH_PROCESS: {
            "required": ["texts", "batch_operation"],
            "optional": ["separator", "old", "new", "start", "end", "pattern", "length", "suffix", "chars"],
            "description": "Process multiple texts with same operation"
        },
        StringOperation.SIMILARITY: {
            "required": ["text1", "text2"],
            "optional": [],
            "description": "Calculate similarity between two strings"
        },
        StringOperation.TRUNCATE: {
            "required": ["text", "length"],
            "optional": ["suffix"],
            "description": "Truncate string to specified length"
        },
        StringOperation.CAMEL_CASE: {
            "required": ["text"],
            "optional": [],
            "description": "Convert string to camelCase"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.string_processor = StringProcessor()
        
        # Dispatch map for operations
        self.dispatch_map = {
            StringOperation.SPLIT: self._handle_split,
            StringOperation.JOIN: self._handle_join,
            StringOperation.REPLACE: self._handle_replace,
            StringOperation.SUBSTRING: self._handle_substring,
            StringOperation.CONCAT: self._handle_concat,
            StringOperation.REPEAT: self._handle_repeat,
            StringOperation.REVERSE: self._handle_reverse,
            StringOperation.SLICE: self._handle_slice,
            
            StringOperation.UPPER: self._handle_upper,
            StringOperation.LOWER: self._handle_lower,
            StringOperation.TITLE: self._handle_title,
            StringOperation.CAPITALIZE: self._handle_capitalize,
            StringOperation.SWAPCASE: self._handle_swapcase,
            StringOperation.CAMEL_CASE: self._handle_camel_case,
            StringOperation.SNAKE_CASE: self._handle_snake_case,
            StringOperation.KEBAB_CASE: self._handle_kebab_case,
            StringOperation.PASCAL_CASE: self._handle_pascal_case,
            
            StringOperation.TRIM: self._handle_trim,
            StringOperation.LTRIM: self._handle_ltrim,
            StringOperation.RTRIM: self._handle_rtrim,
            StringOperation.PAD_LEFT: self._handle_pad_left,
            StringOperation.PAD_RIGHT: self._handle_pad_right,
            StringOperation.PAD_CENTER: self._handle_pad_center,
            
            StringOperation.REGEX_FIND: self._handle_regex_find,
            StringOperation.REGEX_REPLACE: self._handle_regex_replace,
            StringOperation.REGEX_SPLIT: self._handle_regex_split,
            StringOperation.REGEX_EXTRACT: self._handle_regex_extract,
            StringOperation.REGEX_MATCH: self._handle_regex_match,
            StringOperation.REGEX_TEST: self._handle_regex_test,
            
            StringOperation.LENGTH: self._handle_length,
            StringOperation.COUNT: self._handle_count,
            StringOperation.STARTS_WITH: self._handle_starts_with,
            StringOperation.ENDS_WITH: self._handle_ends_with,
            StringOperation.CONTAINS: self._handle_contains,
            StringOperation.INDEX_OF: self._handle_index_of,
            StringOperation.LAST_INDEX_OF: self._handle_last_index_of,
            
            StringOperation.FORMAT: self._handle_format,
            StringOperation.TEMPLATE: self._handle_template,
            StringOperation.INTERPOLATE: self._handle_interpolate,
            StringOperation.TRUNCATE: self._handle_truncate,
            StringOperation.WRAP: self._handle_wrap,
            StringOperation.INDENT: self._handle_indent,
            StringOperation.DEDENT: self._handle_dedent,
            
            StringOperation.IS_ALPHA: self._handle_is_alpha,
            StringOperation.IS_NUMERIC: self._handle_is_numeric,
            StringOperation.IS_ALPHANUMERIC: self._handle_is_alphanumeric,
            StringOperation.IS_EMAIL: self._handle_is_email,
            StringOperation.IS_URL: self._handle_is_url,
            StringOperation.IS_PHONE: self._handle_is_phone,
            StringOperation.IS_EMPTY: self._handle_is_empty,
            StringOperation.IS_BLANK: self._handle_is_blank,
            
            StringOperation.SIMILARITY: self._handle_similarity,
            StringOperation.LEVENSHTEIN: self._handle_levenshtein,
            StringOperation.SOUNDEX: self._handle_soundex,
            StringOperation.NORMALIZE: self._handle_normalize,
            StringOperation.TRANSLITERATE: self._handle_transliterate,
            
            StringOperation.BATCH_PROCESS: self._handle_batch_process,
            StringOperation.MULTI_REPLACE: self._handle_multi_replace,
            StringOperation.CHAIN_OPERATIONS: self._handle_chain_operations,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for string operations."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in StringOperation],
                    "description": "String operation to perform"
                },
                # Basic operations
                "text": {
                    "type": "string",
                    "description": "Input text for operations"
                },
                "separator": {
                    "type": "string",
                    "description": "Separator for split/join operations"
                },
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of strings to join"
                },
                "old": {
                    "type": "string",
                    "description": "Text to replace"
                },
                "new": {
                    "type": "string",
                    "description": "Replacement text"
                },
                "start": {
                    "type": "integer",
                    "description": "Start index"
                },
                "end": {
                    "type": "integer",
                    "description": "End index"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of replacements"
                },
                "length": {
                    "type": "integer",
                    "description": "Length for truncation or padding"
                },
                "width": {
                    "type": "integer",
                    "description": "Width for padding or wrapping"
                },
                "fill_char": {
                    "type": "string",
                    "description": "Character for padding"
                },
                "chars": {
                    "type": "string",
                    "description": "Characters to trim"
                },
                "suffix": {
                    "type": "string",
                    "description": "Suffix for truncation"
                },
                "prefix": {
                    "type": "string",
                    "description": "Prefix for operations"
                },
                "step": {
                    "type": "integer",
                    "description": "Step for slicing"
                },
                # Regex operations
                "pattern": {
                    "type": "string",
                    "description": "Regular expression pattern"
                },
                "replacement": {
                    "type": "string",
                    "description": "Replacement for regex operations"
                },
                "flags": {
                    "type": "integer",
                    "description": "Regex flags"
                },
                "group": {
                    "type": "integer",
                    "description": "Regex group to extract"
                },
                # Validation
                "substring": {
                    "type": "string",
                    "description": "Substring to search for"
                },
                # Formatting
                "template": {
                    "type": "string",
                    "description": "Template string"
                },
                "variables": {
                    "type": "object",
                    "description": "Variables for template"
                },
                "break_long_words": {
                    "type": "boolean",
                    "description": "Break long words in wrap"
                },
                # Advanced operations
                "text1": {
                    "type": "string",
                    "description": "First text for comparison"
                },
                "text2": {
                    "type": "string",
                    "description": "Second text for comparison"
                },
                "form": {
                    "type": "string",
                    "description": "Unicode normalization form"
                },
                "remove_accents": {
                    "type": "boolean",
                    "description": "Remove accents in transliteration"
                },
                # Batch operations
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of texts for batch processing"
                },
                "batch_operation": {
                    "type": "string",
                    "description": "Operation to apply to all texts"
                },
                "replacements": {
                    "type": "object",
                    "description": "Multiple replacements map"
                },
                "operations": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Chain of operations"
                },
                "max_split": {
                    "type": "integer",
                    "description": "Maximum splits for split operation"
                }
            },
            "required": ["operation"],
            "additionalProperties": True
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute string operation."""
        try:
            # Validate parameters
            validation_result = self.validate_params(params)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "error": f"Parameter validation failed: {validation_result['error']}"
                }
            
            operation = StringOperation(params["operation"])
            
            logger.info(f"Executing string operation: {operation}")
            
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
            
            logger.info(f"String operation {operation} completed successfully")
            
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "processing_time": round(end_time - start_time, 4),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"String operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"String operation error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation parameters."""
        try:
            operation = params.get("operation")
            if not operation:
                return {"valid": False, "error": "Operation is required"}
            
            if operation not in [op.value for op in StringOperation]:
                return {"valid": False, "error": f"Invalid operation: {operation}"}
            
            # Get operation metadata
            metadata = self.OPERATION_METADATA.get(StringOperation(operation))
            if metadata:
                # Check required parameters
                for param in metadata["required"]:
                    if param not in params:
                        return {"valid": False, "error": f"Required parameter missing: {param}"}
                
                # Validate specific parameters
                if operation == StringOperation.BATCH_PROCESS:
                    texts = params.get("texts", [])
                    if not isinstance(texts, list) or len(texts) == 0:
                        return {"valid": False, "error": "texts must be a non-empty list"}
                    
                    batch_operation = params.get("batch_operation")
                    if not batch_operation:
                        return {"valid": False, "error": "batch_operation is required"}
                
                if operation in [StringOperation.TRUNCATE, StringOperation.PAD_LEFT, StringOperation.PAD_RIGHT, StringOperation.PAD_CENTER]:
                    length = params.get("length")
                    if length is not None and length < 0:
                        return {"valid": False, "error": "length must be non-negative"}
                
                if operation == StringOperation.REPEAT:
                    count = params.get("count", 1)
                    if count < 0:
                        return {"valid": False, "error": "count must be non-negative"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    # Basic Operations Handlers
    async def _handle_split(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle split operation."""
        text = params["text"]
        separator = params.get("separator", " ")
        max_split = params.get("max_split", -1)
        
        result = self.string_processor.split(text, separator, max_split)
        
        return {
            "parts": result,
            "count": len(result),
            "separator": separator,
            "original_length": len(text)
        }
    
    async def _handle_join(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle join operation."""
        items = params["items"]
        separator = params.get("separator", " ")
        
        result = self.string_processor.join(items, separator)
        
        return {
            "result": result,
            "separator": separator,
            "item_count": len(items),
            "result_length": len(result)
        }
    
    async def _handle_replace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle replace operation."""
        text = params["text"]
        old = params["old"]
        new = params["new"]
        count = params.get("count", -1)
        
        original_count = text.count(old)
        result = self.string_processor.replace(text, old, new, count)
        actual_replacements = original_count if count == -1 else min(count, original_count)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "replacements_made": actual_replacements,
            "occurrences_found": original_count
        }
    
    async def _handle_substring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle substring operation."""
        text = params["text"]
        start = params.get("start", 0)
        end = params.get("end")
        
        result = self.string_processor.substring(text, start, end)
        
        return {
            "result": result,
            "start": start,
            "end": end,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    async def _handle_concat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle concat operation."""
        texts = params.get("texts", [])
        if "text" in params:
            texts.append(params["text"])
        
        result = self.string_processor.concat(*texts)
        
        return {
            "result": result,
            "input_count": len(texts),
            "result_length": len(result)
        }
    
    async def _handle_repeat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle repeat operation."""
        text = params["text"]
        count = params.get("count", 1)
        
        result = self.string_processor.repeat(text, count)
        
        return {
            "result": result,
            "count": count,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    async def _handle_reverse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reverse operation."""
        text = params["text"]
        
        result = self.string_processor.reverse(text)
        
        return {
            "result": result,
            "length": len(text)
        }
    
    async def _handle_slice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle slice operation."""
        text = params["text"]
        start = params.get("start", 0)
        end = params.get("end")
        step = params.get("step", 1)
        
        result = self.string_processor.slice(text, start, end, step)
        
        return {
            "result": result,
            "start": start,
            "end": end,
            "step": step,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    # Case Transformation Handlers
    async def _handle_upper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle upper case operation."""
        text = params["text"]
        result = self.string_processor.upper(text)
        
        return {
            "result": result,
            "original": text,
            "length": len(text)
        }
    
    async def _handle_lower(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lower case operation."""
        text = params["text"]
        result = self.string_processor.lower(text)
        
        return {
            "result": result,
            "original": text,
            "length": len(text)
        }
    
    async def _handle_title(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle title case operation."""
        text = params["text"]
        result = self.string_processor.title(text)
        
        return {
            "result": result,
            "original": text,
            "length": len(text)
        }
    
    async def _handle_capitalize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capitalize operation."""
        text = params["text"]
        result = self.string_processor.capitalize(text)
        
        return {
            "result": result,
            "original": text,
            "length": len(text)
        }
    
    async def _handle_swapcase(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle swapcase operation."""
        text = params["text"]
        result = self.string_processor.swapcase(text)
        
        return {
            "result": result,
            "original": text,
            "length": len(text)
        }
    
    async def _handle_camel_case(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle camel case operation."""
        text = params["text"]
        result = self.string_processor.camel_case(text)
        
        return {
            "result": result,
            "original": text,
            "transformation": "camelCase"
        }
    
    async def _handle_snake_case(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle snake case operation."""
        text = params["text"]
        result = self.string_processor.snake_case(text)
        
        return {
            "result": result,
            "original": text,
            "transformation": "snake_case"
        }
    
    async def _handle_kebab_case(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle kebab case operation."""
        text = params["text"]
        result = self.string_processor.kebab_case(text)
        
        return {
            "result": result,
            "original": text,
            "transformation": "kebab-case"
        }
    
    async def _handle_pascal_case(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pascal case operation."""
        text = params["text"]
        result = self.string_processor.pascal_case(text)
        
        return {
            "result": result,
            "original": text,
            "transformation": "PascalCase"
        }
    
    # Trimming and Padding Handlers
    async def _handle_trim(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trim operation."""
        text = params["text"]
        chars = params.get("chars")
        
        result = self.string_processor.trim(text, chars)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "chars_removed": len(text) - len(result),
            "chars": chars
        }
    
    async def _handle_ltrim(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle left trim operation."""
        text = params["text"]
        chars = params.get("chars")
        
        result = self.string_processor.ltrim(text, chars)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "chars_removed": len(text) - len(result),
            "chars": chars
        }
    
    async def _handle_rtrim(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle right trim operation."""
        text = params["text"]
        chars = params.get("chars")
        
        result = self.string_processor.rtrim(text, chars)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "chars_removed": len(text) - len(result),
            "chars": chars
        }
    
    async def _handle_pad_left(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pad left operation."""
        text = params["text"]
        width = params["width"]
        fill_char = params.get("fill_char", " ")
        
        result = self.string_processor.pad_left(text, width, fill_char)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "padding_added": len(result) - len(text),
            "fill_char": fill_char
        }
    
    async def _handle_pad_right(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pad right operation."""
        text = params["text"]
        width = params["width"]
        fill_char = params.get("fill_char", " ")
        
        result = self.string_processor.pad_right(text, width, fill_char)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "padding_added": len(result) - len(text),
            "fill_char": fill_char
        }
    
    async def _handle_pad_center(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pad center operation."""
        text = params["text"]
        width = params["width"]
        fill_char = params.get("fill_char", " ")
        
        result = self.string_processor.pad_center(text, width, fill_char)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "padding_added": len(result) - len(text),
            "fill_char": fill_char
        }
    
    # Regular Expression Handlers
    async def _handle_regex_find(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regex find operation."""
        text = params["text"]
        pattern = params["pattern"]
        flags = params.get("flags", 0)
        
        matches = self.string_processor.regex_find(text, pattern, flags)
        
        return {
            "matches": matches,
            "count": len(matches),
            "pattern": pattern,
            "text_length": len(text)
        }
    
    async def _handle_regex_replace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regex replace operation."""
        text = params["text"]
        pattern = params["pattern"]
        replacement = params["replacement"]
        flags = params.get("flags", 0)
        
        result = self.string_processor.regex_replace(text, pattern, replacement, flags)
        
        return {
            "result": result,
            "pattern": pattern,
            "replacement": replacement,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    async def _handle_regex_split(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regex split operation."""
        text = params["text"]
        pattern = params["pattern"]
        flags = params.get("flags", 0)
        
        parts = self.string_processor.regex_split(text, pattern, flags)
        
        return {
            "parts": parts,
            "count": len(parts),
            "pattern": pattern,
            "original_length": len(text)
        }
    
    async def _handle_regex_extract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regex extract operation."""
        text = params["text"]
        pattern = params["pattern"]
        group = params.get("group", 0)
        flags = params.get("flags", 0)
        
        extracted = self.string_processor.regex_extract(text, pattern, group, flags)
        
        return {
            "extracted": extracted,
            "pattern": pattern,
            "group": group,
            "found": extracted is not None
        }
    
    async def _handle_regex_match(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regex match operation."""
        text = params["text"]
        pattern = params["pattern"]
        flags = params.get("flags", 0)
        
        matches = self.string_processor.regex_match(text, pattern, flags)
        
        return {
            "matches": matches,
            "pattern": pattern,
            "text_length": len(text)
        }
    
    async def _handle_regex_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regex test operation."""
        text = params["text"]
        pattern = params["pattern"]
        flags = params.get("flags", 0)
        
        found = self.string_processor.regex_test(text, pattern, flags)
        
        return {
            "found": found,
            "pattern": pattern,
            "text_length": len(text)
        }
    
    # String Analysis Handlers
    async def _handle_length(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle length operation."""
        text = params["text"]
        length = self.string_processor.length(text)
        
        return {
            "length": length,
            "text": text[:50] + "..." if len(text) > 50 else text
        }
    
    async def _handle_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle count operation."""
        text = params["text"]
        substring = params["substring"]
        start = params.get("start", 0)
        end = params.get("end")
        
        count = self.string_processor.count(text, substring, start, end)
        
        return {
            "count": count,
            "substring": substring,
            "start": start,
            "end": end,
            "text_length": len(text)
        }
    
    async def _handle_starts_with(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle starts with operation."""
        text = params["text"]
        prefix = params["prefix"]
        start = params.get("start", 0)
        end = params.get("end")
        
        result = self.string_processor.starts_with(text, prefix, start, end)
        
        return {
            "starts_with": result,
            "prefix": prefix,
            "start": start,
            "end": end
        }
    
    async def _handle_ends_with(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ends with operation."""
        text = params["text"]
        suffix = params["suffix"]
        start = params.get("start", 0)
        end = params.get("end")
        
        result = self.string_processor.ends_with(text, suffix, start, end)
        
        return {
            "ends_with": result,
            "suffix": suffix,
            "start": start,
            "end": end
        }
    
    async def _handle_contains(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle contains operation."""
        text = params["text"]
        substring = params["substring"]
        
        result = self.string_processor.contains(text, substring)
        
        return {
            "contains": result,
            "substring": substring,
            "text_length": len(text)
        }
    
    async def _handle_index_of(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle index of operation."""
        text = params["text"]
        substring = params["substring"]
        start = params.get("start", 0)
        end = params.get("end")
        
        index = self.string_processor.index_of(text, substring, start, end)
        
        return {
            "index": index,
            "found": index != -1,
            "substring": substring,
            "start": start,
            "end": end
        }
    
    async def _handle_last_index_of(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle last index of operation."""
        text = params["text"]
        substring = params["substring"]
        start = params.get("start", 0)
        end = params.get("end")
        
        index = self.string_processor.last_index_of(text, substring, start, end)
        
        return {
            "index": index,
            "found": index != -1,
            "substring": substring,
            "start": start,
            "end": end
        }
    
    # Formatting Handlers
    async def _handle_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle format operation."""
        template = params["template"]
        args = params.get("args", [])
        kwargs = params.get("kwargs", {})
        
        result = self.string_processor.format(template, *args, **kwargs)
        
        return {
            "result": result,
            "template": template,
            "args": args,
            "kwargs": kwargs
        }
    
    async def _handle_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle template operation."""
        template = params["template"]
        variables = params.get("variables", {})
        
        result = self.string_processor.template(template, variables)
        
        return {
            "result": result,
            "template": template,
            "variables": variables
        }
    
    async def _handle_interpolate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle interpolate operation."""
        template = params["template"]
        variables = params.get("variables", {})
        
        result = self.string_processor.interpolate(template, variables)
        
        return {
            "result": result,
            "template": template,
            "variables": variables
        }
    
    async def _handle_truncate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle truncate operation."""
        text = params["text"]
        length = params["length"]
        suffix = params.get("suffix", "...")
        
        result = self.string_processor.truncate(text, length, suffix)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result),
            "truncated": len(text) > length,
            "suffix": suffix
        }
    
    async def _handle_wrap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle wrap operation."""
        text = params["text"]
        width = params["width"]
        break_long_words = params.get("break_long_words", True)
        
        lines = self.string_processor.wrap(text, width, break_long_words)
        
        return {
            "lines": lines,
            "line_count": len(lines),
            "width": width,
            "original_length": len(text)
        }
    
    async def _handle_indent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle indent operation."""
        text = params["text"]
        prefix = params.get("prefix", "    ")
        
        result = self.string_processor.indent(text, prefix)
        
        return {
            "result": result,
            "prefix": prefix,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    async def _handle_dedent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dedent operation."""
        text = params["text"]
        
        result = self.string_processor.dedent(text)
        
        return {
            "result": result,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    # Validation Handlers
    async def _handle_is_alpha(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is alpha operation."""
        text = params["text"]
        result = self.string_processor.is_alpha(text)
        
        return {
            "is_alpha": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_numeric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is numeric operation."""
        text = params["text"]
        result = self.string_processor.is_numeric(text)
        
        return {
            "is_numeric": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_alphanumeric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is alphanumeric operation."""
        text = params["text"]
        result = self.string_processor.is_alphanumeric(text)
        
        return {
            "is_alphanumeric": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is email operation."""
        text = params["text"]
        result = self.string_processor.is_email(text)
        
        return {
            "is_email": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is URL operation."""
        text = params["text"]
        result = self.string_processor.is_url(text)
        
        return {
            "is_url": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_phone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is phone operation."""
        text = params["text"]
        result = self.string_processor.is_phone(text)
        
        return {
            "is_phone": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_empty(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is empty operation."""
        text = params["text"]
        result = self.string_processor.is_empty(text)
        
        return {
            "is_empty": result,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_is_blank(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle is blank operation."""
        text = params["text"]
        result = self.string_processor.is_blank(text)
        
        return {
            "is_blank": result,
            "text": text,
            "length": len(text)
        }
    
    # Advanced Operations Handlers
    async def _handle_similarity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle similarity operation."""
        text1 = params["text1"]
        text2 = params["text2"]
        
        similarity = self.string_processor.similarity(text1, text2)
        
        return {
            "similarity": similarity,
            "percentage": round(similarity * 100, 2),
            "text1_length": len(text1),
            "text2_length": len(text2)
        }
    
    async def _handle_levenshtein(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Levenshtein distance operation."""
        text1 = params["text1"]
        text2 = params["text2"]
        
        distance = self.string_processor.levenshtein(text1, text2)
        
        return {
            "distance": distance,
            "text1_length": len(text1),
            "text2_length": len(text2),
            "max_distance": max(len(text1), len(text2))
        }
    
    async def _handle_soundex(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Soundex operation."""
        text = params["text"]
        
        code = self.string_processor.soundex(text)
        
        return {
            "soundex": code,
            "text": text,
            "length": len(text)
        }
    
    async def _handle_normalize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle normalize operation."""
        text = params["text"]
        form = params.get("form", "NFC")
        
        result = self.string_processor.normalize(text, form)
        
        return {
            "result": result,
            "form": form,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    async def _handle_transliterate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transliterate operation."""
        text = params["text"]
        remove_accents = params.get("remove_accents", True)
        
        result = self.string_processor.transliterate(text, remove_accents)
        
        return {
            "result": result,
            "remove_accents": remove_accents,
            "original_length": len(text),
            "result_length": len(result)
        }
    
    # Batch Operations Handlers
    async def _handle_batch_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch process operation."""
        texts = params["texts"]
        batch_operation = params["batch_operation"]
        
        # Filter out parameters already passed as positional arguments or not needed
        filtered_params = {k: v for k, v in params.items() if k not in ["texts", "batch_operation", "operation"]}
        
        start_time = time.time()
        results = self.string_processor.batch_process(texts, batch_operation, **filtered_params)
        end_time = time.time()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(texts),
            "successful": successful,
            "failed": failed,
            "batch_operation": batch_operation,
            "processing_time": round(end_time - start_time, 4),
            "rate": round(len(texts) / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_multi_replace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multi replace operation."""
        text = params["text"]
        replacements = params["replacements"]
        
        result = self.string_processor.multi_replace(text, replacements)
        
        return {
            "result": result,
            "replacements": replacements,
            "original_length": len(text),
            "result_length": len(result),
            "replacement_count": len(replacements)
        }
    
    async def _handle_chain_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chain operations."""
        text = params["text"]
        operations = params["operations"]
        
        result = self.string_processor.chain_operations(text, operations)
        
        return {
            "result": result,
            "operations": operations,
            "operation_count": len(operations),
            "original_length": len(text),
            "result_length": len(result) if isinstance(result, str) else 0
        }