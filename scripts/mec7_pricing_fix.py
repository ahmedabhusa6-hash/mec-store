#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-7.0 PRICING FIX — يبني مفتاح pricing المفقود في mec7.json
السبب: انقطعت الجلسة السابقة قبل حقن جدول التسعير (المكوّن mec7.tsx يستدعي d.pricing
        وكان سينهار التبويب عند الفتح بخطأ TypeError).

المصادر (كلها ملفات موثقة بتاريخ 28/09):
- research/prodseller_live/products_raw.json  (25 منتجاً — تكلفة API الحية + publicPrice + sold + inStock)
- research/prodseller_live/cross_match_live.json (أسعار StackVault التجزئة للمطابقات)
- نطاقات السوق الموثقة من MEC-2/3 (Evo Era Duolingo $0.85، K4G $0.76، GamsGo CapCut $7.49...)

المعادلة الموحدة (تُعلن في التبويب):
  net = rec − cost − round(1.5% × rec, 2) − round(prov% × rec, 2)
  prov: مستقر 3% · متوسط 8% · هش 15% (من سعر البيع — نفس أساس مثالي Gemini وChatGPT)
  net_pct = net / rec × 100

إصلاح إضافي: مثال CapCut في unit_economics.worked كان prov=0.08 (لم تُطبق نسبة 8% على السعر)
→ يُعاد حسابه بالمعادلة الموحدة ليطابق صف الجدول.
"""
import json, copy

BASE = "/home/z/my-project"
PS = f"{BASE}/research/prodseller_live/products_raw.json"
XM = f"{BASE}/research/prodseller_live/cross_match_live.json"
OUT = f"{BASE}/src/lib/data/mec7.json"

# ── قراءة المصادر الحية ──────────────────────────────────────────────
with open(PS, encoding="utf-8") as f:
    ps_products = json.load(f)["products"]
with open(XM, encoding="utf-8") as f:
    xm = {m["label"]: m for m in json.load(f)["matched"]}

# ── قرارات التسعير (rec = قرار تسعير [مستنتج] مرتكز على أرضية حية + نطاق منافس موثق) ──
# name_match: يطابق اسم المنتج في products_raw.json
# rec: السعر المقترح | fragility: stable/medium/fragile | market: نطاق المنافس الموثق
DECISIONS = [
    # (اسم المنتج في API,                     rec,   fragility, market, مصدر النطاق)
    ("Gemini Pro 18Months (link)",            0.69, "stable",  "0.48–1.00", "PS public 0.48 · SV 0.52 · ذروة الندرة 1.00 (ساغا موثقة)"),
    ("Capcut Pro 1 Month FW",                 1.99, "medium",  "1.29–7.49", "PS public 1.29 · SV 1.60 · GamsGo 7.49"),
    ("Microsoft Office 365 Plus 1 year",      0.45, "medium",  "0.29–0.38", "PS public 0.29 · SV 0.38"),
    ("ChatGPT Plus 1 Month ",                 4.99, "fragile", "3.40–5.50", "PS public 3.40 · Evo Era 2HW 4.50–5.50"),
    ("Canva Pro Admin (500 invitations)",     5.60, "medium",  "4.50–5.28", "PS public 4.50 · SV 5.28"),
    ("Canva Pro 2 yrs FW",                    0.95, "medium",  "0.60–1.20", "PS public 0.60 (بلا SV — بناء خاص)"),
    ("Prime Video 6 Months ",                 2.45, "medium",  "1.70–2.35", "PS public 1.70 · SV بناء مجاور 2.35"),
    ("Capcut Pro 7D FW",                      0.22, "stable",  "0.14–0.20", "PS public 0.14 · SV 0.20"),
    ("Notion Plus 12M",                       1.45, "medium",  "1.30–2.00", "PS public 1.30 (SV بناء Business مختلف الهوية)"),
    ("Adobe Express 12M",                     0.69, "stable",  "0.39–0.64", "PS public 0.39 · SV 0.64"),
    ("Gmails Accounts",                       0.80, "stable",  "0.60–0.80", "PS public 0.65 · SV 0.77 · سوق Gmail المعتّق 0.60–0.80"),
    ("iLovePdf Premium 1Yr",                  0.69, "medium",  "0.58–0.69", "SV 0.58 · PS public 0.60"),
    ("Miro Lifetime Panel 100 invite",        9.99, "stable",  "9.00–9.99", "PS public 9.00 · SV 9.60"),
    ("Figma Pro Edu 2yrs",                    4.60, "medium",  "3.60–4.60", "PS public 3.60 · SV 4.60"),
    ("CAPCUT PRO 6 MONTHS ",                 10.99, "medium",  "9.00–10.99", "PS public 9.00 · SV 9.99"),
    ("edX Premium 12Months",                  1.45, "medium",  "1.30–1.60", "PS public 1.30 · SV 1.30"),
    ("Avira Prime 3 Months ",                 1.10, "medium",  "0.90–1.10", "PS public 0.90 · SV 0.99"),
    ("JetBrains Edu Pack 12m",                3.90, "medium",  "3.00–3.90", "PS public 3.00 · SV 3.00"),
    ("Framer AI 1 Year ",                     8.00, "stable",  "6.00–8.00", "PS public 6.00 · SV 7.20"),
    ("Autodesk Admin 3000 invite",           11.99, "stable",  "11.00–13.00", "PS public 11.00 (SV بناء 1-تطبيق مختلف الهوية)"),
    ("HBO MAX 3 MONTHS",                      2.30, "medium",  "1.80–2.45", "PS public 1.80 (بلا SV)"),
    ("CAPCUT PRO 1600 CREDITS",               2.30, "stable",  "1.65–2.30", "PS public 1.65 · SV 2.05"),
    ("Duolingo Super 12M",                    0.85, "stable",  "0.48–0.85", "PS public 0.48 · K4G 0.76 · Evo Era 0.85"),
    ("Capcut pro 6 days FW",                  0.15, "stable",  "0.10–0.15", "PS public 0.10"),
    ("Duolingo 12M new method",               0.29, "stable",  "0.20–0.29", "PS public 0.20 · SV 0.23"),
]
PROV = {"stable": 0.03, "medium": 0.08, "fragile": 0.15}

def r2(x):
    return round(x + 1e-9, 2)

# ── بناء الصفوف ──────────────────────────────────────────────────────
rows, unmatched = [], []
for name, rec, frag, market, _src in DECISIONS:
    # إيجاد المنتج في API الحي (مطابقة اسم مقارنة بالمقاطع الأولى لتفادي اختلاف المسافات)
    prod = next((p for p in ps_products if p["name"].strip().lower() == name.strip().lower()), None)
    if prod is None:  # محاولة ثانية: تجاهل الحالة والمسافات الزائدة
        prod = next((p for p in ps_products if " ".join(p["name"].split()).lower() == " ".join(name.split()).lower()), None)
    if prod is None:
        unmatched.append(name)
        continue
    cost = float(prod["price"])
    fee = r2(0.015 * rec)
    prov = r2(PROV[frag] * rec)
    net = r2(rec - cost - fee - prov)
    pct = round(net / rec * 100, 1)
    rows.append({
        "name": prod["name"].strip(),
        "cost": cost,
        "rec": rec,
        "net": net,
        "net_pct": pct,
        "market": market,
        "fragility": frag,
        "in_stock": bool(prod.get("inStock")),
        "sold": int(prod.get("sold") or 0),
    })

assert not unmatched, f"منتجات بلا مطابقة في API الحي: {unmatched}"
assert len(rows) == 25, f"عدد الصفوف {len(rows)} ≠ 25"
# فحص الأرضية: لا صف يبيع بخسارة، وكل هامش ≥ 10% من السعر (السياسة المعلنة)
for r in rows:
    assert r["net"] > 0, f"هامش سالب: {r['name']}"
    assert r["net_pct"] >= 10.0, f"هامش < 10%: {r['name']} ({r['net_pct']}%)"

avg_net = round(sum(r["net"] for r in rows) / len(rows), 2)
total_net_basket = round(sum(r["net"] for r in rows), 2)

# ── الحقن في mec7.json ───────────────────────────────────────────────
with open(OUT, encoding="utf-8") as f:
    data = json.load(f)

data["pricing"] = rows
data["pricing_meta"] = {
    "built_by": "scripts/mec7_pricing_fix.py",
    "cost_source": "ProdSeller API live 28/09 (research/prodseller_live/products_raw.json)",
    "formula": "net = rec − cost − رسوم دفع 1.5% من السعر − مخصص ضمان (3%/8%/15% من السعر حسب الهشاشة)",
    "avg_net_usd": avg_net,
    "total_net_basket_usd": total_net_basket,
    "rec_class": "مستنتج (قرار تسعير): أرضية = تكلفة API حية · سقف = نطاق المنافس الموثق",
    "note": "متوسط بسيط عبر الـ25 SKU عند أسعارها المقترحة؛ الافتراض التخطيطي المحافظ $0.25/وحدة (مزيج واقعي مرجّح بالمنتجات الرخيصة الأعلى دوراناً)",
}

# ── إصلاح مثال CapCut في worked (كان prov=0.08 بلا تطبيق للنسبة الموحدة) ──
for w in data["unit_economics"]["worked"]:
    if "CapCut" in w["item"]:
        w["prov"] = r2(0.08 * 1.99)   # 0.16
        w["fee"] = r2(0.015 * 1.99)   # 0.03
        w["net"] = r2(1.99 - 1.25 - 0.03 - 0.16)  # 0.55
        w["pct"] = round(w["net"] / 1.99 * 100, 1)  # 27.6

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f"✅ تم حقن pricing: {len(rows)} صفاً")
print(f"   متوسط الهامش الصافي/وحدة عند السعر المقترح: ${avg_net}")
print(f"   صافي السلة الكاملة (وحدة واحدة من كل SKU): ${total_net_basket}")
print(f"   مثال CapCut المُصحح: net=$0.55 · 27.6%")
print("\nجدول التحقق (اسم | تكلفة | سعر | صافٍ | % | هشاشة | مخزون):")
for r in rows:
    print(f"   {r['name'][:36]:38} {r['cost']:>6.2f} {r['rec']:>6.2f} {r['net']:>6.2f} {r['net_pct']:>5.1f}% {r['fragility']:7} {'✓' if r['in_stock'] else 'OOS'}")
