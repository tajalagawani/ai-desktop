#!/usr/bin/env python3
"""
Find Available Port Tool
Scans all flow files and service catalog to find the next available port
"""

import json
import re
import sys
from pathlib import Path
from typing import Set, List


def find_ports_in_flows(flows_dir: str = "./flows") -> Set[int]:
    """Scan all .flow files and extract port numbers"""
    ports = set()
    flows_path = Path(flows_dir)

    if not flows_path.exists():
        return ports

    for flow_file in flows_path.glob("*.flow"):
        try:
            content = flow_file.read_text(encoding='utf-8')
            # Match: port = 9001 or port=9001
            matches = re.findall(r'^port\s*=\s*(\d+)', content, re.MULTILINE)
            for match in matches:
                ports.add(int(match))
        except Exception as e:
            print(f"Warning: Could not read {flow_file}: {e}", file=sys.stderr)

    return ports


def find_ports_in_service_catalog(catalog_path: str = "./catalogs/service-catalog.json") -> Set[int]:
    """Scan service catalog for registered ports"""
    ports = set()
    catalog_file = Path(catalog_path)

    if not catalog_file.exists():
        return ports

    try:
        data = json.loads(catalog_file.read_text(encoding='utf-8'))

        # Check services array
        if 'services' in data:
            for service in data['services']:
                # Check for port field
                if 'port' in service:
                    ports.add(int(service['port']))

                # Check for connection.port
                if 'connection' in service and 'port' in service['connection']:
                    ports.add(int(service['connection']['port']))

                # Check for endpoints with ports
                if 'endpoints' in service:
                    for endpoint in service['endpoints']:
                        if isinstance(endpoint, dict) and 'port' in endpoint:
                            ports.add(int(endpoint['port']))

    except Exception as e:
        print(f"Warning: Could not read service catalog: {e}", file=sys.stderr)

    return ports


def find_ports_in_docker_compose(compose_path: str = "./docker-compose.yml") -> Set[int]:
    """Scan docker-compose.yml for exposed ports"""
    ports = set()
    compose_file = Path(compose_path)

    if not compose_file.exists():
        return ports

    try:
        content = compose_file.read_text(encoding='utf-8')
        # Match: "9001:9001" or - "9001:9001"
        matches = re.findall(r'["\']?(\d{4,5}):(\d{4,5})["\']?', content)
        for host_port, container_port in matches:
            ports.add(int(host_port))
            ports.add(int(container_port))
    except Exception as e:
        print(f"Warning: Could not read docker-compose.yml: {e}", file=sys.stderr)

    return ports


def find_next_available_port(start_port: int = 9001, end_port: int = 9999) -> int:
    """Find the next available port across all sources"""

    # Collect all used ports
    used_ports = set()

    # Scan flow files
    flow_ports = find_ports_in_flows()
    used_ports.update(flow_ports)

    # Scan service catalog
    catalog_ports = find_ports_in_service_catalog("../flow-architect/catalogs/service-catalog.json")
    used_ports.update(catalog_ports)

    # Scan docker-compose.yml
    compose_ports = find_ports_in_docker_compose()
    used_ports.update(compose_ports)

    # Find next available port
    for port in range(start_port, end_port + 1):
        if port not in used_ports:
            return port

    # If all ports exhausted, return error
    raise RuntimeError(f"No available ports in range {start_port}-{end_port}")


def main():
    """CLI for port detection"""
    import argparse

    parser = argparse.ArgumentParser(description='Find next available port for flow deployment')
    parser.add_argument('--start', type=int, default=9001, help='Start of port range (default: 9001)')
    parser.add_argument('--end', type=int, default=9999, help='End of port range (default: 9999)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all used ports')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        # Collect all used ports
        flow_ports = find_ports_in_flows()
        catalog_ports = find_ports_in_service_catalog("../flow-architect/catalogs/service-catalog.json")
        compose_ports = find_ports_in_docker_compose()

        all_used_ports = sorted(flow_ports | catalog_ports | compose_ports)

        # Find next available
        next_port = find_next_available_port(args.start, args.end)

        if args.json:
            # JSON output
            output = {
                "available_port": next_port,
                "used_ports": all_used_ports,
                "sources": {
                    "flows": sorted(list(flow_ports)),
                    "service_catalog": sorted(list(catalog_ports)),
                    "docker_compose": sorted(list(compose_ports))
                }
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            if args.verbose:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("🔍 Port Detection Report")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print()
                print(f"📦 Flow files: {len(flow_ports)} ports used")
                if flow_ports:
                    print(f"   {sorted(flow_ports)}")
                print()
                print(f"📋 Service catalog: {len(catalog_ports)} ports used")
                if catalog_ports:
                    print(f"   {sorted(catalog_ports)}")
                print()
                print(f"🐳 Docker Compose: {len(compose_ports)} ports used")
                if compose_ports:
                    print(f"   {sorted(compose_ports)}")
                print()
                print(f"📊 Total used ports: {len(all_used_ports)}")
                print(f"   {all_used_ports}")
                print()
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            print(f"{next_port}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
