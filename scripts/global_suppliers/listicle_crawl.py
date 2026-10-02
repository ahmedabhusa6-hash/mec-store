#!/usr/bin/env python3
# GDS-3: Listicle/blog crawl — quota-free discovery channel.
# B2B content-marketing articles ("X best topup platforms", "top gift card API
# providers", competitor roundups) mention dozens of supplier domains. This
# crawler walks sitemaps + /blog of qualified entities and discovery sources,
# fetches listicle-style articles, and harvests external supplier domains.
# Chunk-safe: incremental progress + merge into harvest.json on each save.
import json, os, re, sys, time, concurrent.futures, threading
import requests
import urllib3
urllib3.disable_warnings()
from urllib.parse import urlparse
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.0'
PROG = f'{GS}/candidates/listicle_progress.json'
sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals, SKIP_HOSTS
from qualify import root_domain

SITEMAP_PATHS = ['/sitemap.xml', '/sitemap-index.xml', '/sitemap_index.xml',
                 '/blog/sitemap.xml', '/wp-sitemap.xml', '/blog']
LISTICLE_RE = re.compile(r'(best|top[-_ ]?\d*|leading|\d+[-_ ][a-z]+|vs|versus|alternatives|competitors|comparison|providers|platforms|companies|distributors|resellers|aggregators|wholesalers|partners|integrations)', re.I)
ARTICLE_CAP = 25          # max articles per source domain
JUNK_EXT = ('.png','.jpg','.jpeg','.gif','.svg','.css','.js','.ico','.woff','.pdf','.zip','.mp4','.webp','.xml')

def curl(url, timeout=10):
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xml,*/*'},
                         timeout=(4, timeout), allow_redirects=True, verify=False)
        if r.status_code == 200:
            return (r.text or '')[:500000]
    except Exception:
        pass
    return ''

def sitemap_urls(dom):
    """Yield candidate article URLs from sitemaps (recurses one level into sitemap indexes)."""
    urls = set()
    for path in SITEMAP_PATHS:
        xml = curl(f'https://{dom}{path}', 10)
        if not xml:
            continue
        locs = re.findall(r'<loc>\s*(https?://[^<\s]+)\s*</loc>', xml, re.I)
        if not locs:
            continue
        # sitemap index -> recurse into first 3 child sitemaps
        if '</sitemapindex>' in xml.lower():
            kids = [l for l in locs if l.lower().endswith('.xml') or 'sitemap' in l.lower()][:3]
            for k in kids:
                sub = curl(k, 12)
                if sub:
                    urls |= {l for l in re.findall(r'<loc>\s*(https?://[^<\s]+)\s*</loc>', sub, re.I)
                             if not l.lower().endswith(JUNK_EXT)}
        else:
            urls |= {l for l in locs if not l.lower().endswith(JUNK_EXT)}
        if len(urls) > 400:
            break
    return urls

def pick_articles(dom, urls):
    """Keep listicle-looking URLs on this domain, capped."""
    onsite, scored = [], []
    for u in urls:
        try:
            p = urlparse(u)
        except Exception:
            continue
        h = (p.hostname or '').lower().replace('www.', '')
        if root_domain(h) != root_domain(dom):
            continue
        if p.path in ('/', '', '/blog') or p.path.endswith(JUNK_EXT):
            continue
        if any(seg in p.path.lower() for seg in ('/tag/', '/category/', '/author/', '/page/', 'feed')):
            continue
        hits = len(LISTICLE_RE.findall(p.path))
        if hits:
            scored.append((hits, u))
    scored.sort(key=lambda t: -t[0])
    return [u for _, u in scored[:ARTICLE_CAP]]

def extract_links(html):
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href=["\'](https?://[^"\'#?]+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        url, anchor = m.group(1), re.sub(r'<[^>]+>|\s+', ' ', m.group(2)).strip()
        if url.lower().endswith(JUNK_EXT):
            continue
        try:
            host = (urlparse(url).hostname or '').lower().replace('www.', '')
        except Exception:
            continue
        if not host or host in seen:
            continue
        seen.add(host)
        out.append((host, anchor[:120], url))
    return out

def load_existing_hosts():
    doms = set()
    try:
        for e in json.load(open(f'{GS}/entities/qualified.json')):
            doms.add(root_domain(e['Official_Domain']))
        for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']:
            doms.add(root_domain(c['domain']))
        for h in json.load(open(f'{GS}/candidates/harvest.json'))['domains']:
            doms.add(root_domain(h['host']))
    except Exception:
        pass
    return doms

def main():
    # sources: discovery sources + qualified entities (+ their blogs)
    sources = set()
    cands = json.load(open(f'{GS}/candidates/candidates.json'))
    for ds in cands.get('discovery_sources', []):
        sources.add(root_domain(ds['host']))
    for e in json.load(open(f'{GS}/entities/qualified.json')):
        sources.add(root_domain(e['Official_Domain']))
    sources = sorted(s for s in sources if s and '.' in s)
    print(f'Listicle sources: {len(sources)} domains')

    try:
        prog = json.load(open(PROG))
        done_sources, new_hosts = set(prog['done_sources']), prog.get('new_hosts', {})
    except Exception:
        done_sources, new_hosts = set(), {}
    todo = [s for s in sources if s not in done_sources]
    print(f'resume: {len(done_sources)} done, {len(todo)} to crawl')
    lock = threading.Lock()
    existing = load_existing_hosts()

    def work(src):
        try:
            urls = sitemap_urls(src)
            arts = pick_articles(src, urls)
            found = {}
            for a in arts:
                html = curl(a, 12)
                if not html:
                    continue
                title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
                title = re.sub(r'\s+', ' ', title_m.group(1)).strip() if title_m else ''
                for h, anchor, href in extract_links(html):
                    rd = root_domain(h)
                    if h in SKIP_HOSTS or rd in {root_domain(s) for s in SKIP_HOSTS}:
                        continue
                    if rd == root_domain(src) or rd in existing:
                        continue
                    b2b, cats = find_signals(f'{title} {anchor}')
                    rec = found.setdefault(h, {'host': h, 'anchor': anchor[:100], 'source': a,
                                               'ctx': f'listicle:{src}', 'corroboration': 1,
                                               'b2b': set(), 'cats': set()})
                    rec['b2b'] |= b2b; rec['cats'] |= cats
                    if anchor and anchor != rec['anchor']:
                        rec['corroboration'] += 1
            return src, len(arts), found
        except Exception:
            return src, 0, {}

    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for src, n_arts, found in ex.map(work, todo):
            with lock:
                n += 1
                done_sources.add(src)
                for h, rec in found.items():
                    if h in new_hosts:
                        new_hosts[h]['corroboration'] += 1
                    else:
                        new_hosts[h] = {'host': h, 'anchor': rec['anchor'], 'source': rec['source'],
                                        'ctx': rec['ctx'], 'corroboration': rec['corroboration']}
                if n % 5 == 0 or n == len(todo):
                    print(f'  {n}/{len(todo)} sources | articles crawled so far | new hosts: {len(new_hosts)}')
                    json.dump({'done_sources': sorted(done_sources), 'new_hosts': new_hosts},
                              open(PROG, 'w'), ensure_ascii=False)
                    # incremental merge into harvest.json so later pipeline steps see them
                    try:
                        hv = json.load(open(f'{GS}/candidates/harvest.json'))
                        merged = {p['host']: p for p in hv['domains']}
                        added = 0
                        for h, rec in new_hosts.items():
                            if h not in merged:
                                merged[h] = {**rec, 'sources': [rec.get('source', '')][:6],
                                             'origin': 'listicle_crawl'}
                                added += 1
                        hv['domains'] = sorted(merged.values(),
                                               key=lambda r: (-r.get('corroboration', 1), r['host']))
                        json.dump(hv, open(f'{GS}/candidates/harvest.json', 'w'), ensure_ascii=False, indent=1)
                    except Exception as e:
                        print('  merge err:', e)
    print(f'\nLISTICLE CRAWL DONE: {len(new_hosts)} new hosts total')
    for h, r in sorted(new_hosts.items(), key=lambda kv: -kv[1]['corroboration'])[:40]:
        print(f"  {h[:42]:44} corr={r['corroboration']} {r['anchor'][:50]}")

if __name__ == '__main__':
    main()
