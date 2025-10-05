#!/usr/bin/env python3

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass
import queue
import threading

try:
    from .base_node import BaseNode
except ImportError:
    try:
        from base_node import BaseNode
    except ImportError:
        from act_workflow.nodes.base_node import BaseNode

class BatchOperation(Enum):
    PROCESS_BATCH = "process_batch"
    CHUNK_PROCESS = "chunk_process"
    PARALLEL_PROCESS = "parallel_process"
    ASYNC_PROCESS = "async_process"
    QUEUE_PROCESS = "queue_process"
    STREAM_PROCESS = "stream_process"
    THREAD_POOL_PROCESS = "thread_pool_process"
    PROCESS_POOL_PROCESS = "process_pool_process"
    WORKER_POOL_PROCESS = "worker_pool_process"
    BATCH_TRANSFORM = "batch_transform"
    BATCH_FILTER = "batch_filter"
    BATCH_AGGREGATE = "batch_aggregate"
    BATCH_VALIDATE = "batch_validate"
    BATCH_MERGE = "batch_merge"
    BATCH_SPLIT = "batch_split"
    BATCH_PROFILE = "batch_profile"
    BATCH_MONITOR = "batch_monitor"
    BATCH_THROTTLE = "batch_throttle"
    BATCH_COMMIT = "batch_commit"

@dataclass
class BatchConfig:
    batch_size: int = 100
    max_workers: int = 4
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    throttle_rate: float = 0.0
    enable_monitoring: bool = True
    commit_strategy: str = "batch"
    
@dataclass
class BatchResult:
    processed_count: int
    success_count: int
    error_count: int
    total_time: float
    throughput: float
    errors: List[str]
    results: List[Any]
    metrics: Dict[str, Any]

class BatchProcessor:
    def __init__(self, config: BatchConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "total_processed": 0,
            "total_errors": 0,
            "avg_processing_time": 0.0,
            "peak_throughput": 0.0
        }
        self._lock = threading.Lock()
        
    def create_batches(self, items: List[Any], batch_size: int) -> List[List[Any]]:
        """Create batches from items."""
        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batches.append(batch)
        return batches
    
    def process_batch_sync(self, batch: List[Any], processor_func: Callable) -> List[Any]:
        """Process a batch synchronously."""
        results = []
        for item in batch:
            try:
                result = processor_func(item)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing item {item}: {str(e)}")
                results.append(None)
        return results
    
    async def process_batch_async(self, batch: List[Any], processor_func: Callable) -> List[Any]:
        """Process a batch asynchronously."""
        tasks = []
        for item in batch:
            if asyncio.iscoroutinefunction(processor_func):
                task = asyncio.create_task(processor_func(item))
            else:
                task = asyncio.create_task(asyncio.to_thread(processor_func, item))
            tasks.append(task)
        
        results = []
        for task in asyncio.as_completed(tasks, timeout=self.config.timeout):
            try:
                result = await task
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error in async processing: {str(e)}")
                results.append(None)
        
        return results
    
    def process_with_thread_pool(self, batches: List[List[Any]], processor_func: Callable) -> List[Any]:
        """Process batches using ThreadPoolExecutor."""
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_batch = {
                executor.submit(self.process_batch_sync, batch, processor_func): batch
                for batch in batches
            }
            
            for future in as_completed(future_to_batch, timeout=self.config.timeout):
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                except Exception as e:
                    self.logger.error(f"Thread pool batch error: {str(e)}")
                    
        return all_results
    
    def process_with_process_pool(self, batches: List[List[Any]], processor_func: Callable) -> List[Any]:
        """Process batches using ProcessPoolExecutor."""
        all_results = []
        
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_batch = {
                executor.submit(self.process_batch_sync, batch, processor_func): batch
                for batch in batches
            }
            
            for future in as_completed(future_to_batch, timeout=self.config.timeout):
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                except Exception as e:
                    self.logger.error(f"Process pool batch error: {str(e)}")
                    
        return all_results
    
    def process_with_worker_pool(self, items: List[Any], processor_func: Callable) -> List[Any]:
        """Process items using worker pool pattern."""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        
        # Add items to input queue
        for item in items:
            input_queue.put(item)
        
        # Add sentinel values to stop workers
        for _ in range(self.config.max_workers):
            input_queue.put(None)
        
        def worker():
            while True:
                item = input_queue.get()
                if item is None:
                    break
                try:
                    result = processor_func(item)
                    output_queue.put(result)
                except Exception as e:
                    self.logger.error(f"Worker error: {str(e)}")
                    output_queue.put(None)
                finally:
                    input_queue.task_done()
        
        # Start workers
        workers = []
        for _ in range(self.config.max_workers):
            worker_thread = threading.Thread(target=worker)
            worker_thread.start()
            workers.append(worker_thread)
        
        # Wait for all workers to complete
        for worker_thread in workers:
            worker_thread.join()
        
        # Collect results
        results = []
        while not output_queue.empty():
            results.append(output_queue.get())
        
        return results
    
    def apply_throttling(self):
        """Apply throttling if configured."""
        if self.config.throttle_rate > 0:
            time.sleep(self.config.throttle_rate)
    
    def update_metrics(self, processing_time: float, processed_count: int, error_count: int):
        """Update processing metrics."""
        with self._lock:
            self.metrics["total_processed"] += processed_count
            self.metrics["total_errors"] += error_count
            
            # Update average processing time
            if self.metrics["total_processed"] > 0:
                self.metrics["avg_processing_time"] = (
                    self.metrics["avg_processing_time"] + processing_time
                ) / 2
            
            # Update peak throughput
            if processing_time > 0:
                throughput = processed_count / processing_time
                self.metrics["peak_throughput"] = max(
                    self.metrics["peak_throughput"], throughput
                )

class BatchProcessorNode(BaseNode):
    def __init__(self, node_id: str = "batch_processor"):
        super().__init__(node_id)
        self.logger = logging.getLogger(__name__)
        self.operation_map = {
            BatchOperation.PROCESS_BATCH: self._process_batch,
            BatchOperation.CHUNK_PROCESS: self._chunk_process,
            BatchOperation.PARALLEL_PROCESS: self._parallel_process,
            BatchOperation.ASYNC_PROCESS: self._async_process,
            BatchOperation.QUEUE_PROCESS: self._queue_process,
            BatchOperation.STREAM_PROCESS: self._stream_process,
            BatchOperation.THREAD_POOL_PROCESS: self._thread_pool_process,
            BatchOperation.PROCESS_POOL_PROCESS: self._process_pool_process,
            BatchOperation.WORKER_POOL_PROCESS: self._worker_pool_process,
            BatchOperation.BATCH_TRANSFORM: self._batch_transform,
            BatchOperation.BATCH_FILTER: self._batch_filter,
            BatchOperation.BATCH_AGGREGATE: self._batch_aggregate,
            BatchOperation.BATCH_VALIDATE: self._batch_validate,
            BatchOperation.BATCH_MERGE: self._batch_merge,
            BatchOperation.BATCH_SPLIT: self._batch_split,
            BatchOperation.BATCH_PROFILE: self._batch_profile,
            BatchOperation.BATCH_MONITOR: self._batch_monitor,
            BatchOperation.BATCH_THROTTLE: self._batch_throttle,
            BatchOperation.BATCH_COMMIT: self._batch_commit,
        }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [op.value for op in BatchOperation],
                    "description": "The batch processing operation to perform"
                },
                "items": {
                    "type": "array",
                    "description": "Items to process in batches"
                },
                "batch_size": {
                    "type": "integer",
                    "default": 100,
                    "description": "Size of each batch"
                },
                "max_workers": {
                    "type": "integer",
                    "default": 4,
                    "description": "Maximum number of workers"
                },
                "timeout": {
                    "type": "number",
                    "default": 30.0,
                    "description": "Processing timeout in seconds"
                },
                "processor_func": {
                    "type": "string",
                    "description": "Function to process each item"
                },
                "processing_type": {
                    "type": "string",
                    "enum": ["sync", "async", "thread", "process"],
                    "default": "sync",
                    "description": "Type of processing to use"
                },
                "throttle_rate": {
                    "type": "number",
                    "default": 0.0,
                    "description": "Throttling rate in seconds"
                },
                "enable_monitoring": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable performance monitoring"
                },
                "commit_strategy": {
                    "type": "string",
                    "enum": ["batch", "streaming", "individual"],
                    "default": "batch",
                    "description": "Commit strategy for processed items"
                }
            },
            "required": ["operation", "items"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            operation = BatchOperation(params["operation"])
            self.logger.info(f"Executing batch operation: {operation}")
            
            handler = self.operation_map.get(operation)
            if not handler:
                raise ValueError(f"Unknown batch operation: {operation}")
            
            result = await handler(params)
            
            self.logger.info(f"Batch operation {operation} completed successfully")
            return {
                "status": "success",
                "result": result,
                "operation": operation.value
            }
            
        except Exception as e:
            self.logger.error(f"Batch operation error: {str(e)}")
            return {
                "status": "error",
                "error": f"Batch operation error: {str(e)}",
                "operation": params.get("operation", "unknown")
            }
    
    def _create_batch_config(self, params: Dict[str, Any]) -> BatchConfig:
        """Create batch configuration from parameters."""
        return BatchConfig(
            batch_size=params.get("batch_size", 100),
            max_workers=params.get("max_workers", 4),
            timeout=params.get("timeout", 30.0),
            retry_count=params.get("retry_count", 3),
            retry_delay=params.get("retry_delay", 1.0),
            throttle_rate=params.get("throttle_rate", 0.0),
            enable_monitoring=params.get("enable_monitoring", True),
            commit_strategy=params.get("commit_strategy", "batch")
        )
    
    def _create_processor_func(self, func_code: str) -> Callable:
        """Create processor function from code string."""
        if not func_code:
            return lambda x: x
        
        # Create a simple processor function
        def processor(item):
            try:
                local_vars = {"item": item}
                exec(func_code, {}, local_vars)
                return local_vars.get("result", item)
            except Exception as e:
                return f"Error: {str(e)}"
        
        return processor
    
    async def _process_batch(self, params: Dict[str, Any]) -> BatchResult:
        """Process items in batches."""
        items = params.get("items", [])
        config = self._create_batch_config(params)
        processor_func = self._create_processor_func(params.get("processor_func", ""))
        
        start_time = time.time()
        processor = BatchProcessor(config)
        
        batches = processor.create_batches(items, config.batch_size)
        all_results = []
        errors = []
        
        for batch in batches:
            try:
                batch_results = processor.process_batch_sync(batch, processor_func)
                all_results.extend(batch_results)
                processor.apply_throttling()
            except Exception as e:
                error_msg = f"Batch processing error: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Update metrics
        processor.update_metrics(processing_time, len(all_results), len(errors))
        
        return BatchResult(
            processed_count=len(all_results),
            success_count=len([r for r in all_results if r is not None]),
            error_count=len(errors),
            total_time=processing_time,
            throughput=len(all_results) / processing_time if processing_time > 0 else 0,
            errors=errors,
            results=all_results,
            metrics=processor.metrics
        )
    
    async def _chunk_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process items in chunks."""
        items = params.get("items", [])
        chunk_size = params.get("chunk_size", params.get("batch_size", 100))
        
        chunks = []
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            chunks.append({
                "chunk_id": i // chunk_size,
                "size": len(chunk),
                "data": chunk
            })
        
        return {
            "chunk_count": len(chunks),
            "total_items": len(items),
            "chunks": chunks
        }
    
    async def _parallel_process(self, params: Dict[str, Any]) -> BatchResult:
        """Process items in parallel using multiple threads."""
        items = params.get("items", [])
        config = self._create_batch_config(params)
        processor_func = self._create_processor_func(params.get("processor_func", ""))
        
        start_time = time.time()
        processor = BatchProcessor(config)
        
        batches = processor.create_batches(items, config.batch_size)
        all_results = processor.process_with_thread_pool(batches, processor_func)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return BatchResult(
            processed_count=len(all_results),
            success_count=len([r for r in all_results if r is not None]),
            error_count=len([r for r in all_results if r is None]),
            total_time=processing_time,
            throughput=len(all_results) / processing_time if processing_time > 0 else 0,
            errors=[],
            results=all_results,
            metrics=processor.metrics
        )
    
    async def _async_process(self, params: Dict[str, Any]) -> BatchResult:
        """Process items asynchronously."""
        items = params.get("items", [])
        config = self._create_batch_config(params)
        processor_func = self._create_processor_func(params.get("processor_func", ""))
        
        start_time = time.time()
        processor = BatchProcessor(config)
        
        # Process items in async batches
        batches = processor.create_batches(items, config.batch_size)
        all_results = []
        
        for batch in batches:
            batch_results = await processor.process_batch_async(batch, processor_func)
            all_results.extend(batch_results)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return BatchResult(
            processed_count=len(all_results),
            success_count=len([r for r in all_results if r is not None]),
            error_count=len([r for r in all_results if r is None]),
            total_time=processing_time,
            throughput=len(all_results) / processing_time if processing_time > 0 else 0,
            errors=[],
            results=all_results,
            metrics=processor.metrics
        )
    
    async def _queue_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process items using queue-based processing."""
        items = params.get("items", [])
        queue_size = params.get("queue_size", len(items))
        
        processing_queue = asyncio.Queue(maxsize=queue_size)
        results = []
        
        # Add items to queue
        for item in items:
            await processing_queue.put(item)
        
        # Process items from queue
        processed_count = 0
        while not processing_queue.empty():
            try:
                item = await asyncio.wait_for(processing_queue.get(), timeout=1.0)
                results.append(item)
                processed_count += 1
            except asyncio.TimeoutError:
                break
        
        return {
            "processed_count": processed_count,
            "queue_size": queue_size,
            "results": results
        }
    
    async def _stream_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process items in streaming fashion."""
        items = params.get("items", [])
        buffer_size = params.get("buffer_size", 10)
        
        buffer = []
        streamed_batches = []
        
        for item in items:
            buffer.append(item)
            
            if len(buffer) >= buffer_size:
                streamed_batches.append(buffer.copy())
                buffer.clear()
        
        # Process remaining items
        if buffer:
            streamed_batches.append(buffer)
        
        return {
            "stream_count": len(streamed_batches),
            "total_items": len(items),
            "batches": streamed_batches
        }
    
    async def _thread_pool_process(self, params: Dict[str, Any]) -> BatchResult:
        """Process items using thread pool."""
        items = params.get("items", [])
        config = self._create_batch_config(params)
        processor_func = self._create_processor_func(params.get("processor_func", ""))
        
        start_time = time.time()
        processor = BatchProcessor(config)
        
        batches = processor.create_batches(items, config.batch_size)
        all_results = processor.process_with_thread_pool(batches, processor_func)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return BatchResult(
            processed_count=len(all_results),
            success_count=len([r for r in all_results if r is not None]),
            error_count=len([r for r in all_results if r is None]),
            total_time=processing_time,
            throughput=len(all_results) / processing_time if processing_time > 0 else 0,
            errors=[],
            results=all_results,
            metrics=processor.metrics
        )
    
    async def _process_pool_process(self, params: Dict[str, Any]) -> BatchResult:
        """Process items using process pool."""
        items = params.get("items", [])
        config = self._create_batch_config(params)
        processor_func = self._create_processor_func(params.get("processor_func", ""))
        
        start_time = time.time()
        processor = BatchProcessor(config)
        
        batches = processor.create_batches(items, config.batch_size)
        all_results = processor.process_with_process_pool(batches, processor_func)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return BatchResult(
            processed_count=len(all_results),
            success_count=len([r for r in all_results if r is not None]),
            error_count=len([r for r in all_results if r is None]),
            total_time=processing_time,
            throughput=len(all_results) / processing_time if processing_time > 0 else 0,
            errors=[],
            results=all_results,
            metrics=processor.metrics
        )
    
    async def _worker_pool_process(self, params: Dict[str, Any]) -> BatchResult:
        """Process items using worker pool pattern."""
        items = params.get("items", [])
        config = self._create_batch_config(params)
        processor_func = self._create_processor_func(params.get("processor_func", ""))
        
        start_time = time.time()
        processor = BatchProcessor(config)
        
        all_results = processor.process_with_worker_pool(items, processor_func)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return BatchResult(
            processed_count=len(all_results),
            success_count=len([r for r in all_results if r is not None]),
            error_count=len([r for r in all_results if r is None]),
            total_time=processing_time,
            throughput=len(all_results) / processing_time if processing_time > 0 else 0,
            errors=[],
            results=all_results,
            metrics=processor.metrics
        )
    
    async def _batch_transform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transform items in batches."""
        items = params.get("items", [])
        transform_func = params.get("transform_func", "result = item")
        
        transformed_items = []
        for item in items:
            try:
                local_vars = {"item": item}
                exec(transform_func, {}, local_vars)
                transformed_items.append(local_vars.get("result", item))
            except Exception as e:
                transformed_items.append(f"Transform error: {str(e)}")
        
        return {
            "original_count": len(items),
            "transformed_count": len(transformed_items),
            "transformed_items": transformed_items
        }
    
    async def _batch_filter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter items in batches."""
        items = params.get("items", [])
        filter_func = params.get("filter_func", "result = True")
        
        filtered_items = []
        for item in items:
            try:
                local_vars = {"item": item}
                exec(filter_func, {}, local_vars)
                if local_vars.get("result", True):
                    filtered_items.append(item)
            except Exception as e:
                self.logger.error(f"Filter error: {str(e)}")
        
        return {
            "original_count": len(items),
            "filtered_count": len(filtered_items),
            "filtered_items": filtered_items
        }
    
    async def _batch_aggregate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate items in batches."""
        items = params.get("items", [])
        aggregate_func = params.get("aggregate_func", "sum")
        
        if aggregate_func == "sum":
            result = sum(items) if all(isinstance(x, (int, float)) for x in items) else 0
        elif aggregate_func == "count":
            result = len(items)
        elif aggregate_func == "avg":
            result = sum(items) / len(items) if items and all(isinstance(x, (int, float)) for x in items) else 0
        elif aggregate_func == "min":
            result = min(items) if items else None
        elif aggregate_func == "max":
            result = max(items) if items else None
        else:
            result = items
        
        return {
            "item_count": len(items),
            "aggregate_function": aggregate_func,
            "result": result
        }
    
    async def _batch_validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate items in batches."""
        items = params.get("items", [])
        validation_func = params.get("validation_func", "result = True")
        
        valid_items = []
        invalid_items = []
        
        for item in items:
            try:
                local_vars = {"item": item}
                exec(validation_func, {}, local_vars)
                if local_vars.get("result", True):
                    valid_items.append(item)
                else:
                    invalid_items.append(item)
            except Exception as e:
                invalid_items.append(item)
        
        return {
            "total_items": len(items),
            "valid_count": len(valid_items),
            "invalid_count": len(invalid_items),
            "valid_items": valid_items,
            "invalid_items": invalid_items
        }
    
    async def _batch_merge(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple batches."""
        batches = params.get("batches", [])
        merge_strategy = params.get("merge_strategy", "concat")
        
        if merge_strategy == "concat":
            merged = []
            for batch in batches:
                if isinstance(batch, list):
                    merged.extend(batch)
                else:
                    merged.append(batch)
        elif merge_strategy == "interleave":
            merged = []
            max_len = max(len(batch) if isinstance(batch, list) else 1 for batch in batches) if batches else 0
            for i in range(max_len):
                for batch in batches:
                    if isinstance(batch, list) and i < len(batch):
                        merged.append(batch[i])
                    elif not isinstance(batch, list) and i == 0:
                        merged.append(batch)
        else:
            merged = batches
        
        return {
            "batch_count": len(batches),
            "merged_count": len(merged),
            "merge_strategy": merge_strategy,
            "merged_items": merged
        }
    
    async def _batch_split(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Split batches based on criteria."""
        items = params.get("items", [])
        split_criteria = params.get("split_criteria", "size")
        split_value = params.get("split_value", 10)
        
        if split_criteria == "size":
            splits = []
            for i in range(0, len(items), split_value):
                splits.append(items[i:i + split_value])
        elif split_criteria == "count":
            splits = []
            split_size = len(items) // split_value
            for i in range(0, len(items), split_size):
                splits.append(items[i:i + split_size])
        else:
            splits = [items]
        
        return {
            "original_count": len(items),
            "split_count": len(splits),
            "split_criteria": split_criteria,
            "splits": splits
        }
    
    async def _batch_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Profile batch processing performance."""
        items = params.get("items", [])
        
        start_time = time.time()
        
        # Simulate processing
        processed = 0
        for item in items:
            processed += 1
            if processed % 1000 == 0:
                await asyncio.sleep(0.001)  # Yield control
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            "item_count": len(items),
            "processing_time": processing_time,
            "throughput": len(items) / processing_time if processing_time > 0 else 0,
            "items_per_second": len(items) / processing_time if processing_time > 0 else 0
        }
    
    async def _batch_monitor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor batch processing metrics."""
        return {
            "monitoring_enabled": True,
            "timestamp": time.time(),
            "system_metrics": {
                "cpu_usage": "N/A",
                "memory_usage": "N/A",
                "active_threads": threading.active_count()
            }
        }
    
    async def _batch_throttle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply throttling to batch processing."""
        throttle_rate = params.get("throttle_rate", 1.0)
        
        await asyncio.sleep(throttle_rate)
        
        return {
            "throttle_applied": True,
            "throttle_rate": throttle_rate,
            "timestamp": time.time()
        }
    
    async def _batch_commit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Commit batch processing results."""
        items = params.get("items", [])
        commit_strategy = params.get("commit_strategy", "batch")
        
        if commit_strategy == "batch":
            # Simulate batch commit
            committed = len(items)
        elif commit_strategy == "streaming":
            # Simulate streaming commit
            committed = 0
            for item in items:
                committed += 1
                if committed % 10 == 0:
                    await asyncio.sleep(0.001)
        else:
            committed = len(items)
        
        return {
            "commit_strategy": commit_strategy,
            "committed_count": committed,
            "total_items": len(items),
            "success": True
        }