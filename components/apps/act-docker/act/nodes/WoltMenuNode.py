"""
Wolt Menu Node - Comprehensive menu management integration for Wolt Menu API
Supports all major Wolt menu operations including menu creation, item inventory updates,
menu item management, and option management.
Uses Wolt Menu REST API with full API coverage.
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

class WoltMenuOperation:
    """All available Wolt Menu operations based on official API documentation."""
    
    # Menu Management Operations
    CREATE_MENU = "create_menu"
    GET_MENU = "get_menu"
    
    # Item Management Operations
    UPDATE_ITEM_INVENTORY = "update_item_inventory"
    UPDATE_MENU_ITEMS = "update_menu_items"
    
    # Option Management Operations
    UPDATE_MENU_OPTIONS = "update_menu_options"

class WoltMenuNode(BaseNode):
    """
    Comprehensive Wolt Menu integration node supporting all major API operations.
    Handles menu creation, item inventory updates, item management, and option management.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url = "https://pos-integration-service.wolt.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Wolt Menu node."""
        return NodeSchema(
            name="WoltMenuNode",
            description="Comprehensive Wolt Menu management integration supporting menu creation, item inventory, and option management",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Wolt Menu operation to perform",
                    required=True,
                    enum=[
                        WoltMenuOperation.CREATE_MENU,
                        WoltMenuOperation.GET_MENU,
                        WoltMenuOperation.UPDATE_ITEM_INVENTORY,
                        WoltMenuOperation.UPDATE_MENU_ITEMS,
                        WoltMenuOperation.UPDATE_MENU_OPTIONS,
                    ]
                ),
                "api_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Wolt Menu API bearer JWT token",
                    required=True
                ),
                "venue_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique venue identifier",
                    required=True
                ),
                
                # Menu Creation Parameters
                "menu_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Optional menu ID for menu creation",
                    required=False
                ),
                "currency": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Three-letter ISO 4217 currency code (required for menu creation)",
                    required=False
                ),
                "primary_language": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Two-letter ISO 639-1 language code (required for menu creation)",
                    required=False
                ),
                "categories": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of menu categories with items (required for menu creation)",
                    required=False
                ),
                
                # Item Management Parameters
                "items": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of items for inventory/item updates",
                    required=False
                ),
                "item_sku": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="SKU identifier for single item operations",
                    required=False
                ),
                "item_gtin": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="GTIN identifier for single item operations",
                    required=False
                ),
                "item_external_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="External ID for single item operations",
                    required=False
                ),
                "inventory_quantity": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Inventory quantity for single item operations",
                    required=False
                ),
                "item_price": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Item price for item updates",
                    required=False
                ),
                "item_visibility": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Item visibility status for item updates",
                    required=False
                ),
                
                # Option Management Parameters
                "option_values": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of option values for option updates",
                    required=False
                ),
                "option_external_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="External ID for single option operations",
                    required=False
                ),
                "option_price": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Option price for option updates",
                    required=False
                ),
                "option_visibility": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Option visibility status for option updates",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "menu_resource_url": NodeParameterType.STRING,
                "menu_data": NodeParameterType.OBJECT,
                "updated_items_count": NodeParameterType.NUMBER,
                "updated_options_count": NodeParameterType.NUMBER,
                "venue_id": NodeParameterType.STRING,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Wolt Menu-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate API token
        if not params.get("api_token"):
            raise NodeValidationError("Wolt Menu API token is required")
        
        # Always validate venue ID
        if not params.get("venue_id"):
            raise NodeValidationError("venue_id is required for all menu operations")
        
        # Validate operation-specific requirements
        if operation == WoltMenuOperation.CREATE_MENU:
            if not params.get("currency"):
                raise NodeValidationError("currency is required for menu creation")
            if not params.get("primary_language"):
                raise NodeValidationError("primary_language is required for menu creation")
            if not params.get("categories"):
                raise NodeValidationError("categories are required for menu creation")
        
        # Validate item operations
        item_ops = [WoltMenuOperation.UPDATE_ITEM_INVENTORY, WoltMenuOperation.UPDATE_MENU_ITEMS]
        if operation in item_ops:
            has_bulk_items = params.get("items")
            has_single_item = any([
                params.get("item_sku"),
                params.get("item_gtin"),
                params.get("item_external_id")
            ])
            
            if not has_bulk_items and not has_single_item:
                raise NodeValidationError("Either 'items' array or single item identifier (sku/gtin/external_id) is required for item operations")
        
        # Validate option operations
        if operation == WoltMenuOperation.UPDATE_MENU_OPTIONS:
            has_bulk_options = params.get("option_values")
            has_single_option = params.get("option_external_id")
            
            if not has_bulk_options and not has_single_option:
                raise NodeValidationError("Either 'option_values' array or 'option_external_id' is required for option operations")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Wolt Menu operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['api_token']}",
                "Content-Type": "application/json",
                "User-Agent": "WoltMenuNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == WoltMenuOperation.CREATE_MENU:
                return await self._create_menu(params, headers)
            elif operation == WoltMenuOperation.GET_MENU:
                return await self._get_menu(params, headers)
            elif operation == WoltMenuOperation.UPDATE_ITEM_INVENTORY:
                return await self._update_item_inventory(params, headers)
            elif operation == WoltMenuOperation.UPDATE_MENU_ITEMS:
                return await self._update_menu_items(params, headers)
            elif operation == WoltMenuOperation.UPDATE_MENU_OPTIONS:
                return await self._update_menu_options(params, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in WoltMenuNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _create_menu(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Create or replace menu for a venue."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/v1/restaurants/{venue_id}/menu"
            
            payload = {
                "currency": params["currency"],
                "primary_language": params["primary_language"],
                "categories": params["categories"]
            }
            
            # Add optional menu ID
            if params.get("menu_id"):
                payload["id"] = params["menu_id"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 202:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "create_menu",
                            "message": "Menu creation request accepted",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create menu"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create menu: {str(e)}")
    
    async def _get_menu(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Get menu information for a venue."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/v2/venues/{venue_id}/menu"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "get_menu",
                            "menu_resource_url": response_data.get("resource_url"),
                            "menu_data": response_data,
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get menu"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get menu: {str(e)}")
    
    async def _update_item_inventory(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update item inventory for venue items."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/items/inventory"
            
            # Prepare items for update
            items_to_update = []
            
            if params.get("items"):
                # Bulk update
                items_to_update = params["items"]
            else:
                # Single item update
                single_item = {}
                
                # Add identifier
                if params.get("item_sku"):
                    single_item["sku"] = params["item_sku"]
                elif params.get("item_gtin"):
                    single_item["gtin"] = params["item_gtin"]
                elif params.get("item_external_id"):
                    single_item["external_id"] = params["item_external_id"]
                
                # Add inventory quantity
                if params.get("inventory_quantity") is not None:
                    single_item["inventory_quantity"] = params["inventory_quantity"]
                
                items_to_update = [single_item]
            
            payload = {"items": items_to_update}
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 202:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "update_item_inventory",
                            "updated_items_count": len(items_to_update),
                            "message": "Item inventory update request accepted",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update item inventory"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update item inventory: {str(e)}")
    
    async def _update_menu_items(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update menu items for venue."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/items"
            
            # Prepare items for update
            items_to_update = []
            
            if params.get("items"):
                # Bulk update
                items_to_update = params["items"]
            else:
                # Single item update
                single_item = {}
                
                # Add identifier
                if params.get("item_sku"):
                    single_item["sku"] = params["item_sku"]
                elif params.get("item_gtin"):
                    single_item["gtin"] = params["item_gtin"]
                elif params.get("item_external_id"):
                    single_item["external_id"] = params["item_external_id"]
                
                # Add optional fields
                if params.get("item_price") is not None:
                    single_item["price"] = params["item_price"]
                if params.get("item_visibility") is not None:
                    single_item["visibility"] = params["item_visibility"]
                
                items_to_update = [single_item]
            
            payload = {"items": items_to_update}
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 202:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "update_menu_items",
                            "updated_items_count": len(items_to_update),
                            "message": "Menu items update request accepted",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update menu items"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update menu items: {str(e)}")
    
    async def _update_menu_options(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update menu options for venue."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/options/values"
            
            # Prepare options for update
            options_to_update = []
            
            if params.get("option_values"):
                # Bulk update
                options_to_update = params["option_values"]
            else:
                # Single option update
                single_option = {}
                
                # Add identifier
                if params.get("option_external_id"):
                    single_option["external_id"] = params["option_external_id"]
                
                # Add optional fields
                if params.get("option_price") is not None:
                    single_option["price"] = params["option_price"]
                if params.get("option_visibility") is not None:
                    single_option["visibility"] = params["option_visibility"]
                
                options_to_update = [single_option]
            
            payload = {"option_values": options_to_update}
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 202:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "update_menu_options",
                            "updated_options_count": len(options_to_update),
                            "message": "Menu options update request accepted",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update menu options"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update menu options: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "venue_id": None,
            "operation_type": None,
            "menu_resource_url": None,
            "menu_data": None,
            "updated_items_count": None,
            "updated_options_count": None,
            "response_data": None
        }

class WoltMenuHelpers:
    """Helper functions for Wolt Menu operations."""
    
    @staticmethod
    def validate_currency_code(currency: str) -> bool:
        """Validate ISO 4217 currency code format."""
        import re
        return bool(re.match(r'^[A-Z]{3}$', currency))
    
    @staticmethod
    def validate_language_code(language: str) -> bool:
        """Validate ISO 639-1 language code format."""
        import re
        return bool(re.match(r'^[a-z]{2}$', language))
    
    @staticmethod
    def create_menu_category(name: str, items: List[Dict[str, Any]], 
                           external_id: str = None, position: int = None) -> Dict[str, Any]:
        """Create a properly formatted menu category."""
        category = {
            "name": name,
            "items": items
        }
        
        if external_id:
            category["external_id"] = external_id
        if position is not None:
            category["position"] = position
            
        return category
    
    @staticmethod
    def create_menu_item(name: str, price: float, external_id: str = None, 
                        sku: str = None, gtin: str = None, **kwargs) -> Dict[str, Any]:
        """Create a properly formatted menu item."""
        item = {
            "name": name,
            "price": price
        }
        
        if external_id:
            item["external_id"] = external_id
        if sku:
            item["sku"] = sku
        if gtin:
            item["gtin"] = gtin
            
        # Add any additional fields
        for key, value in kwargs.items():
            if value is not None:
                item[key] = value
                
        return item
    
    @staticmethod
    def create_inventory_update(identifier_type: str, identifier_value: str, 
                              quantity: int) -> Dict[str, Any]:
        """Create a properly formatted inventory update."""
        update = {
            identifier_type: identifier_value,
            "inventory_quantity": quantity
        }
        return update
    
    @staticmethod
    def validate_item_identifier(sku: str = None, gtin: str = None, 
                                external_id: str = None) -> bool:
        """Validate that at least one item identifier is provided."""
        return any([sku, gtin, external_id])
    
    @staticmethod
    def format_price(price: Union[int, float]) -> float:
        """Format price to proper decimal format."""
        return round(float(price), 2)
    
    @staticmethod
    def validate_menu_structure(menu_data: Dict[str, Any]) -> List[str]:
        """Validate menu structure and return list of validation errors."""
        errors = []
        
        # Check required fields
        if not menu_data.get("currency"):
            errors.append("Missing required field: currency")
        if not menu_data.get("primary_language"):
            errors.append("Missing required field: primary_language")
        if not menu_data.get("categories"):
            errors.append("Missing required field: categories")
        
        # Validate currency format
        if menu_data.get("currency") and not WoltMenuHelpers.validate_currency_code(menu_data["currency"]):
            errors.append("Invalid currency code format (must be 3-letter ISO 4217)")
        
        # Validate language format
        if menu_data.get("primary_language") and not WoltMenuHelpers.validate_language_code(menu_data["primary_language"]):
            errors.append("Invalid language code format (must be 2-letter ISO 639-1)")
        
        # Validate categories structure
        categories = menu_data.get("categories", [])
        if not isinstance(categories, list):
            errors.append("Categories must be an array")
        elif len(categories) == 0:
            errors.append("At least one category is required")
        
        return errors