#!/usr/bin/env python3
"""
Loop Node for ACT Workflow System

This node provides comprehensive loop control capabilities including:
- For loops with range, list, and dictionary iteration
- While loops with condition evaluation
- Do-while loops
- Nested loop support
- Loop control (break, continue, skip conditions)
- Iteration tracking and statistics
- Parallel iteration support
- Custom iterator support
- Loop optimization and performance monitoring
"""

import time
import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, Iterator
from collections.abc import Iterable

from base_node import BaseNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoopError(Exception):
    """Custom exception for loop errors."""
    pass

class LoopOperation(str, Enum):
    """Enumeration of all loop operations."""
    
    # Basic Loop Types
    FOR_RANGE = "for_range"
    FOR_LIST = "for_list"
    FOR_DICT = "for_dict"
    FOR_ENUMERATE = "for_enumerate"
    FOR_ZIP = "for_zip"
    WHILE = "while"
    DO_WHILE = "do_while"
    
    # Advanced Loop Types
    FOR_NESTED = "for_nested"
    FOR_PARALLEL = "for_parallel"
    FOR_BATCH = "for_batch"
    FOR_CUSTOM = "for_custom"
    
    # Loop Control
    BREAK_CONDITION = "break_condition"
    CONTINUE_CONDITION = "continue_condition"
    SKIP_CONDITION = "skip_condition"
    
    # Iteration Operations
    ITERATE_SLICE = "iterate_slice"
    ITERATE_FILTER = "iterate_filter"
    ITERATE_MAP = "iterate_map"
    ITERATE_REDUCE = "iterate_reduce"
    
    # Performance Operations
    MEASURE_PERFORMANCE = "measure_performance"
    OPTIMIZE_LOOP = "optimize_loop"
    PROFILE_ITERATIONS = "profile_iterations"

class LoopProcessor:
    """Core loop processing engine."""
    
    def __init__(self):
        self.max_iterations = 10000  # Safety limit
        self.break_requested = False
        self.continue_requested = False
        self.iteration_stats = {}
    
    def reset_control_flags(self):
        """Reset loop control flags."""
        self.break_requested = False
        self.continue_requested = False
    
    def for_range(self, start: int, stop: int, step: int = 1, 
                  operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a for loop with range."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for i in range(start, stop, step):
                if iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(i)
                    results.append({
                        'index': i,
                        'value': result,
                        'iteration': iterations
                    })
                else:
                    results.append({
                        'index': i,
                        'value': i,
                        'iteration': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
        
        except Exception as e:
            logger.error(f"Error in for_range loop: {e}")
            raise LoopError(f"For range loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'start': start,
            'stop': stop,
            'step': step,
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def for_list(self, items: List[Any], operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a for loop over a list."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for index, item in enumerate(items):
                if iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(item, index)
                    results.append({
                        'index': index,
                        'item': item,
                        'value': result,
                        'iteration': iterations
                    })
                else:
                    results.append({
                        'index': index,
                        'item': item,
                        'value': item,
                        'iteration': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
        
        except Exception as e:
            logger.error(f"Error in for_list loop: {e}")
            raise LoopError(f"For list loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'items_count': len(items),
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def for_dict(self, dictionary: Dict[Any, Any], operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a for loop over a dictionary."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for key, value in dictionary.items():
                if iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(key, value)
                    results.append({
                        'key': key,
                        'value': value,
                        'result': result,
                        'iteration': iterations
                    })
                else:
                    results.append({
                        'key': key,
                        'value': value,
                        'result': {'key': key, 'value': value},
                        'iteration': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
        
        except Exception as e:
            logger.error(f"Error in for_dict loop: {e}")
            raise LoopError(f"For dict loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'items_count': len(dictionary),
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def for_enumerate(self, items: List[Any], operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a for loop with enumeration."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for index, item in enumerate(items):
                if iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(index, item)
                    results.append({
                        'index': index,
                        'item': item,
                        'value': result,
                        'iteration': iterations
                    })
                else:
                    results.append({
                        'index': index,
                        'item': item,
                        'value': (index, item),
                        'iteration': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
        
        except Exception as e:
            logger.error(f"Error in for_enumerate loop: {e}")
            raise LoopError(f"For enumerate loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'items_count': len(items),
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def for_zip(self, *iterables, operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a for loop with zip."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for items in zip(*iterables):
                if iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(*items)
                    results.append({
                        'items': items,
                        'value': result,
                        'iteration': iterations
                    })
                else:
                    results.append({
                        'items': items,
                        'value': items,
                        'iteration': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
        
        except Exception as e:
            logger.error(f"Error in for_zip loop: {e}")
            raise LoopError(f"For zip loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'iterables_count': len(iterables),
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def while_loop(self, condition: Callable, operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a while loop."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            while condition() and iterations < self.max_iterations:
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(iterations)
                    results.append({
                        'iteration': iterations,
                        'value': result
                    })
                else:
                    results.append({
                        'iteration': iterations,
                        'value': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
        
        except Exception as e:
            logger.error(f"Error in while loop: {e}")
            raise LoopError(f"While loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def do_while_loop(self, condition: Callable, operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a do-while loop."""
        results = []
        iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            while True:
                if iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    if not condition():
                        break
                    continue
                
                iteration_start = time.time()
                
                if operation:
                    result = operation(iterations)
                    results.append({
                        'iteration': iterations,
                        'value': result
                    })
                else:
                    results.append({
                        'iteration': iterations,
                        'value': iterations
                    })
                
                iterations += 1
                
                # Track iteration time
                iteration_time = time.time() - iteration_start
                if iterations not in self.iteration_stats:
                    self.iteration_stats[iterations] = []
                self.iteration_stats[iterations].append(iteration_time)
                
                # Check condition after execution
                if not condition():
                    break
        
        except Exception as e:
            logger.error(f"Error in do-while loop: {e}")
            raise LoopError(f"Do-while loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': iterations,
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / iterations if iterations > 0 else 0
        }
    
    def for_nested(self, outer_iterable: Iterable, inner_iterable: Iterable, 
                   operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute nested for loops."""
        results = []
        outer_iterations = 0
        total_iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for outer_item in outer_iterable:
                if total_iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                inner_iterations = 0
                inner_results = []
                
                for inner_item in inner_iterable:
                    if total_iterations >= self.max_iterations:
                        break
                    
                    if self.break_requested:
                        break
                    
                    if self.continue_requested:
                        self.continue_requested = False
                        continue
                    
                    iteration_start = time.time()
                    
                    if operation:
                        result = operation(outer_item, inner_item)
                        inner_results.append({
                            'outer_item': outer_item,
                            'inner_item': inner_item,
                            'value': result,
                            'inner_iteration': inner_iterations,
                            'total_iteration': total_iterations
                        })
                    else:
                        inner_results.append({
                            'outer_item': outer_item,
                            'inner_item': inner_item,
                            'value': (outer_item, inner_item),
                            'inner_iteration': inner_iterations,
                            'total_iteration': total_iterations
                        })
                    
                    inner_iterations += 1
                    total_iterations += 1
                    
                    # Track iteration time
                    iteration_time = time.time() - iteration_start
                    if total_iterations not in self.iteration_stats:
                        self.iteration_stats[total_iterations] = []
                    self.iteration_stats[total_iterations].append(iteration_time)
                
                results.append({
                    'outer_iteration': outer_iterations,
                    'outer_item': outer_item,
                    'inner_results': inner_results,
                    'inner_iterations': inner_iterations
                })
                
                outer_iterations += 1
        
        except Exception as e:
            logger.error(f"Error in nested for loop: {e}")
            raise LoopError(f"Nested for loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'outer_iterations': outer_iterations,
            'total_iterations': total_iterations,
            'execution_time': end_time - start_time,
            'avg_iteration_time': (end_time - start_time) / total_iterations if total_iterations > 0 else 0
        }
    
    async def for_parallel(self, items: List[Any], operation: Callable, 
                          max_workers: int = 5) -> Dict[str, Any]:
        """Execute a for loop with parallel processing."""
        results = []
        start_time = time.time()
        
        try:
            # Create semaphore to limit concurrent operations
            semaphore = asyncio.Semaphore(max_workers)
            
            async def process_item(item, index):
                async with semaphore:
                    iteration_start = time.time()
                    
                    if asyncio.iscoroutinefunction(operation):
                        result = await operation(item, index)
                    else:
                        result = operation(item, index)
                    
                    iteration_time = time.time() - iteration_start
                    
                    return {
                        'index': index,
                        'item': item,
                        'value': result,
                        'iteration_time': iteration_time
                    }
            
            # Create tasks for all items
            tasks = [process_item(item, i) for i, item in enumerate(items)]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error in parallel for loop: {e}")
            raise LoopError(f"Parallel for loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_iterations': len(items),
            'max_workers': max_workers,
            'execution_time': end_time - start_time,
            'avg_iteration_time': sum(r['iteration_time'] for r in results) / len(results) if results else 0
        }
    
    def for_batch(self, items: List[Any], batch_size: int, 
                  operation: Optional[Callable] = None) -> Dict[str, Any]:
        """Execute a for loop with batch processing."""
        results = []
        batch_count = 0
        total_iterations = 0
        start_time = time.time()
        
        self.reset_control_flags()
        
        try:
            for i in range(0, len(items), batch_size):
                if total_iterations >= self.max_iterations:
                    break
                
                if self.break_requested:
                    break
                
                if self.continue_requested:
                    self.continue_requested = False
                    continue
                
                batch_start = time.time()
                batch = items[i:i + batch_size]
                
                if operation:
                    result = operation(batch, batch_count)
                    results.append({
                        'batch_index': batch_count,
                        'batch': batch,
                        'batch_size': len(batch),
                        'value': result,
                        'start_index': i,
                        'end_index': min(i + batch_size, len(items))
                    })
                else:
                    results.append({
                        'batch_index': batch_count,
                        'batch': batch,
                        'batch_size': len(batch),
                        'value': batch,
                        'start_index': i,
                        'end_index': min(i + batch_size, len(items))
                    })
                
                batch_count += 1
                total_iterations += len(batch)
                
                # Track batch time
                batch_time = time.time() - batch_start
                if batch_count not in self.iteration_stats:
                    self.iteration_stats[batch_count] = []
                self.iteration_stats[batch_count].append(batch_time)
        
        except Exception as e:
            logger.error(f"Error in batch for loop: {e}")
            raise LoopError(f"Batch for loop error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'total_batches': batch_count,
            'total_iterations': total_iterations,
            'batch_size': batch_size,
            'execution_time': end_time - start_time,
            'avg_batch_time': (end_time - start_time) / batch_count if batch_count > 0 else 0
        }
    
    def iterate_slice(self, items: List[Any], start: int, stop: int, step: int = 1) -> Dict[str, Any]:
        """Iterate over a slice of items."""
        start_time = time.time()
        
        try:
            sliced_items = items[start:stop:step]
            results = []
            
            for i, item in enumerate(sliced_items):
                results.append({
                    'slice_index': i,
                    'original_index': start + (i * step),
                    'item': item,
                    'value': item
                })
        
        except Exception as e:
            logger.error(f"Error in slice iteration: {e}")
            raise LoopError(f"Slice iteration error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'slice_size': len(sliced_items),
            'start': start,
            'stop': stop,
            'step': step,
            'execution_time': end_time - start_time
        }
    
    def iterate_filter(self, items: List[Any], filter_func: Callable) -> Dict[str, Any]:
        """Iterate over filtered items."""
        start_time = time.time()
        
        try:
            filtered_items = []
            results = []
            
            for i, item in enumerate(items):
                if filter_func(item):
                    filtered_items.append(item)
                    results.append({
                        'filtered_index': len(filtered_items) - 1,
                        'original_index': i,
                        'item': item,
                        'value': item
                    })
        
        except Exception as e:
            logger.error(f"Error in filter iteration: {e}")
            raise LoopError(f"Filter iteration error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'original_count': len(items),
            'filtered_count': len(filtered_items),
            'filter_ratio': len(filtered_items) / len(items) if items else 0,
            'execution_time': end_time - start_time
        }
    
    def iterate_map(self, items: List[Any], map_func: Callable) -> Dict[str, Any]:
        """Iterate with mapping function."""
        start_time = time.time()
        
        try:
            results = []
            
            for i, item in enumerate(items):
                mapped_value = map_func(item)
                results.append({
                    'index': i,
                    'original_item': item,
                    'mapped_value': mapped_value,
                    'value': mapped_value
                })
        
        except Exception as e:
            logger.error(f"Error in map iteration: {e}")
            raise LoopError(f"Map iteration error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'item_count': len(items),
            'execution_time': end_time - start_time
        }
    
    def iterate_reduce(self, items: List[Any], reduce_func: Callable, initial_value: Any = None) -> Dict[str, Any]:
        """Iterate with reduce function."""
        start_time = time.time()
        
        try:
            if initial_value is not None:
                accumulator = initial_value
            else:
                accumulator = items[0] if items else None
                items = items[1:]
            
            results = []
            
            for i, item in enumerate(items):
                accumulator = reduce_func(accumulator, item)
                results.append({
                    'index': i,
                    'item': item,
                    'accumulator': accumulator,
                    'value': accumulator
                })
        
        except Exception as e:
            logger.error(f"Error in reduce iteration: {e}")
            raise LoopError(f"Reduce iteration error: {e}")
        
        end_time = time.time()
        
        return {
            'results': results,
            'final_value': accumulator,
            'item_count': len(items),
            'execution_time': end_time - start_time
        }
    
    def measure_performance(self, loop_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Measure loop performance."""
        start_time = time.time()
        memory_start = self._get_memory_usage()
        
        try:
            result = loop_func(*args, **kwargs)
            
            end_time = time.time()
            memory_end = self._get_memory_usage()
            
            return {
                'result': result,
                'execution_time': end_time - start_time,
                'memory_usage': memory_end - memory_start,
                'iterations_per_second': result.get('total_iterations', 0) / (end_time - start_time) if end_time > start_time else 0,
                'performance_metrics': {
                    'total_time': end_time - start_time,
                    'memory_delta': memory_end - memory_start,
                    'iterations': result.get('total_iterations', 0)
                }
            }
        
        except Exception as e:
            logger.error(f"Error measuring performance: {e}")
            raise LoopError(f"Performance measurement error: {e}")
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0
    
    def profile_iterations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Profile iteration performance."""
        if not self.iteration_stats:
            return {
                'profile': {},
                'summary': {
                    'total_iterations': 0,
                    'avg_time': 0,
                    'min_time': 0,
                    'max_time': 0
                }
            }
        
        all_times = []
        for iteration_times in self.iteration_stats.values():
            all_times.extend(iteration_times)
        
        if not all_times:
            return {
                'profile': {},
                'summary': {
                    'total_iterations': 0,
                    'avg_time': 0,
                    'min_time': 0,
                    'max_time': 0
                }
            }
        
        return {
            'profile': {
                'iteration_times': self.iteration_stats,
                'slowest_iterations': sorted(
                    [(k, max(v)) for k, v in self.iteration_stats.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            },
            'summary': {
                'total_iterations': len(all_times),
                'avg_time': sum(all_times) / len(all_times),
                'min_time': min(all_times),
                'max_time': max(all_times),
                'total_time': sum(all_times)
            }
        }

class LoopNode(BaseNode):
    """
    Loop node for ACT workflow system.
    
    Provides comprehensive loop control capabilities including:
    - For loops with various iteration patterns
    - While and do-while loops
    - Nested and parallel loops
    - Loop control and optimization
    - Performance monitoring and profiling
    """
    
    def __init__(self):
        super().__init__()
        self.processor = LoopProcessor()
        
        # Dispatch map for operations
        self.dispatch_map = {
            LoopOperation.FOR_RANGE: self._handle_for_range,
            LoopOperation.FOR_LIST: self._handle_for_list,
            LoopOperation.FOR_DICT: self._handle_for_dict,
            LoopOperation.FOR_ENUMERATE: self._handle_for_enumerate,
            LoopOperation.FOR_ZIP: self._handle_for_zip,
            LoopOperation.WHILE: self._handle_while,
            LoopOperation.DO_WHILE: self._handle_do_while,
            LoopOperation.FOR_NESTED: self._handle_for_nested,
            LoopOperation.FOR_PARALLEL: self._handle_for_parallel,
            LoopOperation.FOR_BATCH: self._handle_for_batch,
            LoopOperation.FOR_CUSTOM: self._handle_for_custom,
            LoopOperation.BREAK_CONDITION: self._handle_break_condition,
            LoopOperation.CONTINUE_CONDITION: self._handle_continue_condition,
            LoopOperation.SKIP_CONDITION: self._handle_skip_condition,
            LoopOperation.ITERATE_SLICE: self._handle_iterate_slice,
            LoopOperation.ITERATE_FILTER: self._handle_iterate_filter,
            LoopOperation.ITERATE_MAP: self._handle_iterate_map,
            LoopOperation.ITERATE_REDUCE: self._handle_iterate_reduce,
            LoopOperation.MEASURE_PERFORMANCE: self._handle_measure_performance,
            LoopOperation.OPTIMIZE_LOOP: self._handle_optimize_loop,
            LoopOperation.PROFILE_ITERATIONS: self._handle_profile_iterations,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for loop operations."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in LoopOperation],
                    "description": "Loop operation to perform"
                },
                "start": {
                    "type": "integer",
                    "description": "Start value for range"
                },
                "stop": {
                    "type": "integer",
                    "description": "Stop value for range"
                },
                "step": {
                    "type": "integer",
                    "description": "Step value for range"
                },
                "items": {
                    "type": "array",
                    "description": "Items to iterate over"
                },
                "dictionary": {
                    "type": "object",
                    "description": "Dictionary to iterate over"
                },
                "iterables": {
                    "type": "array",
                    "description": "Multiple iterables for zip"
                },
                "condition": {
                    "type": "string",
                    "description": "Condition for while loops"
                },
                "outer_iterable": {
                    "type": "array",
                    "description": "Outer iterable for nested loops"
                },
                "inner_iterable": {
                    "type": "array",
                    "description": "Inner iterable for nested loops"
                },
                "max_workers": {
                    "type": "integer",
                    "description": "Maximum workers for parallel processing"
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Batch size for batch processing"
                },
                "filter_func": {
                    "type": "string",
                    "description": "Filter function for filtering"
                },
                "map_func": {
                    "type": "string",
                    "description": "Map function for mapping"
                },
                "reduce_func": {
                    "type": "string",
                    "description": "Reduce function for reduction"
                },
                "initial_value": {
                    "type": "any",
                    "description": "Initial value for reduction"
                },
                "operation_code": {
                    "type": "string",
                    "description": "Custom operation code to execute"
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum number of iterations"
                }
            },
            "required": ["operation"],
            "additionalProperties": True
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute loop operation."""
        try:
            operation = LoopOperation(params["operation"])
            
            # Set max iterations if provided
            if "max_iterations" in params:
                self.processor.max_iterations = params["max_iterations"]
            
            logger.info(f"Executing loop operation: {operation}")
            
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
            
            logger.info(f"Loop operation {operation} completed successfully")
            
            return {
                "status": "success",
                "operation": operation.value,
                "result": result,
                "processing_time": round(end_time - start_time, 4),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Loop operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"Loop operation error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    # Loop operation handlers
    async def _handle_for_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle for range operation."""
        start = params["start"]
        stop = params["stop"]
        step = params.get("step", 1)
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_range(start, stop, step, operation)
    
    async def _handle_for_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle for list operation."""
        items = params["items"]
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_list(items, operation)
    
    async def _handle_for_dict(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle for dictionary operation."""
        dictionary = params["dictionary"]
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_dict(dictionary, operation)
    
    async def _handle_for_enumerate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle for enumerate operation."""
        items = params["items"]
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_enumerate(items, operation)
    
    async def _handle_for_zip(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle for zip operation."""
        iterables = params["iterables"]
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_zip(*iterables, operation=operation)
    
    async def _handle_while(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle while loop operation."""
        condition_code = params["condition"]
        condition = self._create_condition_function(condition_code)
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.while_loop(condition, operation)
    
    async def _handle_do_while(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle do-while loop operation."""
        condition_code = params["condition"]
        condition = self._create_condition_function(condition_code)
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.do_while_loop(condition, operation)
    
    async def _handle_for_nested(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle nested for loop operation."""
        outer_iterable = params["outer_iterable"]
        inner_iterable = params["inner_iterable"]
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_nested(outer_iterable, inner_iterable, operation)
    
    async def _handle_for_parallel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parallel for loop operation."""
        items = params["items"]
        max_workers = params.get("max_workers", 5)
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        if operation is None:
            operation = lambda x, i: x  # Default operation
        
        return await self.processor.for_parallel(items, operation, max_workers)
    
    async def _handle_for_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch for loop operation."""
        items = params["items"]
        batch_size = params["batch_size"]
        
        # Create operation function if code provided
        operation = None
        if "operation_code" in params:
            operation = self._create_operation_function(params["operation_code"])
        
        return self.processor.for_batch(items, batch_size, operation)
    
    async def _handle_for_custom(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle custom for loop operation."""
        # This is a placeholder for custom loop implementations
        return {
            "message": "Custom loop operation not implemented",
            "params": params
        }
    
    async def _handle_break_condition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle break condition."""
        self.processor.break_requested = True
        return {"break_requested": True}
    
    async def _handle_continue_condition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle continue condition."""
        self.processor.continue_requested = True
        return {"continue_requested": True}
    
    async def _handle_skip_condition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle skip condition."""
        # This is a placeholder for skip condition logic
        return {"skip_requested": True}
    
    async def _handle_iterate_slice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle slice iteration."""
        items = params["items"]
        start = params["start"]
        stop = params["stop"]
        step = params.get("step", 1)
        
        return self.processor.iterate_slice(items, start, stop, step)
    
    async def _handle_iterate_filter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filter iteration."""
        items = params["items"]
        filter_func_code = params["filter_func"]
        filter_func = self._create_filter_function(filter_func_code)
        
        return self.processor.iterate_filter(items, filter_func)
    
    async def _handle_iterate_map(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle map iteration."""
        items = params["items"]
        map_func_code = params["map_func"]
        map_func = self._create_map_function(map_func_code)
        
        return self.processor.iterate_map(items, map_func)
    
    async def _handle_iterate_reduce(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reduce iteration."""
        items = params["items"]
        reduce_func_code = params["reduce_func"]
        reduce_func = self._create_reduce_function(reduce_func_code)
        initial_value = params.get("initial_value")
        
        return self.processor.iterate_reduce(items, reduce_func, initial_value)
    
    async def _handle_measure_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance measurement."""
        # This would measure performance of another loop operation
        return {"message": "Performance measurement not implemented"}
    
    async def _handle_optimize_loop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle loop optimization."""
        # This would analyze and optimize loop performance
        return {"message": "Loop optimization not implemented"}
    
    async def _handle_profile_iterations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle iteration profiling."""
        results = params.get("results", {})
        return self.processor.profile_iterations(results)
    
    def _create_operation_function(self, code: str) -> Callable:
        """Create operation function from code string."""
        try:
            # Simple eval-based function creation (in production, use safer alternatives)
            namespace = {}
            exec(f"def operation(*args, **kwargs):\n    {code}", namespace)
            return namespace['operation']
        except Exception as e:
            logger.error(f"Error creating operation function: {e}")
            return lambda *args, **kwargs: None
    
    def _create_condition_function(self, code: str) -> Callable:
        """Create condition function from code string."""
        try:
            # Simple eval-based function creation (in production, use safer alternatives)
            namespace = {}
            exec(f"def condition():\n    {code}", namespace)
            return namespace['condition']
        except Exception as e:
            logger.error(f"Error creating condition function: {e}")
            return lambda: False
    
    def _create_filter_function(self, code: str) -> Callable:
        """Create filter function from code string."""
        try:
            # Simple eval-based function creation (in production, use safer alternatives)
            namespace = {}
            exec(f"def filter_func(item):\n    {code}", namespace)
            return namespace['filter_func']
        except Exception as e:
            logger.error(f"Error creating filter function: {e}")
            return lambda item: True
    
    def _create_map_function(self, code: str) -> Callable:
        """Create map function from code string."""
        try:
            # Simple eval-based function creation (in production, use safer alternatives)
            namespace = {}
            exec(f"def map_func(item):\n    {code}", namespace)
            return namespace['map_func']
        except Exception as e:
            logger.error(f"Error creating map function: {e}")
            return lambda item: item
    
    def _create_reduce_function(self, code: str) -> Callable:
        """Create reduce function from code string."""
        try:
            # Simple eval-based function creation (in production, use safer alternatives)
            namespace = {}
            exec(f"def reduce_func(acc, item):\n    {code}", namespace)
            return namespace['reduce_func']
        except Exception as e:
            logger.error(f"Error creating reduce function: {e}")
            return lambda acc, item: acc