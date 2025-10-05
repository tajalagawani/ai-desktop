"""
ConversationMemoryNode - Conversation memory management for LLM workflows.
Handles conversation history, context management, memory optimization, and retrieval.
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
from collections import deque, defaultdict

from .base_node import BaseNode, NodeResult, NodeSchema, NodeParameter, NodeParameterType
from ..utils.validation import NodeValidationError

class ConversationMemoryOperation:
    CREATE_CONVERSATION = "create_conversation"
    ADD_MESSAGE = "add_message"
    GET_CONVERSATION = "get_conversation"
    UPDATE_MESSAGE = "update_message"
    DELETE_MESSAGE = "delete_message"
    CLEAR_CONVERSATION = "clear_conversation"
    GET_RECENT_MESSAGES = "get_recent_messages"
    SEARCH_MESSAGES = "search_messages"
    SUMMARIZE_CONVERSATION = "summarize_conversation"
    COMPRESS_MEMORY = "compress_memory"
    GET_CONTEXT_WINDOW = "get_context_window"
    MANAGE_TOKEN_LIMIT = "manage_token_limit"
    CREATE_MEMORY_SNAPSHOT = "create_memory_snapshot"
    RESTORE_MEMORY_SNAPSHOT = "restore_memory_snapshot"
    ANALYZE_CONVERSATION = "analyze_conversation"
    EXTRACT_KEY_POINTS = "extract_key_points"
    GET_CONVERSATION_STATS = "get_conversation_stats"
    MERGE_CONVERSATIONS = "merge_conversations"
    SPLIT_CONVERSATION = "split_conversation"
    TAG_MESSAGES = "tag_messages"
    FILTER_BY_TAGS = "filter_by_tags"
    SET_MEMORY_PRIORITY = "set_memory_priority"
    OPTIMIZE_MEMORY_USAGE = "optimize_memory_usage"
    CREATE_MEMORY_INDEX = "create_memory_index"
    QUERY_SEMANTIC_MEMORY = "query_semantic_memory"

class ConversationMemoryNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.name = "ConversationMemoryNode"
        self.description = "Conversation memory management for LLM workflows"
        self.version = "1.0.0"
        self.icon_path = "🧠"
        
        # Memory storage
        self.conversations = {}
        self.conversation_metadata = {}
        self.memory_snapshots = {}
        self.memory_index = {}
        
        # Configuration
        self.max_conversations = 1000
        self.max_messages_per_conversation = 10000
        self.default_token_limit = 4096
        self.compression_threshold = 0.8

    async def execute(self, operation: str, params: Dict[str, Any]) -> NodeResult:
        try:
            operation_map = {
                ConversationMemoryOperation.CREATE_CONVERSATION: self._create_conversation,
                ConversationMemoryOperation.ADD_MESSAGE: self._add_message,
                ConversationMemoryOperation.GET_CONVERSATION: self._get_conversation,
                ConversationMemoryOperation.UPDATE_MESSAGE: self._update_message,
                ConversationMemoryOperation.DELETE_MESSAGE: self._delete_message,
                ConversationMemoryOperation.CLEAR_CONVERSATION: self._clear_conversation,
                ConversationMemoryOperation.GET_RECENT_MESSAGES: self._get_recent_messages,
                ConversationMemoryOperation.SEARCH_MESSAGES: self._search_messages,
                ConversationMemoryOperation.SUMMARIZE_CONVERSATION: self._summarize_conversation,
                ConversationMemoryOperation.COMPRESS_MEMORY: self._compress_memory,
                ConversationMemoryOperation.GET_CONTEXT_WINDOW: self._get_context_window,
                ConversationMemoryOperation.MANAGE_TOKEN_LIMIT: self._manage_token_limit,
                ConversationMemoryOperation.CREATE_MEMORY_SNAPSHOT: self._create_memory_snapshot,
                ConversationMemoryOperation.RESTORE_MEMORY_SNAPSHOT: self._restore_memory_snapshot,
                ConversationMemoryOperation.ANALYZE_CONVERSATION: self._analyze_conversation,
                ConversationMemoryOperation.EXTRACT_KEY_POINTS: self._extract_key_points,
                ConversationMemoryOperation.GET_CONVERSATION_STATS: self._get_conversation_stats,
                ConversationMemoryOperation.MERGE_CONVERSATIONS: self._merge_conversations,
                ConversationMemoryOperation.SPLIT_CONVERSATION: self._split_conversation,
                ConversationMemoryOperation.TAG_MESSAGES: self._tag_messages,
                ConversationMemoryOperation.FILTER_BY_TAGS: self._filter_by_tags,
                ConversationMemoryOperation.SET_MEMORY_PRIORITY: self._set_memory_priority,
                ConversationMemoryOperation.OPTIMIZE_MEMORY_USAGE: self._optimize_memory_usage,
                ConversationMemoryOperation.CREATE_MEMORY_INDEX: self._create_memory_index,
                ConversationMemoryOperation.QUERY_SEMANTIC_MEMORY: self._query_semantic_memory,
            }

            if operation not in operation_map:
                return self._create_error_result(f"Unknown operation: {operation}")

            self._validate_params(operation, params)
            result = await operation_map[operation](params)
            
            return self._create_success_result(result, f"Conversation memory operation '{operation}' completed")
            
        except Exception as e:
            return self._create_error_result(f"Conversation memory error: {str(e)}")

    async def _create_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation."""
        conversation_id = params.get("conversation_id") or self._generate_conversation_id()
        metadata = params.get("metadata", {})
        token_limit = params.get("token_limit", self.default_token_limit)
        
        if conversation_id in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' already exists")
        
        conversation = {
            "id": conversation_id,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "token_limit": token_limit,
            "current_tokens": 0,
            "message_count": 0,
            "compressed_segments": []
        }
        
        conversation_metadata = {
            "id": conversation_id,
            "title": metadata.get("title", f"Conversation {conversation_id}"),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "priority": metadata.get("priority", "normal"),
            "participants": metadata.get("participants", []),
            "context": metadata.get("context", {}),
            "summary": "",
            "key_topics": [],
            "sentiment": "neutral"
        }
        
        self.conversations[conversation_id] = conversation
        self.conversation_metadata[conversation_id] = conversation_metadata
        
        return {
            "conversation_id": conversation_id,
            "conversation": conversation,
            "metadata": conversation_metadata
        }

    async def _add_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a message to a conversation."""
        conversation_id = params["conversation_id"]
        role = params["role"]  # user, assistant, system
        content = params["content"]
        metadata = params.get("metadata", {})
        auto_compress = params.get("auto_compress", True)
        
        if conversation_id not in self.conversations:
            # Auto-create conversation if it doesn't exist
            await self._create_conversation({"conversation_id": conversation_id})
        
        conversation = self.conversations[conversation_id]
        
        message = {
            "id": self._generate_message_id(),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "tokens": self._estimate_tokens(content),
            "tags": metadata.get("tags", []),
            "priority": metadata.get("priority", "normal"),
            "edited": False,
            "deleted": False
        }
        
        conversation["messages"].append(message)
        conversation["message_count"] += 1
        conversation["current_tokens"] += message["tokens"]
        conversation["updated_at"] = datetime.now().isoformat()
        
        # Check if compression is needed
        if auto_compress and self._should_compress(conversation):
            compression_result = await self._compress_memory({
                "conversation_id": conversation_id,
                "strategy": "automatic"
            })
            message["compression_triggered"] = True
        
        # Update conversation metadata
        self._update_conversation_metadata(conversation_id, message)
        
        return {
            "message": message,
            "conversation_id": conversation_id,
            "total_messages": conversation["message_count"],
            "total_tokens": conversation["current_tokens"]
        }

    async def _get_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a conversation with optional filtering."""
        conversation_id = params["conversation_id"]
        include_metadata = params.get("include_metadata", True)
        include_deleted = params.get("include_deleted", False)
        message_limit = params.get("message_limit")
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id].copy()
        
        # Filter messages
        messages = conversation["messages"]
        if not include_deleted:
            messages = [msg for msg in messages if not msg.get("deleted", False)]
        
        if message_limit:
            messages = messages[-message_limit:]
        
        conversation["messages"] = messages
        
        result = {"conversation": conversation}
        
        if include_metadata:
            result["metadata"] = self.conversation_metadata.get(conversation_id, {})
        
        return result

    async def _update_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message in a conversation."""
        conversation_id = params["conversation_id"]
        message_id = params["message_id"]
        updates = params["updates"]
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        message_found = False
        
        for message in conversation["messages"]:
            if message["id"] == message_id:
                # Update message fields
                if "content" in updates:
                    old_tokens = message["tokens"]
                    message["content"] = updates["content"]
                    message["tokens"] = self._estimate_tokens(updates["content"])
                    conversation["current_tokens"] += message["tokens"] - old_tokens
                
                if "metadata" in updates:
                    message["metadata"].update(updates["metadata"])
                
                if "tags" in updates:
                    message["tags"] = updates["tags"]
                
                message["edited"] = True
                message["edited_at"] = datetime.now().isoformat()
                conversation["updated_at"] = datetime.now().isoformat()
                
                message_found = True
                break
        
        if not message_found:
            raise NodeValidationError(f"Message '{message_id}' not found")
        
        return {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "updated": True
        }

    async def _delete_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a message from a conversation."""
        conversation_id = params["conversation_id"]
        message_id = params["message_id"]
        hard_delete = params.get("hard_delete", False)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        
        if hard_delete:
            # Remove message completely
            original_count = len(conversation["messages"])
            conversation["messages"] = [msg for msg in conversation["messages"] if msg["id"] != message_id]
            deleted = len(conversation["messages"]) < original_count
        else:
            # Soft delete - mark as deleted
            deleted = False
            for message in conversation["messages"]:
                if message["id"] == message_id:
                    message["deleted"] = True
                    message["deleted_at"] = datetime.now().isoformat()
                    conversation["current_tokens"] -= message["tokens"]
                    deleted = True
                    break
        
        if deleted:
            conversation["updated_at"] = datetime.now().isoformat()
        
        return {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "deleted": deleted,
            "hard_delete": hard_delete
        }

    async def _clear_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear all messages from a conversation."""
        conversation_id = params["conversation_id"]
        keep_metadata = params.get("keep_metadata", True)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        message_count = len(conversation["messages"])
        
        conversation["messages"] = []
        conversation["current_tokens"] = 0
        conversation["message_count"] = 0
        conversation["compressed_segments"] = []
        conversation["updated_at"] = datetime.now().isoformat()
        
        if not keep_metadata:
            self.conversation_metadata[conversation_id] = {
                "id": conversation_id,
                "title": f"Conversation {conversation_id}",
                "description": "",
                "tags": [],
                "priority": "normal",
                "participants": [],
                "context": {},
                "summary": "",
                "key_topics": [],
                "sentiment": "neutral"
            }
        
        return {
            "conversation_id": conversation_id,
            "cleared": True,
            "messages_removed": message_count
        }

    async def _get_recent_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent messages from a conversation."""
        conversation_id = params["conversation_id"]
        limit = params.get("limit", 10)
        role_filter = params.get("role_filter")  # user, assistant, system
        include_metadata = params.get("include_metadata", False)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        messages = conversation["messages"]
        
        # Filter by role if specified
        if role_filter:
            messages = [msg for msg in messages if msg["role"] == role_filter]
        
        # Filter out deleted messages
        messages = [msg for msg in messages if not msg.get("deleted", False)]
        
        # Get recent messages
        recent_messages = messages[-limit:] if limit > 0 else messages
        
        # Include/exclude metadata
        if not include_metadata:
            recent_messages = [{k: v for k, v in msg.items() if k != "metadata"} for msg in recent_messages]
        
        return {
            "messages": recent_messages,
            "count": len(recent_messages),
            "conversation_id": conversation_id,
            "total_tokens": sum(msg["tokens"] for msg in recent_messages)
        }

    async def _search_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search messages in conversations."""
        query = params["query"]
        conversation_id = params.get("conversation_id")  # Search specific conversation
        search_type = params.get("search_type", "content")  # content, metadata, tags
        limit = params.get("limit", 50)
        case_sensitive = params.get("case_sensitive", False)
        
        results = []
        conversations_to_search = [conversation_id] if conversation_id else list(self.conversations.keys())
        
        for conv_id in conversations_to_search:
            if conv_id not in self.conversations:
                continue
            
            conversation = self.conversations[conv_id]
            
            for message in conversation["messages"]:
                if message.get("deleted", False):
                    continue
                
                match = False
                
                if search_type in ["content", "all"]:
                    content = message["content"]
                    if not case_sensitive:
                        content = content.lower()
                        query_lower = query.lower()
                    else:
                        query_lower = query
                    
                    if query_lower in content:
                        match = True
                
                if search_type in ["metadata", "all"] and not match:
                    metadata_str = json.dumps(message.get("metadata", {}))
                    if not case_sensitive:
                        metadata_str = metadata_str.lower()
                        query_lower = query.lower()
                    else:
                        query_lower = query
                    
                    if query_lower in metadata_str:
                        match = True
                
                if search_type in ["tags", "all"] and not match:
                    tags = message.get("tags", [])
                    for tag in tags:
                        tag_check = tag.lower() if not case_sensitive else tag
                        query_check = query.lower() if not case_sensitive else query
                        if query_check in tag_check:
                            match = True
                            break
                
                if match:
                    results.append({
                        "conversation_id": conv_id,
                        "message": message,
                        "conversation_title": self.conversation_metadata.get(conv_id, {}).get("title", "")
                    })
                    
                    if len(results) >= limit:
                        break
            
            if len(results) >= limit:
                break
        
        return {
            "results": results,
            "count": len(results),
            "query": query,
            "search_type": search_type
        }

    async def _summarize_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of a conversation."""
        conversation_id = params["conversation_id"]
        summary_type = params.get("summary_type", "overview")  # overview, detailed, key_points
        max_length = params.get("max_length", 500)
        include_statistics = params.get("include_statistics", True)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
        
        if not messages:
            return {
                "conversation_id": conversation_id,
                "summary": "No messages in conversation",
                "summary_type": summary_type,
                "statistics": {} if include_statistics else None
            }
        
        # Generate summary based on type
        if summary_type == "overview":
            summary = self._generate_overview_summary(messages, max_length)
        elif summary_type == "detailed":
            summary = self._generate_detailed_summary(messages, max_length)
        elif summary_type == "key_points":
            summary = self._generate_key_points_summary(messages, max_length)
        else:
            summary = self._generate_overview_summary(messages, max_length)
        
        # Update conversation metadata
        if conversation_id in self.conversation_metadata:
            self.conversation_metadata[conversation_id]["summary"] = summary
        
        result = {
            "conversation_id": conversation_id,
            "summary": summary,
            "summary_type": summary_type,
            "generated_at": datetime.now().isoformat()
        }
        
        if include_statistics:
            result["statistics"] = self._calculate_conversation_statistics(messages)
        
        return result

    async def _compress_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compress conversation memory to save space."""
        conversation_id = params["conversation_id"]
        strategy = params.get("strategy", "summarize")  # summarize, archive, remove_old
        compression_ratio = params.get("compression_ratio", 0.5)
        preserve_recent = params.get("preserve_recent", 10)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        original_message_count = len(conversation["messages"])
        original_tokens = conversation["current_tokens"]
        
        if strategy == "summarize":
            result = await self._compress_by_summarization(conversation, compression_ratio, preserve_recent)
        elif strategy == "archive":
            result = await self._compress_by_archiving(conversation, compression_ratio, preserve_recent)
        elif strategy == "remove_old":
            result = await self._compress_by_removal(conversation, compression_ratio, preserve_recent)
        else:
            raise NodeValidationError(f"Unknown compression strategy: {strategy}")
        
        # Update conversation statistics
        conversation["updated_at"] = datetime.now().isoformat()
        new_message_count = len(conversation["messages"])
        new_tokens = conversation["current_tokens"]
        
        compression_stats = {
            "conversation_id": conversation_id,
            "strategy": strategy,
            "original_messages": original_message_count,
            "compressed_messages": new_message_count,
            "original_tokens": original_tokens,
            "compressed_tokens": new_tokens,
            "compression_ratio": (original_tokens - new_tokens) / original_tokens if original_tokens > 0 else 0,
            "messages_removed": original_message_count - new_message_count,
            "compressed_at": datetime.now().isoformat()
        }
        
        return {
            "compression_stats": compression_stats,
            "compression_result": result
        }

    async def _get_context_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get messages that fit within a context window."""
        conversation_id = params["conversation_id"]
        token_limit = params.get("token_limit", self.default_token_limit)
        strategy = params.get("strategy", "recent")  # recent, important, balanced
        include_system = params.get("include_system", True)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
        
        if not include_system:
            messages = [msg for msg in messages if msg["role"] != "system"]
        
        if strategy == "recent":
            context_messages = self._get_recent_context(messages, token_limit)
        elif strategy == "important":
            context_messages = self._get_important_context(messages, token_limit)
        elif strategy == "balanced":
            context_messages = self._get_balanced_context(messages, token_limit)
        else:
            context_messages = self._get_recent_context(messages, token_limit)
        
        total_tokens = sum(msg["tokens"] for msg in context_messages)
        
        return {
            "conversation_id": conversation_id,
            "context_messages": context_messages,
            "message_count": len(context_messages),
            "total_tokens": total_tokens,
            "token_limit": token_limit,
            "utilization": total_tokens / token_limit if token_limit > 0 else 0,
            "strategy": strategy
        }

    async def _manage_token_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manage conversation to stay within token limits."""
        conversation_id = params["conversation_id"]
        token_limit = params.get("token_limit")
        action = params.get("action", "compress")  # compress, truncate, summarize
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        
        if token_limit:
            conversation["token_limit"] = token_limit
        else:
            token_limit = conversation["token_limit"]
        
        current_tokens = conversation["current_tokens"]
        
        if current_tokens <= token_limit:
            return {
                "conversation_id": conversation_id,
                "action_needed": False,
                "current_tokens": current_tokens,
                "token_limit": token_limit,
                "utilization": current_tokens / token_limit
            }
        
        # Take action to reduce tokens
        if action == "compress":
            compression_result = await self._compress_memory({
                "conversation_id": conversation_id,
                "strategy": "summarize",
                "compression_ratio": 0.3
            })
            action_result = compression_result
        
        elif action == "truncate":
            # Remove oldest messages
            messages = conversation["messages"]
            while conversation["current_tokens"] > token_limit and messages:
                removed_message = messages.pop(0)
                conversation["current_tokens"] -= removed_message["tokens"]
                conversation["message_count"] -= 1
            
            action_result = {
                "messages_removed": len(conversation["messages"]),
                "tokens_saved": current_tokens - conversation["current_tokens"]
            }
        
        elif action == "summarize":
            # Summarize older messages
            summary_result = await self._summarize_conversation({
                "conversation_id": conversation_id,
                "summary_type": "detailed"
            })
            
            # Replace older messages with summary
            messages = conversation["messages"]
            if len(messages) > 5:  # Keep last 5 messages
                summarized_messages = messages[:-5]
                conversation["messages"] = messages[-5:]
                conversation["current_tokens"] = sum(msg["tokens"] for msg in conversation["messages"])
                
                # Add summary as system message
                summary_message = {
                    "id": self._generate_message_id(),
                    "role": "system",
                    "content": f"Previous conversation summary: {summary_result['summary']}",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"type": "summary", "original_messages": len(summarized_messages)},
                    "tokens": self._estimate_tokens(summary_result['summary']),
                    "tags": ["summary"],
                    "priority": "high",
                    "edited": False,
                    "deleted": False
                }
                
                conversation["messages"].insert(0, summary_message)
                conversation["current_tokens"] += summary_message["tokens"]
            
            action_result = summary_result
        
        return {
            "conversation_id": conversation_id,
            "action_taken": action,
            "action_result": action_result,
            "new_token_count": conversation["current_tokens"],
            "token_limit": token_limit,
            "utilization": conversation["current_tokens"] / token_limit
        }

    async def _create_memory_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a snapshot of conversation memory."""
        conversation_id = params.get("conversation_id")
        snapshot_name = params.get("snapshot_name") or f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        include_metadata = params.get("include_metadata", True)
        
        if conversation_id:
            # Snapshot specific conversation
            if conversation_id not in self.conversations:
                raise NodeValidationError(f"Conversation '{conversation_id}' not found")
            
            snapshot_data = {
                "conversation": self.conversations[conversation_id].copy(),
                "metadata": self.conversation_metadata.get(conversation_id, {}) if include_metadata else None
            }
        else:
            # Snapshot all conversations
            snapshot_data = {
                "conversations": self.conversations.copy(),
                "metadata": self.conversation_metadata.copy() if include_metadata else None
            }
        
        snapshot = {
            "name": snapshot_name,
            "created_at": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "data": snapshot_data,
            "checksum": self._calculate_checksum(snapshot_data)
        }
        
        self.memory_snapshots[snapshot_name] = snapshot
        
        return {
            "snapshot_name": snapshot_name,
            "conversation_id": conversation_id,
            "created_at": snapshot["created_at"],
            "checksum": snapshot["checksum"]
        }

    async def _restore_memory_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restore conversation memory from a snapshot."""
        snapshot_name = params["snapshot_name"]
        verify_checksum = params.get("verify_checksum", True)
        overwrite_existing = params.get("overwrite_existing", False)
        
        if snapshot_name not in self.memory_snapshots:
            raise NodeValidationError(f"Snapshot '{snapshot_name}' not found")
        
        snapshot = self.memory_snapshots[snapshot_name]
        
        # Verify checksum if requested
        if verify_checksum:
            current_checksum = self._calculate_checksum(snapshot["data"])
            if current_checksum != snapshot["checksum"]:
                raise NodeValidationError("Snapshot checksum verification failed")
        
        restored_conversations = []
        
        if "conversation" in snapshot["data"]:
            # Single conversation snapshot
            conversation_id = snapshot["conversation_id"]
            
            if conversation_id in self.conversations and not overwrite_existing:
                raise NodeValidationError(f"Conversation '{conversation_id}' already exists. Use overwrite_existing=True to replace.")
            
            self.conversations[conversation_id] = snapshot["data"]["conversation"]
            if snapshot["data"]["metadata"]:
                self.conversation_metadata[conversation_id] = snapshot["data"]["metadata"]
            
            restored_conversations.append(conversation_id)
        
        else:
            # Multiple conversations snapshot
            for conv_id, conv_data in snapshot["data"]["conversations"].items():
                if conv_id in self.conversations and not overwrite_existing:
                    continue
                
                self.conversations[conv_id] = conv_data
                restored_conversations.append(conv_id)
            
            if snapshot["data"]["metadata"]:
                for conv_id, metadata in snapshot["data"]["metadata"].items():
                    if conv_id in restored_conversations or overwrite_existing:
                        self.conversation_metadata[conv_id] = metadata
        
        return {
            "snapshot_name": snapshot_name,
            "restored_conversations": restored_conversations,
            "restored_count": len(restored_conversations),
            "restored_at": datetime.now().isoformat()
        }

    async def _analyze_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation patterns and characteristics."""
        conversation_id = params["conversation_id"]
        analysis_type = params.get("analysis_type", "comprehensive")  # basic, comprehensive, sentiment, topics
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
        
        analysis = {
            "conversation_id": conversation_id,
            "analysis_type": analysis_type,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if analysis_type in ["basic", "comprehensive"]:
            analysis["basic_stats"] = self._analyze_basic_statistics(messages)
        
        if analysis_type in ["comprehensive", "sentiment"]:
            analysis["sentiment_analysis"] = self._analyze_sentiment(messages)
        
        if analysis_type in ["comprehensive", "topics"]:
            analysis["topic_analysis"] = self._analyze_topics(messages)
        
        if analysis_type == "comprehensive":
            analysis["interaction_patterns"] = self._analyze_interaction_patterns(messages)
            analysis["temporal_patterns"] = self._analyze_temporal_patterns(messages)
            analysis["engagement_metrics"] = self._analyze_engagement_metrics(messages)
        
        return analysis

    async def _extract_key_points(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key points from conversation."""
        conversation_id = params["conversation_id"]
        extraction_method = params.get("extraction_method", "frequency")  # frequency, importance, recent
        max_points = params.get("max_points", 10)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
        
        if extraction_method == "frequency":
            key_points = self._extract_frequent_points(messages, max_points)
        elif extraction_method == "importance":
            key_points = self._extract_important_points(messages, max_points)
        elif extraction_method == "recent":
            key_points = self._extract_recent_points(messages, max_points)
        else:
            key_points = self._extract_frequent_points(messages, max_points)
        
        # Update conversation metadata
        if conversation_id in self.conversation_metadata:
            self.conversation_metadata[conversation_id]["key_topics"] = [point["topic"] for point in key_points]
        
        return {
            "conversation_id": conversation_id,
            "key_points": key_points,
            "extraction_method": extraction_method,
            "extracted_at": datetime.now().isoformat()
        }

    async def _get_conversation_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive conversation statistics."""
        conversation_id = params.get("conversation_id")
        include_global = params.get("include_global", True)
        
        if conversation_id:
            if conversation_id not in self.conversations:
                raise NodeValidationError(f"Conversation '{conversation_id}' not found")
            
            conversation = self.conversations[conversation_id]
            messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
            
            stats = {
                "conversation_id": conversation_id,
                "stats": self._calculate_conversation_statistics(messages),
                "metadata": self.conversation_metadata.get(conversation_id, {})
            }
        else:
            # Global statistics
            stats = {
                "global_stats": self._calculate_global_statistics(),
                "conversation_count": len(self.conversations)
            }
        
        if include_global and conversation_id:
            stats["global_context"] = self._calculate_global_statistics()
        
        return stats

    async def _merge_conversations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple conversations into one."""
        conversation_ids = params["conversation_ids"]
        target_conversation_id = params.get("target_conversation_id")
        merge_strategy = params.get("merge_strategy", "chronological")  # chronological, interleaved
        new_title = params.get("new_title")
        
        if len(conversation_ids) < 2:
            raise NodeValidationError("At least 2 conversations are required for merging")
        
        # Validate all conversations exist
        for conv_id in conversation_ids:
            if conv_id not in self.conversations:
                raise NodeValidationError(f"Conversation '{conv_id}' not found")
        
        # Create target conversation if not specified
        if not target_conversation_id:
            target_conversation_id = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Collect all messages
        all_messages = []
        merged_metadata = {
            "participants": set(),
            "tags": set(),
            "contexts": []
        }
        
        for conv_id in conversation_ids:
            conversation = self.conversations[conv_id]
            messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
            
            # Add conversation context to messages
            for message in messages:
                message["original_conversation"] = conv_id
            
            all_messages.extend(messages)
            
            # Merge metadata
            if conv_id in self.conversation_metadata:
                metadata = self.conversation_metadata[conv_id]
                merged_metadata["participants"].update(metadata.get("participants", []))
                merged_metadata["tags"].update(metadata.get("tags", []))
                merged_metadata["contexts"].append(metadata.get("context", {}))
        
        # Sort messages based on strategy
        if merge_strategy == "chronological":
            all_messages.sort(key=lambda x: x["timestamp"])
        elif merge_strategy == "interleaved":
            # Simple interleaving - could be more sophisticated
            all_messages.sort(key=lambda x: (x["original_conversation"], x["timestamp"]))
        
        # Create merged conversation
        merged_conversation = {
            "id": target_conversation_id,
            "messages": all_messages,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "token_limit": self.default_token_limit,
            "current_tokens": sum(msg["tokens"] for msg in all_messages),
            "message_count": len(all_messages),
            "compressed_segments": [],
            "merged_from": conversation_ids
        }
        
        merged_conversation_metadata = {
            "id": target_conversation_id,
            "title": new_title or f"Merged conversation from {len(conversation_ids)} conversations",
            "description": f"Merged from conversations: {', '.join(conversation_ids)}",
            "tags": list(merged_metadata["tags"]),
            "priority": "normal",
            "participants": list(merged_metadata["participants"]),
            "context": {"merged_contexts": merged_metadata["contexts"]},
            "summary": "",
            "key_topics": [],
            "sentiment": "neutral"
        }
        
        self.conversations[target_conversation_id] = merged_conversation
        self.conversation_metadata[target_conversation_id] = merged_conversation_metadata
        
        return {
            "target_conversation_id": target_conversation_id,
            "merged_conversations": conversation_ids,
            "total_messages": len(all_messages),
            "total_tokens": merged_conversation["current_tokens"],
            "merge_strategy": merge_strategy
        }

    async def _split_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Split a conversation into multiple conversations."""
        conversation_id = params["conversation_id"]
        split_criteria = params["split_criteria"]  # topic_change, time_gap, participant_change, manual
        split_config = params.get("split_config", {})
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
        
        if split_criteria == "topic_change":
            split_points = self._find_topic_change_points(messages, split_config)
        elif split_criteria == "time_gap":
            split_points = self._find_time_gap_points(messages, split_config)
        elif split_criteria == "participant_change":
            split_points = self._find_participant_change_points(messages, split_config)
        elif split_criteria == "manual":
            split_points = split_config.get("split_points", [])
        else:
            raise NodeValidationError(f"Unknown split criteria: {split_criteria}")
        
        # Create sub-conversations
        sub_conversations = []
        start_index = 0
        
        for i, split_point in enumerate(split_points + [len(messages)]):
            if split_point > start_index:
                sub_messages = messages[start_index:split_point]
                sub_conversation_id = f"{conversation_id}_part_{i+1}"
                
                sub_conversation = {
                    "id": sub_conversation_id,
                    "messages": sub_messages,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "token_limit": self.default_token_limit,
                    "current_tokens": sum(msg["tokens"] for msg in sub_messages),
                    "message_count": len(sub_messages),
                    "compressed_segments": [],
                    "split_from": conversation_id
                }
                
                sub_metadata = self.conversation_metadata.get(conversation_id, {}).copy()
                sub_metadata.update({
                    "id": sub_conversation_id,
                    "title": f"{sub_metadata.get('title', 'Conversation')} - Part {i+1}",
                    "description": f"Split from {conversation_id}"
                })
                
                self.conversations[sub_conversation_id] = sub_conversation
                self.conversation_metadata[sub_conversation_id] = sub_metadata
                sub_conversations.append(sub_conversation_id)
                
                start_index = split_point
        
        return {
            "original_conversation_id": conversation_id,
            "sub_conversations": sub_conversations,
            "split_criteria": split_criteria,
            "split_points": split_points
        }

    async def _tag_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add tags to messages in a conversation."""
        conversation_id = params["conversation_id"]
        tagging_rules = params["tagging_rules"]  # List of {condition, tags} rules
        overwrite_existing = params.get("overwrite_existing", False)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        tagged_count = 0
        
        for message in conversation["messages"]:
            if message.get("deleted", False):
                continue
            
            new_tags = []
            
            for rule in tagging_rules:
                condition = rule["condition"]
                tags = rule["tags"]
                
                if self._evaluate_tagging_condition(message, condition):
                    new_tags.extend(tags)
            
            if new_tags:
                if overwrite_existing:
                    message["tags"] = new_tags
                else:
                    existing_tags = set(message.get("tags", []))
                    existing_tags.update(new_tags)
                    message["tags"] = list(existing_tags)
                
                tagged_count += 1
        
        conversation["updated_at"] = datetime.now().isoformat()
        
        return {
            "conversation_id": conversation_id,
            "tagged_messages": tagged_count,
            "tagging_rules_applied": len(tagging_rules)
        }

    async def _filter_by_tags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter messages by tags."""
        conversation_id = params["conversation_id"]
        tags = params["tags"]
        filter_mode = params.get("filter_mode", "any")  # any, all, none
        include_metadata = params.get("include_metadata", False)
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        filtered_messages = []
        
        for message in conversation["messages"]:
            if message.get("deleted", False):
                continue
            
            message_tags = set(message.get("tags", []))
            filter_tags = set(tags)
            
            if filter_mode == "any" and message_tags.intersection(filter_tags):
                filtered_messages.append(message)
            elif filter_mode == "all" and filter_tags.issubset(message_tags):
                filtered_messages.append(message)
            elif filter_mode == "none" and not message_tags.intersection(filter_tags):
                filtered_messages.append(message)
        
        if not include_metadata:
            filtered_messages = [{k: v for k, v in msg.items() if k != "metadata"} for msg in filtered_messages]
        
        return {
            "conversation_id": conversation_id,
            "filtered_messages": filtered_messages,
            "count": len(filtered_messages),
            "filter_tags": tags,
            "filter_mode": filter_mode
        }

    async def _set_memory_priority(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set priority levels for memory management."""
        conversation_id = params["conversation_id"]
        priority_rules = params["priority_rules"]  # List of {condition, priority} rules
        
        if conversation_id not in self.conversations:
            raise NodeValidationError(f"Conversation '{conversation_id}' not found")
        
        conversation = self.conversations[conversation_id]
        updated_count = 0
        
        for message in conversation["messages"]:
            if message.get("deleted", False):
                continue
            
            for rule in priority_rules:
                condition = rule["condition"]
                priority = rule["priority"]
                
                if self._evaluate_priority_condition(message, condition):
                    message["priority"] = priority
                    updated_count += 1
                    break  # Apply first matching rule
        
        conversation["updated_at"] = datetime.now().isoformat()
        
        return {
            "conversation_id": conversation_id,
            "updated_messages": updated_count,
            "priority_rules_applied": len(priority_rules)
        }

    async def _optimize_memory_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize memory usage across all conversations."""
        optimization_strategy = params.get("optimization_strategy", "comprehensive")  # basic, comprehensive, aggressive
        target_memory_usage = params.get("target_memory_usage", 0.8)  # 80% of max capacity
        
        optimization_results = {
            "strategy": optimization_strategy,
            "started_at": datetime.now().isoformat(),
            "conversations_optimized": [],
            "total_memory_saved": 0,
            "total_messages_affected": 0
        }
        
        current_usage = self._calculate_memory_usage()
        
        if current_usage <= target_memory_usage:
            optimization_results["optimization_needed"] = False
            return optimization_results
        
        optimization_results["optimization_needed"] = True
        optimization_results["initial_usage"] = current_usage
        
        # Sort conversations by priority for optimization
        conversations_by_priority = self._sort_conversations_for_optimization()
        
        for conv_id in conversations_by_priority:
            if self._calculate_memory_usage() <= target_memory_usage:
                break
            
            conversation = self.conversations[conv_id]
            original_tokens = conversation["current_tokens"]
            original_messages = len(conversation["messages"])
            
            if optimization_strategy in ["basic", "comprehensive", "aggressive"]:
                # Apply compression
                compression_ratio = 0.3 if optimization_strategy == "aggressive" else 0.5
                await self._compress_memory({
                    "conversation_id": conv_id,
                    "strategy": "summarize",
                    "compression_ratio": compression_ratio
                })
            
            if optimization_strategy in ["comprehensive", "aggressive"]:
                # Remove low-priority messages
                self._remove_low_priority_messages(conv_id)
            
            if optimization_strategy == "aggressive":
                # Archive old conversations
                if self._should_archive_conversation(conv_id):
                    self._archive_conversation(conv_id)
            
            new_tokens = conversation["current_tokens"]
            new_messages = len(conversation["messages"])
            
            optimization_results["conversations_optimized"].append({
                "conversation_id": conv_id,
                "tokens_saved": original_tokens - new_tokens,
                "messages_affected": original_messages - new_messages
            })
            
            optimization_results["total_memory_saved"] += original_tokens - new_tokens
            optimization_results["total_messages_affected"] += original_messages - new_messages
        
        optimization_results["final_usage"] = self._calculate_memory_usage()
        optimization_results["completed_at"] = datetime.now().isoformat()
        
        return optimization_results

    async def _create_memory_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create searchable index of conversation memory."""
        conversation_id = params.get("conversation_id")
        index_type = params.get("index_type", "keyword")  # keyword, semantic, combined
        rebuild_existing = params.get("rebuild_existing", False)
        
        conversations_to_index = [conversation_id] if conversation_id else list(self.conversations.keys())
        
        indexed_conversations = []
        
        for conv_id in conversations_to_index:
            if conv_id not in self.conversations:
                continue
            
            if conv_id in self.memory_index and not rebuild_existing:
                continue
            
            conversation = self.conversations[conv_id]
            messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
            
            if index_type in ["keyword", "combined"]:
                keyword_index = self._create_keyword_index(messages)
            else:
                keyword_index = {}
            
            if index_type in ["semantic", "combined"]:
                semantic_index = self._create_semantic_index(messages)
            else:
                semantic_index = {}
            
            self.memory_index[conv_id] = {
                "conversation_id": conv_id,
                "index_type": index_type,
                "keyword_index": keyword_index,
                "semantic_index": semantic_index,
                "created_at": datetime.now().isoformat(),
                "message_count": len(messages)
            }
            
            indexed_conversations.append(conv_id)
        
        return {
            "indexed_conversations": indexed_conversations,
            "index_type": index_type,
            "total_indexed": len(indexed_conversations)
        }

    async def _query_semantic_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query conversations using semantic search."""
        query = params["query"]
        conversation_id = params.get("conversation_id")
        limit = params.get("limit", 10)
        similarity_threshold = params.get("similarity_threshold", 0.7)
        
        # This is a simplified semantic search implementation
        # In practice, you'd use embeddings and vector similarity
        
        conversations_to_search = [conversation_id] if conversation_id else list(self.conversations.keys())
        
        results = []
        
        for conv_id in conversations_to_search:
            if conv_id not in self.conversations:
                continue
            
            conversation = self.conversations[conv_id]
            messages = [msg for msg in conversation["messages"] if not msg.get("deleted", False)]
            
            for message in messages:
                # Simple semantic similarity (would use embeddings in practice)
                similarity = self._calculate_semantic_similarity(query, message["content"])
                
                if similarity >= similarity_threshold:
                    results.append({
                        "conversation_id": conv_id,
                        "message": message,
                        "similarity_score": similarity,
                        "conversation_title": self.conversation_metadata.get(conv_id, {}).get("title", "")
                    })
        
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "query": query,
            "results": results[:limit],
            "total_matches": len(results),
            "similarity_threshold": similarity_threshold
        }

    # Helper methods
    def _generate_conversation_id(self):
        """Generate unique conversation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"conv_{timestamp}_{len(self.conversations)}"

    def _generate_message_id(self):
        """Generate unique message ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"msg_{timestamp}"

    def _estimate_tokens(self, text):
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4 + 1

    def _should_compress(self, conversation):
        """Check if conversation should be compressed."""
        token_utilization = conversation["current_tokens"] / conversation["token_limit"]
        return token_utilization > self.compression_threshold

    def _update_conversation_metadata(self, conversation_id, message):
        """Update conversation metadata based on new message."""
        if conversation_id not in self.conversation_metadata:
            return
        
        metadata = self.conversation_metadata[conversation_id]
        
        # Update participants
        if message["role"] not in ["system"] and message["role"] not in metadata["participants"]:
            metadata["participants"].append(message["role"])
        
        # Extract and update tags
        if message.get("tags"):
            existing_tags = set(metadata.get("tags", []))
            existing_tags.update(message["tags"])
            metadata["tags"] = list(existing_tags)

    def _generate_overview_summary(self, messages, max_length):
        """Generate overview summary of conversation."""
        if not messages:
            return "No messages to summarize"
        
        total_messages = len(messages)
        user_messages = len([m for m in messages if m["role"] == "user"])
        assistant_messages = len([m for m in messages if m["role"] == "assistant"])
        
        first_message = messages[0]["content"][:100] + "..." if len(messages[0]["content"]) > 100 else messages[0]["content"]
        last_message = messages[-1]["content"][:100] + "..." if len(messages[-1]["content"]) > 100 else messages[-1]["content"]
        
        summary = f"Conversation with {total_messages} messages ({user_messages} from user, {assistant_messages} from assistant). "
        summary += f"Started with: '{first_message}' "
        summary += f"Latest: '{last_message}'"
        
        return summary[:max_length] + "..." if len(summary) > max_length else summary

    def _generate_detailed_summary(self, messages, max_length):
        """Generate detailed summary of conversation."""
        # This would ideally use an LLM to generate a proper summary
        # For now, extract key sentences from each role
        
        user_content = []
        assistant_content = []
        
        for message in messages:
            if message["role"] == "user":
                user_content.append(message["content"][:200])
            elif message["role"] == "assistant":
                assistant_content.append(message["content"][:200])
        
        summary = "User discussed: " + " | ".join(user_content[:3])
        summary += " Assistant responded with: " + " | ".join(assistant_content[:3])
        
        return summary[:max_length] + "..." if len(summary) > max_length else summary

    def _generate_key_points_summary(self, messages, max_length):
        """Generate key points summary."""
        # Extract sentences with important keywords
        important_words = ["important", "key", "main", "critical", "essential", "remember", "note"]
        key_sentences = []
        
        for message in messages:
            sentences = message["content"].split(".")
            for sentence in sentences:
                if any(word in sentence.lower() for word in important_words):
                    key_sentences.append(sentence.strip())
        
        summary = "Key points: " + " | ".join(key_sentences[:5])
        return summary[:max_length] + "..." if len(summary) > max_length else summary

    def _calculate_conversation_statistics(self, messages):
        """Calculate comprehensive conversation statistics."""
        if not messages:
            return {}
        
        total_messages = len(messages)
        total_tokens = sum(msg["tokens"] for msg in messages)
        
        role_counts = defaultdict(int)
        for message in messages:
            role_counts[message["role"]] += 1
        
        time_span = None
        if len(messages) > 1:
            start_time = datetime.fromisoformat(messages[0]["timestamp"])
            end_time = datetime.fromisoformat(messages[-1]["timestamp"])
            time_span = (end_time - start_time).total_seconds()
        
        return {
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "average_tokens_per_message": total_tokens / total_messages,
            "role_distribution": dict(role_counts),
            "time_span_seconds": time_span,
            "first_message_time": messages[0]["timestamp"],
            "last_message_time": messages[-1]["timestamp"]
        }

    async def _compress_by_summarization(self, conversation, compression_ratio, preserve_recent):
        """Compress conversation by summarizing older messages."""
        messages = conversation["messages"]
        
        if len(messages) <= preserve_recent:
            return {"compression_applied": False, "reason": "not enough messages"}
        
        # Keep recent messages, summarize older ones
        messages_to_summarize = messages[:-preserve_recent]
        recent_messages = messages[-preserve_recent:]
        
        # Create summary of older messages
        summary_result = await self._summarize_conversation({
            "conversation_id": conversation["id"]
        })
        
        # Replace older messages with summary
        summary_message = {
            "id": self._generate_message_id(),
            "role": "system",
            "content": f"[COMPRESSED] Previous {len(messages_to_summarize)} messages: {summary_result.get('summary', '')}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {"type": "compression_summary", "original_count": len(messages_to_summarize)},
            "tokens": self._estimate_tokens(summary_result.get('summary', '')),
            "tags": ["compressed"],
            "priority": "high",
            "edited": False,
            "deleted": False
        }
        
        conversation["messages"] = [summary_message] + recent_messages
        conversation["current_tokens"] = sum(msg["tokens"] for msg in conversation["messages"])
        conversation["compressed_segments"].append({
            "original_count": len(messages_to_summarize),
            "compressed_at": datetime.now().isoformat(),
            "summary": summary_result.get('summary', '')
        })
        
        return {
            "compression_applied": True,
            "original_messages": len(messages),
            "compressed_messages": len(conversation["messages"]),
            "summary_created": True
        }

    async def _compress_by_archiving(self, conversation, compression_ratio, preserve_recent):
        """Compress by archiving older messages."""
        messages = conversation["messages"]
        
        if len(messages) <= preserve_recent:
            return {"compression_applied": False, "reason": "not enough messages"}
        
        # Archive older messages
        messages_to_archive = messages[:-preserve_recent]
        conversation["messages"] = messages[-preserve_recent:]
        conversation["current_tokens"] = sum(msg["tokens"] for msg in conversation["messages"])
        
        # Store archived messages
        archive_key = f"{conversation['id']}_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conversation["compressed_segments"].append({
            "type": "archive",
            "archive_key": archive_key,
            "message_count": len(messages_to_archive),
            "archived_at": datetime.now().isoformat()
        })
        
        return {
            "compression_applied": True,
            "original_messages": len(messages),
            "remaining_messages": len(conversation["messages"]),
            "archived_messages": len(messages_to_archive),
            "archive_key": archive_key
        }

    async def _compress_by_removal(self, conversation, compression_ratio, preserve_recent):
        """Compress by removing older messages."""
        messages = conversation["messages"]
        target_count = max(preserve_recent, int(len(messages) * (1 - compression_ratio)))
        
        if len(messages) <= target_count:
            return {"compression_applied": False, "reason": "target already achieved"}
        
        # Remove oldest messages
        removed_count = len(messages) - target_count
        conversation["messages"] = messages[-target_count:]
        conversation["current_tokens"] = sum(msg["tokens"] for msg in conversation["messages"])
        
        return {
            "compression_applied": True,
            "original_messages": len(messages),
            "remaining_messages": len(conversation["messages"]),
            "removed_messages": removed_count
        }

    def _get_recent_context(self, messages, token_limit):
        """Get recent messages that fit within token limit."""
        context_messages = []
        current_tokens = 0
        
        for message in reversed(messages):
            if current_tokens + message["tokens"] <= token_limit:
                context_messages.insert(0, message)
                current_tokens += message["tokens"]
            else:
                break
        
        return context_messages

    def _get_important_context(self, messages, token_limit):
        """Get important messages that fit within token limit."""
        # Sort by priority and recency
        prioritized_messages = sorted(
            messages,
            key=lambda x: (x.get("priority", "normal") == "high", x["timestamp"]),
            reverse=True
        )
        
        context_messages = []
        current_tokens = 0
        
        for message in prioritized_messages:
            if current_tokens + message["tokens"] <= token_limit:
                context_messages.append(message)
                current_tokens += message["tokens"]
            else:
                break
        
        # Sort back to chronological order
        context_messages.sort(key=lambda x: x["timestamp"])
        return context_messages

    def _get_balanced_context(self, messages, token_limit):
        """Get balanced mix of recent and important messages."""
        # Reserve half tokens for recent messages
        recent_limit = token_limit // 2
        important_limit = token_limit - recent_limit
        
        recent_messages = self._get_recent_context(messages, recent_limit)
        important_messages = self._get_important_context(messages, important_limit)
        
        # Combine and deduplicate
        combined_messages = []
        message_ids = set()
        
        for message in recent_messages + important_messages:
            if message["id"] not in message_ids:
                combined_messages.append(message)
                message_ids.add(message["id"])
        
        # Sort chronologically
        combined_messages.sort(key=lambda x: x["timestamp"])
        
        # Ensure we don't exceed token limit
        final_messages = []
        current_tokens = 0
        
        for message in combined_messages:
            if current_tokens + message["tokens"] <= token_limit:
                final_messages.append(message)
                current_tokens += message["tokens"]
            else:
                break
        
        return final_messages

    def _calculate_checksum(self, data):
        """Calculate checksum for data integrity."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _analyze_basic_statistics(self, messages):
        """Analyze basic conversation statistics."""
        return self._calculate_conversation_statistics(messages)

    def _analyze_sentiment(self, messages):
        """Analyze sentiment of conversation."""
        # Simplified sentiment analysis
        positive_words = ["good", "great", "excellent", "love", "like", "happy", "pleased"]
        negative_words = ["bad", "terrible", "hate", "angry", "sad", "frustrated", "awful"]
        
        sentiment_scores = []
        
        for message in messages:
            content_lower = message["content"].lower()
            positive_count = sum(content_lower.count(word) for word in positive_words)
            negative_count = sum(content_lower.count(word) for word in negative_words)
            
            if positive_count > negative_count:
                sentiment_scores.append(1)
            elif negative_count > positive_count:
                sentiment_scores.append(-1)
            else:
                sentiment_scores.append(0)
        
        overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if overall_sentiment > 0.1:
            sentiment_label = "positive"
        elif overall_sentiment < -0.1:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return {
            "overall_sentiment": sentiment_label,
            "sentiment_score": overall_sentiment,
            "positive_messages": sentiment_scores.count(1),
            "negative_messages": sentiment_scores.count(-1),
            "neutral_messages": sentiment_scores.count(0)
        }

    def _analyze_topics(self, messages):
        """Analyze topics in conversation."""
        # Simple keyword extraction
        word_freq = defaultdict(int)
        
        for message in messages:
            words = message["content"].lower().split()
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_freq[word] += 1
        
        # Get most frequent words as topics
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "top_topics": [{"topic": word, "frequency": freq} for word, freq in topics],
            "total_unique_words": len(word_freq)
        }

    def _analyze_interaction_patterns(self, messages):
        """Analyze interaction patterns between participants."""
        role_transitions = []
        
        for i in range(1, len(messages)):
            prev_role = messages[i-1]["role"]
            curr_role = messages[i]["role"]
            role_transitions.append(f"{prev_role}->{curr_role}")
        
        transition_counts = defaultdict(int)
        for transition in role_transitions:
            transition_counts[transition] += 1
        
        return {
            "role_transitions": dict(transition_counts),
            "total_transitions": len(role_transitions)
        }

    def _analyze_temporal_patterns(self, messages):
        """Analyze temporal patterns in conversation."""
        if len(messages) < 2:
            return {"message_intervals": [], "average_interval": 0}
        
        intervals = []
        
        for i in range(1, len(messages)):
            prev_time = datetime.fromisoformat(messages[i-1]["timestamp"])
            curr_time = datetime.fromisoformat(messages[i]["timestamp"])
            interval = (curr_time - prev_time).total_seconds()
            intervals.append(interval)
        
        return {
            "message_intervals": intervals,
            "average_interval": sum(intervals) / len(intervals),
            "min_interval": min(intervals),
            "max_interval": max(intervals)
        }

    def _analyze_engagement_metrics(self, messages):
        """Analyze engagement metrics."""
        total_chars = sum(len(msg["content"]) for msg in messages)
        avg_message_length = total_chars / len(messages) if messages else 0
        
        return {
            "total_characters": total_chars,
            "average_message_length": avg_message_length,
            "longest_message": max((len(msg["content"]) for msg in messages), default=0),
            "shortest_message": min((len(msg["content"]) for msg in messages), default=0)
        }

    def _extract_frequent_points(self, messages, max_points):
        """Extract frequently mentioned points."""
        # Simple frequency-based extraction
        word_freq = defaultdict(int)
        
        for message in messages:
            words = message["content"].lower().split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    word_freq[word] += 1
        
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_points]
        
        return [{"topic": word, "frequency": freq, "type": "frequent"} for word, freq in frequent_words]

    def _extract_important_points(self, messages, max_points):
        """Extract important points based on message priority."""
        important_messages = [msg for msg in messages if msg.get("priority") == "high"]
        
        if not important_messages:
            return self._extract_frequent_points(messages, max_points)
        
        points = []
        for message in important_messages[:max_points]:
            points.append({
                "topic": message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"],
                "message_id": message["id"],
                "type": "important"
            })
        
        return points

    def _extract_recent_points(self, messages, max_points):
        """Extract recent key points."""
        recent_messages = messages[-max_points:] if len(messages) > max_points else messages
        
        return [
            {
                "topic": msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"],
                "message_id": msg["id"],
                "timestamp": msg["timestamp"],
                "type": "recent"
            }
            for msg in recent_messages
        ]

    def _calculate_global_statistics(self):
        """Calculate statistics across all conversations."""
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv["messages"]) for conv in self.conversations.values())
        total_tokens = sum(conv["current_tokens"] for conv in self.conversations.values())
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "average_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0,
            "average_tokens_per_conversation": total_tokens / total_conversations if total_conversations > 0 else 0
        }

    def _find_topic_change_points(self, messages, config):
        """Find points where topic changes significantly."""
        # Simplified topic change detection
        split_points = []
        window_size = config.get("window_size", 5)
        
        for i in range(window_size, len(messages) - window_size, window_size):
            # This would ideally use semantic similarity
            # For now, just split at regular intervals
            split_points.append(i)
        
        return split_points

    def _find_time_gap_points(self, messages, config):
        """Find points where there are significant time gaps."""
        split_points = []
        gap_threshold = config.get("gap_threshold_seconds", 3600)  # 1 hour default
        
        for i in range(1, len(messages)):
            prev_time = datetime.fromisoformat(messages[i-1]["timestamp"])
            curr_time = datetime.fromisoformat(messages[i]["timestamp"])
            gap = (curr_time - prev_time).total_seconds()
            
            if gap > gap_threshold:
                split_points.append(i)
        
        return split_points

    def _find_participant_change_points(self, messages, config):
        """Find points where participants change."""
        split_points = []
        
        current_participants = set()
        
        for i, message in enumerate(messages):
            role = message["role"]
            
            if role not in current_participants and current_participants:
                split_points.append(i)
            
            current_participants.add(role)
        
        return split_points

    def _evaluate_tagging_condition(self, message, condition):
        """Evaluate tagging condition for a message."""
        # Simple condition evaluation
        if condition["type"] == "content_contains":
            return condition["value"].lower() in message["content"].lower()
        elif condition["type"] == "role_equals":
            return message["role"] == condition["value"]
        elif condition["type"] == "tokens_greater_than":
            return message["tokens"] > condition["value"]
        
        return False

    def _evaluate_priority_condition(self, message, condition):
        """Evaluate priority condition for a message."""
        return self._evaluate_tagging_condition(message, condition)

    def _calculate_memory_usage(self):
        """Calculate current memory usage ratio."""
        total_conversations = len(self.conversations)
        return total_conversations / self.max_conversations

    def _sort_conversations_for_optimization(self):
        """Sort conversations by optimization priority."""
        # Sort by token count descending (optimize biggest first)
        conversations = list(self.conversations.items())
        conversations.sort(key=lambda x: x[1]["current_tokens"], reverse=True)
        return [conv_id for conv_id, _ in conversations]

    def _remove_low_priority_messages(self, conversation_id):
        """Remove low priority messages from conversation."""
        conversation = self.conversations[conversation_id]
        original_count = len(conversation["messages"])
        
        # Keep only normal and high priority messages
        conversation["messages"] = [
            msg for msg in conversation["messages"] 
            if msg.get("priority", "normal") in ["normal", "high"]
        ]
        
        # Recalculate tokens
        conversation["current_tokens"] = sum(msg["tokens"] for msg in conversation["messages"])
        
        return original_count - len(conversation["messages"])

    def _should_archive_conversation(self, conversation_id):
        """Check if conversation should be archived."""
        conversation = self.conversations[conversation_id]
        
        # Archive if old and low activity
        last_message_time = datetime.fromisoformat(conversation["updated_at"])
        time_since_update = datetime.now() - last_message_time
        
        return time_since_update.days > 30  # Archive after 30 days of inactivity

    def _archive_conversation(self, conversation_id):
        """Archive a conversation."""
        # In practice, this would move to external storage
        # For now, just mark as archived
        if conversation_id in self.conversation_metadata:
            self.conversation_metadata[conversation_id]["archived"] = True
            self.conversation_metadata[conversation_id]["archived_at"] = datetime.now().isoformat()

    def _create_keyword_index(self, messages):
        """Create keyword index for messages."""
        keyword_index = defaultdict(list)
        
        for i, message in enumerate(messages):
            words = message["content"].lower().split()
            for word in words:
                if len(word) > 3:  # Filter short words
                    keyword_index[word].append(i)
        
        return dict(keyword_index)

    def _create_semantic_index(self, messages):
        """Create semantic index for messages."""
        # Simplified semantic indexing
        # In practice, would use embeddings
        semantic_index = {}
        
        for i, message in enumerate(messages):
            # Simple semantic features
            content = message["content"].lower()
            features = {
                "length": len(content),
                "question": "?" in content,
                "exclamation": "!" in content,
                "contains_numbers": any(char.isdigit() for char in content)
            }
            semantic_index[i] = features
        
        return semantic_index

    def _calculate_semantic_similarity(self, query, content):
        """Calculate semantic similarity between query and content."""
        # Simplified similarity calculation
        # In practice, would use embeddings and cosine similarity
        
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)
        
        return len(intersection) / len(union) if union else 0

    def _validate_params(self, operation: str, params: Dict[str, Any]) -> None:
        """Validate operation parameters."""
        required_params = {
            ConversationMemoryOperation.CREATE_CONVERSATION: [],
            ConversationMemoryOperation.ADD_MESSAGE: ["conversation_id", "role", "content"],
            ConversationMemoryOperation.GET_CONVERSATION: ["conversation_id"],
            ConversationMemoryOperation.UPDATE_MESSAGE: ["conversation_id", "message_id", "updates"],
            ConversationMemoryOperation.DELETE_MESSAGE: ["conversation_id", "message_id"],
            ConversationMemoryOperation.CLEAR_CONVERSATION: ["conversation_id"],
            ConversationMemoryOperation.GET_RECENT_MESSAGES: ["conversation_id"],
            ConversationMemoryOperation.SEARCH_MESSAGES: ["query"],
            ConversationMemoryOperation.SUMMARIZE_CONVERSATION: ["conversation_id"],
            ConversationMemoryOperation.COMPRESS_MEMORY: ["conversation_id"],
            ConversationMemoryOperation.GET_CONTEXT_WINDOW: ["conversation_id"],
            ConversationMemoryOperation.MANAGE_TOKEN_LIMIT: ["conversation_id"],
            ConversationMemoryOperation.CREATE_MEMORY_SNAPSHOT: [],
            ConversationMemoryOperation.RESTORE_MEMORY_SNAPSHOT: ["snapshot_name"],
            ConversationMemoryOperation.ANALYZE_CONVERSATION: ["conversation_id"],
            ConversationMemoryOperation.EXTRACT_KEY_POINTS: ["conversation_id"],
            ConversationMemoryOperation.GET_CONVERSATION_STATS: [],
            ConversationMemoryOperation.MERGE_CONVERSATIONS: ["conversation_ids"],
            ConversationMemoryOperation.SPLIT_CONVERSATION: ["conversation_id", "split_criteria"],
            ConversationMemoryOperation.TAG_MESSAGES: ["conversation_id", "tagging_rules"],
            ConversationMemoryOperation.FILTER_BY_TAGS: ["conversation_id", "tags"],
            ConversationMemoryOperation.SET_MEMORY_PRIORITY: ["conversation_id", "priority_rules"],
            ConversationMemoryOperation.OPTIMIZE_MEMORY_USAGE: [],
            ConversationMemoryOperation.CREATE_MEMORY_INDEX: [],
            ConversationMemoryOperation.QUERY_SEMANTIC_MEMORY: ["query"],
        }

        if operation in required_params:
            for param in required_params[operation]:
                if param not in params:
                    raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="ConversationMemoryNode",
            description="Conversation memory management for LLM workflows",
            version="1.0.0",
            icon_path="🧠",
            auth_params=[],
            parameters=[
                NodeParameter(
                    name="conversation_id",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Unique identifier for the conversation"
                ),
                NodeParameter(
                    name="role",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Role of the message sender: user, assistant, system"
                ),
                NodeParameter(
                    name="content",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Content of the message"
                ),
                NodeParameter(
                    name="metadata",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Additional metadata for the conversation or message"
                ),
                NodeParameter(
                    name="token_limit",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Token limit for the conversation"
                ),
                NodeParameter(
                    name="message_id",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Unique identifier for a specific message"
                ),
                NodeParameter(
                    name="updates",
                    param_type=NodeParameterType.OBJECT,
                    required=False,
                    description="Updates to apply to a message"
                ),
                NodeParameter(
                    name="limit",
                    param_type=NodeParameterType.INTEGER,
                    required=False,
                    description="Maximum number of items to return"
                ),
                NodeParameter(
                    name="query",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Search query string"
                ),
                NodeParameter(
                    name="search_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of search: content, metadata, tags, all"
                ),
                NodeParameter(
                    name="summary_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of summary: overview, detailed, key_points"
                ),
                NodeParameter(
                    name="strategy",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Strategy for compression or context window"
                ),
                NodeParameter(
                    name="compression_ratio",
                    param_type=NodeParameterType.FLOAT,
                    required=False,
                    description="Ratio for memory compression (0.0-1.0)"
                ),
                NodeParameter(
                    name="snapshot_name",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Name for memory snapshot"
                ),
                NodeParameter(
                    name="analysis_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of conversation analysis"
                ),
                NodeParameter(
                    name="conversation_ids",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Array of conversation IDs for merging"
                ),
                NodeParameter(
                    name="split_criteria",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Criteria for splitting conversation"
                ),
                NodeParameter(
                    name="tagging_rules",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Rules for tagging messages"
                ),
                NodeParameter(
                    name="tags",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Tags to filter by"
                ),
                NodeParameter(
                    name="priority_rules",
                    param_type=NodeParameterType.ARRAY,
                    required=False,
                    description="Rules for setting message priority"
                ),
                NodeParameter(
                    name="index_type",
                    param_type=NodeParameterType.STRING,
                    required=False,
                    description="Type of index: keyword, semantic, combined"
                ),
                NodeParameter(
                    name="similarity_threshold",
                    param_type=NodeParameterType.FLOAT,
                    required=False,
                    description="Minimum similarity threshold for semantic search"
                )
            ]
        )