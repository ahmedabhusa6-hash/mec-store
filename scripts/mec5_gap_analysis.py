#!/usr/bin/env python3
"""
MEC-5.0 API Price Gap Analysis Engine
Mission: uncover public vs API/wholesale price gaps for all providers offering
differential API pricing. Sources: ProdSeller channel archive (79 posts),
StackVault exposed API (275 products with price + costPrice).

Output: research/mec5/api_gap_master.json + human-readable tables.
"""
import json, re, os
from datetime import datetime, timezone

BASE = "/home/z/my-project"
OUT_DIR = f"{BASE}/research/mec5"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 1) PRODSELLER — extract every dual/triple price point from channel archive
# ============================================================
def parse_prodseller():
    posts = json.load(open(f"{BASE}/research/deep_dive/prodseller_channel_archive.json"))
    rows = []  # each: product, public, api, bulk, date, post, tier_note

    def add(product, pub, api, bulk, date, note=""):
        rows.append({
            "product": product, "public_usd": pub, "api_usd": api, "bulk_usd": bulk,
            "date": date[:10], "tier_note": note,
        })

    # Hand-extracted from the 79 archived posts (verified against raw text)
    D = [
        # (product, public, api, bulk, iso_date, note)
        ("CapCut Pro 30d",            1.70, None, 1.65, "2026-07-08", "bulk +5"),
        ("Notion (reseller)",         1.40, None, 1.20, "2026-07-13", "bulk +3"),
        ("Adobe Express 12M",         0.94, None, 0.85, "2026-07-17", "bulk 5+"),
        ("Gemini 18M",                0.55, 0.43, None, "2026-07-21", ""),
        ("Outlook/Hotmail ready-made",0.02, 0.015,None, "2026-07-23", "cheapest input"),
        ("iLovePDF 1Y",               1.00, 0.80, None, "2026-07-23", "13:16 post"),
        ("iLovePDF 1Y (disc)",        0.80, 0.70, None, "2026-07-23", "16:48 post"),
        ("Spotify Premium 3M",        0.95, 0.85, None, "2026-07-23", ""),
        ("Coursera Plus 1Y",          1.00, 0.84, None, "2026-07-24", ""),
        ("Office 365 1Y",             0.30, 0.20, None, "2026-07-24", "full warranty"),
        ("CapCut Pro Team 30d",       1.55, 1.45, None, "2026-07-24", ""),
        ("Gemini 18M links (restock)",0.50, 0.46, None, "2026-07-25", ""),
        ("Adobe CC Admin 14 inv",     3.70, 3.30, None, "2026-07-25", "10-day warranty"),
        ("Canva Pro EDU Admin",       5.50, 5.00, None, "2026-07-26", ""),
        ("Gemini 18M (new method)",   1.00, 0.95, None, "2026-07-28", "post-shortage"),
        ("Gemini 18M",                0.75, 0.70, None, "2026-07-30", ""),
        ("Gemini Pro 18M",            0.59, 0.50, None, "2026-07-31", ""),
        ("Gemini Pro 18M",            0.50, 0.45, None, "2026-08-01", "11:16"),
        ("Gemini Pro 18M flash 500x", 0.46, 0.41, None, "2026-08-01", "14:41 flash"),
        ("Gemini Pro 18M flash",      0.45, 0.39, None, "2026-08-04", ""),
        ("CapCut Pro Private",        1.39, 1.29, None, "2026-08-05", ""),
        ("Gemini Pro 18M",            0.44, 0.41, None, "2026-08-16", ""),
        ("Gemini 18M flash",          0.43, 0.40, 0.39, "2026-09-11", "official 3-tier image #134"),
        ("Gemini 18M flash",          0.59, 0.55, None, "2026-09-19", "08:00"),
        ("Duolingo Super 12M",        0.59, 0.55, 0.50, "2026-09-19", "14:06"),
        ("Gmail stable",              0.80, 0.75, 0.60, "2026-09-19", "14:14"),
        ("Gemini 18M",                0.53, 0.50, None, "2026-09-19", "20:21"),
        ("Gemini 18M flash",          0.49, None, 0.45, "2026-09-20", "05:51"),
        ("ChatGPT K12 w/ Codex",      3.90, 3.80, None, "2026-09-20", "24h warranty"),
        ("Office 365 Plus 1Y",        0.29, 0.17, None, "2026-09-20", "5 devices"),
        ("CapCut 7 days",             0.14, 0.13, 0.12, "2026-09-23", "07:22"),
        ("CapCut 6 days",             0.10, 0.09, 0.09, "2026-09-23", "17:07"),
        ("Adobe Express 12M",         0.39, 0.37, None, "2026-09-23", "19:24 activation link"),
        ("Duolingo Super 12M",        0.45, 0.36, 0.34, "2026-09-24", ""),
        ("Gemini 18M flash",          0.69, None, 0.66, "2026-09-25", "15:25"),
        ("Gemini 18M",                0.65, None, 0.63, "2026-09-25", "20:17"),
        ("Gemini 18M",                0.48, None, 0.44, "2026-09-27", "10:05 latest"),
        ("CapCut 1 Month",            1.29, 1.25, 1.20, "2026-09-27", "13:40 latest"),
    ]
    for tup in D:
        add(*tup)

    # compute gaps
    for r in rows:
        ref = r["public_usd"]
        if r["api_usd"] is not None:
            r["api_gap_pct"] = round((ref - r["api_usd"]) / ref * 100, 1)
            r["api_ratio"] = round(r["api_usd"] / ref, 3)
        else:
            r["api_gap_pct"] = None; r["api_ratio"] = None
        if r["bulk_usd"] is not None:
            r["bulk_gap_pct"] = round((ref - r["bulk_usd"]) / ref * 100, 1)
        else:
            r["bulk_gap_pct"] = None

    gaps = [r["api_gap_pct"] for r in rows if r["api_gap_pct"] is not None]
    bgaps = [r["bulk_gap_pct"] for r in rows if r["bulk_gap_pct"] is not None]
    summary = {
        "provider": "ProdSeller",
        "n_posts_scanned": len(posts),
        "n_dual_price_rows": len(rows),
        "n_with_api_price": len(gaps),
        "api_gap_pct": {
            "min": min(gaps), "max": max(gaps),
            "avg": round(sum(gaps)/len(gaps), 1),
            "median": sorted(gaps)[len(gaps)//2],
        },
        "bulk_gap_pct": {
            "min": min(bgaps), "max": max(bgaps),
            "avg": round(sum(bgaps)/len(bgaps), 1),
        } if bgaps else None,
        "structural_evidence": {
            "admin_panel_dual_field": "Official screenshot post #132 (09/09): product form has 'Price (USD)' + 'API Price (optional)' — CapCut Pro 1M FW $1.37 / API $1.29",
            "official_3tier_image": "Post #134 (11/09) image: FLASH SELL $0.43 / API PRICE $0.40 / BULK PRICE $0.39 (Gemini 18M)",
            "api_docs_dual_field": "prodseller.com/api-docs: GET /v1/products returns 'price' (charged) + 'publicPrice' (reference)",
            "marketing_claim": "Post 20/07: 'up to 35% OFF compared to public prices' for API bot users",
        },
    }
    return rows, summary


# ============================================================
# 2) STACKVAULT — 275 products with exposed price + costPrice
# ============================================================
def parse_stackvault():
    d = json.load(open(f"{BASE}/research/b3_stackvault_api.json"))
    prods = [p for p in d["products"] if p.get("price", 0) > 0 and p.get("costPrice", 0) > 0]
    rows = []
    for p in prods:
        price, cost = p["price"], p["costPrice"]
        rows.append({
            "product": p["name"][:80],
            "category": p.get("categoryName", "?"),
            "public_usd": price,
            "cost_usd": cost,
            "gap_pct": round((price - cost) / price * 100, 1),
            "markup_multiple": round(price / cost, 2) if cost else None,
            "stock": p.get("stock"),
        })
    rows.sort(key=lambda r: -r["gap_pct"])
    gaps = [r["gap_pct"] for r in rows]
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r["gap_pct"])
    cat_stats = {c: {"n": len(v), "avg_gap_pct": round(sum(v)/len(v), 1)} for c, v in sorted(by_cat.items(), key=lambda kv: -len(kv[1]))}
    summary = {
        "provider": "StackVault (stackvault.shop / decohomz.com backend)",
        "source": d["source"],
        "n_products_total": d["n"],
        "n_with_dual_price": len(rows),
        "gap_pct": {
            "min": min(gaps), "max": max(gaps),
            "avg": round(sum(gaps)/len(gaps), 1),
            "median": sorted(gaps)[len(gaps)//2],
        },
        "by_category": cat_stats,
        "note": "costPrice = actual input/cost price exposed by API; public price = what the platform charges buyers. This is the platform's OWN margin structure, fully public.",
    }
    return rows, summary


def main():
    ps_rows, ps_sum = parse_prodseller()
    sv_rows, sv_sum = parse_stackvault()

    # ProdSeller: latest price per product (most recent post wins)
    latest = {}
    for r in ps_rows:
        k = r["product"].split("(")[0].strip()
        latest[k] = r  # rows are chronological

    master = {
        "run": "MEC-5.0 API price gap discovery",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "mission": "Uncover public vs API-tier prices for all providers offering differential API pricing",
        "prodseller": {
            "summary": ps_sum,
            "all_rows": ps_rows,
            "latest_per_product": list(latest.values()),
        },
        "stackvault": {
            "summary": sv_sum,
            "top20_gap": sv_rows[:20],
            "bottom10_gap": sv_rows[-10:],
            "all_rows": sv_rows,
        },
    }
    out = f"{OUT_DIR}/api_gap_master.json"
    json.dump(master, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"saved {out} ({os.path.getsize(out)} bytes)")

    # Human tables
    print("\n" + "="*70)
    print("PRODSELLER — API vs PUBLIC (all", len(ps_rows), "rows )")
    print("="*70)
    print(f"{'Product':32} {'Public':>7} {'API':>7} {'Bulk':>7} {'API gap%':>9}")
    for r in ps_rows:
        print(f"{r['product'][:32]:32} {r['public_usd']:>7} {str(r['api_usd']):>7} {str(r['bulk_usd']):>7} {str(r['api_gap_pct']):>9}")
    print("\nAPI gap stats:", json.dumps(ps_sum["api_gap_pct"]))
    print("Bulk gap stats:", json.dumps(ps_sum["bulk_gap_pct"]))

    print("\n" + "="*70)
    print("STACKVAULT — costPrice vs price (", len(sv_rows), "products )")
    print("="*70)
    print(f"{'Product':50} {'Price':>7} {'Cost':>7} {'Gap%':>6} {'x':>5}")
    for r in sv_rows[:25]:
        print(f"{r['product'][:50]:50} {r['public_usd']:>7} {r['cost_usd']:>7} {r['gap_pct']:>6} {r['markup_multiple']:>5}")
    print("...")
    print("\nGap stats:", json.dumps(sv_sum["gap_pct"]))
    print("\nBy category:")
    for c, s in list(sv_sum["by_category"].items())[:10]:
        print(f"  {c:30} n={s['n']:>3} avg_gap={s['avg_gap_pct']}%")


if __name__ == "__main__":
    main()
