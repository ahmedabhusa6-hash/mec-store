// MEC rate limiter — in-memory sliding window per IP+bucket.
// Single-replica deployment (Railway numReplicas=1) → in-memory is correct.
// FIX for audit finding: "no rate limiting on checkout" (12 req in 39s all 200).

type Window = { hits: number[] };

const buckets = new Map<string, Window>();
const MAX_BUCKETS = 50_000;

export type RateRule = { limit: number; windowMs: number };

export const RATE_RULES: Record<string, RateRule> = {
  checkout: { limit: 10, windowMs: 60_000 },
  confirm: { limit: 12, windowMs: 60_000 },
  deposit: { limit: 6, windowMs: 60_000 },
  // FIX (MEC-21-C R-2): wallet_read was 60/min/IP — generous phone-enumeration
  // budget. 20/min is ample for a real user polling their own wallet.
  wallet_read: { limit: 20, windowMs: 60_000 },
  catalog: { limit: 60, windowMs: 60_000 },
  admin: { limit: 30, windowMs: 60_000 },
  generic: { limit: 120, windowMs: 60_000 },
};

/**
 * FIX (P2, AUDIT-3/7 — CWE-348): clientIp() trusts the client-supplied
 * x-forwarded-for header, so a spoofed XFF gives each request a fresh
 * per-IP bucket. Backstop: a GLOBAL cap per bucket (per-IP limit × 30)
 * applies regardless of IP, bounding total abuse even under full spoofing.
 */
const globalBuckets = new Map<string, number[]>();

function globalAllow(bucket: string, now: number): boolean {
  const rule = RATE_RULES[bucket] ?? RATE_RULES.generic;
  const cap = rule.limit * 30;
  let hits = globalBuckets.get(bucket) ?? [];
  hits = hits.filter((t) => now - t < rule.windowMs);
  if (hits.length >= cap) {
    globalBuckets.set(bucket, hits);
    return false;
  }
  hits.push(now);
  globalBuckets.set(bucket, hits);
  return true;
}

export function clientIp(req: Request): string {
  const h = req.headers;
  return (
    h.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    h.get("x-real-ip") ||
    "unknown"
  );
}

/** Returns true if allowed; false if rate-limited. */
export function rateLimit(bucket: string, ip: string): boolean {
  const rule = RATE_RULES[bucket] ?? RATE_RULES.generic;
  const key = `${bucket}:${ip}`;
  const now = Date.now();
  let w = buckets.get(key);
  if (!w) {
    if (buckets.size > MAX_BUCKETS) buckets.clear(); // crude GC for long uptime
    w = { hits: [] };
    buckets.set(key, w);
  }
  w.hits = w.hits.filter((t) => now - t < rule.windowMs);
  if (w.hits.length >= rule.limit) return false;
  w.hits.push(now);
  return true;
}

export function rateLimitResponse(bucket: string): Response {
  const rule = RATE_RULES[bucket] ?? RATE_RULES.generic;
  return Response.json(
    {
      ok: false,
      error: `طلبات كثيرة جدًا — الحد ${rule.limit} طلبًا في الدقيقة. انتظر قليلًا ثم أعد المحاولة.`,
    },
    { status: 429, headers: { "Retry-After": "30" } }
  );
}

/** Extract client IP in Next.js route handlers (Request object). */
export function guard(req: Request, bucket: string): Response | null {
  const now = Date.now();
  if (!globalAllow(bucket, now)) return rateLimitResponse(bucket);
  if (!rateLimit(bucket, clientIp(req))) return rateLimitResponse(bucket);
  return null;
}
