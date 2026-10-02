#!/usr/bin/env python3
# GDS-2: Deep partner-path harvest — quota-free link-graph expansion.
# For each qualified + known entity domain, probe common partner/integration/reseller
# pages and harvest external domains (upstream suppliers, integrations, tech partners).
import json, os, re, sys, concurrent.futures
import requests
import urllib3
urllib3.disable_warnings()
from urllib.parse import urlparse
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals, SKIP_HOSTS
from qualify import root_domain, JUNK

PARTNER_PATHS = [
    '/partners', '/partners.html', '/partner', '/integrations', '/integrations.html',
    '/resellers', '/reseller', '/distributors', '/distributor', '/wholesale',
    '/api', '/api-docs', '/developers', '/docs', '/about', '/about-us', '/company',
    '/sitemap.xml', '/become-a-partner', '/partner-program', '/agency', '/agencies',
    '/where-to-buy', '/stores', '/dealers', '/suppliers', '/technology', '/platform',
]
SUPPLIER_HINT_RE = re.compile(r'(powered by|our (partners|suppliers|integrations|distributors)|integration|partner|reseller|distributor|wholesale|supplier|api|platform|fulfillment|gateway|aggregator)', re.I)
JUNK_EXT = ('.png','.jpg','.jpeg','.gif','.svg','.css','.js','.ico','.woff','.pdf','.zip','.mp4','.webp')

def curl_page(url, timeout=10):
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xml,*/*'},
                         timeout=(4, timeout), allow_redirects=True, verify=False)
        if r.status_code == 200:
            return (r.text or '')[:400000], r.url
        return '', url
    except Exception:
        return '', url

def extract_links(html):
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href=["\'](https?://[^"\'#?]+)["\'][^>]*>(.*?)</a>', html, re.I|re.S):
        url, anchor = m.group(1), re.sub(r'<[^>]+>|\s+', ' ', m.group(2)).strip()
        if url.lower().endswith(JUNK_EXT): continue
        try: host = (urlparse(url).hostname or '').lower().replace('www.','')
        except: continue
        if not host or host in seen: continue
        seen.add(host)
        out.append((host, anchor[:120], url))
    return out

def load_existing():
    doms = set()
    for e in json.load(open(f'{GS}/entities/qualified.json')):
        doms.add(root_domain(e['Official_Domain']))
    try:
        for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']:
            doms.add(root_domain(c['domain']))
    except Exception: pass
    K = json.load(open(f'{GS}/known_entities.json'))
    for r in K['entities']:
        if r['domain']: doms.add(root_domain(r['domain']))
    try:
        for h in json.load(open(f'{GS}/candidates/harvest.json'))['domains']:
            doms.add(root_domain(h['host']))
    except Exception: pass
    return doms

def probe_domain(dom):
    """Probe partner paths on one domain; return harvested external links."""
    found = []
    for path in PARTNER_PATHS:
        url = f'https://{dom}{path}'
        html, final = curl_page(url, 9)
        if not html: continue
        # skip soft-404: page title says not found / zero external links
        title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
        title = re.sub(r'\s+',' ', title_m.group(1)).strip().lower() if title_m else ''
        if 'not found' in title or '404' in title or 'page doesn' in title: continue
        for h, anchor, href in extract_links(html):
            if h in SKIP_HOSTS or root_domain(h) in {root_domain(s) for s in SKIP_HOSTS}: continue
            if h in JUNK or root_domain(h) in {root_domain(j) for j in JUNK}: continue
            if root_domain(h) == dom: continue
            b2b, cats = find_signals(f'{anchor} {h}')
            hint = bool(SUPPLIER_HINT_RE.search(anchor))
            if (b2b and cats) or (hint and b2b) or (hint and path in ('/partners','/integrations','/suppliers','/distributors','/where-to-buy','/dealers')):
                found.append({'host': h, 'anchor': anchor, 'source': url, 'ctx': f'deep:{dom}{path}', 'corroboration': 1})
        # small delay per path to be polite
    return found

def main():
    existing = load_existing()
    seeds = set()
    for e in json.load(open(f'{GS}/entities/qualified.json')):
        seeds.add(e['Official_Domain'])
    K = json.load(open(f'{GS}/known_entities.json'))
    for r in K['entities']:
        if r.get('domain'): seeds.add(root_domain(r['domain']))
    # round-2 expansion: all alive verified pages with any B2B signal (dense partner-graph nodes)
    # round-3 expansion (GDS-3): ALL alive pages — marketplaces/directories with generic
    # homepages are link hubs too; resume support (done_seeds) prevents rework.
    try:
        for v in json.load(open(f'{GS}/candidates/verified_pages.json')):
            if v.get('http') in (200, 403, 406):
                d = v['domain']
                if d.count('.') >= 1:
                    seeds.add(root_domain(d))
    except Exception: pass
    seeds = sorted(s for s in seeds if s and '.' in s)
    # resume support
    PROG = f'{GS}/candidates/harvest_deep_progress.json'
    results, done_seeds = {}, set()
    try:
        prog = json.load(open(PROG))
        results = {h: {**r, 'sources': r.get('sources', [])} for h, r in prog['results'].items()}
        done_seeds = set(prog['done_seeds'])
    except Exception: pass
    seeds = [s for s in seeds if s not in done_seeds]
    print(f'Deep harvest: {len(seeds)} seed domains x {len(PARTNER_PATHS)} paths (quota-free; {len(done_seeds)} already done)')

    def work(dom):
        try: return dom, probe_domain(dom)
        except Exception: return dom, []

    n_done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for dom, found in ex.map(work, seeds):
            n_done += 1
            done_seeds.add(dom)
            for r in found:
                h = r['host']
                if h in results:
                    results[h]['corroboration'] += 1; results[h]['sources'].append(r['source'])
                else:
                    results[h] = {**r, 'sources': [r['source']], 'origin': 'deep_partner'}
            if n_done % 10 == 0:
                print(f'  {n_done}/{len(seeds)} | new hosts: {len(results)}')
                json.dump({'done_seeds': sorted(done_seeds), 'results': results}, open(PROG,'w'), ensure_ascii=False)

    # merge into harvest.json (cumulative)
    out_f = f'{GS}/candidates/harvest.json'
    try: prev = json.load(open(out_f))['domains']
    except Exception: prev = []
    merged = {p['host']: p for p in prev}
    new_n = 0
    for h, r in results.items():
        if h in merged:
            merged[h]['corroboration'] = max(merged[h].get('corroboration',1), r['corroboration'])
            merged[h].setdefault('sources', [])
            merged[h]['sources'] = (merged[h]['sources'] + r['sources'])[:6]
        else:
            merged[h] = {**r, 'sources': r['sources'][:6]}
            new_n += 1
    domains = sorted(merged.values(), key=lambda r: (-r.get('corroboration',1), r['host']))
    json.dump({'generated': datetime.now(timezone.utc).isoformat(timespec='seconds'),
               'n_sources': len(seeds), 'n_new_domains': len(domains), 'domains': domains},
              open(out_f,'w'), ensure_ascii=False, indent=1)
    print(f'\nDEEP HARVEST: +{new_n} new hosts (not in harvest.json before) | cumulative harvest: {len(domains)}')
    for r in sorted(results.values(), key=lambda x: -x['corroboration'])[:30]:
        print(f"  {r['host'][:40]:42} corr={r['corroboration']} {r['anchor'][:50]}")

if __name__ == '__main__':
    main()
