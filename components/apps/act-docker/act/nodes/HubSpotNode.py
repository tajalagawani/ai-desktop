"""
HubSpot CRM & Marketing Automation Integration Node

Comprehensive integration with HubSpot REST API for complete customer relationship management, marketing automation, 
sales pipeline management, and business growth operations. Supports contact and company management, deal tracking, 
marketing campaigns, email automation, and analytics reporting.

Key capabilities include: Contact and company database management, deal pipeline and sales tracking, marketing campaign 
automation, email marketing and sequences, lead scoring and qualification, reporting and analytics, workflow automation, 
integration management, and team collaboration features.

Built for production environments with API key and OAuth 2.0 authentication, comprehensive error handling, 
rate limiting compliance, and enterprise features for sales and marketing teams.
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

class HubSpotNode(BaseNode):
    """Comprehensive HubSpot CRM and marketing automation integration node."""
    
    # Embedded configuration for HubSpot API
    CONFIG = {
        "base_url": "https://api.hubapi.com",
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
            "burst_limit": 10
        }
    }
    
    # Complete operations mapping for HubSpot API
    OPERATIONS = {
        # Contact Operations
        "get_contacts": {
            "method": "GET",
            "endpoint": "/crm/v3/objects/contacts",
            "params": ["limit", "properties", "archived"],
            "required": []
        },
        "get_contact": {
            "method": "GET",
            "endpoint": "/crm/v3/objects/contacts/{contact_id}",
            "params": ["contact_id", "properties", "associations"],
            "required": ["contact_id"]
        },
        "create_contact": {
            "method": "POST",
            "endpoint": "/crm/v3/objects/contacts",
            "params": ["properties"],
            "required": ["properties"]
        },
        "update_contact": {
            "method": "PATCH",
            "endpoint": "/crm/v3/objects/contacts/{contact_id}",
            "params": ["contact_id", "properties"],
            "required": ["contact_id", "properties"]
        },
        "delete_contact": {
            "method": "DELETE",
            "endpoint": "/crm/v3/objects/contacts/{contact_id}",
            "params": ["contact_id"],
            "required": ["contact_id"]
        },
        
        # Company Operations
        "get_companies": {
            "method": "GET",
            "endpoint": "/crm/v3/objects/companies",
            "params": ["limit", "properties", "archived"],
            "required": []
        },
        "get_company": {
            "method": "GET",
            "endpoint": "/crm/v3/objects/companies/{company_id}",
            "params": ["company_id", "properties", "associations"],
            "required": ["company_id"]
        },
        "create_company": {
            "method": "POST",
            "endpoint": "/crm/v3/objects/companies",
            "params": ["properties"],
            "required": ["properties"]
        },
        "update_company": {
            "method": "PATCH",
            "endpoint": "/crm/v3/objects/companies/{company_id}",
            "params": ["company_id", "properties"],
            "required": ["company_id", "properties"]
        },
        "delete_company": {
            "method": "DELETE",
            "endpoint": "/crm/v3/objects/companies/{company_id}",
            "params": ["company_id"],
            "required": ["company_id"]
        },
        
        # Deal Operations
        "get_deals": {
            "method": "GET",
            "endpoint": "/crm/v3/objects/deals",
            "params": ["limit", "properties", "archived"],
            "required": []
        },
        "get_deal": {
            "method": "GET",
            "endpoint": "/crm/v3/objects/deals/{deal_id}",
            "params": ["deal_id", "properties", "associations"],
            "required": ["deal_id"]
        },
        "create_deal": {
            "method": "POST",
            "endpoint": "/crm/v3/objects/deals",
            "params": ["properties"],
            "required": ["properties"]
        },
        "update_deal": {
            "method": "PATCH",
            "endpoint": "/crm/v3/objects/deals/{deal_id}",
            "params": ["deal_id", "properties"],
            "required": ["deal_id", "properties"]
        },
        "delete_deal": {
            "method": "DELETE",
            "endpoint": "/crm/v3/objects/deals/{deal_id}",
            "params": ["deal_id"],
            "required": ["deal_id"]
        },
        
        # Email Operations
        "send_email": {
            "method": "POST",
            "endpoint": "/marketing/v3/transactional/single-send",
            "params": ["emailId", "to", "customProperties"],
            "required": ["emailId", "to"]
        },
        "get_email_campaigns": {
            "method": "GET",
            "endpoint": "/marketing/v3/marketing-emails",
            "params": ["limit", "offset"],
            "required": []
        },
        
        # Properties Operations
        "get_contact_properties": {
            "method": "GET",
            "endpoint": "/crm/v3/properties/contacts",
            "params": ["archived"],
            "required": []
        },
        "create_contact_property": {
            "method": "POST",
            "endpoint": "/crm/v3/properties/contacts",
            "params": ["name", "label", "type", "fieldType", "groupName", "description", "options"],
            "required": ["name", "label", "type", "fieldType", "groupName"]
        },
        
        # Additional CRM Operations
        "get_pipelines": {
            "method": "GET",
            "endpoint": "/crm/v3/pipelines/deals",
            "params": ["archived"],
            "required": []
        },
        "search_contacts": {
            "method": "POST",
            "endpoint": "/crm/v3/objects/contacts/search",
            "params": ["filterGroups", "sorts", "query", "properties", "limit", "after"],
            "required": []
        },
        "search_companies": {
            "method": "POST",
            "endpoint": "/crm/v3/objects/companies/search",
            "params": ["filterGroups", "sorts", "query", "properties", "limit", "after"],
            "required": []
        },
        "search_deals": {
            "method": "POST",
            "endpoint": "/crm/v3/objects/deals/search",
            "params": ["filterGroups", "sorts", "query", "properties", "limit", "after"],
            "required": []
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode()
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the HubSpot node."""
        return NodeSchema(
            name="HubSpotNode",
            description="Comprehensive HubSpot CRM integration supporting contact management, sales pipeline, marketing automation, and business growth operations",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The HubSpot operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                "api_key": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="HubSpot API key (legacy authentication)",
                    required=False
                ),
                "access_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="OAuth 2.0 access token (preferred authentication)",
                    required=False
                ),
                "contact_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Contact ID for contact operations",
                    required=False
                ),
                "company_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Company ID for company operations",
                    required=False
                ),
                "deal_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Deal ID for deal operations",
                    required=False
                ),
                "properties": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Object properties for create/update operations",
                    required=False
                ),
                "limit": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of results to return",
                    required=False
                ),
                "offset": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Number of results to skip",
                    required=False
                ),
                "archived": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Include archived records",
                    required=False
                ),
                "associations": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="List of associations to include",
                    required=False
                ),
                # Email specific
                "emailId": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Email template ID for sending emails",
                    required=False
                ),
                "to": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Email recipient information",
                    required=False
                ),
                "customProperties": NodeParameter(
                    type=NodeParameterType.OBJECT,
                    description="Custom properties for email personalization",
                    required=False
                ),
                # Property creation
                "name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Property name",
                    required=False
                ),
                "label": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Property label",
                    required=False
                ),
                "type": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Property type (string, number, bool, etc.)",
                    required=False
                ),
                "fieldType": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Field type (text, textarea, select, etc.)",
                    required=False
                ),
                "groupName": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Property group name",
                    required=False
                ),
                "description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Property description",
                    required=False
                ),
                "options": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Property options for select fields",
                    required=False
                ),
                # Search parameters
                "filterGroups": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Filter groups for search operations",
                    required=False
                ),
                "sorts": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Sort criteria for search operations",
                    required=False
                ),
                "query": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Search query string",
                    required=False
                ),
                "after": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Pagination cursor",
                    required=False
                )
            },
            outputs={
                "status": NodeParameterType.STRING,
                "contacts": NodeParameterType.ARRAY,
                "contact_info": NodeParameterType.OBJECT,
                "companies": NodeParameterType.ARRAY,
                "company_info": NodeParameterType.OBJECT,
                "deals": NodeParameterType.ARRAY,
                "deal_info": NodeParameterType.OBJECT,
                "properties": NodeParameterType.ARRAY,
                "property_info": NodeParameterType.OBJECT,
                "email_campaigns": NodeParameterType.ARRAY,
                "pipelines": NodeParameterType.ARRAY,
                "search_results": NodeParameterType.ARRAY,
                "total": NodeParameterType.NUMBER,
                "paging": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate HubSpot-specific parameters."""
        params = node_data.get("params", {})
        
        if not params.get("operation"):
            raise NodeValidationError("Operation is required")
        
        if not params.get("api_key") and not params.get("access_token"):
            raise NodeValidationError("Either API key or access token is required")
        
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
        """Execute the HubSpot operation using UniversalRequestNode."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get operation configuration
            operation_config = self.OPERATIONS[operation]
            
            # Prepare authentication - prefer access_token over api_key
            auth_token = params.get("access_token") or params.get("api_key")
            if not auth_token:
                raise NodeValidationError("Authentication token is required")
            
            # Prepare configuration
            config = self.CONFIG.copy()
            
            # For API key authentication, use query parameter instead of header
            if params.get("api_key") and not params.get("access_token"):
                config["authentication"] = {
                    "type": "query_param",
                    "param_name": "hapikey"
                }
            
            # Prepare universal request node parameters
            universal_params = {
                "config": config,
                "method": operation_config["method"],
                "endpoint": operation_config["endpoint"],
                "token": auth_token
            }
            
            # Handle path parameters
            endpoint = operation_config["endpoint"]
            if "{contact_id}" in endpoint:
                endpoint = endpoint.replace("{contact_id}", params.get("contact_id", ""))
            if "{company_id}" in endpoint:
                endpoint = endpoint.replace("{company_id}", params.get("company_id", ""))
            if "{deal_id}" in endpoint:
                endpoint = endpoint.replace("{deal_id}", params.get("deal_id", ""))
            universal_params["endpoint"] = endpoint
            
            # Handle query parameters and body data
            if operation_config["method"] == "GET":
                query_params = {}
                for param in operation_config.get("params", []):
                    if param in params and params[param] is not None:
                        if param in ["limit", "offset"]:
                            query_params[param] = str(params[param])
                        elif param == "properties" and isinstance(params[param], list):
                            query_params["properties"] = ",".join(params[param])
                        elif param == "associations" and isinstance(params[param], list):
                            query_params["associations"] = ",".join(params[param])
                        elif param == "archived":
                            query_params["archived"] = str(params[param]).lower()
                        elif param not in ["contact_id", "company_id", "deal_id"]:
                            query_params[param] = params[param]
                if query_params:
                    universal_params["query_params"] = query_params
            else:
                # POST/PATCH operations - prepare body data
                body_data = {}
                
                if operation.startswith("create_") or operation.startswith("update_"):
                    # For CRM object operations, wrap properties
                    if "properties" in params:
                        body_data["properties"] = params["properties"]
                elif operation == "send_email":
                    # Email sending operations
                    for param in operation_config.get("params", []):
                        if param in params and params[param] is not None:
                            body_data[param] = params[param]
                elif operation == "create_contact_property":
                    # Property creation
                    for param in operation_config.get("params", []):
                        if param in params and params[param] is not None:
                            body_data[param] = params[param]
                elif operation.startswith("search_"):
                    # Search operations
                    for param in operation_config.get("params", []):
                        if param in params and params[param] is not None:
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
                if operation.startswith("get_contacts") or operation == "search_contacts":
                    return {
                        "status": "success",
                        "contacts": response_data.get("results", []),
                        "total": response_data.get("total", 0),
                        "paging": response_data.get("paging", {}),
                        "response_data": response_data
                    }
                elif operation.startswith("get_contact") or operation.startswith("create_contact") or operation.startswith("update_contact"):
                    return {
                        "status": "success",
                        "contact_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_companies") or operation == "search_companies":
                    return {
                        "status": "success",
                        "companies": response_data.get("results", []),
                        "total": response_data.get("total", 0),
                        "paging": response_data.get("paging", {}),
                        "response_data": response_data
                    }
                elif operation.startswith("get_company") or operation.startswith("create_company") or operation.startswith("update_company"):
                    return {
                        "status": "success",
                        "company_info": response_data,
                        "response_data": response_data
                    }
                elif operation.startswith("get_deals") or operation == "search_deals":
                    return {
                        "status": "success",
                        "deals": response_data.get("results", []),
                        "total": response_data.get("total", 0),
                        "paging": response_data.get("paging", {}),
                        "response_data": response_data
                    }
                elif operation.startswith("get_deal") or operation.startswith("create_deal") or operation.startswith("update_deal"):
                    return {
                        "status": "success",
                        "deal_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_email_campaigns":
                    return {
                        "status": "success",
                        "email_campaigns": response_data.get("objects", []),
                        "total": response_data.get("total", 0),
                        "response_data": response_data
                    }
                elif operation == "get_contact_properties":
                    return {
                        "status": "success",
                        "properties": response_data.get("results", []),
                        "response_data": response_data
                    }
                elif operation == "create_contact_property":
                    return {
                        "status": "success",
                        "property_info": response_data,
                        "response_data": response_data
                    }
                elif operation == "get_pipelines":
                    return {
                        "status": "success",
                        "pipelines": response_data.get("results", []),
                        "response_data": response_data
                    }
                elif operation.startswith("search_"):
                    return {
                        "status": "success",
                        "search_results": response_data.get("results", []),
                        "total": response_data.get("total", 0),
                        "paging": response_data.get("paging", {}),
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
            logger.error(f"HubSpot operation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "HUBSPOT_ERROR"
            }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'universal_node'):
            await self.universal_node.close()