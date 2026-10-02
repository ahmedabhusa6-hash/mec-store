#!/usr/bin/env python3
# GDS-2: Deep verify — for alive candidates lacking signals, probe internal pages
# (/about /products /api /pricing ...) to rescue SPA/homepage-silent suppliers. Quota-free.
import json, os, re, sys, concurrent.futures
import requests
import urllib3
urllib3.disable_warnings()
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals
from qualify import root_domain

SUB_PATHS = ['/about', '/about-us', '/company', '/products', '/services', '/pricing',
             '/api', '/api-docs', '/docs', '/developers', '/features', '/solutions',
             '/reseller', '/partners', '/wholesale', '/b2b', '/en', '/en/about']

def curl(url, timeout=9):
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'},
                         timeout=(4, timeout), allow_redirects=True, verify=False)
        if r.status_code == 200:
            return r.text or ''
    except Exception: pass
    return ''

def extract(html):
    title = ''
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
    if m: title = re.sub(r'\s+', ' ', m.group(1)).strip()[:150]
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html[:300000], flags=re.S|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return title, text[:9000]

def deep_probe(task):
    dom, existing = task
    found_b2b, found_cats, best_title = set(), set(), ''
    for path in SUB_PATHS:
        html = curl(f'https://{dom}{path}')
        if not html: continue
        title, text = extract(html)
        b2b, cats = find_signals(f'{title} {text[:7000]}')
        if b2b or cats:
            found_b2b |= b2b; found_cats |= cats
            if title and not best_title: best_title = title
        if found_b2b and found_cats:
            break  # enough — both signals found
    return dom, sorted(found_b2b), sorted(found_cats), best_title

def main():
    cands = {c['domain']: c for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']}
    verified = {v['domain']: v for v in json.load(open(f'{GS}/candidates/verified_pages.json'))}
    # targets: alive (200) but missing either signal; skip already-strong
    targets = []
    for dom, v in verified.items():
        if v.get('http') != 200: continue
        has_b2b = bool(v.get('page_b2b_signals')) or bool(cands.get(dom, {}).get('b2b_signals'))
        has_cat = bool(v.get('page_cat_signals')) or bool(cands.get(dom, {}).get('category_signals'))
        if has_b2b and has_cat: continue
        # rescue candidates: missing something on homepage
        targets.append((dom, v))
    # prioritize: missing only one of the two (closer to qualification)
    targets.sort(key=lambda t: (bool((t[1].get('page_b2b_signals') or cands.get(t[0],{}).get('b2b_signals'))) + bool((t[1].get('page_cat_signals') or cands.get(t[0],{}).get('category_signals'))), t[0]))
    print(f'Deep-verify targets: {len(targets)} alive pages missing signals')
    PROG = f'{GS}/candidates/deep_verify_progress.json'
    try:
        prog = json.load(open(PROG)); done = set(prog['done']); merged = prog['merged']
    except Exception:
        done, merged = set(), {}
    targets = [(d, v) for d, v in targets if d not in done]
    print(f'after resume-skip: {len(targets)}')

    def work(t): return deep_probe(t)
    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for dom, b2b, cats, title in ex.map(work, targets):
            n += 1; done.add(dom)
            if b2b or cats:
                merged[dom] = {'deep_b2b': b2b, 'deep_cats': cats, 'deep_title': title}
                v = verified.get(dom, {})
                v['page_b2b_signals'] = sorted(set(v.get('page_b2b_signals', [])) | set(b2b))
                v['page_cat_signals'] = sorted(set(v.get('page_cat_signals', [])) | set(cats))
                if not v.get('page_title') and title: v['page_title'] = title
                v['deep_verified_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
            if n % 25 == 0:
                print(f'  {n}/{len(targets)} | rescued so far: {len(merged)}')
                json.dump({'done': sorted(done), 'merged': merged}, open(PROG,'w'))
                json.dump(list(verified.values()), open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
    json.dump({'done': sorted(done), 'merged': merged}, open(PROG,'w'))
    json.dump(list(verified.values()), open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
    print(f'\nDEEP VERIFY DONE: rescued {len(merged)} domains with new signals')

if __name__ == '__main__':
    main()
