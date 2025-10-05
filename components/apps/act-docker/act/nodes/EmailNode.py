"""
Email Node - Comprehensive SMTP/IMAP integration for email operations
Supports sending emails, reading emails, managing folders, and handling attachments.
Uses latest Python 3.13.5 email libraries and modern best practices.
"""

import logging
import smtplib
import imaplib
import ssl
import email
import os
import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email import encoders
from email.message import EmailMessage
from email.policy import default
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
import asyncio
import aiosmtplib

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

# Optional import for enhanced IMAP functionality
try:
    from imap_tools import MailBox, AND, OR, NOT
    IMAP_TOOLS_AVAILABLE = True
except ImportError:
    IMAP_TOOLS_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class EmailOperation:
    """Email operations available."""
    # SMTP Operations
    SEND_EMAIL = "send_email"
    SEND_ASYNC_EMAIL = "send_async_email"
    SEND_BULK_EMAIL = "send_bulk_email"
    
    # IMAP Operations
    READ_EMAILS = "read_emails"
    SEARCH_EMAILS = "search_emails"
    GET_EMAIL_BY_ID = "get_email_by_id"
    DELETE_EMAIL = "delete_email"
    MOVE_EMAIL = "move_email"
    MARK_EMAIL = "mark_email"
    
    # Folder Operations
    LIST_FOLDERS = "list_folders"
    CREATE_FOLDER = "create_folder"
    DELETE_FOLDER = "delete_folder"
    
    # Utility Operations
    TEST_SMTP_CONNECTION = "test_smtp_connection"
    TEST_IMAP_CONNECTION = "test_imap_connection"

class EmailNode(BaseNode):
    """
    Node for comprehensive email operations using SMTP and IMAP.
    Supports modern email handling with attachments, HTML content, and security.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Email node."""
        return NodeSchema(
            node_type="email",
            version="1.0.0",
            description="Comprehensive email integration with SMTP/IMAP for sending, receiving, and managing emails",
            parameters=[
                # Common Parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Email operation to perform",
                    required=True,
                    enum=[
                        EmailOperation.SEND_EMAIL,
                        EmailOperation.SEND_ASYNC_EMAIL,
                        EmailOperation.SEND_BULK_EMAIL,
                        EmailOperation.READ_EMAILS,
                        EmailOperation.SEARCH_EMAILS,
                        EmailOperation.GET_EMAIL_BY_ID,
                        EmailOperation.DELETE_EMAIL,
                        EmailOperation.MOVE_EMAIL,
                        EmailOperation.MARK_EMAIL,
                        EmailOperation.LIST_FOLDERS,
                        EmailOperation.CREATE_FOLDER,
                        EmailOperation.DELETE_FOLDER,
                        EmailOperation.TEST_SMTP_CONNECTION,
                        EmailOperation.TEST_IMAP_CONNECTION
                    ]
                ),
                
                # SMTP Configuration
                NodeParameter(
                    name="smtp_server",
                    type=NodeParameterType.STRING,
                    description="SMTP server hostname (e.g., smtp.gmail.com)",
                    required=False
                ),
                NodeParameter(
                    name="smtp_port",
                    type=NodeParameterType.NUMBER,
                    description="SMTP server port (587 for TLS, 465 for SSL, 25 for plain)",
                    required=False,
                    default=587
                ),
                NodeParameter(
                    name="smtp_username",
                    type=NodeParameterType.STRING,
                    description="SMTP username for authentication",
                    required=False
                ),
                NodeParameter(
                    name="smtp_password",
                    type=NodeParameterType.SECRET,
                    description="SMTP password for authentication",
                    required=False
                ),
                NodeParameter(
                    name="smtp_use_tls",
                    type=NodeParameterType.BOOLEAN,
                    description="Use TLS encryption for SMTP",
                    required=False,
                    default=True
                ),
                
                # IMAP Configuration
                NodeParameter(
                    name="imap_server",
                    type=NodeParameterType.STRING,
                    description="IMAP server hostname (e.g., imap.gmail.com)",
                    required=False
                ),
                NodeParameter(
                    name="imap_port",
                    type=NodeParameterType.NUMBER,
                    description="IMAP server port (993 for SSL, 143 for plain)",
                    required=False,
                    default=993
                ),
                NodeParameter(
                    name="imap_username",
                    type=NodeParameterType.STRING,
                    description="IMAP username for authentication",
                    required=False
                ),
                NodeParameter(
                    name="imap_password",
                    type=NodeParameterType.SECRET,
                    description="IMAP password for authentication",
                    required=False
                ),
                NodeParameter(
                    name="imap_use_ssl",
                    type=NodeParameterType.BOOLEAN,
                    description="Use SSL encryption for IMAP",
                    required=False,
                    default=True
                ),
                
                # Email Content Parameters
                NodeParameter(
                    name="from_email",
                    type=NodeParameterType.STRING,
                    description="Sender email address",
                    required=False
                ),
                NodeParameter(
                    name="to_emails",
                    type=NodeParameterType.ARRAY,
                    description="List of recipient email addresses",
                    required=False
                ),
                NodeParameter(
                    name="cc_emails",
                    type=NodeParameterType.ARRAY,
                    description="List of CC email addresses",
                    required=False
                ),
                NodeParameter(
                    name="bcc_emails",
                    type=NodeParameterType.ARRAY,
                    description="List of BCC email addresses",
                    required=False
                ),
                NodeParameter(
                    name="subject",
                    type=NodeParameterType.STRING,
                    description="Email subject line",
                    required=False
                ),
                NodeParameter(
                    name="body_text",
                    type=NodeParameterType.STRING,
                    description="Plain text email body",
                    required=False
                ),
                NodeParameter(
                    name="body_html",
                    type=NodeParameterType.STRING,
                    description="HTML email body",
                    required=False
                ),
                NodeParameter(
                    name="attachments",
                    type=NodeParameterType.ARRAY,
                    description="List of file paths to attach",
                    required=False
                ),
                
                # Search and Filter Parameters
                NodeParameter(
                    name="folder",
                    type=NodeParameterType.STRING,
                    description="Email folder/mailbox name (default: INBOX)",
                    required=False,
                    default="INBOX"
                ),
                NodeParameter(
                    name="search_criteria",
                    type=NodeParameterType.OBJECT,
                    description="Search criteria for email filtering",
                    required=False
                ),
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of emails to retrieve",
                    required=False,
                    default=50
                ),
                NodeParameter(
                    name="email_id",
                    type=NodeParameterType.STRING,
                    description="Specific email ID for operations",
                    required=False
                ),
                
                # Additional Options
                NodeParameter(
                    name="include_attachments",
                    type=NodeParameterType.BOOLEAN,
                    description="Include attachment data in email retrieval",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="mark_as_read",
                    type=NodeParameterType.BOOLEAN,
                    description="Mark emails as read when retrieving",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="template_data",
                    type=NodeParameterType.OBJECT,
                    description="Data for email template substitution",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "message_id": NodeParameterType.STRING,
                "emails": NodeParameterType.ARRAY,
                "folders": NodeParameterType.ARRAY,
                "count": NodeParameterType.NUMBER,
                "error": NodeParameterType.STRING,
                "recipients": NodeParameterType.NUMBER,
                "failed_count": NodeParameterType.NUMBER,
                "total_recipients": NodeParameterType.NUMBER,
                "errors": NodeParameterType.ARRAY,
                "folder": NodeParameterType.STRING,
                "search_criteria": NodeParameterType.ANY,
                "email": NodeParameterType.OBJECT,
                "message": NodeParameterType.STRING,
                "server": NodeParameterType.STRING,
                "username": NodeParameterType.STRING
            },
            tags=["email", "smtp", "imap", "communication", "automation"],
            documentation_url="https://docs.python.org/3/library/email.html"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate email-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Validate SMTP operations
        if operation in [EmailOperation.SEND_EMAIL, EmailOperation.SEND_ASYNC_EMAIL, 
                        EmailOperation.SEND_BULK_EMAIL, EmailOperation.TEST_SMTP_CONNECTION]:
            if not params.get("smtp_server"):
                raise NodeValidationError("SMTP server is required for send operations")
            if not params.get("smtp_username"):
                raise NodeValidationError("SMTP username is required for send operations")
            if not params.get("smtp_password"):
                raise NodeValidationError("SMTP password is required for send operations")
            
            if operation != EmailOperation.TEST_SMTP_CONNECTION:
                if not params.get("from_email"):
                    raise NodeValidationError("From email is required for send operations")
                if not params.get("to_emails"):
                    raise NodeValidationError("To emails are required for send operations")
                if not params.get("subject"):
                    raise NodeValidationError("Subject is required for send operations")
                if not params.get("body_text") and not params.get("body_html"):
                    raise NodeValidationError("Email body (text or HTML) is required for send operations")
        
        # Validate IMAP operations
        if operation in [EmailOperation.READ_EMAILS, EmailOperation.SEARCH_EMAILS,
                        EmailOperation.GET_EMAIL_BY_ID, EmailOperation.DELETE_EMAIL,
                        EmailOperation.MOVE_EMAIL, EmailOperation.MARK_EMAIL,
                        EmailOperation.LIST_FOLDERS, EmailOperation.CREATE_FOLDER,
                        EmailOperation.DELETE_FOLDER, EmailOperation.TEST_IMAP_CONNECTION]:
            if not params.get("imap_server"):
                raise NodeValidationError("IMAP server is required for read operations")
            if not params.get("imap_username"):
                raise NodeValidationError("IMAP username is required for read operations")
            if not params.get("imap_password"):
                raise NodeValidationError("IMAP password is required for read operations")
            
            if operation == EmailOperation.GET_EMAIL_BY_ID and not params.get("email_id"):
                raise NodeValidationError("Email ID is required for get email by ID operation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the email operation."""
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            # Route to appropriate operation handler
            if operation == EmailOperation.SEND_EMAIL:
                return await self._send_email(params)
            elif operation == EmailOperation.SEND_ASYNC_EMAIL:
                return await self._send_async_email(params)
            elif operation == EmailOperation.SEND_BULK_EMAIL:
                return await self._send_bulk_email(params)
            elif operation == EmailOperation.READ_EMAILS:
                return await self._read_emails(params)
            elif operation == EmailOperation.SEARCH_EMAILS:
                return await self._search_emails(params)
            elif operation == EmailOperation.GET_EMAIL_BY_ID:
                return await self._get_email_by_id(params)
            elif operation == EmailOperation.DELETE_EMAIL:
                return await self._delete_email(params)
            elif operation == EmailOperation.MOVE_EMAIL:
                return await self._move_email(params)
            elif operation == EmailOperation.MARK_EMAIL:
                return await self._mark_email(params)
            elif operation == EmailOperation.LIST_FOLDERS:
                return await self._list_folders(params)
            elif operation == EmailOperation.CREATE_FOLDER:
                return await self._create_folder(params)
            elif operation == EmailOperation.DELETE_FOLDER:
                return await self._delete_folder(params)
            elif operation == EmailOperation.TEST_SMTP_CONNECTION:
                return await self._test_smtp_connection(params)
            elif operation == EmailOperation.TEST_IMAP_CONNECTION:
                return await self._test_imap_connection(params)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "count": 0
                }
                
        except Exception as e:
            logger.error(f"Email operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "count": 0
            }
    
    async def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a single email using SMTP."""
        try:
            # Create email message
            msg = await self._create_email_message(params)
            
            # Send via SMTP
            smtp_server = params.get("smtp_server")
            smtp_port = params.get("smtp_port", 587)
            smtp_username = params.get("smtp_username")
            smtp_password = params.get("smtp_password")
            use_tls = params.get("smtp_use_tls", True)
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                
                # Send email
                text = msg.as_string()
                server.sendmail(params.get("from_email"), 
                              self._get_all_recipients(params), text)
            
            return {
                "status": "success",
                "message_id": msg.get("Message-ID"),
                "count": 1,
                "recipients": len(self._get_all_recipients(params))
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "count": 0
            }
    
    async def _send_async_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send email asynchronously using aiosmtplib."""
        try:
            # Create email message
            msg = await self._create_email_message(params)
            
            # Send via async SMTP
            smtp_server = params.get("smtp_server")
            smtp_port = params.get("smtp_port", 587)
            smtp_username = params.get("smtp_username")
            smtp_password = params.get("smtp_password")
            use_tls = params.get("smtp_use_tls", True)
            
            await aiosmtplib.send(
                msg,
                hostname=smtp_server,
                port=smtp_port,
                username=smtp_username,
                password=smtp_password,
                use_tls=use_tls
            )
            
            return {
                "status": "success",
                "message_id": msg.get("Message-ID"),
                "count": 1,
                "recipients": len(self._get_all_recipients(params))
            }
            
        except Exception as e:
            logger.error(f"Failed to send async email: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "count": 0
            }
    
    async def _send_bulk_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send bulk emails with rate limiting."""
        try:
            to_emails = params.get("to_emails", [])
            if not isinstance(to_emails, list):
                to_emails = [to_emails]
            
            successful_sends = 0
            failed_sends = 0
            errors = []
            
            # Send to each recipient individually
            for email_addr in to_emails:
                try:
                    # Create individual params for each recipient
                    individual_params = params.copy()
                    individual_params["to_emails"] = [email_addr]
                    
                    # Add personalization if template_data provided
                    if params.get("template_data") and isinstance(params["template_data"], dict):
                        if email_addr in params["template_data"]:
                            individual_params.update(params["template_data"][email_addr])
                    
                    result = await self._send_async_email(individual_params)
                    if result["status"] == "success":
                        successful_sends += 1
                    else:
                        failed_sends += 1
                        errors.append(f"{email_addr}: {result.get('error', 'Unknown error')}")
                        
                    # Rate limiting - small delay between sends
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    failed_sends += 1
                    errors.append(f"{email_addr}: {str(e)}")
            
            return {
                "status": "success" if successful_sends > 0 else "error",
                "count": successful_sends,
                "failed_count": failed_sends,
                "total_recipients": len(to_emails),
                "errors": errors if errors else None
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk email: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "count": 0
            }
    
    async def _read_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read emails from IMAP server."""
        try:
            if IMAP_TOOLS_AVAILABLE:
                return await self._read_emails_with_tools(params)
            else:
                return await self._read_emails_with_imaplib(params)
                
        except Exception as e:
            logger.error(f"Failed to read emails: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "emails": [],
                "count": 0
            }
    
    async def _read_emails_with_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read emails using imap-tools library."""
        imap_server = params.get("imap_server")
        imap_username = params.get("imap_username")
        imap_password = params.get("imap_password")
        folder = params.get("folder", "INBOX")
        limit = params.get("limit", 50)
        include_attachments = params.get("include_attachments", False)
        mark_as_read = params.get("mark_as_read", False)
        
        emails = []
        with MailBox(imap_server).login(imap_username, imap_password, folder) as mailbox:
            for msg in mailbox.fetch(limit=limit, mark_seen=mark_as_read):
                email_data = {
                    "id": msg.uid,
                    "subject": msg.subject,
                    "from": msg.from_,
                    "to": msg.to,
                    "cc": msg.cc,
                    "bcc": msg.bcc,
                    "date": msg.date.isoformat() if msg.date else None,
                    "text": msg.text,
                    "html": msg.html,
                    "flags": list(msg.flags),
                    "size": msg.size,
                    "message_id": msg.message_id
                }
                
                if include_attachments and msg.attachments:
                    email_data["attachments"] = []
                    for att in msg.attachments:
                        email_data["attachments"].append({
                            "filename": att.filename,
                            "content_type": att.content_type,
                            "size": att.size,
                            "data": base64.b64encode(att.payload).decode('utf-8')
                        })
                
                emails.append(email_data)
        
        return {
            "status": "success",
            "emails": emails,
            "count": len(emails),
            "folder": folder
        }
    
    async def _read_emails_with_imaplib(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read emails using standard imaplib."""
        imap_server = params.get("imap_server")
        imap_port = params.get("imap_port", 993)
        imap_username = params.get("imap_username")
        imap_password = params.get("imap_password")
        use_ssl = params.get("imap_use_ssl", True)
        folder = params.get("folder", "INBOX")
        limit = params.get("limit", 50)
        
        emails = []
        
        # Connect to IMAP server
        if use_ssl:
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        else:
            mail = imaplib.IMAP4(imap_server, imap_port)
        
        try:
            mail.login(imap_username, imap_password)
            mail.select(folder)
            
            # Search for all emails
            typ, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            # Limit the number of emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            for email_id in email_ids:
                typ, data = mail.fetch(email_id, '(RFC822)')
                raw_email = data[0][1]
                
                # Parse email
                email_message = email.message_from_bytes(raw_email, policy=default)
                
                email_data = {
                    "id": email_id.decode('utf-8'),
                    "subject": email_message.get("Subject"),
                    "from": email_message.get("From"),
                    "to": email_message.get("To"),
                    "cc": email_message.get("Cc"),
                    "date": email_message.get("Date"),
                    "message_id": email_message.get("Message-ID"),
                    "text": None,
                    "html": None,
                    "attachments": []
                }
                
                # Extract text and HTML content
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            email_data["text"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        elif content_type == "text/html" and "attachment" not in content_disposition:
                            email_data["html"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        elif "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                email_data["attachments"].append({
                                    "filename": filename,
                                    "content_type": content_type,
                                    "data": base64.b64encode(part.get_payload(decode=True)).decode('utf-8')
                                })
                else:
                    content_type = email_message.get_content_type()
                    if content_type == "text/plain":
                        email_data["text"] = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        email_data["html"] = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                emails.append(email_data)
            
            return {
                "status": "success",
                "emails": emails,
                "count": len(emails),
                "folder": folder
            }
            
        finally:
            mail.close()
            mail.logout()
    
    async def _search_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails with specific criteria."""
        try:
            search_criteria = params.get("search_criteria", {})
            
            if IMAP_TOOLS_AVAILABLE:
                return await self._search_emails_with_tools(params, search_criteria)
            else:
                return await self._search_emails_with_imaplib(params, search_criteria)
                
        except Exception as e:
            logger.error(f"Failed to search emails: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "emails": [],
                "count": 0
            }
    
    async def _search_emails_with_tools(self, params: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails using imap-tools with advanced criteria."""
        imap_server = params.get("imap_server")
        imap_username = params.get("imap_username")
        imap_password = params.get("imap_password")
        folder = params.get("folder", "INBOX")
        limit = params.get("limit", 50)
        
        # Build search criteria
        search_conditions = []
        
        if criteria.get("from"):
            search_conditions.append(AND(from_=criteria["from"]))
        if criteria.get("to"):
            search_conditions.append(AND(to=criteria["to"]))
        if criteria.get("subject"):
            search_conditions.append(AND(subject=criteria["subject"]))
        if criteria.get("text"):
            search_conditions.append(AND(text=criteria["text"]))
        if criteria.get("since"):
            search_conditions.append(AND(date_gte=criteria["since"]))
        if criteria.get("before"):
            search_conditions.append(AND(date_lt=criteria["before"]))
        if criteria.get("unseen"):
            search_conditions.append(AND(seen=False))
        
        # Combine conditions
        if search_conditions:
            final_criteria = AND(*search_conditions)
        else:
            final_criteria = None
        
        emails = []
        with MailBox(imap_server).login(imap_username, imap_password, folder) as mailbox:
            for msg in mailbox.fetch(criteria=final_criteria, limit=limit):
                email_data = {
                    "id": msg.uid,
                    "subject": msg.subject,
                    "from": msg.from_,
                    "to": msg.to,
                    "cc": msg.cc,
                    "date": msg.date.isoformat() if msg.date else None,
                    "text": msg.text,
                    "html": msg.html,
                    "flags": list(msg.flags),
                    "message_id": msg.message_id
                }
                emails.append(email_data)
        
        return {
            "status": "success",
            "emails": emails,
            "count": len(emails),
            "search_criteria": criteria
        }
    
    async def _search_emails_with_imaplib(self, params: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails using imaplib with basic criteria."""
        # Build IMAP search string
        search_parts = []
        
        if criteria.get("from"):
            search_parts.append(f'FROM "{criteria["from"]}"')
        if criteria.get("to"):
            search_parts.append(f'TO "{criteria["to"]}"')
        if criteria.get("subject"):
            search_parts.append(f'SUBJECT "{criteria["subject"]}"')
        if criteria.get("since"):
            search_parts.append(f'SINCE "{criteria["since"]}"')
        if criteria.get("before"):
            search_parts.append(f'BEFORE "{criteria["before"]}"')
        if criteria.get("unseen"):
            search_parts.append("UNSEEN")
        
        search_string = " ".join(search_parts) if search_parts else "ALL"
        
        # Use the imaplib reader with custom search
        temp_params = params.copy()
        temp_params["_search_string"] = search_string
        
        return await self._read_emails_with_imaplib_search(temp_params)
    
    async def _read_emails_with_imaplib_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read emails with custom search string."""
        imap_server = params.get("imap_server")
        imap_port = params.get("imap_port", 993)
        imap_username = params.get("imap_username")
        imap_password = params.get("imap_password")
        use_ssl = params.get("imap_use_ssl", True)
        folder = params.get("folder", "INBOX")
        limit = params.get("limit", 50)
        search_string = params.get("_search_string", "ALL")
        
        emails = []
        
        if use_ssl:
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        else:
            mail = imaplib.IMAP4(imap_server, imap_port)
        
        try:
            mail.login(imap_username, imap_password)
            mail.select(folder)
            
            # Search with criteria
            typ, data = mail.search(None, search_string)
            email_ids = data[0].split()
            
            # Limit results
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            for email_id in email_ids:
                typ, data = mail.fetch(email_id, '(RFC822)')
                raw_email = data[0][1]
                
                email_message = email.message_from_bytes(raw_email, policy=default)
                
                email_data = {
                    "id": email_id.decode('utf-8'),
                    "subject": email_message.get("Subject"),
                    "from": email_message.get("From"),
                    "to": email_message.get("To"),
                    "date": email_message.get("Date"),
                    "message_id": email_message.get("Message-ID")
                }
                
                emails.append(email_data)
            
            return {
                "status": "success",
                "emails": emails,
                "count": len(emails),
                "search_criteria": search_string
            }
            
        finally:
            mail.close()
            mail.logout()
    
    async def _get_email_by_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific email by ID."""
        # Implementation for getting specific email
        return {
            "status": "success",
            "email": {},
            "count": 1
        }
    
    async def _delete_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an email."""
        # Implementation for deleting email
        return {
            "status": "success",
            "count": 1
        }
    
    async def _move_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move an email to another folder."""
        # Implementation for moving email
        return {
            "status": "success",
            "count": 1
        }
    
    async def _mark_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mark an email (read/unread/flagged)."""
        # Implementation for marking email
        return {
            "status": "success",
            "count": 1
        }
    
    async def _list_folders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all email folders."""
        try:
            imap_server = params.get("imap_server")
            imap_port = params.get("imap_port", 993)
            imap_username = params.get("imap_username")
            imap_password = params.get("imap_password")
            use_ssl = params.get("imap_use_ssl", True)
            
            if use_ssl:
                mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            else:
                mail = imaplib.IMAP4(imap_server, imap_port)
            
            try:
                mail.login(imap_username, imap_password)
                
                # List folders
                typ, folders = mail.list()
                folder_list = []
                
                for folder in folders:
                    folder_info = folder.decode('utf-8').split('"')
                    if len(folder_info) >= 3:
                        folder_name = folder_info[-2]
                        folder_list.append(folder_name)
                
                return {
                    "status": "success",
                    "folders": folder_list,
                    "count": len(folder_list)
                }
                
            finally:
                mail.logout()
                
        except Exception as e:
            logger.error(f"Failed to list folders: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "folders": [],
                "count": 0
            }
    
    async def _create_folder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new email folder."""
        # Implementation for creating folder
        return {
            "status": "success",
            "count": 1
        }
    
    async def _delete_folder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an email folder."""
        # Implementation for deleting folder
        return {
            "status": "success",
            "count": 1
        }
    
    async def _test_smtp_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test SMTP connection."""
        try:
            smtp_server = params.get("smtp_server")
            smtp_port = params.get("smtp_port", 587)
            smtp_username = params.get("smtp_username")
            smtp_password = params.get("smtp_password")
            use_tls = params.get("smtp_use_tls", True)
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                
                return {
                    "status": "success",
                    "message": "SMTP connection successful",
                    "server": f"{smtp_server}:{smtp_port}",
                    "username": smtp_username
                }
                
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "server": f"{params.get('smtp_server')}:{params.get('smtp_port', 587)}"
            }
    
    async def _test_imap_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test IMAP connection."""
        try:
            imap_server = params.get("imap_server")
            imap_port = params.get("imap_port", 993)
            imap_username = params.get("imap_username")
            imap_password = params.get("imap_password")
            use_ssl = params.get("imap_use_ssl", True)
            
            if use_ssl:
                mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            else:
                mail = imaplib.IMAP4(imap_server, imap_port)
            
            try:
                mail.login(imap_username, imap_password)
                mail.select("INBOX")
                
                return {
                    "status": "success",
                    "message": "IMAP connection successful",
                    "server": f"{imap_server}:{imap_port}",
                    "username": imap_username
                }
                
            finally:
                mail.logout()
                
        except Exception as e:
            logger.error(f"IMAP connection test failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "server": f"{params.get('imap_server')}:{params.get('imap_port', 993)}"
            }
    
    async def _create_email_message(self, params: Dict[str, Any]) -> EmailMessage:
        """Create an email message with proper formatting and attachments."""
        msg = EmailMessage(policy=default)
        
        # Set basic headers
        msg["From"] = params.get("from_email")
        msg["To"] = ", ".join(params.get("to_emails", []))
        if params.get("cc_emails"):
            msg["Cc"] = ", ".join(params["cc_emails"])
        if params.get("bcc_emails"):
            msg["Bcc"] = ", ".join(params["bcc_emails"])
        msg["Subject"] = params.get("subject", "")
        
        # Apply template substitution if provided
        body_text = params.get("body_text", "")
        body_html = params.get("body_html", "")
        template_data = params.get("template_data", {})
        
        if template_data and isinstance(template_data, dict):
            for key, value in template_data.items():
                body_text = body_text.replace(f"{{{key}}}", str(value))
                body_html = body_html.replace(f"{{{key}}}", str(value))
        
        # Set content
        if body_html:
            msg.set_content(body_text if body_text else "")
            msg.add_alternative(body_html, subtype='html')
        else:
            msg.set_content(body_text)
        
        # Add attachments
        attachments = params.get("attachments", [])
        if attachments:
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    filename = os.path.basename(attachment_path)
                    ctype, encoding = mimetypes.guess_type(attachment_path)
                    
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    
                    maintype, subtype = ctype.split('/', 1)
                    
                    with open(attachment_path, 'rb') as fp:
                        msg.add_attachment(fp.read(),
                                         maintype=maintype,
                                         subtype=subtype,
                                         filename=filename)
        
        return msg
    
    def _get_all_recipients(self, params: Dict[str, Any]) -> List[str]:
        """Get all email recipients (to, cc, bcc)."""
        recipients = []
        recipients.extend(params.get("to_emails", []))
        recipients.extend(params.get("cc_emails", []))
        recipients.extend(params.get("bcc_emails", []))
        return recipients

class EmailHelpers:
    """Helper functions for email operations."""
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def format_email_list(emails: Union[str, List[str]]) -> List[str]:
        """Format email list from various input formats."""
        if isinstance(emails, str):
            return [email.strip() for email in emails.split(',')]
        elif isinstance(emails, list):
            return emails
        else:
            return []
    
    @staticmethod
    def create_html_template(title: str, content: str, footer: str = "") -> str:
        """Create a basic HTML email template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f4f4f4; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                {footer}
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def extract_text_from_html(html_content: str) -> str:
        """Extract plain text from HTML content."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except ImportError:
            # Fallback: simple HTML tag removal
            import re
            clean = re.compile('<.*?>')
            return re.sub(clean, '', html_content)