"""
Revolut Payment Node - Comprehensive payment processing integration for Revolut Business API
Supports all major Revolut payment operations including payment creation, transfers,
payment status tracking, and counterparty management.
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

class RevolutPaymentOperation:
    """All available Revolut Payment operations based on official API documentation."""
    
    # Payment Operations
    CREATE_PAYMENT = "create_payment"
    CREATE_PAYMENT_DRAFT = "create_payment_draft"
    GET_PAYMENT_DRAFT = "get_payment_draft"
    DELETE_PAYMENT_DRAFT = "delete_payment_draft"
    
    # Transfer Operations
    CREATE_INTERNAL_TRANSFER = "create_internal_transfer"
    
    # Counterparty Operations
    CREATE_COUNTERPARTY = "create_counterparty"
    GET_COUNTERPARTY = "get_counterparty"
    GET_COUNTERPARTIES = "get_counterparties"
    DELETE_COUNTERPARTY = "delete_counterparty"
    
    # Currency Exchange Operations
    CREATE_EXCHANGE = "create_exchange"
    
    # Transaction Management
    GET_TRANSACTION = "get_transaction"
    CANCEL_TRANSACTION = "cancel_transaction"

class RevolutPaymentState:
    """Available Revolut payment states."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERTED = "reverted"

class RevolutChargeBearer:
    """Available Revolut charge bearer options."""
    
    DEBTOR = "debtor"
    SHARED = "shared"

class RevolutPaymentNode(BaseNode):
    """
    Comprehensive Revolut Payment integration node supporting all major API operations.
    Handles payment creation, transfers, counterparty management, and payment tracking.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url_prod = "https://b2b.revolut.com"
        self.base_url_sandbox = "https://sandbox-b2b.revolut.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Revolut Payment node."""
        return NodeSchema(
            name="RevolutPaymentNode",
            description="Comprehensive Revolut Payment processing integration supporting payment creation, transfers, counterparty management, and payment tracking",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Revolut Payment operation to perform",
                    required=True,
                    enum=[
                        RevolutPaymentOperation.CREATE_PAYMENT,
                        RevolutPaymentOperation.CREATE_PAYMENT_DRAFT,
                        RevolutPaymentOperation.GET_PAYMENT_DRAFT,
                        RevolutPaymentOperation.DELETE_PAYMENT_DRAFT,
                        RevolutPaymentOperation.CREATE_INTERNAL_TRANSFER,
                        RevolutPaymentOperation.CREATE_COUNTERPARTY,
                        RevolutPaymentOperation.GET_COUNTERPARTY,
                        RevolutPaymentOperation.GET_COUNTERPARTIES,
                        RevolutPaymentOperation.DELETE_COUNTERPARTY,
                        RevolutPaymentOperation.CREATE_EXCHANGE,
                        RevolutPaymentOperation.GET_TRANSACTION,
                        RevolutPaymentOperation.CANCEL_TRANSACTION,
                    ]
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Revolut Business API access token",
                    required=True
                ),
                "environment": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="API environment (production or sandbox)",
                    required=False,
                    default="production",
                    enum=["production", "sandbox"]
                ),
                
                # Payment Parameters
                "request_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique request identifier for payment operations",
                    required=False
                ),
                "account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Source account ID for payments and transfers",
                    required=False
                ),
                "counterparty_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Recipient counterparty ID for payments",
                    required=False
                ),
                "recipient_account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Recipient account ID (optional for external payments)",
                    required=False
                ),
                "amount": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Payment amount",
                    required=False
                ),
                "currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="3-letter ISO currency code",
                    required=False
                ),
                "reference": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Payment reference or description",
                    required=False
                ),
                "charge_bearer": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Who bears the charges (debtor or shared)",
                    required=False,
                    enum=["debtor", "shared"]
                ),
                "schedule_for": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="ISO 8601 date for scheduled payments (up to 30 days in future)",
                    required=False
                ),
                
                # Transfer Parameters
                "source_account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Source account ID for internal transfers",
                    required=False
                ),
                "target_account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Target account ID for internal transfers",
                    required=False
                ),
                "description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Transfer description",
                    required=False
                ),
                
                # Payment Draft Parameters
                "draft_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Payment draft ID for draft operations",
                    required=False
                ),
                "draft_title": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Payment draft title",
                    required=False
                ),
                "payments": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of payment objects for draft creation",
                    required=False
                ),
                
                # Counterparty Parameters
                "counterparty_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Counterparty name",
                    required=False
                ),
                "counterparty_profile_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Counterparty profile type (personal or business)",
                    required=False,
                    enum=["personal", "business"]
                ),
                "counterparty_country": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Counterparty country code (ISO 3166-1 alpha-2)",
                    required=False
                ),
                "bank_country": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Bank country code for counterparty",
                    required=False
                ),
                "bank_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Bank currency for counterparty account",
                    required=False
                ),
                "account_number": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Bank account number",
                    required=False
                ),
                "routing_number": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Bank routing number (for US accounts)",
                    required=False
                ),
                "iban": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="IBAN for European accounts",
                    required=False
                ),
                "bic": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="BIC/SWIFT code",
                    required=False
                ),
                
                # Exchange Parameters
                "from_account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Source account ID for currency exchange",
                    required=False
                ),
                "to_account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Target account ID for currency exchange",
                    required=False
                ),
                "from_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Source currency for exchange",
                    required=False
                ),
                "to_currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Target currency for exchange",
                    required=False
                ),
                
                # Transaction Parameters
                "transaction_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Transaction ID for status or cancel operations",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "payment_id": NodeParameterType.STRING,
                "transaction_id": NodeParameterType.STRING,
                "payment_state": NodeParameterType.STRING,
                "payment_amount": NodeParameterType.NUMBER,
                "payment_currency": NodeParameterType.STRING,
                "payment_reference": NodeParameterType.STRING,
                "created_at": NodeParameterType.STRING,
                "completed_at": NodeParameterType.STRING,
                "draft_id": NodeParameterType.STRING,
                "counterparty_id": NodeParameterType.STRING,
                "counterparties": NodeParameterType.ARRAY,
                "counterparty_count": NodeParameterType.NUMBER,
                "exchange_id": NodeParameterType.STRING,
                "exchange_rate": NodeParameterType.NUMBER,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Revolut Payment-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate access token
        if not params.get("access_token"):
            raise NodeValidationError("Revolut Business API access token is required")
        
        # Validate operation-specific requirements
        payment_ops = [
            RevolutPaymentOperation.CREATE_PAYMENT
        ]
        
        if operation in payment_ops:
            if not params.get("request_id"):
                raise NodeValidationError("request_id is required for payment operations")
            if not params.get("account_id"):
                raise NodeValidationError("account_id is required for payment operations")
            if not params.get("counterparty_id"):
                raise NodeValidationError("counterparty_id is required for payment operations")
            if not params.get("amount"):
                raise NodeValidationError("amount is required for payment operations")
            if not params.get("currency"):
                raise NodeValidationError("currency is required for payment operations")
        
        # Validate transfer operations
        if operation == RevolutPaymentOperation.CREATE_INTERNAL_TRANSFER:
            required_fields = ["request_id", "source_account_id", "target_account_id", "amount", "currency", "description"]
            for field in required_fields:
                if not params.get(field):
                    raise NodeValidationError(f"{field} is required for internal transfer operations")
        
        # Validate draft operations
        if operation == RevolutPaymentOperation.CREATE_PAYMENT_DRAFT:
            if not params.get("draft_title"):
                raise NodeValidationError("draft_title is required for payment draft creation")
            if not params.get("payments"):
                raise NodeValidationError("payments array is required for payment draft creation")
        
        if operation in [RevolutPaymentOperation.GET_PAYMENT_DRAFT, RevolutPaymentOperation.DELETE_PAYMENT_DRAFT]:
            if not params.get("draft_id"):
                raise NodeValidationError("draft_id is required for payment draft operations")
        
        # Validate counterparty operations
        if operation == RevolutPaymentOperation.CREATE_COUNTERPARTY:
            if not params.get("counterparty_name"):
                raise NodeValidationError("counterparty_name is required for counterparty creation")
            if not params.get("counterparty_profile_type"):
                raise NodeValidationError("counterparty_profile_type is required for counterparty creation")
        
        if operation in [RevolutPaymentOperation.GET_COUNTERPARTY, RevolutPaymentOperation.DELETE_COUNTERPARTY]:
            if not params.get("counterparty_id"):
                raise NodeValidationError("counterparty_id is required for counterparty operations")
        
        # Validate exchange operations
        if operation == RevolutPaymentOperation.CREATE_EXCHANGE:
            required_fields = ["request_id", "from_account_id", "to_account_id", "from_currency", "to_currency", "amount"]
            for field in required_fields:
                if not params.get(field):
                    raise NodeValidationError(f"{field} is required for currency exchange operations")
        
        # Validate transaction operations
        if operation in [RevolutPaymentOperation.GET_TRANSACTION, RevolutPaymentOperation.CANCEL_TRANSACTION]:
            if not params.get("transaction_id"):
                raise NodeValidationError("transaction_id is required for transaction operations")
        
        # Validate currency format
        currency_fields = ["currency", "bank_currency", "from_currency", "to_currency"]
        for field in currency_fields:
            if params.get(field) and not self._validate_currency_code(params[field]):
                raise NodeValidationError(f"{field} must be a valid 3-letter ISO 4217 currency code")
        
        # Validate amount is positive
        if params.get("amount") and params.get("amount") <= 0:
            raise NodeValidationError("amount must be a positive number")
        
        return params
    
    def _validate_currency_code(self, currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Revolut Payment operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get base URL based on environment
            base_url = self.base_url_prod if params.get("environment", "production") == "production" else self.base_url_sandbox
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['access_token']}",
                "Content-Type": "application/json",
                "User-Agent": "RevolutPaymentNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == RevolutPaymentOperation.CREATE_PAYMENT:
                return await self._create_payment(params, base_url, headers)
            elif operation == RevolutPaymentOperation.CREATE_PAYMENT_DRAFT:
                return await self._create_payment_draft(params, base_url, headers)
            elif operation == RevolutPaymentOperation.GET_PAYMENT_DRAFT:
                return await self._get_payment_draft(params, base_url, headers)
            elif operation == RevolutPaymentOperation.DELETE_PAYMENT_DRAFT:
                return await self._delete_payment_draft(params, base_url, headers)
            elif operation == RevolutPaymentOperation.CREATE_INTERNAL_TRANSFER:
                return await self._create_internal_transfer(params, base_url, headers)
            elif operation == RevolutPaymentOperation.CREATE_COUNTERPARTY:
                return await self._create_counterparty(params, base_url, headers)
            elif operation == RevolutPaymentOperation.GET_COUNTERPARTY:
                return await self._get_counterparty(params, base_url, headers)
            elif operation == RevolutPaymentOperation.GET_COUNTERPARTIES:
                return await self._get_counterparties(params, base_url, headers)
            elif operation == RevolutPaymentOperation.DELETE_COUNTERPARTY:
                return await self._delete_counterparty(params, base_url, headers)
            elif operation == RevolutPaymentOperation.CREATE_EXCHANGE:
                return await self._create_exchange(params, base_url, headers)
            elif operation == RevolutPaymentOperation.GET_TRANSACTION:
                return await self._get_transaction(params, base_url, headers)
            elif operation == RevolutPaymentOperation.CANCEL_TRANSACTION:
                return await self._cancel_transaction(params, base_url, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in RevolutPaymentNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _create_payment(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a payment."""
        try:
            url = f"{base_url}/api/1.0/pay"
            
            payload = {
                "request_id": params["request_id"],
                "account_id": params["account_id"],
                "receiver": {
                    "counterparty_id": params["counterparty_id"]
                },
                "amount": params["amount"],
                "currency": params["currency"]
            }
            
            # Add optional recipient account ID
            if params.get("recipient_account_id"):
                payload["receiver"]["account_id"] = params["recipient_account_id"]
            
            # Add optional parameters
            if params.get("reference"):
                payload["reference"] = params["reference"]
            if params.get("charge_bearer"):
                payload["charge_bearer"] = params["charge_bearer"]
            if params.get("schedule_for"):
                payload["schedule_for"] = params["schedule_for"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_payment",
                            "payment_id": response_data.get("id"),
                            "payment_state": response_data.get("state"),
                            "payment_amount": response_data.get("amount"),
                            "payment_currency": response_data.get("currency"),
                            "payment_reference": response_data.get("reference"),
                            "created_at": response_data.get("created_at"),
                            "completed_at": response_data.get("completed_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create payment"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create payment: {str(e)}")
    
    async def _create_payment_draft(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a payment draft."""
        try:
            url = f"{base_url}/api/1.0/payment-drafts"
            
            payload = {
                "title": params["draft_title"],
                "payments": params["payments"]
            }
            
            # Add optional schedule
            if params.get("schedule_for"):
                payload["schedule_for"] = params["schedule_for"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_payment_draft",
                            "draft_id": response_data.get("id"),
                            "draft_title": response_data.get("title"),
                            "payments_count": len(response_data.get("payments", [])),
                            "created_at": response_data.get("created_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create payment draft"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create payment draft: {str(e)}")
    
    async def _get_payment_draft(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get payment draft information."""
        try:
            draft_id = params["draft_id"]
            url = f"{base_url}/api/1.0/payment-drafts/{draft_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_payment_draft",
                            "draft_id": draft_id,
                            "draft_title": response_data.get("title"),
                            "payments_count": len(response_data.get("payments", [])),
                            "created_at": response_data.get("created_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get payment draft"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get payment draft: {str(e)}")
    
    async def _delete_payment_draft(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Delete payment draft."""
        try:
            draft_id = params["draft_id"]
            url = f"{base_url}/api/1.0/payment-drafts/{draft_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "delete_payment_draft",
                            "draft_id": draft_id,
                            "message": "Payment draft deleted successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to delete payment draft"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to delete payment draft: {str(e)}")
    
    async def _create_internal_transfer(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create an internal transfer between accounts."""
        try:
            url = f"{base_url}/api/1.0/transfer"
            
            payload = {
                "request_id": params["request_id"],
                "source_account_id": params["source_account_id"],
                "target_account_id": params["target_account_id"],
                "amount": params["amount"],
                "currency": params["currency"],
                "description": params["description"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_internal_transfer",
                            "transaction_id": response_data.get("id"),
                            "transfer_state": response_data.get("state"),
                            "transfer_amount": response_data.get("amount"),
                            "transfer_currency": response_data.get("currency"),
                            "description": response_data.get("description"),
                            "created_at": response_data.get("created_at"),
                            "completed_at": response_data.get("completed_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create internal transfer"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create internal transfer: {str(e)}")
    
    async def _create_counterparty(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a counterparty."""
        try:
            url = f"{base_url}/api/1.0/counterparties"
            
            payload = {
                "name": params["counterparty_name"],
                "profile_type": params["counterparty_profile_type"]
            }
            
            # Add optional country
            if params.get("counterparty_country"):
                payload["country"] = params["counterparty_country"]
            
            # Add bank account details if provided
            bank_details = {}
            if params.get("bank_country"):
                bank_details["country"] = params["bank_country"]
            if params.get("bank_currency"):
                bank_details["currency"] = params["bank_currency"]
            if params.get("account_number"):
                bank_details["account_no"] = params["account_number"]
            if params.get("routing_number"):
                bank_details["routing_number"] = params["routing_number"]
            if params.get("iban"):
                bank_details["iban"] = params["iban"]
            if params.get("bic"):
                bank_details["bic"] = params["bic"]
            
            if bank_details:
                payload["accounts"] = [bank_details]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_counterparty",
                            "counterparty_id": response_data.get("id"),
                            "counterparty_name": response_data.get("name"),
                            "profile_type": response_data.get("profile_type"),
                            "created_at": response_data.get("created_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create counterparty"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create counterparty: {str(e)}")
    
    async def _get_counterparty(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get counterparty information."""
        try:
            counterparty_id = params["counterparty_id"]
            url = f"{base_url}/api/1.0/counterparties/{counterparty_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_counterparty",
                            "counterparty_id": counterparty_id,
                            "counterparty_name": response_data.get("name"),
                            "profile_type": response_data.get("profile_type"),
                            "country": response_data.get("country"),
                            "accounts": response_data.get("accounts", []),
                            "created_at": response_data.get("created_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get counterparty"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get counterparty: {str(e)}")
    
    async def _get_counterparties(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get all counterparties."""
        try:
            url = f"{base_url}/api/1.0/counterparties"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        counterparties = response_data if isinstance(response_data, list) else response_data.get("counterparties", [])
                        return {
                            "status": "success",
                            "operation_type": "get_counterparties",
                            "counterparties": counterparties,
                            "counterparty_count": len(counterparties),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get counterparties"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get counterparties: {str(e)}")
    
    async def _delete_counterparty(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Delete counterparty."""
        try:
            counterparty_id = params["counterparty_id"]
            url = f"{base_url}/api/1.0/counterparties/{counterparty_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "delete_counterparty",
                            "counterparty_id": counterparty_id,
                            "message": "Counterparty deleted successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to delete counterparty"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to delete counterparty: {str(e)}")
    
    async def _create_exchange(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a currency exchange."""
        try:
            url = f"{base_url}/api/1.0/exchange"
            
            payload = {
                "request_id": params["request_id"],
                "from": {
                    "account_id": params["from_account_id"],
                    "currency": params["from_currency"],
                    "amount": params["amount"]
                },
                "to": {
                    "account_id": params["to_account_id"],
                    "currency": params["to_currency"]
                }
            }
            
            # Add optional reference
            if params.get("reference"):
                payload["reference"] = params["reference"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_exchange",
                            "exchange_id": response_data.get("id"),
                            "exchange_state": response_data.get("state"),
                            "exchange_rate": response_data.get("rate"),
                            "from_amount": response_data.get("from", {}).get("amount"),
                            "from_currency": response_data.get("from", {}).get("currency"),
                            "to_amount": response_data.get("to", {}).get("amount"),
                            "to_currency": response_data.get("to", {}).get("currency"),
                            "created_at": response_data.get("created_at"),
                            "completed_at": response_data.get("completed_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create exchange"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create exchange: {str(e)}")
    
    async def _get_transaction(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get transaction information."""
        try:
            transaction_id = params["transaction_id"]
            url = f"{base_url}/api/1.0/transactions/{transaction_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_transaction",
                            "transaction_id": transaction_id,
                            "transaction_state": response_data.get("state"),
                            "transaction_type": response_data.get("type"),
                            "amount": response_data.get("amount"),
                            "currency": response_data.get("currency"),
                            "reference": response_data.get("reference"),
                            "created_at": response_data.get("created_at"),
                            "completed_at": response_data.get("completed_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get transaction"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get transaction: {str(e)}")
    
    async def _cancel_transaction(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Cancel a scheduled transaction."""
        try:
            transaction_id = params["transaction_id"]
            url = f"{base_url}/api/1.0/transactions/{transaction_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "operation_type": "cancel_transaction",
                            "transaction_id": transaction_id,
                            "transaction_state": "cancelled",
                            "message": "Transaction cancelled successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to cancel transaction"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to cancel transaction: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "payment_id": None,
            "transaction_id": None,
            "payment_state": None,
            "payment_amount": None,
            "payment_currency": None,
            "payment_reference": None,
            "created_at": None,
            "completed_at": None,
            "draft_id": None,
            "counterparty_id": None,
            "counterparties": None,
            "counterparty_count": None,
            "exchange_id": None,
            "exchange_rate": None,
            "operation_type": None,
            "response_data": None
        }

class RevolutPaymentHelpers:
    """Helper functions for Revolut Payment operations."""
    
    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as ISO string for API requests."""
        return dt.isoformat()
    
    @staticmethod
    def validate_currency_code(currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    @staticmethod
    def validate_iban(iban: str) -> bool:
        """Basic IBAN validation."""
        import re
        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()
        # Basic pattern check (2 letters + 2 digits + up to 30 alphanumeric)
        return bool(re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$', iban))
    
    @staticmethod
    def validate_bic(bic: str) -> bool:
        """Basic BIC/SWIFT code validation."""
        import re
        # BIC format: 4 letters (bank) + 2 letters (country) + 2 alphanumeric (location) + optional 3 alphanumeric (branch)
        return bool(re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic.upper()))
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate a unique request ID for payment operations."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def format_amount(amount: Union[int, float]) -> float:
        """Format amount to proper decimal format."""
        return round(float(amount), 2)
    
    @staticmethod
    def validate_scheduled_date(date_str: str) -> bool:
        """Validate that scheduled date is in future and within 30 days."""
        try:
            from datetime import datetime, timezone, timedelta
            scheduled_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            max_future = now + timedelta(days=30)
            
            return now < scheduled_date <= max_future
        except ValueError:
            return False
    
    @staticmethod
    def create_payment_object(account_id: str, counterparty_id: str, amount: float, 
                            currency: str, reference: str = None, 
                            recipient_account_id: str = None) -> Dict[str, Any]:
        """Create a properly formatted payment object for drafts."""
        payment = {
            "account_id": account_id,
            "receiver": {
                "counterparty_id": counterparty_id
            },
            "amount": amount,
            "currency": currency
        }
        
        if recipient_account_id:
            payment["receiver"]["account_id"] = recipient_account_id
        if reference:
            payment["reference"] = reference
            
        return payment
    
    @staticmethod
    def parse_payment_state(state: str) -> Dict[str, Any]:
        """Parse and categorize payment state."""
        state_categories = {
            "pending": ["pending"],
            "processing": ["processing"],
            "completed": ["completed"],
            "failed": ["failed"],
            "cancelled": ["cancelled"],
            "reverted": ["reverted"]
        }
        
        for category, states in state_categories.items():
            if state.lower() in states:
                return {
                    "category": category, 
                    "state": state, 
                    "is_final": category in ["completed", "failed", "cancelled", "reverted"]
                }
        
        return {"category": "unknown", "state": state, "is_final": False}
    
    @staticmethod
    def calculate_fees(amount: float, currency: str, charge_bearer: str = "debtor") -> Dict[str, Any]:
        """Estimate fees for payment (basic calculation)."""
        # This is a simplified fee calculation - actual fees depend on many factors
        fee_rates = {
            "EUR": 0.002,  # 0.2%
            "USD": 0.003,  # 0.3%
            "GBP": 0.002,  # 0.2%
        }
        
        base_rate = fee_rates.get(currency, 0.005)  # Default 0.5%
        estimated_fee = amount * base_rate
        
        return {
            "estimated_fee": round(estimated_fee, 2),
            "currency": currency,
            "charge_bearer": charge_bearer,
            "net_amount": round(amount - (estimated_fee if charge_bearer == "debtor" else 0), 2)
        }
    
    @staticmethod
    def validate_counterparty_data(profile_type: str, country: str = None, 
                                 bank_country: str = None) -> List[str]:
        """Validate counterparty data and return list of validation errors."""
        errors = []
        
        if profile_type not in ["personal", "business"]:
            errors.append("profile_type must be 'personal' or 'business'")
        
        if country and len(country) != 2:
            errors.append("country must be a 2-letter ISO 3166-1 alpha-2 code")
        
        if bank_country and len(bank_country) != 2:
            errors.append("bank_country must be a 2-letter ISO 3166-1 alpha-2 code")
        
        return errors
    
    @staticmethod
    def format_bank_account(account_number: str = None, iban: str = None, 
                          routing_number: str = None, bic: str = None,
                          country: str = None, currency: str = None) -> Dict[str, Any]:
        """Format bank account details for counterparty creation."""
        account = {}
        
        if country:
            account["country"] = country
        if currency:
            account["currency"] = currency
        if account_number:
            account["account_no"] = account_number
        if iban:
            account["iban"] = iban
        if routing_number:
            account["routing_number"] = routing_number
        if bic:
            account["bic"] = bic
            
        return account