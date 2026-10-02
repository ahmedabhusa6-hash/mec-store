#!/usr/bin/env python3
# GDS-1: chunked verifier v2 — hard wall-clock timeout per chunk, abandon stragglers, os._exit
import json, sys, time, os, concurrent.futures
sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from verify import verify_one

GS = '/home/z/my-project/research/global_suppliers'
CHUNK = 40
WALL = 100  # seconds per chunk (hard cap)

def main():
    cands = json.load(open(f'{GS}/candidates/candidates.json'))['candidates']
    try: already = {v['domain']: v for v in json.load(open(f'{GS}/candidates/verified_pages.json'))}
    except Exception: already = {}
    todo = [c for c in cands if c['domain'] not in already]
    print(f"remaining: {len(todo)}", flush=True)
    t0 = time.time()
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=12)
    while todo:
        chunk, todo = todo[:CHUNK], todo[CHUNK:]
        futs = {ex.submit(verify_one, c): c['domain'] for c in chunk}
        done, pending = concurrent.futures.wait(list(futs.keys()), timeout=WALL)
        n_ok = 0
        for f in done:
            r = f.result()
            already[r['domain']] = r
            n_ok += 1
        for f in pending:
            f.cancel()
            already[futs[f]] = {'domain': futs[f], 'http': 0, 'page_title': '',
                                'page_b2b_signals': [], 'page_cat_signals': [],
                                'verified_at': 'abandoned-timeout', 'abandoned': True}
        json.dump(list(already.values()), open(f'{GS}/candidates/verified_pages.json','w'), ensure_ascii=False, indent=1)
        alive = sum(1 for v in already.values() if v['http'] == 200)
        strong = sum(1 for v in already.values() if v['http'] == 200 and v['page_b2b_signals'] and v['page_cat_signals'])
        print(f"chunk: +{n_ok} done, {len(pending)} abandoned | total {len(already)} | alive {alive} | strong {strong} | {time.time()-t0:.0f}s", flush=True)
    print("ALL VERIFIED", flush=True)
    os._exit(0)  # hard exit: bypass straggler thread joins

if __name__ == '__main__':
    main()
