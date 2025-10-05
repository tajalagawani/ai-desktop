# === File: act/nodes/telegram_node.py ===

import logging
import json
import asyncio
import os
from typing import Dict, Any, List, Optional, Union, Tuple, BinaryIO
import httpx

# Assuming base_node.py is in the same directory or accessible via the package structure
try:
    from base_node import (
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
    class NodeValidationError(Exception): pass
    class NodeExecutionError(Exception): pass
    class NodeParameterType: ANY="any"; STRING="string"; BOOLEAN="boolean"; NUMBER="number"; ARRAY="array"; OBJECT="object"; SECRET="secret"; FILE="file" # Added FILE
    class NodeParameter:
        def __init__(self, name, type, description, required=True, default=None, enum=None):
            self.name = name; self.type = type; self.description = description; self.required = required; self.default = default; self.enum = enum
    class NodeSchema:
        def __init__(self, node_type, version, description, parameters, outputs, tags=None, author=None):
            self.node_type=node_type; self.version=version; self.description=description; self.parameters=parameters; self.outputs=outputs; self.tags=tags; self.author=author
    class BaseNode:
        def get_schema(self): raise NotImplementedError
        async def execute(self, data): raise NotImplementedError
        def validate_schema(self, data): return data.get("params", {})
        def handle_error(self, error, context=""):
             logger = logging.getLogger(__name__)
             logger.error(f"Error in {context}: {error}", exc_info=True)
             return {"status": "error", "message": f"Error in {context}: {error}", "error_type": type(error).__name__}

# --- Node Logger ---
logger = logging.getLogger(__name__)

class TelegramOperation:
    """Operations available for the Telegram Bot API."""
    GET_ME = "getMe"
    SEND_MESSAGE = "sendMessage"
    FORWARD_MESSAGE = "forwardMessage"
    COPY_MESSAGE = "copyMessage"
    SEND_PHOTO = "sendPhoto"
    SEND_AUDIO = "sendAudio"
    SEND_DOCUMENT = "sendDocument"
    SEND_VIDEO = "sendVideo"
    SEND_ANIMATION = "sendAnimation"
    SEND_VOICE = "sendVoice"
    SEND_VIDEO_NOTE = "sendVideoNote"
    SEND_MEDIA_GROUP = "sendMediaGroup"
    SEND_LOCATION = "sendLocation"
    EDIT_MESSAGE_LIVE_LOCATION = "editMessageLiveLocation"
    STOP_MESSAGE_LIVE_LOCATION = "stopMessageLiveLocation"
    SEND_VENUE = "sendVenue"
    SEND_CONTACT = "sendContact"
    SEND_POLL = "sendPoll"
    SEND_DICE = "sendDice"
    SEND_CHAT_ACTION = "sendChatAction"
    GET_USER_PROFILE_PHOTOS = "getUserProfilePhotos"
    GET_FILE = "getFile"
    BAN_CHAT_MEMBER = "banChatMember"
    UNBAN_CHAT_MEMBER = "unbanChatMember"
    RESTRICT_CHAT_MEMBER = "restrictChatMember"
    PROMOTE_CHAT_MEMBER = "promoteChatMember"
    SET_CHAT_ADMINISTRATOR_CUSTOM_TITLE = "setChatAdministratorCustomTitle"
    BAN_CHAT_SENDER_CHAT = "banChatSenderChat"
    UNBAN_CHAT_SENDER_CHAT = "unbanChatSenderChat"
    SET_CHAT_PERMISSIONS = "setChatPermissions"
    EXPORT_CHAT_INVITE_LINK = "exportChatInviteLink"
    CREATE_CHAT_INVITE_LINK = "createChatInviteLink"
    EDIT_CHAT_INVITE_LINK = "editChatInviteLink"
    REVOKE_CHAT_INVITE_LINK = "revokeChatInviteLink"
    SET_CHAT_PHOTO = "setChatPhoto"
    DELETE_CHAT_PHOTO = "deleteChatPhoto"
    SET_CHAT_TITLE = "setChatTitle"
    SET_CHAT_DESCRIPTION = "setChatDescription"
    PIN_CHAT_MESSAGE = "pinChatMessage"
    UNPIN_CHAT_MESSAGE = "unpinChatMessage"
    UNPIN_ALL_CHAT_MESSAGES = "unpinAllChatMessages"
    LEAVE_CHAT = "leaveChat"
    GET_CHAT = "getChat"
    GET_CHAT_ADMINISTRATORS = "getChatAdministrators"
    GET_CHAT_MEMBERS_COUNT = "getChatMembersCount"
    GET_CHAT_MEMBER = "getChatMember"
    SET_CHAT_STICKER_SET = "setChatStickerSet"
    DELETE_CHAT_STICKER_SET = "deleteChatStickerSet"
    ANSWER_CALLBACK_QUERY = "answerCallbackQuery"
    SET_MY_COMMANDS = "setMyCommands"
    DELETE_MY_COMMANDS = "deleteMyCommands"
    GET_MY_COMMANDS = "getMyCommands"
    EDIT_MESSAGE_TEXT = "editMessageText"
    EDIT_MESSAGE_CAPTION = "editMessageCaption"
    EDIT_MESSAGE_MEDIA = "editMessageMedia"
    EDIT_MESSAGE_REPLY_MARKUP = "editMessageReplyMarkup"
    STOP_POLL = "stopPoll"
    DELETE_MESSAGE = "deleteMessage"
    GET_UPDATES = "getUpdates"
    SET_WEBHOOK = "setWebhook"
    DELETE_WEBHOOK = "deleteWebhook"
    GET_WEBHOOK_INFO = "getWebhookInfo"

class TelegramNode(BaseNode):
    _BASE_API_URL = "https://api.telegram.org/bot"

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            node_type="telegram",
            version="1.0.0",
            description="Interacts with the Telegram Bot API.",
            parameters=[
                NodeParameter(name="bot_token", type=NodeParameterType.SECRET, description="Telegram Bot Token.", required=True),
                NodeParameter(name="operation", type=NodeParameterType.STRING, description="Telegram API method to call.", required=True, enum=[op for op in dir(TelegramOperation) if not op.startswith('_')]),

                # Common Parameters
                NodeParameter(name="chat_id", type=NodeParameterType.ANY, description="Unique identifier for the target chat or username of the target channel (e.g., @channelusername or 123456789).", required=False),
                NodeParameter(name="message_id", type=NodeParameterType.NUMBER, description="Identifier of the message to manipulate.", required=False),
                NodeParameter(name="user_id", type=NodeParameterType.NUMBER, description="Unique identifier of the target user.", required=False),

                # Message Sending Parameters
                NodeParameter(name="text", type=NodeParameterType.STRING, description="Text of the message.", required=False),
                NodeParameter(name="parse_mode", type=NodeParameterType.STRING, enum=["MarkdownV2", "HTML", "Markdown"], description="Formatting style for the message text.", required=False),
                NodeParameter(name="entities", type=NodeParameterType.ARRAY, description="JSON-serialized list of special entities that appear in message text.", required=False),
                NodeParameter(name="disable_web_page_preview", type=NodeParameterType.BOOLEAN, description="Disables link previews for links in this message.", required=False),
                NodeParameter(name="disable_notification", type=NodeParameterType.BOOLEAN, description="Sends the message silently.", required=False),
                NodeParameter(name="protect_content", type=NodeParameterType.BOOLEAN, description="Protects the contents of the sent message from forwarding and saving.", required=False),
                NodeParameter(name="reply_to_message_id", type=NodeParameterType.NUMBER, description="ID of the original message if this is a reply.", required=False),
                NodeParameter(name="allow_sending_without_reply", type=NodeParameterType.BOOLEAN, description="Send message even if the replied-to message is not found.", required=False),
                NodeParameter(name="reply_markup", type=NodeParameterType.OBJECT, description="JSON-serialized object for an inline keyboard, custom reply keyboard, etc.", required=False),

                # File/Media Parameters
                NodeParameter(name="photo", type=NodeParameterType.ANY, description="Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers, or a file path (string) for a new photo, or a URL (string).", required=False), # Can be file_id, URL, or local path
                NodeParameter(name="audio", type=NodeParameterType.ANY, description="Audio file to send.", required=False),
                NodeParameter(name="document", type=NodeParameterType.ANY, description="Document to send.", required=False),
                NodeParameter(name="video", type=NodeParameterType.ANY, description="Video to send.", required=False),
                NodeParameter(name="animation", type=NodeParameterType.ANY, description="Animation file (GIF or H.264/MPEG-4 AVC video without sound).", required=False),
                NodeParameter(name="voice", type=NodeParameterType.ANY, description="Voice message to send.", required=False),
                NodeParameter(name="video_note", type=NodeParameterType.ANY, description="Video note to send.", required=False),
                NodeParameter(name="caption", type=NodeParameterType.STRING, description="Caption for the media (0-1024 characters).", required=False),
                NodeParameter(name="caption_entities", type=NodeParameterType.ARRAY, description="JSON-serialized list of special entities that appear in the caption.", required=False),
                NodeParameter(name="duration", type=NodeParameterType.NUMBER, description="Duration of sent audio/video in seconds.", required=False),
                NodeParameter(name="performer", type=NodeParameterType.STRING, description="Performer of the audio.", required=False),
                NodeParameter(name="title", type=NodeParameterType.STRING, description="Title of the audio/document.", required=False),
                NodeParameter(name="thumb", type=NodeParameterType.ANY, description="Thumbnail of the file sent.", required=False), # Can be file_id, URL, or local path
                NodeParameter(name="width", type=NodeParameterType.NUMBER, description="Video width.", required=False),
                NodeParameter(name="height", type=NodeParameterType.NUMBER, description="Video height.", required=False),
                NodeParameter(name="supports_streaming", type=NodeParameterType.BOOLEAN, description="Pass True, if the uploaded video is suitable for streaming.", required=False),
                NodeParameter(name="media", type=NodeParameterType.ARRAY, description="A JSON-serialized list describing messages to be sent, must include 2-10 items for sendMediaGroup.", required=False), # For sendMediaGroup

                # Location Parameters
                NodeParameter(name="latitude", type=NodeParameterType.NUMBER, description="Latitude of the location.", required=False),
                NodeParameter(name="longitude", type=NodeParameterType.NUMBER, description="Longitude of the location.", required=False),
                NodeParameter(name="horizontal_accuracy", type=NodeParameterType.NUMBER, description="The radius of uncertainty for the location, measured in meters; 0-1500", required=False),
                NodeParameter(name="live_period", type=NodeParameterType.NUMBER, description="Period in seconds for which the location will be updated (see Live Locations). Should be between 60 and 86400.", required=False),
                NodeParameter(name="heading", type=NodeParameterType.NUMBER, description="For live locations, a direction in which the user is moving, in degrees. Must be between 1 and 360.", required=False),
                NodeParameter(name="proximity_alert_radius", type=NodeParameterType.NUMBER, description="For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters. Must be between 1 and 100000.", required=False),

                # Venue Parameters
                NodeParameter(name="address", type=NodeParameterType.STRING, description="Address of the venue.", required=False),
                NodeParameter(name="foursquare_id", type=NodeParameterType.STRING, description="Foursquare identifier of the venue.", required=False),
                NodeParameter(name="foursquare_type", type=NodeParameterType.STRING, description="Foursquare type of the venue.", required=False),
                NodeParameter(name="google_place_id", type=NodeParameterType.STRING, description="Google Places identifier of the venue.", required=False),
                NodeParameter(name="google_place_type", type=NodeParameterType.STRING, description="Google Places type of the venue.", required=False),

                # Contact Parameters
                NodeParameter(name="phone_number", type=NodeParameterType.STRING, description="Contact's phone number.", required=False),
                NodeParameter(name="first_name", type=NodeParameterType.STRING, description="Contact's first name.", required=False),
                NodeParameter(name="last_name", type=NodeParameterType.STRING, description="Contact's last name.", required=False),
                NodeParameter(name="vcard", type=NodeParameterType.STRING, description="Additional data about the contact in vCard format.", required=False),

                # Poll Parameters
                NodeParameter(name="question", type=NodeParameterType.STRING, description="Poll question, 1-300 characters.", required=False),
                NodeParameter(name="options", type=NodeParameterType.ARRAY, description="A JSON-serialized list of answer options, 2-10 strings 1-100 characters each.", required=False), # Array of strings
                NodeParameter(name="is_anonymous", type=NodeParameterType.BOOLEAN, description="True, if the poll needs to be anonymous.", required=False, default=True),
                NodeParameter(name="type", type=NodeParameterType.STRING, enum=["quiz", "regular"], description="Poll type, “quiz” or “regular”.", required=False, default="regular"),
                NodeParameter(name="allows_multiple_answers", type=NodeParameterType.BOOLEAN, description="True, if the poll allows multiple answers.", required=False),
                NodeParameter(name="correct_option_id", type=NodeParameterType.NUMBER, description="0-based identifier of the correct answer option for a quiz.", required=False),
                NodeParameter(name="explanation", type=NodeParameterType.STRING, description="Text that is shown when a user chooses an incorrect answer or taps on the lamp icon in a quiz-style poll.", required=False),
                NodeParameter(name="explanation_parse_mode", type=NodeParameterType.STRING, enum=["MarkdownV2", "HTML", "Markdown"], description="Mode for parsing entities in the explanation.", required=False),
                NodeParameter(name="explanation_entities", type=NodeParameterType.ARRAY, description="JSON-serialized list of special entities that appear in the poll explanation.", required=False),
                NodeParameter(name="open_period", type=NodeParameterType.NUMBER, description="Amount of time in seconds the poll will be active after creation.", required=False),
                NodeParameter(name="close_date", type=NodeParameterType.NUMBER, description="Point in time (Unix timestamp) when the poll will be automatically closed.", required=False),
                NodeParameter(name="is_closed", type=NodeParameterType.BOOLEAN, description="Pass True, if the poll needs to be immediately closed.", required=False),

                # Dice Parameters
                NodeParameter(name="emoji", type=NodeParameterType.STRING, enum=["🎲", "🎯", "🏀", "⚽", "🎳", "🎰"], description="Emoji on which the dice throw animation is based.", required=False),

                # Chat Action Parameters
                NodeParameter(name="action", type=NodeParameterType.STRING, enum=["typing", "upload_photo", "record_video", "upload_video", "record_voice", "upload_voice", "upload_document", "choose_sticker", "find_location", "record_video_note", "upload_video_note"], description="Type of action to broadcast.", required=False),

                # UserProfilePhotos Parameters
                NodeParameter(name="offset", type=NodeParameterType.NUMBER, description="Sequential number of the first photo to be returned. By default, all photos are returned.", required=False),
                NodeParameter(name="limit", type=NodeParameterType.NUMBER, description="Limits the number of photos to be returned. Values between 1-100 are accepted. Defaults to 100.", required=False),

                # File Parameters
                NodeParameter(name="file_id", type=NodeParameterType.STRING, description="File identifier to get info about.", required=False),

                # Chat Member Management Parameters
                NodeParameter(name="until_date", type=NodeParameterType.NUMBER, description="Date when the user will be unbanned/unrestricted, unix time. If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever.", required=False),
                NodeParameter(name="revoke_messages", type=NodeParameterType.BOOLEAN, description="Pass True to delete all messages from the chat for the user that is being removed.", required=False), # for banChatMember
                NodeParameter(name="permissions", type=NodeParameterType.OBJECT, description="A JSON-serialized object for new user permissions (ChatPermissions).", required=False), # for restrictChatMember, setChatPermissions
                NodeParameter(name="can_be_edited",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_manage_chat",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_post_messages",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_edit_messages",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_delete_messages",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_manage_video_chats",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_restrict_members",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_promote_members",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_change_info",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_invite_users",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_pin_messages",type=NodeParameterType.BOOLEAN, required=False),
                NodeParameter(name="can_manage_topics",type=NodeParameterType.BOOLEAN, required=False), # promoteChatMember specific
                NodeParameter(name="is_anonymous", type=NodeParameterType.BOOLEAN, required=False), # promoteChatMember specific
                NodeParameter(name="custom_title", type=NodeParameterType.STRING, description="New custom title for the administrator; 0-16 characters.", required=False),
                NodeParameter(name="sender_chat_id", type=NodeParameterType.NUMBER, description="Unique identifier of the target sender chat.", required=False),

                # Chat Management Parameters
                NodeParameter(name="invite_link", type=NodeParameterType.STRING, description="The invite link to revoke or edit.", required=False),
                NodeParameter(name="name", type=NodeParameterType.STRING, description="Invite link name; 0-32 characters", required=False), # for createChatInviteLink
                NodeParameter(name="expire_date", type=NodeParameterType.NUMBER, description="Point in time (Unix timestamp) when the link will expire.", required=False),
                NodeParameter(name="member_limit", type=NodeParameterType.NUMBER, description="Maximum number of users that can be members of the chat simultaneously after joining the chat via this invite link; 1-99999.", required=False),
                NodeParameter(name="creates_join_request", type=NodeParameterType.BOOLEAN, description="True, if users joining the chat via the link need to be approved by chat administrators.", required=False),
                NodeParameter(name="sticker_set_name", type=NodeParameterType.STRING, description="Name of the sticker set to be set as the group sticker set.", required=False),

                # Callback Query Parameters
                NodeParameter(name="callback_query_id", type=NodeParameterType.STRING, description="Unique identifier for the query to be answered.", required=False),
                NodeParameter(name="show_alert", type=NodeParameterType.BOOLEAN, description="If true, an alert will be shown by the client instead of a notification at the top of the chat screen.", required=False),
                NodeParameter(name="url", type=NodeParameterType.STRING, description="URL that will be opened by the user's client.", required=False), # for answerCallbackQuery, setWebhook
                NodeParameter(name="cache_time", type=NodeParameterType.NUMBER, description="The maximum period in seconds for which the result of the callback query may be cached client-side.", required=False),

                # Bot Commands Parameters
                NodeParameter(name="commands", type=NodeParameterType.ARRAY, description="A JSON-serialized list of BotCommand objects to set.", required=False), # Array of BotCommand objects
                NodeParameter(name="scope", type=NodeParameterType.OBJECT, description="A JSON-serialized object describing the scope of users for which the commands are relevant.", required=False), # BotCommandScope object
                NodeParameter(name="language_code", type=NodeParameterType.STRING, description="A two-letter ISO 639-1 language code.", required=False),

                # Webhook Parameters
                NodeParameter(name="certificate", type=NodeParameterType.ANY, description="Public key certificate to upload.", required=False), # Local file path
                NodeParameter(name="ip_address", type=NodeParameterType.STRING, description="The fixed IP address which will be used to send webhook requests.", required=False),
                NodeParameter(name="max_connections", type=NodeParameterType.NUMBER, description="Maximum allowed number of simultaneous HTTPS connections to the webhook.", required=False),
                NodeParameter(name="allowed_updates", type=NodeParameterType.ARRAY, description="A JSON-serialized list of the update types you want your bot to receive.", required=False), # Array of strings
                NodeParameter(name="drop_pending_updates", type=NodeParameterType.BOOLEAN, description="Pass True to drop all pending updates.", required=False),
                NodeParameter(name="secret_token", type=NodeParameterType.STRING, description="A secret token to be sent in a header “X-Telegram-Bot-Api-Secret-Token” in every webhook request.", required=False),

                # GetUpdates Parameters
                # offset, limit already defined
                NodeParameter(name="timeout", type=NodeParameterType.NUMBER, description="Timeout in seconds for long polling.", required=False),
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY, # The 'result' field from Telegram's JSON response
                "ok": NodeParameterType.BOOLEAN, # Telegram's 'ok' field
                "description": NodeParameterType.STRING, # Telegram's 'description' field for errors
                "error_code": NodeParameterType.NUMBER, # Telegram's 'error_code' field
                "response_headers": NodeParameterType.OBJECT,
                "error_message": NodeParameterType.STRING # For client-side errors
            },
            tags=["communication", "telegram", "bot", "messaging", "social"],
            author="ACT Framework"
        )

    def _clean_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes None values and serializes JSON objects/arrays if needed."""
        cleaned = {}
        for k, v in params.items():
            if v is not None:
                if isinstance(v, (dict, list)) and k in ["reply_markup", "entities", "caption_entities", "options", "permissions", "commands", "scope", "media", "allowed_updates"]:
                    try:
                        cleaned[k] = json.dumps(v)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Could not JSON serialize parameter '{k}': {v}. Error: {e}")
                        # Decide: raise error or send as is / skip? For now, skip.
                        continue
                else:
                    cleaned[k] = v
        return cleaned

    async def _send_request(
        self,
        bot_token: str,
        method: str,
        data_payload: Optional[Dict[str, Any]] = None,
        files_payload: Optional[Dict[str, Tuple[str, BinaryIO, str]]] = None
    ) -> Dict[str, Any]:
        url = f"{self._BASE_API_URL}{bot_token}/{method}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                if files_payload: # Multipart for file uploads
                    response = await client.post(url, data=self._clean_params(data_payload or {}), files=files_payload)
                else: # Form-urlencoded for most other requests
                    response = await client.post(url, data=self._clean_params(data_payload or {}))

                return self._format_telegram_response(response)
            except httpx.RequestError as e:
                logger.error(f"HTTPX RequestError for {method}: {e}", exc_info=True)
                return {"status": "error", "ok": False, "error_message": f"HTTP request failed: {e}"}
            except Exception as e:
                logger.error(f"Unexpected error during Telegram request for {method}: {e}", exc_info=True)
                return {"status": "error", "ok": False, "error_message": f"Internal error: {e}"}

    def _format_telegram_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response from Telegram. Status: {response.status_code}, Content: {response.text[:500]}")
            return {
                "status": "error", "ok": False, "error_code": response.status_code,
                "description": "Invalid JSON response from Telegram.",
                "response_headers": dict(response.headers),
                "error_message": "Invalid JSON response."
            }

        output = {
            "status": "success" if response_json.get("ok") else "error",
            "ok": response_json.get("ok"),
            "result": response_json.get("result"),
            "description": response_json.get("description"),
            "error_code": response_json.get("error_code"),
            "response_headers": dict(response.headers),
            "error_message": None if response_json.get("ok") else response_json.get("description")
        }
        if not output["ok"]:
             logger.error(f"Telegram API Error: Code={output['error_code']}, Desc={output['description']}")
        return output

    def _prepare_file_payload(self, params: Dict[str, Any], file_param_names: List[str]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Separates file parameters for multipart upload and prepares them.
        Returns (data_payload, files_payload)
        """
        data_payload = params.copy()
        files_payload = {}

        for param_name in file_param_names:
            file_value = data_payload.pop(param_name, None)
            if file_value is not None:
                if isinstance(file_value, str) and os.path.isfile(file_value): # Local file path
                    try:
                        file_name = os.path.basename(file_value)
                        # Note: httpx expects (filename, file_object, content_type)
                        # We'll let httpx infer content_type or user can specify if needed via another param
                        files_payload[param_name] = (file_name, open(file_value, "rb"), None)
                    except IOError as e:
                        raise NodeValidationError(f"Could not open file '{file_value}' for parameter '{param_name}': {e}")
                elif isinstance(file_value, str): # Assume file_id or URL
                    data_payload[param_name] = file_value # Keep as string in data payload
                else:
                    raise NodeValidationError(f"Invalid type for file parameter '{param_name}': {type(file_value)}. Expected file path, file_id, or URL string.")
        return data_payload, files_payload if files_payload else None


    async def validate_custom(self, params: Dict[str, Any]) -> None:
        """Custom validation based on the operation type."""
        operation = params.get("operation")
        if not operation:
            raise NodeValidationError("Parameter 'operation' is required.")

        required_for_op = {
            TelegramOperation.SEND_MESSAGE: ["chat_id", "text"],
            TelegramOperation.FORWARD_MESSAGE: ["chat_id", "from_chat_id", "message_id"],
            TelegramOperation.COPY_MESSAGE: ["chat_id", "from_chat_id", "message_id"],
            TelegramOperation.SEND_PHOTO: ["chat_id", "photo"],
            TelegramOperation.SEND_AUDIO: ["chat_id", "audio"],
            TelegramOperation.SEND_DOCUMENT: ["chat_id", "document"],
            TelegramOperation.SEND_VIDEO: ["chat_id", "video"],
            TelegramOperation.SEND_ANIMATION: ["chat_id", "animation"],
            TelegramOperation.SEND_VOICE: ["chat_id", "voice"],
            TelegramOperation.SEND_VIDEO_NOTE: ["chat_id", "video_note"],
            TelegramOperation.SEND_MEDIA_GROUP: ["chat_id", "media"],
            TelegramOperation.SEND_LOCATION: ["chat_id", "latitude", "longitude"],
            TelegramOperation.EDIT_MESSAGE_LIVE_LOCATION: ["latitude", "longitude"], # chat_id or inline_message_id
            TelegramOperation.SEND_VENUE: ["chat_id", "latitude", "longitude", "title", "address"],
            TelegramOperation.SEND_CONTACT: ["chat_id", "phone_number", "first_name"],
            TelegramOperation.SEND_POLL: ["chat_id", "question", "options"],
            TelegramOperation.SEND_DICE: ["chat_id"],
            TelegramOperation.SEND_CHAT_ACTION: ["chat_id", "action"],
            TelegramOperation.GET_USER_PROFILE_PHOTOS: ["user_id"],
            TelegramOperation.GET_FILE: ["file_id"],
            TelegramOperation.BAN_CHAT_MEMBER: ["chat_id", "user_id"],
            TelegramOperation.UNBAN_CHAT_MEMBER: ["chat_id", "user_id"],
            TelegramOperation.RESTRICT_CHAT_MEMBER: ["chat_id", "user_id", "permissions"],
            TelegramOperation.PROMOTE_CHAT_MEMBER: ["chat_id", "user_id"],
            TelegramOperation.SET_CHAT_ADMINISTRATOR_CUSTOM_TITLE: ["chat_id", "user_id", "custom_title"],
            TelegramOperation.SET_CHAT_PERMISSIONS: ["chat_id", "permissions"],
            TelegramOperation.EXPORT_CHAT_INVITE_LINK: ["chat_id"],
            TelegramOperation.CREATE_CHAT_INVITE_LINK: ["chat_id"],
            TelegramOperation.EDIT_CHAT_INVITE_LINK: ["chat_id", "invite_link"],
            TelegramOperation.REVOKE_CHAT_INVITE_LINK: ["chat_id", "invite_link"],
            TelegramOperation.SET_CHAT_PHOTO: ["chat_id", "photo"], # photo is a file
            TelegramOperation.DELETE_CHAT_PHOTO: ["chat_id"],
            TelegramOperation.SET_CHAT_TITLE: ["chat_id", "title"],
            TelegramOperation.SET_CHAT_DESCRIPTION: ["chat_id"],
            TelegramOperation.PIN_CHAT_MESSAGE: ["chat_id", "message_id"],
            TelegramOperation.UNPIN_CHAT_MESSAGE: ["chat_id"],
            TelegramOperation.LEAVE_CHAT: ["chat_id"],
            TelegramOperation.GET_CHAT: ["chat_id"],
            TelegramOperation.GET_CHAT_ADMINISTRATORS: ["chat_id"],
            TelegramOperation.GET_CHAT_MEMBERS_COUNT: ["chat_id"],
            TelegramOperation.GET_CHAT_MEMBER: ["chat_id", "user_id"],
            TelegramOperation.SET_CHAT_STICKER_SET: ["chat_id", "sticker_set_name"],
            TelegramOperation.DELETE_CHAT_STICKER_SET: ["chat_id"],
            TelegramOperation.ANSWER_CALLBACK_QUERY: ["callback_query_id"],
            TelegramOperation.SET_MY_COMMANDS: ["commands"],
            TelegramOperation.EDIT_MESSAGE_TEXT: ["text"], # Needs chat_id+message_id OR inline_message_id
            TelegramOperation.DELETE_MESSAGE: ["chat_id", "message_id"],
            TelegramOperation.SET_WEBHOOK: ["url"],
        }

        # Specific checks for operations needing one of a pair
        if operation in [TelegramOperation.EDIT_MESSAGE_TEXT, TelegramOperation.EDIT_MESSAGE_CAPTION,
                         TelegramOperation.EDIT_MESSAGE_MEDIA, TelegramOperation.EDIT_MESSAGE_REPLY_MARKUP,
                         TelegramOperation.STOP_POLL, TelegramOperation.STOP_MESSAGE_LIVE_LOCATION]:
            if not (params.get("chat_id") and params.get("message_id")) and not params.get("inline_message_id"):
                raise NodeValidationError(f"Operation '{operation}' requires either ('chat_id' and 'message_id') or 'inline_message_id'.")

        if operation in required_for_op:
            for req_param in required_for_op[operation]:
                if params.get(req_param) is None: # Check for None or missing
                    raise NodeValidationError(f"Parameter '{req_param}' is required for operation '{operation}'.")
        
        if operation == TelegramOperation.SEND_MEDIA_GROUP:
            media = params.get("media")
            if not isinstance(media, list) or not (2 <= len(media) <= 10):
                raise NodeValidationError("'media' for sendMediaGroup must be a list with 2-10 items.")


    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        params = node_data.get("params", {})
        node_name = node_data.get('__node_name', 'TelegramNode')
        logger.debug(f"Executing {node_name} with operation: {params.get('operation')}")

        try:
            await self.validate_custom(params) # Use await if validate_custom becomes async
            bot_token = params.get("bot_token")
            operation = params.get("operation")

            # Exclude bot_token and operation from payload sent to Telegram
            api_params = {k: v for k, v in params.items() if k not in ["bot_token", "operation"]}

            data_payload = api_params
            files_payload = None

            # Handle file uploads for relevant operations
            file_operations_map = {
                TelegramOperation.SEND_PHOTO: ["photo", "thumb"],
                TelegramOperation.SEND_AUDIO: ["audio", "thumb"],
                TelegramOperation.SEND_DOCUMENT: ["document", "thumb"],
                TelegramOperation.SEND_VIDEO: ["video", "thumb"],
                TelegramOperation.SEND_ANIMATION: ["animation", "thumb"],
                TelegramOperation.SEND_VOICE: ["voice"],
                TelegramOperation.SEND_VIDEO_NOTE: ["video_note", "thumb"],
                TelegramOperation.SET_CHAT_PHOTO: ["photo"],
                TelegramOperation.SET_WEBHOOK: ["certificate"],
                # Note: sendMediaGroup handles files differently (array of InputMedia objects)
            }

            if operation in file_operations_map:
                data_payload, files_payload = self._prepare_file_payload(api_params, file_operations_map[operation])
            elif operation == TelegramOperation.SEND_MEDIA_GROUP:
                # For sendMediaGroup, media items might contain local file paths.
                # This requires more complex handling to attach multiple files.
                # For simplicity in this example, we assume media items with local paths are pre-processed
                # or this part needs to be expanded to handle multipart for media group items.
                # A common approach is to upload files individually first and use file_ids.
                # Here, we'll just pass it as data, assuming file_ids or URLs are used mostly.
                # If local files must be sent in sendMediaGroup directly, each item in 'media'
                # that's a local file needs to be added to 'files_payload' with a unique key,
                # and the 'media' JSON string needs to reference these attachments (e.g., "attach://file_key").
                pass # Keeping it simple for now, pass 'media' as JSON string in data_payload

            return await self._send_request(bot_token, operation, data_payload, files_payload)

        except NodeValidationError as e:
            logger.error(f"Validation Error in {node_name}: {e}")
            return self.handle_error(e, context=f"{node_name} Validation")
        except Exception as e:
            logger.error(f"Unexpected Error in {node_name}: {e}", exc_info=True)
            return self.handle_error(e, context=f"{node_name} Execution")

# --- Main Block for Standalone Testing (Illustrative) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')

    # Ensure you have BOT_TOKEN in your environment variables for testing
    TEST_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TEST_CHAT_ID = os.environ.get("TELEGRAM_TEST_CHAT_ID") # Your user ID or a test group ID

    if not TEST_BOT_TOKEN or not TEST_CHAT_ID:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_TEST_CHAT_ID environment variables to run tests.")
        exit(1)
    try:
        TEST_CHAT_ID = int(TEST_CHAT_ID)
    except ValueError:
        print("TELEGRAM_TEST_CHAT_ID must be an integer (your user ID or chat ID).")
        exit(1)


    async def test_telegram_node():
        node = TelegramNode()
        print("\n--- Testing TelegramNode ---")

        # Test 1: getMe
        print("\n1. Testing getMe...")
        get_me_result = await node.execute({
            "params": {
                "bot_token": TEST_BOT_TOKEN,
                "operation": TelegramOperation.GET_ME
            }
        })
        print(f"getMe Result: {json.dumps(get_me_result, indent=2)}")
        assert get_me_result["status"] == "success" and get_me_result["ok"]

        # Test 2: sendMessage
        print("\n2. Testing sendMessage...")
        send_message_result = await node.execute({
            "params": {
                "bot_token": TEST_BOT_TOKEN,
                "operation": TelegramOperation.SEND_MESSAGE,
                "chat_id": TEST_CHAT_ID,
                "text": "Hello from ACT Framework TelegramNode! (Test)",
                "parse_mode": "MarkdownV2"
            }
        })
        print(f"sendMessage Result: {json.dumps(send_message_result, indent=2)}")
        assert send_message_result["status"] == "success" and send_message_result["ok"]
        sent_message_id = send_message_result.get("result", {}).get("message_id")


        # Test 3: editMessageText (if sendMessage was successful)
        if sent_message_id:
            print("\n3. Testing editMessageText...")
            await asyncio.sleep(1) # Small delay
            edit_message_result = await node.execute({
                "params": {
                    "bot_token": TEST_BOT_TOKEN,
                    "operation": TelegramOperation.EDIT_MESSAGE_TEXT,
                    "chat_id": TEST_CHAT_ID,
                    "message_id": sent_message_id,
                    "text": "Hello from ACT Framework TelegramNode! (Test _Edited_)"
                }
            })
            print(f"editMessageText Result: {json.dumps(edit_message_result, indent=2)}")
            assert edit_message_result["status"] == "success" and edit_message_result["ok"]


        # Test 4: sendPhoto (with a public URL)
        print("\n4. Testing sendPhoto (URL)...")
        send_photo_result = await node.execute({
            "params": {
                "bot_token": TEST_BOT_TOKEN,
                "operation": TelegramOperation.SEND_PHOTO,
                "chat_id": TEST_CHAT_ID,
                "photo": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", # Example URL
                "caption": "Test Photo from URL"
            }
        })
        print(f"sendPhoto Result: {json.dumps(send_photo_result, indent=2)}")
        assert send_photo_result["status"] == "success" and send_photo_result["ok"]

        # Test 5: sendDocument (local file - create a dummy file for this)
        dummy_file_path = "test_document.txt"
        with open(dummy_file_path, "w") as f:
            f.write("This is a test document for TelegramNode.")

        print("\n5. Testing sendDocument (Local File)...")
        send_document_result = await node.execute({
            "params": {
                "bot_token": TEST_BOT_TOKEN,
                "operation": TelegramOperation.SEND_DOCUMENT,
                "chat_id": TEST_CHAT_ID,
                "document": dummy_file_path,
                "caption": "Test Document from Local File"
            }
        })
        print(f"sendDocument Result: {json.dumps(send_document_result, indent=2)}")
        assert send_document_result["status"] == "success" and send_document_result["ok"]
        os.remove(dummy_file_path) # Clean up


        # Test 6: getChat
        print("\n6. Testing getChat...")
        get_chat_result = await node.execute({
            "params": {
                "bot_token": TEST_BOT_TOKEN,
                "operation": TelegramOperation.GET_CHAT,
                "chat_id": TEST_CHAT_ID
            }
        })
        print(f"getChat Result: {json.dumps(get_chat_result, indent=2)}")
        assert get_chat_result["status"] == "success" and get_chat_result["ok"]

        # Test 7: Delete Message (if edit was successful)
        if sent_message_id and edit_message_result["ok"]:
            print("\n7. Testing deleteMessage...")
            await asyncio.sleep(1)
            delete_message_result = await node.execute({
                "params": {
                    "bot_token": TEST_BOT_TOKEN,
                    "operation": TelegramOperation.DELETE_MESSAGE,
                    "chat_id": TEST_CHAT_ID,
                    "message_id": sent_message_id
                }
            })
            print(f"deleteMessage Result: {json.dumps(delete_message_result, indent=2)}")
            assert delete_message_result["status"] == "success" and delete_message_result["ok"]


        print("\n✅ TelegramNode tests completed (basic).")

    asyncio.run(test_telegram_node())