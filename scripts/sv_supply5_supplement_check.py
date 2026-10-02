#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5 supplement: fresh timestamped check of deep-dive targets
(root domain + storeBatman cluster + decoy names). Passive GET only."""
import json, re, ssl, time, urllib.request, urllib.error

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"}
OUT = "/home/z/my-project/research/sv_supply5_supplement_check.json"

def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return {"status": r.status, "body": r.read().decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": ""}
    except Exception as e:
        return {"status": 0, "error": str(e)[:150], "body": ""}

def og(body):
    t = re.search(r'property="og:title" content="([^"]*)"', body)
    d = re.search(r'property="og:description" content="([^"]*)"', body)
    return (t.group(1) if t else None, d.group(1) if d else None)

TARGETS = {
    "teamsoclo_root": "https://teamsoclo.site/",
    "storeBatman_ch": "https://t.me/storeBatman",
    "Chulopapirel_owner": "https://t.me/Chulopapirel",
    "proofbatman_ch": "https://t.me/proofbatman",
    "BatmanStoreBot_decoy": "https://t.me/BatmanStoreBot",
    "batman_88889_ar": "https://t.me/batman_88889",
}

res = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "targets": {}}
for k, url in TARGETS.items():
    r = get(url)
    out = {"url": url, "http": r["status"], "error": r.get("error", "")[:100]}
    if r["status"] == 200 and r["body"]:
        t, d = og(r["body"])
        out["og_title"], out["og_desc"] = t, d
        m = re.search(r'<div class="tgme_page_extra">([^<]*)</div>', r["body"])
        if m: out["members"] = m.group(1).strip()
        if "tgme_page_button" in r["body"] and "Send Message" in r["body"]:
            out["is_bot_or_user"] = True
        # generic contact page => username does not exist as public channel
        out["generic_page"] = bool(t and "Telegram: Contact" in t)
    res["targets"][k] = out
    print(k, "http=" + str(r["status"]), out.get("members", ""), (out.get("og_title") or "")[:50], out.get("error", ""))
    time.sleep(0.7)

json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
