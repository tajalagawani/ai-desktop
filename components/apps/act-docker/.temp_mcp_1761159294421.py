
import json
import os
from act.mcp_utils import SignatureManager

signature_path = '/Users/tajnoah/Downloads/ai-desktop/signature-system/signatures/user.act.sig'

try:
    sig = SignatureManager(signature_path)

    if not os.path.exists(signature_path):
        result = {
            "success": True,
            "exists": False,
            "authenticated_nodes": [],
            "total": 0
        }
    else:
        sig.load()
        authenticated = sig.get_authenticated_nodes()

        result = {
            "success": True,
            "exists": True,
            "authenticated_nodes": authenticated,
            "total": len(authenticated)
        }

        # Get details for specific node if requested
        node_type = 'null'
        if node_type and node_type != 'null':
            if sig.is_authenticated(node_type):
                result["node"] = {
                    "type": node_type,
                    "authenticated": True,
                    "defaults": sig.get_node_defaults(node_type)
                }
            else:
                result["node"] = {
                    "type": node_type,
                    "authenticated": False
                }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e)
    }))
