#!/usr/bin/env python3
"""
OpenAI Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from  base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class OpenAINode(BaseNode):
    """
    Pure config-driven OpenAI node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    """
    
    # Embedded configuration for OpenAI API
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "openai",
            "display_name": "OpenAI",
            "description": "Comprehensive OpenAI API integration for chat completions, embeddings, images, audio, fine-tuning, assistants, and more",
            "category": "ai",
            "vendor": "openai",
            "version": "1.0.0",
            "author": "ACT Workflow",
            "tags": ["ai", "llm", "openai", "gpt", "embeddings", "images", "audio"],
            "documentation_url": "https://platform.openai.com/docs",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/openai.svg",
            "color": "#412991",
            "created_at": "2025-08-22T16:00:00Z",
            "updated_at": "2025-08-22T16:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.openai.com/v1",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential",
                "retriable_codes": [429, 500, 502, 503, 504]
            },
            "rate_limiting": {
                "requests_per_second": 60,
                "burst_size": 10
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        },
        
        # All parameters with complete metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "OpenAI API key",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^sk-[a-zA-Z0-9-_]+$",
                    "minLength": 10
                }
            },
            "operation": {
                "type": "string",
                "description": "The OpenAI operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["chat_completion", "create_embedding", "generate_image", "transcribe_audio", "list_models"]
            },
            "model": {
                "type": "string",
                "description": "OpenAI model to use",
                "required": False,
                "default": "gpt-4",
                "group": "Model",
                "examples": ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002", "dall-e-3", "whisper-1"],
                "validation": {
                    "enum": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large", "dall-e-2", "dall-e-3", "whisper-1"]
                }
            },
            "messages": {
                "type": "array",
                "description": "Array of message objects for chat completion",
                "required": False,
                "group": "Chat",
                "examples": [[{"role": "user", "content": "Hello, how are you?"}]],
                "validation": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["system", "user", "assistant"]},
                            "content": {"type": "string"}
                        }
                    }
                }
            },
            "prompt": {
                "type": "string",
                "description": "Text prompt for various operations",
                "required": False,
                "group": "Content",
                "examples": ["Write a short story about AI", "Generate an image of a sunset"]
            },
            "input": {
                "type": "string",
                "description": "Text input for embeddings or other operations",
                "required": False,
                "group": "Content",
                "examples": ["This is a sample text for embedding"]
            },
            "temperature": {
                "type": "number",
                "description": "Controls randomness in the output. Higher values make output more random",
                "required": False,
                "default": 1.0,
                "group": "Generation",
                "validation": {
                    "minimum": 0,
                    "maximum": 2
                },
                "examples": [0.1, 0.7, 1.0, 1.5]
            },
            "max_tokens": {
                "type": "number",
                "description": "Maximum number of tokens to generate",
                "required": False,
                "group": "Generation",
                "validation": {
                    "minimum": 1,
                    "maximum": 8192
                },
                "examples": [100, 500, 1000, 2000]
            },
            "top_p": {
                "type": "number",
                "description": "Nucleus sampling parameter",
                "required": False,
                "default": 1.0,
                "group": "Generation",
                "validation": {
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "frequency_penalty": {
                "type": "number",
                "description": "Penalty for token frequency",
                "required": False,
                "default": 0,
                "group": "Generation",
                "validation": {
                    "minimum": -2.0,
                    "maximum": 2.0
                }
            },
            "presence_penalty": {
                "type": "number",
                "description": "Penalty for token presence",
                "required": False,
                "default": 0,
                "group": "Generation",
                "validation": {
                    "minimum": -2.0,
                    "maximum": 2.0
                }
            },
            "size": {
                "type": "string",
                "description": "Size of generated image",
                "required": False,
                "default": "1024x1024",
                "group": "Image",
                "validation": {
                    "enum": ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
                }
            },
            "quality": {
                "type": "string",
                "description": "Quality of generated image",
                "required": False,
                "default": "standard",
                "group": "Image",
                "validation": {
                    "enum": ["standard", "hd"]
                }
            },
            "style": {
                "type": "string",
                "description": "Style of generated image",
                "required": False,
                "default": "vivid",
                "group": "Image",
                "validation": {
                    "enum": ["vivid", "natural"]
                }
            },
            "n": {
                "type": "number",
                "description": "Number of results to generate",
                "required": False,
                "default": 1,
                "group": "Generation",
                "validation": {
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "file": {
                "type": "string",
                "description": "Audio file for transcription (base64 or file path)",
                "required": False,
                "group": "Audio"
            },
            "language": {
                "type": "string",
                "description": "Language of the audio (ISO-639-1 format)",
                "required": False,
                "group": "Audio",
                "examples": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
            },
            "response_format": {
                "type": "string",
                "description": "Format of the transcription response",
                "required": False,
                "default": "json",
                "group": "Audio",
                "validation": {
                    "enum": ["json", "text", "srt", "verbose_json", "vtt"]
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful OpenAI API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "content": {"type": "string", "description": "Generated text content"},
                    "usage": {"type": "object", "description": "Token usage information"},
                    "result": {"type": "object", "description": "Full API response data"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Error code"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "chat_completion": {
                "required_env_keys": ["OPENAI_API_KEY"],
                "optional_env_keys": ["OPENAI_ORG_ID", "OPENAI_PROJECT_ID"]
            },
            "create_embedding": {
                "required_env_keys": ["OPENAI_API_KEY"],
                "optional_env_keys": ["OPENAI_ORG_ID", "OPENAI_PROJECT_ID"]
            },
            "generate_image": {
                "required_env_keys": ["OPENAI_API_KEY"],
                "optional_env_keys": ["OPENAI_ORG_ID", "OPENAI_PROJECT_ID"]
            },
            "transcribe_audio": {
                "required_env_keys": ["OPENAI_API_KEY"],
                "optional_env_keys": ["OPENAI_ORG_ID", "OPENAI_PROJECT_ID"]
            },
            "list_models": {
                "required_env_keys": ["OPENAI_API_KEY"],
                "optional_env_keys": ["OPENAI_ORG_ID", "OPENAI_PROJECT_ID"]
            }
        },
        
        # Error codes specific to OpenAI
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API key",
            "403": "Forbidden - Request not allowed",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded or quota exceeded", 
            "500": "Internal Server Error - OpenAI server error",
            "502": "Bad Gateway - OpenAI server temporarily unavailable",
            "503": "Service Unavailable - OpenAI server overloaded"
        }
    }
    
    # Operation definitions with complete metadata
    OPERATIONS = {
        "chat_completion": {
            "method": "POST",
            "endpoint": "/chat/completions",
            "required_params": ["model", "messages"],
            "optional_params": ["temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty", "n"],
            "body_parameters": ["model", "messages", "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty", "n"],
            "display_name": "Chat Completion",
            "description": "Generate conversational responses using OpenAI's chat models",
            "group": "Chat",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Simple chat",
                    "input": {
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": "Hello!"}]
                    }
                }
            ]
        },
        "create_embedding": {
            "method": "POST", 
            "endpoint": "/embeddings",
            "required_params": ["model", "input"],
            "optional_params": [],
            "body_parameters": ["model", "input"],
            "display_name": "Create Embedding",
            "description": "Convert text into numerical embeddings for similarity search and ML",
            "group": "Embeddings",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "array",
            "examples": [
                {
                    "name": "Text embedding",
                    "input": {
                        "model": "text-embedding-3-small",
                        "input": "This is sample text for embedding"
                    }
                }
            ]
        },
        "generate_image": {
            "method": "POST",
            "endpoint": "/images/generations", 
            "required_params": ["prompt"],
            "optional_params": ["model", "size", "quality", "style", "n"],
            "body_parameters": ["prompt", "model", "size", "quality", "style", "n"],
            "display_name": "Generate Image",
            "description": "Generate images from text descriptions using DALL-E",
            "group": "Images",
            "rate_limit_cost": 5,
            "cache_ttl": 0,
            "response_type": "array",
            "examples": [
                {
                    "name": "Simple image generation",
                    "input": {
                        "prompt": "A sunset over the ocean",
                        "model": "dall-e-3",
                        "size": "1024x1024"
                    }
                }
            ]
        },
        "transcribe_audio": {
            "method": "POST",
            "endpoint": "/audio/transcriptions",
            "required_params": ["file", "model"],
            "optional_params": ["language", "response_format"],
            "body_parameters": ["file", "model", "language", "response_format"],
            "display_name": "Transcribe Audio",
            "description": "Convert audio files to text using Whisper",
            "group": "Audio",
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Audio transcription",
                    "input": {
                        "file": "audio.mp3",
                        "model": "whisper-1",
                        "response_format": "json"
                    }
                }
            ]
        },
        "list_models": {
            "method": "GET",
            "endpoint": "/models",
            "required_params": [],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "List Models",
            "description": "Retrieve list of available OpenAI models",
            "group": "Models",
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "array",
            "examples": [
                {
                    "name": "List all models",
                    "input": {}
                }
            ]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with full config and operations
        # UniversalRequestNode expects the full config dict, not just api_config
        self.universal_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
    
    def get_schema(self) -> NodeSchema:
        """Return basic schema."""
        return NodeSchema(
            node_type="openai",
            version="1.0.0", 
            description="OpenAI API integration with embedded configuration",
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
                    description="OpenAI API key",
                    required=True
                ),
                # Dynamic parameters based on operation
                NodeParameter(
                    name="model",
                    type=NodeParameterType.STRING,
                    description="OpenAI model to use",
                    required=False,
                    default="gpt-3.5-turbo"
                ),
                NodeParameter(
                    name="messages",
                    type=NodeParameterType.ARRAY,
                    description="Messages for chat completion",
                    required=False
                ),
                NodeParameter(
                    name="prompt",
                    type=NodeParameterType.STRING,
                    description="Text prompt",
                    required=False
                ),
                NodeParameter(
                    name="input",
                    type=NodeParameterType.STRING,
                    description="Text input for embeddings",
                    required=False
                ),
                NodeParameter(
                    name="temperature",
                    type=NodeParameterType.NUMBER,
                    description="Temperature (0.0-2.0)",
                    required=False,
                    default=0.7
                ),
                NodeParameter(
                    name="max_tokens",
                    type=NodeParameterType.NUMBER,
                    description="Max tokens in response",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "content": NodeParameterType.STRING,
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
            
            # Prepare request data based on operation
            request_data = self._prepare_request_data(operation, params)
            
            # Prepare parameters for UniversalRequestNode
            # The UniversalRequestNode expects all parameters in the params dict
            universal_params = {
                "operation": operation,
                "api_key": params.get("api_key"),
                **request_data  # Merge in the prepared request data
            }
            
            # Create node_data for UniversalRequestNode
            universal_node_data = {
                "params": universal_params
            }
            
            # Execute via UniversalRequestNode
            result = await self.universal_node.execute(universal_node_data)
            
            # Process and enhance the result
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"OpenAI node error: {str(e)}")
            return {
                "status": "error", 
                "error": str(e),
                "result": None
            }
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation."""
        data = {}
        
        if operation == "chat_completion":
            # Build messages array
            messages = params.get("messages", [])
            if not messages and params.get("prompt"):
                messages = [{"role": "user", "content": params.get("prompt")}]
            
            data = {
                "model": params.get("model", "gpt-3.5-turbo"),
                "messages": messages
            }
            
            # Add optional parameters
            if params.get("temperature"):
                data["temperature"] = params.get("temperature")
            if params.get("max_tokens"):
                data["max_tokens"] = params.get("max_tokens")
            
        elif operation == "create_embedding":
            data = {
                "model": params.get("model", "text-embedding-ada-002"),
                "input": params.get("input")
            }
            
        elif operation == "generate_image":
            data = {
                "prompt": params.get("prompt"),
                "model": params.get("model", "dall-e-3"),
                "size": params.get("size", "1024x1024"),
                "n": params.get("n", 1)
            }
            
        elif operation == "transcribe_audio":
            data = {
                "file": params.get("file"),
                "model": params.get("model", "whisper-1")
            }
        
        # For list_models, no data needed
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process result based on operation type."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("data", {})
        
        # Extract operation-specific data
        if operation == "chat_completion":
            choices = response_data.get("choices", [])
            if choices:
                choice = choices[0]
                message = choice.get("message", {})
                result.update({
                    "content": message.get("content", ""),
                    "usage": response_data.get("usage", {})
                })
        
        elif operation == "create_embedding":
            data = response_data.get("data", [])
            if data:
                result.update({
                    "embedding": data[0].get("embedding", []),
                    "usage": response_data.get("usage", {})
                })
        
        elif operation == "generate_image":
            data = response_data.get("data", [])
            result.update({
                "images": data
            })
        
        elif operation == "transcribe_audio":
            result.update({
                "text": response_data.get("text", "")
            })
        
        elif operation == "list_models":
            result.update({
                "models": response_data.get("data", [])
            })
        
        return result
    
    async def close(self):
        """Clean up resources."""
        # UniversalRequestNode doesn't have a close method
        # It uses session per request, so no cleanup needed
        pass

# That's it! Everything is embedded in the node:
# 1. CONFIG defines the API connection settings
# 2. OPERATIONS defines the available operations 
# 3. UniversalRequestNode handles all HTTP complexity
# 4. Node just maps operations to HTTP requests

if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = OpenAINode()
        
        # Test chat completion
        test_data = {
            "params": {
                "operation": "list_models",
                "api_key": "your-openai-api-key-here",  # Replace with actual API key
              
          
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    asyncio.run(test())