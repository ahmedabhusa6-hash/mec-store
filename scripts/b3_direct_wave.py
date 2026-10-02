#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.3 | Direct HTTP Observation Wave (quota-free evidence layer)
Re-probes §19 channel registry (delta since 00:53 UTC probe) + deep-fetches public
keyshop/marketplace pages for anchor SKUs. All fetches = plain HTTP (independent of
z-ai remote-function quota, which is currently 477-blocked).
Evidence class produced: Directly-Observed [page fetch, timestamped].
Output: research/b3_direct_observations.json
"""
import json, re, time, ssl, urllib.request, urllib.error, html as htmlmod

BASE = "/home/z/my-project"
OUT = BASE + "/research/b3_direct_observations.json"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en,ar;q=0.9,ru;q=0.8,tr;q=0.7",
}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.getcode(), r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        try: body = e.read().decode("utf-8", "replace")[:3000]
        except Exception: body = ""
        return e.code, body, url
    except Exception as e:
        return None, "EXC: %s" % e, url

def clean(s):
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

PRICE_RE = re.compile(
    r"[^\n]{0,60}?(?:\$|€|£|₽|₺|USD|EUR|TRY|RUB|سعر|بسعر)[^\n]{0,70}", re.I)

def price_lines(text, maxn=40):
    out, seen = [], set()
    for m in PRICE_RE.finditer(text):
        line = clean(m.group(0))[:130]
        if line and line not in seen and re.search(r"\d", line):
            seen.add(line); out.append(line)
        if len(out) >= maxn: break
    return out

RESULTS = {"wave_id": "MEC2-20260927-B3-DIRECT",
           "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "channels": {}, "sites": {}, "errors": []}

# ═══ PART 1: §19 channel registry re-probe (32 entities) ═══
ENTITIES = [
    ("gemini12pro_channel","channel","https://t.me/gemini12pro_channel","Gemini12Pro"),
    ("ProdSellerOfficial","channel","https://t.me/ProdSellerOfficial","ProdSeller"),
    ("learnwith_Alex","channel","https://t.me/learnwith_Alex","learnwith_Alex"),
    ("AWZ_invite","private_invite","https://t.me/+AWZ-Jl8sydhiMzYy","AWZ-private"),
    ("Evo_Era_updates","channel","https://t.me/Evo_Era_updates","EvoEra"),
    ("HitMeowShop","channel","https://t.me/HitMeowShop","HitMeow"),
    ("AISUBSID","channel","https://t.me/AISUBSID","AISUBSID"),
    ("verifierg","channel","https://t.me/verifierg","VerifierGroup"),
    ("gemini12pro","channel_or_acct","https://t.me/gemini12pro","Gemini12Pro"),
    ("acczone_logs","channel","https://t.me/acczone_logs","Acczone"),
    ("stackvault_shop","website","https://stackvault.shop","StackVault"),
]
S_PREVIEW = ["gemini12pro_channel","ProdSellerOfficial","learnwith_Alex",
             "Evo_Era_updates","HitMeowShop","AISUBSID","verifierg",
             "gemini12pro","acczone_logs"]

print("── Part 1: channel registry delta re-probe")
for cid, ctype, url, cluster in ENTITIES:
    code, body, final = fetch(url)
    ent = {"url": url, "type": ctype, "cluster": cluster, "http": code,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if code == 200 and "t.me" in url:
        t = re.search(r'property="og:title" content="([^"]*)"', body)
        d = re.search(r'property="og:description" content="([^"]*)"', body)
        ent["og_title"] = htmlmod.unescape(t.group(1)) if t else None
        ent["og_desc"] = htmlmod.unescape(d.group(1))[:400] if d else None
        m = re.search(r'([\d.,KMkm]+)\s*(?:subscribers|members|subscriber)', body)
        ent["members"] = m.group(1) if m else None
    RESULTS["channels"][cid] = ent
    print(" ", cid, code, ent.get("og_title","")[:40] if code==200 else "")
    time.sleep(2.5)

# deep public previews (t.me/s/<name>) — all messages with prices
print("── Part 1b: deep s/ previews")
for cid in S_PREVIEW:
    code, body, _ = fetch("https://t.me/s/" + cid)
    if code != 200:
        RESULTS["channels"].setdefault(cid, {})["s_preview"] = {"http": code}
        print(" ", cid, code, "(no preview)"); time.sleep(2.5); continue
    msgs = re.findall(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', body, re.S)
    dates = re.findall(r'<time datetime="([^"]+)"', body)
    parsed = []
    for i, m in enumerate(msgs):
        txt = clean(m)
        pl = price_lines(m)
        if txt:
            parsed.append({"text": txt[:500], "prices": pl,
                           "date": dates[i] if i < len(dates) else None})
    RESULTS["channels"].setdefault(cid, {})["s_preview"] = {
        "http": code, "n_messages": len(parsed),
        "messages": parsed[-25:],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(" ", cid, code, "msgs:", len(parsed))
    time.sleep(2.5)

# ═══ PART 2: stackvault.shop full catalog ═══
print("── Part 2: stackvault.shop")
for path in ["/products", "/"]:
    code, body, _ = fetch("https://stackvault.shop" + path)
    if code == 200:
        # product blocks: name + price pairs
        prods = re.findall(
            r'<(?:a|h[23])[^>]*href="(/product/[^"]+)"[^>]*>.*?</[^>]+>(?:\s*<[^>]+>)*\s*([^<]{3,60})', body, re.S)
        priced = []
        for pm in re.finditer(r'href="(/product/[^"]+)"(.{0,900}?)(\$[\d.,]+)', body, re.S):
            name = clean(pm.group(2))[:80]
            priced.append({"slug": pm.group(1), "name": name, "price": pm.group(3)})
        # dedupe by slug+price
        seen, uniq = set(), []
        for p in priced:
            k = (p["slug"], p["price"])
            if k not in seen: seen.add(k); uniq.append(p)
        RESULTS["sites"]["stackvault.shop" + path] = {
            "http": code, "n_products": len(uniq), "products": uniq,
            "price_lines": price_lines(body, 60),
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        print(" ", path, code, "products:", len(uniq))
    else:
        RESULTS["sites"]["stackvault.shop" + path] = {"http": code}
        print(" ", path, code)
    time.sleep(3)

# ═══ PART 3: turgame.com discovery + category extraction ═══
print("── Part 3: turgame.com")
code, body, _ = fetch("https://www.turgame.com/")
catlinks = []
if code == 200:
    for m in re.finditer(r'href="(https?://www\.turgame\.com/([a-z0-9-]+))"', body):
        u, slug = m.group(1), m.group(2)
        if any(k in slug for k in ["gift", "card", "steam", "playstation", "psn", "xbox",
                                    "google-play", "apple", "itunes", "razer", "netflix",
                                    "spotify", "roblox", "nintendo", "amazon", "game"]):
            if u not in [c[0] for c in catlinks]:
                catlinks.append((u, slug))
    RESULTS["sites"]["turgame_home"] = {"http": code,
        "candidate_links": [u for u, s in catlinks][:40],
        "price_lines": price_lines(body, 30),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print("  home", code, "candidate links:", len(catlinks))
else:
    RESULTS["sites"]["turgame_home"] = {"http": code}
    print("  home", code)
time.sleep(3)

# fetch top categories (max 8) and extract product+price
turgame_prods = []
for u, slug in catlinks[:8]:
    code, body, _ = fetch(u)
    if code == 200:
        for pm in re.finditer(r'href="(https?://www\.turgame\.com/[a-z0-9-]{6,})"[^>]*>(.{0,600}?)([\d.,]+\s*(?:USD|EUR|TRY|₺|\$|€))', body, re.S):
            name = clean(pm.group(2))[:90]
            if name:
                turgame_prods.append({"url": pm.group(1), "name": name, "price": clean(pm.group(3))})
    print("  cat", slug, code)
    time.sleep(3)
seen, uniq = set(), []
for p in turgame_prods:
    if p["url"] not in seen: seen.add(p["url"]); uniq.append(p)
RESULTS["sites"]["turgame_categories"] = {
    "n_products": len(uniq), "products": uniq[:200],
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
print("  turgame unique products:", len(uniq))

# ═══ PART 4: keyforsteam.de anchor pages ═══
print("── Part 4: keyforsteam.de anchors")
KFS = [
    ("SKU-SW001", "https://www.keyforsteam.de/windows-11-pro-key-kaufen-preisvergleich/"),
    ("SKU-SW007", "https://www.keyforsteam.de/microsoft-office-2024-pro-plus-cd-key-kaufen-preisvergleich/"),
    ("SKU-SW004?", "https://www.keyforsteam.de/microsoft-office-2021-pro-plus-cd-key-kaufen-preisvergleich/"),
]
for sku, u in KFS:
    code, body, _ = fetch(u)
    entry = {"http": code, "url": u,
             "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if code == 200:
        t = re.search(r"<title>([^<]*)</title>", body)
        entry["title"] = clean(t.group(1)) if t else None
        entry["price_lines"] = price_lines(body, 25)
    RESULTS["sites"]["keyforsteam_" + sku] = entry
    print(" ", sku, code, entry.get("title", "")[:60])
    time.sleep(3)

# ═══ PART 5: ggsel.net catalog pages ═══
print("── Part 5: ggsel.net")
for slug in ["chatgpt-plus", "netflix", "spotify", "windows"]:
    u = "https://ggsel.net/catalog/" + slug
    code, body, _ = fetch(u)
    entry = {"http": code, "url": u,
             "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if code == 200:
        entry["price_lines"] = price_lines(body, 30)
        t = re.search(r"<title>([^<]*)</title>", body)
        entry["title"] = clean(t.group(1)) if t else None
    RESULTS["sites"]["ggsel_" + slug] = entry
    print(" ", slug, code, entry.get("title", "")[:55])
    time.sleep(3)

# ═══ PART 6: plati.market + z2u probes ═══
print("── Part 6: plati/z2u probes")
for name, u in [("plati_popular", "https://plati.market/list?sort=popular"),
                ("z2u_home", "https://www.z2u.com/"),
                ("fazercards_en", "https://reseller.fazercards.com/en"),
                ("turgame_wholesale", "https://wholesale.turgame.com")]:
    code, body, _ = fetch(u)
    entry = {"http": code, "url": u,
             "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if code == 200:
        t = re.search(r"<title>([^<]*)</title>", body)
        entry["title"] = clean(t.group(1)) if t else None
        entry["price_lines"] = price_lines(body, 30)
    RESULTS["sites"][name] = entry
    print(" ", name, code, entry.get("title", "")[:55])
    time.sleep(3)

RESULTS["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
json.dump(RESULTS, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_msgs = sum(v.get("s_preview", {}).get("n_messages", 0) for v in RESULTS["channels"].values() if isinstance(v, dict))
print("DONE. channels:", len(RESULTS["channels"]), "| preview msgs:", n_msgs,
      "| sites:", len(RESULTS["sites"]), "->", OUT)
