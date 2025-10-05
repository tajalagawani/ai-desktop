"""
Slack Node - Interacts with Slack API using the official SDK.
Provides access to sending messages, managing channels, and more.
"""

import logging
import json
import asyncio
import time
import os
import ssl
from typing import Dict, Any, List, Optional, Union, Tuple

# Import Slack SDK
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

try:
    from .base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from base_node import (
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

class SlackOperation:
    """Operations available on Slack API."""
    SEND_MESSAGE = "send_message"
    POST_MESSAGE = "post_message"
    UPLOAD_FILE = "upload_file"
    LIST_CHANNELS = "list_channels"
    LIST_USERS = "list_users"
    CREATE_CHANNEL = "create_channel"
    INVITE_USER = "invite_user"
    GET_CHANNEL_HISTORY = "get_channel_history"
    ADD_REACTION = "add_reaction"
    SEARCH_MESSAGES = "search_messages"

class SlackNode(BaseNode):
    """
    Node for interacting with Slack API using the official SDK.
    Provides functionality for messages, channels, and files.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.client = None
        self.async_client = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Slack node."""
        return NodeSchema(
            node_type="slack",
            version="1.0.0",
            description="Interacts with Slack API for messaging and workspace management",
            parameters=[
                # Basic parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Slack API",
                    required=True,
                    enum=[
                        SlackOperation.SEND_MESSAGE,
                        SlackOperation.POST_MESSAGE,
                        SlackOperation.UPLOAD_FILE,
                        SlackOperation.LIST_CHANNELS,
                        SlackOperation.LIST_USERS,
                        SlackOperation.CREATE_CHANNEL,
                        SlackOperation.INVITE_USER,
                        SlackOperation.GET_CHANNEL_HISTORY,
                        SlackOperation.ADD_REACTION,
                        SlackOperation.SEARCH_MESSAGES
                    ]
                ),
                NodeParameter(
                    name="token",
                    type=NodeParameterType.STRING,
                    description="Slack API token",
                    required=True
                ),
                
                # Message parameters
                NodeParameter(
                    name="channel",
                    type=NodeParameterType.STRING,
                    description="Channel ID or name to send message to",
                    required=False
                ),
                NodeParameter(
                    name="text",
                    type=NodeParameterType.STRING,
                    description="Text content of the message",
                    required=False
                ),
                NodeParameter(
                    name="blocks",
                    type=NodeParameterType.ARRAY,
                    description="Block Kit blocks for rich message formatting",
                    required=False
                ),
                NodeParameter(
                    name="attachments",
                    type=NodeParameterType.ARRAY,
                    description="Message attachments",
                    required=False
                ),
                NodeParameter(
                    name="thread_ts",
                    type=NodeParameterType.STRING,
                    description="Thread timestamp to reply to",
                    required=False
                ),
                
                # File upload parameters
                NodeParameter(
                    name="file_path",
                    type=NodeParameterType.STRING,
                    description="Path to file for upload",
                    required=False
                ),
                NodeParameter(
                    name="file_content",
                    type=NodeParameterType.STRING,
                    description="Content for file upload",
                    required=False
                ),
                NodeParameter(
                    name="filename",
                    type=NodeParameterType.STRING,
                    description="Name for the uploaded file",
                    required=False
                ),
                NodeParameter(
                    name="filetype",
                    type=NodeParameterType.STRING,
                    description="File type (e.g., 'text', 'pdf', etc.)",
                    required=False
                ),
                
                # Channel parameters
                NodeParameter(
                    name="channel_name",
                    type=NodeParameterType.STRING,
                    description="Name for new channel creation",
                    required=False
                ),
                NodeParameter(
                    name="is_private",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether the channel is private",
                    required=False,
                    default=False
                ),
                
                # User parameters
                NodeParameter(
                    name="user",
                    type=NodeParameterType.STRING,
                    description="User ID for operations that require it",
                    required=False
                ),
                
                # History parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Max number of items to return",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="oldest",
                    type=NodeParameterType.STRING,
                    description="Start of time range for history",
                    required=False
                ),
                NodeParameter(
                    name="latest",
                    type=NodeParameterType.STRING,
                    description="End of time range for history",
                    required=False
                ),
                
                # Reaction parameters
                NodeParameter(
                    name="reaction",
                    type=NodeParameterType.STRING,
                    description="Emoji name for reaction",
                    required=False
                ),
                NodeParameter(
                    name="timestamp",
                    type=NodeParameterType.STRING,
                    description="Timestamp of message to add reaction to",
                    required=False
                ),
                
                # Search parameters
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query",
                    required=False
                ),
                NodeParameter(
                    name="sort",
                    type=NodeParameterType.STRING,
                    description="Sort direction",
                    required=False,
                    enum=["timestamp", "score"],
                    default="timestamp"
                ),
                NodeParameter(
                    name="sort_dir",
                    type=NodeParameterType.STRING,
                    description="Sort direction",
                    required=False,
                    enum=["asc", "desc"],
                    default="desc"
                ),
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "ts": NodeParameterType.STRING,
                "channel": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["slack", "messaging", "collaboration", "integration"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API token
        if not params.get("token"):
            raise NodeValidationError("Slack API token is required")
            
        # Validate based on operation
        if operation in [SlackOperation.SEND_MESSAGE, SlackOperation.POST_MESSAGE]:
            if not params.get("channel"):
                raise NodeValidationError("Channel is required for sending messages")
                
            if not params.get("text") and not params.get("blocks") and not params.get("attachments"):
                raise NodeValidationError("One of text, blocks, or attachments is required for sending messages")
                
        elif operation == SlackOperation.UPLOAD_FILE:
            if not params.get("channel"):
                raise NodeValidationError("Channel is required for file upload")
                
            if not params.get("file_path") and not params.get("file_content"):
                raise NodeValidationError("Either file_path or file_content is required for file upload")
                
        elif operation == SlackOperation.CREATE_CHANNEL:
            if not params.get("channel_name"):
                raise NodeValidationError("Channel name is required for channel creation")
                
        elif operation == SlackOperation.INVITE_USER:
            if not params.get("channel") or not params.get("user"):
                raise NodeValidationError("Both channel and user are required for inviting a user")
                
        elif operation == SlackOperation.GET_CHANNEL_HISTORY:
            if not params.get("channel"):
                raise NodeValidationError("Channel is required for getting channel history")
                
        elif operation == SlackOperation.ADD_REACTION:
            if not params.get("channel") or not params.get("timestamp") or not params.get("reaction"):
                raise NodeValidationError("Channel, timestamp, and reaction are required for adding reactions")
                
        elif operation == SlackOperation.SEARCH_MESSAGES:
            if not params.get("query"):
                raise NodeValidationError("Query is required for searching messages")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Slack node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize Slack clients (both sync and async) with SSL context to fix certificate issues
            token = validated_data.get("token")
            # Create a custom SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            self.client = WebClient(token=token, ssl=ssl_context)
            self.async_client = AsyncWebClient(token=token, ssl=ssl_context)
            
            # Execute the appropriate operation
            if operation == SlackOperation.SEND_MESSAGE:
                return await self._operation_send_message(validated_data)
            elif operation == SlackOperation.POST_MESSAGE:
                return await self._operation_post_message(validated_data)
            elif operation == SlackOperation.UPLOAD_FILE:
                return await self._operation_upload_file(validated_data)
            elif operation == SlackOperation.LIST_CHANNELS:
                return await self._operation_list_channels(validated_data)
            elif operation == SlackOperation.LIST_USERS:
                return await self._operation_list_users(validated_data)
            elif operation == SlackOperation.CREATE_CHANNEL:
                return await self._operation_create_channel(validated_data)
            elif operation == SlackOperation.INVITE_USER:
                return await self._operation_invite_user(validated_data)
            elif operation == SlackOperation.GET_CHANNEL_HISTORY:
                return await self._operation_get_channel_history(validated_data)
            elif operation == SlackOperation.ADD_REACTION:
                return await self._operation_add_reaction(validated_data)
            elif operation == SlackOperation.SEARCH_MESSAGES:
                return await self._operation_search_messages(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "ts": None,
                    "channel": None
                }
                
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": None
            }
        except Exception as e:
            error_message = f"Error in Slack node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": None
            }
    
    # -------------------------
    # Operation Methods
    # -------------------------
    
    async def _operation_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a Slack channel using the chat.postMessage API.
        
        Args:
            params: Message parameters
            
        Returns:
            Message sending results
        """
        # Extract parameters
        channel = params.get("channel")
        text = params.get("text", "")
        blocks = params.get("blocks")
        attachments = params.get("attachments")
        thread_ts = params.get("thread_ts")
        
        # Build request args
        request_args = {
            "channel": channel,
            "text": text
        }
        
        # Add optional parameters
        if blocks:
            request_args["blocks"] = blocks
        if attachments:
            request_args["attachments"] = attachments
        if thread_ts:
            request_args["thread_ts"] = thread_ts
        
        try:
            # Send message using the async client
            response = await self.async_client.chat_postMessage(**request_args)
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": result.get("ts"),
                "channel": result.get("channel")
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": channel
            }
    
    async def _operation_post_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a Slack channel using the chat.postMessage API.
        This is an alias for send_message for backward compatibility.
        
        Args:
            params: Message parameters
            
        Returns:
            Message sending results
        """
        return await self._operation_send_message(params)
    
    async def _operation_upload_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a file to a Slack channel.
        
        Args:
            params: File parameters
            
        Returns:
            File upload results
        """
        # Extract parameters
        channel = params.get("channel")
        file_path = params.get("file_path")
        file_content = params.get("file_content")
        filename = params.get("filename")
        filetype = params.get("filetype")
        thread_ts = params.get("thread_ts")
        title = params.get("text", "File Upload")
        
        # Build request args
        request_args = {
            "channels": channel,
            "title": title
        }
        
        # Add file source
        if file_path:
            request_args["file"] = file_path
        elif file_content:
            request_args["content"] = file_content
            
            # Filename is required when uploading content
            if filename:
                request_args["filename"] = filename
            else:
                request_args["filename"] = "file.txt"
        
        # Add optional parameters
        if filetype:
            request_args["filetype"] = filetype
        if thread_ts:
            request_args["thread_ts"] = thread_ts
        
        try:
            # Upload file using the async client
            response = await self.async_client.files_upload_v2(**request_args)
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": result.get("file", {}).get("timestamp"),
                "channel": channel
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": channel
            }
    
    async def _operation_list_channels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List channels in the workspace.
        
        Args:
            params: Listing parameters
            
        Returns:
            Channel listing results
        """
        # Extract parameters
        limit = params.get("limit", 100)
        
        try:
            # List channels using the async client
            response = await self.async_client.conversations_list(
                limit=limit,
                types="public_channel,private_channel"
            )
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": None,
                "channel": None
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": None
            }
    
    async def _operation_list_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List users in the workspace.
        
        Args:
            params: Listing parameters
            
        Returns:
            User listing results
        """
        # Extract parameters
        limit = params.get("limit", 100)
        
        try:
            # List users using the async client
            response = await self.async_client.users_list(limit=limit)
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": None,
                "channel": None
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": None
            }
    
    async def _operation_create_channel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new channel in the workspace.
        
        Args:
            params: Channel creation parameters
            
        Returns:
            Channel creation results
        """
        # Extract parameters
        channel_name = params.get("channel_name")
        is_private = params.get("is_private", False)
        
        try:
            # Create channel using the async client
            response = await self.async_client.conversations_create(
                name=channel_name,
                is_private=is_private
            )
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": None,
                "channel": result.get("channel", {}).get("id")
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": None
            }
    
    async def _operation_invite_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invite a user to a channel.
        
        Args:
            params: Invitation parameters
            
        Returns:
            Invitation results
        """
        # Extract parameters
        channel = params.get("channel")
        user = params.get("user")
        
        try:
            # Invite user using the async client
            response = await self.async_client.conversations_invite(
                channel=channel,
                users=[user]
            )
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": None,
                "channel": channel
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": channel
            }
    
    async def _operation_get_channel_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get message history for a channel.
        
        Args:
            params: History parameters
            
        Returns:
            Channel history results
        """
        # Extract parameters
        channel = params.get("channel")
        limit = params.get("limit", 100)
        oldest = params.get("oldest")
        latest = params.get("latest")
        
        # Build request args
        request_args = {
            "channel": channel,
            "limit": limit
        }
        
        # Add optional parameters
        if oldest:
            request_args["oldest"] = oldest
        if latest:
            request_args["latest"] = latest
        
        try:
            # Get history using the async client
            response = await self.async_client.conversations_history(**request_args)
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": None,
                "channel": channel
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": channel
            }
    
    async def _operation_add_reaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a reaction emoji to a message.
        
        Args:
            params: Reaction parameters
            
        Returns:
            Reaction results
        """
        # Extract parameters
        channel = params.get("channel")
        timestamp = params.get("timestamp")
        reaction = params.get("reaction")
        
        try:
            # Add reaction using the async client
            response = await self.async_client.reactions_add(
                channel=channel,
                timestamp=timestamp,
                name=reaction
            )
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": timestamp,
                "channel": channel
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": timestamp,
                "channel": channel
            }
    
    async def _operation_search_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for messages in the workspace.
        
        Args:
            params: Search parameters
            
        Returns:
            Search results
        """
        # Extract parameters
        query = params.get("query")
        sort = params.get("sort", "timestamp")
        sort_dir = params.get("sort_dir", "desc")
        limit = params.get("limit", 100)
        
        try:
            # Search messages using the async client
            response = await self.async_client.search_messages(
                query=query,
                sort=sort,
                sort_dir=sort_dir,
                count=limit
            )
            
            # Process response
            result = response.data
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "error": None,
                "ts": None,
                "channel": None
            }
            
        except SlackApiError as e:
            error_message = f"Slack API error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "ts": None,
                "channel": None
            }


# Main test function for Slack Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Slack Node Test Suite ===")
        
        # Get API token from environment or user input
        token = os.environ.get("SLACK_API_TOKEN")
        if not token:
            token = input("Enter Slack API token: ")
            if not token:
                print("API token is required for testing")
                return
        
        # Get channel ID for testing
        channel = os.environ.get("SLACK_TEST_CHANNEL")
        if not channel:
            channel = input("Enter Slack channel ID or name for testing: ")
            if not channel:
                print("Channel ID is required for testing")
                return
        
        # Create an instance of the Slack Node
        node = SlackNode()
        
        # Test cases - only run if token provided
        test_cases = [
            {
        "name": "Send Message",
        "params": {
            "operation": SlackOperation.SEND_MESSAGE,
            "token": token,
            "channel": "C08FYUWC5NW",  # Use the channel ID
            "text": "Hello from Slack Node test! Current time: " + time.strftime("%Y-%m-%d %H:%M:%S")
        },
            "expected_status": "success"
        },
            {
                "name": "List Channels",
                "params": {
                    "operation": SlackOperation.LIST_CHANNELS,
                    "token": token,
                    "limit": 10
                },
                "expected_status": "success"
            },
            {
                "name": "List Users",
                "params": {
                    "operation": SlackOperation.LIST_USERS,
                    "token": token,
                    "limit": 10
                },
                "expected_status": "success"
            },
            {
                "name": "Get Channel History",
                "params": {
                    "operation": SlackOperation.GET_CHANNEL_HISTORY,
                    "token": token,
                    "channel": "C08FYUWC5NW",  # Use the exact channel ID here
                    "limit": 5
                },
                "expected_status": "success"
            }
        ]
        
        # Run all test cases with a delay between tests
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
                    if result["result"]:
                        print(f"Response preview: {str(result['result'])[:150]}...")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests to avoid rate limiting
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        # Optional manual test for file upload
        run_file_test = input("\nRun file upload test? (y/n): ").lower() == 'y'
        if run_file_test:
            print("\n=== Manual Test: File Upload ===")
            
            # Create a temporary test file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp:
                temp.write("This is a test file created by the Slack Node test suite.\n")
                temp.write(f"Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                temp_path = temp.name
            
            print(f"Created test file at: {temp_path}")
            
            # Upload the file
            file_result = await node.execute({
                "params": {
                    "operation": SlackOperation.UPLOAD_FILE,
                    "token": token,
                    "channel": channel,
                    "file_path": temp_path,
                    "text": "Test file upload from Slack Node"
                }
            })
            
            # Clean up the temp file
            os.unlink(temp_path)
            
            if file_result["status"] == "success":
                print("✅ File upload test successful")
                print(f"Response preview: {str(file_result['result'])[:150]}...")
            else:
                print(f"❌ File upload test failed: {file_result.get('error')}")
        
        # Optional manual test for creating a channel
        run_create_channel = input("\nRun channel creation test? (y/n): ").lower() == 'y'
        if run_create_channel:
            print("\n=== Manual Test: Create Channel ===")
            
            # Generate a unique channel name with timestamp
            timestamp = int(time.time())
            channel_name = f"test-channel-{timestamp}"
            
            # Create the channel
            channel_result = await node.execute({
                "params": {
                    "operation": SlackOperation.CREATE_CHANNEL,
                    "token": token,
                    "channel_name": channel_name,
                    "is_private": False
                }
            })
            
            if channel_result["status"] == "success":
                print(f"✅ Channel creation test successful: #{channel_name}")
                print(f"Response preview: {str(channel_result['result'])[:150]}...")
            else:
                print(f"❌ Channel creation test failed: {channel_result.get('error')}")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())
    
# Register with NodeRegistry
# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("slack", SlackNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register SlackNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")