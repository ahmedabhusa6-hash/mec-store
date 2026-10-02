#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.5g | K4G catalog cross-match vs full 437-SKU catalog + merge accepted."""
import json, re

BASE = "/home/z/my-project"
cat = json.load(open(f"{BASE}/download/catalog_v42.json", encoding="utf-8"))
k4g = json.load(open(f"{BASE}/research/b3_k4g_catalog.json", encoding="utf-8"))
oi = json.load(open(f"{BASE}/download/offers_intelligence.json", encoding="utf-8"))

def norm(s): return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()

# K4G product -> catalog identity matcher (brand/product tokens)
MATCH_RULES = [
    # (k4g_title_tokens, catalog_matcher, grade_if_hit)
    (["duolingo super"], lambda s: "duolingo" in norm(s["brand"]+" "+s["product"]) and "12" in str(s.get("duration_denomination","")), "exact-12m"),
    (["tinder gold"], lambda s: "tinder" in norm(s["brand"]+" "+s["product"]) and "6" in str(s.get("duration_denomination","")), "strong"),
    (["minecraft"], lambda s: "minecraft" in norm(s["brand"]+" "+s["product"]) and "java" in norm(s["product"]), "exact"),
    (["grand theft auto"], lambda s: ("gta" in norm(s["brand"]+" "+s["product"]) or "grand theft" in norm(s["product"])), "exact"),
    (["farming simulator"], lambda s: "farming" in norm(s["product"]), "adjacent"),
    (["ready or not"], lambda s: "ready or not" in norm(s["product"]), "exact"),
    (["bodycam"], lambda s: "bodycam" in norm(s["product"]), "exact"),
    (["sons of the forest"], lambda s: "sons of the forest" in norm(s["product"]), "exact"),
    (["project zomboid"], lambda s: "zomboid" in norm(s["product"]), "exact"),
    (["control"], lambda s: "control" in norm(s["product"]) and "resonant" not in norm(s["product"]), "adjacent"),
]

matches = []
for p in k4g["products"]:
    t = norm(p["title"])
    for toks, matcher, grade in MATCH_RULES:
        if any(tok in t for tok in toks):
            for s in cat["skus"]:
                if matcher(s):
                    matches.append({"sku_id": s["sku_id"], "priority": s["priority"],
                                    "identity": f"{s['brand']} | {s['product']} | {s.get('duration_denomination','')} | {s.get('region','')}",
                                    "k4g_title": p["title"], "eur": p["eur"], "usd": p["usd"],
                                    "discount_pct": p.get("discount"), "grade": grade})
            break

# dedupe by sku_id (keep cheapest usd)
best = {}
for m in matches:
    if m["sku_id"] not in best or (m["usd"] or 9999) < (best[m["sku_id"]]["usd"] or 9999):
        best[m["sku_id"]] = m
final = sorted(best.values(), key=lambda m: m["usd"] or 9999)

print(f"matched: {len(final)}")
for m in final:
    print(f"{m['sku_id']} [{m['priority']}] {m['grade']:<10} USD {m['usd']:<7} EUR {m['eur']:<7} {m['identity'][:44]} <- {m['k4g_title'][:40]}")

# merge into offers_intelligence as k4g_run
k4g_run = {
    "run_id": "MEC2-20260927-K4G",
    "date": "2026-09-27",
    "method": "استخراج مضمّن من __NEXT_DATA__ لصفحة K4G الرئيسية (قناة محددة في Notion) — 21 منتجًا (bestsellers + upcoming) بأسعار EUR/USD مباشرة، بلا حصة",
    "matched": final,
    "unmatched_k4g_products": [p["title"] for p in k4g["products"] if not any(p["title"] == m["k4g_title"] for m in final)],
    "key_findings": [
        "Duolingo Super 12M عند $0.76/€0.65 (-99%) — تحقق متقاطع ثلاثي الطبقات: جملة ProdSeller $0.37 ← سوق K4G $0.76 ← تجزئة Evo Era $0.85 (السوق يتوسط الجملة والتجزئة كما متوقع)",
        "خصومات الأكثر مبيعًا -53..-99% — سوق المفاتيح في ذروة تفاوض على المنتجات الرقمية غير الألعاب أيضًا (Tinder Gold 6M $20.80)",
    ],
    "limitations": ["بيانات الصفحة الرئيسية فقط (bestsellers/upcoming) — ليس الكتالوج الكامل", "أسعار feature_offer لأرخص بائع في السوق", "لحظة 27/09"],
}
oi["k4g_run"] = k4g_run
json.dump(oi, open(f"{BASE}/download/offers_intelligence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# update catalog ledger for matched SKUs
cov = cat.get("coverage_ledger", {})
for m in final:
    sid = m["sku_id"]
    if sid in cov and isinstance(cov[sid], dict):
        cov[sid]["k4g_prefill"] = {"usd": m["usd"], "eur": m["eur"], "grade": m["grade"]}
json.dump(cat, open(f"{BASE}/download/catalog_v42.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nmerged: offers_intelligence.json += k4g_run | catalog ledger updated")
