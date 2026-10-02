#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — Phase 3 Batch A: CONTENT EXTRACTION — research/
Per MASTER AGENT PROMPT §6 (file-type-specific extraction):
  JSON → keys / nested structures / record counts / status fields / identifiers / timestamps
  HTML → title, structure markers
  MD   → headings
  PDF  → flag for manual pass (record explicit limitation)
Output: research/pmrf_v3_build/extract_research.json
"""
import os, json, re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ROOT = "/home/z/my-project"
BUILD = os.path.join(ROOT, "research", "pmrf_v3_build")
TZ = timezone(timedelta(hours=3))
RUN_TS = datetime.now(TZ).isoformat(timespec="seconds")

with open(os.path.join(BUILD, "inventory.json"), encoding="utf-8") as f:
    inv = json.load(f)
arts = [a for a in inv["artifacts"] if a["path"].startswith("research/")]

out = {}
manual_flags = []

def summarize_json(path, data):
    """Structural summary of a JSON research artifact."""
    s = {"json_type": type(data).__name__}
    if isinstance(data, dict):
        s["top_keys"] = list(data.keys())[:40]
        # common research-envelope fields
        for k in ("meta", "summary", "source", "timestamp", "generated_at", "method", "wave", "query", "target"):
            if k in data:
                v = data[k]
                s[f"field:{k}"] = v if isinstance(v, (str, int, float, bool)) else (
                    {"len": len(v), "sample": list(v.keys())[:15] if isinstance(v, dict) else v[:3]} if isinstance(v, (list, dict)) else str(v)[:120])
        # list-valued record collections
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                s.setdefault("record_collections", {})[k] = {
                    "count": len(v),
                    "record_keys": list(v[0].keys())[:25],
                }
            elif isinstance(v, dict) and any(isinstance(x, (int, float)) for x in list(v.values())[:8] if x is not None) and len(v) > 5:
                # counter-like dicts (e.g. prefix counts)
                s.setdefault("counter_maps", {})[k] = dict(list(v.items())[:20]) if len(v) <= 20 else {"_len": len(v), "sample": dict(list(v.items())[:10])}
    elif isinstance(data, list):
        s["count"] = len(data)
        if data and isinstance(data[0], dict):
            s["record_keys"] = list(data[0].keys())[:25]
            s["first_record"] = {k: (str(x)[:80]) for k, x in list(data[0].items())[:12]}
            s["last_record"] = {k: (str(x)[:80]) for k, x in list(data[-1].items())[:12]} if len(data) > 1 else None
    return s

HTML_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
MD_H = re.compile(r"^(#{1,3})\s+(.+)$", re.M)

for a in arts:
    p = a["path"]
    fp = os.path.join(ROOT, p)
    rec = {"artifact_id": a["artifact_id"], "path": p, "size": a["size"], "mtime": a["mtime"],
           "ext": a["ext"], "inspection": None, "content": {}}
    try:
        if a["ext"] == ".json":
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
            rec["content"] = summarize_json(p, data)
            rec["inspection"] = "INSPECTED_SCHEMA"
        elif a["ext"] == ".html":
            with open(fp, encoding="utf-8", errors="replace") as f:
                head = f.read(20_000)
            t = HTML_TITLE.search(head)
            rec["content"] = {"title": (t.group(1).strip()[:120] if t else None), "bytes": a["size"]}
            rec["inspection"] = "INSPECTED_TITLE"
        elif a["ext"] == ".md":
            with open(fp, encoding="utf-8", errors="replace") as f:
                txt = f.read()
            rec["content"] = {"headings": MD_H.findall(txt)[:30], "lines": txt.count("\n") + 1}
            rec["inspection"] = "INSPECTED_HEADINGS"
        elif a["ext"] == ".pdf":
            rec["content"] = {"note": "binary PDF — flagged for manual/structured pass"}
            rec["inspection"] = "BLOCKED_BINARY_PDF"
            manual_flags.append(p)
        elif a["ext"] in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"):
            rec["content"] = {"note": "image capture (evidence snapshot)"}
            rec["inspection"] = "NOT_APPLICABLE_IMAGE"
        else:
            rec["content"] = {"note": f"unparsed type {a['ext']}"}
            rec["inspection"] = "PARTIALLY_INSPECTED"
    except Exception as e:
        rec["inspection"] = "BLOCKED_ERROR"
        rec["content"] = {"error": str(e)[:150]}
    out[p] = rec

# aggregate view per subdir
agg = defaultdict(lambda: {"files": 0, "inspected": 0, "blocked": 0, "partial": 0, "na": 0, "bytes": 0})
for p, r in out.items():
    sd = p.split("/")[1] if p.count("/") >= 1 else "(root)"
    if "/" not in p[8:]:
        sd = "(research root)"
    a = agg[sd]; a["files"] += 1; a["bytes"] += r["size"]
    if r["inspection"] and r["inspection"].startswith("INSPECTED"): a["inspected"] += 1
    elif r["inspection"] and r["inspection"].startswith("BLOCKED"): a["blocked"] += 1
    elif r["inspection"] and r["inspection"].startswith("PARTIAL"): a["partial"] += 1
    else: a["na"] += 1

result = {
    "run": "PMRF v3.0 — Batch A: research/ content extraction",
    "generated_at": RUN_TS,
    "total_artifacts": len(out),
    "per_subdir": dict(agg),
    "manual_followup": manual_flags,
    "artifacts": out,
}
with open(os.path.join(BUILD, "extract_research.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print(f"RUN {RUN_TS}")
print(f"research artifacts processed: {len(out)}")
print("\n== per subdir ==")
for sd, a in sorted(agg.items(), key=lambda x: -x[1]["bytes"]):
    print(f"  {sd:22s} files={a['files']:4d} inspected={a['inspected']:4d} blocked={a['blocked']:2d} partial={a['partial']:2d} na={a['na']:3d} {a['bytes']:>11,} B")
print(f"\nmanual followup (binary PDF): {manual_flags}")
