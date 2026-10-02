#!/usr/bin/env python3
# GDS-1: Harvest v2 — quota-free discovery via list-articles, sitemaps, entity link-graph
# List articles: accept ALL external domains (verify.py provides per-domain evidence)
# Entity pages/sitemaps: follow partner/integration/reseller paths
import json, os, re, sys, concurrent.futures, time
import requests
import urllib3
urllib3.disable_warnings()
from urllib.parse import urlparse
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals, SKIP_HOSTS
from qualify import root_domain, JUNK, TECH_PREFIXES

LISTICLE_RE = re.compile(r'(\d+\s+(best|top|leading|popular)|best\s+\d+|top\s+\d+|best\s+\w+\s+(api|platforms?|providers?|companies|sites|alternatives)|(api|platform|provider|company|site)\s+alternatives|vs\s+)', re.I)
PARTNER_PATH_RE = re.compile(r'/(partners?|integrations?|developers?|resellers?|distributors?|wholesale|api-docs?|docs?/api|api)(/|$|\.)', re.I)

def curl_page(url, timeout=10):
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=(4, timeout), allow_redirects=True, verify=False)
        return (r.text or '')[:400000]
    except Exception:
        return ''

def extract_links(html):
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href=["\'](https?://[^"\'#?]+)["\'][^>]*>(.*?)</a>', html, re.I|re.S):
        url, anchor = m.group(1), re.sub(r'<[^>]+>|\s+', ' ', m.group(2)).strip()
        try: host = (urlparse(url).hostname or '').lower().replace('www.','')
        except: continue
        if not host or host in seen: continue
        seen.add(host)
        out.append((host, anchor[:120], url))
    return out

def load_existing():
    doms = set()
    try:
        for e in json.load(open(f'{GS}/entities/qualified.json')):
            doms.add(root_domain(e['Official_Domain']))
    except Exception: pass
    try:
        for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']:
            doms.add(root_domain(c['domain']))
    except Exception: pass
    K = json.load(open(f'{GS}/known_entities.json'))
    for r in K['entities']:
        if r['domain']: doms.add(root_domain(r['domain']))
    return doms

def main():
    existing = load_existing()

    # --- 1. collect listicle URLs from ALL raw search results (loose pattern) ---
    listicles = []
    rawdir = f'{GS}/raw'
    for rf in sorted(os.listdir(rawdir)):
        if not rf.endswith('.json'): continue
        d = json.load(open(f'{rawdir}/{rf}'))
        for r in d.get('results', []):
            host = r.get('host') or ''
            if not host or host in SKIP_HOSTS: continue
            if LISTICLE_RE.search((r.get('name','') or '')):
                u = r.get('url','')
                if u.startswith('http') and host not in [l[0] for l in listicles]:
                    listicles.append((host, u, (r.get('name') or '')[:80]))
    print(f"Listicle sources from raw results: {len(listicles)}")

    # --- 2. qualified entity domains: homepage + sitemap + common partner pages ---
    try: ents = [e['Official_Domain'] for e in json.load(open(f'{GS}/entities/qualified.json'))]
    except Exception: ents = []
    ent_sources = []
    for d in ents:
        ent_sources.append((d, f'https://{d}/', 'homepage'))
        ent_sources.append((d, f'https://{d}/sitemap.xml', 'sitemap'))

    # --- crawl listicles (accept ALL external domains) ---
    found = {}
    def crawl_listicle(item):
        host, url, title = item
        html = curl_page(url, 15)
        if not html: return []
        local = []
        for h, anchor, href in extract_links(html):
            if h in SKIP_HOSTS or root_domain(h) in {root_domain(s) for s in SKIP_HOSTS}: continue
            if h in JUNK or root_domain(h) in {root_domain(j) for j in JUNK}: continue
            if root_domain(h) in existing or root_domain(h) == root_domain(host): continue
            local.append({'host': h, 'anchor': anchor, 'source': url, 'ctx': f'listicle: {title}'})
        return local

    print(f"Crawling {len(listicles)} listicles...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for i, res in enumerate(ex.map(crawl_listicle, listicles)):
            for r in res:
                h = r['host']
                if h in found: found[h]['corroboration'] += 1; found[h]['sources'].append(r['source'])
                else: found[h] = {**r, 'corroboration': 1, 'sources': [r['source']], 'origin': 'listicle'}
            if (i+1) % 8 == 0: print(f'  {i+1}/{len(listicles)} | new domains: {len(found)}')

    # --- crawl entity pages/sitemaps (signal-in-anchor OR partner-path links) ---
    print(f"Crawling {len(ent_sources)} entity pages/sitemaps...")
    def crawl_entity(item):
        dom, url, kind = item
        html = curl_page(url, 12)
        if not html: return []
        local = []
        if kind == 'sitemap':
            locs = re.findall(r'<loc>(.*?)</loc>', html)
            pages = [l for l in locs if PARTNER_PATH_RE.search(l)][:5]
            for p in pages:
                sub = curl_page(p, 10)
                for h, anchor, href in extract_links(sub or ''):
                    b2b, cats = find_signals(f'{anchor} {h}')
                    if root_domain(h) in existing or root_domain(h) == dom: continue
                    if h in SKIP_HOSTS or h in JUNK: continue
                    if b2b and cats:
                        local.append({'host': h, 'anchor': anchor, 'source': p, 'ctx': f'entity partner page: {dom}'})
        else:
            for h, anchor, href in extract_links(html):
                b2b, cats = find_signals(f'{anchor} {h}')
                if root_domain(h) in existing or root_domain(h) == dom: continue
                if h in SKIP_HOSTS or h in JUNK: continue
                if (b2b and cats) or PARTNER_PATH_RE.search(href):
                    local.append({'host': h, 'anchor': anchor, 'source': url, 'ctx': f'entity links: {dom}'})
        return local
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for i, res in enumerate(ex.map(crawl_entity, ent_sources)):
            for r in res:
                h = r['host']
                if h in found: found[h]['corroboration'] += 1; found[h]['sources'].append(r['source'])
                else: found[h] = {**r, 'corroboration': 1, 'sources': [r['source']], 'origin': 'entity_links'}
            if (i+1) % 15 == 0: print(f'  {i+1}/{len(ent_sources)} | new domains: {len(found)}')

    harvested = sorted(found.values(), key=lambda r: (-r['corroboration'], r['host']))
    out_f = f'{GS}/candidates/harvest.json'
    try: prev = json.load(open(out_f))['domains']
    except Exception: prev = []
    prev_hosts = {p['host'] for p in prev}
    for p in prev:
        if p['host'] not in found: found.setdefault(p['host'], {**p, 'origin': p.get('origin','prev')})
    json.dump({'generated': datetime.now(timezone.utc).isoformat(timespec='seconds'),
               'n_sources': len(listicles)+len(ent_sources), 'n_new_domains': len(found),
               'domains': sorted(found.values(), key=lambda r: (-r.get('corroboration',1), r['host']))},
              open(out_f,'w'), ensure_ascii=False, indent=1)
    print(f"\nHARVESTED (cumulative): {len(found)} candidate domains -> {out_f}")
    for r in sorted(found.values(), key=lambda x: -x.get('corroboration',1))[:25]:
        print(f"  {r['host'][:40]:42} corr={r.get('corroboration',1)} [{r.get('origin','')[:12]:12}] {r.get('anchor','')[:44]}")

if __name__ == '__main__':
    main()
