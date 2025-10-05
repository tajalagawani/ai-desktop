"""
Shopify Node - Unified implementation using UniversalRequestNode
Comprehensive Shopify Admin API integration for e-commerce store management, order processing, product catalog, and customer operations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from universal_request_node import UniversalRequestNode
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError
    )
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )
    except ImportError:
        from universal_request_node import UniversalRequestNode
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError
        )

# Configure logging
logger = logging.getLogger(__name__)

class ShopifyNode(BaseNode):
    """
    Unified Shopify Node using UniversalRequestNode for Shopify Admin API integration.
    Supports comprehensive e-commerce operations including products, orders, customers, inventory, and analytics.
    """
    
    # Configuration for Shopify Admin API
    CONFIG = {
        "base_url": "https://{shop_domain}/admin/api/2023-10",
        "authentication": {
            "type": "header_token",
            "header": "X-Shopify-Access-Token"
        },
        "default_headers": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "retry_config": {
            "max_retries": 3,
            "backoff_factor": 1.0,
            "retry_on_status": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 2,  # Shopify has strict rate limits
            "requests_per_minute": 40
        },
        "timeouts": {
            "connect": 30,
            "read": 300,
            "total": 600
        }
    }
    
    # Operations mapping for Shopify Admin API
    OPERATIONS = {
        # Product Operations
        "list_products": {
            "method": "GET",
            "endpoint": "products.json",
            "required_params": []
        },
        "get_product": {
            "method": "GET",
            "endpoint": "products/{product_id}.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "create_product": {
            "method": "POST",
            "endpoint": "products.json",
            "required_params": ["title"]
        },
        "update_product": {
            "method": "PUT",
            "endpoint": "products/{product_id}.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "delete_product": {
            "method": "DELETE",
            "endpoint": "products/{product_id}.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "count_products": {
            "method": "GET",
            "endpoint": "products/count.json",
            "required_params": []
        },
        
        # Product Variants Operations
        "list_product_variants": {
            "method": "GET",
            "endpoint": "products/{product_id}/variants.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "get_product_variant": {
            "method": "GET",
            "endpoint": "variants/{variant_id}.json",
            "required_params": ["variant_id"],
            "path_params": ["variant_id"]
        },
        "create_product_variant": {
            "method": "POST",
            "endpoint": "products/{product_id}/variants.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "update_product_variant": {
            "method": "PUT",
            "endpoint": "variants/{variant_id}.json",
            "required_params": ["variant_id"],
            "path_params": ["variant_id"]
        },
        "delete_product_variant": {
            "method": "DELETE",
            "endpoint": "variants/{variant_id}.json",
            "required_params": ["variant_id"],
            "path_params": ["variant_id"]
        },
        
        # Order Operations
        "list_orders": {
            "method": "GET",
            "endpoint": "orders.json",
            "required_params": []
        },
        "get_order": {
            "method": "GET",
            "endpoint": "orders/{order_id}.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "create_order": {
            "method": "POST",
            "endpoint": "orders.json",
            "required_params": ["line_items"]
        },
        "update_order": {
            "method": "PUT",
            "endpoint": "orders/{order_id}.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "delete_order": {
            "method": "DELETE",
            "endpoint": "orders/{order_id}.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "close_order": {
            "method": "POST",
            "endpoint": "orders/{order_id}/close.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "reopen_order": {
            "method": "POST",
            "endpoint": "orders/{order_id}/open.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "cancel_order": {
            "method": "POST",
            "endpoint": "orders/{order_id}/cancel.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "count_orders": {
            "method": "GET",
            "endpoint": "orders/count.json",
            "required_params": []
        },
        
        # Customer Operations
        "list_customers": {
            "method": "GET",
            "endpoint": "customers.json",
            "required_params": []
        },
        "get_customer": {
            "method": "GET",
            "endpoint": "customers/{customer_id}.json",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "create_customer": {
            "method": "POST",
            "endpoint": "customers.json",
            "required_params": ["email"]
        },
        "update_customer": {
            "method": "PUT",
            "endpoint": "customers/{customer_id}.json",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "delete_customer": {
            "method": "DELETE",
            "endpoint": "customers/{customer_id}.json",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "count_customers": {
            "method": "GET",
            "endpoint": "customers/count.json",
            "required_params": []
        },
        "search_customers": {
            "method": "GET",
            "endpoint": "customers/search.json",
            "required_params": ["query"]
        },
        
        # Customer Address Operations
        "list_customer_addresses": {
            "method": "GET",
            "endpoint": "customers/{customer_id}/addresses.json",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "get_customer_address": {
            "method": "GET",
            "endpoint": "customers/{customer_id}/addresses/{address_id}.json",
            "required_params": ["customer_id", "address_id"],
            "path_params": ["customer_id", "address_id"]
        },
        "create_customer_address": {
            "method": "POST",
            "endpoint": "customers/{customer_id}/addresses.json",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "update_customer_address": {
            "method": "PUT",
            "endpoint": "customers/{customer_id}/addresses/{address_id}.json",
            "required_params": ["customer_id", "address_id"],
            "path_params": ["customer_id", "address_id"]
        },
        "delete_customer_address": {
            "method": "DELETE",
            "endpoint": "customers/{customer_id}/addresses/{address_id}.json",
            "required_params": ["customer_id", "address_id"],
            "path_params": ["customer_id", "address_id"]
        },
        "set_default_customer_address": {
            "method": "PUT",
            "endpoint": "customers/{customer_id}/addresses/{address_id}/default.json",
            "required_params": ["customer_id", "address_id"],
            "path_params": ["customer_id", "address_id"]
        },
        
        # Inventory Operations
        "list_inventory_levels": {
            "method": "GET",
            "endpoint": "inventory_levels.json",
            "required_params": []
        },
        "adjust_inventory_level": {
            "method": "POST",
            "endpoint": "inventory_levels/adjust.json",
            "required_params": ["inventory_item_id", "location_id", "available_adjustment"]
        },
        "set_inventory_level": {
            "method": "POST",
            "endpoint": "inventory_levels/set.json",
            "required_params": ["inventory_item_id", "location_id", "available"]
        },
        "connect_inventory_level": {
            "method": "POST",
            "endpoint": "inventory_levels/connect.json",
            "required_params": ["inventory_item_id", "location_id"]
        },
        "disconnect_inventory_level": {
            "method": "DELETE",
            "endpoint": "inventory_levels.json",
            "required_params": ["inventory_item_id", "location_id"]
        },
        
        # Inventory Item Operations
        "get_inventory_item": {
            "method": "GET",
            "endpoint": "inventory_items/{inventory_item_id}.json",
            "required_params": ["inventory_item_id"],
            "path_params": ["inventory_item_id"]
        },
        "update_inventory_item": {
            "method": "PUT",
            "endpoint": "inventory_items/{inventory_item_id}.json",
            "required_params": ["inventory_item_id"],
            "path_params": ["inventory_item_id"]
        },
        
        # Collection Operations
        "list_collections": {
            "method": "GET",
            "endpoint": "collections.json",
            "required_params": []
        },
        "get_collection": {
            "method": "GET",
            "endpoint": "collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "create_collection": {
            "method": "POST",
            "endpoint": "collections.json",
            "required_params": ["title"]
        },
        "update_collection": {
            "method": "PUT",
            "endpoint": "collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "delete_collection": {
            "method": "DELETE",
            "endpoint": "collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "count_collections": {
            "method": "GET",
            "endpoint": "collections/count.json",
            "required_params": []
        },
        
        # Smart Collection Operations
        "list_smart_collections": {
            "method": "GET",
            "endpoint": "smart_collections.json",
            "required_params": []
        },
        "get_smart_collection": {
            "method": "GET",
            "endpoint": "smart_collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "create_smart_collection": {
            "method": "POST",
            "endpoint": "smart_collections.json",
            "required_params": ["title", "rules"]
        },
        "update_smart_collection": {
            "method": "PUT",
            "endpoint": "smart_collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "delete_smart_collection": {
            "method": "DELETE",
            "endpoint": "smart_collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        
        # Custom Collection Operations
        "list_custom_collections": {
            "method": "GET",
            "endpoint": "custom_collections.json",
            "required_params": []
        },
        "get_custom_collection": {
            "method": "GET",
            "endpoint": "custom_collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "create_custom_collection": {
            "method": "POST",
            "endpoint": "custom_collections.json",
            "required_params": ["title"]
        },
        "update_custom_collection": {
            "method": "PUT",
            "endpoint": "custom_collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        "delete_custom_collection": {
            "method": "DELETE",
            "endpoint": "custom_collections/{collection_id}.json",
            "required_params": ["collection_id"],
            "path_params": ["collection_id"]
        },
        
        # Fulfillment Operations
        "list_fulfillments": {
            "method": "GET",
            "endpoint": "orders/{order_id}/fulfillments.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "get_fulfillment": {
            "method": "GET",
            "endpoint": "orders/{order_id}/fulfillments/{fulfillment_id}.json",
            "required_params": ["order_id", "fulfillment_id"],
            "path_params": ["order_id", "fulfillment_id"]
        },
        "create_fulfillment": {
            "method": "POST",
            "endpoint": "orders/{order_id}/fulfillments.json",
            "required_params": ["order_id", "line_items"],
            "path_params": ["order_id"]
        },
        "update_fulfillment": {
            "method": "PUT",
            "endpoint": "orders/{order_id}/fulfillments/{fulfillment_id}.json",
            "required_params": ["order_id", "fulfillment_id"],
            "path_params": ["order_id", "fulfillment_id"]
        },
        "complete_fulfillment": {
            "method": "POST",
            "endpoint": "orders/{order_id}/fulfillments/{fulfillment_id}/complete.json",
            "required_params": ["order_id", "fulfillment_id"],
            "path_params": ["order_id", "fulfillment_id"]
        },
        "cancel_fulfillment": {
            "method": "POST",
            "endpoint": "orders/{order_id}/fulfillments/{fulfillment_id}/cancel.json",
            "required_params": ["order_id", "fulfillment_id"],
            "path_params": ["order_id", "fulfillment_id"]
        },
        
        # Discount Code Operations
        "list_discount_codes": {
            "method": "GET",
            "endpoint": "price_rules/{price_rule_id}/discount_codes.json",
            "required_params": ["price_rule_id"],
            "path_params": ["price_rule_id"]
        },
        "get_discount_code": {
            "method": "GET",
            "endpoint": "price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json",
            "required_params": ["price_rule_id", "discount_code_id"],
            "path_params": ["price_rule_id", "discount_code_id"]
        },
        "create_discount_code": {
            "method": "POST",
            "endpoint": "price_rules/{price_rule_id}/discount_codes.json",
            "required_params": ["price_rule_id", "code"],
            "path_params": ["price_rule_id"]
        },
        "update_discount_code": {
            "method": "PUT",
            "endpoint": "price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json",
            "required_params": ["price_rule_id", "discount_code_id"],
            "path_params": ["price_rule_id", "discount_code_id"]
        },
        "delete_discount_code": {
            "method": "DELETE",
            "endpoint": "price_rules/{price_rule_id}/discount_codes/{discount_code_id}.json",
            "required_params": ["price_rule_id", "discount_code_id"],
            "path_params": ["price_rule_id", "discount_code_id"]
        },
        
        # Price Rule Operations
        "list_price_rules": {
            "method": "GET",
            "endpoint": "price_rules.json",
            "required_params": []
        },
        "get_price_rule": {
            "method": "GET",
            "endpoint": "price_rules/{price_rule_id}.json",
            "required_params": ["price_rule_id"],
            "path_params": ["price_rule_id"]
        },
        "create_price_rule": {
            "method": "POST",
            "endpoint": "price_rules.json",
            "required_params": ["title", "target_type", "target_selection", "value_type", "value"]
        },
        "update_price_rule": {
            "method": "PUT",
            "endpoint": "price_rules/{price_rule_id}.json",
            "required_params": ["price_rule_id"],
            "path_params": ["price_rule_id"]
        },
        "delete_price_rule": {
            "method": "DELETE",
            "endpoint": "price_rules/{price_rule_id}.json",
            "required_params": ["price_rule_id"],
            "path_params": ["price_rule_id"]
        },
        
        # Location Operations
        "list_locations": {
            "method": "GET",
            "endpoint": "locations.json",
            "required_params": []
        },
        "get_location": {
            "method": "GET",
            "endpoint": "locations/{location_id}.json",
            "required_params": ["location_id"],
            "path_params": ["location_id"]
        },
        "count_locations": {
            "method": "GET",
            "endpoint": "locations/count.json",
            "required_params": []
        },
        
        # Shop Operations
        "get_shop": {
            "method": "GET",
            "endpoint": "shop.json",
            "required_params": []
        },
        
        # Webhook Operations
        "list_webhooks": {
            "method": "GET",
            "endpoint": "webhooks.json",
            "required_params": []
        },
        "get_webhook": {
            "method": "GET",
            "endpoint": "webhooks/{webhook_id}.json",
            "required_params": ["webhook_id"],
            "path_params": ["webhook_id"]
        },
        "create_webhook": {
            "method": "POST",
            "endpoint": "webhooks.json",
            "required_params": ["topic", "address"]
        },
        "update_webhook": {
            "method": "PUT",
            "endpoint": "webhooks/{webhook_id}.json",
            "required_params": ["webhook_id"],
            "path_params": ["webhook_id"]
        },
        "delete_webhook": {
            "method": "DELETE",
            "endpoint": "webhooks/{webhook_id}.json",
            "required_params": ["webhook_id"],
            "path_params": ["webhook_id"]
        },
        "count_webhooks": {
            "method": "GET",
            "endpoint": "webhooks/count.json",
            "required_params": []
        },
        
        # Transaction Operations
        "list_transactions": {
            "method": "GET",
            "endpoint": "orders/{order_id}/transactions.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "get_transaction": {
            "method": "GET",
            "endpoint": "orders/{order_id}/transactions/{transaction_id}.json",
            "required_params": ["order_id", "transaction_id"],
            "path_params": ["order_id", "transaction_id"]
        },
        "create_transaction": {
            "method": "POST",
            "endpoint": "orders/{order_id}/transactions.json",
            "required_params": ["order_id", "kind"],
            "path_params": ["order_id"]
        },
        "count_transactions": {
            "method": "GET",
            "endpoint": "orders/{order_id}/transactions/count.json",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        
        # Product Image Operations
        "list_product_images": {
            "method": "GET",
            "endpoint": "products/{product_id}/images.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "get_product_image": {
            "method": "GET",
            "endpoint": "products/{product_id}/images/{image_id}.json",
            "required_params": ["product_id", "image_id"],
            "path_params": ["product_id", "image_id"]
        },
        "create_product_image": {
            "method": "POST",
            "endpoint": "products/{product_id}/images.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        },
        "update_product_image": {
            "method": "PUT",
            "endpoint": "products/{product_id}/images/{image_id}.json",
            "required_params": ["product_id", "image_id"],
            "path_params": ["product_id", "image_id"]
        },
        "delete_product_image": {
            "method": "DELETE",
            "endpoint": "products/{product_id}/images/{image_id}.json",
            "required_params": ["product_id", "image_id"],
            "path_params": ["product_id", "image_id"]
        },
        "count_product_images": {
            "method": "GET",
            "endpoint": "products/{product_id}/images/count.json",
            "required_params": ["product_id"],
            "path_params": ["product_id"]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.universal_node = UniversalRequestNode(self.CONFIG, self.OPERATIONS, sandbox_timeout)
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Shopify node."""
        return NodeSchema(
            node_type="shopify",
            version="2.0.0",
            description="Comprehensive Shopify Admin API integration with 80+ operations using UniversalRequestNode for e-commerce store management",
            parameters=[
                # Core configuration
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Shopify operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="shop_domain",
                    type=NodeParameterType.STRING,
                    description="Shopify shop domain (e.g., 'mystore.myshopify.com')",
                    required=True
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.SECRET,
                    description="Shopify Admin API access token",
                    required=True
                ),
                
                # ID parameters
                NodeParameter(
                    name="product_id",
                    type=NodeParameterType.STRING,
                    description="Product ID for product operations",
                    required=False
                ),
                NodeParameter(
                    name="variant_id",
                    type=NodeParameterType.STRING,
                    description="Product variant ID for variant operations",
                    required=False
                ),
                NodeParameter(
                    name="order_id",
                    type=NodeParameterType.STRING,
                    description="Order ID for order operations",
                    required=False
                ),
                NodeParameter(
                    name="customer_id",
                    type=NodeParameterType.STRING,
                    description="Customer ID for customer operations",
                    required=False
                ),
                NodeParameter(
                    name="collection_id",
                    type=NodeParameterType.STRING,
                    description="Collection ID for collection operations",
                    required=False
                ),
                NodeParameter(
                    name="address_id",
                    type=NodeParameterType.STRING,
                    description="Address ID for address operations",
                    required=False
                ),
                NodeParameter(
                    name="inventory_item_id",
                    type=NodeParameterType.STRING,
                    description="Inventory item ID for inventory operations",
                    required=False
                ),
                NodeParameter(
                    name="location_id",
                    type=NodeParameterType.STRING,
                    description="Location ID for inventory operations",
                    required=False
                ),
                NodeParameter(
                    name="fulfillment_id",
                    type=NodeParameterType.STRING,
                    description="Fulfillment ID for fulfillment operations",
                    required=False
                ),
                NodeParameter(
                    name="price_rule_id",
                    type=NodeParameterType.STRING,
                    description="Price rule ID for discount operations",
                    required=False
                ),
                NodeParameter(
                    name="discount_code_id",
                    type=NodeParameterType.STRING,
                    description="Discount code ID for discount operations",
                    required=False
                ),
                NodeParameter(
                    name="webhook_id",
                    type=NodeParameterType.STRING,
                    description="Webhook ID for webhook operations",
                    required=False
                ),
                NodeParameter(
                    name="transaction_id",
                    type=NodeParameterType.STRING,
                    description="Transaction ID for transaction operations",
                    required=False
                ),
                NodeParameter(
                    name="image_id",
                    type=NodeParameterType.STRING,
                    description="Image ID for image operations",
                    required=False
                ),
                
                # Product parameters
                NodeParameter(
                    name="title",
                    type=NodeParameterType.STRING,
                    description="Product or collection title",
                    required=False
                ),
                NodeParameter(
                    name="description",
                    type=NodeParameterType.STRING,
                    description="Product or collection description",
                    required=False
                ),
                NodeParameter(
                    name="vendor",
                    type=NodeParameterType.STRING,
                    description="Product vendor",
                    required=False
                ),
                NodeParameter(
                    name="product_type",
                    type=NodeParameterType.STRING,
                    description="Product type",
                    required=False
                ),
                NodeParameter(
                    name="tags",
                    type=NodeParameterType.STRING,
                    description="Product tags (comma-separated)",
                    required=False
                ),
                NodeParameter(
                    name="published",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether the product is published",
                    required=False,
                    default=True
                ),
                
                # Customer parameters
                NodeParameter(
                    name="email",
                    type=NodeParameterType.STRING,
                    description="Customer email address",
                    required=False
                ),
                NodeParameter(
                    name="first_name",
                    type=NodeParameterType.STRING,
                    description="Customer first name",
                    required=False
                ),
                NodeParameter(
                    name="last_name",
                    type=NodeParameterType.STRING,
                    description="Customer last name",
                    required=False
                ),
                NodeParameter(
                    name="phone",
                    type=NodeParameterType.STRING,
                    description="Customer phone number",
                    required=False
                ),
                NodeParameter(
                    name="accepts_marketing",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether customer accepts marketing",
                    required=False,
                    default=False
                ),
                
                # Order parameters
                NodeParameter(
                    name="line_items",
                    type=NodeParameterType.ARRAY,
                    description="Order line items array",
                    required=False
                ),
                NodeParameter(
                    name="financial_status",
                    type=NodeParameterType.STRING,
                    description="Order financial status",
                    required=False,
                    enum=["pending", "authorized", "partially_paid", "paid", "partially_refunded", "refunded", "voided"]
                ),
                NodeParameter(
                    name="fulfillment_status",
                    type=NodeParameterType.STRING,
                    description="Order fulfillment status",
                    required=False,
                    enum=["fulfilled", "null", "partial", "restocked"]
                ),
                
                # Inventory parameters
                NodeParameter(
                    name="available_adjustment",
                    type=NodeParameterType.NUMBER,
                    description="Inventory adjustment amount (positive or negative)",
                    required=False
                ),
                NodeParameter(
                    name="available",
                    type=NodeParameterType.NUMBER,
                    description="Inventory available quantity",
                    required=False
                ),
                
                # Webhook parameters
                NodeParameter(
                    name="topic",
                    type=NodeParameterType.STRING,
                    description="Webhook topic",
                    required=False
                ),
                NodeParameter(
                    name="address",
                    type=NodeParameterType.STRING,
                    description="Webhook callback URL",
                    required=False
                ),
                NodeParameter(
                    name="format",
                    type=NodeParameterType.STRING,
                    description="Webhook payload format",
                    required=False,
                    enum=["json", "xml"],
                    default="json"
                ),
                
                # Discount parameters
                NodeParameter(
                    name="code",
                    type=NodeParameterType.STRING,
                    description="Discount code",
                    required=False
                ),
                NodeParameter(
                    name="target_type",
                    type=NodeParameterType.STRING,
                    description="Price rule target type",
                    required=False,
                    enum=["line_item", "shipping_line"]
                ),
                NodeParameter(
                    name="target_selection",
                    type=NodeParameterType.STRING,
                    description="Price rule target selection",
                    required=False,
                    enum=["all", "entitled"]
                ),
                NodeParameter(
                    name="value_type",
                    type=NodeParameterType.STRING,
                    description="Price rule value type",
                    required=False,
                    enum=["percentage", "fixed_amount"]
                ),
                NodeParameter(
                    name="value",
                    type=NodeParameterType.STRING,
                    description="Price rule value",
                    required=False
                ),
                
                # Transaction parameters
                NodeParameter(
                    name="kind",
                    type=NodeParameterType.STRING,
                    description="Transaction kind",
                    required=False,
                    enum=["authorization", "capture", "sale", "void", "refund"]
                ),
                NodeParameter(
                    name="amount",
                    type=NodeParameterType.STRING,
                    description="Transaction amount",
                    required=False
                ),
                
                # Collection parameters
                NodeParameter(
                    name="rules",
                    type=NodeParameterType.ARRAY,
                    description="Smart collection rules array",
                    required=False
                ),
                NodeParameter(
                    name="sort_order",
                    type=NodeParameterType.STRING,
                    description="Collection sort order",
                    required=False,
                    enum=["alpha-asc", "alpha-desc", "best-selling", "created", "created-desc", "manual", "price-asc", "price-desc"]
                ),
                
                # Request body
                NodeParameter(
                    name="request_body",
                    type=NodeParameterType.OBJECT,
                    description="Request body for create/update operations",
                    required=False
                ),
                
                # Search and filter parameters
                NodeParameter(
                    name="query",
                    type=NodeParameterType.STRING,
                    description="Search query for customer search",
                    required=False
                ),
                NodeParameter(
                    name="status",
                    type=NodeParameterType.STRING,
                    description="Status filter for orders",
                    required=False,
                    enum=["open", "closed", "cancelled", "any"]
                ),
                
                # Pagination parameters
                NodeParameter(
                    name="limit",
                    type=NodeParameterType.NUMBER,
                    description="Number of results to return",
                    required=False,
                    default=50,
                    min_value=1,
                    max_value=250
                ),
                NodeParameter(
                    name="page_info",
                    type=NodeParameterType.STRING,
                    description="Page info for pagination",
                    required=False
                ),
                NodeParameter(
                    name="since_id",
                    type=NodeParameterType.STRING,
                    description="Return results after this ID",
                    required=False
                ),
                
                # Date parameters
                NodeParameter(
                    name="created_at_min",
                    type=NodeParameterType.STRING,
                    description="Show results created after this date (ISO 8601)",
                    required=False
                ),
                NodeParameter(
                    name="created_at_max",
                    type=NodeParameterType.STRING,
                    description="Show results created before this date (ISO 8601)",
                    required=False
                ),
                NodeParameter(
                    name="updated_at_min",
                    type=NodeParameterType.STRING,
                    description="Show results updated after this date (ISO 8601)",
                    required=False
                ),
                NodeParameter(
                    name="updated_at_max",
                    type=NodeParameterType.STRING,
                    description="Show results updated before this date (ISO 8601)",
                    required=False
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "status_code": NodeParameterType.NUMBER,
                "response_headers": NodeParameterType.OBJECT,
                "product_id": NodeParameterType.STRING,
                "order_id": NodeParameterType.STRING,
                "customer_id": NodeParameterType.STRING,
                "collection_id": NodeParameterType.STRING,
                "inventory_item_id": NodeParameterType.STRING,
                "total_count": NodeParameterType.NUMBER
            },
            tags=["shopify", "ecommerce", "products", "orders", "customers", "api", "unified"],
            author="System",
            documentation_url="https://shopify.dev/docs/api/admin-rest"
        )

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Shopify operation using UniversalRequestNode."""
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                raise NodeValidationError("Operation is required")
                
            if operation not in self.OPERATIONS:
                raise NodeValidationError(f"Unknown operation: {operation}")
            
            # Validate required parameters
            shop_domain = params.get("shop_domain")
            access_token = params.get("access_token")
            
            if not shop_domain:
                raise NodeValidationError("Shop domain is required")
            if not access_token:
                raise NodeValidationError("Access token is required")
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Build the universal request node data
            universal_data = await self._build_universal_request(params, op_config)
            
            # Execute using universal request node
            result = await self.universal_node.execute(universal_data)
            
            # Process the result for Shopify-specific outputs
            return await self._process_result(result, params, operation)
            
        except Exception as e:
            logger.error(f"Error in Shopify operation: {str(e)}")
            return {
                "status": "error",
                "result": None,
                "error": str(e),
                "status_code": None,
                "response_headers": None,
                "product_id": None,
                "order_id": None,
                "customer_id": None,
                "collection_id": None,
                "inventory_item_id": None,
                "total_count": None
            }

    async def _build_universal_request(self, params: Dict[str, Any], op_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build request data for UniversalRequestNode."""
        # Start with base config
        config = self.CONFIG.copy()
        
        # Set up shop domain in base URL
        shop_domain = params.get("shop_domain")
        config["base_url"] = config["base_url"].format(shop_domain=shop_domain)
        
        # Set up authentication
        access_token = params.get("access_token")
        config["authentication"]["token"] = access_token
        
        # Build endpoint with path parameters
        endpoint = op_config["endpoint"]
        path_params = op_config.get("path_params", [])
        
        for param in path_params:
            value = params.get(param)
            if value is not None:
                placeholder = "{" + param + "}"
                endpoint = endpoint.replace(placeholder, str(value))
        
        # Build query parameters
        query_params = {}
        query_mappings = {
            "limit": "limit",
            "page_info": "page_info",
            "since_id": "since_id",
            "created_at_min": "created_at_min",
            "created_at_max": "created_at_max",
            "updated_at_min": "updated_at_min",
            "updated_at_max": "updated_at_max",
            "status": "status",
            "financial_status": "financial_status",
            "fulfillment_status": "fulfillment_status",
            "query": "query"
        }
        
        for param, query_param in query_mappings.items():
            if params.get(param) is not None:
                query_params[query_param] = params[param]
        
        # Handle inventory level operations with special query params
        if "inventory_level" in endpoint:
            if params.get("inventory_item_ids"):
                query_params["inventory_item_ids"] = params["inventory_item_ids"]
            if params.get("location_ids"):
                query_params["location_ids"] = params["location_ids"]
        
        # Build request body based on operation
        request_body = await self._build_request_body(params, op_config, endpoint)
        
        return {
            "params": {
                "config": config,
                "method": op_config["method"],
                "endpoint": endpoint,
                "query_params": query_params if query_params else None,
                "request_body": request_body,
                "timeout": config["timeouts"]["total"]
            }
        }

    async def _build_request_body(self, params: Dict[str, Any], op_config: Dict[str, Any], endpoint: str) -> Optional[Dict[str, Any]]:
        """Build request body for specific operations."""
        operation = params.get("operation", "")
        
        # Use explicit request_body if provided
        if params.get("request_body"):
            return params["request_body"]
        
        # Handle product creation/update
        if "create_product" in operation or "update_product" in operation:
            product_data = {
                "title": params.get("title"),
                "body_html": params.get("description", ""),
                "vendor": params.get("vendor", ""),
                "product_type": params.get("product_type", ""),
                "tags": params.get("tags", ""),
                "published": params.get("published", True)
            }
            return {"product": {k: v for k, v in product_data.items() if v is not None}}
        
        # Handle customer creation/update
        if "create_customer" in operation or "update_customer" in operation:
            customer_data = {
                "email": params.get("email"),
                "first_name": params.get("first_name"),
                "last_name": params.get("last_name"),
                "phone": params.get("phone"),
                "accepts_marketing": params.get("accepts_marketing", False)
            }
            return {"customer": {k: v for k, v in customer_data.items() if v is not None}}
        
        # Handle order creation/update
        if "create_order" in operation or "update_order" in operation:
            order_data = {
                "line_items": params.get("line_items", []),
                "financial_status": params.get("financial_status"),
                "fulfillment_status": params.get("fulfillment_status")
            }
            return {"order": {k: v for k, v in order_data.items() if v is not None}}
        
        # Handle collection creation/update
        if "create_collection" in operation or "update_collection" in operation or "create_custom_collection" in operation or "update_custom_collection" in operation:
            collection_data = {
                "title": params.get("title"),
                "body_html": params.get("description", ""),
                "sort_order": params.get("sort_order")
            }
            return {"collection": {k: v for k, v in collection_data.items() if v is not None}}
        
        # Handle smart collection creation/update
        if "create_smart_collection" in operation or "update_smart_collection" in operation:
            smart_collection_data = {
                "title": params.get("title"),
                "body_html": params.get("description", ""),
                "rules": params.get("rules", []),
                "sort_order": params.get("sort_order")
            }
            return {"smart_collection": {k: v for k, v in smart_collection_data.items() if v is not None}}
        
        # Handle fulfillment creation
        if "create_fulfillment" in operation:
            return {
                "fulfillment": {
                    "line_items": params.get("line_items", []),
                    "tracking_number": params.get("tracking_number"),
                    "tracking_company": params.get("tracking_company"),
                    "notify_customer": params.get("notify_customer", True)
                }
            }
        
        # Handle webhook creation/update
        if "create_webhook" in operation or "update_webhook" in operation:
            webhook_data = {
                "topic": params.get("topic"),
                "address": params.get("address"),
                "format": params.get("format", "json")
            }
            return {"webhook": {k: v for k, v in webhook_data.items() if v is not None}}
        
        # Handle inventory level operations
        if "adjust_inventory_level" in operation:
            return {
                "inventory_item_id": params.get("inventory_item_id"),
                "location_id": params.get("location_id"),
                "available_adjustment": params.get("available_adjustment")
            }
        
        if "set_inventory_level" in operation:
            return {
                "inventory_item_id": params.get("inventory_item_id"),
                "location_id": params.get("location_id"),
                "available": params.get("available")
            }
        
        if "connect_inventory_level" in operation:
            return {
                "inventory_item_id": params.get("inventory_item_id"),
                "location_id": params.get("location_id")
            }
        
        # Handle price rule creation/update
        if "create_price_rule" in operation or "update_price_rule" in operation:
            price_rule_data = {
                "title": params.get("title"),
                "target_type": params.get("target_type"),
                "target_selection": params.get("target_selection"),
                "value_type": params.get("value_type"),
                "value": params.get("value"),
                "starts_at": params.get("starts_at"),
                "ends_at": params.get("ends_at")
            }
            return {"price_rule": {k: v for k, v in price_rule_data.items() if v is not None}}
        
        # Handle discount code creation/update
        if "create_discount_code" in operation or "update_discount_code" in operation:
            return {
                "discount_code": {
                    "code": params.get("code"),
                    "usage_count": params.get("usage_count", 0)
                }
            }
        
        # Handle transaction creation
        if "create_transaction" in operation:
            return {
                "transaction": {
                    "kind": params.get("kind"),
                    "amount": params.get("amount")
                }
            }
        
        # Handle address operations
        if "create_customer_address" in operation or "update_customer_address" in operation:
            address_data = {
                "address1": params.get("address1"),
                "address2": params.get("address2"),
                "city": params.get("city"),
                "province": params.get("province"),
                "country": params.get("country"),
                "zip": params.get("zip"),
                "phone": params.get("phone"),
                "first_name": params.get("first_name"),
                "last_name": params.get("last_name")
            }
            return {"address": {k: v for k, v in address_data.items() if v is not None}}
        
        # Handle product image operations
        if "create_product_image" in operation or "update_product_image" in operation:
            return {
                "image": {
                    "src": params.get("src"),
                    "alt": params.get("alt"),
                    "position": params.get("position")
                }
            }
        
        return None

    async def _process_result(self, result: Dict[str, Any], params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Process result from UniversalRequestNode for Shopify-specific outputs."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("result", {})
        
        # Extract Shopify-specific fields
        product_id = None
        order_id = None
        customer_id = None
        collection_id = None
        inventory_item_id = None
        total_count = None
        
        if isinstance(response_data, dict):
            # Extract IDs from different response formats
            if response_data.get("product"):
                product_id = response_data["product"].get("id")
            elif response_data.get("order"):
                order_id = response_data["order"].get("id")
            elif response_data.get("customer"):
                customer_id = response_data["customer"].get("id")
            elif response_data.get("collection") or response_data.get("smart_collection") or response_data.get("custom_collection"):
                collection_obj = response_data.get("collection") or response_data.get("smart_collection") or response_data.get("custom_collection")
                collection_id = collection_obj.get("id")
            elif response_data.get("inventory_item"):
                inventory_item_id = response_data["inventory_item"].get("id")
            
            # Extract total count from list operations
            if "products" in response_data:
                total_count = len(response_data["products"])
            elif "orders" in response_data:
                total_count = len(response_data["orders"])
            elif "customers" in response_data:
                total_count = len(response_data["customers"])
            elif "collections" in response_data:
                total_count = len(response_data["collections"])
            elif response_data.get("count") is not None:
                total_count = response_data["count"]
        
        return {
            "status": result.get("status"),
            "result": response_data,
            "error": result.get("error"),
            "status_code": result.get("status_code"),
            "response_headers": result.get("response_headers"),
            "product_id": product_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "collection_id": collection_id,
            "inventory_item_id": inventory_item_id,
            "total_count": total_count
        }


# Helper class for creating Shopify API request objects
class ShopifyHelpers:
    """Helper functions for creating Shopify API request objects."""
    
    @staticmethod
    def create_product(title: str, description: str = "", vendor: str = "", product_type: str = "", tags: str = "", published: bool = True) -> Dict[str, Any]:
        """Create product request object."""
        return {
            "product": {
                "title": title,
                "body_html": description,
                "vendor": vendor,
                "product_type": product_type,
                "tags": tags,
                "published": published
            }
        }
    
    @staticmethod
    def create_customer(email: str, first_name: str = "", last_name: str = "", phone: str = "", accepts_marketing: bool = False) -> Dict[str, Any]:
        """Create customer request object."""
        return {
            "customer": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "accepts_marketing": accepts_marketing
            }
        }
    
    @staticmethod
    def create_order(line_items: List[Dict[str, Any]], financial_status: str = None, fulfillment_status: str = None) -> Dict[str, Any]:
        """Create order request object."""
        order_data = {"line_items": line_items}
        if financial_status:
            order_data["financial_status"] = financial_status
        if fulfillment_status:
            order_data["fulfillment_status"] = fulfillment_status
        return {"order": order_data}
    
    @staticmethod
    def create_line_item(variant_id: str, quantity: int, price: str = None) -> Dict[str, Any]:
        """Create line item for orders."""
        line_item = {
            "variant_id": variant_id,
            "quantity": quantity
        }
        if price:
            line_item["price"] = price
        return line_item
    
    @staticmethod
    def create_webhook(topic: str, address: str, format: str = "json") -> Dict[str, Any]:
        """Create webhook request object."""
        return {
            "webhook": {
                "topic": topic,
                "address": address,
                "format": format
            }
        }
    
    @staticmethod
    def create_price_rule(title: str, target_type: str, target_selection: str, value_type: str, value: str, starts_at: str = None, ends_at: str = None) -> Dict[str, Any]:
        """Create price rule request object."""
        price_rule_data = {
            "title": title,
            "target_type": target_type,
            "target_selection": target_selection,
            "value_type": value_type,
            "value": value
        }
        if starts_at:
            price_rule_data["starts_at"] = starts_at
        if ends_at:
            price_rule_data["ends_at"] = ends_at
        return {"price_rule": price_rule_data}


# Register with NodeRegistry if available
if __name__ == "__main__":
    import asyncio
    
    async def test_shopify_node():
        """Test the Shopify node with sample operations."""
        node = ShopifyNode()
        
        # Test schema
        schema = node.get_schema()
        print(f"Shopify Node Schema: {schema.node_type} v{schema.version}")
        print(f"Available operations: {len(node.OPERATIONS)}")
        print(f"Sample operations: {list(node.OPERATIONS.keys())[:10]}...")
        
        print("Shopify Node unified implementation ready!")
    
    asyncio.run(test_shopify_node())

try:
    from node_registry import NodeRegistry
    registry = NodeRegistry()
    registry.register("shopify", ShopifyNode)
    logger.debug("Node registered with registry")
except ImportError:
    logger.warning("Could not register ShopifyNode with registry - module not found")
except Exception as e:
    logger.debug(f"Error registering node with registry: {str(e)}")