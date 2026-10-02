#!/usr/bin/env python3
"""StackVault API data analysis — price vs costPrice (internal cost layer)"""
import json

d = json.load(open('/home/z/my-project/research/b3_stackvault_api.json'))
prods = d['products']
print(f"Source: {d['source']}")
print(f"Total products: {len(prods)}\n")

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

# Structure sample
print("=== SAMPLE PRODUCT (full fields) ===")
print(json.dumps(prods[1] if len(prods) > 1 else prods[0], ensure_ascii=False, indent=1)[:900])
print()

# Analysis: price vs costPrice
both = []
for p in prods:
    pr, cp = num(p.get('price')), num(p.get('costPrice'))
    if pr is not None and cp is not None and cp > 0:
        both.append((p, pr, cp))

print(f"Products with price+costPrice>0: {len(both)}")
if both:
    gaps = []
    for p, pr, cp in both:
        if pr > 0:
            gaps.append((1 - cp / pr) * 100)  # markup of retail over cost
    gaps.sort()
    n = len(gaps)
    print(f"cost as % of retail: {100-gaps[-1]:.1f}% .. {100-gaps[0]:.1f}% | median: {100-gaps[n//2]:.1f}%")
    print(f"retail markup over cost: {gaps[0]:.1f}% .. {gaps[-1]:.1f}% | median: {gaps[n//2]:.1f}%\n")

    # Top sellers / most relevant anchor products
    print("=== KEY PRODUCTS (anchor families) ===")
    KW = ['netflix', 'spotify', 'chatgpt', 'gemini', 'youtube', 'canva', 'office', 'windows',
          'prime', 'hbo', 'max', 'duolingo', 'adobe', 'notion', 'capcut', 'grammarly', 'linkedin',
          'coursera', 'edx', 'figma', 'jetbrains', 'discord', 'nitro', 'xbox', 'game pass',
          'playstation', 'psn', 'steam', 'apple', 'google play', 'amazon', 'tinder', 'vpn',
          'midjourney', 'claude', 'ai', 'shahid', 'anghami', 'starz']
    seen = set()
    rows = []
    for p, pr, cp in both:
        name = (p.get('name') or '').lower()
        for kw in KW:
            if kw in name and p['id'] not in seen:
                seen.add(p['id'])
                rows.append((p.get('name'), pr, cp, p.get('stock'), p.get('sold') or p.get('sales') or '?'))
                break
    rows.sort(key=lambda r: r[1])
    print(f"{'PRODUCT':52s} | {'RETAIL':>7s} | {'COST':>7s} | {'MARGIN%':>7s} | STOCK")
    for name, pr, cp, stk, sold in rows[:60]:
        margin = (1 - cp / pr) * 100 if pr > 0 else 0
        print(f"{name[:52]:52s} | {pr:7.2f} | {cp:7.2f} | {margin:6.1f}% | {stk}")

# Categories
print("\n=== CATEGORIES ===")
cats = {}
for p in prods:
    c = p.get('categoryName') or p.get('category') or '?'
    cats[c] = cats.get(c, 0) + 1
for c, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {c}: {n}")
