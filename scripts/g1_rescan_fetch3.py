#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R2c — acczone /getServices + /getBalance (read-only GET, auth variants)."""
import json, time, gzip
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_rescan_raw3_20261002.json"
ACZ_KEY = "[REDACTED-ACZ-KEY]"

def fetch(name, url, headers=None, timeout=20):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    rec = {"name": name, "url": url, "http": None, "err": None, "len": 0, "body": None,
           "ts": datetime.now(TZ).isoformat()[:19]}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            rec["body"] = raw.decode("utf-8", "replace"); rec["http"] = r.status; rec["len"] = len(rec["body"])
    except urllib.error.HTTPError as e:
        try: rec["body"] = e.read().decode("utf-8", "replace")
        except Exception: rec["body"] = None
        rec["http"] = e.code; rec["err"] = "HTTPError"; rec["len"] = len(rec["body"] or "")
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:120]}"
    return rec

results = {"execution_timestamp": datetime.now(TZ).isoformat(), "fetches": []}
def do(name, url, headers=None):
    rec = fetch(name, url, headers)
    results["fetches"].append(rec)
    b = (rec.get("body") or "")[:110].replace("\n", " ")
    print(f"  [{rec['http'] if rec['http'] is not None else 'ERR'}] {name:28} {b}")
    time.sleep(0.5)
    return rec

BASE = "https://api.acczone.xyz"
J = {"Accept": "application/json"}
do("acz_getServices_plain", BASE + "/getServices", J)
do("acz_getServices_xak", BASE + "/getServices", {"X-API-Key": ACZ_KEY, **J})
do("acz_getServices_bearer", BASE + "/getServices", {"Authorization": "Bearer " + ACZ_KEY, **J})
do("acz_getServices_qkey", BASE + "/getServices?key=" + ACZ_KEY, J)
do("acz_getServices_qapikey", BASE + "/getServices?apikey=" + ACZ_KEY, J)
do("acz_getServices_qtoken", BASE + "/getServices?token=" + ACZ_KEY, J)
do("acz_getBalance_xak", BASE + "/getBalance", {"X-API-Key": ACZ_KEY, **J})
do("acz_getBalance_bearer", BASE + "/getBalance", {"Authorization": "Bearer " + ACZ_KEY, **J})
do("acz_getBalance_qkey", BASE + "/getBalance?key=" + ACZ_KEY, J)

with open(OUT, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("Saved ->", OUT)
