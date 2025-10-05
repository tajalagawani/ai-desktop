"""
Wolt Venue Node - Comprehensive venue management integration for Wolt Venue API
Supports all major Wolt venue operations including status management, opening hours,
delivery provider configuration, and venue settings.
Uses Wolt Venue REST API with full API coverage.
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

class WoltVenueOperation:
    """All available Wolt Venue operations based on official API documentation."""
    
    # Venue Status Operations
    GET_VENUE_STATUS = "get_venue_status"
    UPDATE_ONLINE_STATUS = "update_online_status"
    
    # Delivery Provider Operations
    GET_DELIVERY_PROVIDER = "get_delivery_provider"
    UPDATE_DELIVERY_PROVIDER = "update_delivery_provider"
    
    # Opening Hours Operations
    UPDATE_OPENING_TIMES = "update_opening_times"

class WoltVenueStatus:
    """Available Wolt venue statuses."""
    
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class WoltDeliveryProvider:
    """Available Wolt delivery providers."""
    
    WOLT = "WOLT"
    SELF_DELIVERY = "SELF_DELIVERY"

class WoltVenueNode(BaseNode):
    """
    Comprehensive Wolt Venue integration node supporting all major API operations.
    Handles venue status management, opening hours, delivery provider configuration, and venue settings.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.base_url = "https://pos-integration-service.wolt.com"
        
    def get_schema(self) -> NodeSchema:
        """Return the comprehensive schema for the Wolt Venue node."""
        return NodeSchema(
            name="WoltVenueNode",
            description="Comprehensive Wolt Venue management integration supporting status management, opening hours, and delivery provider configuration",
            version="1.0.0",
            inputs={
                "operation": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="The Wolt Venue operation to perform",
                    required=True,
                    enum=[
                        WoltVenueOperation.GET_VENUE_STATUS,
                        WoltVenueOperation.UPDATE_ONLINE_STATUS,
                        WoltVenueOperation.GET_DELIVERY_PROVIDER,
                        WoltVenueOperation.UPDATE_DELIVERY_PROVIDER,
                        WoltVenueOperation.UPDATE_OPENING_TIMES,
                    ]
                ),
                "api_token": NodeParameter(
                    type=NodeParameterType.SECRET,
                    description="Wolt Venue API bearer JWT token",
                    required=True
                ),
                "venue_id": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Unique venue identifier",
                    required=True
                ),
                
                # Status Management Parameters
                "online_status": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Venue online status (ONLINE or OFFLINE)",
                    required=False,
                    enum=["ONLINE", "OFFLINE"]
                ),
                "offline_until": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Datetime until when venue should be offline (ISO format)",
                    required=False
                ),
                "offline_reason": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Reason for setting venue offline",
                    required=False
                ),
                
                # Delivery Provider Parameters
                "delivery_provider": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Delivery provider (WOLT or SELF_DELIVERY)",
                    required=False,
                    enum=["WOLT", "SELF_DELIVERY"]
                ),
                
                # Opening Hours Parameters
                "opening_times": NodeParameter(
                    type=NodeParameterType.ARRAY,
                    description="Array of opening time objects with day and time information",
                    required=False
                ),
                "monday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Monday opening time (HH:MM format)",
                    required=False
                ),
                "monday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Monday closing time (HH:MM format)",
                    required=False
                ),
                "tuesday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tuesday opening time (HH:MM format)",
                    required=False
                ),
                "tuesday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Tuesday closing time (HH:MM format)",
                    required=False
                ),
                "wednesday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Wednesday opening time (HH:MM format)",
                    required=False
                ),
                "wednesday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Wednesday closing time (HH:MM format)",
                    required=False
                ),
                "thursday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Thursday opening time (HH:MM format)",
                    required=False
                ),
                "thursday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Thursday closing time (HH:MM format)",
                    required=False
                ),
                "friday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Friday opening time (HH:MM format)",
                    required=False
                ),
                "friday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Friday closing time (HH:MM format)",
                    required=False
                ),
                "saturday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Saturday opening time (HH:MM format)",
                    required=False
                ),
                "saturday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Saturday closing time (HH:MM format)",
                    required=False
                ),
                "sunday_open": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Sunday opening time (HH:MM format)",
                    required=False
                ),
                "sunday_close": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Sunday closing time (HH:MM format)",
                    required=False
                ),
                
                # Additional Parameters
                "timezone": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Venue timezone for opening hours",
                    required=False
                ),
                "notes": NodeParameter(
                    type=NodeParameterType.STRING,
                    description="Additional notes for the operation",
                    required=False
                ),
            },
            outputs={
                "status": NodeParameterType.STRING,
                "venue_id": NodeParameterType.STRING,
                "venue_status": NodeParameterType.STRING,
                "online_status": NodeParameterType.STRING,
                "delivery_provider": NodeParameterType.STRING,
                "opening_times": NodeParameterType.ARRAY,
                "venue_info": NodeParameterType.OBJECT,
                "contact_details": NodeParameterType.OBJECT,
                "delivery_area": NodeParameterType.OBJECT,
                "recent_orders": NodeParameterType.ARRAY,
                "operation_type": NodeParameterType.STRING,
                "response_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "error_code": NodeParameterType.STRING,
            }
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Wolt Venue-specific parameters."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        # Always validate operation exists
        if not operation:
            raise NodeValidationError("Operation is required")
        
        # Always validate API token
        if not params.get("api_token"):
            raise NodeValidationError("Wolt Venue API token is required")
        
        # Always validate venue ID
        if not params.get("venue_id"):
            raise NodeValidationError("venue_id is required for all venue operations")
        
        # Validate operation-specific requirements
        if operation == WoltVenueOperation.UPDATE_ONLINE_STATUS:
            if not params.get("online_status"):
                raise NodeValidationError("online_status is required for status updates")
            if params.get("online_status") not in [WoltVenueStatus.ONLINE, WoltVenueStatus.OFFLINE]:
                raise NodeValidationError("online_status must be ONLINE or OFFLINE")
        
        if operation == WoltVenueOperation.UPDATE_DELIVERY_PROVIDER:
            if not params.get("delivery_provider"):
                raise NodeValidationError("delivery_provider is required for delivery provider updates")
            if params.get("delivery_provider") not in [WoltDeliveryProvider.WOLT, WoltDeliveryProvider.SELF_DELIVERY]:
                raise NodeValidationError("delivery_provider must be WOLT or SELF_DELIVERY")
        
        if operation == WoltVenueOperation.UPDATE_OPENING_TIMES:
            has_bulk_times = params.get("opening_times")
            has_individual_times = any([
                params.get("monday_open"), params.get("tuesday_open"), params.get("wednesday_open"),
                params.get("thursday_open"), params.get("friday_open"), params.get("saturday_open"),
                params.get("sunday_open")
            ])
            
            if not has_bulk_times and not has_individual_times:
                raise NodeValidationError("Either 'opening_times' array or individual day opening times are required")
        
        # Validate time format for individual day times
        time_fields = [
            "monday_open", "monday_close", "tuesday_open", "tuesday_close",
            "wednesday_open", "wednesday_close", "thursday_open", "thursday_close",
            "friday_open", "friday_close", "saturday_open", "saturday_close",
            "sunday_open", "sunday_close"
        ]
        
        for field in time_fields:
            if params.get(field) and not self._validate_time_format(params[field]):
                raise NodeValidationError(f"{field} must be in HH:MM format")
        
        return params
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        import re
        return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str))
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Wolt Venue operation."""
        try:
            params = self.validate_custom(node_data)
            operation = params["operation"]
            
            # Create headers
            headers = {
                "Authorization": f"Bearer {params['api_token']}",
                "Content-Type": "application/json",
                "User-Agent": "WoltVenueNode/1.0.0"
            }
            
            # Route to specific operation handler
            if operation == WoltVenueOperation.GET_VENUE_STATUS:
                return await self._get_venue_status(params, headers)
            elif operation == WoltVenueOperation.UPDATE_ONLINE_STATUS:
                return await self._update_online_status(params, headers)
            elif operation == WoltVenueOperation.GET_DELIVERY_PROVIDER:
                return await self._get_delivery_provider(params, headers)
            elif operation == WoltVenueOperation.UPDATE_DELIVERY_PROVIDER:
                return await self._update_delivery_provider(params, headers)
            elif operation == WoltVenueOperation.UPDATE_OPENING_TIMES:
                return await self._update_opening_times(params, headers)
            else:
                raise NodeExecutionError(f"Unknown operation: {operation}")
                
        except NodeValidationError as e:
            return self._format_error_response(str(e), "validation_error")
        except NodeExecutionError as e:
            return self._format_error_response(str(e), "execution_error")
        except Exception as e:
            logger.error(f"Unexpected error in WoltVenueNode: {str(e)}")
            return self._format_error_response(f"Unexpected error: {str(e)}", "unexpected_error")
    
    async def _get_venue_status(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Get venue status and information."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/status"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "get_venue_status",
                            "venue_status": response_data.get("status"),
                            "online_status": response_data.get("online_status"),
                            "venue_info": response_data,
                            "contact_details": response_data.get("contact"),
                            "delivery_area": response_data.get("delivery_area"),
                            "opening_times": response_data.get("opening_times"),
                            "recent_orders": response_data.get("recent_orders", []),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get venue status"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get venue status: {str(e)}")
    
    async def _update_online_status(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update venue online/offline status."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/online"
            
            payload = {
                "status": params["online_status"]
            }
            
            # Add optional offline duration
            if params.get("offline_until"):
                payload["until"] = params["offline_until"]
            
            # Add optional reason for offline status
            if params.get("offline_reason"):
                payload["reason"] = params["offline_reason"]
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "update_online_status",
                            "online_status": params["online_status"],
                            "offline_until": params.get("offline_until"),
                            "offline_reason": params.get("offline_reason"),
                            "message": f"Venue status updated to {params['online_status']}",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update online status"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update online status: {str(e)}")
    
    async def _get_delivery_provider(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Get venue delivery provider information."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/delivery-provider"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "get_delivery_provider",
                            "delivery_provider": response_data.get("delivery_provider"),
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to get delivery provider"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to get delivery provider: {str(e)}")
    
    async def _update_delivery_provider(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update venue delivery provider."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/delivery-provider"
            
            payload = {
                "delivery_provider": params["delivery_provider"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "update_delivery_provider",
                            "delivery_provider": params["delivery_provider"],
                            "message": f"Delivery provider updated to {params['delivery_provider']}",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update delivery provider"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update delivery provider: {str(e)}")
    
    async def _update_opening_times(self, params: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Update venue opening times."""
        try:
            venue_id = params["venue_id"]
            url = f"{self.base_url}/venues/{venue_id}/opening-times"
            
            # Prepare opening times
            if params.get("opening_times"):
                # Use provided opening times array
                availability = params["opening_times"]
            else:
                # Build from individual day parameters
                availability = self._build_opening_times_from_params(params)
            
            payload = {
                "availability": availability
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=payload) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status in [200, 204]:
                        return {
                            "status": "success",
                            "venue_id": venue_id,
                            "operation_type": "update_opening_times",
                            "opening_times": availability,
                            "message": "Opening times updated successfully",
                            "response_data": response_data
                        }
                    else:
                        return self._format_error_response(
                            response_data.get("message", "Failed to update opening times"),
                            f"api_error_{response.status}"
                        )
                        
        except Exception as e:
            raise NodeExecutionError(f"Failed to update opening times: {str(e)}")
    
    def _build_opening_times_from_params(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build opening times array from individual day parameters."""
        days = [
            ("monday", 1), ("tuesday", 2), ("wednesday", 3), ("thursday", 4),
            ("friday", 5), ("saturday", 6), ("sunday", 7)
        ]
        
        availability = []
        
        for day_name, day_num in days:
            open_key = f"{day_name}_open"
            close_key = f"{day_name}_close"
            
            if params.get(open_key) and params.get(close_key):
                availability.append({
                    "opening_day": day_num,
                    "opening_time": params[open_key],
                    "closing_day": day_num,
                    "closing_time": params[close_key]
                })
        
        return availability
    
    def _format_error_response(self, error_message: str, error_code: str) -> Dict[str, Any]:
        """Format error response consistently."""
        return {
            "status": "error",
            "error": error_message,
            "error_code": error_code,
            "venue_id": None,
            "venue_status": None,
            "online_status": None,
            "delivery_provider": None,
            "opening_times": None,
            "venue_info": None,
            "contact_details": None,
            "delivery_area": None,
            "recent_orders": None,
            "operation_type": None,
            "response_data": None
        }

class WoltVenueHelpers:
    """Helper functions for Wolt Venue operations."""
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        import re
        return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str))
    
    @staticmethod
    def create_opening_time(opening_day: int, opening_time: str, 
                           closing_day: int, closing_time: str) -> Dict[str, Any]:
        """Create a properly formatted opening time object."""
        return {
            "opening_day": opening_day,
            "opening_time": opening_time,
            "closing_day": closing_day,
            "closing_time": closing_time
        }
    
    @staticmethod
    def create_weekly_schedule(schedule: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        """Create a weekly schedule from a dictionary of day schedules.
        
        Args:
            schedule: Dict with day names as keys and {'open': 'HH:MM', 'close': 'HH:MM'} as values
        """
        day_mapping = {
            "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
            "friday": 5, "saturday": 6, "sunday": 7
        }
        
        availability = []
        
        for day_name, times in schedule.items():
            if day_name.lower() in day_mapping and times.get("open") and times.get("close"):
                day_num = day_mapping[day_name.lower()]
                availability.append({
                    "opening_day": day_num,
                    "opening_time": times["open"],
                    "closing_day": day_num,
                    "closing_time": times["close"]
                })
        
        return availability
    
    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """Format datetime as ISO string for offline_until parameter."""
        return dt.isoformat()
    
    @staticmethod
    def validate_day_number(day: int) -> bool:
        """Validate day number (1-7)."""
        return 1 <= day <= 7
    
    @staticmethod
    def get_day_name(day_number: int) -> str:
        """Get day name from day number."""
        days = {
            1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
            5: "Friday", 6: "Saturday", 7: "Sunday"
        }
        return days.get(day_number, "Unknown")
    
    @staticmethod
    def parse_venue_status(venue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse venue status information from venue data."""
        return {
            "online_status": venue_data.get("online_status"),
            "is_open": venue_data.get("is_open"),
            "delivery_available": venue_data.get("delivery_available"),
            "pickup_available": venue_data.get("pickup_available"),
            "estimated_delivery_time": venue_data.get("estimated_delivery_time")
        }
    
    @staticmethod
    def validate_delivery_provider(provider: str) -> bool:
        """Validate delivery provider value."""
        return provider in [WoltDeliveryProvider.WOLT, WoltDeliveryProvider.SELF_DELIVERY]
    
    @staticmethod
    def validate_online_status(status: str) -> bool:
        """Validate online status value."""
        return status in [WoltVenueStatus.ONLINE, WoltVenueStatus.OFFLINE]
    
    @staticmethod
    def calculate_opening_hours_summary(opening_times: List[Dict[str, Any]]) -> Dict[str, str]:
        """Calculate a summary of opening hours by day."""
        summary = {}
        
        for time_slot in opening_times:
            day_num = time_slot.get("opening_day")
            opening_time = time_slot.get("opening_time")
            closing_time = time_slot.get("closing_time")
            
            if day_num and opening_time and closing_time:
                day_name = WoltVenueHelpers.get_day_name(day_num)
                summary[day_name] = f"{opening_time} - {closing_time}"
        
        return summary