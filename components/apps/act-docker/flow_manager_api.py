#!/usr/bin/env python3
"""
Flow Manager API
Centralized API to manage all ACT flows
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import json as json_lib
from flow_discovery import FlowDiscovery

app = Flask(__name__)
CORS(app)


def pretty_json(data):
    """Return beautifully formatted JSON response"""
    return Response(
        json_lib.dumps(data, indent=2, sort_keys=False),
        mimetype='application/json'
    )

# Configuration
FLOWS_DIR = "./flows"
DOCKER_COMPOSE_FILE = "docker-compose.yml"


def get_all_flows() -> List[Dict]:
    """Discover all flows"""
    discovery = FlowDiscovery(FLOWS_DIR)
    flows = discovery.discover_flows()
    return flows


def get_container_status(flow_name: str) -> Dict:
    """Get Docker container status for a flow"""
    try:
        container_name = f"act-{flow_name}"
        result = subprocess.run(
            ["docker", "inspect", container_name, "--format", "{{json .State}}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            state = json.loads(result.stdout)
            return {
                "running": state.get("Running", False),
                "status": state.get("Status", "unknown"),
                "started_at": state.get("StartedAt"),
                "pid": state.get("Pid", 0)
            }
        else:
            return {"running": False, "status": "not_found"}
    except Exception as e:
        return {"running": False, "status": "error", "error": str(e)}


def get_flow_health(port: int) -> Dict:
    """Check flow health via HTTP"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "unhealthy", "code": response.status_code}
    except requests.exceptions.RequestException as e:
        return {"status": "unreachable", "error": str(e)}


def get_container_logs(flow_name: str, lines: int = 100) -> str:
    """Get Docker container logs"""
    try:
        container_name = f"act-{flow_name}"
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error fetching logs: {e}"


def docker_compose_command(command: str, service: Optional[str] = None) -> Dict:
    """Execute docker-compose command"""
    try:
        cmd = ["docker-compose", command]
        if service:
            cmd.append(service)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# =============================================
# API Endpoints
# =============================================

@app.route('/api/flows', methods=['GET'])
def list_flows():
    """Get all flows with status"""
    flows = get_all_flows()

    # Enrich with runtime status
    for flow in flows:
        container_status = get_container_status(flow['name'])
        flow['container'] = container_status

        if container_status.get('running'):
            health = get_flow_health(flow['port'])
            flow['health'] = health
        else:
            flow['health'] = {"status": "stopped"}

    return pretty_json({
        "success": True,
        "total": len(flows),
        "flows": flows,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })


@app.route('/api/flows/<flow_name>', methods=['GET'])
def get_flow(flow_name: str):
    """Get specific flow details"""
    flows = get_all_flows()
    flow = next((f for f in flows if f['name'] == flow_name), None)

    if not flow:
        return pretty_json({"success": False, "error": "Flow not found"}), 404

    # Add runtime info
    container_status = get_container_status(flow_name)
    flow['container'] = container_status

    if container_status.get('running'):
        health = get_flow_health(flow['port'])
        flow['health'] = health

        # Get detailed info from flow
        try:
            info_response = requests.get(f"http://localhost:{flow['port']}/api/info", timeout=2)
            if info_response.status_code == 200:
                flow['info'] = info_response.json()
        except:
            pass
    else:
        flow['health'] = {"status": "stopped"}

    return pretty_json({"success": True, "flow": flow})


@app.route('/api/flows/<flow_name>/status', methods=['GET'])
def get_flow_status(flow_name: str):
    """Get flow status"""
    container_status = get_container_status(flow_name)

    if container_status.get('running'):
        flows = get_all_flows()
        flow = next((f for f in flows if f['name'] == flow_name), None)

        if flow:
            health = get_flow_health(flow['port'])
            return jsonify({
                "flow": flow_name,
                "container": container_status,
                "health": health
            })

    return jsonify({
        "flow": flow_name,
        "container": container_status,
        "health": {"status": "stopped"}
    })


@app.route('/api/flows/<flow_name>/restart', methods=['POST'])
def restart_flow(flow_name: str):
    """Restart specific flow"""
    service_name = f"act-{flow_name}"
    result = docker_compose_command("restart", service_name)

    if result['success']:
        return jsonify({
            "success": True,
            "message": f"Flow '{flow_name}' restarted successfully"
        })
    else:
        return jsonify({
            "success": False,
            "error": result.get('stderr', 'Unknown error')
        }), 500


@app.route('/api/flows/<flow_name>/stop', methods=['POST'])
def stop_flow(flow_name: str):
    """Stop specific flow"""
    service_name = f"act-{flow_name}"
    result = docker_compose_command("stop", service_name)

    if result['success']:
        return jsonify({
            "success": True,
            "message": f"Flow '{flow_name}' stopped successfully"
        })
    else:
        return jsonify({
            "success": False,
            "error": result.get('stderr', 'Unknown error')
        }), 500


@app.route('/api/flows/<flow_name>/start', methods=['POST'])
def start_flow(flow_name: str):
    """Start specific flow"""
    service_name = f"act-{flow_name}"
    result = docker_compose_command("start", service_name)

    if result['success']:
        return jsonify({
            "success": True,
            "message": f"Flow '{flow_name}' started successfully"
        })
    else:
        return jsonify({
            "success": False,
            "error": result.get('stderr', 'Unknown error')
        }), 500


@app.route('/api/flows/<flow_name>/logs', methods=['GET'])
def get_flow_logs(flow_name: str):
    """Get flow logs"""
    lines = request.args.get('lines', 100, type=int)
    logs = get_container_logs(flow_name, lines)

    return jsonify({
        "flow": flow_name,
        "lines": lines,
        "logs": logs
    })


@app.route('/api/flows/<flow_name>/health', methods=['GET'])
def check_flow_health(flow_name: str):
    """Check flow health"""
    flows = get_all_flows()
    flow = next((f for f in flows if f['name'] == flow_name), None)

    if not flow:
        return jsonify({"error": "Flow not found"}), 404

    health = get_flow_health(flow['port'])
    return jsonify({
        "flow": flow_name,
        "port": flow['port'],
        "health": health
    })


@app.route('/api/flows/reload-all', methods=['POST'])
def reload_all_flows():
    """Regenerate docker-compose and restart all flows"""
    try:
        # Regenerate docker-compose.yml
        result = subprocess.run(
            ["python3", "docker-compose-generator.py"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": "Failed to regenerate docker-compose.yml",
                "details": result.stderr
            }), 500

        # Restart all services
        restart_result = docker_compose_command("restart")

        return jsonify({
            "success": True,
            "message": "All flows reloaded and restarted",
            "generation_output": result.stdout
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Get overall system statistics"""
    flows = get_all_flows()

    total_flows = len(flows)
    running_flows = 0
    healthy_flows = 0

    for flow in flows:
        container_status = get_container_status(flow['name'])
        if container_status.get('running'):
            running_flows += 1

            health = get_flow_health(flow['port'])
            if health.get('status') == 'healthy':
                healthy_flows += 1

    # Get Docker stats
    try:
        docker_stats = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        containers = [json.loads(line) for line in docker_stats.stdout.strip().split('\n') if line]
    except:
        containers = []

    return pretty_json({
        "success": True,
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "flows": {
            "total": total_flows,
            "running": running_flows,
            "healthy": healthy_flows,
            "stopped": total_flows - running_flows
        },
        "containers": containers,
        "system": {
            "flows_directory": FLOWS_DIR,
            "docker_compose": DOCKER_COMPOSE_FILE
        }
    })


@app.route('/api/system/rebuild', methods=['POST'])
def rebuild_system():
    """Rebuild all Docker images and restart"""
    try:
        # Regenerate config
        gen_result = subprocess.run(
            ["python3", "docker-compose-generator.py"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if gen_result.returncode != 0:
            return jsonify({
                "success": False,
                "error": "Failed to regenerate config"
            }), 500

        # Rebuild and restart
        build_result = subprocess.run(
            ["docker-compose", "up", "--build", "-d"],
            capture_output=True,
            text=True,
            timeout=120
        )

        return jsonify({
            "success": build_result.returncode == 0,
            "message": "System rebuilt successfully" if build_result.returncode == 0 else "Rebuild failed",
            "output": build_result.stdout,
            "error": build_result.stderr
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Management API health check"""
    return pretty_json({
        "success": True,
        "status": "healthy",
        "service": "Flow Manager API",
        "version": "1.0.0",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """API documentation - Beautiful JSON response"""
    from flask import Response
    import json

    doc = {
        "service": "ACT Flow Manager API",
        "version": "1.0.0",
        "description": "Centralized management API for all ACT workflows",
        "documentation": {
            "flows": {
                "title": "Flow Management",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/flows",
                        "description": "List all flows with status",
                        "response": "Array of flow objects with health status"
                    },
                    {
                        "method": "GET",
                        "path": "/api/flows/{name}",
                        "description": "Get detailed information for specific flow",
                        "parameters": {"name": "Flow name (e.g., 'restaurant', 'math')"}
                    },
                    {
                        "method": "GET",
                        "path": "/api/flows/{name}/status",
                        "description": "Get flow runtime status",
                        "response": "Container and health status"
                    },
                    {
                        "method": "POST",
                        "path": "/api/flows/{name}/restart",
                        "description": "Restart specific flow container"
                    },
                    {
                        "method": "POST",
                        "path": "/api/flows/{name}/stop",
                        "description": "Stop specific flow container"
                    },
                    {
                        "method": "POST",
                        "path": "/api/flows/{name}/start",
                        "description": "Start specific flow container"
                    },
                    {
                        "method": "GET",
                        "path": "/api/flows/{name}/logs",
                        "description": "Get flow container logs",
                        "parameters": {"lines": "Number of log lines to retrieve (default: 100)"}
                    },
                    {
                        "method": "GET",
                        "path": "/api/flows/{name}/health",
                        "description": "Check flow health endpoint"
                    },
                    {
                        "method": "POST",
                        "path": "/api/flows/reload-all",
                        "description": "Reload all flows (regenerate config and restart)"
                    }
                ]
            },
            "system": {
                "title": "System Management",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/system/stats",
                        "description": "Get overall system statistics",
                        "response": "Flow counts, container stats, system info"
                    },
                    {
                        "method": "POST",
                        "path": "/api/system/rebuild",
                        "description": "Rebuild all Docker images and restart"
                    },
                    {
                        "method": "GET",
                        "path": "/health",
                        "description": "Management API health check"
                    }
                ]
            }
        },
        "examples": {
            "list_flows": "curl http://localhost:8000/api/flows",
            "get_flow": "curl http://localhost:8000/api/flows/restaurant",
            "restart_flow": "curl -X POST http://localhost:8000/api/flows/restaurant/restart",
            "system_stats": "curl http://localhost:8000/api/system/stats"
        },
        "ui": {
            "management_dashboard": "Open management_ui.html in your browser",
            "description": "Beautiful web interface for managing all flows"
        }
    }

    # Pretty print JSON with indentation
    pretty_json = json.dumps(doc, indent=2, sort_keys=False)

    return Response(pretty_json, mimetype='application/json')


if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎛️  ACT Flow Manager API")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("📍 Management API: http://localhost:8000")
    print("📊 System Stats:   http://localhost:8000/api/system/stats")
    print("📋 List Flows:     http://localhost:8000/api/flows")
    print()
    print("🛑 Stop: Press Ctrl+C")
    print()

    app.run(host="0.0.0.0", port=8000, debug=False)
