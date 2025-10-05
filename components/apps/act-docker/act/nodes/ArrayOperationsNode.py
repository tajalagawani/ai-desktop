#!/usr/bin/env python3
"""
Array Operations Node for ACT Workflow System

This node provides comprehensive array/list operations including:
- Basic operations: sort, reverse, length, clear
- Filtering and mapping: filter, map, select, reject
- Reduction: reduce, sum, average, min, max
- Searching: find, indexOf, includes, count
- Transformation: flatten, unique, chunk, group
- Set operations: union, intersection, difference
- Validation: isEmpty, isArray, every, some
- Batch processing for multiple arrays
- Advanced operations: partition, transpose, zip

All operations support custom predicates and functions for maximum flexibility.
"""

import asyncio
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum
from functools import reduce
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from base_node import BaseNode, NodeParameter, NodeParameterType, NodeSchema


class ArrayOperation(str, Enum):
    """Enumeration of all array operations."""
    
    # Basic Operations
    SORT = "sort"
    REVERSE = "reverse"
    LENGTH = "length"
    CLEAR = "clear"
    COPY = "copy"
    SLICE = "slice"
    CONCAT = "concat"
    JOIN = "join"
    SPLIT = "split"
    
    # Element Operations
    PUSH = "push"
    POP = "pop"
    SHIFT = "shift"
    UNSHIFT = "unshift"
    INSERT = "insert"
    REMOVE = "remove"
    REMOVE_AT = "remove_at"
    REPLACE = "replace"
    SWAP = "swap"
    
    # Filtering and Mapping
    FILTER = "filter"
    MAP = "map"
    SELECT = "select"
    REJECT = "reject"
    COMPACT = "compact"
    FLATTEN = "flatten"
    FLATTEN_DEEP = "flatten_deep"
    
    # Reduction
    REDUCE = "reduce"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    PRODUCT = "product"
    AGGREGATE = "aggregate"
    
    # Searching
    FIND = "find"
    FIND_INDEX = "find_index"
    FIND_LAST = "find_last"
    FIND_LAST_INDEX = "find_last_index"
    INDEX_OF = "index_of"
    LAST_INDEX_OF = "last_index_of"
    INCLUDES = "includes"
    COUNT = "count"
    
    # Transformation
    UNIQUE = "unique"
    UNIQUE_BY = "unique_by"
    CHUNK = "chunk"
    GROUP_BY = "group_by"
    PARTITION = "partition"
    TRANSPOSE = "transpose"
    ZIP = "zip"
    UNZIP = "unzip"
    
    # Set Operations
    UNION = "union"
    INTERSECTION = "intersection"
    DIFFERENCE = "difference"
    SYMMETRIC_DIFFERENCE = "symmetric_difference"
    
    # Validation
    IS_EMPTY = "is_empty"
    IS_ARRAY = "is_array"
    EVERY = "every"
    SOME = "some"
    NONE = "none"
    
    # Comparison
    EQUALS = "equals"
    DEEP_EQUALS = "deep_equals"
    
    # Sorting
    SORT_BY = "sort_by"
    SORT_NUMERIC = "sort_numeric"
    SORT_ALPHABETIC = "sort_alphabetic"
    SORT_REVERSE = "sort_reverse"
    
    # Statistical
    MEDIAN = "median"
    MODE = "mode"
    VARIANCE = "variance"
    STANDARD_DEVIATION = "standard_deviation"
    PERCENTILE = "percentile"
    
    # Utility
    SHUFFLE = "shuffle"
    SAMPLE = "sample"
    TAKE = "take"
    SKIP = "skip"
    HEAD = "head"
    TAIL = "tail"
    ROTATE = "rotate"
    
    # Batch Operations
    BATCH_PROCESS = "batch_process"
    BATCH_FILTER = "batch_filter"
    BATCH_MAP = "batch_map"
    BATCH_REDUCE = "batch_reduce"


class ArrayProcessor:
    """Processor class for array operations."""
    
    def __init__(self):
        self.random_seed = None
    
    def set_seed(self, seed: int):
        """Set random seed for reproducible operations."""
        import random
        self.random_seed = seed
        random.seed(seed)
    
    def sort(self, array: List[Any], reverse: bool = False, key: Optional[str] = None) -> List[Any]:
        """Sort array with optional key function."""
        if not array:
            return []
        
        try:
            if key:
                # Custom key function
                if key == "length":
                    return sorted(array, key=len, reverse=reverse)
                elif key == "numeric":
                    return sorted(array, key=lambda x: float(x) if self._is_numeric(x) else float('inf'), reverse=reverse)
                elif key == "alphabetic":
                    return sorted(array, key=lambda x: str(x).lower(), reverse=reverse)
                else:
                    # Assume it's a property name
                    return sorted(array, key=lambda x: x.get(key, '') if isinstance(x, dict) else getattr(x, key, ''), reverse=reverse)
            else:
                return sorted(array, reverse=reverse)
        except Exception:
            # Fallback to string sort
            return sorted(array, key=str, reverse=reverse)
    
    def reverse(self, array: List[Any]) -> List[Any]:
        """Reverse array."""
        return list(reversed(array))
    
    def length(self, array: List[Any]) -> int:
        """Get array length."""
        return len(array)
    
    def clear(self, array: List[Any]) -> List[Any]:
        """Clear array."""
        return []
    
    def copy(self, array: List[Any]) -> List[Any]:
        """Create a shallow copy of array."""
        return array.copy()
    
    def slice(self, array: List[Any], start: int = 0, end: Optional[int] = None) -> List[Any]:
        """Slice array."""
        return array[start:end]
    
    def concat(self, array: List[Any], *arrays: List[Any]) -> List[Any]:
        """Concatenate arrays."""
        result = array.copy()
        for arr in arrays:
            result.extend(arr)
        return result
    
    def join(self, array: List[Any], separator: str = ",") -> str:
        """Join array elements into a string."""
        return separator.join(str(x) for x in array)
    
    def split(self, string: str, separator: str = ",") -> List[str]:
        """Split string into array."""
        return string.split(separator)
    
    def push(self, array: List[Any], *elements: Any) -> List[Any]:
        """Add elements to end of array."""
        result = array.copy()
        result.extend(elements)
        return result
    
    def pop(self, array: List[Any]) -> Dict[str, Any]:
        """Remove and return last element."""
        if not array:
            return {"array": [], "popped": None}
        
        result = array.copy()
        popped = result.pop()
        return {"array": result, "popped": popped}
    
    def shift(self, array: List[Any]) -> Dict[str, Any]:
        """Remove and return first element."""
        if not array:
            return {"array": [], "shifted": None}
        
        result = array.copy()
        shifted = result.pop(0)
        return {"array": result, "shifted": shifted}
    
    def unshift(self, array: List[Any], *elements: Any) -> List[Any]:
        """Add elements to beginning of array."""
        result = list(elements) + array
        return result
    
    def insert(self, array: List[Any], index: int, *elements: Any) -> List[Any]:
        """Insert elements at specific index."""
        result = array.copy()
        for i, element in enumerate(elements):
            result.insert(index + i, element)
        return result
    
    def remove(self, array: List[Any], element: Any) -> List[Any]:
        """Remove first occurrence of element."""
        result = array.copy()
        try:
            result.remove(element)
        except ValueError:
            pass
        return result
    
    def remove_at(self, array: List[Any], index: int) -> Dict[str, Any]:
        """Remove element at specific index."""
        if not array or index < 0 or index >= len(array):
            return {"array": array.copy(), "removed": None}
        
        result = array.copy()
        removed = result.pop(index)
        return {"array": result, "removed": removed}
    
    def replace(self, array: List[Any], old_element: Any, new_element: Any) -> List[Any]:
        """Replace first occurrence of element."""
        result = array.copy()
        try:
            index = result.index(old_element)
            result[index] = new_element
        except ValueError:
            pass
        return result
    
    def swap(self, array: List[Any], index1: int, index2: int) -> List[Any]:
        """Swap elements at two indices."""
        if not array or index1 < 0 or index2 < 0 or index1 >= len(array) or index2 >= len(array):
            return array.copy()
        
        result = array.copy()
        result[index1], result[index2] = result[index2], result[index1]
        return result
    
    def filter(self, array: List[Any], predicate: str, value: Any = None) -> List[Any]:
        """Filter array based on predicate."""
        if not array:
            return []
        
        try:
            if predicate == "truthy":
                return [x for x in array if x]
            elif predicate == "falsy":
                return [x for x in array if not x]
            elif predicate == "null":
                return [x for x in array if x is None]
            elif predicate == "not_null":
                return [x for x in array if x is not None]
            elif predicate == "empty":
                return [x for x in array if not x]
            elif predicate == "not_empty":
                return [x for x in array if x]
            elif predicate == "numeric":
                return [x for x in array if self._is_numeric(x)]
            elif predicate == "string":
                return [x for x in array if isinstance(x, str)]
            elif predicate == "array":
                return [x for x in array if isinstance(x, list)]
            elif predicate == "object":
                return [x for x in array if isinstance(x, dict)]
            elif predicate == "equals":
                return [x for x in array if x == value]
            elif predicate == "not_equals":
                return [x for x in array if x != value]
            elif predicate == "greater_than":
                return [x for x in array if self._is_numeric(x) and float(x) > float(value)]
            elif predicate == "less_than":
                return [x for x in array if self._is_numeric(x) and float(x) < float(value)]
            elif predicate == "contains":
                return [x for x in array if str(value) in str(x)]
            else:
                return array.copy()
        except Exception:
            return array.copy()
    
    def map(self, array: List[Any], operation: str, value: Any = None) -> List[Any]:
        """Map array elements through operation."""
        if not array:
            return []
        
        try:
            if operation == "to_string":
                return [str(x) for x in array]
            elif operation == "to_number":
                return [float(x) if self._is_numeric(x) else 0 for x in array]
            elif operation == "to_upper":
                return [str(x).upper() for x in array]
            elif operation == "to_lower":
                return [str(x).lower() for x in array]
            elif operation == "length":
                return [len(str(x)) for x in array]
            elif operation == "square":
                return [float(x) ** 2 if self._is_numeric(x) else 0 for x in array]
            elif operation == "sqrt":
                return [math.sqrt(float(x)) if self._is_numeric(x) and float(x) >= 0 else 0 for x in array]
            elif operation == "abs":
                return [abs(float(x)) if self._is_numeric(x) else 0 for x in array]
            elif operation == "multiply":
                return [float(x) * float(value) if self._is_numeric(x) else 0 for x in array]
            elif operation == "add":
                return [float(x) + float(value) if self._is_numeric(x) else str(x) + str(value) for x in array]
            elif operation == "prefix":
                return [str(value) + str(x) for x in array]
            elif operation == "suffix":
                return [str(x) + str(value) for x in array]
            else:
                return array.copy()
        except Exception:
            return array.copy()
    
    def select(self, array: List[Any], property_name: str) -> List[Any]:
        """Select property from array of objects."""
        if not array:
            return []
        
        result = []
        for item in array:
            if isinstance(item, dict):
                result.append(item.get(property_name))
            else:
                result.append(getattr(item, property_name, None))
        return result
    
    def reject(self, array: List[Any], predicate: str, value: Any = None) -> List[Any]:
        """Reject elements based on predicate (opposite of filter)."""
        filtered = self.filter(array, predicate, value)
        return [x for x in array if x not in filtered]
    
    def compact(self, array: List[Any]) -> List[Any]:
        """Remove falsy values from array."""
        return [x for x in array if x]
    
    def flatten(self, array: List[Any], depth: int = 1) -> List[Any]:
        """Flatten array to specified depth."""
        if depth <= 0:
            return array.copy()
        
        result = []
        for item in array:
            if isinstance(item, list):
                result.extend(self.flatten(item, depth - 1))
            else:
                result.append(item)
        return result
    
    def flatten_deep(self, array: List[Any]) -> List[Any]:
        """Flatten array completely."""
        result = []
        for item in array:
            if isinstance(item, list):
                result.extend(self.flatten_deep(item))
            else:
                result.append(item)
        return result
    
    def reduce(self, array: List[Any], operation: str, initial: Any = None) -> Any:
        """Reduce array to single value."""
        if not array:
            return initial
        
        try:
            if operation == "sum":
                return sum(float(x) for x in array if self._is_numeric(x))
            elif operation == "product":
                result = 1
                for x in array:
                    if self._is_numeric(x):
                        result *= float(x)
                return result
            elif operation == "concat":
                return "".join(str(x) for x in array)
            elif operation == "max":
                return max(float(x) for x in array if self._is_numeric(x))
            elif operation == "min":
                return min(float(x) for x in array if self._is_numeric(x))
            elif operation == "average":
                numeric_values = [float(x) for x in array if self._is_numeric(x)]
                return sum(numeric_values) / len(numeric_values) if numeric_values else 0
            elif operation == "count":
                return len(array)
            else:
                return initial
        except Exception:
            return initial
    
    def sum(self, array: List[Any]) -> float:
        """Sum numeric values in array."""
        return sum(float(x) for x in array if self._is_numeric(x))
    
    def average(self, array: List[Any]) -> float:
        """Calculate average of numeric values."""
        numeric_values = [float(x) for x in array if self._is_numeric(x)]
        return sum(numeric_values) / len(numeric_values) if numeric_values else 0
    
    def min(self, array: List[Any]) -> Any:
        """Find minimum value."""
        if not array:
            return None
        
        try:
            numeric_values = [float(x) for x in array if self._is_numeric(x)]
            if numeric_values:
                return min(numeric_values)
            else:
                return min(array)
        except Exception:
            return None
    
    def max(self, array: List[Any]) -> Any:
        """Find maximum value."""
        if not array:
            return None
        
        try:
            numeric_values = [float(x) for x in array if self._is_numeric(x)]
            if numeric_values:
                return max(numeric_values)
            else:
                return max(array)
        except Exception:
            return None
    
    def product(self, array: List[Any]) -> float:
        """Calculate product of numeric values."""
        result = 1
        for x in array:
            if self._is_numeric(x):
                result *= float(x)
        return result
    
    def find(self, array: List[Any], predicate: str, value: Any = None) -> Any:
        """Find first element matching predicate."""
        filtered = self.filter(array, predicate, value)
        return filtered[0] if filtered else None
    
    def find_index(self, array: List[Any], predicate: str, value: Any = None) -> int:
        """Find index of first element matching predicate."""
        for i, item in enumerate(array):
            if self._matches_predicate(item, predicate, value):
                return i
        return -1
    
    def find_last(self, array: List[Any], predicate: str, value: Any = None) -> Any:
        """Find last element matching predicate."""
        filtered = self.filter(array, predicate, value)
        return filtered[-1] if filtered else None
    
    def find_last_index(self, array: List[Any], predicate: str, value: Any = None) -> int:
        """Find index of last element matching predicate."""
        for i in range(len(array) - 1, -1, -1):
            if self._matches_predicate(array[i], predicate, value):
                return i
        return -1
    
    def index_of(self, array: List[Any], element: Any) -> int:
        """Find first index of element."""
        try:
            return array.index(element)
        except ValueError:
            return -1
    
    def last_index_of(self, array: List[Any], element: Any) -> int:
        """Find last index of element."""
        for i in range(len(array) - 1, -1, -1):
            if array[i] == element:
                return i
        return -1
    
    def includes(self, array: List[Any], element: Any) -> bool:
        """Check if array includes element."""
        return element in array
    
    def count(self, array: List[Any], element: Any = None) -> int:
        """Count occurrences of element or total length."""
        if element is None:
            return len(array)
        return array.count(element)
    
    def unique(self, array: List[Any]) -> List[Any]:
        """Get unique elements while preserving order."""
        seen = set()
        result = []
        for item in array:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    def unique_by(self, array: List[Any], key: str) -> List[Any]:
        """Get unique elements by property."""
        seen = set()
        result = []
        for item in array:
            if isinstance(item, dict):
                key_value = item.get(key)
            else:
                key_value = getattr(item, key, None)
            
            if key_value not in seen:
                seen.add(key_value)
                result.append(item)
        return result
    
    def chunk(self, array: List[Any], size: int) -> List[List[Any]]:
        """Split array into chunks of specified size."""
        if size <= 0:
            return []
        
        return [array[i:i + size] for i in range(0, len(array), size)]
    
    def group_by(self, array: List[Any], key: str) -> Dict[str, List[Any]]:
        """Group array elements by property."""
        groups = defaultdict(list)
        for item in array:
            if isinstance(item, dict):
                group_key = item.get(key, 'undefined')
            else:
                group_key = getattr(item, key, 'undefined')
            groups[str(group_key)].append(item)
        return dict(groups)
    
    def partition(self, array: List[Any], predicate: str, value: Any = None) -> Dict[str, List[Any]]:
        """Partition array into two groups based on predicate."""
        truthy = []
        falsy = []
        
        for item in array:
            if self._matches_predicate(item, predicate, value):
                truthy.append(item)
            else:
                falsy.append(item)
        
        return {"truthy": truthy, "falsy": falsy}
    
    def transpose(self, array: List[List[Any]]) -> List[List[Any]]:
        """Transpose 2D array."""
        if not array or not array[0]:
            return []
        
        return list(map(list, zip(*array)))
    
    def zip(self, *arrays: List[Any]) -> List[List[Any]]:
        """Zip multiple arrays together."""
        return list(map(list, zip(*arrays)))
    
    def unzip(self, array: List[List[Any]]) -> List[List[Any]]:
        """Unzip array of arrays."""
        if not array:
            return []
        
        return list(map(list, zip(*array)))
    
    def union(self, *arrays: List[Any]) -> List[Any]:
        """Get union of arrays."""
        result = []
        seen = set()
        
        for array in arrays:
            for item in array:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
        
        return result
    
    def intersection(self, *arrays: List[Any]) -> List[Any]:
        """Get intersection of arrays."""
        if not arrays:
            return []
        
        result = []
        first_set = set(arrays[0])
        
        for item in arrays[0]:
            if item in result:
                continue
            
            if all(item in array for array in arrays[1:]):
                result.append(item)
        
        return result
    
    def difference(self, array: List[Any], *other_arrays: List[Any]) -> List[Any]:
        """Get difference of arrays."""
        exclude = set()
        for other_array in other_arrays:
            exclude.update(other_array)
        
        return [item for item in array if item not in exclude]
    
    def symmetric_difference(self, array1: List[Any], array2: List[Any]) -> List[Any]:
        """Get symmetric difference of two arrays."""
        set1 = set(array1)
        set2 = set(array2)
        return list(set1.symmetric_difference(set2))
    
    def is_empty(self, array: List[Any]) -> bool:
        """Check if array is empty."""
        return len(array) == 0
    
    def is_array(self, value: Any) -> bool:
        """Check if value is an array."""
        return isinstance(value, list)
    
    def every(self, array: List[Any], predicate: str, value: Any = None) -> bool:
        """Check if all elements match predicate."""
        return all(self._matches_predicate(item, predicate, value) for item in array)
    
    def some(self, array: List[Any], predicate: str, value: Any = None) -> bool:
        """Check if any element matches predicate."""
        return any(self._matches_predicate(item, predicate, value) for item in array)
    
    def none(self, array: List[Any], predicate: str, value: Any = None) -> bool:
        """Check if no elements match predicate."""
        return not self.some(array, predicate, value)
    
    def equals(self, array1: List[Any], array2: List[Any]) -> bool:
        """Check if arrays are equal."""
        return array1 == array2
    
    def deep_equals(self, array1: List[Any], array2: List[Any]) -> bool:
        """Check if arrays are deeply equal."""
        if len(array1) != len(array2):
            return False
        
        for a, b in zip(array1, array2):
            if isinstance(a, list) and isinstance(b, list):
                if not self.deep_equals(a, b):
                    return False
            elif a != b:
                return False
        
        return True
    
    def median(self, array: List[Any]) -> float:
        """Calculate median of numeric values."""
        numeric_values = [float(x) for x in array if self._is_numeric(x)]
        return statistics.median(numeric_values) if numeric_values else 0
    
    def mode(self, array: List[Any]) -> List[Any]:
        """Calculate mode of values."""
        if not array:
            return []
        
        counter = Counter(array)
        max_count = max(counter.values())
        return [item for item, count in counter.items() if count == max_count]
    
    def variance(self, array: List[Any]) -> float:
        """Calculate variance of numeric values."""
        numeric_values = [float(x) for x in array if self._is_numeric(x)]
        return statistics.variance(numeric_values) if len(numeric_values) > 1 else 0
    
    def standard_deviation(self, array: List[Any]) -> float:
        """Calculate standard deviation of numeric values."""
        numeric_values = [float(x) for x in array if self._is_numeric(x)]
        return statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
    
    def percentile(self, array: List[Any], percentile: float) -> float:
        """Calculate percentile of numeric values."""
        numeric_values = sorted([float(x) for x in array if self._is_numeric(x)])
        if not numeric_values:
            return 0
        
        index = (percentile / 100) * (len(numeric_values) - 1)
        lower = int(index)
        upper = min(lower + 1, len(numeric_values) - 1)
        
        if lower == upper:
            return numeric_values[lower]
        
        weight = index - lower
        return numeric_values[lower] * (1 - weight) + numeric_values[upper] * weight
    
    def shuffle(self, array: List[Any]) -> List[Any]:
        """Shuffle array randomly."""
        import random
        result = array.copy()
        random.shuffle(result)
        return result
    
    def sample(self, array: List[Any], count: int) -> List[Any]:
        """Sample random elements from array."""
        import random
        if count >= len(array):
            return array.copy()
        
        return random.sample(array, count)
    
    def take(self, array: List[Any], count: int) -> List[Any]:
        """Take first n elements."""
        return array[:count]
    
    def skip(self, array: List[Any], count: int) -> List[Any]:
        """Skip first n elements."""
        return array[count:]
    
    def head(self, array: List[Any], count: int = 1) -> List[Any]:
        """Get first n elements."""
        return array[:count]
    
    def tail(self, array: List[Any], count: int = 1) -> List[Any]:
        """Get last n elements."""
        return array[-count:] if count > 0 else []
    
    def rotate(self, array: List[Any], positions: int) -> List[Any]:
        """Rotate array by n positions."""
        if not array:
            return []
        
        positions = positions % len(array)
        return array[positions:] + array[:positions]
    
    def batch_process(self, arrays: List[List[Any]], operation: str, **kwargs) -> Dict[str, Any]:
        """Process multiple arrays with same operation."""
        results = []
        successful = 0
        failed = 0
        
        for i, array in enumerate(arrays):
            try:
                if hasattr(self, operation):
                    method = getattr(self, operation)
                    # Filter out conflicting parameters
                    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ["arrays", "operation"]}
                    result = method(array, **filtered_kwargs)
                    results.append(result)
                    successful += 1
                else:
                    results.append(None)
                    failed += 1
            except Exception as e:
                results.append(None)
                failed += 1
        
        return {
            "results": results,
            "successful": successful,
            "failed": failed,
            "total": len(arrays)
        }
    
    def batch_filter(self, arrays: List[List[Any]], predicate: str, value: Any = None) -> Dict[str, Any]:
        """Filter multiple arrays."""
        return self.batch_process(arrays, "filter", predicate=predicate, value=value)
    
    def batch_map(self, arrays: List[List[Any]], operation: str, value: Any = None) -> Dict[str, Any]:
        """Map multiple arrays."""
        return self.batch_process(arrays, "map", operation=operation, value=value)
    
    def batch_reduce(self, arrays: List[List[Any]], operation: str, initial: Any = None) -> Dict[str, Any]:
        """Reduce multiple arrays."""
        return self.batch_process(arrays, "reduce", operation=operation, initial=initial)
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _matches_predicate(self, item: Any, predicate: str, value: Any = None) -> bool:
        """Check if item matches predicate."""
        try:
            if predicate == "truthy":
                return bool(item)
            elif predicate == "falsy":
                return not bool(item)
            elif predicate == "null":
                return item is None
            elif predicate == "not_null":
                return item is not None
            elif predicate == "empty":
                return not item
            elif predicate == "not_empty":
                return bool(item)
            elif predicate == "numeric":
                return self._is_numeric(item)
            elif predicate == "string":
                return isinstance(item, str)
            elif predicate == "array":
                return isinstance(item, list)
            elif predicate == "object":
                return isinstance(item, dict)
            elif predicate == "equals":
                return item == value
            elif predicate == "not_equals":
                return item != value
            elif predicate == "greater_than":
                return self._is_numeric(item) and float(item) > float(value)
            elif predicate == "less_than":
                return self._is_numeric(item) and float(item) < float(value)
            elif predicate == "contains":
                return str(value) in str(item)
            else:
                return False
        except Exception:
            return False


class ArrayOperationsNode(BaseNode):
    """
    Array Operations Node for comprehensive array manipulation.
    
    Provides 60+ operations for working with arrays including:
    - Basic operations (sort, reverse, length, etc.)
    - Filtering and mapping with custom predicates
    - Reduction operations (sum, average, min, max, etc.)
    - Searching and indexing
    - Transformation (unique, flatten, chunk, group)
    - Set operations (union, intersection, difference)
    - Statistical operations (median, mode, variance, etc.)
    - Utility operations (shuffle, sample, rotate, etc.)
    - Batch processing for multiple arrays
    """
    
    def __init__(self):
        super().__init__()
        self.array_processor = ArrayProcessor()
    
    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            node_type="array_operations",
            version="1.0.0",
            description="Comprehensive array operations node with 60+ operations for filtering, mapping, reduction, and transformation",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Array operation to perform",
                    required=True,
                    enum=[op.value for op in ArrayOperation]
                ),
                NodeParameter(
                    name="array",
                    type=NodeParameterType.ARRAY,
                    description="Input array to process",
                    required=True
                ),
                NodeParameter(
                    name="arrays",
                    type=NodeParameterType.ARRAY,
                    description="Multiple arrays for batch operations",
                    required=False,
                    operations=["batch_process", "batch_filter", "batch_map", "batch_reduce", "union", "intersection", "difference", "zip"]
                ),
                NodeParameter(
                    name="predicate",
                    type=NodeParameterType.STRING,
                    description="Predicate for filtering operations",
                    required=False,
                    enum=["truthy", "falsy", "null", "not_null", "empty", "not_empty", "numeric", "string", "array", "object", "equals", "not_equals", "greater_than", "less_than", "contains"]
                ),
                NodeParameter(
                    name="value",
                    type=NodeParameterType.ANY,
                    description="Value for comparison operations",
                    required=False
                ),
                NodeParameter(
                    name="key",
                    type=NodeParameterType.STRING,
                    description="Key for sorting or property selection",
                    required=False
                ),
                NodeParameter(
                    name="reverse",
                    type=NodeParameterType.BOOLEAN,
                    description="Reverse order for sorting",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="start",
                    type=NodeParameterType.NUMBER,
                    description="Start index for slicing",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="end",
                    type=NodeParameterType.NUMBER,
                    description="End index for slicing",
                    required=False
                ),
                NodeParameter(
                    name="index",
                    type=NodeParameterType.NUMBER,
                    description="Index for insertion or removal",
                    required=False
                ),
                NodeParameter(
                    name="element",
                    type=NodeParameterType.ANY,
                    description="Element to add, remove, or search for",
                    required=False
                ),
                NodeParameter(
                    name="elements",
                    type=NodeParameterType.ARRAY,
                    description="Multiple elements to add",
                    required=False
                ),
                NodeParameter(
                    name="separator",
                    type=NodeParameterType.STRING,
                    description="Separator for join/split operations",
                    required=False,
                    default=","
                ),
                NodeParameter(
                    name="size",
                    type=NodeParameterType.NUMBER,
                    description="Size for chunking operations",
                    required=False
                ),
                NodeParameter(
                    name="depth",
                    type=NodeParameterType.NUMBER,
                    description="Depth for flatten operations",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="count",
                    type=NodeParameterType.NUMBER,
                    description="Count for sample/take/skip operations",
                    required=False
                ),
                NodeParameter(
                    name="positions",
                    type=NodeParameterType.NUMBER,
                    description="Positions for rotation",
                    required=False,
                    default=1
                ),
                NodeParameter(
                    name="percentile",
                    type=NodeParameterType.NUMBER,
                    description="Percentile value (0-100)",
                    required=False,
                    min_value=0,
                    max_value=100
                ),
                NodeParameter(
                    name="initial",
                    type=NodeParameterType.ANY,
                    description="Initial value for reduction",
                    required=False
                ),
                NodeParameter(
                    name="property_name",
                    type=NodeParameterType.STRING,
                    description="Property name for object operations",
                    required=False
                ),
                NodeParameter(
                    name="old_element",
                    type=NodeParameterType.ANY,
                    description="Element to replace",
                    required=False
                ),
                NodeParameter(
                    name="new_element",
                    type=NodeParameterType.ANY,
                    description="Replacement element",
                    required=False
                ),
                NodeParameter(
                    name="index1",
                    type=NodeParameterType.NUMBER,
                    description="First index for swapping",
                    required=False
                ),
                NodeParameter(
                    name="index2",
                    type=NodeParameterType.NUMBER,
                    description="Second index for swapping",
                    required=False
                ),
                NodeParameter(
                    name="string",
                    type=NodeParameterType.STRING,
                    description="String to split into array",
                    required=False
                ),
                NodeParameter(
                    name="array1",
                    type=NodeParameterType.ARRAY,
                    description="First array for comparison operations",
                    required=False
                ),
                NodeParameter(
                    name="array2",
                    type=NodeParameterType.ARRAY,
                    description="Second array for comparison operations",
                    required=False
                ),
                NodeParameter(
                    name="seed",
                    type=NodeParameterType.NUMBER,
                    description="Random seed for reproducible operations",
                    required=False
                )
            ],
            outputs={
                "result": NodeParameterType.ANY,
                "metadata": NodeParameterType.OBJECT
            },
            tags=["array", "list", "data", "manipulation", "utility"],
            author="System"
        )
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters based on operation."""
        operation = params.get("operation")
        
        if not operation:
            return {"valid": False, "error": "Operation is required"}
        
        if operation not in [op.value for op in ArrayOperation]:
            return {"valid": False, "error": f"Invalid operation: {operation}"}
        
        # Check for required parameters based on operation
        if operation in ["batch_process", "batch_filter", "batch_map", "batch_reduce"]:
            if "arrays" not in params:
                return {"valid": False, "error": f"Operation {operation} requires 'arrays' parameter"}
        elif operation == "split":
            if "string" not in params:
                return {"valid": False, "error": "Split operation requires 'string' parameter"}
        elif operation in ["equals", "deep_equals"]:
            if "array1" not in params or "array2" not in params:
                return {"valid": False, "error": f"Operation {operation} requires 'array1' and 'array2' parameters"}
        elif operation == "symmetric_difference":
            if "array1" not in params or "array2" not in params:
                return {"valid": False, "error": "Symmetric difference requires 'array1' and 'array2' parameters"}
        elif operation == "zip":
            if "arrays" not in params:
                return {"valid": False, "error": "Zip operation requires 'arrays' parameter"}
        elif operation not in ["split", "equals", "deep_equals", "symmetric_difference", "zip"] and "array" not in params:
            return {"valid": False, "error": f"Operation {operation} requires 'array' parameter"}
        
        return {"valid": True}
    
    # Operation metadata for parameter validation
    OPERATION_METADATA = {
        # Basic Operations
        ArrayOperation.SORT: {"required": ["array"], "optional": ["reverse", "key"]},
        ArrayOperation.REVERSE: {"required": ["array"], "optional": []},
        ArrayOperation.LENGTH: {"required": ["array"], "optional": []},
        ArrayOperation.CLEAR: {"required": ["array"], "optional": []},
        ArrayOperation.COPY: {"required": ["array"], "optional": []},
        ArrayOperation.SLICE: {"required": ["array"], "optional": ["start", "end"]},
        ArrayOperation.CONCAT: {"required": ["array"], "optional": ["arrays"]},
        ArrayOperation.JOIN: {"required": ["array"], "optional": ["separator"]},
        ArrayOperation.SPLIT: {"required": ["string"], "optional": ["separator"]},
        
        # Element Operations
        ArrayOperation.PUSH: {"required": ["array"], "optional": ["element", "elements"]},
        ArrayOperation.POP: {"required": ["array"], "optional": []},
        ArrayOperation.SHIFT: {"required": ["array"], "optional": []},
        ArrayOperation.UNSHIFT: {"required": ["array"], "optional": ["element", "elements"]},
        ArrayOperation.INSERT: {"required": ["array", "index"], "optional": ["element", "elements"]},
        ArrayOperation.REMOVE: {"required": ["array", "element"], "optional": []},
        ArrayOperation.REMOVE_AT: {"required": ["array", "index"], "optional": []},
        ArrayOperation.REPLACE: {"required": ["array", "old_element", "new_element"], "optional": []},
        ArrayOperation.SWAP: {"required": ["array", "index1", "index2"], "optional": []},
        
        # Filtering and Mapping
        ArrayOperation.FILTER: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.MAP: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.SELECT: {"required": ["array", "property_name"], "optional": []},
        ArrayOperation.REJECT: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.COMPACT: {"required": ["array"], "optional": []},
        ArrayOperation.FLATTEN: {"required": ["array"], "optional": ["depth"]},
        ArrayOperation.FLATTEN_DEEP: {"required": ["array"], "optional": []},
        
        # Reduction
        ArrayOperation.REDUCE: {"required": ["array", "predicate"], "optional": ["initial"]},
        ArrayOperation.SUM: {"required": ["array"], "optional": []},
        ArrayOperation.AVERAGE: {"required": ["array"], "optional": []},
        ArrayOperation.MIN: {"required": ["array"], "optional": []},
        ArrayOperation.MAX: {"required": ["array"], "optional": []},
        ArrayOperation.PRODUCT: {"required": ["array"], "optional": []},
        ArrayOperation.AGGREGATE: {"required": ["array", "predicate"], "optional": ["initial"]},
        
        # Searching
        ArrayOperation.FIND: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.FIND_INDEX: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.FIND_LAST: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.FIND_LAST_INDEX: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.INDEX_OF: {"required": ["array", "element"], "optional": []},
        ArrayOperation.LAST_INDEX_OF: {"required": ["array", "element"], "optional": []},
        ArrayOperation.INCLUDES: {"required": ["array", "element"], "optional": []},
        ArrayOperation.COUNT: {"required": ["array"], "optional": ["element"]},
        
        # Transformation
        ArrayOperation.UNIQUE: {"required": ["array"], "optional": []},
        ArrayOperation.UNIQUE_BY: {"required": ["array", "key"], "optional": []},
        ArrayOperation.CHUNK: {"required": ["array", "size"], "optional": []},
        ArrayOperation.GROUP_BY: {"required": ["array", "key"], "optional": []},
        ArrayOperation.PARTITION: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.TRANSPOSE: {"required": ["array"], "optional": []},
        ArrayOperation.ZIP: {"required": ["arrays"], "optional": []},
        ArrayOperation.UNZIP: {"required": ["array"], "optional": []},
        
        # Set Operations
        ArrayOperation.UNION: {"required": ["arrays"], "optional": []},
        ArrayOperation.INTERSECTION: {"required": ["arrays"], "optional": []},
        ArrayOperation.DIFFERENCE: {"required": ["array"], "optional": ["arrays"]},
        ArrayOperation.SYMMETRIC_DIFFERENCE: {"required": ["array1", "array2"], "optional": []},
        
        # Validation
        ArrayOperation.IS_EMPTY: {"required": ["array"], "optional": []},
        ArrayOperation.IS_ARRAY: {"required": ["value"], "optional": []},
        ArrayOperation.EVERY: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.SOME: {"required": ["array", "predicate"], "optional": ["value"]},
        ArrayOperation.NONE: {"required": ["array", "predicate"], "optional": ["value"]},
        
        # Comparison
        ArrayOperation.EQUALS: {"required": ["array1", "array2"], "optional": []},
        ArrayOperation.DEEP_EQUALS: {"required": ["array1", "array2"], "optional": []},
        
        # Sorting
        ArrayOperation.SORT_BY: {"required": ["array", "key"], "optional": ["reverse"]},
        ArrayOperation.SORT_NUMERIC: {"required": ["array"], "optional": ["reverse"]},
        ArrayOperation.SORT_ALPHABETIC: {"required": ["array"], "optional": ["reverse"]},
        ArrayOperation.SORT_REVERSE: {"required": ["array"], "optional": []},
        
        # Statistical
        ArrayOperation.MEDIAN: {"required": ["array"], "optional": []},
        ArrayOperation.MODE: {"required": ["array"], "optional": []},
        ArrayOperation.VARIANCE: {"required": ["array"], "optional": []},
        ArrayOperation.STANDARD_DEVIATION: {"required": ["array"], "optional": []},
        ArrayOperation.PERCENTILE: {"required": ["array", "percentile"], "optional": []},
        
        # Utility
        ArrayOperation.SHUFFLE: {"required": ["array"], "optional": ["seed"]},
        ArrayOperation.SAMPLE: {"required": ["array", "count"], "optional": ["seed"]},
        ArrayOperation.TAKE: {"required": ["array", "count"], "optional": []},
        ArrayOperation.SKIP: {"required": ["array", "count"], "optional": []},
        ArrayOperation.HEAD: {"required": ["array"], "optional": ["count"]},
        ArrayOperation.TAIL: {"required": ["array"], "optional": ["count"]},
        ArrayOperation.ROTATE: {"required": ["array"], "optional": ["positions"]},
        
        # Batch Operations
        ArrayOperation.BATCH_PROCESS: {"required": ["arrays", "predicate"], "optional": []},
        ArrayOperation.BATCH_FILTER: {"required": ["arrays", "predicate"], "optional": ["value"]},
        ArrayOperation.BATCH_MAP: {"required": ["arrays", "predicate"], "optional": ["value"]},
        ArrayOperation.BATCH_REDUCE: {"required": ["arrays", "predicate"], "optional": ["initial"]},
    }
    
    # Dispatch map for operations
    dispatch_map = {
        # Basic Operations
        ArrayOperation.SORT: "sort",
        ArrayOperation.REVERSE: "reverse",
        ArrayOperation.LENGTH: "length",
        ArrayOperation.CLEAR: "clear",
        ArrayOperation.COPY: "copy",
        ArrayOperation.SLICE: "slice",
        ArrayOperation.CONCAT: "concat",
        ArrayOperation.JOIN: "join",
        ArrayOperation.SPLIT: "split",
        
        # Element Operations
        ArrayOperation.PUSH: "push",
        ArrayOperation.POP: "pop",
        ArrayOperation.SHIFT: "shift",
        ArrayOperation.UNSHIFT: "unshift",
        ArrayOperation.INSERT: "insert",
        ArrayOperation.REMOVE: "remove",
        ArrayOperation.REMOVE_AT: "remove_at",
        ArrayOperation.REPLACE: "replace",
        ArrayOperation.SWAP: "swap",
        
        # Filtering and Mapping
        ArrayOperation.FILTER: "filter",
        ArrayOperation.MAP: "map",
        ArrayOperation.SELECT: "select",
        ArrayOperation.REJECT: "reject",
        ArrayOperation.COMPACT: "compact",
        ArrayOperation.FLATTEN: "flatten",
        ArrayOperation.FLATTEN_DEEP: "flatten_deep",
        
        # Reduction
        ArrayOperation.REDUCE: "reduce",
        ArrayOperation.SUM: "sum",
        ArrayOperation.AVERAGE: "average",
        ArrayOperation.MIN: "min",
        ArrayOperation.MAX: "max",
        ArrayOperation.PRODUCT: "product",
        ArrayOperation.AGGREGATE: "reduce",
        
        # Searching
        ArrayOperation.FIND: "find",
        ArrayOperation.FIND_INDEX: "find_index",
        ArrayOperation.FIND_LAST: "find_last",
        ArrayOperation.FIND_LAST_INDEX: "find_last_index",
        ArrayOperation.INDEX_OF: "index_of",
        ArrayOperation.LAST_INDEX_OF: "last_index_of",
        ArrayOperation.INCLUDES: "includes",
        ArrayOperation.COUNT: "count",
        
        # Transformation
        ArrayOperation.UNIQUE: "unique",
        ArrayOperation.UNIQUE_BY: "unique_by",
        ArrayOperation.CHUNK: "chunk",
        ArrayOperation.GROUP_BY: "group_by",
        ArrayOperation.PARTITION: "partition",
        ArrayOperation.TRANSPOSE: "transpose",
        ArrayOperation.ZIP: "zip",
        ArrayOperation.UNZIP: "unzip",
        
        # Set Operations
        ArrayOperation.UNION: "union",
        ArrayOperation.INTERSECTION: "intersection",
        ArrayOperation.DIFFERENCE: "difference",
        ArrayOperation.SYMMETRIC_DIFFERENCE: "symmetric_difference",
        
        # Validation
        ArrayOperation.IS_EMPTY: "is_empty",
        ArrayOperation.IS_ARRAY: "is_array",
        ArrayOperation.EVERY: "every",
        ArrayOperation.SOME: "some",
        ArrayOperation.NONE: "none",
        
        # Comparison
        ArrayOperation.EQUALS: "equals",
        ArrayOperation.DEEP_EQUALS: "deep_equals",
        
        # Sorting
        ArrayOperation.SORT_BY: "sort_by",
        ArrayOperation.SORT_NUMERIC: "sort_numeric",
        ArrayOperation.SORT_ALPHABETIC: "sort_alphabetic",
        ArrayOperation.SORT_REVERSE: "sort_reverse",
        
        # Statistical
        ArrayOperation.MEDIAN: "median",
        ArrayOperation.MODE: "mode",
        ArrayOperation.VARIANCE: "variance",
        ArrayOperation.STANDARD_DEVIATION: "standard_deviation",
        ArrayOperation.PERCENTILE: "percentile",
        
        # Utility
        ArrayOperation.SHUFFLE: "shuffle",
        ArrayOperation.SAMPLE: "sample",
        ArrayOperation.TAKE: "take",
        ArrayOperation.SKIP: "skip",
        ArrayOperation.HEAD: "head",
        ArrayOperation.TAIL: "tail",
        ArrayOperation.ROTATE: "rotate",
        
        # Batch Operations
        ArrayOperation.BATCH_PROCESS: "batch_process",
        ArrayOperation.BATCH_FILTER: "batch_filter",
        ArrayOperation.BATCH_MAP: "batch_map",
        ArrayOperation.BATCH_REDUCE: "batch_reduce",
    }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute array operation."""
        try:
            # Validate parameters
            validation_result = self.validate_params(params)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            operation = ArrayOperation(params["operation"])
            
            # Set random seed if provided
            if "seed" in params:
                self.array_processor.set_seed(params["seed"])
            
            # Get the method to call
            method_name = self.dispatch_map.get(operation)
            if not method_name:
                return {
                    "status": "error",
                    "message": f"Operation {operation} not implemented",
                    "timestamp": datetime.now().isoformat()
                }
            
            method = getattr(self.array_processor, method_name)
            
            # Prepare method arguments based on operation
            if operation in [ArrayOperation.SORT_BY, ArrayOperation.SORT_NUMERIC, ArrayOperation.SORT_ALPHABETIC]:
                # Handle sort variants
                if operation == ArrayOperation.SORT_BY:
                    result = self.array_processor.sort(params["array"], params.get("reverse", False), params["key"])
                elif operation == ArrayOperation.SORT_NUMERIC:
                    result = self.array_processor.sort(params["array"], params.get("reverse", False), "numeric")
                elif operation == ArrayOperation.SORT_ALPHABETIC:
                    result = self.array_processor.sort(params["array"], params.get("reverse", False), "alphabetic")
            elif operation == ArrayOperation.SORT_REVERSE:
                result = self.array_processor.sort(params["array"], True)
            elif operation == ArrayOperation.SPLIT:
                result = method(params["string"], params.get("separator", ","))
            elif operation in [ArrayOperation.EQUALS, ArrayOperation.DEEP_EQUALS, ArrayOperation.SYMMETRIC_DIFFERENCE]:
                result = method(params["array1"], params["array2"])
            elif operation == ArrayOperation.ZIP:
                result = method(*params["arrays"])
            elif operation == ArrayOperation.UNION:
                result = method(*params["arrays"])
            elif operation == ArrayOperation.INTERSECTION:
                result = method(*params["arrays"])
            elif operation == ArrayOperation.DIFFERENCE:
                other_arrays = params.get("arrays", [])
                result = method(params["array"], *other_arrays)
            elif operation == ArrayOperation.CONCAT:
                other_arrays = params.get("arrays", [])
                result = method(params["array"], *other_arrays)
            elif operation == ArrayOperation.PUSH:
                elements = params.get("elements", [])
                if "element" in params:
                    elements = [params["element"]] + elements
                result = method(params["array"], *elements)
            elif operation == ArrayOperation.UNSHIFT:
                elements = params.get("elements", [])
                if "element" in params:
                    elements = [params["element"]] + elements
                result = method(params["array"], *elements)
            elif operation == ArrayOperation.INSERT:
                elements = params.get("elements", [])
                if "element" in params:
                    elements = [params["element"]] + elements
                result = method(params["array"], params["index"], *elements)
            elif operation == ArrayOperation.IS_ARRAY:
                result = method(params.get("value", params.get("array")))
            else:
                # Build arguments dynamically
                args = []
                kwargs = {}
                
                # Always include the primary array if it exists
                if "array" in params:
                    args.append(params["array"])
                
                # Add other parameters based on operation metadata
                metadata = self.OPERATION_METADATA.get(operation, {})
                for param_name in metadata.get("required", []):
                    if param_name != "array" and param_name in params:
                        args.append(params[param_name])
                
                for param_name in metadata.get("optional", []):
                    if param_name in params:
                        kwargs[param_name] = params[param_name]
                
                # Handle special cases
                if operation in [ArrayOperation.FILTER, ArrayOperation.MAP, ArrayOperation.REDUCE, ArrayOperation.AGGREGATE]:
                    # These operations need the operation/predicate parameter
                    if "predicate" in params and len(args) == 1:
                        args.append(params["predicate"])
                    
                    # Add value parameter if present
                    if "value" in params:
                        if operation in [ArrayOperation.FILTER, ArrayOperation.MAP]:
                            args.append(params["value"])
                        else:
                            kwargs["value"] = params["value"]
                
                # Call the method
                result = method(*args, **kwargs)
            
            # Prepare response
            response = {
                "status": "success",
                "result": {
                    "result": result,
                    "operation": operation.value,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Add metadata based on operation type
            if operation in [ArrayOperation.LENGTH, ArrayOperation.COUNT]:
                response["result"]["count"] = result
            elif operation in [ArrayOperation.SUM, ArrayOperation.AVERAGE, ArrayOperation.MIN, ArrayOperation.MAX, ArrayOperation.PRODUCT]:
                response["result"]["value"] = result
            elif operation in [ArrayOperation.BATCH_PROCESS, ArrayOperation.BATCH_FILTER, ArrayOperation.BATCH_MAP, ArrayOperation.BATCH_REDUCE]:
                response["result"]["successful"] = result.get("successful", 0)
                response["result"]["failed"] = result.get("failed", 0)
                response["result"]["total"] = result.get("total", 0)
            
            return response
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Array operation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


# Register the node
from base_node import NodeRegistry
NodeRegistry.register("array_operations", ArrayOperationsNode)