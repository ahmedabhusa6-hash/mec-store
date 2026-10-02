# AUDIT-3 — Backend & API Audit (Code + Live Endpoint Tests)

- Agent: AUDIT-3 (Backend & API Engineer)
- Date: 2026-09-28 (local time UTC)
- Scope: 10 API routes (`src/app/api/**`) + 6 libs (`src/lib/{engine,prodseller,ratelimit,admin-auth,format,db}.ts`) + Prisma schema. Live tests against `http://localhost:3000` (sandbox mode, shared prod DB). Prod = GET-only parity check.
- Checkout POST budget respected: exactly **8/8** used (XFF `10.2.2.3` isolated). No burst tests (Agent 10 owns those). No source files modified.
- Test artifacts: test wallets/orders created in shared prod DB (sandbox money): phones `+966555000111`, `+96771234567`, `+96771234568`, `+966577000999`, `+966500111222`; orders `MEC-LPZ4N68YW`, `MEC-LGM9K9K33`.

---

## 1. Executive Summary

The API layer is **functionally solid for the sandbox demo**: server-side price locking, tight phone validation, deposit bounds, sequential payment idempotency, fail-closed admin gate, and refund+apology flow all verified live (21 endpoint test groups, ~66 HTTP requests). Catalog parity local↔prod is byte-identical.

However, the audit found **one P0 and several P1 defects that are dormant in sandbox but become real the moment `STORE_MODE=live`**:

1. **P0 (live)**: `POST /api/store/payments/confirm` has **zero payment verification** — no signature, no txid validation, no amount check. Anyone with a `publicId` (returned by checkout to the buyer) can mark any pending order paid → triggers a real supplier purchase at store's expense.
2. **P1**: No `prisma.$transaction` anywhere (0 grep matches). Checkout wallet flow = check-balance → debit → route → refund is a 6-step non-atomic sequence; a crash/exception mid-flow leaves the customer debited with an order stuck in `routing` and no refund.
3. **P1**: Double-spend race — wallet balance is `SELECT SUM` then separate insert; no row lock/serializable isolation/CHECK constraint. Two concurrent checkouts can both pass the balance check → negative balance. (Single-shot live race didn't trigger; code path unprotected.)
4. **P1**: Confirm has a TOCTOU race (status check → update are separate) — two concurrent confirms of one pending order = double routing = double real purchase in live mode.
5. **P1 (live)**: `routeOrder` calls `psPurchase(String(link.supplier))` — passes supplier code `"ps"` as `product_id` instead of `ChainLink.externalId`. Live-mode purchases would always target a wrong ID → guaranteed failure loop.
6. **P2**: Unauthenticated wallet enumeration → order publicId leak → order detail (incl. `deliveredPayload` = the goods) with no auth. Verified live end-to-end.
7. **P2**: Rate-limit bypass via `X-Forwarded-For` spoofing (first-value trust). Verified live.
8. **P2 (live)**: Apology-farming — failed orders refund 100% **plus** $1; products whose chain is all-skipped (e.g., `chatgpt-plus-1-month`) are guaranteed-fail → +$1 per order, farmable at 10/min (unlimited with XFF spoofing) with real money in live mode.

Severity map used: P0 = exploitable money/goods loss in the CURRENT deployment mode; P1 = money-loss/atomicity under realistic conditions or on mode switch; P2 = security/privacy weakness requiring preconditions; P3 = correctness/robustness nits.

---

## 2. Code Audit

### 2.1 Per-route coverage table

| Route | Input validation | Authz | Rate limit | Transaction / atomicity | Notes |
|---|---|---|---|---|---|
| `GET /api` (route.ts) | n/a | public (health) | **NONE** | n/a | Returns mode+time only. Acceptable, but unguarded. |
| `GET /api/store/catalog` | n/a (no params) | public | `catalog` 60/min ✓ | n/a | Only route with `console.error` logging (line 15). 60s in-memory cache (engine.ts:24-28). |
| `POST /api/store/checkout` | slug: string+non-empty; phone: tight regex; rail: RAILS whitelist; JSON parse errors → 400. **No length caps** on slug/rail. | public (guest store, by design) | `checkout` 10/min ✓ | **NONE** — wallet flow is 6 sequential awaits, no `$transaction`, no try/catch around DB/routeOrder (route.ts:55-98) | Server-side price lock ✓ (37-51). Client price fields never read. Wallet flow: balance check → order.create → debit → route → deliver+cashback / refund+apology. |
| `GET /api/store/orders/[id]` | publicId: used raw in findUnique, **no format/length cap** | **public — no phone match** (order readable by publicId incl. deliveredPayload) | `generic` 120/min ✓ | n/a | Masked phone ✓, transparency steps ✓. |
| `POST /api/store/orders/[id]/restock` | **Body never read** (any/garbage body accepted); no order-status guard (works on delivered/failed) | public | `generic` 120/min ✓ | **NONE** — findFirst-then-create; race → P2002 unique violation → unhandled 500 (schema Waitlist `@@unique([productId, phone])`) | Self-count off-by-one in `waitingAhead` (see live test R1/R2). |
| `POST /api/store/payments/confirm` | publicId: string; txid: `typeof (txid ?? ref) === "string"` — numeric txid silently dropped → falls back to old ref; **no length cap** | **PUBLIC — no payment verification at all** (P0 live) | `confirm` 12/min ✓ | **NONE** — status check (37) then update (42) then route (50): TOCTOU race; crash mid-route → order stuck `routing`, paid, no refund | Sequential idempotency ✓ (36-39) + WalletTx `@@unique([walletId,type,ref])` backstop. Cross-order duplicate txid → P2002 on `Order.paymentRef @unique` → unhandled 500. |
| `GET /api/wallet` | phone: tight regex ✓ | **PUBLIC — any valid-format phone returns full balance + last 50 txs; creates wallet on GET (side effect)** | `wallet_read` 60/min ✓ | n/a | Tx `ref` values leak order publicIds (`MEC-L…-purchase`). |
| `POST /api/wallet/deposit` | phone ✓; amount: `Number.isFinite` + $5–$500 bounds ✓; type coercion: string `"25"` accepted | public | `deposit` 6/min ✓ | single insert (fine) | Sandbox: instant credit, **not idempotent** (ref = timestamp). Live: returns `pending:true`, no record persisted. |
| `GET /api/admin/stats` | n/a | `x-admin-token` (or Bearer) vs `ADMIN_TOKEN`; **fail-closed** if unset/<16 chars ✓; timing-safe-ish compare | `admin` 30/min (before auth ✓) | n/a | `psBalance()` never throws (internal catch → null). |
| `POST /api/admin/sync` | n/a | same gate ✓ | `admin` 30/min ✓ | sync loop: per-link sequential updates, no transaction (acceptable) | `GET` → 405 ✓. `maxDuration=60`. |

### 2.2 Libs

**admin-auth.ts** — [FACT] Fail-closed: `if (!expected || expected.length < 16) return false` (lines 7-10) — missing/weak env denies everything. [OBSERVATION P3] Custom `timingSafeEqual` (18-23) early-returns on length mismatch → token **length** leaks via timing; recommend `crypto.timingSafeEqual` over fixed-length SHA-256 digests of both sides. Accepts `Authorization: Bearer` fallback (12-14).

**ratelimit.ts** — [FACT] In-memory sliding window, per `bucket:ip`, 7 buckets (checkout 10/min, confirm 12/min, deposit 6/min, wallet_read 60/min, catalog 60/min, admin 30/min, generic 120/min). Single-replica assumption documented (line 2). [DEFECT P2] `clientIp` (22-29) trusts `x-forwarded-for` **first value** — on Railway the proxy appends real IP after client-supplied values, so a spoofed XFF wins → per-request unique XFF = unlimited bypass (verified live). [RISK P3] `buckets.clear()` at 50k keys (line 38) wipes ALL rate-limit state — spray 50k unique IPs to globally reset limits.

**engine.ts** —
- [FACT] Catalog cache 60s TTL (24-28) — local warm hit 11ms.
- [DEFECT P1] **No atomicity**: `walletBalance` = `SELECT SUM(walletTx.amount)` (76-79), then callers insert a debit in a separate query. No `prisma.$transaction` (0 matches in src), no `SELECT … FOR UPDATE`, no serializable isolation, no `balance >= 0` CHECK. Double-spend window = balance-read → debit-insert.
- [DEFECT P1 live] Line 176: `psPurchase(String(link.supplier))` passes supplier code (`"ps"`) as `product_id`. `ChainLink.externalId` (schema line 57) exists for the real supplier SKU but is never used. All live-mode purchases would fail → refund+apology loop.
- [OBSERVATION P3] Circuit-breaker fields (`Supplier.openUntil`, `failCount`, `score`) are **display-only** — `routeOrder` never consults them (grep: only admin/stats + intel UI). Failover = static chain priority only; a failing supplier is retried on every order in live mode.
- [OBSERVATION P3] `routeOrder` persists attempts AFTER the chain loop (209-216); if `createMany` throws, result lost and exception propagates to a route with no try/catch.
- [OBSERVATION P3] Margin guard divides by `opts.priceUsd` in message formatting (157) — `priceUsd=0` (bad geo data) → `Infinity%`/`NaN` in message; skip logic itself is safe.
- [RISK P2 live] **Apology farming**: guaranteed-fail chains (all suppliers skipped, e.g. `chatgpt-plus-1-month`: ps stock=0, sv cost $12.81 > 0.9×$3.92) → every order refunds 100% + $1 apology → net **+$1 per failed order** (checkout:92-93, confirm:80-81). Farmable 10/min (XFF spoof: unlimited). Sandbox: demo money only. Live: real liability.

**format.ts** — [FACT] Phone regex `^\+96[67]\d{8,9}$` after stripping non-`[\\d+]` (11-16) — quote-injection safe (verified live). `genPublicId`: 8 chars × 32 alphabet = 2^40 keyspace (enumeration infeasible even at 120/min). `MARGIN_CAP` 0.9, cashback 1%, apology $1, SAR peg 3.75.

**prodseller.ts** — [FACT] `psBalance`/`psProducts` catch all errors → return `null` (45-48, 61-64): **silently swallowed, never logged** — a supplier outage is indistinguishable from "no key". [OBSERVATION P3] `psPurchase` error strings (`String(e).slice(0,120)`, line 85) flow into `Attempt.message` → exposed to end users via order transparency endpoint (internal detail leak). Purchase contract POST `/v1/orders {product_id}` remains unverified against supplier docs (matches worklog 18-19 caveat).

**db.ts** — [OBSERVATION P3] `log: ['query']` enabled unconditionally (line 10) — noisy in production logs, minor perf/info-leak surface.

### 2.3 Error handling inventory

8 `catch` blocks in src (grep). Only **1 logs** (`catalog` route). Silent swallows: `psBalance`, `psProducts` (return null); checkout/confirm/deposit JSON-parse catches return 400 without logging (acceptable — client errors). **6 of 10 route files have no try/catch at all around DB calls** (checkout, confirm, orders/[id], restock, wallet, admin/stats) — unhandled DB errors surface as Next.js default 500s (server console only, no structured logging, no compensation logic).

### 2.4 Concurrency & idempotency analysis (verdicts)

- **Payments idempotency (sequential): VERIFIED GOOD.** `order.status !== "pending_payment"` early-return (confirm:36-39) + `WalletTx @@unique([walletId, type, ref])` backstop. Live: repeat confirm → `idempotent:true`, cashback credited exactly once (balance stayed $0.01).
- **Payments idempotency (concurrent): DEFECT P1.** Status-check→update→route is check-then-act with no guard on the UPDATE's WHERE clause and no lock. Two concurrent confirms both pass line 37 → both route. In live mode = double real purchase; the unique constraint only makes the *second cashback insert* throw P2002 (→500) **after** both purchases executed. Not live-tested (budget); code-read + schema evidence.
- **Checkout atomicity: DEFECT P1.** No `$transaction`. Failure between debit (route:70) and refund (route:92) — crash, DB hiccup, exception in `routeOrder`/`credit` — leaves wallet debited, order stuck `routing`, no delivery, no refund, HTTP 500 to client. Same shape in confirm (paid → stuck `routing`).
- **Double-spend: DEFECT P1 (window unprotected).** Balance is derived (SUM), check and debit are separate queries. Single-shot live race attempt: NOT triggered (REQ-B saw post-debit balance → 402; REQ-A delivered). Code has no protection; window is the ~ms between SUM and insert — winnable with synchronized concurrent requests.
- **Waitlist: DEFECT P3.** findFirst-then-create race → P2002 → 500; dedupe otherwise correct.
- **Cross-order duplicate txid: DEFECT P3.** `Order.paymentRef @unique` — confirming order B with order A's stored txid throws P2002 in the update (confirm:42) → 500, order B stuck `pending_payment`. Code-read only.

---

## 3. Live Test Results (all vs `http://localhost:3000`, sandbox mode)

Legend: status in brackets. Bodies truncated. Full request payloads as sent.

### 3.1 Deposit (`POST /api/wallet/deposit`)

| # | Payload (essence) | Status | Response (essence) |
|---|---|---|---|
| A1 | `{"phone":"+966555000111","amountUsd":25}` | 200 | `{"ok":true,"credited":25,"balance":25,...}` |
| A2/A3 | P2 two × $5 | 200 | balances 5 → 10 |
| B1 | amountUsd 4.99 | 400 | `الإيداع بين $5 و$500 (حدود W1)` |
| B2 | amountUsd 501 | 400 | same |
| B3 | amountUsd 0 | 400 | same |
| B4 | amountUsd −10 | 400 | same |
| B5 | amountUsd "abc" | 400 | same |
| B6 | amountUsd 1e308 | 400 | same |
| C1 | amountUsd **"25" (string)** | **200** | `{"ok":true,"credited":25,...}` — type coercion accepted |
| C2 | amountUsd null | 400 | bounds error (Number(null)=0) |
| C3 | missing phone | 400 | `جوال صحيح مطلوب` |
| C4 | phone +961… (Lebanon) | 400 | `جوال صحيح مطلوب` |
| C5 | malformed JSON `{broken` | 400 | `طلب غير صالح` |
| C6 | no body | 400 | `طلب غير صالح` |
| RL1-7 | 7 rapid $5 deposits, same XFF | 6×200 then **429** | 429 body: `طلبات كثيرة جدًا — الحد 6 طلبًا في الدقيقة…` + `Retry-After: 30` ✓ |
| SP1-3 | 3 deposits, **unique XFF each** | **3×200** | **Rate-limit bypass via spoofed XFF proven** (immediately after the 429) |

### 3.2 Checkout (`POST /api/store/checkout`) — 8 POSTs total

| # | Payload (essence) | Status | Response (essence) |
|---|---|---|---|
| C1 | `{}` | 400 | `بيانات ناقصة: slug + جوال صحيح مطلوبان (+966/+967)` |
| C2 | phone `+9617012345` | 400 | same |
| C3 | phone `' +9665' OR '1'='1 --` (quote injection) | 400 | same — regex rejects |
| C3b | phone `""` | 400 | same |
| C5 | valid phone + slug `canva-pro-2-yrs-fw` + rail trc20 + **tampered `price/priceUsd/amountUsd/payAmount = 0.01`** | **200** | `publicId:"MEC-LPZ4N68YW"`, `payAmount: 1.24`, `centsCode: 29` → server charged YE price **$0.95** + $0.29 marker. **Client price fields fully ignored — price lock proven.** |
| C6 | slug `no-such-product-xyz` | 404 | `المنتج غير موجود` |
| C7 | **concurrent** P2 (balance $10) × product $5.60 — REQ-A | 200 | `{"ok":true,"publicId":"MEC-LGM9K9K33","routed":{"ok":true,"status":"delivered","winner":"ps","cashback":0.06}}` |
| C8 | same, REQ-B (simultaneous) | 402 | `الرصيد غير كافٍ…` — race NOT won this shot (B's balance-read landed after A's debit); ledger after: `10 − 5.60 + 0.06 = 4.46` exact ✓ |

### 3.3 Confirm (`POST /api/store/payments/confirm`)

| # | Payload | Status | Response (essence) |
|---|---|---|---|
| F1 | `{"txid":"TX1"}` (no publicId) | 400 | `publicId مطلوب` |
| F2 | `{"publicId":"MEC-ZZZZZZZZ"}` | 404 | `الطلب غير موجود` |
| F3 | `{"publicId":"MEC-LPZ4N68YW","txid":"TX-AUDIT3-001"}` | 200 | delivered, winner ps, cashback 0.01 (P4 wallet balance 0.01) |
| F4 | repeat same txid | 200 | `{"ok":true,"status":"delivered","idempotent":true}` — **no double credit** (balance still 0.01) |
| F5 | same publicId, different txid | 200 | `idempotent:true` — delivered orders ignore new txids |

### 3.4 Order (`GET /api/store/orders/[id]`)

| # | Request | Status | Response (essence) |
|---|---|---|---|
| O1 | `/MEC-ZZZZZZZZ` | 404 | `الطلب غير موجود` |
| O2 | `/MEC-LPZ4N68YW` | 200 | Full order: masked phone `+967••••4568`, `priceLocked:0.95`, `payAmount:1.24`, SANDBOX receipt payload, transparency steps |
| O3 | `/MEC-LGM9K9K33` (**"foreign"** — publicId discovered only via unauthenticated `GET /api/wallet?phone=…` tx refs) | **200** | Full order incl. `deliveredPayload` (the goods) + masked phone. **No phone-match/auth required — privacy chain proven end-to-end.** |

### 3.5 Restock (`POST /api/store/orders/[id]/restock`)

| # | Request | Status | Response |
|---|---|---|---|
| R1 | order A (delivered), first call | 200 | `{"ok":true,"waitingAhead":1}` |
| R2 | repeat | 200 | `{"ok":true,"waitingAhead":0}` — **R1 counted the just-created row (self) → off-by-one: empty queue reported as "1 ahead"** |
| R3 | random id | 404 | `الطلب غير موجود` |
| R4 | garbage body `'not json at all'` | 200 | `waitingAhead:0` — **body never parsed** |
| R5 | P2's delivered order | 200 | `waitingAhead:1` (again self-count; also: no order-status guard — restock works on delivered orders) |

### 3.6 Wallet (`GET /api/wallet`)

| # | Request | Status | Response |
|---|---|---|---|
| W2 | no phone param | 400 | `جوال صحيح مطلوب (+966/+967)` |
| W3 | `phone=0096651234567` | 400 | same |
| W6 | **never-seen phone** `+966500111222` | 200 | `{"ok":true,"balance":0,"txs":[]}` — **GET creates wallet; anyone can enumerate any valid-format phone's balance + tx history (refs leak order publicIds)** |

### 3.7 Admin (`/api/admin/*`)

| # | Request | Status |
|---|---|---|
| AD1 | `GET stats` no token | 401 (Arabic error, `WWW-Authenticate: Bearer`) |
| AD2 | `GET stats` wrong token | 401 |
| AD3 | `GET stats` valid `x-admin-token` | 200 (mode, 6 suppliers, ordersTotal 38, waitlistTotal 3, ps.live=true) |
| AD3b | valid `Authorization: Bearer` | 200 (fallback accepted) |
| AD4 | `POST sync` no token | 401 |
| AD5 | `GET sync` | 405 (explicit method guard) |

### 3.8 Misc & prod parity

- `GET /api` local + prod: 200 `{"ok":true,"service":"mec-store","mode":"sandbox",...}` both.
- `GET /api/store/catalog`: local 200 / 11ms / 16354 B vs **prod 200 / 1.9s (cold) / 16354 B — byte-identical payload**: 37 products, 4 families, same slugs, same `lastSyncAt` (2026-09-28T10:53:40Z). **Parity: exact.**
- `GET /api/does-not-exist` → 404. `PUT /api/store/catalog` → 405 (method guards work).

---

## 4. Findings Register (classified)

| # | Class | Sev | Finding | Evidence |
|---|---|---|---|---|
| 1 | **DEFECT** | **P0 (live)** | `payments/confirm` has no payment verification — anyone with publicId can mark a pending order paid → real purchase triggered in live mode. Sandbox "simulate" button is the same path. | `confirm/route.ts:12-42` (no auth/signature/amount check anywhere); live F3 confirmed an order with arbitrary txid `TX-AUDIT3-001` |
| 2 | **DEFECT** | **P1** | No `prisma.$transaction` anywhere; checkout wallet flow & confirm flow are multi-step non-atomic. Crash/exception between debit and refund → debited customer, order stuck `routing`, no refund, 500. | grep `$transaction` = 0 matches; `checkout/route.ts:55-98`; `confirm/route.ts:42-86` |
| 3 | **DEFECT** | **P1** | Double-spend: balance = SUM then separate debit insert; no lock/isolation/CHECK. | `engine.ts:76-79, 89-91`; live race single-shot inconclusive (C7/C8: one 402, one delivered) |
| 4 | **DEFECT** | **P1** | Confirm TOCTOU: concurrent confirms of same pending order → double routing → double real purchase (live). Unique constraint stops only the 2nd cashback insert, after purchases ran. | `confirm/route.ts:36-42`; `schema.prisma:145` |
| 5 | **DEFECT** | **P1 (live)** | `psPurchase(String(link.supplier))` passes supplier code `"ps"` as product_id; `ChainLink.externalId` never used → live purchases target wrong ID → guaranteed failure loop. | `engine.ts:176` vs `schema.prisma:57` |
| 6 | **RISK** | **P2 (live)** | Apology farming: guaranteed-fail chains refund 100% + $1 → net +$1/order; farmable 10/min (unlimited via XFF spoof). | `engine.ts:222` (APOLOGY_USD=1); catalog: `chatgpt-plus-1-month` chain ps stock=0 + sv margin-skip; `checkout/route.ts:92-93` |
| 7 | **DEFECT** | **P2** | Unauthenticated wallet enumeration (`GET /api/wallet?phone=`) → tx refs leak order publicIds → `GET /api/store/orders/[id]` returns deliveredPayload with no phone match. | `wallet/route.ts:7-19`; `orders/[id]/route.ts:12-21`; live W6+O3 chain |
| 8 | **DEFECT** | **P2** | Rate-limit bypass: client-supplied `X-Forwarded-For` first value trusted → unique XFF per request = unlimited. | `ratelimit.ts:22-29`; live SP1-3 (3×200 right after 429) |
| 9 | **DEFECT** | **P3** | Restock `waitingAhead` off-by-one on first call (counts the just-created row). | `restock/route.ts:28-30`; live R1=1 vs R2=0 |
| 10 | **DEFECT** | **P3** | Waitlist findFirst-then-create race → P2002 → unhandled 500. | `restock/route.ts:20-27` + `schema.prisma:156` |
| 11 | **DEFECT** | **P3** | Cross-order duplicate txid → `Order.paymentRef @unique` P2002 in confirm update → 500, order stuck pending. | `confirm/route.ts:42` + `schema.prisma:93` (code-read) |
| 12 | **RISK** | **P3** | `buckets.clear()` GC at 50k keys wipes all rate-limit state (spray-to-reset). | `ratelimit.ts:38` |
| 13 | **RISK** | **P3** | No length caps (slug/publicId/txid can be huge); no body-size limit in route handlers → memory surface. | `checkout/route.ts:22-24`, `confirm/route.ts:22-23` |
| 14 | **RISK** | **P3** | Circuit breaker & supplier score display-only — never enforced in routing. | grep: `openUntil/failCount/score` only in `admin/stats` + `store.tsx` |
| 15 | **OBSERVATION** | **P3** | psBalance/psProducts swallow errors silently (return null, no log) — supplier outage invisible. | `prodseller.ts:45-48, 61-64` |
| 16 | **OBSERVATION** | **P3** | psPurchase error strings stored in Attempt.message → exposed via transparency endpoint. | `prodseller.ts:84-85` → `engine.ts:189` → `orders/[id]/route.ts:63` |
| 17 | **OBSERVATION** | **P3** | Deposit type coercion (`"25"` string → 200 credited); deposits not idempotent. | live C1; `deposit/route.ts:19, 43` |
| 18 | **OBSERVATION** | **P3** | Checkout wallet path writes cashback row even when 0 (no `>0` guard, unlike confirm). | `checkout/route.ts:87` vs `confirm/route.ts:71` |
| 19 | **OBSERVATION** | **P3** | Admin token compare early-exits on length (length timing leak). | `admin-auth.ts:18-23` |
| 20 | **OBSERVATION** | P3 | `db.ts` logs all queries unconditionally (`log:['query']`). | `db.ts:10` |
| 21 | **FACT** | — | VERIFIED GOOD: price locking, phone regex (incl. injection), deposit bounds, sequential confirm idempotency (+ no double credit), admin fail-closed gate (401/401/200 + Bearer), 429+Retry-After, refund+apology design, wallet ledger exactness (10→4.46 with cashback, 25→23.94 on P1), catalog cache, local↔prod byte-parity. | §3 |

**Positive verdicts (mission questions):** Idempotency (sequential) = **GOOD**; Idempotency (concurrent) = **BROKEN (TOCTOU)**; Atomicity = **BROKEN (no transactions)**; Concurrency/double-spend = **UNPROTECTED (small window, no lock)**; Admin authz = **GOOD (fail-closed, minor timing nit)**; Rate-limit coverage = **9/10 endpoints guarded** (root `/api` unguarded, trivial), but **bypassable via XFF spoof**.

---

## 5. Regression Test Candidates (for fix-phase re-verification)

1. **Price lock**: checkout with tampered `price/priceUsd/amountUsd` fields → server geo price + cents marker returned (sent 0.01 → charged 0.95+0.29).
2. **Confirm idempotency (sequential)**: repeat confirm (same or different txid) → `{idempotent:true}`, wallet cashback credited exactly once.
3. **Wallet ledger exactness**: deposit → purchase → cashback; balance == Σ(txs) to the cent.
4. **Deposit bounds**: 4.99 / 501 / 0 / −10 / non-finite / non-numeric → 400; 5 and 500 → 200.
5. **Phone gate**: `+961…`, empty, quote-injection, non-string, missing → 400 (checkout/wallet/deposit).
6. **Admin fail-closed**: no token → 401; wrong token → 401; valid token (header or Bearer) → 200; unset/short `ADMIN_TOKEN` env → all denied.
7. **Rate limits**: checkout 10/min, confirm 12/min, deposit 6/min → 429 + `Retry-After: 30` (and after fix: XFF spoof must NOT bypass).
8. **Refund+apology on failed routing**: all-supplier-skip product → order `failed`, refund = amount, apology = $1, wallet credited both.
9. **404s**: unknown slug (checkout), random publicId (order GET, confirm, restock) → 404.
10. **Cashback math**: `round2(amountUsd × 0.01)` with ref `{publicId}-cashback` (and post-fix: no $0.00 rows).
11. **Restock dedupe**: same order twice → no duplicate waitlist row (post-fix: no P2002 500 under concurrency; `waitingAhead` excludes self).
12. **Catalog parity & cache**: 200, `ok:true`, 37 products / 4 families, identical local↔prod, warm <50ms.

---

## 6. Limitations

- Sandbox mode only; P0/P1-live findings (confirm verification, psPurchase product-id, apology farming with real money) are **dormant by design** today and become active at `STORE_MODE=live`.
- Double-spend race: single-shot attempt (checkout budget cap 8); not reproduced live — classification rests on code-read (no lock/transaction). Concurrent-confirm TOCTOU and waitlist P2002 race likewise untested live (would need more checkout POSTs than budget).
- Cross-order duplicate-txid 500: code-read + schema only.
- No burst testing (delegated to Agent 10); rate-limit verification limited to the deposit bucket + bypass demo.
- Local shares the PROD database: audit created sandbox-marked wallets/orders (~$70 demo credits, 4 orders, 3 waitlist rows) — cleanup optional, all marked sandbox/demo refs.
- Admin token read from `/tmp/admin_token.txt` for the 200 test only; token value not recorded here. `POST /api/admin/sync` NOT executed with valid token (mutates DB + 25s supplier call); only its auth gate (401) verified.
