#!/usr/bin/env python3
"""Build ProdSeller package data files: CSV catalog + JSON package (download/)."""
import csv
import json
from datetime import datetime, timezone

ROOT = "/home/z/my-project"
SRC = f"{ROOT}/research/prodseller_live/products_fresh.json"
FRESH = json.load(open(f"{ROOT}/research/prodseller_live/fresh_2026-09-29.json"))
OLD = {p["name"]: p for p in json.load(open(f"{ROOT}/research/prodseller_live/products_raw.json"))["products"]}

prods = sorted(json.load(open(SRC))["products"], key=lambda p: -(p.get("finalPrice") or 0))
now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ── CSV catalog ──
csv_path = f"{ROOT}/download/كتالوج_ProdSeller_الحي_2026-09-29.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["#", "المنتج", "سعر API ($)", "السعر العام ($)", "خصم API (٪)",
                "المخزون", "الوحدات المبيعة", "تسليم فوري", "تغيير عن 27/09"])
    for i, p in enumerate(prods, 1):
        fin = p.get("finalPrice") or p.get("price")
        pub = p.get("publicPrice")
        disc = f"{(1 - fin / pub) * 100:.0f}٪" if (fin and pub and pub > fin) else "—"
        old = OLD.get(p["name"])
        if not old:
            chg = "منتج جديد"
        elif old.get("price") != p.get("price"):
            chg = f"السعر {old.get('price')}←{p.get('price')}"
        elif old.get("inStock") != p.get("inStock"):
            chg = "إعادة تخزين" if p.get("inStock") else "نفد"
        else:
            chg = "—"
        w.writerow([i, p["name"], f"{fin:.2f}" if fin is not None else "—",
                    f"{pub:.2f}" if pub is not None else "—", disc,
                    "متوفر" if p.get("inStock") else "نافد", p.get("sold", 0),
                    "نعم" if p.get("delivery", {}).get("type") == "instant" else "—", chg])

# ── JSON package ──
bal = FRESH["api"]["balance"]["response"]
pkg = {
    "package": "ProdSeller Engagement Package",
    "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "identity": {
        "name": "ProdSeller (Prodseller.com)",
        "website": "https://prodseller.com (لوحة إدارة Angular — لا واجهة بيع عامة)",
        "api_base": "https://prodseller.com/v1",
        "channel": "https://t.me/ProdSellerOfficial",
        "bot": "@prodsellerbot",
        "admin_contact": "@sookbit (og:title: Prodseller.com)",
        "payment": "Binance Pay (أعلن إصلاح مشكلة Binance API في 28/09/2026)",
        "backend_locale_hint": "رسائل خطأ فرنسية (Route introuvable)",
    },
    "account": {
        "username": bal.get("username"),
        "telegram_id": bal.get("telegramId"),
        "membership": bal.get("membership"),
        "balance_usd": bal.get("balance"),
        "api_key_env": "PRODSELLER_API_KEY (in .env, git-ignored)",
        "verified_at": FRESH["run_ts"],
    },
    "api_surface": {
        "GET /v1/balance": "200 — بيانات الحساب والعضوية والرصيد",
        "GET /v1/products": "200 — الكتالوج الكامل بأسعار API والعام",
        "GET /v1/orders": "200 — سجل الطلبات مع ترقيم صفحات (page, limit)",
        "GET /v1/topup": "404 — لا يوجد (الشحن عبر البوت)",
        "auth": "X-API-Key header",
        "rate_limit": "300 طلب / 15 دقيقة (RateLimit headers)",
        "no_public_docs": True,
    },
    "catalog_stats": {
        "total": len(prods),
        "in_stock": sum(1 for p in prods if p.get("inStock")),
        "out_of_stock": sum(1 for p in prods if not p.get("inStock")),
        "price_range": [min(p.get("finalPrice") or 0 for p in prods), max(p.get("finalPrice") or 0 for p in prods)],
        "total_units_sold": sum(p.get("sold", 0) for p in prods),
        "api_discount_range": "2٪–28٪ عن السعر العام",
    },
    "changes_vs_2026_09_27": FRESH["price_diff"],
    "products": [
        {"name": p["name"], "api_price": p.get("finalPrice") or p.get("price"),
         "public_price": p.get("publicPrice"), "in_stock": p.get("inStock"),
         "sold": p.get("sold"), "id": p.get("id")} for p in prods
    ],
    "gemini_price_timeline_published": [
        {"date": "2026-07-21", "price": 0.55, "note": "إطلاق معلن"},
        {"date": "2026-07-28", "price": 1.00, "note": "أزمة انقطاع عالمي — آخر مخزون"},
        {"date": "2026-08-01", "price": 0.46, "note": "فلاش 500 رابط"},
        {"date": "2026-08-04", "price": 0.45, "note": "خصم"},
        {"date": "2026-09-11", "price": 0.43, "note": "فلاش (API 0.40، جملة 0.39)"},
        {"date": "2026-09-19", "price": 0.49, "note": "فلاش متكرر"},
        {"date": "2026-09-25", "price": 0.69, "note": "موجة ارتفاع"},
        {"date": "2026-09-27", "price": 0.48, "note": "خصم (جملة 0.44)"},
        {"date": "2026-09-29", "price": 0.89, "note": "السعر الحي في API — موجة نقص جديدة"},
    ],
    "bargaining_anchors": {
        "flash_floors_documented": {
            "Gemini 18M": 0.41, "Office 365 bulk": 0.17, "CapCut 1M bulk": 1.20,
            "Duolingo Super bulk": 0.34, "K12+Codex API": 3.80, "K12 Edu 2y (new)": 3.40,
            "Outlook/Hotmail API": 0.015, "Adobe Express API": 0.37,
        },
        "advertised_api_discount": "حتى 35٪ عن الأسعار العامة (إعلان 20/07/2026)",
        "competitor_references": {
            "ChatGPT Plus bulk": "AISUBSID $2.90 (طلب مسبق 20+)",
            "K12 Edu 2y": "HitMeowShop $3.85",
            "Gemini 18M bulk": "AiVerseX $0.45",
        },
    },
}
json_path = f"{ROOT}/download/حزمة_ProdSeller_البيانات_2026-09-29.json"
json.dump(pkg, open(json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("CSV :", csv_path, f"({len(prods)} rows)")
print("JSON:", json_path)
