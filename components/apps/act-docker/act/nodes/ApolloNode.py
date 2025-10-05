#!/usr/bin/env python3
"""
Apollo.io Node - Enhanced with ALL 13 advanced features following OpenAI template
Configuration is embedded directly in the node - no separate config.json needed
"""

import logging
from typing import Dict, Any, Optional

try:
    from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        from  base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the Enhanced UniversalRequestNode
try:
    from universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from .universal_request_node import UniversalRequestNode
    except ImportError:
        from .universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class ApolloNode(BaseNode):
    """
    Enhanced Apollo.io node with ALL 13 advanced features - following perfect OpenAI template.
    All operations are handled by Enhanced UniversalRequestNode based on this config.
    """
    
    # Enhanced configuration with ALL 13 features
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "apollo",
            "display_name": "Apollo.io",
            "description": "Comprehensive Apollo.io API integration for B2B sales intelligence, prospecting, lead generation, and contact enrichment",
            "category": "sales",
            "vendor": "apollo.io",
            "version": "2.0.0",
            "author": "ACT Workflow",
            "tags": ["sales", "b2b", "prospecting", "leads", "contacts", "intelligence", "crm", "outreach"],
            "documentation_url": "https://apolloapi.com/docs/",
            "icon": "https://www.apollo.io/favicon.ico",
            "color": "#4A90E2",
            "created_at": "2025-08-25T00:00:00Z",
            "updated_at": "2025-08-25T00:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.apollo.io/v1",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ACT-Workflow/2.0"
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
                "requests_per_minute": 200,
                "requests_per_second": 5.0,
                "burst_size": 10,
                "cost_per_request": 0.005,
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
            "cost_per_1k_requests": 5.00,
            "cost_per_request": 0.005,
            "billing_unit": "requests",
            "free_tier_limit": 500
        },
        
        # Performance monitoring
        "monitoring": {
            "track_response_time": True,
            "log_errors": True,
            "metrics": ["success_rate", "avg_response_time", "error_count", "search_count"],
            "alerts": {
                "error_rate_threshold": 0.05,
                "response_time_threshold": 10000
            }
        },
        
        # Intelligent caching
        "caching": {
            "enabled": True,
            "cache_key_template": "{operation}:{hash}",
            "ttl_seconds": 900,
            "cache_conditions": {
                "only_for": ["GET"],
                "exclude_params": ["timestamp", "page", "per_page"]
            }
        },
        
        # Testing configuration
        "testing": {
            "sandbox_mode": False,
            "test_credentials_param": "test_api_key",
            "validation_endpoint": "/mixed_people/search"
        },
        
        # Documentation links
        "documentation": {
            "api_docs_url": "https://apolloapi.com/docs/",
            "setup_guide": "https://knowledge.apollo.io/hc/en-us/articles/360052155854-Apollo-API",
            "troubleshooting": "https://knowledge.apollo.io/hc/en-us/sections/360012689853-API",
            "changelog": "https://apolloapi.com/docs/changelog"
        },
        
        # All parameters with enhanced metadata
        "parameters": {
            "api_key": {
                "type": "string",
                "description": "Apollo.io API key for authentication",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^[a-zA-Z0-9]{32,}$",
                    "message": "API key must be at least 32 alphanumeric characters",
                    "minLength": 32,
                    "maxLength": 128
                }
            },
            "operation": {
                "type": "string",
                "description": "The Apollo.io operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["search_people", "enrich_person", "search_organizations", "enrich_organization", "get_sequences"]
            },
            "query": {
                "type": "string",
                "description": "Search query keywords",
                "required": False,
                "group": "Search",
                "examples": ["software engineer", "marketing director", "CEO"],
                "validation": {
                    "maxLength": 500
                }
            },
            "person_titles": {
                "type": "array",
                "description": "Array of job titles to search for",
                "required": False,
                "group": "People Filters",
                "examples": [["CEO", "Founder"], ["Sales Director", "VP Sales"]],
                "validation": {
                    "items": {"type": "string", "maxLength": 100},
                    "maxItems": 20
                }
            },
            "q_keywords": {
                "type": "string",
                "description": "Keywords for general search",
                "required": False,
                "group": "Search",
                "examples": ["machine learning", "artificial intelligence", "data science"],
                "validation": {
                    "maxLength": 200
                }
            },
            "person_locations": {
                "type": "array",
                "description": "Geographic locations for people search",
                "required": False,
                "group": "People Filters",
                "examples": [["San Francisco", "New York"], ["United States", "Canada"]],
                "validation": {
                    "items": {"type": "string", "maxLength": 100},
                    "maxItems": 10
                }
            },
            "person_seniorities": {
                "type": "array",
                "description": "Seniority levels to filter by",
                "required": False,
                "group": "People Filters",
                "examples": [["senior", "director"], ["c_level", "vp"]],
                "validation": {
                    "items": {
                        "type": "string",
                        "enum": ["junior", "senior", "manager", "director", "vp", "c_level", "owner", "partner"]
                    },
                    "maxItems": 8
                }
            },
            "organization_names": {
                "type": "array",
                "description": "Specific company names to search within",
                "required": False,
                "group": "Organization Filters",
                "examples": [["Google", "Microsoft"], ["Salesforce", "HubSpot"]],
                "validation": {
                    "items": {"type": "string", "maxLength": 100},
                    "maxItems": 50
                }
            },
            "organization_num_employees_ranges": {
                "type": "array",
                "description": "Company size ranges",
                "required": False,
                "group": "Organization Filters",
                "examples": [["1,10"], ["11,50", "51,200"]],
                "validation": {
                    "items": {
                        "type": "string",
                        "pattern": "^[0-9,]+$"
                    },
                    "maxItems": 10
                }
            },
            "organization_industries": {
                "type": "array",
                "description": "Industry categories to filter companies",
                "required": False,
                "group": "Organization Filters",
                "examples": [["Software"], ["Marketing & Advertising", "Financial Services"]],
                "validation": {
                    "items": {"type": "string", "maxLength": 100},
                    "maxItems": 20
                }
            },
            "technologies": {
                "type": "array",
                "description": "Technologies used by target companies",
                "required": False,
                "group": "Technology Filters",
                "examples": [["Salesforce", "HubSpot"], ["AWS", "Azure", "Google Cloud"]],
                "validation": {
                    "items": {"type": "string", "maxLength": 50},
                    "maxItems": 30
                }
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination",
                "required": False,
                "default": 1,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 1000
                },
                "examples": [1, 2, 5, 10]
            },
            "per_page": {
                "type": "integer",
                "description": "Number of results per page",
                "required": False,
                "default": 25,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "examples": [10, 25, 50, 100]
            },
            "first_name": {
                "type": "string",
                "description": "Person's first name for enrichment",
                "required": False,
                "group": "Enrichment",
                "examples": ["John", "Jane", "Michael"],
                "validation": {
                    "maxLength": 50
                }
            },
            "last_name": {
                "type": "string",
                "description": "Person's last name for enrichment",
                "required": False,
                "group": "Enrichment",
                "examples": ["Smith", "Johnson", "Williams"],
                "validation": {
                    "maxLength": 50
                }
            },
            "email": {
                "type": "string",
                "description": "Email address for person enrichment",
                "required": False,
                "group": "Enrichment",
                "examples": ["john.smith@example.com", "jane@company.com"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid email address"
                }
            },
            "domain": {
                "type": "string",
                "description": "Company domain for organization enrichment",
                "required": False,
                "group": "Enrichment",
                "examples": ["example.com", "company.io", "startup.co"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid domain name"
                }
            },
            "organization_name": {
                "type": "string",
                "description": "Organization name for enrichment",
                "required": False,
                "group": "Enrichment",
                "examples": ["Google Inc", "Microsoft Corporation", "Apple Inc"],
                "validation": {
                    "maxLength": 100
                }
            },
            "reveal_personal_emails": {
                "type": "boolean",
                "description": "Whether to reveal personal email addresses",
                "required": False,
                "default": False,
                "group": "Privacy"
            },
            "webhook_url": {
                "type": "string",
                "description": "Webhook URL for async operations",
                "required": False,
                "group": "Webhooks",
                "examples": ["https://example.com/webhook", "https://api.myapp.com/apollo/callback"],
                "validation": {
                    "pattern": "^https?://[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(/.*)?$",
                    "message": "Webhook URL must be a valid HTTP/HTTPS URL"
                }
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful Apollo.io API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from Apollo.io API"},
                    "people": {"type": "array", "description": "Array of people results"},
                    "organizations": {"type": "array", "description": "Array of organization results"},
                    "result": {"type": "object", "description": "Full API response data"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Apollo.io error code"},
                    "timestamp": {"type": "string", "format": "date-time"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "search_people": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": []
            },
            "enrich_person": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": []
            },
            "search_organizations": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": []
            },
            "enrich_organization": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": []
            },
            "get_sequences": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to Apollo.io
        "error_codes": {
            "400": "Bad Request - Invalid parameters or malformed request",
            "401": "Unauthorized - Invalid or missing API key",
            "403": "Forbidden - Insufficient permissions or rate limit exceeded",
            "404": "Not Found - Resource not found",
            "422": "Unprocessable Entity - Invalid data or validation errors",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - Apollo.io server error",
            "502": "Bad Gateway - Apollo.io server temporarily unavailable",
            "503": "Service Unavailable - Apollo.io server overloaded"
        }
    }
    
    # Enhanced operation definitions with ALL 13 features
    OPERATIONS = {
        "search_people": {
            "method": "POST",
            "endpoint": "/mixed_people/search",
            "required_params": [],
            "optional_params": ["query", "person_titles", "q_keywords", "person_locations", "person_seniorities", "organization_names", "organization_num_employees_ranges", "organization_industries", "technologies", "page", "per_page"],
            "body_parameters": ["query", "person_titles", "q_keywords", "person_locations", "person_seniorities", "organization_names", "organization_num_employees_ranges", "organization_industries", "technologies", "page", "per_page"],
            "display_name": "Search People",
            "description": "Search for people using advanced filters and criteria",
            "group": "People Search",
            "tags": ["people", "search", "prospects", "contacts"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            # 1. Operation-specific output schema
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "people": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "description": "Person ID"},
                                    "first_name": {"type": "string", "description": "First name"},
                                    "last_name": {"type": "string", "description": "Last name"},
                                    "name": {"type": "string", "description": "Full name"},
                                    "title": {"type": "string", "description": "Job title"},
                                    "email": {"type": "string", "description": "Email address"},
                                    "linkedin_url": {"type": "string", "description": "LinkedIn profile URL"},
                                    "organization": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "name": {"type": "string"},
                                            "website_url": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "pagination": {
                            "type": "object",
                            "properties": {
                                "page": {"type": "integer"},
                                "per_page": {"type": "integer"},
                                "total_entries": {"type": "integer"},
                                "total_pages": {"type": "integer"}
                            }
                        }
                    }
                },
                "error": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "type": {"type": "string"}
                            }
                        }
                    }
                },
                "status_codes": {
                    200: "Success",
                    400: "Bad Request - Invalid parameters",
                    401: "Invalid authentication",
                    403: "Rate limit exceeded",
                    429: "Too many requests",
                    500: "Server error"
                }
            },
            
            # 2. Array templates for complex inputs - COMPREHENSIVE COVERAGE
            "array_templates": {
                "person_titles": {
                    "template": ["CEO", "CTO", "CMO", "CFO", "VP Sales", "VP Marketing", "VP Engineering", "Sales Director", "Marketing Director", "Product Manager", "Software Engineer", "Data Scientist", "Business Development", "Account Executive", "Customer Success Manager"],
                    "description": "Common job titles for prospect search",
                    "min_items": 1,
                    "max_items": 20
                },
                "person_locations": {
                    "template": ["San Francisco, CA", "New York, NY", "Los Angeles, CA", "Chicago, IL", "Boston, MA", "Seattle, WA", "Austin, TX", "Denver, CO", "United States", "Canada", "United Kingdom", "Germany", "France", "Australia", "Remote"],
                    "description": "Geographic locations for people search",
                    "min_items": 1,
                    "max_items": 10
                },
                "person_seniorities": {
                    "template": ["c_level", "vp", "director", "manager", "senior", "junior", "owner", "partner"],
                    "description": "Seniority levels to filter by",
                    "min_items": 1,
                    "max_items": 8
                },
                "organization_names": {
                    "template": ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Tesla", "Salesforce", "Netflix", "Stripe", "Airbnb", "Uber", "Shopify", "Zoom", "Slack", "HubSpot"],
                    "description": "Specific company names to search within",
                    "min_items": 1,
                    "max_items": 50
                },
                "organization_num_employees_ranges": {
                    "template": ["1,10", "11,50", "51,200", "201,500", "501,1000", "1001,5000", "5001,10000", "10001+"],
                    "description": "Company size ranges",
                    "min_items": 1,
                    "max_items": 10
                },
                "organization_industries": {
                    "template": ["Software", "Information Technology", "Financial Services", "Healthcare", "Marketing & Advertising", "E-commerce", "Manufacturing", "Education", "Real Estate", "Professional Services", "Media & Entertainment", "Non-profit", "Government", "Transportation", "Energy"],
                    "description": "Industry categories to filter companies",
                    "min_items": 1,
                    "max_items": 20
                },
                "technologies": {
                    "template": ["Salesforce", "HubSpot", "AWS", "Microsoft Azure", "Google Cloud", "Slack", "Zoom", "Shopify", "WordPress", "React", "Node.js", "Python", "Docker", "Kubernetes", "TensorFlow", "Stripe", "Twilio", "MongoDB", "PostgreSQL", "Redis"],
                    "description": "Technologies used by target companies",
                    "min_items": 1,
                    "max_items": 30
                }
            },
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [
                {
                    "when_field": "page",
                    "when_value": "gt_1",
                    "then_require": [],
                    "then_optional": ["per_page"],
                    "require_one_of": [],
                    "mutually_exclusive": []
                }
            ],
            
            # 4. Advanced validation rules
            "validation_rules": {
                "page": {
                    "pattern": "",
                    "message": "Page must be between 1 and 1000",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 1000,
                    "required": False
                },
                "per_page": {
                    "pattern": "",
                    "message": "Per page must be between 1 and 100",
                    "pattern_type": "custom",
                    "min_value": 1,
                    "max_value": 100,
                    "required": False
                },
                "query": {
                    "pattern": "",
                    "message": "Query must not exceed 500 characters",
                    "pattern_type": "custom",
                    "max_length": 500,
                    "required": False
                }
            },
            
            # 6. Pagination handling
            "pagination": {
                "type": "cursor",
                "cursor_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 100,
                "has_more_field": "total_pages",
                "next_cursor_field": "page",
                "response_path": "people"
            },
            
            # 8. Field mapping & transformation
            "field_mapping": {
                "input_transforms": {
                    "person_titles": "validate_titles_array"
                },
                "output_transforms": {
                    "people": "format_people_results"
                },
                "field_aliases": {
                    "q_keywords": "query"
                }
            },
            
            "auth": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Apollo.io API key for authentication"
            },
            "examples": [
                {
                    "name": "Search for CEOs",
                    "description": "Find CEO contacts at technology companies",
                    "input": {
                        "person_titles": ["CEO", "Chief Executive Officer"],
                        "organization_industries": ["Software"],
                        "organization_num_employees_ranges": ["101,500"],
                        "page": 1,
                        "per_page": 25
                    }
                },
                {
                    "name": "Search by keywords",
                    "description": "Search for people using keyword matching",
                    "input": {
                        "q_keywords": "machine learning engineer",
                        "person_locations": ["San Francisco", "New York"],
                        "technologies": ["Python", "TensorFlow", "AWS"],
                        "per_page": 50
                    }
                },
                {
                    "name": "Company-specific search",
                    "description": "Find contacts at specific companies",
                    "input": {
                        "organization_names": ["Google", "Microsoft", "Amazon"],
                        "person_titles": ["Software Engineer", "Product Manager"],
                        "person_seniorities": ["senior", "manager"]
                    }
                }
            ]
        },
        "enrich_person": {
            "method": "POST",
            "endpoint": "/people/match",
            "required_params": [],
            "optional_params": ["first_name", "last_name", "email", "domain", "organization_name", "reveal_personal_emails"],
            "body_parameters": ["first_name", "last_name", "email", "domain", "organization_name", "reveal_personal_emails"],
            "display_name": "Enrich Person",
            "description": "Enrich person data with additional contact information and insights",
            "group": "Data Enrichment",
            "tags": ["enrichment", "person", "data", "contact"],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "object",
            
            # 2. Array templates for enrichment operations
            "array_templates": {
                "personal_emails": {
                    "template": ["john.doe@gmail.com", "jane.smith@yahoo.com", "user@outlook.com"],
                    "description": "Personal email addresses",
                    "min_items": 1,
                    "max_items": 5
                },
                "phone_numbers": {
                    "template": ["+1-555-123-4567", "+44-20-1234-5678", "+1-555-987-6543"],
                    "description": "Phone numbers in various formats",
                    "min_items": 1,
                    "max_items": 3
                }
            },
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "person": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "name": {"type": "string"},
                                "title": {"type": "string"},
                                "email": {"type": "string"},
                                "personal_emails": {"type": "array", "items": {"type": "string"}},
                                "phone_numbers": {"type": "array", "items": {"type": "string"}},
                                "linkedin_url": {"type": "string"},
                                "twitter_url": {"type": "string"},
                                "github_url": {"type": "string"},
                                "facebook_url": {"type": "string"},
                                "organization": {"type": "object"},
                                "employment_history": {"type": "array"}
                            }
                        },
                        "match_score": {"type": "number", "description": "Confidence score of the match"}
                    }
                }
            },
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [
                {
                    "when_field": "email",
                    "when_value": "exists",
                    "then_require": [],
                    "then_optional": ["first_name", "last_name"],
                    "require_one_of": ["email", "first_name"],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "email": {
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid email address",
                    "pattern_type": "email",
                    "required": False
                },
                "domain": {
                    "pattern": "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid domain name",
                    "pattern_type": "custom",
                    "required": False
                }
            },
            
            "auth": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Apollo.io API key for person enrichment"
            },
            "examples": [
                {
                    "name": "Enrich by email",
                    "description": "Enrich a person using their email address",
                    "input": {
                        "email": "john.doe@example.com",
                        "reveal_personal_emails": True
                    }
                },
                {
                    "name": "Enrich by name and company",
                    "description": "Enrich using name and company information",
                    "input": {
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "organization_name": "Google",
                        "domain": "google.com"
                    }
                }
            ]
        },
        "search_organizations": {
            "method": "POST",
            "endpoint": "/organizations/search",
            "required_params": [],
            "optional_params": ["query", "organization_names", "organization_industries", "organization_num_employees_ranges", "technologies", "page", "per_page"],
            "body_parameters": ["query", "organization_names", "organization_industries", "organization_num_employees_ranges", "technologies", "page", "per_page"],
            "display_name": "Search Organizations",
            "description": "Search for companies and organizations using various filters",
            "group": "Organization Search",
            "tags": ["organizations", "companies", "search", "b2b"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "object",
            
            # 2. Array templates for organization search
            "array_templates": {
                "organization_names": {
                    "template": ["Google", "Microsoft", "Amazon", "Salesforce", "Stripe"],
                    "description": "Company names for organization search",
                    "min_items": 1,
                    "max_items": 50
                },
                "organization_industries": {
                    "template": ["Software", "Financial Services", "Healthcare", "Marketing & Advertising"],
                    "description": "Industry categories",
                    "min_items": 1,
                    "max_items": 20
                },
                "organization_num_employees_ranges": {
                    "template": ["1,10", "11,50", "51,200", "201,500"],
                    "description": "Employee count ranges",
                    "min_items": 1,
                    "max_items": 10
                },
                "technologies": {
                    "template": ["Salesforce", "AWS", "React", "Python"],
                    "description": "Technology stack identifiers",
                    "min_items": 1,
                    "max_items": 30
                }
            },
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "organizations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "website_url": {"type": "string"},
                                    "blog_url": {"type": "string"},
                                    "angellist_url": {"type": "string"},
                                    "linkedin_url": {"type": "string"},
                                    "twitter_url": {"type": "string"},
                                    "facebook_url": {"type": "string"},
                                    "primary_phone": {"type": "object"},
                                    "languages": {"type": "array"},
                                    "alexa_ranking": {"type": "integer"},
                                    "phone": {"type": "string"},
                                    "linkedin_uid": {"type": "string"},
                                    "founded_year": {"type": "integer"},
                                    "publicly_traded_symbol": {"type": "string"},
                                    "publicly_traded_exchange": {"type": "string"},
                                    "logo_url": {"type": "string"},
                                    "crunchbase_url": {"type": "string"},
                                    "primary_domain": {"type": "string"}
                                }
                            }
                        },
                        "pagination": {"type": "object"}
                    }
                }
            },
            
            # 6. Pagination handling
            "pagination": {
                "type": "cursor",
                "cursor_param": "page",
                "size_param": "per_page",
                "default_size": 25,
                "max_size": 100,
                "has_more_field": "total_pages",
                "next_cursor_field": "page",
                "response_path": "organizations"
            },
            
            "auth": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Apollo.io API key for organization search"
            },
            "examples": [
                {
                    "name": "Search tech companies",
                    "description": "Find technology companies in a specific size range",
                    "input": {
                        "organization_industries": ["Software"],
                        "organization_num_employees_ranges": ["51,200", "201,500"],
                        "technologies": ["React", "Node.js", "AWS"],
                        "per_page": 50
                    }
                },
                {
                    "name": "Search by company name",
                    "description": "Search for specific companies",
                    "input": {
                        "organization_names": ["Stripe", "Shopify", "Square"],
                        "page": 1,
                        "per_page": 25
                    }
                }
            ]
        },
        "enrich_organization": {
            "method": "POST",
            "endpoint": "/organizations/enrich",
            "required_params": [],
            "optional_params": ["domain", "organization_name"],
            "body_parameters": ["domain", "organization_name"],
            "display_name": "Enrich Organization",
            "description": "Enrich organization data with comprehensive company information",
            "group": "Data Enrichment",
            "tags": ["enrichment", "organization", "company", "data"],
            "rate_limit_cost": 1,
            "cache_ttl": 3600,
            "response_type": "object",
            
            # 2. Array templates for organization enrichment
            "array_templates": {
                "technologies": {
                    "template": ["Salesforce", "AWS", "Google Analytics", "Slack"],
                    "description": "Technologies used by the organization",
                    "min_items": 1,
                    "max_items": 50
                },
                "languages": {
                    "template": ["English", "Spanish", "French", "German"],
                    "description": "Languages supported by the organization",
                    "min_items": 1,
                    "max_items": 10
                }
            },
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "organization": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "website_url": {"type": "string"},
                                "industry": {"type": "string"},
                                "num_employees": {"type": "integer"},
                                "revenue": {"type": "object"},
                                "technologies": {"type": "array"},
                                "founded_year": {"type": "integer"},
                                "headquarters": {"type": "object"},
                                "linkedin_url": {"type": "string"},
                                "crunchbase_url": {"type": "string"}
                            }
                        },
                        "match_score": {"type": "number"}
                    }
                }
            },
            
            # 3. Parameter dependencies & conditional fields
            "parameter_dependencies": [
                {
                    "when_field": "domain",
                    "when_value": "exists",
                    "then_require": [],
                    "then_optional": ["organization_name"],
                    "require_one_of": ["domain", "organization_name"],
                    "mutually_exclusive": []
                }
            ],
            
            "validation_rules": {
                "domain": {
                    "pattern": "^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "message": "Must be a valid domain name",
                    "pattern_type": "custom",
                    "required": False
                }
            },
            
            "auth": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Apollo.io API key for organization enrichment"
            },
            "examples": [
                {
                    "name": "Enrich by domain",
                    "description": "Enrich organization using company domain",
                    "input": {
                        "domain": "stripe.com"
                    }
                },
                {
                    "name": "Enrich by company name",
                    "description": "Enrich organization using company name",
                    "input": {
                        "organization_name": "Stripe Inc"
                    }
                }
            ]
        },
        "get_sequences": {
            "method": "GET",
            "endpoint": "/email_sequences",
            "required_params": [],
            "optional_params": ["page", "per_page"],
            "display_name": "Get Sequences",
            "description": "Retrieve email sequences and outreach campaigns",
            "group": "Sequences",
            "tags": ["sequences", "email", "campaigns", "outreach"],
            "rate_limit_cost": 1,
            "cache_ttl": 600,
            "response_type": "array",
            
            # 2. Array templates for sequence management
            "array_templates": {
                "sequence_names": {
                    "template": ["Cold Outreach Sequence", "Follow-up Sequence", "Re-engagement Sequence"],
                    "description": "Email sequence names",
                    "min_items": 1,
                    "max_items": 20
                }
            },
            
            "output_schema": {
                "success": {
                    "type": "object",
                    "properties": {
                        "email_sequences": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "created_at": {"type": "string", "format": "date-time"},
                                    "updated_at": {"type": "string", "format": "date-time"},
                                    "active": {"type": "boolean"},
                                    "steps_count": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            
            "auth": {
                "required_env_keys": ["APOLLO_API_KEY"],
                "optional_env_keys": [],
                "required_params": ["api_key"],
                "auth_type": "bearer_token",
                "auth_description": "Requires Apollo.io API key to access sequences"
            },
            "examples": [
                {
                    "name": "Get all sequences",
                    "description": "Retrieve all email sequences",
                    "input": {
                        "page": 1,
                        "per_page": 50
                    }
                }
            ]
        }
    }

    def __init__(self, sandbox_timeout: Optional[int] = None):
        """Initialize the enhanced Apollo.io node with embedded configuration."""
        # Initialize the Enhanced UniversalRequestNode with embedded config FIRST
        self.universal_request_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
        
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        logger.debug("Enhanced ApolloNode initialized with all 13 advanced features")

    def get_schema(self) -> NodeSchema:
        """Get the schema for this node - delegated to Enhanced UniversalRequestNode."""
        return self.universal_request_node.get_schema()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request - delegated to Enhanced UniversalRequestNode."""
        logger.debug(f"ApolloNode executing operation: {node_data.get('params', {}).get('operation')}")
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
__all__ = ["ApolloNode"]