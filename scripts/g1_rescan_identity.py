#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R2g — final identity round (passive public):
  - t.me/s/teamsoclo (channel preview — 21x referenced in cb_ descriptions)
  - daily.bddevlab.buzz root (Claude-token CDK gateway)
  - prodseller.com root + /v1/me full body (platform branding)
  - teamsoclo channel: extract announcements (shop? panel? reseller API?)
"""
import json, re, time, gzip
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
PS_KEY = "[REDACTED-PRODSELLER-KEY]"

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
        rec["err"] = f"{type(e).__name__}: {str(e)[:100]}"
    return rec

out = {"execution_timestamp": datetime.now(TZ).isoformat(), "probes": []}
def do(name, url, headers=None):
    rec = fetch(name, url, headers)
    out["probes"].append(rec)
    b = (rec.get("body") or "")[:80].replace("\n", " ")
    print(f"  [{rec['http']}] {name:18} len={rec['len']:>7}  {b}")
    time.sleep(0.6)
    return rec

print("=== final identity round ===")
r_ts = do("teamsoclo_channel", "https://t.me/s/teamsoclo")
do("bddevlab_root", "https://daily.bddevlab.buzz/")
do("prodseller_root", "https://prodseller.com/")
do("ps_v1_me", "https://prodseller.com/v1/me", {"X-API-Key": PS_KEY, "Accept": "application/json"})

# teamsoclo channel posts
if r_ts.get("body"):
    blocks = re.split(r'class="tgme_widget_message ', r_ts["body"])
    msgs = []
    for b in blocks[1:]:
        t = re.search(r'datetime="([\d\-T:+]+)"', b)
        x = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)(?:</div>\s*<div|</div>\s*</div|$)', b, re.S)
        if t:
            txt = re.sub(r"<br\s*/?>", "\n", x.group(1)) if x else ""
            txt = re.sub(r"<[^>]+>", "", txt)
            txt = (txt.replace("&#036;", "$").replace("&#33;", "!").replace("&amp;", "&")
                       .replace("&#039;", "'").replace("&quot;", '"'))
            msgs.append((t.group(1), txt.strip()))
    msgs.sort(key=lambda m: m[0])
    title = re.search(r'<meta property="og:title" content="([^"]+)"', r_ts["body"])
    print(f"\n  teamsoclo channel: {len(msgs)} posts; og:title={title.group(1) if title else None}")
    for dt, tx in msgs[-10:]:
        print(f"\n  --- {dt[:16]} ---\n  {tx[:600]}")
    out["teamsoclo_posts"] = [{"dt": d, "text": t} for d, t in msgs]

# prodseller root title
pr = next((p for p in out["probes"] if p["name"] == "prodseller_root"), None)
if pr and pr.get("body"):
    t = re.search(r"<title>(.*?)</title>", pr["body"], re.S)
    print("\n  prodseller.com title:", t.group(1).strip()[:100] if t else None)

with open("/home/z/my-project/research/g1_rescan_raw6_20261002.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\nSaved -> research/g1_rescan_raw6_20261002.json")
