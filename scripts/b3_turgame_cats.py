#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.3 | Turgame category extraction (WooCommerce) — direct observation, quota-free."""
import json, re, time, ssl, urllib.request, html as htmlmod

OUT = "/home/z/my-project/research/b3_turgame_categories.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Accept-Language": "en,tr;q=0.8"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def fetch(u):
    req = urllib.request.Request(u, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            return r.getcode(), r.read().decode("utf-8", "replace")
    except Exception as e:
        return None, str(e)[:80]

def clean(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

CATS = [
    ("steam", "https://www.turgame.com/steam-gift-cards/"),
    ("playstation", "https://www.turgame.com/playstation-gift-cards/"),
    ("xbox", "https://www.turgame.com/xbox-live-gift-cards/"),
    ("google-play", "https://www.turgame.com/google-play-gift-cards/"),
    ("apple", "https://www.turgame.com/app-store-card-apple-gift-card/"),
    ("amazon", "https://www.turgame.com/amazon-gift-cards/"),
    ("valorant", "https://www.turgame.com/valorant-points-vp/"),
    ("lol", "https://www.turgame.com/lol-rp/"),
    ("windows", "https://www.turgame.com/microsoft-windows/"),
    ("office", "https://www.turgame.com/microsoft-office/"),
    ("streaming", "https://www.turgame.com/streaming/"),
    ("software", "https://www.turgame.com/software/"),
]

RES = {"fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "categories": {}}

for slug, url in CATS:
    code, body = fetch(url)
    entry = {"url": url, "http": code, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if code == 200:
        prods = []
        # observed structure 27/09: <h2 class="woocommerce-loop-product__title"><a href="URL">NAME</a></h2> ... <bdi>5,20&nbsp;<span>USD</span></bdi>
        blocks = re.split(r'woocommerce-loop-product__title', body)
        for seg in blocks[1:]:
            mn = re.search(r'<a href="([^"]+)"[^>]*>([^<]{3,90})</a>', seg[:2000])
            if not mn: continue
            url_p, name = mn.group(1), clean(mn.group(2))
            # price: first bdi in the following ~4000 chars (product block)
            mp = re.search(r'<bdi>([^<]{1,30})<', seg[:4000])
            price = clean(mp.group(1)).replace('\xa0', ' ') if mp else None
            soldout = bool(re.search(r'(?i)sold\s*out|out\s*of\s*stock|stokta\s*yok', seg[:4000]))
            cur = re.search(r'woocommerce-Price-currencySymbol[^>]*>([A-Z]{2,4})<', seg[:4000])
            prods.append({"name": name, "price": price,
                          "currency": cur.group(1) if cur else None,
                          "url": url_p, "sold_out": soldout})
        seen, uniq = set(), []
        for p in prods:
            if p["name"] not in seen:
                seen.add(p["name"]); uniq.append(p)
        entry["n_products"] = len(uniq)
        entry["products"] = uniq[:100]
    RES["categories"][slug] = entry
    print(slug, code, entry.get("n_products", 0))
    time.sleep(3)

json.dump(RES, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
total = sum(c.get("n_products", 0) for c in RES["categories"].values())
print("TOTAL products:", total, "->", OUT)
