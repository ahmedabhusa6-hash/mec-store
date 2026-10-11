/**
 * MEC Intelligence Platform — aggregations over the LIVE Supabase domain
 * (rebuild v4, 2026-10-11). Same public shapes as the previous version, now
 * backed by PostgREST + SQL views (v_*) instead of a local SQLite snapshot.
 * Facts-only: raw_text never leaves this layer except to authenticated owner
 * views; public endpoints select explicit columns only.
 */
import { sbCount, sbGet, q } from "./supabase";

// ─── types (unchanged shapes + extensions) ───────────────────────────
export type LatestPrice = {
  channelId: number | null;
  username: string | null;
  title: string | null;
  kind: string;
  product: string;
  price: number | null;
  currency: string;
  unit: string | null;
  postedAt: string | null;
  ageHours: number | null;
};

export type ProductAgg = {
  product: string;
  bestPrice: number;
  bestSupplier: string;
  bestCurrency: string;
  bestUnit: string | null;
  minPrice: number;
  maxPrice: number;
  suppliers: number;
  observations: number;
  lastSeen: string | null;
};

export type SupplierAgg = {
  channelId: number;
  name: string;
  username: string | null;
  kind: string;
  isPrivate: boolean;
  observations: number;
  products: number;
  firstSeen: string | null;
  lastSeen: string | null;
  avgPriceUsd: number | null;
  signals: { warranty: number; payment: number; minOrder: number; replacement: number };
};

export type ChannelRow = {
  tgId: number;
  username: string | null;
  title: string | null;
  kind: string;
  relevance: string;
  joined: boolean;
  lastScanned: string | null;
  observations: number;
  products: number;
  lastPriceAt: string | null;
};

export type DiscoveryRow = {
  handle: string;
  seenIn: number | null;
  seenAt: string;
  status: string;
  kind: string;
  title: string | null;
  members: number | null;
  previewAt: string | null;
  source: string;
  approvedBy: string | null;
  approvedAt: string | null;
};

export type RunRow = {
  id: number;
  startedAt: string | null;
  finishedAt: string | null;
  runner: string | null;
  dispatchedBy: string | null;
  channelsScanned: number | null;
  newMessages: number | null;
  pricesAdded: number | null;
  newHandles: number | null;
  invitesFound: number | null;
  joinsOk: number | null;
  joinsPrivate: number | null;
  errors: string | null;
  durationS: number | null;
};

export type AlertRow = {
  id: number;
  severity: string;
  category: string;
  title: string;
  message: string | null;
  createdAt: string;
  readAt: string | null;
};

export type AuditRow = {
  id: number;
  actor: string;
  action: string;
  entity: string | null;
  entityId: string | null;
  details: string | null;
  ip: string | null;
  createdAt: string;
};

// ─── helpers ──────────────────────────────────────────────────────────
export function supplierLabel(username: string | null, title: string | null, channelId: number | null): string {
  return title || (username ? `@${username}` : channelId != null ? `#${channelId}` : "مصدر");
}

export function freshnessBucket(ageHours: number | null): "fresh" | "aging" | "stale" | "ancient" | "unknown" {
  if (ageHours == null) return "unknown";
  if (ageHours <= 24) return "fresh";
  if (ageHours <= 72) return "aging";
  if (ageHours <= 24 * 7) return "stale";
  return "ancient";
}

function ageHours(iso: string | null): number | null {
  if (!iso) return null;
  const ms = Date.now() - new Date(iso).getTime();
  return ms > 0 ? +(ms / 3_600_000).toFixed(1) : 0;
}

// ─── latest price per (channel × product) — from the SQL view ────────
type LpRow = {
  channel_id: number | null; username: string | null; title: string | null;
  product: string; price: number | null; currency: string; unit: string | null; posted_at: string | null;
};

export async function latestPrices(limit = 3000): Promise<LatestPrice[]> {
  const rows = await sbGet<LpRow[]>(
    `latest_prices?select=channel_id,username,title,product,price,currency,unit,posted_at&order=posted_at.desc&limit=${limit}`,
  );
  return rows.map((r) => ({
    channelId: r.channel_id,
    username: r.username,
    title: r.title,
    kind: r.username ? "channel" : "private",
    product: r.product,
    price: r.price,
    currency: r.currency,
    unit: r.unit,
    postedAt: r.posted_at,
    ageHours: ageHours(r.posted_at),
  }));
}

// ─── product aggregation (view + latest for best supplier) ────────────
type PsRow = {
  product: string; suppliers: number; observations: number;
  min_price: number | null; max_price: number | null; last_seen: string | null;
};

export async function productsAgg(): Promise<ProductAgg[]> {
  const [stats, latest] = await Promise.all([
    sbGet<PsRow[]>("v_product_stats?order=suppliers.desc,observations.desc&limit=2000"),
    latestPrices(),
  ]);
  // best (cheapest latest) supplier per product
  const best = new Map<string, LatestPrice>();
  for (const p of latest) {
    if (p.price == null) continue;
    const cur = best.get(p.product);
    if (!cur || p.price < (cur.price ?? Infinity)) best.set(p.product, p);
  }
  const out: ProductAgg[] = [];
  for (const s of stats) {
    if (!s.product || s.product.trim().length < 2) continue;
    const b = best.get(s.product);
    out.push({
      product: s.product,
      bestPrice: b?.price ?? s.min_price ?? 0,
      bestSupplier: b ? supplierLabel(b.username, b.title, b.channelId) : "—",
      bestCurrency: b?.currency ?? "USD",
      bestUnit: b?.unit ?? null,
      minPrice: s.min_price ?? 0,
      maxPrice: s.max_price ?? 0,
      suppliers: s.suppliers,
      observations: s.observations,
      lastSeen: s.last_seen,
    });
  }
  return out;
}

// ─── supplier aggregation (view) ──────────────────────────────────────
type SsRow = {
  channel_id: number; username: string | null; title: string | null; kind: string;
  products: number; observations: number; first_seen: string | null; last_seen: string | null;
  avg_price_usd: number | null; warranty: number; payment: number; min_order: number;
};

export async function suppliersAgg(): Promise<SupplierAgg[]> {
  const rows = await sbGet<SsRow[]>("v_supplier_stats?order=observations.desc&limit=2000");
  return rows.map((r) => ({
    channelId: r.channel_id,
    name: supplierLabel(r.username, r.title, r.channel_id),
    username: r.username,
    kind: r.kind,
    isPrivate: !r.username,
    observations: r.observations,
    products: r.products,
    firstSeen: r.first_seen,
    lastSeen: r.last_seen,
    avgPriceUsd: r.avg_price_usd,
    signals: {
      warranty: r.warranty,
      payment: r.payment,
      minOrder: r.min_order,
      replacement: 0,
    },
  }));
}

// ─── channel inventory (view) ─────────────────────────────────────────
type CsRow = {
  tg_id: number; username: string | null; title: string | null; kind: string;
  relevance: string; joined: boolean; last_scanned: string | null;
  observations: number; products: number; last_price_at: string | null;
};

export async function channelsInventory(): Promise<ChannelRow[]> {
  const rows = await sbGet<CsRow[]>("v_channel_stats?order=joined.desc,tg_id.asc&limit=2000");
  return rows.map((r) => ({
    tgId: r.tg_id,
    username: r.username,
    title: r.title,
    kind: r.kind,
    relevance: r.relevance,
    joined: r.joined,
    lastScanned: r.last_scanned,
    observations: r.observations,
    products: r.products,
    lastPriceAt: r.last_price_at,
  }));
}

// ─── daily volume (view) ──────────────────────────────────────────────
export async function dailyVolume(days = 30): Promise<{ day: string; count: number }[]> {
  const rows = await sbGet<{ day: string; count: number }[]>(`v_daily_volume?order=day.desc&limit=${days}`);
  return rows.reverse();
}

// ─── product price trend ──────────────────────────────────────────────
export async function productTrend(
  product: string,
  days = 45,
): Promise<{ day: string; avg: number; min: number; max: number; n: number }[]> {
  const rows = await sbGet<{ posted_at: string; price: number }[]>(
    `price_observations?product=eq.${q(product)}&price=not.is.null&select=posted_at,price&order=posted_at.asc&limit=4000`,
  );
  const byDay = new Map<string, number[]>();
  for (const o of rows) {
    if (!o.posted_at) continue;
    const day = o.posted_at.slice(0, 10);
    (byDay.get(day) ?? byDay.set(day, []).get(day)!).push(o.price);
  }
  return [...byDay.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .slice(-days)
    .map(([day, prices]) => ({
      day,
      avg: +(prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(2),
      min: Math.min(...prices),
      max: Math.max(...prices),
      n: prices.length,
    }));
}

// ─── discoveries (+ approval pipeline) ────────────────────────────────
type DiscRaw = {
  handle: string; seen_in: number | null; seen_at: string; status: string; kind: string;
  title: string | null; members: number | null; preview_at: string | null; source: string;
  approved_by: string | null; approved_at: string | null;
};

export async function discoveriesData(): Promise<{
  total: number;
  byStatus: Record<string, number>;
  byKind: Record<string, number>;
  recent: DiscoveryRow[];
  awaiting: DiscoveryRow[];
}> {
  const [all, recent] = await Promise.all([
    sbGet<{ status: string; kind: string }[]>("discoveries?select=status,kind&limit=5000"),
    sbGet<DiscRaw[]>("discoveries?select=handle,seen_in,seen_at,status,kind,title,members,preview_at,source,approved_by,approved_at&order=seen_at.desc&limit=150"),
  ]);
  const byStatus: Record<string, number> = {};
  const byKind: Record<string, number> = {};
  for (const d of all) {
    byStatus[d.status] = (byStatus[d.status] ?? 0) + 1;
    byKind[d.kind] = (byKind[d.kind] ?? 0) + 1;
  }
  const mapRow = (d: DiscRaw): DiscoveryRow => ({
    handle: d.handle,
    seenIn: d.seen_in,
    seenAt: d.seen_at,
    status: d.status,
    kind: d.kind,
    title: d.title,
    members: d.members,
    previewAt: d.preview_at,
    source: d.source,
    approvedBy: d.approved_by,
    approvedAt: d.approved_at,
  });
  const recentRows = recent.map(mapRow);
  return {
    total: all.length,
    byStatus,
    byKind,
    recent: recentRows,
    awaiting: recentRows.filter((d) => d.status === "awaiting_approval"),
  };
}

// ─── runs ─────────────────────────────────────────────────────────────
type RunRaw = {
  id: number; started_at: string | null; finished_at: string | null; runner: string | null;
  channels_scanned: number | null; new_messages: number | null; prices_added: number | null;
  new_handles: number | null; invites_found: number | null; joins_ok: number | null;
  joins_private: number | null; errors: string | null; dispatched_by: string | null;
};

export async function runsData(limit = 40): Promise<RunRow[]> {
  const rows = await sbGet<RunRaw[]>(
    `runs?select=id,started_at,finished_at,runner,channels_scanned,new_messages,prices_added,new_handles,invites_found,joins_ok,joins_private,errors,dispatched_by&order=id.desc&limit=${limit}`,
  );
  return rows.map((r) => {
    let durationS: number | null = null;
    if (r.started_at && r.finished_at) {
      durationS = Math.round((new Date(r.finished_at).getTime() - new Date(r.started_at).getTime()) / 1000);
    }
    return {
      id: r.id,
      startedAt: r.started_at,
      finishedAt: r.finished_at,
      runner: r.runner,
      dispatchedBy: r.dispatched_by,
      channelsScanned: r.channels_scanned,
      newMessages: r.new_messages,
      pricesAdded: r.prices_added,
      newHandles: r.new_handles,
      invitesFound: r.invites_found,
      joinsOk: r.joins_ok,
      joinsPrivate: r.joins_private,
      errors: r.errors,
      durationS,
    };
  });
}

// ─── quality (computed freshness + coverage) ─────────────────────────
export type Quality = Awaited<ReturnType<typeof qualityData>>;

export async function qualityData() {
  const [latest, channels, volume] = await Promise.all([
    latestPrices(),
    channelsInventory(),
    dailyVolume(14),
  ]);
  const buckets = { fresh: 0, aging: 0, stale: 0, ancient: 0, unknown: 0 } as Record<string, number>;
  for (const p of latest) buckets[freshnessBucket(p.ageHours)]++;
  const now = Date.now();
  const scanAge = (iso: string | null) => (iso ? +(Math.max(0, now - new Date(iso).getTime()) / 3_600_000).toFixed(1) : null);
  const joinedChannels = channels.filter((c) => c.joined);
  const scanCoverage = {
    scannedLast1h: joinedChannels.filter((c) => (scanAge(c.lastScanned) ?? 1e9) <= 1).length,
    scannedLast24h: joinedChannels.filter((c) => (scanAge(c.lastScanned) ?? 1e9) <= 24).length,
    scannedLast72h: joinedChannels.filter((c) => (scanAge(c.lastScanned) ?? 1e9) <= 72).length,
    neverScanned: joinedChannels.filter((c) => !c.lastScanned).length,
    joinedTotal: joinedChannels.length,
  };
  const staleProducts = [...latest]
    .filter((p) => p.price != null && (p.ageHours ?? 0) > 72)
    .sort((a, b) => (b.ageHours ?? 0) - (a.ageHours ?? 0))
    .slice(0, 30);
  const channelHealth = joinedChannels
    .map((c) => ({ ...c, scanAgeHours: scanAge(c.lastScanned) }))
    .sort((a, b) => (b.scanAgeHours ?? 1e9) - (a.scanAgeHours ?? 1e9))
    .slice(0, 30);
  return {
    priceFreshness: buckets,
    scanCoverage,
    staleProducts,
    channelHealth,
    volume14d: volume,
    generatedAt: new Date().toISOString(),
  };
}

// ─── alerts ───────────────────────────────────────────────────────────
type AlertRaw = {
  id: number; severity: string; category: string; title: string;
  message: string | null; created_at: string; read_at: string | null;
};

export async function alertsData(limit = 100): Promise<{ unread: number; alerts: AlertRow[] }> {
  const [rows, unread] = await Promise.all([
    sbGet<AlertRaw[]>(`alerts?select=id,severity,category,title,message,created_at,read_at&order=created_at.desc&limit=${limit}`),
    sbCount("alerts", "&read_at=is.null"),
  ]);
  return {
    unread,
    alerts: rows.map((a) => ({
      id: a.id, severity: a.severity, category: a.category, title: a.title,
      message: a.message, createdAt: a.created_at, readAt: a.read_at,
    })),
  };
}

// ─── audit ────────────────────────────────────────────────────────────
export async function auditData(limit = 200): Promise<AuditRow[]> {
  const rows = await sbGet<{
    id: number; actor: string; action: string; entity: string | null;
    entity_id: string | null; details: unknown; ip: string | null; created_at: string;
  }[]>("audit_log?select=id,actor,action,entity,entity_id,details,ip,created_at&order=created_at.desc&limit=" + limit);
  return rows.map((a) => ({
    id: a.id, actor: a.actor, action: a.action, entity: a.entity, entityId: a.entity_id,
    details: a.details ? JSON.stringify(a.details) : null, ip: a.ip, createdAt: a.created_at,
  }));
}

// ─── settings + policy (governance) ──────────────────────────────────
export const POLICY = {
  joinBudgetPerRun: 3,
  privateJoinCapPerRun: 2,
  joinDelaySeconds: "12–30 (عشوائي)",
  totalJoinCeiling: 400,
  telegramUserLimit: 500,
  safetyMargin: "100 مصدر احتياطي",
  peerFloodPause: "48h تعليق كامل للانضمام",
  floodWaitJoinPause: "max(2x الانتظار, 6h) بحد أقصى 48h",
  scanPauseOnFloodWait: "لكل قناة، بحد أقصى 6h+60s",
  adminGatedChats: "تُتخطى (لا تُرسل طلبات انضمام — سياسة مكافحة السبام)",
  expiredInvites: "تُغلق نهائيًا دون إعادة محاولة",
  privateJoinPolicy: "بانتظار موافقة المالك (awaiting_approval → approved → تنفيذ)",
  publicJoinPolicy: "تلقائي ضمن الميزانيات الانضباطية",
  dataPolicy: "حقائق فقط (أسعار/وحدات/شروط)؛ نصوص الرسائل تبقى في قاعدة المالك الخاصة",
  cron: "*/30 * * * * (UTC) — GitHub Actions",
  tosSources: [
    { name: "شروط خدمة تلغرام", url: "https://telegram.org/tos" },
    { name: "سياسة ترخيص المحتوى", url: "https://telegram.org/tos/content-licensing" },
    { name: "شروط Telegram API", url: "https://core.telegram.org/api/terms" },
    { name: "الأسئلة الشائعة عن السبام", url: "https://telegram.org/faq_spam" },
    { name: "حدود تلغرام (500 قناة/مجموعة)", url: "https://limits.tginfo.me/en" },
  ],
} as const;

export type SettingRow = { key: string; value: string | null; updated_at: string; updated_by: string | null };

export async function settingsData(): Promise<SettingRow[]> {
  return sbGet<SettingRow[]>("settings?select=key,value,updated_at,updated_by&order=key.asc&limit=500");
}

// ─── overview ─────────────────────────────────────────────────────────
export type Overview = Awaited<ReturnType<typeof overview>>;

export async function overview() {
  const [obsCount, channelCount, stmtCount, discCount, runCount, prodCount,
    channels, discoveries, stmtKinds, runs, settings, latest, volume, alertsUnread, awaiting] =
    await Promise.all([
      sbCount("price_observations"),
      sbCount("tg_channels"),
      sbCount("statements"),
      sbCount("discoveries"),
      sbCount("runs"),
      sbCount("v_product_stats"),
      sbGet<{ kind: string; joined: boolean }[]>("tg_channels?select=kind,joined&limit=2000"),
      sbGet<{ status: string; kind: string }[]>("discoveries?select=status,kind&limit=5000"),
      sbGet<{ kind: string; count: number }[]>("v_statement_stats?select=kind,count"),
      runsData(30),
      settingsData(),
      latestPrices(300),
      dailyVolume(14),
      sbCount("alerts", "&read_at=is.null"),
      sbCount("discoveries", "&status=eq.awaiting_approval"),
    ]);

  const kindCounts: Record<string, number> = {};
  for (const c of channels) kindCounts[c.kind] = (kindCounts[c.kind] ?? 0) + 1;
  const discStatus: Record<string, number> = {};
  const discKind: Record<string, number> = {};
  for (const d of discoveries) {
    discStatus[d.status] = (discStatus[d.status] ?? 0) + 1;
    discKind[d.kind] = (discKind[d.kind] ?? 0) + 1;
  }
  const stmtKind: Record<string, number> = {};
  for (const s of stmtKinds) stmtKind[s.kind] = s.count;

  const lastRun = runs[0] ?? null;
  const now = new Date();
  // next scheduled Actions run: every 30 min UTC (cron */30)
  const next = new Date(now);
  next.setUTCSeconds(0, 0);
  next.setUTCMinutes(next.getUTCMinutes() < 30 ? 30 : 60);
  if (next.getUTCMinutes() === 60) { next.setUTCMinutes(0); next.setUTCHours(next.getUTCHours() + 1); }

  const activeBreakers = settings
    .filter((s) => (s.key.startsWith("scan_pause_") || s.key.startsWith("join_pause")) && s.value && new Date(s.value) > now)
    .map((s) => ({ key: s.key, value: s.value, updatedAt: s.updated_at }));

  const recent = [...latest]
    .sort((a, b) => (b.postedAt ?? "").localeCompare(a.postedAt ?? ""))
    .slice(0, 8);

  const priced = latest.filter((p) => p.price != null);
  const fresh = priced.filter((p) => (p.ageHours ?? 1e9) <= 24).length;

  return {
    kpis: {
      observations: obsCount,
      channels: channelCount,
      channelKinds: kindCounts,
      statements: stmtCount,
      statementsByKind: stmtKind,
      discoveries: discCount,
      discoveriesByStatus: discStatus,
      discoveriesByKind: discKind,
      runs: runCount,
      products: prodCount,
      suppliers: new Set(latest.map((p) => p.channelId)).size,
      alertsUnread,
      awaitingApprovals: awaiting,
      freshPrices24h: fresh,
      pricedLatest: priced.length,
    },
    automation: {
      lastRun,
      nextRunUTC: next.toISOString(),
      cadenceMinutes: 30,
      circuitBreakers: activeBreakers,
    },
    volume14d: volume,
    recentPrices: recent,
  };
}
