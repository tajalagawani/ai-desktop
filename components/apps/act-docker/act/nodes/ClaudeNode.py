#!/usr/bin/env python3
"""
Claude Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
Combines all operations from both AnthropicNode.py and ClaudeNode.py
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class ClaudeNode(BaseNode):
    """
    Pure config-driven Claude node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    Combines all operations from Anthropic and Claude APIs.
    """
    
    # Embedded configuration for Claude/Anthropic API
    CONFIG = {
        "base_url": "https://api.anthropic.com/v1",
        "authentication": {
            "type": "api_key",
            "header": "x-api-key"
        },
        "default_headers": {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        },
        "retry_config": {
            "max_attempts": 3,
            "backoff": "exponential",
            "retriable_codes": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 10,  # Conservative rate limit for Anthropic
            "burst_size": 5
        },
        "timeouts": {
            "connect": 10.0,
            "read": 60.0,  # Longer read timeout for Claude responses
            "total": 120.0
        }
    }
    
    # Operation definitions - combining all operations from both files
    OPERATIONS = {
        # Core Claude API operations
        "messages": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "messages"]
        },
        "completion": {
            "method": "POST", 
            "endpoint": "/complete",
            "required_params": ["model", "prompt", "max_tokens_to_sample"]
        },
        
        # Text generation and processing
        "generate_text": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "complete_text": {
            "method": "POST",
            "endpoint": "/messages", 
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "summarize_text": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        
        # Analysis operations
        "analyze_text": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "sentiment_analysis": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "classify_text": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "extract_entities": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        
        # Code operations  
        "generate_code": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "review_code": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "explain_code": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        
        # Creative operations
        "creative_writing": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "brainstorm_ideas": {
            "method": "POST",
            "endpoint": "/messages", 
            "required_params": ["model", "max_tokens", "prompt"]
        },
        
        # Q&A and document operations
        "answer_questions": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        "process_document": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "prompt"]
        },
        
        # Streaming operations
        "stream_message": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "messages"]
        },
        "continue_conversation": {
            "method": "POST",
            "endpoint": "/messages",
            "required_params": ["model", "max_tokens", "messages"]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with embedded config
        self.universal_node = UniversalRequestNode(self.CONFIG)
    
    def get_schema(self) -> NodeSchema:
        """Return basic schema."""
        return NodeSchema(
            node_type="claude",
            version="1.0.0", 
            description="Claude/Anthropic API integration with embedded configuration",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="api_key", 
                    type=NodeParameterType.SECRET,
                    description="Anthropic API key",
                    required=True
                ),
                
                # Model parameters
                NodeParameter(
                    name="model",
                    type=NodeParameterType.STRING,
                    description="Claude model to use",
                    required=False,
                    default="claude-3-sonnet-20240229",
                    enum=[
                        "claude-3-opus-20240229",
                        "claude-3-sonnet-20240229", 
                        "claude-3-haiku-20240307",
                        "claude-3-5-sonnet-20240620",
                        "claude-3-5-haiku-20240620",
                        "claude-2.1",
                        "claude-2.0",
                        "claude-instant-1.2"
                    ]
                ),
                
                # Content parameters
                NodeParameter(
                    name="messages",
                    type=NodeParameterType.ARRAY,
                    description="Messages for conversation",
                    required=False
                ),
                NodeParameter(
                    name="prompt",
                    type=NodeParameterType.STRING,
                    description="Text prompt",
                    required=False
                ),
                NodeParameter(
                    name="system_prompt",
                    type=NodeParameterType.STRING,
                    description="System prompt to set behavior",
                    required=False
                ),
                
                # Generation parameters
                NodeParameter(
                    name="max_tokens",
                    type=NodeParameterType.NUMBER,
                    description="Max tokens in response",
                    required=False,
                    default=1000
                ),
                NodeParameter(
                    name="max_tokens_to_sample",
                    type=NodeParameterType.NUMBER,
                    description="Max tokens to sample (legacy completion)",
                    required=False,
                    default=1000
                ),
                NodeParameter(
                    name="temperature",
                    type=NodeParameterType.NUMBER,
                    description="Temperature (0.0-1.0)",
                    required=False,
                    default=0.7
                ),
                NodeParameter(
                    name="top_p",
                    type=NodeParameterType.NUMBER,
                    description="Top-p sampling parameter",
                    required=False,
                    default=1.0
                ),
                NodeParameter(
                    name="top_k",
                    type=NodeParameterType.NUMBER,
                    description="Top-k sampling parameter",
                    required=False
                ),
                
                # Control parameters
                NodeParameter(
                    name="stop_sequences",
                    type=NodeParameterType.ARRAY,
                    description="Sequences where generation should stop",
                    required=False
                ),
                NodeParameter(
                    name="stream",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable streaming response",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="metadata",
                    type=NodeParameterType.OBJECT,
                    description="Metadata for the request",
                    required=False
                ),
                
                # Tool parameters
                NodeParameter(
                    name="tools",
                    type=NodeParameterType.ARRAY,
                    description="Tools Claude may call",
                    required=False
                ),
                NodeParameter(
                    name="tool_choice",
                    type=NodeParameterType.ANY,
                    description="Controls tool usage",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "content": NodeParameterType.STRING,
                "message": NodeParameterType.OBJECT,
                "conversation": NodeParameterType.ARRAY,
                "analysis_result": NodeParameterType.OBJECT,
                "generated_code": NodeParameterType.STRING,
                "summary": NodeParameterType.STRING,
                "entities": NodeParameterType.ARRAY,
                "sentiment": NodeParameterType.OBJECT,
                "classification": NodeParameterType.OBJECT,
                "ideas": NodeParameterType.ARRAY,
                "answer": NodeParameterType.STRING,
                "usage": NodeParameterType.OBJECT
            }
        )
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute operation using UniversalRequestNode.
        """
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "result": None
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "result": None
                }
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Prepare request data based on operation
            request_data = self._prepare_request_data(operation, params)
            
            # Make request using UniversalRequestNode
            # Pass all parameters including api_key for universal node to access
            request_kwargs = {
                "api_key": params.get("api_key"),  # Claude uses x-api-key header
                **params  # Pass all original parameters
            }
            
            result = await self.universal_node.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if op_config["method"] in ["POST", "PUT", "PATCH"] else None,
                params=request_data if op_config["method"] == "GET" else None,
                **request_kwargs
            )
            
            # Process result
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"Claude node error: {str(e)}")
            return {
                "status": "error", 
                "error": str(e),
                "result": None
            }
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation."""
        data = {}
        
        # Get model and tokens
        model = params.get("model", "claude-3-sonnet-20240229")
        max_tokens = params.get("max_tokens", 1000)
        max_tokens_to_sample = params.get("max_tokens_to_sample", max_tokens)
        
        # Core message operations
        if operation == "messages":
            messages = params.get("messages", [])
            if not messages and params.get("prompt"):
                messages = [{"role": "user", "content": params.get("prompt")}]
            
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "completion":
            data = {
                "model": model,
                "prompt": params.get("prompt"),
                "max_tokens_to_sample": max_tokens_to_sample
            }
            
        # Text generation operations
        elif operation == "generate_text":
            prompt = f"Generate text based on this prompt: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "complete_text":
            prompt = f"Complete the following text: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "summarize_text":
            prompt = f"Please provide a concise summary of the following text: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        # Analysis operations
        elif operation == "analyze_text":
            prompt = f"Please analyze the following text and provide insights: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "sentiment_analysis":
            prompt = f"Please analyze the sentiment of the following text and return your analysis in JSON format: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "classify_text":
            text = params.get("prompt", "")
            categories = params.get("categories", [])
            if categories:
                prompt = f"Please classify the following text into one of these categories {categories}: {text}"
            else:
                prompt = f"Please classify the following text and return the classification in JSON format: {text}"
            
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "extract_entities":
            prompt = f"Please extract entities from the following text and return them in JSON format: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        # Code operations
        elif operation == "generate_code":
            prompt = f"Please generate code for the following request: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "review_code":
            prompt = f"Please review the following code and provide feedback: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "explain_code":
            prompt = f"Please explain the following code: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        # Creative operations
        elif operation == "creative_writing":
            prompt = f"Please help with creative writing for: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "brainstorm_ideas":
            prompt = f"Please brainstorm ideas for: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        # Q&A and document operations
        elif operation == "answer_questions":
            prompt = f"Please answer this question: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        elif operation == "process_document":
            prompt = f"Please process and analyze the following document: {params.get('prompt', '')}"
            messages = [{"role": "user", "content": prompt}]
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
        # Streaming operations
        elif operation in ["stream_message", "continue_conversation"]:
            messages = params.get("messages", [])
            if not messages and params.get("prompt"):
                messages = [{"role": "user", "content": params.get("prompt")}]
            
            data = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
                "stream": True
            }
        
        # Add optional parameters
        if params.get("temperature"):
            data["temperature"] = params.get("temperature")
        if params.get("top_p"):
            data["top_p"] = params.get("top_p")
        if params.get("top_k"):
            data["top_k"] = params.get("top_k")
        if params.get("stop_sequences"):
            data["stop_sequences"] = params.get("stop_sequences")
        if params.get("system_prompt"):
            data["system"] = params.get("system_prompt")
        if params.get("metadata"):
            data["metadata"] = params.get("metadata")
        if params.get("tools"):
            data["tools"] = params.get("tools")
        if params.get("tool_choice"):
            data["tool_choice"] = params.get("tool_choice")
        if params.get("stream"):
            data["stream"] = params.get("stream")
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process result based on operation type."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("data", {})
        
        # Extract content from Claude response format
        content = ""
        if response_data.get("content") and len(response_data["content"]) > 0:
            if isinstance(response_data["content"][0], dict):
                content = response_data["content"][0].get("text", "")
            else:
                content = str(response_data["content"][0])
        
        # Add common fields
        result["content"] = content
        result["message"] = response_data
        result["usage"] = response_data.get("usage", {})
        
        # Add operation-specific processing
        if operation in ["sentiment_analysis", "classify_text", "extract_entities"]:
            # Try to extract JSON from response
            try:
                import json
                if "{" in content and "}" in content:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                    parsed_data = json.loads(json_str)
                    
                    if operation == "sentiment_analysis":
                        result["sentiment"] = parsed_data
                    elif operation == "classify_text":
                        result["classification"] = parsed_data
                    elif operation == "extract_entities":
                        result["entities"] = parsed_data
                else:
                    # Fallback to plain text
                    if operation == "sentiment_analysis":
                        result["sentiment"] = {"analysis": content}
                    elif operation == "classify_text":
                        result["classification"] = {"category": content}
                    elif operation == "extract_entities":
                        result["entities"] = [content]
            except:
                # Fallback processing
                if operation == "sentiment_analysis":
                    result["sentiment"] = {"analysis": content}
                elif operation == "classify_text":
                    result["classification"] = {"category": content}
                elif operation == "extract_entities":
                    result["entities"] = [content]
        
        elif operation == "generate_code":
            result["generated_code"] = content
            
        elif operation == "summarize_text":
            result["summary"] = content
            
        elif operation == "answer_questions":
            result["answer"] = content
            
        elif operation == "brainstorm_ideas":
            # Try to split into list if content has bullet points or numbered items
            ideas = []
            if "•" in content or "-" in content or "\n" in content:
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith("•") or line.startswith("-") or line[0].isdigit()):
                        ideas.append(line)
            if not ideas:
                ideas = [content]
            result["ideas"] = ideas
            
        elif operation == "analyze_text":
            result["analysis_result"] = {"analysis": content}
        
        return result
    
    async def close(self):
        """Clean up resources."""
        if self.universal_node:
            await self.universal_node.close()


if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = ClaudeNode()
        
        # Test message creation
        test_data = {
            "params": {
                "operation": "messages",
                "api_key": "your-anthropic-api-key-here",  # Replace with actual API key
                "model": "claude-3-haiku-20240307",
                "prompt": "Hello! Please respond with a brief greeting.",
                "max_tokens": 100
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    asyncio.run(test())