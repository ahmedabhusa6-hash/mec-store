// Railway GraphQL: find variable IDs for DATABASE_URL + ADMIN_TOKEN, show masked values
require('dotenv').config({ path: '/home/z/my-project/.env', override: true });
const TOKEN = process.env.RAILWAY_TOKEN;

const QUERY = `
query vars($projectId: String!, $environmentId: String!) {
  me { id name }
  project(id: $projectId) {
    name
    environments(first: 5) { edges { node { id name } } }
    services(first: 10) { edges { node { id name } } }
  }
  environment(id: $environmentId) {
    name
    serviceConnections { edges { node { id service { id name } } } }
  }
}`;

async function gql(query, variables) {
  const res = await fetch('https://backboard.railway.com/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${TOKEN}` },
    body: JSON.stringify({ query, variables }),
  });
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors).slice(0, 300));
  return data.data;
}

async function main() {
  const me = await gql(`query { me { id name } }`);
  console.log('auth OK, user:', JSON.stringify(me.me));
  const svc = await gql(`
    query serviceVars($environmentId: String!, $serviceId: String!) {
      service(id: $serviceId) {
        name
        serviceInstances(first: 5) { edges { node { id environment { id name } } } }
      }
      variables(environmentId: $environmentId, serviceId: $serviceId, first: 50) {
        edges { node { id name value createdAt } }
      }
    }`, { environmentId: process.env.RAILWAY_ENVIRONMENT_ID, serviceId: process.env.RAILWAY_SERVICE_ID });
  console.log('service:', svc.service.name);
  for (const edge of svc.variables.edges) {
    const v = edge.node;
    const masked = v.name === 'DATABASE_URL' || v.name === 'ADMIN_TOKEN' || v.name.includes('KEY') || v.name.includes('TOKEN')
      ? v.value.slice(0, 18) + '***' + ` (len=${v.value.length})`
      : v.value.slice(0, 40);
    console.log(`  ${v.id} | ${v.name} = ${masked}`);
  }
}
main().catch(e => { console.error('ERR:', e.message); process.exit(1); });
