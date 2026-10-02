# AUDIT-5 — Frontend & Application Code Audit (MEC Store)

- **Task ID:** AUDIT-5 · **Date:** 2026-09-28 · **Agent:** AUDIT-5 (Frontend & Application Engineer)
- **Scope:** `src/app/**` (page, layout, not-found, intel, globals.css), `src/components/store/store.tsx`, `src/components/intelligence/*` (18 tabs), `src/components/ui/*` (primitives, spot-check), client↔API contract (read of `/api/store/*`, `/api/wallet*`, `/api/admin/*` routes to validate client assumptions). **No modifications.** One dev-server `curl` of `/` and `/intel` to verify rendered markup (allowed; no browser tests).
- **Context read first:** `worklog.md` entry "Task ID: 18-19" (production hardening run; store.tsx reconstructed 1:1 from the deployed bundle + hardening).

---

## 1. Executive Summary

The frontend is a **compact, disciplined two-page app**: an Arabic-first RTL store (`/`) and an owner research dashboard (`intel`, 18 tabs). The store component (`src/components/store/store.tsx`) is **918 lines / 6 components / 29 useState / 6 useEffect / 5 useCallback / 1 useRef** — far from the feared 1,500-line monolith (the 1,510-line figure in worklog 18-19 refers to the *beautified production bundle*, not the source). Decomposition is reasonable: one orchestrator (`Store`) + 5 panel components with clear responsibilities and a simple `view` state machine.

**RTL quality is genuinely high** (FACT): `dir="rtl" lang="ar"` verified in live SSR markup, **zero** physical `ml-/mr-/pl-/pr-` classes in store/app code, logical `ms-/me-/pe-/text-start` used in the intel components, and disciplined `dir="ltr"` on all numeric/mono content. Only 3 harmless physical `text-right` usages remain.

The serious problems are **resilience, not architecture**:

1. **[DEFECT][P1]** The shared `api()` helper (store.tsx:51-56) has **no error handling of any kind** — no HTTP `res.ok` check, no try/catch, no JSON-parse guard — and **none of its ~10 call sites wrap it**. A network blip during checkout permanently disables the buy button (`busy` never resets) with zero feedback; the order-polling interval throws unhandled every 2.5s.
2. **[DEFECT][P1]** The catalog has **no loading, empty, or error state** (store.tsx:879) — a failed/slow `/api/store/catalog` leaves the page showing only the phone card, forever, silently.
3. **[DEFECT][P2]** Client phone validation is much looser than the server's (`≥8 digits` vs `^\+96[67]\d{8,9}$`) — users can "register" numbers the API will reject at checkout/deposit time.
4. **[RISK][P2]** API responses are consumed as untyped `any` with no shape validation; a product missing both region and WW prices (allowed by `getCatalog`, engine.ts:58-60) would throw `TypeError` at store.tsx:133 and **crash the whole page** — there is **no `error.tsx`/`global-error.tsx` anywhere** (verified `src/app/` contents).
5. **[RISK][P2]** `/intel` renders `new Date().toISOString()` into SSR HTML (intel/page.tsx:25) — a **hydration mismatch** by construction (server minute ≠ client minute), confirmed in the served HTML.

Type safety is mixed: `strict: true` and `ignoreBuildErrors: false` (FACT, next.config/tsconfig), zero `@ts-ignore` — but **34 `as any` casts** concentrated in the intelligence components and one in the checkout route. A11y is the weakest dimension: no `aria-label`/`aria-pressed`/`<Label>` in the store at all, with placeholder-only inputs and 8.5–9.5px text sizes.

---

## 2. Component Map

```
app/layout.tsx (SERVER — <html lang="ar" dir="rtl" suppressHydrationWarning>, Tajawal+Geist_Mono
                fonts, metadata AR/OG, <Toaster/> [dead code — see F-14])
├── app/page.tsx (SERVER — header/trust-strip/footer, <h1> MISSING; renders <Store/>)
│   └── components/store/store.tsx ("use client", 918 lines, 6 components):
│       └── Store (orchestrator, store.tsx:767-918)
│           ├── [view=catalog]  StoreGrid      (:64-171)   — search q + family filter, product cards
│           ├── [view=checkout] CheckoutPanel  (:180-301)  — rail selection, submit, payment instructions
│           ├── [view=order]    OrderView      (:313-477)  — 2.5s polling, progress, receipt, waitlist
│           ├── [view=wallet]   WalletPanel    (:485-571)  — balance, deposit, tx ledger
│           ├── [view=admin]    OpsPanel       (:579-764)  — admin token gate, stats, sync
│           └── (header card with phone registration — inline in Store, :813-877)
├── app/not-found.tsx (SERVER — Arabic 404, RTL, links to / and /intel)
├── app/intel/layout.tsx (SERVER — metadata + robots noindex,follow=false)
│   └── app/intel/page.tsx ("use client" — 17 TabsContent; Mec8 fetches /api/store/catalog,
│       all other tabs render statically-imported JSON from src/lib/data/*.json)
└── components/intelligence/* (18 files, ALL "use client"; only mec8/batch2/skus/entities/
    channel-matrix/audit use hooks — search filters & one fetch; shared.tsx = badge helpers)
```

**Store component stats (FACT, counted):** 918 lines; **29 `useState`** (StoreGrid 2, CheckoutPanel 5, OrderView 4, WalletPanel 5, OpsPanel 5, Store 8), **6 `useEffect`**, **5 `useCallback`**, **1 `useRef`** (poll timer), 0 context/0 reducer/0 third-party state libs. Client components project-wide: **20 app-level** (store, intel page, 18 intel tabs incl. shared) + ~47 shadcn primitives (all `'use client'`). Server components: `page.tsx`, `layout.tsx`, `not-found.tsx`, `intel/layout.tsx`, all API routes.

**State management assessment (OBSERVATION):** No prop drilling beyond one level (orchestrator→panel via props — clean). Good derived-state discipline: `region` is derived from `phone` every render (store.tsx:777-778) instead of stored; `price`, `usd`, `canAfford` derived in CheckoutPanel (:190-192). The intentional `phone`/`phoneInput` pair (committed vs editing value, :768-769) is a standard pattern. Real duplication: wallet balance lives in **both** `Store.balance` (:774, fetched by `loadBalance` :785-789) **and** `WalletPanel.balance` (:486, fetched by `refresh` :492-495) from the same endpoint, synced manually via the `onBalance` callback — two fetch paths for one resource (drift-prone; see F-9). List keys: product cards keyed by `p.slug` (:122, good); steps/txs/orders/syncs keyed by array index `key={i}` (:457, :552, :698, :724, :751) — acceptable for append-only lists, but orders/syncs have stable ids (`publicId`, `at`) that would be better keys.

---

## 3. Findings by Category

### 3.1 API Integration (fetch patterns)

**F-01 [DEFECT][P1] — `api()` helper has no error handling; failures strand the UI.**
- Evidence: `store.tsx:51-56` — `async function api(path, body?, headers?) { const res = await fetch(...); return res.json(); }`. No HTTP `res.ok` check (only the *body-level* `ok` field is checked by callers), no try/catch, no non-JSON guard.
- Impact chain (evidence per call site):
  - `CheckoutPanel.submit` (:194-203): `setBusy(true)` → `await api(...)` → if fetch rejects (offline/DNS) **or** server returns non-JSON (proxy 502 HTML), the exception propagates, `setBusy(false)` at :198 never runs → **buy button stuck on "⏳ جارٍ الإنشاء…" forever, no error shown**. This is the payment path — worst possible place.
  - `WalletPanel.deposit` (:499-507): same pattern → deposit button stranded busy.
  - `OrderView` poll (:330-336): `setInterval(async () => { const res = await load(); ... })` — a single rejection inside the interval callback = unhandled promise rejection **every 2.5 s**; `load` (:322-326) also has no guard.
  - `Store.loadCatalog` (:780-783) / `loadBalance` (:785-789) / `OpsPanel.load` (:588-592) / `saveToken` (:595-600) / `sync` (:602-611): all unguarded.
- Mitigating FACT: all app API routes return JSON error bodies (incl. 429 — `lib/ratelimit.ts:50-56` returns Arabic JSON `{ok:false,error}`), so *application-level* errors do display correctly via `res.error` (e.g., store.tsx:202, :505). The gap is purely transport/HTML-body failures.
- RECOMMENDATION: wrap `api()` in try/catch returning `{ok:false,error:"تعذّر الاتصال — تحقق من الشبكة"}`, and add a `finally { setBusy(false) }` in submit/deposit.

**F-02 [DEFECT][P1] — Catalog: no loading skeleton, no empty state, no error/retry.**
- Evidence: `store.tsx:879` — `{view === "catalog" && catalog && (<StoreGrid .../>)}`. While `catalog === null` (fetching **or** failed — the state is indistinguishable) the page renders nothing under the phone card. `loadCatalog` (:780-783) silently swallows failure (`if (res.ok) setCatalog(res)` — else nothing). No `retry` affordance; the only refresh path is a button *inside* StoreGrid (:82-84), which is absent when the grid is absent.
- TEST RESULT (curl of live dev SSR, /tmp/mec_home.html): 27,821 bytes; `grep -c 'جارٍ'` → **0** (no loading marker); zero product names in HTML (the single شاهد/ChatGPT match is the `<meta name="keywords">`, layout.tsx:24-36); `MEC STORE W1` and `تسجيل / تحديث` present.
- Empty sub-case: `products: []` renders header "🛒 المتجر — 0 منتجًا" (:80) and an empty grid — no explanatory empty state (minor).
- RECOMMENDATION: tri-state `catalog: null | error | data` + skeleton (shadcn `skeleton.tsx` exists unused in ui/) + Arabic error card with retry.

**F-03 [RISK][P3] — Polling race: overlapping responses, no abort/in-flight guard.**
- Evidence: `store.tsx:328-339` — `setInterval(... , 2500)` calls `load()` without awaiting the previous one; responses can resolve out of order → a stale `routing` snapshot can overwrite a newer `delivered` snapshot (UI briefly regresses; interval-clear condition at :332 evaluated per-response). No `AbortController` anywhere in the codebase (grep-verified). `eslint-disable react-hooks/exhaustive-deps` at :338. Also :332 dereferences `res.order.status` — if a future API change returns `ok:true` without `order`, TypeError (currently the route always returns `order`, `orders/[id]/route.ts` — ASSUMPTION on contract stability).
- Also `Store` balance effect `useEffect(() => { if (phone) loadBalance(); }, [phone, loadBalance, view])` (:797) refetches on every view switch — intentional freshness, acceptable.

**F-04 [OBSERVATION][P3] — No retry logic anywhere; single-shot fetches.** Only the human-visible "🔄 تحديث المزامنة" button (store.tsx:82) and view-switch refetches act as manual retries. Acceptable for W1; note for resilience roadmap.

### 3.2 Forms & Validation

**F-05 [DEFECT][P2] — Client phone validation much looser than server (validation asymmetry).**
- Evidence: client `register()` — `store.tsx:800-808`: `const cleaned = phoneInput.replace(/[^\d+]/g,""); if (cleaned.replace(/\D/g,"").length < 8) setError(...) else setPhone(cleaned)`. **Any ≥8-digit string passes** (e.g., `0512345678` without country code, `+14155551234`, `+9660512345678` = 10 digits after CC).
- Server authority (good FACT): `lib/format.ts:11-16` `normalizePhone` enforces `^\+96[67]\d{8,9}$`; enforced at checkout (`checkout/route.ts:23-31`, Arabic 400), wallet (`wallet/route.ts:12-17`), deposit (`deposit/route.ts:15-19`).
- Impact: user "registers" successfully, region shows 🌍 دولي (region derived :777-778 from non-966/967 prefix), proceeds to checkout, and only then gets «بيانات ناقصة: slug + جوال صحيح مطلوبان (+966/+967)» (checkout/route.ts:28) — generic panel-level error, not a field error next to the phone input.
- Error display (FACT): Arabic messages throughout; phone errors render inline under the input (:871-875) via `phoneError` — good; checkout errors render as a generic banner inside CheckoutPanel (:281-285), not field-anchored. No inline field-level errors for rail/amount.
- RECOMMENDATION: reuse `normalizePhone` (lib/format.ts) client-side for instant Arabic feedback; import shared constants instead of re-implementing.

**F-06 [OBSERVATION][P2] — Double-submit protection: present on money paths, missing on two actions.**
- Protected (FACT): checkout submit `disabled={busy || (rail==="wallet" && !canAfford)}` (:288); deposit `disabled={busy}` (:525); sync `disabled={busy}` (:673). `busy` set synchronously before `await` (:196, :502, :603) — no double-click window.
- Unprotected: `simulateConfirm` (:341-344) and `restock` (:345-348) — no busy state; double-click fires duplicate requests. Mitigated server-side (FACT): payments idempotent (worklog 18-19 verified), restock dedupes on `(productId, phone)` (`restock/route.ts:20-26`). P3 severity in practice.

**F-07 [OBSERVATION][P2] — Deposit amount validation duplicated, live-mode deposit incomplete in UI.**
- Client guard `!(n >= 5) || n > 500` with Arabic msg (:500-501) duplicates `DEPOSIT_MIN/MAX` from lib/format.ts:70-71 (numeric literals — drift risk). Server re-validates (deposit/route.ts:21-27) — good defense in depth.
- Live-mode gap: when `STORE_MODE === "live"`, deposit returns `{ok:true, pending:true, note}` with **no address** (deposit/route.ts:30-36); WalletPanel shows only `✓ {res.note}` (:505) — the note promises «سيُعرض عنوان إيداع مخصص» but the UI has no pending state and never displays an address. Documented as W2 scope in the route comment, but as written the live deposit flow dead-ends in UI. [RISK][P2 conditional on live mode].

### 3.3 Loading / Empty / Error / Success States (inventory)

| State | Location | Verdict |
|---|---|---|
| Catalog loading | — (store.tsx:879 renders nothing) | **MISSING** [DEFECT P1, F-02] |
| Catalog error | loadCatalog swallows (:780-783) | **MISSING** [F-02] |
| Catalog empty | header count "0 منتجًا" (:80) only | Partial (no message) |
| Product out-of-stock | card opacity + Arabic label + disabled buy + waitlist CTA (:112-116, :151, :154) | **GOOD** |
| Wallet empty txs | "لا حركات بعد" (:548-549) | **GOOD** |
| Wallet requires phone | "سجّل رقم جوالك أولًا" (:908-913) | **GOOD** |
| Checkout success | payment instructions panel (:233-249) → OrderView receipt: delivered payload copy button (:397-424), cashback line (:418-422), refund+apology block (:425-442) | **GOOD** |
| Order failed | refund notice + "أعلمني عند التوفير" → post-register notice (:434-440) | **GOOD** |
| Ops no-orders / no-syncs / auth | "لا طلبات بعد" (:721), "لم تُنفّذ مزامنة بعد" (:748), token gate (:626-646) | **GOOD** |
| OrderView order-load failure | `order` stays null → renders header + back button only, no error text | **MISSING** [P3] |
| Mec8 catalog fetch | loading text (:163); **error swallowed** `.catch(() => setProducts([]))` (:52) → empty table indistinguishable from "no ps products" | Partial [P3, F-15] |

### 3.4 Hydration & SSR Safety

**F-08 [RISK][P2] — `/intel` hydration mismatch by construction.**
- Evidence: `app/intel/page.tsx:1` `'use client'` + `:25` `const lastChecked = new Date().toISOString().slice(0,16)...` rendered at `:53` "Last Checked: {lastChecked}". Client components ARE server-prerendered in App Router → the served HTML embeds the server's minute; hydration renders the client's minute → React 19 hydration error (console error + client re-render of the tree).
- TEST RESULT: `curl /intel` → HTML contains `Last Checked: <!-- -->2026-09-28 11:55 UTC` — server timestamp baked in; any client hydration ≥ 1 minute later mismatches.
- Store page is clean (FACT): `localStorage` reads only inside `useEffect` (:791-795, :586); all `new Date(...).toLocaleTimeString("ar")` usages (:557, :753, :828) render data that exists only after client fetch — never SSR'd. `Math.random`/`Date.now` absent from all rendered components (only in `ui/sidebar.tsx:611`, which is **unused** — not imported by any page; and `lib/format.ts:47` server-side ID gen).
- RECOMMENDATION: compute `lastChecked` in `useEffect` state (post-mount) or render `suppressHydrationWarning` on that span.

**F-09 [OBSERVATION][P2] — Store is effectively client-rendered; SEO impact for an Arabic commerce page.**
- Evidence: `Store` is `'use client'` (store.tsx:1); catalog arrives only via client `fetch` (:781). TEST RESULT (curl /): zero products/prices in SSR HTML (only meta keywords mention product words). No per-product routes exist (no `app/store/[slug]`), and the store page has **no `<h1>`** (grep: only /intel has one) — headline text is a `<div>` (page.tsx:15).
- Mitigating FACT: full Arabic `metadata` (title/description/keywords/OG, layout.tsx:20-45), `lang="ar" dir="rtl"` on `<html>` (SSR-verified), self-hosted Tajawal woff2 (SSR-verified `font/woff2` refs + body font-family style, layout.tsx:9-13, :54-56). Googlebot does execute JS, so indexing is degraded-not-broken; non-JS crawlers and link-preview bots see only header/trust/footer text.
- RECOMMENDATION (W2): server-render catalog (RSC fetch) or per-product static pages; add `<h1>` on `/`.

### 3.5 RTL & A11y (code level)

**RTL verdict: HIGH QUALITY.**
- FACT: `<html lang="ar" dir="rtl" suppressHydrationWarning>` (layout.tsx:53) — verified in live SSR markup of both `/` and `/intel` (`dir="rtl"` count 1 per page).
- FACT (grep, store + app + intelligence): **zero** `ml-`/`mr-`/`pl-`/`pr-`/`text-left`/`left-`/`right-` physical utilities; `space-x-*` not used. Logical properties used where needed: `ms-auto` (intel/page.tsx:40), `text-start`/`pe-2` (skus.tsx:25, :81-87), `text-end` (skus.tsx:41).
- Only 3 physical `text-right` usages — store.tsx:259 (rail buttons), :410 (payload copy button), :688 (supplier table header). In RTL, physical-right == inline-start, so **visually correct** today; they break only if the page is ever rendered LTR. [OBSERVATION][P3] — recommend `text-start` for future-proofing.
- FACT: `dir="ltr"` applied to ~40 numeric/code/mono elements (prices, addresses, publicIds, phone masked, scores) — correct bidi handling for mixed Arabic/latin-numeral content (e.g., store.tsx:132, :225, :362, :373-376, :514; skus.tsx:43, :78).

**A11y findings (all P3 unless noted):**
- **F-10 [OBSERVATION][P3] No `aria-*` on any store interactive element** (grep: `aria-` appears only inside unused ui primitives). Family filter buttons lack `aria-pressed` (:95-105); rail selector buttons lack `role="radio"`/`aria-checked` (:256-261); availability dot relies on color + `●` glyph but has text label (:142-143) — OK.
- **F-11 [OBSERVATION][P3] Placeholder-only inputs; zero `<Label>`/`htmlFor`** in store/app (grep-verified). Inputs: search (:87-93), phone (:850-857), deposit amount (:519-524), admin token (:633-640). Screen-reader support rests entirely on placeholder announcement. `<Input>` primitive supports `aria-invalid` styling (input.tsx:13) but it is never used with `aria-invalid` by the store.
- FACT (good): all clickables are real `<button>`/`<Button>` — no clickable `<div>`s (family chips :95, rails :256, quick-amounts :531, payload copy :402 are all buttons); Enter-key handlers on inputs (:639, :856); no `<img>` tags at all (emoji-only) → no alt issues; `not-found.tsx` uses real `<Link>`s.
- **F-12 [OBSERVATION][P3] No focus management on view switches** (catalog→checkout→order are state swaps, :770): focus stays on the clicked button which may unmount; keyboard users land nowhere. No modals exist (so no focus-trap need). `navigator.clipboard?.writeText` guarded (:405).
- **F-13 [OBSERVATION][P3] Micro-typography & contrast**: text sizes down to `text-[8.5px]` (:127, :555, :737) and `text-[9px]`/`[9.5px]` in many places; `text-zinc-600`/`zinc-700` on `zinc-950` backgrounds (e.g., :145, :163-167, :541-543) — borderline WCAG contrast at tiny sizes. Design choice for density, but flag for a11y review.

### 3.6 Type Safety in Components

- **F-14 [OBSERVATION][P3] `api()` returns `any`; responses consumed without validation.** `res.json()` → `Promise<any>` (store.tsx:55); every call site does dynamic property access (`res.ok`, `res.order`, `res.payment`, `res.balance`, `res.productsSeen`, …) and states are set from `any` (`setCatalog(res)` :782, `setOrder(res.order)` :324, `setStats(res)` :590). Typed interfaces exist (store.tsx:14-37) but are only used for *state*, never to validate *responses* — the fetch→state boundary is unchecked. If a product lacks `prices[region]` and `prices.WW`, `price.price` at :133 (and :190-191) throws TypeError → **crashes the entire client tree**; `getCatalog` builds `prices` straight from DB rows with no WW guarantee (engine.ts:58-60) and the catalog route does not filter priceless products. Combined with **no `error.tsx`/`global-error.tsx`** (verified: only layout/page/not-found/globals.css/intel/api in `src/app/`), this is a white-screen path. [RISK][P2 — data-dependent, contract-adjacent]. RECOMMENDATION: guard `price` (skip card) + add root `error.tsx` (Arabic).
- **F-15 [OBSERVATION][P3] 34 `as any` casts**, concentrated in intelligence components reading static JSON (overview.tsx:9,77,86,101; decisions.tsx:22,48,95,117; direct-wave.tsx:8,64,89,110,143; audit.tsx:10-13; batch3.tsx:8,82,111; skus.tsx:18-19,91; mec5.tsx:24; channels/channel-matrix/mec6/mec7/entities/supply/deep-dive/open-items: 1-5 each) and **1 in an API route** (`checkout/route.ts:32` `RAILS.includes(rail as any)` — should be `(RAILS as readonly string[]).includes(rail)`). Static JSON is bundled at build time so runtime risk is low, but the casts defeat the `strict: true` guarantee (tsconfig.json:11) across the whole dashboard. Zero `@ts-ignore`/`@ts-expect-error` (FACT — good).
- FACT (good): `typescript.ignoreBuildErrors: false` (next.config.ts) — type errors fail the build.

### 3.7 Intel Dashboard (quick pass)

- **F-16 [OBSERVATION][P3] Data loading: static JSON imports, all client-side.** All tabs except Mec8 render `src/lib/data/*.json` via ES imports inside `'use client'` components (e.g., skus.tsx:7, mec5.tsx:4, lib/data/index.ts:2-20) → the entire research dataset ships in the client JS bundle. Fine for a private owner dashboard; would be a bundle-size problem if any of this leaked to the public store chunk (it doesn't — separate route).
- **F-17 [FACT] Tab switching**: Radix `Tabs` (`intel/page.tsx:60-98`), `defaultValue="mec8"`, 17 `TabsContent`s; inactive tabs unmount (no `forceMount`) → only the active tab's JSON render cost is paid per switch. Switching is state-only (no URL hash) → refresh always returns to Mec8 tab (worklog 18-19 already logged the "render check ≠ tab content" lesson).
- Runtime-error scan: components are pure render over static JSON + one guarded fetch (mec8.tsx:46-53, error swallowed — F-15 above / table in 3.3). `batch2.tsx` uses `useMemo` for filtered rows (:27) — fine. `mec8.tsx:59` uses non-null assertion `p.chain.find(...)!` after `.some()` guard (:57) — safe but brittle if supplier codes change. No dangerouslySetInnerHTML outside unused `ui/chart.tsx`. **No runtime-error defect found** in the dashboard beyond the hydration timestamp (F-08).

---

## 4. Hydration / SSR Assessment (summary)

| Risk | Location | Status |
|---|---|---|
| `new Date()` at render | intel/page.tsx:25 | **CONFIRMED mismatch** (SSR minute baked into HTML, verified via curl) [P2] |
| `Date.now`/`Math.random` in rendered tree | none in store/intel (sidebar.tsx:611 unused; format.ts server-only) | Clean |
| `localStorage` | store.tsx:792, :586-596 — read in `useEffect`/handlers only; `getAdminToken()` guards `typeof window` (:58-61) | Clean |
| Locale-dependent rendering | `toLocaleString("ar")` only on client-fetched data (:557,:753,:828) | Clean |
| `suppressHydrationWarning` on `<html>` | layout.tsx:53 | Present (for font/class injection) |

**Store page = hydration-safe. Intel page = one deterministic hydration mismatch.**

## 5. Top-10 Fix List (priority order)

1. **[P1] Harden `api()`** (store.tsx:51-56): try/catch → `{ok:false, error:"تعذّر الاتصال بالخادم…"}`; check `res.ok` HTTP status; guard JSON parse. Fixes stranded-busy checkout/deposit + unhandled polling rejections (F-01).
2. **[P1] Catalog tri-state UI** (store.tsx:879, :780-783): loading skeleton, Arabic error card + retry button, empty-catalog message (F-02).
3. **[P2] Validate phone client-side with `normalizePhone`** (store.tsx:800-808 ← lib/format.ts:11-16) so registration, not checkout, is where invalid numbers die (F-05).
4. **[P2] Add root `app/error.tsx` + `app/global-error.tsx`** (Arabic) — currently ANY client render error white-screens the store (F-14).
5. **[P2] Guard missing prices** in StoreGrid/CheckoutPanel (store.tsx:110-119, :133, :190-191) — skip card / disable buy when `price` undefined (F-14).
6. **[P2] Fix intel hydration**: move `lastChecked` to post-mount state or `suppressHydrationWarning` (intel/page.tsx:25, :53) (F-08).
7. **[P2] Live-mode deposit UX**: pending state + address display, or hide instant-deposit UI when `mode === "live"` (store.tsx:499-507 ↔ deposit/route.ts:30-36) (F-07).
8. **[P3] Single wallet source of truth**: lift balance fetch into `Store` (or context) and have WalletPanel consume it — removes dual-state drift (store.tsx:774/:785 vs :486/:492) (F-09/3.2 state map).
9. **[P3] A11y pass on store**: `aria-label`s on inputs, `aria-pressed` on family chips (store.tsx:95-105), `aria-invalid` on error fields, replace `text-right`→`text-start` (:259,:410,:688), bump 8.5-9.5px text where feasible (F-10..F-13).
10. **[P3] Type the API boundary**: `zod` (or manual guards) on catalog/checkout/order responses; replace `as any` in intel tabs with generated JSON types; fix `rail as any` (checkout/route.ts:32) (F-14/F-15).

(Honorable mentions: polling in-flight guard or AbortController at store.tsx:330; remove dead `Toaster` from layout.tsx:59 or actually adopt toasts for checkout success; URL-encode order view via `/order/[publicId]` for shareability/back-button; add `<h1>` to page.tsx.)

## 6. Limitations

- Static code analysis only — no browser interaction, no visual rendering checks (Agent 6 owns visual), no `next build` (rules), no Lighthouse/axe runs (a11y verdicts are code-level, not WCAG-audited).
- Runtime behaviors (stuck-busy, crash-on-missing-price, hydration console errors) are **derived from code paths**, not reproduced live; the price-crash scenario depends on DB state (no price-less active product verified — flagged as RISK, not confirmed DEFECT).
- The dev server (`localhost:3000`) was curled for markup facts only (dir/lang/fonts/SSR content); production markup assumed identical to source since local tree is the authoritative post-hardening rebuild (worklog 18-19).
- `components/ui/*` primitives (47 files) were spot-checked (input/button/toaster/tabs/skus-usage), not audited line-by-line; most are unused by the two pages.
- Bundle-size, LCP/FCP, and CSP-effectiveness ('unsafe-inline'/'unsafe-eval' present in next.config.ts CSP — noted, security-owned) were not measured.
