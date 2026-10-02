#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — Phase 1+2: RUNTIME DISCOVERY + ARTIFACT INVENTORY
Per MASTER AGENT PROMPT (42 sections), forensic grade:
  - Full walk of /home/z/my-project
  - PROJECT-CREATED vs PLATFORM/ENVIRONMENT classification
  - Per-file records: path, size, mtime(+03:00), ext, sha256
  - Role classification + source/derived heuristics
Outputs:
  research/pmrf_v3_build/discovery.json  (dir map + classification)
  research/pmrf_v3_build/inventory.json  (per-file artifact records)
"""
import os, json, hashlib, sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ROOT = "/home/z/my-project"
BUILD = os.path.join(ROOT, "research", "pmrf_v3_build")
os.makedirs(BUILD, exist_ok=True)
TZ = timezone(timedelta(hours=3))  # Asia/Aden (user setting)

RUN_TS = datetime.now(TZ).isoformat(timespec="seconds")

PLATFORM_TOP = {"node_modules", "skills", "tool-results", ".git", ".next", ".cache", ".turbo"}

def sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for blk in iter(lambda: f.read(1 << 20), b""):
                h.update(blk)
        return h.hexdigest()
    except Exception as e:
        return "HASH_ERROR:" + str(e)[:60]

def iso(ts):
    try:
        return datetime.fromtimestamp(ts, TZ).isoformat(timespec="seconds")
    except Exception:
        return None

# ---- walk ----
dir_stats = {}          # rel_dir -> stats
file_records = []       # per-file records (PROJECT material only)
platform_stats = {}     # PLATFORM dirs -> size/file-count summary (no deep walk for node_modules)

for entry in sorted(os.listdir(ROOT)):
    full = os.path.join(ROOT, entry)
    if os.path.isfile(full):
        st = os.stat(full)
        rec = {
            "artifact_id": None, "path": entry, "type": "root_file",
            "ext": os.path.splitext(entry)[1].lower() or "(none)",
            "size": st.st_size, "mtime": iso(st.st_mtime),
            "sha256": sha256_file(full) if st.st_size < 60 * 1024 * 1024 else "SKIPPED_LARGE",
            "class": "PROJECT", "role": "ROOT_FILE",
        }
        file_records.append(rec)
        continue
    if entry in PLATFORM_TOP:
        # PLATFORM: summary only (no deep walk) — but tool-results gets a light walk for the record
        if entry == "tool-results":
            nfiles = 0; total = 0; exts = defaultdict(int)
            for dp, dn, fn in os.walk(full):
                for f in fn:
                    fp = os.path.join(dp, f); nfiles += 1
                    try: total += os.stat(fp).st_size
                    except OSError: pass
                    exts[os.path.splitext(f)[1].lower() or "(none)"] += 1
            platform_stats[entry] = {"files": nfiles, "bytes": total, "top_ext": dict(exts)}
        else:
            platform_stats[entry] = {"note": "platform dependency tree — excluded from project knowledge"}
        continue
    # PROJECT directory: deep walk
    stats = {"files": 0, "bytes": 0, "ext": defaultdict(int), "subdirs": defaultdict(lambda: {"files": 0, "bytes": 0}),
             "mtime_min": None, "mtime_max": None, "largest": []}
    for dp, dn, fn in os.walk(full):
        for f in fn:
            fp = os.path.join(dp, f)
            rel = os.path.relpath(fp, ROOT)
            subdir = os.path.relpath(dp, full).split(os.sep)[0] if dp != full else "(root)"
            try:
                st = os.stat(fp)
            except OSError:
                continue
            ext = os.path.splitext(f)[1].lower() or "(none)"
            mt = iso(st.st_mtime)
            rec = {
                "artifact_id": None, "path": rel, "type": "file",
                "ext": ext, "size": st.st_size, "mtime": mt,
                "sha256": sha256_file(fp) if st.st_size < 60 * 1024 * 1024 else "SKIPPED_LARGE",
                "class": "PROJECT",
                "top_dir": entry, "subdir": subdir,
            }
            file_records.append(rec)
            stats["files"] += 1; stats["bytes"] += st.st_size
            stats["ext"][ext] += 1
            stats["subdirs"][subdir]["files"] += 1
            stats["subdirs"][subdir]["bytes"] += st.st_size
            if mt:
                stats["mtime_min"] = mt if not stats["mtime_min"] or mt < stats["mtime_min"] else stats["mtime_min"]
                stats["mtime_max"] = mt if not stats["mtime_max"] or mt > stats["mtime_max"] else stats["mtime_max"]
            if len(stats["largest"]) < 12 or st.st_size > stats["largest"][-1][1]:
                stats["largest"].append((rel, st.st_size)); stats["largest"].sort(key=lambda x: -x[1]); stats["largest"] = stats["largest"][:12]
    stats["ext"] = dict(stats["ext"]); stats["subdirs"] = dict(stats["subdirs"])
    dir_stats[entry] = stats

# ---- assign artifact IDs (stable: ordered by path) ----
file_records.sort(key=lambda r: r["path"])
for i, r in enumerate(file_records, 1):
    r["artifact_id"] = f"ART-{i:04d}"

# ---- role classification (first pass heuristics; refined later in synthesis) ----
def classify_role(r):
    p = r["path"]
    top = r.get("top_dir") or "(root)"
    if top == "research":
        if "pmrf_v" in p: return "HISTORICAL_BUILD_INTERMEDIATE"
        return "RAW_EVIDENCE_OR_RESEARCH_OUTPUT"
    if top == "notion_raw": return "RAW_NOTION_EXPORT"
    if top == "scripts": return "METHOD_SCRIPT"
    if top == "download":
        if "PMRF_ARCHIVE" in p or "PROJECT MASTER" in p: return "REFERENCE_CANDIDATE"
        return "RELEASE_ARTIFACT"
    if top in ("src", "prisma", "db", "public", "tests", "mini-services", "examples"): return "APP_CODE_OR_APP_ASSET"
    if top in ("data", "upload"): return "DATA_STAGING"
    if p == "worklog.md": return "OPERATIONAL_RECORD"
    if p in ("package.json", "tsconfig.json", "components.json"): return "APP_CONFIG"
    return "PROJECT_FILE_OTHER"
for r in file_records:
    r["role"] = classify_role(r)

discovery = {
    "run": "PMRF v3.0 — Phase 1+2 Runtime Discovery + Inventory",
    "generated_at": RUN_TS,
    "root": ROOT,
    "platform_material": platform_stats,
    "project_dirs": {k: {
        "files": v["files"], "bytes": v["bytes"],
        "ext_top": sorted(v["ext"].items(), key=lambda x: -x[1])[:8],
        "subdirs": {sk: sv for sk, sv in sorted(v["subdirs"].items(), key=lambda x: -x[1]["bytes"])},
        "mtime_range": [v.get("mtime_min"), v.get("mtime_max")],
        "largest_files": v["largest"][:8],
    } for k, v in dir_stats.items()},
    "totals": {
        "project_files": len(file_records),
        "project_bytes": sum(r["size"] for r in file_records),
        "by_role": dict(sorted(defaultdict(int, {k: sum(1 for r in file_records if r["role"] == k) for k in {r["role"] for r in file_records}}).items())),
    },
}

with open(os.path.join(BUILD, "discovery.json"), "w", encoding="utf-8") as f:
    json.dump(discovery, f, ensure_ascii=False, indent=1)
with open(os.path.join(BUILD, "inventory.json"), "w", encoding="utf-8") as f:
    json.dump({"generated_at": RUN_TS, "count": len(file_records), "artifacts": file_records}, f, ensure_ascii=False, indent=1)

# console summary
print(f"RUN {RUN_TS}")
print(f"PROJECT files: {len(file_records):,}  bytes: {sum(r['size'] for r in file_records):,}")
print("\n== PLATFORM (excluded from project knowledge) ==")
for k, v in platform_stats.items():
    print(f"  {k}: {v.get('files', '—')} files" if "files" in v else f"  {k}: {v.get('note','')}")
print("\n== PROJECT dirs ==")
for k, v in sorted(dir_stats.items(), key=lambda x: -x[1]["bytes"]):
    print(f"  {k:14s} {v['files']:5d} files {v['bytes']:>12,} B  subdirs={len(v['subdirs'])}  mtime[{v.get('mtime_min','?')} → {v.get('mtime_max','?')}]")
print("\n== roles ==")
for k, n in discovery["totals"]["by_role"].items():
    print(f"  {k:32s} {n}")
print("\n== largest files ==")
for r in sorted(file_records, key=lambda x: -x["size"])[:15]:
    print(f"  {r['size']:>12,}  {r['path']}")
