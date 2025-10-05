"""
Revolut Account Node - Comprehensive account management integration for Revolut Business API
Supports all major Revolut account operations including account retrieval, balance management,
transaction listing, and account information management.
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

class RevolutAccountOperation:
    """All available Revolut Account operations based on official API documentation."""
    
    # Account Management Operations
    GET_ACCOUNTS = "get_accounts"
    GET_ACCOUNT = "get_account"
    GET_ACCOUNT_BALANCE = "get_account_balance"
    
    # Transaction Operations
    GET_TRANSACTIONS = "get_transactions"
    GET_TRANSACTION = "get_transaction"
    
    # Account Information Operations
    GET_ACCOUNT_STATEMENT = "get_account_statement"

class RevolutTransactionType:
    """Available Revolut transaction types."""
    
    ATM = "atm"
    CARD_PAYMENT = "card_payment"
    CARD_REFUND = "card_refund"
    CARD_CHARGEBACK = "card_chargeback"
    CARD_CREDIT = "card_credit"
    EXCHANGE = "exchange"
    TRANSFER = "transfer"
    LOAN = "loan"
    FEE = "fee"
    REFUND = "refund"
    TOPUP = "topup"
    TOPUP_RETURN = "topup_return"
    TAX = "tax"
    TAX_REFUND = "tax_refund"

class RevolutTransactionState:
    """Available Revolut transaction states."""
    
    COMPLETED = "completed"
    PENDING = "pending"
    DECLINED = "declined"
    FAILED = "failed"
    REVERTED = "reverted"

class RevolutAccountNode(BaseNode):
    """
    Comprehensive Revolut Account integration node supporting all major API operations.
    Handles account retrieval, balance management, transaction listing, and account information.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url_prod = "https://business.revolut.com"
        self.base_url_sandbox = "https://sandbox-business.revolut.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Revolut Account node."""
        return NodeSchema(
            name="RevolutAccountNode",
            description="Comprehensive Revolut Account management integration supporting account information, balance management, and transaction operations",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Revolut Account operation to perform",
                    required=True,
                    enum=[
                        RevolutAccountOperation.GET_ACCOUNTS,
                        RevolutAccountOperation.GET_ACCOUNT,
                        RevolutAccountOperation.GET_ACCOUNT_BALANCE,
                        RevolutAccountOperation.GET_TRANSACTIONS,
                        RevolutAccountOperation.GET_TRANSACTION,
                        RevolutAccountOperation.GET_ACCOUNT_STATEMENT,
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
                
                # Account Identification Parameters
                "account_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique account identifier for specific account operations",
                    required=False
                ),
                
                # Transaction Parameters
                "transaction_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique transaction identifier for single transaction operations",
                    required=False
                ),
                "id_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Type of ID to retrieve transaction by (id or request_id)",
                    required=False,
                    enum=["id", "request_id"]
                ),
                
                # Transaction Filtering Parameters
                "from_date": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Start date for transaction retrieval (ISO 8601 format)",
                    required=False
                ),
                "to_date": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="End date for transaction retrieval (ISO 8601 format)",
                    required=False
                ),
                "transaction_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Type of transactions to retrieve",
                    required=False,
                    enum=[
                        RevolutTransactionType.ATM,
                        RevolutTransactionType.CARD_PAYMENT,
                        RevolutTransactionType.CARD_REFUND,
                        RevolutTransactionType.CARD_CHARGEBACK,
                        RevolutTransactionType.CARD_CREDIT,
                        RevolutTransactionType.EXCHANGE,
                        RevolutTransactionType.TRANSFER,
                        RevolutTransactionType.LOAN,
                        RevolutTransactionType.FEE,
                        RevolutTransactionType.REFUND,
                        RevolutTransactionType.TOPUP,
                        RevolutTransactionType.TOPUP_RETURN,
                        RevolutTransactionType.TAX,
                        RevolutTransactionType.TAX_REFUND,
                    ]
                ),
                "transaction_state": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="State of transactions to retrieve",
                    required=False,
                    enum=[
                        RevolutTransactionState.COMPLETED,
                        RevolutTransactionState.PENDING,
                        RevolutTransactionState.DECLINED,
                        RevolutTransactionState.FAILED,
                        RevolutTransactionState.REVERTED,
                    ]
                ),
                
                # Pagination Parameters
                "count": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of transactions to retrieve per page",
                    required=False,
                    default=100
                ),
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of records to retrieve",
                    required=False
                ),
                
                # Statement Parameters
                "statement_format": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Format for account statement (PDF, CSV, etc.)",
                    required=False,
                    enum=["pdf", "csv", "xlsx"]
                ),
                "statement_period": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Period for account statement",
                    required=False
                ),
                
                # Additional Parameters
                "currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Currency filter for accounts and transactions",
                    required=False
                ),
                "include_pending": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to include pending transactions",
                    required=False,
                    default=True
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "accounts": NodeParameterType.ARRAY,
                "account_info": NodeParameterType.OBJECT,
                "account_balance": NodeParameterType.OBJECT,
                "transactions": NodeParameterType.ARRAY,
                "transaction_info": NodeParameterType.OBJECT,
                "total_balance": NodeParameterType.NUMBER,
                "available_balance": NodeParameterType.NUMBER,
                "currency": NodeParameterType.STRING,
                "account_id": NodeParameterType.STRING,
                "transaction_count": NodeParameterType.NUMBER,
                "statement_url": NodeParameterType.STRING,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Revolut Account-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate access token
        if not params.get("access_token"):
            raise NodeValidationError("Revolut Business API access token is required")
        
        # Validate operation-specific requirements
        account_specific_ops = [
            RevolutAccountOperation.GET_ACCOUNT,
            RevolutAccountOperation.GET_ACCOUNT_BALANCE,
            RevolutAccountOperation.GET_ACCOUNT_STATEMENT
        ]
        
        if operation in account_specific_ops:
            if not params.get("account_id"):
                raise NodeValidationError("account_id is required for account-specific operations")
        
        # Validate transaction-specific operations
        if operation == RevolutAccountOperation.GET_TRANSACTION:
            if not params.get("transaction_id"):
                raise NodeValidationError("transaction_id is required for single transaction retrieval")
        
        # Validate date format for transaction filtering
        date_fields = ["from_date", "to_date"]
        for field in date_fields:
            if params.get(field) and not self._validate_iso_date(params[field]):
                raise NodeValidationError(f"{field} must be in ISO 8601 format")
        
        # Validate pagination parameters
        if params.get("count") and (params.get("count") < 1 or params.get("count") > 1000):
            raise NodeValidationError("count must be between 1 and 1000")
        
        return params
    
    def _validate_iso_date(self, date_str: str) -> bool:
        """Validate ISO 8601 date format."""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Revolut Account operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get base URL based on environment
            base_url = self.base_url_prod if params.get("environment", "production") == "production" else self.base_url_sandbox
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['access_token']}",
                "Content-Type": "application/json",
                "User-Agent": "RevolutAccountNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == RevolutAccountOperation.GET_ACCOUNTS:
                return await self._get_accounts(params, base_url, headers)
            elif operation == RevolutAccountOperation.GET_ACCOUNT:
                return await self._get_account(params, base_url, headers)
            elif operation == RevolutAccountOperation.GET_ACCOUNT_BALANCE:
                return await self._get_account_balance(params, base_url, headers)
            elif operation == RevolutAccountOperation.GET_TRANSACTIONS:
                return await self._get_transactions(params, base_url, headers)
            elif operation == RevolutAccountOperation.GET_TRANSACTION:
                return await self._get_transaction(params, base_url, headers)
            elif operation == RevolutAccountOperation.GET_ACCOUNT_STATEMENT:
                return await self._get_account_statement(params, base_url, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in RevolutAccountNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _get_accounts(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get all accounts for the business."""
        try:
            url = f"{base_url}/accounts"
            
            # Add query parameters
            query_params = {}
            if params.get("currency"):
                query_params["currency"] = params["currency"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        accounts = response_data if isinstance(response_data, list) else response_data.get("accounts", [])
                        return {
                            "status": "success",
                            "operation_type": "get_accounts",
                            "accounts": accounts,
                            "account_count": len(accounts),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get accounts"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get accounts: {str(e)}")
    
    async def _get_account(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get specific account information."""
        try:
            account_id = params["account_id"]
            url = f"{base_url}/accounts/{account_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_account",
                            "account_id": account_id,
                            "account_info": response_data,
                            "currency": response_data.get("currency"),
                            "account_name": response_data.get("name"),
                            "account_type": response_data.get("type"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get account"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get account: {str(e)}")
    
    async def _get_account_balance(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get account balance information."""
        try:
            account_id = params["account_id"]
            url = f"{base_url}/accounts/{account_id}/balance"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_account_balance",
                            "account_id": account_id,
                            "account_balance": response_data,
                            "total_balance": response_data.get("balance"),
                            "available_balance": response_data.get("available_balance"),
                            "currency": response_data.get("currency"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get account balance"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get account balance: {str(e)}")
    
    async def _get_transactions(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get transaction list with filtering and pagination."""
        try:
            url = f"{base_url}/transactions"
            
            # Build query parameters
            query_params = {}
            
            if params.get("from_date"):
                query_params["from"] = params["from_date"]
            if params.get("to_date"):
                query_params["to"] = params["to_date"]
            if params.get("transaction_type"):
                query_params["type"] = params["transaction_type"]
            if params.get("count"):
                query_params["count"] = params["count"]
            if params.get("account_id"):
                query_params["account_id"] = params["account_id"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        transactions = response_data if isinstance(response_data, list) else response_data.get("transactions", [])
                        
                        # Filter by state if specified
                        if params.get("transaction_state"):
                            transactions = [t for t in transactions if t.get("state") == params["transaction_state"]]
                        
                        return {
                            "status": "success",
                            "operation_type": "get_transactions",
                            "transactions": transactions,
                            "transaction_count": len(transactions),
                            "from_date": params.get("from_date"),
                            "to_date": params.get("to_date"),
                            "transaction_type": params.get("transaction_type"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get transactions"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get transactions: {str(e)}")
    
    async def _get_transaction(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get specific transaction information."""
        try:
            transaction_id = params["transaction_id"]
            url = f"{base_url}/transaction/{transaction_id}"
            
            # Add query parameters if id_type is specified
            query_params = {}
            if params.get("id_type"):
                query_params["id_type"] = params["id_type"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_transaction",
                            "transaction_id": transaction_id,
                            "transaction_info": response_data,
                            "transaction_state": response_data.get("state"),
                            "transaction_type": response_data.get("type"),
                            "amount": response_data.get("amount"),
                            "currency": response_data.get("currency"),
                            "created_at": response_data.get("created_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get transaction"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get transaction: {str(e)}")
    
    async def _get_account_statement(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get account statement."""
        try:
            account_id = params["account_id"]
            url = f"{base_url}/accounts/{account_id}/statement"
            
            # Build query parameters
            query_params = {}
            if params.get("statement_format"):
                query_params["format"] = params["statement_format"]
            if params.get("from_date"):
                query_params["from"] = params["from_date"]
            if params.get("to_date"):
                query_params["to"] = params["to_date"]
            if params.get("statement_period"):
                query_params["period"] = params["statement_period"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "get_account_statement",
                            "account_id": account_id,
                            "statement_url": response_data.get("url"),
                            "statement_format": params.get("statement_format"),
                            "from_date": params.get("from_date"),
                            "to_date": params.get("to_date"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get account statement"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get account statement: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "accounts": None,
            "account_info": None,
            "account_balance": None,
            "transactions": None,
            "transaction_info": None,
            "total_balance": None,
            "available_balance": None,
            "currency": None,
            "account_id": None,
            "transaction_count": None,
            "statement_url": None,
            "operation_type": None,
            "response_data": None
        }

class RevolutAccountHelpers:
    """Helper functions for Revolut Account operations."""
    
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
    def calculate_date_range(days_back: int) -> tuple:
        """Calculate date range for transaction retrieval."""
        to_date = datetime.now(timezone.utc)
        from_date = to_date.replace(hour=0, minute=0, second=0, microsecond=0) - \
                   timedelta(days=days_back)
        
        return from_date.isoformat(), to_date.isoformat()
    
    @staticmethod
    def parse_transaction_amount(transaction: Dict[str, Any]) -> float:
        """Parse transaction amount from transaction data."""
        amount = transaction.get("amount", {})
        if isinstance(amount, dict):
            return float(amount.get("value", 0))
        return float(amount) if amount else 0
    
    @staticmethod
    def filter_transactions_by_amount(transactions: List[Dict[str, Any]], 
                                    min_amount: float = None, 
                                    max_amount: float = None) -> List[Dict[str, Any]]:
        """Filter transactions by amount range."""
        filtered = []
        
        for transaction in transactions:
            amount = RevolutAccountHelpers.parse_transaction_amount(transaction)
            
            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue
                
            filtered.append(transaction)
        
        return filtered
    
    @staticmethod
    def group_transactions_by_type(transactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group transactions by type."""
        grouped = {}
        
        for transaction in transactions:
            tx_type = transaction.get("type", "unknown")
            if tx_type not in grouped:
                grouped[tx_type] = []
            grouped[tx_type].append(transaction)
        
        return grouped
    
    @staticmethod
    def calculate_balance_summary(accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate balance summary across all accounts."""
        total_by_currency = {}
        account_count = len(accounts)
        
        for account in accounts:
            currency = account.get("currency")
            balance = account.get("balance", 0)
            
            if currency:
                if currency not in total_by_currency:
                    total_by_currency[currency] = 0
                total_by_currency[currency] += float(balance) if balance else 0
        
        return {
            "account_count": account_count,
            "balances_by_currency": total_by_currency,
            "currencies": list(total_by_currency.keys())
        }
    
    @staticmethod
    def validate_account_id(account_id: str) -> bool:
        """Validate account ID format."""
        import re
        # Revolut account IDs are typically UUIDs
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, account_id, re.IGNORECASE))
    
    @staticmethod
    def extract_account_summary(account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract account summary information."""
        return {
            "id": account_data.get("id"),
            "name": account_data.get("name"),
            "currency": account_data.get("currency"),
            "balance": account_data.get("balance"),
            "type": account_data.get("type"),
            "state": account_data.get("state"),
            "created_at": account_data.get("created_at")
        }