#!/usr/bin/env python3
"""
GitHub Node - Pure config-driven implementation using UniversalRequestNode
Configuration is embedded directly in the node - no separate config.json needed
"""

import logging
from typing import Dict, Any, Optional

# Import BaseNode with consistent path resolution
try:
    # First try relative import (when imported as part of package)
    from .base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
except ImportError:
    try:
        # Fallback to absolute import
        from act.nodes.base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType
    except ImportError:
        # Last resort - direct import
        from base_node import BaseNode, NodeSchema, NodeParameter, NodeParameterType

# Import the UniversalRequestNode
try:
    from .universal_request_node import UniversalRequestNode
except ImportError:
    try:
        from act.nodes.universal_request_node import UniversalRequestNode
    except ImportError:
        from universal_request_node import UniversalRequestNode

logger = logging.getLogger(__name__)

class GitHubNode(BaseNode):
    """
    Pure config-driven GitHub node with embedded configuration.
    All operations are handled by UniversalRequestNode based on this config.
    """
    
    # Explicit node type for discovery
    node_type = "github"
    
    # Embedded configuration for GitHub API
    CONFIG = {
        # Node metadata - ALL information needed for discovery
        "node_info": {
            "name": "github",
            "display_name": "GitHub",
            "description": "Comprehensive GitHub API integration for repositories, issues, pull requests, workflows, and team management",
            "category": "developer",
            "vendor": "github",
            "version": "1.0.0",
            "author": "ACT Workflow",
            "tags": ["github", "git", "repository", "issues", "pull-requests", "actions", "developer", "vcs"],
            "documentation_url": "https://docs.github.com/rest",
            "icon": "https://cdn.jsdelivr.net/npm/simple-icons@v9/github.svg",
            "color": "#181717",
            "created_at": "2025-08-22T16:00:00Z",
            "updated_at": "2025-08-22T16:00:00Z"
        },
        
        # API connection configuration
        "api_config": {
            "base_url": "https://api.github.com",
            "authentication": {
                "type": "bearer_token",
                "header": "Authorization"
            },
            "default_headers": {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ACT-Workflow-GitHubNode",
                "Content-Type": "application/json"
            },
            "retry_config": {
                "max_attempts": 3,
                "backoff": "exponential",
                "retriable_codes": [429, 500, 502, 503, 504]
            },
            "rate_limiting": {
                "requests_per_second": 50,
                "burst_size": 10
            },
            "timeouts": {
                "connect": 10.0,
                "read": 30.0,
                "total": 60.0
            }
        },
        
        # All parameters with complete metadata
        "parameters": {
            "access_token": {
                "type": "string",
                "description": "GitHub Personal Access Token or OAuth token",
                "required": True,
                "sensitive": True,
                "group": "Authentication",
                "validation": {
                    "pattern": "^(ghp_|gho_|ghu_|ghs_|ghr_)[a-zA-Z0-9]{36}$|^github_pat_[a-zA-Z0-9_]{82}$",
                    "minLength": 40
                },
                "examples": ["ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]
            },
            "operation": {
                "type": "string",
                "description": "The GitHub operation to perform",
                "required": True,
                "group": "Operation",
                "enum": ["get_repo", "create_repo", "list_repos", "list_branches", "get_file_content", 
                        "create_file", "update_file", "create_pull_request", "list_pull_requests",
                        "create_issue", "list_issues", "get_user", "get_authenticated_user",
                        "list_commits", "create_release", "list_releases"]
            },
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization name)",
                "required": False,
                "group": "Repository",
                "examples": ["octocat", "microsoft", "facebook"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "maxLength": 39
                }
            },
            "repo": {
                "type": "string",
                "description": "Repository name",
                "required": False,
                "group": "Repository",
                "examples": ["hello-world", "react", "vscode"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9._-]+$",
                    "maxLength": 100
                }
            },
            "name": {
                "type": "string",
                "description": "Name for repositories, teams, or other resources",
                "required": False,
                "group": "General",
                "examples": ["my-new-repo", "development-team"]
            },
            "description": {
                "type": "string",
                "description": "Description of the repository",
                "required": False,
                "group": "Repository",
                "examples": ["This is my awesome project", "A web application built with React"]
            },
            "private": {
                "type": "boolean",
                "description": "Whether the repository is private (true) or public (false)",
                "required": False,
                "group": "Repository",
                "default": False,
                "examples": [True, False]
            },
            "auto_init": {
                "type": "boolean",
                "description": "Whether to create an initial README file",
                "required": False,
                "group": "Repository",
                "default": False,
                "examples": [True, False]
            },
            "path": {
                "type": "string",
                "description": "File or directory path in repository",
                "required": False,
                "group": "Files",
                "examples": ["README.md", "src/index.js", "docs/api.md"]
            },
            "content": {
                "type": "string",
                "description": "File content (base64 encoded for binary files)",
                "required": False,
                "group": "Files"
            },
            "message": {
                "type": "string",
                "description": "Commit message",
                "required": False,
                "group": "Git",
                "examples": ["Initial commit", "Fix bug in user authentication", "Add new feature"]
            },
            "sha": {
                "type": "string",
                "description": "Git SHA hash",
                "required": False,
                "group": "Git",
                "validation": {
                    "pattern": "^[a-f0-9]{40}$"
                },
                "examples": ["6dcb09b5b57875f334f61aebed695e2e4193db5e"]
            },
            "branch": {
                "type": "string",
                "description": "Branch name",
                "required": False,
                "group": "Branch",
                "examples": ["main", "develop", "feature/new-feature"],
                "default": "main"
            },
            "title": {
                "type": "string",
                "description": "Title for issues, pull requests, or releases",
                "required": False,
                "group": "Content",
                "examples": ["Bug fix for login issue", "Add dark mode support"]
            },
            "body": {
                "type": "string",
                "description": "Description or body text",
                "required": False,
                "group": "Content",
                "examples": ["This PR adds dark mode support to the application"]
            },
            "head": {
                "type": "string",
                "description": "Head branch for pull request",
                "required": False,
                "group": "Pull Request",
                "examples": ["feature/new-feature", "username:branch-name"]
            },
            "base": {
                "type": "string",
                "description": "Base branch for pull request",
                "required": False,
                "group": "Pull Request",
                "examples": ["main", "develop"],
                "default": "main"
            },
            "pull_number": {
                "type": "number",
                "description": "Pull request number",
                "required": False,
                "group": "Pull Request",
                "validation": {
                    "minimum": 1
                },
                "examples": [1, 42, 123]
            },
            "issue_number": {
                "type": "number",
                "description": "Issue number",
                "required": False,
                "group": "Issues",
                "validation": {
                    "minimum": 1
                },
                "examples": [1, 42, 123]
            },
            "username": {
                "type": "string",
                "description": "GitHub username",
                "required": False,
                "group": "User",
                "examples": ["octocat", "defunkt"],
                "validation": {
                    "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
                    "maxLength": 39
                }
            },
            "tag_name": {
                "type": "string",
                "description": "Git tag name for releases",
                "required": False,
                "group": "Releases",
                "examples": ["v1.0.0", "v2.1.3", "release-2023-01"]
            },
            "state": {
                "type": "string",
                "description": "State filter for issues and pull requests",
                "required": False,
                "group": "Filters",
                "validation": {
                    "enum": ["open", "closed", "all"]
                },
                "default": "open"
            },
            "sort": {
                "type": "string",
                "description": "Sort order for lists",
                "required": False,
                "group": "Filters",
                "validation": {
                    "enum": ["created", "updated", "pushed", "full_name"]
                },
                "default": "created"
            },
            "direction": {
                "type": "string",
                "description": "Sort direction",
                "required": False,
                "group": "Filters",
                "validation": {
                    "enum": ["asc", "desc"]
                },
                "default": "desc"
            },
            "per_page": {
                "type": "number",
                "description": "Number of results per page (1-100)",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 1,
                    "maximum": 100
                },
                "default": 30
            },
            "page": {
                "type": "number",
                "description": "Page number for pagination",
                "required": False,
                "group": "Pagination",
                "validation": {
                    "minimum": 1
                },
                "default": 1
            },
            "labels": {
                "type": "array",
                "description": "Array of label names for issue",
                "required": False,
                "group": "Issues",
                "examples": [["bug", "enhancement"], ["documentation"]]
            },
            "assignees": {
                "type": "array",
                "description": "Array of GitHub usernames to assign issue to",
                "required": False,
                "group": "Issues",
                "examples": [["octocat", "defunkt"]]
            },
            "draft": {
                "type": "boolean",
                "description": "Whether the pull request is a draft",
                "required": False,
                "group": "Pull Request",
                "default": False,
                "examples": [True, False]
            },
            "gitignore_template": {
                "type": "string",
                "description": "Gitignore template to use",
                "required": False,
                "group": "Repository",
                "examples": ["Node", "Python", "Java", "Go", "Ruby"]
            },
            "license_template": {
                "type": "string",
                "description": "License template to use",
                "required": False,
                "group": "Repository",
                "examples": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"]
            },
            "has_issues": {
                "type": "boolean",
                "description": "Whether to enable issues for the repository",
                "required": False,
                "group": "Repository Features",
                "default": True,
                "examples": [True, False]
            },
            "has_projects": {
                "type": "boolean",
                "description": "Whether to enable projects for the repository",
                "required": False,
                "group": "Repository Features",
                "default": True,
                "examples": [True, False]
            },
            "has_wiki": {
                "type": "boolean",
                "description": "Whether to enable wiki for the repository",
                "required": False,
                "group": "Repository Features",
                "default": True,
                "examples": [True, False]
            }
        },
        
        # Output definitions
        "outputs": {
            "success": {
                "type": "object",
                "description": "Successful GitHub API response",
                "properties": {
                    "status": {"type": "string", "enum": ["success"]},
                    "data": {"type": "object", "description": "Response data from GitHub API"},
                    "result": {"type": "object", "description": "Full API response data"}
                }
            },
            "error": {
                "type": "object",
                "description": "Error response",
                "properties": {
                    "status": {"type": "string", "enum": ["error"]},
                    "error": {"type": "string", "description": "Error message"},
                    "error_code": {"type": "string", "description": "Error code"}
                }
            }
        },
        
        # Auth configuration - maps operations to required environment keys
        "auth": {
            "get_repo": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "create_repo": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "list_repos": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "list_branches": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "get_file_content": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "create_file": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "update_file": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "create_pull_request": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "list_pull_requests": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "create_issue": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "list_issues": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "get_user": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "get_authenticated_user": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "list_commits": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "create_release": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            },
            "list_releases": {
                "required_env_keys": ["GITHUB_ACCESS_TOKEN"],
                "optional_env_keys": []
            }
        },
        
        # Error codes specific to GitHub
        "error_codes": {
            "400": "Bad Request - Invalid request parameters",
            "401": "Unauthorized - Invalid or missing authentication token",
            "403": "Forbidden - Token lacks required permissions or rate limit exceeded",
            "404": "Not Found - Repository, user, or resource not found",
            "409": "Conflict - Resource already exists or merge conflict",
            "422": "Unprocessable Entity - Validation failed",
            "429": "Too Many Requests - Rate limit exceeded",
            "500": "Internal Server Error - GitHub server error",
            "502": "Bad Gateway - GitHub server temporarily unavailable",
            "503": "Service Unavailable - GitHub maintenance or overload"
        }
    }
    
    # Operation definitions with complete metadata
    OPERATIONS = {
        "get_repo": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}",
            "required_params": ["owner", "repo"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Get Repository",
            "description": "Get detailed information about a repository",
            "group": "Repositories",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "examples": [
                {
                    "name": "Get repository info",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world"
                    }
                }
            ]
        },
        "create_repo": {
            "method": "POST",
            "endpoint": "/user/repos",
            "required_params": ["name"],
            "optional_params": ["description", "private", "auto_init", "has_issues", "has_projects", 
                               "has_wiki", "gitignore_template", "license_template"],
            "body_parameters": ["name", "description", "private", "auto_init", "has_issues", 
                              "has_projects", "has_wiki", "gitignore_template", "license_template"],
            "display_name": "Create Repository",
            "description": "Create a new repository for the authenticated user",
            "group": "Repositories",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Create public repository",
                    "input": {
                        "name": "my-new-repo",
                        "description": "This is my new repository",
                        "private": False,
                        "auto_init": True
                    }
                }
            ]
        },
        "list_repos": {
            "method": "GET",
            "endpoint": "/user/repos",
            "required_params": [],
            "optional_params": ["sort", "direction", "per_page", "page"],
            "body_parameters": [],
            "display_name": "List Repositories",
            "description": "List repositories for the authenticated user",
            "group": "Repositories",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "examples": [
                {
                    "name": "List user repositories",
                    "input": {
                        "sort": "created",
                        "direction": "desc"
                    }
                }
            ]
        },
        "list_branches": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/branches",
            "required_params": ["owner", "repo"],
            "optional_params": ["per_page", "page"],
            "body_parameters": [],
            "display_name": "List Branches",
            "description": "List branches in a repository",
            "group": "Branches",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "examples": [
                {
                    "name": "List repository branches",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world"
                    }
                }
            ]
        },
        "get_file_content": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/contents/{path}",
            "required_params": ["owner", "repo", "path"],
            "optional_params": ["ref"],
            "body_parameters": [],
            "display_name": "Get File Content",
            "description": "Get contents of a file in a repository",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "examples": [
                {
                    "name": "Get README file",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "path": "README.md"
                    }
                }
            ]
        },
        "create_file": {
            "method": "PUT",
            "endpoint": "/repos/{owner}/{repo}/contents/{path}",
            "required_params": ["owner", "repo", "path", "message", "content"],
            "optional_params": ["branch"],
            "body_parameters": ["message", "content", "branch"],
            "display_name": "Create File",
            "description": "Create a new file in a repository",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Create new file",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "path": "newfile.txt",
                        "message": "Create new file",
                        "content": "Hello World!"
                    }
                }
            ]
        },
        "update_file": {
            "method": "PUT",
            "endpoint": "/repos/{owner}/{repo}/contents/{path}",
            "required_params": ["owner", "repo", "path", "message", "content", "sha"],
            "optional_params": ["branch"],
            "body_parameters": ["message", "content", "sha", "branch"],
            "display_name": "Update File",
            "description": "Update an existing file in a repository",
            "group": "Files",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Update existing file",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "path": "README.md",
                        "message": "Update README",
                        "content": "Updated content",
                        "sha": "abc123..."
                    }
                }
            ]
        },
        "create_pull_request": {
            "method": "POST",
            "endpoint": "/repos/{owner}/{repo}/pulls",
            "required_params": ["owner", "repo", "title", "head", "base"],
            "optional_params": ["body", "draft"],
            "body_parameters": ["title", "head", "base", "body", "draft"],
            "display_name": "Create Pull Request",
            "description": "Create a new pull request",
            "group": "Pull Requests",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Create PR",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "title": "New feature",
                        "head": "feature-branch",
                        "base": "main",
                        "body": "This PR adds a new feature"
                    }
                }
            ]
        },
        "list_pull_requests": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/pulls",
            "required_params": ["owner", "repo"],
            "optional_params": ["state", "sort", "direction", "per_page", "page"],
            "body_parameters": [],
            "display_name": "List Pull Requests",
            "description": "List pull requests in a repository",
            "group": "Pull Requests",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "examples": [
                {
                    "name": "List open PRs",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "state": "open"
                    }
                }
            ]
        },
        "create_issue": {
            "method": "POST",
            "endpoint": "/repos/{owner}/{repo}/issues",
            "required_params": ["owner", "repo", "title"],
            "optional_params": ["body", "labels", "assignees"],
            "body_parameters": ["title", "body", "labels", "assignees"],
            "display_name": "Create Issue",
            "description": "Create a new issue",
            "group": "Issues",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Create bug report",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "title": "Bug in login",
                        "body": "Login fails when...",
                        "labels": ["bug"]
                    }
                }
            ]
        },
        "list_issues": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/issues",
            "required_params": ["owner", "repo"],
            "optional_params": ["state", "sort", "direction", "per_page", "page"],
            "body_parameters": [],
            "display_name": "List Issues",
            "description": "List issues in a repository",
            "group": "Issues",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "examples": [
                {
                    "name": "List open issues",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "state": "open"
                    }
                }
            ]
        },
        "get_user": {
            "method": "GET",
            "endpoint": "/users/{username}",
            "required_params": ["username"],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Get User",
            "description": "Get public information about a GitHub user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "object",
            "examples": [
                {
                    "name": "Get user info",
                    "input": {
                        "username": "octocat"
                    }
                }
            ]
        },
        "get_authenticated_user": {
            "method": "GET",
            "endpoint": "/user",
            "required_params": [],
            "optional_params": [],
            "body_parameters": [],
            "display_name": "Get Authenticated User",
            "description": "Get information about the authenticated user",
            "group": "Users",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "object",
            "examples": [
                {
                    "name": "Get current user",
                    "input": {}
                }
            ]
        },
        "list_commits": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/commits",
            "required_params": ["owner", "repo"],
            "optional_params": ["sha", "path", "since", "until", "per_page", "page"],
            "body_parameters": [],
            "display_name": "List Commits",
            "description": "List commits in a repository",
            "group": "Commits",
            "rate_limit_cost": 1,
            "cache_ttl": 60,
            "response_type": "array",
            "examples": [
                {
                    "name": "List recent commits",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world"
                    }
                }
            ]
        },
        "create_release": {
            "method": "POST",
            "endpoint": "/repos/{owner}/{repo}/releases",
            "required_params": ["owner", "repo", "tag_name"],
            "optional_params": ["name", "body", "draft", "prerelease"],
            "body_parameters": ["tag_name", "name", "body", "draft", "prerelease"],
            "display_name": "Create Release",
            "description": "Create a new release",
            "group": "Releases",
            "rate_limit_cost": 1,
            "cache_ttl": 0,
            "response_type": "object",
            "examples": [
                {
                    "name": "Create version release",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world",
                        "tag_name": "v1.0.0",
                        "name": "Version 1.0.0",
                        "body": "First stable release"
                    }
                }
            ]
        },
        "list_releases": {
            "method": "GET",
            "endpoint": "/repos/{owner}/{repo}/releases",
            "required_params": ["owner", "repo"],
            "optional_params": ["per_page", "page"],
            "body_parameters": [],
            "display_name": "List Releases",
            "description": "List releases for a repository",
            "group": "Releases",
            "rate_limit_cost": 1,
            "cache_ttl": 300,
            "response_type": "array",
            "examples": [
                {
                    "name": "List all releases",
                    "input": {
                        "owner": "octocat",
                        "repo": "hello-world"
                    }
                }
            ]
        }
    }
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        
        # Create UniversalRequestNode with full config and operations
        # UniversalRequestNode expects the full config dict, not just api_config
        self.universal_node = UniversalRequestNode(
            config=self.CONFIG,
            operations=self.OPERATIONS,
            sandbox_timeout=sandbox_timeout
        )
    
    def get_schema(self) -> NodeSchema:
        """Return basic schema."""
        return NodeSchema(
            node_type="github",
            version="1.0.0", 
            description="GitHub API integration with embedded configuration",
            parameters=[
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform",
                    required=True,
                    enum=list(self.OPERATIONS.keys())
                ),
                NodeParameter(
                    name="access_token", 
                    type=NodeParameterType.SECRET,
                    description="GitHub Personal Access Token",
                    required=True
                ),
                # Dynamic parameters based on operation
                NodeParameter(
                    name="owner",
                    type=NodeParameterType.STRING,
                    description="Repository owner",
                    required=False
                ),
                NodeParameter(
                    name="repo",
                    type=NodeParameterType.STRING,
                    description="Repository name",
                    required=False
                ),
                NodeParameter(
                    name="name",
                    type=NodeParameterType.STRING,
                    description="Resource name",
                    required=False
                ),
                NodeParameter(
                    name="path",
                    type=NodeParameterType.STRING,
                    description="File path",
                    required=False
                ),
                NodeParameter(
                    name="content",
                    type=NodeParameterType.STRING,
                    description="File content",
                    required=False
                ),
                NodeParameter(
                    name="message",
                    type=NodeParameterType.STRING,
                    description="Commit message",
                    required=False
                ),
                NodeParameter(
                    name="title",
                    type=NodeParameterType.STRING,
                    description="Title for issues, PRs, releases",
                    required=False
                ),
                NodeParameter(
                    name="body",
                    type=NodeParameterType.STRING,
                    description="Body content",
                    required=False
                ),
                NodeParameter(
                    name="state",
                    type=NodeParameterType.STRING,
                    description="State filter",
                    required=False,
                    default="open"
                )
            ],
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "data": NodeParameterType.OBJECT,
                "url": NodeParameterType.STRING,
                "html_url": NodeParameterType.STRING
            }
        )
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute operation using UniversalRequestNode.
        """
        try:
            params = node_data.get("params", {})
            operation = params.get("operation")
            
            if not operation:
                return {
                    "status": "error",
                    "error": "Operation is required",
                    "result": None
                }
            
            if operation not in self.OPERATIONS:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "result": None
                }
            
            # Prepare request data based on operation
            request_data = self._prepare_request_data(operation, params)
            
            # Prepare parameters for UniversalRequestNode
            # The UniversalRequestNode expects all parameters in the params dict
            # Map access_token to api_key for UniversalRequestNode's AuthHandler
            universal_params = {
                "operation": operation,
                "api_key": params.get("access_token"),  # AuthHandler expects api_key
                **request_data  # Merge in the prepared request data
            }
            
            # Create node_data for UniversalRequestNode
            universal_node_data = {
                "params": universal_params
            }
            
            # Execute via UniversalRequestNode
            result = await self.universal_node.execute(universal_node_data)
            
            # Process and enhance the result
            return self._process_result(operation, result)
            
        except Exception as e:
            logger.error(f"GitHub node error: {str(e)}")
            return {
                "status": "error", 
                "error": str(e),
                "result": None
            }
    
    def _prepare_request_data(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data based on operation."""
        data = {}
        
        if operation == "create_repo":
            data = {
                "name": params.get("name"),
                "description": params.get("description", ""),
                "private": params.get("private", False),
                "auto_init": params.get("auto_init", False)
            }
            
            # Add optional parameters
            if params.get("has_issues") is not None:
                data["has_issues"] = params.get("has_issues")
            if params.get("has_projects") is not None:
                data["has_projects"] = params.get("has_projects")
            if params.get("has_wiki") is not None:
                data["has_wiki"] = params.get("has_wiki")
            if params.get("gitignore_template"):
                data["gitignore_template"] = params.get("gitignore_template")
            if params.get("license_template"):
                data["license_template"] = params.get("license_template")
                
        elif operation in ["create_file", "update_file"]:
            import base64
            
            content = params.get("content", "")
            # Check if content is already base64 encoded
            try:
                base64.b64decode(content)
                encoded_content = content
            except:
                # Encode as base64
                encoded_content = base64.b64encode(content.encode()).decode()
            
            data = {
                "message": params.get("message"),
                "content": encoded_content,
                "branch": params.get("branch", "main")
            }
            
            if operation == "update_file":
                data["sha"] = params.get("sha")
                
        elif operation == "create_pull_request":
            data = {
                "title": params.get("title"),
                "head": params.get("head"),
                "base": params.get("base", "main"),
                "body": params.get("body", ""),
                "draft": params.get("draft", False)
            }
            
        elif operation == "create_issue":
            data = {
                "title": params.get("title"),
                "body": params.get("body", "")
            }
            if params.get("labels"):
                data["labels"] = params.get("labels")
            if params.get("assignees"):
                data["assignees"] = params.get("assignees")
                
        elif operation == "create_release":
            data = {
                "tag_name": params.get("tag_name"),
                "name": params.get("name", params.get("tag_name")),
                "body": params.get("body", ""),
                "draft": params.get("draft", False),
                "prerelease": params.get("prerelease", False)
            }
        
        # For GET operations, return params for query string
        elif operation in ["list_repos", "list_branches", "list_pull_requests", "list_issues", 
                          "list_commits", "list_releases"]:
            if params.get("state"):
                data["state"] = params.get("state")
            if params.get("sort"):
                data["sort"] = params.get("sort")
            if params.get("direction"):
                data["direction"] = params.get("direction")
            if params.get("per_page"):
                data["per_page"] = params.get("per_page")
            if params.get("page"):
                data["page"] = params.get("page")
        
        # Pass through required path parameters
        if params.get("owner"):
            data["owner"] = params.get("owner")
        if params.get("repo"):
            data["repo"] = params.get("repo")
        if params.get("path"):
            data["path"] = params.get("path")
        if params.get("username"):
            data["username"] = params.get("username")
        if params.get("sha"):
            data["sha"] = params.get("sha")
        
        return data
    
    def _process_result(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process result based on operation type."""
        if result.get("status") != "success":
            return result
        
        response_data = result.get("data", {})
        
        # Extract operation-specific data
        if isinstance(response_data, dict):
            result.update({
                "data": response_data,
                "url": response_data.get("url", ""),
                "html_url": response_data.get("html_url", "")
            })
            
            # Add specific fields based on operation
            if operation in ["create_file", "update_file"]:
                if response_data.get("content"):
                    result["sha"] = response_data["content"].get("sha", "")
                if response_data.get("commit"):
                    result["message"] = response_data["commit"].get("message", "")
                    
            elif operation in ["create_issue", "create_pull_request"]:
                result["number"] = response_data.get("number")
                result["state"] = response_data.get("state")
                
            elif operation == "create_release":
                result["tag_name"] = response_data.get("tag_name")
                result["id"] = response_data.get("id")
        
        elif isinstance(response_data, list):
            result["data"] = response_data
            result["count"] = len(response_data)
        
        return result
    
    async def close(self):
        """Clean up resources."""
        # UniversalRequestNode doesn't have a close method
        # It uses session per request, so no cleanup needed
        pass

# That's it! Everything is embedded in the node:
# 1. CONFIG defines the API connection settings
# 2. OPERATIONS defines the available operations 
# 3. UniversalRequestNode handles all HTTP complexity
# 4. Node just maps operations to HTTP requests

# Register the GitHub node with the NodeRegistry
logger.debug("🔍 Registering GitHubNode with NodeRegistry")
try:
    # Use the same import strategy as above for consistency
    from .base_node import NodeRegistry
    NodeRegistry.register("github", GitHubNode)
    logger.debug("✅ REGISTERED GitHubNode as 'github' at module level")
except ImportError:
    try:
        from act.nodes.base_node import NodeRegistry
        NodeRegistry.register("github", GitHubNode)
        logger.debug("✅ REGISTERED GitHubNode as 'github' at module level (via act.nodes)")
    except ImportError:
        try:
            from base_node import NodeRegistry
            NodeRegistry.register("github", GitHubNode)
            logger.debug("✅ REGISTERED GitHubNode as 'github' at module level (direct)")
        except Exception as e:
            logger.error(f"❌ ERROR registering GitHubNode: {str(e)}")
except Exception as e:
    logger.error(f"❌ ERROR registering GitHubNode at module level: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    async def test():
        node = GitHubNode()
        
        # Test get authenticated user
        test_data = {
            "params": {
                "operation": "get_authenticated_user",
                "access_token": "ghp_YOUR_TOKEN_HERE",  # Replace with actual token
            }
        }
        
        result = await node.execute(test_data)
        print(f"Result: {result}")
        
        await node.close()
    
    # Uncomment to test
    # asyncio.run(test())