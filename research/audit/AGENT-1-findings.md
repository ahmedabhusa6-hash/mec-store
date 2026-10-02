# AUDIT-1 — Product & Business Architect — MEC Digital Store (JIT Digital Goods)
Date: 2026-09-28 · Auditor: AUDIT-1 · Mode: READ-ONLY (research + HTTP tests, no source modifications)
Environments: LOCAL http://localhost:3000 (RUNNING, sandbox, same DB as prod) · PROD https://mec-store-production.up.railway.app (GET-only smoke)

---

## 1. Executive Summary

MEC is a functioning Arabic-first RTL **JIT digital-goods storefront** (37 products / 4 families) where identity = phone number (+966 SA / +967 YE), pricing is geo-based (SAR peg 3.75 / USD), checkout locks price server-side, a wallet ledger (double-entry-style append-only WalletTx) handles deposit→purchase→refund→cashback→apology, and a JIT router with stock/margin/float guards routes orders through a supplier chain (ProdSeller primary). The **sandbox product genuinely works end-to-end** — verified by 15 HTTP-level journey tests on local (wallet purchase delivered in ~1s with cashback math exact to the cent; TRC-20 flow with simulated confirm; idempotency; refund-on-fail design; rate limiting; fail-closed admin gate).

However, **commercial readiness is blocked for live mode** by: (P0) an unverified payment-confirm webhook that would let any customer mark their own order paid in live mode; (P1) the live purchase path passes the supplier *code* (`"ps"`) instead of the external product ID to ProdSeller; (P1) no phone-ownership verification (OTP) — anyone knowing a phone number could spend that wallet's real balance; (P1) Binance Pay returns a fake constant address even in live mode; plus missing legal pages, support channel, order history, and a waitlist promise with no notification mechanism. Sandbox demo readiness: **VERIFIED**. Live launch readiness: **NOT VERIFIED / BLOCKED**.

---

## 2. Method

1. Read `worklog.md` (esp. entry 18-19) for history: prior hardening audit verified price-lock, idempotent payments, wallet ledger, JIT guards; fixed admin exposure, rate limits, headers, sandbox receipts.
2. Full source read: `src/app/page.tsx`, `src/components/store/store.tsx` (919 lines), `src/lib/{engine,format,prodseller,ratelimit,admin-auth}.ts`, all 9 API routes under `src/app/api/`, `prisma/schema.prisma`, `src/app/not-found.tsx`, `next.config.*`.
3. HTTP journey tests on LOCAL with exact UI payloads (learned from store.tsx, not guessed). **Exactly 6 checkout calls used** (budget 6): 2 successes + 4 error paths. Unique `X-Forwarded-For` per test batch to isolate rate buckets. All raw requests/responses recorded below.
4. PROD GET-only smoke (4 requests): `/api`, `/api/store/catalog`, `/`, `/intel`.
5. Rendered-HTML verification of trust badges via `curl /` + string match.

---

## 3. Product Baseline

### 3.1 Catalog (TEST RESULT — GET /api/store/catalog @ local, 14ms; prod, 230ms)
- **37 products**, mode `sandbox`, 4 families:
  - AI/SaaS + خدمات رقمية: 25 · بث MENA: 7 · بطاقات إقليمية: 4 · بث MENA (متقدم): 1
- Geo prices per product: `SA` (SAR) / `YE` (USD) / `WW` (USD). YE range **$0.15–$111.34**; SA range **1–451 SAR**.
- Supplier chain depth: 17 products single-supplier, 20 dual-supplier (failover possible).
- 14 products carry a "−N% رسمي" discount badge vs `officialUsd` (e.g., adobe-express-12m $119.88 → $0.76 WW).
- 2 fully out-of-stock products: `chatgpt-plus-1-month`, `duolingo-super-12m` (all chain links stock=0).
- Sample: `avira-prime-3-months` YE $1.08 / SA 4 SAR; chain [ps $0.80 stock 100, sv $0.99 stock 70].

### 3.2 Store page sections (FACT — src/app/page.tsx; verified in rendered HTML)
- Header (p. 11-19): logo ⚡ "متجر MEC الرقمي" + tagline "اشتراكات AI · بث MENA · بطاقات إقليمية — تسليم فوري".
- **Trust badges exist** (p. 23-31): "⚡ تسليم ≤ 3 دقائق", "🔒 سعر مقفل 15 دقيقة", "💸 كاش باك 1%" + link "🔬 الاستخبارات" → /intel. All 3 found in served HTML (TEST).
- Trust strip (p. 43-58): no-account phone identity · USDT TRC-20/Binance Pay/wallet · "استرداد كامل إذا تعذّر التسليم + اعتذار $1".
- Footer (p. 66-75): JIT model text — **no legal/support links at all**.
- 404: Arabic custom page (not-found.tsx).

### 3.3 Store component (FACT — store.tsx 919 lines, 5 views at :770)
1. **Catalog** (StoreGrid :64-171): search + family filter pills, availability labels ("متوفر — N موردين" / "نفد حاليًا"), buy button "🛒 اشترِ الآن — تسليم ≤3 دقائق", no-phone warning (prices shown in USD until phone registered).
2. **Checkout** (CheckoutPanel :180-301): locked price display "🔒 هذا السعر مقفول لطلبك", 3 rails (wallet/TRC-20/Binance Pay :174-178), wallet affordability check, crypto payment instructions with cents-code marker, sandbox simulate-confirm button (:246).
3. **Order view** (OrderView :313-477): polls every 2.5s (:330), 4-step progress bar (:350-355), delivered payload with copy-to-clipboard (:397-423), cashback line, failed state with refund+apology + restock CTA (:425-442), transparency panel of routing attempts (:448-471).
4. **Wallet** (WalletPanel :485-571): balance, deposit $5-500 (quick $10/$25/$50/$100), tx ledger with Arabic type labels.
5. **Ops/Admin** (OpsPanel :579-764): token-gated (x-admin-token from localStorage), PS live balance/orders/waitlist/mode cards, live sync button, supplier score + circuit-breaker table, recent orders, sync log.

### 3.4 Order lifecycle (FACT — format.ts:51-57 STATUS_AR)
`pending_payment` (بانتظار الدفع) → `paid` (تم الدفع — قيد التوجيه) → `routing` (الموجّه يشتري من المورد) → `delivered` (تم التسليم ✓) | `failed` (تعذّر التنفيذ — استُرد المبلغ). Wallet-rail orders skip straight to `routing` (checkout/route.ts:67).

### 3.5 Restock/waitlist
Failed order → "🔔 أعلمني عند التوفير" → POST `/api/store/orders/[id]/restock` (store.tsx:437-439; restock/route.ts dedupes on (productId,phone)). Admin sees waitlistTotal. **No notification sender exists** (see Gaps G7).

### 3.6 Admin capabilities
Live ProdSeller sync (POST /api/admin/sync → GET /v1/products + /v1/balance; engine.ts:226-292), stats/supplier health (stats/route.ts). Both fail-closed behind ADMIN_TOKEN ≥16 chars, timing-safe compare (admin-auth.ts:5-23).

---

## 4. Business Logic Map (verified, with evidence)

| Rule | Implementation | Evidence |
|---|---|---|
| Geo pricing SA=SAR, YE/WW=USD | GeoPrice rows per region; region from phone prefix | checkout/route.ts:45-46; format.ts:18-23; schema.prisma:69-80 |
| SAR↔USD conversion | Peg **3.75** (SAR_PEG) | format.ts:40-42, 75; checkout/route.ts:51; store.tsx:191 |
| **Server-side price lock** | Client price never trusted; server reads GeoPrice at checkout, stores `priceLocked` | checkout/route.ts:36-50; schema.prisma:89 (TEST: SA order locked 3 SAR → amountUsd 0.80) |
| Wallet = ledger | balance = SUM(WalletTx); append-only credit(); DB unique (walletId,type,ref) = idempotency | engine.ts:76-91; schema.prisma:145 (TEST: 25 − 1.08 + 0.01 = 23.93 exact) |
| Deposit limits | $5–$500 (W1) | format.ts:70-71; deposit/route.ts:23-28 (TEST: $3 → 400) |
| Cashback | 1% of amountUsd on delivery | format.ts:73; engine.ts:219; checkout/route.ts:87 (TEST: $1.08 → $0.01) |
| Apology credit | $1 on total routing failure | format.ts:74; engine.ts:222; confirm/route.ts:81 |
| Refund on fail | Full amountUsd refunded to wallet | checkout/route.ts:92-98; confirm/route.ts:79-86 |
| Margin guard | supplier cost ≤ 90% of sale price → else skip | format.ts:72 (MARGIN_CAP); engine.ts:152-160 (TEST: avira cost 0.80 ≤ 0.9×1.08=0.972 ✓) |
| Float guard | LIVE mode only: live PS balance < cost → skip | engine.ts:131-134, 162-170 |
| Stock guard | stock==0 → skip supplier | engine.ts:141-150 |
| JIT purchase | LIVE: real POST /v1/orders via ProdSeller; SANDBOX: marked `SANDBOX-RECEIPT` simulated payload | engine.ts:172-205; prodseller.ts:70-89 (TEST: sandbox receipt delivered, 1ms) |
| Payment confirm (webhook) | Marks paid→routing, then routes; idempotent (non-pending → return state) | confirm/route.ts:37-42 (TEST: repeat → `{status:"delivered","idempotent":true}`) |
| Rate limits | checkout 10/min, confirm 12/min, deposit 6/min, wallet_read 60/min, catalog 60/min, admin 30/min, generic 120/min — per IP+bucket in-memory | ratelimit.ts:12-20 (TEST: admin 429 on 31st call) |
| Phone identity | tight regex `^\+96[67]\d{8,9}$`, region derivation, masking | format.ts:11-29 (TEST: bad phone → 400) |
| Rails | wallet / trc20 / binance_pay; crypto gets cents-code marker (1-98¢) on payAmount | format.ts:67; checkout/route.ts:32-34, 102-106 |
| Sandbox vs live | STORE_MODE env (default sandbox). Live: real purchase + live balance check + LIVE_TRC20_ADDRESS + deposit pending; Sandbox: simulated receipt + instant demo deposit + TMECSandbox000000C7Y | engine.ts:14, 131-134, 172-205; checkout/route.ts:8-9, 104-106, 127-129; deposit/route.ts:32-49 |

---

## 5. Journey Test Results (LOCAL, exact payloads from store.tsx)

Checkout calls used: **6/6 budget** (2 success, 4 error-path).

| # | Journey | Request | Response (condensed) | Verdict |
|---|---|---|---|---|
| T1 | Catalog | `GET /api/store/catalog` | 200 · ok · mode sandbox · 37 products · 4 families | PASS |
| T2 | Fresh wallet read | `GET /api/wallet?phone=%2B967778110234` | 200 · balance 0 (pre-deposit). NOTE: unencoded `+` in query → 400 (URL-decode space); UI encodes correctly (store.tsx:493) | PASS |
| T3 | Deposit | `POST /api/wallet/deposit {"phone":"+967778110234","amountUsd":25}` | `{ok:true,credited:25,balance:25,note:"إيداع تجريبي (sandbox) — فوري"}` | PASS |
| T4 | Wallet checkout (YE) | `POST /api/store/checkout {"slug":"avira-prime-3-months","phone":"+967778110234","rail":"wallet"}` | `{ok:true,publicId:"MEC-LRPE4SWMS",routed:{status:"delivered",winner:"ps",cashback:0.01}}` (~1s) | PASS |
| T5 | Order status | `GET /api/store/orders/MEC-LRPE4SWMS` | status delivered · statusAr "تم التسليم ✓" · priceLocked 1.08 · phoneMasked +967••••0234 · payload `SANDBOX-RECEIPT • Avira Prime…` · transparency: ProdSeller/sandbox_purchase/ok/cost 0.80 | PASS |
| T6 | Wallet reflects purchase+cashback | `GET /api/wallet?phone=%2B967778110234` | balance **23.93** · txs: +25 deposit, −1.08 purchase, +0.01 cashback (refs `MEC-LRPE4SWMS-*`) | PASS (exact math) |
| T7 | TRC-20 checkout (SA) | `POST /api/store/checkout {"slug":"adobe-express-12m","phone":"+96650000771","rail":"trc20"}` | `{ok:true,publicId:"MEC-LUWNWXGW5",payment:{rail:trc20,address:"TMECSandbox000000C7Y",amount:1.21,centsCode:41,instructions:"…محاكاة…"}}` | PASS (see G10 re: 1.21) |
| T8 | Payment confirm (sandbox simulation) | `POST /api/store/payments/confirm {"publicId":"MEC-LUWNWXGW5","ref":"trc20-MEC-LUWNWXGW5"}` | `{ok:true,routed:{status:"delivered",winner:"ps",cashback:0.01}}`; repeat → `{status:"delivered",idempotent:true}` (no re-route, no double cashback) | PASS |
| T9 | SA wallet auto-created w/ cashback | `GET /api/wallet?phone=%2B96650000771` | balance 0.01 (cashback only — wallet created on confirm, confirm/route.ts:70-74) | PASS |
| T10 | SA order (geo conversion) | `GET /api/store/orders/MEC-LUWNWXGW5` | region SA · currency SAR · **priceLocked 3** · **amountUsd 0.80** (3÷3.75) · winner ps · cost 0.35 | PASS (peg verified) |
| T11 | Waitlist join | `POST /api/store/orders/MEC-LUWNWXGW5/restock {}` ×2 | 1st: `{ok:true,waitingAhead:1}` · 2nd: `{waitingAhead:0}` — **DEFECT D2** (off-by-one: first call counts the user themself, restock/route.ts:28-30) | PASS w/ defect |
| T12 | Error paths | checkout: bad phone `0551234567` → **400**; unknown slug → **404**; insufficient balance (SA $0.01 vs $1.07) → **402**; rail `visa` → **400**; deposit $3 → **400** | All correct | PASS (6/6 checkout budget used) |
| T13 | Admin gate | `GET /api/admin/stats` no token → **401**; wrong token → **401** (fail-closed) | PASS |
| T14 | Rate limiting | 31 rapid admin calls same IP: 30×401 then **429** | PASS (mechanism works) |
| T15 | PROD smoke (GET-only) | `/api` 200 sandbox · `/api/store/catalog` 200 (37 products, same DB) · `/` 200 · `/intel` 200 | PASS |

Sandbox confirm simulation (mission 3d): the UI "محاكاة تأكيد الدفع (sandbox)" button calls the same `POST /api/store/payments/confirm` endpoint intended as the production webhook path (store.tsx:392-394, confirm/route.ts:7-11) — **the endpoint performs zero payment verification** (txid optional, no signature/on-chain check), see G1.

---

## 6. Product Gaps (evidence-based)

- **G1 [DEFECT P0 — live-mode blocker]** Payment-confirm webhook is unauthenticated and verifies nothing: `confirm/route.ts:16-42` flips pending→routing with optional txid and no signature/on-chain check. In LIVE mode any customer can create an order (checkout), then call confirm without paying → store spends real ProdSeller float, attacker receives goods free. Sandbox demo path by design, but fatal as-is for live.
- **G2 [DEFECT P1 — live-mode blocker]** Live purchase passes the wrong product identifier: `engine.ts:175-176` calls `psPurchase(String(link.supplier))` — i.e. `product_id="ps"` (supplier code), never the ChainLink `externalId` (schema.prisma:57, unused). Live purchases would fail or buy the wrong item. Live path has never been exercised (consistent with worklog 18-19 "live mode purchase endpoint contract unverified").
- **G3 [RISK P1]** No phone-ownership verification (no OTP): anyone who knows a phone number can spend that wallet's balance (checkout wallet rail, checkout/route.ts:55-70) and read its full tx history (`GET /api/wallet?phone=…`, wallet/route.ts — balance+txs of any phone, unmasked). With real deposits in live mode this is wallet theft by phone-number knowledge. Also a privacy leak today.
- **G4 [FACT P1]** No legal pages: only `/`, `/intel`, 404 exist (src/app contents). No terms/privacy/about/contact anywhere; footer (page.tsx:66-75) has zero links; checkout asserts "بالضغط أنت توافق على…" (store.tsx:295-297) with no linked terms. For SA consumer e-commerce this is a compliance blocker (terms, privacy, refund policy, VAT display — SAR prices show no VAT).
- **G5 [FACT P2]** Returning-customer order history missing: no endpoint lists orders by phone (routes: only `/api/store/orders/[publicId]`). publicId is shown once in OrderView; lose it/clear localStorage (phone stored there, store.tsx:792-793) → orders unretrievable. "محفوظ في سجل طلبك دائمًا" (store.tsx:416) promises a history that has no UI/API.
- **G6 [FACT P2]** No customer support channel: no email/WhatsApp/Telegram/support page in the storefront (grep across src: zero support/contact hits in store UI). Failed-order path is fully automated, but delivered-goods complaints (wrong/invalid code) have no channel.
- **G7 [RISK P2]** Waitlist promise without mechanism: "سننبهك عند التوفير" (store.tsx:347) — no notification sender (no email/SMS/push anywhere in codebase); waitlist rows accumulate (admin sees count only).
- **G8 [DEFECT P2]** Binance Pay is a stub in all modes: `checkout/route.ts:104-106` returns constant `"BINANCE-PAY-SANDBOX"` address even when STORE_MODE=live (only trc20 switches addresses). Store advertises Binance Pay as a rail (page.tsx:50-51).
- **G9 [RISK P2]** LIVE_TRC20_ADDR falls back to placeholder `"SET-LIVE-TRC20-ADDRESS"` (checkout/route.ts:9) — misconfigured live deploy would display a fake address to paying customers.
- **G10 [OBSERVATION P2]** Cents-code overpayment never reconciled: payAmount = amountUsd + random 1-98¢ (checkout/route.ts:102-103). T7: $0.80 order requested **$1.21** (+51%). Delta is never credited/refunded and not in any ledger; also cross-order amount collisions are possible (only 98 markers). Material for small tickets in live mode.
- **G11 [DEFECT P3]** Marketing claim vs implementation: badge "🔒 سعر مقفل 15 دقيقة" (page.tsx:27) and footer "الأسعار تتغير مع تحديث الموردين كل 15 دقيقة" (page.tsx:69) — no scheduler/cron exists (no cron config in repo; sync is admin-manual only, engine.ts:226), and locked prices have no TTL (pending orders stay locked indefinitely; no expiry logic).
- **G12 [DEFECT P3]** OOS dead-end CTA: out-of-stock product button reads "نفد — فعّل تنبيه التوفير" but is `disabled` (store.tsx:151-155) — waitlist cannot be joined from the catalog; only from a *failed order* view. Two live OOS products (chatgpt-plus-1-month, duolingo-super-12m) exhibit this.
- **G13 [OBSERVATION P3]** Public catalog API exposes wholesale costs: `chain[].costUsd` + supplier codes/names served publicly (engine.ts:51-57 via /api/store/catalog) — competitor margin intelligence for the taking. Same for per-order attempt costs in order view. Deliberate "transparency" positioning, but a business-intel leak.
- **G14 [OBSERVATION P3]** Admin ops panel lives inside the customer storefront (view toggle store.tsx:840-846) — token-gated, but increases surface/curiosity; separate /admin route would be cleaner.
- **G15 [OBSERVATION P3]** Phone regex accepts non-mobile SA numbers (`+9661xxxxxxx` landline passes `^\+96[67]\d{8,9}$`, format.ts:14) — region SA pricing granted to landline-formatted inputs.
- **G16 [OBSERVATION P3]** Search/filter has no empty state: StoreGrid renders an empty grid silently when a query matches nothing (store.tsx:70-73, 108-159).
- **G17 [RISK P3]** Wallet-rail checkout debits then routes non-atomically (credit then routeOrder, checkout/route.ts:70-76) — a crash mid-route leaves debit without order finalization (refund path only covers explicit routing failure). Mitigated by single-replica + small code path; worth a transaction/retry wrapper.

---

## 7. Commercial Readiness Verdict

**What works (sandbox-verified end-to-end):** catalog + geo-pricing + peg conversion; server-side price lock; wallet ledger with exact math (deposit→purchase→cashback; refund+apology on failure by design); JIT router transparency with stock/margin guards; idempotent payment confirm; rate limiting; fail-closed admin; Arabic RTL UX incl. custom 404; instant sandbox delivery receipts as publicly promised. [TEST RESULTS T1-T15]

**What blocks real (live) launch:**
1. P0 — G1: unverified payment confirm webhook (free-goods bypass).
2. P1 — G2: live purchase passes supplier code instead of product externalId (live path untested end-to-end).
3. P1 — G3: no OTP/phone-ownership check → wallet theft by phone knowledge; wallet read exposes any phone's balance/txs.
4. P1 — G4: no legal pages (terms/privacy/refund/VAT) — SA consumer-law exposure.
5. P2 — G8/G9/G10: Binance Pay stub in live; TRC-20 live address placeholder risk; cents-code overpayment unreconciled.
6. P2 — G5/G6/G7: no order history, no support channel, waitlist notifications undeliverable.

**Payment provider integration status:** simulated in sandbox by design; **live integration is NOT real-ready** — deposit flow in live returns a "pending" placeholder without generating an address (deposit/route.ts:32-40, W2 scope); crypto confirm has no on-chain verification (G1); ProdSeller GET endpoints (balance/products) are real and verified, but POST /v1/orders purchase path is unverified and mis-wired (G2).

**Verdict:** SANDBOX DEMO: production-grade and shippable for demos. **LIVE COMMERCE: NOT READY** — requires closing G1, G2, G3, G4 (and ideally G5-G10) before STORE_MODE=live with real money.

---

## 8. Limitations

- Local tests ran against the shared production DB (sandbox mode); test artifacts left in DB: 1 deposit ($25), 2 delivered orders (MEC-LRPE4SWMS, MEC-LUWNWXGW5), wallets for +967778110234 / +96650000771, 1 waitlist row — cosmetic noise only.
- Checkout budget (6 calls) exhausted; rate-limit behavior for the checkout bucket specifically was not re-triggered (mechanism verified on admin bucket, same code path ratelimit.ts).
- Live-mode branches (STORE_MODE=live: real psPurchase, float guard, live addresses) not executable in this environment — assessed by code reading only.
- Prod testing was GET-only (4 requests) per rules; no mutation/auth attempts on production.
- No browser-level UI testing (prior session's screenshots in research/live_capture/ cover E2E UX; this audit is HTTP+code level).
