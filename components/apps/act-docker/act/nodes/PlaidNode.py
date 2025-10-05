"""
Plaid Node - Comprehensive integration with Plaid REST API
Provides access to all Plaid API operations including accounts, transactions, identity, assets, income, and financial data.
"""

import logging
import json
import asyncio
import time
import os
import ssl
import base64
import hashlib
import hmac
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
from urllib.parse import urlencode

# Import HTTP client for API calls
import aiohttp
import certifi

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

# Configure logging
logger = logging.getLogger(__name__)

class PlaidOperation:
    """Operations available on Plaid REST API."""
    
    # Link Token Management
    CREATE_LINK_TOKEN = "create_link_token"
    GET_LINK_TOKEN = "get_link_token"
    
    # Item Management
    EXCHANGE_PUBLIC_TOKEN = "exchange_public_token"
    CREATE_PUBLIC_TOKEN = "create_public_token"
    ROTATE_ACCESS_TOKEN = "rotate_access_token"
    GET_ITEM = "get_item"
    REMOVE_ITEM = "remove_item"
    UPDATE_ITEM_WEBHOOK = "update_item_webhook"
    INVALIDATE_ACCESS_TOKEN = "invalidate_access_token"
    
    # Account Information
    GET_ACCOUNTS = "get_accounts"
    GET_BALANCE = "get_balance"
    GET_IDENTITY = "get_identity"
    GET_AUTH = "get_auth"
    
    # Transactions
    GET_TRANSACTIONS = "get_transactions"
    GET_TRANSACTIONS_SYNC = "get_transactions_sync"
    REFRESH_TRANSACTIONS = "refresh_transactions"
    
    # Investments
    GET_INVESTMENTS_ACCOUNTS = "get_investments_accounts"
    GET_INVESTMENTS_HOLDINGS = "get_investments_holdings"
    GET_INVESTMENTS_TRANSACTIONS = "get_investments_transactions"
    REFRESH_INVESTMENTS = "refresh_investments"
    
    # Liabilities
    GET_LIABILITIES = "get_liabilities"
    
    # Assets
    CREATE_ASSET_REPORT = "create_asset_report"
    GET_ASSET_REPORT = "get_asset_report"
    GET_ASSET_REPORT_PDF = "get_asset_report_pdf"
    REMOVE_ASSET_REPORT = "remove_asset_report"
    CREATE_AUDIT_COPY = "create_audit_copy"
    REMOVE_AUDIT_COPY = "remove_audit_copy"
    REFRESH_ASSET_REPORT = "refresh_asset_report"
    FILTER_ASSET_REPORT = "filter_asset_report"
    
    # Income Verification
    CREATE_INCOME_VERIFICATION = "create_income_verification"
    GET_INCOME_VERIFICATION = "get_income_verification"
    REFRESH_INCOME_VERIFICATION = "refresh_income_verification"
    
    # Employment Verification
    GET_EMPLOYMENT = "get_employment"
    REFRESH_EMPLOYMENT = "refresh_employment"
    
    # Identity Verification
    CREATE_IDENTITY_VERIFICATION = "create_identity_verification"
    GET_IDENTITY_VERIFICATION = "get_identity_verification"
    LIST_IDENTITY_VERIFICATIONS = "list_identity_verifications"
    RETRY_IDENTITY_VERIFICATION = "retry_identity_verification"
    
    # Payment Initiation
    CREATE_PAYMENT_RECIPIENT = "create_payment_recipient"
    GET_PAYMENT_RECIPIENT = "get_payment_recipient"
    LIST_PAYMENT_RECIPIENTS = "list_payment_recipients"
    CREATE_PAYMENT = "create_payment"
    GET_PAYMENT = "get_payment"
    LIST_PAYMENTS = "list_payments"
    
    # Bank Transfer
    CREATE_BANK_TRANSFER = "create_bank_transfer"
    GET_BANK_TRANSFER = "get_bank_transfer"
    LIST_BANK_TRANSFERS = "list_bank_transfers"
    CANCEL_BANK_TRANSFER = "cancel_bank_transfer"
    
    # Transfer
    CREATE_TRANSFER = "create_transfer"
    GET_TRANSFER = "get_transfer"
    LIST_TRANSFERS = "list_transfers"
    CANCEL_TRANSFER = "cancel_transfer"
    CREATE_TRANSFER_AUTHORIZATION = "create_transfer_authorization"
    
    # Processor Token
    CREATE_PROCESSOR_TOKEN = "create_processor_token"
    
    # Institutions
    GET_INSTITUTIONS = "get_institutions"
    GET_INSTITUTION_BY_ID = "get_institution_by_id"
    SEARCH_INSTITUTIONS = "search_institutions"
    
    # Categories
    GET_CATEGORIES = "get_categories"
    
    # Sandbox
    SANDBOX_PUBLIC_TOKEN_CREATE = "sandbox_public_token_create"
    SANDBOX_ITEM_FIRE_WEBHOOK = "sandbox_item_fire_webhook"
    SANDBOX_ITEM_RESET_LOGIN = "sandbox_item_reset_login"
    SANDBOX_ITEM_SET_VERIFICATION_STATUS = "sandbox_item_set_verification_status"
    SANDBOX_BANK_TRANSFER_SIMULATE = "sandbox_bank_transfer_simulate"
    SANDBOX_TRANSFER_SIMULATE = "sandbox_transfer_simulate"
    SANDBOX_INCOME_FIRE_WEBHOOK = "sandbox_income_fire_webhook"
    
    # Webhooks
    WEBHOOK_VERIFICATION_KEY_GET = "webhook_verification_key_get"
    
    # Monitor
    BEACON_USER_CREATE = "beacon_user_create"
    BEACON_USER_GET = "beacon_user_get"
    BEACON_USER_HISTORY_LIST = "beacon_user_history_list"
    BEACON_DUPLICATE_GET = "beacon_duplicate_get"
    BEACON_REPORT_CREATE = "beacon_report_create"
    BEACON_REPORT_GET = "beacon_report_get"
    
    # Enrich
    ENRICH_TRANSACTIONS = "enrich_transactions"
    
    # Statements
    GET_STATEMENTS = "get_statements"
    DOWNLOAD_STATEMENTS = "download_statements"
    REFRESH_STATEMENTS = "refresh_statements"
    
    # Credit
    GET_CREDIT_AUDIT_COPY_TOKEN = "get_credit_audit_copy_token"
    CREATE_CREDIT_AUDIT_COPY_TOKEN = "create_credit_audit_copy_token"
    REMOVE_CREDIT_AUDIT_COPY_TOKEN = "remove_credit_audit_copy_token"

class PlaidEnvironment:
    """Plaid API environments."""
    SANDBOX = "sandbox"
    DEVELOPMENT = "development" 
    PRODUCTION = "production"

class PlaidHelper:
    """Helper class for Plaid API operations."""
    
    @staticmethod
    def get_environment_url(environment: str) -> str:
        """Get API URL for environment."""
        urls = {
            PlaidEnvironment.SANDBOX: "https://sandbox.plaid.com",
            PlaidEnvironment.DEVELOPMENT: "https://development.plaid.com",
            PlaidEnvironment.PRODUCTION: "https://production.plaid.com"
        }
        return urls.get(environment, urls[PlaidEnvironment.SANDBOX])
    
    @staticmethod
    def format_link_token_data(link_token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format link token data for API requests."""
        formatted = {}
        
        if 'user' in link_token_data:
            formatted['user'] = link_token_data['user']
        if 'client_name' in link_token_data:
            formatted['client_name'] = link_token_data['client_name']
        if 'products' in link_token_data:
            formatted['products'] = link_token_data['products']
        if 'country_codes' in link_token_data:
            formatted['country_codes'] = link_token_data['country_codes']
        if 'language' in link_token_data:
            formatted['language'] = link_token_data['language']
        if 'webhook' in link_token_data:
            formatted['webhook'] = link_token_data['webhook']
        if 'link_customization_name' in link_token_data:
            formatted['link_customization_name'] = link_token_data['link_customization_name']
        if 'account_filters' in link_token_data:
            formatted['account_filters'] = link_token_data['account_filters']
        if 'access_token' in link_token_data:
            formatted['access_token'] = link_token_data['access_token']
        if 'redirect_uri' in link_token_data:
            formatted['redirect_uri'] = link_token_data['redirect_uri']
        if 'android_package_name' in link_token_data:
            formatted['android_package_name'] = link_token_data['android_package_name']
        if 'institution_id' in link_token_data:
            formatted['institution_id'] = link_token_data['institution_id']
        if 'payment_initiation' in link_token_data:
            formatted['payment_initiation'] = link_token_data['payment_initiation']
        if 'deposit_switch' in link_token_data:
            formatted['deposit_switch'] = link_token_data['deposit_switch']
        if 'income_verification' in link_token_data:
            formatted['income_verification'] = link_token_data['income_verification']
        if 'identity_verification' in link_token_data:
            formatted['identity_verification'] = link_token_data['identity_verification']
        if 'auth' in link_token_data:
            formatted['auth'] = link_token_data['auth']
        if 'transfer' in link_token_data:
            formatted['transfer'] = link_token_data['transfer']
        if 'update' in link_token_data:
            formatted['update'] = link_token_data['update']
        if 'eu_config' in link_token_data:
            formatted['eu_config'] = link_token_data['eu_config']
        if 'user_token' in link_token_data:
            formatted['user_token'] = link_token_data['user_token']
            
        return formatted
    
    @staticmethod
    def format_asset_report_data(asset_report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format asset report data for API requests."""
        formatted = {}
        
        if 'access_tokens' in asset_report_data:
            formatted['access_tokens'] = asset_report_data['access_tokens']
        if 'days_requested' in asset_report_data:
            formatted['days_requested'] = asset_report_data['days_requested']
        if 'options' in asset_report_data:
            formatted['options'] = asset_report_data['options']
        if 'user' in asset_report_data:
            formatted['user'] = asset_report_data['user']
            
        return formatted
    
    @staticmethod
    def format_transfer_data(transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format transfer data for API requests."""
        formatted = {}
        
        if 'access_token' in transfer_data:
            formatted['access_token'] = transfer_data['access_token']
        if 'account_id' in transfer_data:
            formatted['account_id'] = transfer_data['account_id']
        if 'authorization_id' in transfer_data:
            formatted['authorization_id'] = transfer_data['authorization_id']
        if 'type' in transfer_data:
            formatted['type'] = transfer_data['type']
        if 'network' in transfer_data:
            formatted['network'] = transfer_data['network']
        if 'amount' in transfer_data:
            formatted['amount'] = transfer_data['amount']
        if 'description' in transfer_data:
            formatted['description'] = transfer_data['description']
        if 'ach_class' in transfer_data:
            formatted['ach_class'] = transfer_data['ach_class']
        if 'user' in transfer_data:
            formatted['user'] = transfer_data['user']
        if 'metadata' in transfer_data:
            formatted['metadata'] = transfer_data['metadata']
        if 'origination_account_id' in transfer_data:
            formatted['origination_account_id'] = transfer_data['origination_account_id']
        if 'iso_currency_code' in transfer_data:
            formatted['iso_currency_code'] = transfer_data['iso_currency_code']
            
        return formatted
    
    @staticmethod
    def format_payment_data(payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format payment initiation data for API requests."""
        formatted = {}
        
        if 'recipient_id' in payment_data:
            formatted['recipient_id'] = payment_data['recipient_id']
        if 'reference' in payment_data:
            formatted['reference'] = payment_data['reference']
        if 'amount' in payment_data:
            formatted['amount'] = payment_data['amount']
        if 'schedule' in payment_data:
            formatted['schedule'] = payment_data['schedule']
        if 'options' in payment_data:
            formatted['options'] = payment_data['options']
            
        return formatted
    
    @staticmethod
    def format_identity_verification_data(identity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format identity verification data for API requests."""
        formatted = {}
        
        if 'template_id' in identity_data:
            formatted['template_id'] = identity_data['template_id']
        if 'gave_consent' in identity_data:
            formatted['gave_consent'] = identity_data['gave_consent']
        if 'user' in identity_data:
            formatted['user'] = identity_data['user']
        if 'is_shareable' in identity_data:
            formatted['is_shareable'] = identity_data['is_shareable']
        if 'is_idempotent' in identity_data:
            formatted['is_idempotent'] = identity_data['is_idempotent']
            
        return formatted
    
    @staticmethod
    def build_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, str]:
        """Build date range for transaction queries."""
        date_range = {}
        
        if start_date:
            date_range['start_date'] = start_date
        if end_date:
            date_range['end_date'] = end_date
            
        return date_range
    
    @staticmethod
    def validate_webhook_signature(body: str, signature: str, key: str) -> bool:
        """Validate webhook signature from Plaid."""
        try:
            expected_signature = base64.b64encode(
                hmac.new(
                    key.encode('utf-8'),
                    body.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

class PlaidNode(BaseNode):
    """
    Plaid Node for comprehensive API integration.
    
    Provides access to all Plaid API operations including accounts, transactions,
    identity, assets, income verification, payment initiation, and financial data.
    """

    def __init__(self):
        super().__init__()
        self.session = None
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = 0

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="plaid",
            description="Comprehensive Plaid API integration for financial data and services",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The Plaid operation to perform",
                    required=True,
                    options=[
                        # Link Token Management
                        PlaidOperation.CREATE_LINK_TOKEN,
                        PlaidOperation.GET_LINK_TOKEN,
                        
                        # Item Management
                        PlaidOperation.EXCHANGE_PUBLIC_TOKEN,
                        PlaidOperation.CREATE_PUBLIC_TOKEN,
                        PlaidOperation.ROTATE_ACCESS_TOKEN,
                        PlaidOperation.GET_ITEM,
                        PlaidOperation.REMOVE_ITEM,
                        PlaidOperation.UPDATE_ITEM_WEBHOOK,
                        PlaidOperation.INVALIDATE_ACCESS_TOKEN,
                        
                        # Account Information
                        PlaidOperation.GET_ACCOUNTS,
                        PlaidOperation.GET_BALANCE,
                        PlaidOperation.GET_IDENTITY,
                        PlaidOperation.GET_AUTH,
                        
                        # Transactions
                        PlaidOperation.GET_TRANSACTIONS,
                        PlaidOperation.GET_TRANSACTIONS_SYNC,
                        PlaidOperation.REFRESH_TRANSACTIONS,
                        
                        # Investments
                        PlaidOperation.GET_INVESTMENTS_ACCOUNTS,
                        PlaidOperation.GET_INVESTMENTS_HOLDINGS,
                        PlaidOperation.GET_INVESTMENTS_TRANSACTIONS,
                        PlaidOperation.REFRESH_INVESTMENTS,
                        
                        # Liabilities
                        PlaidOperation.GET_LIABILITIES,
                        
                        # Assets
                        PlaidOperation.CREATE_ASSET_REPORT,
                        PlaidOperation.GET_ASSET_REPORT,
                        PlaidOperation.GET_ASSET_REPORT_PDF,
                        PlaidOperation.REMOVE_ASSET_REPORT,
                        PlaidOperation.CREATE_AUDIT_COPY,
                        PlaidOperation.REMOVE_AUDIT_COPY,
                        PlaidOperation.REFRESH_ASSET_REPORT,
                        PlaidOperation.FILTER_ASSET_REPORT,
                        
                        # Income Verification
                        PlaidOperation.CREATE_INCOME_VERIFICATION,
                        PlaidOperation.GET_INCOME_VERIFICATION,
                        PlaidOperation.REFRESH_INCOME_VERIFICATION,
                        
                        # Employment Verification
                        PlaidOperation.GET_EMPLOYMENT,
                        PlaidOperation.REFRESH_EMPLOYMENT,
                        
                        # Identity Verification
                        PlaidOperation.CREATE_IDENTITY_VERIFICATION,
                        PlaidOperation.GET_IDENTITY_VERIFICATION,
                        PlaidOperation.LIST_IDENTITY_VERIFICATIONS,
                        PlaidOperation.RETRY_IDENTITY_VERIFICATION,
                        
                        # Payment Initiation
                        PlaidOperation.CREATE_PAYMENT_RECIPIENT,
                        PlaidOperation.GET_PAYMENT_RECIPIENT,
                        PlaidOperation.LIST_PAYMENT_RECIPIENTS,
                        PlaidOperation.CREATE_PAYMENT,
                        PlaidOperation.GET_PAYMENT,
                        PlaidOperation.LIST_PAYMENTS,
                        
                        # Bank Transfer
                        PlaidOperation.CREATE_BANK_TRANSFER,
                        PlaidOperation.GET_BANK_TRANSFER,
                        PlaidOperation.LIST_BANK_TRANSFERS,
                        PlaidOperation.CANCEL_BANK_TRANSFER,
                        
                        # Transfer
                        PlaidOperation.CREATE_TRANSFER,
                        PlaidOperation.GET_TRANSFER,
                        PlaidOperation.LIST_TRANSFERS,
                        PlaidOperation.CANCEL_TRANSFER,
                        PlaidOperation.CREATE_TRANSFER_AUTHORIZATION,
                        
                        # Processor Token
                        PlaidOperation.CREATE_PROCESSOR_TOKEN,
                        
                        # Institutions
                        PlaidOperation.GET_INSTITUTIONS,
                        PlaidOperation.GET_INSTITUTION_BY_ID,
                        PlaidOperation.SEARCH_INSTITUTIONS,
                        
                        # Categories
                        PlaidOperation.GET_CATEGORIES,
                        
                        # Sandbox
                        PlaidOperation.SANDBOX_PUBLIC_TOKEN_CREATE,
                        PlaidOperation.SANDBOX_ITEM_FIRE_WEBHOOK,
                        PlaidOperation.SANDBOX_ITEM_RESET_LOGIN,
                        PlaidOperation.SANDBOX_ITEM_SET_VERIFICATION_STATUS,
                        PlaidOperation.SANDBOX_BANK_TRANSFER_SIMULATE,
                        PlaidOperation.SANDBOX_TRANSFER_SIMULATE,
                        PlaidOperation.SANDBOX_INCOME_FIRE_WEBHOOK,
                        
                        # Webhooks
                        PlaidOperation.WEBHOOK_VERIFICATION_KEY_GET,
                        
                        # Monitor
                        PlaidOperation.BEACON_USER_CREATE,
                        PlaidOperation.BEACON_USER_GET,
                        PlaidOperation.BEACON_USER_HISTORY_LIST,
                        PlaidOperation.BEACON_DUPLICATE_GET,
                        PlaidOperation.BEACON_REPORT_CREATE,
                        PlaidOperation.BEACON_REPORT_GET,
                        
                        # Enrich
                        PlaidOperation.ENRICH_TRANSACTIONS,
                        
                        # Statements
                        PlaidOperation.GET_STATEMENTS,
                        PlaidOperation.DOWNLOAD_STATEMENTS,
                        PlaidOperation.REFRESH_STATEMENTS,
                        
                        # Credit
                        PlaidOperation.GET_CREDIT_AUDIT_COPY_TOKEN,
                        PlaidOperation.CREATE_CREDIT_AUDIT_COPY_TOKEN,
                        PlaidOperation.REMOVE_CREDIT_AUDIT_COPY_TOKEN
                    ]
                ),
                NodeParameter(
                    name="environment",
                    type=NodeParameterType.STRING,
                    description="Plaid environment",
                    required=True,
                    default=PlaidEnvironment.SANDBOX,
                    options=[PlaidEnvironment.SANDBOX, PlaidEnvironment.DEVELOPMENT, PlaidEnvironment.PRODUCTION]
                ),
                NodeParameter(
                    name="client_id",
                    type=NodeParameterType.STRING,
                    description="Plaid Client ID",
                    required=True
                ),
                NodeParameter(
                    name="secret",
                    type=NodeParameterType.STRING,
                    description="Plaid Secret",
                    required=True,
                    sensitive=True
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.STRING,
                    description="Plaid access token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="public_token",
                    type=NodeParameterType.STRING,
                    description="Plaid public token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="link_token",
                    type=NodeParameterType.STRING,
                    description="Plaid link token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="item_id",
                    type=NodeParameterType.STRING,
                    description="Plaid Item ID",
                    required=False
                ),
                NodeParameter(
                    name="account_id",
                    type=NodeParameterType.STRING,
                    description="Account ID",
                    required=False
                ),
                NodeParameter(
                    name="institution_id",
                    type=NodeParameterType.STRING,
                    description="Institution ID",
                    required=False
                ),
                NodeParameter(
                    name="asset_report_token",
                    type=NodeParameterType.STRING,
                    description="Asset Report Token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="audit_copy_token",
                    type=NodeParameterType.STRING,
                    description="Audit Copy Token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="income_verification_id",
                    type=NodeParameterType.STRING,
                    description="Income Verification ID",
                    required=False
                ),
                NodeParameter(
                    name="identity_verification_id",
                    type=NodeParameterType.STRING,
                    description="Identity Verification ID",
                    required=False
                ),
                NodeParameter(
                    name="payment_id",
                    type=NodeParameterType.STRING,
                    description="Payment ID",
                    required=False
                ),
                NodeParameter(
                    name="payment_recipient_id",
                    type=NodeParameterType.STRING,
                    description="Payment Recipient ID",
                    required=False
                ),
                NodeParameter(
                    name="transfer_id",
                    type=NodeParameterType.STRING,
                    description="Transfer ID",
                    required=False
                ),
                NodeParameter(
                    name="bank_transfer_id",
                    type=NodeParameterType.STRING,
                    description="Bank Transfer ID",
                    required=False
                ),
                NodeParameter(
                    name="processor_token",
                    type=NodeParameterType.STRING,
                    description="Processor Token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="beacon_user_id",
                    type=NodeParameterType.STRING,
                    description="Beacon User ID",
                    required=False
                ),
                NodeParameter(
                    name="beacon_report_id",
                    type=NodeParameterType.STRING,
                    description="Beacon Report ID",
                    required=False
                ),
                NodeParameter(
                    name="user_token",
                    type=NodeParameterType.STRING,
                    description="User Token",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="link_token_data",
                    type=NodeParameterType.OBJECT,
                    description="Link token creation data",
                    required=False
                ),
                NodeParameter(
                    name="asset_report_data",
                    type=NodeParameterType.OBJECT,
                    description="Asset report data for creation",
                    required=False
                ),
                NodeParameter(
                    name="transfer_data",
                    type=NodeParameterType.OBJECT,
                    description="Transfer data for creation",
                    required=False
                ),
                NodeParameter(
                    name="payment_data",
                    type=NodeParameterType.OBJECT,
                    description="Payment data for creation",
                    required=False
                ),
                NodeParameter(
                    name="identity_verification_data",
                    type=NodeParameterType.OBJECT,
                    description="Identity verification data",
                    required=False
                ),
                NodeParameter(
                    name="recipient_data",
                    type=NodeParameterType.OBJECT,
                    description="Payment recipient data",
                    required=False
                ),
                NodeParameter(
                    name="webhook_data",
                    type=NodeParameterType.OBJECT,
                    description="Webhook configuration data",
                    required=False
                ),
                NodeParameter(
                    name="enrich_data",
                    type=NodeParameterType.OBJECT,
                    description="Transaction enrichment data",
                    required=False
                ),
                NodeParameter(
                    name="beacon_user_data",
                    type=NodeParameterType.OBJECT,
                    description="Beacon user data",
                    required=False
                ),
                NodeParameter(
                    name="products",
                    type=NodeParameterType.ARRAY,
                    description="Plaid products to use (transactions, auth, identity, etc.)",
                    required=False
                ),
                NodeParameter(
                    name="country_codes",
                    type=NodeParameterType.ARRAY,
                    description="Country codes for institutions",
                    required=False
                ),
                NodeParameter(
                    name="account_ids",
                    type=NodeParameterType.ARRAY,
                    description="List of account IDs",
                    required=False
                ),
                NodeParameter(
                    name="access_tokens",
                    type=NodeParameterType.ARRAY,
                    description="List of access tokens",
                    required=False
                ),
                NodeParameter(
                    name="start_date",
                    type=NodeParameterType.STRING,
                    description="Start date for transactions (YYYY-MM-DD)",
                    required=False
                ),
                NodeParameter(
                    name="end_date",
                    type=NodeParameterType.STRING,
                    description="End date for transactions (YYYY-MM-DD)",
                    required=False
                ),
                NodeParameter(
                    name="count",
                    type=NodeParameterType.INTEGER,
                    description="Number of transactions to return",
                    required=False,
                    default=100
                ),
                NodeParameter(
                    name="offset",
                    type=NodeParameterType.INTEGER,
                    description="Number of transactions to skip",
                    required=False,
                    default=0
                ),
                NodeParameter(
                    name="cursor",
                    type=NodeParameterType.STRING,
                    description="Cursor for pagination",
                    required=False
                ),
                NodeParameter(
                    name="days_requested",
                    type=NodeParameterType.INTEGER,
                    description="Number of days for asset report",
                    required=False,
                    default=365
                ),
                NodeParameter(
                    name="webhook_type",
                    type=NodeParameterType.STRING,
                    description="Webhook type to fire in sandbox",
                    required=False
                ),
                NodeParameter(
                    name="webhook_code",
                    type=NodeParameterType.STRING,
                    description="Webhook code to fire in sandbox",
                    required=False
                ),
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query for institutions",
                    required=False
                ),
                NodeParameter(
                    name="language",
                    type=NodeParameterType.STRING,
                    description="Language for Link",
                    required=False,
                    default="en"
                ),
                NodeParameter(
                    name="client_name",
                    type=NodeParameterType.STRING,
                    description="Client name for Link",
                    required=False
                ),
                NodeParameter(
                    name="user_data",
                    type=NodeParameterType.OBJECT,
                    description="User data for Link token",
                    required=False
                ),
                NodeParameter(
                    name="options",
                    type=NodeParameterType.OBJECT,
                    description="Additional options for operations",
                    required=False
                ),
                NodeParameter(
                    name="webhook_url",
                    type=NodeParameterType.STRING,
                    description="Webhook URL",
                    required=False
                ),
                NodeParameter(
                    name="webhook_signature",
                    type=NodeParameterType.STRING,
                    description="Webhook signature to validate",
                    required=False
                ),
                NodeParameter(
                    name="webhook_payload",
                    type=NodeParameterType.STRING,
                    description="Webhook payload to validate",
                    required=False
                ),
                NodeParameter(
                    name="webhook_key",
                    type=NodeParameterType.STRING,
                    description="Webhook verification key",
                    required=False,
                    sensitive=True
                ),
                NodeParameter(
                    name="timeout",
                    type=NodeParameterType.INTEGER,
                    description="Request timeout in seconds",
                    required=False,
                    default=30
                ),
                NodeParameter(
                    name="retry_attempts",
                    type=NodeParameterType.INTEGER,
                    description="Number of retry attempts for failed requests",
                    required=False,
                    default=3
                ),
                NodeParameter(
                    name="additional_headers",
                    type=NodeParameterType.OBJECT,
                    description="Additional HTTP headers",
                    required=False
                )
            ],
            outputs=[
                "success",
                "error",
                "response_data",
                "status_code",
                "access_token",
                "link_token",
                "item_id",
                "account_id",
                "asset_report_token",
                "transfer_id",
                "payment_id",
                "rate_limit_remaining",
                "rate_limit_reset"
            ],
            metadata={
                "category": "financial_services",
                "vendor": "plaid",
                "api_version": "2020-09-14",
                "documentation": "https://plaid.com/docs/api/",
                "rate_limits": {
                    "requests_per_second": 50,
                    "varies_by_endpoint": True
                }
            }
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with SSL context."""
        if self.session is None or self.session.closed:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self.session

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers

    async def _handle_rate_limiting(self, response: aiohttp.ClientResponse):
        """Handle rate limiting based on response headers."""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
        
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            await asyncio.sleep(retry_after)

    async def _make_request(
        self,
        endpoint: str,
        client_id: str,
        secret: str,
        environment: str,
        data: Dict[str, Any],
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_attempts: int = 3
    ) -> Tuple[Dict[str, Any], int]:
        """Make HTTP request to Plaid API with retries and error handling."""
        
        session = await self._get_session()
        base_url = PlaidHelper.get_environment_url(environment)
        url = f"{base_url}{endpoint}"
        headers = self._get_headers(additional_headers)
        
        # Add client credentials to data
        request_data = data.copy()
        request_data['client_id'] = client_id
        request_data['secret'] = secret
        
        for attempt in range(retry_attempts + 1):
            try:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    await self._handle_rate_limiting(response)
                    
                    if response.status == 429 and attempt < retry_attempts:
                        continue
                    
                    response_text = await response.text()
                    
                    try:
                        if response_text:
                            response_data = json.loads(response_text)
                        else:
                            response_data = {}
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    return response_data, response.status
                    
            except asyncio.TimeoutError:
                if attempt < retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NodeValidationError(f"Request timeout after {timeout} seconds")
            except Exception as e:
                if attempt < retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise NodeValidationError(f"Request failed: {str(e)}")
        
        raise NodeValidationError("All retry attempts failed")

    # Link Token Methods
    async def _create_link_token(self, link_token_data: Dict[str, Any], client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Create a link token."""
        formatted_data = PlaidHelper.format_link_token_data(link_token_data)
        
        response_data, status_code = await self._make_request(
            endpoint="/link/token/create",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_link_token(self, link_token: str, client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Get link token details."""
        data = {
            "link_token": link_token
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/link/token/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Item Methods
    async def _exchange_public_token(self, public_token: str, client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Exchange public token for access token."""
        data = {
            "public_token": public_token
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/item/public_token/exchange",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_item(self, access_token: str, client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Get item information."""
        data = {
            "access_token": access_token
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/item/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _remove_item(self, access_token: str, client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Remove an item."""
        data = {
            "access_token": access_token
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/item/remove",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Account Methods
    async def _get_accounts(self, access_token: str, client_id: str, secret: str, environment: str, account_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get account information."""
        data = {
            "access_token": access_token
        }
        
        if account_ids:
            data["options"] = {"account_ids": account_ids}
        
        response_data, status_code = await self._make_request(
            endpoint="/accounts/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_balance(self, access_token: str, client_id: str, secret: str, environment: str, account_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get account balances."""
        data = {
            "access_token": access_token
        }
        
        if account_ids:
            data["options"] = {"account_ids": account_ids}
        
        response_data, status_code = await self._make_request(
            endpoint="/accounts/balance/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_identity(self, access_token: str, client_id: str, secret: str, environment: str, account_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get identity information."""
        data = {
            "access_token": access_token
        }
        
        if account_ids:
            data["options"] = {"account_ids": account_ids}
        
        response_data, status_code = await self._make_request(
            endpoint="/identity/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_auth(self, access_token: str, client_id: str, secret: str, environment: str, account_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get auth information."""
        data = {
            "access_token": access_token
        }
        
        if account_ids:
            data["options"] = {"account_ids": account_ids}
        
        response_data, status_code = await self._make_request(
            endpoint="/auth/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Transaction Methods
    async def _get_transactions(self, access_token: str, start_date: str, end_date: str, client_id: str, secret: str, environment: str, account_ids: Optional[List[str]] = None, count: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get transactions."""
        data = {
            "access_token": access_token,
            "start_date": start_date,
            "end_date": end_date,
            "options": {
                "count": count,
                "offset": offset
            }
        }
        
        if account_ids:
            data["options"]["account_ids"] = account_ids
        
        response_data, status_code = await self._make_request(
            endpoint="/transactions/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_transactions_sync(self, access_token: str, client_id: str, secret: str, environment: str, cursor: Optional[str] = None, count: int = 100) -> Dict[str, Any]:
        """Get transactions using sync API."""
        data = {
            "access_token": access_token,
            "options": {
                "count": count
            }
        }
        
        if cursor:
            data["cursor"] = cursor
        
        response_data, status_code = await self._make_request(
            endpoint="/transactions/sync",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Asset Report Methods
    async def _create_asset_report(self, asset_report_data: Dict[str, Any], client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Create an asset report."""
        formatted_data = PlaidHelper.format_asset_report_data(asset_report_data)
        
        response_data, status_code = await self._make_request(
            endpoint="/asset_report/create",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_asset_report(self, asset_report_token: str, client_id: str, secret: str, environment: str, include_insights: bool = False) -> Dict[str, Any]:
        """Get an asset report."""
        data = {
            "asset_report_token": asset_report_token,
            "include_insights": include_insights
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/asset_report/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Transfer Methods
    async def _create_transfer(self, transfer_data: Dict[str, Any], client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Create a transfer."""
        formatted_data = PlaidHelper.format_transfer_data(transfer_data)
        
        response_data, status_code = await self._make_request(
            endpoint="/transfer/create",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=formatted_data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_transfer(self, transfer_id: str, client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Get a transfer."""
        data = {
            "transfer_id": transfer_id
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/transfer/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Institution Methods
    async def _get_institutions(self, count: int, offset: int, country_codes: List[str], client_id: str, secret: str, environment: str, products: Optional[List[str]] = None, routing_numbers: Optional[List[str]] = None, oauth: bool = False, include_optional_metadata: bool = False, include_auth_metadata: bool = False, include_payment_initiation_metadata: bool = False) -> Dict[str, Any]:
        """Get institutions."""
        data = {
            "count": count,
            "offset": offset,
            "country_codes": country_codes,
            "options": {
                "products": products or [],
                "routing_numbers": routing_numbers or [],
                "oauth": oauth,
                "include_optional_metadata": include_optional_metadata,
                "include_auth_metadata": include_auth_metadata,
                "include_payment_initiation_metadata": include_payment_initiation_metadata
            }
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/institutions/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _get_institution_by_id(self, institution_id: str, country_codes: List[str], client_id: str, secret: str, environment: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get institution by ID."""
        data = {
            "institution_id": institution_id,
            "country_codes": country_codes
        }
        
        if options:
            data["options"] = options
        
        response_data, status_code = await self._make_request(
            endpoint="/institutions/get_by_id",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Sandbox Methods
    async def _sandbox_public_token_create(self, institution_id: str, initial_products: List[str], client_id: str, secret: str, environment: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a sandbox public token."""
        data = {
            "institution_id": institution_id,
            "initial_products": initial_products
        }
        
        if options:
            data["options"] = options
        
        response_data, status_code = await self._make_request(
            endpoint="/sandbox/public_token/create",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    async def _sandbox_item_fire_webhook(self, access_token: str, webhook_code: str, client_id: str, secret: str, environment: str, webhook_type: Optional[str] = None) -> Dict[str, Any]:
        """Fire a webhook in sandbox."""
        data = {
            "access_token": access_token,
            "webhook_code": webhook_code
        }
        
        if webhook_type:
            data["webhook_type"] = webhook_type
        
        response_data, status_code = await self._make_request(
            endpoint="/sandbox/item/fire_webhook",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Webhook Methods
    async def _webhook_verification_key_get(self, key_id: str, client_id: str, secret: str, environment: str) -> Dict[str, Any]:
        """Get webhook verification key."""
        data = {
            "key_id": key_id
        }
        
        response_data, status_code = await self._make_request(
            endpoint="/webhook_verification_key/get",
            client_id=client_id,
            secret=secret,
            environment=environment,
            data=data
        )
        
        return {"response": response_data, "status_code": status_code}

    # Validation Methods
    async def _validate_webhook(self, webhook_payload: str, webhook_signature: str, webhook_key: str) -> Dict[str, Any]:
        """Validate webhook signature."""
        is_valid = PlaidHelper.validate_webhook_signature(
            webhook_payload, webhook_signature, webhook_key
        )
        
        return {
            "response": {"valid": is_valid},
            "status_code": 200 if is_valid else 401
        }

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Plaid operation."""
        try:
            # Validate required parameters
            operation = parameters.get("operation")
            if not operation:
                raise NodeValidationError("Operation is required")

            environment = parameters.get("environment", PlaidEnvironment.SANDBOX)
            client_id = parameters.get("client_id")
            secret = parameters.get("secret")
            
            if not client_id or not secret:
                raise NodeValidationError("Client ID and secret are required")

            timeout = parameters.get("timeout", 30)
            retry_attempts = parameters.get("retry_attempts", 3)

            # Execute the operation
            result = None
            
            # Link Token operations
            if operation == PlaidOperation.CREATE_LINK_TOKEN:
                link_token_data = parameters.get("link_token_data")
                if not link_token_data:
                    raise NodeValidationError("Link token data is required")
                result = await self._create_link_token(link_token_data, client_id, secret, environment)
            
            elif operation == PlaidOperation.GET_LINK_TOKEN:
                link_token = parameters.get("link_token")
                if not link_token:
                    raise NodeValidationError("Link token is required")
                result = await self._get_link_token(link_token, client_id, secret, environment)
            
            # Item operations
            elif operation == PlaidOperation.EXCHANGE_PUBLIC_TOKEN:
                public_token = parameters.get("public_token")
                if not public_token:
                    raise NodeValidationError("Public token is required")
                result = await self._exchange_public_token(public_token, client_id, secret, environment)
            
            elif operation == PlaidOperation.GET_ITEM:
                access_token = parameters.get("access_token")
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._get_item(access_token, client_id, secret, environment)
            
            elif operation == PlaidOperation.REMOVE_ITEM:
                access_token = parameters.get("access_token")
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._remove_item(access_token, client_id, secret, environment)
            
            # Account operations
            elif operation == PlaidOperation.GET_ACCOUNTS:
                access_token = parameters.get("access_token")
                account_ids = parameters.get("account_ids")
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._get_accounts(access_token, client_id, secret, environment, account_ids)
            
            elif operation == PlaidOperation.GET_BALANCE:
                access_token = parameters.get("access_token")
                account_ids = parameters.get("account_ids")
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._get_balance(access_token, client_id, secret, environment, account_ids)
            
            elif operation == PlaidOperation.GET_IDENTITY:
                access_token = parameters.get("access_token")
                account_ids = parameters.get("account_ids")
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._get_identity(access_token, client_id, secret, environment, account_ids)
            
            elif operation == PlaidOperation.GET_AUTH:
                access_token = parameters.get("access_token")
                account_ids = parameters.get("account_ids")
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._get_auth(access_token, client_id, secret, environment, account_ids)
            
            # Transaction operations
            elif operation == PlaidOperation.GET_TRANSACTIONS:
                access_token = parameters.get("access_token")
                start_date = parameters.get("start_date")
                end_date = parameters.get("end_date")
                account_ids = parameters.get("account_ids")
                count = parameters.get("count", 100)
                offset = parameters.get("offset", 0)
                if not access_token or not start_date or not end_date:
                    raise NodeValidationError("Access token, start date, and end date are required")
                result = await self._get_transactions(access_token, start_date, end_date, client_id, secret, environment, account_ids, count, offset)
            
            elif operation == PlaidOperation.GET_TRANSACTIONS_SYNC:
                access_token = parameters.get("access_token")
                cursor = parameters.get("cursor")
                count = parameters.get("count", 100)
                if not access_token:
                    raise NodeValidationError("Access token is required")
                result = await self._get_transactions_sync(access_token, client_id, secret, environment, cursor, count)
            
            # Asset Report operations
            elif operation == PlaidOperation.CREATE_ASSET_REPORT:
                asset_report_data = parameters.get("asset_report_data")
                if not asset_report_data:
                    raise NodeValidationError("Asset report data is required")
                result = await self._create_asset_report(asset_report_data, client_id, secret, environment)
            
            elif operation == PlaidOperation.GET_ASSET_REPORT:
                asset_report_token = parameters.get("asset_report_token")
                if not asset_report_token:
                    raise NodeValidationError("Asset report token is required")
                result = await self._get_asset_report(asset_report_token, client_id, secret, environment)
            
            # Transfer operations
            elif operation == PlaidOperation.CREATE_TRANSFER:
                transfer_data = parameters.get("transfer_data")
                if not transfer_data:
                    raise NodeValidationError("Transfer data is required")
                result = await self._create_transfer(transfer_data, client_id, secret, environment)
            
            elif operation == PlaidOperation.GET_TRANSFER:
                transfer_id = parameters.get("transfer_id")
                if not transfer_id:
                    raise NodeValidationError("Transfer ID is required")
                result = await self._get_transfer(transfer_id, client_id, secret, environment)
            
            # Institution operations
            elif operation == PlaidOperation.GET_INSTITUTIONS:
                count = parameters.get("count", 100)
                offset = parameters.get("offset", 0)
                country_codes = parameters.get("country_codes", ["US"])
                products = parameters.get("products")
                result = await self._get_institutions(count, offset, country_codes, client_id, secret, environment, products)
            
            elif operation == PlaidOperation.GET_INSTITUTION_BY_ID:
                institution_id = parameters.get("institution_id")
                country_codes = parameters.get("country_codes", ["US"])
                options = parameters.get("options")
                if not institution_id:
                    raise NodeValidationError("Institution ID is required")
                result = await self._get_institution_by_id(institution_id, country_codes, client_id, secret, environment, options)
            
            # Sandbox operations
            elif operation == PlaidOperation.SANDBOX_PUBLIC_TOKEN_CREATE:
                institution_id = parameters.get("institution_id")
                products = parameters.get("products", ["transactions"])
                options = parameters.get("options")
                if not institution_id:
                    raise NodeValidationError("Institution ID is required")
                result = await self._sandbox_public_token_create(institution_id, products, client_id, secret, environment, options)
            
            elif operation == PlaidOperation.SANDBOX_ITEM_FIRE_WEBHOOK:
                access_token = parameters.get("access_token")
                webhook_code = parameters.get("webhook_code")
                webhook_type = parameters.get("webhook_type")
                if not access_token or not webhook_code:
                    raise NodeValidationError("Access token and webhook code are required")
                result = await self._sandbox_item_fire_webhook(access_token, webhook_code, client_id, secret, environment, webhook_type)
            
            # Webhook operations
            elif operation == PlaidOperation.WEBHOOK_VERIFICATION_KEY_GET:
                key_id = parameters.get("key_id")
                if not key_id:
                    raise NodeValidationError("Key ID is required")
                result = await self._webhook_verification_key_get(key_id, client_id, secret, environment)
            
            # Webhook validation
            elif operation == "validate_webhook":
                webhook_payload = parameters.get("webhook_payload")
                webhook_signature = parameters.get("webhook_signature")
                webhook_key = parameters.get("webhook_key")
                if not all([webhook_payload, webhook_signature, webhook_key]):
                    raise NodeValidationError("Webhook payload, signature, and key are required")
                result = await self._validate_webhook(webhook_payload, webhook_signature, webhook_key)
            
            else:
                raise NodeValidationError(f"Unsupported operation: {operation}")

            if not result:
                raise NodeValidationError("Operation failed to return a result")

            # Extract response data and status
            response_data = result.get("response", {})
            status_code = result.get("status_code", 200)
            
            # Determine success based on status code
            success = 200 <= status_code < 300
            
            # Extract specific IDs from response for convenience
            access_token = None
            link_token = None
            item_id = None
            account_id = None
            asset_report_token = None
            transfer_id = None
            payment_id = None
            
            if isinstance(response_data, dict):
                access_token = response_data.get("access_token")
                link_token = response_data.get("link_token")
                item_id = response_data.get("item_id") or (response_data.get("item", {}).get("item_id") if "item" in response_data else None)
                if "accounts" in response_data and response_data["accounts"]:
                    account_id = response_data["accounts"][0].get("account_id")
                asset_report_token = response_data.get("asset_report_token")
                transfer_id = response_data.get("transfer_id") or (response_data.get("transfer", {}).get("id") if "transfer" in response_data else None)
                payment_id = response_data.get("payment_id") or (response_data.get("payment", {}).get("payment_id") if "payment" in response_data else None)

            return {
                "success": success,
                "error": None if success else response_data.get("error_message", response_data.get("display_message", f"HTTP {status_code}")),
                "response_data": response_data,
                "status_code": status_code,
                "access_token": access_token,
                "link_token": link_token,
                "item_id": item_id,
                "account_id": account_id,
                "asset_report_token": asset_report_token,
                "transfer_id": transfer_id,
                "payment_id": payment_id,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }

        except NodeValidationError as e:
            logger.error(f"Validation error in PlaidNode: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_data": None,
                "status_code": 400,
                "access_token": None,
                "link_token": None,
                "item_id": None,
                "account_id": None,
                "asset_report_token": None,
                "transfer_id": None,
                "payment_id": None,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }
        except Exception as e:
            logger.error(f"Unexpected error in PlaidNode: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "response_data": None,
                "status_code": 500,
                "access_token": None,
                "link_token": None,
                "item_id": None,
                "account_id": None,
                "asset_report_token": None,
                "transfer_id": None,
                "payment_id": None,
                "rate_limit_remaining": self.rate_limit_remaining,
                "rate_limit_reset": self.rate_limit_reset
            }

    async def cleanup(self):
        """Cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()

# Register the node
if __name__ == "__main__":
    node = PlaidNode()
    print(f"PlaidNode registered with {len(node.get_schema().parameters)} parameters")