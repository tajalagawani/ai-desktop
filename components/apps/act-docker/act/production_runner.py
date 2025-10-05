#!/usr/bin/env python3
"""
Production Runner for ACT
Supports: Empty flow files, Hot reload, Agent mode, MiniACT mode, Dynamic port
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional

# Add project root to path
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

def read_port_from_flow(flow_file: str = '/app/flow') -> int:
    """Read port from flow file, return 9999 if not found or file doesn't exist"""
    try:
        flow_path = Path(flow_file)
        if not flow_path.exists():
            return 9999

        content = flow_path.read_text(encoding='utf-8')
        match = re.search(r'^\s*port\s*=\s*(\d+)', content, re.MULTILINE)

        if match:
            return int(match.group(1))
        else:
            return 9999

    except Exception as e:
        print(f"Error reading port: {e}")
        return 9999


def main():
    """Main production runner with full feature support"""

    # === Configuration ===
    flow_file = '/app/flow'
    flow_path = Path(flow_file)

    # Detect port from environment, flow file, or default 9999
    env_port = os.environ.get('ACT_PORT')
    flow_port = read_port_from_flow(flow_file)

    # Priority: ENV > Flow file > Default 9999
    if env_port:
        detected_port = int(env_port)
    else:
        detected_port = flow_port
        os.environ['ACT_PORT'] = str(detected_port)

    # === Display Banner ===
    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 ACT Production Server")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not flow_path.exists():
        print(f"⚠️  No flow file found")
        print(f"📄 Expected: {flow_file}")
        print(f"🔌 Default port: {detected_port}")
        print(f"💡 Server will start in WAITING mode")
        print(f"📝 Create flow file for full functionality")
    else:
        print(f"✅ Flow file: {flow_file}")
        print(f"🔌 Port: {detected_port}")
        print(f"🔥 Hot reload: ENABLED")

    print(f"🌐 Server: http://0.0.0.0:{detected_port}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")

    # === Import ACT Components ===
    try:
        from act.execution_manager import ExecutionManager
        from act.agent_server import AgentServer
        from act.miniact_executor import MiniACTExecutor
        from act.flow_watcher import get_watcher

        # === Initialize System ===

        # Check if flow file is empty or doesn't exist
        flow_is_empty = False
        if flow_path.exists():
            content = flow_path.read_text(encoding='utf-8').strip()
            flow_is_empty = len(content) == 0

        if not flow_path.exists() or flow_is_empty:
            # === WAITING MODE - No flow file or empty ===
            print(f"🔧 Starting in WAITING mode...")
            print(f"💡 Create {flow_file} to enable full functionality")
            print("")

            from flask import Flask, jsonify
            from flask_cors import CORS

            app = Flask(__name__)
            CORS(app)

            @app.route('/health')
            def health():
                return jsonify({
                    "status": "waiting",
                    "message": "No flow file loaded",
                    "port": detected_port
                })

            @app.route('/api/info')
            def info():
                return jsonify({
                    "name": "ACT Server",
                    "status": "waiting",
                    "port": detected_port,
                    "mode": "waiting",
                    "message": "Create a flow file to enable Agent or MiniACT mode"
                })

            @app.route('/api/status')
            def status():
                return jsonify({
                    "status": "waiting",
                    "mode": "waiting",
                    "flow_loaded": False,
                    "port": detected_port
                })

            # Setup hot reload for waiting mode
            watcher = get_watcher(flow_file)

            def on_flow_created():
                print("\n🎉 Flow file detected! Please restart to load it.")
                print("   docker-compose restart")

            watcher.register_callback(on_flow_created)
            watcher.start()

            # Run minimal server
            print(f"✅ Server ready on port {detected_port}")
            print(f"   Health: http://0.0.0.0:{detected_port}/health")
            print("")

            # Suppress werkzeug logs
            import logging
            logging.getLogger('werkzeug').setLevel(logging.WARNING)

            app.run(host="0.0.0.0", port=detected_port, debug=False)

        else:
            # === ACTIVE MODE - Flow file exists ===

            # Initialize execution manager
            execution_manager = ExecutionManager(str(flow_file))

            if execution_manager.has_agent_config():
                # Get configuration
                config = execution_manager.get_agent_config()
                deployment = execution_manager.get_deployment_config()

                # Override port from flow file
                config['port'] = detected_port

                # Create agent server
                agent = AgentServer(execution_manager, config, deployment)

                # === Detect Mode ===
                mode = agent._get_server_mode()

                if mode == "agent":
                    print(f"🌐 Mode: AGENT (HTTP Routes Enabled)")
                    print(f"   Routes: {len(agent.aci_nodes)} ACI routes")
                else:
                    print(f"⚡ Mode: MiniACT (Workflow Execution)")
                    print(f"   Nodes: {len(agent.all_nodes)} workflow nodes")

                    # Setup MiniACT executor
                    agent.miniact_executor = MiniACTExecutor(execution_manager)

                    # Check for auto-execute
                    if agent.miniact_executor.auto_execute_on_load():
                        print(f"   ✅ Auto-executed on load")

                print("")

                # === Setup Hot Reload ===
                watcher = get_watcher(flow_file)
                agent.flow_watcher = watcher
                agent.start_time = None

                def on_flow_change():
                    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print("🔄 Flow file changed - Reload triggered")
                    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print("⚠️  Please restart container to apply changes:")
                    print("   docker-compose restart")
                    print("")

                watcher.register_callback(on_flow_change)
                watcher.start()

                # === Display Access Info ===
                print(f"✅ Server ready!")
                print(f"")
                print(f"📍 Access Points:")
                print(f"   🏠 Dashboard:  http://0.0.0.0:{detected_port}/admin/dashboard")
                print(f"   💚 Health:     http://0.0.0.0:{detected_port}/health")
                print(f"   📊 Info:       http://0.0.0.0:{detected_port}/api/info")
                print(f"   📈 Status:     http://0.0.0.0:{detected_port}/api/status")

                if mode == "agent":
                    print(f"   🚀 Routes:     http://0.0.0.0:{detected_port}/aci")
                else:
                    print(f"   ⚡ Execute:    POST http://0.0.0.0:{detected_port}/execute")

                print(f"")
                print(f"🛑 Stop: Press Ctrl+C or run: docker-compose down")
                print("")

                # === Start Server ===
                agent.run()

            else:
                # No agent config but has flow - run MiniACT server
                print(f"⚡ MiniACT Mode (No Agent Config)")
                print(f"   Running as MiniACT server on port {detected_port}")
                print("")

                # Create minimal Flask server for MiniACT
                from flask import Flask, jsonify, request
                from flask_cors import CORS

                app = Flask(__name__)
                CORS(app)

                # Initialize MiniACT executor
                miniact_executor = MiniACTExecutor(execution_manager)

                @app.route('/health')
                def health():
                    return jsonify({
                        "status": "healthy",
                        "mode": "miniact",
                        "port": detected_port
                    })

                @app.route('/api/info')
                def api_info():
                    return jsonify({
                        "name": "MiniACT Workflow",
                        "mode": "miniact",
                        "port": detected_port,
                        "flow_loaded": True
                    })

                @app.route('/api/status')
                def api_status():
                    return jsonify({
                        "status": "running",
                        "mode": "miniact",
                        "flow_loaded": True,
                        "port": detected_port
                    })

                @app.route('/execute', methods=['POST'])
                def execute_workflow():
                    """Execute entire workflow"""
                    try:
                        data = request.get_json() if request.is_json else {}
                        result = miniact_executor.execute_from_start(data)
                        return jsonify(result)
                    except Exception as e:
                        return jsonify({"error": str(e)}), 500

                @app.route('/api/nodes')
                def get_nodes():
                    """Get all nodes in the workflow"""
                    try:
                        nodes = list(execution_manager.actfile_data.get('nodes', {}).keys())
                        return jsonify({"nodes": nodes})
                    except Exception as e:
                        return jsonify({"error": str(e)}), 500

                # Setup hot reload
                watcher = get_watcher(flow_file)

                def on_flow_change():
                    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print("🔄 Flow file changed - Reload triggered")
                    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print("⚠️  Please restart container to apply changes:")
                    print("   docker-compose restart")
                    print("")

                watcher.register_callback(on_flow_change)
                watcher.start()

                # Display access info
                print(f"✅ MiniACT Server ready!")
                print(f"")
                print(f"📍 Access Points:")
                print(f"   💚 Health:     http://0.0.0.0:{detected_port}/health")
                print(f"   📊 Info:       http://0.0.0.0:{detected_port}/api/info")
                print(f"   ⚡ Execute:    POST http://0.0.0.0:{detected_port}/execute")
                print(f"")
                print(f"🛑 Stop: Press Ctrl+C or run: docker-compose down")
                print("")

                # Suppress werkzeug logs
                import logging
                logging.getLogger('werkzeug').setLevel(logging.WARNING)

                # Run server
                app.run(host="0.0.0.0", port=detected_port, debug=False)

    except KeyboardInterrupt:
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🛑 Shutting down ACT Server...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        sys.exit(0)

    except Exception as e:
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"❌ Fatal Error: {e}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
