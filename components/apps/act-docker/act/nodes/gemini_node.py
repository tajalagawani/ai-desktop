# === File: act/nodes/gemini_node.py ===

import logging
import json
import os
import asyncio
import re
import base64
from typing import Dict, Any, Optional, List, Union, Callable

from .base_node import (
    BaseNode, NodeSchema, NodeParameter, NodeParameterType,
    NodeValidationError, NodeExecutionError
)

# --- Node Logger ---
logger = logging.getLogger(__name__)

# --- Optional global client for efficiency ---
_gemini_client = None

class GeminiNode(BaseNode):
    """
    Node for interacting with Google's Gemini models via the Google AI Studio API.
    Provides capabilities for generating text, analyzing images, and web search grounding
    using the Gemini models.
    """
    node_type = "gemini"

    def get_schema(self) -> NodeSchema:
        """Returns the schema definition for the GeminiNode."""
        return NodeSchema(
            node_type="gemini",
            version="1.0.0",
            description="Generates text and processes multimodal inputs using Google's Gemini models with optional web search grounding",
            parameters=[
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.SECRET,
                    description="Google AI Studio API key. If not provided, will use GEMINI_API_KEY environment variable.",
                    required=False,
                    default="${GEMINI_API_KEY}"
                ),
                NodeParameter(
                    name="model",
                    type=NodeParameterType.STRING,
                    description="Gemini model to use (e.g. 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.5-pro-preview-03-25')",
                    required=True,
                    default="gemini-1.5-pro"
                ),
                NodeParameter(
                    name="prompt",
                    type=NodeParameterType.STRING,
                    description="The text prompt to send to Gemini",
                    required=True
                ),
                NodeParameter(
                    name="temperature",
                    type=NodeParameterType.NUMBER,
                    description="Controls randomness. Lower values are more deterministic (range: 0.0 to 1.0)",
                    required=False,
                    default=0.7
                ),
                NodeParameter(
                    name="max_output_tokens",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of tokens to generate",
                    required=False,
                    default=None
                ),
                NodeParameter(
                    name="top_p",
                    type=NodeParameterType.NUMBER,
                    description="Nucleus sampling parameter (range: 0.0 to 1.0)",
                    required=False,
                    default=None
                ),
                NodeParameter(
                    name="top_k",
                    type=NodeParameterType.NUMBER,
                    description="Number of highest probability tokens to consider (range: 1 to 40)",
                    required=False,
                    default=None
                ),
                NodeParameter(
                    name="stream",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to stream the response",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="mime_type",
                    type=NodeParameterType.STRING,
                    description="Response mime type (e.g. 'text/plain', 'application/json')",
                    required=False,
                    default="text/plain"
                ),
                NodeParameter(
                    name="images",
                    type=NodeParameterType.ARRAY,
                    description="Optional array of image URLs or base64 encoded images to include with the prompt",
                    required=False,
                    default=None
                ),
                NodeParameter(
                    name="web_search_grounding",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable web search grounding to get current information from the web",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="search_dynamic_retrieval_threshold",
                    type=NodeParameterType.NUMBER,
                    description="Threshold for dynamic retrieval (0.0 to 1.0). Higher values make the model more likely to use web search",
                    required=False,
                    default=0.5
                )
            ],
            outputs={
                "result_text": NodeParameterType.STRING,
                "finish_reason": NodeParameterType.STRING,
                "usage": NodeParameterType.OBJECT,
                "full_response": NodeParameterType.OBJECT,
                "grounding_metadata": NodeParameterType.OBJECT,
                "search_results": NodeParameterType.ARRAY
            },
            tags=["ai", "nlp", "text generation", "chat", "multimodal", "google", "gemini", "web search", "grounding"],
            author="ACT Framework"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the Gemini operation with the provided data."""
        node_name = node_data.get('__node_name', 'GeminiNode')
        logger.debug(f"Executing GeminiNode: {node_name}")

        try:
            # Extract parameters
            params = node_data.get("params", {})
            
            # Get required parameters
            model = params.get("model", "gemini-1.5-pro")
            prompt = params.get("prompt")
            if not prompt:
                raise NodeValidationError("No prompt provided. The 'prompt' parameter is required.")
            
            # ONLY ADD THIS MINIMAL DEBUG CODE:
            print(f"\n🔍 GEMINI DEBUG - {node_name}")
            print("="*50)
            print(f"📝 PROMPT (first 200 chars): {prompt[:200]}...")
            
            # Check for unresolved placeholders
            if '{{' in prompt and '}}' in prompt:
                unresolved = re.findall(r'\{\{([^}]+)\}\}', prompt)
                print(f"🚨 UNRESOLVED PLACEHOLDERS: {unresolved}")
                print("="*50)
                
                # Return error if placeholders found
                return {
                    "status": "error",
                    "message": f"Prompt contains unresolved placeholders: {unresolved}",
                    "result": {
                        "result_text": "",
                        "finish_reason": "error",
                        "usage": {},
                        "full_response": None,
                        "grounding_metadata": None,
                        "search_results": []
                    }
                }
            else:
                print("✅ No unresolved placeholders found")
                print("="*50)
            
            # Try to import Google Gemini library
            try:
                from google import genai
                from google.genai import types
            except ImportError:
                raise NodeExecutionError("Required package 'google-generativeai' is not installed. Install with 'pip install google-generativeai'")
            
            # Get API key (prioritize parameter, then environment variable)
            api_key = params.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise NodeValidationError("No API key provided. Either set the 'api_key' parameter or GEMINI_API_KEY environment variable.")
            
            # Get optional parameters
            temperature = params.get("temperature")
            max_output_tokens = params.get("max_output_tokens")
            top_p = params.get("top_p")
            top_k = params.get("top_k")
            stream = params.get("stream", False)
            mime_type = params.get("mime_type", "text/plain")
            images = params.get("images", [])
            web_search_grounding = params.get("web_search_grounding", False)
            search_dynamic_retrieval_threshold = params.get("search_dynamic_retrieval_threshold", 0.5)
            
            # IMPORTANT: Check compatibility between web search grounding and mime type
            if web_search_grounding and mime_type != "text/plain":
                logger.warning(f"{node_name} - Web search grounding is not compatible with mime_type '{mime_type}'. Disabling grounding and using text/plain.")
                web_search_grounding = False
                mime_type = "text/plain"
                print(f"⚠️  WEB GROUNDING COMPATIBILITY: Disabled grounding due to mime_type '{params.get('mime_type')}'. Using text/plain instead.")
            
            # Create client
            global _gemini_client
            if _gemini_client is None:
                _gemini_client = genai.Client(api_key=api_key)
            client = _gemini_client
            
            # Set up the contents for the request
            user_parts = []
            
            # Add text prompt
            user_parts.append(types.Part.from_text(text=prompt))
            
            # Add images if provided
            for image in images:
                if image.startswith("http"):
                    # If it's a URL
                    user_parts.append(types.Part.from_uri(uri=image, mime_type="image/jpeg"))
                elif image.startswith("data:"):
                    # If it's a data URI
                    parts = image.split(";base64,")
                    if len(parts) == 2:
                        mime = parts[0].replace("data:", "")
                        data = parts[1]
                        user_parts.append(types.Part.from_data(data=base64.b64decode(data), mime_type=mime))
                else:
                    # Assume it's base64
                    try:
                        user_parts.append(types.Part.from_data(data=base64.b64decode(image), mime_type="image/jpeg"))
                    except:
                        logger.warning(f"Unable to decode image data: {image[:30]}...")
            
            # Create content object with user parts
            contents = [
                types.Content(
                    role="user",
                    parts=user_parts
                )
            ]
            
            # Create generate content config
            generate_content_config = types.GenerateContentConfig(
                response_mime_type=mime_type,
            )
            
            # Add temperature if provided
            if temperature is not None:
                generate_content_config.temperature = float(temperature)
                
            # Add max_output_tokens if provided  
            if max_output_tokens is not None:
                generate_content_config.max_output_tokens = int(max_output_tokens)
                
            # Add top_p if provided
            if top_p is not None:
                generate_content_config.top_p = float(top_p)
                
            # Add top_k if provided
            if top_k is not None:
                generate_content_config.top_k = int(top_k)
            
            # Configure tools for web search grounding
            if web_search_grounding:
                try:
                    # Add Google Search tool - simplified approach
                    google_search_tool = types.Tool(
                        google_search=types.GoogleSearch()
                    )
                    generate_content_config.tools = [google_search_tool]
                    
                    # Try to set dynamic retrieval threshold if supported
                    try:
                        if hasattr(types, 'SearchConfig'):
                            generate_content_config.search_config = types.SearchConfig(
                                dynamic_retrieval_threshold=float(search_dynamic_retrieval_threshold)
                            )
                    except Exception as search_config_error:
                        logger.debug(f"SearchConfig not available or failed: {search_config_error}")
                        
                except Exception as tool_error:
                    logger.warning(f"Failed to configure web search grounding: {tool_error}")
                    # Continue without grounding if it fails
                    web_search_grounding = False
            
            logger.info(f"{node_name} - Executing Gemini with model '{model}', temperature={temperature}, max_tokens={max_output_tokens or 'default'}, web_search_grounding={web_search_grounding}, mime_type='{mime_type}'")
            
            # Handle streaming vs non-streaming
            try:
                if stream:
                    # Use run_in_executor to make synchronous API call asynchronous
                    def generate_stream():
                        result_text = ""
                        for chunk in client.models.generate_content_stream(
                            model=model,
                            contents=contents,
                            config=generate_content_config,
                        ):
                            if chunk.text:
                                result_text += chunk.text
                        return result_text
                    
                    # Execute the stream processing
                    result_text = await asyncio.to_thread(generate_stream)
                    full_response = None
                    grounding_metadata = None
                    search_results = []
                    
                else:
                    # Synchronous response, made async
                    def generate_content():
                        response = client.models.generate_content(
                            model=model,
                            contents=contents,
                            config=generate_content_config,
                        )
                        return response
                    
                    # Execute the content generation
                    response = await asyncio.to_thread(generate_content)
                    result_text = response.text
                    full_response = response
                    
                    # Extract grounding metadata if available
                    grounding_metadata = None
                    search_results = []
                    
                    if web_search_grounding and hasattr(response, 'candidates') and response.candidates:
                        try:
                            candidate = response.candidates[0]
                            
                            # Extract grounding metadata
                            if hasattr(candidate, 'grounding_metadata'):
                                grounding_metadata = candidate.grounding_metadata
                                
                                # Extract search results from grounding metadata
                                if hasattr(grounding_metadata, 'search_entry_point') and grounding_metadata.search_entry_point:
                                    search_results = []
                                    if hasattr(grounding_metadata.search_entry_point, 'rendered_content'):
                                        search_results.append({
                                            "type": "search_entry_point",
                                            "content": grounding_metadata.search_entry_point.rendered_content
                                        })
                                
                                # Extract web search results
                                if hasattr(grounding_metadata, 'web_search_queries'):
                                    for query in grounding_metadata.web_search_queries:
                                        search_results.append({
                                            "type": "search_query",
                                            "query": query
                                        })
                                
                                # Extract grounding supports (citations)
                                if hasattr(grounding_metadata, 'grounding_supports'):
                                    for support in grounding_metadata.grounding_supports:
                                        if hasattr(support, 'segment'):
                                            search_results.append({
                                                "type": "grounding_support",
                                                "segment": {
                                                    "start_index": support.segment.start_index if hasattr(support.segment, 'start_index') else None,
                                                    "end_index": support.segment.end_index if hasattr(support.segment, 'end_index') else None,
                                                    "text": support.segment.text if hasattr(support.segment, 'text') else None
                                                },
                                                "grounding_chunk_indices": support.grounding_chunk_indices if hasattr(support, 'grounding_chunk_indices') else [],
                                                "confidence_scores": support.confidence_scores if hasattr(support, 'confidence_scores') else []
                                            })
                        except Exception as grounding_extract_error:
                            logger.debug(f"Failed to extract grounding metadata: {grounding_extract_error}")
                            grounding_metadata = None
                            search_results = []
                
                # Post-process the result if JSON was requested but we used text/plain due to grounding
                if params.get("mime_type") == "application/json" and mime_type == "text/plain" and web_search_grounding:
                    # Try to extract JSON from the text response
                    try:
                        # Look for JSON content in the response
                        json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                        if json_match:
                            json_text = json_match.group(0)
                            # Validate it's proper JSON
                            json.loads(json_text)
                            result_text = json_text
                            logger.info(f"{node_name} - Successfully extracted JSON from grounded text response")
                    except Exception as json_extract_error:
                        logger.warning(f"{node_name} - Could not extract valid JSON from grounded response: {json_extract_error}")
                        # Keep the original text response
                
                logger.info(f"{node_name} - Successfully generated content with Gemini. Result length: {len(result_text)} chars, Grounding enabled: {web_search_grounding}")
                
                return {
                    "status": "success",
                    "message": "Gemini operation completed successfully.",
                    "result": {
                        "result_text": result_text,
                        "finish_reason": "stop",  # Gemini doesn't expose this directly
                        "usage": {},  # Gemini doesn't expose token usage like OpenAI
                        "full_response": full_response if not stream else None,
                        "grounding_metadata": grounding_metadata,
                        "search_results": search_results
                    }
                }
                
            except Exception as e:
                error_msg = f"Error during Gemini API call: {str(e)}"
                logger.error(f"{node_name} - {error_msg}")
                return self.handle_error(e, context=f"{node_name} API Call")
            
        except Exception as e:
            logger.error(f"Error in {node_name}: {str(e)}", exc_info=True)
            return self.handle_error(e, context=node_name)