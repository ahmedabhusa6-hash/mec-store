#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-7b: final probes — nikokey.com (Chinese factory store) + forks + RichAI + aiversehub.store headers."""
import json, re, urllib.request, gzip, socket
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
OUT = "/home/z/my-project/research/sv_supply7_final_probes.json"

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", "replace")[:3000], dict(e.headers)
        except Exception:
            return e.code, "", {}
    except Exception as e:
        return 0, str(e)[:120], {}

def og(username):
    status, html, _ = fetch(f"https://t.me/{username}")
    if status != 200:
        return {"http": status}
    def meta(prop):
        m = re.search(rf'<meta property="{prop}" content="([^"]*)"', html)
        return m.group(1) if m else ""
    return {"http": status, "og_title": meta("og:title"), "og_desc": meta("og:description")[:220]}

res = {"generated": datetime.now(timezone.utc).isoformat(), "sites": {}, "tg": {}}

for host, url in [
    ("nikokey.com", "https://nikokey.com/"),
    ("aiversehub.store", "https://aiversehub.store/"),
]:
    try:
        ips = socket.gethostbyname_ex(host)[2]
    except Exception as e:
        ips = [f"ERR {e}"[:60]]
    status, body, hdrs = fetch(url)
    title = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", body[:8000], re.S | re.I)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()[:150]
    # language hints
    lang = ""
    m2 = re.search(r'<html[^>]*lang="([^"]*)"', body[:3000])
    if m2:
        lang = m2.group(1)
    res["sites"][host] = {
        "dns_ips": ips, "status": status, "title": title, "html_lang": lang,
        "server": hdrs.get("Server", ""), "size": len(body),
        "body_snippet": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))[:600],
    }
    print(f"[site] {host}: {status} | {title!r} | lang={lang} | server={hdrs.get('Server','')}")

for u in ["fork_bot_channel", "RichAIStoreBot", "lksamon", "Gemini_support_1",
          "gemini12pro_bot", "NevaAI_Shop"]:
    res["tg"][u] = og(u)
    print(f"[tg] @{u}: {res['tg'][u]}")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(f"[✓] saved -> {OUT}")
