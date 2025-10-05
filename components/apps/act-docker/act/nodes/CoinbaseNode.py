#!/usr/bin/env python3
"""
Coinbase Node - Enhanced with ALL 13 advanced features
Configuration is embedded directly in the node - no separate config.json needed
Comprehensive Coinbase Advanced Trade API integration
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the Enhanced UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class CoinbaseNode(BaseNode):
    """
    Enhanced Coinbase node with ALL 13 advanced features.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "coinbase",
            "display_name": "Coinbase Advanced Trade",
            "description": "Comprehensive Coinbase Advanced Trade API integration for cryptocurrency trading, accounts, orders, products, portfolios, and market data",
            "category": "cryptocurrency",
            "vendor": "coinbase",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["coinbase", "crypto", "trading", "bitcoin", "ethereum", "orders", "portfolios", "market-data"],
            "documentation_url": "https://docs.cdp.coinbase.com/advanced-trade/docs/rest-api-overview",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/coinbase.svg",
            "color": "#0052FF",
            "created_at": "2025-08-26T00:00:00Z",
            "updated_at": "2025-08-26T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.coinbase.com",
            "authentication": {
                "type": "api_key_hmac",
                "header": "CB-ACCESS-SIGN"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ACT-Workflow/2.0",
                "CB-VERSION": "2015-07-22"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential_jitter",
                "base_delay": 1.0,
                "max_delay": 60.0,
                "jitter": True,
                "retriable_codes": [429, 500, 502, 503, 504],
                "retriable_exceptions": ["aiohttp.ClientTimeout", "aiohttp.ClientConnectorError"],
                "timeout_ms": 30000
            },
            "rate_limiting": {
                "requests_per_minute": 500,
                "requests_per_second": 15.0,
                "burst_size": 5,
                "cost_per_request": 1,
                "quota_type": "requests"
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        },
        
        # Enhanced pricing information
        "pricing": {
            "cost_per_request": 0.001,
            "billing_unit": "requests",
            "free_tier_limit": 10000
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "rate_limit_usage"],
            "alerts": {
                "error_rate_threshold": 0.05,
                "response_time_threshold": 5000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{hash}",
            "ttl_seconds": 60,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "signature"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": True,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/api/v3/brokerage/time"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://docs.cdp.coinbase.com/advanced-trade/docs/rest-api-overview",
            "setup_guide": "https://docs.cdp.coinbase.com/advanced-trade/docs/auth",
            "troubleshooting": "https://docs.cdp.coinbase.com/advanced-trade/docs/error-codes",
            "changelog": "https://docs.cdp.coinbase.com/advanced-trade/docs/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Coinbase API key",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-f0-9]{32}$",
                    "message": "API key must be a 32-character hex string",
                    "minLength": 32,
                    "maxLength": 32
                }
            },
            "api_secret": {
                "type": "string",
                "description": "Coinbase API secret",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "minLength": 40
                }
            },
            "operation": {
                "type": "string",
                "description": "The Coinbase operation to perform",
                "required": True,
                "group": "Operation",
                "enum": [
                    "list_accounts", "get_account", "create_order", "cancel_orders",
                    "list_orders", "get_order", "preview_order", "list_products",
                    "get_product", "get_product_candles", "get_market_trades",
                    "get_best_bid_ask", "list_portfolios", "create_portfolio",
                    "get_portfolio_breakdown", "create_convert_quote", "get_convert_trade",
                    "get_server_time", "list_fills"
                ]
            },
            "product_id": {
                "type": "string",
                "description": "Product ID (e.g., BTC-USD, ETH-USD)",
                "required": False,
                "group": "Trading",
                "examples": ["BTC-USD", "ETH-USD", "LTC-USD"],
                "validation": {
                    "pattern": "^[A-Z0-9]+-[A-Z0-9]+$"
                }
            },
            "account_uuid": {
                "type": "string",
                "description": "Account UUID",
                "required": False,
                "group": "Account",
                "validation": {
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                }
            },
            "order_id": {
                "type": "string",
                "description": "Order ID",
                "required": False,
                "group": "Trading"
            },
            "client_order_id": {
                "type": "string",
                "description": "Client-specified order ID",
                "required": False,
                "group": "Trading"
            },
            "portfolio_uuid": {
                "type": "string",
                "description": "Portfolio UUID",
                "required": False,
                "group": "Portfolio"
            },
            "side": {
                "type": "string",
                "description": "Order side",
                "required": False,
                "group": "Trading",
                "validation": {
                    "enum": ["BUY", "SELL"]
                }
            },
            "order_type": {
                "type": "string",
                "description": "Order type configuration",
                "required": False,
                "group": "Trading",
                "default": "market_market_ioc",
                "validation": {
                    "enum": ["market_market_ioc", "limit_limit_gtc", "limit_limit_gtd", "stop_limit_stop_limit_gtc"]
                }
            },
            "base_size": {
                "type": "string",
                "description": "Base currency amount",
                "required": False,
                "group": "Trading",
                "examples": ["0.1", "1.0", "0.5"]
            },
            "quote_size": {
                "type": "string",
                "description": "Quote currency amount",
                "required": False,
                "group": "Trading",
                "examples": ["100", "500", "1000"]
            },
            "limit_price": {
                "type": "string",
                "description": "Limit price for limit orders",
                "required": False,
                "group": "Trading"
            },
            "limit": {
                "type": "integer",
                "description": "Number of results to return",
                "required": False,
                "default": 50,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "cursor": {
                "type": "string",
                "description": "Pagination cursor",
                "required": False,
                "group": "Pagination"
            },
            "start": {
                "type": "string",
                "description": "Start time (Unix timestamp)",
                "required": False,
                "group": "Time Range"
            },
            "end": {
                "type": "string",
                "description": "End time (Unix timestamp)",
                "required": False,
                "group": "Time Range"
            },
            "granularity": {
                "type": "string",
                "description": "Candle granularity",
                "required": False,
                "group": "Market Data",
                "default": "ONE_HOUR",
                "validation": {
                    "enum": ["ONE_MINUTE", "FIVE_MINUTE", "FIFTEEN_MINUTE", "THIRTY_MINUTE", "ONE_HOUR", "TWO_HOUR", "SIX_HOUR", "ONE_DAY"]
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Coinbase API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Coinbase API"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Coinbase error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "list_accounts": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "get_account": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "create_order": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "list_orders": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "get_order": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "cancel_orders": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "list_products": {
                "required_env_keys": [],
                "optional_env_keys": []
            },
            "get_product": {
                "required_env_keys": [],
                "optional_env_keys": []
            },
            "get_product_candles": {
                "required_env_keys": [],
                "optional_env_keys": []
            },
            "get_market_trades": {
                "required_env_keys": [],
                "optional_env_keys": []
            },
            "get_best_bid_ask": {
                "required_env_keys": [],
                "optional_env_keys": []
            },
            "get_server_time": {
                "required_env_keys": [],
                "optional_env_keys": []
            },
            "list_portfolios": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "create_portfolio": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "get_portfolio_breakdown": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "create_convert_quote": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "get_convert_trade": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            },
            "list_fills": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to Coinbase
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid API credentials",
            "403": "Forbidden - Request not allowed",
            "404": "Not Found - Resource not found",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Coinbase server error",
            "502": "Bad Gateway - Coinbase server temporarily unavailable",
            "503": "Service Unavailable - Coinbase server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features
    OPERATIONS = {
        "list_accounts": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/accounts",
            "required_params": [],
            "optional_params": ["limit", "cursor"],
            "display_name": "List Accounts",
            "description": "List all trading accounts and their balances",
            "group": "Account Management",
            "tags": ["accounts", "balances", "trading"],
            "rate_limit_cost": 1,
            "cache_ttl": 30,
            "response_type": "object",
            
            # 1. Operation-specific output schema
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "accounts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "uuid": {"type": "string"},
                                    "name": {"type": "string"},
                                    "currency": {"type": "string"},
                                    "available_balance": {
                                        "type": "object",
                                        "properties": {
                                            "value": {"type": "string"},
                                            "currency": {"type": "string"}
                                        }
                                    },
                                    "default": {"type": "boolean"},
                                    "active": {"type": "boolean"},
                                    "created_at": {"type": "string"},
                                    "updated_at": {"type": "string"},
                                    "deleted_at": {"type": "string"},
                                    "type": {"type": "string"},
                                    "ready": {"type": "boolean"},
                                    "hold": {
                                        "type": "object",
                                        "properties": {
                                            "value": {"type": "string"},
                                            "currency": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "has_next": {"type": "boolean"},
                        "cursor": {"type": "string"},
                        "size": {"type": "integer"}
                    }
                }
            },
            
            # 2. Array templates for complex inputs
            "array_templates": {},
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [],
            
            # 4. Advanced validation rules
            "validation_rules": {
                "limit": {
                    "pattern": "",
                    "message": "Limit must be between 1 and 250",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 250,
                    "required": False
                }
            },
            
            # 5. Rate limiting
            "rate_limiting": {
                "requests_per_minute": 300,
                "cost": 1,
                "burst_allowance": 10
            },
            
            # 6. Pagination
            "pagination": {
                "type": "cursor",
                "cursor_param": "cursor",
                "limit_param": "limit",
                "has_more_field": "has_next",
                "default_limit": 49,
                "max_limit": 250
            },
            
            # 7. Error handling
            "error_handling": {
                "retry_codes": [429, 500, 502, 503, 504],
                "timeout_codes": [408],
                "fatal_codes": [401, 403],
                "custom_messages": {
                    "401": "Invalid API credentials. Check your API key and secret.",
                    "403": "Access denied. Verify your API permissions."
                }
            },
            
            # 8. Field mapping & transformation
            "field_mapping": {
                "input_transforms": {},
                "output_transforms": {
                    "created_at": "format_timestamp",
                    "updated_at": "format_timestamp"
                },
                "field_aliases": {}
            },
            
            # 9. Webhook support
            "webhook_support": {
                "supported": False
            },
            
            # 10. Testing mode
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "accounts": [
                        {
                            "uuid": "test-account-uuid",
                            "name": "BTC Wallet",
                            "currency": "BTC",
                            "available_balance": {"value": "1.0", "currency": "BTC"},
                            "default": True,
                            "active": True,
                            "created_at": "2023-01-01T00:00:00Z",
                            "updated_at": "2023-01-01T00:00:00Z",
                            "type": "ACCOUNT_TYPE_CRYPTO",
                            "ready": True,
                            "hold": {"value": "0.0", "currency": "BTC"}
                        }
                    ],
                    "has_next": False,
                    "cursor": "",
                    "size": 1
                }
            },
            
            # 11. Performance monitoring
            "performance_monitoring": {
                "track_latency": True,
                "track_errors": True,
                "alert_on_failure_rate": 0.1,
                "alert_on_latency_ms": 2000
            },
            
            # 12. Caching strategy
            "caching_strategy": {
                "enabled": True,
                "ttl_seconds": 30,
                "cache_key_fields": ["limit"],
                "invalidate_on": ["create_order", "cancel_orders"]
            },
            
            # 13. Documentation links
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getaccounts",
                "examples": "https://docs.cdp.coinbase.com/advanced-trade/docs/auth#examples",
                "troubleshooting": "https://docs.cdp.coinbase.com/advanced-trade/docs/error-codes"
            },
            
            "auth": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "optional_env_keys": [],
                "required_params": ["api_key", "api_secret"],
                "auth_type": "hmac_signature",
                "auth_description": "Requires Coinbase API key and secret for HMAC authentication"
            },
            "examples": [
                {
                    "name": "List all accounts",
                    "description": "Get all trading accounts with default limit",
                    "input": {
                        "limit": 50
                    }
                },
                {
                    "name": "List accounts with pagination",
                    "description": "Get accounts with specific limit and cursor",
                    "input": {
                        "limit": 10,
                        "cursor": "dXNlcl9pZDoxMDA="
                    }
                }
            ]
        },
        
        "get_account": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/accounts/{account_uuid}",
            "required_params": ["account_uuid"],
            "optional_params": [],
            "display_name": "Get Account",
            "description": "Get detailed information about a specific account",
            "group": "Account Management",
            "tags": ["account", "balance", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 15,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "account": {
                            "type": "object",
                            "properties": {
                                "uuid": {"type": "string"},
                                "name": {"type": "string"},
                                "currency": {"type": "string"},
                                "available_balance": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "string"},
                                        "currency": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "account_uuid": {
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    "message": "Account UUID must be a valid UUID format",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "rate_limiting": {"requests_per_minute": 300, "cost": 1, "burst_allowance": 10},
            "pagination": None,
            "error_handling": {
                "retry_codes": [429, 500, 502, 503, 504],
                "timeout_codes": [408],
                "fatal_codes": [401, 403, 404],
                "custom_messages": {"404": "Account not found. Verify the account UUID."}
            },
            "field_mapping": {"input_transforms": {}, "output_transforms": {}, "field_aliases": {}},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "account": {
                        "uuid": "test-account-uuid",
                        "name": "BTC Wallet",
                        "currency": "BTC",
                        "available_balance": {"value": "1.0", "currency": "BTC"}
                    }
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 15, "cache_key_fields": ["account_uuid"]},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getaccount"
            },
            
            "auth": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "required_params": ["api_key", "api_secret"],
                "auth_type": "hmac_signature"
            },
            "examples": [
                {
                    "name": "Get specific account",
                    "description": "Get details for a specific account by UUID",
                    "input": {"account_uuid": "12345678-1234-1234-1234-123456789abc"}
                }
            ]
        },
        
        "create_order": {
            "method": "POST",
            "endpoint": "/api/v3/brokerage/orders",
            "required_params": ["product_id", "side"],
            "optional_params": ["order_type", "base_size", "quote_size", "limit_price", "client_order_id"],
            "body_parameters": ["client_order_id", "product_id", "side", "order_configuration"],
            "display_name": "Create Order",
            "description": "Place a buy or sell order for cryptocurrency",
            "group": "Trading",
            "tags": ["order", "buy", "sell", "trading"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "failure_reason": {"type": "string"},
                        "order_id": {"type": "string"},
                        "success_response": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string"},
                                "product_id": {"type": "string"},
                                "side": {"type": "string"},
                                "client_order_id": {"type": "string"}
                            }
                        }
                    }
                }
            },
            
            "array_templates": {},
            "parameter_dependencies": [
                {
                    "when_field": "order_type",
                    "when_value": "market_market_ioc",
                    "then_require": [],
                    "then_optional": ["base_size", "quote_size"],
                    "require_one_of": ["base_size", "quote_size"],
                    "mutually_exclusive": []
                },
                {
                    "when_field": "order_type",
                    "when_value": "limit_limit_gtc",
                    "then_require": ["base_size", "limit_price"],
                    "then_optional": [],
                    "require_one_of": [],
                    "mutually_exclusive": ["quote_size"]
                }
            ],
            
            "validation_rules": {
                "product_id": {
                    "pattern": "^[A-Z0-9]+-[A-Z0-9]+$",
                    "message": "Product ID must be in format XXX-XXX (e.g., BTC-USD)",
                    "pattern_type": "regex",
                    "required": True
                },
                "side": {
                    "pattern": "^(BUY|SELL)$",
                    "message": "Side must be BUY or SELL",
                    "pattern_type": "regex",
                    "required": True
                },
                "base_size": {
                    "pattern": "^[0-9]+(\\.[0-9]+)?$",
                    "message": "Base size must be a positive number",
                    "pattern_type": "regex",
                    "min_value": 0.00000001,
                    "required": False
                }
            },
            
            "rate_limiting": {"requests_per_minute": 150, "cost": 2, "burst_allowance": 5},
            "pagination": None,
            "error_handling": {
                "retry_codes": [429, 500, 502, 503, 504],
                "timeout_codes": [408],
                "fatal_codes": [400, 401, 403],
                "custom_messages": {
                    "400": "Invalid order parameters. Check product ID, size, and price.",
                    "403": "Insufficient permissions or balance."
                }
            },
            "field_mapping": {
                "input_transforms": {"client_order_id": "generate_uuid_if_empty"},
                "output_transforms": {},
                "field_aliases": {}
            },
            "webhook_support": {
                "supported": True,
                "events": ["order.created", "order.filled", "order.cancelled"],
                "webhook_url_param": "webhook_url"
            },
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "success": True,
                    "order_id": "test-order-id-12345",
                    "success_response": {
                        "order_id": "test-order-id-12345",
                        "product_id": "BTC-USD",
                        "side": "BUY",
                        "client_order_id": "test-client-order-id"
                    }
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True, "alert_on_failure_rate": 0.05},
            "caching_strategy": {"enabled": False},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_postorder"
            },
            
            "auth": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "required_params": ["api_key", "api_secret"],
                "auth_type": "hmac_signature"
            },
            "examples": [
                {
                    "name": "Market buy order",
                    "description": "Place a market buy order with quote size",
                    "input": {
                        "product_id": "BTC-USD",
                        "side": "BUY",
                        "order_type": "market_market_ioc",
                        "quote_size": "100"
                    }
                },
                {
                    "name": "Limit buy order",
                    "description": "Place a limit buy order with base size and price",
                    "input": {
                        "product_id": "BTC-USD",
                        "side": "BUY",
                        "order_type": "limit_limit_gtc",
                        "base_size": "0.01",
                        "limit_price": "45000"
                    }
                }
            ]
        },
        
        "list_orders": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/orders/historical/batch",
            "required_params": [],
            "optional_params": ["product_id", "limit", "cursor", "start", "end"],
            "display_name": "List Orders",
            "description": "List historical orders with optional filtering",
            "group": "Trading",
            "tags": ["orders", "history", "trading"],
            "rate_limit_cost": 1,
            "cache_ttl": 10,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "orders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "order_id": {"type": "string"},
                                    "product_id": {"type": "string"},
                                    "user_id": {"type": "string"},
                                    "order_configuration": {"type": "object"},
                                    "side": {"type": "string"},
                                    "client_order_id": {"type": "string"},
                                    "status": {"type": "string"},
                                    "time_in_force": {"type": "string"},
                                    "created_time": {"type": "string"},
                                    "completion_percentage": {"type": "string"},
                                    "filled_size": {"type": "string"},
                                    "average_filled_price": {"type": "string"},
                                    "fee": {"type": "string"},
                                    "number_of_fills": {"type": "string"},
                                    "filled_value": {"type": "string"},
                                    "pending_cancel": {"type": "boolean"},
                                    "size_in_quote": {"type": "boolean"},
                                    "total_fees": {"type": "string"},
                                    "size_inclusive_of_fees": {"type": "boolean"},
                                    "total_value_after_fees": {"type": "string"},
                                    "trigger_status": {"type": "string"},
                                    "order_type": {"type": "string"},
                                    "reject_reason": {"type": "string"},
                                    "settled": {"type": "boolean"},
                                    "product_type": {"type": "string"},
                                    "reject_message": {"type": "string"},
                                    "cancel_message": {"type": "string"}
                                }
                            }
                        },
                        "has_next": {"type": "boolean"},
                        "cursor": {"type": "string"},
                        "sequence": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "limit": {"min_value": 1, "max_value": 1000, "required": False}
            },
            
            "rate_limiting": {"requests_per_minute": 300, "cost": 1, "burst_allowance": 10},
            "pagination": {
                "type": "cursor",
                "cursor_param": "cursor",
                "limit_param": "limit",
                "has_more_field": "has_next",
                "default_limit": 100,
                "max_limit": 1000
            },
            "error_handling": {"retry_codes": [429, 500, 502, 503, 504], "fatal_codes": [401, 403]},
            "field_mapping": {"output_transforms": {"created_time": "format_timestamp"}},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "orders": [
                        {
                            "order_id": "test-order-123",
                            "product_id": "BTC-USD",
                            "side": "BUY",
                            "status": "FILLED",
                            "created_time": "2023-01-01T00:00:00Z",
                            "filled_size": "0.01",
                            "average_filled_price": "45000"
                        }
                    ],
                    "has_next": False,
                    "cursor": ""
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 10, "cache_key_fields": ["product_id", "limit"]},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_gethistoricalorders"
            },
            
            "auth": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "required_params": ["api_key", "api_secret"],
                "auth_type": "hmac_signature"
            },
            "examples": [
                {
                    "name": "List all orders",
                    "description": "Get recent order history",
                    "input": {"limit": 50}
                },
                {
                    "name": "List BTC orders",
                    "description": "Get BTC-USD order history",
                    "input": {"product_id": "BTC-USD", "limit": 25}
                }
            ]
        },
        
        "get_order": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/orders/historical/{order_id}",
            "required_params": ["order_id"],
            "optional_params": [],
            "display_name": "Get Order",
            "description": "Get details of a specific order by ID",
            "group": "Trading",
            "tags": ["order", "details", "status"],
            "rate_limit_cost": 1,
            "cache_ttl": 15,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string"},
                                "product_id": {"type": "string"},
                                "side": {"type": "string"},
                                "status": {"type": "string"},
                                "created_time": {"type": "string"}
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "order_id": {
                    "pattern": "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
                    "message": "Order ID must be a valid UUID",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "rate_limiting": {"requests_per_minute": 300, "cost": 1, "burst_allowance": 10},
            "pagination": None,
            "error_handling": {
                "retry_codes": [429, 500, 502, 503, 504],
                "fatal_codes": [401, 403, 404],
                "custom_messages": {"404": "Order not found. Verify the order ID."}
            },
            "field_mapping": {"output_transforms": {"created_time": "format_timestamp"}},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "order": {
                        "order_id": "test-order-123",
                        "product_id": "BTC-USD",
                        "side": "BUY",
                        "status": "FILLED",
                        "created_time": "2023-01-01T00:00:00Z"
                    }
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 15, "cache_key_fields": ["order_id"]},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_gethistoricalorder"
            },
            
            "auth": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "required_params": ["api_key", "api_secret"],
                "auth_type": "hmac_signature"
            },
            "examples": [
                {
                    "name": "Get order details",
                    "description": "Get full details of a specific order",
                    "input": {"order_id": "12345678-1234-1234-1234-123456789abc"}
                }
            ]
        },
        
        "cancel_orders": {
            "method": "POST",
            "endpoint": "/api/v3/brokerage/orders/batch_cancel",
            "required_params": ["order_ids"],
            "optional_params": [],
            "body_parameters": ["order_ids"],
            "display_name": "Cancel Orders",
            "description": "Cancel one or more orders by their IDs",
            "group": "Trading",
            "tags": ["cancel", "orders", "trading"],
            "rate_limit_cost": 2,
            "cache_ttl": 0,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "failure_reason": {"type": "string"},
                                    "order_id": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            
            "array_templates": {
                "order_ids": [
                    {"template": "12345678-1234-1234-1234-123456789abc", "description": "Order ID to cancel"}
                ]
            },
            
            "validation_rules": {
                "order_ids": {
                    "pattern": "",
                    "message": "Must provide at least one order ID",
                    "pattern_type": "custom",
                    "min_items": 1,
                    "max_items": 100,
                    "required": True
                }
            },
            
            "rate_limiting": {"requests_per_minute": 100, "cost": 2, "burst_allowance": 3},
            "pagination": None,
            "error_handling": {"retry_codes": [429, 500, 502, 503, 504], "fatal_codes": [400, 401, 403]},
            "field_mapping": {},
            "webhook_support": {"supported": True, "events": ["order.cancelled"]},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "results": [
                        {"success": True, "order_id": "test-order-123"}
                    ]
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": False},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_cancelorders"
            },
            
            "auth": {
                "required_env_keys": ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
                "required_params": ["api_key", "api_secret"],
                "auth_type": "hmac_signature"
            },
            "examples": [
                {
                    "name": "Cancel single order",
                    "description": "Cancel one order by ID",
                    "input": {"order_ids": ["12345678-1234-1234-1234-123456789abc"]}
                },
                {
                    "name": "Cancel multiple orders",
                    "description": "Cancel multiple orders at once",
                    "input": {"order_ids": ["order-id-1", "order-id-2", "order-id-3"]}
                }
            ]
        },
        
        "list_products": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/market/products",
            "required_params": [],
            "optional_params": ["limit", "cursor", "product_type"],
            "display_name": "List Products",
            "description": "List available trading pairs and their information",
            "group": "Market Data",
            "tags": ["products", "pairs", "market"],
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "string"},
                                    "price": {"type": "string"},
                                    "price_percentage_change_24h": {"type": "string"},
                                    "volume_24h": {"type": "string"},
                                    "volume_percentage_change_24h": {"type": "string"},
                                    "base_increment": {"type": "string"},
                                    "quote_increment": {"type": "string"},
                                    "quote_min_size": {"type": "string"},
                                    "quote_max_size": {"type": "string"},
                                    "base_min_size": {"type": "string"},
                                    "base_max_size": {"type": "string"},
                                    "base_name": {"type": "string"},
                                    "quote_name": {"type": "string"},
                                    "watched": {"type": "boolean"},
                                    "is_disabled": {"type": "boolean"},
                                    "new": {"type": "boolean"},
                                    "status": {"type": "string"},
                                    "cancel_only": {"type": "boolean"},
                                    "limit_only": {"type": "boolean"},
                                    "post_only": {"type": "boolean"},
                                    "trading_disabled": {"type": "boolean"},
                                    "auction_mode": {"type": "boolean"},
                                    "product_type": {"type": "string"},
                                    "quote_currency_id": {"type": "string"},
                                    "base_currency_id": {"type": "string"},
                                    "fcm_trading_session_details": {"type": "object"},
                                    "mid_market_price": {"type": "string"}
                                }
                            }
                        },
                        "num_products": {"type": "integer"}
                    }
                }
            },
            
            "validation_rules": {
                "limit": {"min_value": 1, "max_value": 1000, "required": False}
            },
            
            "rate_limiting": {"requests_per_minute": 600, "cost": 1, "burst_allowance": 20},
            "pagination": {
                "type": "offset",
                "offset_param": "offset",
                "limit_param": "limit",
                "default_limit": 100,
                "max_limit": 1000
            },
            "error_handling": {"retry_codes": [429, 500, 502, 503, 504]},
            "field_mapping": {},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "products": [
                        {
                            "product_id": "BTC-USD",
                            "price": "45000.00",
                            "base_name": "Bitcoin",
                            "quote_name": "US Dollar",
                            "status": "online"
                        }
                    ],
                    "num_products": 1
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 300, "cache_key_fields": ["product_type", "limit"]},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getmarketproducts"
            },
            
            "auth": {
                "required_env_keys": [],
                "optional_env_keys": [],
                "required_params": [],
                "auth_type": "none",
                "auth_description": "Public endpoint - no authentication required"
            },
            "examples": [
                {
                    "name": "List all products",
                    "description": "Get all available trading pairs",
                    "input": {"limit": 100}
                },
                {
                    "name": "List spot products only",
                    "description": "Get only spot trading pairs",
                    "input": {"product_type": "SPOT", "limit": 50}
                }
            ]
        },
        
        "get_product": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/market/products/{product_id}",
            "required_params": ["product_id"],
            "optional_params": [],
            "display_name": "Get Product",
            "description": "Get detailed information about a specific trading pair",
            "group": "Market Data",
            "tags": ["product", "pair", "details"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"},
                        "price": {"type": "string"},
                        "price_percentage_change_24h": {"type": "string"},
                        "volume_24h": {"type": "string"},
                        "base_increment": {"type": "string"},
                        "quote_increment": {"type": "string"},
                        "base_name": {"type": "string"},
                        "quote_name": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            
            "validation_rules": {
                "product_id": {
                    "pattern": "^[A-Z0-9]+-[A-Z0-9]+$",
                    "message": "Product ID must be in format XXX-XXX",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "rate_limiting": {"requests_per_minute": 600, "cost": 1, "burst_allowance": 20},
            "pagination": None,
            "error_handling": {
                "retry_codes": [429, 500, 502, 503, 504],
                "fatal_codes": [404],
                "custom_messages": {"404": "Product not found. Check the product ID."}
            },
            "field_mapping": {},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "product_id": "BTC-USD",
                    "price": "45000.00",
                    "base_name": "Bitcoin",
                    "quote_name": "US Dollar",
                    "status": "online"
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 60, "cache_key_fields": ["product_id"]},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getmarketproduct"
            },
            
            "auth": {
                "required_env_keys": [],
                "required_params": [],
                "auth_type": "none"
            },
            "examples": [
                {
                    "name": "Get BTC-USD info",
                    "description": "Get Bitcoin to USD trading pair details",
                    "input": {"product_id": "BTC-USD"}
                }
            ]
        },
        
        "get_product_candles": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/market/products/{product_id}/candles",
            "required_params": ["product_id", "start", "end", "granularity"],
            "optional_params": [],
            "display_name": "Get Product Candles",
            "description": "Get historical price candles for a product",
            "group": "Market Data",
            "tags": ["candles", "ohlc", "historical", "chart"],
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "candles": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "start": {"type": "string"},
                                    "low": {"type": "string"},
                                    "high": {"type": "string"},
                                    "open": {"type": "string"},
                                    "close": {"type": "string"},
                                    "volume": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            
            "validation_rules": {
                "product_id": {
                    "pattern": "^[A-Z0-9]+-[A-Z0-9]+$",
                    "message": "Product ID must be in format XXX-XXX",
                    "pattern_type": "regex",
                    "required": True
                },
                "start": {
                    "pattern": "^[0-9]{10}$",
                    "message": "Start time must be Unix timestamp (10 digits)",
                    "pattern_type": "regex",
                    "required": True
                },
                "end": {
                    "pattern": "^[0-9]{10}$",
                    "message": "End time must be Unix timestamp (10 digits)",
                    "pattern_type": "regex",
                    "required": True
                },
                "granularity": {
                    "pattern": "^(ONE_MINUTE|FIVE_MINUTE|FIFTEEN_MINUTE|THIRTY_MINUTE|ONE_HOUR|TWO_HOUR|SIX_HOUR|ONE_DAY)$",
                    "message": "Invalid granularity value",
                    "pattern_type": "regex",
                    "required": True
                }
            },
            
            "rate_limiting": {"requests_per_minute": 300, "cost": 1, "burst_allowance": 10},
            "pagination": None,
            "error_handling": {"retry_codes": [429, 500, 502, 503, 504], "fatal_codes": [400, 404]},
            "field_mapping": {"output_transforms": {"start": "format_timestamp"}},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "candles": [
                        {
                            "start": "1640995200",
                            "low": "44000.00",
                            "high": "46000.00",
                            "open": "45000.00",
                            "close": "45500.00",
                            "volume": "1234.56"
                        }
                    ]
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 60, "cache_key_fields": ["product_id", "start", "end", "granularity"]},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getmarketproductcandles"
            },
            
            "auth": {"required_env_keys": [], "auth_type": "none"},
            "examples": [
                {
                    "name": "Get hourly BTC candles",
                    "description": "Get 24 hours of BTC-USD hourly candles",
                    "input": {
                        "product_id": "BTC-USD",
                        "start": "1640995200",
                        "end": "1641081600",
                        "granularity": "ONE_HOUR"
                    }
                }
            ]
        },
        
        "get_server_time": {
            "method": "GET",
            "endpoint": "/api/v3/brokerage/time",
            "required_params": [],
            "optional_params": [],
            "display_name": "Get Server Time",
            "description": "Get the current server time",
            "group": "Utilities",
            "tags": ["time", "server", "timestamp"],
            "rate_limit_cost": 1,
            "cache_ttl": 1,
            "response_type": "object",
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "iso": {"type": "string", "format": "date-time"},
                        "epochSeconds": {"type": "string"},
                        "epochMillis": {"type": "string"}
                    }
                }
            },
            
            "rate_limiting": {"requests_per_minute": 600, "cost": 1, "burst_allowance": 20},
            "pagination": None,
            "error_handling": {"retry_codes": [429, 500, 502, 503, 504]},
            "field_mapping": {},
            "webhook_support": {"supported": False},
            "testing_mode": {
                "supported": True,
                "mock_response": {
                    "iso": "2023-01-01T00:00:00Z",
                    "epochSeconds": "1672531200",
                    "epochMillis": "1672531200000"
                }
            },
            "performance_monitoring": {"track_latency": True, "track_errors": True},
            "caching_strategy": {"enabled": True, "ttl_seconds": 1},
            "documentation_links": {
                "official_docs": "https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getservertime"
            },
            
            "auth": {"auth_type": "none"},
            "examples": [
                {
                    "name": "Get current time",
                    "description": "Get Coinbase server time",
                    "input": {}
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced Coinbase node with embedded configuration."""
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Initialize the Enhanced UniversalRequestNode with embedded config
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        logger.info("Enhanced CoinbaseNode initialized with all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"CoinbaseNode executing operation: {node_data.get('params', {}).get('operation')}")
        return await self.universal_request_node.execute(node_data)

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.validate_custom(node_data)

    def get_operation_config(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific operation."""
        return self.OPERATIONS.get(operation)

    def get_base_config(self) -> Dict[str, Any]:
        """Get the base configuration for this node."""
        return self.CONFIG
    
    def get_array_template(self, operation: str, parameter: str) -> Optional[Dict[str, Any]]:
        """Get array template for a parameter in an operation."""
        op_config = self.OPERATIONS.get(operation)
        if not op_config or "array_templates" not in op_config:
            return None
        return op_config["array_templates"].get(parameter)
    
    def get_validation_rules(self, operation: str) -> Dict[str, Any]:
        """Get validation rules for an operation."""
        op_config = self.OPERATIONS.get(operation)
        if not op_config or "validation_rules" not in op_config:
            return {}
        return op_config["validation_rules"]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.universal_request_node.get_metrics()

    @staticmethod
    def format_response(response_data: Any) -> Dict[str, Any]:
        """Format response data consistently."""
        if isinstance(response_data, dict):
            return response_data
        elif isinstance(response_data, list):
            return {"items": response_data, "count": len(response_data)}
        else:
            return {"result": response_data}

# Export the enhanced node class
__all__ = ["CoinbaseNode"]