#!/usr/bin/env python3
# StackVault passive OSINT capture — normal browser-like GET requests ONLY.
# No scanning, no fuzzing, no auth bypass, no exploitation. Public pages only.
import json, re, time
import requests
import urllib3
urllib3.disable_warnings()
from datetime import datetime, timezone

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.0'
OUT = '/home/z/my-project/research/stackvault_live'
import os
os.makedirs(OUT, exist_ok=True)

SEC_HEADERS = ['strict-transport-security','content-security-policy','x-frame-options',
               'x-content-type-options','referrer-policy','permissions-policy',
               'x-xss-protection','cross-origin-opener-policy','cross-origin-resource-policy']

def get(url, timeout=15):
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/json,*/*'},
                         timeout=(5, timeout), allow_redirects=True, verify=False)
        return {'url': url, 'status': r.status_code, 'final_url': r.url,
                'headers': dict(r.headers), 'body': (r.text or '')[:300000], 'cookies': [
                    {'name': c.name, 'secure': c.has_nonstandard_attr('secure') if hasattr(c,'has_nonstandard_attr') else False,
                     'httponly': c.has_nonstandard_attr('httponly') if hasattr(c,'has_nonstandard_attr') else False}
                    for c in r.cookies]}
    except Exception as e:
        return {'url': url, 'status': 0, 'error': str(e)[:200]}

def analyze_headers(h):
    hl = {k.lower(): v for k, v in h.items()}
    sec = {k: hl.get(k, 'MISSING') for k in SEC_HEADERS}
    tech = {}
    if 'server' in hl: tech['server'] = hl['server']
    if 'x-powered-by' in hl: tech['x-powered-by'] = hl['x-powered-by']
    if 'via' in hl: tech['via'] = hl['via']
    if 'cf-ray' in hl or 'cloudflare' in str(hl.get('server','')).lower(): tech['cdn'] = 'Cloudflare'
    return sec, tech

def extract_tech(html):
    tech = set()
    m = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if m: tech.add(f'generator:{m.group(1)}')
    for s in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.I):
        if 'next' in s.lower(): tech.add('Next.js')
        if 'nuxt' in s.lower(): tech.add('Nuxt')
        if 'react' in s.lower(): tech.add('React')
        if 'vue' in s.lower(): tech.add('Vue')
        if '_next/static' in s: tech.add('Next.js(static)')
        if 'svelte' in s.lower(): tech.add('Svelte')
    if re.search(r'__NEXT_DATA__', html): tech.add('Next.js(__NEXT_DATA__)')
    if re.search(r'wp-content|wp-includes', html): tech.add('WordPress')
    if re.search(r'shopify', html, re.I): tech.add('Shopify')
    if re.search(r'wix\.com|wixstatic', html, re.I): tech.add('Wix')
    return sorted(tech)

def extract_api_hints(html, base):
    eps = set()
    for m in re.finditer(r'["\'](/{0,2}(?:api|sv-api|backend)[^"\']{2,120})["\']', html):
        eps.add(m.group(1))
    for m in re.finditer(r'https?://([a-z0-9.-]+\.[a-z]{2,})(/[a-z0-9/_-]{2,60})?', html[:200000], re.I):
        host = m.group(1).lower()
        if any(x in host for x in ('stackvault','decohomz','google','facebook','cloudflare','jsdelivr','unpkg','github','schema.org','w3.org','fonts','gstatic')):
            continue
        eps.add(f'{host}{m.group(2) or ""}')
    return sorted(eps)[:40]

report = {'captured_at': datetime.now(timezone.utc).isoformat(), 'pages': {}, 'security': {}, 'tech': {}, 'notes': []}

# 1. homepage
hp = get('https://stackvault.shop/')
report['pages']['homepage'] = {'status': hp['status'], 'final_url': hp.get('final_url')}
if hp['status']:
    sec, srv_tech = analyze_headers(hp['headers'])
    report['security']['homepage_headers'] = sec
    report['tech']['server'] = srv_tech
    report['tech']['frontend'] = extract_tech(hp['body'])
    report['tech']['api_hints'] = extract_api_hints(hp['body'], 'stackvault.shop')
    report['security']['homepage_cookies'] = hp.get('cookies', [])
    open(f'{OUT}/homepage.html','w').write(hp['body'])
    t = re.search(r'<title[^>]*>(.*?)</title>', hp['body'], re.S|re.I)
    if t: report['pages']['homepage']['title'] = re.sub(r'\s+',' ',t.group(1)).strip()[:120]
    # meta description
    md = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', hp['body'], re.I)
    if md: report['pages']['homepage']['description'] = md.group(1)[:250]
    # save headers
    json.dump(dict(hp['headers']), open(f'{OUT}/homepage_headers.json','w'), indent=1)

# 2. robots.txt + sitemap
for u in ['https://stackvault.shop/robots.txt', 'https://stackvault.shop/sitemap.xml']:
    r = get(u, 10)
    report['pages'][u.split('shop/')[1]] = {'status': r['status'], 'body_head': (r.get('body','') or '')[:800]}
    if r['status'] == 200 and 'Disallow:' in (r.get('body') or ''):
        report['notes'].append(f'robots.txt disallow entries found: ' + '; '.join(
            re.findall(r'Disallow:\s*(\S+)', r['body']))[:300])

# 3. my_orders page (public observation only — no login attempt)
r = get('https://stackvault.shop/my_orders', 12)
report['pages']['my_orders'] = {'status': r['status'], 'final_url': r.get('final_url'),
                                 'redirected_to_login': 'login' in str(r.get('final_url','')).lower()}
if r['status']:
    sec, _ = analyze_headers(r['headers'])
    report['security']['my_orders_headers'] = sec

# 4. known public products API (backend host observed 2026-09-27)
api = get('https://decohomz.com/sv-api/products', 20)
report['pages']['backend_api'] = {'status': api['status'], 'final_url': api.get('final_url')}
try:
    if api['status'] == 200:
        d = api['json'] if 'json' in api else json.loads(api['body'])
        prods = d if isinstance(d, list) else d.get('products', [])
        report['pages']['backend_api']['n_products'] = len(prods)
        json.dump(d, open(f'{OUT}/sv_products_current.json','w'), ensure_ascii=False)
        from collections import Counter
        cats = Counter(p.get('categoryName','?') for p in prods)
        report['pages']['backend_api']['categories'] = dict(cats.most_common())
        idp = Counter(p['id'].split('_')[0] if '_' in p['id'] else 'other' for p in prods)
        report['pages']['backend_api']['id_prefixes'] = dict(idp.most_common(6))
        # cost exposure check (no auth was required -> public data exposure finding)
        n_cost = sum(1 for p in prods if p.get('costPrice') is not None)
        report['security']['cost_price_exposed_publicly'] = {'n_products_with_cost': n_cost, 'total': len(prods)}
except Exception as e:
    report['pages']['backend_api']['parse'] = f'non-json or error: {str(e)[:100]}'
if api['status']:
    sec, srv = analyze_headers(api['headers'])
    report['security']['backend_api_headers'] = sec
    report['tech']['backend_server'] = srv
    json.dump(dict(api['headers']), open(f'{OUT}/api_headers.json','w'), indent=1)

# 5. also try the api on stackvault.shop itself (maybe same API path)
r2 = get('https://stackvault.shop/sv-api/products', 15)
report['pages']['sv_api_on_shop'] = {'status': r2['status']}
if r2['status'] == 200:
    try:
        d = json.loads(r2['body'])
        prods = d if isinstance(d, list) else d.get('products', [])
        report['pages']['sv_api_on_shop']['n_products'] = len(prods)
    except Exception:
        pass

json.dump(report, open(f'{OUT}/capture_report.json','w'), ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
