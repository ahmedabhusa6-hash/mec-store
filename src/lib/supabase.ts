/**
 * MEC Intelligence Platform — LIVE Supabase data layer (rebuild v4, 2026-10-11).
 * Server-side only. Reads/writes go through PostgREST with the service key
 * (bypasses RLS; the public never talks to Supabase directly).
 * 60s in-memory cache per GET path. BigInt TG ids are converted to Number.
 */
const SB_URL = (process.env.SUPABASE_URL ?? "").replace(/\/+$/, "");
const SB_KEY = process.env.SUPABASE_KEY ?? "";

export class SbError extends Error {}

function assertCfg() {
  if (!SB_URL || !SB_KEY) throw new SbError("SUPABASE_URL/SUPABASE_KEY not configured");
}

// ─── cache ────────────────────────────────────────────────────────────
type CacheEntry = { at: number; data: unknown };
const cache = new Map<string, CacheEntry>();

async function cached<T>(key: string, ttlMs: number, fn: () => Promise<T>): Promise<T> {
  const hit = cache.get(key);
  if (hit && Date.now() - hit.at < ttlMs) return hit.data as T;
  const data = await fn();
  cache.set(key, { at: Date.now(), data });
  return data;
}

export function clearSbCache() {
  cache.clear();
}

// ─── REST core ────────────────────────────────────────────────────────
export async function sbGet<T = unknown>(path: string, ttlMs = 60_000): Promise<T> {
  assertCfg();
  return cached(`GET ${path}`, ttlMs, async () => {
    const r = await fetch(`${SB_URL}/rest/v1/${path}`, {
      headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` },
      cache: "no-store",
    });
    if (!r.ok) throw new SbError(`GET ${path} -> ${r.status}: ${(await r.text()).slice(0, 160)}`);
    return (await r.json()) as T;
  });
}

export async function sbCount(table: string, filter = "", ttlMs = 60_000): Promise<number> {
  return cached(`CNT ${table}${filter}`, ttlMs, async () => {
    assertCfg();
    const r = await fetch(`${SB_URL}/rest/v1/${table}?select=*&limit=1${filter}`, {
      headers: {
        apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`,
        Range: "0-0", Prefer: "count=exact",
      },
      cache: "no-store",
    });
    if (!r.ok) throw new SbError(`count ${table} -> ${r.status}`);
    const cr = r.headers.get("content-range") ?? "0/0";
    return parseInt(cr.split("/").pop() ?? "0", 10) || 0;
  });
}

export async function sbPost(path: string, body: unknown, prefer = "return=minimal"): Promise<string> {
  assertCfg();
  const r = await fetch(`${SB_URL}/rest/v1/${path}`, {
    method: "POST",
    headers: {
      apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`,
      "Content-Type": "application/json", Prefer: prefer,
    },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) throw new SbError(`POST ${path} -> ${r.status}: ${text.slice(0, 200)}`);
  return text;
}

export async function sbPatch(path: string, body: unknown): Promise<string> {
  assertCfg();
  const r = await fetch(`${SB_URL}/rest/v1/${path}`, {
    method: "PATCH",
    headers: {
      apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`,
      "Content-Type": "application/json", Prefer: "return=minimal",
    },
    body: JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) throw new SbError(`PATCH ${path} -> ${r.status}: ${text.slice(0, 200)}`);
  return text;
}

export function sbUrl(path: string): string {
  return `${SB_URL}/rest/v1/${path}`;
}

export function sbHeaders(): Record<string, string> {
  return { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` };
}

/** URL-encode a filter value for PostgREST (Arabic product names, +invite keys) */
export function q(v: string): string {
  return encodeURIComponent(v);
}
