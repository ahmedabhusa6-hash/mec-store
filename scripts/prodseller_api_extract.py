#!/usr/bin/env python3
"""
ProdSeller API Live Extraction — MEC-2.x Price Discovery Phase 1
=================================================================
Key provided by user 2026-09-28 (psk_c139...).
Steps:
  1. GET /v1/balance        — validate key, get membership tier
  2. GET /v1/products       — FULL catalog: actual charge price + publicPrice
  3. Save raw JSON + analysis summary
Rate limit: 300 req/15min — we use 2 requests. No orders placed (read-only).
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# FIX (P0, AUDIT-7 — CWE-798): the real API key was embedded verbatim here in
# a git-tracked file. Now read from the environment (.env is git-ignored).
API_KEY = os.environ.get("PRODSELLER_API_KEY", "")
if not API_KEY:
    sys.exit("PRODSELLER_API_KEY not set — export it from .env before running")
BASE_URL = os.environ.get("PRODSELLER_API_URL", "https://prodseller.com/v1")
OUT_DIR = "/home/z/my-project/research/prodseller_live"
HDRS = {
    "X-API-Key": API_KEY,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def call(path, method="GET", body=None, timeout=30):
    data = None
    headers = dict(HDRS)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            rate = {k: v for k, v in resp.headers.items() if "ratelimit" in k.lower() or k.lower() == "retry-after"}
            try:
                return resp.status, json.loads(raw), rate
            except json.JSONDecodeError:
                return resp.status, {"_raw": raw[:2000]}, rate
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        rate = {k: v for k, v in e.headers.items() if "ratelimit" in k.lower()} if e.headers else {}
        try:
            return e.code, json.loads(raw), rate
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:2000]}, rate
    except Exception as e:
        return 0, {"_exception": f"{type(e).__name__}: {e}"}, {}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = {"run_ts": ts, "base_url": BASE_URL, "steps": []}

    # ---- Step 1: balance (key validation) ----
    print("=" * 60)
    print("STEP 1: GET /v1/balance  (key validation)")
    print("=" * 60)
    st, bal, rate = call("/balance")
    print(f"HTTP {st} | rate-headers: {rate}")
    print(json.dumps(bal, ensure_ascii=False, indent=2)[:1500])
    report["steps"].append({"step": "balance", "http": st, "rate_headers": rate, "response": bal})
    if st != 200:
        print("\n[!] Key validation FAILED — aborting before products call.")
        with open(f"{OUT_DIR}/run_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        sys.exit(1)

    # ---- Step 2: full products catalog ----
    print("\n" + "=" * 60)
    print("STEP 2: GET /v1/products  (FULL catalog)")
    print("=" * 60)
    st, prods, rate = call("/products")
    print(f"HTTP {st} | rate-headers: {rate}")
    if st != 200:
        print(json.dumps(prods, ensure_ascii=False, indent=2)[:1500])
        report["steps"].append({"step": "products", "http": st, "response": prods})
        with open(f"{OUT_DIR}/run_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        sys.exit(1)

    plist = prods.get("products", [])
    print(f"Total products: {len(plist)}")

    # Save raw
    raw_path = f"{OUT_DIR}/products_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(prods, f, ensure_ascii=False, indent=2)
    print(f"Raw saved -> {raw_path}")

    # ---- Step 3: quick analysis ----
    instock = [p for p in plist if p.get("inStock")]
    oos = [p for p in plist if not p.get("inStock")]
    act_email = [p for p in plist if p.get("requiresEmailActivation")]

    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    priced = [(p, num(p.get("price")), num(p.get("publicPrice"))) for p in plist]
    have_both = [(p, a, b) for p, a, b in priced if a is not None and b is not None]
    cheaper = [(p, a, b) for p, a, b in have_both if a < b]
    same = [(p, a, b) for p, a, b in have_both if a == b]
    higher = [(p, a, b) for p, a, b in have_both if a > b]

    print("\n----- QUICK STATS -----")
    print(f"in stock: {len(instock)} | out of stock: {len(oos)} | email-activation: {len(act_email)}")
    print(f"price < publicPrice (API discount): {len(cheaper)}")
    print(f"price == publicPrice: {len(same)}")
    print(f"price > publicPrice: {len(higher)}")

    if have_both:
        discounts = []
        for p, a, b in have_both:
            if b > 0:
                discounts.append((1 - a / b) * 100)
        if discounts:
            discounts.sort()
            n = len(discounts)
            print(f"discount% range: {discounts[0]:.1f}% .. {discounts[-1]:.1f}% | median: {discounts[n//2]:.1f}%")

    # price range
    prices = sorted([a for _, a, _ in priced if a is not None])
    if prices:
        print(f"price range: ${prices[0]:.2f} .. ${prices[-1]:.2f}")

    # ---- Step 4: keyword match vs our anchor SKUs ----
    ANCHORS = {
        "netflix": "Netflix",
        "spotify": "Spotify",
        "chatgpt": "ChatGPT",
        "openai": "ChatGPT/OpenAI",
        "gemini": "Gemini",
        "youtube": "YouTube",
        "canva": "Canva",
        "office": "MS Office",
        "windows": "Windows",
        "discord": "Discord",
        "nitro": "Discord Nitro",
        "xbox": "Xbox",
        "game pass": "Xbox GPU",
        "playstation": "PlayStation",
        "psn": "PSN",
        "ps plus": "PS Plus",
        "steam": "Steam",
        "apple": "Apple",
        "itunes": "iTunes",
        "google play": "Google Play",
        "amazon": "Amazon",
        "midjourney": "Midjourney",
        "claude": "Claude",
        "vpn": "VPN",
        "adobe": "Adobe",
        "capcut": "CapCut",
        "prime": "Prime",
        "tinder": "Tinder",
        "shahid": "Shahid",
        "starz": "StarzPlay",
        "anghami": "Anghami",
        "pubg": "PUBG",
        "freefire": "Free Fire",
        "fortnite": "Fortnite",
        "roblox": "Roblox",
        "netflix premium": "Netflix Premium",
    }
    print("\n----- ANCHOR MATCHES (name-based) -----")
    matches = {}
    for p in plist:
        name = (p.get("name") or "").lower()
        desc = (p.get("description") or "").lower()
        blob = name + " || " + desc
        for kw, label in ANCHORS.items():
            if kw in blob:
                matches.setdefault(label, []).append(p)
    for label in sorted(matches):
        items = sorted(matches[label], key=lambda x: (num(x.get("price")) is None, num(x.get("price")) or 0))
        print(f"\n[{label}] — {len(items)} product(s):")
        for p in items[:8]:
            pr, pu = p.get("price"), p.get("publicPrice")
            stk = "IN-STOCK" if p.get("inStock") else "OOS"
            print(f"  - {p.get('name','?')[:58]:58s} | price=${pr} public=${pu} | {stk} | sold={p.get('sold','?')}")

    # Save matches
    with open(f"{OUT_DIR}/anchor_matches.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in matches.items()}, f, ensure_ascii=False, indent=2)

    report["steps"].append({
        "step": "products",
        "http": st,
        "count": len(plist),
        "in_stock": len(instock),
        "out_of_stock": len(oos),
        "email_activation": len(act_email),
        "api_cheaper_than_public": len(cheaper),
        "raw_file": raw_path,
    })
    with open(f"{OUT_DIR}/run_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n[DONE] Read-only extraction complete. No orders placed.")


if __name__ == "__main__":
    main()
