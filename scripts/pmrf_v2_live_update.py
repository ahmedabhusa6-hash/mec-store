#!/usr/bin/env python3
"""
PMRF v2.0 — Phase 17: Live Research Update (READ-ONLY)
Passive OSINT re-verification to the v2.0 execution timestamp:
  - StackVault catalog (decohomz.com/sv-api/products): count, prefixes, costPrice field, key prices
  - teamsoclo gateway pricing: model count vs documented 15
  - HTTP statuses of core domains
  - t.me/s/ public previews of key channels (last messages)
NO purchases, NO POST, NO keys. GET only, public endpoints.
Output: research/pmrf_v2_live_update_20261002.json
"""
import json, datetime, re, time
import urllib.request, urllib.error, ssl
from pathlib import Path

ROOT = Path("/home/z/my-project")
OUT = ROOT / "research" / "pmrf_v2_live_update_20261002.json"
TZ = datetime.timezone(datetime.timedelta(hours=3))  # Asia/Aden UTC+3
TS = datetime.datetime.now(TZ).isoformat(timespec="seconds")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
      "Accept-Language": "en;q=0.9,ar;q=0.8"}

res = {"task": "PMRF v2.0 live research update (read-only)", "execution_timestamp": TS,
       "methodology": "GET-only passive OSINT; public endpoints; no keys; no purchases",
       "stackvault_catalog": {}, "gateway": {}, "domains": {}, "telegram_channels": {}, "errors": []}


def get(url, timeout=20, retries=1):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                body = r.read()
                return r.status, dict(r.headers), body
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), (e.read() if e.fp else b"")
        except Exception as e:
            if attempt >= retries:
                raise
            time.sleep(2)


# ---------- 1. StackVault catalog ----------
try:
    st, hdr, body = get("https://decohomz.com/sv-api/products")
    res["stackvault_catalog"]["http_status"] = st
    if st == 200:
        try:
            data = json.loads(body)
        except Exception:
            data = None
        products = None
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict):
            for k in ("products", "data", "items"):
                if isinstance(data.get(k), list):
                    products = data[k]
                    break
        if products is not None:
            res["stackvault_catalog"]["total"] = len(products)
            # prefix distribution
            prefixes = {}
            prefix_field = None
            if products:
                p0 = products[0]
                for f in ("productId", "product_id", "id", "sku", "_id"):
                    v = p0.get(f) if isinstance(p0, dict) else None
                    if isinstance(v, str) and re.match(r"^(cb_|ps_|mr_)", v):
                        prefix_field = f
                        break
            if prefix_field:
                for p in products:
                    v = str(p.get(prefix_field, ""))
                    m = re.match(r"^(cb_|ps_|mr_)", v)
                    k = m.group(1) if m else (v.split("_")[0] + "_" if "_" in v else "other")
                    prefixes[k] = prefixes.get(k, 0) + 1
            res["stackvault_catalog"]["prefix_field"] = prefix_field
            res["stackvault_catalog"]["prefix_distribution"] = prefixes
            # costPrice leak check
            has_cost = [k for k in (products[0].keys() if products else []) if "cost" in k.lower()]
            res["stackvault_catalog"]["cost_fields_present"] = has_cost
            n_with_cost = sum(1 for p in products if any("cost" in str(k).lower() and p.get(k) not in (None, "", 0) for k in p.keys())) if products else 0
            res["stackvault_catalog"]["records_with_cost_value"] = n_with_cost
            # key price witnesses
            samples = {}
            want = ["ChatGPT Go", "ChatGPT Plus 3D", "ChatGPT Plus", "Grok", "Capcut", "CapCut", "Codex", "Gemini", "Office", "Canva", "Duolingo", "Adobe"]
            for p in products:
                t = str(p.get("title") or p.get("name") or "")
                for w in want:
                    if w.lower() in t.lower() and w not in samples:
                        price = p.get("price") or p.get("salePrice") or p.get("amount")
                        samples[w] = {"title": t[:80], "price": price, "stock": p.get("stock", p.get("quantity")), "id": str(p.get(prefix_field or "id", ""))[:24]}
                        break
            res["stackvault_catalog"]["price_witnesses"] = samples
        else:
            res["stackvault_catalog"]["parse"] = "non-list JSON — keys: " + ",".join(list(data.keys())[:10]) if isinstance(data, dict) else "not json"
    res["stackvault_catalog"]["bytes"] = len(body)
except Exception as e:
    res["errors"].append({"probe": "stackvault_catalog", "error": str(e)[:200]})
    res["stackvault_catalog"]["status"] = "ACCESS_FAILED"

# ---------- 2. teamsoclo gateway pricing ----------
try:
    st, hdr, body = get("https://gpt.teamsoclo.site/api/pricing")
    res["gateway"]["http_status"] = st
    if st == 200:
        data = json.loads(body)
        models = data.get("data", [])
        res["gateway"]["model_count"] = len(models)
        res["gateway"]["model_names"] = [m.get("model_name") or m.get("model") or str(m.get("display_name", "")) for m in models]
        res["gateway"]["pricing_version"] = data.get("pricing_version")
    res["gateway"]["bytes"] = len(body)
except Exception as e:
    res["errors"].append({"probe": "gateway_pricing", "error": str(e)[:200]})
    res["gateway"]["status"] = "ACCESS_FAILED"

# ---------- 3. Domain statuses ----------
DOMAINS = [
    "https://stackvault.shop",
    "https://www.stackvault.shop",
    "https://prodseller.com",
    "https://canboso.com",
    "https://decohomz.com",
    "https://aiversehub.store",
    "https://aixpress.shop",
    "https://cgpt-active.pro",
    "https://nikokey.com",
    "https://redeem.teamsoclo.site",
    "https://docs.teamsoclo.site",
    "https://jcc.tokensunlimited.workers.dev",
    "https://gpt.teamsoclo.site",
    "https://lahastore.up.railway.app",
]
for d in DOMAINS:
    try:
        st, hdr, body = get(d, timeout=15)
        res["domains"][d] = {"status": st, "bytes": len(body),
                             "server": (hdr.get("Server") or hdr.get("server") or "")[:40]}
    except Exception as e:
        res["domains"][d] = {"status": "ACCESS_FAILED", "error": str(e)[:120]}

# ---------- 4. Telegram public previews ----------
CHANNELS = ["ProdSellerOfficial", "Evo_Era_updates", "AISUBSID", "teamsoclo",
            "HitMeowShop", "gemini12pro_channel", "AiVerseXHub", "fork_bot_channel"]
for ch in CHANNELS:
    try:
        st, hdr, body = get(f"https://t.me/s/{ch}", timeout=15)
        html = body.decode("utf-8", "replace")
        info = {"status": st}
        m = re.search(r'<div class="tgme_channel_info_header_title[^"]*"[^>]*>([^<]+)</div>', html)
        if m:
            info["title"] = m.group(1).strip()
        times = re.findall(r'<time datetime="([^"]+)"', html)
        texts = re.findall(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.S)
        info["message_datetimes"] = times[-5:] if times else []
        info["last_messages"] = []
        for t in texts[-3:]:
            clean = re.sub(r"<[^>]+>", " ", t)
            clean = re.sub(r"\s+", " ", clean).strip()
            info["last_messages"].append(clean[:160])
        info["n_messages_on_page"] = len(times)
        res["telegram_channels"][ch] = info
    except Exception as e:
        res["telegram_channels"][ch] = {"status": "ACCESS_FAILED", "error": str(e)[:120]}

OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

# Console digest
digest = {
    "timestamp": TS,
    "stackvault": {k: v for k, v in res["stackvault_catalog"].items() if k in ("http_status", "total", "prefix_distribution", "cost_fields_present", "records_with_cost_value", "status")},
    "gateway": {k: v for k, v in res["gateway"].items() if k in ("http_status", "model_count", "status")},
    "domains": {d: v.get("status") for d, v in res["domains"].items()},
    "telegram": {c: {"status": i.get("status"), "last_dt": (i.get("message_datetimes") or [None])[-1], "n": i.get("n_messages_on_page")} for c, i in res["telegram_channels"].items()},
    "errors": res["errors"],
}
print(json.dumps(digest, ensure_ascii=False, indent=1))
