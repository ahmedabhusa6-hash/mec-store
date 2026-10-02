#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-14 part 2 — block-timestamp forensics on REF_HAKIM + delta page parentage + anchor verification.
Why: line-diff between 26/09 and 02/10 captures is unreliable (different extraction pipelines) —
the authoritative edit signal is each block's own created/last_edited timestamp captured on 02/10.
Outputs -> research/g14_2026-10-02/
"""
import json, os, collections, re

NEW = "/home/z/my-project/notion_raw_v2_20261002"
OUT = "/home/z/my-project/research/g14_2026-10-02"
REF = "3e658a0779e881c49cddd7b74626d61f"  # REF_HAKIM normalized

def save(name, obj):
    with open("%s/%s" % (OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

rh = json.load(open("%s/pages/%s.json" % (NEW, REF), encoding="utf-8"))
blocks = rh.get("blocks", [])

# ---------- 1) block timestamp distribution ----------
def day(ts): return (ts or "")[:10]
created_by_day = collections.Counter(day(b.get("created")) for b in blocks)
edited_by_day = collections.Counter(day(b.get("edited")) for b in blocks)
print("blocks created by day:", dict(sorted(created_by_day.items())))
print("blocks last-edited by day:", dict(sorted(edited_by_day.items())))

# ---------- 2) isolate 27/09 + 02/10 blocks (the delta window on REF_HAKIM) ----------
delta_blocks = [b for b in blocks if day(b.get("edited")) >= "2026-09-27" or day(b.get("created")) >= "2026-09-27"]
delta_extract = [{"type": b.get("type"), "created": b.get("created"), "edited": b.get("edited"),
                  "text": " ".join(b.get("text") or [])[:220]} for b in delta_blocks]
save("ref_hakim_blocks_edited_since_2709.json",
     {"count": len(delta_blocks),
      "note": "كتل المرجع الحاكم التي أُنشئت أو حُررت في/بعد 27/09 (نافذة الدلتا بين لقطتي 26/09 و02/10)",
      "blocks": delta_extract})
print("REF_HAKIM blocks created/edited since 27/09:", len(delta_blocks))
for d in delta_extract[:25]:
    print("   [%s/%s] %s: %s" % ((d["created"] or "")[:10], (d["edited"] or "")[:10], d["type"][:12], d["text"][:90]))

# ---------- 3) price-anchor blocks + their timestamps (G-12 extension core) ----------
ANCHORS = {"2.80": "ChatGPT Plus cost tier-1", "10.67": "cost tier-2", "17.14": "cost tier-3",
           "4.50": "warranty 2h price", "× 1.2": "sell formula", "×1.2": "sell formula",
           "x 1.2": "sell formula", "* 1.2": "sell formula"}
anchor_hits = []
for b in blocks:
    txt = " ".join(b.get("text") or [])
    for pat, lab in ANCHORS.items():
        if pat in txt:
            anchor_hits.append({"pattern": pat, "label": lab, "created": b.get("created"),
                                 "edited": b.get("edited"), "type": b.get("type"),
                                 "context": txt[:260]})
save("ref_hakim_price_anchor_blocks.json", {"count": len(anchor_hits), "hits": anchor_hits})
print("\nprice-anchor blocks in REF_HAKIM:", len(anchor_hits))
for a in anchor_hits[:20]:
    print("   %s [%s|%s] %s" % (a["pattern"], (a["created"] or "")[:10], (a["edited"] or "")[:10], a["context"][:100]))

# ---------- 4) delta page parentage: which captured pages are children of REF_HAKIM ----------
import glob
children, parents_hist = [], collections.Counter()
for fp in glob.glob("%s/pages/*.json" % NEW):
    try:
        j = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue
    pg = j.get("page", {})
    par = pg.get("parent", {})
    pid = (par.get("page_id") or "").replace("-", "").lower()
    parents_hist["page:" + (pid[:12] if pid else "?")] += 1
    if par.get("page_id") and par["page_id"].replace("-", "").lower() == REF:
        children.append({"title": j.get("title", ""), "reason": j.get("capture_reason", ""),
                          "edited": j.get("last_edited", ""), "blocks": j.get("block_count", 0)})
# also: workspace-level parents
save("ref_hakim_children_in_delta.json",
     {"count": len(children),
      "note": "الصفحات الملتقطة في الدلتا التي أبوها REF_HAKIM (من حقل parent في كائن الصفحة)",
      "children": sorted(children, key=lambda c: c["edited"] or "")})
print("\ncaptured delta pages whose parent == REF_HAKIM:", len(children))
for c in sorted(children, key=lambda c: c["edited"] or ""):
    print("   %s | %-14s | %d blk | %s" % (c["edited"][:10], c["reason"], c["blocks"], c["title"][:70]))

# ---------- 5) top parents among all 436 captured pages ----------
print("\ntop parent pages of captured delta pages:")
for p, n in parents_hist.most_common(12):
    print("   %-24s %d" % (p, n))

# ---------- 6) SUPPLIERS_ONLY structure sample ----------
so = json.load(open("%s/pages/%s.json" % (NEW, "3e958a0779e88159b0c4c7b0553270d9"), encoding="utf-8"))
so_heads = [(" ".join(b.get("text") or []))[:90] for b in so.get("blocks", [])
            if b.get("type", "").startswith("heading")]
save("suppliers_only_headings.json", {"count": len(so_heads), "headings": so_heads[:120]})
print("\nSUPPLIERS_ONLY headings:", len(so_heads))
for h in so_heads[:30]: print("   ", h)
