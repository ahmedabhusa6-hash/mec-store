#!/usr/bin/env python3
# GDS-2: Retry bot-blocked (403/406) domains with alternate UA + trailing paths. Quota-free.
import json, re, sys, concurrent.futures
import requests
import urllib3
urllib3.disable_warnings()
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals

UAS = [
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'curl/8.4.0',
]

def curl(url, ua, timeout=9):
    try:
        r = requests.get(url, headers={'User-Agent': ua, 'Accept': 'text/html,*/*'}, timeout=(4, timeout), allow_redirects=True, verify=False)
        return r.status_code, r.text or ''
    except Exception:
        return 0, ''

def extract(html):
    title = ''
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
    if m: title = re.sub(r'\s+', ' ', m.group(1)).strip()[:150]
    desc = ''
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I|re.S)
    if m: desc = re.sub(r'\s+', ' ', m.group(1)).strip()[:300]
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html[:300000], flags=re.S|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    return title, desc, re.sub(r'\s+', ' ', text)[:10000]

def retry_one(item):
    dom, v = item
    for ua in UAS:
        for path in ('/', '/en', '/home'):
            code, html = curl(f'https://{dom}{path}', ua)
            if code == 200 and html:
                title, desc, text = extract(html)
                b2b, cats = find_signals(f'{title} {desc} {text[:7000]}')
                if title or b2b or cats:
                    return dom, {'http': 200, 'final_url': f'https://{dom}{path}', 'page_title': title,
                                 'page_desc': desc, 'page_b2b_signals': sorted(b2b), 'page_cat_signals': sorted(cats),
                                 'bot_blocked': False, 'unblocked_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
            if code in (301, 302, 0, 404): break
        # try next UA
    return dom, None

def main():
    verified = {v['domain']: v for v in json.load(open(f'{GS}/candidates/verified_pages.json'))}
    blocked = [(d, v) for d, v in verified.items() if v.get('bot_blocked')]
    print(f'Retrying {len(blocked)} bot-blocked domains with alternate UAs...')
    PROG = f'{GS}/candidates/unblock_progress.json'
    try: done = set(json.load(open(PROG))['done'])
    except Exception: done = set()
    blocked = [(d, v) for d, v in blocked if d not in done]
    print(f'after resume-skip: {len(blocked)}')

    unblocked = 0
    def work(t): return retry_one(t)
    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for dom, newv in ex.map(work, blocked):
            n += 1; done.add(dom)
            if newv:
                verified[dom] = {**verified.get(dom, {}), **newv}
                unblocked += 1
            if n % 25 == 0:
                print(f'  {n}/{len(blocked)} | unblocked: {unblocked}')
                json.dump({'done': sorted(done)}, open(PROG,'w'))
                json.dump(list(verified.values()), open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
    json.dump({'done': sorted(done)}, open(PROG,'w'))
    json.dump(list(verified.values()), open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
    print(f'\nUNBLOCKED: {unblocked} domains now HTTP 200 with signals')

if __name__ == '__main__':
    main()
