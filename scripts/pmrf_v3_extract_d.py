#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — Phase 3 Batch D: CONTENT EXTRACTION — scripts/ + src/ + prisma + data
  scripts → families, sizes, docstrings/first-lines, group map
  src    → MEC store app: pages, api routes, components, prisma schema tables
  data   → what's in data/ staging
Output: research/pmrf_v3_build/extract_scripts_src.json
"""
import os, json, re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ROOT = "/home/z/my-project"
BUILD = os.path.join(ROOT, "research", "pmrf_v3_build")
TZ = timezone(timedelta(hours=3))
RUN_TS = datetime.now(TZ).isoformat(timespec="seconds")

def first_meaningful(fp, max_lines=8):
    try:
        with open(fp, encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
        for l in lines:
            s = l.strip()
            if s.startswith('"""') or s.startswith("'''"):
                s = s.strip("\"'")
                return s[:120] if s else (lines[2].strip()[:120] if len(lines) > 2 else None)
            if s.startswith("#") and not s.startswith("#!") and len(s) > 4:
                return s.lstrip("# ").strip()[:120]
        return None
    except Exception:
        return None

# ---------- scripts ----------
fam = defaultdict(lambda: {"files": 0, "bytes": 0, "examples": [], "subdirs": set()})
scripts = {}
for dirpath, dn, fn in os.walk(os.path.join(ROOT, "scripts")):
    for f in fn:
        fp = os.path.join(dirpath, f)
        rel = os.path.relpath(fp, ROOT)
        sz = os.path.getsize(fp)
        base = os.path.basename(f)
        family = re.split(r"[_\.\-]", base)[0].lower()
        fam[family]["files"] += 1; fam[family]["bytes"] += sz
        fam[family]["subdirs"].add(rel.split("/")[1])
        if len(fam[family]["examples"]) < 6:
            fam[family]["examples"].append({"file": rel, "size": sz, "purpose": first_meaningful(fp)})
        scripts[rel] = {"size": sz, "purpose": first_meaningful(fp)}

# ---------- src (MEC store app) ----------
app = {"tree": {}, "pages": [], "api_routes": [], "components": [], "lib": []}
for dirpath, dn, fn in os.walk(os.path.join(ROOT, "src")):
    rel_dir = os.path.relpath(dirpath, ROOT)
    for f in fn:
        rel = f"{rel_dir}/{f}"
        app["tree"][rel] = os.path.getsize(os.path.join(dirpath, f))
for rel in app["tree"]:
    if "/app/" in rel or rel.startswith("src/app"):
        if "page." in rel: app["pages"].append(rel)
        if "route." in rel or "/api/" in rel: app["api_routes"].append(rel)
    if "/components/" in rel: app["components"].append(rel)
    if "/lib/" in rel: app["lib"].append(rel)

# prisma schema tables
prisma_tables = []
ps = os.path.join(ROOT, "prisma", "schema.prisma")
if os.path.exists(ps):
    src = open(ps, encoding="utf-8", errors="replace").read()
    prisma_tables = re.findall(r"^model\s+(\w+)\s*\{", src, re.M)
    prisma_raw = src[:400]

# data/
data_files = {}
for dirpath, dn, fn in os.walk(os.path.join(ROOT, "data")):
    for f in fn:
        fp = os.path.join(dirpath, f)
        data_files[os.path.relpath(fp, ROOT)] = {"size": os.path.getsize(fp), "head": open(fp, encoding="utf-8", errors="replace").readline().strip()[:80]}

result = {
    "run": "PMRF v3.0 — Batch D: scripts/ + src/ + prisma + data/",
    "generated_at": RUN_TS,
    "scripts": {
        "total_files": len(scripts),
        "families": {k: {"files": v["files"], "bytes": v["bytes"], "subdirs": sorted(v["subdirs"]), "examples": v["examples"]} for k, v in sorted(fam.items(), key=lambda x: -x[1]["files"])},
        "all_files": scripts,
    },
    "src_app": {
        "total_files": len(app["tree"]),
        "pages": app["pages"],
        "api_routes": app["api_routes"],
        "components_count": len(app["components"]),
        "lib_count": len(app["lib"]),
        "tree_top": dict(list(sorted(app["tree"].items(), key=lambda x: -x[1]))[:25]),
    },
    "prisma": {"tables": prisma_tables, "schema_head": prisma_raw if os.path.exists(ps) else None},
    "data_staging": data_files,
}
with open(os.path.join(BUILD, "extract_scripts_src.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print(f"RUN {RUN_TS}")
print(f"scripts: {len(scripts)} files, {len(fam)} families")
for k, v in sorted(fam.items(), key=lambda x: -x[1]["files"])[:22]:
    ex = v["examples"][0]
    print(f"  {k:22s} files={v['files']:3d} {v['bytes']:>9,}B  e.g. {ex['file'].split('/',1)[1][:44]:44s} | {str(ex['purpose'])[:60]}")
print(f"\nsrc/: {len(app['tree'])} files | pages={len(app['pages'])} | api={len(app['api_routes'])} | components={len(app['components'])} | lib={len(app['lib'])}")
print("prisma tables:", prisma_tables)
print("app pages:", [p.replace('src/app','')[:60] for p in app["pages"]][:14])
print("api routes:", [p.replace('src/app','')[:60] for p in app["api_routes"]][:14])
print(f"\ndata/: {len(data_files)} files")
for k, v in list(data_files.items())[:8]: print(f"  {k[:70]:70s} {v['size']:>8,} | {v['head'][:50]}")
