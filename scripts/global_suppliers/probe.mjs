import ZAI from 'z-ai-web-dev-sdk';
const zai = await ZAI.create();
try {
  const r = await zai.functions.invoke('web_search', { query: 'gift card API provider B2B distribution', num: 5 });
  console.log('SEARCH OK:', (r||[]).length, 'results');
} catch (e) { console.log('SEARCH BLOCKED:', String(e.message).slice(0,80)); }
try {
  const r2 = await zai.functions.invoke('web_reader', { url: 'https://tillo.com/' });
  console.log('READER OK:', String(JSON.stringify(r2)).slice(0,120));
} catch (e) { console.log('READER BLOCKED:', String(e.message).slice(0,80)); }
