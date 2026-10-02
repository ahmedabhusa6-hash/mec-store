#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5h | Turgame P3-relevant category extraction (Notion-specified channel, Amendment A).
Homepage revealed 1000+ categories. Extract P3-relevant ones (~70) in 2 paced batches.
Output: research/b3_turgame_p3.json
"""
import json, os, re, time, urllib.request, gzip

BASE = "/home/z/my-project"
BATCH = int(os.environ.get("BATCH_N", "1"))
OUT = os.path.join(BASE, "research", f"b3_turgame_p3_b{BATCH}.json")

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = r.read()
            if r.headers.get("Content-Encoding") == "gzip": d = gzip.decompress(d)
            return r.status, d.decode("utf-8", "ignore")
    except Exception as e:
        return None, str(e)[:100]

# P3-relevant categories (from homepage link scan, matched to P3 families)
CATS = [
    # Digital Subscriptions (38 P3)
    "netflix", "spotify", "disney", "hulu", "paramount-plus", "starzplay", "osn-plus-algeria",
    "crunchyroll", "tidal", "deezer-premium", "storytel", "dazn", "youtube-tv", "siriusxm",
    "britbox", "mbc-shahid", "anghami-plus", "yango-play-subscription", "bilibili-premium",
    "sling", "vudu", "sawa-play", "wavve" if False else "netflix",
    # Software (10 P3)
    "microsoft-office", "microsoft-windows", "adobe-digital", "mcafee-antivirus", "norton",
    "bitdefender", "exitlag", "software",
    # Game Top-ups (32 P3)
    "pubg-mobile-uc", "valorant-points-vp", "free-fire", "mobile-legends-diamond", "mobile-legends-global",
    "fortnite-game-points", "lol-rp", "call-of-duty-points", "bigo-live-diamonds", "roblox",
    "honor-of-kings-coin", "candy-crush", "whiteout-survival-frost-star", "tango-coins-code",
    "starmaker-coins-top-up", "soulchill-crystal", "yaahlan-diamonds", "yalla-ludo-diamonds",
    "yalla-ludo-gold", "chamet-diamonds-top-up", "likee-diamonds-code", "imvu", "rec-room",
    "jawaker-token", "sugo-coins", "gocash-game-card", "cherry-credits", "karma-koin",
    "nexon-karma-koin", "xsolla", "apex-legends", "black-desert",
    # Gift Cards (43 P3)
    "steam-gift-cards", "playstation-gift-cards", "xbox-live-gift-cards", "google-play-gift-cards",
    "app-store-card-apple-gift-card", "amazon-gift-cards", "razer-gold", "battlenet-gift-card",
    "epic-games", "meta", "tiktok", "binance-gift-card", "cryptovoucher", "flexepin", "webmoney",
    "prepaid-visa", "huawei-gift-card", "gameforge-gift-cards", "discord-nitro",
    # eSIM/Telecom (15 P3)
    "airalo", "alosim", "esimchoice", "etisalat", "du", "sawa-play", "vodafone-top-up",
    "lebara", "lyca-mobile-top-up", "giffgaff-top-up", "salik",
    # VPN
    "surfshark",
]
CATS = sorted(set(CATS))

PRODUCT_RE = re.compile(
    r'<li[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</li>', re.S)
LINK_RE = re.compile(r'<a[^>]+href="(https://www\.turgame\.com/[^"]+)"[^>]*>([^<]*(?:<[^/][^>]*>[^<]*)*?)</a>')
NAME_RE = re.compile(r'<h[23][^>]*>(.*?)</h[23]>', re.S)
PRICE_RE = re.compile(r'<bdi>([0-9]+(?:[.,][0-9]+)?)')
TAG_RE = re.compile(r"<[^>]+>")

def parse_products(html):
    prods = []
    # Turgame product cards: woocommerce list items with <a> title + bdi price
    for m in re.finditer(r'<li\s+class="[^"]*\bproduct\b[^"]*"[^>]*>(.*?)</li>', html, re.S):
        block = m.group(1)
        link = re.search(r'<a[^>]+href="([^"]+)"[^>]*>', block)
        title = re.search(r'title="([^"]+)"', block)
        if not title:
            t2 = re.search(r'<h[23][^>]*>(.*?)</h[23]>', block, re.S)
            title = t2 and type("T", (), {"group": lambda s: re.sub(TAG_RE, "", t2.group(1)).strip()})
        price = PRICE_RE.search(block)
        if not (link and title): continue
        name = title.group(1)
        # clean possible inner tags
        name = re.sub(TAG_RE, "", name).strip()
        if not name or len(name) < 4: continue
        prods.append({
            "name": name[:100],
            "price": price.group(1) if price else None,
            "url": link.group(1)[:120],
        })
    return prods

# batch index defined at top (BATCH_N env)
errors = []
results = {}
start = (BATCH - 1) * 35
end = min(BATCH * 35, len(CATS))
todo = CATS[start:end]
print(f"batch {BATCH}: categories {start}..{end-1} of {len(CATS)}")

for cat in todo:
    url = f"https://www.turgame.com/{cat}/"
    status, html = fetch(url)
    time.sleep(3.0)
    if status != 200 or not isinstance(html, str):
        errors.append({"cat": cat, "http": status, "err": str(html)[:80]})
        print(f"  {cat}: {status} ERR")
        continue
    prods = parse_products(html)
    # filter actual product cards (with prices)
    priced = [p for p in prods if p["price"]]
    results[cat] = {"http": status, "n_products": len(prods), "n_priced": len(priced), "products": priced[:40]}
    print(f"  {cat}: {len(prods)} products, {len(priced)} priced")

out = {"run": f"MEC-2.5h Turgame P3 categories batch {BATCH}",
       "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
       "batch": BATCH, "categories_requested": todo, "errors": errors, "categories": results}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

total_priced = sum(r["n_priced"] for r in results.values())
print(f"\nbatch {BATCH} DONE: {len(results)} categories ok, {len(errors)} errors, {total_priced} priced products")
