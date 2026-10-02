#!/usr/bin/env python3
"""MEC-2.0 G1-a: Direct probe of the Notion governing-reference section-19 Telegram
Reference Registry (2026-09-25) + stackvault.shop.
Read-only HTTP probing. Output: data/research/mec2_channels_raw.json
Every entity gets: HTTP status, og-metadata, title/description, subscriber counts
(channels), bot description, recent message texts (channel public previews),
price-like lines extracted from messages. No fabrication: parse errors recorded
as-is."""
import json, re, time, ssl, sys, urllib.request, urllib.error

OUT = "/home/z/my-project/data/research/mec2_channels_raw.json"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en,ar;q=0.9,ru;q=0.8",
}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# (id, type, url, cluster) — types: channel / bot / account / website / private_invite
ENTITIES = [
    ("gemini12pro_channel",  "channel",        "https://t.me/gemini12pro_channel",  "Gemini12Pro"),
    ("gemini12pro_bot",      "bot",            "https://t.me/gemini12pro_bot",      "Gemini12Pro"),
    ("ProdSellerOfficial",   "channel",        "https://t.me/ProdSellerOfficial",   "ProdSeller"),
    ("learnwith_Alex",       "channel",        "https://t.me/learnwith_Alex",       "learnwith_Alex"),
    ("AWZ_invite",           "private_invite", "https://t.me/+AWZ-Jl8sydhiMzYy",    "AWZ-private"),
    ("Evo_Era_updates",      "channel",        "https://t.me/Evo_Era_updates",      "EvoEra"),
    ("HitMeowShop",          "channel",        "https://t.me/HitMeowShop",          "HitMeow"),
    ("AISUBSID",             "channel",        "https://t.me/AISUBSID",             "AISUBSID"),
    ("verifierg",            "channel",        "https://t.me/verifierg",            "VerifierGroup"),
    ("gemini12pro",          "channel_or_acct","https://t.me/gemini12pro",          "Gemini12Pro"),
    ("acczone_logs",         "channel",        "https://t.me/acczone_logs",         "Acczone"),
    ("ProdSellerBot",        "bot",            "https://t.me/ProdSellerBot",        "ProdSeller"),
    ("Bite_storee_bot",      "bot",            "https://t.me/Bite_storee_bot",      "BiteStore"),
    ("Mike_E_0",             "account",        "https://t.me/Mike_E_0",             "Mike_E"),
    ("acczone_gemini_link_bot","bot",          "https://t.me/acczone_gemini_link_bot","Acczone"),
    ("Acczone_Store_bot",    "bot",            "https://t.me/Acczone_Store_bot",    "Acczone"),
    ("VeirfyerSupportbot",   "bot",            "https://t.me/VeirfyerSupportbot",   "VerifierGroup"),
    ("Veriyferbot",          "bot",            "https://t.me/Veriyferbot",          "VerifierGroup"),
    ("Evolution_Era_bot",    "bot",            "https://t.me/Evolution_Era_bot",    "EvoEra"),
    ("stackvault_support",   "account",        "https://t.me/stackvault_support",   "StackVault"),
    ("stackvault_bot",       "bot",            "https://t.me/stackvault_bot",       "StackVault"),
    ("PremiKeyBot",          "bot",            "https://t.me/PremiKeyBot",          "PremiKey"),
    ("Premikey_bot",         "bot",            "https://t.me/Premikey_bot",         "PremiKey"),
    ("HitmeowSupport",       "account",        "https://t.me/HitmeowSupport",       "HitMeow"),
    ("insightXpro_bot",      "bot",            "https://t.me/insightXpro_bot",      "insightXpro"),
    ("nevakeystore_bot",     "bot",            "https://t.me/nevakeystore_bot",     "NevaKeyStore"),
    ("Gamisellbot",          "bot",            "https://t.me/Gamisellbot",          "Gamisell"),
    ("p_a_store_bot",        "bot",            "https://t.me/p_a_store_bot",        "p_a_store"),
    ("Aisubsglobalbot",      "bot",            "https://t.me/Aisubsglobalbot",      "AISUBSID"),
    ("storeBatmanBot",       "bot",            "https://t.me/storeBatmanBot",       "storeBatman"),
    ("stackvault_shop",      "website",        "https://stackvault.shop",           "StackVault"),
]

# channels worth a public s/ preview attempt (post history may contain live prices)
S_PREVIEW = ["gemini12pro_channel", "ProdSellerOfficial", "learnwith_Alex",
             "Evo_Era_updates", "HitMeowShop", "AISUBSID", "verifierg",
             "gemini12pro", "acczone_logs"]

PRICE_RE = re.compile(
    r"[^\n]{0,60}?(?:\$|€|£|₽|₺|ريال|درهم|د\.إ|ر\.س|USD|EUR|price|سعر|بـ|بسعر|عرض)"
    r"[^\n]{0,80}", re.I)

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.getcode(), r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        try: body = e.read().decode("utf-8", "replace")[:2000]
        except Exception: body = ""
        return e.code, body, url
    except Exception as e:
        return None, "EXC: %s" % e, url

def meta(html, prop):
    m = re.search(r'<meta[^>]+property=["\']og:%s["\'][^>]+content=["\']([^"\']*)' % prop, html) or \
        re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:%s["\']' % prop, html)
    return m.group(1) if m else None

def text_of(html):
    h = re.sub(r"<br\s*/?>", "\n", html)
    h = re.sub(r"</(p|div|li)>", "\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'").replace("&quot;", '"')
    return h

def parse_tme(html):
    d = {"og_title": meta(html, "title"), "og_desc": meta(html, "description")}
    t = re.search(r'class="tgme_page_title"[^>]*>\s*<span[^>]*>([^<]+)</span>', html)
    if t: d["title"] = t.group(1).strip()
    extra = re.search(r'class="tgme_page_extra"[^>]*>([^<]+)</div>', html)
    if extra: d["extra"] = extra.group(1).strip()   # e.g. "12 345 subscribers"
    desc = re.search(r'class="tgme_page_description"[^>]*>(.*?)</div>', html, re.S)
    if desc: d["description"] = text_of(desc.group(1)).strip()[:600]
    action = re.search(r'class="tgme_action_button_label"[^>]*>([^<]+)<', html)
    if action: d["action"] = action.group(1).strip()
    return d

def parse_s_preview(html):
    msgs = []
    for m in re.finditer(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.S):
        msgs.append(text_of(m.group(1)).strip())
        if len(msgs) >= 8: break
    return msgs

results = {"probe_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "entities": {}, "notes": []}

for eid, etype, url, cluster in ENTITIES:
    code, html, final_url = fetch(url)
    rec = {"id": eid, "type": etype, "cluster": cluster, "url": url,
           "http": code, "final_url": final_url, "bytes": len(html)}
    if etype == "website":
        rec["title"] = (re.search(r"<title[^>]*>([^<]*)</title>", html) or [None, None])[1]
        body = text_of(re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S))
        rec["body_excerpt"] = body[:1500]
        # naive product/price lines from static body
        rec["price_lines"] = [l.strip()[:120] for l in body.split("\n")
                              if re.search(r"\$|€|USD|EUR|price|سعر", l, re.I)][:12]
    else:
        rec.update(parse_tme(html))
    results["entities"][eid] = rec
    print("%-26s %-14s http=%s title=%s" % (eid, etype, code, rec.get("title") or rec.get("og_title")))
    time.sleep(1.6)

# channel public previews
results["s_previews"] = {}
for ch in S_PREVIEW:
    code, html, final_url = fetch("https://t.me/s/" + ch)
    rec = {"http": code, "final_url": final_url}
    if code == 200:
        msgs = parse_s_preview(html)
        rec["messages"] = msgs
        lines = []
        for m in msgs:
            for ln in m.split("\n"):
                if PRICE_RE.search(ln): lines.append(ln.strip()[:140])
        rec["price_lines"] = lines[:25]
    results["s_previews"][ch] = rec
    print("s/%-22s http=%s msgs=%s price_lines=%s" % (
        ch, code, len(rec.get("messages", [])), len(rec.get("price_lines", []))))
    time.sleep(1.6)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\nSaved:", OUT)
ok = sum(1 for r in results["entities"].values() if r["http"] == 200)
print("Entities HTTP 200: %d/%d" % (ok, len(ENTITIES)))
