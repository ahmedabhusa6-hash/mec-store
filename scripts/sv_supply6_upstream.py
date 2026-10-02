#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-SUPPLY-6: Upstream sourcing intelligence for AiVerseX Hub & HitMeowShop
Passive OSINT only — public Telegram preview pages (t.me/s/) + public og data.
Goal: find WHERE they buy from (factory/wholesale upstream), via:
  - full channel history (paginated t.me/s/ before=)
  - supplier keyword mentions
  - product format fingerprints (links vs accounts vs API keys)
  - stock/sold counters, price points
"""
import json, re, time, urllib.request, urllib.error, gzip, io
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_supply6_upstream.json"

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)

HTML_ENT = {"&amp;": "&", "&#036;": "$", "&#33;": "!", "&#39;": "'", "&quot;": '"',
            "&lt;": "<", "&gt;": ">", "&#039;": "'", "&nbsp;": " ", "&#160;": " "}

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

def parse_channel_preview(html):
    msgs = []
    for m in MSG_RE.finditer(html):
        post_id, dt, body = m.group(1), m.group(2), strip_tags(m.group(3))
        msgs.append({"post": post_id, "date": dt, "text": clean(body).strip()})
    return msgs

def grab_history(channel, max_pages=12):
    """Pull t.me/s/<channel> with backward pagination."""
    all_msgs, seen = [], set()
    url = f"https://t.me/s/{channel}"
    status, html = fetch(url)
    if status != 200:
        return {"http": status, "error": html[:200], "messages": []}
    msgs = parse_channel_preview(html)
    all_msgs.extend(msgs)
    for mid in [m["post"] for m in msgs]:
        seen.add(mid)
    pages = 1
    while pages < max_pages:
        if not all_msgs:
            break
        last_num = all_msgs[-1]["post"].split("/")[-1]
        last_num = re.sub(r"\D", "", last_num)
        if not last_num:
            break
        status, html = fetch(f"https://t.me/s/{channel}?before={last_num}")
        if status != 200:
            break
        batch = parse_channel_preview(html)
        new = [m for m in batch if m["post"] not in seen]
        if not new:
            break
        for m in new:
            seen.add(m["post"])
        all_msgs.extend(new)
        pages += 1
        time.sleep(1.2)
    all_msgs.sort(key=lambda m: m["date"])
    return {"http": 200, "n_messages": len(all_msgs), "messages": all_msgs}

def og_probe(username):
    status, html = fetch(f"https://t.me/{username}")
    if status != 200:
        return {"http": status}
    def meta(prop):
        m = re.search(rf'<meta property="{prop}" content="([^"]*)"', html)
        return clean(m.group(1)) if m else ""
    return {"http": status, "og_title": meta("og:title"), "og_desc": meta("og:description")}

# ---- supplier keyword scan ----
SUPPLIER_PATTERNS = {
    "teamsoclo": r"teamsoclo|sóc\s*lọ|soc\s*lo",
    "prodseller": r"prodseller|prod\s*seller|sookbit",
    "evo_era": r"evo[\s_-]?era|evolution[\s_-]?era|adham",
    "aisubsid": r"aisubs|ai\s*subs",
    "hitmeow": r"hitmeow|premikey|vahnix",
    "aiversex": r"aiversex|ai\s*verse",
    "gemini_farm_terms": r"redeem|promo\s*code|activation\s*url|reactivat",
    "otp_providers": r"smspool|viotp|2fa\.live|sms-activate|5sim|tiger\s*text",
    "reseller_lang": r"reseller|supplier|wholesal|distributor|vendor|bulk\s*from|buy\s*from",
    "factory_lang": r"our\s*(factory|farm|method|panel|infrastructure)|we\s*(generate|produce|manufacture|create)\b",
    "payment": r"usdt|trc20|binance|momo|gcash|gpay|apple\s*pay|crypto",
}

def scan_keywords(text):
    hits = {}
    tl = text.lower()
    for name, pat in SUPPLIER_PATTERNS.items():
        m = re.search(pat, tl)
        if m:
            hits[name] = m.group(0)
    return hits

def main():
    result = {"generated": datetime.now(timezone.utc).isoformat(), "channels": {}, "og_probes": {}, "keyword_hits": {}}

    for ch in ["AiVerseXHub", "HitMeowShop"]:
        print(f"[+] grabbing history: {ch} ...")
        hist = grab_history(ch, max_pages=14)
        result["channels"][ch] = hist
        print(f"    -> http={hist.get('http')} msgs={hist.get('n_messages', 0)}")

    for u in ["AIVerseXBot_support", "AIVerseXBot", "AiVerseXBot", "PremikeyBot", "Premikey_Bot",
               "HitmeowSupport", "vahnix"]:
        print(f"[+] og probe: @{u}")
        result["og_probes"][u] = og_probe(u)
        time.sleep(0.8)

    for ch, hist in result["channels"].items():
        hits = []
        for m in hist.get("messages", []):
            kw = scan_keywords(m["text"])
            if any(k in kw for k in list(SUPPLIER_PATTERNS)):
                hits.append({"post": m["post"], "date": m["date"], "matched": kw,
                             "text": m["text"][:500]})
        result["keyword_hits"][ch] = hits
        print(f"[kw] {ch}: {len(hits)} messages with supplier/platform keywords")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"[✓] saved -> {OUT}")

if __name__ == "__main__":
    main()
