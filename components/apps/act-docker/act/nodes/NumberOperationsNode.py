#!/usr/bin/env python3
"""
Number Operations Node for ACT Workflow System

This node provides comprehensive numerical operations including:
- Basic arithmetic (add, subtract, multiply, divide, modulo, power)
- Mathematical functions (sqrt, log, sin, cos, tan, factorial)
- Number formatting (currency, percentage, scientific notation)
- Type conversions (int, float, decimal, binary, hex, octal)
- Statistics (mean, median, mode, std dev, variance)
- Number validation and analysis
- Rounding and precision control
- Range and sequence generation
- Batch numerical operations
- Financial calculations (compound interest, loan payments)
"""

import math
import statistics
import decimal
import fractions
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple
import logging

from base_node import BaseNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NumberOperationsError(Exception):
    """Custom exception for number operations errors."""
    pass

class NumberOperation(str, Enum):
    """Enumeration of all number operations."""
    
    # Basic Arithmetic
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    MODULO = "modulo"
    POWER = "power"
    ABSOLUTE = "absolute"
    NEGATE = "negate"
    
    # Mathematical Functions
    SQRT = "sqrt"
    CBRT = "cbrt"
    LOG = "log"
    LOG10 = "log10"
    LOG2 = "log2"
    EXP = "exp"
    FACTORIAL = "factorial"
    
    # Trigonometric Functions
    SIN = "sin"
    COS = "cos"
    TAN = "tan"
    ASIN = "asin"
    ACOS = "acos"
    ATAN = "atan"
    ATAN2 = "atan2"
    
    # Hyperbolic Functions
    SINH = "sinh"
    COSH = "cosh"
    TANH = "tanh"
    
    # Rounding and Precision
    ROUND = "round"
    CEIL = "ceil"
    FLOOR = "floor"
    TRUNC = "trunc"
    
    # Type Conversions
    TO_INT = "to_int"
    TO_FLOAT = "to_float"
    TO_DECIMAL = "to_decimal"
    TO_FRACTION = "to_fraction"
    TO_BINARY = "to_binary"
    TO_HEX = "to_hex"
    TO_OCTAL = "to_octal"
    
    # Number Formatting
    FORMAT_CURRENCY = "format_currency"
    FORMAT_PERCENTAGE = "format_percentage"
    FORMAT_SCIENTIFIC = "format_scientific"
    FORMAT_ENGINEERING = "format_engineering"
    FORMAT_THOUSANDS = "format_thousands"
    
    # Comparison Operations
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    
    # Range and Sequence
    RANGE = "range"
    SEQUENCE = "sequence"
    FIBONACCI = "fibonacci"
    PRIME_NUMBERS = "prime_numbers"
    
    # Statistical Operations
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    VARIANCE = "variance"
    STD_DEV = "std_dev"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    
    # Number Analysis
    IS_EVEN = "is_even"
    IS_ODD = "is_odd"
    IS_PRIME = "is_prime"
    IS_PERFECT = "is_perfect"
    IS_PALINDROME = "is_palindrome"
    GCD = "gcd"
    LCM = "lcm"
    
    # Financial Operations
    COMPOUND_INTEREST = "compound_interest"
    SIMPLE_INTEREST = "simple_interest"
    LOAN_PAYMENT = "loan_payment"
    PRESENT_VALUE = "present_value"
    FUTURE_VALUE = "future_value"
    
    # Batch Operations
    BATCH_CALCULATE = "batch_calculate"
    AGGREGATE = "aggregate"
    
    # Random and Generation
    RANDOM_INT = "random_int"
    RANDOM_FLOAT = "random_float"
    RANDOM_NORMAL = "random_normal"

class NumberProcessor:
    """Core number processing engine."""
    
    def __init__(self):
        self.decimal_context = decimal.Context(prec=28)
        decimal.setcontext(self.decimal_context)
    
    # Basic Arithmetic
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b."""
        if b == 0:
            raise NumberOperationsError("Division by zero")
        return a / b
    
    def modulo(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Get remainder of a divided by b."""
        if b == 0:
            raise NumberOperationsError("Division by zero")
        return a % b
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """Raise base to the power of exponent."""
        return base ** exponent
    
    def absolute(self, x: Union[int, float]) -> Union[int, float]:
        """Get absolute value."""
        return abs(x)
    
    def negate(self, x: Union[int, float]) -> Union[int, float]:
        """Negate a number."""
        return -x
    
    # Mathematical Functions
    def sqrt(self, x: Union[int, float]) -> float:
        """Square root."""
        if x < 0:
            raise NumberOperationsError("Cannot calculate square root of negative number")
        return math.sqrt(x)
    
    def cbrt(self, x: Union[int, float]) -> float:
        """Cube root."""
        if x < 0:
            return -math.pow(-x, 1/3)
        return math.pow(x, 1/3)
    
    def log(self, x: Union[int, float], base: Optional[Union[int, float]] = None) -> float:
        """Natural logarithm or logarithm with specified base."""
        if x <= 0:
            raise NumberOperationsError("Cannot calculate logarithm of non-positive number")
        if base is None:
            return math.log(x)
        if base <= 0 or base == 1:
            raise NumberOperationsError("Invalid logarithm base")
        return math.log(x, base)
    
    def log10(self, x: Union[int, float]) -> float:
        """Base 10 logarithm."""
        if x <= 0:
            raise NumberOperationsError("Cannot calculate logarithm of non-positive number")
        return math.log10(x)
    
    def log2(self, x: Union[int, float]) -> float:
        """Base 2 logarithm."""
        if x <= 0:
            raise NumberOperationsError("Cannot calculate logarithm of non-positive number")
        return math.log2(x)
    
    def exp(self, x: Union[int, float]) -> float:
        """Exponential function (e^x)."""
        return math.exp(x)
    
    def factorial(self, n: int) -> int:
        """Factorial of n."""
        if n < 0:
            raise NumberOperationsError("Cannot calculate factorial of negative number")
        if n > 170:  # Avoid overflow
            raise NumberOperationsError("Factorial too large")
        return math.factorial(n)
    
    # Trigonometric Functions
    def sin(self, x: Union[int, float], degrees: bool = False) -> float:
        """Sine function."""
        if degrees:
            x = math.radians(x)
        return math.sin(x)
    
    def cos(self, x: Union[int, float], degrees: bool = False) -> float:
        """Cosine function."""
        if degrees:
            x = math.radians(x)
        return math.cos(x)
    
    def tan(self, x: Union[int, float], degrees: bool = False) -> float:
        """Tangent function."""
        if degrees:
            x = math.radians(x)
        return math.tan(x)
    
    def asin(self, x: Union[int, float], degrees: bool = False) -> float:
        """Arc sine function."""
        if x < -1 or x > 1:
            raise NumberOperationsError("asin domain error: input must be between -1 and 1")
        result = math.asin(x)
        return math.degrees(result) if degrees else result
    
    def acos(self, x: Union[int, float], degrees: bool = False) -> float:
        """Arc cosine function."""
        if x < -1 or x > 1:
            raise NumberOperationsError("acos domain error: input must be between -1 and 1")
        result = math.acos(x)
        return math.degrees(result) if degrees else result
    
    def atan(self, x: Union[int, float], degrees: bool = False) -> float:
        """Arc tangent function."""
        result = math.atan(x)
        return math.degrees(result) if degrees else result
    
    def atan2(self, y: Union[int, float], x: Union[int, float], degrees: bool = False) -> float:
        """Arc tangent of y/x."""
        result = math.atan2(y, x)
        return math.degrees(result) if degrees else result
    
    # Hyperbolic Functions
    def sinh(self, x: Union[int, float]) -> float:
        """Hyperbolic sine."""
        return math.sinh(x)
    
    def cosh(self, x: Union[int, float]) -> float:
        """Hyperbolic cosine."""
        return math.cosh(x)
    
    def tanh(self, x: Union[int, float]) -> float:
        """Hyperbolic tangent."""
        return math.tanh(x)
    
    # Rounding and Precision
    def round(self, x: Union[int, float], ndigits: int = 0) -> Union[int, float]:
        """Round to specified number of decimal places."""
        return round(x, ndigits)
    
    def ceil(self, x: Union[int, float]) -> int:
        """Ceiling function (round up)."""
        return math.ceil(x)
    
    def floor(self, x: Union[int, float]) -> int:
        """Floor function (round down)."""
        return math.floor(x)
    
    def trunc(self, x: Union[int, float]) -> int:
        """Truncate decimal part."""
        return math.trunc(x)
    
    # Type Conversions
    def to_int(self, x: Union[int, float, str]) -> int:
        """Convert to integer."""
        if isinstance(x, str):
            # Handle different number formats
            x = x.strip()
            if x.startswith('0x') or x.startswith('0X'):
                return int(x, 16)
            elif x.startswith('0o') or x.startswith('0O'):
                return int(x, 8)
            elif x.startswith('0b') or x.startswith('0B'):
                return int(x, 2)
        return int(x)
    
    def to_float(self, x: Union[int, float, str]) -> float:
        """Convert to float."""
        return float(x)
    
    def to_decimal(self, x: Union[int, float, str]) -> decimal.Decimal:
        """Convert to decimal for high precision."""
        return decimal.Decimal(str(x))
    
    def to_fraction(self, x: Union[int, float, str]) -> fractions.Fraction:
        """Convert to fraction."""
        return fractions.Fraction(x)
    
    def to_binary(self, x: int) -> str:
        """Convert integer to binary string."""
        return bin(x)
    
    def to_hex(self, x: int) -> str:
        """Convert integer to hexadecimal string."""
        return hex(x)
    
    def to_octal(self, x: int) -> str:
        """Convert integer to octal string."""
        return oct(x)
    
    # Number Formatting
    def format_currency(self, amount: Union[int, float], currency: str = "$", 
                       decimal_places: int = 2, thousands_separator: str = ",") -> str:
        """Format number as currency."""
        formatted = f"{amount:,.{decimal_places}f}"
        if thousands_separator != ",":
            formatted = formatted.replace(",", thousands_separator)
        return f"{currency}{formatted}"
    
    def format_percentage(self, x: Union[int, float], decimal_places: int = 2) -> str:
        """Format number as percentage."""
        return f"{x * 100:.{decimal_places}f}%"
    
    def format_scientific(self, x: Union[int, float], decimal_places: int = 2) -> str:
        """Format number in scientific notation."""
        return f"{x:.{decimal_places}e}"
    
    def format_engineering(self, x: Union[int, float], decimal_places: int = 2) -> str:
        """Format number in engineering notation (powers of 1000)."""
        if x == 0:
            return f"0.{'0' * decimal_places}e+00"
        
        exponent = math.floor(math.log10(abs(x)))
        engineering_exponent = exponent - (exponent % 3)
        mantissa = x / (10 ** engineering_exponent)
        
        return f"{mantissa:.{decimal_places}f}e{engineering_exponent:+03d}"
    
    def format_thousands(self, x: Union[int, float], separator: str = ",") -> str:
        """Format number with thousands separator."""
        return f"{x:,.0f}".replace(",", separator)
    
    # Comparison Operations
    def equal(self, a: Union[int, float], b: Union[int, float], tolerance: float = 1e-10) -> bool:
        """Check if two numbers are equal within tolerance."""
        return abs(a - b) < tolerance
    
    def not_equal(self, a: Union[int, float], b: Union[int, float], tolerance: float = 1e-10) -> bool:
        """Check if two numbers are not equal within tolerance."""
        return not self.equal(a, b, tolerance)
    
    def greater_than(self, a: Union[int, float], b: Union[int, float]) -> bool:
        """Check if a > b."""
        return a > b
    
    def less_than(self, a: Union[int, float], b: Union[int, float]) -> bool:
        """Check if a < b."""
        return a < b
    
    def greater_equal(self, a: Union[int, float], b: Union[int, float]) -> bool:
        """Check if a >= b."""
        return a >= b
    
    def less_equal(self, a: Union[int, float], b: Union[int, float]) -> bool:
        """Check if a <= b."""
        return a <= b
    
    # Range and Sequence
    def range(self, start: Union[int, float], stop: Union[int, float], 
             step: Union[int, float] = 1) -> List[Union[int, float]]:
        """Generate range of numbers."""
        if step == 0:
            raise NumberOperationsError("Step cannot be zero")
        
        result = []
        current = start
        
        if step > 0:
            while current < stop:
                result.append(current)
                current += step
        else:
            while current > stop:
                result.append(current)
                current += step
        
        return result
    
    def sequence(self, start: Union[int, float], count: int, 
                step: Union[int, float] = 1) -> List[Union[int, float]]:
        """Generate sequence of numbers."""
        if count < 0:
            raise NumberOperationsError("Count must be non-negative")
        
        return [start + i * step for i in range(count)]
    
    def fibonacci(self, n: int) -> List[int]:
        """Generate Fibonacci sequence."""
        if n < 0:
            raise NumberOperationsError("Count must be non-negative")
        if n == 0:
            return []
        if n == 1:
            return [0]
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        
        return fib
    
    def prime_numbers(self, limit: int) -> List[int]:
        """Generate prime numbers up to limit using Sieve of Eratosthenes."""
        if limit < 2:
            return []
        
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit + 1, i):
                    sieve[j] = False
        
        return [i for i, is_prime in enumerate(sieve) if is_prime]
    
    # Statistical Operations
    def mean(self, numbers: List[Union[int, float]]) -> float:
        """Calculate arithmetic mean."""
        if not numbers:
            raise NumberOperationsError("Cannot calculate mean of empty list")
        return statistics.mean(numbers)
    
    def median(self, numbers: List[Union[int, float]]) -> Union[int, float]:
        """Calculate median."""
        if not numbers:
            raise NumberOperationsError("Cannot calculate median of empty list")
        return statistics.median(numbers)
    
    def mode(self, numbers: List[Union[int, float]]) -> Union[int, float]:
        """Calculate mode."""
        if not numbers:
            raise NumberOperationsError("Cannot calculate mode of empty list")
        return statistics.mode(numbers)
    
    def variance(self, numbers: List[Union[int, float]]) -> float:
        """Calculate variance."""
        if len(numbers) < 2:
            raise NumberOperationsError("Need at least 2 numbers for variance")
        return statistics.variance(numbers)
    
    def std_dev(self, numbers: List[Union[int, float]]) -> float:
        """Calculate standard deviation."""
        if len(numbers) < 2:
            raise NumberOperationsError("Need at least 2 numbers for standard deviation")
        return statistics.stdev(numbers)
    
    def min(self, numbers: List[Union[int, float]]) -> Union[int, float]:
        """Find minimum value."""
        if not numbers:
            raise NumberOperationsError("Cannot find minimum of empty list")
        return min(numbers)
    
    def max(self, numbers: List[Union[int, float]]) -> Union[int, float]:
        """Find maximum value."""
        if not numbers:
            raise NumberOperationsError("Cannot find maximum of empty list")
        return max(numbers)
    
    def sum(self, numbers: List[Union[int, float]]) -> Union[int, float]:
        """Calculate sum."""
        return sum(numbers)
    
    # Number Analysis
    def is_even(self, x: int) -> bool:
        """Check if number is even."""
        return x % 2 == 0
    
    def is_odd(self, x: int) -> bool:
        """Check if number is odd."""
        return x % 2 != 0
    
    def is_prime(self, x: int) -> bool:
        """Check if number is prime."""
        if x < 2:
            return False
        if x == 2:
            return True
        if x % 2 == 0:
            return False
        
        for i in range(3, int(x**0.5) + 1, 2):
            if x % i == 0:
                return False
        
        return True
    
    def is_perfect(self, x: int) -> bool:
        """Check if number is perfect (sum of proper divisors equals the number)."""
        if x < 2:
            return False
        
        divisors_sum = 1  # 1 is always a proper divisor
        for i in range(2, int(x**0.5) + 1):
            if x % i == 0:
                divisors_sum += i
                if i != x // i:  # Avoid counting the same divisor twice for perfect squares
                    divisors_sum += x // i
        
        return divisors_sum == x
    
    def is_palindrome(self, x: int) -> bool:
        """Check if number is palindrome."""
        s = str(abs(x))
        return s == s[::-1]
    
    def gcd(self, a: int, b: int) -> int:
        """Calculate greatest common divisor."""
        return math.gcd(a, b)
    
    def lcm(self, a: int, b: int) -> int:
        """Calculate least common multiple."""
        return abs(a * b) // math.gcd(a, b)
    
    # Financial Operations
    def compound_interest(self, principal: float, rate: float, time: float, 
                         compounds_per_year: int = 1) -> float:
        """Calculate compound interest."""
        if principal <= 0:
            raise NumberOperationsError("Principal must be positive")
        if rate < 0:
            raise NumberOperationsError("Rate cannot be negative")
        if time < 0:
            raise NumberOperationsError("Time cannot be negative")
        if compounds_per_year <= 0:
            raise NumberOperationsError("Compounds per year must be positive")
        
        return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
    
    def simple_interest(self, principal: float, rate: float, time: float) -> float:
        """Calculate simple interest."""
        if principal <= 0:
            raise NumberOperationsError("Principal must be positive")
        if rate < 0:
            raise NumberOperationsError("Rate cannot be negative")
        if time < 0:
            raise NumberOperationsError("Time cannot be negative")
        
        return principal * (1 + rate * time)
    
    def loan_payment(self, principal: float, annual_rate: float, years: int) -> float:
        """Calculate monthly loan payment."""
        if principal <= 0:
            raise NumberOperationsError("Principal must be positive")
        if annual_rate < 0:
            raise NumberOperationsError("Rate cannot be negative")
        if years <= 0:
            raise NumberOperationsError("Years must be positive")
        
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return principal / num_payments
        
        return principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
               ((1 + monthly_rate) ** num_payments - 1)
    
    def present_value(self, future_value: float, rate: float, time: float) -> float:
        """Calculate present value."""
        if future_value <= 0:
            raise NumberOperationsError("Future value must be positive")
        if rate < 0:
            raise NumberOperationsError("Rate cannot be negative")
        if time < 0:
            raise NumberOperationsError("Time cannot be negative")
        
        return future_value / (1 + rate) ** time
    
    def future_value(self, present_value: float, rate: float, time: float) -> float:
        """Calculate future value."""
        if present_value <= 0:
            raise NumberOperationsError("Present value must be positive")
        if rate < 0:
            raise NumberOperationsError("Rate cannot be negative")
        if time < 0:
            raise NumberOperationsError("Time cannot be negative")
        
        return present_value * (1 + rate) ** time
    
    # Batch Operations
    def batch_calculate(self, numbers: List[Union[int, float]], operation: str, 
                       operand: Union[int, float] = None, **kwargs) -> List[Dict[str, Any]]:
        """Apply operation to multiple numbers."""
        results = []
        
        for i, num in enumerate(numbers):
            try:
                if operation == 'add':
                    result = self.add(num, operand)
                elif operation == 'subtract':
                    result = self.subtract(num, operand)
                elif operation == 'multiply':
                    result = self.multiply(num, operand)
                elif operation == 'divide':
                    result = self.divide(num, operand)
                elif operation == 'power':
                    result = self.power(num, operand)
                elif operation == 'sqrt':
                    result = self.sqrt(num)
                elif operation == 'absolute':
                    result = self.absolute(num)
                elif operation == 'round':
                    result = self.round(num, kwargs.get('ndigits', 0))
                elif operation == 'log':
                    result = self.log(num, kwargs.get('base'))
                elif operation == 'sin':
                    result = self.sin(num, kwargs.get('degrees', False))
                elif operation == 'cos':
                    result = self.cos(num, kwargs.get('degrees', False))
                elif operation == 'tan':
                    result = self.tan(num, kwargs.get('degrees', False))
                else:
                    raise NumberOperationsError(f"Unknown batch operation: {operation}")
                
                results.append({
                    'index': i,
                    'status': 'success',
                    'input': num,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'input': num,
                    'error': str(e)
                })
        
        return results
    
    def aggregate(self, numbers: List[Union[int, float]], operations: List[str]) -> Dict[str, Any]:
        """Calculate multiple statistics on numbers."""
        if not numbers:
            raise NumberOperationsError("Cannot aggregate empty list")
        
        results = {}
        
        for operation in operations:
            try:
                if operation == 'mean':
                    results[operation] = self.mean(numbers)
                elif operation == 'median':
                    results[operation] = self.median(numbers)
                elif operation == 'mode':
                    results[operation] = self.mode(numbers)
                elif operation == 'variance':
                    results[operation] = self.variance(numbers)
                elif operation == 'std_dev':
                    results[operation] = self.std_dev(numbers)
                elif operation == 'min':
                    results[operation] = self.min(numbers)
                elif operation == 'max':
                    results[operation] = self.max(numbers)
                elif operation == 'sum':
                    results[operation] = self.sum(numbers)
                elif operation == 'count':
                    results[operation] = len(numbers)
                else:
                    results[operation] = {'error': f"Unknown aggregation operation: {operation}"}
            except Exception as e:
                results[operation] = {'error': str(e)}
        
        return results

class NumberOperationsNode(BaseNode):
    """
    Number Operations node for ACT workflow system.
    
    Provides comprehensive numerical operations including:
    - Basic arithmetic and mathematical functions
    - Statistical operations and analysis
    - Number formatting and conversions
    - Financial calculations
    - Batch processing capabilities
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        NumberOperation.ADD: {
            "required": ["a", "b"],
            "optional": [],
            "description": "Add two numbers"
        },
        NumberOperation.DIVIDE: {
            "required": ["a", "b"],
            "optional": [],
            "description": "Divide a by b"
        },
        NumberOperation.SQRT: {
            "required": ["x"],
            "optional": [],
            "description": "Calculate square root"
        },
        NumberOperation.SIN: {
            "required": ["x"],
            "optional": ["degrees"],
            "description": "Calculate sine"
        },
        NumberOperation.MEAN: {
            "required": ["numbers"],
            "optional": [],
            "description": "Calculate arithmetic mean"
        },
        NumberOperation.COMPOUND_INTEREST: {
            "required": ["principal", "rate", "time"],
            "optional": ["compounds_per_year"],
            "description": "Calculate compound interest"
        },
        NumberOperation.BATCH_CALCULATE: {
            "required": ["numbers", "batch_operation"],
            "optional": ["operand", "ndigits", "base", "degrees"],
            "description": "Apply operation to multiple numbers"
        },
        NumberOperation.FIBONACCI: {
            "required": ["n"],
            "optional": [],
            "description": "Generate Fibonacci sequence"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.number_processor = NumberProcessor()
        
        # Dispatch map for operations
        self.dispatch_map = {
            NumberOperation.ADD: self._handle_add,
            NumberOperation.SUBTRACT: self._handle_subtract,
            NumberOperation.MULTIPLY: self._handle_multiply,
            NumberOperation.DIVIDE: self._handle_divide,
            NumberOperation.MODULO: self._handle_modulo,
            NumberOperation.POWER: self._handle_power,
            NumberOperation.ABSOLUTE: self._handle_absolute,
            NumberOperation.NEGATE: self._handle_negate,
            
            NumberOperation.SQRT: self._handle_sqrt,
            NumberOperation.CBRT: self._handle_cbrt,
            NumberOperation.LOG: self._handle_log,
            NumberOperation.LOG10: self._handle_log10,
            NumberOperation.LOG2: self._handle_log2,
            NumberOperation.EXP: self._handle_exp,
            NumberOperation.FACTORIAL: self._handle_factorial,
            
            NumberOperation.SIN: self._handle_sin,
            NumberOperation.COS: self._handle_cos,
            NumberOperation.TAN: self._handle_tan,
            NumberOperation.ASIN: self._handle_asin,
            NumberOperation.ACOS: self._handle_acos,
            NumberOperation.ATAN: self._handle_atan,
            NumberOperation.ATAN2: self._handle_atan2,
            
            NumberOperation.SINH: self._handle_sinh,
            NumberOperation.COSH: self._handle_cosh,
            NumberOperation.TANH: self._handle_tanh,
            
            NumberOperation.ROUND: self._handle_round,
            NumberOperation.CEIL: self._handle_ceil,
            NumberOperation.FLOOR: self._handle_floor,
            NumberOperation.TRUNC: self._handle_trunc,
            
            NumberOperation.TO_INT: self._handle_to_int,
            NumberOperation.TO_FLOAT: self._handle_to_float,
            NumberOperation.TO_DECIMAL: self._handle_to_decimal,
            NumberOperation.TO_FRACTION: self._handle_to_fraction,
            NumberOperation.TO_BINARY: self._handle_to_binary,
            NumberOperation.TO_HEX: self._handle_to_hex,
            NumberOperation.TO_OCTAL: self._handle_to_octal,
            
            NumberOperation.FORMAT_CURRENCY: self._handle_format_currency,
            NumberOperation.FORMAT_PERCENTAGE: self._handle_format_percentage,
            NumberOperation.FORMAT_SCIENTIFIC: self._handle_format_scientific,
            NumberOperation.FORMAT_ENGINEERING: self._handle_format_engineering,
            NumberOperation.FORMAT_THOUSANDS: self._handle_format_thousands,
            
            NumberOperation.EQUAL: self._handle_equal,
            NumberOperation.NOT_EQUAL: self._handle_not_equal,
            NumberOperation.GREATER_THAN: self._handle_greater_than,
            NumberOperation.LESS_THAN: self._handle_less_than,
            NumberOperation.GREATER_EQUAL: self._handle_greater_equal,
            NumberOperation.LESS_EQUAL: self._handle_less_equal,
            
            NumberOperation.RANGE: self._handle_range,
            NumberOperation.SEQUENCE: self._handle_sequence,
            NumberOperation.FIBONACCI: self._handle_fibonacci,
            NumberOperation.PRIME_NUMBERS: self._handle_prime_numbers,
            
            NumberOperation.MEAN: self._handle_mean,
            NumberOperation.MEDIAN: self._handle_median,
            NumberOperation.MODE: self._handle_mode,
            NumberOperation.VARIANCE: self._handle_variance,
            NumberOperation.STD_DEV: self._handle_std_dev,
            NumberOperation.MIN: self._handle_min,
            NumberOperation.MAX: self._handle_max,
            NumberOperation.SUM: self._handle_sum,
            
            NumberOperation.IS_EVEN: self._handle_is_even,
            NumberOperation.IS_ODD: self._handle_is_odd,
            NumberOperation.IS_PRIME: self._handle_is_prime,
            NumberOperation.IS_PERFECT: self._handle_is_perfect,
            NumberOperation.IS_PALINDROME: self._handle_is_palindrome,
            NumberOperation.GCD: self._handle_gcd,
            NumberOperation.LCM: self._handle_lcm,
            
            NumberOperation.COMPOUND_INTEREST: self._handle_compound_interest,
            NumberOperation.SIMPLE_INTEREST: self._handle_simple_interest,
            NumberOperation.LOAN_PAYMENT: self._handle_loan_payment,
            NumberOperation.PRESENT_VALUE: self._handle_present_value,
            NumberOperation.FUTURE_VALUE: self._handle_future_value,
            
            NumberOperation.BATCH_CALCULATE: self._handle_batch_calculate,
            NumberOperation.AGGREGATE: self._handle_aggregate,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for number operations."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in NumberOperation],
                    "description": "Number operation to perform"
                },
                # Basic parameters
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                },
                "x": {
                    "type": "number",
                    "description": "Input number"
                },
                "y": {
                    "type": "number",
                    "description": "Second input number"
                },
                "n": {
                    "type": "integer",
                    "description": "Integer input"
                },
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of numbers"
                },
                # Mathematical parameters
                "base": {
                    "type": "number",
                    "description": "Base for logarithm"
                },
                "exponent": {
                    "type": "number",
                    "description": "Exponent for power operation"
                },
                "degrees": {
                    "type": "boolean",
                    "description": "Use degrees instead of radians"
                },
                # Formatting parameters
                "ndigits": {
                    "type": "integer",
                    "description": "Number of decimal places"
                },
                "currency": {
                    "type": "string",
                    "description": "Currency symbol"
                },
                "decimal_places": {
                    "type": "integer",
                    "description": "Number of decimal places"
                },
                "thousands_separator": {
                    "type": "string",
                    "description": "Thousands separator"
                },
                "separator": {
                    "type": "string",
                    "description": "Separator character"
                },
                # Range parameters
                "start": {
                    "type": "number",
                    "description": "Start value"
                },
                "stop": {
                    "type": "number",
                    "description": "Stop value"
                },
                "step": {
                    "type": "number",
                    "description": "Step value"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of items"
                },
                "limit": {
                    "type": "integer",
                    "description": "Upper limit"
                },
                # Financial parameters
                "principal": {
                    "type": "number",
                    "description": "Principal amount"
                },
                "rate": {
                    "type": "number",
                    "description": "Interest rate"
                },
                "time": {
                    "type": "number",
                    "description": "Time period"
                },
                "compounds_per_year": {
                    "type": "integer",
                    "description": "Compounding frequency"
                },
                "annual_rate": {
                    "type": "number",
                    "description": "Annual interest rate"
                },
                "years": {
                    "type": "integer",
                    "description": "Number of years"
                },
                "future_value": {
                    "type": "number",
                    "description": "Future value"
                },
                "present_value": {
                    "type": "number",
                    "description": "Present value"
                },
                # Batch parameters
                "batch_operation": {
                    "type": "string",
                    "description": "Operation to apply to all numbers"
                },
                "operand": {
                    "type": "number",
                    "description": "Operand for batch operation"
                },
                "operations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of operations for aggregation"
                },
                # Comparison parameters
                "tolerance": {
                    "type": "number",
                    "description": "Tolerance for equality comparison"
                }
            },
            "required": ["operation"],
            "additionalProperties": True
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute number operation."""
        try:
            # Validate parameters
            validation_result = self.validate_params(params)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "error": f"Parameter validation failed: {validation_result['error']}"
                }
            
            operation = NumberOperation(params["operation"])
            
            logger.info(f"Executing number operation: {operation}")
            
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
            
            logger.info(f"Number operation {operation} completed successfully")
            
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "processing_time": round(end_time - start_time, 6),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Number operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"Number operation error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation parameters."""
        try:
            operation = params.get("operation")
            if not operation:
                return {"valid": False, "error": "Operation is required"}
            
            if operation not in [op.value for op in NumberOperation]:
                return {"valid": False, "error": f"Invalid operation: {operation}"}
            
            # Get operation metadata
            metadata = self.OPERATION_METADATA.get(NumberOperation(operation))
            if metadata:
                # Check required parameters
                for param in metadata["required"]:
                    if param not in params:
                        return {"valid": False, "error": f"Required parameter missing: {param}"}
                
                # Validate specific parameters
                if operation == NumberOperation.BATCH_CALCULATE:
                    numbers = params.get("numbers", [])
                    if not isinstance(numbers, list) or len(numbers) == 0:
                        return {"valid": False, "error": "numbers must be a non-empty list"}
                    
                    batch_operation = params.get("batch_operation")
                    if not batch_operation:
                        return {"valid": False, "error": "batch_operation is required"}
                
                if operation in [NumberOperation.FACTORIAL, NumberOperation.FIBONACCI]:
                    n = params.get("n")
                    if n is not None and n < 0:
                        return {"valid": False, "error": "n must be non-negative"}
                
                if operation == NumberOperation.DIVIDE:
                    b = params.get("b")
                    if b is not None and b == 0:
                        return {"valid": False, "error": "Cannot divide by zero"}
                
                if operation in [NumberOperation.SQRT, NumberOperation.LOG, NumberOperation.LOG10, NumberOperation.LOG2]:
                    x = params.get("x")
                    if x is not None and x <= 0:
                        return {"valid": False, "error": "Input must be positive"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    # Basic Arithmetic Handlers
    async def _handle_add(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add operation."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.add(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "addition"
        }
    
    async def _handle_subtract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subtract operation."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.subtract(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "subtraction"
        }
    
    async def _handle_multiply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multiply operation."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.multiply(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "multiplication"
        }
    
    async def _handle_divide(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle divide operation."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.divide(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "division"
        }
    
    async def _handle_modulo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle modulo operation."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.modulo(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "modulo"
        }
    
    async def _handle_power(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle power operation."""
        base = params.get("base", params.get("a"))
        exponent = params.get("exponent", params.get("b"))
        
        result = self.number_processor.power(base, exponent)
        
        return {
            "result": result,
            "base": base,
            "exponent": exponent,
            "operation": "exponentiation"
        }
    
    async def _handle_absolute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle absolute value operation."""
        x = params["x"]
        
        result = self.number_processor.absolute(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "absolute value"
        }
    
    async def _handle_negate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle negate operation."""
        x = params["x"]
        
        result = self.number_processor.negate(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "negation"
        }
    
    # Mathematical Functions Handlers
    async def _handle_sqrt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle square root operation."""
        x = params["x"]
        
        result = self.number_processor.sqrt(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "square root"
        }
    
    async def _handle_cbrt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cube root operation."""
        x = params["x"]
        
        result = self.number_processor.cbrt(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "cube root"
        }
    
    async def _handle_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle logarithm operation."""
        x = params["x"]
        base = params.get("base")
        
        result = self.number_processor.log(x, base)
        
        return {
            "result": result,
            "input": x,
            "base": base or "e",
            "operation": "logarithm"
        }
    
    async def _handle_log10(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle base 10 logarithm operation."""
        x = params["x"]
        
        result = self.number_processor.log10(x)
        
        return {
            "result": result,
            "input": x,
            "base": 10,
            "operation": "base 10 logarithm"
        }
    
    async def _handle_log2(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle base 2 logarithm operation."""
        x = params["x"]
        
        result = self.number_processor.log2(x)
        
        return {
            "result": result,
            "input": x,
            "base": 2,
            "operation": "base 2 logarithm"
        }
    
    async def _handle_exp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exponential operation."""
        x = params["x"]
        
        result = self.number_processor.exp(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "exponential (e^x)"
        }
    
    async def _handle_factorial(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle factorial operation."""
        n = params["n"]
        
        result = self.number_processor.factorial(n)
        
        return {
            "result": result,
            "input": n,
            "operation": "factorial"
        }
    
    # Trigonometric Functions Handlers
    async def _handle_sin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sine operation."""
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.sin(x, degrees)
        
        return {
            "result": result,
            "input": x,
            "degrees": degrees,
            "operation": "sine"
        }
    
    async def _handle_cos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cosine operation."""
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.cos(x, degrees)
        
        return {
            "result": result,
            "input": x,
            "degrees": degrees,
            "operation": "cosine"
        }
    
    async def _handle_tan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tangent operation."""
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.tan(x, degrees)
        
        return {
            "result": result,
            "input": x,
            "degrees": degrees,
            "operation": "tangent"
        }
    
    async def _handle_asin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle arc sine operation."""
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.asin(x, degrees)
        
        return {
            "result": result,
            "input": x,
            "degrees": degrees,
            "operation": "arc sine"
        }
    
    async def _handle_acos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle arc cosine operation."""
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.acos(x, degrees)
        
        return {
            "result": result,
            "input": x,
            "degrees": degrees,
            "operation": "arc cosine"
        }
    
    async def _handle_atan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle arc tangent operation."""
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.atan(x, degrees)
        
        return {
            "result": result,
            "input": x,
            "degrees": degrees,
            "operation": "arc tangent"
        }
    
    async def _handle_atan2(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle atan2 operation."""
        y = params["y"]
        x = params["x"]
        degrees = params.get("degrees", False)
        
        result = self.number_processor.atan2(y, x, degrees)
        
        return {
            "result": result,
            "y": y,
            "x": x,
            "degrees": degrees,
            "operation": "atan2"
        }
    
    # Hyperbolic Functions Handlers
    async def _handle_sinh(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hyperbolic sine operation."""
        x = params["x"]
        
        result = self.number_processor.sinh(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "hyperbolic sine"
        }
    
    async def _handle_cosh(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hyperbolic cosine operation."""
        x = params["x"]
        
        result = self.number_processor.cosh(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "hyperbolic cosine"
        }
    
    async def _handle_tanh(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hyperbolic tangent operation."""
        x = params["x"]
        
        result = self.number_processor.tanh(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "hyperbolic tangent"
        }
    
    # Rounding and Precision Handlers
    async def _handle_round(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle round operation."""
        x = params["x"]
        ndigits = params.get("ndigits", 0)
        
        result = self.number_processor.round(x, ndigits)
        
        return {
            "result": result,
            "input": x,
            "ndigits": ndigits,
            "operation": "round"
        }
    
    async def _handle_ceil(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ceiling operation."""
        x = params["x"]
        
        result = self.number_processor.ceil(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "ceiling"
        }
    
    async def _handle_floor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle floor operation."""
        x = params["x"]
        
        result = self.number_processor.floor(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "floor"
        }
    
    async def _handle_trunc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle truncate operation."""
        x = params["x"]
        
        result = self.number_processor.trunc(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "truncate"
        }
    
    # Type Conversion Handlers
    async def _handle_to_int(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to integer conversion."""
        x = params["x"]
        
        result = self.number_processor.to_int(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "to integer"
        }
    
    async def _handle_to_float(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to float conversion."""
        x = params["x"]
        
        result = self.number_processor.to_float(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "to float"
        }
    
    async def _handle_to_decimal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to decimal conversion."""
        x = params["x"]
        
        result = self.number_processor.to_decimal(x)
        
        return {
            "result": str(result),
            "input": x,
            "operation": "to decimal"
        }
    
    async def _handle_to_fraction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to fraction conversion."""
        x = params["x"]
        
        result = self.number_processor.to_fraction(x)
        
        return {
            "result": str(result),
            "numerator": result.numerator,
            "denominator": result.denominator,
            "input": x,
            "operation": "to fraction"
        }
    
    async def _handle_to_binary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to binary conversion."""
        x = int(params["x"])
        
        result = self.number_processor.to_binary(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "to binary"
        }
    
    async def _handle_to_hex(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to hexadecimal conversion."""
        x = int(params["x"])
        
        result = self.number_processor.to_hex(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "to hexadecimal"
        }
    
    async def _handle_to_octal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle to octal conversion."""
        x = int(params["x"])
        
        result = self.number_processor.to_octal(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "to octal"
        }
    
    # Number Formatting Handlers
    async def _handle_format_currency(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle currency formatting."""
        amount = params["x"]
        currency = params.get("currency", "$")
        decimal_places = params.get("decimal_places", 2)
        thousands_separator = params.get("thousands_separator", ",")
        
        result = self.number_processor.format_currency(amount, currency, decimal_places, thousands_separator)
        
        return {
            "result": result,
            "amount": amount,
            "currency": currency,
            "decimal_places": decimal_places,
            "operation": "currency formatting"
        }
    
    async def _handle_format_percentage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle percentage formatting."""
        x = params["x"]
        decimal_places = params.get("decimal_places", 2)
        
        result = self.number_processor.format_percentage(x, decimal_places)
        
        return {
            "result": result,
            "input": x,
            "decimal_places": decimal_places,
            "operation": "percentage formatting"
        }
    
    async def _handle_format_scientific(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scientific notation formatting."""
        x = params["x"]
        decimal_places = params.get("decimal_places", 2)
        
        result = self.number_processor.format_scientific(x, decimal_places)
        
        return {
            "result": result,
            "input": x,
            "decimal_places": decimal_places,
            "operation": "scientific notation"
        }
    
    async def _handle_format_engineering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle engineering notation formatting."""
        x = params["x"]
        decimal_places = params.get("decimal_places", 2)
        
        result = self.number_processor.format_engineering(x, decimal_places)
        
        return {
            "result": result,
            "input": x,
            "decimal_places": decimal_places,
            "operation": "engineering notation"
        }
    
    async def _handle_format_thousands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle thousands formatting."""
        x = params["x"]
        separator = params.get("separator", ",")
        
        result = self.number_processor.format_thousands(x, separator)
        
        return {
            "result": result,
            "input": x,
            "separator": separator,
            "operation": "thousands formatting"
        }
    
    # Comparison Handlers
    async def _handle_equal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle equality comparison."""
        a = params["a"]
        b = params["b"]
        tolerance = params.get("tolerance", 1e-10)
        
        result = self.number_processor.equal(a, b, tolerance)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "tolerance": tolerance,
            "operation": "equality comparison"
        }
    
    async def _handle_not_equal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inequality comparison."""
        a = params["a"]
        b = params["b"]
        tolerance = params.get("tolerance", 1e-10)
        
        result = self.number_processor.not_equal(a, b, tolerance)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "tolerance": tolerance,
            "operation": "inequality comparison"
        }
    
    async def _handle_greater_than(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greater than comparison."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.greater_than(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "greater than comparison"
        }
    
    async def _handle_less_than(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle less than comparison."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.less_than(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "less than comparison"
        }
    
    async def _handle_greater_equal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greater than or equal comparison."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.greater_equal(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "greater than or equal comparison"
        }
    
    async def _handle_less_equal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle less than or equal comparison."""
        a = params["a"]
        b = params["b"]
        
        result = self.number_processor.less_equal(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "less than or equal comparison"
        }
    
    # Range and Sequence Handlers
    async def _handle_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle range generation."""
        start = params["start"]
        stop = params["stop"]
        step = params.get("step", 1)
        
        result = self.number_processor.range(start, stop, step)
        
        return {
            "result": result,
            "start": start,
            "stop": stop,
            "step": step,
            "count": len(result),
            "operation": "range generation"
        }
    
    async def _handle_sequence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sequence generation."""
        start = params["start"]
        count = params["count"]
        step = params.get("step", 1)
        
        result = self.number_processor.sequence(start, count, step)
        
        return {
            "result": result,
            "start": start,
            "count": count,
            "step": step,
            "operation": "sequence generation"
        }
    
    async def _handle_fibonacci(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Fibonacci sequence generation."""
        n = params["n"]
        
        result = self.number_processor.fibonacci(n)
        
        return {
            "result": result,
            "n": n,
            "count": len(result),
            "operation": "Fibonacci sequence"
        }
    
    async def _handle_prime_numbers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prime number generation."""
        limit = params["limit"]
        
        result = self.number_processor.prime_numbers(limit)
        
        return {
            "result": result,
            "limit": limit,
            "count": len(result),
            "operation": "prime number generation"
        }
    
    # Statistical Operations Handlers
    async def _handle_mean(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mean calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.mean(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "arithmetic mean"
        }
    
    async def _handle_median(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle median calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.median(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "median"
        }
    
    async def _handle_mode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mode calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.mode(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "mode"
        }
    
    async def _handle_variance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle variance calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.variance(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "variance"
        }
    
    async def _handle_std_dev(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle standard deviation calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.std_dev(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "standard deviation"
        }
    
    async def _handle_min(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle minimum calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.min(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "minimum"
        }
    
    async def _handle_max(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle maximum calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.max(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "maximum"
        }
    
    async def _handle_sum(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sum calculation."""
        numbers = params["numbers"]
        
        result = self.number_processor.sum(numbers)
        
        return {
            "result": result,
            "count": len(numbers),
            "operation": "sum"
        }
    
    # Number Analysis Handlers
    async def _handle_is_even(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle even number check."""
        x = int(params["x"])
        
        result = self.number_processor.is_even(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "even number check"
        }
    
    async def _handle_is_odd(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odd number check."""
        x = int(params["x"])
        
        result = self.number_processor.is_odd(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "odd number check"
        }
    
    async def _handle_is_prime(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prime number check."""
        x = int(params["x"])
        
        result = self.number_processor.is_prime(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "prime number check"
        }
    
    async def _handle_is_perfect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle perfect number check."""
        x = int(params["x"])
        
        result = self.number_processor.is_perfect(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "perfect number check"
        }
    
    async def _handle_is_palindrome(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle palindrome number check."""
        x = int(params["x"])
        
        result = self.number_processor.is_palindrome(x)
        
        return {
            "result": result,
            "input": x,
            "operation": "palindrome number check"
        }
    
    async def _handle_gcd(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greatest common divisor."""
        a = int(params["a"])
        b = int(params["b"])
        
        result = self.number_processor.gcd(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "greatest common divisor"
        }
    
    async def _handle_lcm(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle least common multiple."""
        a = int(params["a"])
        b = int(params["b"])
        
        result = self.number_processor.lcm(a, b)
        
        return {
            "result": result,
            "a": a,
            "b": b,
            "operation": "least common multiple"
        }
    
    # Financial Operations Handlers
    async def _handle_compound_interest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle compound interest calculation."""
        principal = params["principal"]
        rate = params["rate"]
        time = params["time"]
        compounds_per_year = params.get("compounds_per_year", 1)
        
        result = self.number_processor.compound_interest(principal, rate, time, compounds_per_year)
        interest = result - principal
        
        return {
            "result": result,
            "principal": principal,
            "rate": rate,
            "time": time,
            "compounds_per_year": compounds_per_year,
            "interest": interest,
            "operation": "compound interest"
        }
    
    async def _handle_simple_interest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle simple interest calculation."""
        principal = params["principal"]
        rate = params["rate"]
        time = params["time"]
        
        result = self.number_processor.simple_interest(principal, rate, time)
        interest = result - principal
        
        return {
            "result": result,
            "principal": principal,
            "rate": rate,
            "time": time,
            "interest": interest,
            "operation": "simple interest"
        }
    
    async def _handle_loan_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle loan payment calculation."""
        principal = params["principal"]
        annual_rate = params["annual_rate"]
        years = params["years"]
        
        result = self.number_processor.loan_payment(principal, annual_rate, years)
        total_payments = result * years * 12
        total_interest = total_payments - principal
        
        return {
            "result": result,
            "principal": principal,
            "annual_rate": annual_rate,
            "years": years,
            "total_payments": total_payments,
            "total_interest": total_interest,
            "operation": "loan payment"
        }
    
    async def _handle_present_value(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle present value calculation."""
        future_value = params["future_value"]
        rate = params["rate"]
        time = params["time"]
        
        result = self.number_processor.present_value(future_value, rate, time)
        
        return {
            "result": result,
            "future_value": future_value,
            "rate": rate,
            "time": time,
            "operation": "present value"
        }
    
    async def _handle_future_value(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle future value calculation."""
        present_value = params["present_value"]
        rate = params["rate"]
        time = params["time"]
        
        result = self.number_processor.future_value(present_value, rate, time)
        
        return {
            "result": result,
            "present_value": present_value,
            "rate": rate,
            "time": time,
            "operation": "future value"
        }
    
    # Batch Operations Handlers
    async def _handle_batch_calculate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch calculation."""
        numbers = params["numbers"]
        batch_operation = params["batch_operation"]
        operand = params.get("operand")
        
        # Filter out parameters already passed as positional arguments or not needed
        filtered_params = {k: v for k, v in params.items() if k not in ["numbers", "batch_operation", "operation", "operand"]}
        
        start_time = time.time()
        results = self.number_processor.batch_calculate(numbers, batch_operation, operand, **filtered_params)
        end_time = time.time()
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        return {
            "results": results,
            "total_items": len(numbers),
            "successful": successful,
            "failed": failed,
            "batch_operation": batch_operation,
            "operand": operand,
            "processing_time": round(end_time - start_time, 6),
            "rate": round(len(numbers) / (end_time - start_time), 2) if end_time > start_time else 0
        }
    
    async def _handle_aggregate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle aggregate operations."""
        numbers = params["numbers"]
        operations = params["operations"]
        
        result = self.number_processor.aggregate(numbers, operations)
        
        return {
            "result": result,
            "numbers_count": len(numbers),
            "operations": operations,
            "operation": "aggregate statistics"
        }