// Railway v2: read variables (bare) → fix DATABASE_URL + rotate ADMIN_TOKEN (skipDeploys)
require('dotenv').config({ path: '/home/z/my-project/.env', override: true });
const crypto = require('crypto');

const ENV_ID = process.env.RAILWAY_ENVIRONMENT_ID;
const PROJ_ID = process.env.RAILWAY_PROJECT_ID;
const SVC_ID = process.env.RAILWAY_SERVICE_ID;

async function gql(query, variables) {
  const res = await fetch('https://backboard.railway.com/graphql/v2', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.RAILWAY_TOKEN}` },
    body: JSON.stringify({ query, variables }),
  });
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors).slice(0, 400));
  return data.data;
}

async function main() {
  const mode = process.argv[2] || 'read';
  const d = await gql(
    `query vars($environmentId: String!, $projectId: String!, $serviceId: String!) {
      variables(environmentId: $environmentId, projectId: $projectId, serviceId: $serviceId, unrendered: true)
    }`,
    { environmentId: ENV_ID, projectId: PROJ_ID, serviceId: SVC_ID }
  );
  const raw = d.variables;
  let vars = {};
  if (typeof raw === 'string') {
    try { vars = JSON.parse(raw); } catch { console.log('raw is string, first 100:', raw.slice(0, 100)); return; }
  } else if (raw && typeof raw === 'object') {
    vars = raw;
  }
  const names = Object.keys(vars);
  console.log(`total vars: ${names.length}`);

  const dbUrl = vars.DATABASE_URL;
  if (dbUrl) {
    const u = new URL(dbUrl);
    console.log(`DATABASE_URL: host=${u.hostname} port=${u.port} params=[${[...u.searchParams.keys()].join(',')}]`);
  } else {
    console.log('DATABASE_URL: NOT FOUND');
  }

  if (mode === 'fix') {
    if (dbUrl) {
      const u = new URL(dbUrl);
      u.searchParams.delete('pgbouncer');
      u.searchParams.set('connection_limit', '5');
      u.port = '5432';
      const newVal = u.toString().replace(/\?$/,'');
      await gql(
        `mutation up($environmentId: String!, $projectId: String!, $serviceId: String!, $name: String!, $value: String!, $skipDeploys: Boolean!) {
          variableUpsert(input: { environmentId: $environmentId, projectId: $projectId, serviceId: $serviceId, name: $name, value: $value, skipDeploys: $skipDeploys })
        }`,
        { environmentId: ENV_ID, projectId: PROJ_ID, serviceId: SVC_ID, name: 'DATABASE_URL', value: newVal, skipDeploys: true }
      );
      const c = new URL(newVal);
      console.log(`DATABASE_URL UPDATED -> port=${c.port} pgbouncer=${c.searchParams.get('pgbouncer')} connection_limit=${c.searchParams.get('connection_limit')} (skipDeploys=true)`);
    }

    const newToken = 'mec_' + crypto.randomBytes(24).toString('base64url');
    await gql(
      `mutation up($environmentId: String!, $projectId: String!, $serviceId: String!, $name: String!, $value: String!, $skipDeploys: Boolean!) {
        variableUpsert(input: { environmentId: $environmentId, projectId: $projectId, serviceId: $serviceId, name: $name, value: $value, skipDeploys: $skipDeploys })
      }`,
      { environmentId: ENV_ID, projectId: PROJ_ID, serviceId: SVC_ID, name: 'ADMIN_TOKEN', value: newToken, skipDeploys: true }
    );
    console.log(`ADMIN_TOKEN ROTATED (len=${newToken.length}, value saved to .env only)`);
    const fs = require('fs');
    const envPath = '/home/z/my-project/.env';
    const env = fs.readFileSync(envPath, 'utf8');
    const updated = env.replace(/^ADMIN_TOKEN=.*$/m, `ADMIN_TOKEN=${newToken}`);
    fs.writeFileSync(envPath, updated);
    console.log('local .env ADMIN_TOKEN updated');
  } else {
    console.log('(read-only — pass "fix" to apply)');
  }
}
main().catch(e => { console.error('ERR:', e.message); process.exit(1); });
