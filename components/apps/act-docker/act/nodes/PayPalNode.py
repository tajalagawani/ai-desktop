#!/usr/bin/env python3
"""
PayPal Node - Unified PayPal API Integration
Comprehensive integration with PayPal REST API using UniversalRequestNode.
Supports orders, payments, subscriptions, invoicing, and webhooks.
"""

import logging
import base64
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError

try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class PayPalNode(BaseNode):
    """
    PayPal Node - Unified PayPal API Integration
    
    Comprehensive integration with PayPal REST API covering:
    - Orders (create, capture, authorize)
    - Payments (captures, refunds, authorizations)
    - Subscriptions and billing plans
    - Invoicing
    - Webhooks and notifications
    - Disputes and payouts
    - Catalog products
    """
    
    CONFIG = {
        "base_url": "https://api-m.paypal.com",
        "sandbox_url": "https://api-m.sandbox.paypal.com",
        "authentication": {
            "type": "custom"  # PayPal uses OAuth2 client credentials
        },
        "default_headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "retry_config": {
            "max_attempts": 3,
            "backoff": "exponential",
            "retriable_codes": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 10,
            "burst_size": 20
        },
        "timeouts": {
            "connect": 10.0,
            "read": 30.0,
            "total": 60.0
        }
    }
    
    OPERATIONS = {
        # Authentication
        "get_access_token": {
            "method": "POST",
            "endpoint": "/v1/oauth2/token",
            "required_params": ["client_id", "client_secret"]
        },
        
        # Orders API v2
        "create_order": {
            "method": "POST",
            "endpoint": "/v2/checkout/orders",
            "required_params": ["purchase_units"]
        },
        "get_order": {
            "method": "GET",
            "endpoint": "/v2/checkout/orders/{order_id}",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "update_order": {
            "method": "PATCH",
            "endpoint": "/v2/checkout/orders/{order_id}",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "authorize_order": {
            "method": "POST",
            "endpoint": "/v2/checkout/orders/{order_id}/authorize",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "capture_order": {
            "method": "POST",
            "endpoint": "/v2/checkout/orders/{order_id}/capture",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        
        # Payments API v2
        "capture_payment": {
            "method": "POST",
            "endpoint": "/v2/payments/authorizations/{authorization_id}/capture",
            "required_params": ["authorization_id"],
            "path_params": ["authorization_id"]
        },
        "get_capture": {
            "method": "GET",
            "endpoint": "/v2/payments/captures/{capture_id}",
            "required_params": ["capture_id"],
            "path_params": ["capture_id"]
        },
        "refund_capture": {
            "method": "POST",
            "endpoint": "/v2/payments/captures/{capture_id}/refund",
            "required_params": ["capture_id"],
            "path_params": ["capture_id"]
        },
        "get_refund": {
            "method": "GET",
            "endpoint": "/v2/payments/refunds/{refund_id}",
            "required_params": ["refund_id"],
            "path_params": ["refund_id"]
        },
        
        # Authorizations API v2
        "get_authorization": {
            "method": "GET",
            "endpoint": "/v2/payments/authorizations/{authorization_id}",
            "required_params": ["authorization_id"],
            "path_params": ["authorization_id"]
        },
        "capture_authorization": {
            "method": "POST",
            "endpoint": "/v2/payments/authorizations/{authorization_id}/capture",
            "required_params": ["authorization_id"],
            "path_params": ["authorization_id"]
        },
        "reauthorize_authorization": {
            "method": "POST",
            "endpoint": "/v2/payments/authorizations/{authorization_id}/reauthorize",
            "required_params": ["authorization_id"],
            "path_params": ["authorization_id"]
        },
        "void_authorization": {
            "method": "POST",
            "endpoint": "/v2/payments/authorizations/{authorization_id}/void",
            "required_params": ["authorization_id"],
            "path_params": ["authorization_id"]
        },
        
        # Subscriptions API v1
        "create_subscription": {
            "method": "POST",
            "endpoint": "/v1/billing/subscriptions",
            "required_params": []
        },
        "get_subscription": {
            "method": "GET",
            "endpoint": "/v1/billing/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "update_subscription": {
            "method": "PATCH",
            "endpoint": "/v1/billing/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "cancel_subscription": {
            "method": "POST",
            "endpoint": "/v1/billing/subscriptions/{subscription_id}/cancel",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "activate_subscription": {
            "method": "POST",
            "endpoint": "/v1/billing/subscriptions/{subscription_id}/activate",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "suspend_subscription": {
            "method": "POST",
            "endpoint": "/v1/billing/subscriptions/{subscription_id}/suspend",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "list_subscriptions": {
            "method": "GET",
            "endpoint": "/v1/billing/subscriptions",
            "required_params": []
        },
        
        # Invoicing API v2
        "create_invoice": {
            "method": "POST",
            "endpoint": "/v2/invoicing/invoices",
            "required_params": []
        },
        "get_invoice": {
            "method": "GET",
            "endpoint": "/v2/invoicing/invoices/{invoice_id}",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "update_invoice": {
            "method": "PUT",
            "endpoint": "/v2/invoicing/invoices/{invoice_id}",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "send_invoice": {
            "method": "POST",
            "endpoint": "/v2/invoicing/invoices/{invoice_id}/send",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "cancel_invoice": {
            "method": "POST",
            "endpoint": "/v2/invoicing/invoices/{invoice_id}/cancel",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "delete_invoice": {
            "method": "DELETE",
            "endpoint": "/v2/invoicing/invoices/{invoice_id}",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "list_invoices": {
            "method": "GET",
            "endpoint": "/v2/invoicing/invoices",
            "required_params": []
        },
        
        # Disputes API v1
        "list_disputes": {
            "method": "GET",
            "endpoint": "/v1/customer/disputes",
            "required_params": []
        },
        "get_dispute": {
            "method": "GET",
            "endpoint": "/v1/customer/disputes/{dispute_id}",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        "update_dispute": {
            "method": "PATCH",
            "endpoint": "/v1/customer/disputes/{dispute_id}",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        
        # Webhooks API v1
        "create_webhook": {
            "method": "POST",
            "endpoint": "/v1/notifications/webhooks",
            "required_params": ["webhook_url", "event_types"]
        },
        "get_webhook": {
            "method": "GET",
            "endpoint": "/v1/notifications/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "path_params": ["webhook_id"]
        },
        "update_webhook": {
            "method": "PATCH",
            "endpoint": "/v1/notifications/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "path_params": ["webhook_id"]
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "/v1/notifications/webhooks/{webhook_id}",
            "required_params": ["webhook_id"],
            "path_params": ["webhook_id"]
        },
        "list_webhooks": {
            "method": "GET",
            "endpoint": "/v1/notifications/webhooks",
            "required_params": []
        },
        "verify_webhook": {
            "method": "POST",
            "endpoint": "/v1/notifications/verify-webhook-signature",
            "required_params": ["webhook_headers", "webhook_body"]
        },
        "simulate_webhook": {
            "method": "POST",
            "endpoint": "/v1/notifications/simulate-event",
            "required_params": []
        },
        
        # Payouts API v1
        "create_payout": {
            "method": "POST",
            "endpoint": "/v1/payments/payouts",
            "required_params": []
        },
        "get_payout": {
            "method": "GET",
            "endpoint": "/v1/payments/payouts/{payout_batch_id}",
            "required_params": ["payout_batch_id"],
            "path_params": ["payout_batch_id"]
        },
        "cancel_payout": {
            "method": "POST",
            "endpoint": "/v1/payments/payouts/{payout_batch_id}/cancel",
            "required_params": ["payout_batch_id"],
            "path_params": ["payout_batch_id"]
        },
        
        # Catalog Products API v1
        "create_product": {
            "method": "POST",
            "endpoint": "/v1/catalogs/products",
            "required_params": []
        },
        "get_product": {
            "method": "GET",
            "endpoint": "/v1/catalogs/products/{product_id}",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "update_product": {
            "method": "PATCH",
            "endpoint": "/v1/catalogs/products/{product_id}",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "list_products": {
            "method": "GET",
            "endpoint": "/v1/catalogs/products",
            "required_params": []
        },
        
        # Billing Plans API v1
        "create_plan": {
            "method": "POST",
            "endpoint": "/v1/billing/plans",
            "required_params": []
        },
        "get_plan": {
            "method": "GET",
            "endpoint": "/v1/billing/plans/{plan_id}",
            "required_params": ["plan_id"],
            "path_params": ["plan_id"]
        },
        "update_plan": {
            "method": "PATCH",
            "endpoint": "/v1/billing/plans/{plan_id}",
            "required_params": ["plan_id"],
            "path_params": ["plan_id"]
        },
        "list_plans": {
            "method": "GET",
            "endpoint": "/v1/billing/plans",
            "required_params": []
        },
        "activate_plan": {
            "method": "POST",
            "endpoint": "/v1/billing/plans/{plan_id}/activate",
            "required_params": ["plan_id"],
            "path_params": ["plan_id"]
        },
        "deactivate_plan": {
            "method": "POST",
            "endpoint": "/v1/billing/plans/{plan_id}/deactivate",
            "required_params": ["plan_id"],
            "path_params": ["plan_id"]
        }
    }

    def __init__(self):
        super().__init__()
        self.client = None
        self.access_token = None

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="paypal",
            description="Comprehensive PayPal API integration for orders, payments, subscriptions, and webhooks",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The PayPal operation to perform",
                    required=True,
                    options=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.STRING,
                    description="PayPal Client ID for authentication",
                    required=True,
                    sensitive=True
                ),
                NodeParameter(
                    name="client_secret",
                    type=NodeParameterType.STRING,
                    description="PayPal Client Secret for authentication",
                    required=True,
                    sensitive=True
                ),
                NodeParameter(
                    name="sandbox",
                    type=NodeParameterType.BOOLEAN,
                    description="Use PayPal sandbox environment",
                    required=False,
                    default=True
                ),
                # Common parameters
                NodeParameter(
                    name="order_id",
                    type=NodeParameterType.STRING,
                    description="Order ID for order operations",
                    required=False
                ),
                NodeParameter(
                    name="payment_id",
                    type=NodeParameterType.STRING,
                    description="Payment ID for payment operations",
                    required=False
                ),
                NodeParameter(
                    name="authorization_id",
                    type=NodeParameterType.STRING,
                    description="Authorization ID for authorization operations",
                    required=False
                ),
                NodeParameter(
                    name="capture_id",
                    type=NodeParameterType.STRING,
                    description="Capture ID for capture operations",
                    required=False
                ),
                NodeParameter(
                    name="refund_id",
                    type=NodeParameterType.STRING,
                    description="Refund ID for refund operations",
                    required=False
                ),
                NodeParameter(
                    name="subscription_id",
                    type=NodeParameterType.STRING,
                    description="Subscription ID for subscription operations",
                    required=False
                ),
                NodeParameter(
                    name="invoice_id",
                    type=NodeParameterType.STRING,
                    description="Invoice ID for invoice operations",
                    required=False
                ),
                NodeParameter(
                    name="dispute_id",
                    type=NodeParameterType.STRING,
                    description="Dispute ID for dispute operations",
                    required=False
                ),
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                NodeParameter(
                    name="payout_batch_id",
                    type=NodeParameterType.STRING,
                    description="Payout batch ID for payout operations",
                    required=False
                ),
                NodeParameter(
                    name="product_id",
                    type=NodeParameterType.STRING,
                    description="Product ID for product operations",
                    required=False
                ),
                NodeParameter(
                    name="plan_id",
                    type=NodeParameterType.STRING,
                    description="Plan ID for plan operations",
                    required=False
                ),
                # Data parameters
                NodeParameter(
                    name="data",
                    type=NodeParameterType.OBJECT,
                    description="Request data for operations that require a body",
                    required=False
                ),
                NodeParameter(
                    name="purchase_units",
                    type=NodeParameterType.OBJECT,
                    description="Purchase units for order creation",
                    required=False
                ),
                NodeParameter(
                    name="intent",
                    type=NodeParameterType.STRING,
                    description="Order intent (CAPTURE or AUTHORIZE)",
                    required=False,
                    default="CAPTURE",
                    options=["CAPTURE", "AUTHORIZE"]
                ),
                NodeParameter(
                    name="webhook_url",
                    type=NodeParameterType.STRING,
                    description="Webhook URL for webhook operations",
                    required=False
                ),
                NodeParameter(
                    name="event_types",
                    type=NodeParameterType.OBJECT,
                    description="Event types for webhook creation",
                    required=False
                ),
                NodeParameter(
                    name="webhook_headers",
                    type=NodeParameterType.OBJECT,
                    description="Webhook headers for verification",
                    required=False
                ),
                NodeParameter(
                    name="webhook_body",
                    type=NodeParameterType.OBJECT,
                    description="Webhook body for verification",
                    required=False
                ),
                NodeParameter(
                    name="params",
                    type=NodeParameterType.OBJECT,
                    description="Query parameters for the request",
                    required=False
                ),
                NodeParameter(
                    name="headers",
                    type=NodeParameterType.OBJECT,
                    description="Additional headers for the request",
                    required=False
                )
            ],
            outputs=[
                "success",
                "error", 
                "data",
                "status_code",
                "order_id",
                "payment_id",
                "access_token"
            ],
            metadata={
                "category": "payments",
                "vendor": "paypal",
                "documentation": "https://developer.paypal.com/api/rest/",
                "rate_limits": {
                    "requests_per_second": 10,
                    "varies_by_endpoint": True
                }
            }
        )

    def _get_config(self, sandbox: bool = True) -> Dict[str, Any]:
        """Get configuration for UniversalRequestNode."""
        config = self.CONFIG.copy()
        
        # Update base URL for environment
        if sandbox:
            config["base_url"] = config["sandbox_url"]
            
        return config

    async def _get_access_token(self, client_id: str, client_secret: str, sandbox: bool = True) -> str:
        """Get PayPal access token using client credentials."""
        # Create a temporary client for token request
        config = self._get_config(sandbox)
        config["authentication"] = {"type": "basic_auth"}
        
        temp_client = UniversalRequestNode(config)
        
        # Prepare basic auth
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_header = base64.b64encode(auth_bytes).decode('utf-8')
        
        try:
            response = await temp_client.request(
                method="POST",
                endpoint="/v1/oauth2/token",
                data="grant_type=client_credentials",
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                content_type="application/x-www-form-urlencoded"
            )
            
            if response.get("status") == "success":
                return response["data"].get("access_token")
            else:
                raise NodeValidationError(f"Failed to get access token: {response.get('error')}")
                
        finally:
            await temp_client.close()

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PayPal operation using UniversalRequestNode."""
        try:
            # Get operation details
            operation = parameters.get("operation")
            if not operation:
                raise NodeValidationError("Operation is required")
                
            if operation not in self.OPERATIONS:
                raise NodeValidationError(f"Unknown operation: {operation}")
                
            # Get credentials
            client_id = parameters.get("client_id")
            client_secret = parameters.get("client_secret")
            if not client_id or not client_secret:
                raise NodeValidationError("PayPal client_id and client_secret are required")
                
            sandbox = parameters.get("sandbox", True)
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Handle authentication operation separately
            if operation == "get_access_token":
                access_token = await self._get_access_token(client_id, client_secret, sandbox)
                return {
                    "success": True,
                    "error": None,
                    "data": {"access_token": access_token},
                    "status_code": 200,
                    "order_id": None,
                    "payment_id": None,
                    "access_token": access_token
                }
            
            # Get access token for other operations
            if not self.access_token:
                self.access_token = await self._get_access_token(client_id, client_secret, sandbox)
            
            # Setup UniversalRequestNode config
            config = self._get_config(sandbox)
            
            # Initialize client if needed
            if not self.client:
                self.client = UniversalRequestNode(config)
            
            # Prepare request parameters with path substitution
            request_params = {}
            
            # Add all provided parameters for path substitution
            for key, value in parameters.items():
                if value is not None and key not in ["operation", "client_id", "client_secret", "sandbox"]:
                    request_params[key] = value
            
            # Prepare request data
            request_data = None
            if operation in ["create_order", "create_subscription", "create_invoice", "create_webhook", "create_product", "create_plan", "create_payout"]:
                request_data = parameters.get("data", {})
                
                # Special handling for order creation
                if operation == "create_order":
                    request_data = {
                        "intent": parameters.get("intent", "CAPTURE"),
                        "purchase_units": parameters.get("purchase_units", [])
                    }
                    if parameters.get("payer"):
                        request_data["payer"] = parameters.get("payer")
                    if parameters.get("application_context"):
                        request_data["application_context"] = parameters.get("application_context")
                
                # Special handling for webhook creation
                elif operation == "create_webhook":
                    request_data = {
                        "url": parameters.get("webhook_url"),
                        "event_types": parameters.get("event_types", [])
                    }
                
                # Special handling for webhook verification
                elif operation == "verify_webhook":
                    webhook_headers = parameters.get("webhook_headers", {})
                    request_data = {
                        "auth_algo": webhook_headers.get("PAYPAL-AUTH-ALGO"),
                        "cert_id": webhook_headers.get("PAYPAL-CERT-ID"), 
                        "transmission_id": webhook_headers.get("PAYPAL-TRANSMISSION-ID"),
                        "transmission_sig": webhook_headers.get("PAYPAL-TRANSMISSION-SIG"),
                        "transmission_time": webhook_headers.get("PAYPAL-TRANSMISSION-TIME"),
                        "webhook_id": parameters.get("webhook_id"),
                        "webhook_event": parameters.get("webhook_body", {})
                    }
            
            elif operation in ["update_order", "update_subscription", "update_invoice", "update_webhook", "update_product", "update_plan", "update_dispute"]:
                request_data = parameters.get("data", [])  # PATCH operations usually expect arrays
            
            elif operation in ["refund_capture", "capture_authorization", "reauthorize_authorization"]:
                request_data = parameters.get("data", {})
            
            # Extract query params and additional headers
            query_params = parameters.get("params", {})
            additional_headers = parameters.get("headers", {})
            
            # Add access token to headers
            additional_headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Add prefer header if specified
            if parameters.get("prefer"):
                additional_headers["Prefer"] = parameters.get("prefer")
            
            # Make the request
            response = await self.client.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if request_data else None,
                params=query_params if query_params else None,
                headers=additional_headers if additional_headers else None,
                **request_params
            )
            
            # Extract specific IDs from response for convenience
            response_data = response.get("data", {})
            order_id = None
            payment_id = None
            
            if isinstance(response_data, dict):
                order_id = response_data.get("id") if "status" in response_data else None
                
                if "payment" in response_data:
                    payment_id = response_data["payment"].get("id")
                elif "id" in response_data and "status" in response_data:
                    payment_id = response_data["id"]
            
            return {
                "success": response.get("status") == "success",
                "error": response.get("error"),
                "data": response_data,
                "status_code": response.get("status_code", 200),
                "order_id": order_id,
                "payment_id": payment_id,
                "access_token": self.access_token
            }
            
        except Exception as e:
            logger.error(f"PayPal operation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "status_code": 500,
                "order_id": None,
                "payment_id": None,
                "access_token": None
            }

    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.close()

class PayPalOperation:
    """PayPal operation constants."""
    # Constants for compatibility
    GET_ACCESS_TOKEN = "get_access_token"
    CREATE_ORDER = "create_order"
    GET_ORDER = "get_order"
    UPDATE_ORDER = "update_order"
    AUTHORIZE_ORDER = "authorize_order"
    CAPTURE_ORDER = "capture_order"
    CAPTURE_PAYMENT = "capture_payment"
    GET_CAPTURE = "get_capture"
    REFUND_CAPTURE = "refund_capture"
    GET_REFUND = "get_refund"
    GET_AUTHORIZATION = "get_authorization"
    CAPTURE_AUTHORIZATION = "capture_authorization"
    REAUTHORIZE_AUTHORIZATION = "reauthorize_authorization"
    VOID_AUTHORIZATION = "void_authorization"
    CREATE_SUBSCRIPTION = "create_subscription"
    GET_SUBSCRIPTION = "get_subscription"
    UPDATE_SUBSCRIPTION = "update_subscription"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    ACTIVATE_SUBSCRIPTION = "activate_subscription"
    SUSPEND_SUBSCRIPTION = "suspend_subscription"
    LIST_SUBSCRIPTIONS = "list_subscriptions"
    CREATE_INVOICE = "create_invoice"
    GET_INVOICE = "get_invoice"
    UPDATE_INVOICE = "update_invoice"
    SEND_INVOICE = "send_invoice"
    CANCEL_INVOICE = "cancel_invoice"
    DELETE_INVOICE = "delete_invoice"
    LIST_INVOICES = "list_invoices"
    LIST_DISPUTES = "list_disputes"
    GET_DISPUTE = "get_dispute"
    UPDATE_DISPUTE = "update_dispute"
    CREATE_WEBHOOK = "create_webhook"
    GET_WEBHOOK = "get_webhook"
    UPDATE_WEBHOOK = "update_webhook"
    DELETE_WEBHOOK = "delete_webhook"
    LIST_WEBHOOKS = "list_webhooks"
    VERIFY_WEBHOOK = "verify_webhook"
    SIMULATE_WEBHOOK = "simulate_webhook"
    CREATE_PAYOUT = "create_payout"
    GET_PAYOUT = "get_payout"
    CANCEL_PAYOUT = "cancel_payout"
    CREATE_PRODUCT = "create_product"
    GET_PRODUCT = "get_product"
    UPDATE_PRODUCT = "update_product"
    LIST_PRODUCTS = "list_products"
    CREATE_PLAN = "create_plan"
    GET_PLAN = "get_plan"
    UPDATE_PLAN = "update_plan"
    LIST_PLANS = "list_plans"
    ACTIVATE_PLAN = "activate_plan"
    DEACTIVATE_PLAN = "deactivate_plan"

class PayPalHelper:
    """Helper utilities for PayPal API operations."""
    
    @staticmethod
    def create_amount(value: str, currency: str = "USD") -> Dict[str, Any]:
        """Create amount object for PayPal payments."""
        return {
            "currency_code": currency,
            "value": value
        }
    
    @staticmethod
    def create_purchase_unit(amount: Dict[str, Any], reference_id: Optional[str] = None) -> Dict[str, Any]:
        """Create purchase unit for orders."""
        unit = {"amount": amount}
        if reference_id:
            unit["reference_id"] = reference_id
        return unit
    
    @staticmethod
    def create_payer(email: str, name: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create payer object."""
        payer = {"email_address": email}
        if name:
            payer["name"] = name
        return payer

# Register the node
if __name__ == "__main__":
    node = PayPalNode()
    print(f"PayPalNode registered with {len(node.get_schema().parameters)} parameters")