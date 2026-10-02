#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5: live verification of stackvault.shop + all supplier links + new entity research.
Passive OSINT only (public GET). Supports resume: merges into existing output."""
import json, re, ssl, sys, time, urllib.request, urllib.error, urllib.parse

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"}
OUT = "/home/z/my-project/research/sv_supply5_live_check.json"

try:
    RESULT = json.load(open(OUT, encoding="utf-8"))
except Exception:
    RESULT = {"generated": "", "targets": {}}

def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            body = r.read().decode("utf-8", "replace")
            return {"status": r.status, "final_url": r.geturl(), "server": r.headers.get("Server", ""),
                    "size": len(body), "body": body}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": "HTTPError", "body": ""}
    except Exception as e:
        return {"status": 0, "error": str(e)[:180], "body": ""}

def og(body):
    t = re.search(r'property="og:title" content="([^"]*)"', body)
    d = re.search(r'property="og:description" content="([^"]*)"', body)
    return (t.group(1) if t else None, d.group(1) if d else None)

def tg_channel(name):
    """Check a Telegram channel: t.me/<name> + t.me/s/<name> message preview."""
    out = {"url": f"https://t.me/{name}"}
    r = get(f"https://t.me/{name}")
    out["http"] = r["status"]
    if r["status"] == 200 and r["body"]:
        t, d = og(r["body"])
        out["og_title"], out["og_desc"] = t, d
        m = re.search(r'<div class="tgme_page_extra">([^<]*)</div>', r["body"])
        if m: out["members"] = m.group(1).strip()
    elif r["status"] == 200:
        out["note"] = "page ok, no og meta"
    # message preview
    s = get(f"https://t.me/s/{name}")
    out["s_preview"] = {"http": s["status"], "n_messages": 0, "messages": []}
    if s["status"] == 200 and s["body"]:
        msgs = []
        for block in re.findall(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', s["body"], re.S)[:20]:
            txt = re.sub(r"<br/?>", "\n", block)
            txt = re.sub(r"<[^>]+>", "", txt)
            txt = re.sub(r"\n{2,}", "\n", txt).strip()
            if txt:
                prices = re.findall(r"\$\s?([0-9]+(?:\.[0-9]{1,2})?)", txt)
                msgs.append({"text": txt[:400], "prices": prices[:8]})
        dates = re.findall(r'<time datetime="([^"]+)"', s["body"])
        out["s_preview"] = {"http": 200, "n_messages": len(msgs), "messages": msgs,
                            "dates": dates[:20]}
        if dates: out["s_preview"]["latest_date"] = dates[-1]
    return out

def tg_bot(name):
    """Check a Telegram bot page t.me/<name>."""
    out = {"url": f"https://t.me/{name}", "type": "bot"}
    r = get(f"https://t.me/{name}")
    out["http"] = r["status"]
    if r["status"] == 200 and r["body"]:
        t, d = og(r["body"])
        out["og_title"], out["og_desc"] = t, d
        if "tgme_page_button" in r["body"] and "Send Message" in r["body"]:
            out["is_bot"] = True
    elif r["status"] == 302 or r["status"] == 301:
        out["note"] = "redirect"
    return out

def site(url, title_hints=True):
    r = get(url)
    out = {"url": url, "status": r["status"], "final_url": r.get("final_url", ""),
           "server": r.get("server", ""), "size": r.get("size", 0), "error": r.get("error", "")}
    if r["status"] == 200 and r["body"]:
        tm = re.search(r"<title[^>]*>([^<]*)</title>", r["body"], re.I)
        if tm: out["title"] = tm.group(1).strip()[:120]
        out["body_head"] = r["body"][:300]
    return out

TARGETS = {
    # == the store to verify (user request) ==
    "stackvault_shop": lambda: site("https://stackvault.shop/"),
    # == ProdSeller cluster ==
    "ProdSellerOfficial_ch": lambda: tg_channel("ProdSellerOfficial"),
    "ProdSellerBot_bot": lambda: tg_bot("ProdSellerBot"),
    "sookbit_admin": lambda: tg_bot("sookbit"),
    "prodseller_io": lambda: site("https://prodseller.io/"),
    "prodseller_api_docs": lambda: site("https://prodseller.io/api/docs"),
    # == HitMeowShop cluster ==
    "HitMeowShop_ch": lambda: tg_channel("HitMeowShop"),
    "PremikeyBot_bot": lambda: tg_bot("PremikeyBot"),
    "Premikey_Bot_bot": lambda: tg_bot("Premikey_Bot"),
    "HitmeowSupport": lambda: tg_bot("HitmeowSupport"),
    "vahnix_admin": lambda: tg_bot("vahnix"),
    # == NEW: storeBatmanBot ==
    "storeBatmanBot_bot": lambda: tg_bot("storeBatmanBot"),
    # == NEW: AiVerseX Hub (variants) ==
    "AiVerseXHub_ch": lambda: tg_channel("AiVerseXHub"),
    "AiVerseX_Hub_ch": lambda: tg_channel("AiVerseX_Hub"),
    "aiversex_bot": lambda: tg_bot("AiVerseXBot"),
    "aiversex_site": lambda: site("https://aiversex.com/"),
    "aiversex_hub_site": lambda: site("https://aiversexhub.com/"),
    # == Evo Era ==
    "Evo_Era_updates_ch": lambda: tg_channel("Evo_Era_updates"),
    "Evolution_Era_bot": lambda: tg_bot("Evolution_Era_bot"),
    "adham_H11_admin": lambda: tg_bot("adham_H11"),
    # == AISUBSID ==
    "AISUBSID_ch": lambda: tg_channel("AISUBSID"),
    "Aisubsglobalbot_bot": lambda: tg_bot("Aisubsglobalbot"),
    "AisubsIDFounder": lambda: tg_bot("AisubsIDFounder"),
    # == Team Sóc Lọ (teamsoclo) ==
    "teamsoclo_tg": lambda: tg_channel("teamsoclo"),
    "gpt_teamsoclo": lambda: site("https://gpt.teamsoclo.site/"),
    "redeem_teamsoclo": lambda: site("https://redeem.teamsoclo.site/"),
    "docs_teamsoclo": lambda: site("https://docs.teamsoclo.site/"),
}

# resume support: skip targets already done in this run's file
done = set(RESULT.get("targets", {}).keys())
queue = [k for k in TARGETS if k not in done]
print(f"targets: {len(TARGETS)} total, {len(done)} already done, {len(queue)} to run")

for i, key in enumerate(queue, 1):
    try:
        RESULT["targets"][key] = TARGETS[key]()
        ok = RESULT["targets"][key].get("http", RESULT["targets"][key].get("status", "?"))
        print(f"[{i}/{len(queue)}] {key}: http={ok}")
    except Exception as e:
        RESULT["targets"][key] = {"error": str(e)[:200]}
        print(f"[{i}/{len(queue)}] {key}: ERROR {e}")
    time.sleep(0.8)
    if i % 8 == 0:  # checkpoint save
        RESULT["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        json.dump(RESULT, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

RESULT["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
json.dump(RESULT, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
