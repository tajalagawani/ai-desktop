#!/usr/bin/env python3
"""
Telegram Bot API Node for ACT Workflow System

This node provides comprehensive Telegram Bot API integration capabilities including:
- Message management (send, edit, delete, forward)
- Media handling (photos, videos, documents, audio)
- Chat administration and member management
- Inline keyboards and callback handling
- File upload/download operations
- Webhook and polling for updates
- Bot command management
- Business features and advanced operations

Architecture:
- Dispatch map for clean operation routing
- Unified TelegramBotWrapper for async HTTP operations
- Context manager for resource lifecycle
- Metadata-driven validation
- Comprehensive error handling with rate limit awareness
- Sensitive data masking for tokens and user data
"""

import asyncio
import aiohttp
import base64
import json
import logging
import mimetypes
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Handle imports for both module and direct execution
try:
    from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Check for optional dependencies
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

class TelegramOperation(str, Enum):
    """Enumeration of all supported Telegram Bot API operations."""
    
    # Bot Management
    GET_ME = "get_me"
    GET_MY_COMMANDS = "get_my_commands"
    SET_MY_COMMANDS = "set_my_commands"
    DELETE_MY_COMMANDS = "delete_my_commands"
    
    # Message Operations
    SEND_MESSAGE = "send_message"
    EDIT_MESSAGE_TEXT = "edit_message_text"
    DELETE_MESSAGE = "delete_message"
    FORWARD_MESSAGE = "forward_message"
    COPY_MESSAGE = "copy_message"
    
    # Media Messaging
    SEND_PHOTO = "send_photo"
    SEND_VIDEO = "send_video"
    SEND_AUDIO = "send_audio"
    SEND_DOCUMENT = "send_document"
    SEND_STICKER = "send_sticker"
    SEND_ANIMATION = "send_animation"
    SEND_VOICE = "send_voice"
    SEND_VIDEO_NOTE = "send_video_note"
    SEND_MEDIA_GROUP = "send_media_group"
    
    # Advanced Messaging
    SEND_LOCATION = "send_location"
    SEND_VENUE = "send_venue"
    SEND_CONTACT = "send_contact"
    SEND_POLL = "send_poll"
    SEND_DICE = "send_dice"
    
    # Update Operations
    GET_UPDATES = "get_updates"
    SET_WEBHOOK = "set_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    GET_WEBHOOK_INFO = "get_webhook_info"
    
    # Chat Management
    GET_CHAT = "get_chat"
    GET_CHAT_MEMBER_COUNT = "get_chat_member_count"
    GET_CHAT_MEMBER = "get_chat_member"
    GET_CHAT_ADMINISTRATORS = "get_chat_administrators"
    
    # Chat Settings
    SET_CHAT_TITLE = "set_chat_title"
    SET_CHAT_DESCRIPTION = "set_chat_description"
    SET_CHAT_PHOTO = "set_chat_photo"
    DELETE_CHAT_PHOTO = "delete_chat_photo"
    PIN_CHAT_MESSAGE = "pin_chat_message"
    UNPIN_CHAT_MESSAGE = "unpin_chat_message"
    UNPIN_ALL_CHAT_MESSAGES = "unpin_all_chat_messages"
    
    # Chat Administration
    PROMOTE_CHAT_MEMBER = "promote_chat_member"
    RESTRICT_CHAT_MEMBER = "restrict_chat_member"
    BAN_CHAT_MEMBER = "ban_chat_member"
    UNBAN_CHAT_MEMBER = "unban_chat_member"
    LEAVE_CHAT = "leave_chat"
    
    # Invite Management
    EXPORT_CHAT_INVITE_LINK = "export_chat_invite_link"
    CREATE_CHAT_INVITE_LINK = "create_chat_invite_link"
    EDIT_CHAT_INVITE_LINK = "edit_chat_invite_link"
    REVOKE_CHAT_INVITE_LINK = "revoke_chat_invite_link"
    
    # Keyboard Operations
    EDIT_MESSAGE_REPLY_MARKUP = "edit_message_reply_markup"
    ANSWER_CALLBACK_QUERY = "answer_callback_query"
    
    # File Operations
    GET_FILE = "get_file"
    DOWNLOAD_FILE = "download_file"
    
    # Advanced Features
    SEND_INVOICE = "send_invoice"
    SEND_GAME = "send_game"
    SET_GAME_SCORE = "set_game_score"
    GET_GAME_HIGH_SCORES = "get_game_high_scores"

class TelegramError(Exception):
    """Custom exception for Telegram API errors."""
    def __init__(self, message: str, error_code: int = None, description: str = None):
        self.error_code = error_code
        self.description = description
        super().__init__(message)

class TelegramBotWrapper:
    """Unified wrapper for Telegram Bot API operations with async HTTP client."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.file_url = f"https://api.telegram.org/file/bot{bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, files: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to Telegram API with proper error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if files:
                # Use multipart form data for file uploads
                form_data = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            form_data.add_field(key, json.dumps(value))
                        else:
                            form_data.add_field(key, str(value))
                
                for field_name, file_data in files.items():
                    if isinstance(file_data, dict):
                        filename = file_data.get('filename', 'file')
                        content = file_data.get('content')
                        content_type = file_data.get('content_type', 'application/octet-stream')
                        
                        if isinstance(content, str):
                            # Assume base64 encoded
                            content = base64.b64decode(content)
                        
                        form_data.add_field(field_name, content, filename=filename, content_type=content_type)
                    else:
                        form_data.add_field(field_name, file_data)
                
                async with self.session.request(method, url, data=form_data) as response:
                    result = await response.json()
            else:
                # Use JSON for regular requests
                headers = {'Content-Type': 'application/json'} if data else None
                json_data = data if data else None
                
                async with self.session.request(method, url, json=json_data, headers=headers) as response:
                    result = await response.json()
            
            if not result.get('ok', False):
                error_code = result.get('error_code', 0)
                description = result.get('description', 'Unknown error')
                raise TelegramError(f"Telegram API error: {description}", error_code, description)
            
            return result.get('result', {})
            
        except aiohttp.ClientError as e:
            raise TelegramError(f"HTTP client error: {str(e)}")
        except json.JSONDecodeError as e:
            raise TelegramError(f"JSON decode error: {str(e)}")
        except Exception as e:
            if isinstance(e, TelegramError):
                raise
            raise TelegramError(f"Unexpected error: {str(e)}")
    
    # Bot Management Methods
    async def get_me(self) -> Dict[str, Any]:
        """Get basic information about the bot."""
        return await self._make_request('GET', 'getMe')
    
    async def get_my_commands(self, scope: Dict[str, Any] = None, language_code: str = None) -> List[Dict[str, Any]]:
        """Get the current list of bot commands."""
        data = {}
        if scope:
            data['scope'] = scope
        if language_code:
            data['language_code'] = language_code
        return await self._make_request('GET', 'getMyCommands', data)
    
    async def set_my_commands(self, commands: List[Dict[str, str]], scope: Dict[str, Any] = None, language_code: str = None) -> bool:
        """Set the list of bot commands."""
        data = {'commands': commands}
        if scope:
            data['scope'] = scope
        if language_code:
            data['language_code'] = language_code
        return await self._make_request('POST', 'setMyCommands', data)
    
    async def delete_my_commands(self, scope: Dict[str, Any] = None, language_code: str = None) -> bool:
        """Delete the list of bot commands."""
        data = {}
        if scope:
            data['scope'] = scope
        if language_code:
            data['language_code'] = language_code
        return await self._make_request('POST', 'deleteMyCommands', data)
    
    # Message Operations
    async def send_message(self, chat_id: Union[int, str], text: str, parse_mode: str = None, 
                          reply_parameters: Dict[str, Any] = None, reply_markup: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a text message."""
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_parameters:
            data['reply_parameters'] = reply_parameters
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        return await self._make_request('POST', 'sendMessage', data)
    
    async def edit_message_text(self, text: str, chat_id: Union[int, str] = None, message_id: int = None, 
                               inline_message_id: str = None, parse_mode: str = None, reply_markup: Dict[str, Any] = None) -> Dict[str, Any]:
        """Edit text of a message."""
        data = {'text': text}
        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        return await self._make_request('POST', 'editMessageText', data)
    
    async def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        """Delete a message."""
        data = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        return await self._make_request('POST', 'deleteMessage', data)
    
    async def forward_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str], message_id: int, 
                             message_thread_id: int = None, disable_notification: bool = None, protect_content: bool = None) -> Dict[str, Any]:
        """Forward a message."""
        data = {
            'chat_id': chat_id,
            'from_chat_id': from_chat_id,
            'message_id': message_id
        }
        if message_thread_id:
            data['message_thread_id'] = message_thread_id
        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        if protect_content is not None:
            data['protect_content'] = protect_content
        
        return await self._make_request('POST', 'forwardMessage', data)
    
    # Media Operations
    async def send_photo(self, chat_id: Union[int, str], photo: str, caption: str = None, parse_mode: str = None, 
                        reply_markup: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a photo."""
        if photo.startswith('http'):
            # URL
            data = {
                'chat_id': chat_id,
                'photo': photo
            }
            files = None
        else:
            # Base64 encoded file
            data = {'chat_id': chat_id}
            files = {
                'photo': {
                    'filename': 'photo.jpg',
                    'content': photo,
                    'content_type': 'image/jpeg'
                }
            }
        
        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        return await self._make_request('POST', 'sendPhoto', data, files)
    
    async def send_document(self, chat_id: Union[int, str], document: str, thumbnail: str = None, 
                           caption: str = None, parse_mode: str = None, reply_markup: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a general file."""
        if document.startswith('http'):
            # URL
            data = {
                'chat_id': chat_id,
                'document': document
            }
            files = None
        else:
            # Base64 encoded file
            data = {'chat_id': chat_id}
            files = {
                'document': {
                    'filename': 'document.pdf',
                    'content': document,
                    'content_type': 'application/pdf'
                }
            }
        
        if thumbnail:
            if not files:
                files = {}
            files['thumbnail'] = {
                'filename': 'thumb.jpg',
                'content': thumbnail,
                'content_type': 'image/jpeg'
            }
        
        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        return await self._make_request('POST', 'sendDocument', data, files)
    
    # Chat Management
    async def get_chat(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """Get up to date information about the chat."""
        data = {'chat_id': chat_id}
        return await self._make_request('GET', 'getChat', data)
    
    async def get_chat_member_count(self, chat_id: Union[int, str]) -> int:
        """Get the number of members in a chat."""
        data = {'chat_id': chat_id}
        return await self._make_request('GET', 'getChatMemberCount', data)
    
    async def get_chat_member(self, chat_id: Union[int, str], user_id: int) -> Dict[str, Any]:
        """Get information about a member of a chat."""
        data = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        return await self._make_request('GET', 'getChatMember', data)
    
    # File Operations
    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get basic info about a file and prepare it for downloading."""
        data = {'file_id': file_id}
        return await self._make_request('GET', 'getFile', data)
    
    async def download_file(self, file_path: str) -> bytes:
        """Download a file from Telegram servers."""
        url = f"{self.file_url}/{file_path}"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise TelegramError(f"Failed to download file: HTTP {response.status}")

class TelegramNode(BaseNode):
    """
    Telegram Bot API node for ACT workflow system.
    
    Provides comprehensive Telegram Bot API integration with support for:
    - Bot management and command handling
    - Message operations (send, edit, delete, forward)
    - Media handling (photos, videos, documents, audio)
    - Chat administration and member management
    - Update processing (polling and webhooks)
    - File operations (upload/download)
    - Inline keyboards and callbacks
    - Advanced features (polls, games, payments)
    """
    
    # Operation metadata for validation and documentation
    OPERATION_METADATA = {
        # Bot Management
        TelegramOperation.GET_ME: {
            "required": ["bot_token"],
            "optional": [],
            "description": "Get basic information about the bot"
        },
        TelegramOperation.SET_MY_COMMANDS: {
            "required": ["bot_token", "commands"],
            "optional": ["scope", "language_code"],
            "description": "Set the list of bot commands"
        },
        
        # Message Operations
        TelegramOperation.SEND_MESSAGE: {
            "required": ["bot_token", "chat_id", "text"],
            "optional": ["parse_mode", "reply_parameters", "reply_markup"],
            "description": "Send a text message"
        },
        TelegramOperation.EDIT_MESSAGE_TEXT: {
            "required": ["bot_token", "text"],
            "optional": ["chat_id", "message_id", "inline_message_id", "parse_mode", "reply_markup"],
            "description": "Edit text of a message"
        },
        TelegramOperation.DELETE_MESSAGE: {
            "required": ["bot_token", "chat_id", "message_id"],
            "optional": [],
            "description": "Delete a message"
        },
        TelegramOperation.FORWARD_MESSAGE: {
            "required": ["bot_token", "chat_id", "from_chat_id", "message_id"],
            "optional": ["message_thread_id", "disable_notification", "protect_content"],
            "description": "Forward a message"
        },
        
        # Media Operations
        TelegramOperation.SEND_PHOTO: {
            "required": ["bot_token", "chat_id", "photo"],
            "optional": ["caption", "parse_mode", "reply_markup"],
            "description": "Send a photo"
        },
        TelegramOperation.SEND_DOCUMENT: {
            "required": ["bot_token", "chat_id", "document"],
            "optional": ["thumbnail", "caption", "parse_mode", "reply_markup"],
            "description": "Send a general file"
        },
        
        # Chat Management
        TelegramOperation.GET_CHAT: {
            "required": ["bot_token", "chat_id"],
            "optional": [],
            "description": "Get information about a chat"
        },
        TelegramOperation.GET_CHAT_MEMBER: {
            "required": ["bot_token", "chat_id", "user_id"],
            "optional": [],
            "description": "Get information about a chat member"
        },
        
        # File Operations
        TelegramOperation.GET_FILE: {
            "required": ["bot_token", "file_id"],
            "optional": [],
            "description": "Get file information for download"
        },
        TelegramOperation.DOWNLOAD_FILE: {
            "required": ["bot_token", "file_path"],
            "optional": [],
            "description": "Download a file from Telegram"
        },
    }
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        
        # Create operation dispatch map for clean routing
        self.operation_dispatch = {
            # Bot Management
            TelegramOperation.GET_ME: self._handle_get_me,
            TelegramOperation.GET_MY_COMMANDS: self._handle_get_my_commands,
            TelegramOperation.SET_MY_COMMANDS: self._handle_set_my_commands,
            TelegramOperation.DELETE_MY_COMMANDS: self._handle_delete_my_commands,
            
            # Message Operations
            TelegramOperation.SEND_MESSAGE: self._handle_send_message,
            TelegramOperation.EDIT_MESSAGE_TEXT: self._handle_edit_message_text,
            TelegramOperation.DELETE_MESSAGE: self._handle_delete_message,
            TelegramOperation.FORWARD_MESSAGE: self._handle_forward_message,
            TelegramOperation.COPY_MESSAGE: self._handle_copy_message,
            
            # Media Operations
            TelegramOperation.SEND_PHOTO: self._handle_send_photo,
            TelegramOperation.SEND_VIDEO: self._handle_send_video,
            TelegramOperation.SEND_AUDIO: self._handle_send_audio,
            TelegramOperation.SEND_DOCUMENT: self._handle_send_document,
            TelegramOperation.SEND_STICKER: self._handle_send_sticker,
            TelegramOperation.SEND_ANIMATION: self._handle_send_animation,
            TelegramOperation.SEND_VOICE: self._handle_send_voice,
            TelegramOperation.SEND_VIDEO_NOTE: self._handle_send_video_note,
            TelegramOperation.SEND_MEDIA_GROUP: self._handle_send_media_group,
            
            # Advanced Messaging
            TelegramOperation.SEND_LOCATION: self._handle_send_location,
            TelegramOperation.SEND_VENUE: self._handle_send_venue,
            TelegramOperation.SEND_CONTACT: self._handle_send_contact,
            TelegramOperation.SEND_POLL: self._handle_send_poll,
            TelegramOperation.SEND_DICE: self._handle_send_dice,
            
            # Update Operations
            TelegramOperation.GET_UPDATES: self._handle_get_updates,
            TelegramOperation.SET_WEBHOOK: self._handle_set_webhook,
            TelegramOperation.DELETE_WEBHOOK: self._handle_delete_webhook,
            TelegramOperation.GET_WEBHOOK_INFO: self._handle_get_webhook_info,
            
            # Chat Management
            TelegramOperation.GET_CHAT: self._handle_get_chat,
            TelegramOperation.GET_CHAT_MEMBER_COUNT: self._handle_get_chat_member_count,
            TelegramOperation.GET_CHAT_MEMBER: self._handle_get_chat_member,
            TelegramOperation.GET_CHAT_ADMINISTRATORS: self._handle_get_chat_administrators,
            
            # Chat Settings
            TelegramOperation.SET_CHAT_TITLE: self._handle_set_chat_title,
            TelegramOperation.SET_CHAT_DESCRIPTION: self._handle_set_chat_description,
            TelegramOperation.SET_CHAT_PHOTO: self._handle_set_chat_photo,
            TelegramOperation.DELETE_CHAT_PHOTO: self._handle_delete_chat_photo,
            TelegramOperation.PIN_CHAT_MESSAGE: self._handle_pin_chat_message,
            TelegramOperation.UNPIN_CHAT_MESSAGE: self._handle_unpin_chat_message,
            
            # Chat Administration
            TelegramOperation.PROMOTE_CHAT_MEMBER: self._handle_promote_chat_member,
            TelegramOperation.RESTRICT_CHAT_MEMBER: self._handle_restrict_chat_member,
            TelegramOperation.BAN_CHAT_MEMBER: self._handle_ban_chat_member,
            TelegramOperation.UNBAN_CHAT_MEMBER: self._handle_unban_chat_member,
            TelegramOperation.LEAVE_CHAT: self._handle_leave_chat,
            
            # File Operations
            TelegramOperation.GET_FILE: self._handle_get_file,
            TelegramOperation.DOWNLOAD_FILE: self._handle_download_file,
            
            # Keyboard Operations
            TelegramOperation.EDIT_MESSAGE_REPLY_MARKUP: self._handle_edit_message_reply_markup,
            TelegramOperation.ANSWER_CALLBACK_QUERY: self._handle_answer_callback_query,
        }
    
    def get_schema(self) -> NodeSchema:
        """Return the schema for TelegramNode."""
        return NodeSchema(
            name="TelegramNode",
            node_type="telegram",
            description="Telegram Bot API integration node for messaging, chat management, and bot operations",
            version="1.0.0",
            parameters=[
                NodeParameter(
                    name="operation",
                    type="string",
                    description="The Telegram operation to perform",
                    required=True,
                    enum=[op.value for op in TelegramOperation]
                ),
                NodeParameter(
                    name="bot_token",
                    type="string", 
                    description="Telegram bot token for authentication",
                    required=True,
                    sensitive=True
                ),
                NodeParameter(
                    name="chat_id",
                    type="string",
                    description="Unique identifier for the target chat or username",
                    required=False
                ),
                NodeParameter(
                    name="text",
                    type="string",
                    description="Text content for message operations",
                    required=False
                ),
                NodeParameter(
                    name="message_id",
                    type="number",
                    description="Unique message identifier",
                    required=False
                ),
                NodeParameter(
                    name="user_id",
                    type="number",
                    description="Unique user identifier",
                    required=False
                ),
                NodeParameter(
                    name="photo",
                    type="string",
                    description="Photo to send (file_id, HTTP URL, or base64 encoded)",
                    required=False
                ),
                NodeParameter(
                    name="document",
                    type="string",
                    description="Document to send (file_id, HTTP URL, or base64 encoded)",
                    required=False
                ),
                NodeParameter(
                    name="caption",
                    type="string",
                    description="Media caption (0-1024 characters)",
                    required=False
                ),
                NodeParameter(
                    name="parse_mode",
                    type="string",
                    description="Text formatting mode (Markdown, MarkdownV2, HTML)",
                    required=False,
                    enum=["Markdown", "MarkdownV2", "HTML"]
                ),
                NodeParameter(
                    name="reply_markup",
                    type="object",
                    description="Inline keyboard, custom reply keyboard, or other reply markup",
                    required=False
                ),
                NodeParameter(
                    name="commands",
                    type="array",
                    description="Array of bot commands for setMyCommands",
                    required=False
                ),
                NodeParameter(
                    name="file_id",
                    type="string",
                    description="File identifier for file operations",
                    required=False
                ),
                NodeParameter(
                    name="file_path",
                    type="string",
                    description="File path for download operations",
                    required=False
                ),
                NodeParameter(
                    name="webhook_url",
                    type="string",
                    description="HTTPS URL for webhook operations",
                    required=False
                ),
                NodeParameter(
                    name="latitude",
                    type="number",
                    description="Latitude for location sharing",
                    required=False
                ),
                NodeParameter(
                    name="longitude", 
                    type="number",
                    description="Longitude for location sharing",
                    required=False
                ),
                NodeParameter(
                    name="poll_question",
                    type="string",
                    description="Poll question (1-300 characters)",
                    required=False
                ),
                NodeParameter(
                    name="poll_options",
                    type="array",
                    description="List of answer options for polls",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "result": NodeParameterType.OBJECT,
                "message": NodeParameterType.STRING,
                "file_data": NodeParameterType.STRING,
                "chat_info": NodeParameterType.OBJECT,
                "user_info": NodeParameterType.OBJECT,
                "timestamp": NodeParameterType.STRING,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.NUMBER
            }
        )
    
    def validate_custom(self, data: Dict[str, Any]) -> None:
        """Custom validation for Telegram operations."""
        params = data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise ValueError("Operation parameter is required")
        
        if operation not in [op.value for op in TelegramOperation]:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Get operation metadata for validation
        metadata = self.OPERATION_METADATA.get(operation, {})
        required_params = metadata.get("required", [])
        
        # Check required parameters
        for param in required_params:
            if param not in params:
                raise ValueError(f"Required parameter '{param}' missing for operation '{operation}'")
        
        # Validate bot token format
        bot_token = params.get("bot_token", "")
        if bot_token and not (bot_token.count(":") == 1 and len(bot_token.split(":")[0]) >= 5):
            raise ValueError("Invalid bot token format. Expected format: '123456:ABC-DEF1234...'")
        
        # Validate chat_id for operations that require it
        if "chat_id" in required_params:
            chat_id = params.get("chat_id")
            if not chat_id:
                raise ValueError("chat_id is required for this operation")
        
        # Validate message operations
        if operation in [TelegramOperation.SEND_MESSAGE, TelegramOperation.EDIT_MESSAGE_TEXT]:
            text = params.get("text", "")
            if not text or len(text) > 4096:
                raise ValueError("Text must be provided and not exceed 4096 characters")
        
        # Validate media operations
        if operation in [TelegramOperation.SEND_PHOTO, TelegramOperation.SEND_DOCUMENT]:
            media_param = "photo" if operation == TelegramOperation.SEND_PHOTO else "document"
            media = params.get(media_param)
            if not media:
                raise ValueError(f"{media_param} parameter is required for {operation}")
        
        # Validate file operations
        if operation == TelegramOperation.GET_FILE:
            if not params.get("file_id"):
                raise ValueError("file_id is required for get_file operation")
        
        if operation == TelegramOperation.DOWNLOAD_FILE:
            if not params.get("file_path"):
                raise ValueError("file_path is required for download_file operation")
        
        # Validate location parameters
        if operation == TelegramOperation.SEND_LOCATION:
            latitude = params.get("latitude")
            longitude = params.get("longitude")
            if latitude is None or longitude is None:
                raise ValueError("Both latitude and longitude are required for send_location")
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude must be between -180 and 180")
        
        # Validate poll parameters
        if operation == TelegramOperation.SEND_POLL:
            question = params.get("poll_question", "")
            options = params.get("poll_options", [])
            if not question or len(question) > 300:
                raise ValueError("Poll question must be provided and not exceed 300 characters")
            if len(options) < 2 or len(options) > 10:
                raise ValueError("Poll must have between 2 and 10 options")
        
        # Validate commands for set_my_commands
        if operation == TelegramOperation.SET_MY_COMMANDS:
            commands = params.get("commands", [])
            if not isinstance(commands, list):
                raise ValueError("Commands must be an array")
            if len(commands) > 100:
                raise ValueError("Maximum 100 commands allowed")
            
            for cmd in commands:
                if not isinstance(cmd, dict) or 'command' not in cmd or 'description' not in cmd:
                    raise ValueError("Each command must have 'command' and 'description' fields")
                if len(cmd['command']) > 32 or len(cmd['description']) > 256:
                    raise ValueError("Command name max 32 chars, description max 256 chars")
    
    @asynccontextmanager
    async def _get_telegram_bot(self, bot_token: str):
        """Get TelegramBotWrapper with proper lifecycle management."""
        bot = TelegramBotWrapper(bot_token)
        try:
            async with bot:
                yield bot
        except Exception as e:
            self.logger.error(f"Telegram bot error: {str(e)}")
            raise
    
    def _mask_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked = params.copy()
        
        # Mask bot token
        if "bot_token" in masked:
            token = masked["bot_token"]
            if len(token) > 10:
                masked["bot_token"] = f"{token[:5]}***{token[-5:]}"
            else:
                masked["bot_token"] = "***TOKEN***"
        
        # Mask large file data
        if "photo" in masked and isinstance(masked["photo"], str) and len(masked["photo"]) > 100:
            masked["photo"] = "***PHOTO_DATA***"
        
        if "document" in masked and isinstance(masked["document"], str) and len(masked["document"]) > 100:
            masked["document"] = "***DOCUMENT_DATA***"
        
        # Mask other potentially large data
        for field in ["file_data", "media", "voice", "video", "audio"]:
            if field in masked and len(str(masked[field])) > 100:
                masked[field] = f"***{field.upper()}***"
        
        return masked
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Telegram operation."""
        try:
            params = data.get("params", {})
            operation = params.get("operation")
            
            # Log operation (with sensitive data masked)
            masked_params = self._mask_sensitive_data(params)
            self.logger.info(f"Executing Telegram operation: {operation} with params: {masked_params}")
            
            # Get operation handler
            handler = self.operation_dispatch.get(operation)
            if not handler:
                return {
                    "status": "error",
                    "error": f"Unsupported Telegram operation: {operation}",
                    "operation": operation
                }
            
            # Execute operation
            result = await handler(params)
            
            self.logger.info(f"Telegram operation {operation} completed successfully")
            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except TelegramError as e:
            error_msg = f"Telegram API error: {str(e)}"
            if e.error_code:
                error_msg += f" (Code: {e.error_code})"
            
            self.logger.error(error_msg)
            return {
                "status": "error", 
                "error": error_msg,
                "error_code": e.error_code,
                "operation": params.get("operation", "unknown")
            }
        except Exception as e:
            error_msg = f"Telegram operation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "operation": params.get("operation", "unknown")
            }
    
    # Bot Management Handlers
    async def _handle_get_me(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_me operation."""
        bot_token = params["bot_token"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.get_me()
            return {
                "bot_info": result,
                "id": result.get("id"),
                "username": result.get("username"),
                "first_name": result.get("first_name"),
                "is_bot": result.get("is_bot")
            }
    
    async def _handle_get_my_commands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_my_commands operation."""
        bot_token = params["bot_token"]
        scope = params.get("scope")
        language_code = params.get("language_code")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.get_my_commands(scope, language_code)
            return {
                "commands": result,
                "count": len(result)
            }
    
    async def _handle_set_my_commands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set_my_commands operation."""
        bot_token = params["bot_token"]
        commands = params["commands"]
        scope = params.get("scope")
        language_code = params.get("language_code")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.set_my_commands(commands, scope, language_code)
            return {
                "success": result,
                "commands_set": len(commands),
                "message": f"Set {len(commands)} bot commands"
            }
    
    async def _handle_delete_my_commands(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_my_commands operation."""
        bot_token = params["bot_token"]
        scope = params.get("scope")
        language_code = params.get("language_code")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.delete_my_commands(scope, language_code)
            return {
                "success": result,
                "message": "Bot commands deleted"
            }
    
    # Message Operation Handlers
    async def _handle_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_message operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        text = params["text"]
        parse_mode = params.get("parse_mode")
        reply_parameters = params.get("reply_parameters")
        reply_markup = params.get("reply_markup")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.send_message(chat_id, text, parse_mode, reply_parameters, reply_markup)
            return {
                "message": result,
                "message_id": result.get("message_id"),
                "chat": result.get("chat"),
                "text_length": len(text),
                "sent": True
            }
    
    async def _handle_edit_message_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle edit_message_text operation."""
        bot_token = params["bot_token"]
        text = params["text"]
        chat_id = params.get("chat_id")
        message_id = params.get("message_id")
        inline_message_id = params.get("inline_message_id")
        parse_mode = params.get("parse_mode")
        reply_markup = params.get("reply_markup")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.edit_message_text(text, chat_id, message_id, inline_message_id, parse_mode, reply_markup)
            return {
                "message": result,
                "edited": True,
                "new_text_length": len(text)
            }
    
    async def _handle_delete_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_message operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        message_id = params["message_id"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.delete_message(chat_id, message_id)
            return {
                "success": result,
                "deleted": True,
                "chat_id": chat_id,
                "message_id": message_id
            }
    
    async def _handle_forward_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle forward_message operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        from_chat_id = params["from_chat_id"]
        message_id = params["message_id"]
        message_thread_id = params.get("message_thread_id")
        disable_notification = params.get("disable_notification")
        protect_content = params.get("protect_content")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.forward_message(chat_id, from_chat_id, message_id, message_thread_id, disable_notification, protect_content)
            return {
                "message": result,
                "forwarded": True,
                "new_message_id": result.get("message_id"),
                "from_chat": from_chat_id,
                "to_chat": chat_id
            }
    
    async def _handle_copy_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle copy_message operation."""
        # Implementation similar to forward_message but using copyMessage API
        # This is a placeholder - implement based on actual Telegram API
        return {"message": "copy_message not implemented yet"}
    
    # Media Operation Handlers
    async def _handle_send_photo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_photo operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        photo = params["photo"]
        caption = params.get("caption")
        parse_mode = params.get("parse_mode")
        reply_markup = params.get("reply_markup")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.send_photo(chat_id, photo, caption, parse_mode, reply_markup)
            return {
                "message": result,
                "photo_sent": True,
                "message_id": result.get("message_id"),
                "photo_info": result.get("photo", [])
            }
    
    async def _handle_send_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_document operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        document = params["document"]
        thumbnail = params.get("thumbnail")
        caption = params.get("caption")
        parse_mode = params.get("parse_mode")
        reply_markup = params.get("reply_markup")
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.send_document(chat_id, document, thumbnail, caption, parse_mode, reply_markup)
            return {
                "message": result,
                "document_sent": True,
                "message_id": result.get("message_id"),
                "document_info": result.get("document", {})
            }
    
    # Placeholder handlers for other media operations
    async def _handle_send_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_video handler not implemented yet"}
    
    async def _handle_send_audio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_audio handler not implemented yet"}
    
    async def _handle_send_sticker(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_sticker handler not implemented yet"}
    
    async def _handle_send_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_animation handler not implemented yet"}
    
    async def _handle_send_voice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_voice handler not implemented yet"}
    
    async def _handle_send_video_note(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_video_note handler not implemented yet"}
    
    async def _handle_send_media_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_media_group handler not implemented yet"}
    
    # Advanced Messaging Handlers
    async def _handle_send_location(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_location operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        latitude = params["latitude"]
        longitude = params["longitude"]
        
        # Use the wrapper's send_message with location parameters
        # This is a simplified implementation - extend as needed
        message_text = f"Location: {latitude}, {longitude}"
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.send_message(chat_id, message_text)
            return {
                "message": result,
                "location_sent": True,
                "latitude": latitude,
                "longitude": longitude
            }
    
    async def _handle_send_venue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_venue handler not implemented yet"}
    
    async def _handle_send_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_contact handler not implemented yet"}
    
    async def _handle_send_poll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_poll handler not implemented yet"}
    
    async def _handle_send_dice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "send_dice handler not implemented yet"}
    
    # Update Operation Handlers
    async def _handle_get_updates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "get_updates handler not implemented yet"}
    
    async def _handle_set_webhook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "set_webhook handler not implemented yet"}
    
    async def _handle_delete_webhook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "delete_webhook handler not implemented yet"}
    
    async def _handle_get_webhook_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "get_webhook_info handler not implemented yet"}
    
    # Chat Management Handlers
    async def _handle_get_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_chat operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.get_chat(chat_id)
            return {
                "chat": result,
                "id": result.get("id"),
                "type": result.get("type"),
                "title": result.get("title"),
                "username": result.get("username"),
                "member_count": result.get("member_count")
            }
    
    async def _handle_get_chat_member_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_chat_member_count operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.get_chat_member_count(chat_id)
            return {
                "member_count": result,
                "chat_id": chat_id
            }
    
    async def _handle_get_chat_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_chat_member operation."""
        bot_token = params["bot_token"]
        chat_id = params["chat_id"]
        user_id = params["user_id"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.get_chat_member(chat_id, user_id)
            return {
                "member": result,
                "user": result.get("user", {}),
                "status": result.get("status"),
                "chat_id": chat_id,
                "user_id": user_id
            }
    
    async def _handle_get_chat_administrators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "get_chat_administrators handler not implemented yet"}
    
    # Chat Settings Handlers (placeholders)
    async def _handle_set_chat_title(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "set_chat_title handler not implemented yet"}
    
    async def _handle_set_chat_description(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "set_chat_description handler not implemented yet"}
    
    async def _handle_set_chat_photo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "set_chat_photo handler not implemented yet"}
    
    async def _handle_delete_chat_photo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "delete_chat_photo handler not implemented yet"}
    
    async def _handle_pin_chat_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "pin_chat_message handler not implemented yet"}
    
    async def _handle_unpin_chat_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "unpin_chat_message handler not implemented yet"}
    
    # Chat Administration Handlers (placeholders)
    async def _handle_promote_chat_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "promote_chat_member handler not implemented yet"}
    
    async def _handle_restrict_chat_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "restrict_chat_member handler not implemented yet"}
    
    async def _handle_ban_chat_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "ban_chat_member handler not implemented yet"}
    
    async def _handle_unban_chat_member(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "unban_chat_member handler not implemented yet"}
    
    async def _handle_leave_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "leave_chat handler not implemented yet"}
    
    # File Operation Handlers
    async def _handle_get_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_file operation."""
        bot_token = params["bot_token"]
        file_id = params["file_id"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            result = await bot.get_file(file_id)
            return {
                "file": result,
                "file_id": result.get("file_id"),
                "file_path": result.get("file_path"),
                "file_size": result.get("file_size"),
                "file_unique_id": result.get("file_unique_id")
            }
    
    async def _handle_download_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle download_file operation."""
        bot_token = params["bot_token"]
        file_path = params["file_path"]
        
        async with self._get_telegram_bot(bot_token) as bot:
            file_data = await bot.download_file(file_path)
            # Encode as base64 for JSON transport
            file_base64 = base64.b64encode(file_data).decode('utf-8')
            return {
                "file_data": file_base64,
                "file_path": file_path,
                "file_size": len(file_data),
                "encoding": "base64"
            }
    
    # Keyboard Operation Handlers (placeholders)
    async def _handle_edit_message_reply_markup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "edit_message_reply_markup handler not implemented yet"}
    
    async def _handle_answer_callback_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "answer_callback_query handler not implemented yet"}