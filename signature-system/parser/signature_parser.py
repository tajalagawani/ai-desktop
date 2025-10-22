"""
ACT Signature Parser
Parses and manages .act.sig files (TOML format)
"""

import toml
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class ActSignatureParser:
    """Parser and manager for ACT signature files"""

    def __init__(self, signature_path: str):
        """
        Initialize signature parser

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
            Defaults dictionary
        """
        defaults_key = f"node:{node_type}.defaults"
        return self.signature.get(defaults_key, {})

    def get_operations(self, node_type: str) -> Dict[str, Any]:
        """
        Get available operations for a node

        Args:
            node_type: Node type

        Returns:
            Operations dictionary
        """
        ops_key = f"node:{node_type}.operations"
        return self.signature.get(ops_key, {})

    def get_node_metadata(self, node_type: str) -> Dict[str, Any]:
        """
        Get metadata for a node

        Args:
            node_type: Node type

        Returns:
            Metadata dictionary
        """
        meta_key = f"node:{node_type}.metadata"
        return self.signature.get(meta_key, {})

    def add_node(
        self,
        node_type: str,
        auth: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None,
        operations: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add or update a node in the signature

        Args:
            node_type: Node type
            auth: Authentication data (will be converted to env references)
            defaults: Default parameters
            operations: Available operations
            metadata: Node metadata
        """
        # Base node section
        node_key = f"node:{node_type}"
        self.signature[node_key] = {
            'type': node_type,
            'enabled': True,
            'authenticated': True,
            'auth_configured_at': datetime.utcnow().isoformat() + 'Z'
        }

        # Auth section (store as env references)
        auth_key = f"node:{node_type}.auth"
        self.signature[auth_key] = self._to_env_references(node_type, auth)

        # Defaults section
        if defaults:
            defaults_key = f"node:{node_type}.defaults"
            self.signature[defaults_key] = defaults

        # Operations section
        if operations:
            ops_key = f"node:{node_type}.operations"
            self.signature[ops_key] = operations

        # Metadata section
        if metadata:
            meta_key = f"node:{node_type}.metadata"
            self.signature[meta_key] = metadata

        # Update global metadata
        if 'metadata' not in self.signature:
            self.signature['metadata'] = {
                'authenticated_nodes': 0,
                'unauthenticated_nodes': 0
            }

        # Increment authenticated count if this is a new node
        if node_key not in [k for k in self.signature.keys() if k.startswith('node:') and not '.' in k.split(':')[1]]:
            self.signature['metadata']['authenticated_nodes'] = \
                self.signature['metadata'].get('authenticated_nodes', 0) + 1

    def remove_node(self, node_type: str) -> bool:
        """
        Remove a node from the signature

        Args:
            node_type: Node type to remove

        Returns:
            True if node was removed, False if not found
        """
        node_key = f"node:{node_type}"

        if node_key not in self.signature:
            return False

        # Remove all sections for this node
        keys_to_remove = [
            key for key in self.signature.keys()
            if key.startswith(f"node:{node_type}")
        ]

        for key in keys_to_remove:
            del self.signature[key]

        # Update metadata
        if 'metadata' in self.signature:
            self.signature['metadata']['authenticated_nodes'] = \
                self.signature['metadata'].get('authenticated_nodes', 1) - 1

        return True

    def update_node_defaults(self, node_type: str, defaults: Dict[str, Any]) -> bool:
        """
        Update default parameters for a node

        Args:
            node_type: Node type
            defaults: New defaults

        Returns:
            True if updated, False if node not found
        """
        if not self.is_authenticated(node_type):
            return False

        defaults_key = f"node:{node_type}.defaults"
        self.signature[defaults_key] = defaults
        return True

    def get_authenticated_nodes(self) -> List[str]:
        """
        Get list of all authenticated node types

        Returns:
            List of node type strings
        """
        nodes = []
        for key in self.signature.keys():
            if key.startswith('node:') and '.' not in key.split(':')[1]:
                node_type = key.split(':')[1]
                if self.is_authenticated(node_type):
                    nodes.append(node_type)
        return nodes

    def validate(self) -> Dict[str, Any]:
        """
        Validate signature file structure and content

        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'errors': list,
                'warnings': list
            }
        """
        errors = []
        warnings = []

        # Check for required sections
        if 'signature' not in self.signature:
            errors.append("Missing [signature] section")
        else:
            sig = self.signature['signature']
            if 'version' not in sig:
                errors.append("Missing signature.version")

        # Check node sections
        for key in self.signature.keys():
            if key.startswith('node:') and '.' not in key.split(':')[1]:
                node_type = key.split(':')[1]

                # Check for required node fields
                if 'authenticated' not in self.signature[key]:
                    errors.append(f"Node '{node_type}' missing 'authenticated' field")

                # Check auth section exists if authenticated
                if self.signature[key].get('authenticated', False):
                    auth_key = f"node:{node_type}.auth"
                    if auth_key not in self.signature:
                        errors.append(f"Node '{node_type}' is authenticated but missing .auth section")
                    else:
                        # Check env references are valid
                        auth = self.signature[auth_key]
                        for field, value in auth.items():
                            if isinstance(value, str) and '{{.env.' in value:
                                env_var = self._extract_env_var(value)
                                if env_var and not os.getenv(env_var):
                                    warnings.append(f"Environment variable '{env_var}' not set for {node_type}.{field}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'authenticated_nodes': len(self.get_authenticated_nodes())
        }

    def _resolve_env_vars(self, obj: Any) -> Any:
        """
        Recursively resolve {{.env.VARIABLE}} references

        Args:
            obj: Object to resolve (dict, list, or primitive)

        Returns:
            Object with env vars resolved
        """
        if isinstance(obj, dict):
            return {k: self._resolve_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_env_vars(item) for item in obj]
        elif isinstance(obj, str) and '{{.env.' in obj:
            env_var = self._extract_env_var(obj)
            if env_var:
                return os.getenv(env_var, obj)
        return obj

    def _extract_env_var(self, value: str) -> Optional[str]:
        """
        Extract environment variable name from {{.env.VAR}} syntax

        Args:
            value: String potentially containing env reference

        Returns:
            Environment variable name or None
        """
        match = re.search(r'\{\{\.env\.(\w+)\}\}', value)
        return match.group(1) if match else None

    def _to_env_references(self, node_type: str, auth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert auth values to {{.env.VARIABLE}} references

        Args:
            node_type: Node type (for variable naming)
            auth: Authentication dictionary

        Returns:
            Auth dict with env references
        """
        result = {}
        for key, value in auth.items():
            # Convert to env reference format
            env_var_name = f"{node_type.upper()}_{key.upper()}"
            result[key] = f"{{{{.env.{env_var_name}}}}}"
        return result

    def get_signature_info(self) -> Dict[str, Any]:
        """
        Get complete signature information

        Returns:
            Dictionary with all signature data
        """
        authenticated = self.get_authenticated_nodes()

        return {
            'version': self.signature.get('signature', {}).get('version', 'unknown'),
            'user_id': self.signature.get('signature', {}).get('user_id', 'unknown'),
            'authenticated_nodes': [
                {
                    'type': node_type,
                    'operations': list(self.get_operations(node_type).keys()),
                    'operation_count': len(self.get_operations(node_type)),
                    'defaults': self.get_node_defaults(node_type),
                    'metadata': self.get_node_metadata(node_type)
                }
                for node_type in authenticated
            ],
            'total_authenticated': len(authenticated),
            'updated_at': self.signature.get('signature', {}).get('updated_at', 'unknown')
        }
