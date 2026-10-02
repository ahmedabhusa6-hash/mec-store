# AGENT-10 — QA, Testing & Independent Verification Report

- **Task ID:** AUDIT-10
- **Agent:** AUDIT-10 (Independent QA / Release-Gate Verification)
- **Date:** 2026-09-28 (11:54–12:01 UTC)
- **Target:** Local `http://localhost:3000` (sandbox, same DB as prod) + Production `https://mec-store-production.up.railway.app` (GET/HEAD only)
- **Method:** REAL execution — curl HTTP transcripts + real browser E2E (agent-browser/Playwright) + API arithmetic verification. **No source modifications.**
- **Purpose:** Independent re-verification of prior session (worklog "18-19") claim of 23/23 PASS after hardening.

---

## 1. Test Strategy — Release-Gate Acceptance Criteria

| Gate | Area | Acceptance Criteria | Method |
|------|------|---------------------|--------|
| G1 | Smoke (local) | `/` 200 + `dir="rtl"` + `lang="ar"`; `/intel` 200; catalog 200 `ok:true` + products; unknown route 404 **Arabic**; `/api` 200 | curl + grep |
| G2 | Security headers (prod) | ALL 6 present: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy | `curl -sI` (1 request, low volume) |
| G3 | Admin gate (local) | no token → 401; wrong token → 401; correct token → 200 (field names only recorded) | curl with/without `x-admin-token` |
| G4 | E2E sandbox purchase (local) | register → deposit → buy → **DELIVERED** with **SANDBOX-marked receipt** → cashback 1% credited; wallet balance = deposit − price + cashback (exact arithmetic) | real browser + API cross-check |
| G5 | Rate limit (local only) | 15 rapid checkout POSTs (isolated X-Forwarded-For): first 10 = 4xx validation, then 429; after 65s wait → non-429 | curl burst |
| G6 | Admin sync (local) | POST with token → 200 + summary; `lastSyncAt` in catalog changes | curl before/after |
| G7 | Console health (E2E) | Zero console/page errors during browser journey | agent-browser console/errors |

---

## 2. Results Table (38 checks — evidence referenced inline)

| ID | Description | Expected | Actual | Verdict | Evidence |
|----|-------------|----------|--------|---------|----------|
| SMOKE-1 | GET `/` (local) | 200 + RTL + Arabic | 200; `dir="rtl"`; `lang="ar"` | **PASS** | curl transcript §3.1 |
| SMOKE-2 | GET `/intel` (local) | 200 | 200; contains `dir="rtl"` | **PASS** | `smoke_intel.html` |
| SMOKE-3 | GET `/api/store/catalog` (local) | 200, ok:true, products | 200 in 9ms; `ok:true`; mode `sandbox`; **37 products**; 4 families; lastSyncAt 2026-09-28T10:53:40Z | **PASS** | `smoke_catalog.json` |
| SMOKE-4 | GET `/xyz` (invalid route) | 404 + Arabic | 404; body: «هذه الصفحة غير موجودة… يمكنك العودة للمتجر أو استعراض لوحة الاستخبارات» + `dir="rtl"` | **PASS** | `smoke_404.html` |
| SMOKE-5 | GET `/api` root | informative JSON | 200 `{"ok":true,"service":"mec-store","mode":"sandbox","time":…}` | **PASS** | §3.1 |
| SEC-1 | Prod security headers | all 6 present | **6/6 present** (exact values §3.2) | **PASS** | `prod_headers.txt` |
| PROD-1 | Prod `/api` alive (low volume) | 200 | 200, mode sandbox | **PASS** | §3.2 |
| PROD-2 | Prod catalog alive (low volume) | 200 + products | 200 in 0.21s; 37 products | **PASS** | `prod_catalog.json` |
| ADM-1 | `/api/admin/stats` no header | 401 | 401 «غير مصرح — لوحة التشغيل تتطلب مفتاح تشغيل صحيحًا» | **PASS** | §3.3 |
| ADM-2 | `/api/admin/stats` wrong token | 401 | 401 | **PASS** | §3.3 |
| ADM-2b | `/api/admin/stats` short token | 401 (fail-closed) | 401 | **PASS** | §3.3 |
| ADM-3 | `/api/admin/stats` correct token | 200 | 200; top-level fields: `attemptStats, mode, ok, orders, ps, suppliers, syncs, waitlistTotal`; 6 suppliers; orders.total 31; 2 syncs | **PASS** | §3.3 (values not recorded — sensitive) |
| ADM-4 | `/api/admin/sync` POST no token | 401 | 401 | **PASS** | §3.3 |
| ADM-5 | `/api/admin/sync` GET | 405 | 405 «Method Not Allowed — استخدم POST» | **PASS** | §3.3 |
| VAL-1 | checkout `{}` | 400 | 400 «بيانات ناقصة: slug + جوال صحيح مطلوبان» | **PASS** | §3.4 |
| VAL-2 | checkout bad phone `+1234567890` | 400 | 400 (tight regex rejects) | **PASS** | §3.4 |
| VAL-3 | checkout bad rail `paypal` | 400 | 400 «وسيلة دفع غير مدعومة» | **PASS** | §3.4 |
| VAL-4 | checkout unknown slug | 404 | 404 «المنتج غير موجود» | **PASS** | §3.4 |
| VAL-5 | wallet bad phone | 400 | 400 «جوال صحيح مطلوب (+966/+967)» | **PASS** | §3.4 |
| VAL-6 | deposit $3 (< min $5) | 400 | 400 «الإيداع بين $5 و$500 (حدود W1)» | **PASS** | §3.4 |
| VAL-7 | deposit $501 (> max $500) | 400 | 400 | **PASS** | §3.4 |
| VAL-8 | order unknown id | 404 | 404 «الطلب غير موجود» | **PASS** | §3.4 |
| VAL-9 | confirm unknown order | 404 | 404 | **PASS** | §3.4 |
| E2E-1 | Store home renders catalog | grid + buy buttons | 37 products; out-of-stock items (e.g. ChatGPT Plus) show **disabled** «نفد — فعّل تنبيه التوفير» | **PASS** | `agent10-01-home.png` |
| E2E-2 | Register phone `+96651110001` | SA region applied | region badge 🇸🇦 السعودية; SA prices shown | **PASS** | `agent10-02-phone-registered.png` |
| E2E-3 | Sandbox deposit $25 | balance $25.00 | balance $25.00; tx `deposit +25.00 (dep-mul6xbwj)` | **PASS** | `agent10-03-wallet-deposit.png` + §3.5 |
| E2E-4 | Checkout form (Canva Pro 2 yrs FW) | locked price | 4 ر.س (≈$1.07) «هذا السعر مقفول لطلبك»; wallet rail shows $25.00 / $1.07 | **PASS** | `agent10-04-checkout-form.png` |
| E2E-5 | Wallet purchase → DELIVERED | delivered + SANDBOX receipt | Order `MEC-LMQQ6VHS5`: status `delivered`, winner `ps`, receipt «SANDBOX-RECEIPT • Canva Pro 2 yrs FW • via ProdSeller • … • محاكاة تسليم» | **PASS** | `agent10-05-order-delivered.png` + §3.5 |
| E2E-6 | Cashback 1% purchase 1 | $0.01 | `cashback +0.01 (MEC-LMQQ6VHS5-cashback)`; UI «كاش باك 1% = $0.01» | **PASS** | §3.5 |
| E2E-7 | Wallet arithmetic after purchase 1 | 25 − 1.07 + 0.01 = 23.94 | **23.94 exact** (UI header + API agree) | **PASS** | §3.5 |
| E2E-8 | TRC-20 checkout → payment instructions | address + cents marker | Order `MEC-LQW67K5QK` pending_payment; addr `TMECSandbox000000C7Y`; payAmount $3.10 = $2.13 + cents marker 97¢ | **PASS** | `agent10-07/08*.png` + §3.5 |
| E2E-9 | Payment confirm (sandbox flow) | delivered + SANDBOX receipt + cashback | Order 2 (confirm via exact UI payload `{publicId, ref:"trc20-…"}`) → delivered, cashback +0.02. Order 3 (`MEC-LJLBRV4TU`, Capcut Pro 7D FW $0.27) confirmed **via the real UI button** → delivered, SANDBOX receipt | **PASS** | `agent10-09/11/12*.png` + §3.5 |
| E2E-10 | Final wallet arithmetic | 25 − 1.07 + 0.01 + 0.02 + 0.00 = 23.96 | **23.96 exact**; ledger: deposit +25.00, purchase −1.07, cashback +0.01, +0.02 | **PASS** | §3.5 |
| E2E-11 | Idempotent re-confirm | no double credit | re-confirm delivered order → 200 `{ok:true, idempotent:true}`; balance unchanged 23.96 | **PASS** | §3.5 |
| CONS-1 | Console/page errors during E2E | 0 errors | **0 errors**; only dev-mode logs (Fast Refresh/HMR/React DevTools info) | **PASS** | §3.6 |
| RL-1 | 15 rapid checkout POSTs (IP 10.10.99.99) | 10×4xx then 429 | `400×10, 429×5`; 429 body: «طلبات كثيرة جدًا — الحد 10 طلبًا في الدقيقة» | **PASS** | §3.7 |
| RL-2 | Window reset after 65s | non-429 | HTTP 400 (validation, not 429) | **PASS** | §3.7 |
| SYNC-1 | POST /api/admin/sync (token) | 200 + summary | 200 in **6.98s**; productsSeen 25, matched 20, changed 0, inStockNow 20, latencyMs 6563, membership bronze | **PASS** | §3.8 |
| SYNC-2 | lastSyncAt changed in catalog | newer timestamp | 2026-09-28T10:53:40.065Z → **2026-09-28T11:58:48.634Z** | **PASS** | §3.8 |

**TOTALS: 38 PASS / 0 FAIL / 0 SKIPPED / 0 BLOCKED**

---

## 3. Evidence & Transcripts

### 3.1 Smoke (local)
```
GET /            → HTTP 200; dir="rtl" ✓; lang="ar" ✓
GET /intel       → HTTP 200; dir="rtl" ✓
GET /api/store/catalog → HTTP 200 (time_total 0.009s)
  {"ok":true,"mode":"sandbox","products":[…37…],"families":[4]}
  lastSyncAt: 2026-09-28T10:53:40.065Z
GET /xyz         → HTTP 404; Arabic body «هذه الصفحة غير موجودة…» + rtl
GET /api         → HTTP 200 {"ok":true,"service":"mec-store","mode":"sandbox","time":"…"}
```

### 3.2 Production security headers (single `curl -sI`, low volume)
```
content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval';
  style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: blob: https:;
  connect-src 'self' https://mec-store-production.up.railway.app https://prodseller.com;
  frame-ancestors 'none'; base-uri 'self'; form-action 'self'
strict-transport-security: max-age=63072000; includeSubDomains; preload
x-frame-options: DENY
x-content-type-options: nosniff
referrer-policy: strict-origin-when-cross-origin
permissions-policy: camera=(), microphone=(), geolocation=()
```
All 6 required headers PRESENT (full file: `prod_headers.txt`). Prod sanity: `/api` 200; `/api/store/catalog` 200 in 0.21s, 37 products (warm cache).

### 3.3 Admin gate (local) — token value NEVER printed
```
GET  /api/admin/stats (no header)            → 401 {"ok":false,"error":"غير مصرح…"}
GET  /api/admin/stats (x-admin-token: wrong) → 401
GET  /api/admin/stats (x-admin-token: short) → 401   [fail-closed]
GET  /api/admin/stats (correct token)        → 200
  top-level field NAMES: attemptStats, mode, ok, orders, ps, suppliers, syncs, waitlistTotal
  (6 suppliers; orders.total=31; waitlistTotal=0; 2 sync log entries — values otherwise not recorded)
POST /api/admin/sync (no token)              → 401
GET  /api/admin/sync                          → 405
```

### 3.4 Input validation (isolated IP 10.10.10.10)
All 9 negative cases returned correct 400/404 with Arabic error messages (see Results Table VAL-1..9). Tight phone regex `^\+96[67]\d{8,9}$` rejects non-SA/YE numbers; deposit limits $5–$500 enforced; unknown product/order → 404.

### 3.5 E2E journey transcript (real browser, sandbox)

| Step | Action | Observed |
|------|--------|----------|
| 1 | Open `http://localhost:3000` | Store grid, 37 products, SANDBOX badge, out-of-stock items disabled (`agent10-01`) |
| 2 | Register phone `+96651110001` | Region badge 🇸🇦 السعودية — ر.س; SA prices applied (`agent10-02`) |
| 3 | Wallet → deposit $25 (default) | «إيداع تجريبي (sandbox) — فوري»; balance $25.00; API tx `deposit +25.00` (`agent10-03`) |
| 4 | Search «Canva Pro» → buy *Canva Pro 2 yrs FW* | Checkout: locked price **4 ر.س ≈ $1.07**, wallet rail `$25.00 / $1.07` (`agent10-04`) |
| 5 | «ادفع من المحفظة» | Order **MEC-LMQQ6VHS5** → status `delivered`, winner `ps`; receipt: `SANDBOX-RECEIPT • Canva Pro 2 yrs FW • via ProdSeller • 2026-09-28T11:55:37.666Z • محاكاة تسليم…`; transparency step `(ProdSeller, sandbox_purchase, ok)` (`agent10-05`) |
| 6 | Wallet refresh | header $23.94; ledger shows 3 txs (`agent10-06`) |
| 7 | Search «CapCut Pro 1 month» → buy with **USDT TRC-20** rail | Order **MEC-LQW67K5QK** `pending_payment`; address `TMECSandbox000000C7Y`; amount **$3.10** = $2.13 + unique cents marker (97) (`agent10-07/08`) |
| 8 | Confirm payment (sandbox) | checkout «محاكاة تأكيد الدفع» button navigates to order view; order-view confirm → **delivered**, cashback +$0.02. (Order 2 confirmed via API POST with the byte-identical payload the UI sends: `{"publicId":"MEC-LQW67K5QK","ref":"trc20-MEC-LQW67K5QK"}` → delivered; order 3 fully confirmed via the actual UI button) (`agent10-09/11/12`) |
| 9 | Final wallet + idempotency | balance **$23.96**; re-confirm delivered order → `{idempotent:true}`, no double credit |

**Cashback arithmetic proof (API-verified, double-entry ledger):**
```
deposit    +25.00   (dep-mul6xbwj)
purchase   − 1.07   (MEC-LMQQ6VHS5-purchase)   ← Canva Pro 2yrs, 4 SAR @3.75 peg
cashback   + 0.01   (MEC-LMQQ6VHS5-cashback)   ← 1% × 1.07 = 0.0107 → round2
cashback   + 0.02   (MEC-LQW67K5QK-cashback)   ← 1% × 2.13 = 0.0213 → round2
cashback   + 0.00   (MEC-LJLBRV4TU — 1% × 0.27 = 0.0027 → rounds to 0; no tx, correctly guarded)
                     ────────────────────────
balance  = 23.96  ✓ EXACT MATCH (UI header + /api/wallet agree)

Mission formula check: deposit − price + cashback = 25.00 − 1.07 + 0.01 = 23.94 ✓ (after purchase 1)
                       plus order-2 cashback 0.02 → 23.96 ✓ (final)
```
All 3 orders DELIVERED with SANDBOX-marked receipts; masked phone `+966••••0001` shown in order UI (PII masking works).

### 3.6 Console health
`agent-browser errors` → **empty** (0 page errors). `console` → only `[Fast Refresh]`/`[HMR]`/React-DevTools info logs (dev-server artifacts; not application errors).

### 3.7 Rate-limit burst (local, isolated `X-Forwarded-For: 10.10.99.99`, invalid payload `{}`)
```
req 1–10  → HTTP 400 (validation: «بيانات ناقصة…»)
req 11–15 → HTTP 429 «طلبات كثيرة جدًا — الحد 10 طلبًا في الدقيقة. انتظر قليلًا ثم أعد المحاولة.»
after 65s → HTTP 400 (window reset confirmed — non-429)
```
Exactly matches configured `checkout: 10/min` sliding window. Not tested on production (per rules).

### 3.8 Admin sync (local, once)
```
POST /api/admin/sync (correct token) → HTTP 200, time_total 6.98s
  {ok:true, productsSeen:25, matched:20, changed:0, inStockNow:20,
   balanceUsd:0, membership:"bronze", latencyMs:6563}
catalog lastSyncAt: 10:53:40.065Z → 11:58:48.634Z  (DB refreshed — evidence sync ran)
```

---

## 4. Failures Analysis

**None.** Zero failures across all 38 checks. Prior session's 23/23 PASS claim is **independently confirmed** and extended (38 checks incl. 9 extra negative-validation cases, idempotency, window-reset, and a second/third full purchase cycle on a fresh phone).

### Observations / Risks (non-blocking)

| # | Class | Severity | Finding |
|---|-------|----------|---------|
| O-1 | OBSERVATION | P3 | The checkout-panel button «▶️ محاكاة تأكيد الدفع (sandbox) — نفس مسار الـwebhook الحقيقي» only *navigates* to the order view; the actual confirm is the order view's own button. Two-step UX; label slightly over-promises. No functional issue (order view button does call `/api/store/payments/confirm`). |
| O-2 | RISK | P2→P3 | ProdSeller live balance is **$0.00 (bronze)** — in LIVE mode the balance guard would block real purchases until the float is topped up. Sandbox unaffected (guard skipped by design). Documented, not a sandbox-release blocker. |
| O-3 | OBSERVATION | P3 | Cashback rounds via `round2`: sub-$0.50 purchases yield $0.00 cashback (e.g. $0.27 → $0.0027 → $0.00; no ledger tx, correctly guarded by `cashback > 0`). Trivial fairness edge case. |
| O-4 | RISK | P3 | Rate limiter is in-memory per-instance (correct for current numReplicas=1; would break silently if scaled horizontally). Already documented in prior session. |
| O-5 | OBSERVATION | P3 | Wallet identity persists in `localStorage` only — closing the browser context (fresh profile) loses the phone (re-entry required). Passwordless by design; UX note only. |
| O-6 | OBSERVATION | P3 | Local dev console emits Fast Refresh logs — dev-mode artifact; production build unaffected (prior session verified 0 errors on prod E2E). |

---

## 5. Acceptance Assessment — Release-Gate Verdict

| Gate | Result |
|------|--------|
| G1 Smoke | ✅ PASS (5/5) |
| G2 Security headers (prod) | ✅ PASS (6/6 headers, strong values: HSTS preload 2y, XFO DENY, CSP with frame-ancestors 'none') |
| G3 Admin gate | ✅ PASS (fail-closed 401s; token-gated 200) |
| G4 E2E sandbox purchase | ✅ PASS (register→deposit→buy→DELIVERED×3, SANDBOX receipts, exact cashback arithmetic 23.94 → 23.96) |
| G5 Rate limiting | ✅ PASS (10/min enforced; window resets) |
| G6 Admin sync | ✅ PASS (6.98s live pull; lastSyncAt refreshed) |
| G7 Console health | ✅ PASS (0 errors) |

**VERDICT: RELEASE-READY (sandbox scope).** All 38 independent checks PASS. The prior session's hardening claims (admin gate, rate limiting, security headers, Arabic 404, sandbox delivery with marked receipts, cashback ledger integrity, price locking) are all **independently re-verified as FACTS** with fresh evidence.

**Caveat (DECISION for owner):** this gate covers SANDBOX mode only. LIVE-mode go-live additionally requires: (1) ProdSeller float top-up (balance $0.00 — O-2), (2) real TRC-20 deposit/confirmation webhook wiring (W2 scope per code comments), (3) live purchase endpoint contract verification vs ProdSeller docs (previously documented as unverified).

## 6. Limitations

1. Rate limiting tested on LOCAL only (per rules); production limits not load-tested (low-volume GET/HEAD only on prod).
2. E2E executed against local dev server (same DB as prod) — prod *UI* E2E not repeated this session (prior session's prod E2E screenshots exist in `research/live_capture/`).
3. Wallet rail tested with 1 purchase; TRC-20 with 2; Binance Pay rail not purchased (sandbox returns static `BINANCE-PAY-SANDBOX` address — same code path as TRC-20; checkout creation path verified).
4. Concurrent-load/soak behavior, DB failure injection, and multi-instance rate-limit behavior out of scope.
5. Console capture covers the exercised journey; non-exercied UI paths (intel dashboard interactions, restock/waitlist flows) not re-tested this session (were covered by prior session).
6. Admin stats field *values* deliberately not recorded (sensitive); only field names + counts.

## 7. Evidence Index (all under `/home/z/my-project/research/audit/`)

- Screenshots: `agent10-01-home.png` … `agent10-12-order3-delivered-ui-confirm.png` (12)
- HTTP artifacts: `prod_headers.txt`, `prod_catalog.json`, `smoke_home.html`, `smoke_intel.html`, `smoke_404.html`, `smoke_catalog.json`
- Order IDs (sandbox): MEC-LMQQ6VHS5 (wallet), MEC-LQW67K5QK (trc20), MEC-LJLBRV4TU (trc20, UI-confirm)
- Test phone: +96651110001 (sandbox wallet, final balance $23.96)
