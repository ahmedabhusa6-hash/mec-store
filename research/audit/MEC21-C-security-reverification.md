# MEC-21-C — Security Re-verification of MEC-20 Fixes (Independent Regression Test)

- **Task ID:** MEC-21-C · **Agent:** Security Re-verification & Regression Specialist (Team 04) · **Date:** 2026-09-28 ~13:00–13:20 UTC
- **Method:** independent black-box re-test of every MEC-20 security fix + targeted source review + git/GitHub history forensics. Production limited to GET/HEAD. All mutations on `http://localhost:3000` (sandbox, shared prod Supabase DB). No source files modified.
- **Secrets policy:** no secret values printed anywhere; hash prefixes (sha256[:12]) and masked tokens only.
- **Test artifacts created (all mine, sandbox, minimal):** 2 orders (`MEC-LBJNBEHFD` delivered $0.27; `MEC-LY2EM8WX2` pending $0.27/USDT-payable $1.10) on fresh phone `+966599173426`; wallet rows auto-created for `+966599173426` + `+966577000483` (by unauth wallet reads); 1 authorized admin sync (6.7s, changed 1 product); 220 invalid-body deposit POSTs (no DB writes).

---

## 1. Executive Verdict

**MEC-20's security work is mostly real and holds up under independent re-testing — but not completely.** Of the 9 fix areas re-tested: **5 VERIFIED FIXED, 3 PARTIALLY FIXED, 1 STILL BROKEN (open defect)**, plus **one new P1-grade discovery**: the *live* ProdSeller API key and the *live* RAILWAY_TOKEN remain recoverable from the **GitHub remote's git history** (hash-verified via GitHub API) — MEC-20 scrubbed the current tree but pushed the full tainted history, contradicting its "unrelated histories / remote never had secrets" claim. The wallet enumeration P1 was never fixed and now provides a 2-hop bypass of the (otherwise working) order-IDOR fix: *phone → wallet/history endpoints → publicId → full order detail incl. deliveredPayload*.

**Recommended immediate actions (order matters):**
1. **Rotate ProdSeller API key + RAILWAY_TOKEN now** (only complete cure for history exposure), then purge history (`git filter-repo` + force-push) — repo is **private** (verified), which is the only reason this is P1 and not P0-live.
2. Close wallet/history phone-bearer exposure (OTP or token returned at first interaction; at minimum stop unauthenticated cross-phone reads).
3. Carry W2 (live payment webhook verification) into go-live gate — confirm's live-mode hardening is code-verified only.

---

## 2. Per-Fix Verification Table

| # | Defect (orig. sev) | Test performed | Result | Status | Evidence |
|---|---|---|---|---|---|
| 1 | Catalog cost leak (P0) | `GET /api/store/catalog` local + prod; full JSON key-scan for `costUsd`/`"cost"`/`checkedAt`/`stockCheckedAt`; product/chain key enumeration; md5 parity | 37/37 products both envs, **byte-identical (md5 7f7658d3…)**; **0 occurrences** of costUsd/cost/checkedAt; chain entries = `{supplier,name,stock}` — **`stock` per supplier still exposed** + top-level `lastSyncAt` (derived from stockCheckedAt). The P0 margin leak (costUsd) is gone. | **PARTIALLY FIXED** (core P0 fixed; residual stock/lastSyncAt = P3 intel) | §3.1 |
| 2 | Order IDOR (P1) | (a) random publicId; (b) created 1 sandbox TRC-20 order (fresh phone) → GET without phone; (c) with wrong phone; (d) with correct phone; (e) case-tampered publicId | (a) 404 · (b) **404 (denial, identical error — no existence oracle)** · (c) 404 · (d) **200 full data** (payAddress, payAmount, status) · (e) 404. Owner-proof enforced (route: `!order || !phone || phone !== order.phone → 404`). Restock route has same guard (code-verified). | **VERIFIED FIXED** (with chained-bypass caveat → §4.2) | §3.2 |
| 3 | Wallet enumeration (P1) | `GET /api/wallet?phone=` with (a) my fresh phone, (b) random unregistered phone, (c) prior-audit phone `+966500000001` (documented artifact) | (a) **200** balance+txs · (b) **200** `{balance:0,txs:[]}` **and silently creates a wallet row** · (c) **200 with real balance $5, 1 tx** — zero ownership proof. New `GET /api/store/orders?phone=` (history) has the same model and returns full publicId list. | **STILL BROKEN — REGRESSION (open defect, P1)** | §3.3, §4.2 |
| 4 | payments/confirm unauth + no mode gate (P0-live) | (a) confirm own pending order w/ fabricated txid; (b) double-confirm; (c) wrong publicId; (d) missing publicId; source review of mode gate + atomic claim | (a) **200 delivered** (sandbox simulation — by design, fabricated txid accepted) · (b) **200 `{status:"delivered", idempotent:true}`** — no second routing · (c) **404** · (d) **400**. Mode gate: `STORE_MODE !== "sandbox" → 403` (confirm/route.ts:24-29) — **code-verified only** (not black-box testable without env change). Atomic claim = conditional `updateMany({where:{id,status:"pending_payment"}})` — code-verified + sequential idempotency proven. | **VERIFIED FIXED (sandbox scope)** — live-mode webhook verification (W2) still pending; gate itself NOT VERIFIABLE black-box | §3.4 |
| 5 | Rate-limit XFF bypass (P2) | Test A: 30 rapid `POST /api/wallet/deposit` (invalid body → 400, no DB) across 3 spoofed XFF IPs. Test B (after 70s): 190 requests across 40 spoofed IPs (≤5/IP so per-IP cap never fires) | Test A: **18×400 + 12×429** — per-spoofed-IP exactly 6 allowed + 4 denied each (per-IP bucketing still keys on XFF[0]; rotation still mints buckets; global cap not reached at 30). Test B: **180×400 + 10×429, first 429 at request #181** — global backstop fired at exactly `limit×30 = 180/min` for deposit, **regardless of IP rotation**. | **VERIFIED FIXED** (global backstop works as designed; bounded, not eliminated — see §5 R-4) | §3.5 |
| 6 | Admin gate | Local: `POST /api/admin/sync` no-token / wrong-token / correct-token (read from .env, masked); `GET /api/admin/sync`; `GET /api/admin/costs` no/wrong/correct; `GET /api/admin/stats` no-token. Prod (GET only): costs/stats no-token | sync: **401 / 401 / 200** (real sync 6.7s, `productsSeen:25, matched:20, changed:1`) · GET sync → **405** · costs: **401 / 401 / 200** (37 products with costUsd — properly gated companion to fix #1) · stats no-token **401** · **prod costs 401, prod stats 401**. Fail-closed + timing-safe compare intact (admin-auth.ts). | **VERIFIED FIXED** | §3.6 |
| 7 | Security headers (prod) | `curl -sI https://mec-store-production.up.railway.app/` | HSTS `max-age=63072000; includeSubDomains; preload` ✓ · X-Frame-Options `DENY` ✓ · CSP present, **`unsafe-eval` REMOVED** ✓ (`unsafe-inline` remains in script-src/style-src) with `frame-ancestors 'none'; base-uri 'self'; form-action 'self'` · XCTO `nosniff` ✓ · Referrer-Policy `strict-origin-when-cross-origin` ✓ · Permissions-Policy `camera=(), microphone=(), geolocation=()` ✓ · no X-Powered-By ✓ | **VERIFIED FIXED** (unsafe-eval removal confirmed; unsafe-inline residual R-6) | §3.7 |
| 8 | Secrets hygiene (P0) | (a) `git ls-files` .env check; (b) tracked-file sweep for ghp_/sbp_/psk_/postgresql:// + ADMIN_TOKEN literal check in src/+prisma/; (c) health response; (d) **git history + GitHub API blob forensics** (hash-compare only) | (a) `.env` NOT tracked (0), gitignored ✓ — **but present in 6 local-history commits**; (b) src/+prisma/ **clean** (env refs only) ✓; full live psk_ key absent from ALL current tracked files ✓ (S2 scrubbed); (c) health = `{ok,service,mode,db,latencyMs,time}` — no internals (benign `service` label only); (d) **NEW: GitHub remote history contains live secrets** — see §4.1 | **PARTIALLY FIXED** (tree clean; history NOT purged — local AND remote) | §3.8, §4.1 |
| 9 | Input validation regression | (a) checkout w/ tampered `price:0.01, priceUsd:-5, amount:0` (trc20); (b) phone `'+OR+1=1--`; (c) 1,048,668-byte body | (a) **server re-priced from DB**: payAmount $1.10 = $0.27 + cents marker 83 — client price fields fully ignored (order `MEC-LY2EM8WX2` = test artifact) · (b) **400** clean · (c) 1MB body **accepted & parsed** (400 on invalid rail, no order) — size cap still absent (P2 residual, unchanged, now bounded by global rate backstop) | **VERIFIED (no regression)** | §3.9 |

**Scorecard: 5 VERIFIED FIXED · 3 PARTIALLY FIXED · 1 STILL BROKEN · 0 fabricated** (fix #4's mode-gate and #8's history dimension carry NOT-VERIFIABLE-black-box components, documented as such).

---

## 3. Test Evidence Detail

### 3.1 Catalog (local + prod)
```
products: 37 (both) | ok:true | mode:sandbox | md5 local == md5 prod (7f7658d3951a8a39e8e80115ed69f326)
occurrences of 'costUsd': 0 · '"cost"': 0 · 'checkedAt': 0 · 'stockCheckedAt': 0
product keys: [chain, family, name, officialUsd, prices, slug, sourceTier]
chain[0] keys: [name, stock, supplier]          <-- stock STILL present (design choice, engine.ts:22)
top-level keys: [families, lastSyncAt, mode, ok, products]   <-- lastSyncAt derived from stockCheckedAt
```
Cost data now only via gated `GET /api/admin/costs` (verified 200 w/ token, 401 without — e.g. adobe-express-12m → ps costUsd $0.35, matching AUDIT-8's originally-leaked value).

### 3.2 Order IDOR
```
GET /api/store/orders/MEC-LZZZZZZZZ                     → 404
POST checkout {capcut-pro-6-days-fw, +966599173426, trc20} → 200 publicId=MEC-LBJNBEHFD payAmount=$0.62 (SAR1→$0.27+¢35)
GET /api/store/orders/MEC-LBJNBEHFD                     → 404  (no phone)
GET …?phone=+966588420917 (wrong owner)                 → 404
GET …?phone=+966599173426 (owner)                       → 200  full order (payAddress TMECSandbox000000C7Y, status, amounts)
GET /api/store/orders/mec-lbjnbehfd?phone=<owner>       → 404  (case-tampered)
```
Error text identical for not-found vs not-owner → no existence oracle. `deliveredPayload` only reachable with correct phone.

### 3.3 Wallet enumeration (STILL BROKEN)
```
GET /api/wallet?phone=+966599173426  (mine)     → 200 {balance:0, txs:[]}
GET /api/wallet?phone=+966577000483  (random)   → 200 {balance:0, txs:[]}   + silently CREATEs wallet row (upsert)
GET /api/wallet?phone=+966500000001 (prior-audit artifact) → 200 balance=$5, tx_count=1, tx fields incl. `ref`
```
`src/app/api/wallet/route.ts:17` — `getOrCreateWallet(phone)` with **zero ownership proof**; phone is a pure bearer secret. Same for the NEW `GET /api/store/orders?phone=` history endpoint (returns publicId list). See §4.2 for the chain.

### 3.4 payments/confirm
```
POST confirm {MEC-LBJNBEHFD, txid:"0x fab ric ated…"} → 200 {delivered, winner:ps, cashback:0}   (sandbox simulation)
POST confirm {MEC-LBJNBEHFD, txid:"0xsecond…"}        → 200 {status:delivered, idempotent:true}  (no re-route)
POST confirm {MEC-LTAMPERED9,…}                       → 404
POST confirm {txid only}                              → 400
```
Mode gate (code, confirm/route.ts:24-29): `STORE_MODE !== "sandbox"` → 403 «التأكيد اليدوي معطّل في الوضع الحي…». Atomic claim (route.ts:60-67): `updateMany({where:{id, status:"pending_payment"}})` + `count===0 → idempotent return` — kills the TOCTOU double-route. Concurrent race not re-runnable (single order, already claimed); DB-conditional update is atomic by construction.

### 3.5 Rate-limit XFF bypass — global backstop
Config (src/lib/ratelimit.ts): per-IP buckets keyed on XFF[0] (unchanged by design) + **global per-bucket cap = limit×30** (deposit 180/min, checkout 300/min, confirm 360/min).
```
TEST A (30 req, 3 spoofed IPs 1.2.3.4/5.6.7.8/9.10.11.12, round-robin):
  total: 18×400 + 12×429 | per-IP: exactly 6×400 + 4×429 each
  → per-IP buckets still keyed on spoofed XFF; rotation still mints buckets; global not reached at n=30

TEST B (190 req, 40 distinct spoofed 10.x.y.z IPs, ≤5 hits/IP so per-IP cap NEVER fires):
  180×400 + 10×429 | FIRST 429 at request #181
  → global cap triggered at exactly deposit(6)×30 = 180/min — 429 regardless of XFF rotation ✓
```

### 3.6 Admin gate
```
local POST /api/admin/sync  no token → 401 | wrong → 401 | correct (masked me***) → 200 {ok, productsSeen:25, matched:20, changed:1, latencyMs:6725}
local GET  /api/admin/sync           → 405 (method gate, non-sensitive)
local GET  /api/admin/costs no/wrong → 401 / 401 | correct → 200 (37 products, costUsd present — gated)
local GET  /api/admin/stats no token → 401
PROD (GET only) costs → 401 | stats → 401
```
One real sync executed as side effect (documented; same as AUDIT-10/MEC-20 precedent).

### 3.7 Production headers (full values)
```
strict-transport-security: max-age=63072000; includeSubDomains; preload
x-frame-options: DENY
content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
  font-src 'self' data:; img-src 'self' data: blob: https:; connect-src 'self' https://mec-store-production.up.railway.app https://prodseller.com;
  frame-ancestors 'none'; base-uri 'self'; form-action 'self'      ← NO unsafe-eval ✓
x-content-type-options: nosniff
referrer-policy: strict-origin-when-cross-origin
permissions-policy: camera=(), microphone=(), geolocation=()
server: railway-hikari | x-powered-by: absent
```

### 3.8 Secrets hygiene
```
git ls-files | grep -c '^\.env$'            → 0  ✓ (.env gitignored)
src/+prisma/ scan ghp_/sbp_/psk_/postgresql:// → 0 hits ✓
ADMIN_TOKEN in src/prisma → process.env refs + UI text only, no literals ✓
/api/health (local+prod) → {ok, service:"mec-store", mode, db, latencyMs, time} — no internals ✓
live psk_ key (sha256[:12]=769564eabe16) NOT in any current tracked file ✓ (S2 scrubbed)
BUT: .env blobs in 6 local-history commits (a5ab8d0…0e08876); prefix "psk_c139***" still in tracked
     worklog.md:328 + 15 tool-results files (current tree) — and in remote history
```

### 3.9 Input validation
```
checkout {price:0.01, priceUsd:-5, amount:0} → 200, payAmount $1.10 (server price: SAR1→$0.27 + ¢83 marker) — client price ignored
checkout phone "'+OR+1=1--"                  → 400 «بيانات ناقصة…»
checkout 1,048,668-byte JSON                 → parsed, 400 (invalid rail) — no size cap (P2 residual)
```

---

## 4. New Findings (this round)

### 4.1 [P1 — NEW, confirmed] Live secrets recoverable from GitHub remote git history
**Evidence chain (all hash-compared, values never printed):**
1. `origin/main` (9f5787b "MEC-20: audited, hardened, optimized release") — its **history includes the full local commit chain** (a5ab8d0 → … → 0e08876 → 52d82a1), i.e. the push was **NOT** an "unrelated histories" whitelist push as MEC-20's worklog claims; only the **tip tree** was whitelisted.
2. Historical blob `fb9525efe32…` of `scripts/prodseller_api_extract.py` (in commits 26844e23, 0e088762) **contains the LIVE ProdSeller API key** — verified locally AND **fetched back from the GitHub API** (`GET /repos/…/git/blobs/fb9525efe32…` → contains live key: **True**, sha256[:12]=769564eabe16, len 52).
3. Historical `.env` blob `12dd54f5…` (commit 0e08876) contains `RAILWAY_TOKEN` **identical to the current live value** (len 36) + an older 33-char GITHUB_TOKEN (≠ current) + a local `file:` DATABASE_URL (not a secret). Older blobs: NOTION_TOKEN (old) + file: URLs only. **Current** ADMIN_TOKEN/PRODSELLER_API_KEY/supabase URLs were never committed.
4. Repo visibility: **private** (authenticated API check) — the only factor keeping this at P1.

**Impact:** anyone with read access to the private repo (collaborator, leaked GitHub token, account compromise, future visibility flip) recovers the **active supplier key** (wholesale account takeover / financial loss) and the **active Railway token** (infra control). MEC-20 claims "secret removal" and "Remote .env never existed (verified)" are true only for the current tree — the remediation is **incomplete and its verification was too shallow**.
**Fix:** rotate ProdSeller key + RAILWAY_TOKEN immediately (only complete cure), then `git filter-repo` purge + force-push; verify old GITHUB_TOKEN (33-char) is revoked; scrub psk_c139 prefix from tracked worklog/tool-results.

### 4.2 [P1 — chained bypass of fix #2] Phone-bearer endpoints restore full order exposure
`GET /api/wallet?phone=` (balance + full tx list, refs contain `{publicId}-purchase/-cashback`) and the NEW `GET /api/store/orders?phone=` (returns publicId list) require **no ownership proof**. Chain with the fixed order endpoint: *know only the victim's phone → read balance/txs → extract publicId from refs (or history list) → `GET /api/store/orders/{publicId}?phone={victim}` → 200 incl. `deliveredPayload`, `payAddress`.* The IDOR fix's effective strength collapses to "attacker must know the phone" — which these same endpoints hand out. Also enables unauthenticated wallet-row creation (DB bloat, original F12 — verified: random phone GET created a row) and balance existence-oracle for any Saudi/Yemeni number.

### 4.3 Minor observations
- **[P3]** Deposit still coerces `amountUsd` via `Number()` — string `"5"` accepted (deposit/route.ts:19; original V7 unchanged).
- **[P3]** `LIVE_TRC20_ADDR` fallback `"SET-LIVE-TRC20-ADDRESS"` still fail-open if env unset in live mode (checkout/route.ts:10; original F14 unchanged).
- **[P3]** Admin token still stored in browser localStorage (store.tsx UI text confirms) — compounds with residual CSP `unsafe-inline`.
- **[P3]** Catalog still exposes per-supplier `stock` + `lastSyncAt` (supplier inventory intel).
- **[P4]** `buckets.clear()` at 50k per-IP keys: XFF-flooding an attacker can wipe all per-IP buckets (limit reset for everyone); global backstop unaffected.
- **[P4]** `/api/health` discloses `service:"mec-store"` label (benign, noted for completeness).
- **[INFO]** One admin sync side effect: 1 product changed (live sync, authorized, documented).

---

## 5. Residual Risk Register

| ID | Risk | Sev | Exposure condition | Owner action |
|---|---|---|---|---|
| R-1 | Live ProdSeller key + live RAILWAY_TOKEN in GitHub remote history (private repo) | **P1** (→P0 if repo public/shared) | Repo read access / visibility flip / token leak | Rotate both keys NOW; filter-repo purge + force-push; revoke old GITHUB_TOKEN |
| R-2 | Wallet + order-history endpoints = phone-bearer (no ownership proof) → chained bypass of IDOR fix | **P1** | Attacker knows/guesses victim phone | OTP or per-phone token at first interaction; stop unauth cross-phone reads; mask tx refs |
| R-3 | payments/confirm live-mode: no webhook signature/on-chain verification yet (W2); mode gate code-verified only | P1-at-go-live | STORE_MODE=live | Implement W2 verification before live; add live-mode gate integration test |
| R-4 | Rate limiter: per-IP attribution still trusts XFF[0]; global caps = 30× nominal (checkout 300/min, confirm 360/min spoofable); in-memory single-replica | P2 | Coordinated abuse w/ header rotation | Parse trusted proxy IP (last XFF hop / x-real-ip); lower global caps on money endpoints |
| R-5 | No request body size cap (1MB+ accepted) | P2 | Memory pressure at scale | 64KB body cap on JSON routes |
| R-6 | CSP `unsafe-inline` (script+style); admin token in localStorage | P2 | Any future XSS | Nonce-based CSP; move token out of localStorage |
| R-7 | psk_c139 prefix in tracked worklog.md:328 + 15 tool-results files (also in remote history) | P3 | Repo read access | Scrub prefix mentions |
| R-8 | Deposit string-coercion; LIVE_TRC20_ADDR placeholder fallback; catalog stock/lastSyncAt; buckets.clear() wipe; `service` label in health | P3–P4 | Various | Backlog hygiene items |

---

## 6. Test Budget Compliance
- Production: **GET/HEAD only** (catalog, health, headers, admin no-token 401s, repo-visibility API GET, blob GET) — zero mutations. ✅
- Local sandbox orders: **2** (both on one fresh phone, cheapest product $0.27). ✅
- No token/key values printed (hashes/masks only). ✅
- No DoS: max burst 190 sequential lightweight requests, local only, invalid bodies (no DB writes). ✅
- No data extraction beyond own records + one documented prior-audit artifact phone (balance aggregate only). ✅
- Source files: **none modified**. Writes: this findings file + worklog append only. ✅

---
*Generated by MEC-21-C. Every result above was actually executed and observed; nothing is inferred from MEC-20 claims without independent re-test (exceptions explicitly marked "code-verified only").*
