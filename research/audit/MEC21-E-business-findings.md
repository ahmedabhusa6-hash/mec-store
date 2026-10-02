# MEC-21-E — Product Management & Business Readiness Findings
Date: 2026-09-28 · Agent: MEC-21-E (Team 05 — Product/Business Readiness)
Mode: local sandbox journeys (fresh phone, 2-order budget respected) + read-only DB analytics + code reading + PROD GET-only smoke.
DB footprint: 1 wallet, 1 deposit ($10), 2 delivered orders, 1 waitlist row (all sandbox-marked, phone +966554002199).

---

## 1. Executive Summary

The sandbox product is **functionally complete for its W1 scope**: all 3 audited user journeys PASS end-to-end (wallet happy path with exact ledger math; TRC-20 with instructions + simulated webhook confirm + idempotency; waitlist join with owner-proofing). Catalog data integrity is 100% (37/37 products × 3 regions priced, 0 negative margins, 0 margin-guard violations). Legal pages are substantive Arabic documents specific to digital goods — a real trust asset. Delivery SLA claim (≤3 min) holds for **all 20 delivered sandbox orders** (median 2.3s, max 32s).

**However, commercial (live) readiness remains blocked**, and this audit found **one NEW P0-live defect** no prior agent caught: in `STORE_MODE=live`, the JIT router **falls through to sandbox simulation for any non-ProdSeller supplier** — 12/37 products (all Turgame-first) would charge real money and deliver a fake `SANDBOX-RECEIPT` string; another 20 ps-first products hit the same path on failover. Combined with the known W2 blockers (payment verification, OTP), $0.00 ProdSeller float (bronze — verified via sync log), no cash-out tooling despite the refund policy promising 24h cash refunds, and zero analytics, the store cannot take real money today.

**Scores (criteria in §9): Technical asset quality HIGH · Product readiness 90% (sandbox scope) · Commercial readiness 25% (live scope).** No monetary valuation produced — the $100,000 figure is treated strictly as a strategic reference benchmark.

---

## 2. User Journey Verification (local sandbox, fresh phone +966554002199)

| # | Journey step | Result | Evidence (FACT unless noted) |
|---|---|---|---|
| A1 | Fresh wallet read (pre-registration state) | **PASS** | `GET /api/wallet?phone=+966554002199` → `{balance:0, txs:[]}` |
| A2 | Wallet deposit $10 (sandbox) | **PASS** | 200 `{credited:10, balance:10, note:"إيداع تجريبي (sandbox) — فوري"}` |
| A3 | Catalog browse | **PASS** | 37 products / 4 families, mode sandbox, 6.9ms warm |
| A4 | Wallet purchase → delivered | **PASS** | `MEC-LT5GHHHJR` office-365 (SA 2 SAR → $0.53), delivered in **1.23s**, winner ps, `SANDBOX-RECEIPT` payload |
| A5 | Receipt + order detail | **PASS** | priceLocked 2 SAR, amountUsd 0.53 (peg 3.75 ✓), statusAr "تم التسليم ✓", transparency step `sandbox_purchase` latencyMs 1 |
| A6 | Cashback + ledger arithmetic | **PASS (exact)** | 10 − 0.53 + 0.01 = **9.48** — wallet API + tx rows agree (purchase/cashback refs `MEC-LT5GHHHJR-*`) |
| A7 | Order history correctness | **PASS** | `GET /api/store/orders?phone=` → 1 order, correct product/status/price/rail |
| B1 | TRC-20 order creation | **PASS** | `MEC-LHP2ZDR5L` → pending_payment + instructions: address `TMECSandbox000000C7Y`, amount **1.71** ($0.80 + centsCode 91), Arabic instructions |
| B2 | Payment instructions screen data | **PASS** | order detail while pending: payAddress + payAmount 1.71 + priceLocked 3 SAR + amountUsd 0.80 |
| B3 | Sandbox confirm (simulated webhook) | **PASS** | 200 → delivered, winner ps, cashback 0.01; wallet 9.48 + 0.01 = **9.49 exact** |
| B4 | Confirm idempotency | **PASS** | repeat confirm → `{status:"delivered", idempotent:true}` — no re-route, no double cashback |
| B5 | History after 2nd order | **PASS** | 2 orders, newest-first, both "تم التسليم ✓" |
| C1 | Waitlist join (owner) | **PASS** | `POST .../restock?phone=` → `{ok:true, waitingAhead:0}` — off-by-one fixed (own entry excluded) |
| C2 | Waitlist idempotency | **PASS** | repeat → `{ok:true, waitingAhead:0}`, no duplicate row (DB: exactly 1 row) |
| C3 | Waitlist owner-proof | **PASS** | wrong phone → 404 (same message as not-found — no existence leak) |
| C4 | Order owner-proof | **PASS** | order detail with wrong phone → 404 |
| C5 | OOS product UX entry | **FAIL → GAP (G-B1)** | `chatgpt-plus-1-month` (both suppliers stock=0): catalog card shows "نفد حاليًا" but buy button is **disabled** (`store.tsx:164 disabled={!availability.ok}`) — waitlist **cannot be joined from the catalog**; only reachable from a *failed order* view. (AGENT-1 G12 still open.) |

**Journey verdict: 17/18 PASS; the single FAIL is the known OOS dead-end CTA (UX gap, not a money-path defect).**
Note on product choice: cheapest wallet-payable product is `capcut-pro-6-days-fw` (SA 1 SAR = $0.27) but its 1% cashback ($0.0027) rounds to $0.00; I purchased the cheapest product with a **material cashback** (office-365, 2 SAR) to verify full ledger arithmetic — cashback-rounds-to-zero documented as P3 by AUDIT-10.

---

## 3. Margin Analysis (internal, own DB — FACT)

Method: per product, best (min-cost) **active, in-stock** chain link vs. region price; SA converted at peg 3.75.

| Family | n | Avg margin % (YE) | Avg margin % (SA) | Avg margin $ (YE) | Routable (margin-guard pass) |
|---|---|---|---|---|---|
| AI/SaaS + خدمات رقمية | 25 | **31.68%** | **37.55%** | $0.76 | 24/24 |
| بث MENA | 7 | 20.01% | 25.88% | **$6.55** (highest $/order) | 7/7 |
| بث MENA (متقدم) | 1 | 20.02% | 25.94% | $1.83 | 1/1 |
| بطاقات إقليمية (Turgame) | 4 | 16.68% | 22.94% | $0.98 | 4/4 |
| **Overall (36 in-stock)** | — | **27.42%** | **33.33%** | — | 0 guard violations |

- **Best-margin category: AI/SaaS subscriptions** (avg 31.7% YE / 37.6% SA; top: office-365 53.3%, adobe-express 49.3%, duolingo-12m 48.3%).
- **Highest absolute profit per order: MENA streaming** (avg $6.55/order on big tickets) — the volume play is AI/SaaS, the ticket play is streaming.
- **Thinnest: Turgame regional cards** (~16.7% — near the structural floor set by supplier pricing).
- 0 negative margins, 0 margin-cap (90%) violations, 1 product with no routable in-stock chain (chatgpt-plus-1-month, OOS).
- OBSERVATION: SA margins run ~6pp above YE — geo-pricing adds a real premium for the Saudi market.

---

## 4. Revenue Mechanics & Ledger Integrity

**Where money enters (FACT, code-verified):**
1. Sandbox deposit = instant demo credit (verified A2). 2. **Live deposit = placeholder** — returns "pending" text, generates **no address**, credits nothing (`deposit/route.ts:32-40`, W2). 3. TRC-20 direct = instructions + cents-code marker; live confirmation requires W2 (manual confirm correctly 403-gated in live). 4. **Binance Pay = constant stub address `BINANCE-PAY-SANDBOX` in ALL modes including live** (`checkout/route.ts:135-137` — AGENT-1 G8 still open). 5. Live TRC-20 address falls back to placeholder `SET-LIVE-TRC20-ADDRESS` if env unset (G9 still open).

**Cents-code overpayment (G10 still open — fresh evidence):** my $0.80 TRC-20 order requested **$1.71** (+113.75% marker). The 91¢ delta is never credited, refunded, or ledgered. On small tickets the marker dominates the amount; needs reconciliation logic before live.

**Ledger integrity (my orders only, per rules):** both orders exact to the cent (9.48 → 9.49). Aggregate (all-time, all sandbox demo money): deposits $370 / purchases −$14.94 / refunds $2.07 / cashback $0.21 / apology $3 → net liability **$360.34** across 27 wallets. **Real revenue to date: $0.00** (STORE_MODE=sandbox everywhere; all receipts SANDBOX-marked).

**Cash-out GAP (new, G-B2):** refund policy promises cash refund of unused balance within 24h (deposit network), ≤72h business otherwise — **no cash-out capability exists anywhere in the codebase** (no USDT send, no admin withdrawal tooling). The promise is currently unexecutable.

---

## 5. Order History Analytics (48 orders, DB FACT)

| Status | Count | Reading |
|---|---|---|
| pending_payment | 25 | stale test residue (oldest 10:56Z) — never confirmed; invisible to users, cleanup pending |
| delivered | 20 | flows complete — wallet 12, trc20 8 |
| failed | 3 | refund+apology path exercised (pre-fix apology-farming residue: 3×$1 to same phone within 49s at 10:55-10:56Z, before the 24h-cap fix shipped ~12:15Z) |

Rail split: wallet 14 (12 delivered / 2 failed) · trc20 34 (8 delivered / 1 failed / 25 pending). Conversion of *confirmed* orders → delivered: 20/23 = 87% (3 failures were guaranteed-fail chains, all auto-refunded).

---

## 6. Product Data Quality (launch-facing)

- **Pricing: 100% complete** — 37/37 products have SA+YE+WW prices, 0 non-positive prices (VERIFIED).
- Supplier wiring: **25/25 ps chain links have externalId** (the G2 live-wiring fix is in the data, not just code).
- Costs: 0 chain links with cost ≤ 0.
- Gaps: 12/37 missing `nameEn` (Arabic-only names — fine for W1 Arabic-first, limits future EN SEO); 19/37 missing `officialUsd` (no "−N% رسمي" discount badge); **no image or description fields exist at all** (schema is text-only) — cards show name+price+availability only; acceptable for W1, weak merchandising for higher tickets (e.g., 451 SAR items).

---

## 7. Operational Readiness

**Delivery SLA (≤3 دقائق claim):** VERIFIED in sandbox — 20/20 delivered orders within 180s; min 1.0s / median 2.3s / avg 5.8s / max 32.1s (createdAt→deliveredAt). Caveat: sandbox purchases are simulated; **live SLA is unverified** (depends on real ProdSeller purchase latency — last sync call took 15.95s round-trip, though that includes catalog pull).

**Admin capabilities (code-verified, 401 fail-closed on prod):** stats (mode, PS balance/membership, supplier health, attempt stats, recent 12 orders, sync log, waitlist total), live ProdSeller sync, gated costs/margins view. **Missing for daily operations:** no order search/customer lookup UI (no filter by phone/status), **no manual refund/void/re-delivery tooling** (refunds exist only as automatic routing-failure path — policy §2's ≤24h re-execution promise has no tool), no waitlist notification sender (count only), no export/reporting, no cash-out processing (see G-B2), no revenue dashboard (only raw counts).

**Supplier float: $0.00 (bronze)** — FACT from sync log: "مزامنة حية … الرصيد $0.00 (bronze)" (4/4 syncs today show $0). Float guard verified working: the 3 failed live-mode test orders show `skipped_no_float` steps (balance $0 < cost → skip → fail-safe refund). **At $0 float, the first live order on any ps product will fail-and-refund.** Capital $1000 (project) vs $0 on account — funding gap. (Direct ProdSeller dashboard: NOT ACCESSIBLE from this environment.)

**Sync cadence: NO automation.** 0 cron/scheduler configs in repo (CI workflow is build-only; no vercel/railway scheduled jobs). 4 manual admin syncs total (gaps 52-65 min between). The false "كل 15 دقيقة" footer claim was **removed** in MEC-20 (now "الأسعار تتحدّث مع كل مزامنة للموردين" — accurate). Residual freshness problem: sync only refreshes **ps** links; **sv (StackVault) and turgame stock data is ~11.1 hours old** and never auto-refreshes — the "متوفر" label on 12 turgame-first products rests on stale data.

**NEW P0-live defect (G-B0) — live mode simulates delivery for non-ps suppliers:** `engine.ts routeOrder` gates the real purchase on `STORE_MODE==="live" && isPs`; any **non-ps** link (turgame: 12 products priority-1; sv: failover position in 20 more) **falls through to the sandbox-simulation block and returns a marked SANDBOX-RECEIPT as "delivered"** — in live mode this charges real money for a fake receipt. No prior agent report contains this finding (grepped). Fix is small (skip non-implemented suppliers in live like the `skipped_no_external_id` pattern); full Turgame live support is M-effort. **This is a hard live-launch blocker in addition to W2.**

---

## 8. Legal & Trust (all three pages fetched local + prod, byte-identical, HTTP 200)

- **/terms (2,168 chars):** substantive — JIT model defined, price-lock, rails, deposit limits, cents-code exact-amount requirement, ≤3-min delivery, auto-refund + apology, fair use, **explicit sandbox disclaimer** (§6), governing law SA+YE, last-updated date. Arabic quality: professional, consistent store terminology.
- **/privacy (1,843 chars):** honest data-minimization story (phone = identity; no cards stored; Supabase EU + RLS), **transparently discloses the phone-knowledge risk and states OTP is coming in W2**, deletion/cash-refund rights, localStorage-only cookies claim.
- **/refund (1,806 chars):** digital-goods-specific — auto-refund on fulfillment failure, ≤24h re-execution-or-refund for non-working codes, prorated refunds for partially consumed subs, 24h full cash-out then ≤72h business, explicit exclusions (revealed-code wrong purchases, third-party bans, sandbox disclaimer).
- Footer links all three (G4 from AGENT-1: **CLOSED** for existence+linking+content).
- Residual trust gaps: refund §5 says "قناة الدعم المعلنة عند الإطلاق" — **support channel does not exist yet**; no VAT display/inclusion statement for SA prices (15% VAT treatment unstated — compliance question for SA consumer e-commerce); cash-out promise unexecutable today (G-B2).

---

## 9. Commercial Readiness vs $100,000 Benchmark (strategic reference — NOT a valuation)

### 9.1 VERIFIED strengths (technical assets)
1. **Working JIT engine** — atomic wallet checkout ($transaction + conditional INSERT), idempotent payment confirm (atomic claim), stock/margin/float/breaker guards, failover, fail-safe refund+apology (all re-verified by this audit's journeys).
2. **Exact financial ledger** — derived balance, append-only, unique-ref idempotency; arithmetic exact to the cent on fresh test orders.
3. **Hardened security posture** — 10-agent audit + ~30 fixes verified in production: owner-proofed order/waitlist access (re-verified 404s), fail-closed admin (401 on prod), RLS 10/10 + zero anon grants, cost-leak closed (public catalog contains no costUsd — re-verified), live-mode confirm gate (403).
4. **Arabic-first RTL UX** — bidi-correct, custom 404, tri-state catalog, substantive Arabic legal pages.
5. **Deployed + verified** — production E2E (MEC-20), CI green on latest main push (9f5787b, verified via GitHub API, event=push conclusion=success), rollback plan documented.
6. **Complete, consistent catalog data** — 37 products × 3 regions, zero pricing defects, healthy margin structure (27-33% avg).

### 9.2 VERIFIED gaps blocking commercial launch
| # | Gap | Why it matters commercially | Effort |
|---|---|---|---|
| G-B0 | **NEW: live mode simulates delivery for non-ps suppliers** (12 Turgame-first products + 20 failover paths) | Real money for fake receipts = chargeback/fraud exposure, instant reputational death | **S** (skip-guard) / **M** (full Turgame integration) |
| 1 | W2: payment verification — signed webhook / on-chain TRON check + OTP phone verification | Cannot safely accept real money; wallet theft by phone knowledge; deposit-in-live is a placeholder | **M** |
| 2 | ProdSeller float **$0.00 (bronze)** + live purchase contract untested | Zero fulfillment capital: every live ps order fails-and-refunds until funded; JIT model stops at order #1 | **S** (top-up) + **M** (contract verification) |
| 3 | No support channel + no refund/cash-out tooling | Policy promises 24h cash refunds and ≤24h issue resolution — currently unexecutable; SA consumer-law exposure | **M** |
| 4 | Zero product analytics (no traffic/funnel/cohort/revenue instrumentation) | Cannot steer acquisition or detect leakage; a $100k-asset growth story needs data from day one | **S-M** |
| 5 | Key rotation not done (ProdSeller key + ADMIN_TOKEN; .env was git-tracked historically) | Security hygiene before real money | **S** |
| 6 | Single replica + in-memory rate limiter/circuit breaker | Availability SPOF; restart wipes breaker/buckets | **M** |
| 7 | Binance Pay stub + TRC-20 live-address placeholder fallback | Advertised rail that can't take live payments; misconfig risk shows fake address to payers | **S** (remove/hide) / **M** (real integration) |
| 8 | Sandbox residue (25 pending orders, 27 wallets incl. $360 demo liability) + sandbox mode itself | Must be cleaned/migrated before real books exist | **S** |
| 9 | OOS waitlist dead-end + no notification sender (G12/G7 still open) | Conversion loss on stockouts; waitlist promise undeliverable | **S-M** |
| 10 | No VAT display statement for SA | SA consumer e-commerce compliance question | **S** |

### 9.3 Scores (explicit criteria)

**Technical asset quality: HIGH**
Criteria: (a) end-to-end functionality verified repeatedly by independent agents — re-confirmed today (17/18 journey checks); (b) financial correctness — exact ledger math, atomicity, idempotency; (c) security — audited, fixed, re-verified; (d) deployability — running in production with green CI and rollback path; (e) data integrity — 100% pricing completeness. Deductions: no automated unit tests (API regression suite only), single-replica constraints, the newly-found G-B0 shows live-path logic is still under-tested — quality is high **for the sandbox product and architecture**, not yet proven for the live money path.

**Product readiness: 90% (sandbox scope)**
Criteria (weighted): core purchase flows 3/3 PASS (30% weight — full); catalog/data completeness (20% — 95%: pricing perfect, nameEn/officialUsd/images gaps); trust & legal (20% — 85%: substantive pages, no support channel/VAT statement); retention features (15% — 75%: history ✓, waitlist mechanism ✓, notifications ✗, OOS UX fail); operational claim accuracy (15% — 90%: SLA verified, sync claim fixed, freshness partial). No invented precision: this is a criteria-based estimate, not a measurement.

**Commercial readiness: 25% (live scope)**
Criteria: payment rails live-ready 0/3 rails (25% weight → ~0); supplier fulfillment live-ready (25% → 30%: ps wiring fixed but unfunded/untested, non-ps simulates, sv/turgame stale); compliance & trust for real customers (20% → 55%: legal pages done, support/VAT/cash-out missing); operations tooling (15% → 40%: sync+costs exist, no refunds/lookup/cash-out); analytics & growth (15% → 0%). Sandbox is excellent; **live commerce remains NOT READY** — consistent with MEC-20's verdict, now with G-B0 added to the blocker list.

---

## 10. Recommendations (priority order)
1. **Fix G-B0** (one-line-class guard: skip non-implemented suppliers in live mode) — before ANY live testing.
2. Close W2 (payment webhook/OTP) — already scoped.
3. Fund ProdSeller float (≥ a few hundred USD) + one real end-to-end purchase test on the cheapest item.
4. Stand up support channel + manual refund/cash-out tooling to make the refund policy executable.
5. Add minimal analytics instrumentation before launch traffic.
6. Rotate ProdSeller key + ADMIN_TOKEN; clean sandbox residue before go-live.
7. Enable OOS catalog waitlist join (G12) and a notification sender.

## 11. Limitations
- Local dev server shares the production DB (sandbox mode) — standard for this project; my mutations are listed above and are sandbox-marked.
- One transient read anomaly: a waitlist `findMany` returned empty immediately after creation, then the row appeared on re-query (~seconds later, via pooled connection) — non-reproducible; classified OBSERVATION (possible pooler read-lag), not a defect.
- Live-mode branches (G-B0, float guard, live addresses) assessed by code reading + DB residue; not executable in sandbox (by design).
- Prod interactions were GET-only (8 requests: health, catalog, /intel, 3 legal pages, 2 admin 401 probes).
- Apology-cap fix verified in code but not adversarially re-tested (would need a failed order; budget spent).
- No monetary valuation produced; percentages are criteria-based judgments with stated weights, not measurements.
