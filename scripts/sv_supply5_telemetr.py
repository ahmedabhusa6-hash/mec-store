#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5: telemetr.io profile fetch for storeBatman + AiVerseXHub clusters."""
import json, re, ssl, time, html, urllib.request, urllib.error

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
OUT = "/home/z/my-project/research/sv_supply5_telemetr.json"

def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)[:150]

def clean(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()

result = {}
targets = {
    "storeBatman": "https://telemetr.io/channels/storeBatman",
    "storeBatmanBot": "https://telemetr.io/bots/storeBatmanBot",
    "AiVerseXHub": "https://telemetr.io/channels/AiVerseXHub",
    "AIVerseXBot": "https://telemetr.io/bots/AIVerseXBot",
    "ProdSellerOfficial": "https://telemetr.io/channels/ProdSellerOfficial",
    "HitMeowShop": "https://telemetr.io/channels/HitMeowShop",
}
for name, url in targets.items():
    st, body = get(url)
    rec = {"url": url, "http": st}
    if st == 200 and body:
        # title & meta description
        tm = re.search(r"<title[^>]*>([^<]*)</title>", body, re.I)
        md = re.search(r'name="description" content="([^"]*)"', body)
        if tm: rec["title"] = clean(tm.group(1))[:160]
        if md: rec["meta_desc"] = clean(md.group(1))[:300]
        # stats in body text
        txt = clean(body)
        for pat, key in [(r"([\d,\.Kk]+)\s*(?:subscribers|members)", "members"),
                         (r"([\d,\.Kk]+)\s*posts?", "posts"),
                         (r"language[:\s]+(\w+)", "language"),
                         (r"category[:\s]+([\w &]+?)(?:\s{2,}|$)", "category")]:
            m = re.search(pat, txt, re.I)
            if m: rec[key] = m.group(1)[:40]
        # links (t.me / websites) in page
        rec["tme_links"] = sorted(set(re.findall(r"t\.me/([A-Za-z0-9_]+)", body)))[:12]
        rec["ext_links"] = sorted(set(l for l in re.findall(r'https?://([a-z0-9\.\-]+\.[a-z]{2,})', body)
                                      if not any(x in l for x in ["telemetr.io", "telegram.org", "google", "facebook", "twitter", "cdn.", "cdnjs", "fonts.", "jsdelivr", "cloudflare", "github", "schema.org"])))[:10]
    else:
        rec["note"] = "unreachable or not listed"
    result[name] = rec
    print(f"--- {name}: http={st} title={rec.get('title','')[:70]}")
    if "meta_desc" in rec: print("    desc:", rec["meta_desc"][:180])
    if "members" in rec: print("    members:", rec["members"])
    time.sleep(1.2)

json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
