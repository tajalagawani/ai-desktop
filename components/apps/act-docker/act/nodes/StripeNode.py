"""
Stripe Node - Comprehensive payment processing integration for Stripe API
Supports all major Stripe operations including payments, customers, subscriptions,
invoices, refunds, disputes, transfers, and more.
Uses Stripe Python SDK with full API coverage.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import stripe
from decimal import Decimal

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

class StripeOperation:
    """All available Stripe operations."""
    
    # Payment Intents Operations
    CREATE_PAYMENT_INTENT = "create_payment_intent"
    RETRIEVE_PAYMENT_INTENT = "retrieve_payment_intent"
    UPDATE_PAYMENT_INTENT = "update_payment_intent"
    CONFIRM_PAYMENT_INTENT = "confirm_payment_intent"
    CAPTURE_PAYMENT_INTENT = "capture_payment_intent"
    CANCEL_PAYMENT_INTENT = "cancel_payment_intent"
    LIST_PAYMENT_INTENTS = "list_payment_intents"
    INCREMENT_PAYMENT_INTENT_AUTH = "increment_payment_intent_authorization"
    SEARCH_PAYMENT_INTENTS = "search_payment_intents"
    VERIFY_MICRODEPOSITS = "verify_microdeposits"
    
    # Customer Operations
    CREATE_CUSTOMER = "create_customer"
    RETRIEVE_CUSTOMER = "retrieve_customer"
    UPDATE_CUSTOMER = "update_customer"
    DELETE_CUSTOMER = "delete_customer"
    LIST_CUSTOMERS = "list_customers"
    SEARCH_CUSTOMERS = "search_customers"
    CREATE_CUSTOMER_SOURCE = "create_customer_source"
    RETRIEVE_CUSTOMER_SOURCE = "retrieve_customer_source"
    UPDATE_CUSTOMER_SOURCE = "update_customer_source"
    DELETE_CUSTOMER_SOURCE = "delete_customer_source"
    LIST_CUSTOMER_SOURCES = "list_customer_sources"
    
    # Subscription Operations
    CREATE_SUBSCRIPTION = "create_subscription"
    RETRIEVE_SUBSCRIPTION = "retrieve_subscription"
    UPDATE_SUBSCRIPTION = "update_subscription"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    LIST_SUBSCRIPTIONS = "list_subscriptions"
    SEARCH_SUBSCRIPTIONS = "search_subscriptions"
    RESUME_SUBSCRIPTION = "resume_subscription"
    PAUSE_SUBSCRIPTION = "pause_subscription"
    DELETE_SUBSCRIPTION_DISCOUNT = "delete_subscription_discount"
    RETRIEVE_UPCOMING_INVOICE = "retrieve_upcoming_invoice"
    
    # Invoice Operations
    CREATE_INVOICE = "create_invoice"
    RETRIEVE_INVOICE = "retrieve_invoice"
    UPDATE_INVOICE = "update_invoice"
    DELETE_INVOICE = "delete_invoice"
    FINALIZE_INVOICE = "finalize_invoice"
    PAY_INVOICE = "pay_invoice"
    SEND_INVOICE = "send_invoice"
    VOID_INVOICE = "void_invoice"
    MARK_INVOICE_UNCOLLECTIBLE = "mark_invoice_uncollectible"
    LIST_INVOICES = "list_invoices"
    SEARCH_INVOICES = "search_invoices"
    CREATE_INVOICE_ITEM = "create_invoice_item"
    RETRIEVE_INVOICE_ITEM = "retrieve_invoice_item"
    UPDATE_INVOICE_ITEM = "update_invoice_item"
    DELETE_INVOICE_ITEM = "delete_invoice_item"
    LIST_INVOICE_ITEMS = "list_invoice_items"
    
    # Product & Price Operations
    CREATE_PRODUCT = "create_product"
    RETRIEVE_PRODUCT = "retrieve_product"
    UPDATE_PRODUCT = "update_product"
    DELETE_PRODUCT = "delete_product"
    LIST_PRODUCTS = "list_products"
    SEARCH_PRODUCTS = "search_products"
    CREATE_PRICE = "create_price"
    RETRIEVE_PRICE = "retrieve_price"
    UPDATE_PRICE = "update_price"
    LIST_PRICES = "list_prices"
    SEARCH_PRICES = "search_prices"
    
    # Charge Operations (Legacy but still supported)
    CREATE_CHARGE = "create_charge"
    RETRIEVE_CHARGE = "retrieve_charge"
    UPDATE_CHARGE = "update_charge"
    CAPTURE_CHARGE = "capture_charge"
    LIST_CHARGES = "list_charges"
    SEARCH_CHARGES = "search_charges"
    
    # Refund Operations
    CREATE_REFUND = "create_refund"
    RETRIEVE_REFUND = "retrieve_refund"
    UPDATE_REFUND = "update_refund"
    CANCEL_REFUND = "cancel_refund"
    LIST_REFUNDS = "list_refunds"
    
    # Dispute Operations
    RETRIEVE_DISPUTE = "retrieve_dispute"
    UPDATE_DISPUTE = "update_dispute"
    CLOSE_DISPUTE = "close_dispute"
    LIST_DISPUTES = "list_disputes"
    
    # Transfer Operations
    CREATE_TRANSFER = "create_transfer"
    RETRIEVE_TRANSFER = "retrieve_transfer"
    UPDATE_TRANSFER = "update_transfer"
    LIST_TRANSFERS = "list_transfers"
    CREATE_TRANSFER_REVERSAL = "create_transfer_reversal"
    RETRIEVE_TRANSFER_REVERSAL = "retrieve_transfer_reversal"
    UPDATE_TRANSFER_REVERSAL = "update_transfer_reversal"
    LIST_TRANSFER_REVERSALS = "list_transfer_reversals"
    
    # Payout Operations
    CREATE_PAYOUT = "create_payout"
    RETRIEVE_PAYOUT = "retrieve_payout"
    UPDATE_PAYOUT = "update_payout"
    CANCEL_PAYOUT = "cancel_payout"
    LIST_PAYOUTS = "list_payouts"
    
    # Balance Operations
    RETRIEVE_BALANCE = "retrieve_balance"
    RETRIEVE_BALANCE_TRANSACTION = "retrieve_balance_transaction"
    LIST_BALANCE_TRANSACTIONS = "list_balance_transactions"
    
    # Payment Method Operations
    CREATE_PAYMENT_METHOD = "create_payment_method"
    RETRIEVE_PAYMENT_METHOD = "retrieve_payment_method"
    UPDATE_PAYMENT_METHOD = "update_payment_method"
    LIST_PAYMENT_METHODS = "list_payment_methods"
    ATTACH_PAYMENT_METHOD = "attach_payment_method"
    DETACH_PAYMENT_METHOD = "detach_payment_method"
    
    # Setup Intent Operations
    CREATE_SETUP_INTENT = "create_setup_intent"
    RETRIEVE_SETUP_INTENT = "retrieve_setup_intent"
    UPDATE_SETUP_INTENT = "update_setup_intent"
    CONFIRM_SETUP_INTENT = "confirm_setup_intent"
    CANCEL_SETUP_INTENT = "cancel_setup_intent"
    LIST_SETUP_INTENTS = "list_setup_intents"
    
    # Checkout Session Operations
    CREATE_CHECKOUT_SESSION = "create_checkout_session"
    RETRIEVE_CHECKOUT_SESSION = "retrieve_checkout_session"
    LIST_CHECKOUT_SESSIONS = "list_checkout_sessions"
    EXPIRE_CHECKOUT_SESSION = "expire_checkout_session"
    
    # Coupon Operations
    CREATE_COUPON = "create_coupon"
    RETRIEVE_COUPON = "retrieve_coupon"
    UPDATE_COUPON = "update_coupon"
    DELETE_COUPON = "delete_coupon"
    LIST_COUPONS = "list_coupons"
    
    # Tax Rate Operations
    CREATE_TAX_RATE = "create_tax_rate"
    RETRIEVE_TAX_RATE = "retrieve_tax_rate"
    UPDATE_TAX_RATE = "update_tax_rate"
    LIST_TAX_RATES = "list_tax_rates"
    
    # Webhook Endpoint Operations
    CREATE_WEBHOOK_ENDPOINT = "create_webhook_endpoint"
    RETRIEVE_WEBHOOK_ENDPOINT = "retrieve_webhook_endpoint"
    UPDATE_WEBHOOK_ENDPOINT = "update_webhook_endpoint"
    DELETE_WEBHOOK_ENDPOINT = "delete_webhook_endpoint"
    LIST_WEBHOOK_ENDPOINTS = "list_webhook_endpoints"
    
    # Event Operations
    RETRIEVE_EVENT = "retrieve_event"
    LIST_EVENTS = "list_events"
    
    # File Operations
    CREATE_FILE = "create_file"
    RETRIEVE_FILE = "retrieve_file"
    LIST_FILES = "list_files"
    
    # Account Operations (Connect)
    CREATE_ACCOUNT = "create_account"
    RETRIEVE_ACCOUNT = "retrieve_account"
    UPDATE_ACCOUNT = "update_account"
    DELETE_ACCOUNT = "delete_account"
    LIST_ACCOUNTS = "list_accounts"
    CREATE_ACCOUNT_LINK = "create_account_link"
    CREATE_LOGIN_LINK = "create_login_link"
    
    # Utility Operations
    TEST_WEBHOOK_ENDPOINT = "test_webhook_endpoint"
    CONSTRUCT_EVENT = "construct_event"

class StripeNode(BaseNode):
    """
    Comprehensive Stripe payment processing node supporting all major Stripe API operations.
    Handles payments, subscriptions, customers, invoices, and more.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.stripe = stripe
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Stripe node."""
        return NodeSchema(
            node_type="stripe",
            version="1.0.0",
            description="Comprehensive Stripe payment processing with full API coverage",
            parameters=[
                # Common Parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Stripe operation to perform",
                    required=True,
                    enum=[
                        # Payment Intents
                        StripeOperation.CREATE_PAYMENT_INTENT,
                        StripeOperation.RETRIEVE_PAYMENT_INTENT,
                        StripeOperation.UPDATE_PAYMENT_INTENT,
                        StripeOperation.CONFIRM_PAYMENT_INTENT,
                        StripeOperation.CAPTURE_PAYMENT_INTENT,
                        StripeOperation.CANCEL_PAYMENT_INTENT,
                        StripeOperation.LIST_PAYMENT_INTENTS,
                        StripeOperation.INCREMENT_PAYMENT_INTENT_AUTH,
                        StripeOperation.SEARCH_PAYMENT_INTENTS,
                        StripeOperation.VERIFY_MICRODEPOSITS,
                        # Customers
                        StripeOperation.CREATE_CUSTOMER,
                        StripeOperation.RETRIEVE_CUSTOMER,
                        StripeOperation.UPDATE_CUSTOMER,
                        StripeOperation.DELETE_CUSTOMER,
                        StripeOperation.LIST_CUSTOMERS,
                        StripeOperation.SEARCH_CUSTOMERS,
                        StripeOperation.CREATE_CUSTOMER_SOURCE,
                        StripeOperation.RETRIEVE_CUSTOMER_SOURCE,
                        StripeOperation.UPDATE_CUSTOMER_SOURCE,
                        StripeOperation.DELETE_CUSTOMER_SOURCE,
                        StripeOperation.LIST_CUSTOMER_SOURCES,
                        # Subscriptions
                        StripeOperation.CREATE_SUBSCRIPTION,
                        StripeOperation.RETRIEVE_SUBSCRIPTION,
                        StripeOperation.UPDATE_SUBSCRIPTION,
                        StripeOperation.CANCEL_SUBSCRIPTION,
                        StripeOperation.LIST_SUBSCRIPTIONS,
                        StripeOperation.SEARCH_SUBSCRIPTIONS,
                        StripeOperation.RESUME_SUBSCRIPTION,
                        StripeOperation.PAUSE_SUBSCRIPTION,
                        StripeOperation.DELETE_SUBSCRIPTION_DISCOUNT,
                        StripeOperation.RETRIEVE_UPCOMING_INVOICE,
                        # Invoices
                        StripeOperation.CREATE_INVOICE,
                        StripeOperation.RETRIEVE_INVOICE,
                        StripeOperation.UPDATE_INVOICE,
                        StripeOperation.DELETE_INVOICE,
                        StripeOperation.FINALIZE_INVOICE,
                        StripeOperation.PAY_INVOICE,
                        StripeOperation.SEND_INVOICE,
                        StripeOperation.VOID_INVOICE,
                        StripeOperation.MARK_INVOICE_UNCOLLECTIBLE,
                        StripeOperation.LIST_INVOICES,
                        StripeOperation.SEARCH_INVOICES,
                        StripeOperation.CREATE_INVOICE_ITEM,
                        StripeOperation.RETRIEVE_INVOICE_ITEM,
                        StripeOperation.UPDATE_INVOICE_ITEM,
                        StripeOperation.DELETE_INVOICE_ITEM,
                        StripeOperation.LIST_INVOICE_ITEMS,
                        # Products & Prices
                        StripeOperation.CREATE_PRODUCT,
                        StripeOperation.RETRIEVE_PRODUCT,
                        StripeOperation.UPDATE_PRODUCT,
                        StripeOperation.DELETE_PRODUCT,
                        StripeOperation.LIST_PRODUCTS,
                        StripeOperation.SEARCH_PRODUCTS,
                        StripeOperation.CREATE_PRICE,
                        StripeOperation.RETRIEVE_PRICE,
                        StripeOperation.UPDATE_PRICE,
                        StripeOperation.LIST_PRICES,
                        StripeOperation.SEARCH_PRICES,
                        # Charges
                        StripeOperation.CREATE_CHARGE,
                        StripeOperation.RETRIEVE_CHARGE,
                        StripeOperation.UPDATE_CHARGE,
                        StripeOperation.CAPTURE_CHARGE,
                        StripeOperation.LIST_CHARGES,
                        StripeOperation.SEARCH_CHARGES,
                        # Refunds
                        StripeOperation.CREATE_REFUND,
                        StripeOperation.RETRIEVE_REFUND,
                        StripeOperation.UPDATE_REFUND,
                        StripeOperation.CANCEL_REFUND,
                        StripeOperation.LIST_REFUNDS,
                        # Disputes
                        StripeOperation.RETRIEVE_DISPUTE,
                        StripeOperation.UPDATE_DISPUTE,
                        StripeOperation.CLOSE_DISPUTE,
                        StripeOperation.LIST_DISPUTES,
                        # Transfers
                        StripeOperation.CREATE_TRANSFER,
                        StripeOperation.RETRIEVE_TRANSFER,
                        StripeOperation.UPDATE_TRANSFER,
                        StripeOperation.LIST_TRANSFERS,
                        StripeOperation.CREATE_TRANSFER_REVERSAL,
                        StripeOperation.RETRIEVE_TRANSFER_REVERSAL,
                        StripeOperation.UPDATE_TRANSFER_REVERSAL,
                        StripeOperation.LIST_TRANSFER_REVERSALS,
                        # Payouts
                        StripeOperation.CREATE_PAYOUT,
                        StripeOperation.RETRIEVE_PAYOUT,
                        StripeOperation.UPDATE_PAYOUT,
                        StripeOperation.CANCEL_PAYOUT,
                        StripeOperation.LIST_PAYOUTS,
                        # Balance
                        StripeOperation.RETRIEVE_BALANCE,
                        StripeOperation.RETRIEVE_BALANCE_TRANSACTION,
                        StripeOperation.LIST_BALANCE_TRANSACTIONS,
                        # Payment Methods
                        StripeOperation.CREATE_PAYMENT_METHOD,
                        StripeOperation.RETRIEVE_PAYMENT_METHOD,
                        StripeOperation.UPDATE_PAYMENT_METHOD,
                        StripeOperation.LIST_PAYMENT_METHODS,
                        StripeOperation.ATTACH_PAYMENT_METHOD,
                        StripeOperation.DETACH_PAYMENT_METHOD,
                        # Setup Intents
                        StripeOperation.CREATE_SETUP_INTENT,
                        StripeOperation.RETRIEVE_SETUP_INTENT,
                        StripeOperation.UPDATE_SETUP_INTENT,
                        StripeOperation.CONFIRM_SETUP_INTENT,
                        StripeOperation.CANCEL_SETUP_INTENT,
                        StripeOperation.LIST_SETUP_INTENTS,
                        # Checkout Sessions
                        StripeOperation.CREATE_CHECKOUT_SESSION,
                        StripeOperation.RETRIEVE_CHECKOUT_SESSION,
                        StripeOperation.LIST_CHECKOUT_SESSIONS,
                        StripeOperation.EXPIRE_CHECKOUT_SESSION,
                        # Coupons
                        StripeOperation.CREATE_COUPON,
                        StripeOperation.RETRIEVE_COUPON,
                        StripeOperation.UPDATE_COUPON,
                        StripeOperation.DELETE_COUPON,
                        StripeOperation.LIST_COUPONS,
                        # Tax Rates
                        StripeOperation.CREATE_TAX_RATE,
                        StripeOperation.RETRIEVE_TAX_RATE,
                        StripeOperation.UPDATE_TAX_RATE,
                        StripeOperation.LIST_TAX_RATES,
                        # Webhook Endpoints
                        StripeOperation.CREATE_WEBHOOK_ENDPOINT,
                        StripeOperation.RETRIEVE_WEBHOOK_ENDPOINT,
                        StripeOperation.UPDATE_WEBHOOK_ENDPOINT,
                        StripeOperation.DELETE_WEBHOOK_ENDPOINT,
                        StripeOperation.LIST_WEBHOOK_ENDPOINTS,
                        # Events
                        StripeOperation.RETRIEVE_EVENT,
                        StripeOperation.LIST_EVENTS,
                        # Files
                        StripeOperation.CREATE_FILE,
                        StripeOperation.RETRIEVE_FILE,
                        StripeOperation.LIST_FILES,
                        # Accounts
                        StripeOperation.CREATE_ACCOUNT,
                        StripeOperation.RETRIEVE_ACCOUNT,
                        StripeOperation.UPDATE_ACCOUNT,
                        StripeOperation.DELETE_ACCOUNT,
                        StripeOperation.LIST_ACCOUNTS,
                        StripeOperation.CREATE_ACCOUNT_LINK,
                        StripeOperation.CREATE_LOGIN_LINK,
                        # Utility
                        StripeOperation.TEST_WEBHOOK_ENDPOINT,
                        StripeOperation.CONSTRUCT_EVENT
                    ]
                ),
                
                # Authentication
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.SECRET,
                    description="Stripe API key (starts with sk_test_ or sk_live_)",
                    required=True
                ),
                NodeParameter(
                    name="stripe_account",
                    type=NodeParameterType.STRING,
                    description="Connected account ID for Stripe Connect operations",
                    required=False
                ),
                NodeParameter(
                    name="idempotency_key",
                    type=NodeParameterType.STRING,
                    description="Unique key to prevent duplicate operations",
                    required=False
                ),
                
                # Payment Intent Parameters
                NodeParameter(
                    name="amount",
                    type=NodeParameterType.NUMBER,
                    description="Amount in cents (e.g., 1000 = $10.00)",
                    required=False,
                    operations=[
                        StripeOperation.CREATE_PAYMENT_INTENT,
                        StripeOperation.UPDATE_PAYMENT_INTENT,
                        StripeOperation.CREATE_CHARGE,
                        StripeOperation.CREATE_REFUND
                    ]
                ),
                NodeParameter(
                    name="currency",
                    type=NodeParameterType.STRING,
                    description="Three-letter ISO currency code (e.g., 'usd')",
                    required=False,
                    default="usd"
                ),
                NodeParameter(
                    name="payment_method",
                    type=NodeParameterType.STRING,
                    description="Payment method ID to attach",
                    required=False
                ),
                NodeParameter(
                    name="payment_method_types",
                    type=NodeParameterType.ARRAY,
                    description="Payment method types to accept",
                    required=False,
                    default=["card"]
                ),
                NodeParameter(
                    name="confirm",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to confirm the payment immediately",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="capture_method",
                    type=NodeParameterType.STRING,
                    description="Capture method: 'automatic' or 'manual'",
                    required=False,
                    default="automatic"
                ),
                NodeParameter(
                    name="setup_future_usage",
                    type=NodeParameterType.STRING,
                    description="Indicates intent to save payment method",
                    required=False,
                    enum=["on_session", "off_session"]
                ),
                
                # Customer Parameters
                NodeParameter(
                    name="customer",
                    type=NodeParameterType.STRING,
                    description="Customer ID",
                    required=False
                ),
                NodeParameter(
                    name="email",
                    type=NodeParameterType.STRING,
                    description="Customer email address",
                    required=False
                ),
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Customer name",
                    required=False
                ),
                NodeParameter(
                    name="phone",
                    type=NodeParameterType.STRING,
                    description="Customer phone number",
                    required=False
                ),
                NodeParameter(
                    name="address",
                    type=NodeParameterType.OBJECT,
                    description="Customer address object",
                    required=False
                ),
                NodeParameter(
                    name="shipping",
                    type=NodeParameterType.OBJECT,
                    description="Shipping information",
                    required=False
                ),
                NodeParameter(
                    name="tax_exempt",
                    type=NodeParameterType.STRING,
                    description="Customer tax exemption status",
                    required=False,
                    enum=["none", "exempt", "reverse"]
                ),
                
                # Subscription Parameters
                NodeParameter(
                    name="items",
                    type=NodeParameterType.ARRAY,
                    description="Subscription items with price IDs",
                    required=False
                ),
                NodeParameter(
                    name="trial_period_days",
                    type=NodeParameterType.NUMBER,
                    description="Number of trial days",
                    required=False
                ),
                NodeParameter(
                    name="trial_end",
                    type=NodeParameterType.NUMBER,
                    description="Unix timestamp for trial end",
                    required=False
                ),
                NodeParameter(
                    name="cancel_at_period_end",
                    type=NodeParameterType.BOOLEAN,
                    description="Cancel subscription at period end",
                    required=False,
                    default=False
                ),
                NodeParameter(
                    name="billing_cycle_anchor",
                    type=NodeParameterType.NUMBER,
                    description="Timestamp for billing cycle anchor",
                    required=False
                ),
                NodeParameter(
                    name="proration_behavior",
                    type=NodeParameterType.STRING,
                    description="How to handle prorations",
                    required=False,
                    enum=["create_prorations", "none", "always_invoice"]
                ),
                
                # Invoice Parameters
                NodeParameter(
                    name="auto_advance",
                    type=NodeParameterType.BOOLEAN,
                    description="Auto-finalize draft invoices",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="collection_method",
                    type=NodeParameterType.STRING,
                    description="Invoice collection method",
                    required=False,
                    enum=["charge_automatically", "send_invoice"]
                ),
                NodeParameter(
                    name="days_until_due",
                    type=NodeParameterType.NUMBER,
                    description="Days until invoice is due",
                    required=False
                ),
                NodeParameter(
                    name="due_date",
                    type=NodeParameterType.NUMBER,
                    description="Unix timestamp for due date",
                    required=False
                ),
                
                # Product & Price Parameters
                NodeParameter(
                    name="product",
                    type=NodeParameterType.STRING,
                    description="Product ID",
                    required=False
                ),
                NodeParameter(
                    name="unit_amount",
                    type=NodeParameterType.NUMBER,
                    description="Price unit amount in cents",
                    required=False
                ),
                NodeParameter(
                    name="recurring",
                    type=NodeParameterType.OBJECT,
                    description="Recurring price configuration",
                    required=False
                ),
                NodeParameter(
                    name="price_data",
                    type=NodeParameterType.OBJECT,
                    description="Inline price data",
                    required=False
                ),
                
                # Common Parameters
                NodeParameter(
                    name="description",
                    type=NodeParameterType.STRING,
                    description="Description for the operation",
                    required=False
                ),
                NodeParameter(
                    name="metadata",
                    type=NodeParameterType.OBJECT,
                    description="Set of key-value pairs for metadata",
                    required=False
                ),
                NodeParameter(
                    name="expand",
                    type=NodeParameterType.ARRAY,
                    description="Properties to expand in response",
                    required=False
                ),
                
                # ID Parameters
                NodeParameter(
                    name="payment_intent_id",
                    type=NodeParameterType.STRING,
                    description="Payment Intent ID",
                    required=False
                ),
                NodeParameter(
                    name="customer_id",
                    type=NodeParameterType.STRING,
                    description="Customer ID",
                    required=False
                ),
                NodeParameter(
                    name="subscription_id",
                    type=NodeParameterType.STRING,
                    description="Subscription ID",
                    required=False
                ),
                NodeParameter(
                    name="invoice_id",
                    type=NodeParameterType.STRING,
                    description="Invoice ID",
                    required=False
                ),
                NodeParameter(
                    name="product_id",
                    type=NodeParameterType.STRING,
                    description="Product ID",
                    required=False
                ),
                NodeParameter(
                    name="price_id",
                    type=NodeParameterType.STRING,
                    description="Price ID",
                    required=False
                ),
                NodeParameter(
                    name="charge_id",
                    type=NodeParameterType.STRING,
                    description="Charge ID",
                    required=False
                ),
                NodeParameter(
                    name="refund_id",
                    type=NodeParameterType.STRING,
                    description="Refund ID",
                    required=False
                ),
                NodeParameter(
                    name="source_id",
                    type=NodeParameterType.STRING,
                    description="Source ID",
                    required=False
                ),
                
                # List Parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of objects to retrieve",
                    required=False,
                    default=10,
                    min_value=1,
                    max_value=100
                ),
                NodeParameter(
                    name="starting_after",
                    type=NodeParameterType.STRING,
                    description="Cursor for pagination",
                    required=False
                ),
                NodeParameter(
                    name="ending_before",
                    type=NodeParameterType.STRING,
                    description="Cursor for reverse pagination",
                    required=False
                ),
                
                # Search Parameters
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query using Stripe's search syntax",
                    required=False
                ),
                
                # Webhook Parameters
                NodeParameter(
                    name="url",
                    type=NodeParameterType.STRING,
                    description="Webhook endpoint URL",
                    required=False
                ),
                NodeParameter(
                    name="enabled_events",
                    type=NodeParameterType.ARRAY,
                    description="Events to enable for webhook",
                    required=False
                ),
                NodeParameter(
                    name="webhook_endpoint_id",
                    type=NodeParameterType.STRING,
                    description="Webhook endpoint ID",
                    required=False
                ),
                NodeParameter(
                    name="payload",
                    type=NodeParameterType.STRING,
                    description="Webhook payload",
                    required=False
                ),
                NodeParameter(
                    name="sig_header",
                    type=NodeParameterType.STRING,
                    description="Stripe signature header",
                    required=False
                ),
                NodeParameter(
                    name="webhook_secret",
                    type=NodeParameterType.SECRET,
                    description="Webhook endpoint secret",
                    required=False
                ),
                
                # Additional Parameters
                NodeParameter(
                    name="statement_descriptor",
                    type=NodeParameterType.STRING,
                    description="Statement descriptor for charges",
                    required=False
                ),
                NodeParameter(
                    name="transfer_data",
                    type=NodeParameterType.OBJECT,
                    description="Transfer data for connected accounts",
                    required=False
                ),
                NodeParameter(
                    name="application_fee_amount",
                    type=NodeParameterType.NUMBER,
                    description="Application fee amount in cents",
                    required=False
                ),
                NodeParameter(
                    name="on_behalf_of",
                    type=NodeParameterType.STRING,
                    description="Connected account ID to act on behalf of",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "object": NodeParameterType.OBJECT,
                "objects": NodeParameterType.ARRAY,
                "id": NodeParameterType.STRING,
                "error": NodeParameterType.STRING,
                "count": NodeParameterType.NUMBER,
                "has_more": NodeParameterType.BOOLEAN,
                "url": NodeParameterType.STRING,
                "created": NodeParameterType.NUMBER,
                "livemode": NodeParameterType.BOOLEAN,
                "type": NodeParameterType.STRING,
                "data": NodeParameterType.ANY,
                "next_page": NodeParameterType.STRING,
                "previous_page": NodeParameterType.STRING
            },
            tags=["payment", "stripe", "billing", "subscription", "finance"],
            documentation_url="https://stripe.com/docs/api"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stripe-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
        
        if not params.get("api_key"):
            raise NodeValidationError("Stripe API key is required")
        
        # Validate API key format
        api_key = params.get("api_key")
        if not api_key.startswith(("sk_test_", "sk_live_")):
            raise NodeValidationError("Invalid Stripe API key format")
        
        # Operation-specific validations
        if operation == StripeOperation.CREATE_PAYMENT_INTENT:
            if params.get("amount") is None:
                raise NodeValidationError("Amount is required for creating payment intent")
            if params.get("amount") <= 0:
                raise NodeValidationError("Amount must be greater than 0")
                
        elif operation == StripeOperation.CREATE_CUSTOMER:
            # At least one identifier should be provided
            if not any([params.get("email"), params.get("name"), params.get("phone")]):
                raise NodeValidationError("At least one of email, name, or phone is required")
                
        elif operation == StripeOperation.CREATE_SUBSCRIPTION:
            if not params.get("customer"):
                raise NodeValidationError("Customer ID is required for creating subscription")
            if not params.get("items"):
                raise NodeValidationError("Items are required for creating subscription")
                
        elif operation in [
            StripeOperation.RETRIEVE_PAYMENT_INTENT,
            StripeOperation.UPDATE_PAYMENT_INTENT,
            StripeOperation.CONFIRM_PAYMENT_INTENT,
            StripeOperation.CAPTURE_PAYMENT_INTENT,
            StripeOperation.CANCEL_PAYMENT_INTENT
        ]:
            if not params.get("payment_intent_id"):
                raise NodeValidationError("Payment Intent ID is required")
                
        elif operation in [
            StripeOperation.RETRIEVE_CUSTOMER,
            StripeOperation.UPDATE_CUSTOMER,
            StripeOperation.DELETE_CUSTOMER
        ]:
            if not params.get("customer_id"):
                raise NodeValidationError("Customer ID is required")
                
        elif operation in [
            StripeOperation.RETRIEVE_SUBSCRIPTION,
            StripeOperation.UPDATE_SUBSCRIPTION,
            StripeOperation.CANCEL_SUBSCRIPTION
        ]:
            if not params.get("subscription_id"):
                raise NodeValidationError("Subscription ID is required")
                
        elif operation in [
            StripeOperation.RETRIEVE_INVOICE,
            StripeOperation.UPDATE_INVOICE,
            StripeOperation.FINALIZE_INVOICE,
            StripeOperation.PAY_INVOICE,
            StripeOperation.SEND_INVOICE,
            StripeOperation.VOID_INVOICE
        ]:
            if not params.get("invoice_id"):
                raise NodeValidationError("Invoice ID is required")
                
        elif operation in [
            StripeOperation.CREATE_REFUND
        ]:
            if not params.get("charge_id") and not params.get("payment_intent_id"):
                raise NodeValidationError("Either Charge ID or Payment Intent ID is required")
                
        elif operation == StripeOperation.CONSTRUCT_EVENT:
            if not params.get("payload"):
                raise NodeValidationError("Payload is required for constructing webhook event")
            if not params.get("sig_header"):
                raise NodeValidationError("Signature header is required for constructing webhook event")
            if not params.get("webhook_secret"):
                raise NodeValidationError("Webhook secret is required for constructing webhook event")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Stripe operation."""
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            # Set API key
            self.stripe.api_key = params.get("api_key")
            
            # Set Stripe account if provided
            stripe_account = params.get("stripe_account")
            
            # Set idempotency key if provided
            idempotency_key = params.get("idempotency_key")
            
            # Common request options
            request_options = {}
            if stripe_account:
                request_options["stripe_account"] = stripe_account
            if idempotency_key:
                request_options["idempotency_key"] = idempotency_key
            
            # Route to appropriate operation handler
            if operation == StripeOperation.CREATE_PAYMENT_INTENT:
                return await self._create_payment_intent(params, request_options)
            elif operation == StripeOperation.RETRIEVE_PAYMENT_INTENT:
                return await self._retrieve_payment_intent(params, request_options)
            elif operation == StripeOperation.UPDATE_PAYMENT_INTENT:
                return await self._update_payment_intent(params, request_options)
            elif operation == StripeOperation.CONFIRM_PAYMENT_INTENT:
                return await self._confirm_payment_intent(params, request_options)
            elif operation == StripeOperation.CAPTURE_PAYMENT_INTENT:
                return await self._capture_payment_intent(params, request_options)
            elif operation == StripeOperation.CANCEL_PAYMENT_INTENT:
                return await self._cancel_payment_intent(params, request_options)
            elif operation == StripeOperation.LIST_PAYMENT_INTENTS:
                return await self._list_payment_intents(params, request_options)
            elif operation == StripeOperation.SEARCH_PAYMENT_INTENTS:
                return await self._search_payment_intents(params, request_options)
                
            # Customer operations
            elif operation == StripeOperation.CREATE_CUSTOMER:
                return await self._create_customer(params, request_options)
            elif operation == StripeOperation.RETRIEVE_CUSTOMER:
                return await self._retrieve_customer(params, request_options)
            elif operation == StripeOperation.UPDATE_CUSTOMER:
                return await self._update_customer(params, request_options)
            elif operation == StripeOperation.DELETE_CUSTOMER:
                return await self._delete_customer(params, request_options)
            elif operation == StripeOperation.LIST_CUSTOMERS:
                return await self._list_customers(params, request_options)
            elif operation == StripeOperation.SEARCH_CUSTOMERS:
                return await self._search_customers(params, request_options)
                
            # Subscription operations
            elif operation == StripeOperation.CREATE_SUBSCRIPTION:
                return await self._create_subscription(params, request_options)
            elif operation == StripeOperation.RETRIEVE_SUBSCRIPTION:
                return await self._retrieve_subscription(params, request_options)
            elif operation == StripeOperation.UPDATE_SUBSCRIPTION:
                return await self._update_subscription(params, request_options)
            elif operation == StripeOperation.CANCEL_SUBSCRIPTION:
                return await self._cancel_subscription(params, request_options)
            elif operation == StripeOperation.LIST_SUBSCRIPTIONS:
                return await self._list_subscriptions(params, request_options)
            elif operation == StripeOperation.SEARCH_SUBSCRIPTIONS:
                return await self._search_subscriptions(params, request_options)
                
            # Invoice operations
            elif operation == StripeOperation.CREATE_INVOICE:
                return await self._create_invoice(params, request_options)
            elif operation == StripeOperation.RETRIEVE_INVOICE:
                return await self._retrieve_invoice(params, request_options)
            elif operation == StripeOperation.UPDATE_INVOICE:
                return await self._update_invoice(params, request_options)
            elif operation == StripeOperation.FINALIZE_INVOICE:
                return await self._finalize_invoice(params, request_options)
            elif operation == StripeOperation.PAY_INVOICE:
                return await self._pay_invoice(params, request_options)
            elif operation == StripeOperation.SEND_INVOICE:
                return await self._send_invoice(params, request_options)
            elif operation == StripeOperation.VOID_INVOICE:
                return await self._void_invoice(params, request_options)
            elif operation == StripeOperation.LIST_INVOICES:
                return await self._list_invoices(params, request_options)
                
            # Product operations
            elif operation == StripeOperation.CREATE_PRODUCT:
                return await self._create_product(params, request_options)
            elif operation == StripeOperation.RETRIEVE_PRODUCT:
                return await self._retrieve_product(params, request_options)
            elif operation == StripeOperation.UPDATE_PRODUCT:
                return await self._update_product(params, request_options)
            elif operation == StripeOperation.DELETE_PRODUCT:
                return await self._delete_product(params, request_options)
            elif operation == StripeOperation.LIST_PRODUCTS:
                return await self._list_products(params, request_options)
                
            # Price operations
            elif operation == StripeOperation.CREATE_PRICE:
                return await self._create_price(params, request_options)
            elif operation == StripeOperation.RETRIEVE_PRICE:
                return await self._retrieve_price(params, request_options)
            elif operation == StripeOperation.UPDATE_PRICE:
                return await self._update_price(params, request_options)
            elif operation == StripeOperation.LIST_PRICES:
                return await self._list_prices(params, request_options)
                
            # Charge operations
            elif operation == StripeOperation.CREATE_CHARGE:
                return await self._create_charge(params, request_options)
            elif operation == StripeOperation.RETRIEVE_CHARGE:
                return await self._retrieve_charge(params, request_options)
            elif operation == StripeOperation.UPDATE_CHARGE:
                return await self._update_charge(params, request_options)
            elif operation == StripeOperation.CAPTURE_CHARGE:
                return await self._capture_charge(params, request_options)
            elif operation == StripeOperation.LIST_CHARGES:
                return await self._list_charges(params, request_options)
                
            # Refund operations
            elif operation == StripeOperation.CREATE_REFUND:
                return await self._create_refund(params, request_options)
            elif operation == StripeOperation.RETRIEVE_REFUND:
                return await self._retrieve_refund(params, request_options)
            elif operation == StripeOperation.UPDATE_REFUND:
                return await self._update_refund(params, request_options)
            elif operation == StripeOperation.LIST_REFUNDS:
                return await self._list_refunds(params, request_options)
                
            # Balance operations
            elif operation == StripeOperation.RETRIEVE_BALANCE:
                return await self._retrieve_balance(params, request_options)
            elif operation == StripeOperation.LIST_BALANCE_TRANSACTIONS:
                return await self._list_balance_transactions(params, request_options)
                
            # Webhook operations
            elif operation == StripeOperation.CONSTRUCT_EVENT:
                return await self._construct_event(params)
                
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }
                
        except stripe.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "type": type(e).__name__,
                "code": getattr(e, "code", None),
                "param": getattr(e, "param", None),
                "stripe_error": True
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }
    
    # Payment Intent Methods
    async def _create_payment_intent(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new payment intent."""
        try:
            intent_params = {
                "amount": params.get("amount"),
                "currency": params.get("currency", "usd"),
            }
            
            # Add optional parameters
            optional_params = [
                "payment_method", "payment_method_types", "customer", 
                "description", "metadata", "setup_future_usage",
                "shipping", "statement_descriptor", "transfer_data",
                "application_fee_amount", "on_behalf_of", "capture_method",
                "confirm", "confirmation_method", "mandate", "mandate_data",
                "off_session", "payment_method_data", "payment_method_options",
                "receipt_email", "return_url", "use_stripe_sdk"
            ]
            
            for param in optional_params:
                if params.get(param) is not None:
                    intent_params[param] = params.get(param)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(**intent_params, **request_options)
            
            return {
                "status": "success",
                "object": intent.to_dict(),
                "id": intent.id,
                "type": "payment_intent",
                "livemode": intent.livemode,
                "created": intent.created
            }
            
        except Exception as e:
            raise e
    
    async def _retrieve_payment_intent(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a payment intent."""
        intent = stripe.PaymentIntent.retrieve(
            params.get("payment_intent_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": intent.to_dict(),
            "id": intent.id,
            "type": "payment_intent"
        }
    
    async def _update_payment_intent(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a payment intent."""
        intent = stripe.PaymentIntent.modify(
            params.get("payment_intent_id"),
            **self._filter_update_params(params),
            **request_options
        )
        
        return {
            "status": "success",
            "object": intent.to_dict(),
            "id": intent.id,
            "type": "payment_intent"
        }
    
    async def _confirm_payment_intent(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Confirm a payment intent."""
        confirm_params = {}
        optional_params = [
            "payment_method", "payment_method_data", "payment_method_options",
            "receipt_email", "setup_future_usage", "shipping",
            "mandate", "mandate_data", "return_url", "use_stripe_sdk",
            "off_session", "payment_method_types", "radar_options"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                confirm_params[param] = params.get(param)
        
        intent = stripe.PaymentIntent.confirm(
            params.get("payment_intent_id"),
            **confirm_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": intent.to_dict(),
            "id": intent.id,
            "type": "payment_intent",
            "requires_action": intent.status == "requires_action",
            "next_action": intent.next_action.to_dict() if intent.next_action else None
        }
    
    async def _capture_payment_intent(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a payment intent."""
        capture_params = {}
        if params.get("amount_to_capture"):
            capture_params["amount_to_capture"] = params.get("amount_to_capture")
        if params.get("application_fee_amount"):
            capture_params["application_fee_amount"] = params.get("application_fee_amount")
        if params.get("statement_descriptor"):
            capture_params["statement_descriptor"] = params.get("statement_descriptor")
        if params.get("metadata"):
            capture_params["metadata"] = params.get("metadata")
        if params.get("transfer_data"):
            capture_params["transfer_data"] = params.get("transfer_data")
        
        intent = stripe.PaymentIntent.capture(
            params.get("payment_intent_id"),
            **capture_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": intent.to_dict(),
            "id": intent.id,
            "type": "payment_intent"
        }
    
    async def _cancel_payment_intent(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a payment intent."""
        cancel_params = {}
        if params.get("cancellation_reason"):
            cancel_params["cancellation_reason"] = params.get("cancellation_reason")
        
        intent = stripe.PaymentIntent.cancel(
            params.get("payment_intent_id"),
            **cancel_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": intent.to_dict(),
            "id": intent.id,
            "type": "payment_intent"
        }
    
    async def _list_payment_intents(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List payment intents."""
        list_params = self._get_list_params(params)
        if params.get("customer"):
            list_params["customer"] = params.get("customer")
        if params.get("created"):
            list_params["created"] = params.get("created")
        
        intents = stripe.PaymentIntent.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [intent.to_dict() for intent in intents.data],
            "count": len(intents.data),
            "has_more": intents.has_more,
            "url": intents.url
        }
    
    async def _search_payment_intents(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Search payment intents."""
        search_params = {
            "query": params.get("query"),
            "limit": params.get("limit", 10),
            "page": params.get("page")
        }
        
        result = stripe.PaymentIntent.search(**search_params, **request_options)
        
        return {
            "status": "success",
            "objects": [intent.to_dict() for intent in result.data],
            "count": len(result.data),
            "has_more": result.has_more,
            "total_count": result.total_count,
            "url": result.url,
            "next_page": result.next_page
        }
    
    # Customer Methods
    async def _create_customer(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer."""
        customer_params = {}
        
        # Add customer fields
        fields = [
            "email", "name", "phone", "address", "shipping",
            "balance", "cash_balance", "coupon", "description",
            "invoice_prefix", "invoice_settings", "metadata",
            "next_invoice_sequence", "payment_method", "preferred_locales",
            "promotion_code", "source", "tax", "tax_exempt",
            "tax_id_data", "test_clock"
        ]
        
        for field in fields:
            if params.get(field) is not None:
                customer_params[field] = params.get(field)
        
        customer = stripe.Customer.create(**customer_params, **request_options)
        
        return {
            "status": "success",
            "object": customer.to_dict(),
            "id": customer.id,
            "type": "customer",
            "created": customer.created
        }
    
    async def _retrieve_customer(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a customer."""
        customer = stripe.Customer.retrieve(
            params.get("customer_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": customer.to_dict(),
            "id": customer.id,
            "type": "customer"
        }
    
    async def _update_customer(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer."""
        customer = stripe.Customer.modify(
            params.get("customer_id"),
            **self._filter_update_params(params, exclude=["customer_id"]),
            **request_options
        )
        
        return {
            "status": "success",
            "object": customer.to_dict(),
            "id": customer.id,
            "type": "customer"
        }
    
    async def _delete_customer(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a customer."""
        deletion = stripe.Customer.delete(
            params.get("customer_id"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": deletion.to_dict(),
            "id": deletion.id,
            "deleted": deletion.deleted
        }
    
    async def _list_customers(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List customers."""
        list_params = self._get_list_params(params)
        if params.get("email"):
            list_params["email"] = params.get("email")
        if params.get("created"):
            list_params["created"] = params.get("created")
        if params.get("test_clock"):
            list_params["test_clock"] = params.get("test_clock")
        
        customers = stripe.Customer.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [customer.to_dict() for customer in customers.data],
            "count": len(customers.data),
            "has_more": customers.has_more,
            "url": customers.url
        }
    
    async def _search_customers(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Search customers."""
        search_params = {
            "query": params.get("query"),
            "limit": params.get("limit", 10),
            "page": params.get("page")
        }
        
        result = stripe.Customer.search(**search_params, **request_options)
        
        return {
            "status": "success",
            "objects": [customer.to_dict() for customer in result.data],
            "count": len(result.data),
            "has_more": result.has_more,
            "total_count": result.total_count,
            "url": result.url,
            "next_page": result.next_page
        }
    
    # Subscription Methods
    async def _create_subscription(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new subscription."""
        sub_params = {
            "customer": params.get("customer"),
            "items": params.get("items")
        }
        
        # Add optional subscription parameters
        optional_params = [
            "add_invoice_items", "application_fee_percent", "automatic_tax",
            "backdate_start_date", "billing_cycle_anchor", "billing_thresholds",
            "cancel_at", "cancel_at_period_end", "collection_method",
            "coupon", "currency", "days_until_due", "default_payment_method",
            "default_source", "default_tax_rates", "description", "expand",
            "invoice_settings", "metadata", "off_session", "on_behalf_of",
            "payment_behavior", "payment_settings", "pending_invoice_item_interval",
            "promotion_code", "proration_behavior", "transfer_data",
            "trial_end", "trial_from_plan", "trial_period_days", "trial_settings"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                sub_params[param] = params.get(param)
        
        subscription = stripe.Subscription.create(**sub_params, **request_options)
        
        return {
            "status": "success",
            "object": subscription.to_dict(),
            "id": subscription.id,
            "type": "subscription",
            "created": subscription.created
        }
    
    async def _retrieve_subscription(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a subscription."""
        subscription = stripe.Subscription.retrieve(
            params.get("subscription_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": subscription.to_dict(),
            "id": subscription.id,
            "type": "subscription"
        }
    
    async def _update_subscription(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a subscription."""
        subscription = stripe.Subscription.modify(
            params.get("subscription_id"),
            **self._filter_update_params(params, exclude=["subscription_id"]),
            **request_options
        )
        
        return {
            "status": "success",
            "object": subscription.to_dict(),
            "id": subscription.id,
            "type": "subscription"
        }
    
    async def _cancel_subscription(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a subscription."""
        cancel_params = {}
        if params.get("invoice_now"):
            cancel_params["invoice_now"] = params.get("invoice_now")
        if params.get("prorate"):
            cancel_params["prorate"] = params.get("prorate")
        if params.get("cancellation_details"):
            cancel_params["cancellation_details"] = params.get("cancellation_details")
        
        subscription = stripe.Subscription.delete(
            params.get("subscription_id"),
            **cancel_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": subscription.to_dict(),
            "id": subscription.id,
            "type": "subscription",
            "canceled_at": subscription.canceled_at
        }
    
    async def _list_subscriptions(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List subscriptions."""
        list_params = self._get_list_params(params)
        
        # Add subscription-specific filters
        filter_params = [
            "collection_method", "created", "current_period_end",
            "current_period_start", "customer", "plan", "price",
            "status", "test_clock"
        ]
        
        for param in filter_params:
            if params.get(param) is not None:
                list_params[param] = params.get(param)
        
        subscriptions = stripe.Subscription.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [sub.to_dict() for sub in subscriptions.data],
            "count": len(subscriptions.data),
            "has_more": subscriptions.has_more,
            "url": subscriptions.url
        }
    
    async def _search_subscriptions(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Search subscriptions."""
        search_params = {
            "query": params.get("query"),
            "limit": params.get("limit", 10),
            "page": params.get("page")
        }
        
        result = stripe.Subscription.search(**search_params, **request_options)
        
        return {
            "status": "success",
            "objects": [sub.to_dict() for sub in result.data],
            "count": len(result.data),
            "has_more": result.has_more,
            "total_count": result.total_count,
            "url": result.url,
            "next_page": result.next_page
        }
    
    # Invoice Methods
    async def _create_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice."""
        invoice_params = {
            "customer": params.get("customer")
        }
        
        # Add optional invoice parameters
        optional_params = [
            "account_tax_ids", "application_fee_amount", "auto_advance",
            "automatic_tax", "collection_method", "currency", "custom_fields",
            "days_until_due", "default_payment_method", "default_source",
            "default_tax_rates", "description", "discounts", "due_date",
            "expand", "footer", "from_invoice", "issuer", "metadata",
            "on_behalf_of", "payment_settings", "pending_invoice_items_behavior",
            "rendering", "rendering_options", "shipping_cost", "shipping_details",
            "statement_descriptor", "subscription", "transfer_data"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                invoice_params[param] = params.get(param)
        
        invoice = stripe.Invoice.create(**invoice_params, **request_options)
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice",
            "created": invoice.created
        }
    
    async def _retrieve_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve an invoice."""
        invoice = stripe.Invoice.retrieve(
            params.get("invoice_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice"
        }
    
    async def _update_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update an invoice."""
        invoice = stripe.Invoice.modify(
            params.get("invoice_id"),
            **self._filter_update_params(params, exclude=["invoice_id"]),
            **request_options
        )
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice"
        }
    
    async def _finalize_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize an invoice."""
        finalize_params = {}
        if params.get("auto_advance"):
            finalize_params["auto_advance"] = params.get("auto_advance")
        
        invoice = stripe.Invoice.finalize_invoice(
            params.get("invoice_id"),
            **finalize_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice",
            "finalized_at": invoice.finalized_at
        }
    
    async def _pay_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Pay an invoice."""
        pay_params = {}
        optional_params = [
            "forgive", "mandate", "off_session", "paid_out_of_band",
            "payment_method", "source"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                pay_params[param] = params.get(param)
        
        invoice = stripe.Invoice.pay(
            params.get("invoice_id"),
            **pay_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice",
            "paid": invoice.paid,
            "payment_intent": invoice.payment_intent
        }
    
    async def _send_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Send an invoice."""
        invoice = stripe.Invoice.send_invoice(
            params.get("invoice_id"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice"
        }
    
    async def _void_invoice(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Void an invoice."""
        invoice = stripe.Invoice.void_invoice(
            params.get("invoice_id"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": invoice.to_dict(),
            "id": invoice.id,
            "type": "invoice",
            "voided_at": invoice.voided_at
        }
    
    async def _list_invoices(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List invoices."""
        list_params = self._get_list_params(params)
        
        # Add invoice-specific filters
        filter_params = [
            "collection_method", "created", "customer", "due_date",
            "status", "subscription"
        ]
        
        for param in filter_params:
            if params.get(param) is not None:
                list_params[param] = params.get(param)
        
        invoices = stripe.Invoice.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [invoice.to_dict() for invoice in invoices.data],
            "count": len(invoices.data),
            "has_more": invoices.has_more,
            "url": invoices.url
        }
    
    # Product Methods
    async def _create_product(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product."""
        product_params = {
            "name": params.get("name")
        }
        
        # Add optional product parameters
        optional_params = [
            "active", "attributes", "caption", "deactivate_on",
            "default_price_data", "description", "expand", "features",
            "id", "images", "metadata", "package_dimensions",
            "shippable", "statement_descriptor", "tax_code",
            "type", "unit_label", "url"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                product_params[param] = params.get(param)
        
        product = stripe.Product.create(**product_params, **request_options)
        
        return {
            "status": "success",
            "object": product.to_dict(),
            "id": product.id,
            "type": "product",
            "created": product.created
        }
    
    async def _retrieve_product(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a product."""
        product = stripe.Product.retrieve(
            params.get("product_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": product.to_dict(),
            "id": product.id,
            "type": "product"
        }
    
    async def _update_product(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product."""
        product = stripe.Product.modify(
            params.get("product_id"),
            **self._filter_update_params(params, exclude=["product_id"]),
            **request_options
        )
        
        return {
            "status": "success",
            "object": product.to_dict(),
            "id": product.id,
            "type": "product"
        }
    
    async def _delete_product(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a product."""
        deletion = stripe.Product.delete(
            params.get("product_id"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": deletion.to_dict(),
            "id": deletion.id,
            "deleted": deletion.deleted
        }
    
    async def _list_products(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List products."""
        list_params = self._get_list_params(params)
        
        # Add product-specific filters
        if params.get("active") is not None:
            list_params["active"] = params.get("active")
        if params.get("created"):
            list_params["created"] = params.get("created")
        if params.get("type"):
            list_params["type"] = params.get("type")
        if params.get("ids"):
            list_params["ids"] = params.get("ids")
        if params.get("shippable") is not None:
            list_params["shippable"] = params.get("shippable")
        if params.get("url"):
            list_params["url"] = params.get("url")
        
        products = stripe.Product.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [product.to_dict() for product in products.data],
            "count": len(products.data),
            "has_more": products.has_more,
            "url": products.url
        }
    
    # Price Methods
    async def _create_price(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new price."""
        price_params = {
            "currency": params.get("currency", "usd")
        }
        
        # Handle unit amount or unit amount decimal
        if params.get("unit_amount") is not None:
            price_params["unit_amount"] = params.get("unit_amount")
        elif params.get("unit_amount_decimal") is not None:
            price_params["unit_amount_decimal"] = params.get("unit_amount_decimal")
        
        # Handle product or product data
        if params.get("product"):
            price_params["product"] = params.get("product")
        elif params.get("product_data"):
            price_params["product_data"] = params.get("product_data")
        
        # Add optional price parameters
        optional_params = [
            "active", "billing_scheme", "currency_options", "custom_unit_amount",
            "expand", "lookup_key", "metadata", "nickname", "recurring",
            "tax_behavior", "tiers", "tiers_mode", "transfer_lookup_key",
            "transform_quantity"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                price_params[param] = params.get(param)
        
        price = stripe.Price.create(**price_params, **request_options)
        
        return {
            "status": "success",
            "object": price.to_dict(),
            "id": price.id,
            "type": "price",
            "created": price.created
        }
    
    async def _retrieve_price(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a price."""
        price = stripe.Price.retrieve(
            params.get("price_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": price.to_dict(),
            "id": price.id,
            "type": "price"
        }
    
    async def _update_price(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a price."""
        update_params = {}
        
        # Only certain fields can be updated on a price
        updatable_fields = [
            "active", "currency_options", "expand", "lookup_key",
            "metadata", "nickname", "tax_behavior", "transfer_lookup_key"
        ]
        
        for field in updatable_fields:
            if params.get(field) is not None:
                update_params[field] = params.get(field)
        
        price = stripe.Price.modify(
            params.get("price_id"),
            **update_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": price.to_dict(),
            "id": price.id,
            "type": "price"
        }
    
    async def _list_prices(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List prices."""
        list_params = self._get_list_params(params)
        
        # Add price-specific filters
        filter_params = [
            "active", "created", "currency", "lookup_keys",
            "product", "recurring", "type"
        ]
        
        for param in filter_params:
            if params.get(param) is not None:
                list_params[param] = params.get(param)
        
        prices = stripe.Price.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [price.to_dict() for price in prices.data],
            "count": len(prices.data),
            "has_more": prices.has_more,
            "url": prices.url
        }
    
    # Charge Methods (Legacy)
    async def _create_charge(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new charge (legacy, use Payment Intents instead)."""
        charge_params = {
            "amount": params.get("amount"),
            "currency": params.get("currency", "usd")
        }
        
        # Handle source
        if params.get("source"):
            charge_params["source"] = params.get("source")
        elif params.get("customer"):
            charge_params["customer"] = params.get("customer")
        
        # Add optional charge parameters
        optional_params = [
            "application_fee_amount", "capture", "description",
            "destination", "metadata", "on_behalf_of", "radar_options",
            "receipt_email", "shipping", "statement_descriptor",
            "statement_descriptor_suffix", "transfer_data", "transfer_group"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                charge_params[param] = params.get(param)
        
        charge = stripe.Charge.create(**charge_params, **request_options)
        
        return {
            "status": "success",
            "object": charge.to_dict(),
            "id": charge.id,
            "type": "charge",
            "created": charge.created
        }
    
    async def _retrieve_charge(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a charge."""
        charge = stripe.Charge.retrieve(
            params.get("charge_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": charge.to_dict(),
            "id": charge.id,
            "type": "charge"
        }
    
    async def _update_charge(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a charge."""
        charge = stripe.Charge.modify(
            params.get("charge_id"),
            **self._filter_update_params(params, exclude=["charge_id"]),
            **request_options
        )
        
        return {
            "status": "success",
            "object": charge.to_dict(),
            "id": charge.id,
            "type": "charge"
        }
    
    async def _capture_charge(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a charge."""
        capture_params = {}
        
        optional_params = [
            "amount", "application_fee_amount", "receipt_email",
            "statement_descriptor", "statement_descriptor_suffix",
            "transfer_data", "transfer_group"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                capture_params[param] = params.get(param)
        
        charge = stripe.Charge.capture(
            params.get("charge_id"),
            **capture_params,
            **request_options
        )
        
        return {
            "status": "success",
            "object": charge.to_dict(),
            "id": charge.id,
            "type": "charge",
            "captured": charge.captured
        }
    
    async def _list_charges(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List charges."""
        list_params = self._get_list_params(params)
        
        # Add charge-specific filters
        if params.get("created"):
            list_params["created"] = params.get("created")
        if params.get("customer"):
            list_params["customer"] = params.get("customer")
        if params.get("payment_intent"):
            list_params["payment_intent"] = params.get("payment_intent")
        if params.get("transfer_group"):
            list_params["transfer_group"] = params.get("transfer_group")
        
        charges = stripe.Charge.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [charge.to_dict() for charge in charges.data],
            "count": len(charges.data),
            "has_more": charges.has_more,
            "url": charges.url
        }
    
    # Refund Methods
    async def _create_refund(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new refund."""
        refund_params = {}
        
        # Handle charge or payment intent
        if params.get("charge_id"):
            refund_params["charge"] = params.get("charge_id")
        elif params.get("payment_intent_id"):
            refund_params["payment_intent"] = params.get("payment_intent_id")
        
        # Add optional refund parameters
        optional_params = [
            "amount", "currency", "customer", "instructions_email",
            "metadata", "origin", "reason", "refund_application_fee",
            "reverse_transfer"
        ]
        
        for param in optional_params:
            if params.get(param) is not None:
                refund_params[param] = params.get(param)
        
        refund = stripe.Refund.create(**refund_params, **request_options)
        
        return {
            "status": "success",
            "object": refund.to_dict(),
            "id": refund.id,
            "type": "refund",
            "created": refund.created
        }
    
    async def _retrieve_refund(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a refund."""
        refund = stripe.Refund.retrieve(
            params.get("refund_id"),
            expand=params.get("expand"),
            **request_options
        )
        
        return {
            "status": "success",
            "object": refund.to_dict(),
            "id": refund.id,
            "type": "refund"
        }
    
    async def _update_refund(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Update a refund."""
        refund = stripe.Refund.modify(
            params.get("refund_id"),
            **self._filter_update_params(params, exclude=["refund_id"]),
            **request_options
        )
        
        return {
            "status": "success",
            "object": refund.to_dict(),
            "id": refund.id,
            "type": "refund"
        }
    
    async def _list_refunds(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List refunds."""
        list_params = self._get_list_params(params)
        
        # Add refund-specific filters
        if params.get("charge"):
            list_params["charge"] = params.get("charge")
        if params.get("payment_intent"):
            list_params["payment_intent"] = params.get("payment_intent")
        if params.get("created"):
            list_params["created"] = params.get("created")
        
        refunds = stripe.Refund.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [refund.to_dict() for refund in refunds.data],
            "count": len(refunds.data),
            "has_more": refunds.has_more,
            "url": refunds.url
        }
    
    # Balance Methods
    async def _retrieve_balance(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve account balance."""
        balance = stripe.Balance.retrieve(**request_options)
        
        return {
            "status": "success",
            "object": balance.to_dict(),
            "type": "balance",
            "livemode": balance.livemode
        }
    
    async def _list_balance_transactions(self, params: Dict[str, Any], request_options: Dict[str, Any]) -> Dict[str, Any]:
        """List balance transactions."""
        list_params = self._get_list_params(params)
        
        # Add balance transaction filters
        filter_params = [
            "available_on", "created", "currency", "payout",
            "source", "type"
        ]
        
        for param in filter_params:
            if params.get(param) is not None:
                list_params[param] = params.get(param)
        
        transactions = stripe.BalanceTransaction.list(**list_params, **request_options)
        
        return {
            "status": "success",
            "objects": [txn.to_dict() for txn in transactions.data],
            "count": len(transactions.data),
            "has_more": transactions.has_more,
            "url": transactions.url
        }
    
    # Webhook Methods
    async def _construct_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Construct and verify a webhook event."""
        try:
            event = stripe.Webhook.construct_event(
                params.get("payload"),
                params.get("sig_header"),
                params.get("webhook_secret")
            )
            
            return {
                "status": "success",
                "object": event,
                "id": event.get("id"),
                "type": event.get("type"),
                "created": event.get("created"),
                "livemode": event.get("livemode"),
                "data": event.get("data")
            }
            
        except stripe.SignatureVerificationError as e:
            return {
                "status": "error",
                "error": "Invalid signature",
                "stripe_error": True,
                "type": "SignatureVerificationError"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }
    
    # Helper Methods
    def _get_list_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get common list parameters."""
        list_params = {
            "limit": params.get("limit", 10)
        }
        
        if params.get("starting_after"):
            list_params["starting_after"] = params.get("starting_after")
        if params.get("ending_before"):
            list_params["ending_before"] = params.get("ending_before")
        if params.get("expand"):
            list_params["expand"] = params.get("expand")
        
        return list_params
    
    def _filter_update_params(self, params: Dict[str, Any], exclude: List[str] = None) -> Dict[str, Any]:
        """Filter parameters for update operations."""
        if exclude is None:
            exclude = []
        
        # Common fields to exclude from updates
        exclude.extend([
            "operation", "api_key", "stripe_account", "idempotency_key"
        ])
        
        update_params = {}
        for key, value in params.items():
            if key not in exclude and value is not None:
                update_params[key] = value
        
        return update_params


class StripeHelpers:
    """Helper functions for Stripe operations."""
    
    @staticmethod
    def format_amount(amount: int, currency: str = "usd") -> str:
        """Format amount from cents to readable format."""
        # Most currencies use 2 decimal places
        decimal_currencies = ["usd", "eur", "gbp", "cad", "aud", "nzd"]
        zero_decimal_currencies = ["jpy", "krw", "vnd", "clp", "pyg", "xof"]
        
        if currency.lower() in zero_decimal_currencies:
            return f"{amount:,} {currency.upper()}"
        elif currency.lower() in decimal_currencies:
            return f"{amount/100:,.2f} {currency.upper()}"
        else:
            # Default to 2 decimal places
            return f"{amount/100:,.2f} {currency.upper()}"
    
    @staticmethod
    def construct_metadata(data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """Construct metadata dictionary with string values."""
        metadata = {}
        
        for key, value in data.items():
            meta_key = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Flatten nested dictionaries
                nested = StripeHelpers.construct_metadata(value, f"{meta_key}_")
                metadata.update(nested)
            elif isinstance(value, (list, tuple)):
                # Convert lists to comma-separated strings
                metadata[meta_key] = ",".join(str(v) for v in value)
            elif value is not None:
                # Convert to string
                metadata[meta_key] = str(value)
        
        return metadata
    
    @staticmethod
    def parse_webhook_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse webhook event for easier handling."""
        return {
            "id": event.get("id"),
            "type": event.get("type"),
            "created": event.get("created"),
            "livemode": event.get("livemode"),
            "object_type": event.get("data", {}).get("object", {}).get("object"),
            "object_id": event.get("data", {}).get("object", {}).get("id"),
            "object": event.get("data", {}).get("object", {}),
            "previous_attributes": event.get("data", {}).get("previous_attributes", {}),
            "request": event.get("request", {}),
            "pending_webhooks": event.get("pending_webhooks", 0)
        }
    
    @staticmethod
    def create_price_data(amount: int, currency: str = "usd", 
                         product_name: str = None, recurring: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create inline price data for checkout sessions."""
        price_data = {
            "unit_amount": amount,
            "currency": currency
        }
        
        if product_name:
            price_data["product_data"] = {"name": product_name}
        
        if recurring:
            price_data["recurring"] = recurring
        
        return price_data
    
    @staticmethod
    def create_line_item(price: str = None, quantity: int = 1, 
                        price_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a line item for checkout sessions."""
        line_item = {"quantity": quantity}
        
        if price:
            line_item["price"] = price
        elif price_data:
            line_item["price_data"] = price_data
        else:
            raise ValueError("Either price or price_data must be provided")
        
        return line_item
    
    @staticmethod
    def calculate_application_fee(amount: int, percentage: float) -> int:
        """Calculate application fee amount from percentage."""
        return int(amount * (percentage / 100))
    
    @staticmethod
    def verify_webhook_signature(payload: str, sig_header: str, 
                                webhook_secret: str) -> bool:
        """Verify webhook signature."""
        try:
            stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return True
        except stripe.SignatureVerificationError:
            return False
    
    @staticmethod
    def format_error_response(error: stripe.StripeError) -> Dict[str, Any]:
        """Format Stripe error for consistent response."""
        return {
            "status": "error",
            "error": str(error),
            "type": type(error).__name__,
            "code": getattr(error, "code", None),
            "param": getattr(error, "param", None),
            "doc_url": getattr(error, "doc_url", None),
            "request_id": getattr(error, "request_id", None),
            "stripe_error": True
        }