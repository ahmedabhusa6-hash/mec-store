#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1a R3 — ObjectId timestamp forensics (offline, pure analysis)
MongoDB ObjectId = 8 hex chars unix ts + 10 hex random/counter.
Decode insertion times for: cb_ (StackVault wholesale line), ps_ (ProdSeller direct line),
ProdSeller-API own catalog, canboso, DigitalCore, RichAI.
Infer operator timezone from activity-hour distribution.
Output: research/g1a_r3_objectid_forensics_20261002.json
"""
import json, re
from datetime import datetime, timezone, timedelta
from collections import Counter

R = "/home/z/my-project/research/"
OUT = R + "g1a_r3_objectid_forensics_20261002.json"

OID_RE = re.compile(r"^[0-9a-f]{24}$")

def decode(oid):
    ts = int(oid[:8], 16)
    return ts

def load_products(path):
    try:
        d = json.load(open(path))
    except Exception:
        return None
    if isinstance(d, dict):
        for k in ("products", "items", "data"):
            if k in d and isinstance(d[k], list):
                return d[k]
        return None
    if isinstance(d, list):
        return d
    return None

def extract(prods, id_field_candidates=("id", "_id", "productId", "product_id")):
    out = []
    for p in (prods or []):
        if not isinstance(p, dict): continue
        oid = None
        for f in id_field_candidates:
            v = p.get(f)
            if isinstance(v, str) and OID_RE.match(v):
                oid = v; break
            if isinstance(v, dict):
                vv = v.get("$oid")
                if isinstance(vv, str) and OID_RE.match(vv):
                    oid = vv; break
        if oid:
            out.append({"oid": oid, "ts": decode(oid), "name": str(p.get("name", ""))[:60]})
    return out

datasets = {
    "stackvault_cb_": R + "g1_cb_live_catalog_20261002.json",
    "stackvault_master": R + "sv_master_refresh_20261002.json",
    "prodseller_api_old": R + "prodseller_live/products_raw.json",
    "prodseller_api_fresh": R + "prodseller_live/products_fresh.json",
    "r3_newkeys_raw": R + "g1_r3_newkeys_raw_20261002.json",
}

parsed = {}
for name, path in datasets.items():
    prods = load_products(path)
    if prods is None:
        # try nested search for r3 raw
        try:
            d = json.load(open(path))
            found = []
            def walk(x):
                if isinstance(x, list) and x and isinstance(x[0], dict) and any(
                        isinstance(x[0].get(f), str) and OID_RE.match(str(x[0].get(f))) is not None for f in ("id", "_id", "productId")):
                    found.append(x); return
                if isinstance(x, dict):
                    for v in x.values(): walk(v)
                elif isinstance(x, list):
                    for v in x[:50]: walk(v)
            walk(d)
            prods = found[0] if found else None
        except Exception:
            prods = None
    parsed[name] = extract(prods) if prods else []
    print(f"{name}: {len(parsed[name])} ObjectIds")

# For stackvault master: split by prefix
sv = parsed.get("stackvault_master", [])
cb_ids = [x for x in sv if x["oid"].startswith("cb_") or True]  # sv ids may have cb_ prefix inside id field
# actually check: ids in master may be like cb_xxx; extract separately
try:
    d = json.load(open(datasets["stackvault_master"]))
    sv_products = d.get("products") or d.get("catalog") or []
    cb_line, ps_line, mr_line, other = [], [], [], []
    for p in sv_products:
        pid = str(p.get("id", ""))
        base = pid[3:] if len(pid) == 3+24 and OID_RE.match(pid[3:]) else None
        if base:
            rec = {"oid": base, "ts": decode(base), "name": str(p.get("name",""))[:60], "pid": pid}
            if pid.startswith("cb_"): cb_line.append(rec)
            elif pid.startswith("ps_"): ps_line.append(rec)
            elif pid.startswith("mr_"): mr_line.append(rec)
            else: other.append(rec)
    print(f"master split: cb_={len(cb_line)} ps_={len(ps_line)} mr_={len(mr_line)} other={len(other)}")
    parsed["sv_cb_line"] = cb_line
    parsed["sv_ps_line"] = ps_line
    parsed["sv_mr_line"] = mr_line
except Exception as e:
    print("master split failed:", e)

# cb catalog raw ids (id = cb_<oid>)
cbcat = parsed.get("stackvault_cb_", [])
for rec in cbcat:
    m = re.match(r"^cb_([0-9a-f]{24})$", rec["oid"])  # already matched? cb_ ids won't match OID_RE
# re-extract cb_ with prefix strip
cb2 = []
prods = load_products(datasets["stackvault_cb_"])
for p in (prods or []):
    pid = str(p.get("id", ""))
    m = re.match(r"^(cb_|ps_|mr_)([0-9a-f]{24})$", pid)
    if m:
        cb2.append({"oid": m.group(2), "ts": decode(m.group(2)), "name": str(p.get("name",""))[:60], "pid": pid})
parsed["cb_catalog_all"] = cb2
print("cb_catalog prefixes:", Counter([r["pid"][:3] for r in cb2]))

TZ_CANDIDATES = {
    "Vietnam (UTC+7)": 7, "France (UTC+2 CEST)": 2, "Egypt (UTC+3)": 3,
    "Saudi (UTC+3)": 3, "India (UTC+5:30)": 5.5, "China (UTC+8)": 8, "Indonesia WIB (UTC+7)": 7,
    "UK (UTC+1)": 1, "US East (UTC-4)": -4,
}

def hour_hist(records):
    h = Counter()
    for r in records:
        dt = datetime.fromtimestamp(r["ts"], tz=timezone.utc)
        h[dt.hour] += 1
    return h

def tz_fit(records):
    """fraction of insertions within 08:00-23:59 local time"""
    if not records: return {}
    fits = {}
    for name, off in TZ_CANDIDATES.items():
        good = 0
        for r in records:
            dt = datetime.fromtimestamp(r["ts"], tz=timezone.utc) + timedelta(hours=off)
            if 8 <= dt.hour < 24: good += 1
        fits[name] = round(good / len(records), 3)
    # also night-activity metric (00-07 local = graveyard)
    return fits

def night_frac(records, off):
    if not records: return None
    n = sum(1 for r in records
            if 0 <= (datetime.fromtimestamp(r["ts"], tz=timezone.utc) + timedelta(hours=off)).hour < 7)
    return round(n / len(records), 3)

analysis = {}
for name in ["sv_cb_line", "sv_ps_line", "sv_mr_line", "cb_catalog_all",
             "prodseller_api_old", "prodseller_api_fresh"]:
    recs = parsed.get(name) or []
    if not recs: continue
    recs_d = [r for r in recs if r["ts"] > 1420000000]  # sane ts (>2015)
    if not recs_d: continue
    tss = sorted(r["ts"] for r in recs_d)
    span = (datetime.fromtimestamp(tss[0], tz=timezone.utc), datetime.fromtimestamp(tss[-1], tz=timezone.utc))
    analysis[name] = {
        "n": len(recs_d),
        "first_insert": span[0].isoformat(),
        "last_insert": span[1].isoformat(),
        "hour_hist_utc": dict(sorted(hour_hist(recs_d).items())),
        "tz_fit_08_24_local": tz_fit(recs_d),
        "night_frac": {k: night_frac(recs_d, v) for k, v in TZ_CANDIDATES.items() if k in
                       ("Vietnam (UTC+7)", "France (UTC+2 CEST)", "Egypt (UTC+3)", "India (UTC+5:30)", "China (UTC+8)")},
        "top_names": [r["name"] for r in recs_d[:5]],
    }

# bulk-import detection: consecutive ts within small windows
def bulk_events(recs, gap=120):
    if not recs: return []
    tss = sorted((r["ts"], r["name"]) for r in recs)
    events, cur = [], [tss[0]]
    for t in tss[1:]:
        if t[0] - cur[-1][0] <= gap: cur.append(t)
        else:
            if len(cur) >= 5: events.append({"count": len(cur), "start": datetime.fromtimestamp(cur[0][0], tz=timezone.utc).isoformat(), "sample": cur[0][1]})
            cur = [t]
    if len(cur) >= 5: events.append({"count": len(cur), "start": datetime.fromtimestamp(cur[0][0], tz=timezone.utc).isoformat(), "sample": cur[0][1]})
    return events

for name in ["sv_cb_line", "sv_ps_line", "prodseller_api_fresh", "cb_catalog_all"]:
    recs = parsed.get(name) or []
    if recs:
        analysis.setdefault(name, {})["bulk_import_events"] = bulk_events([r for r in recs if r["ts"] > 1420000000])

out = {"run": "G-1a R3 ObjectId forensics", "datasets": {k: len(v) for k, v in parsed.items()},
       "analysis": analysis, "method": "MongoDB ObjectId first-8-hex = unix ts; tz_fit = share of inserts 08:00-23:59 local"}
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)

for name, a in analysis.items():
    print(f"\n=== {name} (n={a['n']}) ===")
    print(f" first: {a['first_insert']}\n last:  {a['last_insert']}")
    fits = sorted(a["tz_fit_08_24_local"].items(), key=lambda x: -x[1])[:5]
    print(" tz fit (08-24 local):", fits)
    print(" night frac:", {k: v for k, v in a.get("night_frac", {}).items()})
    evs = a.get("bulk_import_events", [])
    print(f" bulk events (>=5 within 120s): {len(evs)}")
    for e in evs[:6]: print("   ", e)
print("\nSaved:", OUT)
