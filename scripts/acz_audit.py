#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACZ — Acczone API audit with delivered key (read-only GET only).

Key delivered by user 2026-10-02 (G-13 outstanding item #1).
Auth method (per official docs page): ?apikey= query parameter.
Rate limit: 1 request / 2 seconds (429 otherwise) -> sleep 2.6s.
ETHICS (PMRF §2): read-only. /buyCpn /add /ipn /webhooks are NEVER called.
Outputs: research/acz_audit_raw_20261002.json
"""
import json, time, gzip
import urllib.request, urllib.error
import ssl
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
BASE = "https://api.acczone.xyz"
ACZ_KEY = "[REDACTED-ACZ-KEY]"
OUT = "/home/z/my-project/research/acz_audit_raw_20261002.json"
MAX_PAGES = 40  # hard cap: 40 x 100 = 4000 records

ctx = ssl.create_default_context()

def fetch(name, url, timeout=25):
    h = {"User-Agent": UA, "Accept": "application/json, text/plain, */*",
         "Accept-Encoding": "gzip", "Referer": BASE + "/",
         "Origin": BASE}
    req = urllib.request.Request(url, headers=h)
    rec = {"name": name, "url": url.replace(ACZ_KEY, "KEY_REDACTED"),
           "http": None, "err": None, "len": 0, "body": None,
           "ts": datetime.now(TZ).isoformat()[:19]}
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            rec["body"] = raw.decode("utf-8", "replace")
            rec["http"] = r.status; rec["len"] = len(rec["body"])
    except urllib.error.HTTPError as e:
        try: rec["body"] = e.read().decode("utf-8", "replace")
        except Exception: rec["body"] = None
        rec["http"] = e.code; rec["err"] = "HTTPError"; rec["len"] = len(rec["body"] or "")
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:150]}"
    return rec

results = {"execution_timestamp": datetime.now(TZ).isoformat(),
           "target": BASE, "key_fingerprint": ACZ_KEY[:8] + "..." + ACZ_KEY[-6:],
           "key_length": len(ACZ_KEY), "fetches": []}

def do(name, url, pause=2.6):
    rec = fetch(name, url)
    results["fetches"].append(rec)
    b = (rec.get("body") or "")[:130].replace("\n", " ")
    print(f"  [{rec['http'] if rec['http'] is not None else 'ERR'}] {name:30} len={rec['len']:<7} {b}")
    time.sleep(pause)
    return rec

print("=== Acczone authenticated audit (read-only) ===")
print("ts:", results["execution_timestamp"])

# 0) documentation + spec (change detection vs 02/10 snapshot)
do("docs_index", BASE + "/", pause=1.2)
do("openapi", BASE + "/openapi.json", pause=1.2)

# 1) account identity + balance  (THE decisive test: documented ?apikey= param)
r_bal = do("getBalance_apikey", BASE + "/getBalance?apikey=" + ACZ_KEY)

# 1b) error semantics: wrong key (control) — proves the param is being read
do("getBalance_wrongkey", BASE + "/getBalance?apikey=INVALID_KEY_TEST_000", pause=2.6)

# 2) services catalog (public per docs; confirm current state)
r_svc = do("getServices", BASE + "/getServices")

# 3) activation history — paginated, read-only
hist_pages = []
page = 1
empty_streak = 0
while page <= MAX_PAGES:
    r = do(f"getHistory_p{page}", BASE + f"/getHistory?apikey={ACZ_KEY}&page={page}&limit=100")
    hist_pages.append(r)
    ok = False
    if r["http"] == 200 and r["body"]:
        try:
            arr = json.loads(r["body"])
            if isinstance(arr, list) and len(arr) > 0:
                ok = True
        except Exception:
            pass
    if not ok:
        empty_streak += 1
        if empty_streak >= 2 or (isinstance(arr if 'arr' in dir() else None, list) and len(arr) == 0):
            break
        if r["http"] == 429:
            time.sleep(4); empty_streak = 0; continue
    else:
        empty_streak = 0
    page += 1

# summary
def count_hist():
    n = 0
    for r in hist_pages:
        if r["http"] == 200 and r["body"]:
            try:
                a = json.loads(r["body"])
                if isinstance(a, list): n += len(a)
            except Exception: pass
    return n

results["summary"] = {
    "balance_http": r_bal["http"],
    "balance_parse": (json.loads(r_bal["body"]) if r_bal["http"] == 200 and r_bal["body"] and r_bal["body"].strip().startswith("{") else None),
    "history_pages_fetched": len(hist_pages),
    "history_records": count_hist(),
}
with open(OUT, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\nSaved ->", OUT)
print("history records:", results["summary"]["history_records"])
