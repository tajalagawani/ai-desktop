"""
Hugging Face Node - Comprehensive integration with Hugging Face Inference API
Provides access to all Hugging Face API operations including model inference, text generation, classification, and dataset management.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from urllib.parse import urlencode

# Import HTTP client for API calls
import aiohttp
import certifi

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class HuggingFaceOperation:
    """Operations available on Hugging Face Inference API."""
    
    # Text Generation
    TEXT_GENERATION = "text_generation"
    TEXT_COMPLETION = "text_completion"
    
    # Classification
    TEXT_CLASSIFICATION = "text_classification"
    TOKEN_CLASSIFICATION = "token_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    
    # Translation and Language
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    
    # Image Operations
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    IMAGE_SEGMENTATION = "image_segmentation"
    
    # Audio Operations
    SPEECH_RECOGNITION = "speech_recognition"
    TEXT_TO_SPEECH = "text_to_speech"
    
    # Model Operations
    GET_MODEL_INFO = "get_model_info"
    LIST_MODELS = "list_models"
    
    # Dataset Operations
    GET_DATASET_INFO = "get_dataset_info"
    LIST_DATASETS = "list_datasets"

class HuggingFaceNode(BaseNode):
    """
    Node for interacting with Hugging Face Inference API.
    Provides comprehensive functionality for AI model inference, text generation, and dataset operations.
    """
    
    BASE_URL = "https://api-inference.huggingface.co"
    HUB_URL = "https://huggingface.co/api"
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.session = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Hugging Face node."""
        return NodeSchema(
            node_type="huggingface",
            version="1.0.0",
            description="Comprehensive integration with Hugging Face Inference API for AI model inference, text generation, and dataset operations",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Hugging Face API",
                    required=True,
                    enum=[
                        HuggingFaceOperation.TEXT_GENERATION,
                        HuggingFaceOperation.TEXT_COMPLETION,
                        HuggingFaceOperation.TEXT_CLASSIFICATION,
                        HuggingFaceOperation.TOKEN_CLASSIFICATION,
                        HuggingFaceOperation.SENTIMENT_ANALYSIS,
                        HuggingFaceOperation.TRANSLATION,
                        HuggingFaceOperation.SUMMARIZATION,
                        HuggingFaceOperation.QUESTION_ANSWERING,
                        HuggingFaceOperation.IMAGE_CLASSIFICATION,
                        HuggingFaceOperation.OBJECT_DETECTION,
                        HuggingFaceOperation.IMAGE_SEGMENTATION,
                        HuggingFaceOperation.SPEECH_RECOGNITION,
                        HuggingFaceOperation.TEXT_TO_SPEECH,
                        HuggingFaceOperation.GET_MODEL_INFO,
                        HuggingFaceOperation.LIST_MODELS,
                        HuggingFaceOperation.GET_DATASET_INFO,
                        HuggingFaceOperation.LIST_DATASETS
                    ]
                ),
                NodeParameter(
                    name="api_token",
                    type=NodeParameterType.SECRET,
                    description="Hugging Face API token for authentication",
                    required=True
                ),
                NodeParameter(
                    name="model_id",
                    type=NodeParameterType.STRING,
                    description="Model ID for inference operations",
                    required=False
                ),
                NodeParameter(
                    name="text_input",
                    type=NodeParameterType.STRING,
                    description="Text input for text-based operations",
                    required=False
                ),
                NodeParameter(
                    name="image_input",
                    type=NodeParameterType.STRING,
                    description="Base64 encoded image or image URL",
                    required=False
                ),
                NodeParameter(
                    name="audio_input",
                    type=NodeParameterType.STRING,
                    description="Base64 encoded audio data",
                    required=False
                ),
                NodeParameter(
                    name="max_tokens",
                    type=NodeParameterType.NUMBER,
                    description="Maximum tokens for generation",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="temperature",
                    type=NodeParameterType.NUMBER,
                    description="Temperature for text generation",
                    required=False,
                    default=0.7
                ),
                NodeParameter(
                    name="top_p",
                    type=NodeParameterType.NUMBER,
                    description="Top-p sampling parameter",
                    required=False
                ),
                NodeParameter(
                    name="dataset_id",
                    type=NodeParameterType.STRING,
                    description="Dataset ID for dataset operations",
                    required=False
                ),
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query for model/dataset listing",
                    required=False
                ),
                NodeParameter(
                    name="task",
                    type=NodeParameterType.STRING,
                    description="Task type filter for model search",
                    required=False
                ),
                NodeParameter(
                    name="parameters",
                    type=NodeParameterType.OBJECT,
                    description="Additional parameters for model inference",
                    required=False
                ),
                NodeParameter(
                    name="options",
                    type=NodeParameterType.OBJECT,
                    description="API options like use_cache, wait_for_model",
                    required=False
                )
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "generated_text": NodeParameterType.STRING,
                "classification_result": NodeParameterType.OBJECT,
                "translation_result": NodeParameterType.STRING,
                "summary": NodeParameterType.STRING,
                "answer": NodeParameterType.STRING,
                "image_results": NodeParameterType.ARRAY,
                "audio_results": NodeParameterType.OBJECT,
                "model_info": NodeParameterType.OBJECT,
                "models": NodeParameterType.ARRAY,
                "dataset_info": NodeParameterType.OBJECT,
                "datasets": NodeParameterType.ARRAY,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT
            },
            
            # Add metadata
            tags=["huggingface", "ai", "ml", "nlp", "api", "integration"],
            author="System",
            documentation_url="https://huggingface.co/docs/api-inference"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API token
        if not params.get("api_token"):
            raise NodeValidationError("Hugging Face API token is required")
            
        # Validate based on operation
        if operation in [HuggingFaceOperation.TEXT_GENERATION, HuggingFaceOperation.TEXT_COMPLETION,
                        HuggingFaceOperation.TEXT_CLASSIFICATION, HuggingFaceOperation.SENTIMENT_ANALYSIS,
                        HuggingFaceOperation.TRANSLATION, HuggingFaceOperation.SUMMARIZATION]:
            if not params.get("text_input"):
                raise NodeValidationError("Text input is required for text operations")
                
        elif operation in [HuggingFaceOperation.IMAGE_CLASSIFICATION, HuggingFaceOperation.OBJECT_DETECTION,
                          HuggingFaceOperation.IMAGE_SEGMENTATION]:
            if not params.get("image_input"):
                raise NodeValidationError("Image input is required for image operations")
                
        elif operation in [HuggingFaceOperation.SPEECH_RECOGNITION]:
            if not params.get("audio_input"):
                raise NodeValidationError("Audio input is required for audio operations")
                
        elif operation in [HuggingFaceOperation.GET_MODEL_INFO]:
            if not params.get("model_id"):
                raise NodeValidationError("Model ID is required for model info operations")
                
        elif operation in [HuggingFaceOperation.GET_DATASET_INFO]:
            if not params.get("dataset_id"):
                raise NodeValidationError("Dataset ID is required for dataset info operations")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Hugging Face node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize HTTP session
            await self._init_session()
            
            # Execute the appropriate operation
            if operation == HuggingFaceOperation.TEXT_GENERATION:
                return await self._operation_text_generation(validated_data)
            elif operation == HuggingFaceOperation.TEXT_CLASSIFICATION:
                return await self._operation_text_classification(validated_data)
            elif operation == HuggingFaceOperation.SENTIMENT_ANALYSIS:
                return await self._operation_sentiment_analysis(validated_data)
            elif operation == HuggingFaceOperation.TRANSLATION:
                return await self._operation_translation(validated_data)
            elif operation == HuggingFaceOperation.SUMMARIZATION:
                return await self._operation_summarization(validated_data)
            elif operation == HuggingFaceOperation.QUESTION_ANSWERING:
                return await self._operation_question_answering(validated_data)
            elif operation == HuggingFaceOperation.IMAGE_CLASSIFICATION:
                return await self._operation_image_classification(validated_data)
            elif operation == HuggingFaceOperation.SPEECH_RECOGNITION:
                return await self._operation_speech_recognition(validated_data)
            elif operation == HuggingFaceOperation.GET_MODEL_INFO:
                return await self._operation_get_model_info(validated_data)
            elif operation == HuggingFaceOperation.LIST_MODELS:
                return await self._operation_list_models(validated_data)
            elif operation == HuggingFaceOperation.GET_DATASET_INFO:
                return await self._operation_get_dataset_info(validated_data)
            elif operation == HuggingFaceOperation.LIST_DATASETS:
                return await self._operation_list_datasets(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "status_code": None,
                    "response_headers": None
                }
                
        except Exception as e:
            error_message = f"Error in Hugging Face node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "status_code": None,
                "response_headers": None
            }
        finally:
            # Clean up session
            await self._cleanup_session()
    
    async def _init_session(self):
        """Initialize HTTP session."""
        if not self.session:
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
    
    async def _cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any], 
                          data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the Hugging Face API."""
        url = f"{self.BASE_URL}/{endpoint}" if not endpoint.startswith("http") else endpoint
        
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_headers = dict(response.headers)
                
                # Handle different response content types
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    logger.error(error_message)
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except aiohttp.ClientError as e:
            error_message = f"HTTP error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Text Operations
    # -------------------------
    
    async def _operation_text_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text using a language model."""
        model_id = params.get("model_id", "gpt2")
        text_input = params.get("text_input")
        max_tokens = params.get("max_tokens", 100)
        temperature = params.get("temperature", 0.7)
        
        request_data = {
            "inputs": text_input,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature
            }
        }
        
        # Add additional parameters if provided
        if params.get("parameters"):
            request_data["parameters"].update(params.get("parameters"))
        
        # Add options if provided
        if params.get("options"):
            request_data["options"] = params.get("options")
        
        result = await self._make_request("POST", f"models/{model_id}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], list) and len(result["result"]) > 0:
                generated_text = result["result"][0].get("generated_text", "")
                result["generated_text"] = generated_text
        
        return result
    
    async def _operation_text_classification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Classify text using a classification model."""
        model_id = params.get("model_id", "distilbert-base-uncased-finetuned-sst-2-english")
        text_input = params.get("text_input")
        
        request_data = {"inputs": text_input}
        
        # Add options if provided
        if params.get("options"):
            request_data["options"] = params.get("options")
        
        result = await self._make_request("POST", f"models/{model_id}", params, request_data)
        
        if result["status"] == "success":
            result["classification_result"] = result["result"]
        
        return result
    
    async def _operation_sentiment_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        model_id = params.get("model_id", "cardiffnlp/twitter-roberta-base-sentiment-latest")
        text_input = params.get("text_input")
        
        request_data = {"inputs": text_input}
        
        # Add options if provided
        if params.get("options"):
            request_data["options"] = params.get("options")
        
        result = await self._make_request("POST", f"models/{model_id}", params, request_data)
        
        if result["status"] == "success":
            result["classification_result"] = result["result"]
        
        return result
    
    async def _operation_translation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Translate text using a translation model."""
        model_id = params.get("model_id", "Helsinki-NLP/opus-mt-en-fr")
        text_input = params.get("text_input")
        
        request_data = {"inputs": text_input}
        
        # Add options if provided
        if params.get("options"):
            request_data["options"] = params.get("options")
        
        result = await self._make_request("POST", f"models/{model_id}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], list) and len(result["result"]) > 0:
                translation_text = result["result"][0].get("translation_text", "")
                result["translation_result"] = translation_text
        
        return result
    
    async def _operation_summarization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize text using a summarization model."""
        model_id = params.get("model_id", "facebook/bart-large-cnn")
        text_input = params.get("text_input")
        
        request_data = {"inputs": text_input}
        
        # Add parameters if provided
        if params.get("parameters"):
            request_data["parameters"] = params.get("parameters")
        
        # Add options if provided
        if params.get("options"):
            request_data["options"] = params.get("options")
        
        result = await self._make_request("POST", f"models/{model_id}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            if isinstance(result["result"], list) and len(result["result"]) > 0:
                summary_text = result["result"][0].get("summary_text", "")
                result["summary"] = summary_text
        
        return result
    
    async def _operation_question_answering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Answer questions using a QA model."""
        model_id = params.get("model_id", "deepset/roberta-base-squad2")
        text_input = params.get("text_input")
        question = params.get("question", text_input)
        context = params.get("context", "")
        
        request_data = {
            "inputs": {
                "question": question,
                "context": context
            }
        }
        
        # Add options if provided
        if params.get("options"):
            request_data["options"] = params.get("options")
        
        result = await self._make_request("POST", f"models/{model_id}", params, request_data)
        
        if result["status"] == "success" and result["result"]:
            answer_text = result["result"].get("answer", "")
            result["answer"] = answer_text
        
        return result
    
    # -------------------------
    # Image Operations
    # -------------------------
    
    async def _operation_image_classification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Classify images using a classification model."""
        model_id = params.get("model_id", "google/vit-base-patch16-224")
        image_input = params.get("image_input")
        
        # Handle base64 encoded image
        if image_input.startswith("data:"):
            # Extract base64 data
            image_data = image_input.split(",")[1]
        else:
            image_data = image_input
        
        # For image classification, we need to send binary data
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}"
        }
        
        try:
            import base64
            binary_data = base64.b64decode(image_data)
            
            url = f"{self.BASE_URL}/models/{model_id}"
            async with self.session.post(url, headers=headers, data=binary_data) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "image_results": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error processing image: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Audio Operations
    # -------------------------
    
    async def _operation_speech_recognition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize speech from audio using ASR model."""
        model_id = params.get("model_id", "facebook/wav2vec2-base-960h")
        audio_input = params.get("audio_input")
        
        # Handle base64 encoded audio
        if audio_input.startswith("data:"):
            # Extract base64 data
            audio_data = audio_input.split(",")[1]
        else:
            audio_data = audio_input
        
        # For speech recognition, we need to send binary data
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}"
        }
        
        try:
            import base64
            binary_data = base64.b64decode(audio_data)
            
            url = f"{self.BASE_URL}/models/{model_id}"
            async with self.session.post(url, headers=headers, data=binary_data) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "audio_results": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error processing audio: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Model Operations
    # -------------------------
    
    async def _operation_get_model_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific model."""
        model_id = params.get("model_id")
        
        url = f"{self.HUB_URL}/models/{model_id}"
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "model_info": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error getting model info: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    async def _operation_list_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available models."""
        query_params = []
        
        if params.get("query"):
            query_params.append(f"search={params.get('query')}")
        if params.get("task"):
            query_params.append(f"filter={params.get('task')}")
        
        url = f"{self.HUB_URL}/models"
        if query_params:
            url += "?" + "&".join(query_params)
        
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "models": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error listing models: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    # -------------------------
    # Dataset Operations
    # -------------------------
    
    async def _operation_get_dataset_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific dataset."""
        dataset_id = params.get("dataset_id")
        
        url = f"{self.HUB_URL}/datasets/{dataset_id}"
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "dataset_info": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error getting dataset info: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }
    
    async def _operation_list_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available datasets."""
        query_params = []
        
        if params.get("query"):
            query_params.append(f"search={params.get('query')}")
        
        url = f"{self.HUB_URL}/datasets"
        if query_params:
            url += "?" + "&".join(query_params)
        
        headers = {
            "Authorization": f"Bearer {params.get('api_token')}"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                response_headers = dict(response.headers)
                
                if response.content_type == 'application/json':
                    response_data = await response.json()
                else:
                    response_data = await response.text()
                
                if response.status >= 400:
                    error_message = f"Hugging Face API error {response.status}: {response_data}"
                    return {
                        "status": "error",
                        "error": error_message,
                        "result": response_data,
                        "status_code": response.status,
                        "response_headers": response_headers
                    }
                
                return {
                    "status": "success",
                    "result": response_data,
                    "datasets": response_data,
                    "error": None,
                    "status_code": response.status,
                    "response_headers": response_headers
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error listing datasets: {str(e)}",
                "result": None,
                "status_code": None,
                "response_headers": None
            }


# Utility functions for common Hugging Face operations
class HuggingFaceHelpers:
    """Helper functions for common Hugging Face operations."""
    
    @staticmethod
    def create_text_generation_params(max_tokens: int = 100, temperature: float = 0.7, 
                                    top_p: float = None, top_k: int = None) -> Dict[str, Any]:
        """Create parameters for text generation."""
        params = {
            "max_new_tokens": max_tokens,
            "temperature": temperature
        }
        if top_p is not None:
            params["top_p"] = top_p
        if top_k is not None:
            params["top_k"] = top_k
        return params
    
    @staticmethod
    def create_qa_input(question: str, context: str) -> Dict[str, Any]:
        """Create input for question answering."""
        return {
            "question": question,
            "context": context
        }
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """Encode image file to base64."""
        import base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_string}"
    
    @staticmethod
    def encode_audio_to_base64(audio_path: str) -> str:
        """Encode audio file to base64."""
        import base64
        with open(audio_path, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
        return f"data:audio/wav;base64,{encoded_string}"


# Main test function for Hugging Face Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Hugging Face Node Test Suite ===")
        
        # Get API token from environment or user input
        api_token = os.environ.get("HUGGINGFACE_API_TOKEN")
        
        if not api_token:
            print("Hugging Face API token not found in environment variables")
            print("Please set HUGGINGFACE_API_TOKEN")
            print("Or provide it when prompted...")
            api_token = input("Enter Hugging Face API token: ")
        
        if not api_token:
            print("Hugging Face API token is required for testing")
            return
        
        # Create an instance of the Hugging Face Node
        node = HuggingFaceNode()
        
        # Test cases
        test_cases = [
            {
                "name": "Text Generation",
                "params": {
                    "operation": HuggingFaceOperation.TEXT_GENERATION,
                    "api_token": api_token,
                    "model_id": "gpt2",
                    "text_input": "The future of AI is",
                    "max_tokens": 50
                },
                "expected_status": "success"
            },
            {
                "name": "Text Classification",
                "params": {
                    "operation": HuggingFaceOperation.TEXT_CLASSIFICATION,
                    "api_token": api_token,
                    "text_input": "I love this product!"
                },
                "expected_status": "success"
            }
        ]
        
        # Run test cases
        total_tests = len(test_cases)
        passed_tests = 0
        
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            
            try:
                # Prepare node data
                node_data = {
                    "params": test_case["params"]
                }
                
                # Execute the node
                result = await node.execute(node_data)
                
                # Check if the result status matches expected status
                if result["status"] == test_case["expected_status"]:
                    print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                    if result.get("generated_text"):
                        print(f"Generated text: {result['generated_text'][:100]}...")
                    if result.get("classification_result"):
                        print(f"Classification: {result['classification_result']}")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests to avoid rate limiting
                await asyncio.sleep(2.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("huggingface", HuggingFaceNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register HuggingFaceNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")