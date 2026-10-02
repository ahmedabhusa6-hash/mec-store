// Poll Railway deployments until the latest is SUCCESS/FAILED, then print status
require('dotenv').config({ path: '/home/z/my-project/.env', override: true });

async function gql(query, variables) {
  const res = await fetch('https://backboard.railway.com/graphql/v2', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.RAILWAY_TOKEN}` },
    body: JSON.stringify({ query, variables }),
  });
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors).slice(0, 300));
  return data.data;
}

async function main() {
  for (let i = 0; i < 40; i++) {
    const d = await gql(
      `query deps($input: DeploymentListInput!) {
        deployments(input: $input) {
          edges { node { id status createdAt } }
        }
      }`,
      { input: { projectId: process.env.RAILWAY_PROJECT_ID, environmentId: process.env.RAILWAY_ENVIRONMENT_ID, serviceId: process.env.RAILWAY_SERVICE_ID } }
    );
    const deps = d.deployments.edges.map(e => e.node);
    const latest = deps[0];
    console.log(`[${new Date().toISOString().slice(11, 19)}] ${latest.id.slice(0, 8)} status=${latest.status} src=${JSON.stringify(latest.meta?.source).slice(0, 40)}`);
    if (latest.status === 'SUCCESS' || latest.status === 'FAILED' || latest.status === 'CRASHED') {
      console.log('FINAL:', latest.status);
      process.exit(latest.status === 'SUCCESS' ? 0 : 1);
    }
    await new Promise(r => setTimeout(r, 15000));
  }
  console.log('TIMEOUT waiting for deployment');
  process.exit(2);
}
main().catch(e => { console.error('ERR:', e.message); process.exit(1); });
