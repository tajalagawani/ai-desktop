#!/usr/bin/env python3
"""
Read port from flow file and output it for Docker Compose
"""
import re
import sys

def read_port_from_flow(flow_file='/app/flow'):
    """Read port configuration from flow file"""
    try:
        with open(flow_file, 'r') as f:
            content = f.read()

        # Look for port = <number> in [configuration] section
        match = re.search(r'^\s*port\s*=\s*(\d+)', content, re.MULTILINE)
        if match:
            return int(match.group(1))
        else:
            # Default port if not found
            return 8080
    except Exception as e:
        print(f"Error reading port: {e}", file=sys.stderr)
        return 8080

if __name__ == "__main__":
    port = read_port_from_flow()
    print(port)
