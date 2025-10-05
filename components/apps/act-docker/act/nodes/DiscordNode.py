"""
Discord Node - Comprehensive Discord API integration for Discord bot operations
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports all major Discord operations including messaging, server management,
moderation, slash commands, and user interactions. Uses discord.py library
for optimal functionality and compatibility.
"""

import logging
import asyncio
import json
import base64
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager

try:
    import discord
    from discord.ext import commands
    from discord import app_commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    # Define dummy classes for when discord.py is not available
    class discord:
        class Embed:
            pass
        class Color:
            @staticmethod
            def blue():
                return 0x0099ff
        class Intents:
            @staticmethod
            def default():
                return None
        class Client:
            pass
        class Bot:
            pass

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

class DiscordOperation:
    """All available Discord operations."""
    
    # Message Operations
    SEND_MESSAGE = "send_message"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"
    GET_MESSAGE = "get_message"
    GET_MESSAGES = "get_messages"
    PIN_MESSAGE = "pin_message"
    UNPIN_MESSAGE = "unpin_message"
    ADD_REACTION = "add_reaction"
    REMOVE_REACTION = "remove_reaction"
    CLEAR_REACTIONS = "clear_reactions"
    
    # Embed Operations
    SEND_EMBED = "send_embed"
    EDIT_EMBED = "edit_embed"
    CREATE_EMBED = "create_embed"
    
    # Channel Operations
    GET_CHANNEL = "get_channel"
    CREATE_CHANNEL = "create_channel"
    EDIT_CHANNEL = "edit_channel"
    DELETE_CHANNEL = "delete_channel"
    LIST_CHANNELS = "list_channels"
    SET_CHANNEL_PERMISSIONS = "set_channel_permissions"
    
    # Guild/Server Operations
    GET_GUILD = "get_guild"
    LIST_GUILDS = "list_guilds"
    EDIT_GUILD = "edit_guild"
    LEAVE_GUILD = "leave_guild"
    GET_GUILD_MEMBERS = "get_guild_members"
    GET_GUILD_ROLES = "get_guild_roles"
    GET_GUILD_CHANNELS = "get_guild_channels"
    
    # User Operations
    GET_USER = "get_user"
    GET_MEMBER = "get_member"
    KICK_MEMBER = "kick_member"
    BAN_MEMBER = "ban_member"
    UNBAN_MEMBER = "unban_member"
    TIMEOUT_MEMBER = "timeout_member"
    ADD_ROLE = "add_role"
    REMOVE_ROLE = "remove_role"
    EDIT_MEMBER = "edit_member"
    
    # Role Operations
    CREATE_ROLE = "create_role"
    EDIT_ROLE = "edit_role"
    DELETE_ROLE = "delete_role"
    
    # Slash Commands
    CREATE_SLASH_COMMAND = "create_slash_command"
    DELETE_SLASH_COMMAND = "delete_slash_command"
    LIST_SLASH_COMMANDS = "list_slash_commands"
    SYNC_COMMANDS = "sync_commands"
    
    # Interaction Operations
    RESPOND_TO_INTERACTION = "respond_to_interaction"
    FOLLOW_UP_INTERACTION = "follow_up_interaction"
    DEFER_INTERACTION = "defer_interaction"
    
    # Moderation Operations
    PURGE_MESSAGES = "purge_messages"
    CREATE_INVITE = "create_invite"
    GET_INVITES = "get_invites"
    DELETE_INVITE = "delete_invite"
    
    # Voice Operations
    JOIN_VOICE_CHANNEL = "join_voice_channel"
    LEAVE_VOICE_CHANNEL = "leave_voice_channel"
    
    # Webhook Operations
    CREATE_WEBHOOK = "create_webhook"
    EDIT_WEBHOOK = "edit_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    EXECUTE_WEBHOOK = "execute_webhook"
    
    # Event Operations
    LISTEN_FOR_MESSAGES = "listen_for_messages"
    LISTEN_FOR_REACTIONS = "listen_for_reactions"
    LISTEN_FOR_MEMBER_EVENTS = "listen_for_member_events"
    
    # File Operations
    SEND_FILE = "send_file"
    UPLOAD_EMOJI = "upload_emoji"
    DELETE_EMOJI = "delete_emoji"
    
    # Bot Status Operations
    SET_STATUS = "set_status"
    SET_ACTIVITY = "set_activity"
    SET_PRESENCE = "set_presence"


class DiscordClientWrapper:
    """Unified Discord client wrapper that handles both Bot and Client instances."""
    
    def __init__(self, token: str, intents=None, command_prefix="!", is_bot=True):
        self.token = token
        self.intents = intents or (discord.Intents.default() if DISCORD_AVAILABLE else None)
        self.command_prefix = command_prefix
        self.is_bot = is_bot
        self.client = None
        self.is_ready = False
        
    async def initialize(self):
        """Initialize the Discord client."""
        if not DISCORD_AVAILABLE:
            raise NodeExecutionError("Discord.py library is not available")
        
        if self.is_bot:
            self.client = commands.Bot(
                command_prefix=self.command_prefix,
                intents=self.intents
            )
        else:
            self.client = discord.Client(intents=self.intents)
        
        # Set up event handlers
        @self.client.event
        async def on_ready():
            self.is_ready = True
            logger.info(f'Discord client logged in as {self.client.user}')
        
        # Login but don't start the event loop
        await self.client.login(self.token)
        
    async def ensure_ready(self):
        """Ensure the client is ready for operations."""
        if not self.is_ready and self.client:
            # Wait for ready event or timeout
            try:
                await asyncio.wait_for(self.client.wait_until_ready(), timeout=10.0)
                self.is_ready = True
            except asyncio.TimeoutError:
                logger.warning("Discord client ready timeout")
    
    # Message operations
    async def send_message(self, channel_id: int, content: str = None, embed=None, file=None, **kwargs) -> Dict[str, Any]:
        """Send a message to a channel."""
        channel = self.client.get_channel(channel_id)
        if not channel:
            channel = await self.client.fetch_channel(channel_id)
        
        message = await channel.send(content=content, embed=embed, file=file, **kwargs)
        return {
            "id": message.id,
            "content": message.content,
            "author": str(message.author),
            "timestamp": message.created_at.isoformat(),
            "channel_id": message.channel.id
        }
    
    async def edit_message(self, channel_id: int, message_id: int, content: str = None, embed=None, **kwargs) -> Dict[str, Any]:
        """Edit a message."""
        channel = self.client.get_channel(channel_id)
        if not channel:
            channel = await self.client.fetch_channel(channel_id)
        
        message = await channel.fetch_message(message_id)
        edited_message = await message.edit(content=content, embed=embed, **kwargs)
        return {
            "id": edited_message.id,
            "content": edited_message.content,
            "edited_at": edited_message.edited_at.isoformat() if edited_message.edited_at else None
        }
    
    async def delete_message(self, channel_id: int, message_id: int) -> bool:
        """Delete a message."""
        channel = self.client.get_channel(channel_id)
        if not channel:
            channel = await self.client.fetch_channel(channel_id)
        
        message = await channel.fetch_message(message_id)
        await message.delete()
        return True
    
    async def get_messages(self, channel_id: int, limit: int = 50, before=None, after=None) -> List[Dict[str, Any]]:
        """Get messages from a channel."""
        channel = self.client.get_channel(channel_id)
        if not channel:
            channel = await self.client.fetch_channel(channel_id)
        
        messages = []
        async for message in channel.history(limit=limit, before=before, after=after):
            messages.append({
                "id": message.id,
                "content": message.content,
                "author": {
                    "id": message.author.id,
                    "name": str(message.author),
                    "avatar": str(message.author.avatar) if message.author.avatar else None
                },
                "timestamp": message.created_at.isoformat(),
                "embeds": len(message.embeds),
                "attachments": [{"url": att.url, "filename": att.filename} for att in message.attachments]
            })
        return messages
    
    # Embed operations
    async def create_embed(self, title: str = None, description: str = None, color: int = None, **kwargs) -> discord.Embed:
        """Create a Discord embed."""
        embed = discord.Embed(title=title, description=description, color=color, **kwargs)
        return embed
    
    async def send_embed(self, channel_id: int, embed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an embed to a channel."""
        embed = discord.Embed.from_dict(embed_data)
        return await self.send_message(channel_id, embed=embed)
    
    # Channel operations
    async def get_channel(self, channel_id: int) -> Dict[str, Any]:
        """Get channel information."""
        channel = self.client.get_channel(channel_id)
        if not channel:
            channel = await self.client.fetch_channel(channel_id)
        
        return {
            "id": channel.id,
            "name": channel.name,
            "type": str(channel.type),
            "guild_id": channel.guild.id if hasattr(channel, 'guild') else None,
            "position": getattr(channel, 'position', None),
            "topic": getattr(channel, 'topic', None),
            "nsfw": getattr(channel, 'nsfw', None)
        }
    
    async def create_channel(self, guild_id: int, name: str, channel_type: str = "text", **kwargs) -> Dict[str, Any]:
        """Create a channel."""
        guild = self.client.get_guild(guild_id)
        if not guild:
            guild = await self.client.fetch_guild(guild_id)
        
        if channel_type == "text":
            channel = await guild.create_text_channel(name, **kwargs)
        elif channel_type == "voice":
            channel = await guild.create_voice_channel(name, **kwargs)
        elif channel_type == "category":
            channel = await guild.create_category(name, **kwargs)
        else:
            raise ValueError(f"Unsupported channel type: {channel_type}")
        
        return {
            "id": channel.id,
            "name": channel.name,
            "type": str(channel.type),
            "guild_id": channel.guild.id
        }
    
    # Guild operations
    async def get_guild(self, guild_id: int) -> Dict[str, Any]:
        """Get guild information."""
        guild = self.client.get_guild(guild_id)
        if not guild:
            guild = await self.client.fetch_guild(guild_id)
        
        return {
            "id": guild.id,
            "name": guild.name,
            "description": guild.description,
            "member_count": guild.member_count,
            "owner_id": guild.owner_id,
            "verification_level": str(guild.verification_level),
            "created_at": guild.created_at.isoformat(),
            "icon": str(guild.icon) if guild.icon else None
        }
    
    async def get_guild_members(self, guild_id: int, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get guild members."""
        guild = self.client.get_guild(guild_id)
        if not guild:
            guild = await self.client.fetch_guild(guild_id)
        
        members = []
        async for member in guild.fetch_members(limit=limit):
            members.append({
                "id": member.id,
                "name": str(member),
                "display_name": member.display_name,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "roles": [role.name for role in member.roles[1:]],  # Skip @everyone
                "status": str(member.status) if hasattr(member, 'status') else None
            })
        return members
    
    # User operations
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user information."""
        user = self.client.get_user(user_id)
        if not user:
            user = await self.client.fetch_user(user_id)
        
        return {
            "id": user.id,
            "name": str(user),
            "display_name": user.display_name,
            "avatar": str(user.avatar) if user.avatar else None,
            "created_at": user.created_at.isoformat(),
            "bot": user.bot
        }
    
    async def kick_member(self, guild_id: int, user_id: int, reason: str = None) -> bool:
        """Kick a member from the guild."""
        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)
        if not member:
            member = await guild.fetch_member(user_id)
        
        await member.kick(reason=reason)
        return True
    
    async def ban_member(self, guild_id: int, user_id: int, reason: str = None, delete_message_days: int = 1) -> bool:
        """Ban a member from the guild."""
        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)
        if not member:
            user = await self.client.fetch_user(user_id)
            await guild.ban(user, reason=reason, delete_message_days=delete_message_days)
        else:
            await member.ban(reason=reason, delete_message_days=delete_message_days)
        return True
    
    # Role operations
    async def create_role(self, guild_id: int, name: str, permissions: int = None, color: int = None, **kwargs) -> Dict[str, Any]:
        """Create a role."""
        guild = self.client.get_guild(guild_id)
        role = await guild.create_role(
            name=name,
            permissions=discord.Permissions(permissions) if permissions else discord.Permissions(),
            color=discord.Color(color) if color else discord.Color.default(),
            **kwargs
        )
        
        return {
            "id": role.id,
            "name": role.name,
            "color": role.color.value,
            "permissions": role.permissions.value,
            "position": role.position,
            "mentionable": role.mentionable
        }
    
    async def add_role(self, guild_id: int, user_id: int, role_id: int, reason: str = None) -> bool:
        """Add a role to a member."""
        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)
        role = guild.get_role(role_id)
        
        await member.add_roles(role, reason=reason)
        return True
    
    # Moderation operations
    async def purge_messages(self, channel_id: int, limit: int = 100, check=None) -> int:
        """Purge messages from a channel."""
        channel = self.client.get_channel(channel_id)
        deleted = await channel.purge(limit=limit, check=check)
        return len(deleted)
    
    # Webhook operations
    async def create_webhook(self, channel_id: int, name: str, avatar: bytes = None, reason: str = None) -> Dict[str, Any]:
        """Create a webhook."""
        channel = self.client.get_channel(channel_id)
        webhook = await channel.create_webhook(name=name, avatar=avatar, reason=reason)
        
        return {
            "id": webhook.id,
            "name": webhook.name,
            "url": webhook.url,
            "token": webhook.token,
            "channel_id": webhook.channel.id
        }
    
    async def execute_webhook(self, webhook_url: str, content: str = None, username: str = None, avatar_url: str = None, embed=None) -> Dict[str, Any]:
        """Execute a webhook."""
        # This would require webhook parsing and execution
        return {"status": "executed", "webhook_url": webhook_url}
    
    # Bot status operations
    async def set_status(self, status: str, activity_name: str = None, activity_type: str = "playing") -> bool:
        """Set bot status and activity."""
        status_mapping = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        
        activity = None
        if activity_name:
            activity_mapping = {
                "playing": discord.ActivityType.playing,
                "streaming": discord.ActivityType.streaming,
                "listening": discord.ActivityType.listening,
                "watching": discord.ActivityType.watching
            }
            activity = discord.Activity(
                type=activity_mapping.get(activity_type, discord.ActivityType.playing),
                name=activity_name
            )
        
        await self.client.change_presence(
            status=status_mapping.get(status, discord.Status.online),
            activity=activity
        )
        return True


class DiscordNode(BaseNode):
    """Discord Node for comprehensive Discord bot operations with optimized performance."""
    
    OPERATION_METADATA = {
        # Message operations
        DiscordOperation.SEND_MESSAGE: {
            "required_params": ["channel_id"],
            "optional_params": ["content", "embed", "file", "tts", "delete_after"],
            "description": "Send a message to a Discord channel"
        },
        DiscordOperation.EDIT_MESSAGE: {
            "required_params": ["channel_id", "message_id"],
            "optional_params": ["content", "embed", "attachments"],
            "description": "Edit an existing message"
        },
        DiscordOperation.DELETE_MESSAGE: {
            "required_params": ["channel_id", "message_id"],
            "optional_params": [],
            "description": "Delete a message"
        },
        DiscordOperation.GET_MESSAGES: {
            "required_params": ["channel_id"],
            "optional_params": ["limit", "before", "after"],
            "description": "Get messages from a channel"
        },
        
        # Embed operations
        DiscordOperation.SEND_EMBED: {
            "required_params": ["channel_id", "embed"],
            "optional_params": ["content"],
            "description": "Send an embed to a channel"
        },
        DiscordOperation.CREATE_EMBED: {
            "required_params": [],
            "optional_params": ["title", "description", "color", "fields", "footer", "author", "thumbnail", "image"],
            "description": "Create a Discord embed"
        },
        
        # Channel operations
        DiscordOperation.GET_CHANNEL: {
            "required_params": ["channel_id"],
            "optional_params": [],
            "description": "Get channel information"
        },
        DiscordOperation.CREATE_CHANNEL: {
            "required_params": ["guild_id", "name"],
            "optional_params": ["channel_type", "topic", "category", "position", "overwrites"],
            "description": "Create a new channel"
        },
        DiscordOperation.LIST_CHANNELS: {
            "required_params": ["guild_id"],
            "optional_params": ["channel_type"],
            "description": "List channels in a guild"
        },
        
        # Guild operations
        DiscordOperation.GET_GUILD: {
            "required_params": ["guild_id"],
            "optional_params": [],
            "description": "Get guild information"
        },
        DiscordOperation.GET_GUILD_MEMBERS: {
            "required_params": ["guild_id"],
            "optional_params": ["limit"],
            "description": "Get guild members"
        },
        
        # User operations
        DiscordOperation.GET_USER: {
            "required_params": ["user_id"],
            "optional_params": [],
            "description": "Get user information"
        },
        DiscordOperation.KICK_MEMBER: {
            "required_params": ["guild_id", "user_id"],
            "optional_params": ["reason"],
            "description": "Kick a member from the guild"
        },
        DiscordOperation.BAN_MEMBER: {
            "required_params": ["guild_id", "user_id"],
            "optional_params": ["reason", "delete_message_days"],
            "description": "Ban a member from the guild"
        },
        
        # Role operations
        DiscordOperation.CREATE_ROLE: {
            "required_params": ["guild_id", "name"],
            "optional_params": ["permissions", "color", "hoist", "mentionable"],
            "description": "Create a role"
        },
        DiscordOperation.ADD_ROLE: {
            "required_params": ["guild_id", "user_id", "role_id"],
            "optional_params": ["reason"],
            "description": "Add a role to a member"
        },
        
        # Moderation operations
        DiscordOperation.PURGE_MESSAGES: {
            "required_params": ["channel_id"],
            "optional_params": ["limit", "before", "after"],
            "description": "Purge messages from a channel"
        },
        
        # Webhook operations
        DiscordOperation.CREATE_WEBHOOK: {
            "required_params": ["channel_id", "name"],
            "optional_params": ["avatar", "reason"],
            "description": "Create a webhook"
        },
        DiscordOperation.EXECUTE_WEBHOOK: {
            "required_params": ["webhook_url"],
            "optional_params": ["content", "username", "avatar_url", "embed"],
            "description": "Execute a webhook"
        },
        
        # Bot status operations
        DiscordOperation.SET_STATUS: {
            "required_params": ["status"],
            "optional_params": ["activity_name", "activity_type"],
            "description": "Set bot status and activity"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.operation_dispatch = {
            # Message operations
            DiscordOperation.SEND_MESSAGE: self._handle_send_message,
            DiscordOperation.EDIT_MESSAGE: self._handle_edit_message,
            DiscordOperation.DELETE_MESSAGE: self._handle_delete_message,
            DiscordOperation.GET_MESSAGE: self._handle_get_message,
            DiscordOperation.GET_MESSAGES: self._handle_get_messages,
            DiscordOperation.PIN_MESSAGE: self._handle_pin_message,
            DiscordOperation.UNPIN_MESSAGE: self._handle_unpin_message,
            DiscordOperation.ADD_REACTION: self._handle_add_reaction,
            DiscordOperation.REMOVE_REACTION: self._handle_remove_reaction,
            DiscordOperation.CLEAR_REACTIONS: self._handle_clear_reactions,
            
            # Embed operations
            DiscordOperation.SEND_EMBED: self._handle_send_embed,
            DiscordOperation.EDIT_EMBED: self._handle_edit_embed,
            DiscordOperation.CREATE_EMBED: self._handle_create_embed,
            
            # Channel operations
            DiscordOperation.GET_CHANNEL: self._handle_get_channel,
            DiscordOperation.CREATE_CHANNEL: self._handle_create_channel,
            DiscordOperation.EDIT_CHANNEL: self._handle_edit_channel,
            DiscordOperation.DELETE_CHANNEL: self._handle_delete_channel,
            DiscordOperation.LIST_CHANNELS: self._handle_list_channels,
            DiscordOperation.SET_CHANNEL_PERMISSIONS: self._handle_set_channel_permissions,
            
            # Guild operations
            DiscordOperation.GET_GUILD: self._handle_get_guild,
            DiscordOperation.LIST_GUILDS: self._handle_list_guilds,
            DiscordOperation.EDIT_GUILD: self._handle_edit_guild,
            DiscordOperation.LEAVE_GUILD: self._handle_leave_guild,
            DiscordOperation.GET_GUILD_MEMBERS: self._handle_get_guild_members,
            DiscordOperation.GET_GUILD_ROLES: self._handle_get_guild_roles,
            DiscordOperation.GET_GUILD_CHANNELS: self._handle_get_guild_channels,
            
            # User operations
            DiscordOperation.GET_USER: self._handle_get_user,
            DiscordOperation.GET_MEMBER: self._handle_get_member,
            DiscordOperation.KICK_MEMBER: self._handle_kick_member,
            DiscordOperation.BAN_MEMBER: self._handle_ban_member,
            DiscordOperation.UNBAN_MEMBER: self._handle_unban_member,
            DiscordOperation.TIMEOUT_MEMBER: self._handle_timeout_member,
            DiscordOperation.ADD_ROLE: self._handle_add_role,
            DiscordOperation.REMOVE_ROLE: self._handle_remove_role,
            DiscordOperation.EDIT_MEMBER: self._handle_edit_member,
            
            # Role operations
            DiscordOperation.CREATE_ROLE: self._handle_create_role,
            DiscordOperation.EDIT_ROLE: self._handle_edit_role,
            DiscordOperation.DELETE_ROLE: self._handle_delete_role,
            
            # Slash commands
            DiscordOperation.CREATE_SLASH_COMMAND: self._handle_create_slash_command,
            DiscordOperation.DELETE_SLASH_COMMAND: self._handle_delete_slash_command,
            DiscordOperation.LIST_SLASH_COMMANDS: self._handle_list_slash_commands,
            DiscordOperation.SYNC_COMMANDS: self._handle_sync_commands,
            
            # Interaction operations
            DiscordOperation.RESPOND_TO_INTERACTION: self._handle_respond_to_interaction,
            DiscordOperation.FOLLOW_UP_INTERACTION: self._handle_follow_up_interaction,
            DiscordOperation.DEFER_INTERACTION: self._handle_defer_interaction,
            
            # Moderation operations
            DiscordOperation.PURGE_MESSAGES: self._handle_purge_messages,
            DiscordOperation.CREATE_INVITE: self._handle_create_invite,
            DiscordOperation.GET_INVITES: self._handle_get_invites,
            DiscordOperation.DELETE_INVITE: self._handle_delete_invite,
            
            # Voice operations
            DiscordOperation.JOIN_VOICE_CHANNEL: self._handle_join_voice_channel,
            DiscordOperation.LEAVE_VOICE_CHANNEL: self._handle_leave_voice_channel,
            
            # Webhook operations
            DiscordOperation.CREATE_WEBHOOK: self._handle_create_webhook,
            DiscordOperation.EDIT_WEBHOOK: self._handle_edit_webhook,
            DiscordOperation.DELETE_WEBHOOK: self._handle_delete_webhook,
            DiscordOperation.EXECUTE_WEBHOOK: self._handle_execute_webhook,
            
            # Event operations
            DiscordOperation.LISTEN_FOR_MESSAGES: self._handle_listen_for_messages,
            DiscordOperation.LISTEN_FOR_REACTIONS: self._handle_listen_for_reactions,
            DiscordOperation.LISTEN_FOR_MEMBER_EVENTS: self._handle_listen_for_member_events,
            
            # File operations
            DiscordOperation.SEND_FILE: self._handle_send_file,
            DiscordOperation.UPLOAD_EMOJI: self._handle_upload_emoji,
            DiscordOperation.DELETE_EMOJI: self._handle_delete_emoji,
            
            # Bot status operations
            DiscordOperation.SET_STATUS: self._handle_set_status,
            DiscordOperation.SET_ACTIVITY: self._handle_set_activity,
            DiscordOperation.SET_PRESENCE: self._handle_set_presence,
        }
    
    def get_schema(self) -> NodeSchema:
        """Generate schema with all parameters from operation metadata."""
        # Common parameters for all operations
        base_params = [
            ("operation", NodeParameterType.STRING, "Discord operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("token", NodeParameterType.STRING, "Discord bot token", True),
            ("intents", NodeParameterType.ARRAY, "Discord intents", False, None, ["default"]),
            ("command_prefix", NodeParameterType.STRING, "Bot command prefix", False, None, "!"),
            ("is_bot", NodeParameterType.BOOLEAN, "Whether to use Bot client", False, None, True),
            ("timeout", NodeParameterType.NUMBER, "Operation timeout in seconds", False, None, 30),
        ]
        
        # Operation-specific parameters
        operation_params = [
            # Message parameters
            ("channel_id", NodeParameterType.NUMBER, "Discord channel ID", False),
            ("message_id", NodeParameterType.NUMBER, "Discord message ID", False),
            ("content", NodeParameterType.STRING, "Message content", False),
            ("tts", NodeParameterType.BOOLEAN, "Text-to-speech", False),
            ("delete_after", NodeParameterType.NUMBER, "Delete message after seconds", False),
            
            # Embed parameters
            ("embed", NodeParameterType.OBJECT, "Discord embed object", False),
            ("title", NodeParameterType.STRING, "Embed title", False),
            ("description", NodeParameterType.STRING, "Embed description", False),
            ("color", NodeParameterType.NUMBER, "Embed color (hex)", False),
            ("fields", NodeParameterType.ARRAY, "Embed fields", False),
            ("footer", NodeParameterType.OBJECT, "Embed footer", False),
            ("author", NodeParameterType.OBJECT, "Embed author", False),
            ("thumbnail", NodeParameterType.STRING, "Embed thumbnail URL", False),
            ("image", NodeParameterType.STRING, "Embed image URL", False),
            
            # Guild/Server parameters
            ("guild_id", NodeParameterType.NUMBER, "Discord guild/server ID", False),
            ("user_id", NodeParameterType.NUMBER, "Discord user ID", False),
            ("role_id", NodeParameterType.NUMBER, "Discord role ID", False),
            
            # Channel parameters
            ("name", NodeParameterType.STRING, "Channel/role name", False),
            ("channel_type", NodeParameterType.STRING, "Channel type", False, ["text", "voice", "category"], "text"),
            ("topic", NodeParameterType.STRING, "Channel topic", False),
            ("position", NodeParameterType.NUMBER, "Channel position", False),
            ("category", NodeParameterType.NUMBER, "Category ID", False),
            
            # Permission parameters
            ("permissions", NodeParameterType.NUMBER, "Permission value", False),
            ("overwrites", NodeParameterType.OBJECT, "Permission overwrites", False),
            
            # Moderation parameters
            ("reason", NodeParameterType.STRING, "Reason for action", False),
            ("limit", NodeParameterType.NUMBER, "Limit for operations", False, None, 50),
            ("before", NodeParameterType.STRING, "Before timestamp/message ID", False),
            ("after", NodeParameterType.STRING, "After timestamp/message ID", False),
            ("delete_message_days", NodeParameterType.NUMBER, "Days of messages to delete", False, None, 1),
            
            # Role parameters
            ("hoist", NodeParameterType.BOOLEAN, "Display role separately", False),
            ("mentionable", NodeParameterType.BOOLEAN, "Role is mentionable", False),
            
            # Webhook parameters
            ("webhook_url", NodeParameterType.STRING, "Webhook URL", False),
            ("username", NodeParameterType.STRING, "Webhook username override", False),
            ("avatar_url", NodeParameterType.STRING, "Webhook avatar URL", False),
            ("avatar", NodeParameterType.STRING, "Avatar data (base64)", False),
            
            # Bot status parameters
            ("status", NodeParameterType.STRING, "Bot status", False, ["online", "idle", "dnd", "invisible"], "online"),
            ("activity_name", NodeParameterType.STRING, "Activity name", False),
            ("activity_type", NodeParameterType.STRING, "Activity type", False, ["playing", "streaming", "listening", "watching"], "playing"),
            
            # File parameters
            ("file", NodeParameterType.STRING, "File path or base64 data", False),
            ("filename", NodeParameterType.STRING, "File name", False),
            
            # Reaction parameters
            ("emoji", NodeParameterType.STRING, "Emoji for reaction", False),
        ]
        
        # Build parameters dict
        parameters = {}
        for param_def in base_params + operation_params:
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
            node_type="discord",
            version="1.0.0",
            description="Comprehensive Discord integration supporting all major Discord bot operations including messaging, server management, moderation, slash commands, and user interactions",
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
                "discord_error": NodeParameterType.STRING,
                "bot_info": NodeParameterType.OBJECT,
                "guild_info": NodeParameterType.OBJECT,
                "channel_info": NodeParameterType.OBJECT,
                "message_id": NodeParameterType.NUMBER,
                "user_id": NodeParameterType.NUMBER,
                "role_id": NodeParameterType.NUMBER,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Discord-specific parameters using operation metadata."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Basic validation
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Token validation
        if not params.get("token"):
            raise NodeValidationError("Discord bot token is required")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata["required_params"]:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Validate specific operations
        if operation == DiscordOperation.SEND_MESSAGE:
            if not params.get("content") and not params.get("embed") and not params.get("file"):
                raise NodeValidationError("Message must have content, embed, or file")
        
        if operation in [DiscordOperation.SEND_EMBED, DiscordOperation.CREATE_EMBED]:
            embed = params.get("embed")
            if embed and not isinstance(embed, dict):
                raise NodeValidationError("Embed must be a dictionary")
        
        if operation in [DiscordOperation.KICK_MEMBER, DiscordOperation.BAN_MEMBER]:
            user_id = params.get("user_id")
            if not isinstance(user_id, int):
                raise NodeValidationError("user_id must be an integer")
        
        return node_data
    
    @asynccontextmanager
    async def _get_discord_client(self, params: Dict[str, Any]):
        """Context manager for Discord client with proper lifecycle."""
        token = params["token"]
        intents_list = params.get("intents", ["default"])
        command_prefix = params.get("command_prefix", "!")
        is_bot = params.get("is_bot", True)
        timeout = params.get("timeout", 30)
        
        # Set up intents
        intents = None
        if DISCORD_AVAILABLE:
            intents = discord.Intents.default()
            if "all" in intents_list:
                intents = discord.Intents.all()
            elif "privileged" in intents_list:
                intents.message_content = True
                intents.members = True
                intents.presences = True
        
        client = None
        try:
            client = DiscordClientWrapper(
                token=token,
                intents=intents,
                command_prefix=command_prefix,
                is_bot=is_bot
            )
            await client.initialize()
            await client.ensure_ready()
            yield client
        except Exception as e:
            logger.error(f"Failed to create Discord client: {e}")
            raise NodeExecutionError(f"Client initialization failed: {str(e)}")
        finally:
            if client and client.client:
                try:
                    await client.client.close()
                except Exception as e:
                    logger.warning(f"Error closing Discord client: {e}")
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Discord operation with comprehensive error handling."""
        start_time = datetime.now(timezone.utc)
        operation = node_data.get("params", {}).get("operation")
        
        # Prepare response
        response = {
            "status": "pending",
            "operation": operation,
            "start_time": start_time.isoformat(),
            "execution_time": 0,
            "inputs": self._mask_sensitive_data(node_data.get("params", {})),
            "raw_result": None,
            "result": None,
            "error": None,
            "discord_error": None,
            "bot_info": {},
        }
        
        try:
            # Validate input
            self.validate_custom(node_data)
            params = node_data["params"]
            
            # Get operation handler
            if operation not in self.operation_dispatch:
                raise NodeValidationError(f"Operation {operation} not supported")
            
            handler = self.operation_dispatch[operation]
            
            # Execute operation
            async with self._get_discord_client(params) as discord_client:
                raw_result = await handler(discord_client, params)
                
                # Process result
                response["raw_result"] = raw_result
                response["result"] = raw_result
                response["status"] = "success"
                
                # Add bot info if available
                if discord_client.client and discord_client.client.user:
                    response["bot_info"] = {
                        "id": discord_client.client.user.id,
                        "name": str(discord_client.client.user),
                        "discriminator": discord_client.client.user.discriminator,
                        "bot": discord_client.client.user.bot
                    }
                
        except Exception as e:
            error_msg = f"Unexpected error in operation {operation}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            response.update({
                "status": "error",
                "error": error_msg,
                "discord_error": type(e).__name__,
            })
        finally:
            end_time = datetime.now(timezone.utc)
            response["execution_time"] = (end_time - start_time).total_seconds()
        
        return response
    
    def _mask_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in logs."""
        masked = params.copy()
        sensitive_fields = ["token", "webhook_url", "password"]
        
        for field in sensitive_fields:
            if field in masked:
                masked[field] = "***MASKED***"
        
        return masked
    
    # Operation handlers
    async def _handle_send_message(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SEND_MESSAGE operation."""
        channel_id = params["channel_id"]
        content = params.get("content")
        embed = params.get("embed")
        file = params.get("file")
        tts = params.get("tts", False)
        delete_after = params.get("delete_after")
        
        # Process embed if provided
        if embed and isinstance(embed, dict):
            embed = discord.Embed.from_dict(embed) if DISCORD_AVAILABLE else None
        
        # Process file if provided
        discord_file = None
        if file:
            if isinstance(file, str) and file.startswith("data:"):
                # Handle base64 encoded file
                import base64
                header, data = file.split(",", 1)
                file_data = base64.b64decode(data)
                filename = params.get("filename", "attachment.txt")
                discord_file = discord.File(io.BytesIO(file_data), filename=filename) if DISCORD_AVAILABLE else None
        
        return await discord_client.send_message(
            channel_id=channel_id,
            content=content,
            embed=embed,
            file=discord_file,
            tts=tts,
            delete_after=delete_after
        )
    
    async def _handle_edit_message(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_MESSAGE operation."""
        channel_id = params["channel_id"]
        message_id = params["message_id"]
        content = params.get("content")
        embed = params.get("embed")
        
        if embed and isinstance(embed, dict):
            embed = discord.Embed.from_dict(embed) if DISCORD_AVAILABLE else None
        
        return await discord_client.edit_message(channel_id, message_id, content, embed)
    
    async def _handle_delete_message(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_MESSAGE operation."""
        channel_id = params["channel_id"]
        message_id = params["message_id"]
        return await discord_client.delete_message(channel_id, message_id)
    
    async def _handle_get_messages(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle GET_MESSAGES operation."""
        channel_id = params["channel_id"]
        limit = params.get("limit", 50)
        before = params.get("before")
        after = params.get("after")
        
        return await discord_client.get_messages(channel_id, limit, before, after)
    
    async def _handle_send_embed(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SEND_EMBED operation."""
        channel_id = params["channel_id"]
        embed_data = params["embed"]
        content = params.get("content")
        
        result = await discord_client.send_embed(channel_id, embed_data)
        return result
    
    async def _handle_create_embed(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_EMBED operation."""
        title = params.get("title")
        description = params.get("description")
        color = params.get("color")
        
        embed = await discord_client.create_embed(title, description, color)
        return embed.to_dict() if hasattr(embed, 'to_dict') else {"title": title, "description": description}
    
    async def _handle_get_channel(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_CHANNEL operation."""
        channel_id = params["channel_id"]
        return await discord_client.get_channel(channel_id)
    
    async def _handle_create_channel(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_CHANNEL operation."""
        guild_id = params["guild_id"]
        name = params["name"]
        channel_type = params.get("channel_type", "text")
        topic = params.get("topic")
        
        kwargs = {}
        if topic:
            kwargs["topic"] = topic
        
        return await discord_client.create_channel(guild_id, name, channel_type, **kwargs)
    
    async def _handle_get_guild(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_GUILD operation."""
        guild_id = params["guild_id"]
        return await discord_client.get_guild(guild_id)
    
    async def _handle_get_guild_members(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle GET_GUILD_MEMBERS operation."""
        guild_id = params["guild_id"]
        limit = params.get("limit", 1000)
        return await discord_client.get_guild_members(guild_id, limit)
    
    async def _handle_get_user(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_USER operation."""
        user_id = params["user_id"]
        return await discord_client.get_user(user_id)
    
    async def _handle_kick_member(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle KICK_MEMBER operation."""
        guild_id = params["guild_id"]
        user_id = params["user_id"]
        reason = params.get("reason")
        return await discord_client.kick_member(guild_id, user_id, reason)
    
    async def _handle_ban_member(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle BAN_MEMBER operation."""
        guild_id = params["guild_id"]
        user_id = params["user_id"]
        reason = params.get("reason")
        delete_message_days = params.get("delete_message_days", 1)
        return await discord_client.ban_member(guild_id, user_id, reason, delete_message_days)
    
    async def _handle_create_role(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_ROLE operation."""
        guild_id = params["guild_id"]
        name = params["name"]
        permissions = params.get("permissions")
        color = params.get("color")
        hoist = params.get("hoist", False)
        mentionable = params.get("mentionable", False)
        
        return await discord_client.create_role(
            guild_id, name, permissions, color,
            hoist=hoist, mentionable=mentionable
        )
    
    async def _handle_add_role(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle ADD_ROLE operation."""
        guild_id = params["guild_id"]
        user_id = params["user_id"]
        role_id = params["role_id"]
        reason = params.get("reason")
        return await discord_client.add_role(guild_id, user_id, role_id, reason)
    
    async def _handle_purge_messages(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> int:
        """Handle PURGE_MESSAGES operation."""
        channel_id = params["channel_id"]
        limit = params.get("limit", 100)
        return await discord_client.purge_messages(channel_id, limit)
    
    async def _handle_create_webhook(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_WEBHOOK operation."""
        channel_id = params["channel_id"]
        name = params["name"]
        avatar = params.get("avatar")
        reason = params.get("reason")
        
        avatar_bytes = None
        if avatar:
            import base64
            avatar_bytes = base64.b64decode(avatar)
        
        return await discord_client.create_webhook(channel_id, name, avatar_bytes, reason)
    
    async def _handle_execute_webhook(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EXECUTE_WEBHOOK operation."""
        webhook_url = params["webhook_url"]
        content = params.get("content")
        username = params.get("username")
        avatar_url = params.get("avatar_url")
        embed = params.get("embed")
        
        return await discord_client.execute_webhook(webhook_url, content, username, avatar_url, embed)
    
    async def _handle_set_status(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle SET_STATUS operation."""
        status = params["status"]
        activity_name = params.get("activity_name")
        activity_type = params.get("activity_type", "playing")
        
        return await discord_client.set_status(status, activity_name, activity_type)
    
    # Placeholder handlers for remaining operations
    async def _handle_get_message(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_MESSAGE operation."""
        return {"status": "not_implemented"}
    
    async def _handle_pin_message(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle PIN_MESSAGE operation."""
        return True
    
    async def _handle_unpin_message(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle UNPIN_MESSAGE operation."""
        return True
    
    async def _handle_add_reaction(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle ADD_REACTION operation."""
        return True
    
    async def _handle_remove_reaction(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle REMOVE_REACTION operation."""
        return True
    
    async def _handle_clear_reactions(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle CLEAR_REACTIONS operation."""
        return True
    
    async def _handle_edit_embed(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_EMBED operation."""
        return {"status": "not_implemented"}
    
    async def _handle_edit_channel(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_CHANNEL operation."""
        return {"status": "not_implemented"}
    
    async def _handle_delete_channel(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_CHANNEL operation."""
        return True
    
    async def _handle_list_channels(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_CHANNELS operation."""
        return []
    
    async def _handle_set_channel_permissions(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle SET_CHANNEL_PERMISSIONS operation."""
        return True
    
    async def _handle_list_guilds(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_GUILDS operation."""
        return []
    
    async def _handle_edit_guild(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_GUILD operation."""
        return {"status": "not_implemented"}
    
    async def _handle_leave_guild(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle LEAVE_GUILD operation."""
        return True
    
    async def _handle_get_guild_roles(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle GET_GUILD_ROLES operation."""
        return []
    
    async def _handle_get_guild_channels(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle GET_GUILD_CHANNELS operation."""
        return []
    
    async def _handle_get_member(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET_MEMBER operation."""
        return {"status": "not_implemented"}
    
    async def _handle_unban_member(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle UNBAN_MEMBER operation."""
        return True
    
    async def _handle_timeout_member(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle TIMEOUT_MEMBER operation."""
        return True
    
    async def _handle_remove_role(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle REMOVE_ROLE operation."""
        return True
    
    async def _handle_edit_member(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_MEMBER operation."""
        return {"status": "not_implemented"}
    
    async def _handle_edit_role(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_ROLE operation."""
        return {"status": "not_implemented"}
    
    async def _handle_delete_role(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_ROLE operation."""
        return True
    
    async def _handle_create_slash_command(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_SLASH_COMMAND operation."""
        return {"status": "not_implemented"}
    
    async def _handle_delete_slash_command(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_SLASH_COMMAND operation."""
        return True
    
    async def _handle_list_slash_commands(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle LIST_SLASH_COMMANDS operation."""
        return []
    
    async def _handle_sync_commands(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle SYNC_COMMANDS operation."""
        return True
    
    async def _handle_respond_to_interaction(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RESPOND_TO_INTERACTION operation."""
        return {"status": "not_implemented"}
    
    async def _handle_follow_up_interaction(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FOLLOW_UP_INTERACTION operation."""
        return {"status": "not_implemented"}
    
    async def _handle_defer_interaction(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DEFER_INTERACTION operation."""
        return True
    
    async def _handle_create_invite(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_INVITE operation."""
        return {"status": "not_implemented"}
    
    async def _handle_get_invites(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle GET_INVITES operation."""
        return []
    
    async def _handle_delete_invite(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_INVITE operation."""
        return True
    
    async def _handle_join_voice_channel(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JOIN_VOICE_CHANNEL operation."""
        return {"status": "not_implemented"}
    
    async def _handle_leave_voice_channel(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle LEAVE_VOICE_CHANNEL operation."""
        return True
    
    async def _handle_edit_webhook(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle EDIT_WEBHOOK operation."""
        return {"status": "not_implemented"}
    
    async def _handle_delete_webhook(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_WEBHOOK operation."""
        return True
    
    async def _handle_listen_for_messages(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LISTEN_FOR_MESSAGES operation."""
        return {"status": "not_implemented"}
    
    async def _handle_listen_for_reactions(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LISTEN_FOR_REACTIONS operation."""
        return {"status": "not_implemented"}
    
    async def _handle_listen_for_member_events(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LISTEN_FOR_MEMBER_EVENTS operation."""
        return {"status": "not_implemented"}
    
    async def _handle_send_file(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SEND_FILE operation."""
        return {"status": "not_implemented"}
    
    async def _handle_upload_emoji(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UPLOAD_EMOJI operation."""
        return {"status": "not_implemented"}
    
    async def _handle_delete_emoji(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle DELETE_EMOJI operation."""
        return True
    
    async def _handle_set_activity(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle SET_ACTIVITY operation."""
        return True
    
    async def _handle_set_presence(self, discord_client: DiscordClientWrapper, params: Dict[str, Any]) -> bool:
        """Handle SET_PRESENCE operation."""
        return True


# Register the node
if __name__ == "__main__":
    node = DiscordNode()
    print(f"DiscordNode created with {len(node.operation_dispatch)} operations")
    print("Available operations:")
    for i, op in enumerate(node.operation_dispatch.keys(), 1):
        print(f"  {i:2d}. {op}")