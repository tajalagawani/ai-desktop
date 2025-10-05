#!/usr/bin/env python3
"""
Flow Discovery Script
Scans flows/ directory and extracts metadata from each .flow file
"""

import re
from pathlib import Path
from typing import List, Dict, Optional


class FlowDiscovery:
    """Discover and parse all flow files in a directory"""

    def __init__(self, flows_dir: str = "./flows"):
        self.flows_dir = Path(flows_dir)

    def discover_flows(self) -> List[Dict[str, any]]:
        """
        Find all .flow files and extract their metadata

        Returns:
            List of flow metadata dictionaries with:
            - name: Flow name (filename without .flow)
            - path: Full path to flow file
            - port: Port number from flow file (auto-assigned if missing)
            - agent_name: Agent name from [agent] section
            - mode: 'agent' or 'miniact' (detected from routes)
        """
        if not self.flows_dir.exists():
            print(f"⚠️  Flows directory not found: {self.flows_dir}")
            return []

        flow_files = sorted(self.flows_dir.glob("*.flow"))

        if not flow_files:
            print(f"⚠️  No .flow files found in {self.flows_dir}")
            return []

        flows_metadata = []
        used_ports = set()
        next_auto_port = 9000  # Start auto-assigning from port 9000

        for flow_file in flow_files:
            metadata = self._parse_flow_metadata(flow_file, used_ports, next_auto_port)
            if metadata:
                flows_metadata.append(metadata)
                used_ports.add(metadata['port'])
                # Update next_auto_port if we auto-assigned
                if 'auto_assigned' in metadata and metadata['auto_assigned']:
                    next_auto_port = metadata['port'] + 1

        return flows_metadata

    def _parse_flow_metadata(self, flow_path: Path, used_ports: set, next_auto_port: int) -> Optional[Dict]:
        """Extract metadata from a single flow file"""
        try:
            content = flow_path.read_text(encoding='utf-8')

            # Skip empty files
            if not content.strip():
                print(f"⚠️  Skipping empty flow: {flow_path.name}")
                return None

            # Extract port (from [agent] section or deployment section)
            port = self._extract_port(content)
            auto_assigned = False

            if not port:
                # Auto-assign port if not found
                while next_auto_port in used_ports:
                    next_auto_port += 1
                port = next_auto_port
                auto_assigned = True
                print(f"🔧 Auto-assigned port {port} to {flow_path.name}")

            # Extract agent name
            agent_name = self._extract_agent_name(content)

            # Detect mode (agent vs miniact)
            mode = self._detect_mode(content)

            # Flow name from filename
            flow_name = flow_path.stem

            return {
                "name": flow_name,
                "path": str(flow_path.absolute()),
                "port": port,
                "agent_name": agent_name or f"{flow_name}-agent",
                "mode": mode,
                "auto_assigned": auto_assigned
            }

        except Exception as e:
            print(f"❌ Error parsing {flow_path.name}: {e}")
            return None

    def _extract_port(self, content: str) -> Optional[int]:
        """Extract port number from flow file"""
        # Try [deployment] section first
        match = re.search(r'^\s*port\s*=\s*(\d+)', content, re.MULTILINE)
        if match:
            return int(match.group(1))

        # Try [agent] section
        match = re.search(r'\[agent\].*?port\s*=\s*(\d+)', content, re.DOTALL)
        if match:
            return int(match.group(1))

        return None

    def _extract_agent_name(self, content: str) -> Optional[str]:
        """Extract agent name from [agent] section"""
        match = re.search(r'agent_name\s*=\s*["\']?([^"\'\n]+)["\']?', content)
        if match:
            return match.group(1).strip()
        return None

    def _detect_mode(self, content: str) -> str:
        """Detect if flow is in agent or miniact mode"""
        # Check for ACI node definitions (agent mode indicator)
        has_aci_nodes = bool(re.search(r'\[node:.*\]\s*type\s*=\s*aci_node', content))

        # Check for route definitions
        has_routes = bool(re.search(r'route\s*=', content))

        if has_aci_nodes or has_routes:
            return "agent"
        return "miniact"

    def validate_flows(self, flows: List[Dict]) -> Dict[str, any]:
        """
        Validate discovered flows for conflicts

        Returns:
            Dictionary with validation results:
            - valid: True if all flows are valid
            - errors: List of error messages
            - warnings: List of warning messages
        """
        errors = []
        warnings = []

        if not flows:
            errors.append("No valid flows found")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Check for port conflicts
        ports = {}
        for flow in flows:
            port = flow['port']
            if port in ports:
                errors.append(
                    f"Port conflict: {flow['name']} and {ports[port]} both use port {port}"
                )
            else:
                ports[port] = flow['name']

        # Check for duplicate names
        names = {}
        for flow in flows:
            name = flow['name']
            if name in names:
                errors.append(
                    f"Duplicate flow name: {name} appears multiple times"
                )
            else:
                names[name] = True

        # Warn about port ranges
        for flow in flows:
            port = flow['port']
            if port < 1024:
                warnings.append(
                    f"{flow['name']}: Port {port} is in privileged range (< 1024)"
                )
            elif port > 65535:
                errors.append(
                    f"{flow['name']}: Invalid port {port} (must be 1-65535)"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def print_summary(self, flows: List[Dict]):
        """Print a formatted summary of discovered flows"""
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📦 Discovered {len(flows)} flow(s)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for flow in flows:
            mode_icon = "🌐" if flow['mode'] == 'agent' else "⚡"
            port_info = f"{flow['port']}"
            if flow.get('auto_assigned'):
                port_info += " (auto-assigned)"

            print(f"\n{mode_icon} {flow['name']}")
            print(f"   Port: {port_info}")
            print(f"   Mode: {flow['mode']}")
            print(f"   Agent: {flow['agent_name']}")
            print(f"   File: {Path(flow['path']).name}")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


def main():
    """CLI for flow discovery"""
    import sys

    flows_dir = sys.argv[1] if len(sys.argv) > 1 else "./flows"

    print(f"🔍 Scanning for flows in: {flows_dir}")

    discovery = FlowDiscovery(flows_dir)
    flows = discovery.discover_flows()

    if not flows:
        print("❌ No valid flows found")
        sys.exit(1)

    # Print summary
    discovery.print_summary(flows)

    # Validate
    validation = discovery.validate_flows(flows)

    if validation['warnings']:
        print("⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
        print()

    if validation['errors']:
        print("❌ Errors:")
        for error in validation['errors']:
            print(f"   • {error}")
        print()
        sys.exit(1)

    print("✅ All flows validated successfully")

    # Output JSON for use by other scripts
    if "--json" in sys.argv:
        import json
        print(json.dumps(flows, indent=2))


if __name__ == "__main__":
    main()
