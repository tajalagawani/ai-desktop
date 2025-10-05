#!/usr/bin/env python3
"""
Square Node - Unified Square API Integration
Comprehensive integration with Square REST API using UniversalRequestNode.
Supports all Square operations: payments, orders, customers, catalog, inventory, loyalty, and business management.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType, NodeValidationError

try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class SquareNode(BaseNode):
    """
    Square Node - Unified Square API Integration
    
    Comprehensive integration with Square REST API covering:
    - Payments, Refunds, Orders
    - Customers, Customer Groups, Customer Segments
    - Catalog, Inventory
    - Invoices, Subscriptions
    - Cards, Gift Cards, Loyalty
    - Locations, Merchants, Team Management
    - Devices, Disputes, Webhooks, Labor Management
    """
    
    CONFIG = {
        "base_url": "https://connect.squareup.com/v2",
        "sandbox_url": "https://connect.squareupsandbox.com/v2",
        "authentication": {
            "type": "bearer_token",
            "header": "Authorization"
        },
        "default_headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Square-Version": "2025-07-16"
        },
        "retry_config": {
            "max_attempts": 3,
            "backoff": "exponential",
            "retriable_codes": [429, 500, 502, 503, 504]
        },
        "rate_limiting": {
            "requests_per_second": 100,
            "burst_size": 200
        },
        "timeouts": {
            "connect": 10.0,
            "read": 30.0,
            "total": 60.0
        }
    }
    
    OPERATIONS = {
        # Authentication & OAuth
        "get_access_token": {
            "method": "POST",
            "endpoint": "/oauth2/token",
            "required_params": ["grant_type"]
        },
        "renew_token": {
            "method": "POST",
            "endpoint": "/oauth2/renew",
            "required_params": ["access_token"]
        },
        "revoke_token": {
            "method": "POST",
            "endpoint": "/oauth2/revoke",
            "required_params": ["access_token"]
        },
        
        # Payments API
        "create_payment": {
            "method": "POST",
            "endpoint": "/payments",
            "required_params": ["source_id", "amount_money"]
        },
        "get_payment": {
            "method": "GET",
            "endpoint": "/payments/{payment_id}",
            "required_params": ["payment_id"],
            "path_params": ["payment_id"]
        },
        "update_payment": {
            "method": "PUT",
            "endpoint": "/payments/{payment_id}",
            "required_params": ["payment_id"],
            "path_params": ["payment_id"]
        },
        "cancel_payment": {
            "method": "POST",
            "endpoint": "/payments/{payment_id}/cancel",
            "required_params": ["payment_id"],
            "path_params": ["payment_id"]
        },
        "complete_payment": {
            "method": "POST",
            "endpoint": "/payments/{payment_id}/complete",
            "required_params": ["payment_id"],
            "path_params": ["payment_id"]
        },
        "list_payments": {
            "method": "GET",
            "endpoint": "/payments",
            "required_params": []
        },
        
        # Refunds API
        "create_refund": {
            "method": "POST",
            "endpoint": "/refunds",
            "required_params": ["payment_id", "amount_money"]
        },
        "get_refund": {
            "method": "GET",
            "endpoint": "/refunds/{refund_id}",
            "required_params": ["refund_id"],
            "path_params": ["refund_id"]
        },
        "list_refunds": {
            "method": "GET",
            "endpoint": "/refunds",
            "required_params": []
        },
        
        # Checkout API
        "create_checkout": {
            "method": "POST",
            "endpoint": "/locations/{location_id}/checkouts",
            "required_params": ["location_id", "order"],
            "path_params": ["location_id"]
        },
        
        # Orders API
        "create_order": {
            "method": "POST",
            "endpoint": "/orders",
            "required_params": ["location_id"]
        },
        "update_order": {
            "method": "PUT",
            "endpoint": "/orders/{order_id}",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "batch_retrieve_orders": {
            "method": "POST",
            "endpoint": "/orders/batch-retrieve",
            "required_params": ["location_id"]
        },
        "calculate_order": {
            "method": "POST",
            "endpoint": "/orders/calculate",
            "required_params": ["order"]
        },
        "clone_order": {
            "method": "POST",
            "endpoint": "/orders/{order_id}/clone",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "search_orders": {
            "method": "POST",
            "endpoint": "/orders/search",
            "required_params": []
        },
        "retrieve_order": {
            "method": "GET",
            "endpoint": "/orders/{order_id}",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        "pay_order": {
            "method": "POST",
            "endpoint": "/orders/{order_id}/pay",
            "required_params": ["order_id"],
            "path_params": ["order_id"]
        },
        
        # Customers API
        "create_customer": {
            "method": "POST",
            "endpoint": "/customers",
            "required_params": []
        },
        "delete_customer": {
            "method": "DELETE",
            "endpoint": "/customers/{customer_id}",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "retrieve_customer": {
            "method": "GET",
            "endpoint": "/customers/{customer_id}",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "update_customer": {
            "method": "PUT",
            "endpoint": "/customers/{customer_id}",
            "required_params": ["customer_id"],
            "path_params": ["customer_id"]
        },
        "list_customers": {
            "method": "GET",
            "endpoint": "/customers",
            "required_params": []
        },
        "search_customers": {
            "method": "POST",
            "endpoint": "/customers/search",
            "required_params": []
        },
        "create_customer_card": {
            "method": "POST",
            "endpoint": "/customers/{customer_id}/cards",
            "required_params": ["customer_id", "card_nonce"],
            "path_params": ["customer_id"]
        },
        "delete_customer_card": {
            "method": "DELETE",
            "endpoint": "/customers/{customer_id}/cards/{card_id}",
            "required_params": ["customer_id", "card_id"],
            "path_params": ["customer_id", "card_id"]
        },
        
        # Customer Groups API
        "list_customer_groups": {
            "method": "GET",
            "endpoint": "/customers/groups",
            "required_params": []
        },
        "create_customer_group": {
            "method": "POST",
            "endpoint": "/customers/groups",
            "required_params": ["name"]
        },
        "delete_customer_group": {
            "method": "DELETE",
            "endpoint": "/customers/groups/{group_id}",
            "required_params": ["group_id"],
            "path_params": ["group_id"]
        },
        "retrieve_customer_group": {
            "method": "GET",
            "endpoint": "/customers/groups/{group_id}",
            "required_params": ["group_id"],
            "path_params": ["group_id"]
        },
        "update_customer_group": {
            "method": "PUT",
            "endpoint": "/customers/groups/{group_id}",
            "required_params": ["group_id"],
            "path_params": ["group_id"]
        },
        
        # Customer Segments API
        "list_customer_segments": {
            "method": "GET",
            "endpoint": "/customers/segments",
            "required_params": []
        },
        "retrieve_customer_segment": {
            "method": "GET",
            "endpoint": "/customers/segments/{segment_id}",
            "required_params": ["segment_id"],
            "path_params": ["segment_id"]
        },
        
        # Catalog API
        "batch_delete_catalog_objects": {
            "method": "POST",
            "endpoint": "/catalog/batch-delete",
            "required_params": ["object_ids"]
        },
        "batch_retrieve_catalog_objects": {
            "method": "POST",
            "endpoint": "/catalog/batch-retrieve",
            "required_params": ["object_ids"]
        },
        "batch_upsert_catalog_objects": {
            "method": "POST",
            "endpoint": "/catalog/batch-upsert",
            "required_params": ["batches"]
        },
        "create_catalog_image": {
            "method": "POST",
            "endpoint": "/catalog/images",
            "required_params": []
        },
        "update_catalog_image": {
            "method": "PUT",
            "endpoint": "/catalog/images/{image_id}",
            "required_params": ["image_id"],
            "path_params": ["image_id"]
        },
        "catalog_info": {
            "method": "GET",
            "endpoint": "/catalog/info",
            "required_params": []
        },
        "list_catalog": {
            "method": "GET",
            "endpoint": "/catalog/list",
            "required_params": []
        },
        "upsert_catalog_object": {
            "method": "POST",
            "endpoint": "/catalog/object",
            "required_params": ["object"]
        },
        "delete_catalog_object": {
            "method": "DELETE",
            "endpoint": "/catalog/object/{object_id}",
            "required_params": ["object_id"],
            "path_params": ["object_id"]
        },
        "retrieve_catalog_object": {
            "method": "GET",
            "endpoint": "/catalog/object/{object_id}",
            "required_params": ["object_id"],
            "path_params": ["object_id"]
        },
        "search_catalog_objects": {
            "method": "POST",
            "endpoint": "/catalog/search",
            "required_params": []
        },
        "search_catalog_items": {
            "method": "POST",
            "endpoint": "/catalog/search-catalog-items",
            "required_params": []
        },
        "update_item_modifier_lists": {
            "method": "POST",
            "endpoint": "/catalog/update-item-modifier-lists",
            "required_params": ["item_ids"]
        },
        "update_item_taxes": {
            "method": "POST",
            "endpoint": "/catalog/update-item-taxes",
            "required_params": ["item_ids"]
        },
        
        # Inventory API
        "retrieve_inventory_adjustment": {
            "method": "GET",
            "endpoint": "/inventory/adjustments/{adjustment_id}",
            "required_params": ["adjustment_id"],
            "path_params": ["adjustment_id"]
        },
        "batch_change_inventory": {
            "method": "POST",
            "endpoint": "/inventory/changes/batch-create",
            "required_params": ["changes"]
        },
        "batch_retrieve_inventory_changes": {
            "method": "POST",
            "endpoint": "/inventory/changes/batch-retrieve",
            "required_params": []
        },
        "batch_retrieve_inventory_counts": {
            "method": "POST",
            "endpoint": "/inventory/counts/batch-retrieve",
            "required_params": []
        },
        "retrieve_inventory_changes": {
            "method": "GET",
            "endpoint": "/inventory/changes",
            "required_params": []
        },
        "retrieve_inventory_count": {
            "method": "GET",
            "endpoint": "/inventory/{catalog_object_id}",
            "required_params": ["catalog_object_id"],
            "path_params": ["catalog_object_id"]
        },
        "retrieve_inventory_physical_count": {
            "method": "GET",
            "endpoint": "/inventory/physical-counts/{physical_count_id}",
            "required_params": ["physical_count_id"],
            "path_params": ["physical_count_id"]
        },
        
        # Invoices API
        "list_invoices": {
            "method": "GET",
            "endpoint": "/invoices",
            "required_params": ["location_id"]
        },
        "create_invoice": {
            "method": "POST",
            "endpoint": "/invoices",
            "required_params": ["invoice"]
        },
        "search_invoices": {
            "method": "POST",
            "endpoint": "/invoices/search",
            "required_params": ["query"]
        },
        "delete_invoice": {
            "method": "DELETE",
            "endpoint": "/invoices/{invoice_id}",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "get_invoice": {
            "method": "GET",
            "endpoint": "/invoices/{invoice_id}",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "update_invoice": {
            "method": "PUT",
            "endpoint": "/invoices/{invoice_id}",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "cancel_invoice": {
            "method": "POST",
            "endpoint": "/invoices/{invoice_id}/cancel",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "publish_invoice": {
            "method": "POST",
            "endpoint": "/invoices/{invoice_id}/publish",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        "send_invoice": {
            "method": "POST",
            "endpoint": "/invoices/{invoice_id}/send",
            "required_params": ["invoice_id"],
            "path_params": ["invoice_id"]
        },
        
        # Subscriptions API
        "create_subscription": {
            "method": "POST",
            "endpoint": "/subscriptions",
            "required_params": ["location_id"]
        },
        "bulk_swap_plan": {
            "method": "POST",
            "endpoint": "/subscriptions/bulk-swap-plan",
            "required_params": ["new_plan_variation_id"]
        },
        "search_subscriptions": {
            "method": "POST",
            "endpoint": "/subscriptions/search",
            "required_params": []
        },
        "retrieve_subscription": {
            "method": "GET",
            "endpoint": "/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "update_subscription": {
            "method": "PUT",
            "endpoint": "/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "delete_subscription_action": {
            "method": "DELETE",
            "endpoint": "/subscriptions/{subscription_id}/actions/{action_id}",
            "required_params": ["subscription_id", "action_id"],
            "path_params": ["subscription_id", "action_id"]
        },
        "change_billing_anchor_date": {
            "method": "POST",
            "endpoint": "/subscriptions/{subscription_id}/actions/change-billing-anchor-date",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "cancel_subscription": {
            "method": "POST",
            "endpoint": "/subscriptions/{subscription_id}/actions/cancel",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "list_subscription_events": {
            "method": "GET",
            "endpoint": "/subscriptions/{subscription_id}/events",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "pause_subscription": {
            "method": "POST",
            "endpoint": "/subscriptions/{subscription_id}/actions/pause",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "resume_subscription": {
            "method": "POST",
            "endpoint": "/subscriptions/{subscription_id}/actions/resume",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "swap_plan": {
            "method": "POST",
            "endpoint": "/subscriptions/{subscription_id}/actions/swap-plan",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        
        # Cards API
        "list_cards": {
            "method": "GET",
            "endpoint": "/cards",
            "required_params": []
        },
        "create_card": {
            "method": "POST",
            "endpoint": "/cards",
            "required_params": ["source_id"]
        },
        "retrieve_card": {
            "method": "GET",
            "endpoint": "/cards/{card_id}",
            "required_params": ["card_id"],
            "path_params": ["card_id"]
        },
        "disable_card": {
            "method": "POST",
            "endpoint": "/cards/{card_id}/disable",
            "required_params": ["card_id"],
            "path_params": ["card_id"]
        },
        
        # Gift Cards API
        "list_gift_cards": {
            "method": "GET",
            "endpoint": "/gift-cards",
            "required_params": []
        },
        "create_gift_card": {
            "method": "POST",
            "endpoint": "/gift-cards",
            "required_params": ["location_id"]
        },
        "retrieve_gift_card_from_gan": {
            "method": "POST",
            "endpoint": "/gift-cards/from-gan",
            "required_params": ["gan"]
        },
        "retrieve_gift_card_from_nonce": {
            "method": "POST",
            "endpoint": "/gift-cards/from-nonce",
            "required_params": ["nonce"]
        },
        "link_customer_to_gift_card": {
            "method": "POST",
            "endpoint": "/gift-cards/{gift_card_id}/link-customer",
            "required_params": ["gift_card_id", "customer_id"],
            "path_params": ["gift_card_id"]
        },
        "unlink_customer_from_gift_card": {
            "method": "POST",
            "endpoint": "/gift-cards/{gift_card_id}/unlink-customer",
            "required_params": ["gift_card_id"],
            "path_params": ["gift_card_id"]
        },
        "retrieve_gift_card": {
            "method": "GET",
            "endpoint": "/gift-cards/{gift_card_id}",
            "required_params": ["gift_card_id"],
            "path_params": ["gift_card_id"]
        },
        
        # Gift Card Activities API
        "list_gift_card_activities": {
            "method": "GET",
            "endpoint": "/gift-cards/activities",
            "required_params": []
        },
        "create_gift_card_activity": {
            "method": "POST",
            "endpoint": "/gift-cards/activities",
            "required_params": ["gift_card_activity"]
        },
        "retrieve_gift_card_activity": {
            "method": "GET",
            "endpoint": "/gift-cards/activities/{activity_id}",
            "required_params": ["activity_id"],
            "path_params": ["activity_id"]
        },
        
        # Loyalty API
        "create_loyalty_account": {
            "method": "POST",
            "endpoint": "/loyalty/accounts",
            "required_params": ["loyalty_account"]
        },
        "search_loyalty_accounts": {
            "method": "POST",
            "endpoint": "/loyalty/accounts/search",
            "required_params": ["query"]
        },
        "retrieve_loyalty_account": {
            "method": "GET",
            "endpoint": "/loyalty/accounts/{account_id}",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "accumulate_loyalty_points": {
            "method": "POST",
            "endpoint": "/loyalty/accounts/{account_id}/accumulate",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "adjust_loyalty_points": {
            "method": "POST",
            "endpoint": "/loyalty/accounts/{account_id}/adjust",
            "required_params": ["account_id"],
            "path_params": ["account_id"]
        },
        "search_loyalty_events": {
            "method": "POST",
            "endpoint": "/loyalty/events/search",
            "required_params": ["query"]
        },
        "list_loyalty_programs": {
            "method": "GET",
            "endpoint": "/loyalty/programs",
            "required_params": []
        },
        "retrieve_loyalty_program": {
            "method": "GET",
            "endpoint": "/loyalty/programs/{program_id}",
            "required_params": ["program_id"],
            "path_params": ["program_id"]
        },
        "calculate_loyalty_points": {
            "method": "POST",
            "endpoint": "/loyalty/programs/{program_id}/calculate",
            "required_params": ["program_id"],
            "path_params": ["program_id"]
        },
        "list_loyalty_promotions": {
            "method": "GET",
            "endpoint": "/loyalty/programs/{program_id}/promotions",
            "required_params": ["program_id"],
            "path_params": ["program_id"]
        },
        "create_loyalty_promotion": {
            "method": "POST",
            "endpoint": "/loyalty/programs/{program_id}/promotions",
            "required_params": ["program_id"],
            "path_params": ["program_id"]
        },
        "retrieve_loyalty_promotion": {
            "method": "GET",
            "endpoint": "/loyalty/programs/{program_id}/promotions/{promotion_id}",
            "required_params": ["program_id", "promotion_id"],
            "path_params": ["program_id", "promotion_id"]
        },
        "cancel_loyalty_promotion": {
            "method": "POST",
            "endpoint": "/loyalty/programs/{program_id}/promotions/{promotion_id}/cancel",
            "required_params": ["program_id", "promotion_id"],
            "path_params": ["program_id", "promotion_id"]
        },
        "create_loyalty_reward": {
            "method": "POST",
            "endpoint": "/loyalty/rewards",
            "required_params": ["reward"]
        },
        "search_loyalty_rewards": {
            "method": "POST",
            "endpoint": "/loyalty/rewards/search",
            "required_params": ["query"]
        },
        "delete_loyalty_reward": {
            "method": "DELETE",
            "endpoint": "/loyalty/rewards/{reward_id}",
            "required_params": ["reward_id"],
            "path_params": ["reward_id"]
        },
        "retrieve_loyalty_reward": {
            "method": "GET",
            "endpoint": "/loyalty/rewards/{reward_id}",
            "required_params": ["reward_id"],
            "path_params": ["reward_id"]
        },
        "redeem_loyalty_reward": {
            "method": "POST",
            "endpoint": "/loyalty/rewards/{reward_id}/redeem",
            "required_params": ["reward_id"],
            "path_params": ["reward_id"]
        },
        
        # Locations API
        "list_locations": {
            "method": "GET",
            "endpoint": "/locations",
            "required_params": []
        },
        "create_location": {
            "method": "POST",
            "endpoint": "/locations",
            "required_params": ["location"]
        },
        "retrieve_location": {
            "method": "GET",
            "endpoint": "/locations/{location_id}",
            "required_params": ["location_id"],
            "path_params": ["location_id"]
        },
        "update_location": {
            "method": "PUT",
            "endpoint": "/locations/{location_id}",
            "required_params": ["location_id"],
            "path_params": ["location_id"]
        },
        
        # Merchants API
        "list_merchants": {
            "method": "GET",
            "endpoint": "/merchants",
            "required_params": []
        },
        "retrieve_merchant": {
            "method": "GET",
            "endpoint": "/merchants/{merchant_id}",
            "required_params": ["merchant_id"],
            "path_params": ["merchant_id"]
        },
        
        # Devices API
        "list_device_codes": {
            "method": "GET",
            "endpoint": "/devices/codes",
            "required_params": []
        },
        "create_device_code": {
            "method": "POST",
            "endpoint": "/devices/codes",
            "required_params": ["device_code"]
        },
        "get_device_code": {
            "method": "GET",
            "endpoint": "/devices/codes/{code_id}",
            "required_params": ["code_id"],
            "path_params": ["code_id"]
        },
        
        # Disputes API
        "list_disputes": {
            "method": "GET",
            "endpoint": "/disputes",
            "required_params": []
        },
        "retrieve_dispute": {
            "method": "GET",
            "endpoint": "/disputes/{dispute_id}",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        "accept_dispute": {
            "method": "POST",
            "endpoint": "/disputes/{dispute_id}/accept",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        "list_dispute_evidence": {
            "method": "GET",
            "endpoint": "/disputes/{dispute_id}/evidence",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        "create_dispute_evidence_file": {
            "method": "POST",
            "endpoint": "/disputes/{dispute_id}/evidence-files",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        "create_dispute_evidence_text": {
            "method": "POST",
            "endpoint": "/disputes/{dispute_id}/evidence-text",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        "delete_dispute_evidence": {
            "method": "DELETE",
            "endpoint": "/disputes/{dispute_id}/evidence/{evidence_id}",
            "required_params": ["dispute_id", "evidence_id"],
            "path_params": ["dispute_id", "evidence_id"]
        },
        "retrieve_dispute_evidence": {
            "method": "GET",
            "endpoint": "/disputes/{dispute_id}/evidence/{evidence_id}",
            "required_params": ["dispute_id", "evidence_id"],
            "path_params": ["dispute_id", "evidence_id"]
        },
        "submit_evidence": {
            "method": "POST",
            "endpoint": "/disputes/{dispute_id}/submit-evidence",
            "required_params": ["dispute_id"],
            "path_params": ["dispute_id"]
        },
        
        # Team API
        "create_team_member": {
            "method": "POST",
            "endpoint": "/team-members",
            "required_params": ["team_member"]
        },
        "bulk_create_team_members": {
            "method": "POST",
            "endpoint": "/team-members/bulk-create",
            "required_params": ["team_members"]
        },
        "bulk_update_team_members": {
            "method": "POST",
            "endpoint": "/team-members/bulk-update",
            "required_params": ["team_members"]
        },
        "search_team_members": {
            "method": "POST",
            "endpoint": "/team-members/search",
            "required_params": ["query"]
        },
        "retrieve_team_member": {
            "method": "GET",
            "endpoint": "/team-members/{team_member_id}",
            "required_params": ["team_member_id"],
            "path_params": ["team_member_id"]
        },
        "update_team_member": {
            "method": "PUT",
            "endpoint": "/team-members/{team_member_id}",
            "required_params": ["team_member_id"],
            "path_params": ["team_member_id"]
        },
        "retrieve_wage_setting": {
            "method": "GET",
            "endpoint": "/team-members/{team_member_id}/wage-setting",
            "required_params": ["team_member_id"],
            "path_params": ["team_member_id"]
        },
        "update_wage_setting": {
            "method": "PUT",
            "endpoint": "/team-members/{team_member_id}/wage-setting",
            "required_params": ["team_member_id"],
            "path_params": ["team_member_id"]
        },
        
        # Labor API
        "list_break_types": {
            "method": "GET",
            "endpoint": "/labor/break-types",
            "required_params": []
        },
        "create_break_type": {
            "method": "POST",
            "endpoint": "/labor/break-types",
            "required_params": ["break_type"]
        },
        "delete_break_type": {
            "method": "DELETE",
            "endpoint": "/labor/break-types/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "get_break_type": {
            "method": "GET",
            "endpoint": "/labor/break-types/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "update_break_type": {
            "method": "PUT",
            "endpoint": "/labor/break-types/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "list_employee_wages": {
            "method": "GET",
            "endpoint": "/labor/employee-wages",
            "required_params": []
        },
        "get_employee_wage": {
            "method": "GET",
            "endpoint": "/labor/employee-wages/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "create_shift": {
            "method": "POST",
            "endpoint": "/labor/shifts",
            "required_params": ["shift"]
        },
        "search_shifts": {
            "method": "POST",
            "endpoint": "/labor/shifts/search",
            "required_params": ["query"]
        },
        "delete_shift": {
            "method": "DELETE",
            "endpoint": "/labor/shifts/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "get_shift": {
            "method": "GET",
            "endpoint": "/labor/shifts/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "update_shift": {
            "method": "PUT",
            "endpoint": "/labor/shifts/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "list_team_member_wages": {
            "method": "GET",
            "endpoint": "/labor/team-member-wages",
            "required_params": []
        },
        "get_team_member_wage": {
            "method": "GET",
            "endpoint": "/labor/team-member-wages/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        "list_workweek_configs": {
            "method": "GET",
            "endpoint": "/labor/workweek-configs",
            "required_params": []
        },
        "update_workweek_config": {
            "method": "PUT",
            "endpoint": "/labor/workweek-configs/{id}",
            "required_params": ["id"],
            "path_params": ["id"]
        },
        
        # Webhooks API
        "create_webhook_subscription": {
            "method": "POST",
            "endpoint": "/webhooks/subscriptions",
            "required_params": ["subscription"]
        },
        "delete_webhook_subscription": {
            "method": "DELETE",
            "endpoint": "/webhooks/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "retrieve_webhook_subscription": {
            "method": "GET",
            "endpoint": "/webhooks/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "update_webhook_subscription": {
            "method": "PUT",
            "endpoint": "/webhooks/subscriptions/{subscription_id}",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        "list_webhook_event_types": {
            "method": "GET",
            "endpoint": "/webhooks/event-types",
            "required_params": []
        },
        "list_webhook_subscriptions": {
            "method": "GET",
            "endpoint": "/webhooks/subscriptions",
            "required_params": []
        },
        "test_webhook_subscription": {
            "method": "POST",
            "endpoint": "/webhooks/subscriptions/{subscription_id}/test",
            "required_params": ["subscription_id"],
            "path_params": ["subscription_id"]
        },
        
        # Sites API
        "list_sites": {
            "method": "GET",
            "endpoint": "/sites",
            "required_params": []
        }
    }

    def __init__(self):
        super().__init__()
        self.client = None

    def get_schema(self) -> NodeSchema:
        return NodeSchema(
            name="square",
            description="Comprehensive Square API integration for payment processing and business management",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="The Square operation to perform",
                    required=True,
                    options=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="access_token",
                    type=NodeParameterType.STRING,
                    description="Square access token or personal access token",
                    required=True,
                    sensitive=True
                ),
                NodeParameter(
                    name="environment",
                    type=NodeParameterType.STRING,
                    description="Square environment",
                    required=False,
                    default="production",
                    options=["production", "sandbox"]
                ),
                NodeParameter(
                    name="square_version",
                    type=NodeParameterType.STRING,
                    description="Square API version",
                    required=False,
                    default="2025-07-16"
                ),
                # Dynamic parameters for various operations
                NodeParameter(
                    name="payment_id",
                    type=NodeParameterType.STRING,
                    description="Payment ID",
                    required=False
                ),
                NodeParameter(
                    name="refund_id",
                    type=NodeParameterType.STRING,
                    description="Refund ID",
                    required=False
                ),
                NodeParameter(
                    name="order_id",
                    type=NodeParameterType.STRING,
                    description="Order ID",
                    required=False
                ),
                NodeParameter(
                    name="customer_id",
                    type=NodeParameterType.STRING,
                    description="Customer ID",
                    required=False
                ),
                NodeParameter(
                    name="location_id",
                    type=NodeParameterType.STRING,
                    description="Location ID",
                    required=False
                ),
                NodeParameter(
                    name="merchant_id",
                    type=NodeParameterType.STRING,
                    description="Merchant ID",
                    required=False
                ),
                NodeParameter(
                    name="catalog_object_id",
                    type=NodeParameterType.STRING,
                    description="Catalog Object ID",
                    required=False
                ),
                NodeParameter(
                    name="inventory_adjustment_id",
                    type=NodeParameterType.STRING,
                    description="Inventory Adjustment ID",
                    required=False
                ),
                NodeParameter(
                    name="invoice_id",
                    type=NodeParameterType.STRING,
                    description="Invoice ID",
                    required=False
                ),
                NodeParameter(
                    name="subscription_id",
                    type=NodeParameterType.STRING,
                    description="Subscription ID",
                    required=False
                ),
                NodeParameter(
                    name="card_id",
                    type=NodeParameterType.STRING,
                    description="Card ID",
                    required=False
                ),
                NodeParameter(
                    name="gift_card_id",
                    type=NodeParameterType.STRING,
                    description="Gift Card ID",
                    required=False
                ),
                NodeParameter(
                    name="loyalty_account_id",
                    type=NodeParameterType.STRING,
                    description="Loyalty Account ID",
                    required=False
                ),
                NodeParameter(
                    name="team_member_id",
                    type=NodeParameterType.STRING,
                    description="Team Member ID",
                    required=False
                ),
                NodeParameter(
                    name="dispute_id",
                    type=NodeParameterType.STRING,
                    description="Dispute ID",
                    required=False
                ),
                NodeParameter(
                    name="webhook_subscription_id",
                    type=NodeParameterType.STRING,
                    description="Webhook Subscription ID",
                    required=False
                ),
                NodeParameter(
                    name="device_code_id",
                    type=NodeParameterType.STRING,
                    description="Device Code ID",
                    required=False
                ),
                NodeParameter(
                    name="shift_id",
                    type=NodeParameterType.STRING,
                    description="Shift ID",
                    required=False
                ),
                NodeParameter(
                    name="break_type_id",
                    type=NodeParameterType.STRING,
                    description="Break Type ID",
                    required=False
                ),
                NodeParameter(
                    name="customer_group_id",
                    type=NodeParameterType.STRING,
                    description="Customer Group ID",
                    required=False
                ),
                NodeParameter(
                    name="customer_segment_id",
                    type=NodeParameterType.STRING,
                    description="Customer Segment ID",
                    required=False
                ),
                NodeParameter(
                    name="loyalty_program_id",
                    type=NodeParameterType.STRING,
                    description="Loyalty Program ID",
                    required=False
                ),
                NodeParameter(
                    name="loyalty_promotion_id",
                    type=NodeParameterType.STRING,
                    description="Loyalty Promotion ID",
                    required=False
                ),
                NodeParameter(
                    name="loyalty_reward_id",
                    type=NodeParameterType.STRING,
                    description="Loyalty Reward ID",
                    required=False
                ),
                NodeParameter(
                    name="gift_card_activity_id",
                    type=NodeParameterType.STRING,
                    description="Gift Card Activity ID",
                    required=False
                ),
                # Data parameters for creating/updating
                NodeParameter(
                    name="data",
                    type=NodeParameterType.OBJECT,
                    description="Request data for operations that require a body",
                    required=False
                ),
                NodeParameter(
                    name="idempotency_key",
                    type=NodeParameterType.STRING,
                    description="Idempotency key for request (auto-generated if not provided)",
                    required=False
                ),
                NodeParameter(
                    name="params",
                    type=NodeParameterType.OBJECT,
                    description="Query parameters for the request",
                    required=False
                ),
                NodeParameter(
                    name="headers",
                    type=NodeParameterType.OBJECT,
                    description="Additional headers for the request",
                    required=False
                )
            ],
            outputs=[
                "success",
                "error",
                "data",
                "status_code",
                "payment_id",
                "order_id",
                "customer_id",
                "location_id",
                "merchant_id"
            ],
            metadata={
                "category": "payments",
                "vendor": "square",
                "api_version": "2025-07-16",
                "documentation": "https://developer.squareup.com/reference/square",
                "rate_limits": {
                    "requests_per_second": 100,
                    "varies_by_endpoint": True
                }
            }
        )

    def _get_config(self, environment: str = "production", square_version: str = "2025-07-16") -> Dict[str, Any]:
        """Get configuration for UniversalRequestNode."""
        config = self.CONFIG.copy()
        
        # Update base URL for environment
        if environment == "sandbox":
            config["base_url"] = config["sandbox_url"]
            
        # Update Square version in headers
        config["default_headers"]["Square-Version"] = square_version
        
        return config

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Square operation using UniversalRequestNode."""
        try:
            # Get operation details
            operation = parameters.get("operation")
            if not operation:
                raise NodeValidationError("Operation is required")
                
            if operation not in self.OPERATIONS:
                raise NodeValidationError(f"Unknown operation: {operation}")
                
            access_token = parameters.get("access_token")
            if not access_token:
                raise NodeValidationError("Access token is required")
                
            environment = parameters.get("environment", "production")
            square_version = parameters.get("square_version", "2025-07-16")
            
            # Get operation config
            op_config = self.OPERATIONS[operation]
            
            # Setup UniversalRequestNode config
            config = self._get_config(environment, square_version)
            
            # Initialize client if needed
            if not self.client:
                self.client = UniversalRequestNode(config)
            
            # Prepare request parameters with path substitution
            request_params = {}
            
            # Add all provided parameters for path substitution
            for key, value in parameters.items():
                if value is not None and key not in ["operation", "access_token", "environment", "square_version"]:
                    request_params[key] = value
            
            # Generate idempotency key if needed for payment operations
            if operation in ["create_payment", "create_refund"] and not parameters.get("idempotency_key"):
                request_params["idempotency_key"] = str(uuid.uuid4())
            
            # Extract request data and params
            request_data = parameters.get("data") or {}
            query_params = parameters.get("params") or {}
            additional_headers = parameters.get("headers") or {}
            
            # Add access token
            request_params["token"] = access_token
            
            # Make the request
            response = await self.client.request(
                method=op_config["method"],
                endpoint=op_config["endpoint"],
                data=request_data if request_data else None,
                params=query_params if query_params else None,
                headers=additional_headers if additional_headers else None,
                **request_params
            )
            
            # Extract specific IDs from response for convenience
            response_data = response.get("data", {})
            payment_id = None
            order_id = None
            customer_id = None
            location_id = None
            merchant_id = None
            
            if isinstance(response_data, dict):
                if "payment" in response_data:
                    payment_id = response_data["payment"].get("id")
                elif "id" in response_data and "status" in response_data and "source_type" in response_data:
                    payment_id = response_data["id"]
                
                if "order" in response_data:
                    order_id = response_data["order"].get("id")
                elif "id" in response_data and "state" in response_data:
                    order_id = response_data["id"]
                
                if "customer" in response_data:
                    customer_id = response_data["customer"].get("id")
                elif "id" in response_data and ("given_name" in response_data or "family_name" in response_data):
                    customer_id = response_data["id"]
                
                if "location" in response_data:
                    location_id = response_data["location"].get("id")
                elif "id" in response_data and "name" in response_data and "address" in response_data:
                    location_id = response_data["id"]
                
                if "merchant" in response_data:
                    merchant_id = response_data["merchant"].get("id")
            
            return {
                "success": response.get("status") == "success",
                "error": response.get("error"),
                "data": response_data,
                "status_code": response.get("status_code", 200),
                "payment_id": payment_id,
                "order_id": order_id,
                "customer_id": customer_id,
                "location_id": location_id,
                "merchant_id": merchant_id
            }
            
        except Exception as e:
            logger.error(f"Square operation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "status_code": 500,
                "payment_id": None,
                "order_id": None,
                "customer_id": None,
                "location_id": None,
                "merchant_id": None
            }

    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.close()

class SquareOperation:
    """Square operation constants."""
    # Constants remain the same for compatibility
    GET_ACCESS_TOKEN = "get_access_token"
    RENEW_TOKEN = "renew_token"
    REVOKE_TOKEN = "revoke_token"
    CREATE_PAYMENT = "create_payment"
    GET_PAYMENT = "get_payment"
    UPDATE_PAYMENT = "update_payment"
    CANCEL_PAYMENT = "cancel_payment"
    COMPLETE_PAYMENT = "complete_payment"
    LIST_PAYMENTS = "list_payments"
    CREATE_REFUND = "create_refund"
    GET_REFUND = "get_refund"
    LIST_REFUNDS = "list_refunds"
    CREATE_CHECKOUT = "create_checkout"
    CREATE_ORDER = "create_order"
    UPDATE_ORDER = "update_order"
    BATCH_RETRIEVE_ORDERS = "batch_retrieve_orders"
    CALCULATE_ORDER = "calculate_order"
    CLONE_ORDER = "clone_order"
    SEARCH_ORDERS = "search_orders"
    RETRIEVE_ORDER = "retrieve_order"
    PAY_ORDER = "pay_order"
    CREATE_CUSTOMER = "create_customer"
    DELETE_CUSTOMER = "delete_customer"
    RETRIEVE_CUSTOMER = "retrieve_customer"
    UPDATE_CUSTOMER = "update_customer"
    LIST_CUSTOMERS = "list_customers"
    SEARCH_CUSTOMERS = "search_customers"
    CREATE_CUSTOMER_CARD = "create_customer_card"
    DELETE_CUSTOMER_CARD = "delete_customer_card"
    LIST_CUSTOMER_GROUPS = "list_customer_groups"
    CREATE_CUSTOMER_GROUP = "create_customer_group"
    DELETE_CUSTOMER_GROUP = "delete_customer_group"
    RETRIEVE_CUSTOMER_GROUP = "retrieve_customer_group"
    UPDATE_CUSTOMER_GROUP = "update_customer_group"
    LIST_CUSTOMER_SEGMENTS = "list_customer_segments"
    RETRIEVE_CUSTOMER_SEGMENT = "retrieve_customer_segment"
    BATCH_DELETE_CATALOG_OBJECTS = "batch_delete_catalog_objects"
    BATCH_RETRIEVE_CATALOG_OBJECTS = "batch_retrieve_catalog_objects"
    BATCH_UPSERT_CATALOG_OBJECTS = "batch_upsert_catalog_objects"
    CREATE_CATALOG_IMAGE = "create_catalog_image"
    UPDATE_CATALOG_IMAGE = "update_catalog_image"
    CATALOG_INFO = "catalog_info"
    LIST_CATALOG = "list_catalog"
    UPSERT_CATALOG_OBJECT = "upsert_catalog_object"
    DELETE_CATALOG_OBJECT = "delete_catalog_object"
    RETRIEVE_CATALOG_OBJECT = "retrieve_catalog_object"
    SEARCH_CATALOG_OBJECTS = "search_catalog_objects"
    SEARCH_CATALOG_ITEMS = "search_catalog_items"
    UPDATE_ITEM_MODIFIER_LISTS = "update_item_modifier_lists"
    UPDATE_ITEM_TAXES = "update_item_taxes"
    RETRIEVE_INVENTORY_ADJUSTMENT = "retrieve_inventory_adjustment"
    BATCH_CHANGE_INVENTORY = "batch_change_inventory"
    BATCH_RETRIEVE_INVENTORY_CHANGES = "batch_retrieve_inventory_changes"
    BATCH_RETRIEVE_INVENTORY_COUNTS = "batch_retrieve_inventory_counts"
    RETRIEVE_INVENTORY_CHANGES = "retrieve_inventory_changes"
    RETRIEVE_INVENTORY_COUNT = "retrieve_inventory_count"
    RETRIEVE_INVENTORY_PHYSICAL_COUNT = "retrieve_inventory_physical_count"
    LIST_INVOICES = "list_invoices"
    CREATE_INVOICE = "create_invoice"
    SEARCH_INVOICES = "search_invoices"
    DELETE_INVOICE = "delete_invoice"
    GET_INVOICE = "get_invoice"
    UPDATE_INVOICE = "update_invoice"
    CANCEL_INVOICE = "cancel_invoice"
    PUBLISH_INVOICE = "publish_invoice"
    SEND_INVOICE = "send_invoice"
    CREATE_SUBSCRIPTION = "create_subscription"
    BULK_SWAP_PLAN = "bulk_swap_plan"
    SEARCH_SUBSCRIPTIONS = "search_subscriptions"
    RETRIEVE_SUBSCRIPTION = "retrieve_subscription"
    UPDATE_SUBSCRIPTION = "update_subscription"
    DELETE_SUBSCRIPTION_ACTION = "delete_subscription_action"
    CHANGE_BILLING_ANCHOR_DATE = "change_billing_anchor_date"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    LIST_SUBSCRIPTION_EVENTS = "list_subscription_events"
    PAUSE_SUBSCRIPTION = "pause_subscription"
    RESUME_SUBSCRIPTION = "resume_subscription"
    SWAP_PLAN = "swap_plan"
    LIST_CARDS = "list_cards"
    CREATE_CARD = "create_card"
    RETRIEVE_CARD = "retrieve_card"
    DISABLE_CARD = "disable_card"
    LIST_GIFT_CARDS = "list_gift_cards"
    CREATE_GIFT_CARD = "create_gift_card"
    RETRIEVE_GIFT_CARD_FROM_GAN = "retrieve_gift_card_from_gan"
    RETRIEVE_GIFT_CARD_FROM_NONCE = "retrieve_gift_card_from_nonce"
    LINK_CUSTOMER_TO_GIFT_CARD = "link_customer_to_gift_card"
    UNLINK_CUSTOMER_FROM_GIFT_CARD = "unlink_customer_from_gift_card"
    RETRIEVE_GIFT_CARD = "retrieve_gift_card"
    LIST_GIFT_CARD_ACTIVITIES = "list_gift_card_activities"
    CREATE_GIFT_CARD_ACTIVITY = "create_gift_card_activity"
    RETRIEVE_GIFT_CARD_ACTIVITY = "retrieve_gift_card_activity"
    CREATE_LOYALTY_ACCOUNT = "create_loyalty_account"
    SEARCH_LOYALTY_ACCOUNTS = "search_loyalty_accounts"
    RETRIEVE_LOYALTY_ACCOUNT = "retrieve_loyalty_account"
    ACCUMULATE_LOYALTY_POINTS = "accumulate_loyalty_points"
    ADJUST_LOYALTY_POINTS = "adjust_loyalty_points"
    SEARCH_LOYALTY_EVENTS = "search_loyalty_events"
    LIST_LOYALTY_PROGRAMS = "list_loyalty_programs"
    RETRIEVE_LOYALTY_PROGRAM = "retrieve_loyalty_program"
    CALCULATE_LOYALTY_POINTS = "calculate_loyalty_points"
    LIST_LOYALTY_PROMOTIONS = "list_loyalty_promotions"
    CREATE_LOYALTY_PROMOTION = "create_loyalty_promotion"
    RETRIEVE_LOYALTY_PROMOTION = "retrieve_loyalty_promotion"
    CANCEL_LOYALTY_PROMOTION = "cancel_loyalty_promotion"
    CREATE_LOYALTY_REWARD = "create_loyalty_reward"
    SEARCH_LOYALTY_REWARDS = "search_loyalty_rewards"
    DELETE_LOYALTY_REWARD = "delete_loyalty_reward"
    RETRIEVE_LOYALTY_REWARD = "retrieve_loyalty_reward"
    REDEEM_LOYALTY_REWARD = "redeem_loyalty_reward"
    LIST_LOCATIONS = "list_locations"
    CREATE_LOCATION = "create_location"
    RETRIEVE_LOCATION = "retrieve_location"
    UPDATE_LOCATION = "update_location"
    LIST_MERCHANTS = "list_merchants"
    RETRIEVE_MERCHANT = "retrieve_merchant"
    LIST_DEVICE_CODES = "list_device_codes"
    CREATE_DEVICE_CODE = "create_device_code"
    GET_DEVICE_CODE = "get_device_code"
    LIST_DISPUTES = "list_disputes"
    RETRIEVE_DISPUTE = "retrieve_dispute"
    ACCEPT_DISPUTE = "accept_dispute"
    LIST_DISPUTE_EVIDENCE = "list_dispute_evidence"
    CREATE_DISPUTE_EVIDENCE_FILE = "create_dispute_evidence_file"
    CREATE_DISPUTE_EVIDENCE_TEXT = "create_dispute_evidence_text"
    DELETE_DISPUTE_EVIDENCE = "delete_dispute_evidence"
    RETRIEVE_DISPUTE_EVIDENCE = "retrieve_dispute_evidence"
    SUBMIT_EVIDENCE = "submit_evidence"
    CREATE_TEAM_MEMBER = "create_team_member"
    BULK_CREATE_TEAM_MEMBERS = "bulk_create_team_members"
    BULK_UPDATE_TEAM_MEMBERS = "bulk_update_team_members"
    SEARCH_TEAM_MEMBERS = "search_team_members"
    RETRIEVE_TEAM_MEMBER = "retrieve_team_member"
    UPDATE_TEAM_MEMBER = "update_team_member"
    RETRIEVE_WAGE_SETTING = "retrieve_wage_setting"
    UPDATE_WAGE_SETTING = "update_wage_setting"
    LIST_BREAK_TYPES = "list_break_types"
    CREATE_BREAK_TYPE = "create_break_type"
    DELETE_BREAK_TYPE = "delete_break_type"
    GET_BREAK_TYPE = "get_break_type"
    UPDATE_BREAK_TYPE = "update_break_type"
    LIST_EMPLOYEE_WAGES = "list_employee_wages"
    GET_EMPLOYEE_WAGE = "get_employee_wage"
    CREATE_SHIFT = "create_shift"
    SEARCH_SHIFTS = "search_shifts"
    DELETE_SHIFT = "delete_shift"
    GET_SHIFT = "get_shift"
    UPDATE_SHIFT = "update_shift"
    LIST_TEAM_MEMBER_WAGES = "list_team_member_wages"
    GET_TEAM_MEMBER_WAGE = "get_team_member_wage"
    LIST_WORKWEEK_CONFIGS = "list_workweek_configs"
    UPDATE_WORKWEEK_CONFIG = "update_workweek_config"
    CREATE_WEBHOOK_SUBSCRIPTION = "create_webhook_subscription"
    DELETE_WEBHOOK_SUBSCRIPTION = "delete_webhook_subscription"
    RETRIEVE_WEBHOOK_SUBSCRIPTION = "retrieve_webhook_subscription"
    UPDATE_WEBHOOK_SUBSCRIPTION = "update_webhook_subscription"
    LIST_WEBHOOK_EVENT_TYPES = "list_webhook_event_types"
    LIST_WEBHOOK_SUBSCRIPTIONS = "list_webhook_subscriptions"
    TEST_WEBHOOK_SUBSCRIPTION = "test_webhook_subscription"
    LIST_SITES = "list_sites"

class SquareHelper:
    """Helper utilities for Square API operations."""
    
    @staticmethod
    def format_money(amount_cents: int, currency: str = "USD") -> Dict[str, Any]:
        """Format money object for Square API."""
        return {
            "amount": amount_cents,
            "currency": currency
        }
    
    @staticmethod
    def generate_idempotency_key() -> str:
        """Generate a unique idempotency key."""
        return str(uuid.uuid4())

# Register the node
if __name__ == "__main__":
    node = SquareNode()
    print(f"SquareNode registered with {len(node.get_schema().parameters)} parameters")