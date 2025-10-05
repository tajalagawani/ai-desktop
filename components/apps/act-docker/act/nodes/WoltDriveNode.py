"""
Wolt Drive Node - Comprehensive delivery integration for Wolt Drive API
Supports all major Wolt Drive operations including shipment promises, delivery orders,
delivery fee estimation, and both venueful and venueless delivery approaches.
Uses Wolt Drive REST API with full API coverage.
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import aiohttp
import time

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

class WoltDriveOperation:
    """All available Wolt Drive operations based on official API documentation."""
    
    # Venueful Operations
    CREATE_SHIPMENT_PROMISE_VENUEFUL = "create_shipment_promise_venueful"
    CREATE_DELIVERY_ORDER_VENUEFUL = "create_delivery_order_venueful"
    GET_AVAILABLE_VENUES = "get_available_venues"
    
    # Venueless Operations
    ESTIMATE_DELIVERY_FEE_VENUELESS = "estimate_delivery_fee_venueless"
    CREATE_DELIVERY_ORDER_VENUELESS = "create_delivery_order_venueless"
    
    # Order Management Operations
    GET_DELIVERY_HANDSHAKE = "get_delivery_handshake"
    CANCEL_DELIVERY = "cancel_delivery"

class WoltDriveNode(BaseNode):
    """
    Comprehensive Wolt Drive integration node supporting all major API operations.
    Handles delivery promises, order creation, fee estimation, and delivery tracking.
    
    Supports both venueful (pre-configured venues) and venueless approaches.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url_prod = "https://daas-public-api.wolt.com"
        self.base_url_staging = "https://daas-public-api.development.dev.woltapi.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Wolt Drive node."""
        return NodeSchema(
            name="WoltDriveNode",
            description="Comprehensive Wolt Drive delivery integration supporting shipment promises, delivery orders, fee estimation, and tracking",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Wolt Drive operation to perform",
                    required=True,
                    enum=[
                        WoltDriveOperation.CREATE_SHIPMENT_PROMISE_VENUEFUL,
                        WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUEFUL,
                        WoltDriveOperation.ESTIMATE_DELIVERY_FEE_VENUELESS,
                        WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUELESS,
                        WoltDriveOperation.GET_AVAILABLE_VENUES,
                        WoltDriveOperation.GET_DELIVERY_HANDSHAKE,
                        WoltDriveOperation.CANCEL_DELIVERY,
                    ]
                ),
                "api_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Wolt Drive API bearer token",
                    required=True
                ),
                "environment": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="API environment (production or staging)",
                    required=False,
                    default="production",
                    enum=["production", "staging"]
                ),
                
                # Venue Configuration
                "venue_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Venue ID for venueful operations",
                    required=False
                ),
                "merchant_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Merchant ID for venueless operations",
                    required=False
                ),
                
                # Delivery Location Parameters
                "pickup_street": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Pickup street address",
                    required=False
                ),
                "pickup_city": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Pickup city",
                    required=False
                ),
                "pickup_post_code": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Pickup postal code",
                    required=False
                ),
                "pickup_latitude": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Pickup location latitude",
                    required=False
                ),
                "pickup_longitude": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Pickup location longitude",
                    required=False
                ),
                "dropoff_street": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Delivery street address",
                    required=False
                ),
                "dropoff_city": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Delivery city",
                    required=False
                ),
                "dropoff_post_code": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Delivery postal code",
                    required=False
                ),
                "dropoff_latitude": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Delivery location latitude",
                    required=False
                ),
                "dropoff_longitude": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Delivery location longitude",
                    required=False
                ),
                
                # Delivery Details
                "scheduled_dropoff_time": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Scheduled delivery time in ISO format (optional)",
                    required=False
                ),
                "delivery_instructions": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Special delivery instructions",
                    required=False
                ),
                "contact_less_delivery": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to use contact-less delivery",
                    required=False,
                    default=False
                ),
                "cash_on_delivery": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether cash on delivery is required",
                    required=False,
                    default=False
                ),
                
                # Parcel Information
                "parcel_weight": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Parcel weight in grams",
                    required=False
                ),
                "parcel_height": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Parcel height in cm",
                    required=False
                ),
                "parcel_width": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Parcel width in cm",
                    required=False
                ),
                "parcel_length": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Parcel length in cm",
                    required=False
                ),
                "parcel_description": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Description of the parcel contents",
                    required=False
                ),
                
                # Order Information
                "order_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="External order ID for tracking",
                    required=False
                ),
                "delivery_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Wolt delivery ID for status operations",
                    required=False
                ),
                "shipment_promise_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Shipment promise ID from previous promise request",
                    required=False
                ),
                
                # Customer Information
                "customer_name": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Customer full name",
                    required=False
                ),
                "customer_phone": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Customer phone number",
                    required=False
                ),
                "customer_email": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Customer email address",
                    required=False
                ),
                
                # Additional Options
                "return_to_sender": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to return package to sender if delivery fails",
                    required=False,
                    default=False
                ),
                "priority_delivery": NodeParameter(
                    type=NodeParameterType.BOOLEAN,
                    description="Whether this is a priority delivery",
                    required=False,
                    default=False
                ),
                "value_of_goods": NodeParameter(
                    type=NodeParameterType.NUMBER,
                    description="Value of goods being delivered (for insurance)",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "delivery_id": NodeParameterType.STRING,
                "shipment_promise_id": NodeParameterType.STRING,
                "estimated_delivery_time": NodeParameterType.STRING,
                "estimated_delivery_fee": NodeParameterType.NUMBER,
                "tracking_url": NodeParameterType.STRING,
                "delivery_status": NodeParameterType.STRING,
                "venues": NodeParameterType.ARRAY,
                "venue_count": NodeParameterType.NUMBER,
                "handshake_pin": NodeParameterType.STRING,
                "pin_verification_enabled": NodeParameterType.BOOLEAN,
                "order_id": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Wolt Drive-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate API token
        if not params.get("api_token"):
            raise NodeValidationError("Wolt Drive API token is required")
        
        # Validate operation-specific requirements
        if operation in [WoltDriveOperation.CREATE_SHIPMENT_PROMISE_VENUEFUL, 
                        WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUEFUL]:
            if not params.get("venue_id"):
                raise NodeValidationError("venue_id is required for venueful operations")
        
        if operation in [WoltDriveOperation.ESTIMATE_DELIVERY_FEE_VENUELESS,
                        WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUELESS]:
            if not params.get("merchant_id"):
                raise NodeValidationError("merchant_id is required for venueless operations")
        
        # Validate location requirements for delivery operations
        delivery_ops = [
            WoltDriveOperation.CREATE_SHIPMENT_PROMISE_VENUEFUL,
            WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUEFUL,
            WoltDriveOperation.ESTIMATE_DELIVERY_FEE_VENUELESS,
            WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUELESS
        ]
        
        if operation in delivery_ops:
            # Validate dropoff location
            if not all([params.get("dropoff_street"), params.get("dropoff_city")]):
                raise NodeValidationError("dropoff_street and dropoff_city are required for delivery operations")
        
        # Validate merchant ID for venue operations
        if operation == WoltDriveOperation.GET_AVAILABLE_VENUES:
            if not params.get("merchant_id"):
                raise NodeValidationError("merchant_id is required for available venues operation")
        
        # Validate order ID for handshake operations
        if operation == WoltDriveOperation.GET_DELIVERY_HANDSHAKE:
            if not params.get("order_id"):
                raise NodeValidationError("order_id is required for handshake operations")
        
        # Validate delivery ID for cancel operations
        if operation == WoltDriveOperation.CANCEL_DELIVERY:
            if not params.get("delivery_id"):
                raise NodeValidationError("delivery_id is required for cancel delivery operation")
        
        # Validate shipment promise ID for venueful delivery order creation
        if operation == WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUEFUL:
            if not params.get("shipment_promise_id"):
                raise NodeValidationError("shipment_promise_id is required for venueful delivery order creation")
        
        return params
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Wolt Drive operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Get base URL based on environment
            base_url = self.base_url_prod if params.get("environment", "production") == "production" else self.base_url_staging
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['api_token']}",
                "Content-Type": "application/json",
                "User-Agent": "WoltDriveNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == WoltDriveOperation.CREATE_SHIPMENT_PROMISE_VENUEFUL:
                return await self._create_shipment_promise_venueful(params, base_url, headers)
            elif operation == WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUEFUL:
                return await self._create_delivery_order_venueful(params, base_url, headers)
            elif operation == WoltDriveOperation.ESTIMATE_DELIVERY_FEE_VENUELESS:
                return await self._estimate_delivery_fee_venueless(params, base_url, headers)
            elif operation == WoltDriveOperation.CREATE_DELIVERY_ORDER_VENUELESS:
                return await self._create_delivery_order_venueless(params, base_url, headers)
            elif operation == WoltDriveOperation.GET_AVAILABLE_VENUES:
                return await self._get_available_venues(params, base_url, headers)
            elif operation == WoltDriveOperation.GET_DELIVERY_HANDSHAKE:
                return await self._get_delivery_handshake(params, base_url, headers)
            elif operation == WoltDriveOperation.CANCEL_DELIVERY:
                return await self._cancel_delivery(params, base_url, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in WoltDriveNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _create_shipment_promise_venueful(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a shipment promise for venueful delivery."""
        try:
            venue_id = params["venue_id"]
            url = f"{base_url}/v1/venues/{venue_id}/shipment-promises"
            
            payload = {
                "dropoff": {
                    "location": {
                        "street": params["dropoff_street"],
                        "city": params["dropoff_city"]
                    }
                }
            }
            
            # Add optional location details
            if params.get("dropoff_post_code"):
                payload["dropoff"]["location"]["postcode"] = params["dropoff_post_code"]
            
            if params.get("dropoff_latitude") and params.get("dropoff_longitude"):
                payload["dropoff"]["location"]["coordinates"] = {
                    "lat": params["dropoff_latitude"],
                    "lon": params["dropoff_longitude"]
                }
            
            # Add scheduled delivery time if provided
            if params.get("scheduled_dropoff_time"):
                payload["dropoff"]["time"] = params["scheduled_dropoff_time"]
            
            # Add parcel information if provided
            if any(params.get(key) for key in ["parcel_weight", "parcel_height", "parcel_width", "parcel_length"]):
                payload["parcel"] = {}
                if params.get("parcel_weight"):
                    payload["parcel"]["weight"] = params["parcel_weight"]
                if params.get("parcel_height"):
                    payload["parcel"]["height"] = params["parcel_height"]
                if params.get("parcel_width"):
                    payload["parcel"]["width"] = params["parcel_width"]
                if params.get("parcel_length"):
                    payload["parcel"]["length"] = params["parcel_length"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "shipment_promise_id": response_data.get("id"),
                            "estimated_delivery_time": response_data.get("estimated_delivery_time"),
                            "estimated_delivery_fee": response_data.get("price", {}).get("total"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create shipment promise"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create shipment promise: {str(e)}")
    
    async def _create_delivery_order_venueful(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a delivery order for venueful delivery."""
        try:
            venue_id = params["venue_id"]
            url = f"{base_url}/v1/venues/{venue_id}/deliveries"
            
            payload = {
                "shipment_promise_id": params["shipment_promise_id"]
            }
            
            # Add customer information if provided
            if any(params.get(key) for key in ["customer_name", "customer_phone", "customer_email"]):
                payload["customer"] = {}
                if params.get("customer_name"):
                    payload["customer"]["name"] = params["customer_name"]
                if params.get("customer_phone"):
                    payload["customer"]["phone"] = params["customer_phone"]
                if params.get("customer_email"):
                    payload["customer"]["email"] = params["customer_email"]
            
            # Add delivery options
            if params.get("delivery_instructions"):
                payload["delivery_instructions"] = params["delivery_instructions"]
            
            if params.get("contact_less_delivery"):
                payload["contact_less_delivery"] = params["contact_less_delivery"]
            
            if params.get("cash_on_delivery"):
                payload["cash_on_delivery"] = params["cash_on_delivery"]
            
            if params.get("order_id"):
                payload["external_order_id"] = params["order_id"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "delivery_id": response_data.get("id"),
                            "tracking_url": response_data.get("tracking_url"),
                            "delivery_status": response_data.get("status"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create delivery order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create delivery order: {str(e)}")
    
    async def _estimate_delivery_fee_venueless(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Estimate delivery fee for venueless delivery."""
        try:
            merchant_id = params["merchant_id"]
            url = f"{base_url}/merchants/{merchant_id}/delivery-fee"
            
            payload = {
                "pickup": {
                    "location": {
                        "street": params.get("pickup_street", ""),
                        "city": params.get("pickup_city", "")
                    }
                },
                "dropoff": {
                    "location": {
                        "street": params["dropoff_street"],
                        "city": params["dropoff_city"]
                    }
                }
            }
            
            # Add coordinates if provided
            if params.get("pickup_latitude") and params.get("pickup_longitude"):
                payload["pickup"]["location"]["coordinates"] = {
                    "lat": params["pickup_latitude"],
                    "lon": params["pickup_longitude"]
                }
            
            if params.get("dropoff_latitude") and params.get("dropoff_longitude"):
                payload["dropoff"]["location"]["coordinates"] = {
                    "lat": params["dropoff_latitude"],
                    "lon": params["dropoff_longitude"]
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "estimated_delivery_fee": response_data.get("price", {}).get("total"),
                            "estimated_delivery_time": response_data.get("estimated_delivery_time"),
                            "delivery_available": response_data.get("available", False),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to estimate delivery fee"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to estimate delivery fee: {str(e)}")
    
    async def _create_delivery_order_venueless(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a delivery order for venueless delivery."""
        try:
            merchant_id = params["merchant_id"]
            url = f"{base_url}/merchants/{merchant_id}/delivery-order"
            
            payload = {
                "pickup": {
                    "location": {
                        "street": params.get("pickup_street", ""),
                        "city": params.get("pickup_city", "")
                    }
                },
                "dropoff": {
                    "location": {
                        "street": params["dropoff_street"],
                        "city": params["dropoff_city"]
                    }
                }
            }
            
            # Add coordinates if provided
            if params.get("pickup_latitude") and params.get("pickup_longitude"):
                payload["pickup"]["location"]["coordinates"] = {
                    "lat": params["pickup_latitude"],
                    "lon": params["pickup_longitude"]
                }
            
            if params.get("dropoff_latitude") and params.get("dropoff_longitude"):
                payload["dropoff"]["location"]["coordinates"] = {
                    "lat": params["dropoff_latitude"],
                    "lon": params["dropoff_longitude"]
                }
            
            # Add customer information
            if any(params.get(key) for key in ["customer_name", "customer_phone", "customer_email"]):
                payload["customer"] = {}
                if params.get("customer_name"):
                    payload["customer"]["name"] = params["customer_name"]
                if params.get("customer_phone"):
                    payload["customer"]["phone"] = params["customer_phone"]
                if params.get("customer_email"):
                    payload["customer"]["email"] = params["customer_email"]
            
            # Add parcel information
            if any(params.get(key) for key in ["parcel_weight", "parcel_description"]):
                payload["parcel"] = {}
                if params.get("parcel_weight"):
                    payload["parcel"]["weight"] = params["parcel_weight"]
                if params.get("parcel_description"):
                    payload["parcel"]["description"] = params["parcel_description"]
            
            # Add delivery options
            if params.get("delivery_instructions"):
                payload["delivery_instructions"] = params["delivery_instructions"]
            
            if params.get("order_id"):
                payload["external_order_id"] = params["order_id"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 201]:
                        return {
                            "status": "success",
                            "delivery_id": response_data.get("id"),
                            "tracking_url": response_data.get("tracking_url"),
                            "delivery_status": response_data.get("status"),
                            "estimated_delivery_time": response_data.get("estimated_delivery_time"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to create delivery order"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to create delivery order: {str(e)}")
    
    async def _get_available_venues(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get available venues for delivery."""
        try:
            merchant_id = params["merchant_id"]
            url = f"{base_url}/merchants/{merchant_id}/available-venues"
            
            payload = {}
            
            # Add pickup location if provided
            if params.get("pickup_street") and params.get("pickup_city"):
                payload["pickup"] = {
                    "location": {
                        "street": params["pickup_street"],
                        "city": params["pickup_city"]
                    }
                }
                
                if params.get("pickup_post_code"):
                    payload["pickup"]["location"]["postcode"] = params["pickup_post_code"]
                
                if params.get("pickup_latitude") and params.get("pickup_longitude"):
                    payload["pickup"]["location"]["coordinates"] = {
                        "lat": params["pickup_latitude"],
                        "lon": params["pickup_longitude"]
                    }
            
            # Add dropoff location if provided
            if params.get("dropoff_street") and params.get("dropoff_city"):
                payload["dropoff"] = {
                    "location": {
                        "street": params["dropoff_street"],
                        "city": params["dropoff_city"]
                    }
                }
                
                if params.get("dropoff_post_code"):
                    payload["dropoff"]["location"]["postcode"] = params["dropoff_post_code"]
                
                if params.get("dropoff_latitude") and params.get("dropoff_longitude"):
                    payload["dropoff"]["location"]["coordinates"] = {
                        "lat": params["dropoff_latitude"],
                        "lon": params["dropoff_longitude"]
                    }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        venues = response_data.get("venues", [])
                        return {
                            "status": "success",
                            "venues": venues,
                            "venue_count": len(venues),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get available venues"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get available venues: {str(e)}")
    
    async def _get_delivery_handshake(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get delivery handshake details including PIN verification."""
        try:
            order_id = params.get("order_id")
            if not order_id:
                raise NodeValidationError("order_id is required for handshake operations")
            
            url = f"{base_url}/order/{order_id}/handshake-delivery"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "order_id": order_id,
                            "handshake_pin": response_data.get("pin"),
                            "pin_verification_enabled": response_data.get("pin_verification_enabled", False),
                            "delivery_details": response_data.get("delivery_details"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get delivery handshake"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get delivery handshake: {str(e)}")
    
    
    async def _cancel_delivery(self, params: Dict[str, Any], base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Cancel a delivery order."""
        try:
            delivery_id = params["delivery_id"]
            url = f"{base_url}/v1/deliveries/{delivery_id}/cancel"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "delivery_id": delivery_id,
                            "delivery_status": "cancelled",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to cancel delivery"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to cancel delivery: {str(e)}")
    
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "delivery_id": None,
            "shipment_promise_id": None,
            "estimated_delivery_time": None,
            "estimated_delivery_fee": None,
            "tracking_url": None,
            "delivery_status": None,
            "courier_location": None,
            "delivery_eta": None,
            "response_data": None
        }

class WoltDriveHelpers:
    """Helper functions for Wolt Drive operations."""
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate latitude and longitude coordinates."""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    @staticmethod
    def format_address(street: str, city: str, post_code: str = None) -> Dict[str, str]:
        """Format address for API requests."""
        address = {"street": street, "city": city}
        if post_code:
            address["postcode"] = post_code
        return address
    
    @staticmethod
    def calculate_parcel_volume(height: float, width: float, length: float) -> float:
        """Calculate parcel volume in cubic centimeters."""
        return height * width * length
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Basic phone number validation."""
        import re
        # Simple regex for international phone numbers
        pattern = r'^[\+]?[1-9][\d]{1,14}$'
        return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))
    
    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as ISO string for API."""
        return dt.isoformat()
    
    @staticmethod
    def parse_delivery_status(status: str) -> Dict[str, Any]:
        """Parse and categorize delivery status."""
        status_categories = {
            "pending": ["pending", "received", "assigned"],
            "in_transit": ["picked_up", "in_transit", "arriving"],
            "delivered": ["delivered", "completed"],
            "failed": ["cancelled", "failed", "returned"]
        }
        
        for category, statuses in status_categories.items():
            if status.lower() in statuses:
                return {"category": category, "status": status, "is_final": category in ["delivered", "failed"]}
        
        return {"category": "unknown", "status": status, "is_final": False}