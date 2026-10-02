#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-MASTER-RELEASE: fresh verification sweep for PROJECT MASTER REFERENCE FILE
Passive OSINT only — public endpoints, no auth, no interaction.
Timestamp reference: 2026-10-02T02:49+03:00 (Asia/Aden) / 2026-10-01T23:49Z
Output: research/sv_master_refresh_20261002.json
"""
import json, re, time, urllib.request, gzip
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_master_refresh_20261002.json"

def fetch(url, timeout=25, hdrs=None):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
         "Accept-Encoding": "gzip"}
    if hdrs:
        h.update(hdrs)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)[:200]

HTML_ENT = {"&amp;": "&", "&#036;": "$", "&#39;": "'", "&quot;": '"', "&lt;": "<",
            "&gt;": ">", "&#039;": "'", "&nbsp;": " ", "&#160;": " "}

def clean(t):
    for k, v in HTML_ENT.items():
        t = t.replace(k, v)
    return t

MSG_RE = re.compile(
    r'<div class="tgme_widget_message_wrap js-widget_message_wrap"[^>]*>.*?'
    r'data-post="([^"]+)"[^>]*>.*?'
    r'<time datetime="([^"]+)"[^>]*>.*?'
    r'<div class="tgme_widget_message_text js-message_text[^"]*" dir="auto">(.*?)</div>',
    re.S)

def strip_tags(html):
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</?(?:b|i|u|s|em|strong|a|span|code|pre|tg-spoiler)[^>]*>', '', html)
    html = re.sub(r'<[^>]+>', '', html)
    return html

def tg_page1(channel):
    status, html = fetch(f"https://t.me/s/{channel}")
    if status != 200:
        return {"http": status, "messages": []}
    msgs = [{"post": m.group(1), "date": m.group(2),
             "text": clean(strip_tags(m.group(3))).strip()} for m in MSG_RE.finditer(html)]
    dates = [m["date"][:10] for m in msgs]
    return {"http": status, "n": len(msgs),
            "newest": max(dates) if dates else None,
            "oldest": min(dates) if dates else None,
            "latest3": [{"date": m["date"][:16], "text": m["text"][:220]} for m in msgs[-3:]]}

def sub_count(channel):
    status, html = fetch(f"https://t.me/{channel}")
    if status != 200:
        return None
    m = re.search(r'tgme_page_extra">([^<]+)</span>', html)
    return clean(m.group(1)).strip() if m else None

result = {"execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
          "reference_timestamp": "2026-10-02T02:49+03:00",
          "probes": {}}

# --- 1) StackVault live catalog ---
print("[1] stackvault.shop + decohomz catalog ...")
st, html = fetch("https://stackvault.shop")
result["probes"]["stackvault_shop"] = {"http": st, "server_alive": st == 200}
st, body = fetch("https://decohomz.com/sv-api/products")
cat = {"http": st}
if st == 200 and body.lstrip()[:1] in "[{":
    try:
        j = json.loads(body)
        items = j if isinstance(j, list) else j.get("products") or j.get("data") or []
        cat["n_products"] = len(items)
        from collections import Counter
        pref = Counter()
        for it in items:
            pid = str(it.get("id") or it.get("_id") or "")
            pref[pid.split("_")[0] + "_" if "_" in pid else "other"] += 1
        cat["prefix_counts"] = dict(pref.most_common(6))
        withstock = sum(1 for it in items if (it.get("stock") or 0) or 0)
        cat["in_stock"] = withstock
        costs = [it.get("costPrice") for it in items if it.get("costPrice") is not None]
        cat["cost_leak_present"] = len(costs) == len(items) and len(items) > 0
        cat["cost_price_sample"] = costs[:3]
    except Exception as e:
        cat["parse_error"] = str(e)[:120]
result["probes"]["sv_catalog"] = cat
print(f"    stackvault={result['probes']['stackvault_shop']['http']} catalog={cat}")

# --- 2) Telegram channels page-1 ---
CHANNELS = ["AiVerseXHub", "Evo_Era_updates", "AISUBSID", "fork_bot_channel", "teamsoclo",
            "ProdSellerOfficial", "HitMeowShop", "gemini12pro_channel", "Gt_Verified",
            "acczone_logs", "Gemini_Shop_Robot", "Mike_E_0"]
print("[2] Telegram page-1 sweep (12 channels) ...")
result["probes"]["tg"] = {}
for ch in CHANNELS:
    info = tg_page1(ch)
    info["subscribers_og"] = sub_count(ch)
    result["probes"]["tg"][ch] = info
    print(f"    {ch:22} http={info['http']} newest={info['newest']} subs={info['subscribers_og']}")
    time.sleep(0.7)

# --- 3) Gateways & sites ---
print("[3] Gateways & sites ...")
sites = {
    "gpt.status": "https://gpt.teamsoclo.site/api/status",
    "gpt.pricing_version": "https://gpt.teamsoclo.site/api/pricing",
    "redeem.teamsoclo.site": "https://redeem.teamsoclo.site/",
    "jcc.workers.dev": "https://jcc.tokensunlimited.workers.dev/",
    "nikokey.com": "https://nikokey.com/",
    "aiversehub.store": "https://aiversehub.store/",
    "teamsoclo.site_root": "https://teamsoclo.site/",
}
result["probes"]["sites"] = {}
for name, url in sites.items():
    st, body = fetch(url, timeout=20)
    info = {"http": st, "size": len(body)}
    if st == 200:
        if "pricing" in name:
            try:
                j = json.loads(body)
                info["pricing_version"] = j.get("pricing_version")
                info["n_models"] = len(j.get("data") or [])
            except Exception:
                info["body_head"] = body[:120]
        else:
            t = re.search(r"<title>([^<]*)</title>", body)
            info["title"] = clean(t.group(1)) if t else ""
    result["probes"]["sites"][name] = info
    print(f"    {name:26} {info}")
    time.sleep(0.7)

with open(OUT, "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(f"\nSAVED {OUT}")
