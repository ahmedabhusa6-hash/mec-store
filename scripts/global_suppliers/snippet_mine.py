#!/usr/bin/env python3
# GDS-3: Snippet domain mining — quota-free second extraction pass.
# Raw search results' snippets often mention the REAL supplier domain (directory
# pages, articles, forum posts). process.py only kept the result's own host;
# this pass mines every domain-like token inside snippets and adds NEW domains
# as candidates. Qualification still requires official-page verification later.
import json, os, re, sys

GS = '/home/z/my-project/research/global_suppliers'
sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals, SKIP_HOSTS
from qualify import root_domain

TLD_RE = re.compile(
    r'\b((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+'
    r'(?:com|net|org|io|co|ai|app|dev|shop|store|site|online|biz|info|us|uk|de|fr|es|it|nl|eu|'
    r'tr|ru|ua|pl|cz|in|id|my|sg|th|vn|ph|pk|bd|lk|ae|sa|kw|qa|bh|om|jo|eg|ma|dz|tn|ly|sd|ye|iq|'
    r'ke|ng|gh|za|tz|ug|et|br|mx|ar|cl|co|pe|py|ec|ve|ca|au|nz|jp|kr|cn|hk|tw|kz|uz|ge|am|az|ro|bg|gr|hu|se|no|fi|dk|at|ch|be|pt|il|ir))\b',
    re.I)

JUNK_TOKENS = re.compile(r'(example|domain|website|yoursite|sitename|company|yourdomain|sample|test|localhost|email|\.png|\.jpg|\.jpeg|\.gif|\.svg|\.css|\.js|\.pdf|\.zip|w3\.org|schema\.org|google\.com|facebook\.com|youtube\.com|twitter\.com|x\.com|linkedin\.com|instagram\.com|tiktok\.com|wikipedia\.org|amazon\.|apple\.com|microsoft\.com|play\.google|apps\.apple|support\.google|accounts\.google|policies\.google|maps\.google|plus\.google|t\.me|telegram|whatsapp|medium\.com|reddit\.com|quora\.com|pinterest|github\.com|gitlab\.com|stackoverflow|wordpress\.org|wordpress\.com|blogspot|gstatic|googleapis|googleusercontent|cloudflare|facebook|instagram|amzn\.|youtu\.be|bit\.ly|tinyurl|ow\.ly|goo\.gl|cutt\.ly|is\.gd|shorturl)', re.I)


def host_of(url):
    m = re.search(r'https?://([^/\s"#\']+)', url or '', re.I)
    h = (m.group(1) if m else '').lower().split(':')[0]
    return h[4:] if h.startswith('www.') else h


def main():
    # existing universe
    existing = set()
    try:
        for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']:
            existing.add(c['domain']); existing.add(root_domain(c['domain']))
    except Exception:
        pass
    K = json.load(open(f'{GS}/known_entities.json'))
    for r in K['entities']:
        if r.get('domain'):
            existing.add(r['domain']); existing.add(root_domain(r['domain']))
    skip_roots = {root_domain(s) for s in SKIP_HOSTS}

    mined = {}   # domain -> {names, b2b, cats, evidence}
    raws = sorted(f for f in os.listdir(f'{GS}/raw') if f.endswith('.json'))
    for rf in raws:
        d = json.load(open(f'{GS}/raw/{rf}'))
        for r in d.get('results', []):
            own_host = r.get('host') or host_of(r.get('url', ''))
            blob = f"{r.get('name','')} {r.get('snippet','')}"
            for m in TLD_RE.finditer(blob):
                dom = m.group(1).lower()
                if dom == own_host or root_domain(dom) == root_domain(own_host or 'x.invalid'):
                    continue
                if dom in existing or root_domain(dom) in existing:
                    continue
                if dom in SKIP_HOSTS or root_domain(dom) in skip_roots:
                    continue
                if JUNK_TOKENS.search(dom):
                    continue
                b2b, cats = find_signals(blob)
                rec = mined.setdefault(dom, {'names': set(), 'b2b': set(), 'cats': set(), 'ev': []})
                rec['names'].add(re.sub(r'\s+', ' ', r.get('name', ''))[:60])
                rec['b2b'] |= b2b; rec['cats'] |= cats
                rec['ev'].append({'query': d.get('query', ''), 'url': r.get('url', '')[:180],
                                  'title': r.get('name', '')[:100], 'snippet': (r.get('snippet', '') or '')[:220]})

    # keep only domains mentioned with some supplier-ish context (b2b or cats) OR mentioned 2+ times
    out = []
    for dom, rec in mined.items():
        if rec['b2b'] or rec['cats'] or len(rec['ev']) >= 2:
            out.append({
                'domain': dom,
                'names': sorted(n for n in rec['names'] if n)[:3],
                'b2b_signals': sorted(rec['b2b']),
                'category_signals': sorted(rec['cats']),
                'n_evidence': len(rec['ev']),
                'n_official_evidence': 0,
                'corroboration_queries': len({e['query'] for e in rec['ev']}),
                'regions_seen': [],
                'evidence': rec['ev'][:5],
                'source': 'snippet_mining',
            })
    out.sort(key=lambda c: (-len(c['b2b_signals']) - len(c['category_signals']), -c['n_evidence']))
    json.dump(out, open(f'{GS}/candidates/snippet_mined.json', 'w'), ensure_ascii=False, indent=1)
    print(f'SNIPPET MINING: {len(out)} new domains mined from {len(raws)} raw files')
    for c in out[:40]:
        print(f"  {c['domain'][:40]:42} b2b={','.join(c['b2b_signals'])[:26]:28} cats={','.join(c['category_signals'])[:30]:32} ev={c['n_evidence']}")


if __name__ == '__main__':
    main()
