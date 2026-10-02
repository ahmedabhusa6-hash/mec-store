# MEC-21-D — Post-Optimization Performance Re-Measurement & Health-Latency Investigation

Agent: MEC-21-D — Performance & Reliability Measurement Specialist (Team 07 execution)
Date: 2026-09-28, 13:00–13:12 UTC (all measurements real; nothing fabricated; NOT VERIFIED marked where applicable)
Method: measurement-only. curl GET/HEAD `--max-time 30`, source reads, sandbox-side Prisma/pg8000 probes. **No source changes, no builds, no restarts, no load tests.**
Targets: Production https://mec-store-production.up.railway.app (Railway single replica, standalone, BUILD_ID `tS2O8_82rBwmPOD83JZYX`) + local **production-mode** server http://localhost:3000 (running `NODE_ENV=production node .next/standalone/server.js` — same BUILD_ID as prod, byte-identical HTML/CSS/JS hashes; NOT `next dev`).

---

## 1. Executive Summary

| Verdict | Detail |
|---|---|
| ✅ **Cold-cache cliff ELIMINATED** | First catalog request after >120 s TTL expiry: **TTFB 230 ms** (was **2,601 ms**, −91%). SWR stale-serve verified twice on prod + once locally (2.96 ms). Warm/warm-stale ratio now **1.01×** (was 12×). |
| 🔴 **ROOT CAUSE of slow `/api/health` (1,090 ms) FOUND & REPRODUCED** | Railway runtime `DATABASE_URL` uses Supabase **transaction pooler :6543 with `pgbouncer=true&connection_limit=1`**. With `pgbouncer=true`, **every Prisma query pays full connection re-establishment**: measured **983 ms/query from sandbox** (vs 194–205 ms without the flag) — decomposition proves `pgbouncer=true` is the sole culprit. On Railway this = **713–857 ms per query**, hence health TTFB 894–1,076 ms. |
| 🔴 **NEW P1: DB head-of-line blocking during SWR background refresh** | `connection_limit=1` + the per-query tax ⇒ every ~120 s TTL expiry (and after each admin sync), the 4-query catalog rebuild (~2.5–2.9 s) **queues ALL other DB queries**. Measured: health fired during refresh waited **2,452 ms**. Checkout/wallet/order-status would stall the same way. |
| ✅ MEC-20 fixes verified | SWR cache ✓ (measured), circuit breaker ✓ (real, code-verified), externalId ✓, apology cap ✓, health endpoint ✓ (works), Prisma `log:['query']` disabled ✓, deps 48→14 ✓. |
| ❌ MEC-20 claim NOT implemented | "Font preloads trimmed" — **layout.tsx still declares Tajawal 400/500/700/800; prod HTML still preloads 9 woff2 (99,900 B)**; weight 500 is used only by `/intel` components, not the store. |
| ⚠️ Parity gap | Local `.env`/standalone uses `:5432` session pooler (fast path, 194 ms) while Railway runtime uses `:6543?pgbouncer=true&connection_limit=1` — all local testing (MEC-20 regression suite/E2E) ran the fast config and could not see the prod DB tax. |

**Bottom line:** user-facing warm paths are healthy (TTFB ~222–249 ms, network-bound; server-side cost 2–4 ms) and the historic 12× cold cliff is gone. The dominant remaining cost is **not the app — it is one query-string parameter** (`pgbouncer=true`) in Railway's runtime `DATABASE_URL`, taxing every DB query ~5× and serializing all DB work behind a 1-connection pool. Removing it (switch to `:5432` session pooler, drop `pgbouncer=true`, raise `connection_limit`) should take health from ~0.96 s → ~0.25 s TTFB and eliminate the 2.5 s stall windows.

---

## 2. Methodology

- **Prod:** `curl -sS -o <body|/dev/null> -w '%{http_code}\t%{time_appconnect}\t%{time_starttransfer}\t%{time_total}\t%{size_download}' --max-time 30` sequential; batches `/`×10, catalog×10 warm, health×5 rapid, `/intel`×5, 404×3 (within max-10 rule), plus 14 single-shot diagnostics (cold test, header checks, HTML captures, refresh-contention probe, health-after-idle). **47 prod GET/HEAD total, GET/HEAD only, no writes.** Client→Railway edge `hkg1` ≈ 180 ms network floor (same path as AGENT-8).
- **Local:** identical curl format against `localhost:3000` = production-mode standalone build (**same BUILD_ID as Railway**; `/` body 26,692 B and all chunk hashes byte-identical to prod). This makes local server-side timings directly comparable to prod (only network + env differ).
- **DB probes (sandbox side, read-only):** raw `pg8000` connection timing to Supabase `aws-1-eu-west-3` (both pooler ports); Prisma `$queryRaw SELECT 1` timing matrix isolating each `DATABASE_URL` parameter (project's own `@prisma/client`). No data read beyond `SELECT 1`.
- **Railway config evidence:** GraphQL v2 API (read-only) — variable **names + derived host/port/params only**; secret values never printed or stored.
- **Times (UTC):** prod `/` 13:00:22 · catalog warm 13:00:39 · health rapid 13:00:51 · intel/404/headers 13:01:55–13:01:57 · prod cold test 13:04:45 · local batch 13:02:13–13:05:25 · probes 13:06–13:09 · refresh-contention probe 13:10:18 · header checks 13:11.

---

## 3. Raw Data

### 3.1 Production (2026-09-28 13:00–13:11 UTC)

| Endpoint | n | Status | TTFB min / **med** / max (ms) | TOTAL med (ms) | Body (B) |
|---|---|---|---|---|---|
| `/` (static prerender) | 10 | 200 | 181 / **222** / 272 | 226 | 26,692 |
| `/api/store/catalog` (warm) | 10 | 200 | 213 / **227** / 499¹ | 228 | 13,329 |
| `/api/store/catalog` **first GET after >120 s TTL expiry (SWR stale-serve)** | 1 | 200 | **230** | 232 | 13,329 |
| — immediate 2nd GET | 1 | 200 | 224 | 226 | 13,329 |
| — immediate 3rd GET | 1 | 200 | 224 | 225 | 13,329 |
| `/api/health` (rapid back-to-back) | 5 | 200 | 894 / **959** / 1,076 | 959 | 110 |
| `/api/health` after ~4 min idle | 1 | 200 | **1,919** | 1,919 | 111 |
| `/api/health` fired during catalog background refresh | 1 | 200 | **2,670** | 2,670 | 111 |
| `/api/health` after refresh completed | 1 | 200 | 922 | 922 | 110 |
| `/intel` (static prerender) | 5 | 200 | 212 / **249** / 270 | 258 | 48,362 |
| `/nope-mec21d` (custom 404) | 3 | 404 | 180 / **183** / 226 | 185 | 13,329² |

¹ one 499 ms outlier among ten (transient; median robust). ² 404 is an HTML page; 13,329 B equal to catalog size is coincidence.

**Server-reported DB latency inside `/api/health` (`latencyMs`, app-measured `SELECT 1` wall time, excludes client network):**

| Condition | latencyMs |
|---|---|
| rapid ×5 | 713 / 713 / 715 / 714 / **857** |
| after ~4 min idle | **1,727** |
| concurrent with catalog background refresh | **2,452** |
| after refresh completed | **698** |

**Cache headers (captured 13:11 UTC):**
- `/` and `/intel`: `cache-control: s-maxage=31536000`, `etag` present, `x-nextjs-cache: HIT`, `x-nextjs-prerender: 1` ✓ (unchanged, healthy)
- `/api/store/catalog`: `cache-control: public, max-age=30, stale-while-revalidate=30` — **still no ETag** (AGENT-8 P3 open; not claimed by MEC-20)
- 404: `no-store` ✓ correct
- Security headers all present; CSP now **without** `unsafe-eval` ✓ (MEC-20 fix live)

### 3.2 Local production-mode standalone (same BUILD_ID as prod; DB via `.next/standalone/.env` → `:5432` session pooler)

| Endpoint | n | TTFB min / **med** / max (ms) | Body (B) |
|---|---|---|---|
| `/` | 5 | 2 / **2** / 2 | 26,692 (byte-identical to prod) |
| `/api/store/catalog` (warm) | 5 | 2 / **3** / 4 | 13,329 |
| `/api/store/catalog` first after >120 s idle (SWR) | 1 | **2.96** | 13,329 |
| — immediate 2nd | 1 | 2.0 | 13,329 |
| `/api/health` rapid ×5 | 5 | 194 / **195** / 385 | 110 (`latencyMs` 192×4, one 382) |
| `/api/health` after ~3 min idle | 1 | **615** | `latencyMs` **613** |
| `/intel` ×3 | 3 | 1.7–3.8 | 48,362 |

### 3.3 DB path probes from sandbox (read-only, `SELECT 1` only)

**Raw pg8000 to Supabase eu-west-3 (sandbox RTT ≈ 195 ms):**

| Port / mode | fresh connect (TCP+TLS+auth) | reused connection query | after 2 s idle |
|---|---|---|---|
| `:5432` session pooler | 1,416–1,457 ms | 196–205 ms | 202 ms |
| `:6543` transaction pooler | 1,428 ms | 197–199 ms | 197 ms |

→ Both poolers are fast and hold connections fine at the protocol level.

**Prisma `$queryRaw SELECT 1` parameter matrix (project's `@prisma/client`, same process, 300–400 ms gaps):**

| Config | first query | rapid follow-ups | after 3 s idle | after 10 s idle |
|---|---|---|---|---|
| **A** `:5432`, no params *(= local .env)* | 1,569 ms | **194, 194, 194, 194, 194** | 194 ms | 386 ms |
| **B** `:6543?pgbouncer=true&connection_limit=1` *(= Railway runtime)* | 2,182 ms | **983, 987, 983, 984, 983** | 983 ms | 1,180 ms |
| **C** `:6543`, no params | 1,682 ms | 205, 205, 205 | — | — |
| **D** `:5432?pgbouncer=true&connection_limit=1` | 2,208 ms | 991, 1,000, 991 | — | — |
| **E** `:6543?connection_limit=1` | 1,598 ms | 197, 197, 197 | — | — |
| **F** `:6543?pgbouncer=true` | 2,180 ms | 986, 983, 985 | — | — |

→ **`pgbouncer=true` alone adds ~790 ms per query** (B/F/D ≈ 983–1,000 ms vs A/C/E ≈ 194–205 ms), flat regardless of 300 ms / 3 s / 10 s gaps — i.e., every query re-pays multi-round-trip connection setup. Port 6543 and `connection_limit=1` are individually innocent.

### 3.4 Railway runtime configuration (GraphQL v2, values masked — only host/port/params shown)

- Runtime `DATABASE_URL`: `aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1`
- Local `.env` and `.next/standalone/.env`: `aws-1-eu-west-3.pooler.supabase.com:5432/postgres` (no params)
- **Dev/prod parity gap confirmed** — the two differ; local tests never exercised the slow config.

### 3.5 Bundle & assets (prod HTML + local `.next` — same build, all hashes matched; no rebuild performed)

| Asset | AGENT-8 (pre-fix) | Now | Δ |
|---|---|---|---|
| `/` JS | ~681 KB / 10 chunks (prior-build estimate) | **674,820 B** / 11 chunks (gzip-9 **206,617 B**) | ≈ −1% |
| `/intel` extra JS | 638,231 B | **557,914 B** (main chunk 535,737 B) | −12.6% |
| `/intel` total JS | ~1.29 MB (est.) | **1,181,379 B** (gzip-9 316,657 B) | −8% |
| CSS on `/` | 13.5 KB (**broken Tailwind**, zero utilities) | **79,476 B** (working — intentional AUDIT-6 fix) | +66 KB (correct) |
| woff2 preloads on `/` | 9 (weight 500 unused) | **9 preloads = 99,900 B** (layout.tsx still declares weights 400/**500**/700/800; `font-medium` used only in `/intel` components — supply.tsx, entities.tsx — not in store) | **unchanged — trim NOT done** |
| Runtime deps | 48 | **14** ✓ (prisma 6.19.3 in tree) | −71% ✓ |

### 3.6 Reliability spot-checks (code-verified)

1. **Circuit breaker — REAL now** (`src/lib/engine.ts:147-160, 236-244, 264`): in-memory `Map<supplier,{fails,openUntil}>`; `breakerOpen()` checked in `routeOrder` before live purchase; `breakerRecord()` written after each live PS attempt; 3 consecutive fails → 5 min open. Enforced in **live mode only** (sandbox never reaches it — runtime behavior NOT VERIFIED, consistent with sandbox deployment). Single-replica in-memory = acceptable for 1 replica.
2. **externalId fix — VERIFIED**: `engine.ts:262` `psPurchase(String(link.externalId))`; links without externalId are skipped with an explicit fail step (`:249-257`). Was supplier code "ps" before.
3. **Apology cap — VERIFIED**: `creditApologyGuarded()` (`engine.ts:123-132`) — once per phone per 24 h, full refund always.
4. **Cache invalidation — VERIFIED (code)**: `syncFromProdSeller()` → `invalidateCatalog()` (`engine.ts:363`); admin sync route is token-gated + rate-limited (`api/admin/sync/route.ts`). Runtime re-test not needed (unchanged since AUDIT-8 verified the same call).
5. **Health under DB outage — code-verified, NOT runtime-testable safely**: `SELECT 1` throws → `ok:false, db:false`, **HTTP 503**, error logged (`src/app/api/health/route.ts:16-28`). Correct semantics for a Railway healthcheck.
6. **Single-replica cold start — partial evidence**: in-process recovery after idle costs 1,727 ms (health first-touch). A **post-deploy** first catalog request hits `catalogCache === null` → full 4-query rebuild on the slow config ≈ 2.8–3 s (code-path verified; NOT MEASURED — would require a restart/deploy, out of scope). No SIGTERM graceful drain found previously; unchanged.
7. **Prisma logging — VERIFIED**: `src/lib/db.ts:12` `log: ['error','warn']` (query logging removed).

---

## 4. Delta vs AGENT-8 Baseline

| Metric | AGENT-8 (2026-09-28 ~11:53 UTC) | MEC-21-D (13:00–13:11 UTC) | Δ |
|---|---|---|---|
| `/` TTFB med | 223 ms | 222 ms | ≈ 0% (network-bound) |
| `/` body | 24,122 B | 26,692 B | +10.6% (styled page, richer content) |
| Catalog warm TTFB med | 217 ms | 227 ms | +4.6% (noise; server-side 2–4 ms) |
| **Catalog COLD (first after TTL)** | **2,601 ms** | **230 ms** | **−91% — cliff eliminated (12× → 1.01×)** |
| Catalog body | 16,354 B | 13,329 B | −18.5% (costUsd/checkedAt stripped) |
| `/intel` TTFB med | 189 ms | 249 ms | +32%³ |
| 404 TTFB med | 188 ms | 183 ms | −3% |
| `/api/health` | **404 — did not exist** | 200; TTFB med 959 ms rapid / 1,919 ms after idle | NEW endpoint; slow — root cause §5 |
| Catalog ETag | none | **still none** | unchanged (P3 open) |
| Catalog Cache-Control | `public, max-age=30, swr=30` | same | unchanged |
| Prisma `log:['query']` | on (61% of logs) | **off** | fixed ✓ |
| Runtime deps | 48 | 14 | −71% ✓ |
| Store JS (uncompressed / gz-9) | ~681 KB / ~205 KB est. | 674,820 B / 206,617 B | ≈ −1% |
| `/intel` extra chunk | 638,231 B | 557,914 B | −12.6% |
| CSS on `/` | 13.5 KB broken | 79,476 B working | intentional fix |
| Font preloads | 9 woff2, weight 500 unused in store | 9 woff2 (99,900 B), 500 used only by /intel | **claim "trimmed" NOT true** |
| Circuit breaker | display-only fiction | real (code-verified, live-mode) | fixed ✓ |
| psPurchase product_id | supplier code (live 100% fail) | `externalId` | fixed ✓ |
| Catalog cold cliff root cost (4-query rebuild) | 2,601 ms visible | **~2.5–2.9 s paid in background** (measured via contention probe: health waited 2,452 ms) | unchanged, now hidden |

³ `/intel` is static (`x-nextjs-cache: HIT`, prerender 1 — verified); server cost is ms; both sessions' min values differ by ~35 ms — attributed to edge/network path variance between sessions, not an app regression. NOT actionable.

---

## 5. Health-Latency Root-Cause Analysis

**Observation to explain:** orchestrator measured `/api/health` ≈ 1,090 ms once; our rapid ×5 = TTFB 894–1,076 ms with **server-side `latencyMs` 713–857 ms flat**; after ~4 min idle = 1,727 ms server-side.

**Investigation chain (all evidence above):**
1. **Source** (`src/app/api/health/route.ts`): one `db.$queryRaw SELECT 1` per request + JSON with self-measured `latencyMs`. `force-dynamic`. So TTFB = network + one DB round trip.
2. **Rapid back-to-back does NOT drop** (713→713→715→714→857): rules out a one-off cold Prisma connection. Every request pays the same cost.
3. **Local production-mode twin (same build) is fast**: 192 ms flat rapid, 613 ms after idle → the app code and Prisma pooling are fine; the difference must be **environment**.
4. **Raw pooler protocol test**: `:6543` transaction pooler holds connections fine (197 ms reused) → the pooler is not inherently slow.
5. **Railway runtime `DATABASE_URL` (masked, via GraphQL): `:6543?pgbouncer=true&connection_limit=1`** vs local `:5432` no params — **the configs differ**.
6. **Parameter matrix (§3.3)**: with the exact Railway config, Prisma pays **983 ms per query, flat, forever** (sandbox). Decomposition isolates **`pgbouncer=true`** as the sole cause (+~790 ms/query); port and `connection_limit=1` are innocent alone.

**Root cause (high confidence, reproduced):** `pgbouncer=true` in the Railway runtime `DATABASE_URL` makes every Prisma query re-pay multi-round-trip connection establishment (~4–5 RTTs) instead of reusing the pooled connection — consistent with the transaction pooler tearing down the client session after Prisma's pgbouncer-compatible teardown (no prepared statements / `DISCARD ALL`-style cleanup). Railway origin → Supabase Paris RTT ≈ 150–180 ms ⇒ **~713 ms per query**; sandbox RTT ≈ 195 ms ⇒ ~983 ms. The orchestrator's 1,090 ms = 713 ms query + ~380 ms edge/network variance. First call after idle additionally pays a fully cold pool (1,727 ms).

**This also retro-explains AGENT-8's 2,601 ms cold cliff:** catalog rebuild = 4 sequential queries × ~650 ms (the same tax) — now served around by SWR but still paid by the background refresh, measured at ~2.5–2.9 s via the contention probe.

**Collateral reliability effect (NEW finding, P1):** with `connection_limit=1`, the SWR background refresh (4 queries ≈ 2.5–2.9 s) **head-of-line-blocks every other DB query** — measured: concurrent health waited 2,452 ms. Under live traffic, every TTL expiry (120 s) or admin-sync invalidation opens a ~2.5–3 s window in which checkout, wallet, deposit, and order-status queries queue. Wallet TOCTOU/timeout risks compound.

**Recommended fix (NOT applied — measurement-only mandate):** change Railway runtime `DATABASE_URL` to the session pooler form proven locally: `postgresql://…@aws-1-eu-west-3.pooler.supabase.com:5432/postgres` (drop `pgbouncer=true`; drop or raise `connection_limit` — suggest 5, and align the local `.env` to the same string for parity). Expected, from measured config A: per-query ~150–200 ms from Railway, health TTFB ≈ 250–400 ms, background refresh ≈ 0.8–1.2 s, stall windows reduced ~3×. Verify Supabase session-pooler client limits before scaling traffic.

---

## 6. Remaining Bottlenecks (ranked)

| # | Sev | Finding | Evidence | Fix direction |
|---|---|---|---|---|
| 1 | **P1** | `pgbouncer=true` in Railway `DATABASE_URL`: ~713 ms/DB-query tax (5×); health 0.9–1.9 s; retro-cause of the old 2.6 s cliff | §3.1 latencyMs, §3.3 matrix, §3.4 config | Switch runtime URL to `:5432` session pooler without `pgbouncer=true`; raise `connection_limit`; align local `.env` |
| 2 | **P1** | `connection_limit=1` head-of-line blocking: ~2.5–2.9 s DB stall window every TTL expiry / admin sync | health during refresh = 2,452 ms (§3.1) | Included in #1 (limit ≥ 5); optionally move refresh off-request path |
| 3 | **P2** | Post-deploy first catalog request: full rebuild (cache null) ≈ 2.8–3 s on current config + no SIGTERM drain; single replica | engine.ts `getCatalog(force/null)` path; cold-start partial evidence 1,727 ms | Fix #1 cuts it to ~1 s; optional: Railway healthcheck-driven warmup or prewarm-on-boot; graceful drain |
| 4 | **P2** | Font preloads not trimmed (MEC-20 claim unfulfilled): 9 woff2 = 99,900 B preloaded on every page; weight 500 used only by `/intel` | prod HTML preload list; layout.tsx:12; `font-medium` only in intel components | Drop weight 500 from Tajawal (map intel `font-medium`→`font-normal`/`font-semibold`), or split font config per route |
| 5 | **P3** | Catalog API still lacks ETag/304 (`max-age=30, swr=30` only) | §3.1 headers | Cheap `lastSyncAt`-based ETag (AGENT-8 #9) |
| 6 | **P3** | `/intel` eager 558 KB extra chunk (no `next/dynamic`) — unchanged | §3.5 | Lazy-load tabs (AGENT-8 #10) |
| 7 | **P3** | Dev/prod env parity gap: local `.env` DB config ≠ Railway runtime — masked the health issue through the entire MEC-20 local test suite | §3.4 | Same string in both; add a config-parity check to CI |

**Explicitly healthy:** warm-path TTFBs (network-bound), SWR cache behavior, static prerender + etag on pages, 404 handling, security headers (incl. CSP without `unsafe-eval`), rate limiting (no 429 at measurement volume), DB indexes (unchanged since AUDIT-8 PASS), payload sizes (13.3 KB catalog).

---

## 7. MEC-20 Claims Verification (this audit's scope)

| Claim | Status |
|---|---|
| engine.ts SWR stale-while-revalidate catalog cache | ✅ VERIFIED (measured: 230 ms first-hit-after-TTL vs 2,601 ms; TTL now 120 s) |
| Real circuit breaker (failCount/openUntil) | ✅ VERIFIED in code (live-mode only; runtime NOT VERIFIABLE in sandbox) |
| externalId passed to psPurchase | ✅ VERIFIED (engine.ts:262) |
| Apology cap | ✅ VERIFIED (24 h/phone) |
| Health endpoint added | ✅ VERIFIED (works; latency explained in §5) |
| Query logging disabled | ✅ VERIFIED (`log:['error','warn']`) |
| Font preloads trimmed | ❌ **NOT DONE** (9 preloads live; weight 500 still configured; only /intel uses it) |
| Deps pruned 48→14 | ✅ VERIFIED (package.json: 14) |

## 8. Limitations

1. Prod latencies measured from one sandbox location via edge `hkg1` (~180 ms floor); MENA UX will differ. Server-side costs isolated where possible via `latencyMs` and the local production-mode twin.
2. Cold tests measured the SWR stale-serve path only; the true post-deploy `catalogCache===null` full-rebuild path was NOT measured (requires restart — out of safety scope); its duration is inferred from the per-query tax (4 × ~713 ms) and the measured 2,452 ms refresh-contention window.
3. Circuit breaker and live-mode purchase path runtime-untestable (STORE_MODE=sandbox confirmed by health body: `mode:"sandbox"`).
4. Prisma parameter matrix ran from the sandbox (RTT ≈195 ms), not from Railway's origin; Railway per-query cost (713 ms) is measured via `latencyMs`, decomposition was done sandbox-side — magnitudes differ with RTT, conclusion (pgbouncer=true ⇒ per-query reconnect cost) is RTT-scaled and consistent across both.
5. Bundle sizes attributed via local `.next` files matched to production HTML hashes (all 11+3 chunks and 9 fonts matched; same BUILD_ID); no rebuild performed.
6. 47 prod GET/HEAD requests total (core batches within the 10-per-endpoint rule + 14 diagnostic single-shots); no writes, no secrets printed (Railway variable values masked at source; DB URL password never written to any file).

— MEC-21-D · 2026-09-28 · raw data: `/tmp/mec21d/*.tsv`, `prod_*.json/html/txt`, probes `prisma_probe.cjs`, `prisma_probe2.cjs`
