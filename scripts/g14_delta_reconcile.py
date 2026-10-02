#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-14 — NOTION DELTA DETAILED RECONCILIATION — 2026-10-02
Extension of G-12 (foundational-layer price reconciliation). User focus:
  (a) supplier research dated today 02/10 (trio 3ed58a07… pages)
  (b) the governing reference (REF_HAKIM) — 3,243 blocks, changed 27/09
Analysis:
  A) Load 6 focus pages from notion_raw_v2_20261002/pages/
  B) REF_HAKIM deep structure: block-type histogram + headings map + child_page children
     + line-level diff vs old 26/09 text export
  C) Entity extraction (t.me handles / @handles / domains / registry names) and
     cross-reference vs: §19 channel registry (hardcoded) + entity_registry.json (10)
     + gds_qualified_entities.json (230)
  D) Price extraction with context + reconciliation anchors (G-12 extension):
     ChatGPT Plus cost ladder 2.80/10.67/17.14 · sell=cost×1.2 · 4.50/2h · 8-10/3mo
  E) Outputs -> research/g14_2026-10-02/
Zero-hallucination: every claim in outputs carries its source page id + block evidence.
"""
import json, os, re, difflib, collections

NEW = "/home/z/my-project/notion_raw_v2_20261002"
OLD_TEXT = "/home/z/my-project/notion_raw/text/3e658a0779e881c49cddd7b74626d61f.txt"
OUT = "/home/z/my-project/research/g14_2026-10-02"
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT + "/extracted_fulltext", exist_ok=True)

PAGES = {
    "REF_HAKIM":   {"id": "3e658a0779e881c49cddd7b74626d61f", "label": "المرجع الحاكم — قاعدة بيانات أرخص موردي ومتاجر المنتجات والخدمات الرقمية (3,243 كتلة · CHANGED 27/09)", "focus": "primary"},
    "DR_FINDINGS": {"id": "3ed58a0779e88183a21aeb6999ed4924", "label": "Deep Research Findings — Supplier Intelligence — 2026-10-02 (127 كتلة · NEW)", "focus": "primary"},
    "TG_PROVIDERS":{"id": "3ed58a0779e881b3954fe116cd960d77", "label": "Supplier Intelligence — Telegram API Providers — Research & System Design (401 كتلة · NEW)", "focus": "primary"},
    "DR_PROMPT":   {"id": "3ed58a0779e88116b4b9c4a0eea3e91a", "label": "Final Deep Research Prompt — Provider Intelligence Engine (147 كتلة · NEW)", "focus": "primary"},
    "SUPPLIERS_ONLY":{"id": "3e958a0779e88159b0c4c7b0553270d9", "label": "موردين فقط (2,608 كتل · NEW 29/09)", "focus": "secondary"},
    "ZAI_ENG":     {"id": "3ec58a0779e8812ea7ebf73d377c9ba2", "label": "مرجع حاكم — هندسة Z.ai Agent / GLM (407 كتل · NEW 02/10)", "focus": "secondary"},
}

# §19 channel registry (governing channel/handle list — PMRF §34.3)
CH19 = {
    "gemini12pro_channel": "قناة", "gemini12pro_bot": "بوت", "ProdSellerOfficial": "قناة",
    "learnwith_Alex": "قناة", "Evo_Era_updates": "قناة", "stackvault.shop": "متجر",
    "HitMeowShop": "قناة/متجر", "AISUBSID": "قناة", "verifierg": "قناة", "gemini12pro": "قناة/بوت",
    "ProdSellerBot": "بوت", "Bite_storee_bot": "بوت", "Mike_E_0": "بوت", "acczone_gemini_link_bot": "بوت",
    "acczone_logs": "بوت", "Acczone_Store_bot": "بوت", "VeirfyerSupportbot": "بوت", "Veriyferbot": "بوت",
    "Evolution_Era_bot": "بوت", "stackvault_support": "بوت دعم", "stackvault_bot": "بوت",
    "PremiKeyBot": "بوت", "Premikey_bot": "بوت", "HitmeowSupport": "بوت دعم", "insightXpro_bot": "بوت",
    "nevakeystore_bot": "بوت", "Gamisellbot": "بوت", "p_a_store_bot": "بوت", "storeBatmanBot": "بوت",
    "Aisubsglobalbot": "بوت",
}
# known project brand tokens (case-insensitive substring match)
KNOWN_BRANDS = ["prodseller", "stackvault", "hitmeow", "acczone", "aisubsid", "aisubs",
                "evo_era", "evolution era", "evolutionera", "teamsoclo", "tokensunlimited",
                "gemini12pro", "eneba", "turgame", "gg sel", "ggsel", "kinguin", "g2a",
                "z2u", "allkeyshop", "cdkeys", "royalcdkeys", "storebatman", "gamisell",
                "nevakey", "premikey", "premikey", "insightxpro", "verifierg", "veriyfer",
                "reloadly", "fazercards", "keyforsteam", "cjs cd keys", "dolaa"]

PRICE_ANCHORS = [
    ("ChatGPT Plus — سلّم الكلفة (MEC-2.3): 2.80 → 10.67 → 17.14", ["2.80", "10.67", "17.14"]),
    ("معادلة البيع = الكلفة × 1.2 (MEC-2.3)", ["1.2x", "× 1.2", "x 1.2", "* 1.2", "×1.2"]),
    ("هرم الضمان: $4.50/ساعتين مقابل $8-10/3 أشهر", ["4.50", "4.5/2", "$8-10", "8–10", "$8–10"]),
]

def load_page(pid):
    return json.load(open("%s/pages/%s.json" % (NEW, pid), encoding="utf-8"))

def fulltext(pg):
    lines = [pg.get("title", "")]
    for b in pg.get("blocks", []):
        for t in (b.get("text") or []):
            if t and t.strip():
                lines.append(t.strip())
    return lines

def save(name, obj):
    with open("%s/%s" % (OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# ============ A) LOAD ============
loaded = {}
for key, meta in PAGES.items():
    pg = load_page(meta["id"])
    lines = fulltext(pg)
    loaded[key] = {"meta": meta, "page": pg, "lines": lines}
    with open("%s/extracted_fulltext/%s.txt" % (OUT, key), "w", encoding="utf-8") as f:
        f.write(meta["label"] + "\n" + "=" * 60 + "\n" + "\n".join(lines))
    print("loaded %-14s blocks=%-5d text-lines=%d" % (key, pg.get("block_count", 0), len(lines)))

# ============ B) REF_HAKIM deep structure ============
rh = loaded["REF_HAKIM"]["page"]
hist = collections.Counter(b.get("type") for b in rh.get("blocks", []))
headings = []
children_pages = []
for b in rh.get("blocks", []):
    t = b.get("type", "")
    txt = " ".join(b.get("text") or [])
    if t in ("heading_1", "heading_2", "heading_3") and txt:
        headings.append({"level": int(t[-1]), "text": txt[:120]})
    if t == "child_page" and txt:
        children_pages.append(txt[:100])

old_lines = [l.strip() for l in open(OLD_TEXT, encoding="utf-8").read().splitlines() if l.strip()]
new_lines = loaded["REF_HAKIM"]["lines"]
old_set = set(old_lines); new_set = set(new_lines)
added = [l for l in new_lines if l not in old_set and l != loaded["REF_HAKIM"]["page"].get("title", " ")]
removed = [l for l in old_lines if l not in new_set and l != old_lines[0]]
ref_structure = {
    "page": PAGES["REF_HAKIM"]["label"],
    "block_count": rh.get("block_count"),
    "block_type_histogram": dict(hist.most_common()),
    "headings_count": len(headings),
    "headings_first_60": headings[:60],
    "child_page_blocks_count": len(children_pages),
    "child_page_blocks": children_pages,
    "diff_vs_2609": {"old_text_lines": len(old_lines), "new_text_lines": len(new_lines),
                      "added_lines_count": len(added), "removed_lines_count": len(removed),
                      "added_sample_80": added[:80], "removed_sample_20": removed[:20],
                      "method_note": "فرق أسطر نصية (وليس فرق كتل) — التقاط 26/09 قديم والتقاط 02/10 بعد تحرير 27/09؛ الأسطر المضافة تشمل مراجع الصفحات الابنة الجديدة (نتائج MEC) وأي callouts"},
}
save("ref_hakim_structure.json", ref_structure)
print("\nREF_HAKIM: types=%s | headings=%d | child_pages=%d | added_lines=%d removed=%d" %
      (dict(hist.most_common(5)), len(headings), len(children_pages), len(added), len(removed)))

# ============ C) Entity extraction + cross-ref ============
# registries
reg_main = json.load(open("/home/z/my-project/research/entity_registry.json", encoding="utf-8"))["entities"]
reg_gds = json.load(open("/home/z/my-project/download/gds_qualified_entities.json", encoding="utf-8"))["entities"]
gds_names = {e.get("Brand_Name", "").lower(): e.get("Entity_ID") for e in reg_gds if e.get("Brand_Name")}
gds_domains = {e.get("Official_Domain", "").lower().replace("www.", ""): e.get("Entity_ID") for e in reg_gds if e.get("Official_Domain")}
main_names = {e["name"].lower(): e for e in reg_main}
main_domains = {e.get("domain", "").lower(): e["name"] for e in reg_main if e.get("domain")}
# multi-name registry entries (e.g. "Kinguin / G2A / Z2U ...") explode
for n in list(main_names):
    for part in n.split("/"):
        if part.strip(): main_names.setdefault(part.strip().lower(), main_names[n])

handle_re = re.compile(r"(?:t\.me/|@)([A-Za-z0-9_]{3,64})", re.IGNORECASE)
url_re = re.compile(r"(?:https?://)?(?:www\.)?([A-Za-z0-9][A-Za-z0-9-]{1,60}\.(?:com|net|io|org|shop|me|dev|app|xyz|pro|store|site|online|co|ai|gg|to|ru|in|tr)(?:/[^\s\u0600-\u06FF\"')\]]*)?)", re.IGNORECASE)

def classify_mention(handle=None, domain=None, brand=None):
    """Return classification for an extracted mention."""
    if handle:
        h = handle.lower().rstrip("/")
        if h in CH19: return ("KNOWN_S19", CH19[h])
        # brand-ish handles also match known brands
    if domain:
        d = domain.lower().split("/")[0].replace("www.", "")
        if d in main_domains: return ("KNOWN_REGISTRY", main_domains[d])
        if d in gds_domains: return ("KNOWN_GDS", gds_domains[d])
        if any(b in d for b in KNOWN_BRANDS): return ("KNOWN_BRAND", d)
        return ("NEW_DOMAIN", d)
    if handle:
        hl = handle.lower()
        if any(b.replace(" ", "") in hl.replace("_", "") for b in KNOWN_BRANDS): return ("KNOWN_BRAND", hl)
        return ("NEW_HANDLE", hl)
    return ("UNKNOWN", "")

entity_report = {}
for key, obj in loaded.items():
    text = "\n".join(obj["lines"])
    found = collections.OrderedDict()
    for m in handle_re.finditer(text):
        h = m.group(1)
        cls, ref = classify_mention(handle=h)
        k = "@" + h
        if k not in found: found[k] = {"class": cls, "ref": ref, "source": key}
    for m in url_re.finditer(text):
        u = m.group(1)
        if any(x in u.lower() for x in ("notion.so", "app.notion", "t.me/")): continue
        cls, ref = classify_mention(domain=u)
        k = u if "/" in u else u.lower()
        if k.lower() not in {kk.lower() for kk in found}: found[k] = {"class": cls, "ref": ref, "source": key}
    # registry name mentions (substring search in full text)
    tl = text.lower()
    for nm in main_names:
        if nm in tl and len(nm) > 3:
            k = nm
            if not any(k.lower() == kk.lower().lstrip("@") for kk in found):
                found[k] = {"class": "KNOWN_REGISTRY_MENTION", "ref": main_names[nm].get("name"), "source": key}
    entity_report[key] = {"label": obj["meta"]["label"], "mentions": found}
    counts = collections.Counter(v["class"] for v in found.values())
    print("entities %-14s: %s" % (key, dict(counts)))
save("entities_crossref.json", entity_report)

# ============ D) Price extraction + G-12 anchors ============
price_re = re.compile(
    r"(\$|USD\s?|دولار|ر\.س|ريال|SAR)\s?(\d{1,5}(?:[.,]\d{1,3})?)|(\d{1,5}(?:[.,]\d{1,3})?)\s?(دولار|ر\.س|ريال|USD|\$)", re.UNICODE)

def ctx(lines, idx, w=1):
    return " … ".join(l[:90] for l in lines[max(0, idx - w):idx + w + 1])

price_report = {}
for key, obj in loaded.items():
    hits = []
    lines = obj["lines"]
    for i, l in enumerate(lines):
        for m in price_re.finditer(l):
            val = m.group(2) or m.group(3)
            cur = (m.group(1) or m.group(4) or "").strip()
            hits.append({"value": val, "currency": cur, "context": ctx(lines, i)})
    # anchors
    tl = " ".join(lines)
    anchors = []
    for label, pats in PRICE_ANCHORS:
        matched = [p for p in pats if p in tl]
        anchors.append({"anchor": label, "patterns_found": matched,
                        "verdict": "PRESENT" if matched else "ABSENT"})
    price_report[key] = {"label": obj["meta"]["label"], "price_mentions_count": len(hits),
                          "price_mentions_sample_60": hits[:60], "anchors": anchors}
    print("prices %-14s: mentions=%d | anchors: %s" %
          (key, len(hits), [a["verdict"] for a in anchors]))
save("prices_reconciliation.json", price_report)

# ============ E) Summary ============
summary = {
    "operation": "G-14 detailed Notion delta reconciliation",
    "generated": "2026-10-02",
    "focus_pages": {k: {"id": v["meta"]["id"], "blocks": loaded[k]["page"].get("block_count"),
                         "text_lines": len(loaded[k]["lines"])} for k, v in loaded.items()},
    "ref_hakim": {"block_count": rh.get("block_count"), "heading_count": len(headings),
                   "child_pages": len(children_pages),
                   "added_lines_vs_2609": len(added), "removed_lines_vs_2609": len(removed)},
    "next": "تحليل النتائج وكتابة التقرير التفصيلي + طبقة PMRF v3.2",
}
save("00_summary.json", summary)
print("\noutputs ->", OUT)
