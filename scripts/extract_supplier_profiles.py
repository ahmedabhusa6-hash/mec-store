#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5: extract per-supplier profiles from archived intel (step 1: local data)."""
import json, re, os

R = "/home/z/my-project/research"
OUT = "/home/z/my-project/research/supplier_profiles_extracted.json"

hist = json.load(open(f"{R}/b3_channel_history.json", encoding="utf-8"))
obs = json.load(open(f"{R}/b3_direct_observations.json", encoding="utf-8"))
tso = json.load(open(f"{R}/stackvault_live/teamsoclo_intel.json", encoding="utf-8"))
tsx = json.load(open(f"{R}/stackvault_live/teamsoclo_extra.json", encoding="utf-8"))
prec = json.load(open(f"{R}/stackvault_live/supply_sources_precise.json", encoding="utf-8"))
sv_prod = json.load(open(f"{R}/stackvault_live/sv_products_current.json", encoding="utf-8"))

profiles = {}

def price_rows(msgs, limit=40):
    """Extract (text, prices found) rows from channel messages."""
    rows = []
    for m in msgs:
        t = m.get("text") or m.get("message") or ""
        if not t: continue
        prices = re.findall(r"\$\s?([0-9]+(?:\.[0-9]{1,2})?)", t)
        if prices:
            rows.append({"date": m.get("date", ""), "text": t[:220], "prices": prices[:6]})
    return rows[:limit]

for ch, data in hist.items():
    msgs = data.get("messages", [])
    profiles[ch] = {
        "n_total": data.get("n_total"),
        "n_priced": data.get("n_priced"),
        "price_messages": price_rows(msgs),
        "first_msg_date": msgs[0].get("date") if msgs else None,
        "last_msg_date": msgs[-1].get("date") if msgs else None,
    }

# direct observations channels detail
obs_ch = {}
for ch, data in obs.get("channels", {}).items():
    if isinstance(data, dict):
        obs_ch[ch] = {k: v for k, v in data.items() if k in
                      ("title", "description", "subscribers", "n_messages", "samples",
                       "channel_url", "username", "verified", "note")}
profiles["_obs_channels"] = obs_ch

# teamsoclo intel summary
profiles["_teamsoclo"] = {
    "intel_keys": list(tso.keys()),
    "intel": tso,
    "extra": tsx,
}

# SV catalog supplier census (prefix-based)
pref = prec["supply_sources"]["id_prefix_census"]
profiles["_sv_catalog"] = {
    "catalog_size": prec["supply_sources"]["catalog_size"],
    "prefix_census": pref,
    "teamsoclo_signals": prec["supply_sources"]["external_signals_in_descriptions"]["teamsoclo.site"],
    "ops_link": prec["supply_sources"]["external_signals_in_descriptions"]["ops link"],
}

# per-supplier SV cost medians by prefix (from products file)
def med(vals):
    v = sorted(vals); n = len(v)
    return round((v[n//2] if n % 2 else (v[n//2-1]+v[n//2])/2), 2) if v else None

by_prefix = {}
for p in sv_prod if isinstance(sv_prod, list) else sv_prod.get("products", []):
    pid = p.get("id", "")
    m = re.match(r"^(ps|mr|dummy)_?", pid)
    if not m: continue
    tag = m.group(1)
    by_prefix.setdefault(tag, {"n": 0, "costs": [], "families": {}})
    d = by_prefix[tag]
    d["n"] += 1
    c = p.get("costPrice")
    if isinstance(c, (int, float)): d["costs"].append(c)
    fam = p.get("category", "?")
    d["families"][fam] = d["families"].get(fam, 0) + 1
for tag, d in by_prefix.items():
    d["cost_median"] = med(d["costs"])
    d["cost_min"] = min(d["costs"]) if d["costs"] else None
    d["cost_max"] = max(d["costs"]) if d["costs"] else None
    d.pop("costs")
profiles["_sv_cost_by_prefix"] = by_prefix

json.dump(profiles, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
print("\n=== channel price-message counts:")
for ch in ["ProdSellerOfficial", "Evo_Era_updates", "gemini12pro_channel", "HitMeowShop", "AISUBSID"]:
    p = profiles[ch]
    print(f"{ch}: total={p['n_total']} priced={p['n_priced']} extracted_rows={len(p['price_messages'])} range={p['first_msg_date']}..{p['last_msg_date']}")
print("\n=== obs channels:", list(obs_ch.keys()))
print("\n=== sv cost by prefix:", json.dumps(by_prefix, ensure_ascii=False, default=str)[:600])
