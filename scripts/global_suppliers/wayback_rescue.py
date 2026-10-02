#!/usr/bin/env python3
# GDS-3: Wayback Machine rescue for bot-blocked domains — quota-free.
# For each domain still bot-blocked (403/406, zero signals), fetch its latest
# archived snapshot from the Internet Archive (public CDX API + raw snapshot)
# and extract B2B/category signals from the archived official page.
# Evidence type recorded as 'archived official page (Wayback)' — clearly distinct
# from live-fetch evidence; qualify.py still gates on signal presence.
import json, re, sys, time, concurrent.futures
import requests
import urllib3
urllib3.disable_warnings()
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from process import find_signals

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
CDX = 'https://web.archive.org/cdx/search/cdx'
PROG = f'{GS}/candidates/wayback_progress.json'
VP = f'{GS}/candidates/verified_pages.json'


def cdx_latest(domain):
    """Return (timestamp, original_url) of most recent 200 snapshot, or None."""
    try:
        r = requests.get(CDX, params={
            'url': domain, 'output': 'json', 'limit': '-5',
            'filter': 'statuscode:200', 'collapse': 'digest',
        }, headers={'User-Agent': UA}, timeout=25)
        rows = r.json()
        if not isinstance(rows, list) or len(rows) < 2:
            return None
        # rows[0] = header; take the last row (most recent)
        hdr = rows[0]
        i_ts, i_orig = hdr.index('timestamp'), hdr.index('original')
        row = rows[-1]
        return row[i_ts], row[i_orig]
    except Exception:
        return None


def fetch_snapshot(ts, orig):
    """Fetch raw archived page (id_ suffix = no wayback toolbar)."""
    url = f'https://web.archive.org/web/{ts}id_/https://{orig}'
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=40)
        if r.status_code == 200:
            return (r.text or '')[:400000]
    except Exception:
        pass
    return ''


def extract(html):
    title = ''
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
    if m:
        title = re.sub(r'\s+', ' ', m.group(1)).strip()[:150]
    desc = ''
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I | re.S) or \
        re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html, re.I | re.S)
    if m:
        desc = re.sub(r'\s+', ' ', m.group(1)).strip()[:300]
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html[:400000], flags=re.S | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    return title, desc, re.sub(r'\s+', ' ', text)[:12000]


def rescue_one(dom):
    """Try to rescue one blocked domain via archive. Returns dict or None."""
    snap = cdx_latest(dom)
    if not snap:
        return None
    ts, orig = snap
    # reject stale archives older than ~6 years (business may have changed)
    try:
        year = int(ts[:4])
        if year < 2020:
            return None
    except Exception:
        return None
    html = fetch_snapshot(ts, orig)
    if not html:
        return None
    title, desc, text = extract(html)
    b2b, cats = find_signals(f'{title} {desc} {text[:8000]}')
    if not (title or b2b or cats):
        return None
    return {
        'domain': dom, 'http': 200, 'final_url': f'https://{dom}/',
        'page_title': title, 'page_desc': desc,
        'page_b2b_signals': sorted(b2b), 'page_cat_signals': sorted(cats),
        'bot_blocked': True, 'wayback_ts': ts,
        'wayback_rescued_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'evidence': 'archived official page (Wayback)',
    }


def main():
    verified = {v['domain']: v for v in json.load(open(VP))}
    try:
        prog = json.load(open(PROG))
        done = set(prog['done'])
    except Exception:
        done = set()
    targets = [(d, v) for d, v in verified.items()
               if v.get('bot_blocked') and d not in done]
    print(f'Wayback rescue targets: {len(targets)} bot-blocked domains')
    rescued, n = {}, 0
    lock = __import__('threading').Lock()

    def work(item):
        d, _v = item
        r = rescue_one(d)
        return d, r

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for dom, res in ex.map(work, targets):
            with lock:
                n += 1
                done.add(dom)
                if res:
                    rescued[dom] = res
                    verified[dom] = res  # replace blocked entry
                if n % 20 == 0:
                    print(f'  {n}/{len(targets)} | rescued: {len(rescued)}')
                    json.dump({'done': sorted(done), 'rescued': rescued}, open(PROG, 'w'))
                    json.dump(list(verified.values()), open(VP, 'w'), ensure_ascii=False, indent=1)
    json.dump({'done': sorted(done), 'rescued': rescued}, open(PROG, 'w'))
    json.dump(list(verified.values()), open(VP, 'w'), ensure_ascii=False, indent=1)
    print(f'\nWAYBACK RESCUE DONE: {len(rescued)} domains rescued with signals')
    for d, r in sorted(rescued.items()):
        print(f"  {d[:40]:42} b2b={','.join(r['page_b2b_signals'])[:28]:30} cats={','.join(r['page_cat_signals'])[:38]}")


if __name__ == '__main__':
    main()
