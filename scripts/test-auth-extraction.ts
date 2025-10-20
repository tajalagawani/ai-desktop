import { parseAllNodes } from '../lib/node-parser';

console.log('Testing Auth Extraction...\n');

try {
  const catalog = parseAllNodes();

  // Filter nodes that require auth
  const authNodes = catalog.nodes.filter(n => n.authInfo.requiresAuth);

  console.log(`✅ Found ${authNodes.length} nodes requiring authentication\n`);

  // Show sample nodes with auth details
  const samples = authNodes.slice(0, 10);

  samples.forEach(node => {
    console.log(`📦 ${node.displayName} (${node.id})`);
    console.log(`   Auth Type: ${node.authInfo.authType || 'not specified'}`);
    console.log(`   Auth Fields:`);

    node.authInfo.authFields.forEach(field => {
      console.log(`     - ${field.field}`);
      console.log(`       Type: ${field.type}`);
      console.log(`       Description: ${field.description}`);
      console.log(`       Required: ${field.required}`);
      if (field.pattern) {
        console.log(`       Pattern: ${field.pattern}`);
      }
    });

    console.log('');
  });

  // Statistics
  console.log('\n📊 Auth Statistics:');
  console.log(`Total nodes: ${catalog.total}`);
  console.log(`Nodes requiring auth: ${authNodes.length}`);
  console.log(`Nodes without auth: ${catalog.total - authNodes.length}`);

  // Count by auth type
  const authTypes: Record<string, number> = {};
  authNodes.forEach(n => {
    const type = n.authInfo.authType || 'unspecified';
    authTypes[type] = (authTypes[type] || 0) + 1;
  });

  console.log('\nAuth types:');
  Object.entries(authTypes)
    .sort(([, a], [, b]) => b - a)
    .forEach(([type, count]) => {
      console.log(`  ${type}: ${count} nodes`);
    });

  // Count auth fields
  const totalAuthFields = authNodes.reduce((sum, n) => sum + n.authInfo.authFields.length, 0);
  console.log(`\nTotal auth fields: ${totalAuthFields}`);
  console.log(`Average auth fields per node: ${(totalAuthFields / authNodes.length).toFixed(1)}`);

} catch (error) {
  console.error('❌ Error:', error);
  process.exit(1);
}
