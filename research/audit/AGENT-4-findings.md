# AUDIT-4 — Database & Supabase Audit Findings (READ-ONLY)

**Task ID:** AUDIT-4 · **Date:** 2026-09-28 · **Scope:** production Supabase PostgreSQL (aws-1-eu-west-3) backing MEC store on Railway
**Method guarantee:** every executed statement was `SELECT` / `EXPLAIN` (planning only, never `ANALYZE`) / catalog read. No writes, no locks, no DDL. Credentials fetched via Railway variables API and never printed.

---

## 1. Executive Summary

**Overall verdict: HEALTHY.** All 10 expected tables exist with **zero column drift** vs `prisma/schema.prisma`; all **7 hot-path indexes from task 18-19 verified present**; **RLS enabled on all 10 tables with 0 policies (deny-all)**; **anon + authenticated have ZERO privileges** (verified 3 independent ways); wallet ledger reconciles **to the cent** ($114.55 derived = ledger math); **0 orphaned FK rows**; **100% geo-price coverage** (SA/YE/WW for all 37 products); every delivered order (8/8) carries a SANDBOX-marked receipt, consistent with live `STORE_MODE=sandbox`.

**Top risks found (all process-level, no data defects):**
1. **[RISK][P2]** `ALTER DEFAULT PRIVILEGES` was NOT revoked — any **future** table in `public` auto-grants full DML to `anon`/`authenticated` (and would ship without RLS → re-exposed via PostgREST).
2. **[RISK][P2]** No migration history (`prisma/migrations/` absent, no `_prisma_migrations` table) + `db:push` script runs `prisma db push --accept-data-loss` — a divergent schema edit could silently destroy production data.
3. **[RISK][P2]** No app-level backup capability: `pg_dump` not installed locally, no backup scripts in repo. Recovery depends entirely on Supabase platform backups (not verifiable from here, though WAL archiving is demonstrably active).
4. **[DRIFT][P3]** 5 indexes declared in `schema.prisma` are absent from the live DB (Product family/active, ChainLink supplierId/active, Attempt supplierCode+status) — harmless at current scale, but schema-vs-DB drift is real.

---

## 2. Connection & Method

- Credentials obtained from Railway GraphQL variables API (project `a574c5d0-…`, env `89138798-…`, service `79f9401c-…`), `RAILWAY_TOKEN` loaded from `.env` — values masked/never emitted.
- Connection: `pg8000.native`, SSL, user `postgres`, **PostgreSQL 17.6** (x86_64, GCC 15.2). Connection path goes through **Supavisor/pgbouncer** (`pgbouncer.get_auth` is the #1 call in `pg_stat_statements`, 2440 calls).
- Scripts (new, allowed): `scripts/audit/agent4_db_audit.py` (main), `scripts/audit/agent4_supplemental.py`. Both enforce a read-only guard: statement must start with `SELECT|EXPLAIN|WITH`, single-statement only, `EXPLAIN` without `ANALYZE`.
- Raw evidence: `research/audit/agent4_db_audit.json` (full result dump) + console transcripts in this report.

---

## 3. Schema Verification

### 3.1 Tables, rows, sizes (FACT)

| Table | Rows | Total size | Prisma cols vs live | PK | FKs | Unique constraints |
|---|---|---|---|---|---|---|
| Product | 37 | 48 kB | 10/10 **MATCH** | id | — | slug |
| Supplier | 6 | 48 kB | 10/10 **MATCH** | id | — | code |
| ChainLink | 57 | 96 kB | 10/10 **MATCH** | id | productId→Product, supplierId→Supplier | (productId,supplierId) |
| GeoPrice | 111 | 96 kB | 6/6 **MATCH** | id | productId→Product | (productId,region) |
| Order | 35 | 144 kB | 21/21 **MATCH** | id | productId→Product | publicId, paymentRef |
| Attempt | 14 | 48 kB | 9/9 **MATCH** | id | orderId→Order | — |
| Wallet | 14 | 48 kB | 3/3 **MATCH** | id | — | phone |
| WalletTx | 27 | 64 kB | 7/7 **MATCH** | id | walletId→Wallet | (walletId,type,ref) |
| Waitlist | 1 | 48 kB | 4/4 **MATCH** | id | productId→Product | (productId,phone) |
| SyncLog | 2 | 32 kB | 10/10 **MATCH** | id | — | — |

**[FACT]** All 10 planned tables present; **0 missing columns, 0 extra columns** — no drift between `prisma/schema.prisma` and live DB (column-level). Total data footprint < 1 MB.

### 3.2 Indexes (FACT)

27 indexes total = 10 PK + 9 unique + 8 secondary. **Hot-path set from worklog 18-19 — 7/7 VERIFIED:**

| Hot-path index | Status |
|---|---|
| `Order_phone_idx` (phone) | ✅ OK |
| `Order_createdAt_idx` (createdAt **DESC**) | ✅ OK |
| `Order_status_idx` (status) — the 7th | ✅ OK |
| `WalletTx_walletId_idx` | ✅ OK |
| `Attempt_orderId_idx` | ✅ OK |
| `ChainLink_productId_idx` | ✅ OK |
| `GeoPrice_productId_idx` | ✅ OK |

**[DRIFT][P3]** Declared in `schema.prisma` but **absent live** (applied via `db push` never re-run after they were added to the file): `Product_family_idx`, `Product_active_idx`, `ChainLink_supplierId_idx`, `ChainLink_active_idx`, `Attempt_supplierCode_status_idx`. Planner does not need them at 37-product scale (see §6). A future `db push` would create them (benign).

---

## 4. RLS & Permissions (critical)

**[FACT] RLS per table (all 10):** `relrowsecurity = ON`, `relforcerowsecurity = OFF`, **0 policies** → deny-all posture for any non-owner role. RLS-off for the app itself is expected (app connects as `postgres` = table owner, bypasses RLS).

**[FACT] PostgREST roles exist:** `anon`, `authenticated`, `service_role`, `authenticator` (non-super, no-login except authenticator), plus `supabase_admin` (superuser) and `supabase_read_only_user` — full Supabase platform present (schemas: `auth`, `storage`, `realtime`, `vault`, `graphql`, `extensions`, `pgbouncer`).

**[FACT] Grant verification (3 independent methods, all agree):**

| Role | `information_schema.role_table_grants` | raw `relacl` (aclexplode) | `has_table_privilege` matrix |
|---|---|---|---|
| `anon` | **0 grants** | **0 entries** | all false (10 tables × 4 privs) |
| `authenticated` | **0 grants** | **0 entries** | all false |
| `service_role` | 70 grants (7 privs × 10 tables) | 80 entries | full CRUD |

→ **Task 18-19 claim "REVOKE ALL from anon/authenticated (PostgREST locked)" is VERIFIED at DB level.** [OBSERVATION][P3] `service_role` retains full DML — Supabase default; exposure only if the service key leaks (not used by the app).

**[DEFECT→RISK][P2] Default privileges NOT revoked.** `pg_default_acl` shows (grantors `postgres` **and** `supabase_admin`): future relations in `public` → `anon=arwdDxtm`, `authenticated=arwdDxtm`, `service_role=arwdDxtm`. Combined with RLS not being auto-enabled on new tables, **any table added later would be fully readable/writable through the public PostgREST endpoint**. The 18-19 hardening fixed existing tables only.
**[RECOMMENDATION][P2]** (when a write window is authorized): `ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;` (repeat for `supabase_admin`), or disable PostgREST/Data API in the Supabase dashboard.

---

## 5. Data Integrity Results

### 5a. Wallet ledger (exact reconciliation — TEST RESULT: PASS)
- **[FACT]** `Wallet` has **no stored balance column** (only id/phone/createdAt) — balance is derived by `SUM(WalletTx)` ⇒ stored-vs-derived drift is **impossible by construction** (matches task 18-19).
- Ledger math: deposits **$115.00** + refunds **$2.07** + cashback **$0.08** + apology **$3.00** − purchases **$5.60** = **$114.55** = Σ per-wallet derived balances = total customer liability. **Exact match, 0 discrepancies.**
- 14 wallets (phones masked, e.g. `+96651***01`: $23.94/3 txs); top balance $49.32; 6 wallets empty (0 txs).
- WalletTx types: deposit 6 / purchase 7 / refund 3 / cashback 8 / apology 3 = 27 rows. Idempotency unique key `(walletId,type,ref)` present.

### 5b. Orphans (TEST RESULT: PASS — 0 everywhere)
`orders→product 0 · attempts→order 0 · chainlinks→product 0 · chainlinks→supplier 0 · geoprices→product 0 · wallettx→wallet 0 · waitlist→product 0` — FKs enforced, referential integrity intact.

### 5c. GeoPrice coverage (TEST RESULT: PASS)
37/37 products have **all three** regions: SA(SAR)=37, YE(USD)=37, WW(USD)=37 → 111 rows. **0 products missing +966 or +967 pricing; 0 unsellable products.**

### 5d–5f. Products / duplicates / sellability
- Duplicate slugs: **0** (unique constraint active).
- Products: **37 active, 0 inactive**; **0** active-without-active-chain (JIT-dead); **0** active-without-prices.

### 5g–5h. Orders & sandbox (FACT)
- Status distribution: `pending_payment=24`, `delivered=8`, `failed=3` (35 total). Rails: `trc20=28`, `wallet=7`.
- **No `mode` column on Order.** Sandbox provenance is only inferable from payload prefix. All 8 delivered orders have `deliveredPayload LIKE 'SANDBOX%'` → **8/8 sandbox receipts, 0 real purchases** — consistent with Railway env `STORE_MODE=sandbox` (verified live this audit).
- GMV $34.11 (sandbox), recorded COGS $3.50, cashback $0.08, apology $3.00.
- **[OBSERVATION][P3]** 24 `pending_payment` orders are stale test/abuse residue (incl. 12 rate-limit test checkouts) — no TTL/cleanup job.
- **[OBSERVATION][P3]** `Attempt.supplierCode` stores **display names** ("ProdSeller", "sv") not supplier codes ("ps") — engine.ts maps via `SUPPLIER_NAMES` before persisting; breaks clean grouping against `Supplier.code` in analytics.

### 5i. Suppliers (FACT — non-secret fields)
`ps`=ProdSeller [api, **active**] · `sv`=StackVault [semi, **active**] · `turgame`=Turgame [semi, **active**] · `ggsel`=GGSel (VPN) [semi, inactive] · `kinguin`=Kinguin [inactive; name garbled `"(W3) anual]"` — **[OBSERVATION][P3] data-quality**] · `reloadly`=Reloadly (W2) [api, inactive]. All score 0.5, failCount 0, no open circuits.

### 5j. SyncLog recency (FACT)
2 sync runs, both `ps ok=true`; **last sync 2026-09-28 10:53:54Z** (seen=25, matched=25, changed=0, **balanceUsd=0.00**). **[OBSERVATION][P3]** ProdSeller float is $0 — in live mode the float guard would (correctly) skip all PS purchases; irrelevant while sandbox.

---

## 6. Query Efficiency

**EXPLAIN (planning-only) on real app patterns** (from `src/lib/engine.ts` + API routes):

| Pattern (source) | Plan | Verdict |
|---|---|---|
| Catalog join: products+prices+chains+suppliers (`getCatalog`) | Seq scans (37/57/111 rows) + **Memoize** on `Supplier_pkey` | Optimal at scale-of-data; total cost ~20 units |
| Recent 12 orders (`admin/stats`) | **Index Scan `Order_createdAt_idx`** | ✅ hot-path index actively used |
| Chains by product + active (`checkout`, `payments/confirm`) | **Index Scan `ChainLink_productId_idx`** + filter | ✅ |
| Wallet SUM(amount) by walletId (`walletBalance`) | Seq scan (27 rows) | Fine; planner correctly prefers scan; index exists for scale |
| Attempts by order (`orders/[id]`) | Seq scan (14 rows) | Fine; index exists for scale |
| WalletTx history (walletId, createdAt DESC, take 50) | Seq scan + sort | Fine now; **[RECOMMENDATION][P3]** composite `WalletTx(walletId, createdAt DESC)` when wallets grow |

**[FACT]** `pg_stat_user_tables`: heavy real index utilization — GeoPrice 447 idx-scans vs 50 seq, ChainLink 271/103, Wallet 253/6, Supplier 178/15. `pg_stat_statements` shows **no slow application queries**; top statements are platform (pgbouncer auth 607ms total) and seed inserts (GeoPrice ×403).
**[RECOMMENDATION][P3]** At >1k products/orders: add the 5 missing declared indexes (esp. `ChainLink(supplierId)` for the admin sync join `supplier.code='ps'`) and the 3 composites noted above. **No missing index is a defect today** (all tables < 150 rows).

---

## 7. Migration Assessment

- **[FACT]** `prisma/` contains **only** `schema.prisma` — **no `migrations/` directory**; no `_prisma_migrations` table in DB (only Supabase's own `auth.schema_migrations` / `realtime.schema_migrations` exist). Schema lifecycle = `prisma db push`.
- **[RISK][P2]** `package.json` → `"db:push": "prisma db push --accept-data-loss"`: if `schema.prisma` ever diverges destructively (rename/delete column), push will execute the drop against production **without prompt**. `db:migrate` (`prisma migrate dev`) exists but is unused and would currently collide with the push-managed state.
- **[RECOMMENDATION][P2]** Establish a baseline migration (no changes now): `prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script` → save as `migrations/0_init/migration.sql`, `prisma migrate resolve --applied "0_init"` (after creating `_prisma_migrations`), then switch deploys to `prisma migrate deploy` and **remove `--accept-data-loss`**. Until then, treat `schema.prisma` + this audit's index inventory as the reconciliation baseline (5 declared indexes missing live — see §3.2).

---

## 8. Backup / Recovery Evidence

- **[FACT]** `pg_dump` **not installed** in this workspace; no backup scripts anywhere in the repo; no scheduled export job evidence.
- **[FACT]** Platform-side: **WAL archiving ACTIVE** — `pg_stat_archiver`: archived_count=36, failed=0, last WAL `000000010000000000000025` archived 2026-09-28 11:54Z; `wal_level=logical`; no replication slots readable (empty). Supabase automated backups/PITR are plan-dependent and **not verifiable from DB access** (dashboard not accessible — consistent with task 18-19 note).
- **[ASSUMPTION][P3]** Supabase performs automated backups per plan (daily on Pro; 7-day PITR) — unverified.
- **[RECOMMENDATION][P2]** Add an app-level backup: nightly `pg_dump` (or SQL export via the same pg8000 path) to object storage. Entire DB < 1 MB — trivial cost, closes the single-vendor recovery gap.

---

## 9. Limitations

1. No Supabase dashboard access → cannot confirm backup schedule/retention, PostgREST/Data-API toggle state, or plan-level PITR. DB-level grant revocation is the verified lock.
2. `pg_stat_*` counters are since last stats reset — scan ratios are relative evidence, not lifetime absolutes.
3. EXPLAIN was planning-only (per mission rules) — no execution timings; conclusions combine plans with `pg_stat_statements` runtime data.
4. Data volumes are tiny (< 150 rows/table) — index adequacy findings are forward-looking by necessity.
5. Phone numbers PII-masked in all outputs; connection strings/credentials never emitted (verified by script design).
6. `service_role` key custody and Railway secret rotation are outside DB-audit scope.

**Evidence artifacts:** `research/audit/agent4_db_audit.json` · `scripts/audit/agent4_db_audit.py` · `scripts/audit/agent4_supplemental.py`
