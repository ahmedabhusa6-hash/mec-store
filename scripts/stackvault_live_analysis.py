#!/usr/bin/env python3
"""LIVE StackVault (322 products) analysis: cost layer + ProdSeller cross-match + markup table"""
import json
from datetime import datetime, timezone

OUT = "/home/z/my-project/research/prodseller_live"
ps = json.load(open(f"{OUT}/products_raw.json"))["products"]
sv_live = json.load(open(f"{OUT}/stackvault_live.json"))
sv = sv_live if isinstance(sv_live, list) else sv_live.get("products", sv_live.get("data", []))
print(f"LIVE StackVault products: {len(sv)}\n")

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

# --- Full catalog stats ---
both = [(p, num(p.get("price")), num(p.get("costPrice"))) for p in sv]
both = [(p, pr, cp) for p, pr, cp in both if pr and cp and cp > 0]
print(f"With price+cost: {len(both)}")
gaps = sorted((1 - cp / pr) * 100 for _, pr, cp in both)
n = len(gaps)
print(f"Markup over cost: {gaps[0]:.1f}% .. {gaps[-1]:.1f}% | median {gaps[n//2]:.1f}%")

# --- Cost = retail products (zero margin, promos) ---
zero = [(p, pr, cp) for p, pr, cp in both if abs(pr - cp) < 0.005]
print(f"Zero-margin (price==cost): {len(zero)}")

# --- Cross-match vs ProdSeller ---
def norm(s):
    s = (s or "").lower()
    for j in ["✅","🌐","🎨","😶‍🌫️","😀","📩","🛡️","🚚","📦","🦈","😎","⭐","💼","💰","📝","🍎","🤖","🤶","🍿","🔥","⚡","(fw)","full warranty"]:
        s = s.replace(j, "")
    return " ".join(s.split())

MAPPING = {
    "capcut pro 1 month": "CapCut Pro 1M",
    "capcut pro 7d": "CapCut Pro 7D",
    "capcut pro 6 days": "CapCut 6-days",
    "capcut pro 6 months": "CapCut Pro 6M",
    "1600 credits": "CapCut 1600cr",
    "office 365 plus 1 year": "Office365 1yr",
    "ms office 365 plus 12m": "Office365 12M",
    "gemini": "Gemini 18M",
    "canva pro admin": "Canva Admin500",
    "chatgpt plus": "ChatGPT Plus 1M",
    "adobe express 12": "Adobe Express 12M",
    "gmails accounts": "Gmail fresh",
    "ilovepdf": "iLovePDF 1yr",
    "edx premium": "edX 12M",
    "avira prime": "Avira 3M",
    "jetbrains": "JetBrains 12m",
    "figma pro edu": "Figma 2yrs",
    "miro": "Miro 100",
    "notion": "Notion 12M",
    "duolingo": "Duolingo 12M",
    "prime video 6": "PrimeVideo 6M",
    "hbo max 3": "HBO 3M",
    "hbo max - 3": "HBO 3M",
    "autodesk": "Autodesk 3000",
    "framer": "Framer 1yr",
}
ps_by_norm = {norm(p["name"]): p for p in ps}

print(f"\n{'='*100}")
print(f"CROSS-MATCH (LIVE): ProdSeller API × StackVault cost | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
print(f"{'='*100}")
print(f"{'PRODUCT':18s} | {'PS-API':>6s} | {'SV-COST':>7s} | {'SV-RETAIL':>9s} | {'MARKUP':>6s} | VERDICT")
print("─" * 100)
matched = []
for kw, label in MAPPING.items():
    ps_p = None
    for k2, v in ps_by_norm.items():
        if kw in k2 or k2 in kw:
            ps_p = v
            break
    sv_p = next((s for s in sv if kw in norm(s.get("name", ""))), None)
    if not sv_p:
        continue
    ps_price = num(ps_p["price"]) if ps_p else None
    sv_cost, sv_retail = num(sv_p.get("costPrice")), num(sv_p.get("price"))
    if ps_price is None:
        print(f"{label:18s} | {'—':>6s} | {sv_cost:7.2f} | {sv_retail:9.2f} | {(1-sv_cost/sv_retail)*100:5.0f}% | SV-only")
        continue
    delta = abs(sv_cost - ps_price)
    verdict = "EXACT" if delta < 0.005 else ("±2¢" if delta <= 0.02 else ("CLOSE" if delta <= 0.3 else "DIFF"))
    mk = (1 - sv_cost / sv_retail) * 100 if sv_retail else 0
    print(f"{label:18s} | {ps_price:6.2f} | {sv_cost:7.2f} | {sv_retail:9.2f} | {mk:5.0f}% | {verdict}")
    matched.append({"label": label, "ps_api": ps_price, "sv_cost": sv_cost, "sv_retail": sv_retail,
                    "delta": delta, "verdict": verdict, "markup_pct": round(mk, 1),
                    "sv_stock": sv_p.get("stock"), "sv_name": sv_p.get("name")})

ex = [m for m in matched if m["verdict"] in ("EXACT", "±2¢")]
print("─" * 100)
print(f"MATCHED: {len(matched)} | EXACT/±2¢: {len(ex)} | CLOSE: {len([m for m in matched if m['verdict']=='CLOSE'])} | DIFF: {len([m for m in matched if m['verdict']=='DIFF'])}")

# --- NEW products in live SV (not in B3 capture) ---
b3 = {norm(p.get("name","")) for p in json.load(open("/home/z/my-project/research/b3_stackvault_api.json"))["products"]}
new = [p for p in sv if norm(p.get("name","")) not in b3]
print(f"\nNEW in LIVE vs B3 capture: {len(new)}")
for p in new[:25]:
    print(f"  + {p.get('name','')[:55]:55s} | ${p.get('price')} (cost ${p.get('costPrice')}) | stock {p.get('stock')}")

# --- Gemini search in SV (bestseller check) ---
print("\nGEMINI products in SV:")
for p in sv:
    if "gemini" in norm(p.get("name", "")):
        print(f"  · {p.get('name','')[:60]:60s} | ${p.get('price')} (cost ${p.get('costPrice')}) | stock {p.get('stock')}")

with open(f"{OUT}/cross_match_live.json", "w", encoding="utf-8") as f:
    json.dump({"ts": datetime.now(timezone.utc).isoformat(), "sv_count": len(sv),
               "matched": matched, "new_count": len(new)}, f, ensure_ascii=False, indent=2)
print(f"\nSaved -> {OUT}/cross_match_live.json")
