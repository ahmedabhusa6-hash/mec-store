# AGENT-7 — Security Threat Model Audit (MEC Store)

- **Task ID:** AUDIT-7 · **Date:** 2026-09-28 · **Scope:** authorized, safe/low-impact, read-only analysis + local black-box tests (no source modifications; prod limited to GET/HEAD)
- **Targets:** local `http://localhost:3000` (sandbox, same DB) + prod `https://mec-store-production.up.railway.app` (sandbox mode, verified via `GET /api`)
- **Secrets policy:** no secret values are printed anywhere in this report; references are file:line only.

---

## 1. Threat Model

### 1.1 Assets
| Asset | Location | Impact if compromised |
|---|---|---|
| Wallet balances (WalletTx sums, USD) | Supabase Postgres `Wallet`/`WalletTx` | Direct financial loss / free goods |
| Order PII (customer phone numbers) | `Order.phone`, `Waitlist.phone` | Privacy violation (CWE-359) |
| Delivered payloads (product codes) | `Order.deliveredPayload` | Theft of purchased goods |
| Admin APIs (`/api/admin/stats`, `/sync`) | Next route handlers | Supplier account data leak; 25s live syncs vs ProdSeller (supplier-ban/DoS) |
| ProdSeller API key (`PRODSELLER_API_KEY`, psk_…) | env / Railway variables | Wholesale account takeover, financial loss |
| Supabase DB (RLS on; anon/authenticated REVOKEd per prior audit) | Postgres | Full store compromise if creds leak |
| Storefront availability | Railway single replica | Revenue loss (no HA) |

### 1.2 Trust Boundaries
```
[Anonymous Browser] ──TLS──▶ [Railway hikari edge (hkg1)] ──▶ [Next.js 16.3.6 route handlers]
                                                                    │──▶ Supabase Postgres (service role via DATABASE_URL — RLS/REVOKE mitigate anon path)
                                                                    │──▶ ProdSeller API (X-API-Key, server-only)
                                                                    └─▶ In-memory rate limiter (per XFF IP)
[Admin token holder] ──x-admin-token──▶ admin routes (timing-safe compare)
```
Boundary crossings: (1) browser→Next API (all input untrusted: JSON bodies, query strings, `X-Forwarded-For`); (2) Next→Supabase (trusted service connection, parameterized via Prisma); (3) Next→ProdSeller (trusted, key server-side only — verified `src/lib/prodseller.ts:5` reads env, no client exposure).

### 1.3 Actors
- **Anonymous customer:** can call all store/wallet endpoints; identity = phone number (bearer-style); no accounts/passwords.
- **Admin token holder:** 46-char token (47 bytes incl. newline in `/tmp/admin_token.txt`); full supplier/order/PII visibility + live sync trigger.
- **Supabase roles:** anon/authenticated revoked (prior audit); app uses pooled service URL.
- **Network attacker:** controls headers (incl. XFF) at the Railway edge — see §5.

### 1.4 Entry Points (10 API routes + root)
`/api` (health, unguarded), `/api/store/catalog` (GET, catalog 60/min), `/api/store/checkout` (POST, 10/min), `/api/store/orders/[id]` (GET, generic 120/min), `/api/store/orders/[id]/restock` (POST, generic), `/api/store/payments/confirm` (POST, confirm 12/min), `/api/wallet` (GET, wallet_read 60/min), `/api/wallet/deposit` (POST, deposit 6/min), `/api/admin/stats` (GET, admin 30/min + token), `/api/admin/sync` (POST, admin 30/min + token).

### 1.5 Critical Flow — Checkout Money Path
`checkout` → server-side price lock (client price NEVER trusted — verified `checkout/route.ts:36-51`) → wallet rail: `walletBalance ≥ amountUsd` check → Order create → `credit(-amount)` → `routeOrder` (supplier chain, margin guard 0.9) → delivered: cashback 1% / failed: refund + $1 apology. TRC20/Binance rail: pending_payment order + payment address → `payments/confirm` marks paid → routes. Integrity controls: WalletTx `@@unique([walletId, type, ref])` gives DB-level idempotency for credit refs (`{publicId}-refund` etc.); confirm endpoint early-returns if `status !== "pending_payment"` (app-level idempotency). **Gap:** confirm has no STORE_MODE gate and no payment-proof/webhook signature (F5), and the status check is check-then-act (race, F5b).

---

## 2. Secrets Hygiene (tracked files only)

**Method:** `git ls-files -z | xargs -0 rg -l "ghp_|sbp_|psk_|AKIA|postgresql://|password\s*="` then per-file pattern identification; values never printed.

| # | Finding | Class | Severity |
|---|---|---|---|
| S1 | `.env` **is git-TRACKED** (`git ls-files --error-unmatch .env` → `.env`). Contains ADMIN_TOKEN, DATABASE_URL, DIRECT_DATABASE_URL, GITHUB_TOKEN, PRODSELLER_API_KEY, RAILWAY_TOKEN, STORE_MODE. Tracked since *Initial commit*; history includes 5 commits touching it. | **DEFECT [CWE-798]** | **P0** |
| S2 | Live ProdSeller API key embedded verbatim in tracked `scripts/prodseller_api_extract.py:19` (`API_KEY = "psk_…"`). **Confirmed identical to the active `PRODSELLER_API_KEY` in `.env`** (safe hash comparison, sha256 prefix `769564eabe16`). | **DEFECT [CWE-798]** | **P0** |
| S3 | Key prefix partially disclosed in tracked `worklog.md:328` ("psk_c139...") and mirrored in `tool-results/read_*.txt:328`. | DEFECT [CWE-522] | P2 |
| S4 | `scripts/db_fixes.py`, `scripts/db_audit.py`: `postgresql://` matches are a **regex parser** for a URL fetched at runtime from the Railway API via `RAILWAY_TOKEN` env var — no embedded secret. Hardcoded Railway PROJECT/ENV/SVC UUIDs (lines 9-11) = metadata, not credentials. | OBSERVATION | P3 |
| S5 | No `.env.example` exists (nothing to leak). `next.config.ts`, `package.json`, `public/` clean of secrets. `research/mec5/agent_c_raw/z2u_api_key.json` and offgamers HTML matches are third-party **public vendor docs** (scraped), not MEC credentials. | OBSERVATION | — |
| S6 | Client bundle check: no psk_/token literals in `src/components` or `src/app` (only Arabic UI text mentioning the token *name* in `store.tsx:630` and doc text `deep-dive.tsx:85`). ProdSeller key used server-side only. | TEST RESULT (PASS) | — |
| S7 | Mitigating factor: `git remote -v` is **empty** — no remote configured; repo not pushed. Exposure currently limited to this workspace. Does NOT cure history: any future `git push`/archive/sync leaks everything. | FACT | — |

**Verdict:** Suspected P0 **confirmed twice over** (.env tracked + live supplier key in tracked script). Rotate ProdSeller key + GITHUB_TOKEN, purge from history, `git rm --cached .env`, add `.env` to `.gitignore`.

---

## 3. AuthZ / IDOR Results (local + prod)

| Test | Request | Result | Class |
|---|---|---|---|
| A1 | `GET /api/admin/stats` no token | **401** (local + prod) | TEST RESULT (PASS) |
| A2 | `GET /api/admin/stats` garbage token | **401** | TEST RESULT (PASS) |
| A3 | `GET /api/admin/stats` valid token | **200**; fields recorded (names only): `mode, ps{balanceUsd,live,membership,username}, suppliers[], attemptStats[], orders{recent[], total}, syncs[], waitlistTotal`. `orders.recent` includes **full unmasked phone numbers** (route selects `phone: true`) — admin-authorized, acceptable but PII-bearing (CWE-200, P3). | TEST RESULT (PASS) |
| A4 | `POST /api/admin/sync` no/garbage token | **401/401** (prod GET → 405, non-sensitive) | TEST RESULT (PASS) |
| A5 | `GET /api/store/orders/MEC-LZZZZZZZZ` (nonexistent) | **404** `{"ok":false,"error":"الطلب غير موجود"}` — no stack, no diff between missing/malformed | TEST RESULT (PASS) |
| A6 | Order ownership: code review `orders/[id]/route.ts` — **NO phone/owner verification**. Anyone holding a `publicId` receives `payAddress, payAmount, deliveredPayload` (the product code!), `winner`, masked phone. `publicId` = `MEC-L` + 8 chars from 32-char alphabet via `Math.random()` (≈2^40, non-CSPRNG — F13). Enumeration infeasible at rate limits, but ID is a pure bearer secret with no second factor. Verified live: read my own test order fully unauthenticated. | **DEFECT/RISK [CWE-639]** | **P1** |
| A7 | Wallet read: `GET /api/wallet?phone=+966500000001` and `+967700000002` (two different phones, no auth) → **200 both, local AND prod**. Anyone who knows/guesses a victim's phone can read balance + last 50 transactions. Phone = bearer secret. | **DEFECT [CWE-639/209]** | **P1** |
| A8 | `GET /api/wallet?phone=123` / quote-injection phone | **400** clean | TEST RESULT (PASS) |
| A9 | `POST /api/store/payments/confirm {publicId}` — **unauthenticated payment confirmation**. No STORE_MODE check, no signature/proof. In sandbox this is the by-design "محاكاة" path; **in live mode the same code marks any known-publicId order paid and triggers real supplier purchase → free goods** (CWE-306). Idempotency: early-return if `status != pending_payment`; race remains (F5b): two concurrent confirms both pass the check → double `routeOrder` (double supplier spend in live); second refund `credit()` blocked by `@@unique([walletId,type,ref])` → throws 500. | **DEFECT [CWE-306 + CWE-367]** | **P1 (P0 at live go-live)** |
| A10 | Admin auth internals: fail-closed if token unset/<16 chars; custom `timingSafeEqual` correct constant-time loop; early length return leaks only length. Brute force: 46-char token, ≥62^46 space if random alnum — infeasible even unthrottled. Note: admin 30/min throttle is itself XFF-bypassable (§5) but entropy compensates. | FACT / RISK (P3) | — |

---

## 4. Input Validation Attack Results (local, low volume)

| Attack | Payload | Result | Class |
|---|---|---|---|
| V1 | Quote-injection phone `'+OR+1=1--` (checkout + wallet) | **400** clean (regex `^\+96[67]\d{8,9}$` strips/rejects) | TEST RESULT (PASS) |
| V2 | `__proto__` / `constructor.prototype` JSON keys (checkout) | Keys ignored (no deep merge into objects) → request proceeded to wallet-balance check → **402**; no pollution, no 500 | TEST RESULT (PASS) |
| V3 | 1MB body (1,048,661 B JSON, 1MB `pad` field) | **Accepted & processed** (402). No request-size cap on route handlers (Next App Router default = unlimited). Memory-exhaustion surface at scale; mitigated by rate limits (unless XFF-spoofed, §5). | OBSERVATION [CWE-400] P2 |
| V4 | Unicode/Bidi (`\u202E` etc.) in slug/phone | **400** `طلب غير صالح` | TEST RESULT (PASS) |
| V5 | Duplicate JSON keys (`slug`×2, `rail`×2) | `JSON.parse` last-wins → order created on `trc20` rail (sandbox, $0.82 pending). Standard parser semantics; no security impact. Test artifact documented below. | OBSERVATION P4 |
| V6 | Deposit `amountUsd` as `-5`, `1e308`, `"abc"`, `NaN` | **400** each (bounds 5–500, `Number.isFinite`) | TEST RESULT (PASS) |
| V7 | Deposit `amountUsd` as **string `"5"`** | **Accepted** via `Number()` coercion → credited $5 sandbox money to test phone. Loose typing; bounded; sandbox-only value. | OBSERVATION [CWE-20] P3 |
| V8 | XSS sinks: single `dangerouslySetInnerHTML` in `src/components/ui/chart.tsx:83` (shadcn) — injects CSS custom props from **developer-supplied ChartConfig**, not user input; component unused by app. API responses are `application/json` + `X-Content-Type-Options: nosniff` → no HTML reflection. React escaping elsewhere. | TEST RESULT (PASS) | — |
| V9 | SQLi: **zero** `$queryRaw`/`$executeRaw` in `src/` — all queries via Prisma parameterized API. | TEST RESULT (PASS) | — |
| V10 | No 500s / stack traces leaked in ANY test (all errors are clean Arabic 4xx JSON). | TEST RESULT (PASS) | — |

**Test artifacts created (all sandbox-simulated, no real value, no destructive ops):** wallets for test phones +966500000001 / +967700000002 / +966500000009; one $5 sandbox deposit credit on +966500000001; one sandbox order `MEC-L4W78XTHZ` (trc20, pending_payment, never confirmed). Team may purge at will.

---

## 5. Rate-Limiter Bypass Analysis (XFF)

**Code:** `src/lib/ratelimit.ts:22-29` — `clientIp()` = `x-forwarded-for` **first** element → `x-real-ip` → `"unknown"`.

**Local test (catalog bucket, 60/min):**
- 40 requests with `X-Forwarded-For: 1.2.3.4` → **40× 200**
- 40 requests with `X-Forwarded-For: 5.6.7.8` (same real client, same minute) → **40× 200** — i.e., 80 requests > 60/min cap from one client
- Control: +25 more on `1.2.3.4` → 20× 200, **5× 429** (cap fires exactly at 60 for that spoofed IP)

**Verdict:** [TEST RESULT] **Bypass mechanism CONFIRMED locally** — per-IP isolation keys on a client-suppliable header; rotating XFF values mints unlimited fresh buckets (checkout 10/min, deposit 6/min, confirm 12/min, admin 30/min all bypassable the same way). The limiter is also in-memory per-process → any future multi-replica/scale-out silently breaks it (worklog already notes numReplicas=1 dependency).

**Railway behavior:** edge is `railway-hikari` (`x-railway-edge: hkg1` observed). Whether hikari **overwrites** or **appends to** X-Forwarded-For could not be verified without prod limit-testing (excluded by rules — would require >60 rapid prod requests). **[ASSUMPTION]** Railway does not sanitize client-supplied XFF (community-reported behavior; append-model proxies leave the client's value as element #0, which is exactly what `clientIp()` reads). Under the overwrite-model the prod risk drops to P3; under append/pass-model it is P2 as tested. **Recommendation:** parse the **last** XFF element (proxy-appended client IP) or use Railway's connection-level IP (`request.headers.get('x-real-ip')` set by proxy, verified trust), and add a global (IP-agnostic) concurrency cap on money endpoints.

---

## 6. Headers Assessment (PROD, `curl -I`, 2026-09-28)

| Header | Present | Value | Assessment |
|---|---|---|---|
| CSP | ✅ | `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: blob: https:; connect-src 'self' …railway.app https://prodseller.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'` | Good baseline, but `script-src` allows **both `unsafe-inline` AND `unsafe-eval`** — effectively neutralizes CSP against script injection. `unsafe-eval` is typically unnecessary for a Next prod build; `unsafe-inline` can be replaced by nonces (Next supports via middleware). `img-src https:` allows any host. No `object-src` (falls back to `default-src 'self'` — acceptable). [OBSERVATION][CWE-693] P2 |
| HSTS | ✅ | `max-age=63072000; includeSubDomains; preload` | Excellent (2y + preload). |
| X-Frame-Options | ✅ | `DENY` | Good (redundant w/ `frame-ancestors 'none'` — fine). |
| X-Content-Type-Options | ✅ | `nosniff` | Good. |
| Referrer-Policy | ✅ | `strict-origin-when-cross-origin` | Good. |
| Permissions-Policy | ✅ | `camera=(), microphone=(), geolocation=()` | Good. |
| Misc | — | `server: railway-hikari`, no `X-Powered-By` (`poweredByHeader:false`) | Good fingerprint hygiene. |

**Compounding factor:** `store.tsx` UI stores the ADMIN_TOKEN in browser **localStorage** — any XSS (currently none found) + `unsafe-inline` CSP = admin token theft → full supplier-data access. Fix CSP → shrink blast radius. [RISK] P2.

---

## 7. Dependency Audit (isolated, `/tmp/agent7-npm`, no repo changes)

Method: copy `package.json` → `npm i --package-lock-only --ignore-scripts` → `npm audit --json`. **Repo itself has NO package-lock.json** (uses `bun.lock`) — immutability/supply-chain gap [OBSERVATION P3, CWE-1357].

**Totals: 4 HIGH · 0 critical · 0 moderate · 0 low** (57 deps incl. transitive in lockfile).

| Package (direct?) | Severity | Advisory | Fix |
|---|---|---|---|
| `prisma@^6.11.1` (direct) | high | via `@prisma/config` → `deepmerge-ts <8.0.0` — stack exhaustion merging recursive object graphs (DoS) | fix available (prisma upgrade) |
| `@prisma/config` (transitive) | high | same chain | fix available |
| `deepmerge-ts` (transitive) | high | stack exhaustion | 8.0.0 |
| `sharp@^0.34.3` (direct) | high | libvips CVE-2026-33327/33328/35590/35591 + libheif GHSA-g89c-p67h-r497, GHSA-2jg2-4ch7-h545 (untrusted image parsing → memory corruption/RCE class) | **sharp@0.35.5** (semver-major) |

Notes: `next@^16.3.6` clean (prior 2 critical RCEs already patched, per worklog 18-19). Exploitability: sharp only matters if `next/image` optimization serves attacker-controlled images (currently catalog is data-only — no user uploads found → practical exposure LOW, hence P2 not P1). deepmerge-ts path is build-time/config-time in Prisma, low runtime exposure.

---

## 8. Findings Summary Table

| ID | Finding | Class | Sev | CWE | Status |
|---|---|---|---|---|---|
| S1 | `.env` tracked in git with all 6 production secrets, since initial commit | DEFECT | **P0** | CWE-798 | CONFIRMED (FACT) |
| S2 | Live ProdSeller API key embedded in tracked `scripts/prodseller_api_extract.py:19`; verified == active key | DEFECT | **P0** | CWE-798 | CONFIRMED (FACT) |
| A9 | Unauthenticated `payments/confirm` (no mode gate, no signature) → free-order at live go-live; TOCTOU double-route race | DEFECT | **P1 (P0 live)** | CWE-306/367 | CONFIRMED (code+test) |
| A7 | Wallet balance+history readable for ANY phone, no auth (prod verified 200) | DEFECT | **P1** | CWE-639 | CONFIRMED (TEST RESULT) |
| A6 | Order details incl. `deliveredPayload`/`payAddress` readable with publicId only; no owner proof | DEFECT | **P1** | CWE-639 | CONFIRMED (TEST RESULT) |
| F6 | Rate limiter keyed on spoofable XFF[0] — bypass mechanism confirmed locally; Railway sanitization UNVERIFIED | DEFECT/RISK | **P2** | CWE-348 | CONFIRMED local; prod ASSUMPTION |
| F7 | CSP `unsafe-inline`+`unsafe-eval` in script-src; admin token in localStorage | OBSERVATION | P2 | CWE-693 | CONFIRMED (prod headers) |
| V3 | No request body size cap (1MB accepted) | OBSERVATION | P2 | CWE-400 | CONFIRMED (TEST RESULT) |
| DEP | 4 high vulns (prisma chain DoS; sharp libvips/libheif) — no package-lock.json in repo | DEFECT | P2 | CWE-1104/1357 | CONFIRMED (npm audit) |
| S3 | Key prefix leak in worklog.md:328 + tool-results mirrors | DEFECT | P2 | CWE-522 | CONFIRMED |
| A3 | admin/stats exposes full unmasked phones (authorized admin only) | OBSERVATION | P3 | CWE-200 | CONFIRMED |
| V7 | Deposit amount accepted as string (Number coercion) | OBSERVATION | P3 | CWE-20 | CONFIRMED |
| F12 | Unauthenticated wallet-row creation via upsert (DB bloat, XFF-bypassable) | RISK | P3 | CWE-770 | CONFIRMED |
| F13 | `genPublicId` uses `Math.random()` (non-CSPRNG), ~2^40 space | RISK | P3 | CWE-338 | CONFIRMED (UNCONFIRMED practicality) |
| F14 | LIVE_TRC20_ADDR fallback string "SET-LIVE-TRC20-ADDRESS" if env unset in live mode | RISK | P3 | CWE-1188 | CONFIRMED (code) |
| RL2 | In-memory limiter breaks silently if replicas > 1 | RISK | P3 | — | CONFIRMED (design) |
| S4 | Railway project/env/service UUIDs hardcoded in tracked scripts | OBSERVATION | P3 | — | CONFIRMED |
| PASS | Admin gate (401/401/200 local+prod), fail-closed, constant-time | TEST RESULT | — | — | PASS |
| PASS | Input validation battery (V1,V2,V4,V6): clean 4xx, no pollution, no 500s, no stack leaks | TEST RESULT | — | — | PASS |
| PASS | No raw SQL (Prisma only) → SQLi N/A | TEST RESULT | — | — | PASS |
| PASS | No secrets in client bundle / next.config / package.json / public | TEST RESULT | — | — | PASS |

---

## 9. Remediation Plan (priority order)

1. **[P0] Secret rotation + purge (S1/S2/S3):** rotate ProdSeller API key (psk_) and GITHUB_TOKEN immediately; `git rm --cached .env scripts/prodseller_api_extract.py` (or scrub line 19), add to `.gitignore`; rewrite history (`git filter-repo`) before any remote is ever added; scrub worklog/tool-results key-prefix mentions.
2. **[P1] Confirm endpoint (A9):** require webhook signature/HMAC or out-of-band verification before honoring `payments/confirm` in live mode; hard-gate sandbox simulation on `STORE_MODE === "sandbox"`; make the status transition atomic (`updateMany({where:{id, status:"pending_payment"}})` + check count) to kill the TOCTOU race.
3. **[P1] Wallet/Order BOLA (A6/A7):** require a one-time OTP or order-token (returned only at creation) for order/wallet reads; at minimum stop returning `deliveredPayload`/`payAddress` without possession proof, and consider masking tx notes; rate-limit wallet enumeration per IP *and* global.
4. **[P2] Rate limiter (F6):** use proxy-trusted IP (last XFF element / x-real-ip as set by Railway) + per-endpoint global caps independent of IP; document replica assumption.
5. **[P2] CSP (F7):** drop `unsafe-eval`; move to nonce-based script-src via middleware; move admin token out of localStorage (session-scoped memory / cookie).
6. **[P2] Deps (DEP):** `sharp@0.35.5`, prisma upgrade path; commit a lockfile (bun.lock exists — keep `npm audit`/`bun audit --audit-level=high` in CI).
7. **[P3]** body-size cap (e.g., 64KB), `crypto.randomUUID`-style publicId or longer alphabet, reject non-number `amountUsd` (`typeof === "number"`), fail-fast if `LIVE_TRC20_ADDRESS` unset in live mode, cap wallet auto-creation.

## 10. Residual Risks
- Railway XFF sanitization unverified (ASSUMPTION) — treat money-endpoint limits as untrusted until fixed.
- Git history still contains all secrets until history rewrite; rotation is the only complete remedy.
- Single-replica availability (DoS = downtime) accepted by platform choice.
- Sandbox money/PII test artifacts (documented §4) exist in DB.
- Admin PII panel + supplier balance visibility remains high-value if ADMIN_TOKEN leaks (rotation cadence absent).

---
*Generated by AUDIT-7. All tests were safe, low-volume, local-first; production limited to GET/HEAD. No source files modified.*
