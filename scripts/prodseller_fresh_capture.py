#!/usr/bin/env python3
"""
ProdSeller Fresh Live Capture — SV-PS-PREP (2026-09-29)
========================================================
Read-only. Goal: prepare the complete ProdSeller package.
  A. API surface map: /balance, /products, + probe docs/openapi/orders endpoints
  B. Fresh catalog + price diff vs 2026-09-27 capture
  C. Telegram fresh captures: ProdSellerOfficial preview, bot, @sookbit
Saves: research/prodseller_live/fresh_2026-09-29.json (+ tg_*.json)
No orders placed. ~12 requests total (limit 300/15min).
"""
import json
import os
import re
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone

ROOT = "/home/z/my-project"
OUT = f"{ROOT}/research/prodseller_live"
BASE = "https://prodseller.com/v1"

# ---- load key from .env (never print) ----
key = ""
with open(f"{ROOT}/.env") as f:
    for line in f:
        if line.startswith("PRODSELLER_API_KEY="):
            key = line.strip().split("=", 1)[1]
if not key:
    raise SystemExit("key missing")

HDRS = {
    "X-API-Key": key,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
}


def call(path, base=None, with_key=True, timeout=25):
    h = dict(HDRS if with_key else {"User-Agent": HDRS["User-Agent"], "Accept": "application/json, text/html;q=0.9,*/*;q=0.8"})
    req = urllib.request.Request((base or BASE) + path, headers=h, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
            return r.status, raw, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:1500], dict(e.headers or {})
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}", {}


def tg_preview(channel):
    """Fetch t.me/s/<channel> preview: last messages + meta."""
    st, raw, _ = call("", base=f"https://t.me/s/{channel}", with_key=False, timeout=25)
    if st != 200:
        return {"http": st, "error": raw[:200]}
    msgs = []
    # message blocks
    for m in re.finditer(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', raw, re.S):
        txt = re.sub(r"<br/?>", "\n", m.group(1))
        txt = re.sub(r"<[^>]+>", "", txt)
        msgs.append(txt.strip()[:900])
    dates = re.findall(r'<time datetime="([^"]+)"', raw)
    title = re.search(r'property="og:title" content="([^"]*)"', raw)
    desc = re.search(r'property="og:description" content="([^"]*)"', raw)
    return {
        "http": st,
        "og_title": title.group(1) if title else None,
        "og_desc": desc.group(1) if desc else None,
        "n_messages": len(msgs),
        "dates": dates[-len(msgs):] if msgs else [],
        "messages": msgs[-25:],
    }


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"run_ts": ts, "base_url": BASE, "api": {}, "tg": {}, "price_diff": []}

    print("=" * 62)
    print("A) API SURFACE — read-only probes")
    print("=" * 62)
    # 1. balance
    st, body, hdr = call("/balance")
    bal = {}
    try:
        bal = json.loads(body)
    except Exception:
        bal = {"_raw": body[:400]}
    out["api"]["balance"] = {"http": st, "response": bal,
                             "ratelimit": {k: v for k, v in hdr.items() if "ratelimit" in k.lower()}}
    print(f"/balance -> {st}: {json.dumps(bal, ensure_ascii=False)[:200]}")

    # 2. products (fresh)
    st, body, _ = call("/products")
    prods = {}
    try:
        prods = json.loads(body)
    except Exception:
        prods = {"_raw": body[:400]}
    out["api"]["products_http"] = st
    plist = prods.get("products", [])
    print(f"/products -> {st}: {len(plist)} products")

    # 3. docs / openapi probes (map the API surface)
    for p in ["/orders", "/orders?page=1&limit=5", "/topup", "/membership", "/tiers"]:
        st2, body2, _ = call(p)
        out["api"]["probe_" + p.strip('/').replace('/', '_').replace('?', '_').replace('&', '_').replace('=', '_')] = {
            "http": st2, "body_head": body2[:400]}
        print(f"probe {p:28s} -> {st2} | {body2[:100].replace(chr(10),' ')}")

    # root site
    st2, body2, _ = call("", base="https://prodseller.com", with_key=False)
    out["api"]["site_root"] = {"http": st2, "body_head": body2[:400]}
    print(f"site root -> {st2} | {body2[:100].replace(chr(10),' ')}")

    # ---- price diff vs 27/09 ----
    print("\n" + "=" * 62)
    print("B) PRICE DIFF vs 2026-09-27 capture")
    print("=" * 62)
    try:
        old = {p["name"]: p for p in json.load(open(f"{OUT}/products_raw.json"))["products"]}
    except Exception:
        old = {}
    fresh = {p["name"]: p for p in plist}
    for name, np in sorted(fresh.items()):
        op = old.get(name)
        if not op:
            out["price_diff"].append({"product": name, "change": "NEW",
                                      "price_now": np.get("price"), "stock": np.get("inStock")})
            print(f"  NEW        {name[:45]:45s} ${np.get('price')}")
            continue
        diffs = []
        for f in ("price", "publicPrice", "inStock"):
            if np.get(f) != op.get(f):
                diffs.append(f"{f}: {op.get(f)} -> {np.get(f)}")
        if diffs:
            out["price_diff"].append({"product": name, "change": "CHANGED", "details": diffs,
                                      "price_now": np.get("price"), "price_old": op.get("price")})
            print(f"  CHANGED    {name[:45]:45s} {'; '.join(diffs)}")
    if not out["price_diff"]:
        print("  (no changes vs 27/09)")

    # ---- Telegram ----
    print("\n" + "=" * 62)
    print("C) TELEGRAM fresh captures")
    print("=" * 62)
    for label, ch in [("ProdSellerOfficial", "ProdSellerOfficial"),
                      ("ProdSellerBot", "prodsellerbot"),
                      ("sookbit", "sookbit")]:
        pv = tg_preview(ch)
        out["tg"][label] = pv
        print(f"{label}: HTTP {pv.get('http')} | msgs={pv.get('n_messages')} | title={pv.get('og_title')}")
        if pv.get("messages"):
            print("  latest:", pv["messages"][-1][:150].replace("\n", " | "))

    with open(f"{OUT}/fresh_2026-09-29.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # separate raw products file for the dossier
    with open(f"{OUT}/products_fresh.json", "w", encoding="utf-8") as f:
        json.dump(prods, f, ensure_ascii=False, indent=1)
    print(f"\n[DONE] saved -> {OUT}/fresh_2026-09-29.json + products_fresh.json (read-only, no orders)")


if __name__ == "__main__":
    main()
