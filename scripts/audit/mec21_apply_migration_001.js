// MEC-21: apply versioned migration 20260928130000_product_aliases to Supabase
// Idempotent (IF NOT EXISTS + UPDATE-by-slug), additive-only, reversible.
require('dotenv').config({ path: '/home/z/my-project/.env', override: true });
const fs = require('fs');
const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient({ log: [] });

async function main() {
  const sql = fs.readFileSync('/home/z/my-project/prisma/migrations/20260928130000_product_aliases/migration.sql', 'utf8');
  // Split on ';' at line ends; strip comment lines; drop empty chunks
  const statements = sql
    .split(/;\s*\n/)
    .map(s => s.split('\n').filter(line => !line.trim().startsWith('--')).join('\n').trim())
    .filter(s => s.length > 0);

  console.log(`Applying ${statements.length} statements...`);
  for (const stmt of statements) {
    const first = stmt.split('\n')[0].slice(0, 60);
    await p.$executeRawUnsafe(stmt);
    console.log('  OK:', first, '...');
  }

  // Verify
  const col = await p.$queryRawUnsafe(`SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name='Product' AND column_name='aliases'`);
  console.log('COLUMN:', JSON.stringify(col[0]));
  const filled = await p.$queryRawUnsafe(`SELECT count(*)::int AS n FROM "Product" WHERE aliases <> ''`);
  const total = await p.$queryRawUnsafe(`SELECT count(*)::int AS n FROM "Product"`);
  console.log(`BACKFILL: ${filled[0].n}/${total[0].n} products have aliases`);
  const sample = await p.$queryRawUnsafe(`SELECT slug, aliases FROM "Product" WHERE slug IN ('chatgpt-plus-1-month','turgame-12-netflix-20-000-cop')`);
  sample.forEach(s => console.log('  ', s.slug, '→', s.aliases.slice(0, 50)));
  await p.$disconnect();
}
main().catch(e => { console.error('MIGRATION FAILED:', e.message.slice(0, 300)); process.exit(1); });
