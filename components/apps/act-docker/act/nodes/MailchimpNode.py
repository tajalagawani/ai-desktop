"""
Mailchimp Node - Comprehensive integration with Mailchimp Marketing API v3

Provides access to all Mailchimp API operations including lists, campaigns, automations, reports, and audience management.
Supports complete email marketing workflow integration with audience management, campaign creation and automation,
detailed analytics and reporting, and comprehensive subscriber engagement tracking.

Key capabilities include: List and audience management, subscriber lifecycle tracking, campaign creation and scheduling,
automation workflow setup, template management, reporting and analytics, A/B testing, segmentation and targeting,
interest categories and tags, e-commerce integration, and comprehensive email marketing automation.

Built for production environments with API key authentication, comprehensive error handling,
rate limiting compliance, and team collaboration features for email marketing and audience management.
"""

import logging
from typing import Dict, Any, Optional

try:
    from universal_request_node import UniversalRequestNode
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from universal_request_node import UniversalRequestNode
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

logger = logging.getLogger(__name__)

class MailchimpNode(BaseNode):
    """Comprehensive Mailchimp Marketing API v3 integration node."""
    
    # Embedded configuration for Mailchimp API
    CONFIG = {
        "base_url": "https://{dc}.api.mailchimp.com/3.0",
        "authentication": {
            "type": "basic_auth",
            "username": "anystring",
            "password": "{api_key}"
        },
        "headers": {
            "Content-Type": "application/json"
        },
        "timeout": 30,
        "retry_config": {
            "max_retries": 3,
            "retry_delay": 1.0,
            "exponential_backoff": True
        },
        "rate_limiting": {
            "max_requests_per_minute": 600,
            "burst_limit": 60
        }
    }
    
    # Complete operations mapping for Mailchimp API (80+ key operations)
    OPERATIONS = {
        # Authentication
        "ping": {
            "method": "GET",
            "endpoint": "/ping",
            "params": [],
            "required": []
        },
        
        # Lists Operations
        "get_lists": {
            "method": "GET",
            "endpoint": "/lists",
            "params": ["fields", "exclude_fields", "count", "offset", "before_date_created", "since_date_created", "before_campaign_last_sent", "since_campaign_last_sent", "email", "sort_field", "sort_dir"],
            "required": []
        },
        "get_list": {
            "method": "GET",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id", "fields", "exclude_fields", "include_total_contacts"],
            "required": ["list_id"]
        },
        "create_list": {
            "method": "POST",
            "endpoint": "/lists",
            "params": ["list_name", "permission_reminder", "use_archive_bar", "campaign_defaults", "notify_on_subscribe", "notify_on_unsubscribe", "email_type_option", "double_optin", "marketing_permissions", "request_body"],
            "required": ["list_name", "permission_reminder", "campaign_defaults"]
        },
        "update_list": {
            "method": "PATCH",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id", "request_body"],
            "required": ["list_id", "request_body"]
        },
        "delete_list": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id"],
            "required": ["list_id"]
        },
        "batch_sub_or_unsub": {
            "method": "POST",
            "endpoint": "/lists/{list_id}",
            "params": ["list_id", "members", "update_existing", "request_body"],
            "required": ["list_id", "members"]
        },
        
        # List Members Operations
        "get_list_members": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/members",
            "params": ["list_id", "fields", "exclude_fields", "count", "offset", "email_type", "status", "since_timestamp_opt", "before_timestamp_opt", "since_last_changed", "before_last_changed", "unique_email_id", "vip_only", "interest_category_id", "interest_ids", "interest_match", "sort_field", "sort_dir", "since_last_campaign", "unsubscribed_since"],
            "required": ["list_id"]
        },
        "get_list_member": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}",
            "params": ["list_id", "subscriber_hash", "fields", "exclude_fields"],
            "required": ["list_id", "subscriber_hash"]
        },
        "add_list_member": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/members",
            "params": ["list_id", "email_address", "status", "email_type", "merge_fields", "interests", "language", "vip", "location", "marketing_permissions", "ip_signup", "timestamp_signup", "ip_opt", "timestamp_opt", "tags", "request_body"],
            "required": ["list_id", "email_address", "status"]
        },
        "update_list_member": {
            "method": "PATCH",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}",
            "params": ["list_id", "subscriber_hash", "request_body"],
            "required": ["list_id", "subscriber_hash", "request_body"]
        },
        "add_or_update_list_member": {
            "method": "PUT",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}",
            "params": ["list_id", "subscriber_hash", "email_address", "status_if_new", "merge_fields", "interests", "language", "vip", "location", "marketing_permissions", "ip_signup", "timestamp_signup", "ip_opt", "timestamp_opt", "tags", "request_body"],
            "required": ["list_id", "subscriber_hash", "email_address", "status_if_new"]
        },
        "delete_list_member": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}",
            "params": ["list_id", "subscriber_hash"],
            "required": ["list_id", "subscriber_hash"]
        },
        "archive_list_member": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}/actions/delete-permanent",
            "params": ["list_id", "subscriber_hash"],
            "required": ["list_id", "subscriber_hash"]
        },
        
        # List Member Tags Operations
        "get_list_member_tags": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}/tags",
            "params": ["list_id", "subscriber_hash", "fields", "exclude_fields", "count", "offset"],
            "required": ["list_id", "subscriber_hash"]
        },
        "add_list_member_tags": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}/tags",
            "params": ["list_id", "subscriber_hash", "tags", "request_body"],
            "required": ["list_id", "subscriber_hash", "tags"]
        },
        "remove_list_member_tags": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/members/{subscriber_hash}/tags",
            "params": ["list_id", "subscriber_hash", "tags", "request_body"],
            "required": ["list_id", "subscriber_hash", "tags"]
        },
        
        # List Segments Operations
        "get_list_segments": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/segments",
            "params": ["list_id", "fields", "exclude_fields", "count", "offset", "type", "since_created_at", "before_created_at", "include_cleaned", "include_transactional", "include_unsubscribed"],
            "required": ["list_id"]
        },
        "get_list_segment": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/segments/{segment_id}",
            "params": ["list_id", "segment_id", "fields", "exclude_fields", "include_cleaned", "include_transactional", "include_unsubscribed"],
            "required": ["list_id", "segment_id"]
        },
        "create_list_segment": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/segments",
            "params": ["list_id", "segment_name", "static_segment", "options", "request_body"],
            "required": ["list_id", "segment_name"]
        },
        "update_list_segment": {
            "method": "PATCH",
            "endpoint": "/lists/{list_id}/segments/{segment_id}",
            "params": ["list_id", "segment_id", "request_body"],
            "required": ["list_id", "segment_id", "request_body"]
        },
        "delete_list_segment": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}/segments/{segment_id}",
            "params": ["list_id", "segment_id"],
            "required": ["list_id", "segment_id"]
        },
        "get_segment_members": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/segments/{segment_id}/members",
            "params": ["list_id", "segment_id", "fields", "exclude_fields", "count", "offset", "include_cleaned", "include_transactional", "include_unsubscribed"],
            "required": ["list_id", "segment_id"]
        },
        "add_segment_member": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/segments/{segment_id}/members",
            "params": ["list_id", "segment_id", "email_address", "request_body"],
            "required": ["list_id", "segment_id", "email_address"]
        },
        "remove_segment_member": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}/segments/{segment_id}/members/{subscriber_hash}",
            "params": ["list_id", "segment_id", "subscriber_hash"],
            "required": ["list_id", "segment_id", "subscriber_hash"]
        },
        
        # Interest Categories Operations
        "get_interest_categories": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/interest-categories",
            "params": ["list_id", "fields", "exclude_fields", "count", "offset", "type"],
            "required": ["list_id"]
        },
        "get_interest_category": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}",
            "params": ["list_id", "interest_category_id", "fields", "exclude_fields"],
            "required": ["list_id", "interest_category_id"]
        },
        "create_interest_category": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/interest-categories",
            "params": ["list_id", "category_title", "category_type", "display_order", "request_body"],
            "required": ["list_id", "category_title", "category_type"]
        },
        "update_interest_category": {
            "method": "PATCH",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}",
            "params": ["list_id", "interest_category_id", "request_body"],
            "required": ["list_id", "interest_category_id", "request_body"]
        },
        "delete_interest_category": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}",
            "params": ["list_id", "interest_category_id"],
            "required": ["list_id", "interest_category_id"]
        },
        
        # Interest Operations
        "get_interests": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}/interests",
            "params": ["list_id", "interest_category_id", "fields", "exclude_fields", "count", "offset"],
            "required": ["list_id", "interest_category_id"]
        },
        "get_interest": {
            "method": "GET",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}/interests/{interest_id}",
            "params": ["list_id", "interest_category_id", "interest_id", "fields", "exclude_fields"],
            "required": ["list_id", "interest_category_id", "interest_id"]
        },
        "create_interest": {
            "method": "POST",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}/interests",
            "params": ["list_id", "interest_category_id", "interest_name", "display_order", "request_body"],
            "required": ["list_id", "interest_category_id", "interest_name"]
        },
        "update_interest": {
            "method": "PATCH",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}/interests/{interest_id}",
            "params": ["list_id", "interest_category_id", "interest_id", "request_body"],
            "required": ["list_id", "interest_category_id", "interest_id", "request_body"]
        },
        "delete_interest": {
            "method": "DELETE",
            "endpoint": "/lists/{list_id}/interest-categories/{interest_category_id}/interests/{interest_id}",
            "params": ["list_id", "interest_category_id", "interest_id"],
            "required": ["list_id", "interest_category_id", "interest_id"]
        },
        
        # Campaigns Operations
        "get_campaigns": {
            "method": "GET",
            "endpoint": "/campaigns",
            "params": ["fields", "exclude_fields", "count", "offset", "type", "status", "before_send_time", "since_send_time", "before_create_time", "since_create_time", "list_id", "folder_id", "member_id", "sort_field", "sort_dir"],
            "required": []
        },
        "get_campaign": {
            "method": "GET",
            "endpoint": "/campaigns/{campaign_id}",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "create_campaign": {
            "method": "POST",
            "endpoint": "/campaigns",
            "params": ["campaign_type", "recipients", "settings", "variate_settings", "tracking", "rss_opts", "social_card", "content_type", "request_body"],
            "required": ["campaign_type", "recipients", "settings"]
        },
        "update_campaign": {
            "method": "PATCH",
            "endpoint": "/campaigns/{campaign_id}",
            "params": ["campaign_id", "request_body"],
            "required": ["campaign_id", "request_body"]
        },
        "delete_campaign": {
            "method": "DELETE",
            "endpoint": "/campaigns/{campaign_id}",
            "params": ["campaign_id"],
            "required": ["campaign_id"]
        },
        "cancel_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/cancel-send",
            "params": ["campaign_id"],
            "required": ["campaign_id"]
        },
        "send_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/send",
            "params": ["campaign_id"],
            "required": ["campaign_id"]
        },
        "schedule_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/schedule",
            "params": ["campaign_id", "schedule_time", "timewarp", "batch_delivery", "request_body"],
            "required": ["campaign_id", "schedule_time"]
        },
        "unschedule_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/unschedule",
            "params": ["campaign_id"],
            "required": ["campaign_id"]
        },
        "test_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/test",
            "params": ["campaign_id", "test_emails", "send_type", "request_body"],
            "required": ["campaign_id", "test_emails", "send_type"]
        },
        "pause_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/pause",
            "params": ["campaign_id"],
            "required": ["campaign_id"]
        },
        "resume_campaign": {
            "method": "POST",
            "endpoint": "/campaigns/{campaign_id}/actions/resume",
            "params": ["campaign_id"],
            "required": ["campaign_id"]
        },
        
        # Campaign Content Operations
        "get_campaign_content": {
            "method": "GET",
            "endpoint": "/campaigns/{campaign_id}/content",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "set_campaign_content": {
            "method": "PUT",
            "endpoint": "/campaigns/{campaign_id}/content",
            "params": ["campaign_id", "plain_text", "html", "url", "template", "archive", "request_body"],
            "required": ["campaign_id"]
        },
        
        # Automations Operations
        "get_automations": {
            "method": "GET",
            "endpoint": "/automations",
            "params": ["count", "offset", "fields", "exclude_fields", "before_create_time", "since_create_time", "before_start_time", "since_start_time", "status"],
            "required": []
        },
        "get_automation": {
            "method": "GET",
            "endpoint": "/automations/{workflow_id}",
            "params": ["workflow_id", "fields", "exclude_fields"],
            "required": ["workflow_id"]
        },
        "start_automation": {
            "method": "POST",
            "endpoint": "/automations/{workflow_id}/actions/start-all-emails",
            "params": ["workflow_id"],
            "required": ["workflow_id"]
        },
        "pause_automation": {
            "method": "POST",
            "endpoint": "/automations/{workflow_id}/actions/pause-all-emails",
            "params": ["workflow_id"],
            "required": ["workflow_id"]
        },
        "archive_automation": {
            "method": "POST",
            "endpoint": "/automations/{workflow_id}/actions/archive",
            "params": ["workflow_id"],
            "required": ["workflow_id"]
        },
        
        # Automation Emails Operations
        "get_automation_emails": {
            "method": "GET",
            "endpoint": "/automations/{workflow_id}/emails",
            "params": ["workflow_id", "fields", "exclude_fields"],
            "required": ["workflow_id"]
        },
        "get_automation_email": {
            "method": "GET",
            "endpoint": "/automations/{workflow_id}/emails/{email_id}",
            "params": ["workflow_id", "email_id", "fields", "exclude_fields"],
            "required": ["workflow_id", "email_id"]
        },
        "update_automation_email": {
            "method": "PATCH",
            "endpoint": "/automations/{workflow_id}/emails/{email_id}",
            "params": ["workflow_id", "email_id", "request_body"],
            "required": ["workflow_id", "email_id", "request_body"]
        },
        "delete_automation_email": {
            "method": "DELETE",
            "endpoint": "/automations/{workflow_id}/emails/{email_id}",
            "params": ["workflow_id", "email_id"],
            "required": ["workflow_id", "email_id"]
        },
        "start_automation_email": {
            "method": "POST",
            "endpoint": "/automations/{workflow_id}/emails/{email_id}/actions/start",
            "params": ["workflow_id", "email_id"],
            "required": ["workflow_id", "email_id"]
        },
        "pause_automation_email": {
            "method": "POST",
            "endpoint": "/automations/{workflow_id}/emails/{email_id}/actions/pause",
            "params": ["workflow_id", "email_id"],
            "required": ["workflow_id", "email_id"]
        },
        
        # Templates Operations
        "get_templates": {
            "method": "GET",
            "endpoint": "/templates",
            "params": ["fields", "exclude_fields", "count", "offset", "created_by", "since_created_at", "before_created_at", "type", "category", "folder_id", "sort_field", "sort_dir"],
            "required": []
        },
        "get_template": {
            "method": "GET",
            "endpoint": "/templates/{template_id}",
            "params": ["template_id", "fields", "exclude_fields"],
            "required": ["template_id"]
        },
        "create_template": {
            "method": "POST",
            "endpoint": "/templates",
            "params": ["template_name", "folder_id", "html", "request_body"],
            "required": ["template_name", "html"]
        },
        "update_template": {
            "method": "PATCH",
            "endpoint": "/templates/{template_id}",
            "params": ["template_id", "request_body"],
            "required": ["template_id", "request_body"]
        },
        "delete_template": {
            "method": "DELETE",
            "endpoint": "/templates/{template_id}",
            "params": ["template_id"],
            "required": ["template_id"]
        },
        "get_template_default_content": {
            "method": "GET",
            "endpoint": "/templates/{template_id}/default-content",
            "params": ["template_id", "fields", "exclude_fields"],
            "required": ["template_id"]
        },
        
        # Reports Operations
        "get_campaign_reports": {
            "method": "GET",
            "endpoint": "/reports",
            "params": ["fields", "exclude_fields", "count", "offset", "type", "before_send_time", "since_send_time"],
            "required": []
        },
        "get_campaign_report": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "get_campaign_abuse_reports": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/abuse-reports",
            "params": ["campaign_id", "fields", "exclude_fields", "count", "offset"],
            "required": ["campaign_id"]
        },
        "get_campaign_advice": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/advice",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "get_campaign_click_reports": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/click-details",
            "params": ["campaign_id", "fields", "exclude_fields", "count", "offset"],
            "required": ["campaign_id"]
        },
        "get_campaign_domain_performance": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/domain-performance",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "get_campaign_email_activity": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/email-activity",
            "params": ["campaign_id", "fields", "exclude_fields", "count", "offset", "since"],
            "required": ["campaign_id"]
        },
        "get_subscriber_email_activity": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/email-activity/{subscriber_hash}",
            "params": ["campaign_id", "subscriber_hash", "fields", "exclude_fields"],
            "required": ["campaign_id", "subscriber_hash"]
        },
        "get_campaign_locations": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/locations",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "get_campaign_sent_to": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/sent-to",
            "params": ["campaign_id", "fields", "exclude_fields", "count", "offset"],
            "required": ["campaign_id"]
        },
        "get_campaign_sub_reports": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/sub-reports",
            "params": ["campaign_id", "fields", "exclude_fields"],
            "required": ["campaign_id"]
        },
        "get_campaign_unsubscribes": {
            "method": "GET",
            "endpoint": "/reports/{campaign_id}/unsubscribed",
            "params": ["campaign_id", "fields", "exclude_fields", "count", "offset"],
            "required": ["campaign_id"]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Mailchimp node."""
        return NodeSchema(
            name="MailchimpNode",
            description="Comprehensive Mailchimp Marketing API v3 integration for email marketing and audience management",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Mailchimp operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "api_key": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Mailchimp API key for authentication",
                    required=True
                ),
                # Common ID parameters
                "list_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List ID for list operations",
                    required=False
                ),
                "subscriber_hash": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Subscriber hash (MD5 of lowercase email) for member operations",
                    required=False
                ),
                "segment_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Segment ID for segment operations",
                    required=False
                ),
                "interest_category_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Interest category ID for interest category operations",
                    required=False
                ),
                "interest_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Interest ID for interest operations",
                    required=False
                ),
                "campaign_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Campaign ID for campaign operations",
                    required=False
                ),
                "workflow_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Automation workflow ID for automation operations",
                    required=False
                ),
                "email_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email ID for automation email operations",
                    required=False
                ),
                "template_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Template ID for template operations",
                    required=False
                ),
                # List parameters
                "list_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="List name for list creation",
                    required=False
                ),
                "permission_reminder": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Permission reminder for list creation",
                    required=False
                ),
                "campaign_defaults": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Campaign defaults for list creation",
                    required=False
                ),
                "use_archive_bar": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use archive bar",
                    required=False
                ),
                "notify_on_subscribe": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email to notify on subscribe",
                    required=False
                ),
                "notify_on_unsubscribe": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email to notify on unsubscribe",
                    required=False
                ),
                "email_type_option": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to allow HTML or text emails",
                    required=False
                ),
                "double_optin": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use double opt-in",
                    required=False
                ),
                "marketing_permissions": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to enable marketing permissions",
                    required=False
                ),
                # Member parameters
                "email_address": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email address for member operations",
                    required=False
                ),
                "status": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Subscriber status (subscribed/unsubscribed/cleaned/pending)",
                    required=False
                ),
                "status_if_new": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Status if new member (subscribed/unsubscribed/cleaned/pending)",
                    required=False
                ),
                "email_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email type preference (html/text)",
                    required=False
                ),
                "merge_fields": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Merge field values",
                    required=False
                ),
                "interests": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Interest preferences",
                    required=False
                ),
                "language": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Language preference",
                    required=False
                ),
                "vip": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="VIP status",
                    required=False
                ),
                "location": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Location information",
                    required=False
                ),
                "ip_signup": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="IP address used for signup",
                    required=False
                ),
                "timestamp_signup": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Timestamp of signup",
                    required=False
                ),
                "ip_opt": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="IP address used for opt-in",
                    required=False
                ),
                "timestamp_opt": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Timestamp of opt-in",
                    required=False
                ),
                "tags": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Tags for member",
                    required=False
                ),
                "members": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of members for batch operations",
                    required=False
                ),
                "update_existing": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to update existing members",
                    required=False
                ),
                # Segment parameters
                "segment_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Segment name for segment creation",
                    required=False
                ),
                "static_segment": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Static segment member emails",
                    required=False
                ),
                "options": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Segment options",
                    required=False
                ),
                # Interest category parameters
                "category_title": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Interest category title",
                    required=False
                ),
                "category_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Interest category type (checkboxes/dropdown/radio/hidden)",
                    required=False
                ),
                "display_order": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Display order",
                    required=False
                ),
                # Interest parameters
                "interest_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Interest name",
                    required=False
                ),
                # Campaign parameters
                "campaign_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Campaign type (regular/plaintext/absplit/rss/variate)",
                    required=False
                ),
                "recipients": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Campaign recipients",
                    required=False
                ),
                "settings": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Campaign settings",
                    required=False
                ),
                "variate_settings": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="A/B testing settings",
                    required=False
                ),
                "tracking": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Tracking settings",
                    required=False
                ),
                "rss_opts": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="RSS campaign options",
                    required=False
                ),
                "social_card": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Social card settings",
                    required=False
                ),
                "content_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Content type (template/drag_and_drop/html/url)",
                    required=False
                ),
                "schedule_time": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Schedule time for campaign",
                    required=False
                ),
                "timewarp": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use timewarp",
                    required=False
                ),
                "batch_delivery": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Batch delivery settings",
                    required=False
                ),
                "test_emails": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Test email addresses",
                    required=False
                ),
                "send_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Test send type (html/plaintext)",
                    required=False
                ),
                # Content parameters
                "plain_text": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Plain text content",
                    required=False
                ),
                "html": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="HTML content",
                    required=False
                ),
                "url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="URL for content import",
                    required=False
                ),
                "template": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Template settings",
                    required=False
                ),
                "archive": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Archive settings",
                    required=False
                ),
                # Template parameters
                "template_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Template name for template creation",
                    required=False
                ),
                "folder_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Folder ID",
                    required=False
                ),
                # Pagination parameters
                "fields": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Fields to include in response",
                    required=False
                ),
                "exclude_fields": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Fields to exclude from response",
                    required=False
                ),
                "count": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of items to return",
                    required=False
                ),
                "offset": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of items to skip",
                    required=False
                ),
                "sort_field": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Field to sort by",
                    required=False
                ),
                "sort_dir": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Sort direction (ASC/DESC)",
                    required=False
                ),
                # Date filters
                "before_date_created": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter by creation date (before)",
                    required=False
                ),
                "since_date_created": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter by creation date (since)",
                    required=False
                ),
                "before_send_time": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter by send time (before)",
                    required=False
                ),
                "since_send_time": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter by send time (since)",
                    required=False
                ),
                # Generic request body
                "request_body": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "lists": NodeParameterType.ARRAY,
                "list_info": NodeParameterType.OBJECT,
                "members": NodeParameterType.ARRAY,
                "member_info": NodeParameterType.OBJECT,
                "segments": NodeParameterType.ARRAY,
                "segment_info": NodeParameterType.OBJECT,
                "interest_categories": NodeParameterType.ARRAY,
                "interest_category_info": NodeParameterType.OBJECT,
                "interests": NodeParameterType.ARRAY,
                "interest_info": NodeParameterType.OBJECT,
                "campaigns": NodeParameterType.ARRAY,
                "campaign_info": NodeParameterType.OBJECT,
                "campaign_content": NodeParameterType.OBJECT,
                "automations": NodeParameterType.ARRAY,
                "automation_info": NodeParameterType.OBJECT,
                "automation_emails": NodeParameterType.ARRAY,
                "automation_email_info": NodeParameterType.OBJECT,
                "templates": NodeParameterType.ARRAY,
                "template_info": NodeParameterType.OBJECT,
                "template_content": NodeParameterType.OBJECT,
                "reports": NodeParameterType.ARRAY,
                "report_info": NodeParameterType.OBJECT,
                "ping_response": NodeParameterType.OBJECT,
                "tags": NodeParameterType.ARRAY,
                "batch_result": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Mailchimp-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("api_key"):
            raise NodeValidationError("Mailchimp API key is required")
        
        operation = params["operation"]
        if operation not in self.OPERATIONS:
            raise NodeValidationError(f"Unknown operation: {operation}")
        
        # Check required parameters for operation
        operation_config = self.OPERATIONS[operation]
        for required_param in operation_config.get("required", []):
            if not params.get(required_param):
                raise NodeValidationError(f"Parameter '{required_param}' is required for operation '{operation}'")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Mailchimp operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Extract data center from API key
            api_key = params["api_key"]
            if '-' not in api_key:
                raise NodeValidationError("Invalid Mailchimp API key format - missing data center")
            
            dc = api_key.split('-')[-1]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare configuration with authentication and data center
            config = self.CONFIG.copy()
            config["base_url"] = config["base_url"].format(dc=dc)
            config["authentication"]["password"] = api_key
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": None  # Using basic auth instead
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            path_params = {
                "list_id": params.get("list_id"),
                "subscriber_hash": params.get("subscriber_hash"),
                "segment_id": params.get("segment_id"),
                "interest_category_id": params.get("interest_category_id"),
                "interest_id": params.get("interest_id"),
                "campaign_id": params.get("campaign_id"),
                "workflow_id": params.get("workflow_id"),
                "email_id": params.get("email_id"),
                "template_id": params.get("template_id")
            }
            
            for param_name, param_value in path_params.items():
                if f"{{{param_name}}}" in endpoint and param_value:
                    endpoint = endpoint.replace(f"{{{param_name}}}", param_value)
            
            universal_params["endpoint"] = endpoint
            
            # Handle query parameters and body data
            if operation_config["method"] == "GET":
                query_params = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        if param not in ["list_id", "subscriber_hash", "segment_id", "interest_category_id", 
                                        "interest_id", "campaign_id", "workflow_id", "email_id", "template_id"]:
                            query_params[param] = params[param]
                
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PUT/PATCH/DELETE operations - prepare body data
                body_data = {}
                
                if params.get("request_body"):
                    body_data = params["request_body"]
                else:
                    # Build body based on operation
                    if operation == "create_list":
                        body_data = {
                            "name": params.get("list_name"),
                            "contact": params.get("campaign_defaults"),
                            "permission_reminder": params.get("permission_reminder"),
                            "use_archive_bar": params.get("use_archive_bar"),
                            "campaign_defaults": params.get("campaign_defaults"),
                            "notify_on_subscribe": params.get("notify_on_subscribe"),
                            "notify_on_unsubscribe": params.get("notify_on_unsubscribe"),
                            "email_type_option": params.get("email_type_option"),
                            "double_optin": params.get("double_optin"),
                            "marketing_permissions": params.get("marketing_permissions")
                        }
                    elif operation == "add_list_member" or operation == "add_or_update_list_member":
                        body_data = {
                            "email_address": params.get("email_address"),
                            "status": params.get("status") if operation == "add_list_member" else None,
                            "status_if_new": params.get("status_if_new") if operation == "add_or_update_list_member" else None,
                            "email_type": params.get("email_type"),
                            "merge_fields": params.get("merge_fields", {}),
                            "interests": params.get("interests", {}),
                            "language": params.get("language"),
                            "vip": params.get("vip"),
                            "location": params.get("location"),
                            "marketing_permissions": params.get("marketing_permissions"),
                            "ip_signup": params.get("ip_signup"),
                            "timestamp_signup": params.get("timestamp_signup"),
                            "ip_opt": params.get("ip_opt"),
                            "timestamp_opt": params.get("timestamp_opt"),
                            "tags": params.get("tags", [])
                        }
                    elif operation == "batch_sub_or_unsub":
                        body_data = {
                            "members": params.get("members", []),
                            "update_existing": params.get("update_existing", True)
                        }
                    elif operation in ["add_list_member_tags", "remove_list_member_tags"]:
                        body_data = {
                            "tags": [{"name": tag, "status": "active" if operation == "add_list_member_tags" else "inactive"} 
                                    for tag in params.get("tags", [])]
                        }
                    elif operation == "create_list_segment":
                        body_data = {
                            "name": params.get("segment_name"),
                            "static_segment": params.get("static_segment", []),
                            "options": params.get("options", {})
                        }
                    elif operation == "add_segment_member":
                        body_data = {"email_address": params.get("email_address")}
                    elif operation == "create_interest_category":
                        body_data = {
                            "title": params.get("category_title"),
                            "type": params.get("category_type"),
                            "display_order": params.get("display_order")
                        }
                    elif operation == "create_interest":
                        body_data = {
                            "name": params.get("interest_name"),
                            "display_order": params.get("display_order")
                        }
                    elif operation == "create_campaign":
                        body_data = {
                            "type": params.get("campaign_type"),
                            "recipients": params.get("recipients"),
                            "settings": params.get("settings"),
                            "variate_settings": params.get("variate_settings"),
                            "tracking": params.get("tracking"),
                            "rss_opts": params.get("rss_opts"),
                            "social_card": params.get("social_card"),
                            "content_type": params.get("content_type")
                        }
                    elif operation == "schedule_campaign":
                        body_data = {
                            "schedule_time": params.get("schedule_time"),
                            "timewarp": params.get("timewarp"),
                            "batch_delivery": params.get("batch_delivery")
                        }
                    elif operation == "test_campaign":
                        body_data = {
                            "test_emails": params.get("test_emails", []),
                            "send_type": params.get("send_type")
                        }
                    elif operation == "set_campaign_content":
                        body_data = {
                            "plain_text": params.get("plain_text"),
                            "html": params.get("html"),
                            "url": params.get("url"),
                            "template": params.get("template"),
                            "archive": params.get("archive")
                        }
                    elif operation == "create_template":
                        body_data = {
                            "name": params.get("template_name"),
                            "folder_id": params.get("folder_id"),
                            "html": params.get("html")
                        }
                
                # Clean up None values
                body_data = {k: v for k, v in body_data.items() if v is not None}
                
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation == "ping":
                    return {
                        "status": "success",
                        "ping_response": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_lists") or operation == "get_lists":
                    return {
                        "status": "success",
                        "lists": response_data.get("lists", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_list") or operation.startswith("create_list") or operation.startswith("update_list"):
                    return {
                        "status": "success",
                        "list_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_list_members") or operation == "get_list_members":
                    return {
                        "status": "success",
                        "members": response_data.get("members", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_list_member") or operation.startswith("add_list_member") or operation.startswith("update_list_member") or operation.startswith("add_or_update_list_member"):
                    return {
                        "status": "success",
                        "member_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "batch_sub_or_unsub":
                    return {
                        "status": "success",
                        "batch_result": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_list_member_tags") or operation == "get_list_member_tags":
                    return {
                        "status": "success",
                        "tags": response_data.get("tags", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_list_segments") or operation == "get_list_segments":
                    return {
                        "status": "success",
                        "segments": response_data.get("segments", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_list_segment") or operation.startswith("create_list_segment") or operation.startswith("update_list_segment"):
                    return {
                        "status": "success",
                        "segment_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_segment_members") or operation == "get_segment_members":
                    return {
                        "status": "success",
                        "members": response_data.get("members", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_interest_categories") or operation == "get_interest_categories":
                    return {
                        "status": "success",
                        "interest_categories": response_data.get("categories", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_interest_category") or operation.startswith("create_interest_category") or operation.startswith("update_interest_category"):
                    return {
                        "status": "success",
                        "interest_category_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_interests") or operation == "get_interests":
                    return {
                        "status": "success",
                        "interests": response_data.get("interests", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_interest") or operation.startswith("create_interest") or operation.startswith("update_interest"):
                    return {
                        "status": "success",
                        "interest_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_campaigns") or operation == "get_campaigns":
                    return {
                        "status": "success",
                        "campaigns": response_data.get("campaigns", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_campaign") or operation.startswith("create_campaign") or operation.startswith("update_campaign"):
                    return {
                        "status": "success",
                        "campaign_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_campaign_content") or operation.startswith("set_campaign_content"):
                    return {
                        "status": "success",
                        "campaign_content": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_automations") or operation == "get_automations":
                    return {
                        "status": "success",
                        "automations": response_data.get("automations", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_automation"):
                    return {
                        "status": "success",
                        "automation_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_automation_emails") or operation == "get_automation_emails":
                    return {
                        "status": "success",
                        "automation_emails": response_data.get("emails", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_automation_email") or operation.startswith("update_automation_email"):
                    return {
                        "status": "success",
                        "automation_email_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_templates") or operation == "get_templates":
                    return {
                        "status": "success",
                        "templates": response_data.get("templates", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_template") or operation.startswith("create_template") or operation.startswith("update_template"):
                    return {
                        "status": "success",
                        "template_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_template_default_content"):
                    return {
                        "status": "success",
                        "template_content": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_campaign_reports") or operation == "get_campaign_reports":
                    return {
                        "status": "success",
                        "reports": response_data.get("reports", []),
                        "response_data": response_data
                    }
                elif operation.startswith("get_campaign_report") or operation.startswith("get_campaign_"):
                    return {
                        "status": "success",
                        "report_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("delete_") or operation.startswith("cancel_") or operation.startswith("send_") or operation.startswith("schedule_") or operation.startswith("unschedule_") or operation.startswith("test_") or operation.startswith("pause_") or operation.startswith("resume_") or operation.startswith("start_") or operation.startswith("archive_") or operation.startswith("remove_"):
                    return {
                        "status": "success",
                        "response_data": response_data
                    }
                else:
                    return {
                        "status": "success",
                        "response_data": response_data
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Mailchimp operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "MAILCHIMP_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()