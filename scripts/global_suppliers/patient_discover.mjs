// GDS-2: Patient discovery runner — waits through 429 windows, never wastes a query.
// Usage: nohup node patient_discover.mjs <maxQueries> <wallBudgetMinutes> >> patient.log 2>&1 &
// - Only OK queries are committed to the ledger (429s are retried later, not burned).
// - Retries wave-1 queries whose only ledger entry is ok:false.
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';

const GS = '/home/z/my-project/research/global_suppliers';
const RAW = `${GS}/raw`;
const STATE_F = `${GS}/state.json`;
const LEDGER = `${GS}/discovery_ledger.json`;
const QUERIES = JSON.parse(fs.readFileSync(`${GS}/queries.json`, 'utf-8')).queries;

const maxQ = parseInt(process.argv[2] || '2000', 10);
const WALL_MS = parseInt(process.argv[3] || '540', 10) * 60 * 1000; // default 9h
const PACE_MS = 5000;
const T0 = Date.now();

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
function load(f, dflt) { try { return JSON.parse(fs.readFileSync(f, 'utf-8')); } catch { return dflt; } }
function save(f, o) { fs.writeFileSync(f, JSON.stringify(o, null, 1), 'utf-8'); }
const ts = () => new Date().toISOString().slice(11, 19);

async function main() {
  const state = load(STATE_F, { run: 'GDS-1', counters: { queries_ok: 0, queries_fail: 0, results: 0 }, rate_limit: { blocked: false, streak: 0 } });
  const ledger = load(LEDGER, { entries: [] });
  state.run = 'GDS-2';
  // done = queries with an OK entry; failed-only entries get retried
  const okIds = new Set(ledger.entries.filter(e => e.ok).map(e => e.qid));
  const queue = QUERIES.filter(q => !okIds.has(q.id));
  console.log(`[${ts()}] patient start | plan=${QUERIES.length} remaining=${queue.length} maxQ=${maxQ} wall=${WALL_MS / 60000}min`);

  const zai = await ZAI.create();
  let ran = 0, ok = 0, backoff = 150000, consecutive429 = 0, lastSave = 0;

  for (let i = 0; i < queue.length; i++) {
    if (ran >= maxQ) { console.log(`[${ts()}] query budget reached (${maxQ})`); break; }
    if (Date.now() - T0 > WALL_MS) { console.log(`[${ts()}] wall budget reached`); break; }
    const q = queue[i];

    let rec = null;
    try {
      const r = await zai.functions.invoke('web_search', { query: q.q, num: 10 });
      const results = (Array.isArray(r) ? r : []).map(x => ({
        name: x.name, url: x.url, host: (x.host_name || '').replace(/^www\./, ''),
        snippet: (x.snippet || '').slice(0, 350)
      }));
      rec = { qid: q.id, ts: new Date().toISOString(), ok: true, region: q.region, lang: q.lang, family: q.family, query: q.q, n: results.length, results };
      save(`${RAW}/${q.id}.json`, rec);
      ok++; ran++; consecutive429 = 0; backoff = 150000;
      ledger.entries.push({ qid: q.id, ok: true, region: q.region, lang: q.lang, family: q.family, query: q.q, n: results.length, ts: rec.ts });
      console.log(`[${ts()}] OK ${ran} (${ok}/${queue.length} left) ${q.region}/${q.lang} ${q.family} · ${results.length}`);
      await sleep(PACE_MS);
    } catch (e) {
      const msg = String(e && e.message || e);
      const is429 = msg.includes('429') || msg.toLowerCase().includes('too many');
      if (is429) {
        consecutive429++;
        console.log(`[${ts()}] 429 #${consecutive429} — backing off ${backoff / 1000}s (query NOT burned: ${q.q.slice(0, 50)})`);
        i--; // retry same query after backoff
        await sleep(backoff);
        backoff = Math.min(backoff + 150000, 600000); // 150s→300s→450s→600s cap
      } else {
        ran++;
        console.log(`[${ts()}] ERR (non-429, skipped): ${msg.slice(0, 100)}`);
        await sleep(PACE_MS);
      }
    }
    // periodic state save (every 20 queries)
    if (ok - lastSave >= 20) {
      state.counters.queries_ok = ledger.entries.filter(e => e.ok).length;
      state.counters.queries_fail = ledger.entries.filter(e => !e.ok).length;
      state.counters.results = ledger.entries.reduce((a, e) => a + (e.n || 0), 0);
      save(LEDGER, ledger); save(STATE_F, state);
      lastSave = ok;
    }
  }

  state.counters.queries_ok = ledger.entries.filter(e => e.ok).length;
  state.counters.queries_fail = ledger.entries.filter(e => !e.ok).length;
  state.counters.results = ledger.entries.reduce((a, e) => a + (e.n || 0), 0);
  ledger.finished = new Date().toISOString();
  save(LEDGER, ledger); save(STATE_F, state);
  console.log(`[${ts()}] DONE. thisRun_ok=${ok} | ledger_ok=${state.counters.queries_ok} | results=${state.counters.results}`);
  process.exit(0);
}
main().catch(e => { console.error('FATAL', e); process.exit(1); });
