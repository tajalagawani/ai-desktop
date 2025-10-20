import { parseAllNodes } from '../lib/node-parser';

console.log('Testing Node Parser...\n');

try {
  const catalog = parseAllNodes();

  console.log(`✅ Successfully parsed ${catalog.total} nodes`);
  console.log(`Generated: ${catalog.generated}\n`);

  // Show first 5 nodes as sample
  console.log('Sample nodes:\n');
  catalog.nodes.slice(0, 5).forEach(node => {
    console.log(`📦 ${node.displayName} (${node.id})`);
    console.log(`   Description: ${node.description.substring(0, 80)}...`);
    console.log(`   Operations: ${node.operations.length}`);
    console.log(`   Parameters: ${node.parameters.length}`);
    console.log(`   Categories: ${Object.keys(node.operationCategories).join(', ')}`);
    console.log(`   Capabilities: ${Object.entries(node.capabilities).filter(([k, v]) => v).map(([k]) => k).join(', ')}`);
    console.log('');
  });

  // Show statistics
  console.log('\n📊 Statistics:');
  console.log(`Total nodes: ${catalog.total}`);

  const totalOps = catalog.nodes.reduce((sum, n) => sum + n.operations.length, 0);
  console.log(`Total operations: ${totalOps}`);

  const nodesWithOps = catalog.nodes.filter(n => n.operations.length > 0).length;
  console.log(`Nodes with operations: ${nodesWithOps}`);

  const nodesWithParams = catalog.nodes.filter(n => n.parameters.length > 0).length;
  console.log(`Nodes with parameters: ${nodesWithParams}`);

  // Show all tags
  const allTags = new Set<string>();
  catalog.nodes.forEach(n => n.tags.forEach(t => allTags.add(t)));
  console.log(`\nAll tags: ${Array.from(allTags).sort().join(', ')}`);

  // Show nodes by category
  console.log('\n📁 Nodes by tag:');
  const tagCounts: Record<string, number> = {};
  catalog.nodes.forEach(n => {
    n.tags.forEach(tag => {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    });
  });
  Object.entries(tagCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .forEach(([tag, count]) => {
      console.log(`   ${tag}: ${count} nodes`);
    });

} catch (error) {
  console.error('❌ Error:', error);
  process.exit(1);
}
