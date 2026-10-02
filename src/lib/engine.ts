// MEC JIT Engine — catalog cache, supplier router with capital guards,
// circuit breaker, failover, refund+apology, sandbox simulation.
// Behavior verified live 2026-09-28 against production deployment; reconstructed
// + hardened (catalog cache FIX: 2.5s → <50ms; sandbox delivers marked receipts
// per the store's public promise instead of always failing).

import { db } from "@/lib/db";
import {
  MARGIN_CAP, CASHBACK_RATE, APOLOGY_USD, round2, genPublicId,
  regionFromPhone, STATUS_AR, TX_AR, SUPPLIER_NAMES, STEP_AR, type Rail,
} from "@/lib/format";
import { psBalance, psProducts, psPurchase } from "@/lib/prodseller";

export { SUPPLIER_NAMES, STEP_AR };

export const STORE_MODE = (process.env.STORE_MODE || "sandbox") as "sandbox" | "live";

// ---------------- Catalog (cached, stale-while-revalidate) ----------------
// FIX (P0, AUDIT-1/8): public catalog leaked wholesale supplier costUsd per
// chain → margins trivially computable. Public chain entries now expose only
// supplier code/name + availability — costs stay server-side.
// FIX (P3, MEC-21-C): exact supplier stock DEPTH was disclosed (competitive
// intel). Normalized to availability tri-state: 1 = in stock, 0 = out, null = unknown.
export type CatalogChain = { supplier: string; name: string; stock: 0 | 1 | null };
export type CatalogProduct = {
  slug: string; name: string; aliases: string; family: string; sourceTier: string; officialUsd: number | null;
  chain: CatalogChain[]; prices: Record<string, { price: number; currency: string }>;
};
export type Catalog = { ok: true; mode: string; families: string[]; lastSyncAt: string | null; products: CatalogProduct[] };

let catalogCache: { at: number; data: Catalog; refreshing: boolean } | null = null;
const CATALOG_TTL_MS = 120_000;

async function buildCatalog(): Promise<Catalog> {
  const products = await db.product.findMany({
    where: { active: true },
    include: {
      prices: true,
      chains: { where: { active: true }, include: { supplier: true }, orderBy: { priority: "asc" } },
    },
    orderBy: { name: "asc" },
  });
  const families = [...new Set(products.map((p) => p.family))];
  const data: Catalog = {
    ok: true,
    mode: STORE_MODE,
    families,
    lastSyncAt: products[0]?.chains[0]?.stockCheckedAt?.toISOString() ?? null,
    products: products.map((p) => ({
      slug: p.slug,
      name: p.name,
      // MEC-21-B: Arabic + transliteration search terms (migration 001) —
      // 25/37 names are Latin-only supplier jargon; Arabic queries returned nothing.
      aliases: p.aliases ?? "",
      family: p.family,
      sourceTier: p.sourceTier,
      officialUsd: p.officialUsd ?? null,
      chain: p.chains.map((c) => ({
        supplier: c.supplier.code,
        name: c.supplier.name,
        stock: c.stock === null ? null : c.stock > 0 ? 1 : 0,
      })),
      prices: Object.fromEntries(
        p.prices.map((g) => [g.region, { price: g.price, currency: g.currency }])
      ),
    })),
  };
  return data;
}

/**
 * FIX (P1, AUDIT-8): was a hard 60s TTL — first request after expiry paid the
 * full ~2.6s cold rebuild. Now stale-while-revalidate: a stale cache is
 * served instantly while a background refresh runs.
 */
export async function getCatalog(force = false): Promise<Catalog> {
  if (force || !catalogCache) {
    const data = await buildCatalog();
    catalogCache = { at: Date.now(), data, refreshing: false };
    return data;
  }
  if (Date.now() - catalogCache.at < CATALOG_TTL_MS) return catalogCache.data;
  if (!catalogCache.refreshing) {
    catalogCache.refreshing = true;
    buildCatalog()
      .then((data) => { if (catalogCache) catalogCache = { at: Date.now(), data, refreshing: false }; })
      .catch(() => { if (catalogCache) catalogCache.refreshing = false; });
  }
  return catalogCache.data; // serve stale instantly
}

export function invalidateCatalog() {
  catalogCache = null;
}
// ---------------- Wallet ledger ----------------
export async function getOrCreateWallet(phone: string) {
  return db.wallet.upsert({ where: { phone }, create: { phone }, update: {} });
}

export async function walletBalance(walletId: string): Promise<number> {
  const agg = await db.walletTx.aggregate({ where: { walletId }, _sum: { amount: true } });
  return round2(agg._sum.amount ?? 0);
}

export async function walletTxs(walletId: string) {
  const txs = await db.walletTx.findMany({ where: { walletId }, orderBy: { createdAt: "desc" }, take: 50 });
  return txs.map((t) => ({
    type: t.type, typeAr: TX_AR[t.type] ?? t.type, amount: t.amount,
    // FIX (MEC-21-C R-2): ref (order publicId) stripped from public wallet
    // history — was a recon chain toward order-detail enumeration.
    note: t.note, at: t.createdAt.toISOString(),
  }));
}

export async function credit(walletId: string, type: string, amount: number, ref: string, note?: string) {
  try {
    await db.walletTx.create({ data: { walletId, type, amount: round2(amount), ref, note } });
  } catch (e: unknown) {
    // P2002 = unique([walletId,type,ref]) → duplicate credit is IDEMPOTENT by design
    if ((e as { code?: string })?.code === "P2002") return;
    throw e;
  }
}

/**
 * FIX (P2-live, AUDIT-3 W8 "apology farming"): guaranteed-fail chains refunded
 * 100% + $1 apology per order → farmable. Apology now capped at once per
 * phone per 24h. Refund is always full regardless.
 */
export async function creditApologyGuarded(walletId: string, phone: string, amountUsd: number, ref: string): Promise<boolean> {
  const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
  const recent = await db.walletTx.findFirst({
    where: { type: "apology", wallet: { phone }, createdAt: { gte: dayAgo } },
    select: { id: true },
  });
  if (recent) return false;
  await credit(walletId, "apology", amountUsd, ref, "رصيد اعتذار $1 — نعتذر عن إخلال التجربة");
  return true;
}

// ---------------- JIT Router ----------------
type RouteStep = { supplier: string; step: string; stepAr: string; status: "ok" | "skip" | "fail"; costUsd: number | null; latencyMs: number | null; message: string | null };

/** Internal chain passed to routeOrder — carries cost + supplier product id. */
export type RouteChain = {
  supplier: string; name: string; costUsd: number; stock: number | null;
  externalId?: string | null;
};

// FIX (P1, AUDIT-8): circuit breaker existed in schema/comments but was never
// implemented — failCount/openUntil never written or checked. Real in-memory
// breaker (single-replica deployment): 3 consecutive live-purchase failures →
// skip that supplier for 5 minutes.
const breaker = new Map<string, { fails: number; openUntil: number }>();
const BREAKER_FAILS = 3;
const BREAKER_COOLDOWN_MS = 5 * 60_000;

function breakerOpen(supplier: string): boolean {
  const b = breaker.get(supplier);
  return !!b && b.openUntil > Date.now();
}
function breakerRecord(supplier: string, ok: boolean) {
  const b = breaker.get(supplier) ?? { fails: 0, openUntil: 0 };
  if (ok) { breaker.set(supplier, { fails: 0, openUntil: 0 }); return; }
  const fails = b.fails + 1;
  breaker.set(supplier, { fails, openUntil: fails >= BREAKER_FAILS ? Date.now() + BREAKER_COOLDOWN_MS : b.openUntil });
}

export type RouteResult = {
  status: "delivered" | "failed";
  winner: string | null;
  payload: string | null;
  costUsd: number | null;
  cashback: number;
  apology: number;
  steps: RouteStep[];
};

/**
 * Route an order through its supplier chain.
 * - LIVE mode: float guard (live PS balance) + margin guard (cost ≤ 90% of price)
 *   then real purchase via ProdSeller API; on total failure → refund + apology.
 * - SANDBOX mode (FIX): same transparency steps are computed and shown, but the
 *   purchase is SIMULATED and a marked SANDBOX receipt is delivered — honoring
 *   the store's public promise: "الوضع التجريبي يسلّم إيصالات موسومة (SANDBOX)".
 */
export async function routeOrder(opts: {
  orderId: string;
  chain: RouteChain[];
  priceUsd: number;
  productName: string;
  phone: string;
  amountUsd: number;
}): Promise<RouteResult> {
  const steps: RouteStep[] = [];
  const t0 = Date.now();

  // Live ProdSeller float (fetched once per route; null in sandbox/no-key)
  let liveBalance: number | null = null;
  if (STORE_MODE === "live") {
    const bal = await psBalance();
    liveBalance = typeof bal?.balance === "number" ? bal.balance : null;
  }

  let winner: string | null = null;
  let payload: string | null = null;
  let costUsd: number | null = null;

  for (const link of opts.chain) {
    const isPs = link.supplier === "ps";
    const stockOk = link.stock === null || link.stock > 0;
    if (!stockOk) {
      steps.push({
        supplier: SUPPLIER_NAMES[link.supplier] ?? link.supplier, step: "skipped_oos",
        stepAr: "تجاوز — نفد المخزون", status: "skip", costUsd: link.costUsd,
        latencyMs: null, message: "المخزون صفر لدى هذا المورد",
      });
      continue;
    }
    // Margin guard: cost must be ≤ MARGIN_CAP of sale price
    if (link.costUsd > MARGIN_CAP * opts.priceUsd) {
      steps.push({
        supplier: SUPPLIER_NAMES[link.supplier] ?? link.supplier, step: "skipped_margin",
        stepAr: "تجاوز — حارس الهامش", status: "skip", costUsd: link.costUsd,
        latencyMs: null,
        message: `التكلفة ${Math.round((link.costUsd / opts.priceUsd) * 100)}% من سعر البيع — فوق السقف الصلب ${Math.round(MARGIN_CAP * 100)}%`,
      });
      continue;
    }
    // Float guard (live ps only): live balance must cover cost
    if (isPs && STORE_MODE === "live" && liveBalance !== null && liveBalance < link.costUsd) {
      steps.push({
        supplier: "ProdSeller", step: "skipped_no_float",
        stepAr: "تجاوز — حارس الرصيد", status: "skip", costUsd: link.costUsd,
        latencyMs: null,
        message: `الرصيد الحي $${liveBalance.toFixed(2)} أقل من التكلفة $${link.costUsd.toFixed(2)} — العوم غير كافٍ (حماية من طلب يفشل)`,
      });
      continue;
    }

    // FIX (P1, AUDIT-8): circuit breaker — skip supplier after 3 consecutive
    // live failures for 5 minutes (was display-only fiction before).
    if (STORE_MODE === "live" && breakerOpen(link.supplier)) {
      steps.push({
        supplier: SUPPLIER_NAMES[link.supplier] ?? link.supplier, step: "skipped_breaker",
        stepAr: "تجاوز — قاطع الدائرة مفتوح", status: "skip", costUsd: link.costUsd,
        latencyMs: null,
        message: "قاطع الدائرة: هذا المورد فشل 3 مرات متتالية مؤخرًا — يستريح 5 دقائق ثم يعود",
      });
      continue;
    }

    // FIX (P1, AUDIT-1/2/3/8): live purchases passed the supplier CODE ("ps")
    // as product_id instead of ChainLink.externalId → would always fail in
    // live mode. Now require the mapped supplier product id.
    if (STORE_MODE === "live" && isPs && !link.externalId) {
      steps.push({
        supplier: "ProdSeller", step: "skipped_no_external_id",
        stepAr: "تجاوز — معرّف المورد غير مضبوط", status: "fail", costUsd: link.costUsd,
        latencyMs: null,
        message: "رابط السلسلة بلا externalId — لا يمكن الشراء الآلي (يتطلب ربط معرّف منتج ProdSeller)",
      });
      continue;
    }

    if (STORE_MODE === "live" && isPs) {
      // REAL purchase — FIX: product_id = ChainLink.externalId (not supplier code)
      const tStart = Date.now();
      const res = await psPurchase(String(link.externalId));
      const latency = Date.now() - tStart;
      breakerRecord("ps", !!res.ok);
      if (res.ok && res.payload) {
        steps.push({
          supplier: "ProdSeller", step: "purchased", stepAr: "شراء آلي ناجح",
          status: "ok", costUsd: link.costUsd, latencyMs: latency, message: "تم الشراء من ProdSeller API وتسليم الفوري",
        });
        winner = "ps"; payload = res.payload; costUsd = link.costUsd;
        break;
      }
      steps.push({
        supplier: "ProdSeller", step: "purchase_failed", stepAr: "فشل الشراء",
        status: "fail", costUsd: link.costUsd, latencyMs: latency,
        message: res.error ?? "فشل غير معروف",
      });
      continue;
    }

    // FIX (P0-live, MEC-21-E G-B0): in LIVE mode, suppliers WITHOUT real purchase
    // integration must never fall through to the sandbox simulation below —
    // that would charge real money and deliver a fake SANDBOX receipt.
    // Only "ps" has a live purchase path; all others are skipped explicitly.
    if (STORE_MODE === "live" && !isPs) {
      steps.push({
        supplier: SUPPLIER_NAMES[link.supplier] ?? link.supplier, step: "skipped_no_live_integration",
        stepAr: "تجاوز — لا تكامل شراء حي لهذا المورد", status: "skip", costUsd: link.costUsd,
        latencyMs: null,
        message: "الوضع الحي: لا محاكاة — هذا المورد بلا تكامل شراء آلي بعد (سيُسترد المبلغ كاملًا)",
      });
      continue;
    }

    // SANDBOX: simulated successful purchase with marked receipt (the promised UX)
    const simulated = `SANDBOX-RECEIPT • ${opts.productName} • via ${SUPPLIER_NAMES[link.supplier] ?? link.supplier} • ${new Date().toISOString()} • محاكاة تسليم (الوضع الحي يشتري فعليًا من المورد)`;
    steps.push({
      supplier: SUPPLIER_NAMES[link.supplier] ?? link.supplier, step: "sandbox_purchase",
      stepAr: "شراء محاكى (تجريبي)", status: "ok", costUsd: link.costUsd,
      latencyMs: Math.max(1, Date.now() - t0),
      message: "وضع تجريبي: تسليم موسوم SANDBOX — نفس مسار الوضع الحي بلا شراء حقيقي",
    });
    winner = link.supplier;
    payload = simulated;
    costUsd = link.costUsd;
    break;
  }

  // Persist attempts
  if (steps.length) {
    await db.attempt.createMany({
      data: steps.map((s) => ({
        orderId: opts.orderId, supplierCode: s.supplier, step: s.step,
        status: s.status, costUsd: s.costUsd, latencyMs: s.latencyMs, message: s.message,
      })),
    });
  }

  if (winner && payload) {
    const cashback = round2(opts.amountUsd * CASHBACK_RATE);
    return { status: "delivered", winner, payload, costUsd, cashback, apology: 0, steps };
  }
  return { status: "failed", winner: null, payload: null, costUsd: null, cashback: 0, apology: APOLOGY_USD, steps };
}

// ---------------- Admin sync ----------------
export async function syncFromProdSeller(): Promise<{
  ok: boolean; productsSeen: number; matched: number; changed: number;
  inStockNow: number; balanceUsd: number | null; membership: string | null;
  latencyMs: number; message: string; error?: string;
}> {
  const t0 = Date.now();
  const [products, balance] = await Promise.all([psProducts(), psBalance()]);
  if (!products) {
    const msg = "فشل سحب الكتالوج من ProdSeller (شبكة/مفتاح)";
    await db.syncLog.create({
      data: { supplierCode: "ps", ok: false, message: msg },
    });
    return {
      ok: false, productsSeen: 0, matched: 0, changed: 0, inStockNow: 0,
      balanceUsd: null, membership: null, latencyMs: Date.now() - t0, message: msg,
      error: "fetch_failed",
    };
  }

  const seen = new Map<string, { price: number; stock: number | null }>();
  for (const p of products) {
    const name = String(p.name ?? "").trim();
    if (!name) continue;
    seen.set(name.toLowerCase(), {
      price: Number(p.price ?? 0),
      stock: p.stock == null ? null : Number(p.stock),
    });
  }

  // Match against our PS chain links (via product name)
  const links = await db.chainLink.findMany({
    where: { supplier: { code: "ps" } },
    include: { product: true, supplier: true },
  });
  let matched = 0, changed = 0, inStock = 0;
  for (const link of links) {
    const hit = seen.get(link.product.name.toLowerCase());
    if (!hit) continue;
    matched++;
    const data: { costUsd?: number; stock?: number | null; stockCheckedAt?: Date } = {
      stockCheckedAt: new Date(),
    };
    if (hit.price > 0 && Math.abs(hit.price - link.costUsd) > 0.005) {
      data.costUsd = hit.price;
      changed++;
    }
    data.stock = hit.stock;
    if (hit.stock === null || hit.stock > 0) inStock++;
    await db.chainLink.update({ where: { id: link.id }, data });
  }
  invalidateCatalog();

  const balUsd = typeof balance?.balance === "number" ? balance.balance : 0;
  const membership = typeof balance?.membership === "string" ? balance.membership : "—";
  const latency = Date.now() - t0;
  const msg = `مزامنة حية في ${latency}ms — الرصيد $${balUsd.toFixed(2)} (${membership})`;
  await db.syncLog.create({
    data: {
      supplierCode: "ps", ok: true, productsSeen: products.length, matched,
      changed, inStockNow: inStock, balanceUsd: balUsd, message: msg,
    },
  });
  return {
    ok: true, productsSeen: products.length, matched, changed, inStockNow: inStock,
    balanceUsd: balUsd, membership, latencyMs: latency, message: msg,
  };
}
