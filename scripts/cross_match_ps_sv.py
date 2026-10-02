#!/usr/bin/env python3
"""
CROSS-MATCH: ProdSeller API live prices  ×  StackVault costPrice
===============================================================
Hypothesis: StackVault's internal costPrice == ProdSeller API price
(same source). This script verifies product-by-product.
"""
import json
import urllib.request
import os
from datetime import datetime, timezone

OUT = "/home/z/my-project/research/prodseller_live"

# --- Load ProdSeller live data (fetched today with valid key) ---
ps = json.load(open(f"{OUT}/products_raw.json"))["products"]

# --- Load StackVault data (B3 capture 2026-09-27) ---
sv = json.load(open("/home/z/my-project/research/b3_stackvault_api.json"))

# --- Live re-fetch StackVault (to be current) ---
print("Live re-fetch StackVault API...")
try:
    req = urllib.request.Request(
        sv["source"],
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
                 "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        live = json.loads(r.read().decode("utf-8"))
    live_prods = live if isinstance(live, list) else live.get("products", live.get("data", []))
    print(f"  LIVE OK: {len(live_prods)} products")
    with open(f"{OUT}/stackvault_live.json", "w", encoding="utf-8") as f:
        json.dump(live, f, ensure_ascii=False, indent=1)
    sv_prods = live_prods
    sv_source = sv["source"] + " (LIVE " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M") + ")"
except Exception as e:
    print(f"  LIVE FETCH FAILED ({type(e).__name__}: {e}) — using B3 capture 2026-09-27")
    sv_prods = sv["products"]
    sv_source = sv["source"] + " (B3 capture 2026-09-27)"

# --- Normalize names for matching ---
def norm(s):
    s = (s or "").lower().strip()
    for junk in ["✅", "🌐", "🎨", "😶‍🌫️", "😀", "📩", "🛡️", "🚚", "📦", "🦈", "😎", "⭐", "💼", "💰", "📝", "🍎", "🤖", "🤶", "🍿", "(can be monetized)"]:
        s = s.replace(junk, "")
    return " ".join(s.split())

# Manual mapping: ProdSeller product -> StackVault keyword(s)
MAPPING = [
    ("Capcut Pro 1 Month FW", ["capcut pro 1 month fw", "capcut pro 1 month"]),
    ("Capcut Pro 7D FW", ["capcut pro 7d fw", "capcut pro 7d"]),
    ("Capcut pro 6 days FW", ["capcut pro 6 days", "capcut 6 days", "capcut pro 6 days fw"]),
    ("CAPCUT PRO 6 MONTHS", ["capcut pro 6 months", "capcut 6 months"]),
    ("CAPCUT PRO 1600 CREDITS", ["capcut 1600", "1600 credits"]),
    ("Microsoft Office 365 Plus 1 year", ["office 365 plus 1 year", "microsoft office 365 plus"]),
    ("MS Office 365 Plus 12M", ["ms office 365 plus 12m", "office 365 plus 12m"]),
    ("Gemini Pro 18Months (link)", ["gemini pro 18", "gemini 18month", "gemini 18"]),
    ("Canva Pro 2 yrs FW", ["canva pro 2 yrs", "canva 2 yrs"]),
    ("Canva Pro Admin (500 invitations)", ["canva pro admin", "canva admin", "canva 500"]),
    ("ChatGPT Plus 1 Month", ["chatgpt plus 1 month", "chatgpt plus"]),
    ("Adobe Express 12M", ["adobe express 12"]),
    ("Gmails Accounts", ["gmails accounts", "gmail account"]),
    ("iLovePdf Premium 1Yr", ["ilovepdf"]),
    ("edX Premium 12Months", ["edx premium"]),
    ("Avira Prime 3 Months", ["avira prime"]),
    ("JetBrains Edu Pack 12m", ["jetbrains"]),
    ("Figma Pro Edu 2yrs", ["figma pro edu", "figma edu"]),
    ("Miro Lifetime Panel 100 invite", ["miro"]),
    ("Notion Plus 12M", ["notion plus 12", "notion edu"]),
    ("Duolingo Super 12M", ["duolingo super 12"]),
    ("Duolingo 12M new method", ["duolingo 12m new"]),
    ("Prime Video 6 Months", ["prime video 6"]),
    ("HBO MAX 3 MONTHS", ["hbo max 3 months", "hbo max - 3"]),
    ("HBO MAX 1 month", ["hbo max - 1 month", "hbo max 1 month"]),
    ("Autodesk Admin 3000 invite", ["autodesk"]),
    ("Framer AI 1 Year", ["framer"]),
]

print(f"\n{'='*95}")
print(f"CROSS-MATCH: ProdSeller API price  vs  StackVault costPrice")
print(f"ProdSeller: LIVE {datetime.now(timezone.utc).strftime('%Y-%m-%d')} (25 products) | StackVault: {sv_source}")
print(f"{'='*95}")
print(f"{'PRODUCT':40s} | {'PS-API':>7s} | {'SV-COST':>7s} | {'SV-RETAIL':>9s} | {'Δ cost':>6s} | VERDICT")
print("-" * 95)

results = []
for ps_name, kws in MAPPING:
    p = next((x for x in ps if norm(x["name"]) == norm(ps_name)), None)
    if p is None:
        p = next((x for x in ps if norm(ps_name).startswith(norm(x["name"])[:12])), None)
    if p is None:
        continue
    # find SV product
    sv_match = None
    for sp in sv_prods:
        nm = norm(sp.get("name", ""))
        if any(kw in nm for kw in kws):
            sv_match = sp
            break
    if sv_match is None:
        print(f"{ps_name[:40]:40s} | {p['price']:7.2f} | {'—':>7s} | {'—':>9s} | {'—':>6s} | no SV match")
        results.append({"product": ps_name, "ps_api": p["price"], "sv_cost": None, "sv_retail": None})
        continue
    ps_price = float(p["price"])
    sv_cost = float(sv_match.get("costPrice") or 0)
    sv_retail = float(sv_match.get("price") or 0)
    delta = abs(sv_cost - ps_price)
    verdict = "EXACT" if delta < 0.005 else ("±2¢" if delta <= 0.02 else ("CLOSE" if delta <= 0.30 else "DIFFERENT"))
    print(f"{ps_name[:40]:40s} | {ps_price:7.2f} | {sv_cost:7.2f} | {sv_retail:9.2f} | {delta:6.2f} | {verdict}")
    results.append({"product": ps_name, "ps_api": ps_price, "sv_cost": sv_cost,
                    "sv_retail": sv_retail, "delta": delta, "verdict": verdict,
                    "sv_name": sv_match.get("name"), "sv_stock": sv_match.get("stock")})

# Summary
matched = [r for r in results if r.get("sv_cost") is not None]
exact = [r for r in matched if r["verdict"] in ("EXACT", "±2¢")]
close = [r for r in matched if r["verdict"] == "CLOSE"]
diff = [r for r in matched if r["verdict"] == "DIFFERENT"]
print("-" * 95)
print(f"MATCHED: {len(matched)}/{len(results)} | EXACT/±2¢: {len(exact)} | CLOSE(≤$0.30): {len(close)} | DIFFERENT: {len(diff)}")
if exact:
    print("\n>>> CONFIRMED: StackVault costPrice ≈ ProdSeller API price — SAME WHOLESALE SOURCE")
    print(">>> StackVault retail markup over cost:")
    for r in sorted(matched, key=lambda x: x.get("sv_retail", 0) or 0):
        if r["sv_retail"]:
            mk = (1 - r["sv_cost"] / r["sv_retail"]) * 100
            print(f"    {r['product'][:38]:38s}: retail ${r['sv_retail']:.2f} = +{mk:.0f}% over cost ${r['sv_cost']:.2f}")

with open(f"{OUT}/cross_match_ps_stackvault.json", "w", encoding="utf-8") as f:
    json.dump({"generated": datetime.now(timezone.utc).isoformat(), "sv_source": sv_source,
               "results": results}, f, ensure_ascii=False, indent=2)
print(f"\nSaved -> {OUT}/cross_match_ps_stackvault.json")
