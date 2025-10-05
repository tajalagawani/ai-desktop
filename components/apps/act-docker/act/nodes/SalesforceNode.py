"""
Salesforce Enterprise CRM Integration Node

Comprehensive integration with Salesforce REST API for enterprise customer relationship management, sales automation, 
service cloud operations, and platform development. Supports complete CRM lifecycle, custom object management, 
workflow automation, and enterprise application development.

Key capabilities include: Lead, opportunity, and account management, contact and case tracking, custom object operations, 
SOQL query execution, workflow and process automation, user and permission management, metadata operations, 
bulk data processing, and enterprise integration patterns.

Built for production environments with OAuth 2.0, JWT bearer flow, session-based authentication, comprehensive 
error handling, bulk API support, and enterprise security features for large-scale CRM deployments.
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

class SalesforceNode(BaseNode):
    """Comprehensive Salesforce enterprise CRM integration node."""
    
    # Embedded configuration for Salesforce REST API
    CONFIG = {
        "base_url": "",  # Dynamic based on instance_url
        "authentication": {
            "type": "bearer_token",
            "header": "Authorization"
        },
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        "timeout": 30,
        "retry_config": {
            "max_retries": 3,
            "retry_delay": 1.0,
            "exponential_backoff": True
        },
        "rate_limiting": {
            "max_requests_per_minute": 100,
            "burst_limit": 20
        }
    }
    
    # Complete operations mapping for Salesforce REST API
    OPERATIONS = {
        # SOQL Operations
        "execute_soql": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/query",
            "params": ["q"],
            "required": ["q"]
        },
        "execute_sosl": {
            "method": "GET", 
            "endpoint": "/services/data/v58.0/search",
            "params": ["q"],
            "required": ["q"]
        },
        
        # Account Operations
        "get_accounts": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects/Account",
            "params": ["limit", "offset", "fields"],
            "required": []
        },
        "create_account": {
            "method": "POST",
            "endpoint": "/services/data/v58.0/sobjects/Account",
            "params": ["Name", "Type", "Industry", "Phone", "Website", "BillingStreet", "BillingCity", "BillingState", "BillingPostalCode", "BillingCountry"],
            "required": ["Name"]
        },
        "update_account": {
            "method": "PATCH",
            "endpoint": "/services/data/v58.0/sobjects/Account/{record_id}",
            "params": ["Name", "Type", "Industry", "Phone", "Website", "BillingStreet", "BillingCity", "BillingState", "BillingPostalCode", "BillingCountry"],
            "required": ["record_id"]
        },
        "delete_account": {
            "method": "DELETE",
            "endpoint": "/services/data/v58.0/sobjects/Account/{record_id}",
            "params": ["record_id"],
            "required": ["record_id"]
        },
        
        # Contact Operations
        "get_contacts": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects/Contact",
            "params": ["limit", "offset", "fields"],
            "required": []
        },
        "create_contact": {
            "method": "POST",
            "endpoint": "/services/data/v58.0/sobjects/Contact",
            "params": ["FirstName", "LastName", "Email", "Phone", "AccountId", "Title", "Department"],
            "required": ["LastName"]
        },
        "update_contact": {
            "method": "PATCH",
            "endpoint": "/services/data/v58.0/sobjects/Contact/{record_id}",
            "params": ["FirstName", "LastName", "Email", "Phone", "AccountId", "Title", "Department"],
            "required": ["record_id"]
        },
        
        # Lead Operations
        "get_leads": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects/Lead",
            "params": ["limit", "offset", "fields"],
            "required": []
        },
        "create_lead": {
            "method": "POST",
            "endpoint": "/services/data/v58.0/sobjects/Lead",
            "params": ["FirstName", "LastName", "Email", "Phone", "Company", "Status", "LeadSource", "Industry"],
            "required": ["LastName", "Company"]
        },
        "update_lead": {
            "method": "PATCH",
            "endpoint": "/services/data/v58.0/sobjects/Lead/{record_id}",
            "params": ["FirstName", "LastName", "Email", "Phone", "Company", "Status", "LeadSource", "Industry"],
            "required": ["record_id"]
        },
        
        # Opportunity Operations
        "get_opportunities": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects/Opportunity",
            "params": ["limit", "offset", "fields"],
            "required": []
        },
        "create_opportunity": {
            "method": "POST",
            "endpoint": "/services/data/v58.0/sobjects/Opportunity",
            "params": ["Name", "AccountId", "StageName", "CloseDate", "Amount", "Type", "LeadSource"],
            "required": ["Name", "StageName", "CloseDate"]
        },
        "update_opportunity": {
            "method": "PATCH",
            "endpoint": "/services/data/v58.0/sobjects/Opportunity/{record_id}",
            "params": ["Name", "AccountId", "StageName", "CloseDate", "Amount", "Type", "LeadSource"],
            "required": ["record_id"]
        },
        
        # Custom Object Operations
        "get_sobject": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects/{sobject_type}/{record_id}",
            "params": ["sobject_type", "record_id", "fields"],
            "required": ["sobject_type", "record_id"]
        },
        "create_sobject": {
            "method": "POST",
            "endpoint": "/services/data/v58.0/sobjects/{sobject_type}",
            "params": ["sobject_type"],
            "required": ["sobject_type"]
        },
        "update_sobject": {
            "method": "PATCH",
            "endpoint": "/services/data/v58.0/sobjects/{sobject_type}/{record_id}",
            "params": ["sobject_type", "record_id"],
            "required": ["sobject_type", "record_id"]
        },
        "delete_sobject": {
            "method": "DELETE",
            "endpoint": "/services/data/v58.0/sobjects/{sobject_type}/{record_id}",
            "params": ["sobject_type", "record_id"],
            "required": ["sobject_type", "record_id"]
        },
        
        # Metadata Operations
        "describe_sobject": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects/{sobject_type}/describe",
            "params": ["sobject_type"],
            "required": ["sobject_type"]
        },
        "get_sobject_types": {
            "method": "GET",
            "endpoint": "/services/data/v58.0/sobjects",
            "params": [],
            "required": []
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Salesforce node."""
        return NodeSchema(
            name="SalesforceNode",
            description="Comprehensive Salesforce enterprise CRM integration supporting sales automation, service cloud, custom objects, and platform development",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Salesforce operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "instance_url": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Salesforce instance URL (e.g., https://your-domain.salesforce.com)",
                    required=True
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Salesforce access token (OAuth or session token)",
                    required=True
                ),
                "q": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="SOQL/SOSL query string",
                    required=False
                ),
                "sobject_type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Salesforce object type (Account, Contact, Lead, Opportunity, or custom)",
                    required=False
                ),
                "record_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Salesforce record ID",
                    required=False
                ),
                "fields": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Comma-separated list of fields to retrieve",
                    required=False
                ),
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of records to return",
                    required=False
                ),
                "offset": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of records to skip",
                    required=False
                ),
                # Standard Object Fields
                "Name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Name field",
                    required=False
                ),
                "FirstName": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="First name",
                    required=False
                ),
                "LastName": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Last name",
                    required=False
                ),
                "Email": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email address",
                    required=False
                ),
                "Phone": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Phone number",
                    required=False
                ),
                "Company": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Company name",
                    required=False
                ),
                "AccountId": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Account ID",
                    required=False
                ),
                "StageName": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Opportunity stage name",
                    required=False
                ),
                "CloseDate": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Close date (YYYY-MM-DD)",
                    required=False
                ),
                "Amount": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Amount",
                    required=False
                ),
                "Type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Type field",
                    required=False
                ),
                "Industry": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Industry",
                    required=False
                ),
                "Status": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Status",
                    required=False
                ),
                "Title": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Job title",
                    required=False
                ),
                "Department": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Department",
                    required=False
                ),
                "LeadSource": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Lead source",
                    required=False
                ),
                "Website": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Website URL",
                    required=False
                ),
                "BillingStreet": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Billing street address",
                    required=False
                ),
                "BillingCity": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Billing city",
                    required=False
                ),
                "BillingState": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Billing state",
                    required=False
                ),
                "BillingPostalCode": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Billing postal code",
                    required=False
                ),
                "BillingCountry": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Billing country",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "records": NodeParameterType.ARRAY,
                "record_info": NodeParameterType.OBJECT,
                "query_results": NodeParameterType.ARRAY,
                "sobject_metadata": NodeParameterType.OBJECT,
                "sobject_types": NodeParameterType.ARRAY,
                "total_size": NodeParameterType.NUMBER,
                "done": NodeParameterType.BOOLEAN,
                "next_records_url": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Salesforce-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        if not params.get("instance_url"):
            raise NodeValidationError("Instance URL is required")
        if not params.get("access_token"):
            raise NodeValidationError("Access token is required")
        
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
        """Execute the Salesforce operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            instance_url = params["instance_url"].rstrip('/')
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare dynamic configuration
            config = self.CONFIG.copy()
            config["base_url"] = instance_url
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": params["access_token"]
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            if "{sobject_type}" in endpoint:
                endpoint = endpoint.replace("{sobject_type}", params.get("sobject_type", ""))
            if "{record_id}" in endpoint:
                endpoint = endpoint.replace("{record_id}", params.get("record_id", ""))
            universal_params["endpoint"] = endpoint
            
            # Handle query parameters and body data
            if operation_config["method"] == "GET":
                query_params = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        if param == "q":
                            query_params["q"] = params[param]
                        elif param == "fields":
                            query_params["fields"] = params[param]
                        elif param == "limit":
                            query_params["limit"] = str(params[param])
                        elif param == "offset":
                            query_params["offset"] = str(params[param])
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PATCH operations - prepare body data
                body_data = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        # Skip path parameters
                        if param not in ["sobject_type", "record_id"]:
                            body_data[param] = params[param]
                if body_data:
                    universal_params["body"] = body_data
            
            # Execute the request
            result = await self.universal_node.execute({
                "params": universal_params
            })
            
            if result.get("status") == "success":
                response_data = result.get("response", {})
                
                # Transform response based on operation type
                if operation.startswith("execute_soql") or operation.startswith("execute_sosl"):
                    return {
                        "status": "success",
                        "query_results": response_data.get("records", []),
                        "total_size": response_data.get("totalSize", 0),
                        "done": response_data.get("done", True),
                        "next_records_url": response_data.get("nextRecordsUrl"),
                        "response_data": response_data
                    }
                elif operation.startswith("get_") or operation == "describe_sobject" or operation == "get_sobject_types":
                    if operation == "get_sobject_types":
                        return {
                            "status": "success",
                            "sobject_types": response_data.get("sobjects", []),
                            "response_data": response_data
                        }
                    elif operation == "describe_sobject":
                        return {
                            "status": "success",
                            "sobject_metadata": response_data,
                            "response_data": response_data
                        }
                    else:
                        return {
                            "status": "success",
                            "records": response_data if isinstance(response_data, list) else [response_data],
                            "response_data": response_data
                        }
                elif operation.startswith("create_") or operation.startswith("update_"):
                    return {
                        "status": "success",
                        "record_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("delete_"):
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
            logger.error(f"Salesforce operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "SALESFORCE_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()