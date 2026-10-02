#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACZ analysis — consolidate Acczone audit findings into research/acz_analysis_20261002.json."""
import json, hashlib
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/acz_analysis_20261002.json"

raw = json.load(open("/home/z/my-project/research/acz_audit_raw_20261002.json"))
prev = json.load(open("/home/z/my-project/research/g1_rescan_raw3_20261002.json"))
mast = json.load(open("/home/z/my-project/research/sv_master_catalog_consolidated_20261002.json"))

def body(recs, name):
    return [r["body"] for r in recs if r["name"] == name][0]

# --- balance ---
bal = json.loads(body(raw["fetches"], "getBalance_apikey"))
# --- services now/prev ---
svc_now = json.loads(body(raw["fetches"], "getServices"))
svc_prev = json.loads(body(prev["fetches"], "acz_getServices_plain"))
pm = {s["key"]: s for s in svc_prev}

# --- delta table ---
delta = []
for s in svc_now:
    p = pm.get(s["key"], {})
    delta.append({
        "key": s["key"], "name": s["name"],
        "price_prev": p.get("price"), "price_now": s["price"],
        "price_change_pct": round((s["price"] - p["price"]) / p["price"] * 100, 1) if p.get("price") else None,
        "stock_prev": p.get("stock"), "stock_now": s["stock"],
        "stock_delta": s["stock"] - (p.get("stock") or 0),
        "created_at": s["created_at"],
    })

window_h = 11.19  # 03:47:51 -> 15:06:50 +03
for d in delta:
    d["burn_rate_per_h"] = round(-d["stock_delta"] / window_h, 2) if d["stock_delta"] else 0.0
    d["stock_days_left_at_rate"] = round(d["stock_now"] / (-d["stock_delta"] / window_h) / 24, 1) if d["stock_delta"] else None

# --- StackVault retail matches ---
sv = mast["entities"]["stackvault_live"]["products"]
sv_match = {}
for p in sv:
    n = (p.get("name") or "").lower()
    if "apple music 5m" in n: sv_match["APPLE_MUSIC_PREPAID_V2"] = p
    elif "adobe express" in n: sv_match.setdefault("ADOBE_EXPRESS", []).append(p)
    elif "gemini pro 18" in n: sv_match["geminilive"] = p

# --- ladder (all documented sources, USD) ---
ladder = {
    "APPLE_MUSIC_5M": {
        "acczone_api": 0.10, "geminishop_panel_aivaulthub": 0.40, "aivx_aiversehub": 0.85,
        "geminishop_tg_ad": 0.85, "stackvault_retail_mr": 2.35, "cb_link_variant": 1.96,
        "spread_acczone_to_sv": "23.5x",
    },
    "ADOBE_EXPRESS_12M": {
        "acczone_api": 0.30, "aivx_aiversehub": 0.40, "geminishop_tg_ad": 1.00,
        "stackvault_retail_mr": 0.64, "stackvault_retail_ps": 0.89,
    },
    "DUOLINGO_SUPER_12M": {
        "acczone_api": 0.35, "known_wholesale_floor_28_09": 0.37, "known_slide": [0.59, 0.45, 0.37],
        "geminishop_tg_ad": 1.50,
        "note": "SV sells only Max tier (12M $21.44) - different product",
    },
    "GEMINI_18M": {
        "acczone_api_now": 0.69, "acczone_docs_era_01_09": 0.40,
        "prodseller_api": 0.40, "aivx_ladder": [0.65, 0.63, 0.60, 0.39],
        "geminishop_tg_ad": 0.40, "digitalcore": [0.80, 0.70],
        "canboso": 0.65, "stackvault_retail_ps": 0.67, "evo_era_retail": 0.85,
    },
}

# --- description template match (apple music) ---
acz_am = [s for s in svc_now if s["key"] == "APPLE_MUSIC_PREPAID_V2"][0]
sv_am = sv_match["APPLE_MUSIC_PREPAID_V2"]
tmpl = {
    "acz_terms": ["1 Month Warranty After Activation", "Apple Music 5 Month Activation Link",
                   "fresh accounts in the Indian region; use a VPN", "UPI/card required, Buyer's responsibility",
                   "Link Hold Warranty: 24H"],
    "sv_mr_terms": ["1 Month Warranty", "Apple Music 5 Month Activaton Link",
                     "fresh account of Indian Region use vpn", "Valid payment method upi / card (Buyers responsibility)",
                     "Link Hold Time is 24 hour, Warranty till activation"],
    "verdict": "SAME_TEMPLATE_FAMILY — paraphrase-level match on all 5 warranty/region/hold terms",
}

analysis = {
    "task": "ACZ — Acczone API audit with delivered key (G-13 item 1)",
    "built_at": datetime.now(TZ).isoformat(),
    "key_fingerprint": raw["key_fingerprint"],
    "A_key_status": {
        "verdict": "VALID_AND_WORKING",
        "auth_method": "GET ?apikey=<KEY> query parameter (documented)",
        "control_wrong_key": "400 {detail: Invalid API Key}",
        "control_missing": "400 {detail: Missing API Key}",
        "c13_root_cause": "Prior session used ?key= / X-API-Key / Bearer on getBalance -> 'Missing API Key' -> misdiagnosed as truncated key. Key was complete all along.",
    },
    "B_account": {
        "user_id": bal["user_id"], "username": bal["username"], "first_name": bal["first_name"],
        "created_at": bal["created_at"], "verified_at": bal["verified_at"], "balance": bal["balance"],
        "identity_chain": "8th platform key resolving to same TG account 7334478984 (A7MED/Z555Mm): ProdSeller, LahaStore/ver_pixel, AIVerseX, Gemini Shop/aivaulthub, AIXpress, canboso/PremiKey, RichAI, DigitalCore, Acczone",
        "note": "Acczone account created 2026-09-24 23:07:35 (pre-project, day of market shock era)",
    },
    "C_history": {
        "verdict": "EMPTY",
        "records": 0,
        "meaning": "Account registered but NEVER transacted on Acczone API. Dormant. Ahmed's actual sourcing runs through cb_/ProdSeller + stackvault svr_.",
    },
    "D_catalog": {
        "services_now": svc_now, "delta_vs_0347_snapshot": delta,
        "window_hours": window_h,
        "total_stock_burn": sum(-d["stock_delta"] for d in delta),
        "observed_changes": [
            "APPLE_MUSIC_PREPAID_V2 price $0.30 -> $0.10 (-66.7%) SAME-DAY cut",
            "geminilive stock -62 (bestseller, burn 5.53/h, ~1.3 days of stock left)",
            "DUOLINGO stock -50 (burn 4.47/h)",
            "docs-era service 'gemini' $0.40 (created 2026-09-01) replaced by 'geminilive' $0.69 (2026-09-30) = +72.5% rotation",
        ],
    },
    "E_platform": {
        "framework": "FastAPI activation/coupon engine",
        "endpoints": ["GET /getServices (public)", "GET /getBalance?apikey=",
                      "GET /getHistory?apikey=&page=&limit= (max 100)",
                      "GET /buyCpn?apikey=&service_key=&quantity= (PURCHASE - never called)",
                      "GET /add (undocumented - skipped, mutation risk)",
                      "POST /ipn", "POST /webhooks/ccpayment (crypto CCPayment webhook)"],
        "rate_limit": "1 request / 2 seconds",
        "dns": "api.acczone.xyz = Cloudflare (104.21.18.73 / 172.67.180.205) - origin hidden",
        "docs_openapi_unchanged_vs_morning": True,
    },
    "F_price_ladder": ladder,
    "G_stackvault_crossmatch": {
        "apple_music": {"acz_price": 0.10, "sv_id": sv_am["id"], "sv_price": sv_am["price_usd"],
                         "sv_stock": sv_am["stock"], "markup_x": round(sv_am["price_usd"] / 0.10, 1),
                         "template_match": tmpl},
        "adobe_express": [{"sv_id": p["id"], "sv_price": p["price_usd"], "sv_stock": p["stock"]}
                           for p in sv_match.get("ADOBE_EXPRESS", [])],
        "gemini_18m": {"sv_id": sv_match["geminilive"]["id"], "sv_price": sv_match["geminilive"]["price_usd"],
                        "sv_stock": sv_match["geminilive"]["stock"],
                        "note": "ACZ $0.69 > SV retail $0.67 — Acczone NOT competitive on Gemini"},
        "verdict": "ACZ catalog = 'Indian UPI-activation quad' (Adobe Express + Apple Music + Duolingo Super + Gemini Pro). "
                   "Same 4 families as Gemini Shop TG ad & AiVerseX panel. Apple Music template match links ACZ supply pool "
                   "to SV mr_/Evo_Era line. ACZ = cheapest documented source for 3 of 4 SKUs.",
    },
    "H_positioning": {
        "self_claim": "«أكبر مزود لجميع المنتجات» — self-declared, observed in Acczone cluster marketing (invite store 3,650 members + logs channel 8,316 + store bot + gemini link checker bot)",
        "api_reality": "4 SKUs only — activation-link wholesale API, focused on Indian UPI-activation family",
        "layer": "Layer 2 wholesale/API (per supply-chain map)",
        "cluster": "Mike_E_0 (operator, legal identity unknown) + api.acczone.xyz + AWZ/Acczone Store (retail) + @Acczone_Store_bot + @acczone_logs + @acczone_gemini_link_bot",
        "velocity_evidence": "116 stock units consumed in 11.3h across 4 SKUs — real transaction volume despite $0 balance on Ahmed's account",
    },
    "I_practical_intelligence": {
        "cheapest_documented": ["Apple Music 5M $0.10 (23.5x below SV retail)", "Adobe Express 12M $0.30", "Duolingo Super 12M $0.35 (undercuts $0.37 floor)"],
        "not_competitive": ["Gemini 18M $0.69 (ProdSeller $0.40 / GeminiShop $0.40 / SV retail $0.67)"],
        "for_target_store": "Acczone viable for the 3 Indian-activation SKUs; balance top-up via CCPayment crypto would be required (balance $0); no purchase performed (read-only ethics).",
    },
}

with open(OUT, "w") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=1)
print("Saved ->", OUT)
print()
print("Delta table:")
for d in delta:
    print(f"  {d['key']:26} ${d['price_prev']:.2f} -> ${d['price_now']:.2f}  stock {d['stock_prev']} -> {d['stock_now']} ({d['stock_delta']:+d})  burn/h {d['burn_rate_per_h']}")
