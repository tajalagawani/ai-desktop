#!/usr/bin/env python3
"""
Deploy the todo-api.flow service
"""

import requests
import json
import sys
import time

API_BASE = "http://localhost:3000"

def deploy_flow(flow_name: str):
    """Deploy a flow by calling the flows API"""

    print(f"[Deploy] Starting deployment for: {flow_name}")
    print("=" * 60)

    # Call the start action
    url = f"{API_BASE}/api/flows"
    payload = {
        "action": "start",
        "flowName": flow_name
    }

    print(f"[Deploy] POST {url}")
    print(f"[Deploy] Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, timeout=60)

        print(f"[Deploy] Status Code: {response.status_code}")

        result = response.json()
        print(f"[Deploy] Response: {json.dumps(result, indent=2)}")

        if result.get('success'):
            print("=" * 60)
            print("✅ Deployment successful!")
            print("=" * 60)

            # Wait a moment for container to start
            print("\n[Deploy] Waiting for service to start...")
            time.sleep(3)

            # Check status
            check_status(flow_name)

            return True
        else:
            print("=" * 60)
            print("❌ Deployment failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("=" * 60)
            return False

    except Exception as e:
        print("=" * 60)
        print("❌ Exception during deployment!")
        print(f"Error: {str(e)}")
        print("=" * 60)
        return False

def check_status(flow_name: str):
    """Check the status of a deployed flow"""

    print(f"\n[Status] Checking status for: {flow_name}")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/api/flows", timeout=30)
        result = response.json()

        if result.get('success'):
            flows = result.get('flows', [])

            # Find our flow
            todo_flow = next((f for f in flows if f['name'] == flow_name), None)

            if todo_flow:
                print(f"[Status] Flow found!")
                print(f"  Name: {todo_flow.get('name')}")
                print(f"  Port: {todo_flow.get('port')}")
                print(f"  Mode: {todo_flow.get('mode')}")
                print(f"  Agent: {todo_flow.get('agent_name')}")
                print(f"  Description: {todo_flow.get('description')}")

                container = todo_flow.get('container', {})
                print(f"\n[Container Status]")
                print(f"  Running: {container.get('running')}")
                print(f"  Status: {container.get('status')}")

                health = todo_flow.get('health', {})
                print(f"\n[Health Status]")
                print(f"  Status: {health.get('status')}")

                if container.get('running'):
                    port = todo_flow.get('port')
                    print(f"\n✅ Service is running!")
                    print(f"   Access at: http://localhost:{port}")
                    print(f"\n📋 Available endpoints:")
                    print(f"   - GET    http://localhost:{port}/api/todos")
                    print(f"   - POST   http://localhost:{port}/api/todos")
                    print(f"   - GET    http://localhost:{port}/api/todos/:id")
                    print(f"   - PUT    http://localhost:{port}/api/todos/:id")
                    print(f"   - DELETE http://localhost:{port}/api/todos/:id")
                    print(f"   - GET    http://localhost:{port}/api/todos/status/:status")
                    print(f"\n🔍 Test with:")
                    print(f'   curl http://localhost:{port}/health')
                    print(f'   curl http://localhost:{port}/api/todos')
                else:
                    print(f"\n⚠️  Service is not running yet")
                    print(f"   Status: {container.get('status')}")

            else:
                print(f"[Status] Flow '{flow_name}' not found in active flows")
        else:
            print(f"[Status] Failed to fetch flows: {result.get('error')}")

    except Exception as e:
        print(f"[Status] Error checking status: {str(e)}")

    print("=" * 60)

if __name__ == "__main__":
    flow_name = "todo-api"

    print("\n🚀 Todo API Deployment Script")
    print("=" * 60)

    success = deploy_flow(flow_name)

    sys.exit(0 if success else 1)
