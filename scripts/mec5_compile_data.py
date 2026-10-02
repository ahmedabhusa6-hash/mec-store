#!/usr/bin/env python3
"""MEC-5.0: compile master API-gap dataset → src/lib/data/mec5.json for the new tab."""
import json, os
from datetime import datetime, timezone

BASE = "/home/z/my-project"
OUT = f"{BASE}/src/lib/data/mec5.json"

master = json.load(open(f"{BASE}/research/mec5/api_gap_master.json"))

# ---- load agent reports (defensively) ----
def load(p):
    try:
        return json.load(open(p))
    except Exception as e:
        print("WARN:", p, e)
        return {}

a = load(f"{BASE}/research/mec5/agent_A_turgame_gamsgo.json")
b = load(f"{BASE}/research/mec5/agent_B_kinguin_seagm_offgamers.json")
c = load(f"{BASE}/research/mec5/agent_C_z2u_u7buy_wholesale.json")
a_full = load(f"{BASE}/research/mec5/agentA_turgame_dual_prices_full.json")

ps = master["prodseller"]; sv = master["stackvault"]

# ---- ProdSeller: compact rows for UI ----
ps_rows = []
for r in ps["latest_per_product"]:
    ps_rows.append({
        "product": r["product"], "public": r["public_usd"],
        "api": r["api_usd"], "bulk": r["bulk_usd"],
        "gap": r["api_gap_pct"] if r["api_gap_pct"] is not None else (r["bulk_gap_pct"]),
        "date": r["date"],
    })
# also keep the full chronological series compact
ps_all = [
    {"product": r["product"], "public": r["public_usd"], "api": r["api_usd"],
     "bulk": r["bulk_usd"], "gap": r["api_gap_pct"], "date": r["date"]}
    for r in ps["all_rows"]
]

# ---- StackVault: top 15 + bottom 5 + category stats ----
sv_top = [
    {"product": r["product"][:70], "price": r["public_usd"], "cost": r["cost_usd"],
     "gap": r["gap_pct"], "x": r["markup_multiple"]}
    for r in sv["top20_gap"][:15]
]
sv_bottom = [
    {"product": r["product"][:70], "price": r["public_usd"], "cost": r["cost_usd"],
     "gap": r["gap_pct"], "x": r["markup_multiple"]}
    for r in sv["bottom10_gap"][:5]
]

# ---- Turgame rows from agent A (14 dual rows in report + 225 full) ----
turg_rows = []
try:
    for t in (a if isinstance(a, list) else [a]):
        pass
except Exception:
    pass
# agent A report structure: list of 2 targets
turgame_dual = []
gamsgo_notes = ""
if isinstance(a, list):
    for target in a:
        if isinstance(target, dict) and "turgame" in str(target.get("target", "")).lower():
            turgame_dual = target.get("dual_price_rows", [])[:14]
            gamsgo_notes = ""
elif isinstance(a, dict):
    turgame_dual = a.get("dual_price_rows", [])

# ---- Kinguin wholesale tiers (official docs example) ----
kinguin = {
    "exists": True,
    "docs": "github.com/kinguinltdhk/Kinguin-eCommerce-API (public, updated 2026-09-18)",
    "access": "Kinguin ID → APPLY FOR ACCESS → approval → X-Api-Key · sandbox self-serve at sandbox.kinguin.net/integration",
    "endpoints_live": "gateway.kinguin.net/esa/api (401 structured = live) + sandbox gateway",
    "example_tiers": [
        {"qty": "1+", "price": 5.79, "gap": 0.0},
        {"qty": "10+", "price": 5.50, "gap": 5.0},
        {"qty": "50+", "price": 5.40, "gap": 6.7},
        {"qty": "100+", "price": 5.30, "gap": 8.5},
        {"qty": "500+", "price": 5.20, "gap": 10.2},
    ],
    "note": "Counter-Strike: Source (kinguinId 1949) — official docs example. Wholesale = per-offer wholesale.enabled + tiers[]; added 2024-06-18",
}

# ---- verdicts table (the master answer) ----
verdicts = [
    {"provider": "StackVault", "api": "نعم — مكشوف سابقًا", "gap": "19.9% متوسط (13–57.4%)", "n": "274 منتجًا",
     "access": "API كان مفتوحًا (decohomz.com/sv-api) — الآن 403", "verdict": "أعلى فجوة موثقة — بنية تكلفة كاملة مكشوفة", "status": "confirmed"},
    {"provider": "ProdSeller", "api": "نعم — رسمي", "gap": "12.0% متوسط · وسيط 9.1% (2.6–41.4%)", "n": "38 صفًا مؤرخًا",
     "access": "بوت تيليجرام + USDT — لا KYC، فوري", "verdict": "أفضل بوابة مرجعية + أدلة هيكلية ثلاثية (لوحة التحكم + صورة رسمية + وثائق API)", "status": "confirmed"},
    {"provider": "Kinguin", "api": "نعم — رسمي", "gap": "5.0–10.2% (طبقات كمية)", "n": "مثال رسمي موثق",
     "access": "طلب موافقة + sandbox ذاتي", "verdict": "جملة كمية موثقة في الوثائق الرسمية — الطبقات 10+/50+/100+/500+", "status": "confirmed"},
    {"provider": "Turgame", "api": "نعم — B2B رسمي", "gap": "~0.91% أرضية الكتالوج العام (0.48–1.27%)", "n": "225 صفًا مطابقًا",
     "access": "استمارة جملة + KYC (معرف ضريبي) + اتفاقية موزع + محفظة", "verdict": "الأرضية العلنية ~1% فقط — خصومات Bronze→Platinum الحقيقية مخفية خلف البوابة", "status": "partial"},
    {"provider": "Reloadly", "api": "نعم — مجاني ذاتي", "gap": "2–10% (discountPercentage منشور لكل منتج)", "n": "عينات وثائق",
     "access": "تسجيل مجاني + توثيق علني كامل", "verdict": "الوحيد الذي ينشر نسب الخصم عن قيمة الاسمية علنًا لكل علامة", "status": "confirmed"},
    {"provider": "DingConnect", "api": "نعم — مجاني", "gap": "خلف تسجيل دخول مجاني", "n": "—",
     "access": "حساب مجاني + API", "verdict": "نفس بنية Reloadly لكن الأسعار مخفية خلف login", "status": "hidden"},
    {"provider": "Bitrefill", "api": "نعم — REST v2 علني", "gap": "صفر (تعادل تجزئة + مشاركة إيراد)", "n": "—",
     "access": "مفتوح", "verdict": "لا فجوة سعرية — يعوّضها revenue share للأدوات", "status": "none"},
    {"provider": "U7BUY", "api": "بائع فقط (Supply-side)", "gap": "لا فجوة شرائية", "n": "—",
     "access": "حساب + طلب + مراجعة يدوية", "verdict": "API لأتمتة البيع (webhooks) وليس لشراء أرخص — عمولة 10%", "status": "none"},
    {"provider": "Z2U", "api": "لا يوجد", "gap": "—", "n": "—",
     "access": "—", "verdict": "سوق C2C — البائعون يحددون الأسعار، رسوم 5–9% على البائع", "status": "none"},
    {"provider": "GamsGo", "api": "لا يوجد", "gap": "—", "n": "—",
     "access": "—", "verdict": "سوق C2C + برنامج بائعين (عمولات 4.9–9.9%) — ليس مورد API", "status": "none"},
    {"provider": "SEAGM", "api": "استفسار فقط", "gap": "غير منشور", "n": "—",
     "access": "استمارة شراكة — رأس مال $3,000–50,000 + طلب أدنى $10,000", "verdict": "B2B بكميات كبيرة جدًا — أسعار بالتسعير فقط", "status": "inquiry"},
    {"provider": "OffGamers", "api": "مورد فقط (Supply-side)", "gap": "غير منشور", "n": "—",
     "access": "طلب Reseller عبر تذكرة", "verdict": "API للموردين (تسعير + مخزون) — جهة الشراء بالاستمارة، الولاء نقاط فقط", "status": "inquiry"},
]

# ---- structural evidence (ProdSeller) ----
structural = {
    "admin_panel": "منشور #132 (09/09): لقطة من لوحة تحكم ProdSeller تُظهر حقلين: «Price (USD) $1.37» + «API Price (optional) $1.29» لمنتج CapCut Pro 1 Month FW",
    "official_image": "منشور #134 (11/09): صورة رسمية بثلاث طبقات — FLASH SELL $0.43 / API PRICE $0.40 / BULK PRICE $0.39 (Gemini 18M)",
    "api_docs": "prodseller.com/api-docs: نقطة GET /v1/products تُرجع «price» (المخصوم فعليًا من مفتاحك) + «publicPrice» (المعلن للمرجع) — بنية الفجوة مدمجة في التصميم",
    "marketing": "منشور 20/07: إعلان رسمي «خصم حتى 35% مقارنة بالأسعار العامة لمستخدمي API بوت»",
    "old_endpoint": "البوابة القديمة http://51.77.244.194 تحوّلت 301 إلى prodseller.com (12/08) — لا نسخة قديمة مكشوفة",
    "wayback": "أرشيف الويب لا يحتفظ بلقطات لصفحات الأسعار (التحقق تعذّر — قيد الاسترجاع)",
}

data = {
    "run": "MEC-5.0 — كشف فجوات أسعار API",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "mission": "تحويل أسعار الجملة عبر الواجهات البرمجية من مجهول إلى معلوم موثق: من يقدم سعرًا مختلفًا في API؟ وبكم؟",
    "headline_stats": {
        "providers_scanned": 12,
        "with_confirmed_dual_pricing": 4,
        "prodseller_rows": len(ps_all),
        "stackvault_products": sv["summary"]["n_with_dual_price"],
        "prodseller_gap": ps["summary"]["api_gap_pct"],
        "stackvault_gap": sv["summary"]["gap_pct"],
    },
    "prodseller": {
        "summary": ps["summary"],
        "structural_evidence": structural,
        "latest_per_product": ps_rows,
        "all_rows": ps_all,
    },
    "stackvault": {
        "summary": sv["summary"],
        "top_gap": sv_top,
        "bottom_gap": sv_bottom,
    },
    "kinguin": kinguin,
    "turgame": {
        "exists": True,
        "portal": "wholesale.turgame.com",
        "catalog_floor_gap": {"avg": 0.91, "median": 0.94, "range": "0.48–1.27%", "n_matched": 225},
        "tiers": "Bronze (₺0) / Silver (₺5K) / Gold (₺20K) / Platinum (₺50K) — خصومات فعلية سرية داخل البوابة",
        "kyc": "استمارة + معرف وطني/ضريبي + اتفاقية موزع v1.0.0 + محفظة Turgame للتسوية",
        "sample_rows": [
            {"product": "Google Play TR 500", "retail": "—", "wholesale": "491.64 TRY = 98.3% من القيمة الاسمية", "gap": 1.7},
            {"product": "Steam KSA 20 SAR", "retail": "254.10 TRY", "wholesale": "251.60 TRY", "gap": 0.98},
            {"product": "PS US $100", "retail": "4626.20 TRY", "wholesale": "4581.30 TRY", "gap": 0.97},
        ],
        "supply_note": "رموز Turgame تتدفق من شبكة توزيع EZPIN (retailer_item_id: EZPIN-1065)",
    },
    "reloadly": {
        "exists": True,
        "model": "خصم منشور لكل منتج (discountPercentage) + نقطة GET /discounts مخصصة",
        "doc_samples": [
            {"brand": "1-800-PetSupplies", "discount": 7.5},
            {"brand": "Apple Music 12m Canada", "discount": 2.0},
            {"brand": "Afghan Wireless (شحن)", "discount": 10.0},
        ],
        "access": "تسجيل مجاني ذاتي الخدمة + توثيق علني",
    },
    "verdicts": verdicts,
    "leaderboard": [
        {"provider": "StackVault", "gap": "19.9%", "color": "rose"},
        {"provider": "ProdSeller", "gap": "12.0%", "color": "amber"},
        {"provider": "Kinguin", "gap": "5–10.2%", "color": "emerald"},
        {"provider": "Reloadly", "gap": "2–10%", "color": "cyan"},
        {"provider": "Turgame", "gap": "~1% (أرضية علنية)", "color": "zinc"},
    ],
    "next_moves": [
        "فتح حساب ProdSeller (بوت + USDT) ← GET /v1/products يكشف الفجوة الفعلية لكل منتج لحظيًا",
        "تسجيل Kinguin sandbox ← سحب كامل الكتالوج مع offers[].wholesale.tiers",
        "حساب Reloadly مجاني ← GET /discounts لكل العلامات",
        "استمارة Turgame الجملة ← كشف خصومات Bronze→Platinum الحقيقية",
    ],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
print("saved", OUT, os.path.getsize(OUT), "bytes")
print("verdicts:", len(verdicts), "| ps rows:", len(ps_all), "| latest:", len(ps_rows))
