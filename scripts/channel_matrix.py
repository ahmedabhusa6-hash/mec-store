#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.4 | Channel Evaluation Matrix — 32+ channels vs Dolaa-model retail store
Part 1: compile matrix from all evidence sources (quota-free).
Sources:
  - data/research/mec2_channels_raw.json   (31 §19 entities + s_previews)
  - research/b3_channel_history.json       (5 channels, 297 messages, price traces)
  - research/b3_stackvault_api.json        (275 products, costPrice exposed)
  - research/b3_turgame_categories.json    (117 products, 12 categories)
  - download/channel_evaluation.json       (10 clusters: roles, risk grades)
  - download/offers_intelligence.json      (230 offers across channels)
Output: download/channel_matrix.json
"""
import json, os, re, statistics

BASE = "/home/z/my-project"
def L(p): return json.load(open(os.path.join(BASE, p), encoding="utf-8"))

raw = L("data/research/mec2_channels_raw.json")
hist = L("research/b3_channel_history.json")
sv = L("research/b3_stackvault_api.json")
tg = L("research/b3_turgame_categories.json")
ce = L("download/channel_evaluation.json")
oi = L("download/offers_intelligence.json")

ent = raw["entities"]
previews = raw.get("s_previews", {})

# cluster lookup by cluster name
cluster_by_name = {c["name"]: c for c in ce["clusters"]}

# raw cluster id -> eval cluster name mapping
CLUSTER_MAP = {
    "Gemini12Pro": "Gemini GPT / Gemini12Pro",
    "VerifierGroup": "Verifier Group (طبقة الثقة)",
    "ProdSeller": "ProdSeller",
    "Acczone": "Acczone",
    "StackVault": "StackVault",
    "HitMeow": "HitMeow / PremiKey",
    "PremiKey": "HitMeow / PremiKey",
    "AISUBSID": "AISUBS.ID",
    "EvoEra": "Evo Era",
    "learnwith_Alex": "learnwith_Alex / Bite Store",
    "BiteStore": "learnwith_Alex / Bite Store",
    # micro-stores cluster (all single-entity clusters below)
    "AWZ-private": "متاجر صغيرة (بوتات فردية)",
    "Mike_E": "متاجر صغيرة (بوتات فردية)",
    "insightXpro": "متاجر صغيرة (بوتات فردية)",
    "NevaKeyStore": "متاجر صغيرة (بوتات فردية)",
    "Gamisell": "متاجر صغيرة (بوتات فردية)",
    "p_a_store": "متاجر صغيرة (بوتات فردية)",
    "storeBatman": "متاجر صغيرة (بوتات فردية)",
}

# entity id -> cluster name from raw entities
def cluster_of(eid):
    e = ent.get(eid, {})
    return e.get("cluster", "?")

# ---------- price extraction from channel histories ----------
PRICE_RE = re.compile(r"\$\s?([0-9]+(?:\.[0-9]{1,3})?)")
def extract_channel_prices(name):
    """Return list of (product_hint, price, text_excerpt) from a channel history."""
    h = hist.get(name)
    if not h: return []
    out = []
    for m in h.get("messages", []):
        t = m.get("text", "")
        prices = PRICE_RE.findall(t)
        if not prices: continue
        lo = min(float(p) for p in prices)
        # product hint: first 60 chars cleaned
        hint = re.sub(r"[^\w\s\u0600-\u06FF+]", " ", t)[:70].strip()
        hint = re.sub(r"\s+", " ", hint)
        out.append({"hint": hint, "min_usd": lo, "n_prices": len(prices)})
    return out

# ---------- StackVault API stats ----------
sv_products = [p for p in sv["products"] if p.get("id") != "dummy-free-test" and p.get("costPrice")]
sv_margins = [(p["price"] - p["costPrice"]) / p["costPrice"] * 100 for p in sv_products if p.get("costPrice") and p["price"]]
sv_stats = {
    "n_products": len(sv_products),
    "median_markup_pct": round(statistics.median(sv_margins), 1) if sv_margins else None,
    "min_markup_pct": round(min(sv_margins), 1) if sv_margins else None,
    "max_markup_pct": round(max(sv_margins), 1) if sv_margins else None,
    "n_with_cost": len(sv_margins),
}

# ---------- Turgame stats ----------
tg_all = []
for cname, c in tg.get("categories", {}).items():
    if not isinstance(c, dict): continue
    for p in c.get("products", []):
        p["_cat"] = cname
        tg_all.append(p)
tg_stats = {"n_products": len(tg_all), "n_categories": len(tg.get("categories", {}))}

# entity id -> cluster name from raw entities (via CLUSTER_MAP)
def cluster_name_of(e):
    return CLUSTER_MAP.get(e.get("cluster", ""), e.get("cluster", "?"))

# ---------- Layer A: §19 registry matrix ----------
layerA = []
for eid, e in ent.items():
    cname = cluster_name_of(e)
    cl = cluster_by_name.get(cname, {})
    hp = extract_channel_prices(eid)
    min_anchor = min((x["min_usd"] for x in hp), default=None)
    layerA.append({
        "id": eid,
        "type": e.get("type", "channel"),
        "cluster": cname,
        "cluster_raw": e.get("cluster", "?"),
        "url": e.get("url", ""),
        "http": e.get("http"),
        "subscribers": e.get("extra", ""),
        "title": e.get("og_title", e.get("title", "")),
        "role_in_chain": cl.get("role_in_chain", "غير محدد"),
        "risk_grade": cl.get("risk_grade", "غير مقيّم"),
        "language": cl.get("language", "?"),
        "n_history_messages": hist.get(eid, {}).get("n_total", 0),
        "n_priced_messages": hist.get(eid, {}).get("n_priced", 0),
        "n_preview_messages": len(previews.get(eid, {}).get("messages", [])),
        "min_price_anchor_usd": min_anchor,
        "price_samples": hp[:6],
        "layer": None,  # assigned below
        "dolaa_fit": None,  # assigned below
    })

# layer assignment by cluster role
def assign_layer(row):
    c = row["cluster"]
    if c == "ProdSeller": return "جملة/API (Wholesale)"
    if c == "Acczone": return "جملة معلنة (Wholesale-claimed)"
    if c == "Gemini GPT / Gemini12Pro": return "مصنع + تجزئة (Manufacturing+Retail)"
    if c == "AISUBS.ID": return "مصنع حسابات (Manufacturing)"
    if c == "StackVault": return "تجزئة منظمة (Organized Retail)"
    if c == "HitMeow / PremiKey": return "تجزئة + معرفة طرق (Retail+Methods)"
    if c == "Evo Era": return "تجزئة آلية (Automated Retail)"
    if c == "Verifier Group (طبقة الثقة)": return "طبقة ثقة/ضمان (Escrow/Trust)"
    if c == "learnwith_Alex / Bite Store": return "بائع طرق (Methods Seller)"
    if c == "متاجر صغيرة (بوتات فردية)": return "تجزئة فردية (Micro Retail)"
    return "غير مصنف"

# entity id -> cluster name from raw entities (via CLUSTER_MAP)
def cluster_name_of(e):
    return CLUSTER_MAP.get(e.get("cluster", ""), e.get("cluster", "?"))

def assign_dolaa_fit(row):
    """What a Dolaa-model Gulf retail store would use this channel for."""
    layer = row["layer"]
    risk = row["risk_grade"]
    risky = any(k in risk for k in ["حرج", "عالٍ"])
    fit = {
        "جملة/API (Wholesale)": "قناة توريد أساسية مرشحة — أسعار API أرخص حتى 35% من معلنة",
        "جملة معلنة (Wholesale-claimed)": "مصدر توريد ثانوي — الادعاء غير قابل للتحقق الخارجي",
        "مصنع + تجزئة (Manufacturing+Retail)": "مصدر توريد منخفض الكلفة لعائلة AI — مخاطر ToS عالية",
        "مصنع حسابات (Manufacturing)": "الطبقة الأدنى كلفة (نجاح 1-2% لطريقة UPI) — أعلى هشاشة",
        "تجزئة منظمة (Organized Retail)": "منافس مباشر نموذجي لدولا لا مصدر توريد — معادلة التسعير cost×1.2 مرصودة",
        "تجزئة + معرفة طرق (Retail+Methods)": "منافس + مصدر معرفة طرق التصنيع — لا يُنصح كمصدر (خطر احتيال داخلي موثق)",
        "تجزئة آلية (Automated Retail)": "منافس微观 — مؤشر أسعار سوقي حي",
        "طبقة ثقة/ضمان (Escrow/Trust)": "بنية تحتية للثقة — تُستخدم كوسيط دفع لا كمصدر",
        "بائع طرق (Methods Seller)": "غير مناسب — محتوى احتيالي موثق",
        "تجزئة فردية (Micro Retail)": "منافسون صغار — مؤشر أسعار فقط",
    }.get(layer, "غير محدد")
    if risky and "توريد" in fit and "ثانوي" not in fit and "مرشحة" in fit:
        fit += " — بحذر: درجة الخطر عالية"
    return fit

for row in layerA:
    row["layer"] = assign_layer(row)
    row["dolaa_fit"] = assign_dolaa_fit(row)

# ---------- discovered sub-entities (post-registry) ----------
sv_api = {
    "id": "stackvault_backend_api",
    "type": "api-backend",
    "cluster": "StackVault",
    "url": "decohomz.com/sv-api/products (خلف stackvault.shop)",
    "http": 200,
    "subscribers": "-",
    "title": "StackVault Backend API",
    "role_in_chain": "طبقة التكلفة الداخلية للمتجر — costPrice مكشوف لكل منتج",
    "risk_grade": "متوسط (كشف تكلفة داخلي = ثغرة موثقة؛ المتجر نفسه غير موثق خارجيًا)",
    "language": "الإنجليزية",
    "n_history_messages": 0,
    "n_priced_messages": 0,
    "n_preview_messages": 0,
    "min_price_anchor_usd": min((p["costPrice"] for p in sv_products), default=None),
    "price_samples": [],
    "layer": "طبقة تكلفة داخلية (Internal Cost)",
    "dolaa_fit": "أقوى دليل مشروع على بنية تكلفة متجر تجزئة: معادلة التسعير retail=cost×1.2 موثقة عبر 274 منتجًا",
    "stats": sv_stats,
}
aiversex = {
    "id": "AiVerseXBot",
    "type": "bot (مكتشف داخل معاينة قناة)",
    "channel_hint": "gemini12pro_channel — رابط طلب مدفوع",
    "cluster": "Gemini GPT / Gemini12Pro",
    "url": "t.me/AiVerseXBot",
    "role_in_chain": "بوت طلبات تجزئة داخل منظومة gemini12pro (Gemini 18 شهرًا $0.45)",
    "risk_grade": "متوسط-عالٍ (ضمن منظومة عروض Pixel)",
    "layer": "تجزئة متخصصة (Specialized Retail)",
    "dolaa_fit": "قناة طلب لعروض Gemini منخفضة الكلفة — نفس مخاطر ToS للمنظومة الأم",
    "evidence": "مرصود في معاينة s/ 27/09",
}
gtv = {
    "id": "Gt_Verified",
    "type": "bot (مكتشف داخل معاينة قناة)",
    "channel_hint": "gemini12pro_channel — رابط جملة",
    "cluster": "Gemini GPT / Gemini12Pro",
    "url": "t.me/Gt_Verified",
    "role_in_chain": "بوت جملة داخل منظومة gemini12pro (Gemini 18m أسعار جملة)",
    "risk_grade": "متوسط-عالٍ",
    "layer": "جملة متخصصة (Specialized Wholesale)",
    "dolaa_fit": "طبقة جملة داخل منظومة واحدة — أدنى من ProdSeller في التنوع",
    "evidence": "مرصود في معاينة s/ 27/09",
}

# ---------- Layer B: marketplace/B2B channels from offers ----------
# count offers per channel across all data structures
ch_offers = {}
def bump(ch):
    if not ch or ch == "?" or ch is None: return
    ch_offers[str(ch)] = ch_offers.get(str(ch), 0) + 1

for sku_id, s in oi.get("price_intelligence", {}).items():
    if not isinstance(s, dict): continue
    for key in ["cheapest_directly_observed", "cheapest_advertised_or_official"]:
        o = s.get(key)
        if isinstance(o, dict): bump(o.get("seller"))
# mec2 offers
for o in oi.get("mec2_run", {}).get("offers", []):
    bump(o.get("seller"))
# batch2 advertised index
cai = oi.get("batch2_run", {}).get("cheapest_advertised_index", {})
if isinstance(cai, dict):
    for sku_id, s in cai.items():
        if not isinstance(s, dict): continue
        o = s.get("cheapest_advertised_batch2")
        if isinstance(o, dict): bump(o.get("seller"))

marketplace_channels = []
for ch, n in sorted(ch_offers.items(), key=lambda x: -x[1]):
    if any(k in str(ch).lower() for k in ["t.me", "telegram", "stackvault", "prodseller", "gemini", "hitmeow", "evo era", "aisubs", "acczone"]):
        continue  # already in Layer A
    marketplace_channels.append({"channel": ch, "n_offers": n, "layer": "سوق/متجر مفتوح (Marketplace)"})

# ---------- summary stats ----------
summary = {
    "layerA_registry_entities": len(layerA),
    "layerA_discovered": [sv_api["id"], aiversex["id"], gtv["id"]],
    "total_rows": len(layerA) + 3,
    "sv_stats": sv_stats,
    "tg_stats": tg_stats,
    "marketplace_channels_with_offers": len(marketplace_channels),
    "generated": "2026-09-27",
    "evidence_class": "مرصود مباشرة (HTTP 200 + معاينات s/ + API مكشوف) — الأسعار معلنة لا معاملاتية",
}

out = {
    "generated": "2026-09-27",
    "run": "MEC-2.4 channel matrix (quota-free compilation)",
    "matrix_layerA": layerA,
    "discovered_entities": [sv_api, aiversex, gtv],
    "matrix_layerB_marketplaces": marketplace_channels,
    "stackvault_cost_layer": {
        "formula": "retail = cost × 1.2 (وسيط)",
        "n": sv_stats["n_with_cost"],
        "median_markup_pct": sv_stats["median_markup_pct"],
        "range": [sv_stats["min_markup_pct"], sv_stats["max_markup_pct"]],
    },
    "summary": summary,
    "limitations": [
        "دولا (المتجر محل السؤال) غير قابل للرصد المباشر: النطاقات المرشحة متوقفة/موقوفة (dolaa.com parked) — التحليل يُبنى على نموذج المتجر الخليجي العام بالأدلة المرصودة",
        "كل الأسعار معلنة (إعلاني ≠ معاملاتي)",
        "بوابات الجملة خلف تسجيل دخول (Turgame Wholesale/Reloadly) — أسعار الجملة الحقيقية تتطلب فتح حساب B2B",
        "سمعة الكيانات غير قابلة للتحقق خارجيًا (لا بصمة مستقلة لأي عنقود)",
    ],
}

with open(os.path.join(BASE, "download", "channel_matrix.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("OK — matrix written")
print("Layer A rows:", len(layerA), "| discovered:", 3, "| marketplace channels:", len(marketplace_channels))
print("StackVault:", sv_stats)
print("Turgame:", tg_stats)
print("\nTop marketplace channels by offers:")
for m in marketplace_channels[:15]:
    print(f"  {m['channel']}: {m['n_offers']}")
print("\nChannel layers distribution:")
from collections import Counter
for k, v in Counter(r["layer"] for r in layerA).items():
    print(f"  {k}: {v}")
