#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-SUPPLY-7: Deep expansion of the supply chain map
  A) gemini12pro_channel (Chinese 142K hub) — FULL paginated history = advertiser census
  B) teamsoclo (VN) — deep history for reseller structure
  C) New node probes: Gemini_Shop_Robot, AIXpress_Bot, stlzect, nevakeystore_bot,
     aiversehub.store (AiVerseX's own domain from July ad), gemini12pro bot
Passive OSINT — public pages only.
"""
import json, re, time, urllib.request, urllib.error, gzip, socket
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_supply7_map_expansion.json"
ENT = {"&amp;": "&", "&#036;": "$", "&#33;": "!", "&#39;": "'", "&quot;": '"',
       "&lt;": "<", "&gt;": ">", "&nbsp;": " ", "&#160;": " ", "&hearts;": "♥"}

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,vi;q=0.8", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)[:120]

def clean(t):
    for k, v in ENT.items():
        t = t.replace(k, v)
    return t

MSG_RE = re.compile(
    r'data-post="([^"]+)"[^>]*>.*?<time datetime="([^"]+)"[^>]*>.*?'
    r'<div class="tgme_widget_message_text js-message_text[^"]*" dir="auto">(.*?)</div>', re.S)

def strip_tags(html):
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</?(?:b|i|u|s|em|strong|a|span|code|pre|tg-spoiler)[^>]*>', '', html)
    html = re.sub(r'<[^>]+>', '', html)
    return clean(html).strip()

def parse_msgs(html):
    out = []
    for m in MSG_RE.finditer(html):
        out.append({"post": m.group(1), "date": m.group(2), "text": strip_tags(m.group(3))})
    return out

def deep_history(channel, max_pages=25, pause=1.0):
    all_msgs, seen = [], set()
    status, html = fetch(f"https://t.me/s/{channel}")
    if status != 200:
        return {"http": status, "error": "no preview", "messages": []}
    for m in parse_msgs(html):
        if m["post"] not in seen:
            seen.add(m["post"]); all_msgs.append(m)
    pages = 1
    while pages < max_pages and all_msgs:
        last = re.sub(r"\D", "", all_msgs[-1]["post"].split("/")[-1])
        if not last:
            break
        status, html = fetch(f"https://t.me/s/{channel}?before={last}")
        if status != 200:
            break
        batch = [m for m in parse_msgs(html) if m["post"] not in seen]
        if not batch:
            break
        for m in batch:
            seen.add(m["post"]); all_msgs.append(m)
        pages += 1
        time.sleep(pause)
    all_msgs.sort(key=lambda m: m["date"])
    return {"http": 200, "n_messages": len(all_msgs), "pages": pages, "messages": all_msgs}

def og(username):
    status, html = fetch(f"https://t.me/{username}")
    if status != 200:
        return {"http": status}
    def meta(prop):
        m = re.search(rf'<meta property="{prop}" content="([^"]*)"', html)
        return clean(m.group(1)) if m else ""
    return {"http": status, "og_title": meta("og:title"), "og_desc": meta("og:description")[:250]}

def http_probe(url):
    status, body = fetch(url)
    title = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", body[:5000], re.S | re.I)
    if m:
        title = clean(m.group(1))[:120]
    return {"status": status, "title": title, "size": len(body)}

def dns_probe(host):
    try:
        ips = socket.gethostbyname_ex(host)[2]
        return {"ips": ips}
    except Exception as e:
        return {"error": str(e)[:80]}

result = {"generated": datetime.now(timezone.utc).isoformat()}

# ---- A) Chinese hub deep history ----
print("[A] gemini12pro_channel deep history ...")
result["gemini12pro_channel"] = deep_history("gemini12pro_channel", max_pages=25)
print("    msgs:", result["gemini12pro_channel"].get("n_messages"),
      "pages:", result["gemini12pro_channel"].get("pages"))

# ---- B) teamsoclo deep history ----
print("[B] teamsoclo deep history ...")
result["teamsoclo"] = deep_history("teamsoclo", max_pages=18)
print("    msgs:", result["teamsoclo"].get("n_messages"),
      "pages:", result["teamsoclo"].get("pages"))

# ---- C) new node OG probes ----
probes = ["Gemini_Shop_Robot", "Gemini_shop_Robot", "AIXpress_Bot", "stlzect",
          "nevakeystore_bot", "gemini12pro", "AIVerseXSupport", "acczone_logs",
          "verifierg"]
result["og_probes"] = {}
for u in probes:
    print(f"[C] og @{u}")
    result["og_probes"][u] = og(u)
    print("   ", result["og_probes"][u])
    time.sleep(0.8)

# ---- D) AiVerseX store domain from July ad ----
result["aiversehub_store"] = {
    "dns": dns_probe("aiversehub.store"),
    "http": http_probe("https://aiversehub.store/"),
    "gemini_path": http_probe("https://aiversehub.store/gemini"),
}
print("[D] aiversehub.store:", result["aiversehub_store"]["dns"], result["aiversehub_store"]["http"]["status"])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(f"[✓] saved -> {OUT}")
