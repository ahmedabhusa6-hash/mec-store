#!/usr/bin/env python3
"""Filter Notion index → isolate Supplier Intelligence project cluster + match the 33 expected pages."""
import json, re, unicodedata
from collections import defaultdict

IDX = "/home/z/my-project/scripts/notion/index.json"
with open(IDX, encoding="utf-8") as f:
    index = json.load(f)

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D\u2B00-\u2BFF]")

def norm(s):
    s = EMOJI_RE.sub("", s)
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u2014", "-").replace("\u2013", "-").replace("–", "-").replace("—", "-")
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("مصدر - ", "").replace("مصدر-", "")
    return s

EXPECTED = [
    ("DB", "مرجع حاكم — قاعدة بيانات أرخص موردي ومتاجر المنتجات والخدمات الرقمية"),
    ("PG", "Supplier Intelligence Prompt Lab — ChatGPT × Claude × Final Reference"),
    ("PG", "Prompt Development History — Supplier Intelligence"),
    ("PG", "معجم البحث العميق والمتعدد المسارات — Supplier Discovery Lexicon"),
    ("PG", "المواصفة التشغيلية — البحث العميق العالمي عن الموردين ومصادرهم"),
    ("PG", "global_digital_products_database"),
    ("PG", "Canonical Registry — Prompt & Evolution"),
    ("DB", "Version Registry — Supplier Intelligence Prompts"),
    ("DB", "Decision Log — Supplier Intelligence"),
    ("DB", "Interaction Archive — Supplier Intelligence"),
    ("PG", "Operating Protocol — Notion-First ChatGPT ↔ Claude Relay"),
    ("PG", "ChatGPT Workspace — Review & Analysis"),
    ("PG", "Claude Sonnet 5 Workspace — Research & Drafts"),
    ("PG", "DEC — Establish ChatGPT / Claude / Canonical three-space governance"),
    ("PG", "DEC — Explicit ChatGPT Claude Edit Boundaries"),
    ("PG", "DEC — Project-Scope Notion Working Authorization"),
    ("PG", "DEC — Approved Separation of Supplier Intelligence Prompt Layers"),
    ("PG", "DEC — Product & Service Scope Clarification for Supplier Intelligence"),
    ("PG", "Bootstrap approval gate when no Approved Prompt exists"),
    ("PG", "v4.0 — Current Baseline Candidate"),
    ("PG", "v4.1 — Pre-Claude Repair Candidate"),
    ("PG", "v4.1 Candidate — Exact Prompt Text"),
    ("PG", "v4.2 — Catalog/Batch Architecture Candidate"),
    ("PG", "Pre-Claude Repair Audit — v4.0 → v4.1"),
    ("PG", "Cycle 1 — User Request"),
    ("PG", "Cycle 1 — ChatGPT Analysis & Pre-Claude Decision"),
    ("PG", "Cycle 1 — Claude Handoff — v4.1 Independent Validation"),
    ("PG", "Cycle 1 — Claude Response — v4.1 Artifact Missing"),
    ("PG", "Cycle 2 — Claude Handoff — Full Project Brainstorm & Intelligence Extraction"),
    ("PG", "Cycle 2 — Claude Handoff — v4.1 Artifact-Verified"),
    ("PG", "Cycle 3 — Claude Handoff — Final Brainstorm + Repair-Controlled Boundaries"),
    ("PG", "Cycle 4 — z.ai Runtime Evidence — 400+ SKU Catalog / Batch Execution"),
    ("PG", "Cycle 5 — Claude Response — v4.1 Runtime Audit → v4.2 Candidate"),
]

all_pages = index["pages"]
all_dbs = index["databases"]

# --- 1. understand structure: group by parent prefix
def parent_key(p): return p["parent"].split(":")[1] if ":" in p["parent"] else p["parent"]
groups = defaultdict(lambda: {"pages": [], "dbs": []})
for p in all_pages:
    groups[parent_key(p)]["pages"].append(p)
for d in all_dbs:
    groups[parent_key(d)]["dbs"].append(d)

print("=== STRUCTURE: parent-cluster sizes ===")
for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]["pages"]) - len(kv[1]["dbs"])):
    print("cluster %s : %d pages, %d dbs" % (k, len(v["pages"]), len(v["dbs"])))

# --- 2. match expected list
print("\n=== MATCH: 33 expected items vs index ===")
matches = []
used = set()
for kind, title in EXPECTED:
    nt = norm(title)
    found = None
    pool = all_dbs if kind == "DB" else all_pages
    # pass 1: strong containment either way
    for item in pool:
        ni = norm(item["title"])
        if not ni or item["id"] in used:
            continue
        if nt in ni or ni in nt:
            found = item; break
    # pass 2: relaxed — compare significant token overlap
    if not found:
        toks = set(re.findall(r"[a-z0-9\u0600-\u06FF]{3,}", nt))
        best, best_score = None, 0.0
        for item in pool:
            ni = norm(item["title"])
            if not ni or item["id"] in used:
                continue
            itoks = set(re.findall(r"[a-z0-9\u0600-\u06FF]{3,}", ni))
            if not toks or not itoks:
                continue
            score = len(toks & itoks) / max(1, min(len(toks), len(itoks)))
            if score > best_score and score >= 0.6:
                best, best_score = item, score
        found = best
    if found:
        used.add(found["id"])
        matches.append({"expected": title, "kind": kind, "id": found["id"],
                        "title": found["title"], "url": found["url"],
                        "parent": found["parent"], "edited": found.get("last_edited", "")})
        print("OK   [%s] %s\n     → id=%s | parent=%s | edited=%s" % (kind, title[:70], found["id"][:8], found["parent"], found.get("last_edited", "")))
    else:
        matches.append({"expected": title, "kind": kind, "id": None})
        print("MISS [%s] %s" % (kind, title[:80]))

# --- 3. unmatched pages inside supplier cluster (parent of Decision Log etc.)
supplier_parents = set()
for m in matches:
    if m.get("id") and m.get("parent", "").startswith("page:"):
        supplier_parents.add(m["parent"].split(":")[1])
print("\nSupplier-cluster parent prefixes:", supplier_parents)

print("\n=== UNMATCHED objects inside supplier clusters ===")
for pp in supplier_parents:
    for p in all_pages:
        if parent_key(p) == pp and p["id"] not in used:
            print("PAGE * %s (edited %s)" % (p["title"][:100], p.get("last_edited", "")))
    for d in all_dbs:
        if parent_key(d) == pp and d["id"] not in used:
            print("DB   * %s (edited %s)" % (d["title"][:100], d.get("last_edited", "")))

with open("/home/z/my-project/scripts/notion/matches.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=1)
print("\nSaved matches.json — matched %d/%d" % (sum(1 for m in matches if m.get("id")), len(EXPECTED)))
