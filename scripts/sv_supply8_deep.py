#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-SUPPLY-8: Deep-dive on 4 branches — AISUBSID / Pixel farms / Indian layer / VN gateways
Passive OSINT only — public t.me/s/ previews, og metadata, public GET pages.
Usage: python3 sv_supply8_deep.py <phase>   # aisubsid | pixel | india | vietnam
Output: research/sv_supply8_deep.json (phases merge into one file)
"""
import json, re, sys, time, urllib.request, urllib.error, gzip
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_supply8_deep.json"

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
    url = f"https://t.me/s/{channel}"
    status, html = fetch(url)
    if status != 200:
        return {"http": status, "error": html[:200], "messages": [], "pages": 0}
    msgs = parse_channel_preview(html)
    all_msgs.extend(msgs)
    for mid in [m["post"] for m in msgs]:
        seen.add(mid)
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
        return {"http": status}
    title = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    desc = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    return {"http": status,
            "og_title": clean(title.group(1)) if title else "",
            "og_desc": clean(desc.group(1))[:400] if desc else ""}

def extract_handles(msgs, exclude=()):
    text = "\n".join(m.get("text", "") for m in msgs)
    from collections import Counter
    c = Counter(re.findall(r'@([A-Za-z0-9_]{4,})', text))
    return {h: n for h, n in c.most_common(40) if h.lower() not in {e.lower() for e in exclude}}

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
    print(f"saved → {OUT}")

# ---------------- PHASE 1: AISUBSID ----------------
def phase_aisubsid():
    out = load_out()
    print("== AISUBSID: full history ==")
    hist = grab_history("AISUBSID", max_pages=14)
    print(f"  msgs={hist.get('n_messages')} pages={hist.get('pages')} span={hist.get('first')}→{hist.get('last')}")
    handles = extract_handles(hist.get("messages", []), exclude=["AISUBSID", "Aisubsglobalbot"])
    print("  handles found:", handles)
    probes = {"Aisubsglobalbot": og_probe("Aisubsglobalbot")}
    time.sleep(0.8)
    for h in list(handles)[:12]:
        probes[h] = og_probe(h)
        time.sleep(0.8)
    out["AISUBSID"] = {"history": hist, "handles": handles, "og_probes": probes}
    save_out(out)

# ---------------- PHASE 2: PIXEL FARMS ----------------
def phase_pixel():
    out = load_out()
    print("== fork_bot_channel: full history ==")
    hist = grab_history("fork_bot_channel", max_pages=14)
    print(f"  msgs={hist.get('n_messages')} pages={hist.get('pages')} span={hist.get('first')}→{hist.get('last')}")
    handles = extract_handles(hist.get("messages", []), exclude=["fork_bot_channel"])
    print("  handles found:", handles)
    probes = {}
    for h in ["ver_pixel_bot", "fork_bot"] + list(handles)[:10]:
        probes[h] = og_probe(h)
        time.sleep(0.8)
    print("== nikokey.com homepage ==")
    st, html = fetch("https://nikokey.com", timeout=30)
    niko = {"http": st, "size": len(html)}
    if st == 200:
        t = re.search(r'<title[^>]*>([^<]*)</title>', html)
        niko["title"] = clean(t.group(1)) if t else ""
        for kw in ["pixel", "gemini", "alipay", "usdt", "price", "upgrade", "niko"]:
            niko[f"kw_{kw}"] = len(re.findall(kw, html, re.I))
    out["pixel"] = {"fork_bot_channel": hist, "handles": handles, "og_probes": probes, "nikokey": niko}
    save_out(out)

# ---------------- PHASE 3: INDIAN LAYER ----------------
def phase_india():
    out = load_out()
    print("== AiVerseXHub: deeper pagination (20 pages) ==")
    av = grab_history("AiVerseXHub", max_pages=20)
    print(f"  msgs={av.get('n_messages')} pages={av.get('pages')} span={av.get('first')}→{av.get('last')}")
    print("== Evo_Era_updates: deeper pagination (16 pages) ==")
    ev = grab_history("Evo_Era_updates", max_pages=16)
    print(f"  msgs={ev.get('n_messages')} pages={ev.get('pages')} span={ev.get('first')}→{ev.get('last')}")
    probes = {}
    for h in ["adham_H11", "Iruleeverywhere", "Iruleeveryone", "demonytt", "moneytalksluxe"]:
        probes[h] = og_probe(h)
        time.sleep(0.8)
    out["india"] = {"AiVerseXHub": av, "Evo_Era_updates": ev, "og_probes": probes}
    save_out(out)

# ---------------- PHASE 4: VIETNAM ----------------
def phase_vietnam():
    out = load_out()
    print("== teamsoclo: full deep history ==")
    ts = grab_history("teamsoclo", max_pages=20)
    print(f"  msgs={ts.get('n_messages')} pages={ts.get('pages')} span={ts.get('first')}→{ts.get('last')}")
    handles = extract_handles(ts.get("messages", []), exclude=["teamsoclo"])
    print("  handles found:", handles)
    print("== gateway probes ==")
    gateways = {}
    for u in ["https://jcc.tokensunlimited.workers.dev",
              "https://tokensunlimited.workers.dev",
              "https://redeem.teamsoclo.site",
              "https://gpt.teamsoclo.site/api/status"]:
        st, body = fetch(u, timeout=25)
        gateways[u] = {"http": st, "head": body[:200] if st == 200 else body[:120]}
        time.sleep(0.8)
    probes = {}
    for h in list(handles)[:10]:
        probes[h] = og_probe(h)
        time.sleep(0.8)
    out["vietnam"] = {"teamsoclo": ts, "handles": handles, "og_probes": probes, "gateways": gateways}
    save_out(out)

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"aisubsid": phase_aisubsid, "pixel": phase_pixel,
          "india": phase_india, "vietnam": phase_vietnam}.get(phase)
    if not fn:
        print("phases: aisubsid | pixel | india | vietnam")
        sys.exit(1)
    fn()
