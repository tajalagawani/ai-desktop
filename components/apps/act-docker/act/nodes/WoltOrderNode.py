"""
Wolt Order Node - Comprehensive order management integration for Wolt Order API
Supports all major Wolt order operations including order retrieval, status management,
self-delivery operations, and order modifications.
Uses Wolt Order REST API with full API coverage.
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

class WoltOrderOperation:
    """All available Wolt Order operations based on official API documentation."""
    
    # Order Retrieval Operations
    GET_ORDER = "get_order"
    GET_ORDER_V2 = "get_order_v2"
    
    # Order Status Management Operations
    ACCEPT_ORDER = "accept_order"
    REJECT_ORDER = "reject_order"
    MARK_ORDER_READY = "mark_order_ready"
    MARK_ORDER_DELIVERED = "mark_order_delivered"
    CONFIRM_PREORDER = "confirm_preorder"
    
    # Self-Delivery Operations
    ACCEPT_SELF_DELIVERY = "accept_self_delivery"
    MARK_PICKUP_COMPLETED = "mark_pickup_completed"
    MARK_COURIER_AT_CUSTOMER = "mark_courier_at_customer"
    UPDATE_DELIVERY_LOCATION = "update_delivery_location"
    UPDATE_DELIVERY_ETA = "update_delivery_eta"
    
    # Order Modification Operations
    REPLACE_ORDER_ITEMS = "replace_order_items"
    MARK_SENT_TO_POS = "mark_sent_to_pos"
    MARK_DEPOSITS_RETURNED = "mark_deposits_returned"

class WoltOrderStatus:
    """Available Wolt order statuses."""
    
    RECEIVED = "received"
    FETCHED = "fetched"
    ACKNOWLEDGED = "acknowledged"
    PRODUCTION = "production"
    READY = "ready"
    DELIVERED = "delivered"
    REJECTED = "rejected"
    REFUNDED = "refunded"

class WoltOrderType:
    """Available Wolt order types."""
    
    INSTANT = "instant"
    PREORDER = "preorder"

class WoltOrderNode(BaseNode):
    """
    Comprehensive Wolt Order integration node supporting all major API operations.
    Handles order retrieval, status management, self-delivery operations, and order modifications.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url = "https://pos-integration-service.wolt.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Wolt Order node."""
        return NodeSchema(
            name="WoltOrderNode",
            description="Comprehensive Wolt Order management integration supporting order lifecycle, status management, and self-delivery operations",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Wolt Order operation to perform",
                    required=True,
                    enum=[
                        WoltOrderOperation.GET_ORDER,
                        WoltOrderOperation.GET_ORDER_V2,
                        WoltOrderOperation.ACCEPT_ORDER,
                        WoltOrderOperation.REJECT_ORDER,
                        WoltOrderOperation.MARK_ORDER_READY,
                        WoltOrderOperation.MARK_ORDER_DELIVERED,
                        WoltOrderOperation.CONFIRM_PREORDER,
                        WoltOrderOperation.ACCEPT_SELF_DELIVERY,
                        WoltOrderOperation.MARK_PICKUP_COMPLETED,
                        WoltOrderOperation.MARK_COURIER_AT_CUSTOMER,
                        WoltOrderOperation.UPDATE_DELIVERY_LOCATION,
                        WoltOrderOperation.UPDATE_DELIVERY_ETA,
                        WoltOrderOperation.REPLACE_ORDER_ITEMS,
                        WoltOrderOperation.MARK_SENT_TO_POS,
                        WoltOrderOperation.MARK_DEPOSITS_RETURNED,
                    ]
                ),
                "api_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Wolt Order API bearer JWT token",
                    required=True
                ),
                "order_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique order identifier",
                    required=True
                ),
                
                # Order Status Management Parameters
                "rejection_reason": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Reason for order rejection",
                    required=False
                ),
                "estimated_preparation_time": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Estimated preparation time in minutes",
                    required=False
                ),
                
                # Self-Delivery Parameters
                "courier_latitude": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Courier current latitude",
                    required=False
                ),
                "courier_longitude": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Courier current longitude",
                    required=False
                ),
                "delivery_eta": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Estimated delivery time in ISO format",
                    required=False
                ),
                "courier_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Courier name for self-delivery",
                    required=False
                ),
                "courier_phone": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Courier phone number for self-delivery",
                    required=False
                ),
                
                # Order Modification Parameters
                "replacement_items": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of replacement items for order modification",
                    required=False
                ),
                "reason_for_replacement": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Reason for item replacement",
                    required=False
                ),
                "refund_amount": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Refund amount for item replacements",
                    required=False
                ),
                
                # Additional Parameters
                "notes": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Additional notes for the operation",
                    required=False
                ),
                "pos_reference": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="POS system reference number",
                    required=False
                ),
                "delivery_instructions": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Special delivery instructions",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "order_id": NodeParameterType.STRING,
                "order_status": NodeParameterType.STRING,
                "order_type": NodeParameterType.STRING,
                "order_data": NodeParameterType.OBJECT,
                "venue_info": NodeParameterType.OBJECT,
                "customer_info": NodeParameterType.OBJECT,
                "items": NodeParameterType.ARRAY,
                "price_info": NodeParameterType.OBJECT,
                "delivery_info": NodeParameterType.OBJECT,
                "operation_type": NodeParameterType.STRING,
                "estimated_ready_time": NodeParameterType.STRING,
                "courier_info": NodeParameterType.OBJECT,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Wolt Order-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate API token
        if not params.get("api_token"):
            raise NodeValidationError("Wolt Order API token is required")
        
        # Always validate order ID
        if not params.get("order_id"):
            raise NodeValidationError("order_id is required for all order operations")
        
        # Validate operation-specific requirements
        if operation == WoltOrderOperation.REJECT_ORDER:
            if not params.get("rejection_reason"):
                raise NodeValidationError("rejection_reason is required for order rejection")
        
        # Validate self-delivery location operations
        location_ops = [WoltOrderOperation.UPDATE_DELIVERY_LOCATION]
        if operation in location_ops:
            if not all([params.get("courier_latitude"), params.get("courier_longitude")]):
                raise NodeValidationError("courier_latitude and courier_longitude are required for location updates")
        
        # Validate ETA operations
        if operation == WoltOrderOperation.UPDATE_DELIVERY_ETA:
            if not params.get("delivery_eta"):
                raise NodeValidationError("delivery_eta is required for ETA updates")
        
        # Validate item replacement operations
        if operation == WoltOrderOperation.REPLACE_ORDER_ITEMS:
            if not params.get("replacement_items"):
                raise NodeValidationError("replacement_items are required for item replacement")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Wolt Order operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['api_token']}",
                "Content-Type": "application/json",
                "User-Agent": "WoltOrderNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == WoltOrderOperation.GET_ORDER:
                return await self._get_order(params, headers)
            elif operation == WoltOrderOperation.GET_ORDER_V2:
                return await self._get_order_v2(params, headers)
            elif operation == WoltOrderOperation.ACCEPT_ORDER:
                return await self._accept_order(params, headers)
            elif operation == WoltOrderOperation.REJECT_ORDER:
                return await self._reject_order(params, headers)
            elif operation == WoltOrderOperation.MARK_ORDER_READY:
                return await self._mark_order_ready(params, headers)
            elif operation == WoltOrderOperation.MARK_ORDER_DELIVERED:
                return await self._mark_order_delivered(params, headers)
            elif operation == WoltOrderOperation.CONFIRM_PREORDER:
                return await self._confirm_preorder(params, headers)
            elif operation == WoltOrderOperation.ACCEPT_SELF_DELIVERY:
                return await self._accept_self_delivery(params, headers)
            elif operation == WoltOrderOperation.MARK_PICKUP_COMPLETED:
                return await self._mark_pickup_completed(params, headers)
            elif operation == WoltOrderOperation.MARK_COURIER_AT_CUSTOMER:
                return await self._mark_courier_at_customer(params, headers)
            elif operation == WoltOrderOperation.UPDATE_DELIVERY_LOCATION:
                return await self._update_delivery_location(params, headers)
            elif operation == WoltOrderOperation.UPDATE_DELIVERY_ETA:
                return await self._update_delivery_eta(params, headers)
            elif operation == WoltOrderOperation.REPLACE_ORDER_ITEMS:
                return await self._replace_order_items(params, headers)
            elif operation == WoltOrderOperation.MARK_SENT_TO_POS:
                return await self._mark_sent_to_pos(params, headers)
            elif operation == WoltOrderOperation.MARK_DEPOSITS_RETURNED:
                return await self._mark_deposits_returned(params, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in WoltOrderNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _get_order(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Get order details using v1 API."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "get_order",
                            "order_status": response_data.get("order_status"),
                            "order_type": response_data.get("type"),
                            "order_data": response_data,
                            "venue_info": response_data.get("venue"),
                            "customer_info": response_data.get("customer"),
                            "items": response_data.get("items", []),
                            "price_info": response_data.get("price"),
                            "delivery_info": response_data.get("delivery"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get order: {str(e)}")
    
    async def _get_order_v2(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Get order details using v2 API."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/v2/orders/{order_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "get_order_v2",
                            "order_status": response_data.get("order_status"),
                            "order_type": response_data.get("type"),
                            "order_data": response_data,
                            "venue_info": response_data.get("venue"),
                            "customer_info": response_data.get("customer"),
                            "items": response_data.get("items", []),
                            "price_info": response_data.get("price"),
                            "delivery_info": response_data.get("delivery"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get order: {str(e)}")
    
    async def _accept_order(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Accept an order."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/accept"
            
            payload = {}
            
            # Add optional preparation time
            if params.get("estimated_preparation_time"):
                payload["estimated_preparation_time"] = params["estimated_preparation_time"]
            
            # Add optional notes
            if params.get("notes"):
                payload["notes"] = params["notes"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "accept_order",
                            "order_status": WoltOrderStatus.ACKNOWLEDGED,
                            "estimated_ready_time": params.get("estimated_preparation_time"),
                            "message": "Order accepted successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to accept order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to accept order: {str(e)}")
    
    async def _reject_order(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Reject an order."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/reject"
            
            payload = {
                "reason": params["rejection_reason"]
            }
            
            # Add optional notes
            if params.get("notes"):
                payload["notes"] = params["notes"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "reject_order",
                            "order_status": WoltOrderStatus.REJECTED,
                            "rejection_reason": params["rejection_reason"],
                            "message": "Order rejected successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to reject order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to reject order: {str(e)}")
    
    async def _mark_order_ready(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Mark order as ready for pickup/delivery."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/ready"
            
            payload = {}
            
            # Add optional notes
            if params.get("notes"):
                payload["notes"] = params["notes"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "mark_order_ready",
                            "order_status": WoltOrderStatus.READY,
                            "message": "Order marked as ready",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to mark order ready"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to mark order ready: {str(e)}")
    
    async def _mark_order_delivered(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Mark order as delivered."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/delivered"
            
            payload = {}
            
            # Add optional notes
            if params.get("notes"):
                payload["notes"] = params["notes"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "mark_order_delivered",
                            "order_status": WoltOrderStatus.DELIVERED,
                            "message": "Order marked as delivered",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to mark order delivered"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to mark order delivered: {str(e)}")
    
    async def _confirm_preorder(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Confirm a preorder."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/confirm-preorder"
            
            payload = {}
            
            # Add optional preparation time
            if params.get("estimated_preparation_time"):
                payload["estimated_preparation_time"] = params["estimated_preparation_time"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "confirm_preorder",
                            "order_type": WoltOrderType.PREORDER,
                            "estimated_ready_time": params.get("estimated_preparation_time"),
                            "message": "Preorder confirmed successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to confirm preorder"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to confirm preorder: {str(e)}")
    
    async def _accept_self_delivery(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Accept order for self-delivery."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/self-delivery/accept"
            
            payload = {}
            
            # Add courier information
            if params.get("courier_name"):
                payload["courier_name"] = params["courier_name"]
            if params.get("courier_phone"):
                payload["courier_phone"] = params["courier_phone"]
            if params.get("estimated_preparation_time"):
                payload["estimated_preparation_time"] = params["estimated_preparation_time"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "accept_self_delivery",
                            "order_status": WoltOrderStatus.ACKNOWLEDGED,
                            "courier_info": {
                                "name": params.get("courier_name"),
                                "phone": params.get("courier_phone")
                            },
                            "message": "Self-delivery order accepted",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to accept self-delivery order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to accept self-delivery order: {str(e)}")
    
    async def _mark_pickup_completed(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Mark pickup as completed for self-delivery."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/pickup-completed"
            
            payload = {}
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "mark_pickup_completed",
                            "message": "Pickup marked as completed",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to mark pickup completed"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to mark pickup completed: {str(e)}")
    
    async def _mark_courier_at_customer(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Mark courier as arrived at customer location."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/courier-at-customer"
            
            payload = {}
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "mark_courier_at_customer",
                            "message": "Courier marked as arrived at customer",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to mark courier at customer"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to mark courier at customer: {str(e)}")
    
    async def _update_delivery_location(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update courier delivery location."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/delivery/tracking/location"
            
            payload = {
                "latitude": params["courier_latitude"],
                "longitude": params["courier_longitude"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "update_delivery_location",
                            "courier_info": {
                                "latitude": params["courier_latitude"],
                                "longitude": params["courier_longitude"]
                            },
                            "message": "Delivery location updated",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update delivery location"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update delivery location: {str(e)}")
    
    async def _update_delivery_eta(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update delivery ETA."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/delivery/eta"
            
            payload = {
                "eta": params["delivery_eta"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "update_delivery_eta",
                            "delivery_eta": params["delivery_eta"],
                            "message": "Delivery ETA updated",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update delivery ETA"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update delivery ETA: {str(e)}")
    
    async def _replace_order_items(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Replace items in an order."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/replace-items"
            
            payload = {
                "items": params["replacement_items"]
            }
            
            # Add optional fields
            if params.get("reason_for_replacement"):
                payload["reason"] = params["reason_for_replacement"]
            if params.get("refund_amount"):
                payload["refund_amount"] = params["refund_amount"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "replace_order_items",
                            "replacement_items": params["replacement_items"],
                            "refund_amount": params.get("refund_amount"),
                            "message": "Order items replaced successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to replace order items"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to replace order items: {str(e)}")
    
    async def _mark_sent_to_pos(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Mark order as sent to POS system."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/sent-to-pos"
            
            payload = {}
            
            # Add optional POS reference
            if params.get("pos_reference"):
                payload["pos_reference"] = params["pos_reference"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "mark_sent_to_pos",
                            "pos_reference": params.get("pos_reference"),
                            "message": "Order marked as sent to POS",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to mark order sent to POS"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to mark order sent to POS: {str(e)}")
    
    async def _mark_deposits_returned(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Mark deposits as returned for an order."""
        try:
            order_id = params["order_id"]
            url = f"{self.base_url}/orders/{order_id}/deposits-returned"
            
            payload = {}
            
            # Add optional notes
            if params.get("notes"):
                payload["notes"] = params["notes"]
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "operation_type": "mark_deposits_returned",
                            "message": "Deposits marked as returned",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to mark deposits returned"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to mark deposits returned: {str(e)}")
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "order_id": None,
            "order_status": None,
            "order_type": None,
            "order_data": None,
            "venue_info": None,
            "customer_info": None,
            "items": None,
            "price_info": None,
            "delivery_info": None,
            "operation_type": None,
            "estimated_ready_time": None,
            "courier_info": None,
            "response_data": None
        }

class WoltOrderHelpers:
    """Helper functions for Wolt Order operations."""
    
    @staticmethod
    def validate_order_status_transition(current_status: str, target_status: str) -> bool:
        """Validate if order status transition is allowed."""
        valid_transitions = {
            WoltOrderStatus.RECEIVED: [WoltOrderStatus.ACKNOWLEDGED, WoltOrderStatus.REJECTED],
            WoltOrderStatus.FETCHED: [WoltOrderStatus.ACKNOWLEDGED, WoltOrderStatus.REJECTED],
            WoltOrderStatus.ACKNOWLEDGED: [WoltOrderStatus.PRODUCTION, WoltOrderStatus.REJECTED],
            WoltOrderStatus.PRODUCTION: [WoltOrderStatus.READY],
            WoltOrderStatus.READY: [WoltOrderStatus.DELIVERED],
        }
        
        allowed_targets = valid_transitions.get(current_status, [])
        return target_status in allowed_targets
    
    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as ISO string for ETA updates."""
        return dt.isoformat()
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate latitude and longitude coordinates."""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    @staticmethod
    def create_replacement_item(item_id: str, quantity: int, reason: str = None) -> Dict[str, Any]:
        """Create a properly formatted replacement item."""
        item = {
            "item_id": item_id,
            "quantity": quantity
        }
        
        if reason:
            item["reason"] = reason
            
        return item
    
    @staticmethod
    def calculate_preparation_time(item_count: int, complexity_factor: float = 1.0) -> int:
        """Calculate estimated preparation time based on item count and complexity."""
        base_time = 5  # Base preparation time in minutes
        time_per_item = 2  # Additional time per item
        
        estimated_time = base_time + (item_count * time_per_item * complexity_factor)
        return max(int(estimated_time), 5)  # Minimum 5 minutes
    
    @staticmethod
    def parse_order_type(order_data: Dict[str, Any]) -> str:
        """Parse and return order type from order data."""
        return order_data.get("type", WoltOrderType.INSTANT)
    
    @staticmethod
    def extract_customer_info(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract customer information from order data."""
        customer = order_data.get("customer", {})
        return {
            "name": customer.get("name"),
            "phone": customer.get("phone"),
            "email": customer.get("email"),
            "address": customer.get("address")
        }
    
    @staticmethod
    def extract_delivery_info(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract delivery information from order data."""
        delivery = order_data.get("delivery", {})
        return {
            "method": delivery.get("method"),
            "address": delivery.get("address"),
            "instructions": delivery.get("instructions"),
            "eta": delivery.get("eta")
        }