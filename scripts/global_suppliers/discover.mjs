// GDS-1: Paced discovery runner — resumable, rate-limit aware
// Usage: node discover.mjs <maxQueries> [startFrom]
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';

const GS = '/home/z/my-project/research/global_suppliers';
const RAW = `${GS}/raw`;
const STATE_F = `${GS}/state.json`;
const LEDGER = `${GS}/discovery_ledger.json`;
const QUERIES = JSON.parse(fs.readFileSync(`${GS}/queries.json`, 'utf-8')).queries;

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
function load(f, dflt) { try { return JSON.parse(fs.readFileSync(f, 'utf-8')); } catch { return dflt; } }
function save(f, o) { fs.writeFileSync(f, JSON.stringify(o, null, 1), 'utf-8'); }

async function main() {
  const maxQ = parseInt(process.argv[2] || '40', 10);
  const state = load(STATE_F, { run: 'GDS-1', counters: { queries_ok: 0, queries_fail: 0, results: 0 }, rate_limit: { blocked: false, streak: 0 }, checkpoint: { qualified: 0 } });
  const ledger = load(LEDGER, { entries: [] });
  // derive counters from ledger (single source of truth; avoids double-count drift)
  state.counters.queries_ok = ledger.entries.filter(e => e.ok).length;
  state.counters.queries_fail = ledger.entries.filter(e => !e.ok).length;
  state.counters.results = ledger.entries.reduce((a, e) => a + (e.n || 0), 0);
  const doneIds = new Set(ledger.entries.map(e => e.qid));
  const zai = await ZAI.create();

  let ran = 0, ok = 0, fail = 0, consecutiveFails = 0;
  state.rate_limit.streak = 0; // fresh run = fresh attempt (previous block may have cleared)
  for (const q of QUERIES) {
    if (ran >= maxQ) break;
    if (doneIds.has(q.id)) continue;
    if (state.rate_limit.streak >= 3) { console.log('RATE LIMIT STOP (3 consecutive failures)'); break; }

    let attempt = 0, rec = null, success = false;
    while (attempt < 2) {
      attempt++;
      try {
        const r = await zai.functions.invoke('web_search', { query: q.q, num: 10 });
        const results = (Array.isArray(r) ? r : []).map(x => ({
          name: x.name, url: x.url, host: (x.host_name || '').replace(/^www\./, ''),
          snippet: (x.snippet || '').slice(0, 350)
        }));
        rec = { qid: q.id, ts: new Date().toISOString(), ok: true, region: q.region, lang: q.lang, family: q.family, query: q.q, n: results.length, results };
        success = true; ok++;
        save(`${RAW}/${q.id}.json`, rec);
        state.counters.queries_ok++; state.counters.results += results.length;
        consecutiveFails = 0; state.rate_limit.streak = 0;
        break; // SUCCESS = stop retry loop (critical: no double-invoke)
      } catch (e) {
        const msg = String(e && e.message || e);
        if (attempt === 1) { await sleep(20000); } // cooldown, single retry
        else { rec = { qid: q.id, ts: new Date().toISOString(), ok: false, error: msg.slice(0, 150) }; fail++; consecutiveFails++; state.rate_limit.streak = consecutiveFails; }
      }
    }
    ledger.entries.push({ qid: rec.qid, ok: rec.ok, region: q.region, lang: q.lang, family: q.family, query: q.q, n: rec.n || 0, error: rec.error || null, ts: rec.ts });
    ran++;
    if (ran % 10 === 0 || ran >= maxQ) { save(LEDGER, ledger); save(STATE_F, state); }
    console.log(`[${rec.ok ? 'OK ' : 'ERR'} ${ran}/${maxQ}] ${q.region}/${q.lang} ${q.family} · ${rec.n || rec.error || 0}`);
    await sleep(5000);
  }
  ledger.finished = new Date().toISOString();
  save(LEDGER, ledger); save(STATE_F, state);
  console.log(`\nDONE. ran=${ran} ok=${ok} fail=${fail} | total_ok=${state.counters.queries_ok} total_results=${state.counters.results}`);
}
main().catch(e => { console.error('FATAL', e); process.exit(1); });
