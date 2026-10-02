#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5d | Extended Telegram s/ preview wave — channels not yet deep-probed.
Quota-free HTTP. Targets: §19 entities without history data yet.
Pacing: 2.5s between requests (lesson: aggressive throttling).
Output: research/b3_tg_extended.json
"""
import json, os, re, time, urllib.request, gzip, io

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "research", "b3_tg_extended.json")

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html", "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            return r.status, data.decode("utf-8", "ignore")
    except Exception as e:
        return None, str(e)[:120]

MSG_RE = re.compile(
    r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>', re.S)
TAG_RE = re.compile(r"<[^>]+>")
DATE_RE = re.compile(r'<time datetime="([^"]+)"')

def extract_messages(html):
    msgs = []
    # split by message blocks to associate dates
    blocks = re.split(r'<div class="tgme_widget_message ', html)
    for b in blocks[1:]:
        tm = MSG_RE.search(b)
        if not tm: continue
        text = TAG_RE.sub(" ", tm.group(1))
        text = re.sub(r"\s+", " ", text).strip()
        if not text: continue
        dm = DATE_RE.search(b)
        date = dm.group(1) if dm else ""
        msgs.append({"text": text[:600], "date": date})
    return msgs

PRICE_RE = re.compile(r"\$\s?([0-9]+(?:\.[0-9]{1,3})?)|([0-9]+(?:\.[0-9]{1,2})?)\s?(?:USDT|USD)")

def has_price(m):
    return bool(PRICE_RE.search(m["text"]))

# targets: §19 entities NOT yet in b3_channel_history (5 done) — channels/chats only (bots have no s/)
DONE = {"ProdSellerOfficial", "Evo_Era_updates", "gemini12pro_channel", "HitMeowShop", "AISUBSID"}
raw = json.load(open(os.path.join(BASE, "data", "research", "mec2_channels_raw.json"), encoding="utf-8"))

targets = []
for eid, e in raw["entities"].items():
    if eid in DONE: continue
    if e.get("type") == "website": continue
    # bots don't have public s/ preview (they're chats) — but try channels only
    if e.get("type") in ("channel", "chat", "logs"): 
        targets.append((eid, e.get("url", "")))

print(f"targets: {len(targets)}")
results = {}
for eid, url in targets:
    if not url: continue
    s_url = url.replace("t.me/", "t.me/s/")
    status, html = fetch(s_url)
    time.sleep(2.5)
    if status != 200 or not isinstance(html, str) or len(html) < 500:
        results[eid] = {"http": status, "n_messages": 0, "messages": [], "note": str(html)[:80]}
        print(f"  {eid}: {status} — skip")
        continue
    msgs = extract_messages(html)
    priced = [m for m in msgs if has_price(m)]
    results[eid] = {"http": status, "url": s_url, "n_messages": len(msgs),
                    "n_priced": len(priced), "messages": msgs[:20], "priced": priced[:12]}
    print(f"  {eid}: {status} | msgs={len(msgs)} priced={len(priced)}")

out = {"run": "MEC-2.5d extended TG s/ wave", "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
       "results": results}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

total_priced = sum(r.get("n_priced", 0) for r in results.values())
total_msgs = sum(r.get("n_messages", 0) for r in results.values())
print(f"\nDONE: {len(results)} entities | {total_msgs} messages | {total_priced} priced")
