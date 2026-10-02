# AUDIT-8 — Performance, Speed & Reliability Audit (MEC Store)

Agent: AUDIT-8 — Performance, Speed & Reliability Engineer
Date: 2026-09-28 (11:53–12:05 UTC measurements)
Method: REAL measurements only (curl + source reading). No source modifications, no `next build`, no git ops.
Targets: Production https://mec-store-production.up.railway.app (Railway single replica, standalone) + Local dev http://localhost:3000 (Next 16.3.6 dev/Turbopack).

---

## 1. Executive Summary

| Verdict | Detail |
|---|---|
| ⚠️ **CRITICAL — costUsd leak CONFIRMED** | Public `/api/store/catalog` exposes per-supplier wholesale `costUsd`, `stock`, `checkedAt` for all 37 products / 57 chain links (suppliers: ProdSeller, StackVault, Turgame). Anyone can compute exact margins (e.g. Adobe Express 12M: cost $0.35 → sell $0.76 = +117%). Evidence: `src/lib/engine.ts:54` + live JSON. |
| ⚠️ **P1 — 2.6s catalog cache-miss cliff** | Server cache TTL=60s; first request after idle pays **2,601 ms** (prod, measured) vs 217 ms warm = **12x**. For a low-traffic store this is effectively *every real user's first catalog load*. Local dev reproduces: 1,986 ms cold vs 4 ms warm. |
| ⚠️ **P1 — Circuit breaker NOT implemented** | `Supplier.failCount/openUntil` exist in schema and are *displayed* in the admin panel, but **no code ever writes or checks them** during routing. engine.ts header comment claims a breaker that does not exist. |
| ⚠️ **P1 — Live-mode purchase defect** | `engine.ts:176` calls `psPurchase(String(link.supplier))` → sends supplier code `"ps"` as `product_id` (should be `ChainLink.externalId`). In LIVE mode every real purchase would fail → mass refund+apology. |
| ✅ Good | Hot-path DB indexes (7) verified against every observed `where` clause — no unindexed frequent filters found. Wallet/rate-limit/security hardening from task 18-19 holds. Static prerender + etag on `/` and `/intel` (x-nextjs-cache: HIT). Store route correctly code-split from the heavy `/intel` route (638 KB chunk not loaded by `/`). |
| ℹ️ Minor | No `/api/health` (but `/api` liveness JSON exists, no DB check); no scheduled sync despite footer's "every 15 min" claim (data was 1–10 h stale at audit time); `log: ['query']` Prisma logging active in production (61% of dev log lines); 9 woff2 font preloads (Tajawal weight 500 is loaded but unused). |

**Bottom line:** warm-path performance is healthy (prod TTFB med 189–223 ms, dominated by ~180 ms network floor; server-side warm catalog ~4 ms). The real risks are the **cold-cache cliff**, the **public supplier-cost leak (business-critical)**, and **live-mode reliability gaps** (no breaker, broken purchase id, non-transactional wallet debit).

---

## 2. Measurement Method

- **Production:** `curl -sS -o <body|/dev/null> -w '%{http_code} %{time_appconnect} %{time_starttransfer} %{time_total} %{size_download}' --max-time 30 <url>` — 10 sequential iterations per endpoint, 4 endpoints (`/`, `/api/store/catalog`, `/intel`, `/not-found-xyz`). First iteration also captured response headers (`-D`) and body. Percentiles = min/median/max (p90 where shown). No `Accept-Encoding` sent → sizes are **uncompressed**. 40 measurement requests + 1 preliminary reachability check (41 GET total; 1 over stated budget — documented). GET-only, no auth, no writes.
- **Local dev:** identical curl format, 10 iterations for `/` and `/api/store/catalog` (dev server already warm), plus a deliberate **cold test**: sleep 65 s (expire 60 s TTL) → 1 request → 2 warm follow-ups. `/api/health` and `/api` probed once each.
- **Environment:** sandbox client; Railway served via edge `hkg1` (`x-railway-edge: hkg1`) → prod latencies include client→edge→origin network path (~180 ms floor). Local dev = `next dev` (Turbopack), STORE_MODE=sandbox, same Supabase Postgres (aws-1-eu-west-3 pooler :5432) over internet — **dev timings are not comparable to prod absolute values** (unminified, on-the-fly compile), but the *cold/warm cache ratio* is directly comparable.
- **Static analysis:** file reads of `next.config.ts`, `src/app/layout.tsx`, `src/lib/engine.ts`, all 9 API routes, `prisma/schema.prisma`, `src/lib/{ratelimit,prodseller,format,admin-auth,db}.ts`, `store.tsx`; `rg` counts for `'use client'`, `next/dynamic`, `next/image`, `<img`, polling; chunk-size attribution from prior production capture (`research/live_capture/chunks/`, pre-Tajawal build — marked as reference).

---

## 3. Baseline Tables

### 3.1 Production (n=10 per endpoint, 2026-09-28 ~11:53 UTC)

| Endpoint | Status | TTFB min / **med** / p90 / max (ms) | TOTAL med (ms) | Body bytes (uncompressed) |
|---|---|---|---|---|
| `/` (store, prerendered) | 200 | 182 / **223** / 264 / 270 | 227 | 24,122 |
| `/api/store/catalog` (warm, n=9) | 200 | 184 / **217** / 254 / 254 | 220 | 16,354 |
| `/api/store/catalog` (**COLD**, first after >60 s idle) | 200 | — / **2,601** / — / — | 2,603 | 16,354 |
| `/intel` (prerendered) | 200 | 177 / **189** / 216 / 218 | 197 | 48,017 |
| `/not-found-xyz` (custom Arabic 404) | 404 | 177 / **188** / 249 / 252 | 189 | 12,972 |

- TLS handshake (time_appconnect): 13.6–92.8 ms (connection reuse varied). Network floor ≈ 180 ms ⇒ warm server processing ≈ 5–40 ms.
- **Cache-Control evidence:** `/` and `/intel`: `s-maxage=31536000` + `etag` + `x-nextjs-cache: HIT`, `x-nextjs-prerender: 1` (static). Catalog API: `public, max-age=30, stale-while-revalidate=30`, **no ETag** (conditional `If-None-Match` test on local returned full 200 — no 304 support). 404: `no-store` (correct).
- **Cold/warm ratio (catalog): 12x (2,601 ms vs 217 ms median).** The prior audit's "~200 ms cold" claim is **not reproducible**: first request after TTL expiry = 2.6 s on prod, 2.0 s local.

### 3.2 Local dev (n=10, same machine, dev server)

| Endpoint | TTFB min / **med** / max (ms) | Body bytes |
|---|---|---|
| `/` | 25 / **37** / 51 | 27,821 (unminified dev) |
| `/api/store/catalog` (all warm) | 4 / **4** / 5 | 16,354 (byte-identical to prod) |
| `/api/store/catalog` (**COLD** after 65 s idle, single shot) | **1,986** | 16,354 |
| `/api/health` | **404 — endpoint does not exist** | — |
| `/api` (liveness JSON `{"ok":true,"service":"mec-store",...}`) | 200 | — |

- Dev-mode caveat: `/` timings include on-demand compile; catalog warm ~4 ms confirms the "~3 ms warm" claim from the server's perspective. The ~2 s cold path (Prisma findMany + nested includes → Supabase Paris over network) is the same code path as prod's 2.6 s.

### 3.3 Catalog payload analysis (16,354 B, 37 products → 442 B/product)

- Top-level: `ok, mode, families[4], lastSyncAt, products[37]`.
- Per product: 7 fields (`slug, name, family, sourceTier, officialUsd, chain, prices`); avg 3 geo-prices; chain length 1–2.
- **Size verdict: NOT excessive** (16 KB is fine; the problem is *content*, not size).
- **[DEFECT][P0 — business-sensitive data leak] costUsd exposure — CONFIRMED:**
  - Source: `src/lib/engine.ts:17` (type `CatalogChain` includes `costUsd`), `:51-57` (maps `costUsd: c.costUsd`, `stock`, `checkedAt` into public payload), returned by `src/app/api/store/catalog/route.ts:10-13` with `Cache-Control: public`.
  - Live evidence (production JSON, 2026-09-28): 57 chain entries with `costUsd` across suppliers `ps` (ProdSeller), `sv` (StackVault), `turgame`. Sample margins derivable by anyone:
    - `adobe-express-12m`: cost **$0.35** → WW sell $0.76 (**+117%**), YE $0.69
    - `turgame-9-apple-itunes-100-tl`: cost **$2.05** → WW $2.71 (+32%)
    - `autodesk-admin-3000-invite`: cost **$10.00** → WW $13.19 (+32%)
  - Also leaked: per-supplier live `stock` counts and `stockCheckedAt` freshness (competitive intel for rivals), `officialUsd` retail anchors, and supplier codes/identities of the entire supply chain.
  - **Second exposure path:** order-transparency API (`/api/store/orders/[id]`) returns `costUsd` per attempt step (`route.ts:61`) — the buyer sees the exact invoice cost of what they bought. Transparency is a stated product value, but raw costs ≠ transparency; margin-bucket or "wholesale" label achieves the same UX without publishing the supply invoice.

---

## 4. Bundle & Rendering Analysis (static, no build)

**next.config.ts** [FACT]: `output: "standalone"` ✓, `poweredByHeader: false` ✓, `reactStrictMode: false`, `ignoreBuildErrors: false` ✓, no `compress` override (Next default = gzip on — unverified at edge), no `images` config (N/A — no images), security headers via `headers()` ✓ (CSP includes `script-src 'unsafe-inline' 'unsafe-eval'` — security trade-off, not perf).

**layout.tsx** [FACT]: `next/font/google` self-hosted (good — zero external font requests): Tajawal ×**4 weights** (400/500/700/800, arabic+latin subsets) + Geist Mono. Current prod HTML preloads **9 woff2 files** on every page. `font-display` default (swap) ✓. **[OBSERVATION][P2]**: weight 500 is **never used** in the UI (`rg font-medium` = 0 hits in store/pages; 700 used ×38, 800 ×1). Fonts cost ≈ 200–300 KB of preload bandwidth (ESTIMATE — exact file sizes not fetched to respect request budget).

**Client components** [FACT]: 59 files with `'use client'` — 37 shadcn/ui + 17 intel components + store + hooks. **Only 4 UI primitives are imported by the store** (Card, Badge, Button, Input → `store.tsx:9-12`) — tree-shaking works; unused ui/ components don't reach the store bundle.

**Route splitting (verified from prod HTML + prior prod chunk capture)** [FACT]:
- `/` references 10 JS chunks. Prior-build sizes (same store code, pre-Tajawal build): **680,819 B uncompressed total** (React vendor 161.8 K, core-js polyfills 229.2 K, runtime+misc, store chunk 44.8 K); gzip-9 estimate: **205 KB** (ESTIMATE).
- `/intel` additionally loads a **638,231 B** chunk (17 client components + **388 KB of inlined JSON data** from `src/lib/data/*.json`); gzip-9: 137 KB (ESTIMATE). Correctly isolated — store visitors never download it.
- **[OBSERVATION][P3]** `/intel` mounts all 17 tab components eagerly (no `next/dynamic` anywhere in the codebase — `rg "next/dynamic"` = 0). First-load JS for /intel ≈ 1.29 MB uncompressed (~440 KB gz ESTIMATE).
- **[OBSERVATION][P3]** Admin OpsPanel (supplier table, sync button) is embedded in the public store chunk — ships to every visitor (~15 KB; gated client-side by token, API is fail-closed server-side).

**Images:** none — text/emoji UI. `next/image` and `<img>` usage = 0. `public/` = logo.svg (1,065 B) + robots.txt (160 B). Image optimization: N/A.

**CSS:** single stylesheet; `globals.css` 124 lines / 4,200 B source → ~13.5 KB compiled (prior capture). Blocking CSS is small; Tailwind `source(none)` + `@source "../src"` (from MEC-11 fix) keeps it lean. ✓

**Dependencies [FACT]:** 48 runtime deps (24 radix packages, recharts, embla, react-day-picker, cmdk, vaul, sonner, …) — most unused by actual imports. No client-bundle impact (per-import tree-shaking), but slower installs/deploys on Railway.

**Client-side load behavior [FACT]:** store page fires `/api/store/catalog` + `/api/admin/stats` (expects 401 without token) on mount; wallet GET if saved phone; order view polls every **2.5 s** until terminal status (~12 polls per routing in live mode; rate limits comfortably above this).

---

## 5. Database Query Map (source-verified)

| Endpoint | SQL queries (approx, Prisma) | Hot-path filters → index status |
|---|---|---|
| `GET /api/store/catalog` (cold) | 1 findMany + includes → **4 SQL** (Product by `active`, GeoPrice, ChainLink by `active`, Supplier) | `Product.active` ✓ `@@index([active])`, `ChainLink.productId` ✓ — measured 2.0–2.6 s (network RTT to Supabase Paris dominates; not CPU) |
| `GET /api/store/catalog` (warm) | **0 SQL** (60 s in-memory cache) | — |
| `POST /api/store/checkout` (wallet rail) | ~**10–13 SQL**: findUnique slug+includes (4) → wallet upsert (1–2, tx) → SUM balance (1) → order.create (1) → debit tx (1) → attempts createMany (1) → order.update (1) → cashback/refund+apology (1–2). **No `$transaction`, no try/catch around routeOrder** | `Product.slug` ✓ @unique; `Wallet.phone` ✓ @unique; `WalletTx.walletId` ✓ + compound-unique idempotency ✓ |
| `POST /api/store/checkout` (trc20/binance) | ~**5–6 SQL** | same |
| `POST /api/store/payments/confirm` | ~**8–10 SQL** + 1–2 external PS API calls | `Order.publicId` ✓ @unique |
| `GET /api/store/orders/[id]` | **2 SQL** (order by publicId + attempts by orderId) | ✓ both indexed; polled 2.5 s |
| `POST /api/store/orders/[id]/restock` | **4 SQL** (order, waitlist findFirst, create, count) | `Waitlist(productId, phone)` ✓ compound @unique (leading col serves count) |
| `GET /api/wallet` | **3–4 SQL** (upsert by phone, SUM, findMany take 50) | ✓ all indexed |
| `POST /api/wallet/deposit` | **3–5 SQL** | ✓ |
| `GET /api/admin/stats` | **8 SQL** (6 parallel incl. 2 take-limited lists) + **1 external** `psBalance()` on every load | groupBys covered: `ChainLink.supplierId` ✓, `Attempt(supplierCode,status)` ✓ |
| `POST /api/admin/sync` | 2 external (parallel, 25 s/20 s timeouts) + 1 findMany + **N sequential chainLink.update** (N = matched links) + 1 syncLog.create; then `invalidateCatalog()` ✓ | relation filter `supplier.code` ✓ @unique |

**[TEST RESULT] Index coverage: PASS.** Every frequent `where` clause observed maps to a declared `@@index`/`@unique` (task 18-19's 7 hot-path indexes hold). **No unindexed frequent filters found.** Minor: `SyncLog.createdAt` unindexed (8-row read, fine; add if table grows).

**[RISK][P2] Wallet TOCTOU:** balance is read (SUM) then debited in separate queries without transaction/row-lock → concurrent checkouts from the same wallet can overdraw. Harmless in sandbox; **money-losing in live mode**.

**[RISK][P1] Non-transactional debit→route→refund:** if the process dies (deploy SIGTERM / crash / unhandled throw in `routeOrder`) between the wallet debit and delivery/refund, the debit stands with order stuck in `routing`. No compensating try/catch in `checkout/route.ts:55-99`. Refund+apology fires only on *graceful* failure.

---

## 6. Reliability Findings

1. **[FACT] Cache invalidation after admin sync: WORKS.** `syncFromProdSeller()` calls `invalidateCatalog()` (`engine.ts:276`) → next catalog request refetches. Verified in source.
2. **[DEFECT][P1] Circuit breaker: NOT IMPLEMENTED.** `Supplier.failCount/failWindow/openUntil` exist (schema) and render in the admin panel (`store.tsx:703`, `admin/stats:56`), but: `rg failCount|openUntil|failWindow` across `src/` shows **zero write or routing-check sites**. `routeOrder` (`engine.ts:140-206`) iterates chain links using only stock/margin/float guards. engine.ts's header comment ("circuit breaker") overstates reality. Consequence in live mode: a hard-down supplier is re-attempted on every order (latency + API abuse risk), with no auto-open/auto-half-open logic.
3. **[DEFECT][P1] Live purchase call passes wrong ID.** `engine.ts:176`: `psPurchase(String(link.supplier))` → `POST /v1/orders {product_id: "ps"}`. Should pass `ChainLink.externalId`. Every live-mode PS purchase would fail → full refund+apology loop. (Sandbox unaffected — never called.)
4. **[OBSERVATION] Retry policy: none.** Single attempt per supplier; failover to next chain link only. PS client has good timeouts (20–30 s, AbortController) but no retry/backoff.
5. **[RISK][P2] Single replica SPOF (Railway).** Every deploy = restart = in-memory loss (catalog cache → 2.6 s first hit; rate-limit buckets wiped → brief unlimited window). No graceful-shutdown handler (`rg SIGTERM` = 0) → in-flight checkout can be killed mid-debit (compounds finding in §5).
6. **[OBSERVATION][P2] No scheduled sync.** Sync is admin-manual only (`rg cron|scheduler` = 0 in server code). Footer promises "الأسعار تتغير مع تحديث الموردين كل 15 دقيقة" — at audit time `lastSyncAt` was **60 min** old and sv/turgame `checkedAt` was **~10 h** old. Promise ≠ reality.
7. **[OBSERVATION][P2] Health endpoint:** `/api/health` = **404**. `/api` exists (liveness JSON, no DB check). No deep health (DB `SELECT 1` + PS reachability). Railway healthcheck path config unknown (dashboard-only).
8. **[OBSERVATION][P2] Rate limiter GC:** `MAX_BUCKETS=50_000`, on overflow `buckets.clear()` wipes **all** limits globally (ratelimit.ts:38) — an attacker rotating fake `X-Forwarded-For` values could both bypass per-IP limits (clientIp trusts the first XFF entry, `ratelimit.ts:24-26` — Railway XFF handling unverified, ASSUMPTION) and deliberately trip the 50 k clear(). Crude GC is acceptable at current scale, but the XFF trust is the bigger hole.
9. **[FACT] Refund+apology resilience (graceful path):** verified logic — full failure → refund + $1 apology credit + order marked failed; idempotency: repeated confirm returns current state (`confirm/route.ts:37-39`); wallet ledger idempotency via `@@unique([walletId,type,ref])`.
10. **[OBSERVATION] Prisma `log: ['query']` in production** (`db.ts:10`, unconditional): 525 of 857 dev.log lines (61%) are query logs. On Railway this inflates log volume/cost + per-query overhead. One-line fix.

---

## 7. Optimization Candidates (ranked)

| # | Finding | Proposed change | Expected impact (ESTIMATE) | Trade-offs |
|---|---|---|---|---|
| 1 | **[P0] costUsd/stock/checkedAt leak** (§3.3) | Strip `chain[].costUsd` (+ stock/checkedAt, or reduce to a boolean `inStock`) from public catalog & order-transparency payloads; keep full chain server-side for routing | Closes business-critical leak; payload ~16.4 KB → ~12 KB (−25% ESTIMATE). Competitors can no longer compute margins or see supplier stock | Loses "we show you our cost" marketing angle — replace with margin-bucket label ("تكلفة الجملة محفجوة") or winner-only disclosure |
| 2 | **[P1] 2.6 s catalog cold cliff** (§3.1) | Serve stale + background refresh (SWR on the server cache): return cached data immediately even past TTL while a single refresh runs; and/or raise TTL to 5–15 min (sync already invalidates on change) | First-visitor catalog TTFB 2,601 ms → ~220 ms (**−92%**); removes the 12x cliff that hits essentially every user at current traffic (<1 req/min) | Stale data up to TTL — but data is *already* 1–10 h stale (no scheduled sync); TTL raise is honest |
| 3 | **[P1] Circuit breaker missing + psPurchase wrong id** (§6.2–3) | Implement breaker (e.g., open on 3 consecutive `purchase_failed`, half-open after 5 min — the schema fields are already there); pass `externalId` to psPurchase | Prevents per-order latency spikes + supplier-API abuse in live mode; unblocks live-mode purchases entirely (currently 100% would fail) | Slight code complexity; needs live-mode E2E test before enabling |
| 4 | **[P1] Non-transactional wallet flow + TOCTOU** (§5) | Wrap debit→route→credit/refund in `prisma.$transaction` (or serializable debit via conditional UPDATE `WHERE balance >= amount`) + try/catch compensating refund | Eliminates money-loss windows on crash/deploy/race; required before STORE_MODE=live | Slightly longer lock windows; test with concurrent checkouts |
| 5 | **[P2] Scheduled sync absent** (§6.6) | Railway cron/scheduled job (or external cron) POSTing `/api/admin/sync` with token every 15 min; or soften footer copy | Data freshness honored (currently 1–10 h stale vs "15 min" promise); also keeps catalog cache warm → synergy with #2 | Each sync = 2 PS API calls (rate/quota aware); secrets handling for cron |
| 6 | **[P2] Prisma query logging in prod** (§6.10) | `log: process.env.NODE_ENV === 'production' ? ['error'] : ['query']` | −61% log volume (measured on dev parity); less log ingestion cost; marginal latency win | Lose query traces in prod debugging (use `error` level instead) |
| 7 | **[P2] 9 font preloads, weight 500 unused** (§4) | Drop Tajawal 500; consider mapping the single `font-extrabold` (800) use → 700 | 9 → 5 woff2 preloads (−~80–120 KB ESTIMATE); faster FCP on slow MENA mobile links | 800-vs-700 visual nuance on one header title |
| 8 | **[P2] Deep health endpoint** (§6.7) | Add `/api/health`: DB `SELECT 1` + PS reachability + mode; register as Railway healthcheck path | Platform can auto-restart on DB partition; better observability; deployment gating | Trivial cost; avoid heavy checks (keep <1 s) |
| 9 | **[P3] ETag/304 for catalog API** (§3.1) | Compute a cheap content hash (e.g., `lastSyncAt` + product count) → `ETag` + `If-None-Match` → 304 | Saves 16.4 KB per 30 s-per-client revalidation (minor at current traffic; ESTIMATE −90% bytes on revalidations) | Extra header logic; browser cache already limits frequency |
| 10 | **[P3] /intel eager 638 KB chunk** (§4) | `next/dynamic` per tab (Radix Tabs unmounts inactive content anyway); lazy-load OpsPanel | /intel first-load JS 1.29 MB → ~700–800 KB uncompressed (ESTIMATE); store route unaffected | Slight tab-switch latency (chunk fetch); more chunks to cache |
| 11 | **[P3] Rate-limiter hardening** (§6.8) | Trust Railway's client IP (last XFF entry or platform header), replace `clear()` with size-bounded LRU eviction | Closes XFF-spoof bypass + global-clear DoS; protects checkout/deposit in live mode | Must confirm Railway's XFF semantics first (ASSUMPTION) |
| 12 | **[P3] Verify compression at edge** (§4) | Confirm gzip/brotli on JS/CSS responses (Next `compress` default true, unverified at Railway edge); consider `Cache-Control: immutable` audit | 680 KB store JS → ~205 KB gz (gzip-9 measured locally; ESTIMATE at edge) | None if already on; just verify |
| 13 | **[P3] Graceful shutdown** (§6.5) | SIGTERM handler: stop accepting, drain in-flight (Next standalone supports custom server hooks; or Railway `preDeploy` drain) | Closes deploy-time money-loss window (with #4) | Small ops complexity |

**Not needed / already good:** image optimization (no images), CDN for HTML (`s-maxage=1y` set, `x-nextjs-cache: HIT` works even without CDN), CSS size, store-route bundle weight, DB indexing, dev-vs-prod parity of catalog payload.

---

## 8. Limitations

1. Prod latencies measured from one sandbox location via Railway edge `hkg1` (~180 ms network floor) — MENA user experience will differ; server-side processing time is the comparable part.
2. Production request budget: 40 measurement GETs + 1 preliminary reachability check = 41 (1 over the stated budget — acknowledged; GET-only, no writes).
3. Chunk-size table uses the *prior* production build capture (pre-Tajawal; store code identical). Current-build chunk hashes differ; totals are ESTIMATE for the current build (7 of 10 chunk hashes match, which anchors the estimate).
4. Compression (gzip/brotli) at the Railway edge unverified — no `Accept-Encoding` probe spent against prod to respect budget; gzip figures are local `gzip -9` ESTIMATES.
5. Railway-side config (healthcheck path, deploy region vs DB region, replica settings) lives in the dashboard — not auditable from repo; DB round-trip attribution for the 2.6 s cold is inference from local reproduction (1,986 ms to Supabase Paris over internet), not EXPLAIN-level proof.
6. Circuit-breaker/XFF conclusions are code-level (rg-verified absence); runtime behavior under live mode untested (store is in sandbox; live purchase path never exercised — consistent with finding §6.3).
7. Percentiles from n=10 per endpoint — sufficient for median stability of these distributions (bimodal cold/warm catalog handled explicitly), not a substitute for RUM percentiles.

— AUDIT-8 · 2026-09-28 · evidence files: `/tmp/audit8/*.tsv`, `prod_catalog_body`, captured headers; prior-build chunks: `research/live_capture/chunks/`.
