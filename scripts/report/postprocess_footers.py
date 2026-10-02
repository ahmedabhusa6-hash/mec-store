#!/usr/bin/env python3
"""Post-process docx per toc.md: patch footer PAGE field format switches (ROMAN/arabic)
and strip empty <w:pgNumType/> from cover section. WPS compatibility."""
import sys, zipfile, shutil, re, os

path = sys.argv[1]
tmp = path + ".tmp"
shutil.copy(path, tmp)

with zipfile.ZipFile(tmp, "r") as zin:
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}

# 1) document.xml: remove empty pgNumType (cover section)
doc = data["word/document.xml"].decode("utf-8")
doc = doc.replace("<w:pgNumType/>", "")
data["word/document.xml"] = doc.encode("utf-8")

# 2) find section order → footer refs (footer2 belongs to front-matter roman, footer3 to body)
# map: locate sectPr blocks in order; extract footerReference ids and pgNumType fmt
sect_fmts = []
for m in re.finditer(r"<w:sectPr[^>]*>.*?</w:sectPr>", doc, re.S):
    blk = m.group(0)
    fmt = None
    fm = re.search(r'<w:pgNumType[^>]*w:fmt="([^"]+)"', blk)
    if fm: fmt = fm.group(1)
    refs = re.findall(r'<w:footerReference[^>]*r:id="(rId\d+)"', blk)
    sect_fmts.append((fmt, refs))
print("sections:", sect_fmts)

# resolve rIds to footer files via document.xml.rels
rels = data["word/_rels/document.xml.rels"].decode("utf-8")
rid2file = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(footer\d+\.xml)"', rels))

def patch_footer(fname, word_fmt):
    key = "word/" + fname
    if key not in data: return False
    xml = data[key].decode("utf-8")
    xml2 = re.sub(r"(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)",
                  r"\1 PAGE \\* " + word_fmt + r" \\* MERGEFORMAT \2", xml)
    if xml2 != xml:
        data[key] = xml2.encode("utf-8")
        print("patched", fname, "→", word_fmt)
        return True
    print("no PAGE field found in", fname)
    return False

for fmt, refs in sect_fmts:
    word_fmt = None
    if fmt and "roman" in fmt.lower(): word_fmt = "ROMAN"
    elif fmt in ("decimal", None): word_fmt = "arabic"
    if word_fmt:
        for rid in refs:
            f = rid2file.get(rid)
            if f: patch_footer(f, word_fmt)

with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
    for n in names:
        zout.writestr(n, data[n])
os.remove(tmp)
print("post-process done:", path)
