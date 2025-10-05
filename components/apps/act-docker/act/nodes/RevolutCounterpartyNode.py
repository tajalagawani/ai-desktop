"""
Revolut Counterparty Node - Comprehensive counterparty management integration for Revolut Business API
Supports all major Revolut counterparty operations including counterparty creation, retrieval,
bank account management, and international counterparty support.
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

class RevolutCounterpartyOperation:
    """All available Revolut Counterparty operations based on official API documentation."""
    
    # Counterparty Management Operations
    CREATE_COUNTERPARTY = "create_counterparty"
    GET_COUNTERPARTIES = "get_counterparties"
    GET_COUNTERPARTY = "get_counterparty"
    DELETE_COUNTERPARTY = "delete_counterparty"
    
    # Validation Operations
    VALIDATE_ACCOUNT_NAME = "validate_account_name"

class RevolutCounterpartyProfileType:
    """Available Revolut counterparty profile types."""
    
    PERSONAL = "personal"
    BUSINESS = "business"

class RevolutCounterpartyState:
    """Available Revolut counterparty states."""
    
    CREATED = "created"
    PENDING = "pending"

class RevolutCounterpartyNode(BaseNode):
    """
    Comprehensive Revolut Counterparty integration node supporting all major API operations.
    Handles counterparty creation, retrieval, bank account management, and international support.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url_prod = "https://b2b.revolut.com"
        self.base_url_sandbox = "https://sandbox-b2b.revolut.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Revolut Counterparty node."""
        return NodeSchema(
            name="RevolutCounterpartyNode",
            description="Comprehensive Revolut Counterparty management integration supporting counterparty creation, bank account management, and international counterparty support",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Revolut Counterparty operation to perform",
                    required=True,
                    enum=[
                        RevolutCounterpartyOperation.CREATE_COUNTERPARTY,
                        RevolutCounterpartyOperation.GET_COUNTERPARTIES,
                        RevolutCounterpartyOperation.GET_COUNTERPARTY,
                        RevolutCounterpartyOperation.DELETE_COUNTERPARTY,
                        RevolutCounterpartyOperation.VALIDATE_ACCOUNT_NAME,
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
                
                # Counterparty Identification Parameters
                "counterparty_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique counterparty identifier for specific operations",
                    required=False
                ),
                
                # Profile Parameters
                "profile_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Counterparty profile type",
                    required=False,
                    enum=["personal", "business"]
                ),
                "individual_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Full name for individual counterparties",
                    required=False
                ),
                "first_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="First name for individual counterparties (alternative to individual_name)",
                    required=False
                ),
                "last_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Last name for individual counterparties (alternative to individual_name)",
                    required=False
                ),
                "company_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Company name for business counterparties",
                    required=False
                ),
                "custom_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Custom name for Revolut user counterparties",
                    required=False
                ),
                
                # Revolut User Parameters
                "revtag": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Revolut tag for existing Revolut users",
                    required=False
                ),
                
                # Bank Account Parameters
                "bank_country": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Bank country code (2-letter ISO 3166)",
                    required=False
                ),
                "currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="ISO 4217 currency code (uppercase)",
                    required=False
                ),
                "account_no": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Bank account number",
                    required=False
                ),
                "sort_code": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="UK sort code (6 digits)",
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
                "routing_number": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="US routing number (9 digits)",
                    required=False
                ),
                "clabe": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="CLABE number for Mexico",
                    required=False
                ),
                "ifsc": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="IFSC code for India",
                    required=False
                ),
                "bsb": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="BSB number for Australia",
                    required=False
                ),
                
                # Filtering Parameters (for listing counterparties)
                "name_filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Partial counterparty name match for filtering",
                    required=False
                ),
                "account_no_filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Exact account number for filtering",
                    required=False
                ),
                "sort_code_filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Exact sort code for filtering",
                    required=False
                ),
                "iban_filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Exact IBAN for filtering",
                    required=False
                ),
                "bic_filter": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Exact BIC for filtering",
                    required=False
                ),
                "created_before": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter counterparties created before this date (ISO 8601)",
                    required=False
                ),
                "created_after": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Filter counterparties created after this date (ISO 8601)",
                    required=False
                ),
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of counterparties to return (1-1000, default 100)",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "counterparties": NodeParameterType.ARRAY,
                "counterparty_count": NodeParameterType.NUMBER,
                "counterparty_id": NodeParameterType.STRING,
                "counterparty_info": NodeParameterType.OBJECT,
                "counterparty_name": NodeParameterType.STRING,
                "profile_type": NodeParameterType.STRING,
                "counterparty_state": NodeParameterType.STRING,
                "bank_country": NodeParameterType.STRING,
                "accounts": NodeParameterType.ARRAY,
                "account_count": NodeParameterType.NUMBER,
                "validation_result": NodeParameterType.OBJECT,
                "is_valid": NodeParameterType.BOOLEAN,
                "created_at": NodeParameterType.STRING,
                "updated_at": NodeParameterType.STRING,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Revolut Counterparty-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate access token
        if not params.get("access_token"):
            raise NodeValidationError("Revolut Business API access token is required")
        
        # Validate operation-specific requirements
        counterparty_specific_ops = [
            RevolutCounterpartyOperation.GET_COUNTERPARTY,
            RevolutCounterpartyOperation.DELETE_COUNTERPARTY
        ]
        
        if operation in counterparty_specific_ops:
            if not params.get("counterparty_id"):
                raise NodeValidationError("counterparty_id is required for counterparty-specific operations")
        
        # Validate counterparty creation requirements
        if operation == RevolutCounterpartyOperation.CREATE_COUNTERPARTY:
            # Must have profile type
            if not params.get("profile_type"):
                raise NodeValidationError("profile_type is required for counterparty creation")
            
            if params.get("profile_type") not in [RevolutCounterpartyProfileType.PERSONAL, RevolutCounterpartyProfileType.BUSINESS]:
                raise NodeValidationError("profile_type must be 'personal' or 'business'")
            
            # Validate naming requirements based on profile type
            if params.get("profile_type") == RevolutCounterpartyProfileType.PERSONAL:
                has_individual_name = params.get("individual_name")
                has_name_parts = params.get("first_name") and params.get("last_name")
                has_revtag = params.get("revtag")
                
                if not (has_individual_name or has_name_parts or has_revtag):
                    raise NodeValidationError("For personal counterparties, provide either 'individual_name', 'first_name'+'last_name', or 'revtag'")
            
            elif params.get("profile_type") == RevolutCounterpartyProfileType.BUSINESS:
                has_company_name = params.get("company_name")
                has_revtag = params.get("revtag")
                
                if not (has_company_name or has_revtag):
                    raise NodeValidationError("For business counterparties, provide either 'company_name' or 'revtag'")
            
            # Validate bank account details (at least one method required if not using revtag)
            if not params.get("revtag"):
                bank_methods = [
                    params.get("account_no"),
                    params.get("iban"),
                    params.get("clabe"),
                    params.get("ifsc"),
                    params.get("bsb")
                ]
                
                if not any(bank_methods):
                    raise NodeValidationError("Bank account details required: provide account_no, iban, clabe, ifsc, or bsb")
        
        # Validate account name validation requirements
        if operation == RevolutCounterpartyOperation.VALIDATE_ACCOUNT_NAME:
            if not all([params.get("account_no"), params.get("sort_code")]):
                raise NodeValidationError("account_no and sort_code are required for account name validation")
        
        # Validate currency format
        if params.get("currency") and not self._validate_currency_code(params["currency"]):
            raise NodeValidationError("currency must be a valid 3-letter ISO 4217 currency code")
        
        # Validate country format
        if params.get("bank_country") and not self._validate_country_code(params["bank_country"]):
            raise NodeValidationError("bank_country must be a valid 2-letter ISO 3166 country code")
        
        # Validate date format
        date_fields = ["created_before", "created_after"]
        for field in date_fields:
            if params.get(field) and not self._validate_iso_date(params[field]):
                raise NodeValidationError(f"{field} must be in ISO 8601 format")
        
        # Validate limit
        if params.get("limit") and (params.get("limit") < 1 or params.get("limit") > 1000):
            raise NodeValidationError("limit must be between 1 and 1000")
        
        return params
    
    def _validate_currency_code(self, currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    def _validate_country_code(self, country: str) -> bool:
        """Validate ISO 3166 country code format."""
        import re
        return bool(re.match(r'^[A-Z]{2}$', country))
    
    def _validate_iso_date(self, date_str: str) -> bool:
        """Validate ISO 8601 date format."""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Revolut Counterparty operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get base URL based on environment
            base_url = self.base_url_prod if params.get("environment", "production") == "production" else self.base_url_sandbox
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['access_token']}",
                "Content-Type": "application/json",
                "User-Agent": "RevolutCounterpartyNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == RevolutCounterpartyOperation.CREATE_COUNTERPARTY:
                return await self._create_counterparty(params, base_url, headers)
            elif operation == RevolutCounterpartyOperation.GET_COUNTERPARTIES:
                return await self._get_counterparties(params, base_url, headers)
            elif operation == RevolutCounterpartyOperation.GET_COUNTERPARTY:
                return await self._get_counterparty(params, base_url, headers)
            elif operation == RevolutCounterpartyOperation.DELETE_COUNTERPARTY:
                return await self._delete_counterparty(params, base_url, headers)
            elif operation == RevolutCounterpartyOperation.VALIDATE_ACCOUNT_NAME:
                return await self._validate_account_name(params, base_url, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in RevolutCounterpartyNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _create_counterparty(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a counterparty."""
        try:
            url = f"{base_url}/api/1.0/counterparties"
            
            payload = {
                "profile_type": params["profile_type"]
            }
            
            # Add naming based on profile type and available data
            if params.get("revtag"):
                payload["revtag"] = params["revtag"]
                if params.get("custom_name"):
                    payload["name"] = params["custom_name"]
            elif params.get("profile_type") == RevolutCounterpartyProfileType.PERSONAL:
                if params.get("individual_name"):
                    payload["individual_name"] = params["individual_name"]
                elif params.get("first_name") and params.get("last_name"):
                    payload["first_name"] = params["first_name"]
                    payload["last_name"] = params["last_name"]
            elif params.get("profile_type") == RevolutCounterpartyProfileType.BUSINESS:
                if params.get("company_name"):
                    payload["company_name"] = params["company_name"]
            
            # Add bank details if not using revtag
            if not params.get("revtag"):
                if params.get("bank_country"):
                    payload["bank_country"] = params["bank_country"]
                if params.get("currency"):
                    payload["currency"] = params["currency"]
                
                # Add account identification
                if params.get("account_no"):
                    payload["account_no"] = params["account_no"]
                if params.get("sort_code"):
                    payload["sort_code"] = params["sort_code"]
                if params.get("iban"):
                    payload["iban"] = params["iban"]
                if params.get("bic"):
                    payload["bic"] = params["bic"]
                if params.get("routing_number"):
                    payload["routing_number"] = params["routing_number"]
                if params.get("clabe"):
                    payload["clabe"] = params["clabe"]
                if params.get("ifsc"):
                    payload["ifsc"] = params["ifsc"]
                if params.get("bsb"):
                    payload["bsb"] = params["bsb"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "operation_type": "create_counterparty",
                            "counterparty_id": response_data.get("id"),
                            "counterparty_info": response_data,
                            "counterparty_name": response_data.get("name"),
                            "profile_type": response_data.get("profile_type"),
                            "counterparty_state": response_data.get("state"),
                            "bank_country": response_data.get("country"),
                            "accounts": response_data.get("accounts", []),
                            "account_count": len(response_data.get("accounts", [])),
                            "created_at": response_data.get("created_at"),
                            "updated_at": response_data.get("updated_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create counterparty"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create counterparty: {str(e)}")
    
    async def _get_counterparties(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get all counterparties with optional filtering."""
        try:
            url = f"{base_url}/api/1.0/counterparties"
            
            # Add query parameters
            query_params = {}
            
            # Filtering parameters
            if params.get("name_filter"):
                query_params["name"] = params["name_filter"]
            if params.get("account_no_filter"):
                query_params["account_no"] = params["account_no_filter"]
            if params.get("sort_code_filter"):
                query_params["sort_code"] = params["sort_code_filter"]
            if params.get("iban_filter"):
                query_params["iban"] = params["iban_filter"]
            if params.get("bic_filter"):
                query_params["bic"] = params["bic_filter"]
            if params.get("created_before"):
                query_params["created_before"] = params["created_before"]
            if params.get("created_after"):
                query_params["created_after"] = params["created_after"]
            if params.get("limit"):
                query_params["limit"] = params["limit"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
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
    
    async def _get_counterparty(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get specific counterparty information."""
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
                            "counterparty_info": response_data,
                            "counterparty_name": response_data.get("name"),
                            "profile_type": response_data.get("profile_type"),
                            "counterparty_state": response_data.get("state"),
                            "bank_country": response_data.get("country"),
                            "accounts": response_data.get("accounts", []),
                            "account_count": len(response_data.get("accounts", [])),
                            "created_at": response_data.get("created_at"),
                            "updated_at": response_data.get("updated_at"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get counterparty"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get counterparty: {str(e)}")
    
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
    
    async def _validate_account_name(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate UK account name (Confirmation of Payee)."""
        try:
            # Note: This endpoint may not be directly available in the standard API
            # Implementation would depend on specific Revolut API availability
            url = f"{base_url}/api/1.0/counterparties/validate"
            
            payload = {
                "account_no": params["account_no"],
                "sort_code": params["sort_code"]
            }
            
            # Add optional name for validation
            if params.get("individual_name"):
                payload["name"] = params["individual_name"]
            elif params.get("company_name"):
                payload["name"] = params["company_name"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "operation_type": "validate_account_name",
                            "validation_result": response_data,
                            "is_valid": response_data.get("valid", False),
                            "account_no": params["account_no"],
                            "sort_code": params["sort_code"],
                            "validation_details": response_data.get("details"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to validate account name"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to validate account name: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "counterparties": None,
            "counterparty_count": None,
            "counterparty_id": None,
            "counterparty_info": None,
            "counterparty_name": None,
            "profile_type": None,
            "counterparty_state": None,
            "bank_country": None,
            "accounts": None,
            "account_count": None,
            "validation_result": None,
            "is_valid": None,
            "created_at": None,
            "updated_at": None,
            "operation_type": None,
            "response_data": None
        }

class RevolutCounterpartyHelpers:
    """Helper functions for Revolut Counterparty operations."""
    
    @staticmethod
    def validate_currency_code(currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    @staticmethod
    def validate_country_code(country: str) -> bool:
        """Validate ISO 3166 country code format."""
        import re
        return bool(re.match(r'^[A-Z]{2}$', country))
    
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
    def validate_uk_sort_code(sort_code: str) -> bool:
        """Validate UK sort code format."""
        import re
        # Remove hyphens and spaces
        clean_code = sort_code.replace('-', '').replace(' ', '')
        # Should be exactly 6 digits
        return bool(re.match(r'^[0-9]{6}$', clean_code))
    
    @staticmethod
    def validate_us_routing_number(routing_number: str) -> bool:
        """Validate US routing number format."""
        import re
        # Should be exactly 9 digits
        return bool(re.match(r'^[0-9]{9}$', routing_number))
    
    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as ISO string for API requests."""
        return dt.isoformat()
    
    @staticmethod
    def parse_counterparty_state(state: str) -> Dict[str, Any]:
        """Parse and categorize counterparty state."""
        state_info = {
            "created": {
                "category": "active",
                "can_receive_payments": True,
                "description": "Counterparty is active and ready for transactions"
            },
            "pending": {
                "category": "pending",
                "can_receive_payments": False,
                "description": "Counterparty is pending verification (manual 2FA approval required)"
            }
        }
        
        return state_info.get(state.lower(), {
            "category": "unknown",
            "can_receive_payments": False,
            "description": f"Unknown state: {state}"
        })
    
    @staticmethod
    def build_bank_account_object(account_no: str = None, iban: str = None, 
                                sort_code: str = None, bic: str = None,
                                routing_number: str = None, country: str = None,
                                currency: str = None) -> Dict[str, Any]:
        """Build bank account object for counterparty creation."""
        account = {}
        
        if country:
            account["country"] = country
        if currency:
            account["currency"] = currency
        if account_no:
            account["account_no"] = account_no
        if iban:
            account["iban"] = iban
        if sort_code:
            account["sort_code"] = sort_code
        if bic:
            account["bic"] = bic
        if routing_number:
            account["routing_number"] = routing_number
            
        return account
    
    @staticmethod
    def get_supported_countries() -> Dict[str, Dict[str, Any]]:
        """Get list of supported countries with their bank account requirements."""
        return {
            "GB": {
                "name": "United Kingdom",
                "required_fields": ["account_no", "sort_code"],
                "optional_fields": ["iban"],
                "currency": "GBP"
            },
            "US": {
                "name": "United States",
                "required_fields": ["account_no", "routing_number"],
                "optional_fields": ["bic"],
                "currency": "USD"
            },
            "DE": {
                "name": "Germany",
                "required_fields": ["iban"],
                "optional_fields": ["bic"],
                "currency": "EUR"
            },
            "FR": {
                "name": "France",
                "required_fields": ["iban"],
                "optional_fields": ["bic"],
                "currency": "EUR"
            },
            "AU": {
                "name": "Australia",
                "required_fields": ["account_no", "bsb"],
                "optional_fields": [],
                "currency": "AUD"
            },
            "IN": {
                "name": "India",
                "required_fields": ["account_no", "ifsc"],
                "optional_fields": [],
                "currency": "INR"
            },
            "MX": {
                "name": "Mexico",
                "required_fields": ["clabe"],
                "optional_fields": [],
                "currency": "MXN"
            }
        }
    
    @staticmethod
    def validate_counterparty_data(profile_type: str, individual_name: str = None,
                                 company_name: str = None, first_name: str = None,
                                 last_name: str = None, revtag: str = None) -> List[str]:
        """Validate counterparty data and return list of validation errors."""
        errors = []
        
        if profile_type not in ["personal", "business"]:
            errors.append("profile_type must be 'personal' or 'business'")
            return errors
        
        if profile_type == "personal":
            has_individual_name = bool(individual_name)
            has_name_parts = bool(first_name and last_name)
            has_revtag = bool(revtag)
            
            if not (has_individual_name or has_name_parts or has_revtag):
                errors.append("For personal counterparties, provide either 'individual_name', 'first_name'+'last_name', or 'revtag'")
        
        elif profile_type == "business":
            has_company_name = bool(company_name)
            has_revtag = bool(revtag)
            
            if not (has_company_name or has_revtag):
                errors.append("For business counterparties, provide either 'company_name' or 'revtag'")
        
        return errors
    
    @staticmethod
    def format_counterparty_summary(counterparty_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format counterparty data into a summary object."""
        return {
            "id": counterparty_data.get("id"),
            "name": counterparty_data.get("name"),
            "profile_type": counterparty_data.get("profile_type"),
            "state": counterparty_data.get("state"),
            "country": counterparty_data.get("country"),
            "account_count": len(counterparty_data.get("accounts", [])),
            "can_receive_payments": counterparty_data.get("state") == "created",
            "created_at": counterparty_data.get("created_at"),
            "updated_at": counterparty_data.get("updated_at")
        }
    
    @staticmethod
    def extract_account_identifiers(account_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract key identifiers from account data."""
        identifiers = {}
        
        if account_data.get("account_no"):
            identifiers["account_number"] = account_data["account_no"]
        if account_data.get("iban"):
            identifiers["iban"] = account_data["iban"]
        if account_data.get("sort_code"):
            identifiers["sort_code"] = account_data["sort_code"]
        if account_data.get("bic"):
            identifiers["bic"] = account_data["bic"]
        if account_data.get("routing_number"):
            identifiers["routing_number"] = account_data["routing_number"]
        
        return identifiers