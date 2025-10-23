#!/bin/bash
# Quick MCP Tools Test Script

echo "🧪 Testing ACT Signature System MCP Tools"
echo "=========================================="
echo ""

cd /Users/tajnoah/Downloads/ai-desktop/signature-system/mcp

echo "Test 1: List Available Nodes"
echo "-----------------------------"
node -e "
import('./tools/catalog/list-available-nodes.js').then(async ({ listAvailableNodes }) => {
  const result = await listAvailableNodes({});
  const data = JSON.parse(result.content[0].text);
  if (data.status === 'success') {
    console.log('✅ SUCCESS - Found', data.total_nodes, 'nodes');
    console.log('   Sample:', data.nodes.slice(0, 5).map(n => n.type).join(', '));
  } else {
    console.log('❌ FAILED -', data.message);
  }
});
"

echo ""
echo "Test 2: Get System Status"
echo "-------------------------"
node -e "
import('./tools/utility/get-system-status.js').then(async ({ getSystemStatus }) => {
  const result = await getSystemStatus({});
  const data = JSON.parse(result.content[0].text);
  if (data.status === 'success') {
    console.log('✅ SUCCESS');
    console.log('   Python:', data.python.version);
    console.log('   MCP Server:', data.mcp_server.status);
  } else {
    console.log('❌ FAILED -', data.message);
  }
});
"

echo ""
echo "Test 3: Get Node Info (GitHub)"
echo "-------------------------------"
node -e "
import('./tools/catalog/get-node-info.js').then(async ({ getNodeInfo }) => {
  const result = await getNodeInfo({ node_type: 'github' });
  const data = JSON.parse(result.content[0].text);
  if (data.status === 'success') {
    console.log('✅ SUCCESS - Node ID:', data.id);
    console.log('   Display Name:', data.displayName);
    console.log('   Operations:', data.operations.length);
  } else {
    console.log('❌ FAILED -', data.message);
  }
});
"

echo ""
echo "=========================================="
echo "✅ All tests complete!"
