// MEC-2.0 G1-b + G2-a: paced research wave (26 queries)
// Reputation (TG registry clusters) + supply-chain economics evidence + better-channel scan
// Output: data/research/mec2_search_results.json
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';

const OUT = '/home/z/my-project/data/research/mec2_search_results.json';
const QUERIES = [
  // --- G2-a: supply-chain economics evidence ---
  ['ECON', 'YouTube Premium family plan India price 189 rupees per month'],
  ['ECON', 'Spotify Premium Family India price 179 rupees month'],
  ['ECON', 'Netflix India subscription price mobile basic standard premium 2026'],
  ['ECON', 'Google One AI Pro 12 months free trial Pixel promo redeem code'],
  ['ECON', 'Google One AI Pro 试用码 出售 便宜 Gemini 升级'],
  ['ECON', 'Reloadly gift card API pricing discount face value B2B'],
  ['ECON', 'Turgame wholesale dealer portal discount game wallet'],
  ['ECON', 'where do G2A Kinguin sellers get cheap cd keys gray market study'],
  ['ECON', 'Humble Bundle keys resell profit gray market reddit'],
  ['ECON', 'Steam regional pricing Turkey Argentina cheaper arbitrage 2026'],
  ['ECON', 'edu email account for sale student discount verification SheerID price'],
  ['ECON', 'Xbox Game Pass Ultimate Turkey price lira cheaper conversion'],
  // --- G1-b: registry cluster reputation ---
  ['REPU', 'ProdSeller telegram bot review gemini'],
  ['REPU', 'Acczone store telegram review'],
  ['REPU', 'HitMeow shop telegram premikey'],
  ['REPU', 'StackVault shop review digital subscriptions'],
  ['REPU', 'gemini12pro channel gemini pixel helper bot'],
  ['REPU', 'Veriyferbot verifier bot telegram escrow guarantee'],
  ['REPU', 'Gamisell telegram bot review'],
  ['REPU', 'Neva AI nevakeystore telegram'],
  ['REPU', 'insightXpro bot store telegram'],
  ['REPU', 'Evolution Era telegram store bot'],
  // --- G1-b: better channels ---
  ['BETTER', 'cheapest legit ChatGPT Plus subscription deal 2026'],
  ['BETTER', 'best trusted game key sites 2026 Eneba Kinguin Driffy comparison'],
  ['BETTER', 'AI subscription wholesale API reseller digital goods plati digiseller'],
  ['BETTER', 'plati market digiseller digital goods wholesale seller'],
];

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function main() {
  const zai = await ZAI.create();
  const results = { started: new Date().toISOString(), queries: [] };
  let ok = 0, fail = 0;
  for (const [group, q] of QUERIES) {
    let attempt = 0, rec = null;
    while (attempt < 2) {
      attempt++;
      try {
        const r = await zai.functions.invoke('web_search', { query: q, num: 8 });
        rec = { group, query: q, attempt, ok: true, count: Array.isArray(r) ? r.length : 0,
                results: (Array.isArray(r) ? r : []).map(x => ({
                  name: x.name, url: x.url, host: x.host_name, date: x.date,
                  snippet: (x.snippet || '').slice(0, 400) })) };
        ok++;
        break;
      } catch (e) {
        if (attempt === 1) { await sleep(15000); } // cool-down then single retry
        else rec = { group, query: q, attempt, ok: false, error: String(e && e.message || e).slice(0, 200) };
      }
    }
    results.queries.push(rec);
    console.log(`[${rec.ok ? 'OK ' : 'ERR'}] ${group} · ${q} · ${rec.count || 0} results`);
    await sleep(5000);
  }
  results.finished = new Date().toISOString();
  results.summary = { total: QUERIES.length, ok, fail: QUERIES.length - ok };
  fs.writeFileSync(OUT, JSON.stringify(results, null, 1), 'utf-8');
  console.log('\nSaved:', OUT, '| ok:', ok, '| fail:', QUERIES.length - ok);
}
main().catch(e => { console.error('FATAL', e); process.exit(1); });
