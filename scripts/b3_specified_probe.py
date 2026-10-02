#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5e | Direct price probe of Notion-specified channels not yet price-observed.
Quota-free HTTP. Targets: FazerCards, Ding, DT One, Mega Center, Al Momaiz,
vividgold (re-probe), bittopup, K4G. Pacing 3s (lesson: 1-2 fetches per site).
Output: research/b3_specified_channels_probe.json
"""
import json, os, re, time, urllib.request, gzip

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "research", "b3_specified_channels_probe.json")

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml", "Accept-Encoding": "gzip",
        "Accept-Language": "en;q=0.9,ar;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            return r.status, data.decode("utf-8", "ignore"), r.url
    except Exception as e:
        return None, str(e)[:150], url

TAG_RE = re.compile(r"<[^>]+>")
def clean(html, limit=3000):
    t = TAG_RE.sub(" ", html)
    return re.sub(r"\s+", " ", t).strip()[:limit]

# price-like lines: capture context around currency amounts
PRICE_CTX = re.compile(r".{0,70}?(?:USD|\$|€|£|SAR|AED)\s?[0-9]+(?:\.[0-9]{1,2})?.{0,40}", re.I)

TARGETS = [
    ("FazerCards", "https://fazercards.com/"),
    ("FazerCards-shop", "https://fazercards.com/shop/"),
    ("Ding", "https://www.ding.com/"),
    ("DT-One", "https://www.dtone.com/"),
    ("MegaCenter", "https://megacenter.sa/"),
    ("AlMomaiz", "https://almomaiz.com/"),
    ("vividgold", "https://vividgold.africa/"),
    ("bittopup", "https://bittopup.com/"),
    ("K4G", "https://k4g.com/"),
    ("cardsouq", "https://www.cardsouq.com/"),
]

results = {}
for name, url in TARGETS:
    status, html, final = fetch(url)
    time.sleep(3.0)
    if status != 200 or not isinstance(html, str):
        results[name] = {"url": url, "http": status, "note": str(html)[:100]}
        print(f"{name}: {status} — {str(html)[:60]}")
        continue
    text = clean(html)
    prices = [p.strip() for p in PRICE_CTX.findall(text)][:15]
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
    results[name] = {
        "url": url, "final_url": final, "http": status, "bytes": len(html),
        "title": title.group(1).strip()[:100] if title else "",
        "price_lines": prices, "text_excerpt": text[:600],
    }
    print(f"{name}: {status} | {len(html)}B | title={results[name]['title'][:50]} | prices={len(prices)}")
    for p in prices[:5]:
        print("   $", p[:90])

out = {"run": "MEC-2.5e specified-channels direct probe", "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
       "results": results}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nDONE:", len(results), "targets")
