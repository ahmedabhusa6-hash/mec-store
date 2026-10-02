#!/usr/bin/env python3
# GDS-2: Mine existing project research files for supplier domains not yet in the GDS pipeline.
# Quota-free: extracts every domain-looking token from prior intelligence files.
import json, os, re, sys
from urllib.parse import urlparse

sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals, SKIP_HOSTS
from qualify import root_domain, JUNK

GS = '/home/z/my-project/research/global_suppliers'
R = '/home/z/my-project/research'
NOTION = '/home/z/my-project/notion_raw'

DOMAIN_RE = re.compile(r'\b((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:com|net|org|io|co|app|dev|me|tv|gg|xyz|shop|store|site|online|biz|info|pro|cloud|digital|games|gaming|tech|link|space|world|zone|card|cards|gift|topup|top|life|live|one|now|new|best|fast|pay|pay[0-9]?|wallet|pin|pins|key|keys|code|codes|voucher|credits?|recharge|reload|gamer|play|win|gold|vip|express|market|trade|buy|sell|shop|store|sa|ae|eg|tr|id|in|pk|bd|vn|th|ph|my|sg|jp|kr|cn|tw|hk|ng|gh|ke|tz|ug|za|et|ma|dz|tn|br|mx|ar|co|cl|pe|ec|pl|ro|bg|cz|ua|ru|kz|uz|kg|az|ge|am|by|md|de|fr|es|it|nl|se|uk|au|ca))\b', re.I)

def load_domains(path):
    doms = set()
    try:
        raw = open(path, encoding='utf-8', errors='ignore').read()
        for m in DOMAIN_RE.finditer(raw):
            d = m.group(1).lower()
            if len(d) > 5: doms.add(d)
    except Exception: pass
    return doms

def main():
    # existing universe
    have = set()
    for e in json.load(open(f'{GS}/entities/qualified.json')):
        have.add(root_domain(e['Official_Domain']))
    try:
        for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']:
            have.add(root_domain(c['domain']))
    except Exception: pass
    for r in json.load(open(f'{GS}/known_entities.json'))['entities']:
        if r.get('domain'): have.add(root_domain(r['domain']))
    try:
        for h in json.load(open(f'{GS}/candidates/harvest.json'))['domains']:
            have.add(root_domain(h['host']))
    except Exception: pass
    qc = set(json.load(open(f'{GS}/entities/qc_rejects.json')).keys())
    qc_roots = {root_domain(q) for q in qc}

    # scan files
    files = []
    for name in os.listdir(R):
        p = os.path.join(R, name)
        if os.path.isfile(p) and name.endswith(('.json','.md')):
            files.append(p)
    for sub in ('mec5','deep_dive','pages','live_capture','prodseller_live','actions','audit'):
        d = os.path.join(R, sub)
        if os.path.isdir(d):
            for name in os.listdir(d):
                p = os.path.join(d, name)
                if os.path.isfile(p) and name.endswith(('.json','.md')):
                    files.append(p)
    if os.path.isdir(NOTION):
        for root, _, fnames in os.walk(NOTION):
            for name in fnames:
                if name.endswith(('.json','.md','.txt')):
                    files.append(os.path.join(root, name))
    print(f'Scanning {len(files)} research files...')

    found = {}
    for p in files:
        for d in load_domains(p):
            if d in SKIP_HOSTS or root_domain(d) in {root_domain(s) for s in SKIP_HOSTS}: continue
            if d in JUNK or root_domain(d) in {root_domain(j) for j in JUNK}: continue
            rt = root_domain(d)
            if rt in have or rt in qc_roots or rt in qc: continue
            b2b, cats = find_signals(d)
            if b2b and cats:
                found.setdefault(d, {'host': d, 'anchor': '', 'sources': [p], 'ctx': 'project-mining',
                                     'corroboration': 1, 'origin': 'project_mining'})
            else:
                # keep neutral domains too, lower priority (they'll need verification)
                found.setdefault(d, {'host': d, 'anchor': '', 'sources': [p], 'ctx': 'project-mining-neutral',
                                     'corroboration': 1, 'origin': 'project_mining_neutral'})
            found[d]['sources'] = (found[d]['sources'] + [p])[:5]

    # merge into harvest.json
    out_f = f'{GS}/candidates/harvest.json'
    try: prev = json.load(open(out_f))['domains']
    except Exception: prev = []
    merged = {p['host']: p for p in prev}
    new_n = 0
    for h, r in found.items():
        if h not in merged:
            merged[h] = r; new_n += 1
        else:
            merged[h]['corroboration'] = max(merged[h].get('corroboration',1), 1)
    domains = sorted(merged.values(), key=lambda r: (-r.get('corroboration',1), r['host']))
    json.dump({'generated': __import__('datetime').datetime.now().isoformat(timespec='seconds'),
               'n_new_domains': len(domains), 'domains': domains},
              open(out_f,'w'), ensure_ascii=False, indent=1)
    sig = [d for d in found.values() if d['origin']=='project_mining']
    print(f'MINED: +{new_n} new hosts from project research | with-signals: {len(sig)} | cumulative harvest: {len(domains)}')
    for r in sorted(sig, key=lambda x: x['host'])[:40]:
        print(f"  {r['host'][:42]:44} src={os.path.basename(r['sources'][0])[:40]}")

if __name__ == '__main__':
    main()
