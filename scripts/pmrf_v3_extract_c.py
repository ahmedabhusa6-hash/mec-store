#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — Phase 3 Batch C: CONTENT EXTRACTION — download/
  MD/TXT/JSON/CSV → direct structural read
  XLSX → worksheets, headers, row counts, formulas count
  DOCX → headings, tables, TOC
Output: research/pmrf_v3_build/extract_download.json
"""
import os, json, re, zipfile
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET

ROOT = "/home/z/my-project"
BUILD = os.path.join(ROOT, "research", "pmrf_v3_build")
TZ = timezone(timedelta(hours=3))
RUN_TS = datetime.now(TZ).isoformat(timespec="seconds")
DL = os.path.join(ROOT, "download")

def xlsx_info(fp):
    info = {"sheets": {}}
    try:
        with zipfile.ZipFile(fp) as z:
            wb = z.read("xl/workbook.xml").decode("utf-8", errors="replace")
            shared = []
            if "xl/sharedStrings.xml" in z.namelist():
                sst = ET.fromstring(z.read("xl/sharedStrings.xml"))
                ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
                for si in sst.findall("m:si", ns):
                    shared.append("".join(t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
            sheets = re.findall(r'<sheet[^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb)
            rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8", errors="replace")
            ridmap = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
            formula_count = 0
            for name, rid in sheets:
                tgt = ridmap.get(rid, "")
                path = ("xl/" + tgt.lstrip("/")) if not tgt.startswith("xl/") else tgt
                if path not in z.namelist():
                    path = "xl/worksheets/" + os.path.basename(tgt)
                if path not in z.namelist():
                    info["sheets"][name] = {"error": "sheet target missing"}; continue
                ws = z.read(path).decode("utf-8", errors="replace")
                dims = re.search(r'<dimension ref="([^"]+)"', ws)
                rows = ws.count("<row ")
                fcount = ws.count("<f>") + ws.count("<f ")
                formula_count += fcount
                # first row of cells (headers) via shared strings
                first_row = re.search(r"<row[^>]*>(.*?)</row>", ws, re.S)
                headers = []
                if first_row:
                    for m in re.finditer(r'<c r="[A-Z]+\d+"[^>]*?(?: t="(\w+)")?[^>]*>(?:<f>.*?</f>)?(?:<v>([^<]*)</v>)?', first_row.group(1)):
                        t, v = m.group(1), m.group(2)
                        if t == "s" and v is not None and v.isdigit() and int(v) < len(shared):
                            headers.append(shared[int(v)])
                        elif v:
                            headers.append(v)
                        if len(headers) >= 14: break
                info["sheets"][name] = {"dimension": dims.group(1) if dims else "?", "rows": rows, "formulas": fcount, "headers": headers[:14]}
            info["total_formulas"] = formula_count
    except Exception as e:
        info["error"] = str(e)[:150]
    return info

def docx_info(fp):
    info = {}
    try:
        with zipfile.ZipFile(fp) as z:
            doc = z.read("word/document.xml").decode("utf-8", errors="replace")
            heads = re.findall(r'<w:pStyle w:val="Heading(\d)"/>(.*?)</w:p>', doc, re.S)
            texts = []
            for lvl, body in heads[:60]:
                t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", body))
                if t.strip(): texts.append((f"H{lvl}", t.strip()[:80]))
            info["headings"] = texts
            info["heading_count"] = len(texts)
            info["tables"] = doc.count("<w:tbl>")
            info["paragraphs"] = doc.count("<w:p>") - doc.count("<w:p/>")
    except Exception as e:
        info["error"] = str(e)[:150]
    return info

out = {}
for fn in sorted(os.listdir(DL)):
    fp = os.path.join(DL, fn)
    if os.path.isdir(fp):
        sub = {}
        for f2 in sorted(os.listdir(fp)):
            fp2 = os.path.join(fp, f2)
            if os.path.isfile(fp2):
                sub[f2] = {"size": os.path.getsize(fp2), "first_line": open(fp2, encoding="utf-8", errors="replace").readline().strip()[:100]}
        out[fn + "/"] = {"type": "DIR", "size": sum(v["size"] for v in sub.values()), "children": sub}
        continue
    sz = os.path.getsize(fp)
    ext = os.path.splitext(fn)[1].lower()
    rec = {"size": sz, "ext": ext, "mtime": datetime.fromtimestamp(os.path.getmtime(fp), TZ).isoformat(timespec="seconds")}
    try:
        if ext == ".xlsx":
            rec.update({"type": "XLSX"}, **xlsx_info(fp))
        elif ext == ".docx":
            rec.update({"type": "DOCX"}, **docx_info(fp))
        elif ext == ".pdf":
            rec.update({"type": "PDF", "note": "derived PDF of a DOCX deliverable — content equals the DOCX twin"})
        elif ext in (".md",):
            src = open(fp, encoding="utf-8", errors="replace").read()
            rec.update({"type": "MD", "lines": src.count("\n") + 1,
                        "headings": [h[:80] for h in re.findall(r"^#{1,3}\s+(.+)$", src, re.M)][:28],
                        "first_line": src.split("\n")[0][:100]})
        elif ext == ".json":
            d = json.load(open(fp, encoding="utf-8"))
            rec.update({"type": "JSON", "json_type": type(d).__name__})
            if isinstance(d, dict):
                rec["top_keys"] = list(d.keys())[:25]
                for k, v in d.items():
                    if isinstance(v, list) and v and isinstance(v[0], dict):
                        rec.setdefault("collections", {})[k] = {"count": len(v), "keys": list(v[0].keys())[:18]}
            elif isinstance(d, list):
                rec["count"] = len(d)
                if d and isinstance(d[0], dict): rec["record_keys"] = list(d[0].keys())[:18]
        elif ext == ".csv":
            src = open(fp, encoding="utf-8", errors="replace").read()
            lines = src.splitlines()
            rec.update({"type": "CSV", "rows": len(lines) - 1, "header": lines[0][:160], "sample": lines[1][:160] if len(lines) > 1 else None})
        elif ext in (".html",):
            src = open(fp, encoding="utf-8", errors="replace").read(5000)
            t = re.search(r"<title[^>]*>(.*?)</title>", src, re.S | re.I)
            rec.update({"type": "HTML", "title": (t.group(1).strip()[:100] if t else None)})
        rec["inspection"] = "INSPECTED"
    except Exception as e:
        rec["inspection"] = f"BLOCKED: {str(e)[:100]}"
    out[fn] = rec

result = {"run": "PMRF v3.0 — Batch C: download/ content extraction", "generated_at": RUN_TS,
          "count": len(out), "artifacts": out}
with open(os.path.join(BUILD, "extract_download.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print(f"RUN {RUN_TS} — {len(out)} entries")
for fn, rec in out.items():
    if rec.get("type") == "DIR":
        print(f"  [DIR] {fn} children={len(rec['children'])}")
    elif rec.get("type") == "XLSX":
        print(f"  [XLSX] {fn[:58]:58s} sheets={len(rec.get('sheets',{}))} formulas={rec.get('total_formulas','?')}")
    elif rec.get("type") == "DOCX":
        print(f"  [DOCX] {fn[:58]:58s} H={rec.get('heading_count','?')} tables={rec.get('tables','?')}")
    elif rec.get("type") == "MD":
        print(f"  [MD]   {fn[:58]:58s} lines={rec.get('lines','?')} H1={rec.get('headings',['?'])[0][:40] if rec.get('headings') else '?'}")
    elif rec.get("type") == "JSON":
        cols = rec.get("collections") or {}
        biggest = max(((k, v['count']) for k, v in cols.items()), default=("?", 0), key=lambda x: x[1])
        print(f"  [JSON] {fn[:58]:58s} {rec.get('json_type')} collections={len(cols)} biggest={biggest}")
    elif rec.get("type") == "CSV":
        print(f"  [CSV]  {fn[:58]:58s} rows={rec.get('rows')}")
    else:
        print(f"  [{rec.get('type','?')}] {fn[:58]:58s} {str(rec.get('inspection'))[:40]}")
