// MEC-21 baseline DB verification (Team 03 scope)
require('dotenv').config({ path: '/home/z/my-project/.env', override: true });
const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient({ log: [] });

async function main() {
  const tables = await p.$queryRawUnsafe("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1");
  console.log('TABLES:', tables.map(t => t.tablename).join(', '));

  const rls = await p.$queryRawUnsafe("SELECT c.relname, c.relrowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY 1");
  console.log('RLS_ENABLED:', rls.map(r => `${r.relname}=${r.relrowsecurity}`).join(', '));

  const counts = await p.$queryRawUnsafe('SELECT (SELECT count(*)::int FROM "Product") AS products, (SELECT count(*)::int FROM "ChainLink") AS chainlinks, (SELECT count(*)::int FROM "Order") AS orders, (SELECT count(*)::int FROM "WalletTx") AS wallet_txs, (SELECT count(*)::int FROM "Wallet") AS wallets, (SELECT count(*)::int FROM "Attempt") AS attempts, (SELECT count(*)::int FROM "GeoPrice") AS geoprices');
  console.log('COUNTS:', JSON.stringify(counts[0]));

  // anon role grants in public schema (PostgREST lockdown check)
  const grants = await p.$queryRawUnsafe("SELECT table_name, privilege_type FROM information_schema.role_table_grants WHERE grantee='anon' AND table_schema='public' LIMIT 20");
  console.log('ANON_GRANTS:', grants.length === 0 ? 'NONE (locked down) ✓' : JSON.stringify(grants));

  // indexes
  const idx = await p.$queryRawUnsafe("SELECT indexname FROM pg_indexes WHERE schemaname='public' ORDER BY 1");
  console.log('INDEXES:', idx.map(i => i.indexname).join(', '));

  await p.$disconnect();
}
main().catch(e => { console.error('DB ERROR:', e.message.slice(0, 300)); process.exit(1); });
