// MEC-21-E — Product/Business readiness analytics (READ-ONLY DB queries)
// Margin analysis per region, order status distribution, delivery SLA,
// product data quality, wallet aggregate mechanics, sync log cadence/float.
require('dotenv').config({ path: '/home/z/my-project/.env', override: true });
const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient({ log: [] });

const SAR_PEG = 3.75; // format.ts SAR_PEG
const MARGIN_CAP = 0.9; // format.ts MARGIN_CAP
const r2 = (x) => Math.round(x * 100) / 100;

async function main() {
  // ---------- 1. MARGIN ANALYSIS (37 products × regions, via best active in-stock chain) ----------
  const products = await p.product.findMany({
    where: { active: true },
    include: {
      prices: true,
      chains: { where: { active: true }, include: { supplier: true }, orderBy: { priority: 'asc' } },
    },
    orderBy: { name: 'asc' },
  });

  const famAgg = {}; // family -> {n, marginPctYE:[], marginUsdYE:[], ...}
  const perProduct = [];
  let guardViolations = 0, noRoutableChain = 0;
  for (const prod of products) {
    const inStockChains = prod.chains.filter((c) => c.stock === null || c.stock > 0);
    const bestCost = inStockChains.length ? Math.min(...inStockChains.map((c) => c.costUsd)) : null;
    const anyCost = prod.chains.length ? Math.min(...prod.chains.map((c) => c.costUsd)) : null;
    const row = { slug: prod.slug, name: prod.name, family: prod.family, chains: prod.chains.length, inStock: inStockChains.length, bestCost, anyCost, regions: {} };
    for (const g of prod.prices) {
      const amountUsd = g.region === 'SA' ? r2(g.price / SAR_PEG) : g.price;
      const cost = bestCost ?? anyCost;
      const marginUsd = cost == null ? null : r2(amountUsd - cost);
      const marginPct = cost == null || amountUsd === 0 ? null : r2(((amountUsd - cost) / amountUsd) * 100);
      row.regions[g.region] = { price: g.price, cur: g.currency, amountUsd, cost, marginUsd, marginPct, routable: inStockChains.length > 0 && cost != null && cost <= MARGIN_CAP * amountUsd };
      if (g.region === 'YE' && cost != null && inStockChains.length > 0 && cost > MARGIN_CAP * amountUsd) guardViolations++;
    }
    if (!inStockChains.length) noRoutableChain++;
    perProduct.push(row);
    const f = (famAgg[prod.family] ??= { n: 0, marginPctYE: [], marginUsdYE: [], marginPctSA: [], routableYE: 0, guardViolYE: 0 });
    f.n++;
    const ye = row.regions.YE, sa = row.regions.SA;
    if (ye && ye.cost != null && row.inStock > 0) { f.marginPctYE.push(ye.marginPct); f.marginUsdYE.push(ye.marginUsd); if (ye.cost <= MARGIN_CAP * ye.amountUsd) f.routableYE++; else f.guardViolYE++; }
    if (sa && sa.cost != null && row.inStock > 0) f.marginPctSA.push(sa.marginPct);
  }
  const avg = (a) => (a.length ? r2(a.reduce((x, y) => x + y, 0) / a.length) : null);
  console.log('=== MARGIN BY FAMILY (YE USD retail; best in-stock chain cost) ===');
  for (const [fam, f] of Object.entries(famAgg)) {
    console.log(`${fam} | n=${f.n} | avgMargin% YE=${avg(f.marginPctYE)} SA=${avg(f.marginPctSA)} | avgMargin$ YE=${avg(f.marginUsdYE)} | routableYE=${f.routableYE}/${f.marginPctYE.length}${f.guardViolYE ? ` | GUARD-VIOLATIONS=${f.guardViolYE}` : ''}`);
  }
  const allYE = perProduct.flatMap((r) => (r.regions.YE && r.regions.YE.cost != null && r.inStock > 0 ? [r.regions.YE.marginPct] : []));
  const allSA = perProduct.flatMap((r) => (r.regions.SA && r.regions.SA.cost != null && r.inStock > 0 ? [r.regions.SA.marginPct] : []));
  console.log(`OVERALL avg margin% (in-stock, best chain): YE=${avg(allYE)} | SA=${avg(allSA)} | products with NO routable in-stock chain=${noRoutableChain} | YE guard violations=${guardViolations}`);
  const best = [...perProduct].filter(r => r.regions.YE?.cost != null && r.inStock > 0).sort((a, b) => b.regions.YE.marginPct - a.regions.YE.marginPct);
  console.log('TOP 5 margin% (YE):', best.slice(0, 5).map(r => `${r.slug} ${r.regions.YE.marginPct}%`).join(' | '));
  console.log('BOTTOM 5 margin% (YE):', best.slice(-5).map(r => `${r.slug} ${r.regions.YE.marginPct}%`).join(' | '));
  const negative = perProduct.filter(r => r.regions.YE?.cost != null && r.regions.YE.marginUsd < 0);
  console.log('NEGATIVE-margin products (YE, any chain incl OOS):', negative.map(r => `${r.slug} (${r.regions.YE.marginUsd}$)`).join(', ') || 'none');

  // ---------- 2. ORDER STATUS DISTRIBUTION ----------
  const byStatus = await p.$queryRawUnsafe('SELECT status, count(*)::int AS n FROM "Order" GROUP BY status ORDER BY n DESC');
  console.log('\n=== ORDER STATUS DISTRIBUTION ===');
  for (const s of byStatus) console.log(`${s.status}: ${s.n}`);
  const byRail = await p.$queryRawUnsafe('SELECT rail, status, count(*)::int AS n FROM "Order" GROUP BY rail, status ORDER BY rail, status');
  console.log('BY RAIL×STATUS:', byRail.map(r => `${r.rail}/${r.status}=${r.n}`).join(' | '));
  const oldestPending = await p.order.findFirst({ where: { status: 'pending_payment' }, orderBy: { createdAt: 'asc' }, select: { publicId: true, createdAt: true } });
  const totalOrders = await p.order.count();
  console.log(`total=${totalOrders} | oldest pending_payment: ${oldestPending ? oldestPending.createdAt.toISOString() : 'none'}`);

  // ---------- 3. DELIVERY SLA (delivered orders: createdAt → deliveredAt / updatedAt) ----------
  const delivered = await p.order.findMany({ where: { status: 'delivered' }, select: { publicId: true, rail: true, createdAt: true, updatedAt: true, deliveredAt: true } });
  const dt = delivered.map(o => ({ id: o.publicId, rail: o.rail, dSec: o.deliveredAt ? (o.deliveredAt - o.createdAt) / 1000 : null, uSec: (o.updatedAt - o.createdAt) / 1000 }));
  const nums = dt.filter(x => x.dSec != null).map(x => x.dSec).sort((a, b) => a - b);
  const med = nums.length ? nums[Math.floor(nums.length / 2)] : null;
  console.log('\n=== DELIVERY SLA (delivered orders) ===');
  console.log(`n=${delivered.length} | createdAt→deliveredAt sec: min=${nums.length ? r2(nums[0]) : '-'} med=${med != null ? r2(med) : '-'} avg=${nums.length ? r2(nums.reduce((a, b) => a + b, 0) / nums.length) : '-'} max=${nums.length ? r2(nums[nums.length - 1]) : '-'} | over180s=${nums.filter(x => x > 180).length}`);
  console.log('null deliveredAt count:', delivered.filter(o => !o.deliveredAt).length);
  console.log('sample (5):', dt.slice(0, 5).map(x => `${x.id} ${x.rail} ${x.dSec ?? 'null'}s`).join(' | '));

  // ---------- 4. PRODUCT DATA QUALITY ----------
  console.log('\n=== PRODUCT DATA QUALITY ===');
  console.log(`active products=${products.length}`);
  const missNameEn = products.filter(x => !x.nameEn).length;
  const missOfficial = products.filter(x => x.officialUsd == null).length;
  const missKind = products.filter(x => !x.deliveryKind).length;
  console.log(`missing nameEn=${missNameEn} | missing officialUsd=${missOfficial} | missing deliveryKind=${missKind}`);
  const noImages = 'NO image/description columns in Product schema (catalog is text-only by design)';
  console.log(noImages);
  const regionGaps = [];
  for (const prod of products) {
    const rs = new Set(prod.prices.map(g => g.region));
    for (const want of ['SA', 'YE', 'WW']) if (!rs.has(want)) regionGaps.push(`${prod.slug}:${want}`);
    for (const g of prod.prices) if (!(g.price > 0)) regionGaps.push(`${prod.slug}:${g.region}=PRICE<=0`);
  }
  console.log('GeoPrice region gaps / non-positive prices:', regionGaps.join(', ') || 'NONE (37×3 complete)');
  const psLinks = await p.chainLink.findMany({ where: { active: true, supplier: { code: 'ps' } }, select: { externalId: true, costUsd: true, stock: true } });
  const psNoExt = psLinks.filter(l => !l.externalId).length;
  console.log(`ps chain links=${psLinks.length} | MISSING externalId (live-purchase blocker)=${psNoExt}`);
  const badCost = await p.chainLink.count({ where: { costUsd: { not: { gt: 0 } } } });
  console.log(`chain links with cost<=0: ${badCost}`);
  const oosProducts = perProduct.filter(r => r.inStock === 0);
  console.log('fully-OOS products:', oosProducts.map(r => r.slug).join(', ') || 'none');

  // ---------- 5. WAITLIST ----------
  const wlRaw = await p.$queryRawUnsafe('SELECT w."productId", p.slug, count(*)::int AS n FROM "Waitlist" w JOIN "Product" p ON p.id = w."productId" GROUP BY w."productId", p.slug ORDER BY n DESC');
  const wlProducts = wlRaw.map(w => ({ name: w.slug, n: w.n }));
  console.log('\n=== WAITLIST ===');
  console.log(`total rows=${await p.waitlist.count()} | by product: ${wlProducts.map(w => `${w.name}=${w.n}`).join(', ') || 'empty'}`);

  // ---------- 6. WALLET AGGREGATE MECHANICS (money-in/out, ledger-wide) ----------
  const txByType = await p.$queryRawUnsafe('SELECT type, count(*)::int AS n, ROUND(SUM(amount)::numeric, 2)::float AS sum FROM "WalletTx" GROUP BY type ORDER BY type');
  console.log('\n=== WALLET LEDGER (aggregate, all-time sandbox) ===');
  let liability = 0;
  for (const t of txByType) { const s = r2(t.sum ?? 0); liability += s; console.log(`${t.type}: n=${t.n} sum=$${s}`); }
  console.log(`NET wallet liability (sum all tx)=$${r2(liability)} | wallets=${await p.wallet.count()}`);

  // ---------- 7. SYNC LOG: cadence + ProdSeller float evidence ----------
  const syncs = await p.syncLog.findMany({ orderBy: { createdAt: 'desc' }, take: 10 });
  const total = await p.syncLog.count();
  const first = await p.syncLog.findFirst({ orderBy: { createdAt: 'asc' } });
  console.log('\n=== SYNC LOG (manual admin syncs) ===');
  console.log(`total syncs=${total} | span: ${first ? first.createdAt.toISOString() : '-'} → ${syncs[0]?.createdAt.toISOString()}`);
  for (const s of syncs.slice(0, 6)) console.log(`${s.createdAt.toISOString()} ok=${s.ok} seen=${s.productsSeen} matched=${s.matched} changed=${s.changed} inStock=${s.inStockNow} balance=$${s.balanceUsd}`);
  const gaps = [];
  for (let i = 0; i < syncs.length - 1; i++) gaps.push(r2((syncs[i].createdAt - syncs[i + 1].createdAt) / 60000));
  console.log('gaps between recent syncs (min):', gaps.join(', '));

  await p.$disconnect();
}
function allYeSafe(a) { return a; }
main().catch(e => { console.error('DB ERROR:', e.message.slice(0, 300)); process.exit(1); });
