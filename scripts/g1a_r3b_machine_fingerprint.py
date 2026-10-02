#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1a R3b — MongoDB machine-fingerprint clustering + separated line analysis
ObjectId bytes 8-13 (hex chars 8-17) = per-process random value => clusters = insertion processes/machines.
Q: were cb_ rows created by the same process family as the platform's own catalog rows?
Output: research/g1a_r3b_machine_fingerprint_20261002.json
"""
import json, re
from datetime import datetime, timezone
from collections import Counter, defaultdict

R = "/home/z/my-project/research/"
OUT = R + "g1a_r3b_machine_fingerprint_20261002.json"

OID = re.compile(r"^[0-9a-f]{24}$")

# --- load cb_ catalog (StackVault view) ---
d = json.load(open(R + "g1_cb_live_catalog_20261002.json"))
prods = d.get("products", [])
cb, ps = [], []
for p in prods:
    pid = str(p.get("id", ""))
    m = re.match(r"^(cb_|ps_)([0-9a-f]{24})$", pid)
    if m:
        oid = m.group(2)
        rec = {"oid": oid, "ts": int(oid[:8], 16), "mid": oid[8:18], "cnt": int(oid[18:], 16),
               "name": str(p.get("name", ""))[:70]}
        (cb if m.group(1) == "cb_" else ps).append(rec)

# --- load prodseller api catalog ---
d2 = json.load(open(R + "prodseller_live/products_fresh.json"))
prods2 = d2.get("products", [])
platform = []
for p in prods2:
    oid = str(p.get("id", ""))
    if OID.match(oid):
        platform.append({"oid": oid, "ts": int(oid[:8], 16), "mid": oid[8:18], "cnt": int(oid[18:], 16),
                          "name": str(p.get("name", ""))[:70]})

print(f"cb_={len(cb)} ps_={len(ps)} platform={len(platform)}")

# --- machine fingerprint clusters ---
def clusters(recs, label):
    by_mid = defaultdict(list)
    for r in recs: by_mid[r["mid"]].append(r)
    cl = sorted(by_mid.values(), key=lambda x: -len(x))
    out = []
    for c in cl[:12]:
        tss = sorted(r["ts"] for r in c)
        out.append({"machine_hex": c[0]["mid"], "n_products": len(c),
                    "first": datetime.fromtimestamp(tss[0], tz=timezone.utc).isoformat(),
                    "last": datetime.fromtimestamp(tss[-1], tz=timezone.utc).isoformat(),
                    "span_days": round((tss[-1] - tss[0]) / 86400, 1),
                    "sample": c[0]["name"]})
    print(f"\n=== {label}: {len(by_mid)} distinct machine fingerprints ===")
    for o in out: print(" ", o)
    return {o["machine_hex"]: o for o in out}, set(by_mid.keys())

cb_cl, cb_mids = clusters(cb, "cb_ line")
ps_cl, ps_mids = clusters(ps, "ps_ line")
pl_cl, pl_mids = clusters(platform, "platform catalog (prodseller.com API)")

# cross-shared fingerprints
shared = {
    "cb_∩platform": sorted(cb_mids & pl_mids),
    "ps_∩platform": sorted(ps_mids & pl_mids),
    "cb_∩ps_": sorted(cb_mids & ps_mids),
}
print("\n=== SHARED machine fingerprints ===")
for k, v in shared.items(): print(f" {k}: {len(v)} {v[:5]}")

# --- hour histograms (UTC) full ---
def hist(recs):
    return dict(sorted(Counter(datetime.fromtimestamp(r["ts"], tz=timezone.utc).hour for r in recs).items()))

# separated ps_ check vs platform ObjectId equality
ps_oids = {r["oid"] for r in ps}
pl_oids = {r["oid"] for r in platform}
print(f"\nps_ ∩ platform ObjectId: {len(ps_oids & pl_oids)} / ps_={len(ps_oids)} platform={len(pl_oids)}")

# cb_ hour histogram in local candidate zones
def local_hist(recs, off):
    return dict(sorted(Counter((datetime.fromtimestamp(r["ts"], tz=timezone.utc) + __import__("datetime").timedelta(hours=off)).hour for r in recs).items()))

result = {
    "counts": {"cb_": len(cb), "ps_": len(ps), "platform": len(platform)},
    "machine_fingerprints": {
        "cb_top": list(cb_cl.values()),
        "ps_top": list(ps_cl.values()),
        "platform_top": list(pl_cl.values()),
        "shared": shared,
        "distinct_counts": {"cb_": len(cb_mids), "ps_": len(ps_mids), "platform": len(pl_mids)},
    },
    "hour_hist_utc": {"cb_": hist(cb), "ps_": hist(ps), "platform": hist(platform)},
    "ps_platform_oid_overlap": len(ps_oids & pl_oids),
    "notes": "machine_hex = ObjectId[8:18] = per-process random; same value => same mongod/import process family",
}
json.dump(result, open(OUT, "w"), ensure_ascii=False, indent=1)
print("\nSaved:", OUT)
