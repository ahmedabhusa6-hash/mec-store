// Generate actions.json (research action log summary) from actions-log.jsonl
import * as fs from 'fs';

const LOG = '/home/z/my-project/data/research/actions-log.jsonl';
const OUT = '/home/z/my-project/src/lib/data/actions.json';

const lines = fs.readFileSync(LOG, 'utf-8').trim().split('\n');
const records = lines.map((l) => JSON.parse(l));

const summary = {
  total_actions: records.length,
  by_retrieval: {} as Record<string, number>,
  by_discovery_family: {} as Record<string, number>,
  actions: records.map((r) => ({
    action_id: r.action_id,
    timestamp_utc: r.timestamp_utc,
    branch: r.parent_branch,
    sku_id: r.sku_id,
    objective: r.objective_addressed,
    discovery_family: r.discovery_family,
    method: r.method_tool,
    query: r.query,
    retrieval_status: r.retrieval_status,
    result_count: r.result_count,
    budget_debit: r.budget_debit,
    sources: r.sources.map((s: any) => s.host),
  })),
};

for (const r of records) {
  summary.by_retrieval[r.retrieval_status] = (summary.by_retrieval[r.retrieval_status] || 0) + 1;
  const fam = r.discovery_family.split('(')[0].trim();
  summary.by_discovery_family[fam] = (summary.by_discovery_family[fam] || 0) + 1;
}

fs.writeFileSync(OUT, JSON.stringify(summary, null, 2));
console.log(`actions.json written: ${summary.total_actions} actions`);
console.log('by_retrieval:', summary.by_retrieval);
console.log('families:', Object.keys(summary.by_discovery_family).length);
