#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1 RESCAN R2 — ANALYSIS (all local, no network).
Inputs : research/g1_rescan_raw_20261002.json (raw1), g1_rescan_raw3_20261002.json (raw3),
         research/stackvault_live/sv_products_current.json (old 357 archive),
         research/g1_cb_live_catalog_20261002.json (03:17 catalog)
Output : research/g1_rescan_analysis_20261002.json + console report
Tests  :
  R1  live recount (357 claim vs reality) + delta vs 03:17
  R2  357 reconciliation: old ps_/mr_ archive vs live cb_/ps_/mr_ (migrated/kept/dropped/new)
  R3  ObjectId cross-match: cb_ hex vs ProdSeller-fresh raw ObjectIds
  R4  name cross-match: cb_ vs each entity (ProdSeller, laha, AIVerseX, GeminiShop, acczone)
  R5  price comparison for matched families
  R6  description/boilerplate template overlap
  R7  gemini12pro channel forensics (resumption after 29d silence?)
  R8  verdict synthesis per entity: IDENTIFIED / PARTIAL / EXCLUDED
"""
import json, re, unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_rescan_analysis_20261002.json"

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B00-\U00002BFF"
    "\U0000FE0F\U0000200D\U00002700-\U000027bf\U0001f900-\U0001f9FF\U00002190-\U000021FF"
    "\U000025A0-\U000025FF\U0000200B\U0000FE0E\U00002764\U00002705\U0000274C\U00002757]+")

def norm_title(t):
    t = EMOJI_RE.sub(" ", t or "")
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"\d+", "#", t)
    t = re.sub(r"[^a-z#\*\(\)\&\+\-\.,:/% ']", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def name_key(t):
    t = EMOJI_RE.sub(" ", t or "")
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"[^a-z ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def desc_head(d, lines=3):
    d = d or ""
    parts = [l for l in d.split("\n") if l.strip()][:lines]
    out = []
    for l in parts:
        l = EMOJI_RE.sub(" ", l)
        l = re.sub(r"\d+", "#", l)
        l = re.sub(r"https?://\S+", "URL", l)
        out.append(re.sub(r"\s+", " ", l).strip().lower())
    return " | ".join(out)

def jload(p):
    return json.load(open(p))

raw1 = jload("/home/z/my-project/research/g1_rescan_raw_20261002.json")
raw3 = jload("/home/z/my-project/research/g1_rescan_raw3_20261002.json")
def body(name, src=raw1):
    return next((f["body"] for f in src["fetches"] if f["name"] == name), None)

R = {"execution_timestamp": datetime.now(TZ).isoformat(), "tests": {}}

# ---------------- catalogs ----------------
sv = json.loads(body("sv_public"))["products"]
def pref(it):
    pid = str(it.get("id") or "")
    return pid.split("_")[0] if "_" in pid else "other"
sv_cb   = [it for it in sv if pref(it) == "cb"]
sv_ps   = [it for it in sv if pref(it) == "ps"]
sv_mr   = [it for it in sv if pref(it) == "mr"]
sv_oth  = [it for it in sv if pref(it) == "other"]
print(f"[R1] LIVE NOW: total={len(sv)} cb={len(sv_cb)} ps={len(sv_ps)} mr={len(sv_mr)} other={len(sv_oth)}")
R["tests"]["R1_live_recount"] = {"total": len(sv), "cb": len(sv_cb), "ps": len(sv_ps),
                                 "mr": len(sv_mr), "other": len(sv_oth),
                                 "user_claim_cb_357": "REFUTED — live cb_ = 229; 357 = pre-migration archive total",
                                 "pagination_probe": "identical payload with ?limit=2000&offset=0 (207744 bytes = byte-identical)",
                                 "bearer_probe": "svr_ Bearer returns same public payload"}

# delta vs 03:17
prev = jload("/home/z/my-project/research/g1_cb_live_catalog_20261002.json")["products"]
prev_ids = {str(it.get("id")) for it in prev}
cur_ids = {str(it.get("id")) for it in sv}
gone = prev_ids - cur_ids
new = cur_ids - prev_ids
print(f"[R1] delta vs 03:17: gone={len(gone)} new={len(new)}")
for g in gone: print("   GONE:", g[:40], "|", next((it.get('name') for it in prev if str(it.get('id'))==g), '?')[:70])
for n in new: print("   NEW :", n[:40], "|", next((it.get('name') for it in sv if str(it.get('id'))==n), '?')[:70])
R["tests"]["R1_delta_vs_0317"] = {"gone": sorted(gone), "new": sorted(new)}

# ---------------- R2: 357 reconciliation ----------------
arch = jload("/home/z/my-project/research/stackvault_live/sv_products_current.json")
arch_items = arch if isinstance(arch, list) else (arch.get("products") or arch.get("data") or [])
arch_ps = [it for it in arch_items if pref(it) == "ps"]
arch_mr = [it for it in arch_items if pref(it) == "mr"]
print(f"\n[R2] OLD ARCHIVE (29-30/09): total={len(arch_items)} ps={len(arch_ps)} mr={len(arch_mr)}")
arch_ps_names = {name_key(it.get("name")): it for it in arch_ps}
cb_names = {name_key(it.get("name")): it for it in sv_cb}
live_ps_names = {name_key(it.get("name")) for it in sv_ps}
live_mr_names = {name_key(it.get("name")) for it in sv_mr}
migrated = set(arch_ps_names) & set(cb_names)
kept_ps = set(arch_ps_names) & live_ps_names
kept_mr_ids = {str(it.get('id')) for it in arch_mr} & {str(it.get('id')) for it in sv_mr}
dropped_ps = [k for k in arch_ps_names if k not in cb_names and k not in live_ps_names]
# mr_ dropped by id
mr_gone_ids = {str(it.get('id')) for it in arch_mr} - {str(it.get('id')) for it in sv_mr}
new_in_cb = [k for k in cb_names if k not in arch_ps_names]
print(f"   migrated ps_->cb_: {len(migrated)} | kept as ps_: {len(kept_ps)} | dropped ps_: {len(dropped_ps)}")
print(f"   mr_ kept: {len(kept_mr_ids)}/{len(arch_mr)} | mr_ gone: {len(mr_gone_ids)}")
print(f"   cb_ products NEW vs archive: {len(new_in_cb)}")
R["tests"]["R2_reconciliation_357"] = {
    "archive_total": len(arch_items), "archive_ps": len(arch_ps), "archive_mr": len(arch_mr),
    "migrated_ps_to_cb": len(migrated), "kept_as_ps": len(kept_ps), "dropped_ps": len(dropped_ps),
    "mr_kept": len(kept_mr_ids), "mr_gone": len(mr_gone_ids), "mr_gone_ids": sorted(mr_gone_ids),
    "cb_new_vs_archive": len(new_in_cb),
    "dropped_ps_sample": dropped_ps[:25], "cb_new_sample": new_in_cb[:35],
    "accounting": f"{len(migrated)} migrated + {len(kept_ps)} kept-ps + {len(dropped_ps)} dropped = {len(arch_ps)} old-ps ; live cb_ = {len(migrated)} migrated + {len(new_in_cb)} new = {len(sv_cb)}"}

# ---------------- entity catalogs ----------------
ps_fresh = json.loads(body("ps_products"))["products"]
laha = json.loads(body("laha_products_xak"))["products"]
aivx = json.loads(body("aivx_products"))["services"]
gshop = json.loads(body("gshop_products"))["products"]
acz = json.loads(body("acz_getServices_plain", raw3))
print(f"\n[CATALOGS] ProdSeller={len(ps_fresh)} laha={len(laha)} AIVerseX={len(aivx)} GeminiShop={len(gshop)} acczone={len(acz)}")
R["entity_catalogs"] = {
    "prodseller_fresh": {"n": len(ps_fresh), "id_format": "raw Mongo ObjectId (24hex)",
                          "items": [{"id": it.get("id"), "name": it.get("name"), "price": it.get("price"),
                                     "publicPrice": it.get("publicPrice"), "inStock": it.get("inStock"),
                                     "sold": it.get("sold")} for it in ps_fresh]},
    "laha_verpixel": {"n": len(laha), "id_format": "numeric",
                       "items": [{"id": it.get("id"), "name": it.get("name"), "category": it.get("category"),
                                  "price": it.get("price"), "stock": it.get("stock")} for it in laha]},
    "aivx_aiversehub": {"n": len(aivx), "id_format": "service_XXXX",
                         "items": [{"id": it.get("service_id"), "name": it.get("name"),
                                    "price": it.get("price"), "stock": it.get("stock")} for it in aivx]},
    "geminishop_aivaulthub": {"n": len(gshop), "id_format": "service_XXXX",
                               "items": [{"id": it.get("service_id"), "name": it.get("name"),
                                          "stock": it.get("stock"),
                                          "tier_price": (it.get("pricing_tiers") or [{}])[0].get("price")} for it in gshop]},
    "acczone_mike": {"n": len(acz), "id_format": "UPPER_SNAKE key",
                      "items": [{"key": it.get("key"), "name": it.get("name"), "price": it.get("price"),
                                 "is_active": it.get("is_active"), "created_at": it.get("created_at")} for it in acz]},
}

# ---------------- R3: ObjectId cross-match ----------------
cb_hex = {str(it["id"])[3:]: it for it in sv_cb if re.fullmatch(r"cb_[0-9a-f]{24}", str(it.get("id")))}
ps_fresh_ids = {str(it.get("id")): it for it in ps_fresh}
obj_overlap = set(cb_hex) & set(ps_fresh_ids)
print(f"\n[R3] ObjectId cross-match cb_({len(cb_hex)}) vs ProdSeller-fresh({len(ps_fresh_ids)}): overlap={len(obj_overlap)}")
for o in obj_overlap:
    print(f"   MATCH cb_{o[:12]}.. = ps '{ps_fresh_ids[o].get('name')[:50]}' vs cb '{cb_hex[o].get('name')[:50]}'")
R["tests"]["R3_objectid_match"] = {"n_cb_hex": len(cb_hex), "n_ps_fresh": len(ps_fresh_ids),
                                    "overlap": len(obj_overlap),
                                    "matches": [{"hex": o, "ps_name": ps_fresh_ids[o].get("name"),
                                                 "cb_name": cb_hex[o].get("name"),
                                                 "ps_price": ps_fresh_ids[o].get("price"),
                                                 "cb_price": cb_hex[o].get("price")} for o in obj_overlap]}

# ---------------- R4/R5/R6: name + price + template matching ----------------
def match_entity(entity_name, items, name_fn, price_fn, desc_fn=None):
    ent = {}
    for it in items:
        k = name_key(name_fn(it))
        if k: ent[k] = it
    inter = set(ent) & set(cb_names)
    res = {"entity": entity_name, "n_entity": len(ent), "n_cb": len(cb_names),
           "name_matches": len(inter), "matches": []}
    for k in sorted(inter):
        cb_it = cb_names[k]; en_it = ent[k]
        res["matches"].append({
            "name": cb_it.get("name"), "cb_price": cb_it.get("price"),
            "entity_price": price_fn(en_it),
            "cb_id": str(cb_it.get("id"))[:30], "entity_id": str(en_it.get("id"))[:30]})
    print(f"\n[R4] {entity_name}: name matches vs cb_ = {len(inter)}/{len(ent)}")
    for m in res["matches"][:12]:
        print(f"   ~ {m['name'][:52]:52} cb=${m['cb_price']} ent=${m['entity_price']}")
    return res

r_ps   = match_entity("ProdSeller(fresh)", ps_fresh, lambda x: x.get("name"), lambda x: x.get("price"))
r_laha = match_entity("laha/ver_pixel", laha, lambda x: x.get("name"), lambda x: x.get("price"))
r_aivx = match_entity("AIVerseX", aivx, lambda x: x.get("name"), lambda x: x.get("price"))
r_gsh  = match_entity("GeminiShop", gshop, lambda x: x.get("name"),
                       lambda x: ((x.get("pricing_tiers") or [{}])[0].get("price")))
r_acz  = match_entity("acczone/Mike", acz, lambda x: x.get("name"), lambda x: x.get("price"))
R["tests"]["R4_name_matching"] = {"prodseller": r_ps, "laha": r_laha, "aivx": r_aivx,
                                   "geminishop": r_gsh, "acczone": r_acz}

# family-level overlap (soft signal even without exact name match)
def family(name):
    n = (name or "").lower()
    for k in ["chatgpt","gemini","claude","perplexity","duolingo","capcut","canva","office","adobe",
              "spotify","youtube","netflix","kling","gmail","apple","discord","telegram","copilot",
              "cursor","netflix","express","canva"]:
        if k in n: return k
    return "other"
cb_fam = Counter(family(it.get("name")) for it in sv_cb)
famtab = {}
for label, items in [("ProdSeller", ps_fresh), ("laha", laha), ("AIVerseX", aivx),
                      ("GeminiShop", gshop), ("acczone", acz)]:
    famtab[label] = dict(Counter(family((it.get("name") or it.get("key") or "")) for it in items))
R["tests"]["R5_family_overlap"] = {"cb_families": dict(cb_fam.most_common()), "entities": famtab}
print("\n[R5] cb_ families:", cb_fam.most_common(8))
for lab, f in famtab.items():
    shared = {k: (v, cb_fam.get(k, 0)) for k, v in f.items() if k != "other" and cb_fam.get(k, 0) > 0}
    print(f"   {lab:12} shared-with-cb: {shared}")

# description boilerplate: laha/ps have descriptions?
r_ps_tpl = Counter(desc_head(it.get("description") or "") for it in ps_fresh if it.get("description"))
r_laha_tpl = Counter(desc_head(str(it.get("description") or it.get("title") or "")) for it in laha)
cb_tpl = Counter(desc_head(it.get("description")) for it in sv_cb if it.get("description"))
tpl_shared_ps = set(r_ps_tpl) & set(cb_tpl)
tpl_shared_laha = set(r_laha_tpl) & set(cb_tpl)
print(f"\n[R6] shared desc templates: with-ProdSeller={len(tpl_shared_ps)} with-laha={len(tpl_shared_laha)}")
R["tests"]["R6_desc_templates"] = {"shared_with_prodseller": len(tpl_shared_ps),
                                    "shared_with_laha": len(tpl_shared_laha),
                                    "ps_top_templates": r_ps_tpl.most_common(8),
                                    "laha_top_templates": r_laha_tpl.most_common(8)}

# ---------------- R7: gemini12pro channel forensics ----------------
g12 = body("g12_channel") or ""
posts = re.findall(r'<time[^>]*datetime="([\d\-T:+]+)"[^>]*>', g12)
texts = re.findall(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', g12, re.S)
def strip_html(h):
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    return h.strip()
clean = [strip_html(t) for t in texts]
print(f"\n[R7] gemini12pro channel: {len(posts)} timestamps on page; last={posts[-1] if posts else None}")
for dt, tx in zip(posts[-len(clean):] if len(posts) >= len(clean) else posts, clean[-6:]):
    print(f"   {dt[:16]} :: {tx[:150]!r}")
g12_events = []
try:
    dts = [datetime.fromisoformat(p) for p in posts]
    dts.sort()
    gaps = [(dts[i+1]-dts[i]).total_seconds()/86400 for i in range(len(dts)-1)]
    max_gap = max(gaps) if gaps else 0
    print(f"   posts on page={len(dts)} max_gap_days={max_gap:.1f}")
    g12_events = {"posts_on_page": len(dts), "first": dts[0].isoformat()[:16], "last": dts[-1].isoformat()[:16],
                  "max_gap_days": round(max_gap, 1)}
except Exception as e:
    print("   date parse err:", e)
R["tests"]["R7_gemini12pro"] = {**(g12_events or {}), "recent_texts": clean[-8:]}

# ---------------- R8: verdict synthesis ----------------
verdict = {}
for label, res in [("ProdSeller", r_ps), ("laha/ver_pixel", r_laha), ("AIVerseX", r_aivx),
                   ("GeminiShop", r_gsh), ("acczone/Mike_E_0", r_acz)]:
    n = res["name_matches"]
    if n >= 5 or (label == "ProdSeller" and obj_overlap):
        verdict[label] = "MATCH/LINKED"
    elif n >= 1:
        verdict[label] = f"PARTIAL ({n} name match)"
    else:
        verdict[label] = "NO_OVERLAP"
R["tests"]["R8_verdicts"] = verdict
print("\n[R8] verdicts:", json.dumps(verdict, ensure_ascii=False, indent=1))

with open(OUT, "w") as f:
    json.dump(R, f, ensure_ascii=False, indent=1)
print("\nSaved ->", OUT)
