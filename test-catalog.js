// Test script for catalog API
const fetch = require('node-fetch');

async function testCatalog() {
  console.log('Testing Catalog API...\n');

  try {
    const response = await fetch('http://localhost:3000/api/catalog');

    if (!response.ok) {
      const error = await response.text();
      console.error('API Error:', error);
      return;
    }

    const data = await response.json();

    console.log('Catalog Version:', data.version);
    console.log('Last Updated:', data.last_updated);
    console.log('\nStatistics:');
    console.log('- Total Services:', data.stats?.total || 0);
    console.log('- Infrastructure:', data.stats?.infrastructure || 0);
    console.log('- Flows:', data.stats?.flows || 0);
    console.log('- Running:', data.stats?.running || 0);
    console.log('- Stopped:', data.stats?.stopped || 0);
    console.log('- Available:', data.stats?.available || 0);

    console.log('\nVPS Status:');
    if (data.vps) {
      console.log('- Disk Total:', data.vps.diskSpace?.total);
      console.log('- Disk Used:', data.vps.diskSpace?.used);
      console.log('- Disk Available:', data.vps.diskSpace?.available);
      console.log('- Docker Images:', data.vps.docker?.imageCount);
      console.log('- Docker Containers:', data.vps.docker?.containerCount);
    }

    console.log('\nFlow Services:');
    const flows = data.services?.filter(s => s.type === 'flow') || [];
    flows.forEach(flow => {
      console.log(`\n- ${flow.name} (${flow.id})`);
      console.log(`  Status: ${flow.status}`);
      console.log(`  Endpoints: ${flow.endpoints?.length || 0}`);
      if (flow.endpoints?.length > 0) {
        flow.endpoints.slice(0, 3).forEach(ep => {
          console.log(`    ${ep.method} ${ep.path}`);
        });
        if (flow.endpoints.length > 3) {
          console.log(`    ... and ${flow.endpoints.length - 3} more`);
        }
      }
    });

  } catch (error) {
    console.error('Failed to test catalog:', error.message);
  }
}

testCatalog();