#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-SUPPLY-9: Penetration deepening + FULL price refresh + trusted-links verification
Passive OSINT only — public t.me/s/ previews, og metadata, public GET pages, public New API status/pricing endpoints.
Usage: python3 sv_supply9_deepen.py <phase>   # handles | pixel | gateways | prices
Output: research/sv_supply9_deepen.json (phases merge into one file)
"""
import json, re, sys, time, urllib.request, urllib.error, gzip
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_supply9_deepen.json"

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

def grab_history(channel, max_pages=14):
    all_msgs, seen = [], set()
    status, html = fetch(f"https://t.me/s/{channel}")
    if status != 200:
        return {"http": status, "error": str(html)[:200], "messages": [], "pages": 0}
    msgs = parse_channel_preview(html)
    all_msgs.extend(msgs)
    for m in msgs:
        seen.add(m["post"])
    pages = 1
    while pages < max_pages:
        if not all_msgs:
            break
        last_num = re.sub(r"\D", "", all_msgs[-1]["post"].split("/")[-1])
        if not last_num:
            break
        status, html = fetch(f"https://t.me/s/{channel}?before={last_num}")
        if status != 200:
            break
        msgs = parse_channel_preview(html)
        new = [m for m in msgs if m["post"] not in seen]
        if not new:
            break
        for m in new:
            seen.add(m["post"])
        all_msgs.extend(new)
        pages += 1
        time.sleep(1.0)
    all_msgs.sort(key=lambda m: m["date"])
    return {"http": 200, "pages": pages, "n_messages": len(all_msgs),
            "first": all_msgs[0]["date"][:10] if all_msgs else None,
            "last": all_msgs[-1]["date"][:10] if all_msgs else None,
            "messages": all_msgs}

def og_probe(handle):
    status, html = fetch(f"https://t.me/{handle}")
    if status != 200:
        return {"http": status, "error": str(html)[:150]}
    title = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    desc = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    sub = re.search(r'tgme_page_extra">([^<]+)</span>', html)
    return {"http": status,
            "og_title": clean(title.group(1)) if title else "",
            "og_desc": clean(desc.group(1))[:400] if desc else "",
            "extra": clean(sub.group(1)).strip() if sub else ""}

def load_out():
    try:
        with open(OUT) as f:
            return json.load(f)
    except Exception:
        return {"generated": datetime.now(timezone.utc).isoformat()}

def save_out(d):
    d["generated"] = datetime.now(timezone.utc).isoformat()
    with open(OUT, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

# ============================================================ PHASE: handles
# Fresh verification of EVERY link in the user's 30-link message (trusted-links table)
USER_LINKS = [
    "gemini12pro_channel", "gemini12pro", "gemini12pro_bot", "fork_bot_channel",
    "ver_pixel_bot", "leo_dfx", "HitMeowShop", "PremiKeyBot", "HitmeowSupport",
    "teamsoclo", "AiVerseXHub", "AiVerseXBot", "AIVerseXSupport", "Gt_Verified",
    "GoChecker_Bot", "Gemini_Shop_Robot", "AIXpress_Bot", "RichAIStoreBot",
    "AISUBSID", "Aisubsglobalbot", "ProdSellerOfficial", "ProdSellerBot",
    "Evo_Era_updates", "Evolution_Era_bot", "adham_H11", "acczone_logs",
    "Acczone_Store_bot", "acczone_gemini_link_bot", "Mike_E_0",
]

def phase_handles():
    d = load_out()
    probes = {}
    for h in USER_LINKS:
        probes[h] = og_probe(h)
        print(f"  {h}: {probes[h].get('http')} | {probes[h].get('og_title','')[:40]} | {probes[h].get('extra','')}")
        time.sleep(0.8)
    d["handles"] = probes
    save_out(d)
    print(f"OK {len(probes)} handles verified")

# ============================================================ PHASE: pixel
def phase_pixel():
    d = load_out()
    print("[+] gemini12pro_channel deep pagination (14 pages)...")
    d["pixel_deep"] = {"gemini12pro_channel": grab_history("gemini12pro_channel", 14)}
    g = d["pixel_deep"]["gemini12pro_channel"]
    print(f"    → {g.get('n_messages')} msgs | {g.get('first')} → {g.get('last')}")
    # nikokey.com full-page price scan
    print("[+] nikokey.com price/keyword scan...")
    status, html = fetch("https://nikokey.com", timeout=30)
    if status == 200:
        text = clean(strip_tags(html))
        prices = re.findall(r'(?:US?\$|\$|USD|CNY|¥|￥)\s?\d+(?:\.\d+)?', text)
        d["pixel_deep"]["nikokey"] = {
            "http": 200, "size": len(html),
            "title": (re.search(r"<title>([^<]*)</title>", html) or [None, ""])[1] if re.search(r"<title>([^<]*)</title>", html) else "",
            "prices_found": list(dict.fromkeys(prices))[:40],
            "kw": {k: (k.lower() in text.lower()) for k in
                   ["pixel", "gemini", "alipay", "usdt", "upgrade", "niko", "key", "plan", "price"]},
        }
        print(f"    → 200, {len(html)}B, prices={list(dict.fromkeys(prices))[:10]}")
    else:
        d["pixel_deep"]["nikokey"] = {"http": status}
        print(f"    → {status}")
    save_out(d)
    print("OK pixel phase")

# ============================================================ PHASE: gateways
def phase_gateways():
    d = load_out()
    gw = {}
    targets = [
        ("gpt.status", "https://gpt.teamsoclo.site/api/status"),
        ("gpt.pricing", "https://gpt.teamsoclo.site/api/pricing"),
        ("gpt.pricing_v2", "https://gpt.teamsoclo.site/api/pricing/0"),
        ("gpt.models", "https://gpt.teamsoclo.site/v1/models"),
        ("gpt.home", "https://gpt.teamsoclo.site/"),
        ("jcc.status", "https://jcc.tokensunlimited.workers.dev/api/status"),
        ("jcc.pricing", "https://jcc.tokensunlimited.workers.dev/api/pricing"),
        ("jcc.home", "https://jcc.tokensunlimited.workers.dev/"),
        ("tu.home", "https://tokensunlimited.workers.dev/"),
        ("redeem.home", "https://redeem.teamsoclo.site/"),
        ("niko.api", "https://nikokey.com/api/status"),
    ]
    for name, url in targets:
        status, body = fetch(url, timeout=20)
        info = {"http": status, "size": len(body)}
        if status == 200:
            if body.lstrip()[:1] in "{[":
                try:
                    j = json.loads(body)
                    info["json_keys"] = list(j.keys())[:15] if isinstance(j, dict) else f"list[{len(j)}]"
                    if isinstance(j, dict) and "data" in j and isinstance(j["data"], list):
                        info["n_data"] = len(j["data"])
                        info["sample"] = j["data"][:3]
                    elif isinstance(j, dict):
                        info["raw"] = json.dumps(j, ensure_ascii=False)[:600]
                except Exception:
                    info["body_head"] = body[:300]
            else:
                info["title"] = (re.search(r"<title>([^<]*)</title>", body) or [None, ""])[1] if re.search(r"<title>([^<]*)</title>", body) else ""
                info["body_head"] = clean(body[:300])
        gw[name] = info
        print(f"  {name}: {status} {info.get('json_keys') or info.get('title') or info.get('body_head','')[:60] if status==200 else ''}")
        time.sleep(0.8)
    d["gateways_deep"] = gw
    save_out(d)
    print("OK gateway phase")

# ============================================================ PHASE: prices
PRICE_CHANNELS = ["AiVerseXHub", "Evo_Era_updates", "AISUBSID", "fork_bot_channel",
                  "teamsoclo", "ProdSellerOfficial", "acczone_logs", "gemini12pro_channel",
                  "HitMeowShop", "Gt_Verified"]
PRICE_RE = re.compile(r'(?:US?D?\s?\$|\$|₹|Rp|đ|₽)\s?\d[\d,]*(?:\.\d+)?', re.I)

def phase_prices():
    d = load_out()
    fresh = {}
    for ch in PRICE_CHANNELS:
        status, html = fetch(f"https://t.me/s/{ch}")
        msgs = parse_channel_preview(html) if status == 200 else []
        fresh[ch] = {"http": status, "n_latest": len(msgs),
                     "newest_date": msgs[0]["date"][:10] if msgs else None,
                     "latest": msgs[:8]}
        print(f"  {ch}: {status} | latest {fresh[ch]['newest_date']} | {len(msgs)} msgs on page1")
        time.sleep(0.8)
    d["price_refresh"] = fresh
    # price extraction across ALL stored histories (supply8 + supply9)
    corpus = {}
    def add_corpus(src, msgs):
        for m in msgs:
            t = m.get("text", "")
            hits = PRICE_RE.findall(t)
            if hits:
                corpus.setdefault(src, []).append({"date": m.get("date", "")[:10],
                                                   "post": m.get("post", ""),
                                                   "prices": hits,
                                                   "text": t[:280]})
    s8 = load_prev("/home/z/my-project/research/sv_supply8_deep.json")
    for grp, node in s8.items():
        if not isinstance(node, dict):
            continue
        for k, v in node.items():
            if isinstance(v, dict) and "messages" in v:
                add_corpus(f"s8.{grp}.{k}", v["messages"])
            elif isinstance(v, dict) and "history" in v and isinstance(v["history"], dict) and "messages" in v["history"]:
                add_corpus(f"s8.{grp}.{k}", v["history"]["messages"])
    s7 = load_prev("/home/z/my-project/research/sv_supply7_map_expansion.json")
    for k, v in s7.items():
        if isinstance(v, dict) and "messages" in v:
            add_corpus(f"s7.{k}", v["messages"])
    for ch, node in fresh.items():
        add_corpus(f"fresh.{ch}", node.get("latest", []))
    d["price_mentions"] = {k: sorted(v, key=lambda x: x["date"]) for k, v in corpus.items()}
    save_out(d)
    total = sum(len(v) for v in corpus.values())
    print(f"OK price phase — {total} price-bearing posts across {len(corpus)} streams")

def load_prev(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "handles":
        phase_handles()
    elif phase == "pixel":
        phase_pixel()
    elif phase == "gateways":
        phase_gateways()
    elif phase == "prices":
        phase_prices()
    else:
        print("phases: handles | pixel | gateways | prices")
