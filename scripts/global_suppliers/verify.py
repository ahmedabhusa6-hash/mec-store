#!/usr/bin/env python3
# GDS-1: Verify candidate domains via direct HTTP (requests) — official page evidence, no search quota
# - existence proof (HTTP status)
# - title/description extraction
# - B2B + category signal detection ON THE OFFICIAL PAGE (strongest evidence)
import json, os, re, sys, concurrent.futures
import requests
import urllib3
urllib3.disable_warnings()
from urllib.parse import urlparse

GS = '/home/z/my-project/research/global_suppliers'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals, SKIP_HOSTS  # reuse signal dicts

def curl_page(url, timeout=10):
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'},
                         timeout=(4, timeout), allow_redirects=True, verify=False)
        return r.status_code, r.url, (r.text or '')[:400000]  # cap body: prevents regex blowups
    except Exception:
        return 0, url, ''

def extract_meta(html):
    title = ''
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
    if m: title = re.sub(r'\s+', ' ', m.group(1)).strip()[:150]
    desc = ''
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I|re.S) or \
        re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html, re.I|re.S)
    if m: desc = re.sub(r'\s+', ' ', m.group(1)).strip()[:300]
    og = ''
    m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', html, re.I|re.S)
    if m: og = re.sub(r'\s+', ' ', m.group(1)).strip()[:300]
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html[:400000], flags=re.S|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return title, (desc or og), text[:12000]

def verify_one(cand):
    dom = cand['domain']
    for scheme in ('https',):
        url = f'{scheme}://{dom}/'
        code, final_url, body = curl_page(url)
        if code in (200, 403, 406):  # 403/406 = exists but bot-blocked (Cloudflare etc.)
            title, desc, text = extract_meta(body)
            sig_text = f'{title} {desc} {text[:6000]}'
            b2b, cats = find_signals(sig_text)
            return {
                'domain': dom, 'http': code, 'final_url': final_url,
                'page_title': title, 'page_desc': desc,
                'page_b2b_signals': sorted(b2b), 'page_cat_signals': sorted(cats),
                'verified_at': __import__('datetime').datetime.now().isoformat(timespec='seconds'),
                'bot_blocked': code in (403, 406),
            }
        if code in (301, 302, 0) or (500 <= code < 600):
            continue
    return {'domain': dom, 'http': code, 'page_title': '', 'page_b2b_signals': [], 'page_cat_signals': [], 'verified_at': __import__('datetime').datetime.now().isoformat(timespec='seconds'), 'dead': code in (0, 404, 410)}

def main():
    cands = json.load(open(f'{GS}/candidates/candidates.json'))['candidates']
    already = {}
    try:
        for v in json.load(open(f'{GS}/candidates/verified_pages.json')):
            already[v['domain']] = v
    except Exception: pass
    todo = [c for c in cands if c['domain'] not in already]
    print(f"Verifying {len(todo)} / {len(cands)} candidate domains (direct HTTP)...")
    results = []
    def work(c): return verify_one(c)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(work, c) for c in todo]
        for i, fut in enumerate(concurrent.futures.as_completed(futs)):
            results.append(fut.result())
            if (i+1) % 20 == 0:  # incremental save (crash-safe)
                json.dump(list(already.values()) + results, open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
                print(f'  {i+1}/{len(todo)} (saved)')
    merged = list(already.values()) + results
    json.dump(merged, open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
    alive = [r for r in merged if r['http'] == 200]
    blocked = [r for r in merged if r.get('bot_blocked')]
    dead = [r for r in merged if r.get('dead') or r['http'] in (0,404,410)]
    with_b2b = [r for r in alive if r['page_b2b_signals'] and r['page_cat_signals']]
    print(f"\nVERIFIED PAGES: {len(merged)} total | alive 200: {len(alive)} | bot-blocked: {len(blocked)} | dead: {len(dead)}")
    print(f"alive WITH on-page B2B+category signals: {len(with_b2b)}")
    for r in sorted(with_b2b, key=lambda x: -len(x['page_b2b_signals']))[:30]:
        print(f"  {r['domain'][:38]:40} {r['http']} b2b={','.join(r['page_b2b_signals'])[:30]:32} cats={','.join(r['page_cat_signals'])[:40]}")

if __name__ == '__main__':
    main()
