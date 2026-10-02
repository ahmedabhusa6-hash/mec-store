#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5: storeBatman cluster full dump (channel + proof + owner)."""
import json, re, ssl, time, html, urllib.request, urllib.error

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
OUT = "/home/z/my-project/research/sv_supply5_storebatman.json"

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

def full_channel(name):
    rec = {"name": name}
    st, body = get(f"https://t.me/{name}")
    rec["page_http"] = st
    if st == 200 and body:
        t = re.search(r'property="og:title" content="([^"]*)"', body)
        d = re.search(r'property="og:description" content="([^"]*)"', body)
        extra = re.search(r'<div class="tgme_page_extra">([^<]*)</div>', body)
        rec["og_title"] = html.unescape(t.group(1)) if t else None
        rec["og_desc"] = html.unescape(d.group(1)) if d else None
        if extra: rec["members"] = extra.group(1).strip()
    st, body = get(f"https://t.me/s/{name}")
    msgs = []
    if st == 200 and body:
        blocks = re.split(r'class="tgme_widget_message ', body)
        for b in blocks[1:]:
            dm = re.search(r'<time datetime="([^"]+)"', b)
            tm = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', b, re.S)
            if not tm: continue
            txt = clean(tm.group(1))
            if not txt: continue
            prices = re.findall(r"\$\s?([0-9]+(?:\.[0-9]{1,2})?)|([0-9]+(?:\.[0-9]{1,2})?)\s?(?:USDT|usdt)", txt)
            flat = [a or b for a, b in prices][:10]
            msgs.append({"date": dm.group(1) if dm else "", "text": txt[:700], "prices": flat})
    rec["messages"] = msgs
    rec["n_messages"] = len(msgs)
    return rec

result = {}
for ch in ["storeBatman", "proofbatman", "Chulopapirel", "BatmanStoreBot"]:
    result[ch] = full_channel(ch)
    print(f"--- {ch}: http={result[ch]['page_http']} msgs={result[ch]['n_messages']} title={result[ch].get('og_title')} members={result[ch].get('members')}")
    time.sleep(0.8)

json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
print()
for ch in ["storeBatman", "proofbatman"]:
    print("=" * 25, ch, "messages:")
    for m in result[ch]["messages"][:14]:
        print(">", m["date"][:16], "|", m["text"][:160].replace("\n", " ¶ "))
    print()
