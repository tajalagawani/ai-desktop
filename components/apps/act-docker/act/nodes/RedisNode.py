"""
Redis Node - Comprehensive Redis integration for caching, pub/sub, and data structures
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import redis
import redis.asyncio as aioredis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

# Configure logging with proper masking
logger = logging.getLogger(__name__)

class RedisOperation:
    """All available Redis operations."""
    
    # Connection Operations
    AUTH = "auth"
    PING = "ping"
    INFO = "info"
    CONFIG_GET = "config_get"
    CONFIG_SET = "config_set"
    TIME = "time"
    DBSIZE = "dbsize"
    FLUSHDB = "flushdb"
    FLUSHALL = "flushall"
    
    # String Operations
    SET = "set"
    GET = "get"
    MSET = "mset"
    MGET = "mget"
    INCR = "incr"
    DECR = "decr"
    INCRBY = "incrby"
    DECRBY = "decrby"
    APPEND = "append"
    STRLEN = "strlen"
    
    # Generic Key Operations
    DEL = "del"
    EXISTS = "exists"
    EXPIRE = "expire"
    TTL = "ttl"
    TYPE = "type"
    KEYS = "keys"
    SCAN = "scan"
    RENAME = "rename"
    
    # List Operations
    LPUSH = "lpush"
    RPUSH = "rpush"
    LPOP = "lpop"
    RPOP = "rpop"
    LLEN = "llen"
    LINDEX = "lindex"
    LRANGE = "lrange"
    LTRIM = "ltrim"
    LSET = "lset"
    LREM = "lrem"
    
    # Set Operations
    SADD = "sadd"
    SREM = "srem"
    SCARD = "scard"
    SISMEMBER = "sismember"
    SMEMBERS = "smembers"
    SPOP = "spop"
    SRANDMEMBER = "srandmember"
    SINTER = "sinter"
    SUNION = "sunion"
    SDIFF = "sdiff"
    
    # Sorted Set Operations
    ZADD = "zadd"
    ZREM = "zrem"
    ZCARD = "zcard"
    ZCOUNT = "zcount"
    ZRANGE = "zrange"
    ZRANGEBYSCORE = "zrangebyscore"
    ZRANK = "zrank"
    ZSCORE = "zscore"
    ZINCRBY = "zincrby"
    
    # Hash Operations
    HSET = "hset"
    HGET = "hget"
    HMSET = "hmset"
    HMGET = "hmget"
    HGETALL = "hgetall"
    HDEL = "hdel"
    HEXISTS = "hexists"
    HLEN = "hlen"
    HKEYS = "hkeys"
    HVALS = "hvals"
    HINCRBY = "hincrby"
    
    # Stream Operations
    XADD = "xadd"
    XLEN = "xlen"
    XRANGE = "xrange"
    XREAD = "xread"
    XDEL = "xdel"
    XTRIM = "xtrim"
    
    # Pub/Sub Operations
    PUBLISH = "publish"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUBSUB = "pubsub"
    
    # Transaction Operations
    PIPELINE = "pipeline"
    MULTI = "multi"
    EXEC = "exec"
    WATCH = "watch"
    UNWATCH = "unwatch"

class RedisClient:
    """Unified Redis client wrapper that handles sync/async operations."""
    
    def __init__(self, client: Union[redis.Redis, aioredis.Redis]):
        self.client = client
        self.is_async = isinstance(client, aioredis.Redis)
    
    async def maybe_await(self, result):
        """Helper to handle both sync and async results."""
        if self.is_async and asyncio.iscoroutine(result):
            return await result
        return result
    
    async def ping(self) -> bool:
        return await self.maybe_await(self.client.ping())
    
    async def auth(self, password: str) -> bool:
        return await self.maybe_await(self.client.auth(password))
    
    async def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        return await self.maybe_await(self.client.info(section))
    
    async def config_get(self, parameter: str) -> Dict[str, Any]:
        return await self.maybe_await(self.client.config_get(parameter))
    
    async def config_set(self, parameter: str, value: Any) -> bool:
        return await self.maybe_await(self.client.config_set(parameter, value))
    
    async def time(self) -> List[int]:
        return await self.maybe_await(self.client.time())
    
    async def dbsize(self) -> int:
        return await self.maybe_await(self.client.dbsize())
    
    async def flushdb(self, asynchronous: bool = False) -> bool:
        return await self.maybe_await(self.client.flushdb(asynchronous))
    
    async def flushall(self, asynchronous: bool = False) -> bool:
        return await self.maybe_await(self.client.flushall(asynchronous))
    
    # String operations
    async def set(self, key: str, value: Any, ex: Optional[int] = None, 
                  px: Optional[int] = None, nx: bool = False, xx: bool = False) -> bool:
        return await self.maybe_await(self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx))
    
    async def get(self, key: str) -> Optional[str]:
        result = await self.maybe_await(self.client.get(key))
        return result.decode('utf-8') if result else None
    
    async def mset(self, mapping: Dict[str, Any]) -> bool:
        return await self.maybe_await(self.client.mset(mapping))
    
    async def mget(self, keys: List[str]) -> List[Optional[str]]:
        results = await self.maybe_await(self.client.mget(keys))
        return [r.decode('utf-8') if r else None for r in results]
    
    async def incr(self, key: str, amount: int = 1) -> int:
        return await self.maybe_await(self.client.incr(key, amount))
    
    async def decr(self, key: str, amount: int = 1) -> int:
        return await self.maybe_await(self.client.decr(key, amount))
    
    async def append(self, key: str, value: str) -> int:
        return await self.maybe_await(self.client.append(key, value))
    
    async def strlen(self, key: str) -> int:
        return await self.maybe_await(self.client.strlen(key))
    
    # Key operations
    async def delete(self, *keys: str) -> int:
        return await self.maybe_await(self.client.delete(*keys))
    
    async def exists(self, *keys: str) -> int:
        return await self.maybe_await(self.client.exists(*keys))
    
    async def expire(self, key: str, seconds: int) -> bool:
        return await self.maybe_await(self.client.expire(key, seconds))
    
    async def ttl(self, key: str) -> int:
        return await self.maybe_await(self.client.ttl(key))
    
    async def type(self, key: str) -> str:
        result = await self.maybe_await(self.client.type(key))
        return result.decode('utf-8') if isinstance(result, bytes) else result
    
    async def keys(self, pattern: str = "*") -> List[str]:
        results = await self.maybe_await(self.client.keys(pattern))
        return [k.decode('utf-8') if isinstance(k, bytes) else k for k in results]
    
    async def scan(self, cursor: int = 0, match: Optional[str] = None, count: Optional[int] = None) -> Tuple[int, List[str]]:
        cursor, keys = await self.maybe_await(self.client.scan(cursor, match, count))
        return cursor, [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
    
    async def rename(self, src: str, dst: str) -> bool:
        return await self.maybe_await(self.client.rename(src, dst))
    
    # List operations
    async def lpush(self, key: str, *values: Any) -> int:
        return await self.maybe_await(self.client.lpush(key, *values))
    
    async def rpush(self, key: str, *values: Any) -> int:
        return await self.maybe_await(self.client.rpush(key, *values))
    
    async def lpop(self, key: str) -> Optional[str]:
        result = await self.maybe_await(self.client.lpop(key))
        return result.decode('utf-8') if result else None
    
    async def rpop(self, key: str) -> Optional[str]:
        result = await self.maybe_await(self.client.rpop(key))
        return result.decode('utf-8') if result else None
    
    async def llen(self, key: str) -> int:
        return await self.maybe_await(self.client.llen(key))
    
    async def lindex(self, key: str, index: int) -> Optional[str]:
        result = await self.maybe_await(self.client.lindex(key, index))
        return result.decode('utf-8') if result else None
    
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        results = await self.maybe_await(self.client.lrange(key, start, end))
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        return await self.maybe_await(self.client.ltrim(key, start, end))
    
    async def lset(self, key: str, index: int, value: Any) -> bool:
        return await self.maybe_await(self.client.lset(key, index, value))
    
    async def lrem(self, key: str, count: int, value: Any) -> int:
        return await self.maybe_await(self.client.lrem(key, count, value))
    
    # Set operations
    async def sadd(self, key: str, *members: Any) -> int:
        return await self.maybe_await(self.client.sadd(key, *members))
    
    async def srem(self, key: str, *members: Any) -> int:
        return await self.maybe_await(self.client.srem(key, *members))
    
    async def scard(self, key: str) -> int:
        return await self.maybe_await(self.client.scard(key))
    
    async def sismember(self, key: str, member: Any) -> bool:
        return await self.maybe_await(self.client.sismember(key, member))
    
    async def smembers(self, key: str) -> set:
        results = await self.maybe_await(self.client.smembers(key))
        return {r.decode('utf-8') if isinstance(r, bytes) else r for r in results}
    
    async def spop(self, key: str, count: Optional[int] = None) -> Union[str, List[str], None]:
        result = await self.maybe_await(self.client.spop(key, count))
        if result is None:
            return None
        if isinstance(result, list):
            return [r.decode('utf-8') if isinstance(r, bytes) else r for r in result]
        return result.decode('utf-8') if isinstance(result, bytes) else result
    
    async def srandmember(self, key: str, count: Optional[int] = None) -> Union[str, List[str], None]:
        result = await self.maybe_await(self.client.srandmember(key, count))
        if result is None:
            return None
        if isinstance(result, list):
            return [r.decode('utf-8') if isinstance(r, bytes) else r for r in result]
        return result.decode('utf-8') if isinstance(result, bytes) else result
    
    async def sinter(self, *keys: str) -> set:
        results = await self.maybe_await(self.client.sinter(*keys))
        return {r.decode('utf-8') if isinstance(r, bytes) else r for r in results}
    
    async def sunion(self, *keys: str) -> set:
        results = await self.maybe_await(self.client.sunion(*keys))
        return {r.decode('utf-8') if isinstance(r, bytes) else r for r in results}
    
    async def sdiff(self, *keys: str) -> set:
        results = await self.maybe_await(self.client.sdiff(*keys))
        return {r.decode('utf-8') if isinstance(r, bytes) else r for r in results}
    
    # Sorted set operations
    async def zadd(self, key: str, mapping: Dict[str, float], **kwargs) -> int:
        return await self.maybe_await(self.client.zadd(key, mapping, **kwargs))
    
    async def zrem(self, key: str, *members: Any) -> int:
        return await self.maybe_await(self.client.zrem(key, *members))
    
    async def zcard(self, key: str) -> int:
        return await self.maybe_await(self.client.zcard(key))
    
    async def zcount(self, key: str, min_score: float, max_score: float) -> int:
        return await self.maybe_await(self.client.zcount(key, min_score, max_score))
    
    async def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> List[Union[str, Tuple[str, float]]]:
        results = await self.maybe_await(self.client.zrange(key, start, end, withscores=withscores))
        if withscores:
            return [(r[0].decode('utf-8') if isinstance(r[0], bytes) else r[0], r[1]) for r in results]
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    async def zrangebyscore(self, key: str, min_score: float, max_score: float, 
                           start: Optional[int] = None, num: Optional[int] = None, 
                           withscores: bool = False) -> List[Union[str, Tuple[str, float]]]:
        results = await self.maybe_await(self.client.zrangebyscore(key, min_score, max_score, start, num, withscores))
        if withscores:
            return [(r[0].decode('utf-8') if isinstance(r[0], bytes) else r[0], r[1]) for r in results]
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    async def zrank(self, key: str, member: Any) -> Optional[int]:
        return await self.maybe_await(self.client.zrank(key, member))
    
    async def zscore(self, key: str, member: Any) -> Optional[float]:
        return await self.maybe_await(self.client.zscore(key, member))
    
    async def zincrby(self, key: str, amount: float, member: Any) -> float:
        return await self.maybe_await(self.client.zincrby(key, amount, member))
    
    # Hash operations
    async def hset(self, key: str, field: str, value: Any) -> int:
        return await self.maybe_await(self.client.hset(key, field, value))
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        result = await self.maybe_await(self.client.hget(key, field))
        return result.decode('utf-8') if result else None
    
    async def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        return await self.maybe_await(self.client.hmset(key, mapping))
    
    async def hmget(self, key: str, *fields: str) -> List[Optional[str]]:
        results = await self.maybe_await(self.client.hmget(key, *fields))
        return [r.decode('utf-8') if r else None for r in results]
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        results = await self.maybe_await(self.client.hgetall(key))
        return {k.decode('utf-8') if isinstance(k, bytes) else k: 
                v.decode('utf-8') if isinstance(v, bytes) else v 
                for k, v in results.items()}
    
    async def hdel(self, key: str, *fields: str) -> int:
        return await self.maybe_await(self.client.hdel(key, *fields))
    
    async def hexists(self, key: str, field: str) -> bool:
        return await self.maybe_await(self.client.hexists(key, field))
    
    async def hlen(self, key: str) -> int:
        return await self.maybe_await(self.client.hlen(key))
    
    async def hkeys(self, key: str) -> List[str]:
        results = await self.maybe_await(self.client.hkeys(key))
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    async def hvals(self, key: str) -> List[str]:
        results = await self.maybe_await(self.client.hvals(key))
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    async def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        return await self.maybe_await(self.client.hincrby(key, field, amount))
    
    # Stream operations
    async def xadd(self, key: str, fields: Dict[str, Any], id: str = "*") -> str:
        result = await self.maybe_await(self.client.xadd(key, fields, id))
        return result.decode('utf-8') if isinstance(result, bytes) else result
    
    async def xlen(self, key: str) -> int:
        return await self.maybe_await(self.client.xlen(key))
    
    async def xrange(self, key: str, start: str = "-", end: str = "+", count: Optional[int] = None) -> List[Tuple[str, Dict[str, str]]]:
        results = await self.maybe_await(self.client.xrange(key, start, end, count))
        return [(r[0].decode('utf-8') if isinstance(r[0], bytes) else r[0], 
                {k.decode('utf-8') if isinstance(k, bytes) else k: 
                 v.decode('utf-8') if isinstance(v, bytes) else v 
                 for k, v in r[1].items()}) for r in results]
    
    async def xread(self, streams: Dict[str, str], count: Optional[int] = None, block: Optional[int] = None) -> List[Tuple[str, List[Tuple[str, Dict[str, str]]]]]:
        results = await self.maybe_await(self.client.xread(streams, count, block))
        return [(r[0].decode('utf-8') if isinstance(r[0], bytes) else r[0], 
                [(entry[0].decode('utf-8') if isinstance(entry[0], bytes) else entry[0], 
                  {k.decode('utf-8') if isinstance(k, bytes) else k: 
                   v.decode('utf-8') if isinstance(v, bytes) else v 
                   for k, v in entry[1].items()}) for entry in r[1]]) for r in results]
    
    async def xdel(self, key: str, *ids: str) -> int:
        return await self.maybe_await(self.client.xdel(key, *ids))
    
    async def xtrim(self, key: str, maxlen: int, approximate: bool = True) -> int:
        return await self.maybe_await(self.client.xtrim(key, maxlen, approximate))
    
    # Pub/Sub operations
    async def publish(self, channel: str, message: Any) -> int:
        return await self.maybe_await(self.client.publish(channel, message))
    
    async def pubsub_channels(self, pattern: str = "*") -> List[str]:
        results = await self.maybe_await(self.client.pubsub_channels(pattern))
        return [r.decode('utf-8') if isinstance(r, bytes) else r for r in results]
    
    async def pubsub_numsub(self, *channels: str) -> Dict[str, int]:
        results = await self.maybe_await(self.client.pubsub_numsub(*channels))
        return {k.decode('utf-8') if isinstance(k, bytes) else k: v for k, v in results.items()}
    
    async def close(self):
        """Close the connection."""
        if self.is_async:
            await self.client.close()
        else:
            self.client.close()


class OperationMetadata:
    """Metadata for Redis operations including parameter requirements."""
    
    def __init__(self, required_params: List[str], optional_params: List[str] = None, 
                 handler: Optional[Callable] = None):
        self.required_params = required_params
        self.optional_params = optional_params or []
        self.handler = handler


class RedisNode(BaseNode):
    """
    Comprehensive Redis integration node supporting all major API operations.
    Handles caching, pub/sub, data structures, and advanced Redis features.
    """
    
    # Operation metadata table - programmatic validation generation
    OPERATION_METADATA = {
        # Connection operations
        RedisOperation.PING: OperationMetadata([]),
        RedisOperation.AUTH: OperationMetadata(["password"]),
        RedisOperation.INFO: OperationMetadata([], ["section"]),
        RedisOperation.CONFIG_GET: OperationMetadata(["parameter"]),
        RedisOperation.CONFIG_SET: OperationMetadata(["parameter", "value"]),
        RedisOperation.TIME: OperationMetadata([]),
        RedisOperation.DBSIZE: OperationMetadata([]),
        RedisOperation.FLUSHDB: OperationMetadata([], ["asynchronous"]),
        RedisOperation.FLUSHALL: OperationMetadata([], ["asynchronous"]),
        
        # String operations
        RedisOperation.SET: OperationMetadata(["key", "value"], ["expiration_seconds", "expiration_ms", "nx", "xx"]),
        RedisOperation.GET: OperationMetadata(["key"]),
        RedisOperation.MSET: OperationMetadata(["mapping"]),
        RedisOperation.MGET: OperationMetadata(["keys"]),
        RedisOperation.INCR: OperationMetadata(["key"], ["amount"]),
        RedisOperation.DECR: OperationMetadata(["key"], ["amount"]),
        RedisOperation.APPEND: OperationMetadata(["key", "value"]),
        RedisOperation.STRLEN: OperationMetadata(["key"]),
        
        # Key operations
        RedisOperation.DEL: OperationMetadata(["key"]),
        RedisOperation.EXISTS: OperationMetadata(["key"]),
        RedisOperation.EXPIRE: OperationMetadata(["key", "seconds"]),
        RedisOperation.TTL: OperationMetadata(["key"]),
        RedisOperation.TYPE: OperationMetadata(["key"]),
        RedisOperation.KEYS: OperationMetadata([], ["pattern"]),
        RedisOperation.SCAN: OperationMetadata([], ["cursor", "match", "count"]),
        RedisOperation.RENAME: OperationMetadata(["src", "dst"]),
        
        # List operations
        RedisOperation.LPUSH: OperationMetadata(["key", "value"]),
        RedisOperation.RPUSH: OperationMetadata(["key", "value"]),
        RedisOperation.LPOP: OperationMetadata(["key"]),
        RedisOperation.RPOP: OperationMetadata(["key"]),
        RedisOperation.LLEN: OperationMetadata(["key"]),
        RedisOperation.LINDEX: OperationMetadata(["key", "index"]),
        RedisOperation.LRANGE: OperationMetadata(["key", "start", "end"]),
        RedisOperation.LTRIM: OperationMetadata(["key", "start", "end"]),
        RedisOperation.LSET: OperationMetadata(["key", "index", "value"]),
        RedisOperation.LREM: OperationMetadata(["key", "count", "value"]),
        
        # Set operations
        RedisOperation.SADD: OperationMetadata(["key", "member"]),
        RedisOperation.SREM: OperationMetadata(["key", "member"]),
        RedisOperation.SCARD: OperationMetadata(["key"]),
        RedisOperation.SISMEMBER: OperationMetadata(["key", "member"]),
        RedisOperation.SMEMBERS: OperationMetadata(["key"]),
        RedisOperation.SPOP: OperationMetadata(["key"], ["count"]),
        RedisOperation.SRANDMEMBER: OperationMetadata(["key"], ["count"]),
        RedisOperation.SINTER: OperationMetadata(["keys"]),
        RedisOperation.SUNION: OperationMetadata(["keys"]),
        RedisOperation.SDIFF: OperationMetadata(["keys"]),
        
        # Sorted set operations
        RedisOperation.ZADD: OperationMetadata(["key", "score", "member"]),
        RedisOperation.ZREM: OperationMetadata(["key", "member"]),
        RedisOperation.ZCARD: OperationMetadata(["key"]),
        RedisOperation.ZCOUNT: OperationMetadata(["key", "min_score", "max_score"]),
        RedisOperation.ZRANGE: OperationMetadata(["key", "start", "end"], ["withscores"]),
        RedisOperation.ZRANGEBYSCORE: OperationMetadata(["key", "min_score", "max_score"], ["start", "num", "withscores"]),
        RedisOperation.ZRANK: OperationMetadata(["key", "member"]),
        RedisOperation.ZSCORE: OperationMetadata(["key", "member"]),
        RedisOperation.ZINCRBY: OperationMetadata(["key", "amount", "member"]),
        
        # Hash operations
        RedisOperation.HSET: OperationMetadata(["key", "field", "value"]),
        RedisOperation.HGET: OperationMetadata(["key", "field"]),
        RedisOperation.HMSET: OperationMetadata(["key", "mapping"]),
        RedisOperation.HMGET: OperationMetadata(["key", "fields"]),
        RedisOperation.HGETALL: OperationMetadata(["key"]),
        RedisOperation.HDEL: OperationMetadata(["key", "field"]),
        RedisOperation.HEXISTS: OperationMetadata(["key", "field"]),
        RedisOperation.HLEN: OperationMetadata(["key"]),
        RedisOperation.HKEYS: OperationMetadata(["key"]),
        RedisOperation.HVALS: OperationMetadata(["key"]),
        RedisOperation.HINCRBY: OperationMetadata(["key", "field"], ["amount"]),
        
        # Stream operations
        RedisOperation.XADD: OperationMetadata(["key", "fields"], ["id"]),
        RedisOperation.XLEN: OperationMetadata(["key"]),
        RedisOperation.XRANGE: OperationMetadata(["key"], ["start", "end", "count"]),
        RedisOperation.XREAD: OperationMetadata(["streams"], ["count", "block"]),
        RedisOperation.XDEL: OperationMetadata(["key", "ids"]),
        RedisOperation.XTRIM: OperationMetadata(["key", "maxlen"], ["approximate"]),
        
        # Pub/Sub operations
        RedisOperation.PUBLISH: OperationMetadata(["channel", "message"]),
        RedisOperation.PUBSUB: OperationMetadata([], ["pattern"]),
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create dispatch map for operations
        self.operation_dispatch = {
            RedisOperation.PING: self._handle_ping,
            RedisOperation.AUTH: self._handle_auth,
            RedisOperation.INFO: self._handle_info,
            RedisOperation.CONFIG_GET: self._handle_config_get,
            RedisOperation.CONFIG_SET: self._handle_config_set,
            RedisOperation.TIME: self._handle_time,
            RedisOperation.DBSIZE: self._handle_dbsize,
            RedisOperation.FLUSHDB: self._handle_flushdb,
            RedisOperation.FLUSHALL: self._handle_flushall,
            
            # String operations
            RedisOperation.SET: self._handle_set,
            RedisOperation.GET: self._handle_get,
            RedisOperation.MSET: self._handle_mset,
            RedisOperation.MGET: self._handle_mget,
            RedisOperation.INCR: self._handle_incr,
            RedisOperation.DECR: self._handle_decr,
            RedisOperation.APPEND: self._handle_append,
            RedisOperation.STRLEN: self._handle_strlen,
            
            # Key operations
            RedisOperation.DEL: self._handle_del,
            RedisOperation.EXISTS: self._handle_exists,
            RedisOperation.EXPIRE: self._handle_expire,
            RedisOperation.TTL: self._handle_ttl,
            RedisOperation.TYPE: self._handle_type,
            RedisOperation.KEYS: self._handle_keys,
            RedisOperation.SCAN: self._handle_scan,
            RedisOperation.RENAME: self._handle_rename,
            
            # List operations
            RedisOperation.LPUSH: self._handle_lpush,
            RedisOperation.RPUSH: self._handle_rpush,
            RedisOperation.LPOP: self._handle_lpop,
            RedisOperation.RPOP: self._handle_rpop,
            RedisOperation.LLEN: self._handle_llen,
            RedisOperation.LINDEX: self._handle_lindex,
            RedisOperation.LRANGE: self._handle_lrange,
            RedisOperation.LTRIM: self._handle_ltrim,
            RedisOperation.LSET: self._handle_lset,
            RedisOperation.LREM: self._handle_lrem,
            
            # Set operations
            RedisOperation.SADD: self._handle_sadd,
            RedisOperation.SREM: self._handle_srem,
            RedisOperation.SCARD: self._handle_scard,
            RedisOperation.SISMEMBER: self._handle_sismember,
            RedisOperation.SMEMBERS: self._handle_smembers,
            RedisOperation.SPOP: self._handle_spop,
            RedisOperation.SRANDMEMBER: self._handle_srandmember,
            RedisOperation.SINTER: self._handle_sinter,
            RedisOperation.SUNION: self._handle_sunion,
            RedisOperation.SDIFF: self._handle_sdiff,
            
            # Sorted set operations
            RedisOperation.ZADD: self._handle_zadd,
            RedisOperation.ZREM: self._handle_zrem,
            RedisOperation.ZCARD: self._handle_zcard,
            RedisOperation.ZCOUNT: self._handle_zcount,
            RedisOperation.ZRANGE: self._handle_zrange,
            RedisOperation.ZRANGEBYSCORE: self._handle_zrangebyscore,
            RedisOperation.ZRANK: self._handle_zrank,
            RedisOperation.ZSCORE: self._handle_zscore,
            RedisOperation.ZINCRBY: self._handle_zincrby,
            
            # Hash operations
            RedisOperation.HSET: self._handle_hset,
            RedisOperation.HGET: self._handle_hget,
            RedisOperation.HMSET: self._handle_hmset,
            RedisOperation.HMGET: self._handle_hmget,
            RedisOperation.HGETALL: self._handle_hgetall,
            RedisOperation.HDEL: self._handle_hdel,
            RedisOperation.HEXISTS: self._handle_hexists,
            RedisOperation.HLEN: self._handle_hlen,
            RedisOperation.HKEYS: self._handle_hkeys,
            RedisOperation.HVALS: self._handle_hvals,
            RedisOperation.HINCRBY: self._handle_hincrby,
            
            # Stream operations
            RedisOperation.XADD: self._handle_xadd,
            RedisOperation.XLEN: self._handle_xlen,
            RedisOperation.XRANGE: self._handle_xrange,
            RedisOperation.XREAD: self._handle_xread,
            RedisOperation.XDEL: self._handle_xdel,
            RedisOperation.XTRIM: self._handle_xtrim,
            
            # Pub/Sub operations
            RedisOperation.PUBLISH: self._handle_publish,
            RedisOperation.PUBSUB: self._handle_pubsub,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Redis node."""
        # Create a simple schema with common parameters
        parameters = {}
        
        # Add basic parameters
        param_definitions = [
            ("operation", NodeParameterType.STRING, "The Redis operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("host", NodeParameterType.STRING, "Redis host address", True, None, "localhost"),
            ("port", NodeParameterType.NUMBER, "Redis port number", True, None, 6379),
            ("db", NodeParameterType.NUMBER, "Redis database number", True, None, 0),
            ("password", NodeParameterType.SECRET, "Redis password (if authentication required)", False),
            ("username", NodeParameterType.STRING, "Redis username (Redis 6.0+)", False),
            ("async_mode", NodeParameterType.BOOLEAN, "Use async Redis client", False, None, False),
            ("timeout", NodeParameterType.NUMBER, "Connection timeout in seconds", False, None, 10),
            ("ssl", NodeParameterType.BOOLEAN, "Use SSL connection", False, None, False),
            
            # Generic parameters
            ("key", NodeParameterType.STRING, "Redis key", False),
            ("value", NodeParameterType.ANY, "Value to store", False),
            ("keys", NodeParameterType.ARRAY, "Array of keys", False),
            ("mapping", NodeParameterType.OBJECT, "Key-value mapping", False),
            ("expiration_seconds", NodeParameterType.NUMBER, "Expiration time in seconds", False),
            ("expiration_ms", NodeParameterType.NUMBER, "Expiration time in milliseconds", False),
            ("nx", NodeParameterType.BOOLEAN, "Only set if key doesn't exist", False, None, False),
            ("xx", NodeParameterType.BOOLEAN, "Only set if key exists", False, None, False),
            
            # List parameters
            ("index", NodeParameterType.NUMBER, "List index", False),
            ("start", NodeParameterType.NUMBER, "Start index", False),
            ("end", NodeParameterType.NUMBER, "End index", False),
            ("count", NodeParameterType.NUMBER, "Count or limit", False),
            
            # Set parameters
            ("member", NodeParameterType.ANY, "Set member", False),
            ("members", NodeParameterType.ARRAY, "Array of set members", False),
            
            # Sorted set parameters
            ("score", NodeParameterType.NUMBER, "Score for sorted set", False),
            ("min_score", NodeParameterType.NUMBER, "Minimum score", False),
            ("max_score", NodeParameterType.NUMBER, "Maximum score", False),
            ("withscores", NodeParameterType.BOOLEAN, "Include scores in result", False, None, False),
            ("amount", NodeParameterType.NUMBER, "Amount to increment/decrement", False, None, 1),
            
            # Hash parameters
            ("field", NodeParameterType.STRING, "Hash field", False),
            ("fields", NodeParameterType.ARRAY, "Array of hash fields", False),
            
            # Stream parameters
            ("id", NodeParameterType.STRING, "Stream entry ID", False, None, "*"),
            ("ids", NodeParameterType.ARRAY, "Array of stream entry IDs", False),
            ("streams", NodeParameterType.OBJECT, "Stream configuration", False),
            ("maxlen", NodeParameterType.NUMBER, "Maximum stream length", False),
            ("approximate", NodeParameterType.BOOLEAN, "Use approximate trimming", False, None, True),
            ("block", NodeParameterType.NUMBER, "Block timeout in milliseconds", False),
            
            # Pub/Sub parameters
            ("channel", NodeParameterType.STRING, "Pub/Sub channel", False),
            ("message", NodeParameterType.ANY, "Message to publish", False),
            ("pattern", NodeParameterType.STRING, "Pattern for keys or channels", False, None, "*"),
            
            # Scan parameters
            ("cursor", NodeParameterType.NUMBER, "Scan cursor", False, None, 0),
            ("match", NodeParameterType.STRING, "Match pattern", False),
            
            # Misc parameters
            ("parameter", NodeParameterType.STRING, "Configuration parameter", False),
            ("section", NodeParameterType.STRING, "Info section", False),
            ("asynchronous", NodeParameterType.BOOLEAN, "Perform operation asynchronously", False, None, False),
            ("seconds", NodeParameterType.NUMBER, "Time in seconds", False),
            ("src", NodeParameterType.STRING, "Source key", False),
            ("dst", NodeParameterType.STRING, "Destination key", False),
            ("num", NodeParameterType.NUMBER, "Number of results", False),
        ]
        
        # Build parameters dict
        for param_def in param_definitions:
            name = param_def[0]
            param_type = param_def[1]
            description = param_def[2]
            required = param_def[3]
            enum = param_def[4] if len(param_def) > 4 else None
            default = param_def[5] if len(param_def) > 5 else None
            
            param_kwargs = {
                "name": name,
                "type": param_type,
                "description": description,
                "required": required
            }
            
            if enum:
                param_kwargs["enum"] = enum
            if default is not None:
                param_kwargs["default"] = default
            
            parameters[name] = NodeParameter(**param_kwargs)
        
        return NodeSchema(
            node_type="redis",
            version="1.0.0",
            description="Comprehensive Redis integration supporting all major operations including caching, pub/sub, data structures, and advanced features",
            parameters=list(parameters.values()),
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "start_time": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER,
                "inputs": NodeParameterType.OBJECT,
                "raw_result": NodeParameterType.ANY,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "redis_error": NodeParameterType.STRING,
                "connection_info": NodeParameterType.OBJECT,
                "type": NodeParameterType.STRING,
                "key": NodeParameterType.STRING,
                "count": NodeParameterType.NUMBER,
                "has_more": NodeParameterType.BOOLEAN,
                "cursor": NodeParameterType.NUMBER,
                "entry_id": NodeParameterType.STRING,
                "subscribers": NodeParameterType.NUMBER,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Redis-specific parameters using operation metadata."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Basic validation
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Connection validation
        if not params.get("host"):
            raise NodeValidationError("Host is required")
        
        port = params.get("port")
        if port is not None and not isinstance(port, int):
            raise NodeValidationError("Port must be a number")
        
        db = params.get("db")
        if db is not None and not isinstance(db, int):
            raise NodeValidationError("Database must be a number")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata.required_params:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Additional validation for specific operations
        if operation == RedisOperation.ZADD:
            if "score" in params and not isinstance(params["score"], (int, float)):
                raise NodeValidationError("Score must be a number")
        
        if operation in [RedisOperation.LINDEX, RedisOperation.LSET]:
            if "index" in params and not isinstance(params["index"], int):
                raise NodeValidationError("Index must be an integer")
        
        if operation in [RedisOperation.LRANGE, RedisOperation.LTRIM]:
            if "start" in params and not isinstance(params["start"], int):
                raise NodeValidationError("Start must be an integer")
            if "end" in params and not isinstance(params["end"], int):
                raise NodeValidationError("End must be an integer")
        
        return node_data
    
    @asynccontextmanager
    async def _get_redis_client(self, params: Dict[str, Any]):
        """Context manager for Redis client with proper connection lifecycle."""
        host = params.get("host", "localhost")
        port = params.get("port", 6379)
        db = params.get("db", 0)
        password = params.get("password")
        username = params.get("username")
        timeout = params.get("timeout", 10)
        ssl = params.get("ssl", False)
        async_mode = params.get("async_mode", False)
        
        connection_kwargs = {
            "host": host,
            "port": port,
            "db": db,
            "socket_timeout": timeout,
            "ssl": ssl,
            "decode_responses": False,  # We handle decoding in RedisClient
        }
        
        if password:
            connection_kwargs["password"] = password
        if username:
            connection_kwargs["username"] = username
        
        client = None
        try:
            if async_mode:
                client = aioredis.Redis(**connection_kwargs)
            else:
                client = redis.Redis(**connection_kwargs)
            
            redis_client = RedisClient(client)
            yield redis_client
        finally:
            if client:
                await redis_client.close()
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked_data = data.copy()
        
        # Mask password
        if "password" in masked_data:
            masked_data["password"] = "***MASKED***"
        
        return masked_data
    
    def _create_standard_response(self, operation: str, start_time: datetime, 
                                 params: Dict[str, Any], result: Any, 
                                 error: Optional[str] = None, 
                                 redis_error: Optional[str] = None) -> Dict[str, Any]:
        """Create standardized response shape."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "status": "success" if error is None else "error",
            "operation": operation,
            "start_time": start_time.isoformat(),
            "execution_time": execution_time,
            "inputs": self._mask_sensitive_data(params),
            "raw_result": result,
            "result": result,
        }
        
        if error:
            response["error"] = error
        
        if redis_error:
            response["redis_error"] = redis_error
        
        # Add connection info (without sensitive data)
        response["connection_info"] = {
            "host": params.get("host", "localhost"),
            "port": params.get("port", 6379),
            "db": params.get("db", 0),
        }
        
        return response
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Redis operation using dispatch map."""
        start_time = datetime.now()
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Get handler from dispatch map
        handler = self.operation_dispatch.get(operation)
        if not handler:
            return self._create_standard_response(
                operation, start_time, params, None,
                error=f"Unknown operation: {operation}"
            )
        
        try:
            # Create Redis client with proper connection lifecycle
            async with self._get_redis_client(params) as redis_client:
                # Call the handler
                result = await handler(redis_client, params)
                
                return self._create_standard_response(
                    operation, start_time, params, result
                )
        
        except RedisError as e:
            error_type = type(e).__name__
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), redis_error=error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in operation {operation}: {e}")
            return self._create_standard_response(
                operation, start_time, params, None,
                error=str(e), redis_error=type(e).__name__
            )
    
    # Connection operation handlers
    async def _handle_ping(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle PING operation."""
        return await redis_client.ping()
    
    async def _handle_auth(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle AUTH operation."""
        password = params.get("password")
        return await redis_client.auth(password)
    
    async def _handle_info(self, redis_client: RedisClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle INFO operation."""
        section = params.get("section")
        return await redis_client.info(section)
    
    async def _handle_config_get(self, redis_client: RedisClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CONFIG GET operation."""
        parameter = params.get("parameter")
        return await redis_client.config_get(parameter)
    
    async def _handle_config_set(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle CONFIG SET operation."""
        parameter = params.get("parameter")
        value = params.get("value")
        return await redis_client.config_set(parameter, value)
    
    async def _handle_time(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[int]:
        """Handle TIME operation."""
        return await redis_client.time()
    
    async def _handle_dbsize(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle DBSIZE operation."""
        return await redis_client.dbsize()
    
    async def _handle_flushdb(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle FLUSHDB operation."""
        asynchronous = params.get("asynchronous", False)
        return await redis_client.flushdb(asynchronous)
    
    async def _handle_flushall(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle FLUSHALL operation."""
        asynchronous = params.get("asynchronous", False)
        return await redis_client.flushall(asynchronous)
    
    # String operation handlers
    async def _handle_set(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle SET operation."""
        key = params.get("key")
        value = params.get("value")
        
        # Map friendly expiration params to Redis params
        ex = params.get("expiration_seconds")
        px = params.get("expiration_ms")
        nx = params.get("nx", False)
        xx = params.get("xx", False)
        
        return await redis_client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
    
    async def _handle_get(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[str]:
        """Handle GET operation."""
        key = params.get("key")
        return await redis_client.get(key)
    
    async def _handle_mset(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle MSET operation."""
        mapping = params.get("mapping")
        return await redis_client.mset(mapping)
    
    async def _handle_mget(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[Optional[str]]:
        """Handle MGET operation."""
        keys = params.get("keys")
        return await redis_client.mget(keys)
    
    async def _handle_incr(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle INCR operation."""
        key = params.get("key")
        amount = params.get("amount", 1)
        return await redis_client.incr(key, amount)
    
    async def _handle_decr(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle DECR operation."""
        key = params.get("key")
        amount = params.get("amount", 1)
        return await redis_client.decr(key, amount)
    
    async def _handle_append(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle APPEND operation."""
        key = params.get("key")
        value = params.get("value")
        return await redis_client.append(key, value)
    
    async def _handle_strlen(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle STRLEN operation."""
        key = params.get("key")
        return await redis_client.strlen(key)
    
    # Key operation handlers
    async def _handle_del(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle DEL operation."""
        key = params.get("key")
        keys = params.get("keys", [])
        
        if key:
            return await redis_client.delete(key)
        elif keys:
            return await redis_client.delete(*keys)
        else:
            return 0
    
    async def _handle_exists(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle EXISTS operation."""
        key = params.get("key")
        keys = params.get("keys", [])
        
        if key:
            return await redis_client.exists(key)
        elif keys:
            return await redis_client.exists(*keys)
        else:
            return 0
    
    async def _handle_expire(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle EXPIRE operation."""
        key = params.get("key")
        seconds = params.get("seconds")
        return await redis_client.expire(key, seconds)
    
    async def _handle_ttl(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle TTL operation."""
        key = params.get("key")
        return await redis_client.ttl(key)
    
    async def _handle_type(self, redis_client: RedisClient, params: Dict[str, Any]) -> str:
        """Handle TYPE operation."""
        key = params.get("key")
        return await redis_client.type(key)
    
    async def _handle_keys(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[str]:
        """Handle KEYS operation."""
        pattern = params.get("pattern", "*")
        return await redis_client.keys(pattern)
    
    async def _handle_scan(self, redis_client: RedisClient, params: Dict[str, Any]) -> Tuple[int, List[str]]:
        """Handle SCAN operation."""
        cursor = params.get("cursor", 0)
        match = params.get("match")
        count = params.get("count")
        return await redis_client.scan(cursor, match, count)
    
    async def _handle_rename(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle RENAME operation."""
        src = params.get("src")
        dst = params.get("dst")
        return await redis_client.rename(src, dst)
    
    # List operation handlers
    async def _handle_lpush(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle LPUSH operation."""
        key = params.get("key")
        value = params.get("value")
        return await redis_client.lpush(key, value)
    
    async def _handle_rpush(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle RPUSH operation."""
        key = params.get("key")
        value = params.get("value")
        return await redis_client.rpush(key, value)
    
    async def _handle_lpop(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[str]:
        """Handle LPOP operation."""
        key = params.get("key")
        return await redis_client.lpop(key)
    
    async def _handle_rpop(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[str]:
        """Handle RPOP operation."""
        key = params.get("key")
        return await redis_client.rpop(key)
    
    async def _handle_llen(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle LLEN operation."""
        key = params.get("key")
        return await redis_client.llen(key)
    
    async def _handle_lindex(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[str]:
        """Handle LINDEX operation."""
        key = params.get("key")
        index = params.get("index")
        return await redis_client.lindex(key, index)
    
    async def _handle_lrange(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[str]:
        """Handle LRANGE operation."""
        key = params.get("key")
        start = params.get("start")
        end = params.get("end")
        return await redis_client.lrange(key, start, end)
    
    async def _handle_ltrim(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle LTRIM operation."""
        key = params.get("key")
        start = params.get("start")
        end = params.get("end")
        return await redis_client.ltrim(key, start, end)
    
    async def _handle_lset(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle LSET operation."""
        key = params.get("key")
        index = params.get("index")
        value = params.get("value")
        return await redis_client.lset(key, index, value)
    
    async def _handle_lrem(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle LREM operation."""
        key = params.get("key")
        count = params.get("count")
        value = params.get("value")
        return await redis_client.lrem(key, count, value)
    
    # Set operation handlers
    async def _handle_sadd(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle SADD operation."""
        key = params.get("key")
        member = params.get("member")
        members = params.get("members", [])
        
        if member:
            return await redis_client.sadd(key, member)
        elif members:
            return await redis_client.sadd(key, *members)
        else:
            return 0
    
    async def _handle_srem(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle SREM operation."""
        key = params.get("key")
        member = params.get("member")
        members = params.get("members", [])
        
        if member:
            return await redis_client.srem(key, member)
        elif members:
            return await redis_client.srem(key, *members)
        else:
            return 0
    
    async def _handle_scard(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle SCARD operation."""
        key = params.get("key")
        return await redis_client.scard(key)
    
    async def _handle_sismember(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle SISMEMBER operation."""
        key = params.get("key")
        member = params.get("member")
        return await redis_client.sismember(key, member)
    
    async def _handle_smembers(self, redis_client: RedisClient, params: Dict[str, Any]) -> set:
        """Handle SMEMBERS operation."""
        key = params.get("key")
        return await redis_client.smembers(key)
    
    async def _handle_spop(self, redis_client: RedisClient, params: Dict[str, Any]) -> Union[str, List[str], None]:
        """Handle SPOP operation."""
        key = params.get("key")
        count = params.get("count")
        return await redis_client.spop(key, count)
    
    async def _handle_srandmember(self, redis_client: RedisClient, params: Dict[str, Any]) -> Union[str, List[str], None]:
        """Handle SRANDMEMBER operation."""
        key = params.get("key")
        count = params.get("count")
        return await redis_client.srandmember(key, count)
    
    async def _handle_sinter(self, redis_client: RedisClient, params: Dict[str, Any]) -> set:
        """Handle SINTER operation."""
        keys = params.get("keys")
        return await redis_client.sinter(*keys)
    
    async def _handle_sunion(self, redis_client: RedisClient, params: Dict[str, Any]) -> set:
        """Handle SUNION operation."""
        keys = params.get("keys")
        return await redis_client.sunion(*keys)
    
    async def _handle_sdiff(self, redis_client: RedisClient, params: Dict[str, Any]) -> set:
        """Handle SDIFF operation."""
        keys = params.get("keys")
        return await redis_client.sdiff(*keys)
    
    # Sorted set operation handlers
    async def _handle_zadd(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle ZADD operation."""
        key = params.get("key")
        score = params.get("score")
        member = params.get("member")
        mapping = params.get("mapping")
        
        if mapping:
            return await redis_client.zadd(key, mapping)
        elif score is not None and member:
            return await redis_client.zadd(key, {member: score})
        else:
            return 0
    
    async def _handle_zrem(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle ZREM operation."""
        key = params.get("key")
        member = params.get("member")
        members = params.get("members", [])
        
        if member:
            return await redis_client.zrem(key, member)
        elif members:
            return await redis_client.zrem(key, *members)
        else:
            return 0
    
    async def _handle_zcard(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle ZCARD operation."""
        key = params.get("key")
        return await redis_client.zcard(key)
    
    async def _handle_zcount(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle ZCOUNT operation."""
        key = params.get("key")
        min_score = params.get("min_score")
        max_score = params.get("max_score")
        return await redis_client.zcount(key, min_score, max_score)
    
    async def _handle_zrange(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[Union[str, Tuple[str, float]]]:
        """Handle ZRANGE operation."""
        key = params.get("key")
        start = params.get("start")
        end = params.get("end")
        withscores = params.get("withscores", False)
        return await redis_client.zrange(key, start, end, withscores)
    
    async def _handle_zrangebyscore(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[Union[str, Tuple[str, float]]]:
        """Handle ZRANGEBYSCORE operation."""
        key = params.get("key")
        min_score = params.get("min_score")
        max_score = params.get("max_score")
        start = params.get("start")
        num = params.get("num")
        withscores = params.get("withscores", False)
        return await redis_client.zrangebyscore(key, min_score, max_score, start, num, withscores)
    
    async def _handle_zrank(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[int]:
        """Handle ZRANK operation."""
        key = params.get("key")
        member = params.get("member")
        return await redis_client.zrank(key, member)
    
    async def _handle_zscore(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[float]:
        """Handle ZSCORE operation."""
        key = params.get("key")
        member = params.get("member")
        return await redis_client.zscore(key, member)
    
    async def _handle_zincrby(self, redis_client: RedisClient, params: Dict[str, Any]) -> float:
        """Handle ZINCRBY operation."""
        key = params.get("key")
        amount = params.get("amount")
        member = params.get("member")
        return await redis_client.zincrby(key, amount, member)
    
    # Hash operation handlers
    async def _handle_hset(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle HSET operation."""
        key = params.get("key")
        field = params.get("field")
        value = params.get("value")
        return await redis_client.hset(key, field, value)
    
    async def _handle_hget(self, redis_client: RedisClient, params: Dict[str, Any]) -> Optional[str]:
        """Handle HGET operation."""
        key = params.get("key")
        field = params.get("field")
        return await redis_client.hget(key, field)
    
    async def _handle_hmset(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle HMSET operation."""
        key = params.get("key")
        mapping = params.get("mapping")
        return await redis_client.hmset(key, mapping)
    
    async def _handle_hmget(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[Optional[str]]:
        """Handle HMGET operation."""
        key = params.get("key")
        fields = params.get("fields")
        return await redis_client.hmget(key, *fields)
    
    async def _handle_hgetall(self, redis_client: RedisClient, params: Dict[str, Any]) -> Dict[str, str]:
        """Handle HGETALL operation."""
        key = params.get("key")
        return await redis_client.hgetall(key)
    
    async def _handle_hdel(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle HDEL operation."""
        key = params.get("key")
        field = params.get("field")
        fields = params.get("fields", [])
        
        if field:
            return await redis_client.hdel(key, field)
        elif fields:
            return await redis_client.hdel(key, *fields)
        else:
            return 0
    
    async def _handle_hexists(self, redis_client: RedisClient, params: Dict[str, Any]) -> bool:
        """Handle HEXISTS operation."""
        key = params.get("key")
        field = params.get("field")
        return await redis_client.hexists(key, field)
    
    async def _handle_hlen(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle HLEN operation."""
        key = params.get("key")
        return await redis_client.hlen(key)
    
    async def _handle_hkeys(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[str]:
        """Handle HKEYS operation."""
        key = params.get("key")
        return await redis_client.hkeys(key)
    
    async def _handle_hvals(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[str]:
        """Handle HVALS operation."""
        key = params.get("key")
        return await redis_client.hvals(key)
    
    async def _handle_hincrby(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle HINCRBY operation."""
        key = params.get("key")
        field = params.get("field")
        amount = params.get("amount", 1)
        return await redis_client.hincrby(key, field, amount)
    
    # Stream operation handlers
    async def _handle_xadd(self, redis_client: RedisClient, params: Dict[str, Any]) -> str:
        """Handle XADD operation."""
        key = params.get("key")
        fields = params.get("fields")
        entry_id = params.get("id", "*")
        return await redis_client.xadd(key, fields, entry_id)
    
    async def _handle_xlen(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle XLEN operation."""
        key = params.get("key")
        return await redis_client.xlen(key)
    
    async def _handle_xrange(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[Tuple[str, Dict[str, str]]]:
        """Handle XRANGE operation."""
        key = params.get("key")
        start = params.get("start", "-")
        end = params.get("end", "+")
        count = params.get("count")
        return await redis_client.xrange(key, start, end, count)
    
    async def _handle_xread(self, redis_client: RedisClient, params: Dict[str, Any]) -> List[Tuple[str, List[Tuple[str, Dict[str, str]]]]]:
        """Handle XREAD operation."""
        streams = params.get("streams")
        count = params.get("count")
        block = params.get("block")
        return await redis_client.xread(streams, count, block)
    
    async def _handle_xdel(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle XDEL operation."""
        key = params.get("key")
        ids = params.get("ids")
        return await redis_client.xdel(key, *ids)
    
    async def _handle_xtrim(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle XTRIM operation."""
        key = params.get("key")
        maxlen = params.get("maxlen")
        approximate = params.get("approximate", True)
        return await redis_client.xtrim(key, maxlen, approximate)
    
    # Pub/Sub operation handlers
    async def _handle_publish(self, redis_client: RedisClient, params: Dict[str, Any]) -> int:
        """Handle PUBLISH operation."""
        channel = params.get("channel")
        message = params.get("message")
        return await redis_client.publish(channel, message)
    
    async def _handle_pubsub(self, redis_client: RedisClient, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUBSUB operation."""
        pattern = params.get("pattern", "*")
        
        # Get pubsub info
        channels = await redis_client.pubsub_channels(pattern)
        numsub = await redis_client.pubsub_numsub(*channels) if channels else {}
        
        return {
            "channels": channels,
            "subscribers": numsub,
            "total_channels": len(channels),
            "total_subscribers": sum(numsub.values()) if numsub else 0
        }


# Helper functions for serialization (if needed)
def serialize_value(value: Any) -> str:
    """Serialize a value for Redis storage."""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    elif isinstance(value, (dict, list)):
        return json.dumps(value)
    else:
        return str(value)


def deserialize_value(value: str) -> Any:
    """Deserialize a value from Redis storage."""
    if not value:
        return value
    
    try:
        # Try to parse as JSON
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # If it's not JSON, try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # If it's not a number, return as string
            return value