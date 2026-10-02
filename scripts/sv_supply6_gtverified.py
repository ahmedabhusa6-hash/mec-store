#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-6b: probe @GT_VERIFIED (AiVerseX bulk arm) + related leads."""
import json, re, time, urllib.request, gzip
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_supply6_gtverified.json"

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)

def og(username):
    status, html = fetch(f"https://t.me/{username}")
    if status != 200:
        return {"http": status}
    def meta(prop):
        m = re.search(rf'<meta property="{prop}" content="([^"]*)"', html)
        return m.group(1) if m else ""
    extra = ""
    m = re.search(r'<div class="tgme_channel_info_header_subtitle[^"]*"[^>]*>(.*?)</div>', html, re.S)
    if m:
        extra = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return {"http": status, "og_title": meta("og:title"),
            "og_desc": meta("og:description"), "subtitle": extra[:200]}

def preview(channel, pages=3):
    """t.me/s/ preview with light pagination."""
    msgs, seen = [], set()
    status, html = fetch(f"https://t.me/s/{channel}")
    if status != 200:
        return {"http": status, "messages": []}
    MSG_RE = re.compile(
        r'data-post="([^"]+)"[^>]*>.*?<time datetime="([^"]+)"[^>]*>.*?'
        r'<div class="tgme_widget_message_text js-message_text[^"]*" dir="auto">(.*?)</div>', re.S)
    def strip(h):
        h = re.sub(r'<br\s*/?>', '\n', h)
        h = re.sub(r'<[^>]+>', '', h)
        for k, v in {"&amp;": "&", "&#036;": "$", "&#33;": "!", "&#39;": "'",
                     "&quot;": '"', "&lt;": "<", "&gt;": ">", "&nbsp;": " "}.items():
            h = h.replace(k, v)
        return h.strip()
    for m in MSG_RE.finditer(html):
        pid = m.group(1)
        if pid not in seen:
            seen.add(pid)
            msgs.append({"post": pid, "date": m.group(2), "text": strip(m.group(3))})
    for _ in range(pages - 1):
        if not msgs:
            break
        last = re.sub(r"\D", "", msgs[-1]["post"].split("/")[-1])
        if not last:
            break
        status, html = fetch(f"https://t.me/s/{channel}?before={last}")
        if status != 200:
            break
        batch = []
        for m in MSG_RE.finditer(html):
            pid = m.group(1)
            if pid not in seen:
                seen.add(pid)
                batch.append({"post": pid, "date": m.group(2), "text": strip(m.group(3))})
        if not batch:
            break
        msgs.extend(batch)
        time.sleep(1.0)
    msgs.sort(key=lambda m: m["date"])
    return {"http": 200, "n_messages": len(msgs), "messages": msgs}

result = {"generated": datetime.now(timezone.utc).isoformat(), "probes": {}}

# 1) @GT_VERIFIED — AiVerseX bulk-sales contact
for u in ["GT_VERIFIED"]:
    print(f"[+] og @{u}")
    result["probes"][f"og_{u}"] = og(u)
    print("   ", result["probes"][f"og_{u}"])

# 2) if GT_VERIFIED is a channel, pull preview
t = result["probes"]["og_GT_VERIFIED"].get("og_title", "")
if t and "Contact" not in t:
    print("[+] preview GT_VERIFIED ...")
    result["probes"]["preview_GT_VERIFIED"] = preview("GT_VERIFIED", pages=4)
    print("    msgs:", result["probes"]["preview_GT_VERIFIED"].get("n_messages"))
else:
    # it's a user/bot — try common channel variants
    for ch in ["GT_VERIFIED", "gt_verified", "GTVerified"]:
        print(f"[+] trying channel preview: {ch}")
        p = preview(ch, pages=4)
        if p.get("http") == 200 and p.get("n_messages", 0) > 0:
            result["probes"][f"preview_{ch}"] = p
            print("    msgs:", p["n_messages"])
        time.sleep(0.8)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(f"[✓] saved -> {OUT}")
