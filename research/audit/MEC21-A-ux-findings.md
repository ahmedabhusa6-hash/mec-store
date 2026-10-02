# MEC-21-A — UX/UI, Arabic RTL & Accessibility RE-AUDIT (post-CSS-fix)

Date: 2026-09-28 · Agent: MEC-21-A (Team 06) · Scope: delta re-audit of AGENT-6 render-blocked items now that the Tailwind P0 is fixed. REAL browser verification (agent-browser/Chromium), no source modifications.

---

## 1. Executive Verdict

**The P0 Tailwind fix is CONFIRMED WORKING on local AND production.** Computed-style evidence: `max-w-6xl` → 1152px, 3-column product grid, sticky header (top=0 under scroll), dark zinc-950 theme, rounded corners, 703 utility rules in the stylesheet — identical values on `http://localhost:3000` and `https://mec-store-production.up.railway.app`. Every AGENT-6 "NOT VERIFIED (render-blocked)" item has now been tested for real.

**Score: 18 items VERIFIED/PASS · 6 defects remain (0 P0/P1, 1 P2-remainder, 5 P3) · 1 env-limited (hover visual).** The storefront is now visually credible, RTL-correct, keyboard-operable end-to-end (full purchase completed by keyboard + minimal pointer), console-clean on all four targets, and the E2E sandbox purchase (register → $10 deposit → buy → SANDBOX receipt) succeeded with exact ledger math ($10.00 − $0.27 = $9.73).

Previously-flagged items now FIXED: h1 added; Tajawal bold weights load; /intel mobile overflow gone (local+prod); catalog tri-state (error + retry verified live by network interception); phone input `aria-label` + `inputmode`. Still open: sub-12px Arabic micro-text (150 DOM instances), a **new worst-contrast finding** (`text-zinc-600` @ **2.57:1** ×39 — supplier-chain line on every product card), tap targets all <44px, RTL flow arrows still point wrong way (store.tsx:470), 3 inputs still placeholder-only, deposit quick-amounts still 2-tap.

---

## 2. Styling Fix Confirmation (P0 delta from MEC-20 / AGENT-6)

| Probe | Broken state (AGENT-6) | Now (local) | Now (production) |
|---|---|---|---|
| `main` max-width | `none` (edge-to-edge) | **1152px** | **1152px** |
| Product grid | 1 raw column | **3 columns** (37 cards) | **3 columns** (37 cards) |
| Header position | static | **sticky** (top=0 @ scrollY 1200) | sticky |
| Page background | white `lab(100 0 0)` | **zinc-950** `lab(2.51 …)` | zinc-950 |
| Buy button | radius 0, padding 0 | **radius 8px, pad 8×16, h 40px** | styled |
| Utilities layer | empty | **703 rules** (recursive CSSOM walk) | 764 total style rules |
| Tajawal weights | 500/800/900 never load | **400/500/700/800/900 all load**; `.font-bold`→700, `.font-extrabold`→800 computed | — |

Screenshots: `mec21-ux-01-desktop-store.png`, `mec21-ux-17-prod-desktop.png`, `mec21-ux-21-desktop-full.png` (full page).

**VERDICT: P0 FIX VERIFIED (local + production parity at computed-style level).**

---

## 3. Verified-Items Table (previously NOT VERIFIED → now tested)

| # | Item (AGENT-6 ref) | Status | Evidence | Severity |
|---|---|---|---|---|
| 1 | Tailwind utilities render (§3.1) | **VERIFIED** | §2 table above; screenshots 01/17/21 | — (P0 closed) |
| 2 | RTL grid placement — first card on RIGHT (§3.2) | **VERIFIED** | First DOM card bbox x=909–1267 = rightmost of 3 cols at 1440px; `direction: rtl` computed | — |
| 3 | Mixed bidi / LTR isolation (§3.2) | **VERIFIED** | Order view: `$0.27`, `+966••••4093`, `MEC-L6VCG6RYF` all `dir=ltr`-isolated inside RTL containers; order block `direction: rtl` | — |
| 4 | Focus states / focus ring (§3.5) | **VERIFIED** | Tab log 12 elements: plain buttons/links → browser `outline: auto`; ui `<Button>`/`<Input>` (shared classes `focus-visible:ring-[3px] ring-ring/50`) → computed ring shadow `oklab(0.708 / 0.5) 0 0 0 3px` after `transition-all` settles; `:focus-visible` matched on all | — |
| 5 | Keyboard navigation full flow (§3.5) | **VERIFIED** | Tab reaches every control (catalog → product buy → checkout pay options → phone → deposit); Enter activates back-button and buy-button (both tested); Enter in phone input submits registration; purchase completed | — |
| 6 | Hover states (§3.5) | **VERIFIED (CSS-level)** | `.hover\:bg-emerald-800:hover{background-color:var(--color-emerald-800)}` present inside `@media (hover: hover)`; classes + vars resolve (emerald-800 ≠ 900 measured). Headless Chromium reports `(hover: none)` so live visual swap is not triggerable in this env — environment artifact, not an app defect | — |
| 7 | Sticky header (§3.4) | **VERIFIED** | Desktop: header top=0 at scrollY=1200. Mobile 390px: top=0, height 130px (wraps — see note N6) | — |
| 8 | h1 on store page (§3.3, P2) | **VERIFIED FIXED** | `<h1>متجر MEC الرقمي</h1>` present, computed weight 800, 15px | P2 closed |
| 9 | Tajawal bold triggers (§3.3) | **VERIFIED FIXED** | `document.fonts.check` true for 700/800/900; 79 `.font-bold` elements compute 700; `.font-extrabold` → 800 | P2 closed |
| 10 | /intel mobile overflow (§3.4, P2 629>390) | **VERIFIED FIXED** | `scrollWidth 390 = clientWidth 390` local AND prod; wide table (503px) now inside `overflow-x-auto` wrapper; live-prices tab table 335px, no page overflow (screenshots 15/16/19) | P2 closed |
| 11 | Catalog fetch states (§3.5, P2 silent blank) | **VERIFIED FIXED** | Network-intercepted `**/api/store/catalog*` →abort→ page shows `⚠️ تعذّر الاتصال — تحقق من الشبكة وأعد المحاولة` + `🔄 إعادة المحاولة` button; unblocked + clicked retry → 37 cards restored. Loading skeleton (`⏳ جارٍ تحميل المتجر…` + 3 `animate-pulse` cards) verified in source (store.tsx:944–953); too fast to catch live (warm API ≈4ms) | P2 closed |
| 12 | Tap targets ≥44px mobile (§3.4) | **DEFECT — NOT FIXED** | 48/48 interactive elements in `main` < 44px height @390px: buy buttons 306×**40**, family chips **30px**, wallet/admin toggles **36px**, sync button **28px** | **P3** |
| 13 | Arabic micro-text ≥12px (§3.3, P2) | **PARTIALLY FIXED — DEFECT REMAINS** | 9.5px eliminated; several sizes raised to 11/12px; BUT **150 DOM elements still <12px** (133×10px, 16×10.5px, 1×11px) across header badges, trust strip, card meta, footer | **P2 (remainder)** |
| 14 | Text contrast (§3.6, P3 zinc-500 4.12:1) | **DEFECT — WORSE INSTANCE FOUND** | zinc-500/zinc-950 = **4.12:1** ×4 instances (fails AA); **NEW: `text-zinc-600`/zinc-950 = 2.57:1 ×39** ("سلسلة N موردين / مورد واحد" supplier-chain line on every product card + footer). All colored meta passes big: emerald-500 7.84, rose-400 7.39, violet-300 10.78, cyan-300 13.73, amber-300 13.80, zinc-400 7.76, zinc-300 13.46 | **P3 (pervasive)** |
| 15 | RTL process-flow arrows (§3.2, P3) | **NOT FIXED** | store.tsx:470 still `يفحص السلسلة → حارس الهامش → حارس الرصيد الحي → الشراء…` — U+2192 is not bidi-mirrored, so in the RTL flow the glyph points right (back toward the previous step) while reading order runs right→left. Contrast: `→ رجوع للمتجر` (line 224) correctly right-pointing for "back"; checkout CTA `←` (line 259) correctly left-pointing | **P3** |
| 16 | Form input labels (§3.6, P3) | **PARTIALLY FIXED** | Phone input: `aria-label="رقم الجوال"` + `inputMode="tel"` ✓ (a11y tree: `textbox "رقم الجوال"`). Search input (`ابحث عن منتج…`), deposit amount (spinbutton, unnamed), admin token (`admin token…`) remain **placeholder-only** (a11y tree shows unnamed spinbutton) | **P3** |
| 17 | Wallet panel states (§3.5) | **VERIFIED** | Empty: `📦 لا طلبات بعد`. Deposit success: `✓ إيداع تجريبي (sandbox) — فوري` + ledger row `+$10.00` (double-entry list). Insufficient balance: pay button disabled + `الرصيد غير كافٍ — اشحن المحفظة` CTA (observed pre-deposit). Balance refresh lags toast by ~5s (poll) — P3 observation persists | — |
| 18 | Checkout flow states (§3.5) | **VERIFIED** | Creating: `⏳ جارٍ الإنشاء…`; stepper 4 states rendered RTL-correct (x-geometry 995→722→450→177 = right-to-left progression); delivered: `تم التسليم ✓` + SANDBOX-RECEIPT block (LTR mono, correctly isolated) + copy affordance; OOS: card opacity .6, button opacity .5 + `pointer-events:none` (computed) | — |
| 19 | Console / network (§3.7) | **VERIFIED CLEAN** | Local `/` and `/intel`: 0 console errors, 0 page errors; only non-200s are intentional admin-gate 401s (`/api/admin/stats`, `/api/admin/costs`). Production `/` + `/intel`: 31/31 requests 200, console empty | — |
| 20 | E2E sanity (sandbox, local) | **VERIFIED** | Fresh phone **+966582174093** → deposit **$10.00** (rate-limit-safe, 1 attempt) → bought **Capcut pro 6 days FW @ 1 ر.س ($0.27)** → order **MEC-L6VCG6RYF** DELIVERED with SANDBOX receipt → wallet **$9.73** exact (10 − 0.27; cashback $0.0027 rounds to $0 — known AUDIT-10 P3). Receipt RTL container + LTR-isolated amounts/phone verified | — |
| 21 | Store mobile overflow (§3.4) | **VERIFIED NONE** | 390=390 local + production; 1-col grid; checkout view 390px, pay button 324px full-width | — |
| 22 | Production parity | **VERIFIED** | All §2 probes equal on prod; h1 ✓, 37 cards ✓, mobile no-overflow ✓, console clean ✓ (read-only: loads + computed styles only, zero form submissions on prod) | — |

**Counts: 18 VERIFIED/PASS (incl. 5 prior defects confirmed fixed: h1, Tajawal bold, /intel overflow, catalog states, phone label) · 6 DEFECTS remaining · 1 env-limited verification (hover visual).**

---

## 4. New Defects Found (this round)

- **[NEW][P3] N1 — `text-zinc-600` at 2.57:1 contrast, 39 instances.** The supplier-chain meta line ("سلسلة 2 موردين" / "مورد واحد") renders at zinc-600 on zinc-950 on EVERY product card, plus footer payment line. Fails WCAG AA (4.5:1) by a wide margin — the worst contrast on the page and it sits on trust-relevant copy. Fix: bump to zinc-400 (7.76:1 AAA) — 1-line change ×2 class sites.
- **[NEW][P3] N2 — All mobile tap targets < 44px.** 48/48 interactive elements measured at 390px: buy buttons 40px (borderline), family filter chips 30px, header wallet/admin toggles 36px, sync 28px. Apple HIG 44px / Material 48dp. Fix: `min-h-11` (44px) on interactive controls.
- **[NEW][OBSERVATION][P3] N3 — Sticky header consumes 130px (15%) of mobile viewport** (brand + badge chips wrap). Consider compact sticky (brand only) on <sm.
- **[NOTED] N4 — view state machine hides catalog when wallet/admin opens** (`view` switch replaces catalog). By design, but the "المحفظة" toggle is the only way back — first-time users may be confused why products "disappeared" after deposit. Low priority.

---

## 5. Remaining Defects (carry-over, updated)

| ID | Defect | Severity | Status vs AGENT-6 |
|---|---|---|---|
| D1 | Arabic micro-text <12px — 150 DOM instances (133×10px, 16×10.5px) | **P2 remainder** | Partially improved (9.5px gone; 11/12px introduced) |
| D2 | RTL flow arrows point wrong way (store.tsx:470) | P3 | Unchanged |
| D3 | Contrast: zinc-600 2.57:1 ×39 (new) + zinc-500 4.12:1 ×4 | P3 | Expanded finding |
| D4 | Placeholder-only inputs: search, deposit amount, admin token | P3 | Phone fixed; 3 remain |
| D5 | Tap targets <44px (48/48 on mobile) | P3 | Confirmed rendered |
| D6 | Deposit UX: quick-amounts prefill only (2-tap); balance lags success toast ~5s | P3 | Confirmed unchanged |

---

## 6. Recommendations (priority order)

1. **[P2] Typography batch**: raise all Arabic UI text to ≥12px (one Tailwind pass over `text-[10px]`/`text-[10.5px]` in page.tsx + store.tsx) — bundle with D3 contrast fix (`text-zinc-600`→`text-zinc-400`, `text-zinc-500`→`text-zinc-400`) and D2 arrow swap (`→`→`←` at store.tsx:470 only; back-arrows stay `→`). All three are class-only edits, zero logic risk.
2. **[P3] Tap targets**: `min-h-11` on family chips, header toggles, buy buttons.
3. **[P3] `aria-label`s** on search ("ابحث عن منتج"), deposit amount ("مبلغ الإيداع بالدولار"), admin token ("مفتاح التشغيل").
4. **[P3] One-tap quick-amount deposit** (deposit on chip click) + optimistic balance update after deposit (or poll immediately post-success).
5. **[P3] Mobile sticky header compaction** (<sm: hide badge chips or single row).
6. Optional polish: `th[scope]` on /intel tables (AGENT-6 §3.6), `inputMode="decimal"` on deposit.

---

## 7. Method & Evidence Inventory

- Tool: agent-browser (Chromium), isolated session `--session mec21a` (avoids cross-agent browser-state contamination found on the default session — a leftover `mec-phone` localStorage + foreign checkout view was observed there).
- Viewports: 1440×900, 390×844. Targets: local `/`, `/intel`; production `/`, `/intel` (read-only).
- Techniques: computed-style/CSSOM probes (incl. recursive `@layer utilities` walk — 703 rules), bounding-box geometry for RTL order/stepper/tap targets, WCAG contrast computation from rendered colors, Tab-key focus logging, network route interception (abort catalog API — client-side only, no server impact), real sandbox E2E.
- 21 screenshots: `research/audit/mec21-ux-01…21-*.png`.
- Limitations: hover visual change unverifiable in headless env (`(hover: none)` media — rules confirmed present under `@media (hover: hover)`); loading skeleton verified in source + architecture, not captured live (warm API 4ms); no screen-reader run; Chromium only.
- Production touched with GET/reload/computed-style probes only — **no forms submitted, no purchases** (per safety mandate).
