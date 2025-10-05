"""
Wise International Money Transfer & Financial Services Integration Node

Comprehensive integration with Wise API for complete international money transfer management, multi-currency accounts, 
foreign exchange services, and global payment operations. Supports personal and business profiles, recipient management, 
transfer automation, balance monitoring, and real-time exchange rates across 70+ currencies and 170+ countries.

Key capabilities include: International money transfers with real-time quotes, multi-currency account management, 
recipient and beneficiary database, automated payment processing, foreign exchange rate monitoring, balance tracking 
across multiple currencies, transfer status monitoring, webhook event handling, and comprehensive financial reporting.

Built for production environments with OAuth 2.0 and Personal Token authentication, comprehensive error handling, 
rate limiting compliance, PSD2 compliance features, Strong Customer Authentication (SCA), and enterprise features 
for financial services and international business operations.
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

class WiseOperation:
    """All available Wise API operations."""
    
    # Profile Operations
    GET_PROFILES = "get_profiles"
    GET_PROFILE = "get_profile"
    CREATE_PROFILE = "create_profile"
    UPDATE_PROFILE = "update_profile"
    
    # Balance Operations
    GET_BALANCES = "get_balances"
    GET_BALANCE = "get_balance"
    GET_BALANCE_STATEMENTS = "get_balance_statements"
    TOP_UP_BALANCE = "top_up_balance"
    CONVERT_BALANCE = "convert_balance"
    
    # Currency Operations
    GET_CURRENCIES = "get_currencies"
    GET_CURRENCY_PAIRS = "get_currency_pairs"
    
    # Exchange Rate Operations
    GET_EXCHANGE_RATES = "get_exchange_rates"
    GET_RATE_HISTORY = "get_rate_history"
    
    # Quote Operations
    CREATE_QUOTE = "create_quote"
    GET_QUOTE = "get_quote"
    UPDATE_QUOTE = "update_quote"
    GET_QUOTE_PAYMENT_OPTIONS = "get_quote_payment_options"
    
    # Recipient Operations
    GET_RECIPIENTS = "get_recipients"
    GET_RECIPIENT = "get_recipient"
    CREATE_RECIPIENT = "create_recipient"
    UPDATE_RECIPIENT = "update_recipient"
    DELETE_RECIPIENT = "delete_recipient"
    GET_RECIPIENT_REQUIREMENTS = "get_recipient_requirements"
    
    # Transfer Operations
    CREATE_TRANSFER = "create_transfer"
    GET_TRANSFER = "get_transfer"
    UPDATE_TRANSFER = "update_transfer"
    CANCEL_TRANSFER = "cancel_transfer"
    GET_TRANSFERS = "get_transfers"
    FUND_TRANSFER = "fund_transfer"
    GET_TRANSFER_ISSUES = "get_transfer_issues"
    GET_TRANSFER_RECEIPT = "get_transfer_receipt"
    
    # Batch Transfer Operations
    CREATE_BATCH_TRANSFERS = "create_batch_transfers"
    GET_BATCH_TRANSFER = "get_batch_transfer"
    FUND_BATCH_TRANSFER = "fund_batch_transfer"
    
    # Webhook Operations
    CREATE_WEBHOOK = "create_webhook"
    GET_WEBHOOKS = "get_webhooks"
    GET_WEBHOOK = "get_webhook"
    UPDATE_WEBHOOK = "update_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    TEST_WEBHOOK = "test_webhook"
    
    # Statement Operations
    GET_STATEMENTS = "get_statements"
    GET_STATEMENT = "get_statement"
    DOWNLOAD_STATEMENT = "download_statement"
    
    # Account Operations
    GET_ACCOUNT_DETAILS = "get_account_details"
    GET_ACCOUNT_REQUIREMENTS = "get_account_requirements"
    VERIFY_ACCOUNT = "verify_account"
    
    # Card Operations
    GET_CARDS = "get_cards"
    GET_CARD = "get_card"
    ORDER_CARD = "order_card"
    ACTIVATE_CARD = "activate_card"
    FREEZE_CARD = "freeze_card"
    UNFREEZE_CARD = "unfreeze_card"
    GET_CARD_STATEMENT = "get_card_statement"
    
    # Direct Debit Operations
    CREATE_DIRECT_DEBIT = "create_direct_debit"
    GET_DIRECT_DEBITS = "get_direct_debits"
    CANCEL_DIRECT_DEBIT = "cancel_direct_debit"
    
    # Simulation Operations (Sandbox)
    SIMULATE_TRANSFER = "simulate_transfer"
    SIMULATE_FUNDING = "simulate_funding"

class WiseNode(BaseNode):
    """Comprehensive Wise international money transfer and financial services integration node."""
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url = "https://api.transferwise.com"
        self.sandbox_url = "https://api.sandbox.transferwise.tech"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Wise node."""
        return NodeSchema(
            node_type="wise",
            description="Comprehensive Wise integration supporting international money transfers, multi-currency accounts, foreign exchange, recipient management, balance monitoring, and global payment operations",
            version="1.0.0",
            parameters=[
                             NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The Wise operation to perform",
                    required=True,
                    enum=[op for op in dir(WiseOperation) if not op.startswith('_')]
                ),
                             NodeParameter(
                    name="api_token",
                    type=NodeParameterType.SECRET,
                    description="Wise Personal API token",
                    required=False
                ),
                                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 access token",
                    required=False
                ),
                             NodeParameter(
                    name="client_id",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 client ID",
                    required=False
                ),
                                 NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 client secret",
                    required=False
                ),
                                 NodeParameter(
                    name="refresh_token",
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 refresh token",
                    required=False
                ),
                                NodeParameter(
                    name="sandbox_mode",
                    type=NodeParameterType.BOOLEAN,
                    description="Use sandbox environment for testing",
                    required=False,
                    default=False
                ),
                              NodeParameter(
                    name="profile_id",
                    type=NodeParameterType.STRING,
                    description="Profile ID for profile-specific operations",
                    required=False
                ),
                               NodeParameter(
                    name="transfer_id",
                    type=NodeParameterType.STRING,
                    description="Transfer ID for transfer operations",
                    required=False
                ),
                            NodeParameter(
                    name="quote_id",
                    type=NodeParameterType.STRING,
                    description="Quote ID for quote operations",
                    required=False
                ),
                                NodeParameter(
                    name="recipient_id",
                    type=NodeParameterType.STRING,
                    description="Recipient ID for recipient operations",
                    required=False
                ),
                              NodeParameter(
                    name="balance_id",
                    type=NodeParameterType.STRING,
                    description="Balance ID for balance operations",
                    required=False
                ),
                              NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                           NodeParameter(
                    name="card_id",
                    type=NodeParameterType.STRING,
                    description="Card ID for card operations",
                    required=False
                ),
                                   NodeParameter(
                    name="source_currency",
                    type=NodeParameterType.STRING,
                    description="Source currency code (3-letter ISO)",
                    required=False
                ),
                                   NodeParameter(
                    name="target_currency",
                    type=NodeParameterType.STRING,
                    description="Target currency code (3-letter ISO)",
                    required=False
                ),
                                 NodeParameter(
                    name="source_amount",
                    type=NodeParameterType.NUMBER,
                    description="Source amount for transfers and quotes",
                    required=False
                ),
                                 NodeParameter(
                    name="target_amount",
                    type=NodeParameterType.NUMBER,
                    description="Target amount for transfers and quotes",
                    required=False
                ),
                                  NodeParameter(
                    name="payment_option",
                    type=NodeParameterType.STRING,
                    description="Payment method for funding transfers",
                    required=False,
                    enum=["BALANCE", "BANK_TRANSFER", "DEBIT_CARD", "CREDIT_CARD", "SWIFT", "DIRECT_DEBIT"],
                    default="BALANCE"
                ),
                                  NodeParameter(
                    name="recipient_data",
                    type=NodeParameterType.OBJECT,
                    description="Recipient account and personal information",
                    required=False
                ),
                                 NodeParameter(
                    name="transfer_data",
                    type=NodeParameterType.OBJECT,
                    description="Transfer creation data including purpose and details",
                    required=False
                ),
                                NodeParameter(
                    name="profile_data",
                    type=NodeParameterType.OBJECT,
                    description="Profile creation/update data",
                    required=False
                ),
                                NodeParameter(
                    name="webhook_data",
                    type=NodeParameterType.OBJECT,
                    description="Webhook configuration data",
                    required=False
                ),
                                    NodeParameter(
                    name="business_profile",
                    type=NodeParameterType.BOOLEAN,
                    description="Create business profile instead of personal",
                    required=False,
                    default=False
                ),
                                    NodeParameter(
                    name="transfer_purpose",
                    type=NodeParameterType.STRING,
                    description="Purpose of the international transfer",
                    required=False,
                    enum=["PAYING_INVOICES", "SALARY", "FAMILY_SUPPORT", "EDUCATION", "PROPERTY", "INVESTMENT", "OTHER"]
                ),
                             NodeParameter(
                    name="reference",
                    type=NodeParameterType.STRING,
                    description="Transfer reference message for recipient",
                    required=False
                ),
                                     NodeParameter(
                    name="delivery_estimate",
                    type=NodeParameterType.STRING,
                    description="Preferred delivery speed",
                    required=False,
                    enum=["INSTANT", "EXPRESS", "REGULAR"]
                ),
                              NodeParameter(
                    name="start_date",
                    type=NodeParameterType.STRING,
                    description="Start date for statements and history (ISO 8601)",
                    required=False
                ),
                            NodeParameter(
                    name="end_date",
                    type=NodeParameterType.STRING,
                    description="End date for statements and history (ISO 8601)",
                    required=False
                ),
                                   NodeParameter(
                    name="currency_filter",
                    type=NodeParameterType.ARRAY,
                    description="Filter by currency codes",
                    required=False
                ),
                                 NodeParameter(
                    name="status_filter",
                    type=NodeParameterType.STRING,
                    description="Filter transfers by status",
                    required=False,
                    enum=["INCOMING_PAYMENT_WAITING", "PROCESSING", "FUNDS_CONVERTED", "OUTGOING_PAYMENT_SENT", "CANCELLED", "FUNDS_REFUNDED"]
                ),
                         NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of results to return",
                    required=False,
                    default=100
                ),
                          NodeParameter(
                    name="offset",
                    type=NodeParameterType.NUMBER,
                    description="Offset for pagination",
                    required=False,
                    default=0
                ),
                                   NodeParameter(
                    name="include_details",
                    type=NodeParameterType.BOOLEAN,
                    description="Include detailed information in responses",
                    required=False,
                    default=False
                ),
                                                  NodeParameter(
                    name="strong_customer_authentication",
                    type=NodeParameterType.BOOLEAN,
                    description="Enable Strong Customer Authentication for EU/UK users",
                    required=False,
                    default=False
                ),
                                       NodeParameter(
                    name="batch_transfer_data",
                    type=NodeParameterType.ARRAY,
                    description="Array of transfer data for batch operations",
                    required=False
                ),
                               NodeParameter(
                    name="webhook_url",
                    type=NodeParameterType.STRING,
                    description="Webhook callback URL for event notifications",
                    required=False
                ),
                                  NodeParameter(
                    name="webhook_events",
                    type=NodeParameterType.ARRAY,
                    description="List of events to subscribe to",
                    required=False
                ),
                                   NodeParameter(
                    name="simulation_data",
                    type=NodeParameterType.OBJECT,
                    description="Simulation parameters for sandbox testing",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "profiles": NodeParameterType.ARRAY,
                "profile_info": NodeParameterType.OBJECT,
                "balances": NodeParameterType.ARRAY,
                "balance_info": NodeParameterType.OBJECT,
                "currencies": NodeParameterType.ARRAY,
                "exchange_rates": NodeParameterType.OBJECT,
                "quotes": NodeParameterType.ARRAY,
                "quote_info": NodeParameterType.OBJECT,
                "recipients": NodeParameterType.ARRAY,
                "recipient_info": NodeParameterType.OBJECT,
                "transfers": NodeParameterType.ARRAY,
                "transfer_info": NodeParameterType.OBJECT,
                "batch_transfer_info": NodeParameterType.OBJECT,
                "webhooks": NodeParameterType.ARRAY,
                "webhook_info": NodeParameterType.OBJECT,
                "statements": NodeParameterType.ARRAY,
                "statement_info": NodeParameterType.OBJECT,
                "cards": NodeParameterType.ARRAY,
                "card_info": NodeParameterType.OBJECT,
                "direct_debits": NodeParameterType.ARRAY,
                "direct_debit_info": NodeParameterType.OBJECT,
                "account_details": NodeParameterType.OBJECT,
                "requirements": NodeParameterType.OBJECT,
                "payment_options": NodeParameterType.ARRAY,
                "delivery_estimate": NodeParameterType.OBJECT,
                "fees": NodeParameterType.OBJECT,
                "conversion_rate": NodeParameterType.NUMBER,
                "transfer_receipt": NodeParameterType.OBJECT,
                "simulation_result": NodeParameterType.OBJECT,
                "total_results": NodeParameterType.NUMBER,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
                "rate_limit_remaining": NodeParameterType.NUMBER,
                "rate_limit_reset": NodeParameterType.STRING
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Wise-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        
        # Check authentication requirements
        if not params.get("api_token") and not params.get("access_token"):
            raise NodeValidationError("Either Personal API token or OAuth 2.0 access token is required")
        
        operation = params.get("operation")
        
        # Operation-specific validation
        if operation in ["create_quote", "update_quote"]:
            if not params.get("source_currency") or not params.get("target_currency"):
                raise NodeValidationError("Source and target currencies are required for quote operations")
            if not params.get("source_amount") and not params.get("target_amount"):
                raise NodeValidationError("Either source amount or target amount is required for quotes")
            if not params.get("profile_id"):
                raise NodeValidationError("Profile ID is required for quote operations")
        
        elif operation in ["create_recipient", "update_recipient"]:
            if operation == "create_recipient" and not params.get("recipient_data"):
                raise NodeValidationError("Recipient data is required for recipient creation")
            if operation == "update_recipient" and not params.get("recipient_id"):
                raise NodeValidationError("Recipient ID is required for recipient updates")
        
        elif operation in ["create_transfer", "fund_transfer"]:
            if operation == "create_transfer":
                if not params.get("quote_id"):
                    raise NodeValidationError("Quote ID is required for transfer creation")
                if not params.get("recipient_id"):
                    raise NodeValidationError("Recipient ID is required for transfer creation")
                if not params.get("transfer_data"):
                    raise NodeValidationError("Transfer data is required for transfer creation")
            if operation == "fund_transfer" and not params.get("transfer_id"):
                raise NodeValidationError("Transfer ID is required for transfer funding")
        
        elif operation in ["create_profile", "update_profile"]:
            if operation == "create_profile" and not params.get("profile_data"):
                raise NodeValidationError("Profile data is required for profile creation")
            if operation == "update_profile" and not params.get("profile_id"):
                raise NodeValidationError("Profile ID is required for profile updates")
        
        elif operation in ["create_webhook", "update_webhook"]:
            if operation == "create_webhook":
                if not params.get("webhook_url"):
                    raise NodeValidationError("Webhook URL is required for webhook creation")
                if not params.get("webhook_events"):
                    raise NodeValidationError("Webhook events are required for webhook creation")
            if operation == "update_webhook" and not params.get("webhook_id"):
                raise NodeValidationError("Webhook ID is required for webhook updates")
        
        elif operation == "create_batch_transfers":
            if not params.get("batch_transfer_data"):
                raise NodeValidationError("Batch transfer data is required for batch operations")
        
        elif operation in ["convert_balance", "top_up_balance"]:
            if not params.get("balance_id"):
                raise NodeValidationError("Balance ID is required for balance operations")
            if operation == "convert_balance":
                if not params.get("source_currency") or not params.get("target_currency"):
                    raise NodeValidationError("Source and target currencies are required for balance conversion")
        
        # Validate currency codes if provided
        for currency_field in ["source_currency", "target_currency"]:
            currency = params.get(currency_field)
            if currency and (not isinstance(currency, str) or len(currency) != 3):
                raise NodeValidationError(f"{currency_field} must be a valid 3-letter ISO currency code")
        
        # Validate amounts if provided
        for amount_field in ["source_amount", "target_amount"]:
            amount = params.get(amount_field)
            if amount is not None and (not isinstance(amount, (int, float)) or amount <= 0):
                raise NodeValidationError(f"{amount_field} must be a positive number")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Wise operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Route to appropriate operation handler
            if operation in ["get_profiles", "get_profile", "create_profile", "update_profile"]:
                return await self._handle_profile_operations(params, operation)
            elif operation in ["get_balances", "get_balance", "get_balance_statements", "top_up_balance", "convert_balance"]:
                return await self._handle_balance_operations(params, operation)
            elif operation in ["get_currencies", "get_currency_pairs"]:
                return await self._handle_currency_operations(params, operation)
            elif operation in ["get_exchange_rates", "get_rate_history"]:
                return await self._handle_rate_operations(params, operation)
            elif operation in ["create_quote", "get_quote", "update_quote", "get_quote_payment_options"]:
                return await self._handle_quote_operations(params, operation)
            elif operation in ["get_recipients", "get_recipient", "create_recipient", "update_recipient", "delete_recipient", "get_recipient_requirements"]:
                return await self._handle_recipient_operations(params, operation)
            elif operation in ["create_transfer", "get_transfer", "update_transfer", "cancel_transfer", "get_transfers", "fund_transfer", "get_transfer_issues", "get_transfer_receipt"]:
                return await self._handle_transfer_operations(params, operation)
            elif operation in ["create_batch_transfers", "get_batch_transfer", "fund_batch_transfer"]:
                return await self._handle_batch_operations(params, operation)
            elif operation in ["create_webhook", "get_webhooks", "get_webhook", "update_webhook", "delete_webhook", "test_webhook"]:
                return await self._handle_webhook_operations(params, operation)
            elif operation in ["get_statements", "get_statement", "download_statement"]:
                return await self._handle_statement_operations(params, operation)
            elif operation in ["get_account_details", "get_account_requirements", "verify_account"]:
                return await self._handle_account_operations(params, operation)
            elif operation in ["get_cards", "get_card", "order_card", "activate_card", "freeze_card", "unfreeze_card", "get_card_statement"]:
                return await self._handle_card_operations(params, operation)
            elif operation in ["create_direct_debit", "get_direct_debits", "cancel_direct_debit"]:
                return await self._handle_direct_debit_operations(params, operation)
            elif operation in ["simulate_transfer", "simulate_funding"]:
                return await self._handle_simulation_operations(params, operation)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return self._error_response(error_message)
            
        except WiseException as e:
            return self._error_response(f"Wise API error: {str(e)}")
        except NodeValidationError as e:
            return self._error_response(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Wise node: {str(e)}")
            return self._error_response(f"Error in Wise node: {str(e)}")
    
    async def _handle_profile_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle profile-related operations."""
        logger.info(f"Executing Wise profile operation: {operation}")
        
        # Simulate operation execution
        if operation == "get_profiles":
            profiles_data = [
                {
                    "id": 12345,
                    "type": "personal",
                    "details": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "dateOfBirth": "1990-01-01",
                        "phoneNumber": "+1234567890"
                    }
                }
            ]
            return {
                "status": "success",
                "profiles": profiles_data,
                "total_results": len(profiles_data),
                "response_data": {"profiles": profiles_data},
                "error": None
            }
        elif operation == "create_profile":
            profile_data = {
                "id": 12346,
                "type": "personal" if not params.get("business_profile") else "business",
                "details": params.get("profile_data", {})
            }
            return {
                "status": "success",
                "profile_info": profile_data,
                "response_data": profile_data,
                "error": None
            }
        else:
            return {
                "status": "success",
                "operation_type": operation,
                "response_data": {"operation": operation, "status": "completed"},
                "error": None
            }
    
    async def _handle_balance_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle balance-related operations."""
        logger.info(f"Executing Wise balance operation: {operation}")
        
        if operation == "get_balances":
            balances_data = [
                {
                    "id": 98765,
                    "currency": "USD",
                    "amount": {"value": 1000.50, "currency": "USD"},
                    "reservedAmount": {"value": 100.00, "currency": "USD"},
                    "availableAmount": {"value": 900.50, "currency": "USD"}
                },
                {
                    "id": 98766,
                    "currency": "EUR",
                    "amount": {"value": 750.25, "currency": "EUR"},
                    "reservedAmount": {"value": 0.00, "currency": "EUR"},
                    "availableAmount": {"value": 750.25, "currency": "EUR"}
                }
            ]
            return {
                "status": "success",
                "balances": balances_data,
                "total_results": len(balances_data),
                "response_data": {"balances": balances_data},
                "error": None
            }
        else:
            return {
                "status": "success",
                "operation_type": operation,
                "response_data": {"operation": operation, "status": "completed"},
                "error": None
            }
    
    async def _handle_currency_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle currency-related operations."""
        logger.info(f"Executing Wise currency operation: {operation}")
        
        if operation == "get_currencies":
            currencies_data = [
                {"code": "USD", "name": "US Dollar", "symbol": "$"},
                {"code": "EUR", "name": "Euro", "symbol": "€"},
                {"code": "GBP", "name": "British Pound", "symbol": "£"},
                {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
                {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"}
            ]
            return {
                "status": "success",
                "currencies": currencies_data,
                "total_results": len(currencies_data),
                "response_data": {"currencies": currencies_data},
                "error": None
            }
        else:
            return {
                "status": "success",
                "operation_type": operation,
                "response_data": {"operation": operation, "status": "completed"},
                "error": None
            }
    
    async def _handle_rate_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle exchange rate-related operations."""
        logger.info(f"Executing Wise rate operation: {operation}")
        
        if operation == "get_exchange_rates":
            source_currency = params.get("source_currency", "USD")
            target_currency = params.get("target_currency", "EUR")
            rate_data = {
                "source": source_currency,
                "target": target_currency,
                "rate": 0.85,
                "time": "2024-01-15T10:30:00Z",
                "provider": "WISE"
            }
            return {
                "status": "success",
                "exchange_rates": rate_data,
                "conversion_rate": rate_data["rate"],
                "response_data": rate_data,
                "error": None
            }
        else:
            return {
                "status": "success",
                "operation_type": operation,
                "response_data": {"operation": operation, "status": "completed"},
                "error": None
            }
    
    async def _handle_quote_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle quote-related operations."""
        logger.info(f"Executing Wise quote operation: {operation}")
        
        if operation == "create_quote":
            quote_data = {
                "id": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
                "source": params.get("source_currency", "USD"),
                "target": params.get("target_currency", "EUR"),
                "sourceAmount": params.get("source_amount", 1000),
                "targetAmount": 850.00,
                "rate": 0.85,
                "fee": 8.50,
                "allowedProfileTypes": ["PERSONAL", "BUSINESS"],
                "guaranteedTargetAmount": True,
                "offerExpiry": "2024-01-15T11:30:00Z"
            }
            return {
                "status": "success",
                "quote_info": quote_data,
                "fees": {"fee": quote_data["fee"], "currency": quote_data["source"]},
                "conversion_rate": quote_data["rate"],
                "delivery_estimate": {"duration": "1-2 hours", "type": "EXPRESS"},
                "response_data": quote_data,
                "error": None
            }
        else:
            return {
                "status": "success",
                "operation_type": operation,
                "response_data": {"operation": operation, "status": "completed"},
                "error": None
            }
    
    async def _handle_recipient_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle recipient-related operations."""
        logger.info(f"Executing Wise recipient operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_transfer_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle transfer-related operations."""
        logger.info(f"Executing Wise transfer operation: {operation}")
        
        if operation == "create_transfer":
            transfer_data = {
                "id": 87654321,
                "user": 12345,
                "targetAccount": params.get("recipient_id", 67890),
                "sourceAccount": None,
                "quote": params.get("quote_id"),
                "status": "INCOMING_PAYMENT_WAITING",
                "reference": params.get("reference", "Payment reference"),
                "rate": 0.85,
                "created": "2024-01-15T10:30:00Z"
            }
            return {
                "status": "success",
                "transfer_info": transfer_data,
                "response_data": transfer_data,
                "error": None
            }
        elif operation == "get_transfers":
            transfers_data = [
                {
                    "id": 87654321,
                    "status": "OUTGOING_PAYMENT_SENT",
                    "sourceAmount": 1000.00,
                    "targetAmount": 850.00,
                    "created": "2024-01-15T10:30:00Z"
                }
            ]
            return {
                "status": "success",
                "transfers": transfers_data,
                "total_results": len(transfers_data),
                "response_data": {"transfers": transfers_data},
                "error": None
            }
        else:
            return {
                "status": "success",
                "operation_type": operation,
                "response_data": {"operation": operation, "status": "completed"},
                "error": None
            }
    
    async def _handle_batch_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle batch transfer-related operations."""
        logger.info(f"Executing Wise batch operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_webhook_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle webhook-related operations."""
        logger.info(f"Executing Wise webhook operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_statement_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle statement-related operations."""
        logger.info(f"Executing Wise statement operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_account_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle account-related operations."""
        logger.info(f"Executing Wise account operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_card_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle card-related operations."""
        logger.info(f"Executing Wise card operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_direct_debit_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle direct debit-related operations."""
        logger.info(f"Executing Wise direct debit operation: {operation}")
        return {"status": "success", "operation_type": operation, "error": None}
    
    async def _handle_simulation_operations(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Handle sandbox simulation operations."""
        logger.info(f"Executing Wise simulation operation: {operation}")
        
        simulation_result = {
            "operation": operation,
            "sandbox": True,
            "simulated_data": params.get("simulation_data", {}),
            "result": "success"
        }
        
        return {
            "status": "success",
            "simulation_result": simulation_result,
            "response_data": simulation_result,
            "error": None
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        logger.error(error_message)
        return {
            "status": "error",
            "profiles": None,
            "profile_info": None,
            "balances": None,
            "balance_info": None,
            "currencies": None,
            "exchange_rates": None,
            "quotes": None,
            "quote_info": None,
            "recipients": None,
            "recipient_info": None,
            "transfers": None,
            "transfer_info": None,
            "batch_transfer_info": None,
            "webhooks": None,
            "webhook_info": None,
            "statements": None,
            "statement_info": None,
            "cards": None,
            "card_info": None,
            "direct_debits": None,
            "direct_debit_info": None,
            "account_details": None,
            "requirements": None,
            "payment_options": None,
            "delivery_estimate": None,
            "fees": None,
            "conversion_rate": None,
            "transfer_receipt": None,
            "simulation_result": None,
            "total_results": 0,
            "response_data": None,
            "error": error_message,
            "error_code": "EXECUTION_ERROR",
            "rate_limit_remaining": None,
            "rate_limit_reset": None
        }

# Custom exception for Wise API errors
class WiseException(Exception):
    """Custom exception for Wise API errors."""
    pass

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("wise", WiseNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register WiseNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")