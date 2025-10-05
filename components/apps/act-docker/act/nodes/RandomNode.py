#!/usr/bin/env python3
"""
Random Node for ACT Workflow System

This node provides comprehensive random number and data generation capabilities including:
- Random numbers (integers, floats, ranges)
- Random strings (alphabets, patterns, lengths)
- Random choices from lists/arrays
- Probability distributions (normal, uniform, exponential, etc.)
- Seed management for reproducible results
- Statistical random sampling
- Random data generation for testing

Architecture:
- Dispatch map for clean operation routing
- Multiple random generation strategies
- Seed management for reproducibility
- Statistical distribution support
- Batch generation capabilities
- Custom alphabet and pattern support
"""

import random
import secrets
import string
import math
import statistics
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
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
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

class RandomOperation(str, Enum):
    """Enumeration of all supported random operations."""
    
    # Basic Random Numbers
    RANDOM_INTEGER = "random_integer"
    RANDOM_FLOAT = "random_float"
    RANDOM_BOOLEAN = "random_boolean"
    RANDOM_BYTES = "random_bytes"
    
    # Random Strings
    RANDOM_STRING = "random_string"
    RANDOM_PASSWORD = "random_password"
    RANDOM_HEX = "random_hex"
    RANDOM_UUID = "random_uuid"
    
    # Random Choices
    RANDOM_CHOICE = "random_choice"
    RANDOM_CHOICES = "random_choices"
    RANDOM_SAMPLE = "random_sample"
    RANDOM_SHUFFLE = "random_shuffle"
    
    # Probability Distributions
    NORMAL_DISTRIBUTION = "normal_distribution"
    UNIFORM_DISTRIBUTION = "uniform_distribution"
    EXPONENTIAL_DISTRIBUTION = "exponential_distribution"
    BINOMIAL_DISTRIBUTION = "binomial_distribution"
    POISSON_DISTRIBUTION = "poisson_distribution"
    GAMMA_DISTRIBUTION = "gamma_distribution"
    BETA_DISTRIBUTION = "beta_distribution"
    
    # Seed Management
    SET_SEED = "set_seed"
    GET_SEED = "get_seed"
    RESET_SEED = "reset_seed"
    
    # Batch Operations
    BATCH_INTEGERS = "batch_integers"
    BATCH_FLOATS = "batch_floats"
    BATCH_STRINGS = "batch_strings"
    BATCH_CHOICES = "batch_choices"
    
    # Statistical Sampling
    WEIGHTED_CHOICE = "weighted_choice"
    RESERVOIR_SAMPLING = "reservoir_sampling"
    STRATIFIED_SAMPLING = "stratified_sampling"
    
    # Custom Patterns
    RANDOM_PATTERN = "random_pattern"
    RANDOM_REGEX = "random_regex"
    
    # Data Generation
    RANDOM_DATE = "random_date"
    RANDOM_TIME = "random_time"
    RANDOM_DATETIME = "random_datetime"
    RANDOM_COLOR = "random_color"
    RANDOM_COORDINATES = "random_coordinates"

class RandomError(Exception):
    """Custom exception for random operations."""
    pass

class RandomGenerator:
    """Comprehensive random generation utilities."""
    
    # Predefined alphabets
    ALPHABETS = {
        'letters': string.ascii_letters,
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'digits': string.digits,
        'alphanumeric': string.ascii_letters + string.digits,
        'hexdigits': string.hexdigits.lower(),
        'punctuation': string.punctuation,
        'printable': string.printable.replace(' \t\n\r\x0b\x0c', ''),
        'password': string.ascii_letters + string.digits + '!@#$%^&*',
        'base64': string.ascii_letters + string.digits + '+/',
        'url_safe': string.ascii_letters + string.digits + '-_',
        'safe': 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # No confusing chars
    }
    
    def __init__(self, seed: Optional[int] = None):
        self.random_state = random.Random()
        self.seed = seed
        if seed is not None:
            self.set_seed(seed)
    
    def set_seed(self, seed: int) -> None:
        """Set the random seed for reproducible results."""
        self.seed = seed
        self.random_state.seed(seed)
        random.seed(seed)
        
        if NUMPY_AVAILABLE:
            np.random.seed(seed)
    
    def get_seed(self) -> Optional[int]:
        """Get the current seed."""
        return self.seed
    
    def reset_seed(self) -> None:
        """Reset the seed to None (use system time)."""
        self.seed = None
        self.random_state.seed()
        random.seed()
        
        if NUMPY_AVAILABLE:
            np.random.seed()
    
    def random_integer(self, min_val: int = 0, max_val: int = 100) -> int:
        """Generate a random integer in the specified range."""
        return self.random_state.randint(min_val, max_val)
    
    def random_float(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generate a random float in the specified range."""
        return self.random_state.uniform(min_val, max_val)
    
    def random_boolean(self, probability: float = 0.5) -> bool:
        """Generate a random boolean with specified probability of True."""
        return self.random_state.random() < probability
    
    def random_bytes(self, length: int = 16) -> bytes:
        """Generate random bytes."""
        return secrets.token_bytes(length)
    
    def random_string(self, length: int = 10, alphabet: str = None) -> str:
        """Generate a random string with specified length and alphabet."""
        if alphabet is None:
            alphabet = self.ALPHABETS['alphanumeric']
        
        return ''.join(self.random_state.choice(alphabet) for _ in range(length))
    
    def random_password(self, length: int = 12, 
                       include_uppercase: bool = True,
                       include_lowercase: bool = True,
                       include_digits: bool = True,
                       include_symbols: bool = True,
                       exclude_ambiguous: bool = True) -> str:
        """Generate a secure random password."""
        alphabet = ""
        
        if include_lowercase:
            alphabet += string.ascii_lowercase
        if include_uppercase:
            alphabet += string.ascii_uppercase
        if include_digits:
            alphabet += string.digits
        if include_symbols:
            alphabet += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        if exclude_ambiguous:
            # Remove potentially confusing characters
            ambiguous = "0O1lI"
            alphabet = ''.join(c for c in alphabet if c not in ambiguous)
        
        if not alphabet:
            raise RandomError("No valid characters available for password generation")
        
        password = ''.join(self.random_state.choice(alphabet) for _ in range(length))
        
        # Ensure password meets requirements
        if include_uppercase and not any(c.isupper() for c in password):
            password = password[:-1] + self.random_state.choice(string.ascii_uppercase)
        if include_lowercase and not any(c.islower() for c in password):
            password = password[:-1] + self.random_state.choice(string.ascii_lowercase)
        if include_digits and not any(c.isdigit() for c in password):
            password = password[:-1] + self.random_state.choice(string.digits)
        if include_symbols and not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
            password = password[:-1] + self.random_state.choice("!@#$%^&*")
        
        return password
    
    def random_hex(self, length: int = 16) -> str:
        """Generate a random hexadecimal string."""
        return secrets.token_hex(length)
    
    def random_choice(self, choices: List[Any]) -> Any:
        """Choose a random element from a list."""
        if not choices:
            raise RandomError("Cannot choose from empty list")
        return self.random_state.choice(choices)
    
    def random_choices(self, choices: List[Any], k: int = 1, weights: List[float] = None) -> List[Any]:
        """Choose k random elements from a list with optional weights."""
        if not choices:
            raise RandomError("Cannot choose from empty list")
        
        if weights:
            if len(weights) != len(choices):
                raise RandomError("Weights must have same length as choices")
            return self.random_state.choices(choices, weights=weights, k=k)
        
        return self.random_state.choices(choices, k=k)
    
    def random_sample(self, population: List[Any], k: int) -> List[Any]:
        """Sample k unique elements from population without replacement."""
        if k > len(population):
            raise RandomError("Sample size cannot be larger than population")
        
        return self.random_state.sample(population, k)
    
    def random_shuffle(self, items: List[Any]) -> List[Any]:
        """Shuffle a list and return the shuffled copy."""
        shuffled = items.copy()
        self.random_state.shuffle(shuffled)
        return shuffled
    
    def weighted_choice(self, choices: List[Any], weights: List[float]) -> Any:
        """Choose a random element with weighted probabilities."""
        if len(choices) != len(weights):
            raise RandomError("Choices and weights must have same length")
        
        total = sum(weights)
        if total <= 0:
            raise RandomError("Weights must sum to a positive value")
        
        # Normalize weights
        normalized_weights = [w/total for w in weights]
        
        # Use cumulative distribution
        cumulative = []
        total = 0
        for weight in normalized_weights:
            total += weight
            cumulative.append(total)
        
        rand = self.random_state.random()
        for i, cum_weight in enumerate(cumulative):
            if rand <= cum_weight:
                return choices[i]
        
        return choices[-1]  # Fallback
    
    def normal_distribution(self, mean: float = 0.0, std_dev: float = 1.0, count: int = 1) -> Union[float, List[float]]:
        """Generate random numbers from normal distribution."""
        if count == 1:
            return self.random_state.gauss(mean, std_dev)
        return [self.random_state.gauss(mean, std_dev) for _ in range(count)]
    
    def uniform_distribution(self, min_val: float = 0.0, max_val: float = 1.0, count: int = 1) -> Union[float, List[float]]:
        """Generate random numbers from uniform distribution."""
        if count == 1:
            return self.random_state.uniform(min_val, max_val)
        return [self.random_state.uniform(min_val, max_val) for _ in range(count)]
    
    def exponential_distribution(self, rate: float = 1.0, count: int = 1) -> Union[float, List[float]]:
        """Generate random numbers from exponential distribution."""
        if count == 1:
            return self.random_state.expovariate(rate)
        return [self.random_state.expovariate(rate) for _ in range(count)]
    
    def binomial_distribution(self, n: int, p: float, count: int = 1) -> Union[int, List[int]]:
        """Generate random numbers from binomial distribution."""
        if NUMPY_AVAILABLE:
            if count == 1:
                return int(np.random.binomial(n, p))
            return [int(x) for x in np.random.binomial(n, p, count)]
        else:
            # Fallback implementation
            def binomial_sample():
                return sum(1 for _ in range(n) if self.random_state.random() < p)
            
            if count == 1:
                return binomial_sample()
            return [binomial_sample() for _ in range(count)]
    
    def poisson_distribution(self, lam: float, count: int = 1) -> Union[int, List[int]]:
        """Generate random numbers from Poisson distribution."""
        if NUMPY_AVAILABLE:
            if count == 1:
                return int(np.random.poisson(lam))
            return [int(x) for x in np.random.poisson(lam, count)]
        else:
            # Fallback implementation using inverse transform
            def poisson_sample():
                L = math.exp(-lam)
                k = 0
                p = 1.0
                while p > L:
                    k += 1
                    p *= self.random_state.random()
                return k - 1
            
            if count == 1:
                return poisson_sample()
            return [poisson_sample() for _ in range(count)]
    
    def random_pattern(self, pattern: str) -> str:
        """Generate random string based on pattern."""
        result = ""
        i = 0
        while i < len(pattern):
            char = pattern[i]
            
            if char == '\\' and i + 1 < len(pattern):
                # Escape sequence
                result += pattern[i + 1]
                i += 2
            elif char == 'd':
                # Digit
                result += self.random_state.choice(string.digits)
                i += 1
            elif char == 'l':
                # Lowercase letter
                result += self.random_state.choice(string.ascii_lowercase)
                i += 1
            elif char == 'u':
                # Uppercase letter
                result += self.random_state.choice(string.ascii_uppercase)
                i += 1
            elif char == 'a':
                # Any letter
                result += self.random_state.choice(string.ascii_letters)
                i += 1
            elif char == 'w':
                # Word character (letter or digit)
                result += self.random_state.choice(string.ascii_letters + string.digits)
                i += 1
            elif char == 's':
                # Space
                result += ' '
                i += 1
            elif char == 'x':
                # Hexadecimal digit
                result += self.random_state.choice(string.hexdigits.lower())
                i += 1
            elif char == 'p':
                # Punctuation
                result += self.random_state.choice(string.punctuation)
                i += 1
            else:
                # Literal character
                result += char
                i += 1
        
        return result
    
    def random_date(self, start_date: str = None, end_date: str = None) -> str:
        """Generate random date between start and end dates."""
        if start_date is None:
            start_date = "2020-01-01"
        if end_date is None:
            end_date = "2030-12-31"
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        time_between = end - start
        days_between = time_between.days
        
        random_days = self.random_state.randint(0, days_between)
        random_date = start + timedelta(days=random_days)
        
        return random_date.strftime("%Y-%m-%d")
    
    def random_datetime(self, start_datetime: str = None, end_datetime: str = None) -> str:
        """Generate random datetime between start and end datetimes."""
        if start_datetime is None:
            start_datetime = "2020-01-01 00:00:00"
        if end_datetime is None:
            end_datetime = "2030-12-31 23:59:59"
        
        start = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
        
        time_between = end - start
        seconds_between = time_between.total_seconds()
        
        random_seconds = self.random_state.random() * seconds_between
        random_datetime = start + timedelta(seconds=random_seconds)
        
        return random_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    def random_color(self, format: str = "hex") -> str:
        """Generate random color in specified format."""
        r = self.random_state.randint(0, 255)
        g = self.random_state.randint(0, 255)
        b = self.random_state.randint(0, 255)
        
        if format == "hex":
            return f"#{r:02x}{g:02x}{b:02x}"
        elif format == "rgb":
            return f"rgb({r}, {g}, {b})"
        elif format == "rgba":
            a = self.random_state.random()
            return f"rgba({r}, {g}, {b}, {a:.2f})"
        elif format == "hsl":
            # Convert RGB to HSL
            r_norm, g_norm, b_norm = r/255, g/255, b/255
            max_val = max(r_norm, g_norm, b_norm)
            min_val = min(r_norm, g_norm, b_norm)
            
            h = s = l = (max_val + min_val) / 2
            
            if max_val == min_val:
                h = s = 0
            else:
                d = max_val - min_val
                s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
                
                if max_val == r_norm:
                    h = (g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)
                elif max_val == g_norm:
                    h = (b_norm - r_norm) / d + 2
                elif max_val == b_norm:
                    h = (r_norm - g_norm) / d + 4
                
                h /= 6
            
            return f"hsl({int(h*360)}, {int(s*100)}%, {int(l*100)}%)"
        else:
            raise RandomError(f"Unsupported color format: {format}")
    
    def random_coordinates(self, min_lat: float = -90.0, max_lat: float = 90.0,
                          min_lon: float = -180.0, max_lon: float = 180.0) -> tuple:
        """Generate random geographical coordinates."""
        lat = self.random_state.uniform(min_lat, max_lat)
        lon = self.random_state.uniform(min_lon, max_lon)
        return (lat, lon)

class RandomNode(BaseNode):
    """
    Random number and data generation node for ACT workflow system.
    
    Provides comprehensive random generation capabilities including:
    - Random numbers (integers, floats, booleans)
    - Random strings (passwords, hex, patterns)
    - Random choices and sampling
    - Probability distributions
    - Seed management for reproducibility
    - Batch operations for efficiency
    - Statistical sampling methods
    - Random data generation for testing
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        RandomOperation.RANDOM_INTEGER: {
            "required": [],
            "optional": ["min_val", "max_val"],
            "description": "Generate random integer in specified range"
        },
        RandomOperation.RANDOM_FLOAT: {
            "required": [],
            "optional": ["min_val", "max_val"],
            "description": "Generate random float in specified range"
        },
        RandomOperation.RANDOM_STRING: {
            "required": [],
            "optional": ["length", "alphabet"],
            "description": "Generate random string with specified length and alphabet"
        },
        RandomOperation.RANDOM_CHOICE: {
            "required": ["choices"],
            "optional": [],
            "description": "Choose random element from list"
        },
        RandomOperation.RANDOM_CHOICES: {
            "required": ["choices"],
            "optional": ["k", "weights"],
            "description": "Choose k random elements with optional weights"
        },
        RandomOperation.NORMAL_DISTRIBUTION: {
            "required": [],
            "optional": ["mean", "std_dev", "count"],
            "description": "Generate numbers from normal distribution"
        },
        RandomOperation.SET_SEED: {
            "required": ["seed"],
            "optional": [],
            "description": "Set random seed for reproducible results"
        },
        RandomOperation.BATCH_INTEGERS: {
            "required": ["count"],
            "optional": ["min_val", "max_val"],
            "description": "Generate batch of random integers"
        },
        RandomOperation.RANDOM_PASSWORD: {
            "required": [],
            "optional": ["length", "include_uppercase", "include_lowercase", "include_digits", "include_symbols"],
            "description": "Generate secure random password"
        },
        RandomOperation.RANDOM_DATE: {
            "required": [],
            "optional": ["start_date", "end_date"],
            "description": "Generate random date in specified range"
        },
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        self.random_generator = RandomGenerator()
        
        # Create operation dispatch map
        self.operation_dispatch = {
            RandomOperation.RANDOM_INTEGER: self._handle_random_integer,
            RandomOperation.RANDOM_FLOAT: self._handle_random_float,
            RandomOperation.RANDOM_BOOLEAN: self._handle_random_boolean,
            RandomOperation.RANDOM_BYTES: self._handle_random_bytes,
            RandomOperation.RANDOM_STRING: self._handle_random_string,
            RandomOperation.RANDOM_PASSWORD: self._handle_random_password,
            RandomOperation.RANDOM_HEX: self._handle_random_hex,
            RandomOperation.RANDOM_UUID: self._handle_random_uuid,
            RandomOperation.RANDOM_CHOICE: self._handle_random_choice,
            RandomOperation.RANDOM_CHOICES: self._handle_random_choices,
            RandomOperation.RANDOM_SAMPLE: self._handle_random_sample,
            RandomOperation.RANDOM_SHUFFLE: self._handle_random_shuffle,
            RandomOperation.NORMAL_DISTRIBUTION: self._handle_normal_distribution,
            RandomOperation.UNIFORM_DISTRIBUTION: self._handle_uniform_distribution,
            RandomOperation.EXPONENTIAL_DISTRIBUTION: self._handle_exponential_distribution,
            RandomOperation.BINOMIAL_DISTRIBUTION: self._handle_binomial_distribution,
            RandomOperation.POISSON_DISTRIBUTION: self._handle_poisson_distribution,
            RandomOperation.GAMMA_DISTRIBUTION: self._handle_gamma_distribution,
            RandomOperation.BETA_DISTRIBUTION: self._handle_beta_distribution,
            RandomOperation.SET_SEED: self._handle_set_seed,
            RandomOperation.GET_SEED: self._handle_get_seed,
            RandomOperation.RESET_SEED: self._handle_reset_seed,
            RandomOperation.BATCH_INTEGERS: self._handle_batch_integers,
            RandomOperation.BATCH_FLOATS: self._handle_batch_floats,
            RandomOperation.BATCH_STRINGS: self._handle_batch_strings,
            RandomOperation.BATCH_CHOICES: self._handle_batch_choices,
            RandomOperation.WEIGHTED_CHOICE: self._handle_weighted_choice,
            RandomOperation.RESERVOIR_SAMPLING: self._handle_reservoir_sampling,
            RandomOperation.STRATIFIED_SAMPLING: self._handle_stratified_sampling,
            RandomOperation.RANDOM_PATTERN: self._handle_random_pattern,
            RandomOperation.RANDOM_REGEX: self._handle_random_regex,
            RandomOperation.RANDOM_DATE: self._handle_random_date,
            RandomOperation.RANDOM_TIME: self._handle_random_time,
            RandomOperation.RANDOM_DATETIME: self._handle_random_datetime,
            RandomOperation.RANDOM_COLOR: self._handle_random_color,
            RandomOperation.RANDOM_COORDINATES: self._handle_random_coordinates,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the schema for RandomNode."""
        return NodeSchema(
            name="RandomNode",
            node_type="random",
            description="Comprehensive random number and data generation",
            version="1.0.0",
            parameters=[
                NodeParameter(
                    name="operation",
                    type="string",
                    description="The random operation to perform",
                    required=True,
                    enum=[op.value for op in RandomOperation]
                ),
                NodeParameter(
                    name="min_val",
                    type="number",
                    description="Minimum value for random numbers",
                    required=False
                ),
                NodeParameter(
                    name="max_val",
                    type="number",
                    description="Maximum value for random numbers",
                    required=False
                ),
                NodeParameter(
                    name="length",
                    type="number",
                    description="Length of generated strings",
                    required=False
                ),
                NodeParameter(
                    name="alphabet",
                    type="string",
                    description="Alphabet for string generation",
                    required=False
                ),
                NodeParameter(
                    name="choices",
                    type="array",
                    description="Array of choices for random selection",
                    required=False
                ),
                NodeParameter(
                    name="weights",
                    type="array",
                    description="Weights for weighted random selection",
                    required=False
                ),
                NodeParameter(
                    name="count",
                    type="number",
                    description="Number of random values to generate",
                    required=False
                ),
                NodeParameter(
                    name="seed",
                    type="number",
                    description="Random seed for reproducible results",
                    required=False
                ),
                NodeParameter(
                    name="mean",
                    type="number",
                    description="Mean for normal distribution",
                    required=False
                ),
                NodeParameter(
                    name="std_dev",
                    type="number",
                    description="Standard deviation for normal distribution",
                    required=False
                ),
                NodeParameter(
                    name="probability",
                    type="number",
                    description="Probability for boolean generation",
                    required=False
                ),
                NodeParameter(
                    name="include_uppercase",
                    type="boolean",
                    description="Include uppercase letters in password",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="include_lowercase",
                    type="boolean",
                    description="Include lowercase letters in password",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="include_digits",
                    type="boolean",
                    description="Include digits in password",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="include_symbols",
                    type="boolean",
                    description="Include symbols in password",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="pattern",
                    type="string",
                    description="Pattern for random string generation",
                    required=False
                ),
                NodeParameter(
                    name="start_date",
                    type="string",
                    description="Start date for random date generation",
                    required=False
                ),
                NodeParameter(
                    name="end_date",
                    type="string",
                    description="End date for random date generation",
                    required=False
                ),
                NodeParameter(
                    name="format",
                    type="string",
                    description="Format for output (e.g., color format)",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "value": NodeParameterType.ANY,
                "values": NodeParameterType.ARRAY,
                "seed": NodeParameterType.NUMBER,
                "statistics": NodeParameterType.OBJECT,
                "timestamp": NodeParameterType.STRING,
                "error": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, data: Dict[str, Any]) -> None:
        """Custom validation for random operations."""
        params = data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation parameter is required")
        
        if operation not in [op.value for op in RandomOperation]:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Get operation metadata
        metadata = self.OPERATION_METADATA.get(operation, {})
        required_params = metadata.get("required", [])
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                raise ValueError(f"Required parameter '{param}' missing for operation '{operation}'")
        
        # Operation-specific validation
        if operation in [RandomOperation.RANDOM_INTEGER, RandomOperation.RANDOM_FLOAT]:
            min_val = params.get("min_val")
            max_val = params.get("max_val")
            if min_val is not None and max_val is not None and min_val >= max_val:
                raise ValueError("min_val must be less than max_val")
        
        if operation == RandomOperation.RANDOM_STRING:
            length = params.get("length", 10)
            if not isinstance(length, int) or length < 1:
                raise ValueError("Length must be a positive integer")
        
        if operation == RandomOperation.RANDOM_CHOICE:
            choices = params.get("choices", [])
            if not choices:
                raise ValueError("Choices cannot be empty")
        
        if operation == RandomOperation.SET_SEED:
            seed = params.get("seed")
            if not isinstance(seed, int):
                raise ValueError("Seed must be an integer")
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a random operation."""
        try:
            params = data.get("params", {})
            operation = params.get("operation")
            
            self.logger.info(f"Executing random operation: {operation}")
            
            # Get operation handler
            handler = self.operation_dispatch.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Unsupported random operation: {operation}",
                    "operation": operation
                }
            
            # Execute operation
            result = await handler(params)
            
            self.logger.info(f"Random operation {operation} completed successfully")
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except RandomError as e:
            error_msg = f"Random operation error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
        except Exception as e:
            error_msg = f"Random operation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
    
    # Operation Handlers
    async def _handle_random_integer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_integer operation."""
        min_val = params.get("min_val", 0)
        max_val = params.get("max_val", 100)
        
        value = self.random_generator.random_integer(min_val, max_val)
        return {
            "value": value,
            "min_val": min_val,
            "max_val": max_val,
            "type": "integer"
        }
    
    async def _handle_random_float(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_float operation."""
        min_val = params.get("min_val", 0.0)
        max_val = params.get("max_val", 1.0)
        
        value = self.random_generator.random_float(min_val, max_val)
        return {
            "value": value,
            "min_val": min_val,
            "max_val": max_val,
            "type": "float"
        }
    
    async def _handle_random_boolean(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_boolean operation."""
        probability = params.get("probability", 0.5)
        
        value = self.random_generator.random_boolean(probability)
        return {
            "value": value,
            "probability": probability,
            "type": "boolean"
        }
    
    async def _handle_random_bytes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_bytes operation."""
        length = params.get("length", 16)
        
        value = self.random_generator.random_bytes(length)
        return {
            "value": value.hex(),
            "length": length,
            "type": "bytes"
        }
    
    async def _handle_random_string(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_string operation."""
        length = params.get("length", 10)
        alphabet = params.get("alphabet")
        
        value = self.random_generator.random_string(length, alphabet)
        return {
            "value": value,
            "length": length,
            "alphabet": alphabet or "alphanumeric",
            "type": "string"
        }
    
    async def _handle_random_password(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_password operation."""
        length = params.get("length", 12)
        include_uppercase = params.get("include_uppercase", True)
        include_lowercase = params.get("include_lowercase", True)
        include_digits = params.get("include_digits", True)
        include_symbols = params.get("include_symbols", True)
        
        value = self.random_generator.random_password(
            length, include_uppercase, include_lowercase, 
            include_digits, include_symbols
        )
        return {
            "value": value,
            "length": length,
            "requirements": {
                "uppercase": include_uppercase,
                "lowercase": include_lowercase,
                "digits": include_digits,
                "symbols": include_symbols
            },
            "type": "password"
        }
    
    async def _handle_random_hex(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_hex operation."""
        length = params.get("length", 16)
        
        value = self.random_generator.random_hex(length)
        return {
            "value": value,
            "length": length,
            "type": "hex"
        }
    
    async def _handle_random_uuid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_uuid operation."""
        import uuid
        value = str(uuid.uuid4())
        return {
            "value": value,
            "type": "uuid"
        }
    
    async def _handle_random_choice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_choice operation."""
        choices = params["choices"]
        
        value = self.random_generator.random_choice(choices)
        return {
            "value": value,
            "choices": choices,
            "choices_count": len(choices),
            "type": "choice"
        }
    
    async def _handle_random_choices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_choices operation."""
        choices = params["choices"]
        k = params.get("k", 1)
        weights = params.get("weights")
        
        values = self.random_generator.random_choices(choices, k, weights)
        return {
            "values": values,
            "choices": choices,
            "k": k,
            "weights": weights,
            "type": "choices"
        }
    
    async def _handle_random_sample(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_sample operation."""
        population = params["population"]
        k = params["k"]
        
        values = self.random_generator.random_sample(population, k)
        return {
            "values": values,
            "population_size": len(population),
            "sample_size": k,
            "type": "sample"
        }
    
    async def _handle_random_shuffle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_shuffle operation."""
        items = params["items"]
        
        shuffled = self.random_generator.random_shuffle(items)
        return {
            "shuffled": shuffled,
            "original": items,
            "length": len(items),
            "type": "shuffle"
        }
    
    async def _handle_normal_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle normal_distribution operation."""
        mean = params.get("mean", 0.0)
        std_dev = params.get("std_dev", 1.0)
        count = params.get("count", 1)
        
        values = self.random_generator.normal_distribution(mean, std_dev, count)
        
        if count == 1:
            return {
                "value": values,
                "mean": mean,
                "std_dev": std_dev,
                "type": "normal_distribution"
            }
        else:
            return {
                "values": values,
                "count": count,
                "mean": mean,
                "std_dev": std_dev,
                "statistics": {
                    "actual_mean": statistics.mean(values),
                    "actual_std_dev": statistics.stdev(values) if len(values) > 1 else 0
                },
                "type": "normal_distribution"
            }
    
    async def _handle_set_seed(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set_seed operation."""
        seed = params["seed"]
        
        self.random_generator.set_seed(seed)
        return {
            "seed": seed,
            "message": f"Random seed set to {seed}",
            "type": "seed"
        }
    
    async def _handle_get_seed(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_seed operation."""
        seed = self.random_generator.get_seed()
        return {
            "seed": seed,
            "type": "seed"
        }
    
    async def _handle_reset_seed(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reset_seed operation."""
        self.random_generator.reset_seed()
        return {
            "message": "Random seed reset to system time",
            "type": "seed"
        }
    
    async def _handle_batch_integers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch_integers operation."""
        count = params["count"]
        min_val = params.get("min_val", 0)
        max_val = params.get("max_val", 100)
        
        values = [self.random_generator.random_integer(min_val, max_val) for _ in range(count)]
        return {
            "values": values,
            "count": count,
            "min_val": min_val,
            "max_val": max_val,
            "statistics": {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values)
            },
            "type": "batch_integers"
        }
    
    async def _handle_random_date(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_date operation."""
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        
        value = self.random_generator.random_date(start_date, end_date)
        return {
            "value": value,
            "start_date": start_date,
            "end_date": end_date,
            "type": "date"
        }
    
    async def _handle_random_color(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_color operation."""
        format = params.get("format", "hex")
        
        value = self.random_generator.random_color(format)
        return {
            "value": value,
            "format": format,
            "type": "color"
        }
    
    async def _handle_random_coordinates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_coordinates operation."""
        min_lat = params.get("min_lat", -90.0)
        max_lat = params.get("max_lat", 90.0)
        min_lon = params.get("min_lon", -180.0)
        max_lon = params.get("max_lon", 180.0)
        
        lat, lon = self.random_generator.random_coordinates(min_lat, max_lat, min_lon, max_lon)
        return {
            "latitude": lat,
            "longitude": lon,
            "bounds": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon
            },
            "type": "coordinates"
        }
    
    # Placeholder handlers for advanced operations
    async def _handle_uniform_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle uniform_distribution operation."""
        return {"message": "uniform_distribution operation not yet implemented"}
    
    async def _handle_exponential_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exponential_distribution operation."""
        return {"message": "exponential_distribution operation not yet implemented"}
    
    async def _handle_binomial_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle binomial_distribution operation."""
        return {"message": "binomial_distribution operation not yet implemented"}
    
    async def _handle_poisson_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle poisson_distribution operation."""
        return {"message": "poisson_distribution operation not yet implemented"}
    
    async def _handle_gamma_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gamma_distribution operation."""
        return {"message": "gamma_distribution operation not yet implemented"}
    
    async def _handle_beta_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle beta_distribution operation."""
        return {"message": "beta_distribution operation not yet implemented"}
    
    async def _handle_batch_floats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch_floats operation."""
        return {"message": "batch_floats operation not yet implemented"}
    
    async def _handle_batch_strings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch_strings operation."""
        return {"message": "batch_strings operation not yet implemented"}
    
    async def _handle_batch_choices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch_choices operation."""
        return {"message": "batch_choices operation not yet implemented"}
    
    async def _handle_weighted_choice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weighted_choice operation."""
        return {"message": "weighted_choice operation not yet implemented"}
    
    async def _handle_reservoir_sampling(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reservoir_sampling operation."""
        return {"message": "reservoir_sampling operation not yet implemented"}
    
    async def _handle_stratified_sampling(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stratified_sampling operation."""
        return {"message": "stratified_sampling operation not yet implemented"}
    
    async def _handle_random_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_pattern operation."""
        return {"message": "random_pattern operation not yet implemented"}
    
    async def _handle_random_regex(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_regex operation."""
        return {"message": "random_regex operation not yet implemented"}
    
    async def _handle_random_time(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_time operation."""
        return {"message": "random_time operation not yet implemented"}
    
    async def _handle_random_datetime(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle random_datetime operation."""
        return {"message": "random_datetime operation not yet implemented"}