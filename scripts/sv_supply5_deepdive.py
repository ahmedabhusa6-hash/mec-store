#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5 deep dive: @storeBatmanBot discovery + AiVerseXHub full price catalog."""
import json, re, ssl, time, html, urllib.request, urllib.error

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
OUT = "/home/z/my-project/research/sv_supply5_deepdive.json"

def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)[:150]

def clean(t):
    t = html.unescape(t)
    t = re.sub(r"<br/?>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\n{2,}", "\n", t).strip()

def channel_messages(name, max_m=40):
    """Full message extraction from t.me/s/ with proper entity decode."""
    st, body = get(f"https://t.me/s/{name}")
    if st != 200 or not body:
        return {"http": st, "messages": []}
    msgs = []
    # message blocks with their dates
    blocks = re.split(r'class="tgme_widget_message ', body)
    for b in blocks[1:]:
        dm = re.search(r'<time datetime="([^"]+)"', b)
        tm = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', b, re.S)
        if not tm: continue
        txt = clean(tm.group(1))
        if not txt: continue
        prices = re.findall(r"\$\s?([0-9]+(?:\.[0-9]{1,2})?)", txt)
        msgs.append({"date": dm.group(1) if dm else "", "text": txt[:600], "prices": prices[:10]})
    return {"http": 200, "n_messages": len(msgs), "messages": msgs[:max_m]}

result = {}

# 1) storeBatmanBot: full bot page raw
st, body = get("https://t.me/storeBatmanBot")
sb = {"http": st}
if body:
    for pat, key in [(r'property="og:title" content="([^"]*)"', "og_title"),
                     (r'property="og:description" content="([^"]*)"', "og_desc"),
                     (r'property="og:image" content="([^"]*)"', "og_image"),
                     (r'<div class="tgme_page_extra">([^<]*)</div>', "extra")]:
        m = re.search(pat, body)
        if m: sb[key] = html.unescape(m.group(1))
    # any t.me links inside page
    sb["links_in_page"] = sorted(set(re.findall(r'https://t\.me/([A-Za-z0-9_]+)', body)))[:15]
result["storeBatmanBot_page"] = sb

# 2) possible linked channels for storebat
candidates = ["storeBatman", "storeBatmanShop", "storebatshop", "storebatman_shop",
              "storebat_channel", "storebatstore", "BatmanStoreBot", "storeBatmanNews"]
found = {}
for c in candidates:
    st, body = get(f"https://t.me/{c}")
    if st == 200 and body:
        t = re.search(r'property="og:title" content="([^"]*)"', body)
        d = re.search(r'property="og:description" content="([^"]*)"', body)
        extra = re.search(r'<div class="tgme_page_extra">([^<]*)</div>', body)
        rec = {"http": 200, "og_title": html.unescape(t.group(1)) if t else None,
               "og_desc": html.unescape(d.group(1)) if d else None}
        if extra: rec["members"] = extra.group(1).strip()
        # detect "no such account" placeholder: title contains 'Telegram: Contact'
        if rec["og_title"] and "Telegram: Contact" not in rec["og_title"]:
            found[c] = rec
    time.sleep(0.7)
result["storebat_candidates"] = found

# 3) AiVerseX full channel dump
result["AiVerseXHub_full"] = channel_messages("AiVerseXHub")
# bot pages of AiVerseX
for b, key in [("AIVerseXBot", "AIVerseXBot"), ("AiVerseXBot", "AiVerseXBot_alias"),
               ("AIVerseXBot_support", "support_probe")]:
    st, body = get(f"https://t.me/{b}")
    if st == 200 and body:
        t = re.search(r'property="og:title" content="([^"]*)"', body)
        d = re.search(r'property="og:description" content="([^"]*)"', body)
        result[key] = {"http": 200, "og_title": html.unescape(t.group(1)) if t else None,
                       "og_desc": html.unescape(d.group(1)) if d else None}
    time.sleep(0.6)

json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
print("\nstoreBatmanBot page:", json.dumps(result["storeBatmanBot_page"], ensure_ascii=False, indent=1))
print("\nstorebat candidates found:", json.dumps(found, ensure_ascii=False, indent=1))
print("\nAiVerseX messages:", result["AiVerseXHub_full"].get("n_messages"))
for m in result["AiVerseXHub_full"]["messages"][:12]:
    print(" >", m["date"][:16], "|", m["text"][:130].replace("\n", " ¶ "))
print("\nAIVerseXBot:", result.get("AIVerseXBot"))
