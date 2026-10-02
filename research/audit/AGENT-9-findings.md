# AUDIT-9 — DevOps, GitHub & Deployment Audit (MEC Store)

Agent: AUDIT-9 (DevOps / GitHub / Deployment)
Date: 2026-09-28 (session after MEC-18/19 hardening)
Scope: READ-ONLY. No pushes, no deploys, no config changes, no source modifications.
Evidence: live GitHub REST API, Railway GraphQL v2 (read queries + introspection), local git, live HTTP probes of production URL. All tokens masked; no secret values appear in this file.

---

## 1. Executive Summary

| Area | Verdict |
|---|---|
| Local git | `main` @ `0e08876` (MEC-18/19 hardening), 2,216 tracked files, **no remotes**, 2 modified + several untracked files. Authoritative tree for production. |
| GitHub remote | `ahmedabhusa6-hash/mec-store` (private), HEAD `cdab8bc`, **8 commits, 167 tree entries (136 blobs)**, last push 2026-09-28T01:59:00Z — **STALE, pre-hardening** (Next `^16.1.1`, no admin gate, no rate limit, no security headers). |
| Remote hygiene | **CLEAN**: no `.env`, no `notion_raw/`, no `research/`, no `db/`, no logs on remote. `.env.example` is a placeholder template only. |
| Local hygiene | **P0 DEFECT**: `.env` (with GITHUB_TOKEN, RAILWAY_TOKEN, ADMIN_TOKEN, PRODSELLER_API_KEY, DB URLs) is **tracked and was re-committed in `0e08876`** → secrets live in local git history. Must never be pushed as-is (sync plan uses isolated worktree with whitelist). `db/custom.db` also tracked (P1). |
| Divergence | **22 remote-only blobs** (old modular `engine/`, `store-*` split, `mec10`, `[publicId]` routes, `scripts/seed.mjs`, stale `package-lock.json`…) vs **local reconstruction** (monolith `engine.ts`, `store.tsx`, `ratelimit.ts`, `admin-auth.ts`, …). All 5 key-file hashes DIFFER. Histories are unrelated → sync requires force-push of a clean single commit. |
| CI | 1 workflow `deploy.yml` (ACTIVE). **2 defects**: corrupted trigger `branches: ain]` (yet push of `cdab8bc` still triggered a run — evidence run `36368040983`) and `tar` writing into its own input dir → all 3 push runs FAILED at "Build tarball", Upload always SKIPPED → **CI has never deployed anything** (accidental safety net). |
| Railway | Service `mec-store`, builder RAILPACK, 1 replica (null→default), source shows repo label `ahmedabhusa6-hash/mec-store` (auto-deploy state not verifiable with project token — risk flagged). Latest deployment `f2c88f49` **SUCCESS** (2026-09-28T11:21:50Z, `railway up` CLI). 1 service domain, 0 custom domains. 18 variables (names incl. `ADMIN_TOKEN`, `STORE_MODE`) — **no new vars needed for release**. |
| Production health | `GET /` → 200 (0.25 s), **all 6 security headers present**, `/api` → 200, `/api/admin/stats` without token → **401** (admin gate live). |
| Rollback | Mutations confirmed in schema: `deploymentRedeploy(id, usePreviousImageTag)`, `deploymentRollback(id)`, `serviceInstanceRedeploy(environmentId, serviceId)`. Rollback target = `f2c88f49` (cached image digest). |

**Bottom line:** remote is a stale pre-hardening mirror; local is authoritative but contains tracked secrets — sync MUST use the isolated-worktree whitelist method (below) with a force-push replacing the 8 throwaway remote commits. CI is broken-but-harmless; fix or disable it during push. Release path `railway up` is proven (f2c88f49); no env changes required.

---

## 2. Local Git State

- **FACT** Branch `main`, HEAD `0e08876` "MEC-18/19: production audit + hardening deploy…". `git remote -v` → **empty** (no remotes).
- **FACT** 2,216 tracked files. Top-level breakdown:

| Count | Dir/File | Notes |
|---|---|---|
| 1124 | `notion_raw/` | PRIVATE research data — **must NEVER be pushed** |
| 678 | `research/` | audit/research payloads — never push |
| 129 | `scripts/` | local tooling (incl. audit scripts) — never push |
| 110 | `src/` | production app code — whitelist |
| 96 | `data/` | research data — never push |
| 21 | `download/` | deliverables — never push |
| 18 | `tool-results/` | agent artifacts — never push |
| 9 | `.zscripts/`, 3 `tests/`, 2 `examples/`, 1 `mini-services/` | private tooling — never push |
| 2 | `public/` (`logo.svg`, `robots.txt`) | whitelist |
| 1 each | `prisma/schema.prisma`, `package.json`, `next.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.mjs`, `eslint.config.mjs`, `components.json`, `bun.lock`, `.gitignore`, `.railwayignore`, `Caddyfile`, `worklog.md` | configs — whitelist (except Caddyfile/worklog) |
| 1 | **`.env`** | **P0 — secrets tracked** |
| 1 | **`db/custom.db`** | **P1 — SQLite DB tracked** |

- **OBSERVATION** Uncommitted: `.env` (modified — token refresh, expected), `src/app/api/store/catalog/route.ts` (+1 line: `console.error("[catalog] failed:", e)` — trivial observability fix, **not in HEAD**, would be excluded by worktree sync; recommend committing it to main before sync). Untracked: `scripts/audit_env_setup.py`, `scripts/db_probe.mjs`, 5 `tool-results/*` — harmless (untracked).
- **DEFECT P0** `.env` tracked AND modified in `0e08876` (`git log -- .env` shows blobs at `0e08876`, `4fac65b`, `4c3530d`, `60e40f6`, `a5ab8d0`) → GITHUB_TOKEN / RAILWAY_TOKEN / ADMIN_TOKEN / PRODSELLER_API_KEY / DATABASE_URL / DIRECT_DATABASE_URL exist in local history blobs. Local repo must never be pushed directly.
- **DEFECT P1** `db/custom.db` tracked (customer/order data risk if leaked).
- **OBSERVATION** `.gitignore` content is reasonable (`.env*`, `*.log`, `node_modules`, `/.next`, `local-*`, `.claude`, `/skills/`) but cannot untrack already-committed files.
- **OBSERVATION** 8 tracked paths under a quoted `"scripts…` prefix (unicode/space names) — hygiene noise only.
- **OBSERVATION** `.railwayignore` is high quality: root-anchored (`/.env`, `/research`, `/notion_raw`, `/data`, `/download`, `/scripts`, `/tool-results`, `/db`, `/worklog.md`, `/Caddyfile`, `/examples`, `/skills`, `/tests`, `/.git`, `/node_modules`, `/.next`) — matches worklog claim (285 KB upload vs 23 MB tree).
- **TEST RESULT** Secret spot-check of whitelist candidates (`src/`, `prisma/`, root configs, `public/`): regex scan for `psk_…`, `ghp_…`, `sk-…`, `[REDACTED-DB-URL]//`, `Bearer …`, hardcoded `ADMIN_TOKEN=` → **0 hits — clean**.

---

## 3. GitHub Remote State (read-only API)

- **FACT** Repo `ahmedabhusa6-hash/mec-store`: private, default branch `main`, pushed_at `2026-09-28T01:59:00Z`, size 490 KB.
- **FACT** HEAD `cdab8bc5519…` (2026-09-28T01:58:58Z, "workflow: رفع مباشر عبر REST… + إزالة التشخيص"). 8 commits total, all 2026-09-27/28 (initial `012d9e18` "MEC Store W1").
- **FACT** Tree `main?recursive=1`: 167 entries = 136 blobs + 31 dirs, not truncated. Top-level: `src` 118, `public` 2, `scripts` 2, plus 14 root files (`.env.example`, `.github/workflows/deploy.yml`, `.gitignore`, `Caddyfile`, `README.md`, `components.json`, `eslint.config.mjs`, `next.config.ts`, `package-lock.json`, `package.json`, `postcss.config.mjs`, `prisma/schema.prisma`, `tailwind.config.ts`, `tsconfig.json`).
- **FACT (sensitive check)** Remote contains **NO** `.env`, **NO** `notion_raw/`, **NO** `research/`, **NO** `db/*.db`, **NO** logs/tokens. `.env.example` = placeholders only (`psk_ضع_مفتاحك…`). `README.md` scanned: only the words "postgres/postgresql" (stack table) — no secrets.
- **FACT** Remote `package.json`: `next ^16.1.1` (pre-hardening, 2 known critical RCEs), build script runs `node scripts/seed.mjs`; local: `next ^16.3.6`, no seed step, `postinstall: prisma generate`. Remote `package-lock.json` (136-blob set) is **stale vs local `package.json`** — if anything ever runs `npm ci` on remote, it installs the vulnerable Next 16.1.1.

### 3.1 Key-file hash comparison (remote blob sha vs `git hash-object` local)

| File | Remote blob | Local blob | Verdict |
|---|---|---|---|
| `package.json` | `27f48e8bba27…` | `44f2ffba4b86…` | **DIFF** (16.1.1→16.3.6, deps 67→48, scripts changed) |
| `next.config.ts` | `0bd2f1124a09…` | `05348672401f…` | **DIFF** (hardening added 6 security headers) |
| `prisma/schema.prisma` | `75cd3912d9ae…` | `c3152c50e74f…` | **DIFF** |
| `src/lib/engine.ts` | **ABSENT** | `b0a897748e53…` | **DIFF** (local monolith replaces remote `src/lib/engine/{circuit,ledger,pricing,prodseller,router}.ts`) |
| `src/app/page.tsx` | `0af3bf77a938…` | `6773e52d81be…` | **DIFF** |

**Conclusion:** remote = pre-hardening tree in every audited dimension. **The whole app surface must be replaced**, not merged.

### 3.2 File-set divergence (remote-only vs local-only)

Remote-only (22 blobs) — all candidates for deletion in sync:
`src/lib/engine/{circuit,ledger,pricing,prodseller,router}.ts`, `src/components/store/{store-admin,store-catalog,store-checkout,store-order,store-types,store-wallet}.tsx`, `src/components/intelligence/mec10.tsx`, `src/lib/data/{mec10,mec8}.json`, `src/app/api/store/orders/[publicId]/{route,restock/route}.ts`, `scripts/seed.mjs`, `scripts/data/ps-products-raw.json`, `package-lock.json`, `Caddyfile`, + housekeeping to keep (updated): `.env.example`, `.github/workflows/deploy.yml`, `README.md`.

Local-only (in whitelist, new to remote): `src/lib/{ratelimit,admin-auth,format,prodseller}.ts`, `src/app/not-found.tsx`, `src/app/api/admin/{stats,sync}/route.ts` (gated versions), `src/app/api/wallet/**`, `src/app/api/store/orders/[id]/**`, `src/app/intel/{page,layout}.tsx`, `src/components/store/store.tsx`, `src/components/intelligence/mec8.tsx`, `.railwayignore`.

- **TEST RESULT** No `src/` file references `lib/engine/`, `scripts/seed`, or `ps-products-raw` → local tree is self-consistent (matches successful build of deployment `f2c88f49`).

---

## 4. CI Findings (`.github/workflows/deploy.yml`)

- **FACT** One workflow, state **active** (id 368697416). Triggers: `workflow_dispatch` + `push` with **corrupted branch filter `branches: ain]`** (verified byte-level via raw fetch; intended `main`).
- **FACT** Pipeline: checkout → `tar czf deploy.tar.gz … .` (in-repo) → `POST https://backboard.railway.app/project/{id}/environment/{id}/up?serviceId=…` with GitHub secret `RAILWAY_TOKEN` (secret name verified; value never read).
- **DEFECT P1** Trigger corruption — yet push of `cdab8bc` **did** trigger run `36368040983` (event=push, branch=main, head_sha=cdab8bc, created 01:59:02Z, 4 s after push). ⇒ **pushes to main CAN fire this workflow.**
- **DEFECT P1** `tar` writes `deploy.tar.gz` into `.` while archiving `.` → `tar: .: file changed as we read it` → **"Build tarball" step failed in all 3 push runs; "Upload to Railway" always SKIPPED** ⇒ CI has never deployed. This is a deterministic accident, not a safeguard.
- **FACT** 4 runs total: 3 × "Deploy to Railway" failure (push, 01:54/01:56/01:59Z) + 1 × "Diagnose Railway CLI" success (dispatch, 01:56Z — diagnose workflow since removed from tree).
- **RISK P2** The REST upload endpoint in CI (`backboard.railway.app`) + repo secret `RAILWAY_TOKEN`: if the workflow is ever fixed, **every push to main auto-deploys to production**. For the planned sync push this must be pre-empted (disable workflow or fix it consciously in the same commit).
- **RECOMMENDATION** In the sync commit either (a) ship a FIXED workflow (correct `branches: [main]`, tarball to `$RUNNER_TEMP` + `tar -C`, then upload), or (b) keep it disabled until a controlled CI release policy exists. Default plan: **disable before push, re-enable with fix after verification.**

---

## 5. Railway State (GraphQL v2, read-only)

- **FACT** Project `a574c5d0-f136-446f-b8c9-2ceba79e4214` "mec-store", single environment `production` (`89138798-…`, not ephemeral).
- **FACT** Service `79f9401c-3598-4cbe-a5fe-d50c13191820` "mec-store"; instance `39babcef-…`: builder **RAILPACK**, `numReplicas: null` (⇒ 1), `rootDirectory/buildCommand/startCommand: null` (package.json-driven), `watchPatterns: []`, `isUpdatable: false`, `sleepApplication: false`, `region: null`, `healthcheckPath: null`.
- **FACT** `source: {image: null, repo: "ahmedabhusa6-hash/mec-store"}` — repo label present. Deployments on record were all made by CLI upload (`meta.cliCaller: "agent_unknown:proc:caddy"`, `reason: deploy`).
- **RISK P2 (unverified)** Railway↔GitHub auto-deploy cannot be confirmed/denied with a project token (no `Project.githubIntegration` field in scope; `serviceInstanceAutoDeployUpdate` mutation exists). All observed deployments are CLI-sourced and no GitHub-triggered deployment exists on the service, but before the sync push the orchestrator should confirm in the Railway UI (Settings → Source) that GitHub auto-deploy is OFF, or rely on the fact that even if Railway auto-deploys, it would build the same hardened tree that the release plan deploys anyway.
- **FACT** Deployments visible (service-scoped): `f2c88f49…` **SUCCESS** created 2026-09-28T11:21:50.528Z (image digest `sha256:f746819cb131…`) and `2ad8b20b…` **FAILED** 11:20:14Z (the `.railwayignore` data-pattern first attempt per worklog). No GitHub-triggered deployments.
- **FACT** Domains: 1 service domain `mec-store-production.up.railway.app` (created 2026-09-28T01:54:16Z); **0 custom domains**.
- **FACT** Variables (names only, 18): `ADMIN_TOKEN`, `DATABASE_URL`, `DIRECT_DATABASE_URL`, `HOSTNAME`, `PRODSELLER_API_KEY`, `PRODSELLER_BASE_URL`, `STORE_MODE` + 11 auto-injected `RAILWAY_*`. No `GITHUB_TOKEN` on Railway (good).
- **TEST RESULT (live probes)** `GET /` → 200 (0.247 s); headers present: `content-security-policy`, `permissions-policy`, `referrer-policy`, `strict-transport-security` (2 y + preload), `x-content-type-options`, `x-frame-options: DENY`; `GET /api` → 200; `GET /api/admin/stats` without token → **401**. Production matches the hardened build.

---

## 6. Sensitive-File Audit

| Item | Local tracked? | On remote? | Classification |
|---|---|---|---|
| `.env` (6+ secrets) | YES (P0, incl. in `0e08876`) | **NO** | DEFECT P0 local / FACT clean remote |
| `db/custom.db` | YES | NO | DEFECT P1 local |
| `notion_raw/` (1124 files) | YES | NO | OK (never push) |
| `research/`, `data/`, `download/`, `tool-results/` | YES | NO | OK (never push) |
| `.env.example` | NO | YES (placeholders only) | SAFE |
| `README.md` | NO | YES (architecture doc, secret-scan clean) | SAFE — preserve in sync |
| Whitelisted code/configs | — | — | TEST RESULT: 0 secret-pattern hits |
| `worklog.md` | YES (tracked) | NO | never push (contains operational history) |

---

## 7. Sync Plan (prepare-only — orchestrator executes)

Principle: **never push local history** (contains `.env` blobs). Build ONE clean commit in an isolated worktree from whitelisted files, force-push over the 8 throwaway remote commits.

0. **(Recommended) Disable CI auto-trigger before push:**
   `curl -X PUT -H "Authorization: Bearer $GH_TOK" https://api.github.com/repos/ahmedabhusa6-hash/mec-store/actions/workflows/deploy.yml/disable`
   (If skipped: the workflow will fire and fail at "Build tarball"; Upload is skipped → no deploy. Verify after push either way.)
1. **Optionally commit the pending 1-line catalog fix first** (so the synced tree includes it): `git add src/app/api/store/catalog/route.ts && git commit -m "catalog: log fetch failure"`.
2. `git worktree add --detach /tmp/gh-sync 0e08876` (use HEAD if step 1 done).
3. Empty the worktree index: `cd /tmp/gh-sync && git rm -rq .`
4. Copy whitelist (123 files) from the main tree:
   ```
   cd /home/z/my-project
   git ls-files -- 'src/*' 'prisma/*' 'public/*' package.json next.config.ts tsconfig.json \
     tailwind.config.ts postcss.config.mjs eslint.config.mjs components.json bun.lock \
     .gitignore .railwayignore | while read -r f; do
       mkdir -p "/tmp/gh-sync/$(dirname "$f")"; cp "$f" "/tmp/gh-sync/$f"; done
   ```
5. Add housekeeping files (3):
   - `.env.example` — regenerated template (DATABASE_URL, DIRECT_DATABASE_URL, PRODSELLER_API_KEY, PRODSELLER_BASE_URL, STORE_MODE, **ADMIN_TOKEN** placeholders).
   - `README.md` — preserve current remote content (fetch via API; verified secret-clean).
   - `.github/workflows/deploy.yml` — **fixed** version (`branches: [main]`, tarball to `$RUNNER_TEMP/deploy.tar.gz` via `tar -C "$PWD" -czf "$RUNNER_TEMP/deploy.tar.gz" .`) — or omit if workflow left disabled.
   (Expected clean-tree total: **~126 files**.)
6. **Safety gates (all must pass):**
   - `test ! -e /tmp/gh-sync/.env` (and `git -C /tmp/gh-sync ls-files | grep -E '^\.env$|^notion_raw|^research|^db/|custom\.db|tool-results'` → empty)
   - Secret scan of worktree: `rg -l "psk_[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{20,}|postgres(ql)?://[^\"']*: [^\"']*@" /tmp/gh-sync` → empty
   - `git -C /tmp/gh-sync ls-files | wc -l` → ~126; spot-check `git -C /tmp/gh-sync hash-object package.json` equals expected local blob.
7. Commit (detached HEAD):
   ```
   git -C /tmp/gh-sync add -A
   git -C /tmp/gh-sync -c user.name="mec-deploy" -c user.email="deploy@mec.local" \
     commit -m "MEC-20: sync hardened production source (Next 16.3.6, admin token gate, rate limiting, security headers, sandbox delivery, engine consolidation, .railwayignore) — replaces pre-hardening tree; removes stale engine/*, store-*, mec10, [publicId] routes, seed pipeline, package-lock.json, Caddyfile"
   ```
8. Push (token from `.env`, never echoed; mask any URL output):
   ```
   GH_TOK=$(grep '^GITHUB_TOKEN=' /home/z/my-project/.env | cut -d= -f2)
   git -C /tmp/gh-sync push "https://x-access-token:${GH_TOK}@github.com/ahmedabhusa6-hash/mec-store.git" "+HEAD:main" 2>&1 | sed -E 's#//[^@/]+@#/***@#g'
   ```
9. **Verify via API:** GET `commits/main` → new sha/date; GET `git/trees/main?recursive=1` → ~126 blobs, no `.env`/`notion_raw`; blob sha of `package.json` == local `git hash-object package.json`.
10. **CI check:** GET `actions/runs` → if workflow was enabled, expect a failed "Build tarball" run with "Upload to Railway" skipped (harmless). Then either re-enable with fixed workflow or leave disabled.
11. Cleanup: `git worktree remove --force /tmp/gh-sync`.

---

## 8. Release & Rollback Plan (Railway, `railway up` — orchestrator executes)

**Release steps:**
1. Precondition: sync (§7) completed; local build green (`npm run build` / `next build` — 0 TS errors per MEC-18/19); `.railwayignore` intact (verified this audit).
2. Env vars: **no changes needed** — all 18 required names already set (incl. `ADMIN_TOKEN`, `STORE_MODE`, `PRODSELLER_*`, `DIRECT_DATABASE_URL`). Any future var addition goes via `variableUpsert` mutation or dashboard.
3. Deploy: `RAILWAY_API_TOKEN=<token> railway up --service mec-store --environment production` (same method as f2c88f49; ~285 KB upload). Do NOT commit the token anywhere.
4. Watch build via GraphQL `deployments` (status: BUILDING → SUCCESS) or `railway` dashboard.
5. Post-deploy smoke (read-only): `/` 200 + 6 headers; `/api` 200; `/api/admin/stats` → 401; catalog latency; 11th checkout/min → 429; one sandbox E2E purchase (register→deposit→buy→SANDBOX receipt).

**Rollback procedure (if new deployment fails or regresses):**
- Known-good target: deployment `f2c88f49-8a49-41d7-a11e-a3aa6d79cb97` (SUCCESS, image digest `sha256:f746819cb131…` — cached, so rollback is fast).
- Mutation (verified in schema):
  `mutation { deploymentRedeploy(id: "f2c88f49-8a49-41d7-a11e-a3aa6d79cb97", usePreviousImageTag: true) { id status } }`
  (Alternatives: `deploymentRollback(id: …)`, `serviceInstanceRedeploy(environmentId: "89138798-…", serviceId: "79f9401c-…")` for last-good.)
- Domain is service-attached — no domain reconfiguration on rollback.
- **DB caution:** current schema == deployed schema (this sync changes no schema), so rollback is code-only. Any FUTURE release that runs `prisma db push` must treat rollback as code+data (document before release).

**Risks & mitigations:**
| Risk | Sev | Mitigation |
|---|---|---|
| Push to GitHub triggers deploy.yml auto-deploy (REST upload) | P2 | Disable workflow before push (step 0); post-push runs check; even unfixed it fails at tar step |
| Railway GitHub auto-deploy active (repo label present) | P2 | Verify in Railway UI before push; if it fires, it builds the same hardened tree — verify deployment list after push |
| Force-push rewrites remote 8-commit history | P3 | Remote is a throwaway mirror; all live content preserved in the new tree; deleted-file list documented in commit message |
| Stale `package-lock.json` left on remote → `npm ci` installs Next 16.1.1 | P1 | Sync deletes it (whitelist excludes it; `bun.lock` shipped instead) |
| `.env` ever entering a push | P0 | Whitelist copy method + hard safety gates (§7.6); remote re-verified after push |
| Rate limiter in-memory (per-instance) | P3 | Accepted (documented MEC-18/19); single replica today; revisit if numReplicas > 1 |
| `db/custom.db` / `notion_raw/` exposure via accidental direct push | P0 | No remote configured in main repo; only worktree method used; gates check paths |

---

## 9. Limitations

- GitHub API read scope used; push ability asserted from mission context (not tested — read-only mandate).
- Railway GitHub-integration (auto-deploy) state not visible with a project token — flagged as unverified risk, needs UI/owner confirmation.
- Variable VALUES intentionally never read (names only); no verification that values are current/valid beyond live-app behavior (admin gate 401, catalog 200 prove DB + tokens work).
- Only 2 deployments visible via service-scoped query; older (01:5xZ) deployments not returned by API (pruned or out of scope) — the 01:58Z deployment referenced in worklog could not be inspected.
- Worklog Task 16 entry (worktree method) was lost in the environment recycle (worklog reverted to tasks 1-11 + 18-19); method reconstructed from mission context + remote commit evidence (cdab8bc lineage = clean single-tree pushes).
- Hash comparisons used working-tree files for locals; only `catalog/route.ts` differs from HEAD (1 log line) — verdicts unaffected.
