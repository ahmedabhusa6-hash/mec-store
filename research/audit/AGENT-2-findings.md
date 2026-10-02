# AUDIT-2 — System Architecture & Code Quality Audit (MEC Store)

Task ID: AUDIT-2 · Agent: Architecture & Code Quality Engineer · Read-only audit (no source modifications)
Scope: `/home/z/my-project` local tree (declared authoritative per worklog Task 18-19). No HTTP endpoint testing (owned by other agents), no `next build`, no git ops.

---

## 1. Executive Summary

The codebase is a small, cleanly-layered Next.js 16 App Router app (11,345 TS/TSX lines in `src/`, 10 API route files, 7 lib service modules, 10 Prisma models) with excellent store↔intelligence separation and a consistent Arabic-first error contract. `npx tsc --noEmit` passes with **0 errors**. However:

- **[FACT][P2]** ESLint is effectively disarmed: `eslint.config.mjs:10-45` turns off ~30 quality rules (incl. `no-explicit-any`, `no-unused-vars`, `no-undef`, `no-unreachable`, `exhaustive-deps`, `no-console`), and `tsconfig.json:13` sets `noImplicitAny: false` under `strict: true`. The green tsc/“0 errors” signal is therefore weaker than it appears.
- **[TEST RESULT][P2]** `npm run lint` exits **1** with **2250 problems** — but 2222 warnings come from linting minified research artifacts (`research/live_capture/chunks/*.js`), i.e. missing eslint ignores, not product code. Scoped `npx eslint src/` = **6 problems (5 errors, 1 warning)**, all in `store.tsx` (`react-hooks/set-state-in-effect`).
- **[DEFECT][P1]** Live-mode purchase call passes the **supplier code as product ID**: `engine.ts:176` `psPurchase(String(link.supplier))` → POST `/v1/orders {product_id:"ps"}`. The schema already has `ChainLink.externalId` (`prisma/schema.prisma` ChainLink model) which is never used. Latent (sandbox unaffected; fires when `STORE_MODE=live`).
- **[DEFECT/RISK][P1]** Payment confirmation endpoint is mode-blind: `src/app/api/store/payments/confirm/route.ts` has no `STORE_MODE` gate and accepts any client-supplied `txid` without verification; the UI shows the "محاكاة تأكيد الدفع (sandbox)" button regardless of mode (`store.tsx:244-248`, `store.tsx:386-395`). In live mode a user could trigger a real supplier purchase without paying.
- **[RISK][P2]** Wallet debit is not transactional: `checkout/route.ts:56-70` reads balance → creates order → writes debit ledger row in separate awaited calls with no DB transaction or idempotency key; concurrent checkouts can double-spend into negative balance.
- **[FACT][P2]** 35 of 48 runtime dependencies are unreachable from app code (shadcn scaffold: ~4,887 of 5,397 lines in `src/components/ui/` are dead). Worklog Task 18-19 claims “removed 18 unused deps” on the deployed repo — the local tree still carries them (divergence confirmed).
- **[RISK][P2]** No `package-lock.json` locally (only `bun.lock`, 222 KB); remote GitHub reportedly has a package-lock.json → non-reproducible npm installs on Railway vs local bun resolution.
- **[FACT][P3]** `store.tsx` (918 lines) bundles 6 components + duplicated client-side copies of server constants (`REGION_LABELS`≡`REGIONS`, `fmt`≈`fmtPrice`, region detection ≡ `regionFromPhone`).

Overall verdict: architecture is sound for current scale; the P1 items are live-mode go-live blockers, everything else is hygiene.

---

## 2. Verification Results (commands I own)

### 2.1 `npx tsc --noEmit`
```
$ cd /home/z/my-project && npx tsc --noEmit; echo $?
TSC_EXIT_CODE=0
```
**[TEST RESULT]** 0 type errors, exit 0. Caveats: `tsconfig.json:13` `noImplicitAny: false` weakens `strict: true`; `ignoreBuildErrors: false` is correctly set in `next.config.ts:34-36`.

### 2.2 `npm run lint` (= `eslint .`)
```
$ npm run lint
✖ 2250 problems (27 errors, 2223 warnings)   → exit code 1
```
**[TEST RESULT]** Rule breakdown (from full output):
- 2222 × `@typescript-eslint/no-unused-expressions` (warning) — ALL from `research/live_capture/chunks/*.js` minified production bundles
- 12 × `no-require-imports` (error) — `scripts/report/*.js`
- 10 × `no-this-alias` (error) — `scripts/report/*.js`
- 5 × `react-hooks/set-state-in-effect` (error) — `src/components/store/store.tsx:497,586,593,793,797`
- 1 × unused eslint-disable directive (warning) — `store.tsx:338`

**[TEST RESULT]** Scoped re-run `npx eslint src/` → **6 problems (5 errors, 1 warning)**, all in `store.tsx` (same 5 set-state-in-effect errors + 1 unused-disable). src/ is otherwise lint-clean.

**[DEFECT][P2]** Root cause of the 2250 noise: `eslint.config.mjs:47` ignores only `node_modules/.next/out/build/next-env.d.ts/examples/skills` — `research/`, `scripts/`, `data/`, `download/` are linted. `npm run lint` therefore fails in CI anywhere and masks real signal.

**[OBSERVATION][P2]** Lint config disarms the safety net (eslint.config.mjs:12-44): `no-explicit-any`, `no-unused-vars`, `no-non-null-assertion`, `ban-ts-comment`, `exhaustive-deps`, `no-console`, `no-undef`, `no-unreachable`, `no-debugger`, `prefer-const`… all OFF. This is why an unused import (`REGIONS` in `checkout/route.ts:3`, never referenced in body) and 77 `any`s pass silently.

---

## 3. Architecture Map

### 3.1 Layers (verified by import tracing)

```
L1 UI (client components)
 ├─ /            → src/app/page.tsx → src/components/store/store.tsx (918 ln, 6 components)
 ├─ /intel       → src/app/intel/page.tsx → 17 × src/components/intelligence/*.tsx + shared.tsx
 └─ shadcn       → src/components/ui/* (42 files, 5,397 ln — only 9 reachable: button,badge,card,input,tabs,progress,collapsible,toast,toaster)
L2 API routes (10 files, 517 ln) — src/app/api/**
    api/route.ts (health) · store/{catalog,checkout,orders/[id],orders/[id]/restock,payments/confirm} · wallet/{,deposit} · admin/{stats,sync}
L3 lib services — engine.ts (292) · prodseller.ts (89) · ratelimit.ts (63) · format.ts (75) · admin-auth.ts (30) · db.ts (12) · utils.ts (6) · data/*.json (420 KB static)
L4 Prisma ORM — schema.prisma, 10 models: Product, Supplier, ChainLink, GeoPrice, Order, Attempt, Wallet, WalletTx, Waitlist, SyncLog
L5 PostgreSQL (Supabase via Railway)  +  External: ProdSeller API (https://prodseller.com/v1, X-API-Key)
```

### 3.2 Dependency direction — **[FACT]** clean, one-way, no cycles
- Routes → lib (db, engine, format, ratelimit, admin-auth, prodseller). engine → db, format, prodseller. prodseller → (nothing local). No lib module imports app/components.
- **[FACT]** No circular imports: `engine.ts` imports `psBalance, psProducts` statically from prodseller (`engine.ts:12`); `psPurchase` via dynamic `await import` (`engine.ts:175`) — redundant (module already loaded) but harmless.
- **[FACT]** UI never touches DB/Prisma: only route handlers import `@/lib/db` (grep verified). `store.tsx` imports only React + 4 ui primitives (`store.tsx:8-12`).
- **[FACT]** Store↔Intelligence separation is complete: zero cross-imports between `components/store` and `components/intelligence` (grep verified). Store = live DB/API data; Intel = static JSON artifacts in `lib/data/` (17 files import `@/lib/data`).

### 3.3 Where business logic lives
- **engine.ts** = service layer: catalog cache (60s TTL, `engine.ts:24-69`), wallet ledger (`:72-91`), JIT router with margin/float guards + sandbox simulation (`:118-223`), ProdSeller sync (`:226-292`). **[OBSERVATION]** Cohesion is moderate: 4 distinct responsibilities in 292 lines; acceptable now, will strain if suppliers multiply.
- **[OBSERVATION][P3]** Order orchestration leaks into routes: checkout (132 ln) contains wallet debit flow + crypto payment instruction construction inline (`checkout/route.ts:55-131`); confirm repeats the post-routing delivered/failed handling (`confirm/route.ts:61-86` ≈ `checkout/route.ts:78-98`). This is the main duplication cluster (see §4.1).
- **[FACT]** Domain constants properly centralized in `format.ts:67-75` (RAILS, DEPOSIT_MIN/MAX, MARGIN_CAP, CASHBACK_RATE, APOLOGY_USD, SAR_PEG) — but `SAR_PEG` and `fmtPrice` are exported and never used (`sarToUsd` hardcodes 3.75 at `format.ts:41`; client re-implements at `store.tsx:191`).

---

## 4. Code Quality Findings

### 4.1 Duplication (API routes + client)
| # | Duplicated block | Locations | Lines |
|---|---|---|---|
| D1 | `SUPPLIER_NAMES` map `{ps:"ProdSeller",sv:"StackVault",…}` | `engine.ts:106-108` vs `orders/[id]/route.ts:23` | 2×3 |
| D2 | Step Arabic labels (`stepAr`) | inline in `engine.ts:145-201` vs `STEP_AR` in `orders/[id]/route.ts:24-31` | 2×7 entries |
| D3 | Chain→CatalogChain mapping lambda | `checkout/route.ts:73-75` ≡ `confirm/route.ts:52-54` | 2×3 |
| D4 | Post-route delivered/failed handling (order update + cashback/refund/apology credits + response) | `checkout/route.ts:78-98` ≈ `confirm/route.ts:61-86` | ~2×25 |
| D5 | JSON body parse + guard + phone validation boilerplate | `checkout/route.ts:12-31`, `confirm/route.ts:13-26`, `deposit/route.ts:8-28` | 3×~15 |
| D6 | Client copies of server constants: `REGION_LABELS`(store.tsx:39-43)≡`REGIONS`(format.ts:2-6); `fmt`(store.tsx:47-49)≈`fmtPrice`(format.ts:31-33); region detection (store.tsx:777-778)≡`regionFromPhone`(format.ts:18-23); RAILS display (store.tsx:174-178) vs RAILS (format.ts:67) | 4 pairs | ~20 |

**[OBSERVATION][P3]** D1–D5 are the strongest case for a `lib/api-helpers.ts` (parse/validate/chain-map/finishOrder). D6 risks drift: `fmt` renders SAR unrounded while `fmtPrice` rounds (store.tsx:48 vs format.ts:32).

### 4.2 Dead code
- **[FACT][P2]** `src/components/ui/`: 42 files / 5,397 lines; only 9 files (510 lines) reachable from app code (grep trace: app-level imports only touch card, badge, input, button, toaster, toast, tabs, progress, collapsible). ~**4,887 lines (90.5%) dead** — incl. `sidebar.tsx` (726 ln), `chart.tsx` (353), `menubar.tsx` (276), `dropdown-menu.tsx` (257).
- **[FACT][P3]** Unused lib exports: `SAR_PEG`, `fmtPrice` (`format.ts:31,75` — zero references), `invalidateCatalog` only used internally (`engine.ts:276`), `REGIONS` imported-but-unused in `checkout/route.ts:3`.
- **[FACT][P3]** Dead config: `tailwind.config.ts` imports `tailwindcss-animate` but Tailwind v4 CSS-first setup (`globals.css` has no `@config`) never reads it. `src/hooks/use-mobile.ts` only used by dead `sidebar.tsx`.
- **[FACT][P3]** `store.tsx:338` `eslint-disable-next-line react-hooks/exhaustive-deps` is redundant (rule globally off) — flagged as unused directive by lint.

### 4.3 Error response shapes — **[FACT]** consistent
All 10 routes return `{ ok: false, error: <Arabic string> }` on failure and `{ ok: true, … }` on success; status codes used coherently (400/401/402/404/405/409/429/500/502). Spot evidence: `catalog:16`, `checkout:19,27,33,42,48,60`, `confirm:20,25,33`, `orders/[id]:20`, `restock:16`, `wallet:14`, `deposit:15,21,26`, `admin-auth.ts:25-29`, `ratelimit.ts:48-57`, `admin/sync:19,23`. **[OBSERVATION]** Only catalog route has a try/catch for DB failure (500); checkout/confirm/wallet would surface unhandled Prisma errors as raw Next 500s — acceptable at this scale, note for consistency.

### 4.4 Magic numbers
- **[FACT][P3]** Named & good: `CATALOG_TTL_MS=60_000` (engine.ts:25), `MARGIN_CAP`, `CASHBACK_RATE`, `APOLOGY_USD`, `DEPOSIT_MIN/MAX` (format.ts:70-74), `MAX_BUCKETS=50_000` (ratelimit.ts:8).
- **[OBSERVATION][P3]** Unnamed: cents marker `1 + Math.floor(Math.random()*98)` (checkout:102); price-change epsilon `0.005` (engine:268); admin token min length `16` (admin-auth:7); discount heuristic `2.5 * price.price` (store.tsx:117); order poll `2500` ms (store.tsx:330/336); SAR peg `3.75` hardcoded client-side (store.tsx:191) and in `sarToUsd` (format.ts:41) despite `SAR_PEG` constant existing; ProdSeller timeouts 20000/25000/30000 (prodseller.ts:22,55,73).

### 4.5 File sizes (top 10 of src/, `wc -l`)
| File | Lines | Note |
|---|---|---|
| components/store/store.tsx | 918 | 6 components in one file (mission's "~1500" = beautified prod bundle `research/live_capture/store_component_beautified.js`, not source) |
| components/ui/sidebar.tsx | 726 | dead |
| intelligence/mec7.tsx | 392 | data-render |
| intelligence/deep-dive.tsx | 392 | data-render |
| ui/chart.tsx | 353 | dead |
| intelligence/mec5.tsx | 345 | data-render |
| lib/engine.ts | 292 | service layer |
| ui/menubar.tsx | 276 | dead |
| intelligence/mec6.tsx | 261 | data-render |
| ui/dropdown-menu.tsx | 257 | dead |

### 4.6 Comments & naming
- **[FACT]** Comments are English, dated, and rationale-bearing in the hardened modules (`engine.ts:1-5,110-117`, `admin-auth.ts:1-3`, `ratelimit.ts:1-3`, `next.config.ts:3-5`) — good fix-provenance discipline. Intelligence components are sparsely commented (data-heavy render code).
- **[FACT]** Naming convention is consistent: English identifiers/API keys, Arabic ONLY in user-facing strings and DB display labels (STATUS_AR/TX_AR), correct `dir="ltr"` isolation for numbers/codes (store.tsx:132,374 etc.). No Arabic identifiers in code. No mixed-language identifiers found.

---

## 5. Type Safety

| Metric | Count | Evidence / worst examples |
|---|---|---|
| `any` usages (`: any`, `as any`, `<any>`) | **77** total in src/ (≈75 outside ui/) | intelligence data-render pattern `const d = data as any` (mec5.tsx:23, mec6.tsx:23, mec7.tsx:28, deep-dive.tsx:12, batch3.tsx:8, channel-matrix.tsx:9, decisions.tsx:22, direct-wave.tsx:8) + map callbacks `(r: any, i: number)` (~60 sites). API/lib: `checkout/route.ts:32` `RAILS.includes(rail as any)`; `prodseller.ts:58-59` `(data as any)?.products` |
| `as <Type>` casts (non-any) | 5 | `prodseller.ts:35` `as T` (generic, legit); `skus.tsx:57,125,136` `as Record<string, unknown>`; `db.ts:3` `globalThis as unknown as {prisma…}` (standard Prisma singleton) |
| `@ts-ignore` / `@ts-expect-error` | **0** | grep verified |
| Non-null `!` assertions | **0** | grep verified |
| tsconfig strictness | `strict: true` BUT `noImplicitAny: false` (tsconfig.json:11-13); `skipLibCheck`, `allowJs: true` | weakens strict mode for implicit-any params |

**[OBSERVATION][P2]** The `any` mass is concentrated in intelligence components consuming untyped JSON (`lib/data/*.json` via `resolveJsonModule`) — a data-typing problem, not laziness in the store core. Store core (engine/prodseller/routes/format) has exactly 3 `any`s, one of which (`checkout:32`) is trivially fixable with a type-guard (`RAILS.includes(rail as Rail)` or `(RAILS as readonly string[]).includes(rail)`).

---

## 6. Dependency Analysis

`package.json`: **48 runtime deps + 9 devDeps** (mec-store@0.2.1). Versions: `next ^16.3.6` (installed 16.3.6; eslint-config-next 16.1.3 — **[OBSERVATION][P3]** minor mismatch), `react ^19.0.0` (deduped 19.2.3), `prisma`/`@prisma/client ^6.11.1`, `typescript ^5`, Node v24.21.0, npm 11.19.0, bun 1.3.14.

### 6.1 Reachability test (grep every dep in src/, then trace ui-component graph from app entries)
Actually imported by app code (13 runtime): `next`, `react`, `react-dom` (peer), `@prisma/client`, `prisma` (CLI — postinstall `prisma generate`, package.json:14), `class-variance-authority`, `clsx`, `tailwind-merge` (via ui/button, ui/badge, lib/utils), `lucide-react` (via reachable toast.tsx), and 5 radix: `react-slot` (button), `react-tabs`, `react-progress`, `react-collapsible`, `react-toast` (toast→toaster→layout.tsx).

**[FACT][P2] UNUSED runtime dependencies (35 of 48)** — zero imports reachable from any app entry (evidence: per-dep grep + ui import-graph trace):
1–22. Radix: `react-accordion`, `react-alert-dialog`, `react-aspect-ratio`, `react-avatar`, `react-checkbox`, `react-context-menu`, `react-dialog`, `react-dropdown-menu`, `react-hover-card`, `react-label`, `react-menubar`, `react-navigation-menu`, `react-popover`, `react-radio-group`, `react-scroll-area`, `react-select`, `react-separator`, `react-slider`, `react-switch`, `react-toggle`, `react-toggle-group`, `react-tooltip`
23. `cmdk` (ui/command — dead) · 24. `embla-carousel-react` (ui/carousel — dead) · 25. `input-otp` (dead) · 26. `react-day-picker` (ui/calendar — dead) · 27. `react-hook-form` (ui/form — dead) · 28. `react-resizable-panels` (ui/resizable — dead) · 29. `recharts` (ui/chart — dead) · 30. `vaul` (ui/drawer — dead) · 31. `next-themes` (ui/sonner — dead) · 32. `sonner` (ui/sonner — dead; toaster uses radix toast, not sonner) · 33. `tailwindcss-animate` (only imported by unreferenced tailwind.config.ts under Tailwind v4 CSS-first) · 34. `sharp` (0 src imports; no `next/image` usage anywhere — only needed if image optimization is enabled) · 35. (borderline) `react-day-picker` already listed; all remaining accounted.

Risky/heavy flags:
- **[RISK][P3]** `recharts` (~500 KB min) — heavy, currently dead; keep only if intel charts planned.
- **[OBSERVATION]** `next 16.3.6` is recent and correct per worklog RCE-patch rationale; `eslint-config-next 16.1.3` lags `next 16.3.6`.

### 6.2 Lockfile / reproducibility
- **[FACT][P2]** Local repo has **no `package-lock.json`** and no yarn/pnpm lock; only `bun.lock` (222,005 bytes, `ls` verified). Build script uses npm/Node (`package.json:8` `next build`…, `postinstall: prisma generate`), Railway start = `node .next/standalone/server.js`. GitHub remote reportedly carries a `package-lock.json` → **local (bun) vs CI (npm) vs remote (npm lock) resolution divergence**; fresh `npm ci` on the remote lock may install a different tree than local `bun install`. Reproducibility risk until one package manager + one committed lockfile is enforced.

---

## 7. Refactoring Plan (incremental, no rewrites)

| ID | Problem (evidence) | Proposed change | Risk | Effort |
|---|---|---|---|---|
| R1 | **[DEFECT][P1] Live purchase sends supplier code as product_id** — `engine.ts:176` `psPurchase(String(link.supplier))`; schema field `ChainLink.externalId` exists unused | Add `externalId` to `CatalogChain` (engine.ts:17) + populate in mapping (engine.ts:52, checkout:74, confirm:53); pass it to `psPurchase`; reject live purchase when `externalId` null | Low (additive); MUST be verified against ProdSeller order docs before go-live | **M** |
| R2 | **[DEFECT/RISK][P1] Confirm endpoint mode-blind + unverified txid** — confirm/route.ts:12-59 no `STORE_MODE` check; UI sandbox button always rendered (store.tsx:244-248, 386-395) | Gate: in live mode require server-side payment verification (webhook signature or on-chain tx check) before status→routing; hide simulate button when `catalog.mode === "live"` | Medium (touches money path) — go-live blocker | **M** |
| R3 | **[RISK][P2] Non-transactional wallet debit** — checkout:56-70 balance-read → order-create → credit, no tx/idempotency; same in confirm | Wrap debit+order+route in `prisma.$transaction` (or add conditional ledger write + unique constraint on `ref`); add idempotency key per publicId | Medium; test with concurrent checkouts | **M** |
| R4 | **[DEFECT][P2] `npm run lint` fails on research artifacts** — eslint.config.mjs:47 ignores | Add `research/**`, `scripts/**`, `data/**`, `download/**`, `notion_raw/**`, `tool-results/**`, `*.js` chunks to ignores → lint reflects src only | None | **S** |
| R5 | **[FACT][P2] 35 unused deps + ~4,887 dead ui lines** (§6.1, §4.2) | Delete unused ui components + prune package.json deps (keep sharp only when enabling next/image); aligns local tree with the hardened deployed tree per worklog 18-19 | Low (verify build after prune) | **S-M** |
| R6 | **[RISK][P2] No npm lockfile / bun vs npm divergence** (§6.2) | Commit a single authoritative lockfile matching Railway's builder (npm `package-lock.json`); optionally drop bun.lock | Low | **S** |
| R7 | **[OBSERVATION][P3] Route duplication D1–D5** (§4.1) | Create `lib/api-helpers.ts`: `parseJson(req)`, `requirePhone(body)`, `toCatalogChain(links)`, `finishOrder(orderId, result)` (shared delivered/failed handling), move `SUPPLIER_NAMES`/`STEP_AR` next to engine exports | Low — pure extraction, behavior-identical | **M** |
| R8 | **[OBSERVATION][P3] store.tsx 918 ln, 6 components + client/server constant drift D6** | Split into `store/{StoreGrid,CheckoutPanel,OrderView,WalletPanel,OpsPanel}.tsx` + `lib/constants.client.ts` (or import type-only from format.ts) to dedupe REGION_LABELS/fmt/region detection | Low-Medium (pure moves; watch the 5 set-state-in-effect errors → convert localStorage loads to lazy `useState` initializers) | **M** |
| R9 | **[OBSERVATION][P2] Quality guardrails off** — eslint.config.mjs:12-44, tsconfig `noImplicitAny:false` | Incrementally re-enable: `no-unused-vars` (warn), `@typescript-eslint/no-explicit-any` (warn), `react-hooks/exhaustive-deps` (warn), then `noImplicitAny:true`; fix fallout (~77 any + 1 unused import + 5 hook errors) | Medium (churn), high value | **M** |
| R10 | **[OBSERVATION][P3] Magic numbers** (§4.4) | Name constants: `CENTS_MARKER_MIN/MAX`, `PRICE_EPSILON`, `ADMIN_TOKEN_MIN_LEN`, `ORDER_POLL_MS`, reuse `SAR_PEG` in `sarToUsd` + client | None | **S** |

**Top-5 priority order: R1 → R2 → R3 → R4 → R5** (money-path correctness first, then hygiene en-masse).

---

## 8. Limitations

- Static analysis only: no runtime testing, no HTTP endpoint calls (owned by other agents), no `next build` (per rules) — bundle-size claims for `lib/data/*.json` (420 KB static imports into the `/intel` client bundle) are inferred from import graph, not measured.
- "Unused dependency" = no import reachable from `src/` app entries; transitively-required packages (`react-dom`, `prisma` CLI, `@prisma/client`) were excluded from the unused list despite 0 direct imports. `sharp` flagged removable only because `next/image` is unused.
- Remote GitHub tree (with its package-lock.json and pruned deps) could not be inspected (token lost per worklog 18-19); divergence statements rely on the mission brief + local evidence.
- The 5 `react-hooks/set-state-in-effect` errors were not behavior-tested (they are lint-level findings; cascading-render impact is a React 19/compiler recommendation, not a measured perf defect).
- Worklog Task 18-19 states the deployed tree had 18 deps removed; local `package.json` still lists 48 — assumed to be reconstruction divergence, not audit error (grep evidence in §6.1).
