"""
Revolut Card Node - Comprehensive card management integration for Revolut Business API
Supports all major Revolut card operations including card creation, status management,
spending controls, and card security settings.
Uses Revolut Business REST API with full API coverage.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import aiohttp

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

# Configure logging
logger = logging.getLogger(__name__)

class RevolutCardOperation:
    """All available Revolut Card operations based on official API documentation."""
    
    # Card Management Operations
    GET_CARDS = "get_cards"
    GET_CARD = "get_card"
    GET_CARD_SENSITIVE_DETAILS = "get_card_sensitive_details"
    CREATE_VIRTUAL_CARD = "create_virtual_card"
    UPDATE_CARD = "update_card"
    TERMINATE_CARD = "terminate_card"
    
    # Card Control Operations
    FREEZE_CARD = "freeze_card"
    UNFREEZE_CARD = "unfreeze_card"

class RevolutCardStatus:
    """Available Revolut card statuses."""
    
    ACTIVE = "active"
    FROZEN = "frozen"
    TERMINATED = "terminated"

class RevolutSpendingLimitType:
    """Available Revolut spending limit types."""
    
    SINGLE = "single"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"

class RevolutCardNode(BaseNode):
    """
    Comprehensive Revolut Card integration node supporting all major API operations.
    Handles card creation, status management, spending controls, and card security settings.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url_prod = "https://b2b.revolut.com"
        self.base_url_sandbox = "https://sandbox-b2b.revolut.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Revolut Card node."""
        return NodeSchema(
            name="RevolutCardNode",
            description="Comprehensive Revolut Card management integration supporting card creation, status management, spending controls, and security settings",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Revolut Card operation to perform",
                    required=True,
                    enum=[
                        RevolutCardOperation.GET_CARDS,
                        RevolutCardOperation.GET_CARD,
                        RevolutCardOperation.GET_CARD_SENSITIVE_DETAILS,
                        RevolutCardOperation.CREATE_VIRTUAL_CARD,
                        RevolutCardOperation.UPDATE_CARD,
                        RevolutCardOperation.TERMINATE_CARD,
                        RevolutCardOperation.FREEZE_CARD,
                        RevolutCardOperation.UNFREEZE_CARD,
                    ]
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Revolut Business API access token",
                    required=True
                ),
                "environment": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="API environment (production only - sandbox not supported for cards)",
                    required=False,
                    default="production",
                    enum=["production"]
                ),
                
                # Card Identification Parameters
                "card_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique card identifier for specific card operations",
                    required=False
                ),
                
                # Card Creation Parameters
                "request_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique request identifier for card creation (v4 UUID recommended)",
                    required=False
                ),
                "holder_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Team member ID who will be the card holder",
                    required=False
                ),
                "card_label": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Label for the card (e.g., 'Marketing Card')",
                    required=False
                ),
                "virtual": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to create a virtual card (true for virtual, false not supported via API)",
                    required=False,
                    default=True
                ),
                
                # Account Linking Parameters
                "linked_accounts": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of account IDs to link to the card",
                    required=False
                ),
                
                # Merchant Category Parameters
                "allowed_categories": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of allowed merchant categories",
                    required=False
                ),
                
                # Spending Limit Parameters
                "single_transaction_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Single transaction spending limit amount",
                    required=False
                ),
                "single_transaction_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for single transaction limit",
                    required=False
                ),
                "daily_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Daily spending limit amount",
                    required=False
                ),
                "daily_limit_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for daily spending limit",
                    required=False
                ),
                "weekly_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Weekly spending limit amount",
                    required=False
                ),
                "weekly_limit_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for weekly spending limit",
                    required=False
                ),
                "monthly_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Monthly spending limit amount",
                    required=False
                ),
                "monthly_limit_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for monthly spending limit",
                    required=False
                ),
                "quarterly_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Quarterly spending limit amount",
                    required=False
                ),
                "quarterly_limit_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for quarterly spending limit",
                    required=False
                ),
                "yearly_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Yearly spending limit amount",
                    required=False
                ),
                "yearly_limit_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for yearly spending limit",
                    required=False
                ),
                "all_time_limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="All-time spending limit amount",
                    required=False
                ),
                "all_time_limit_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency for all-time spending limit",
                    required=False
                ),
                
                # Filtering Parameters (for listing cards)
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of cards to return",
                    required=False
                ),
                "created_before": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter cards created before this date (ISO 8601 format)",
                    required=False
                ),
                "created_after": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter cards created after this date (ISO 8601 format)",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "cards": NodeParameterType.ARRAY,
                "card_count": NodeParameterType.NUMBER,
                "card_id": NodeParameterType.STRING,
                "card_info": NodeParameterType.OBJECT,
                "card_status": NodeParameterType.STRING,
                "card_label": NodeParameterType.STRING,
                "holder_id": NodeParameterType.STRING,
                "spending_limits": NodeParameterType.OBJECT,
                "linked_accounts": NodeParameterType.ARRAY,
                "allowed_categories": NodeParameterType.ARRAY,
                "sensitive_details": NodeParameterType.OBJECT,
                "card_number": NodeParameterType.STRING,
                "cvv": NodeParameterType.STRING,
                "expiry_date": NodeParameterType.STRING,
                "created_at": NodeParameterType.STRING,
                "updated_at": NodeParameterType.STRING,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Revolut Card-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate access token
        if not params.get("access_token"):
            raise NodeValidationError("Revolut Business API access token is required")
        
        # Validate environment (cards API only works in production)
        if params.get("environment") and params.get("environment") != "production":
            raise NodeValidationError("Cards API is only available in production environment")
        
        # Validate operation-specific requirements
        card_specific_ops = [
            RevolutCardOperation.GET_CARD,
            RevolutCardOperation.GET_CARD_SENSITIVE_DETAILS,
            RevolutCardOperation.UPDATE_CARD,
            RevolutCardOperation.TERMINATE_CARD,
            RevolutCardOperation.FREEZE_CARD,
            RevolutCardOperation.UNFREEZE_CARD
        ]
        
        if operation in card_specific_ops:
            if not params.get("card_id"):
                raise NodeValidationError("card_id is required for card-specific operations")
        
        # Validate card creation requirements
        if operation == RevolutCardOperation.CREATE_VIRTUAL_CARD:
            if not params.get("request_id"):
                raise NodeValidationError("request_id is required for card creation")
            if not params.get("holder_id"):
                raise NodeValidationError("holder_id is required for card creation")
            
            # Validate spending limits have matching currencies
            limit_pairs = [
                ("single_transaction_limit", "single_transaction_currency"),
                ("daily_limit", "daily_limit_currency"),
                ("weekly_limit", "weekly_limit_currency"),
                ("monthly_limit", "monthly_limit_currency"),
                ("quarterly_limit", "quarterly_limit_currency"),
                ("yearly_limit", "yearly_limit_currency"),
                ("all_time_limit", "all_time_limit_currency")
            ]
            
            for amount_field, currency_field in limit_pairs:
                if params.get(amount_field) and not params.get(currency_field):
                    raise NodeValidationError(f"{currency_field} is required when {amount_field} is specified")
                if params.get(amount_field) and params.get(amount_field) <= 0:
                    raise NodeValidationError(f"{amount_field} must be a positive number")
        
        # Validate currency format
        currency_fields = [
            "single_transaction_currency", "daily_limit_currency", "weekly_limit_currency",
            "monthly_limit_currency", "quarterly_limit_currency", "yearly_limit_currency",
            "all_time_limit_currency"
        ]
        
        for field in currency_fields:
            if params.get(field) and not self._validate_currency_code(params[field]):
                raise NodeValidationError(f"{field} must be a valid 3-letter ISO 4217 currency code")
        
        # Validate date format for filtering
        date_fields = ["created_before", "created_after"]
        for field in date_fields:
            if params.get(field) and not self._validate_iso_date(params[field]):
                raise NodeValidationError(f"{field} must be in ISO 8601 format")
        
        return params
    
    def _validate_currency_code(self, currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    def _validate_iso_date(self, date_str: str) -> bool:
        """Validate ISO 8601 date format."""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Revolut Card operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Always use production URL (cards API not available in sandbox)
            base_url = self.base_url_prod
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['access_token']}",
                "Content-Type": "application/json",
                "User-Agent": "RevolutCardNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == RevolutCardOperation.GET_CARDS:
                return await self._get_cards(params, base_url, headers)
            elif operation == RevolutCardOperation.GET_CARD:
                return await self._get_card(params, base_url, headers)
            elif operation == RevolutCardOperation.GET_CARD_SENSITIVE_DETAILS:
                return await self._get_card_sensitive_details(params, base_url, headers)
            elif operation == RevolutCardOperation.CREATE_VIRTUAL_CARD:
                return await self._create_virtual_card(params, base_url, headers)
            elif operation == RevolutCardOperation.UPDATE_CARD:
                return await self._update_card(params, base_url, headers)
            elif operation == RevolutCardOperation.TERMINATE_CARD:
                return await self._terminate_card(params, base_url, headers)
            elif operation == RevolutCardOperation.FREEZE_CARD:
                return await self._freeze_card(params, base_url, headers)
            elif operation == RevolutCardOperation.UNFREEZE_CARD:
                return await self._unfreeze_card(params, base_url, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in RevolutCardNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _get_cards(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get all cards with optional filtering."""
        try:
            url = f"{base_url}/api/1.0/cards"
            
            # Add query parameters
            query_params = {}
            if params.get("limit"):
                query_params["limit"] = params["limit"]
            if params.get("created_before"):
                query_params["created_before"] = params["created_before"]
            if params.get("created_after"):
                query_params["created_after"] = params["created_after"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        cards = response_data if isinstance(response_data, list) else response_data.get("cards", [])
                        return {
                            "status": "success",
                            "operation_type": "get_cards",
                            "cards": cards,
                            "card_count": len(cards),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get cards"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get cards: {str(e)}")
    
    async def _get_card(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get specific card information."""
        try:
            card_id = params["card_id"]
            url = f"{base_url}/api/1.0/cards/{card_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_card",
                            "card_id": card_id,
                            "card_info": response_data,
                            "card_status": response_data.get("status"),
                            "card_label": response_data.get("label"),
                            "holder_id": response_data.get("holder_id"),
                            "spending_limits": response_data.get("spending_limits"),
                            "linked_accounts": response_data.get("accounts", []),
                            "allowed_categories": response_data.get("categories", []),
                            "created_at": response_data.get("created_at"),
                            "updated_at": response_data.get("updated_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get card"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get card: {str(e)}")
    
    async def _get_card_sensitive_details(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get sensitive card details (requires READ_SENSITIVE_CARD_DATA scope and IP whitelisting)."""
        try:
            card_id = params["card_id"]
            url = f"{base_url}/api/1.0/cards/{card_id}/sensitive-details"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_card_sensitive_details",
                            "card_id": card_id,
                            "sensitive_details": response_data,
                            "card_number": response_data.get("pan"),
                            "cvv": response_data.get("cvv"),
                            "expiry_date": response_data.get("expiry"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get card sensitive details"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get card sensitive details: {str(e)}")
    
    async def _create_virtual_card(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a virtual card."""
        try:
            url = f"{base_url}/api/1.0/cards"
            
            payload = {
                "virtual": params.get("virtual", True),
                "holder_id": params["holder_id"],
                "request_id": params["request_id"]
            }
            
            # Add optional label
            if params.get("card_label"):
                payload["label"] = params["card_label"]
            
            # Add linked accounts
            if params.get("linked_accounts"):
                payload["accounts"] = params["linked_accounts"]
            
            # Add allowed categories
            if params.get("allowed_categories"):
                payload["categories"] = params["allowed_categories"]
            
            # Build spending limits
            spending_limits = self._build_spending_limits(params)
            if spending_limits:
                payload["spending_limits"] = spending_limits
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_virtual_card",
                            "card_id": response_data.get("id"),
                            "card_info": response_data,
                            "card_status": response_data.get("status"),
                            "card_label": response_data.get("label"),
                            "holder_id": response_data.get("holder_id"),
                            "spending_limits": response_data.get("spending_limits"),
                            "linked_accounts": response_data.get("accounts", []),
                            "allowed_categories": response_data.get("categories", []),
                            "created_at": response_data.get("created_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create virtual card"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create virtual card: {str(e)}")
    
    async def _update_card(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Update card details."""
        try:
            card_id = params["card_id"]
            url = f"{base_url}/api/1.0/cards/{card_id}"
            
            payload = {}
            
            # Add optional label
            if params.get("card_label"):
                payload["label"] = params["card_label"]
            
            # Add allowed categories
            if params.get("allowed_categories"):
                payload["categories"] = params["allowed_categories"]
            
            # Build spending limits
            spending_limits = self._build_spending_limits(params)
            if spending_limits:
                payload["spending_limits"] = spending_limits
            
            # Ensure we have something to update
            if not payload:
                raise NodeValidationError("At least one field must be provided for card update")
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "update_card",
                            "card_id": card_id,
                            "card_info": response_data,
                            "card_label": response_data.get("label"),
                            "spending_limits": response_data.get("spending_limits"),
                            "allowed_categories": response_data.get("categories", []),
                            "updated_at": response_data.get("updated_at"),
                            "message": "Card updated successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update card"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update card: {str(e)}")
    
    async def _terminate_card(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Terminate card permanently."""
        try:
            card_id = params["card_id"]
            url = f"{base_url}/api/1.0/cards/{card_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "terminate_card",
                            "card_id": card_id,
                            "card_status": "terminated",
                            "message": "Card terminated successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to terminate card"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to terminate card: {str(e)}")
    
    async def _freeze_card(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Freeze card temporarily."""
        try:
            card_id = params["card_id"]
            url = f"{base_url}/api/1.0/cards/{card_id}/freeze"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "freeze_card",
                            "card_id": card_id,
                            "card_status": "frozen",
                            "message": "Card frozen successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to freeze card"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to freeze card: {str(e)}")
    
    async def _unfreeze_card(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Unfreeze card."""
        try:
            card_id = params["card_id"]
            url = f"{base_url}/api/1.0/cards/{card_id}/unfreeze"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "unfreeze_card",
                            "card_id": card_id,
                            "card_status": "active",
                            "message": "Card unfrozen successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to unfreeze card"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to unfreeze card: {str(e)}")
    
    def _build_spending_limits(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build spending limits object from parameters."""
        spending_limits = {}
        
        limit_mappings = [
            ("single_transaction_limit", "single_transaction_currency", "single"),
            ("daily_limit", "daily_limit_currency", "day"),
            ("weekly_limit", "weekly_limit_currency", "week"),
            ("monthly_limit", "monthly_limit_currency", "month"),
            ("quarterly_limit", "quarterly_limit_currency", "quarter"),
            ("yearly_limit", "yearly_limit_currency", "year"),
            ("all_time_limit", "all_time_limit_currency", "all_time")
        ]
        
        for amount_field, currency_field, limit_type in limit_mappings:
            if params.get(amount_field) and params.get(currency_field):
                spending_limits[limit_type] = {
                    "amount": params[amount_field],
                    "currency": params[currency_field]
                }
        
        return spending_limits
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "cards": None,
            "card_count": None,
            "card_id": None,
            "card_info": None,
            "card_status": None,
            "card_label": None,
            "holder_id": None,
            "spending_limits": None,
            "linked_accounts": None,
            "allowed_categories": None,
            "sensitive_details": None,
            "card_number": None,
            "cvv": None,
            "expiry_date": None,
            "created_at": None,
            "updated_at": None,
            "operation_type": None,
            "response_data": None
        }

class RevolutCardHelpers:
    """Helper functions for Revolut Card operations."""
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate a unique request ID for card creation (v4 UUID)."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def validate_currency_code(currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as ISO string for API requests."""
        return dt.isoformat()
    
    @staticmethod
    def create_spending_limit(amount: float, currency: str) -> Dict[str, Any]:
        """Create a properly formatted spending limit object."""
        return {
            "amount": amount,
            "currency": currency
        }
    
    @staticmethod
    def validate_spending_limits(limits: Dict[str, Any]) -> List[str]:
        """Validate spending limits and return list of validation errors."""
        errors = []
        
        valid_limit_types = ["single", "day", "week", "month", "quarter", "year", "all_time"]
        
        for limit_type, limit_data in limits.items():
            if limit_type not in valid_limit_types:
                errors.append(f"Invalid limit type: {limit_type}")
                continue
            
            if not isinstance(limit_data, dict):
                errors.append(f"Limit data for {limit_type} must be an object")
                continue
            
            if "amount" not in limit_data:
                errors.append(f"Amount is required for {limit_type} limit")
            elif not isinstance(limit_data["amount"], (int, float)) or limit_data["amount"] <= 0:
                errors.append(f"Amount for {limit_type} limit must be a positive number")
            
            if "currency" not in limit_data:
                errors.append(f"Currency is required for {limit_type} limit")
            elif not RevolutCardHelpers.validate_currency_code(limit_data["currency"]):
                errors.append(f"Invalid currency code for {limit_type} limit")
        
        return errors
    
    @staticmethod
    def parse_card_status(status: str) -> Dict[str, Any]:
        """Parse and categorize card status."""
        status_info = {
            "active": {"category": "active", "can_spend": True, "description": "Card is active and can be used for spending"},
            "frozen": {"category": "frozen", "can_spend": False, "description": "Card is temporarily frozen"},
            "terminated": {"category": "terminated", "can_spend": False, "description": "Card is permanently terminated"}
        }
        
        return status_info.get(status.lower(), {
            "category": "unknown", 
            "can_spend": False, 
            "description": f"Unknown status: {status}"
        })
    
    @staticmethod
    def calculate_limit_usage(current_spending: float, limit_amount: float) -> Dict[str, Any]:
        """Calculate spending limit usage percentage."""
        if limit_amount <= 0:
            return {"usage_percentage": 0, "remaining": 0, "exceeded": False}
        
        usage_percentage = (current_spending / limit_amount) * 100
        remaining = max(0, limit_amount - current_spending)
        exceeded = current_spending > limit_amount
        
        return {
            "usage_percentage": round(usage_percentage, 2),
            "remaining": round(remaining, 2),
            "exceeded": exceeded,
            "current_spending": current_spending,
            "limit_amount": limit_amount
        }
    
    @staticmethod
    def get_merchant_categories() -> List[str]:
        """Get list of common merchant categories for card restrictions."""
        return [
            "services", "shopping", "furniture", "groceries", "restaurants",
            "fuel", "travel", "entertainment", "health", "education",
            "utilities", "insurance", "charity", "government", "online"
        ]
    
    @staticmethod
    def validate_card_label(label: str) -> bool:
        """Validate card label format and length."""
        if not label or not isinstance(label, str):
            return False
        
        # Check length (reasonable limit)
        if len(label) > 50:
            return False
        
        # Check for valid characters (alphanumeric, spaces, common punctuation)
        import re
        return bool(re.match(r'^[a-zA-Z0-9\s\-_\.]+$', label))
    
    @staticmethod
    def format_card_summary(card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format card data into a summary object."""
        return {
            "id": card_data.get("id"),
            "label": card_data.get("label"),
            "status": card_data.get("status"),
            "holder_id": card_data.get("holder_id"),
            "type": "virtual" if card_data.get("virtual") else "physical",
            "has_spending_limits": bool(card_data.get("spending_limits")),
            "linked_accounts_count": len(card_data.get("accounts", [])),
            "restricted_categories": len(card_data.get("categories", [])) > 0,
            "created_at": card_data.get("created_at"),
            "updated_at": card_data.get("updated_at")
        }
    
    @staticmethod
    def compare_spending_limits(old_limits: Dict[str, Any], new_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Compare old and new spending limits to show changes."""
        changes = {
            "added": {},
            "modified": {},
            "removed": {}
        }
        
        # Check for added and modified limits
        for limit_type, limit_data in new_limits.items():
            if limit_type not in old_limits:
                changes["added"][limit_type] = limit_data
            elif old_limits[limit_type] != limit_data:
                changes["modified"][limit_type] = {
                    "old": old_limits[limit_type],
                    "new": limit_data
                }
        
        # Check for removed limits
        for limit_type in old_limits:
            if limit_type not in new_limits:
                changes["removed"][limit_type] = old_limits[limit_type]
        
        return changes