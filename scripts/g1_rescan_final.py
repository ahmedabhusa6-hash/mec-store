#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R2d — final round:
  G1  full gemini12pro post texts (no truncation) — esp. 01/09 (@AIXpre..) & 30/09 (direct supplier)
  G2  passive GET of new identity-lead domains: vibi.top, dongvanfb.net,
      get-opt.phh.info.vn, daily.bddevlab.buzz/redeem.html, duc-dop-error-guide.pages.dev
READ-ONLY / passive public pages only."""
import json, re, time, gzip
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))

def fetch(name, url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"})
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
        rec["http"] = e.code; rec["err"] = "HTTPError"
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:100]}"
    return rec

# ---- G1: full g12 texts ----
raw1 = json.load(open("/home/z/my-project/research/g1_rescan_raw_20261002.json"))
g12 = next(f["body"] for f in raw1["fetches"] if f["name"] == "g12_channel")
blocks = re.split(r'class="tgme_widget_message ', g12)
msgs = []
for b in blocks[1:]:
    t = re.search(r'datetime="([\d\-T:+]+)"', b)
    x = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)(?:</div>\s*<div|</div>\s*</div|$)', b, re.S)
    if t:
        txt = re.sub(r"<br\s*/?>", "\n", x.group(1)) if x else ""
        txt = re.sub(r"<[^>]+>", "", txt)
        txt = (txt.replace("&#036;", "$").replace("&#33;", "!").replace("&amp;", "&")
                   .replace("&#039;", "'").replace("&quot;", '"').replace("&#128073;", "->"))
        msgs.append((t.group(1), txt.strip()))
msgs.sort(key=lambda m: m[0])
print("=== G1: gemini12pro FULL POSTS (last 10) ===")
for dt, tx in msgs[-10:]:
    print(f"\n--- {dt[:16]} ---\n{tx[:900]}")

out = {"g12_full_posts": [{"dt": d, "text": t} for d, t in msgs], "probes": []}

# ---- G2: passive domain probes ----
print("\n\n=== G2: identity-lead domain probes (passive) ===")
for name, url in [
    ("vibi_top", "https://vibi.top/"),
    ("vibi_docs_vi", "https://vibi.top/docs-setup/vi"),
    ("dongvanfb", "https://dongvanfb.net/"),
    ("getopt_phh", "https://get-opt.phh.info.vn/"),
    ("bddevlab_redeem", "https://daily.bddevlab.buzz/redeem.html"),
    ("ducdop_guide", "https://duc-dop-error-guide.pages.dev/"),
]:
    rec = fetch(name, url)
    out["probes"].append(rec)
    title = re.search(r"<title>(.*?)</title>", rec.get("body") or "", re.S)
    desc = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{0,160})"', rec.get("body") or "")
    print(f"  [{rec['http']}] {name:16} len={rec['len']:>7} title={title.group(1).strip()[:70] if title else None}")
    if desc: print(f"        desc: {desc.group(1)[:130]}")
    time.sleep(0.6)

with open("/home/z/my-project/research/g1_rescan_raw4_20261002.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\nSaved -> research/g1_rescan_raw4_20261002.json")
