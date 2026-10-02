#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.4 | Next.js data prep: channel-matrix.json (compact for the app tab)."""
import json, os
BASE = "/home/z/my-project"
MX = json.load(open(f"{BASE}/download/channel_matrix.json", encoding="utf-8"))

rows = []
for r in MX["matrix_layerA"]:
    rows.append({
        "id": r["id"], "type": r["type"], "cluster": r["cluster"].split(" / ")[0],
        "layer": r["layer"], "risk": r["risk_grade"][:80],
        "anchor": round(r["min_price_anchor_usd"], 2) if r.get("min_price_anchor_usd") is not None else None,
        "fit": r["dolaa_fit"], "subs": (r.get("subscribers") or "")[:40],
    })
for d in MX["discovered_entities"]:
    a = d.get("min_price_anchor_usd")
    rows.append({
        "id": d["id"], "type": d["type"], "cluster": "مكتشف (27/09)",
        "layer": d["layer"], "risk": d["risk_grade"][:80],
        "anchor": round(a, 3) if a is not None else None,
        "fit": d["dolaa_fit"], "subs": "-",
    })

# layer distribution
from collections import Counter
dist = dict(Counter(r["layer"] for r in rows))

mkt = [{"channel": m["channel"], "n_offers": m["n_offers"]} for m in MX["matrix_layerB_marketplaces"][:20]]

out = {
    "run": "MEC-2.4 مصفوفة القنوات + الهندسة العكسية لنموذج دولا",
    "date": "2026-09-27",
    "totals": {
        "registry": len(MX["matrix_layerA"]),
        "discovered": len(MX["discovered_entities"]),
        "marketplaces": len(MX["matrix_layerB_marketplaces"]),
        "all": len(MX["matrix_layerA"]) + len(MX["discovered_entities"]) + len(MX["matrix_layerB_marketplaces"]),
    },
    "layer_distribution": dist,
    "sv_formula": MX["stackvault_cost_layer"],
    "channels": rows,
    "marketplaces_top": mkt,
    "hypotheses": [
        {"h": "H1 التحكيم الإقليمي", "mech": "شراء بمناطق رخيصة (لبنان/الهند/تركيا/الأرجنتين) وإعادة بيع خليجيًا", "evidence": "قوية — PSN لبنان $9.07 · Spotify هندي $0.79/ش · خصومات TR/AR 38-46%", "covers": "البطاقات + اشتراكات الألعاب + Spotify", "sustain": "عالية — فروق بنية تعرفة الناشر"},
        {"h": "H2 الجملة/API", "mech": "حساب موزع وشراء بالكتالوج (ProdSeller-style)", "evidence": "قوية جدًا — 274 كلفة داخلية مرصودة · ChatGPT من $2.80 · إعلان خصم API حتى 35%", "covers": "كل عائلات AI/SaaS + البرمجيات", "sustain": "الأعلى — نموذج الشركة نفسه"},
        {"h": "H3 التصنيع الرمادي", "mech": "مصانع حسابات UPI + مفاتيح حجمية + روابط Pixel", "evidence": "متوسطة-قوية — Win11 €1.03 · Office2024 €0.56 · SheerID موثقة نصًا", "covers": "المفاتيح الرمادية + حسابات AI الهشة", "sustain": "هشة — قابلة للترقيع (رُصد فعليًا 12→6 أشهر)"},
        {"h": "H4 التقسيم المؤسسي", "mech": "مقاعد Teams/Edu تُقسم وتباع", "evidence": "متوسطة — Canva 500-لوحة $2.50 · Duolingo $0.50 · MS365 مقعد $21.67 نظري", "covers": "Canva · Coursera · MS365 · Duolingo", "sustain": "متوسطة — حتى مراجعة عقود المؤسسات"},
    ],
    "margin_calc": [
        {"product": "ChatGPT Plus شهر", "floor": "$2.80", "stable": "$10.67", "official": "$20.00"},
        {"product": "Netflix شهر", "floor": "≈$3.33", "stable": "—", "official": "$26.99"},
        {"product": "Spotify شهر", "floor": "$0.79", "stable": "$3.74", "official": "$12.99"},
        {"product": "MS365 سنة", "floor": "$0.21", "stable": "$8.33", "official": "$129.99"},
        {"product": "Office 2024", "floor": "$0.60", "stable": "$2.63", "official": "$249.99"},
        {"product": "Xbox GPU شهر", "floor": "$4.00", "stable": "$14.09", "official": "$22.99"},
        {"product": "PSN $10 أمريكي", "floor": "$9.07", "stable": "الاسمي -1..15%", "official": "$10.00"},
    ],
    "verdict": "لا قناة واحدة تفسّر كتالوجًا عريضًا — محفظة مركبة إجبارية: عمود جملة/API + تحكيم إقليمي للبطاقات + تقسيم مؤسسي للتعليمية + تصنيع داخلي للهوامش القصوى فقط",
    "limits": "أسعار معلنة لا معاملاتية · جملة B2B خلف تسجيل · لا سمعة مستقلة · المتجر محل السؤال غير مرصود مباشرة (النطاقات متوقفة)",
}
os.makedirs(f"{BASE}/src/lib/data", exist_ok=True)
with open(f"{BASE}/src/lib/data/channel-matrix.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK — channel-matrix.json:", len(rows), "rows,", len(mkt), "marketplaces")
