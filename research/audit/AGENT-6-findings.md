# AGENT-6 — UX/UI, Arabic & RTL Browser Audit (MEC Store)

Date: 2026-09-28 · Auditor: AUDIT-6 · Scope: REAL browser audit, no source modifications.

---

## 1. Executive Summary

**P0 HEADLINE: The entire Tailwind CSS layer is missing — the store renders as raw unstyled HTML on BOTH local dev and production.** Every utility class (grids, colors, spacing, modal positioning, focus rings) compiles to nothing because `src/app/globals.css` declares `@import "tailwindcss" source(none); @source "../src";` — from `src/app/`, `"../src"` resolves to `src/src/`, **which does not exist**. Tailwind therefore scans zero files and emits an empty utilities layer (theme/preflight layers do load). Root cause was reproduced in isolation (`/tmp/twtest`): identical directives → 0 utilities; changing to `@source "../"` → utilities generate. Fix is a 1-line change (not applied — audit-only mandate).

Despite this, **functional flows are intact** (registration → deposit → purchase → SANDBOX receipt → cashback, on desktop AND mobile, zero console errors), and the **Arabic/RTL foundation is genuinely solid**: `dir="rtl"` correct, phone input properly `dir="ltr"`-isolated, mixed English-product-name bidi rendering measured correct, Latin numerals consistent, back-arrow directionality correct. One real RTL defect found (process-flow arrows point the wrong way) plus typography/a11y issues (no `h1`, 9.5–10px Arabic micro-text, placeholder-only labels).

**RTL verdict: structurally PASS (rendered layout pending CSS fix). Mobile verdict: no horizontal overflow on store; /intel overflows (629px > 390px). Console: clean on / and /intel, local + production.**

---

## 2. Method

- Tool: `agent-browser` (Playwright/Chromium headless) + `curl` HTML inspection + computed-style/DOM-geometry `eval` probes + VLM (z-ai vision, glm-5v-turbo) as secondary visual confirmation.
- Viewports: Desktop **1440×900**, Mobile **390×844** (emulated).
- Targets: `http://localhost:3000` (/ and /intel), `https://mec-store-production.up.railway.app` (read-only parity).
- Evidence: 21 screenshots in `/home/z/my-project/research/audit/agent6-*.png`; scratch reproduction in `/tmp/twtest/` (no project files touched).
- Real interactions performed (sandbox): phone registration +966512345678 → $25 deposit → wallet purchase ×2 (desktop + mobile) → receipts.

---

## 3. Findings by Area

### 3.1 Global Visual Regression (blocking finding)

- **[DEFECT][P0] Tailwind utilities not generated — site is raw unstyled HTML (local + production).**
  Evidence: computed `max-width: none` on `main.max-w-6xl` (w=1440 edge-to-edge); `body` background `lab(100 0 0)` (white) & black text; buy buttons `border-radius:0; padding:0`; stylesheet = 45 rules: 16 `@font-face` + theme/preflight `@layer` blocks + **empty utilities layer** (`@layer components, utilities;` declared, zero rules).
  Screenshots: `agent6-desktop-01-store-full.png`, `agent6-desktop-03-prod-unstyled-proof.png` (production, identical).
  VLM confirmation (desktop-01): *"raw unstyled HTML … plain white background, default browser fonts … single-column list … blue underlined links."*
- **[FACT] Root cause (reproduced):** `globals.css` line `@source "../src";` — from `src/app/globals.css` resolves to `/home/z/my-project/src/src/` (nonexistent — verified `ls`). Scratch compile via `@tailwindcss/postcss` (Tailwind 4.1.18): broken directive → 0 utilities for `max-w-6xl/bg-zinc-950/grid-cols-3`; `@source "../"` → 3/3 generated.
- **[FACT] Historical:** `research/live_capture/final_store_desktop.png` (task 18-19, the "23/23 PASS" deploy) **also shows an unstyled page** (VLM-verified) — the regression shipped to production unnoticed; prior retest verified function, not pixels.
- **[RISK] Cascading effects:** sticky header (`sticky top-0`) currently static; designed focus rings (`focus-visible:ring-[3px]`) inactive (browser default outline IS visible now); bold Tajawal weights (500/800/900) never load (lazy-load on use; `document.fonts.check` false) so weight hierarchy is invisible; intended 40px tap targets render 24px.
- **[RECOMMENDATION][P0]** Change `@source "../src"` → `@source "../"` (or delete `source(none)`+`@source` and use default auto-detection), rebuild, redeploy, and re-run THIS audit's render-blocked checks (§3.2–3.6 marked NOT VERIFIED).

### 3.2 RTL Verification

- **[FACT]** `<html lang="ar" dir="rtl">` (curl HTML + computed). Grid/price containers inherit `direction: rtl`.
- **[TEST RESULT]** Phone input: explicit `dir="ltr"` attribute (computed `direction:ltr`, `text-align:start`) — correct LTR isolation of `+966512345678` inside RTL layout. ✔
- **[TEST RESULT]** Mixed bidi (English product names in Arabic sentences): measured word geometry of card title `Apple iTunes تركيا — 100 TL` via Range API — visual right→left order = `Apple iTunes` (LTR block) → `تركيا` → `100 TL` — **correct bidi, no garbling**. Same pattern for `PSN تركيا — 500 TRY`, `Steam محفظة السعودية — 20 SAR`.
- **[TEST RESULT]** Numerals: 100% Latin/Western digits (prices `3 ر.س`, `$0.76`, times `11:58:48 ص`); no Arabic-Indic ٠١٢ anywhere → **consistent**. Dates use RLM correctly (`28‏/9، 11:59 ص`).
- **[TEST RESULT]** Back arrow: `→ رجوع للمتجر` — right-pointing = correct "back" direction for RTL. ✔
- **[DEFECT][P3]** Process-flow arrows wrong direction in RTL: `يفحص السلسلة → حارس الهامش → الشراء` — measured: arrow glyph sits between the words but **points right at the source**, while semantic flow runs right→left. Should use `←` (or CSS `scaleX(-1)` / logical arrow). Locations: router-status box (store.tsx), similar flow copy.
- **[OBSERVATION]** Card grid RTL placement: grid container `direction: rtl` (computed) → per CSS Grid spec, once utilities load the **first card will sit on the RIGHT**. **RENDER NOT VERIFIED** (CSS bug → currently single full-width column). Re-test after fix.
- **[OBSERVATION]** USD amounts (`$25.00`, `$0.80`) render with `dir="ltr"` isolation inside RTL rows. ✔ (verified on price element: `dir=ltr`).

### 3.3 Typography

- **[FACT]** Tajawal actually applied: computed `body` font-family `Tajawal, "Tajawal Fallback", …`; self-hosted via `next/font` (16 @font-face rules, Arabic + Latin unicode-range split). `document.fonts.check('16px Tajawal')` = true. ✔
- **[DEFECT][P2]** Micro-typography for Arabic UI text: `text-[9.5px]` ×2, `text-[10px]` ×12, `text-[10.5px]` ×3 (trust badges strip, header/footer meta). Below any legibility floor for Arabic script (recommend ≥12px); hurts elderly users and perceived trust.
- **[DEFECT][P2]** Zero heading elements on the store page (`h1=h2=h3=0` — verified live DOM). Visual hierarchy is flat: largest text = prices (24px mono); brand name only 15px. (404 page has a proper `h1`; /intel has `h1` ✔.)
- **[OBSERVATION]** Line-heights: micro text `leading-4` (≈1.45) acceptable; body 15px at `leading-5` (1.33) tight for Arabic — recommend ≥1.5.
- **[FACT]** Latin product names/digits render in Tajawal's Latin subset (no font-switch flash) — good.

### 3.4 Responsive / Mobile (390×844)

- **[TEST RESULT]** Store: **no horizontal overflow** — `scrollWidth 390 = clientWidth 390`; zero off-viewport elements. (Caveat: unstyled single-column flow; re-test after CSS fix.)
- **[TEST RESULT]** Full purchase flow operable at 390px: screenshots `agent6-mobile-02…05`; VLM: *"no horizontal clipping; text wraps correctly; phone number and $24.21 displayed LTR; readable."*
- **[DEFECT][P2]** /intel mobile horizontal overflow: `scrollWidth 629 > 390` (local AND production — same 629px). Wide tables force 239px horizontal scroll; in RTL this scrolls leftward — disorienting. Needs re-test after CSS fix (tables may be constrained then), but flag now.
- **[OBSERVATION]** Sticky header designed (`sticky top-0 z-40`) — currently `position: static` (CSS bug). NOT VERIFIED rendered.
- **[OBSERVATION]** Tap targets: intended `h-10` (40px) full-width buy buttons — borderline vs 44px (Apple HIG)/48dp (Material). Current rendered 24px is a CSS-bug artifact. NOT VERIFIED styled.
- **[OBSERVATION]** No viewport `<meta>` issues (`width=device-width, initial-scale=1` present ✔).

### 3.5 Interaction States

- **[FACT]** Designed states exist in classes (render-blocked by P0): `hover:bg-emerald-800`, `focus-visible:ring-[3px] focus-visible:border-ring`, `disabled:opacity-50 disabled:pointer-events-none`. NOT VERIFIED rendered.
- **[TEST RESULT]** Keyboard Tab navigation works; focus moves through header/catalog buttons; **focus IS currently visible** (browser default `outline: auto 1px`, because `outline-none` utility also missing). Designed 3px ring NOT VERIFIED.
- **[TEST RESULT]** Disabled states functional: OOS cards → `button[disabled] "نفد — فعّل تنبيه التوفير"`; pay button disabled until wallet funded, then enabled. ✔
- **[TEST RESULT]** Purchase progress states (desktop `agent6-desktop-10/11`, mobile `agent6-mobile-05`): stepper `بانتظار الدفع → تم الدفع → الموجّه يشتري → تم التسليم`, animated router box (source: `animate-pulse` "⚙️ الموجّه يعمل الآن…"), SANDBOX receipt block with copy affordance, cashback `+$0.01` — all rendered and sequenced correctly.
- **[DEFECT][P2]** Catalog fetch: **no loading skeleton, no error state, no auto-retry** — `loadCatalog = if (res.ok) setCatalog(res)` (store.tsx:782); on failure the catalog area is permanently blank with no message (only a manual "🔄 تحديث المزامنة" button). Bad for flaky mobile networks (Yemen market).
- **[OBSERVATION][P3]** Deposit UX: success toast "✓ إيداع تجريبي — فوري" appears ~2–4s **before** balance/ledger refresh (polling) — momentary "did it work?" doubt.
- **[OBSERVATION][P3]** Quick-amount buttons ($10/$25/$50/$100) only prefill the amount spinbutton; a second "إيداع" click is required — one-tap expectation unmet (I clicked $25 expecting a deposit).

### 3.6 Accessibility

- **[FACT]** Landmarks on both pages: `header`(banner) / `main` / `footer`(contentinfo). /intel additionally has `h1` + `role="tablist"`. ✔
- **[DEFECT][P2]** Store page: zero headings (see §3.3) — screen-reader section navigation impossible.
- **[TEST RESULT]** No `<img>` elements anywhere (SVG/emoji icons) → no alt-text debt; but emojis-as-icons (⚡🔒💸👛) are read literally by screen readers. [OBSERVATION][P3].
- **[TEST RESULT]** Contrast (computed from Tailwind palette of classes actually used): body zinc-100/zinc-950 **18.1:1 AAA**; muted zinc-400/zinc-950 **7.76:1 AAA**; buy-btn emerald-100/emerald-900 **8.57:1 AAA**; badge emerald-300/emerald-950 **9.94:1 AAA**; **zinc-500/zinc-950 = 4.12:1 — FAILS AA** for the 10px meta text that uses it. **[DEFECT][P3]**.
- **[OBSERVATION][P3]** All inputs (phone, search, deposit amount) are placeholder-only — no `<label>`, no `aria-label` (verified live DOM).
- **[OBSERVATION][P3]** /intel tables: `th[scope]` missing (2 tables).

### 3.7 Console Errors

- **[TEST RESULT]** Local `/`: clean — zero errors/warnings beyond HMR noise; zero failed requests (all API calls 200: catalog, wallet ×n, deposit, checkout).
- **[TEST RESULT]** Local `/intel`: clean — zero console errors, zero failed requests.
- **[TEST RESULT]** Production `/` (fresh reload): clean — zero console errors, zero 4xx/5xx.
- **[FACT]** The CSS omission is **silent** — no console error, no build error (Tailwind happily emits empty utilities) → why it survived prior audits.

### 3.8 /intel Quick Pass

- **[TEST RESULT]** Loads (title "Supplier Intelligence — مركز استخبارات الأسعار"), RTL, 17 tab buttons; clicked 3 tabs (🔓 الأسعار الحية API، سجل التدقيق، مصفوفة 91 قناة) — all switch and render correct content (stats, tables, Arabic narrative). Screenshots `agent6-desktop-12/13/14`.
- **[OBSERVATION]** Arabic shell + English data entries (audit-log records in English) — acceptable for an owner research tool; keep as conscious choice. Mobile overflow defect noted in §3.4.

---

## 4. UX Improvement Priorities (Usability/Trust/Conversion-justified)

1. **[P0] Fix Tailwind `@source` path** (`"../src"` → `"../"`), rebuild, redeploy. Until then the storefront projects zero trust — a payments site that looks like broken 1995 HTML cannot convert Saudi/Yemeni buyers. Then **re-run render-blocked checks** (grid RTL order, focus ring, hover, tap targets, sticky header, styled modal).
2. **[P2] Catalog loading/error states** (skeleton + error + auto-retry): silent blank catalog = direct lost sales on unstable mobile data (primary Yemen channel).
3. **[P2] Typography floor for Arabic**: ≥12px minimum, real `h1` on store, raise trust-badge strip size — trust badges are the conversion argument and currently the smallest text on the page.
4. **[P2] /intel mobile tables**: wrap in horizontal-scroll container or responsive cards (owner checks prices on phone).
5. **[P3] RTL flow arrows** (`→` → `←`), phone input `type="tel"` + `inputmode`, fix zinc-500 contrast pair, form labels/`aria-label`s, deposit one-tap + balance refresh timing, `th[scope]`.

---

## 5. Limitations

- All styling-dependent visual verdicts (rendered RTL grid order, hover/focus/disabled visuals, tap-target styled sizes, sticky behavior, modal overlay design, intended font weights) are **design-verified from class names or NOT VERIFIED** because of the P0 CSS omission — a follow-up visual audit after the fix is REQUIRED.
- Chromium only (no Safari/Firefox); mobile emulated, no real device; no screen-reader run (TalkBack/VoiceOver) — a11y findings are DOM/contrast-based.
- VLM (glm-5v-turbo) used as secondary confirmation only; primary evidence is computed styles + DOM geometry (VLM misidentified some details, e.g., "Visa/Mastercard" hallucination — discounted).
- Production checked read-only (load + console + CSS); purchase E2E executed only on local sandbox. Production and local confirmed byte-equivalent in behavior/CSS for all compared probes.
- Scratch Tailwind reproduction ran in `/tmp` (diagnostic only); project sources untouched per mandate.
