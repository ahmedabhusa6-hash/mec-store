// ============================================================
// Research Action Runner — Supplier Intelligence Engine v4.1
// Executes web_search Research Actions with full audit logging.
// Usage: bun scripts/research-runner.ts <wave-file.json>
// ============================================================
import ZAI from 'z-ai-web-dev-sdk';
import * as fs from 'fs';
import * as path from 'path';

const RESEARCH_DIR = '/home/z/my-project/data/research';
const RAW_DIR = path.join(RESEARCH_DIR, 'raw');
const LOG_FILE = path.join(RESEARCH_DIR, 'actions-log.jsonl');
const BUDGET_FILE = path.join(RESEARCH_DIR, 'budget.json');

interface ActionDef {
  action_id: string;
  branch: string;
  sku_id: string | null;
  objective: string;
  discovery_family: string;
  method: string;
  query: string;
  num?: number;
  recency_days?: number;
}

interface ActionRecord {
  action_id: string;
  timestamp_utc: string;
  parent_branch: string;
  sku_id: string | null;
  objective_addressed: string;
  discovery_family: string;
  method_tool: string;
  query: string;
  retrieval_status: 'Success' | 'Success-Empty' | 'Failed';
  result_count: number;
  sources: { url: string; host: string; name: string; date: string }[];
  yield_classification: 'Pending-Review';
  budget_debit: number;
}

async function main() {
  const waveFile = process.argv[2];
  if (!waveFile) {
    console.error('Usage: bun scripts/research-runner.ts <wave-file.json>');
    process.exit(1);
  }
  const actions: ActionDef[] = JSON.parse(fs.readFileSync(waveFile, 'utf-8'));

  // Load budget state
  let budget: { total_cap: number; used: number; reserve: number };
  if (fs.existsSync(BUDGET_FILE)) {
    budget = JSON.parse(fs.readFileSync(BUDGET_FILE, 'utf-8'));
  } else {
    budget = { total_cap: 96, used: 0, reserve: 24 }; // C4: 96 cap, 25% reserve
  }

  if (budget.used + actions.length > budget.total_cap) {
    console.error(`BUDGET EXCEEDED: used=${budget.used}, requested=${actions.length}, cap=${budget.total_cap}`);
    process.exit(2);
  }

  const zai = await ZAI.create();
  const logStream = fs.createWriteStream(LOG_FILE, { flags: 'a' });

  for (const action of actions) {
    const ts = new Date().toISOString();
    let record: ActionRecord;
    try {
      const results: any[] = await zai.functions.invoke('web_search', {
        query: action.query,
        num: action.num ?? 8,
        ...(action.recency_days ? { recency_days: action.recency_days } : {}),
      });
      const sources = (results || []).map((r: any) => ({
        url: r.url,
        host: r.host_name,
        name: r.name,
        date: r.date || '',
      }));
      record = {
        action_id: action.action_id,
        timestamp_utc: ts,
        parent_branch: action.branch,
        sku_id: action.sku_id,
        objective_addressed: action.objective,
        discovery_family: action.discovery_family,
        method_tool: `web_search (${action.method})`,
        query: action.query,
        retrieval_status: (results && results.length > 0) ? 'Success' : 'Success-Empty',
        result_count: sources.length,
        sources,
        yield_classification: 'Pending-Review',
        budget_debit: 1,
      };
      fs.writeFileSync(
        path.join(RAW_DIR, `${action.action_id}.json`),
        JSON.stringify({ action, results, timestamp: ts }, null, 2)
      );
    } catch (err: any) {
      record = {
        action_id: action.action_id,
        timestamp_utc: ts,
        parent_branch: action.branch,
        sku_id: action.sku_id,
        objective_addressed: action.objective,
        discovery_family: action.discovery_family,
        method_tool: `web_search (${action.method})`,
        query: action.query,
        retrieval_status: 'Failed',
        result_count: 0,
        sources: [],
        yield_classification: 'Pending-Review',
        budget_debit: 1,
      };
      fs.writeFileSync(
        path.join(RAW_DIR, `${action.action_id}.json`),
        JSON.stringify({ action, error: err?.message || String(err), timestamp: ts }, null, 2)
      );
    }
    logStream.write(JSON.stringify(record) + '\n');
    budget.used += record.budget_debit;
    console.log(
      `[${record.action_id}] ${record.retrieval_status} (${record.result_count} results) | budget: ${budget.used}/${budget.total_cap}`
    );
  }

  logStream.end();
  fs.writeFileSync(BUDGET_FILE, JSON.stringify(budget, null, 2));
  console.log(`\nWave complete. Budget: ${budget.used}/${budget.total_cap} used, reserve ${budget.reserve}.`);
}

main().catch((e) => {
  console.error('RUNNER FATAL:', e);
  process.exit(3);
});
