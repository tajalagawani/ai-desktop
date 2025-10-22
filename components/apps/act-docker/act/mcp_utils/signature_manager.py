"""
ACT Signature Manager

Manages .act.sig files (TOML format) for pre-authenticated node access.
"""

import toml
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class SignatureManager:
    """Manager for ACT signature files"""

    def __init__(self, signature_path: str):
        """
        Initialize signature manager

        Args:
            signature_path: Path to .act.sig file
        """
        self.signature_path = signature_path
        self.signature: Dict[str, Any] = {}
        self._loaded = False

    def load(self) -> Dict[str, Any]:
        """
        Load and parse signature file

        Returns:
            Parsed signature dictionary

        Raises:
            FileNotFoundError: If signature file doesn't exist
            toml.TomlDecodeError: If TOML syntax is invalid
        """
        if not os.path.exists(self.signature_path):
            raise FileNotFoundError(f"Signature file not found: {self.signature_path}")

        with open(self.signature_path, 'r') as f:
            self.signature = toml.load(f)

        self._loaded = True
        return self.signature

    def save(self) -> None:
        """
        Save signature back to file

        Raises:
            RuntimeError: If signature not loaded
        """
        if not self._loaded:
            raise RuntimeError("Signature must be loaded before saving")

        # Update modified timestamp
        if 'signature' in self.signature:
            self.signature['signature']['updated_at'] = datetime.utcnow().isoformat() + 'Z'

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.signature_path), exist_ok=True)

        with open(self.signature_path, 'w') as f:
            toml.dump(self.signature, f)

    def is_authenticated(self, node_type: str) -> bool:
        """
        Check if a node is authenticated

        Args:
            node_type: Node type (e.g., "github")

        Returns:
            True if authenticated, False otherwise
        """
        node_key = f"node:{node_type}"
        return (node_key in self.signature and
                self.signature[node_key].get('authenticated', False))

    def get_node_auth(self, node_type: str, resolve_env: bool = True) -> Dict[str, Any]:
        """
        Get authentication data for a node

        Args:
            node_type: Node type
            resolve_env: Whether to resolve {{.env.VAR}} references

        Returns:
            Authentication dictionary
        """
        auth_key = f"node:{node_type}.auth"
        auth = self.signature.get(auth_key, {})

        if resolve_env:
            auth = self._resolve_env_vars(auth)

        return auth

    def get_node_defaults(self, node_type: str) -> Dict[str, Any]:
        """
        Get default parameters for a node

        Args:
            node_type: Node type

        Returns:
            Default parameters dictionary
        """
        defaults_key = f"node:{node_type}.defaults"
        return self.signature.get(defaults_key, {})

    def get_authenticated_nodes(self) -> List[str]:
        """
        Get list of all authenticated node types

        Returns:
            List of node type strings
        """
        nodes = []
        for key in self.signature.keys():
            if key.startswith('node:') and not '.' in key.split('node:')[1]:
                node_type = key.split('node:')[1]
                if self.is_authenticated(node_type):
                    nodes.append(node_type)
        return nodes

    def add_node(self, node_type: str, auth: Dict[str, Any],
                 defaults: Optional[Dict[str, Any]] = None,
                 operations: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Add or update a node in signature

        Args:
            node_type: Node type
            auth: Authentication data (will be stored with .env references)
            defaults: Default parameters
            operations: Available operations
            metadata: Additional metadata
        """
        # Add node section
        node_key = f"node:{node_type}"
        self.signature[node_key] = {
            'type': node_type,
            'enabled': True,
            'authenticated': True
        }

        if metadata:
            self.signature[node_key].update(metadata)

        # Add auth section (convert to .env references)
        auth_key = f"node:{node_type}.auth"
        self.signature[auth_key] = self._create_env_references(node_type, auth)

        # Add defaults section
        if defaults:
            defaults_key = f"node:{node_type}.defaults"
            self.signature[defaults_key] = defaults

        # Add operations section
        if operations:
            ops_key = f"node:{node_type}.operations"
            self.signature[ops_key] = operations

        # Update metadata
        if 'metadata' not in self.signature:
            self.signature['metadata'] = {}

        self.signature['metadata']['authenticated_nodes'] = len(self.get_authenticated_nodes())
        self.signature['metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'

        self._loaded = True

    def remove_node(self, node_type: str):
        """
        Remove a node from signature

        Args:
            node_type: Node type to remove
        """
        # Remove all sections for this node
        keys_to_remove = [k for k in self.signature.keys() if k.startswith(f"node:{node_type}")]

        for key in keys_to_remove:
            del self.signature[key]

        # Update metadata
        if 'metadata' in self.signature:
            self.signature['metadata']['authenticated_nodes'] = len(self.get_authenticated_nodes())
            self.signature['metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'

        self._loaded = True

    def update_defaults(self, node_type: str, defaults: Dict[str, Any]):
        """
        Update default parameters for a node

        Args:
            node_type: Node type
            defaults: New default parameters
        """
        if not self.is_authenticated(node_type):
            raise ValueError(f"Node '{node_type}' is not authenticated")

        defaults_key = f"node:{node_type}.defaults"
        self.signature[defaults_key] = defaults

        self._loaded = True

    def _resolve_env_vars(self, obj: Any) -> Any:
        """
        Recursively resolve {{.env.VARIABLE}} references

        Args:
            obj: Object to resolve (dict, list, str, etc.)

        Returns:
            Resolved object
        """
        if isinstance(obj, dict):
            return {k: self._resolve_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Match {{.env.VAR_NAME}}
            pattern = r'\{\{\.env\.([A-Z_][A-Z0-9_]*)\}\}'
            matches = re.findall(pattern, obj)

            if matches:
                for var_name in matches:
                    value = os.getenv(var_name, '')
                    obj = obj.replace(f'{{{{.env.{var_name}}}}}', value)

            return obj
        else:
            return obj

    def _create_env_references(self, node_type: str, auth: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert auth data to .env references

        Args:
            node_type: Node type
            auth: Auth data with actual values

        Returns:
            Auth data with {{.env.VAR}} references
        """
        result = {}
        node_prefix = node_type.upper()

        for key, value in auth.items():
            env_var = f"{node_prefix}_{key.upper()}"
            result[key] = f"{{{{.env.{env_var}}}}}"

            # Set environment variable
            os.environ[env_var] = str(value)

        return result
