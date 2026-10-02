#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-MASTER-CATALOG — Consolidate ALL pulled product catalogs into one unified dataset.
Sources: 11 catalog pulls (2026-09-29 → 2026-10-02) + gateway pricing + cross-matches.
Output:  research/sv_master_catalog_consolidated_20261002.json
Read-only consolidation — no network calls.
"""
import json, os, statistics

R = "/home/z/my-project/research"
USD_RATE_VND = 25945  # documented from canboso balance (F5, 2026-10-02)

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def fnum(x):
    try:
        v = float(x)
        return v
    except (TypeError, ValueError):
        return None

def sbool(v):
    """stock value -> bool (handles str/int/None)"""
    if v is None: return False
    if isinstance(v, bool): return v
    try: return int(v) > 0
    except (TypeError, ValueError): return False

def desc_head(s, n=140):
    if not s: return ""
    s = " ".join(str(s).split())
    return (s[:n] + "…") if len(s) > n else s

out = {"task": "SV-MASTER-CATALOG — unified product catalog consolidation",
       "built_at": "2026-10-02", "currency_note": f"LahaStore prices in VND converted at {USD_RATE_VND} VND/USD (canboso usdRate, 2026-10-02)",
       "entities": {}, "gateway": {}, "cross_matches": {}, "audit": {}}

# ── 1. StackVault LIVE (282) ─────────────────────────────────────────────
live = load(f"{R}/g1_cb_live_catalog_20261002.json")["products"]
sv_live = []
for p in live:
    sv_live.append({"id": p["id"], "name": p["name"], "category": p.get("categoryName") or p.get("category"),
                    "price_usd": fnum(p["price"]), "stock": int(fnum(p["stock"]) or 0),
                    "in_stock": str(p.get("inStock")).lower() == "true",
                    "prefix": p["id"].split("_")[0] if "_" in p["id"] else "other",
                    "description_head": desc_head(p.get("description"))})
out["entities"]["stackvault_live"] = {
    "display": "StackVault — الكتالوج الحي", "platform": "stackvault.shop (decohomz.com/sv-api)",
    "pulled_at": "2026-10-02 ~03:25 +03", "n": len(sv_live), "products": sv_live,
    "verdict": "الهدف الرئيسي — مكتمل: cb_ 229 · ps_ 20 · mr_ 32 · dummy 1"}

# ── 2. StackVault ARCHIVE (357, with costPrice leak) ─────────────────────
arch = load(f"{R}/stackvault_live/sv_products_current.json")["products"]
sv_arch = []
for p in arch:
    cost = fnum(p.get("costPrice"))
    price = fnum(p["price"])
    margin = None
    if cost and cost > 0 and price is not None:
        margin = round((price - cost) / cost, 4)
    sv_arch.append({"id": p["id"], "name": p["name"], "category": p.get("categoryName") or p.get("category"),
                    "cost_usd": cost, "price_usd": price, "margin": margin,
                    "stock": int(fnum(p["stock"]) or 0),
                    "prefix": p["id"].split("_")[0] if "_" in p["id"] else "other"})
out["entities"]["stackvault_archive"] = {
    "display": "StackVault — أرشيف ما قبل الهجرة (مع costPrice)", "platform": "stackvault.shop (29-30/09)",
    "pulled_at": "2026-09-30", "n": len(sv_arch), "products": sv_arch,
    "verdict": "ذهب المفاوضات: تسريب costPrice مغلَق حاليًا — هامش الربح محسوب لكل منتج"}

# ── 3-7. Entity catalogs from rescan analysis ────────────────────────────
ec = load(f"{R}/g1_rescan_analysis_20261002.json")["entity_catalogs"]

ps_items = [{"id": it["id"], "name": it["name"], "category": "", "price_usd": fnum(it["price"]),
             "public_price": fnum(it.get("publicPrice")), "stock": None,
             "in_stock": bool(it.get("inStock")), "sold": it.get("sold"),
             "description_head": ""} for it in ec["prodseller_fresh"]["items"]]
out["entities"]["prodseller"] = {
    "display": "ProdSeller — منصة اللوحة الجملية", "platform": "prodseller.com (SookBit, OVH Strasbourg)",
    "pulled_at": "2026-09-29", "n": len(ps_items), "products": ps_items,
    "verdict": "اللوحة الأم لخط ps_/cb_ — cb_ = حساب جملة مباشر عليها (G-1 RESOLVED)"}

laha_items = [{"id": it["id"], "name": it["name"], "category": it.get("category", ""),
               "price_vnd": fnum(it["price"]), "price_usd": round(fnum(it["price"]) / USD_RATE_VND, 2) if fnum(it["price"]) else None,
               "stock": it.get("stock"), "in_stock": sbool(it.get("stock")),
               "description_head": ""} for it in ec["laha_verpixel"]["items"]]
out["entities"]["lahastore"] = {
    "display": "LahaStore — ver_pixel", "platform": "lahastore.up.railway.app/api/v1 (psk_)",
    "pulled_at": "2026-10-02 ~03:45 +03", "n": len(laha_items), "products": laha_items,
    "verdict": "مستبعد كمورد cb_ (صفر تطابق) — الأسعار بالدونج الفيتنامي محوّلة للدولار"}

aivx_items = [{"id": it["id"], "name": it["name"], "category": "", "price_usd": fnum(it["price"]),
               "stock": it.get("stock"), "in_stock": sbool(it.get("stock")), "description_head": ""}
              for it in ec["aivx_aiversehub"]["items"]]
out["entities"]["aiversex"] = {
    "display": "AIVerseX — aiversehub.store", "platform": "aiversehub.store/api/v1 (AK_)",
    "pulled_at": "2026-10-02 ~03:45 +03", "n": len(aivx_items), "products": aivx_items,
    "verdict": "مستبعد كمورد cb_ (صفر تطابق من 35 منتجًا)"}

gshop_items = [{"id": it["id"], "name": it["name"], "category": "", "price_usd": fnum(it.get("tier_price")),
                "stock": it.get("stock"), "in_stock": sbool(it.get("stock")), "description_head": ""}
               for it in ec["geminishop_aivaulthub"]["items"]]
out["entities"]["geminishop"] = {
    "display": "Gemini_Shop — واجهة aivaulthub", "platform": "reseller.aivaulthub.store/api/v1 (rsk_)",
    "pulled_at": "2026-10-02 ~03:45 +03", "n": len(gshop_items), "products": gshop_items,
    "verdict": "مستبعد (6 منتجات، صفر تطابق)"}

acz_items = [{"id": it["key"], "name": it["name"], "category": "", "price_usd": fnum(it["price"]),
              "stock": None, "in_stock": bool(it.get("is_active")), "description_head": ""}
             for it in ec["acczone_mike"]["items"]]
out["entities"]["acczone"] = {
    "display": "Acczone — Mike_E_0", "platform": "بوت تيليجرام (مفتاح مقتطع)",
    "pulled_at": "2026-10-02 ~03:45 +03", "n": len(acz_items), "products": acz_items,
    "verdict": "مستبعد (4 منتجات، صفر تطابق) — الكتالوج مصغّر"}

# ── 8. canboso/PremiKey (349) from raw body ──────────────────────────────
raw3 = load(f"{R}/g1_r3_newkeys_raw_20261002.json")
canboso_body = next(p["body"] for p in raw3["probes"] if p["name"] == "premi_products_X-API-Key")
canboso = json.loads(canboso_body)["products"]
cb_items = []
for it in canboso:
    pr = it.get("price") or {}
    av = it.get("availability") or {}
    amount = pr.get("amount") if isinstance(pr, dict) else fnum(pr)
    cb_items.append({"id": it["productId"], "name": it["name"], "category": it.get("productType") or "",
                     "price_usd": fnum(amount), "stock": av.get("available"),
                     "in_stock": sbool(av.get("available")), "sold": av.get("sold"),
                     "description_head": desc_head(it.get("description"), 100)})
out["entities"]["canboso_premikey"] = {
    "display": "PremiKey/HitMeow — canboso.com", "platform": "canboso.com/api/v2/telegram-buyer (tgb_ · X-API-Key · Binance Pay)",
    "pulled_at": "2026-10-02 ~04:15 +03", "n": len(cb_items), "products": cb_items,
    "verdict": "لوحة شقيقة من الحوض الكتالوجي المشترك (550 اسمًا) — قاعدة Mongo مستقلة؛ وسيط cb_/canboso = 0.91"}

# ── 9. DigitalCore (11) from raw body ────────────────────────────────────
dc_body = next(p["body"] for p in raw3["probes"] if p["name"] == "dc_user_products")
dc = json.loads(dc_body)
dc_items = [{"id": it["id"], "name": it["name"], "category": "", "price_usd": fnum(it["price"]),
             "price_from": fnum(it.get("priceFrom")), "stock": it.get("stock"),
             "in_stock": sbool(it.get("stock")),
             "tiers": [(t["minQty"], t.get("maxQty"), t["price"]) for t in it.get("tiers", [])],
             "description_head": ""} for it in dc]
out["entities"]["digitalcore"] = {
    "display": "DigitalCore — DCoreStoreBot", "platform": "digitalcore.top/api/user (UUID Api-Key)",
    "pulled_at": "2026-10-02 ~04:15 +03", "n": len(dc_items), "products": dc_items,
    "verdict": "مورد جملة API موثق (تدرجات كمية +12-47%) — مستبعد كهوية cb_"}

# ── 10. AIXpress (2, dormant) ────────────────────────────────────────────
fu = load(f"{R}/g1_r3_followup_20261002.json")["tests"]["F1"]
smp = fu["sample"]
aix_items = [{"id": smp["service_id"], "name": smp["name"], "category": "", "price_usd": smp["price"],
              "stock": smp["stock"], "in_stock": False, "description_head": ""},
             {"id": "service_?(aixpress-2)", "name": "gemini pro 18m (2)", "category": "", "price_usd": 0.45,
              "stock": 0, "in_stock": False, "description_head": "السعر من جولة R3 — النشر خامِل (مخزون 0)"}]
out["entities"]["aixpress"] = {
    "display": "AIXpress — aixpress.shop", "platform": "aixpress.shop/api/v1 (AK_ — نشر فعلي؛ وثائق البوت متقادمة)",
    "pulled_at": "2026-10-02 ~04:19 +03", "n": len(aix_items), "products": aix_items,
    "verdict": "خامِل: منتجان فقط، مخزون 0، رصيد $0 — نفس صندوق AIVerseX (188.166.90.19)"}

# ── 11. RichAIStore (25) from raw body ───────────────────────────────────
rich_body = next(p["body"] for p in raw3["probes"] if p["name"] == "richai_probe_telegram_api_v1_products")
rich = json.loads(rich_body)["products"]
rich_items = [{"id": it["id"], "name": it["name"], "category": it.get("product_type") or "",
               "price_usd": fnum(it.get("retail_price")), "unit_price": fnum(it.get("your_unit_price")),
               "stock": it.get("stock"), "in_stock": sbool(it.get("stock")),
               "description_head": desc_head(it.get("description"), 100)} for it in rich]
out["entities"]["richai"] = {
    "display": "RichAIStore — cgpt-active.pro", "platform": "cgpt-active.pro/telegram/api/v1 (Bearer rsk_ · Reseller API v1.0.0)",
    "pulled_at": "2026-10-02 ~04:19 +03", "n": len(rich_items), "products": rich_items,
    "verdict": "منصة CDK كاملة التوثيق (12 نقطة نهاية + تذاكر) — مستبعدة (صفر تطابق مع cb_)"}

# ── Gateway pricing (15 models) ──────────────────────────────────────────
gw = load(f"{R}/sv_master_gateway_pricing_20261002.json")
out["gateway"] = {"platform": "gpt.teamsoclo.site/api/pricing (Team Sóc Lọ 🇻🇳)",
                  "pricing_version": gw.get("pricing_version"),
                  "models": [{"model": m["model_name"], "quota_type": m.get("quota_type"),
                              "model_ratio": m.get("model_ratio"), "model_price": m.get("model_price"),
                              "completion_ratio": m.get("completion_ratio")} for m in gw["data"]]}

# ── Cross-matches: cb_ vs canboso (111 pairs) ────────────────────────────
an = load(f"{R}/g1_r3_newkeys_analysis_20261002.json")["tests"]
pairs = an["P3"]["samples"]
out["cross_matches"]["cb_vs_canboso"] = {
    "n_pairs": len(pairs),
    "pairs": [{"name": p["cb_name"], "cb_price": p["cb_price"], "canboso_price": p["premi_price"],
               "ratio": round(p["cb_price"] / p["premi_price"], 3) if p["premi_price"] else None} for p in pairs]}
final = load(f"{R}/g1_r3_final_20261002.json")
out["cross_matches"]["pool_matrix"] = final["S4_pool_matrix"]
out["cross_matches"]["ps_live_margins_note"] = "هوامش خط ps_ الحي (CapCut): +12% إلى +154%، وسيط ≈ +20-28% (من G-1-RESCAN-R2)"

# ── Audit stats ──────────────────────────────────────────────────────────
audit = {"total_product_records": 0, "per_entity": {}}
for k, e in out["entities"].items():
    prices = [p["price_usd"] for p in e["products"] if p.get("price_usd") is not None]
    audit["per_entity"][k] = {"n": e["n"],
                              "price_min": min(prices) if prices else None,
                              "price_max": max(prices) if prices else None,
                              "in_stock_n": sum(1 for p in e["products"] if p.get("in_stock"))}
    audit["total_product_records"] += e["n"]
audit["gateway_models"] = len(out["gateway"]["models"])
margins = [p["margin"] for p in sv_arch if p["margin"] is not None]
audit["archive_margin_stats"] = {"n_with_cost": len(margins),
                                 "median": round(statistics.median(margins), 3) if margins else None,
                                 "min": round(min(margins), 3) if margins else None,
                                 "max": round(max(margins), 3) if margins else None}
ratios = [p["ratio"] for p in out["cross_matches"]["cb_vs_canboso"]["pairs"] if p["ratio"]]
audit["cb_canboso_ratio"] = {"n": len(ratios), "median": round(statistics.median(ratios), 3),
                             "p25": round(statistics.quantiles(ratios, n=4)[0], 3),
                             "p75": round(statistics.quantiles(ratios, n=4)[2], 3)} if ratios else {}
out["audit"] = audit

path = f"{R}/sv_master_catalog_consolidated_20261002.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"OK → {path} ({os.path.getsize(path)//1024}KB)")
print(json.dumps(audit, ensure_ascii=False, indent=1))
