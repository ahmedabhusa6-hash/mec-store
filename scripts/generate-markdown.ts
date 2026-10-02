// Generate complete Markdown dataset export — semantically identical to web page
import {
  entitiesOfficial, entitiesB2B, entitiesMarket, entitiesUnverified, unverifiedNote,
  skuData, runData, actionsData, stats,
} from '../src/lib/data/index';

const W = [];
const p = (s = '') => W.push(s);

const now = new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';

p('# Adaptive Supplier Intelligence — Batch 1 Dataset');
p('');
p(`> **Engine**: Adaptive Supplier Intelligence Research Engine — v4.1 Candidate`);
p(`> **Run ID**: ${runData.run_metadata.run_id} · **Prompt Version**: ${runData.run_metadata.prompt_version}`);
p(`> **Primary Objective**: PRICE INTELLIGENCE (supplier discovery = mechanism; upstream/legitimacy = supporting dimensions)`);
p(`> **Program Scope**: 400+ SKU digital products/services catalog — this file documents **Batch 1** (${stats.skusExecuted} SKUs executed, remaining catalog queued)`);
p(`> **Generated**: ${now}`);
p('');
p(`**Governing price formulation** — used exclusively, never "cheapest in the world":`);
p('');
p('> *"the lowest price discovered and verified within the research scope, at the time of checking, under the specified SKU and offer conditions."*');
p('');
p('---');
p('');

// ============ 1. RUN METADATA
p('## 1. Run Metadata');
p('');
p('| Field | Value |');
p('|---|---|');
p(`| Run ID | ${runData.run_metadata.run_id} |`);
p(`| Started | ${runData.run_metadata.start_utc} |`);
p(`| Complexity Class | ${runData.run_metadata.complexity_class} (C4) |`);
p(`| Actions Executed | ${actionsData.total_actions} / 96 (${actionsData.by_retrieval.Success} success, ${actionsData.by_retrieval.Failed} failed) |`);
p(`| Reserve | 24 untouched |`);
p(`| Transaction Verification | **Not Performed** (all offers — listing-level evidence only) |`);
p(`| Output Contract | Web Page + Markdown (this file) — semantically identical |`);
p('');
p('**Core invariants enforced throughout**: Discovered ≠ Verified ≠ Supplier ≠ Upstream Source ≠ Primary Source ≠ Lowest Verified Price · Advertised Price ≠ Transaction Price · Availability ≠ Purchase · Product availability ≠ Resale Authorization · Technical similarity ≠ Business Relationship · Search failure ≠ Non-Existence.');
p('');

// ============ 2. SCOPE LOCK
p('## 2. Scope Lock');
p('');
p('**Locked (immutable for the run):**');
for (const l of runData.scope_lock.locked) p(`- ${l}`);
p('');
p('**Proposed Scope Expansions (NOT executed — require user authorization):**');
p('');
for (const e of runData.scope_lock.proposed_scope_expansions) {
  p(`- **${e.proposal}** — ${e.reason} → \`${e.status}\``);
}
p('');

// ============ 3. SKU RECORDS
p('## 3. SKU Records & Price Intelligence (Batch 1)');
p('');
for (const sku of skuData.batch1_skus) {
  p(`### ${sku.sku_id} — ${sku.identity.brand} ${sku.identity.product}`);
  p('');
  p(`**Family**: ${sku.family}`);
  p('');
  p(`**SKU Identity** (comparability basis):`);
  p('');
  p('```json');
  p(JSON.stringify(sku.identity, null, 2));
  p('```');
  p('');
  const a = sku.official_anchor;
  p(`**Official Anchor**: ${a && a.price != null ? `${a.price} ${a.currency} / ${a.per}` : '**Unknown — Retrieval-Limited**'} `);
  p(`- Evidence Level: \`${a?.evidence_level}\` · Freshness: \`${a?.freshness}\``);
  p(`- Evidence: ${a?.evidence}`);
  p('');
  if (sku.offers && sku.offers.length) {
    p('**Offers** (each an independent commercial proposition):');
    p('');
    p('| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |');
    p('|---|---|---|---|---|---|---|---|---|');
    for (const o of sku.offers) {
      p(`| ${o.entity} | ${o.price != null ? o.price : '—'} | ${o.unit || '—'} | ${o.match} | ${o.price_evidence} | ${o.freshness} | ${o.guarantee || 'Unknown'} | ${o.resale || 'Unknown'} | ${o.source} |`);
    }
    p('');
  } else {
    p('**Offers**: None captured (honest empty state — see coverage).');
    p('');
  }
  p('**Price Intelligence**:');
  p('');
  const pi = sku.price_intelligence as Record<string, unknown>;
  for (const [k, v] of Object.entries(pi)) {
    const label = k.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase());
    p(`- **${label}**: ${v}`);
  }
  p('');
  p('**Coverage**:');
  p('');
  for (const [k, v] of Object.entries((sku.coverage || {}) as Record<string, unknown>)) {
    if (k === 'notes') continue;
    p(`- ${k}: ${v}`);
  }
  if ((sku.coverage as any)?.notes) p(`- Notes: ${(sku.coverage as any).notes}`);
  p('');
  p('---');
  p('');
}

// ============ 4. REMAINING CATALOG
p('## 4. Remaining Catalog (400+ SKU program)');
p('');
p('| Family | Status | Planned Coverage |');
p('|---|---|---|');
for (const f of skuData.remaining_catalog.status_per_family) {
  p(`| ${f.family} | ${f.status} | ${f.planned} |`);
}
p('');
p(`> Every "Not Searched" status is an honest §15 state — it never means "does not exist". ${skuData.remaining_catalog.expansion_note}`);
p('');

// ============ 5. ENTITIES
p('## 5. Entities & Role Classification');
p('');
const emitEntity = (e: any) => {
  p(`#### ${e.id} — ${e.name}`);
  p('');
  p(`- **Type**: ${e.type}`);
  p(`- **Role**: ${e.role}`);
  p(`- **Status**: ${e.status}`);
  p(`- **Verified via**: ${(e.verified_via || []).join(', ') || '—'}`);
  p(`- **Independence**: ${e.independence || 'N/A'}`);
  p(`- **Guarantee**: ${e.guarantee || 'Unknown'}`);
  p(`- **Resale**: ${e.resale || 'Unknown'}`);
  if (e.evidence) {
    p('- **Evidence**:');
    for (const ev of e.evidence) {
      p(`  - [${ev.action}] ${ev.source} — ${ev.observation} (\`${ev.evidence_level}\`, Freshness: ${ev.freshness})`);
    }
  }
  if (e.relationships && e.relationships.length) {
    p('- **Relationships**:');
    for (const r of e.relationships) p(`  - → ${r.to}: ${r.type} — \`${r.status}\``);
  }
  if (e.notes) p(`- **Notes**: ${e.notes}`);
  p('');
};

p(`### 5.1 Publishers / Official Sources (${entitiesOfficial.length})`);
p('');
for (const e of entitiesOfficial) emitEntity(e);

p(`### 5.2 B2B / Upstream API Infrastructure (${entitiesB2B.length})`);
p('');
for (const e of entitiesB2B) emitEntity(e);

p(`### 5.3 Marketplaces / Sellers / Services (${entitiesMarket.length})`);
p('');
for (const e of entitiesMarket) emitEntity(e);

p(`### 5.4 Unverified Leads — from project seeds (${entitiesUnverified.length} groups, retained in Open-Items Ledger)`);
p('');
p(`> ${unverifiedNote}`);
p('');
p('| ID | Name | Seed Layer | Verification Attempts | Status |');
p('|---|---|---|---|---|');
for (const e of entitiesUnverified) {
  p(`| ${e.id} | ${e.name.length > 60 ? e.name.slice(0, 57) + '...' : e.name} | ${e.seed_layer} | ${(e.verification_attempts || []).join('; ') || '—'} | ${e.status} |`);
}
p('');

// ============ 6. SUPPLY CHAIN
p('## 6. Supply Chain / Upstream Tracing');
p('');
p('**Role taxonomy** (not a mandatory sequence): Seller → Reseller → Wholesaler → Distributor → Aggregator → Upstream Supplier → Primary Source.');
p('');
p('**Deepest evidence-supportable upstream layer this run**: B2B digital-value API infrastructure (DT One, Reloadly, DingConnect).');
p('');
p('| Relationship | Type | Status | Evidence |');
p('|---|---|---|---|');
p('| DT One → PayPal (France airtime) | Infrastructure provider | Documented (dtone.com case study) | A076 |');
p('| DT One → Bitget Wallet (top-ups, 170+ countries) | Infrastructure provider | Documented (press release Mar 2026) | A076 |');
p('| B2B platforms → MENA retailers | Suspected supply chain | **Unresolved Hypothesis (H3)** — zero direct evidence | — |');
p('| Turgame ↔ Definite Play | Candidate entity merge | **Unresolved (H2)** — no evidence either direction | A058/A075 |');
p('| Reloadly (dual seed listing) | Entity resolution | Resolved: single entity, dual role records in seeds | A040 |');
p('');
p('**Invariant enforced**: Upstream ≠ Cheapest. No upstream link was inferred from lower price, catalogue similarity, shared branding, or common language (§7).');
p('');

// ============ 7. COVERAGE
p('## 7. Coverage Status by Discovery Family');
p('');
p('| Discovery Family | Status | Detail |');
p('|---|---|---|');
for (const c of runData.coverage_matrix) {
  p(`| ${c.discovery_family} | ${c.status} | ${c.detail} |`);
}
p('');
p('**Statuses used** (exclusively): Not Searched · Searched — No Useful Result · Retrieval Failed / Access Unavailable · Budget-Limited · Unresolved · Verified Findings. Retrieval failure is never converted into non-existence.');
p('');

// ============ 8. BRANCHES
p('## 8. Branch Terminal States & Stopping Diagnoses');
p('');
p('| Branch | Terminal State | Diagnosis |');
p('|---|---|---|');
for (const b of runData.branch_terminal_states) {
  p(`| ${b.branch} | ${b.state} | ${b.diagnosis} |`);
}
p('');
p('**Four-cause diagnostic enforced**: True Saturation / Retrieval Ceiling / Poor Query Strategy / Insufficient Exploration — differentiated per branch before closure. Retrieval-Limited, Budget-Limited, and Scope-Excluded are never labeled "saturated".');
p('');

// ============ 9. HYPOTHESES
p('## 9. Open Hypotheses & Unresolved Claims');
p('');
for (const h of runData.open_hypotheses) {
  p(`### ${h.id}: ${h.statement}`);
  p('');
  p(`- **Status**: ${h.status}`);
  p('- **Supporting evidence**:');
  for (const s of h.supporting) p(`  - ${s}`);
  p('- **Contradicting evidence**:');
  for (const c of h.contradicting) p(`  - ${c}`);
  p('- **Next actions**:');
  for (const n of h.next_actions) p(`  - ${n}`);
  p('');
}
p('**Unresolved material claims**:');
p('');
for (const c of runData.unresolved_claims) p(`- ${c}`);
p('');

// ============ 10. EXCLUSION SCREEN
p('## 10. Exclusion / Unauthorized-Activity Screen');
p('');
p('Protocol: Signal → Supporting Evidence → Classification → Action. A signal without sufficient evidence remains a review state, never an accusation.');
p('');
const ex = runData.exclusion_screen as any;
p(`- **Excluded-Confirmed**: ${ex.excluded_confirmed.length === 0 ? 'None this run (no direct evidence of stolen credentials, OTP bypass, or cracked access captured — honest state)' : ex.excluded_confirmed.join('; ')}`);
p(`- **Excluded-Suspected / Needs-Human-Review**: ${ex.excluded_suspected_needs_review.length} subject groups quarantined from commercial ranking (see below)`);
p(`- **Not-Excluded with flags**: ${ex.not_excluded_with_flags.length} (Z2U account listings; individual classifieds sellers)`);
p('');
for (const s of ex.excluded_suspected_needs_review) {
  p(`- **${s.subject}** — Signal: ${s.signal} → \`${s.classification}\` → ${s.action}`);
}
p('');

// ============ 11. BUDGET & FAILURES
p('## 11. Budget Summary & Failure/Recovery Log');
p('');
const b = runData.budget_summary as any;
p('| Field | Value |');
p('|---|---|');
p(`| Complexity class | ${b.complexity_class} |`);
p(`| Total cap | ${b.total_cap} |`);
p(`| Actions executed | ${b.actions_executed} |`);
p(`| Failures | ${b.actions_failed} (no-results: ${b.failures_by_cause.no_results_422}, rate-limited: ${b.failures_by_cause.rate_limited_429}, junk-results: ${b.failures_by_cause.garbage_results_success_status}) |`);
p(`| Reserve | ${b.reserve_untouched} untouched |`);
p(`| Per-branch cap | ${b.per_branch_max} |`);
p(`| Hypothesis minimum rule | ${b.hypothesis_minimum_rule} |`);
p('');
p('**Failure → Recovery log** (§19 — every failure recovered via construction/method/channel switch or honestly terminalized):');
p('');
p('| Actions | Subject | Failure | Recovery | Outcome |');
p('|---|---|---|---|---|');
for (const f of runData.failure_recovery_log) {
  p(`| ${f.action} | ${f.sku} | ${f.failure} | ${f.recovery} | ${f.outcome} |`);
}
p('');

// ============ 12. RESEARCH ACTION LOG
p('## 12. Research Action Log (complete — 76 actions)');
p('');
p('| ID | Time (UTC) | Branch | SKU | Discovery Family | Query | Retrieval | Results |');
p('|---|---|---|---|---|---|---|---|');
for (const a of actionsData.actions) {
  const q = a.query.replace(/\|/g, '/').slice(0, 80);
  p(`| ${a.action_id} | ${a.timestamp_utc.slice(11, 19)} | ${a.branch} | ${a.sku_id || '—'} | ${a.discovery_family.split('(')[0].trim()} | ${q} | ${a.retrieval_status} | ${a.result_count} |`);
}
p('');

// ============ 13. AUDIT
p('## 13. Audit Record (§23)');
p('');
const au = runData.audit_record as any;
p('**What was established**:');
for (const x of au.what_was_established) p(`- ${x}`);
p('');
p(`**What remains unresolved**: ${au.what_remains_unresolved}`);
p('');
p('**What was inaccessible**:');
for (const x of au.what_was_inaccessible) p(`- ${x}`);
p('');
p(`**What was excluded and why**: ${au.what_was_excluded_and_why}`);
p('');
p('**Which conclusions survived counter-evidence**:');
for (const x of au.which_conclusions_survived_counter_evidence) p(`- ${x}`);
p('');
p(`**Why research stopped**: ${au.why_research_stopped}`);
p('');
p('**Important routes not searched**:');
for (const x of au.important_routes_not_searched) p(`- ${x}`);
p('');
p('**What could materially change current conclusions**:');
for (const x of au.what_could_materially_change_conclusions) p(`- ${x}`);
p('');
p('**Tool limitations affecting completeness**:');
for (const x of au.tool_limitations_affecting_completeness) p(`- ${x}`);
p('');
p(`**Transaction Verification**: ${runData.transaction_verification.status} — ${runData.transaction_verification.note}`);
p('');
p('---');
p('');
p(`*Dataset completeness: ${stats.skusExecuted} SKUs executed / 400+ program scope · ${stats.entitiesVerified} verified entities + ${stats.entitiesUnverifiedGroups} unverified lead groups · ${stats.offersCaptured} offers · ${stats.actionsExecuted} research actions logged · Last Checked: ${now}. Continued batches will extend this dataset under the same run contract.*`);

import * as fs from 'fs';
fs.writeFileSync('/home/z/my-project/download/supplier-intelligence-batch1-dataset.md', W.join('\n'));
console.log(`Markdown written: ${W.length} lines → download/supplier-intelligence-batch1-dataset.md`);
