#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — LIVE RE-VERIFICATION (GET-only, passive OSINT)
Mirrors pmrf_v2_live_update.py surface set:
  - StackVault catalog (decohomz.com/sv-api/products) with full UA
  - teamsoclo gateway (gpt.teamsoclo.site/api/pricing + /api/status)
  - 14 domains
  - 8 Telegram public previews (t.me/s/)
  - costPrice field check
Compares against v2.0 witness (pmrf_v2_live_update_20261002.json) → delta report
Output: research/pmrf_v3_live_update_20261002.json
"""
import json, re, hashlib, os
from datetime import datetime, timezone, timedelta
import urllib.request, urllib.error
import ssl

ROOT = "/home/z/my-project"
TZ = timezone(timedelta(hours=3))
RUN_TS = datetime.now(TZ).isoformat(timespec="seconds")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
CTX = ssl.create_default_context()

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            body = r.read()
            return r.status, body.decode("utf-8", errors="replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, (e.read(400).decode("utf-8", errors="replace") if e.fp else ""), dict(e.headers)
    except Exception as e:
        return 0, f"ERR:{type(e).__name__}:{str(e)[:80]}", {}

out = {"run": "PMRF v3.0 live re-verification", "ts": RUN_TS, "method": "GET-only passive, full browser UA", "surfaces": {}}

# 1) StackVault catalog
st, body, _ = get("https://decohomz.com/sv-api/products")
cat = {"http": st}
if st == 200:
    try:
        data = json.loads(body)
        prods = data.get("products") or (data if isinstance(data, list) else [])
        cat["count"] = len(prods)
        pref = {}
        cost_fields = 0
        ids = []
        for p in prods:
            pid = str(p.get("id") or p.get("_id") or "")
            m = re.match(r"^([a-z]+)_", pid)
            pref[m.group(1) if m else "(noprefix)"] = pref.get(m.group(1) if m else "(noprefix)", 0) + 1
            if any(k in p for k in ("costPrice", "cost_price", "cost")):
                cost_fields += 1
            ids.append(pid)
        cat["prefixes"] = pref
        cat["cost_fields_present"] = cost_fields
        cat["ids_sha256"] = hashlib.sha256(",".join(sorted(ids)).encode()).hexdigest()[:16]
        # price witnesses (sample)
        sample = []
        for p in prods:
            t = str(p.get("title") or p.get("name") or "")
            if any(k in t for k in ("ChatGPT", "Office 365", "Canva", "Codex", "Gemini", "Capcut")):
                sample.append({"id": str(p.get("id"))[:24], "title": t[:60], "price": p.get("price"), "stock": p.get("stock")})
            if len(sample) >= 8: break
        cat["price_witness_sample"] = sample
    except Exception as e:
        cat["parse_error"] = str(e)[:120]
        cat["body_head"] = body[:200]
else:
    cat["body_head"] = body[:200]
out["surfaces"]["sv_catalog"] = cat

# 2) teamsoclo gateway
st, body, _ = get("https://gpt.teamsoclo.site/api/pricing")
gw = {"http": st}
if st == 200:
    try:
        data = json.loads(body)
        models = data.get("data") or data.get("models") or []
        if isinstance(models, dict): models = list(models.values())
        gw["model_count"] = len(models)
        names = sorted(str(m.get("model") or m.get("name") or m)[:40] for m in models)[:20] if models else []
        gw["models_sample"] = names
    except Exception as e:
        gw["parse_error"] = str(e)[:120]
out["surfaces"]["teamsoclo_gateway"] = gw

# 3) domains
DOMAINS = ["https://stackvault.shop", "https://www.prodseller.com", "https://canboso.com", "https://decohomz.com",
           "https://cgpt-active.pro", "https://nikokey.com", "https://gpt.teamsoclo.site", "https://redeem.teamsoclo.site",
           "https://docs.teamsoclo.site", "https://jcc.tokensunlimited.workers.dev", "https://aiversehub.store",
           "https://aixpress.shop", "https://lahastore.up.railway.app", "https://www.decohomz.com"]
dom = {}
for u in DOMAINS:
    st, body, _ = get(u, timeout=15)
    dom[u.replace("https://", "")] = st
out["surfaces"]["domains_14"] = dom

# 4) Telegram channels
CH = ["ProdSellerOfficial", "Evo_Era_updates", "AISUBSID", "teamsoclo", "HitMeowShop", "fork_bot_channel", "gemini12pro", "AiVerseXHub"]
tg = {}
for c in CH:
    st, body, _ = get(f"https://t.me/s/{c}", timeout=15)
    rec = {"http": st}
    if st == 200:
        # last message time
        times = re.findall(r'datetime="([^"]+)"', body)
        rec["messages"] = body.count('class="tgme_widget_message')
        rec["last_msg_datetime_attr"] = times[-1] if times else None
    tg[c] = rec
out["surfaces"]["telegram_8"] = tg

# 5) delta vs v2.0 witness
delta = {"base": "research/pmrf_v2_live_update_20261002.json (witness 2026-10-02T07:11+03)"}
try:
    v2 = json.load(open(os.path.join(ROOT, "research/pmrf_v2_live_update_20261002.json"), encoding="utf-8"))
    v2cat = v2.get("surfaces", {}).get("sv_catalog", {}) or v2.get("stackvault_catalog", {})
    if "count" in cat and "count" in v2cat:
        delta["catalog_v2"] = v2cat["count"]
        delta["catalog_v3"] = cat["count"]
        delta["catalog_change"] = cat["count"] - v2cat["count"]
    v2gw = v2.get("surfaces", {}).get("teamsoclo_gateway", {}) or v2.get("teamsoclo_gateway", {})
    if "model_count" in gw and "model_count" in v2gw:
        delta["gateway_v2"] = v2gw["model_count"]
        delta["gateway_v3"] = gw["model_count"]
except Exception as e:
    delta["error"] = str(e)[:120]
out["delta_vs_v2"] = delta

path = os.path.join(ROOT, "research/pmrf_v3_live_update_20261002.json")
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"RUN {RUN_TS}")
print("SV catalog:", json.dumps(cat, ensure_ascii=False)[:400])
print("Gateway:", json.dumps(gw, ensure_ascii=False)[:250])
print("Domains:", dom)
print("Telegram:", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'last'} for k, v in tg.items()}, ensure_ascii=False)[:600])
print("Delta:", json.dumps(delta, ensure_ascii=False)[:300])
