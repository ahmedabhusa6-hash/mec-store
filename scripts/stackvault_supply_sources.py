#!/usr/bin/env python3
# SV-SUPPLY: Precise supply-source extraction for stackvault.shop
# Passive OSINT only — public API GET + link verification. No auth, no scanning.
import json, re, time, statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
import requests, urllib3
urllib3.disable_warnings()

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
OUT = '/home/z/my-project/research/stackvault_live'
res = {'generated': datetime.now(timezone.utc).isoformat(), 'link_verification': {}, 'supply_sources': {}}

# ============ 1. LINK VERIFICATION (fresh, now) ============
def check(url):
    try:
        r = requests.get(url, headers=UA, timeout=(5, 20), verify=False, allow_redirects=True)
        return {'status': r.status_code, 'final_url': r.url, 'server': r.headers.get('server',''),
                'ip_note': '', 'size': len(r.text or ''), 't_ok': True}
    except Exception as e:
        return {'status': 0, 'error': str(e)[:150], 't_ok': False}

res['link_verification']['https://stackvault.shop/'] = check('https://stackvault.shop/')
res['link_verification']['https://stackvault.shop/my_orders'] = check('https://stackvault.shop/my_orders')
import socket
try:
    ips = sorted({ai[4][0] for ai in socket.getaddrinfo('stackvault.shop', 443)})
    res['link_verification']['dns_ips'] = ips
    for ip in ips:
        try:
            res['link_verification'].setdefault('reverse_dns', {})[ip] = socket.gethostbyaddr(ip)[0]
        except Exception:
            res['link_verification'].setdefault('reverse_dns', {})[ip] = '(no PTR)'
except Exception as e:
    res['link_verification']['dns_error'] = str(e)[:100]

# ============ 2. LIVE CATALOG PULL ============
api = None
for endpoint in ['https://decohomz.com/sv-api/products', 'https://stackvault.shop/sv-api/products']:
    r = check(endpoint)
    if r['status'] == 200:
        try:
            api = requests.get(endpoint, headers=UA, timeout=(5, 30), verify=False)
            data = api.json()
            prods = data if isinstance(data, list) else data.get('products', [])
            res['supply_sources']['catalog_endpoint_used'] = endpoint
            break
        except Exception:
            continue
if api is None:
    # fallback to most recent saved capture
    data = json.load(open(f'{OUT}/sv_products_current.json'))
    prods = data if isinstance(data, list) else data.get('products', [])
    res['supply_sources']['catalog_endpoint_used'] = 'fallback:saved_capture_2026-09-29'

res['supply_sources']['catalog_size'] = len(prods)
res['supply_sources']['captured_at'] = datetime.now(timezone.utc).isoformat()

# ============ 3. SUPPLIER FINGERPRINT CENSUS ============
# ID prefixes are supplier-integration fingerprints:
#   ps_*  = ProdSeller marketplace product IDs (direct fingerprint)
#   mr_*  = manually-added / secondary source
#   dummy = test
prefixes = Counter()
prefix_examples = defaultdict(list)
for p in prods:
    pid = p.get('id', '')
    pre = pid.split('_')[0] if '_' in pid else ('dummy' if 'dummy' in pid else 'other')
    prefixes[pre] += 1
    if len(prefix_examples[pre]) < 5:
        prefix_examples[pre].append({'id': pid, 'name': p.get('name','')[:70]})
res['supply_sources']['id_prefix_census'] = dict(prefixes.most_common())
res['supply_sources']['id_prefix_examples'] = {k: v for k, v in prefix_examples.items()}

# ============ 4. MARGIN / PRICING STRUCTURE (cost = what they PAY supplier) ============
margins = []
fam_margin = defaultdict(list)
for p in prods:
    cost, price = p.get('costPrice'), p.get('price')
    if cost is not None and price not in (None, 0) and isinstance(cost, (int, float)) and cost > 0:
        m = (price - cost) / cost * 100
        margins.append(m)
        fam_margin[p.get('categoryName', '?')].append(m)
res['supply_sources']['cost_price_visibility'] = {
    'n_with_cost': len(margins),
    'note': 'costPrice = supplier purchase cost, exposed on public API'}
if margins:
    res['supply_sources']['margin_stats_pct'] = {
        'mean': round(statistics.mean(margins), 1),
        'median': round(statistics.median(margins), 1),
        'min': round(min(margins), 1), 'max': round(max(margins), 1)}
res['supply_sources']['margin_by_category_pct'] = {
    k: {'mean': round(statistics.mean(v), 1), 'n': len(v)}
    for k, v in sorted(fam_margin.items(), key=lambda x: -len(x[1]))}

# ============ 5. EXTERNAL SUPPLIER DOMAINS MINED FROM DESCRIPTIONS ============
SUPPLIER_DOMAIN_PATTERNS = [
    (r'(https?://(?:[a-z0-9-]+\.)*teamsoclo\.site[^\s"\']*)', 'teamsoclo.site'),
    (r'(https?://(?:[a-z0-9-]+\.)*(?:2fa\.live|viotp\.com|smspool\.net|5sim\.(?:net|biz)|sms-activate\.[a-z]+|smstools\.[a-z]+|tiger-sms\.[a-z]+)[^\s"\']*)', 'OTP/SMS provider'),
    (r'(https?://(?:[a-z0-9-]+\.)*(?:drive\.google\.com|docs\.google\.com|sheets\.co|notion\.so|t\.me|telegram\.me)[^\s"\']*)', 'ops link'),
    (r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?)\b', 'raw IP endpoint'),
    (r'(https?://(?:[a-z0-9-]+\.)*(?:prodseller\.com|prodseller\.io)[^\s"\']*)', 'ProdSeller direct'),
    (r'(https?://(?:[a-z0-9-]+\.)*(?:enot\.io|cryptomus\.com|payop\.com|coinpayments\.net|mercadopago|payment)[^\s"\']*)', 'payment'),
]
domain_hits = defaultdict(list)
for p in prods:
    desc = p.get('description') or ''
    for pat, label in SUPPLIER_DOMAIN_PATTERNS:
        for m in re.finditer(pat, desc, re.I):
            domain_hits[label].append({'product': p.get('name','')[:60], 'hit': m.group(1)[:160]})
res['supply_sources']['external_signals_in_descriptions'] = {
    k: {'count': len(v), 'samples': v[:4]} for k, v in sorted(domain_hits.items(), key=lambda x: -len(x[1]))}

# ============ 6. PRODUCT FAMILY → SUPPLIER MAPPING ============
fam_counts = Counter(p.get('categoryName','?') for p in prods)
res['supply_sources']['catalog_families'] = dict(fam_counts.most_common())

# AI credits products => teamsoclo.site family fingerprint
ai_kw = ('chatgpt','claude','gemini','grok','cursor','openai','perplexity','midjourney','quillbot','grammarly',
         'canva','capcut','freepik','scribd','turnitin','deepl','adobe','figma','notion','perplex')
ai_items = [p for p in prods if any(k in (p.get('name','')+ (p.get('description') or '')).lower() for k in ai_kw)]
res['supply_sources']['ai_saas_family'] = {
    'n_products': len(ai_items),
    'sample': [p['name'][:60] for p in ai_items[:10]]}

# ============ 7. CROSS-MATCH vs ProdSeller channel capture (27/09) ============
try:
    prefill = json.load(open('/home/z/my-project/research/b3_prefill_strict.json'))
    res['cross_match_prodseller'] = {
        'matched_families': len(prefill.get('sv_matches', [])),
        'note': 'strict SKU identity matches vs ProdSeller channel listings 2026-09-27'}
except Exception as e:
    res['cross_match_prodseller'] = {'error': str(e)[:80]}

# stock provenance: stock values hint at reseller auto-stock sync
stock_vals = [p.get('stock') for p in prods if isinstance(p.get('stock'), (int, float))]
res['supply_sources']['stock_sync_hint'] = {
    'n': len(stock_vals),
    'distinct_values_top': dict(Counter(stock_vals).most_common(6)),
    'note': '999/dummy = test; small ints = synced reseller stock'}

json.dump(res, open(f'{OUT}/supply_sources_precise.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:5500])
