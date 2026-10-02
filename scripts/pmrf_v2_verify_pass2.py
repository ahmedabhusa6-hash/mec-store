#!/usr/bin/env python3
"""
PMRF v2.0 — corrected second-pass checks + live catalog delta (282→280).
Outputs: research/pmrf_v2_evidence_audit2_20261002.json (checks)
         research/pmrf_v2_live_delta_20261002.json (catalog diff)
"""
import json, datetime, re
import urllib.request, ssl
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path("/home/z/my-project")
TZ = datetime.timezone(datetime.timedelta(hours=3))
TS = datetime.datetime.now(TZ).isoformat(timespec="seconds")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
      "Accept": "application/json, text/plain, */*",
      "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
      "Referer": "https://stackvault.shop/"}

checks = {"execution_timestamp": TS, "items": []}


def check(name, expected, result_value, ok, detail):
    checks["items"].append({"check": name, "expected": expected, "observed": result_value,
                            "result": "PASS" if ok else "FAIL", "detail": detail})


# 1. Scenario count — column C (الرمز), rows >= 5
wb = load_workbook(ROOT / "download/مصفوفة_حملة_التفاوض_2026-10-02.xlsx", read_only=True)
ws = wb["السيناريوهات"]
codes = []
for row in ws.iter_rows(min_row=5, min_col=3, max_col=3, values_only=True):
    v = row[0]
    if isinstance(v, str) and re.match(r"^S-[A-Z]\d+$", v.strip()):
        codes.append(v.strip())
sc_total = len(codes)
# per-party probability sums: column E (الاحتمال) grouped by column B (الطرف)
parties, probs = {}, {}
for row in ws.iter_rows(min_row=5, min_col=2, max_col=6, values_only=True):
    party, code, prob = row[0], row[1], row[4]
    if isinstance(code, str) and re.match(r"^S-[A-Z]\d+$", code.strip()):
        try:
            p = float(prob)
            probs[party] = probs.get(party, 0.0) + p
            parties[party] = parties.get(party, 0) + 1
        except (TypeError, ValueError):
            pass
check("حملة التفاوض = 30 سيناريو (عمود الرمز)", 30, sc_total, sc_total == 30, {"codes": codes[:35]})
check("مجموع احتمالات كل طرف = 1.00", "4 parties x 1.00",
      {k: round(v, 3) for k, v in probs.items()},
      all(abs(v - 1.0) < 0.005 for v in probs.values()) and len(probs) >= 4,
      {"per_party_scenarios": parties})
wb.close()

# 2. docx 13 H1 sections (guarded)
import docx
d = docx.Document(ROOT / "download/دليل_حملة_التفاوض_الافتتاحية_2026-10-02.docx")
h1 = [p.text.strip()[:50] for p in d.paragraphs
      if p.style is not None and p.style.name == "Heading 1" and p.text.strip()]
check("دليل الحملة = 13 قسمًا (Heading 1)", 13, len(h1), len(h1) == 13, {"titles": h1})

# 3. Consolidated catalog accounting (v1.5 wording): 1,112 = entities only; +15 gateway = 1,127
cons = json.loads((ROOT / "research/sv_master_catalog_consolidated_20261002.json").read_text())
ent_counts = {}
for name, blk in cons["entities"].items():
    for k in ("products", "items", "catalog", "records"):
        if isinstance(blk.get(k), list):
            ent_counts[name] = len(blk[k])
            break
ent_sum = sum(ent_counts.values())
gw = len(cons.get("gateway", {}).get("products", []))
check("محاسبة الكتالوج الموحد", "entities 1112 (+15 gateway = 1127)",
      {"entities": ent_sum, "gateway": gw, "grand": ent_sum + gw},
      ent_sum == 1112, "v1.5 §4.1 وصف 1,112 بأنها «11 كيان + البوابة» — التصحيح: 1,112 = الكيانات فقط؛ البوابة +15 = 1,127")

# 4. PMRF v1.5 §1 version field vs header
pmrf_txt = (ROOT / "download/PROJECT MASTER REFERENCE FILE.md").read_text(encoding="utf-8")
sec1 = pmrf_txt.split("## 2.")[0]
m = re.search(r"\|\s*الإصدار\s*\|\s*\*\*(v[\d.]+)\*\*", sec1)
sec1_ver = m.group(1) if m else None
check("اتساق جدول الهوية §1 مع ترويسة v1.5", "v1.5", sec1_ver,
      sec1_ver == "v1.5",
      "إن كانت v1.4 → تعارض داخلي في v1.5 يُصحح في v2.0")

# ---------- live catalog delta ----------
def fetch_catalog():
    req = urllib.request.Request("https://decohomz.com/sv-api/products", headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
        return json.loads(r.read())

live = fetch_catalog()
products = live if isinstance(live, list) else live.get("products")
cur = {}
prefixes = {}
for p in products:
    pid = str(p.get("id", ""))
    m = re.match(r"^(cb_|ps_|mr_)", pid)
    key = m.group(1) if m else ("dummy/other" if not m else "?")
    prefixes[key] = prefixes.get(key, 0) + 1
    cur[pid] = {"name": p.get("name"), "price": p.get("price"), "stock": p.get("stock")}

arch = json.loads((ROOT / "research/g1_cb_live_catalog_20261002.json").read_text())
arch_products = arch["products"] if isinstance(arch, dict) else arch
prev = {str(p.get("id", "")): {"name": p.get("name"), "price": p.get("price")} for p in arch_products}

dropped = {k: prev[k] for k in prev if k not in cur}
added = {k: cur[k] for k in cur if k not in prev}
price_changed = {k: {"was": prev[k]["price"], "now": cur[k]["price"], "name": cur[k]["name"]}
                 for k in prev if k in cur and prev[k]["price"] != cur[k]["price"]}

witnesses = {}
for p in products:
    n = str(p.get("name", "")).lower()
    for w in ("chatgpt go", "plus 1m 3d", "chatgpt plus 1m", "grok", "capcut", "codex", "office", "canva", "duolingo", "adobe", "gemini"):
        if w in n and w not in witnesses:
            witnesses[w] = {"name": p.get("name"), "price": p.get("price"), "stock": p.get("stock"), "id": str(p.get("id"))[:24]}

delta = {
    "execution_timestamp": TS,
    "endpoint": "https://decohomz.com/sv-api/products",
    "http_total_now": len(products),
    "http_total_prev_witness": 282,
    "prefix_distribution_now": prefixes,
    "prefix_distribution_prev": {"cb_": 229, "ps_": 20, "mr_": 32, "dummy/other": 1},
    "dropped_since_0210_scan": dropped,
    "added_since_0210_scan": added,
    "price_changed_since_0210_scan": price_changed,
    "price_witnesses_now": witnesses,
    "cost_field_present": any("cost" in str(k).lower() for k in products[0].keys()) if products else None,
}
(ROOT / "research/pmrf_v2_live_delta_20261002.json").write_text(json.dumps(delta, ensure_ascii=False, indent=1), encoding="utf-8")
checks["live_catalog_delta_summary"] = {
    "total": len(products), "prefixes": prefixes,
    "dropped": list(dropped.keys()), "added": list(added.keys()),
    "n_price_changed": len(price_changed), "cost_field": delta["cost_field_present"],
}

(ROOT / "research/pmrf_v2_evidence_audit2_20261002.json").write_text(json.dumps(checks, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(checks, ensure_ascii=False, indent=1))
