#!/usr/bin/env python3
# Post-process MEC-21 report docx (WPS compat):
# 1. footer instrText: Roman for section-2 footer, arabic for body footer
# 2. remove empty <w:pgNumType/> elements
import re
import shutil
import sys
import zipfile
import os

SRC = "/home/z/my-project/download/MEC-21_التقرير_الهندسي_النهائي.docx"
TMP = "/tmp/mec21_docx"

if os.path.exists(TMP):
    shutil.rmtree(TMP)
with zipfile.ZipFile(SRC) as z:
    z.extractall(TMP)

# --- 1. identify footers and their section order via document.xml ---
doc_path = os.path.join(TMP, "word", "document.xml")
doc = open(doc_path, encoding="utf-8").read()

# remove empty pgNumType (cover section emits it)
before = doc.count("<w:pgNumType/>")
doc = doc.replace("<w:pgNumType/>", "")
open(doc_path, "w", encoding="utf-8").write(doc)
print(f"removed empty pgNumType: {before}")

# footer references in document order (footerReference r:id)
refs = re.findall(r'w:footerReference[^>]*r:id="(rId\d+)"', doc)
print("footer refs in order:", refs)

# map rId -> footer file via document.xml.rels
rels = open(os.path.join(TMP, "word", "_rels", "document.xml.rels"), encoding="utf-8").read()
rid2file = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(footer\d+\.xml)"', rels))
print("rid->file:", rid2file)

# first referenced footer belongs to section 2 (Roman); second to section 3 (arabic)
seen = []
for r in refs:
    f = rid2file.get(r)
    if f and f not in seen:
        seen.append(f)
print("footer files in order:", seen)

fmts = ["ROMAN", "arabic"]
for i, fname in enumerate(seen[:2]):
    fpath = os.path.join(TMP, "word", fname)
    if not os.path.exists(fpath):
        print("missing", fname); continue
    fx = open(fpath, encoding="utf-8").read()
    fmt = fmts[i] if i < 2 else "arabic"
    fx2, n = re.subn(
        r'(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)',
        rf'\1 PAGE \\* {fmt} \\* MERGEFORMAT \2',
        fx,
    )
    open(fpath, "w", encoding="utf-8").write(fx2)
    print(f"{fname}: patched {n} PAGE fields -> {fmt}")

# --- rezip ---
out = SRC
if os.path.exists(out):
    os.remove(out)
zf = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
for root, _, files in os.walk(TMP):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, TMP)
        zf.write(full, rel)
zf.close()
print("rezipped:", out, os.path.getsize(out), "bytes")
