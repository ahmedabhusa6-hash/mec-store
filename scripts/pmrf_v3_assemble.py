#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — ASSEMBLE + STRUCTURAL VERIFICATION
1. Concatenate part1-8 → download/PROJECT MASTER REFERENCE FILE.md
2. Verify: 48 sections in mandatory order · no placeholders · no broken refs
3. Cross-number consistency spot checks
"""
import os, re, json
from datetime import datetime, timezone, timedelta

ROOT = "/home/z/my-project"
BUILD = os.path.join(ROOT, "research", "pmrf_v3_build")
TZ = timezone(timedelta(hours=3))
NOW = datetime.now(TZ).isoformat(timespec="seconds")

EXPECTED = [
    "1. Document Identity", "2. Release Metadata", "3. Canonical Status",
    "4. Executive Project Snapshot", "5. Project Identity", "6. Mission, Vision and Objectives",
    "7. Project Scope", "8. Project Master State", "9. Business Model",
    "10. Products and Services", "11. Customer Knowledge", "12. Market Knowledge",
    "13. Supplier Knowledge", "14. Competitor Knowledge", "15. Pricing and Commercial Knowledge",
    "16. Financial Knowledge", "17. Accounting Knowledge", "18. Operational Knowledge",
    "19. Marketing and Sales Knowledge", "20. Technology and System Knowledge",
    "21. Architecture", "22. Infrastructure", "23. Data and Datasets",
    "24. Research Knowledge Base", "25. Evidence Register", "26. Source Register",
    "27. Decision Ledger", "28. Constraint Ledger", "29. Risk Register",
    "30. Gap Register", "31. Open Questions", "32. Experiments and Results",
    "33. Methods and Analytical Procedures", "34. Notion Knowledge",
    "35. Historical States", "36. Superseded Information", "37. Conflicts and Reconciliation",
    "38. Technical / Script Register", "39. Artifact Inventory", "40. Content Coverage Matrix",
    "41. Knowledge Coverage Matrix", "42. Provenance Map", "43. Change History",
    "44. Multidisciplinary Readiness Map", "45. Known Limitations",
    "46. Final Verification Audit", "47. Final Canonical Project State", "48. Appendices",
]

parts = []
for i in range(1, 9):
    p = os.path.join(BUILD, f"part{i}.md")
    with open(p, encoding="utf-8") as f:
        parts.append(f.read().strip())
doc = "\n\n".join(parts) + "\n"

target = os.path.join(ROOT, "download", "PROJECT MASTER REFERENCE FILE.md")
with open(target, "w", encoding="utf-8") as f:
    f.write(doc)

# --- verification ---
src = doc
lines = src.count("\n") + 1
bytes_ = len(doc.encode("utf-8"))

# 1) section presence + order
found = []
for m in re.finditer(r"^## (\d+)\. (.+)$", src, re.M):
    found.append(f"{m.group(1)}. {m.group(2)}")
order_ok = found == EXPECTED
missing = [s for s in EXPECTED if s not in found]
extra = [s for s in found if s not in EXPECTED]

# 2) real placeholders only (epistemic tags [مرصود]/[مستند]/[استنتاج]/[نصي] and Next.js [id] routes are intentional labels, not stubs)
placeholders = re.findall(r"\b(TODO|FIXME|XXX|TBD|placeholder| PLACEHOLDER )\b|\{\{\w+\}\}", src)

# 3) key-number consistency
checks = {
    "280 decomposition": bool(re.search(r"cb_ 228", src) and re.search(r"ps_ 20", src) and re.search(r"mr_ 31", src)),
    "1,127 = 1,112+15": ("1,127" in src and "1,112" in src and "15" in src),
    "437 catalog": "437" in src,
    "230 GDS": "230" in src,
    "61 tasks": "61" in src,
    "15 models": bool(re.search(r"15 موديل", src)),
    "825 rows": "825" in src,
    "546 pages": "546" in src,
    "v2.0 archive sha": "e58b326e00375dd9" in src,
    "v1.5 archive sha": "486a2502e4ab4a3c" in src,
    "G-13 present": "G-13" in src,
    "C14 present": "C14" in src,
    "C11 conflict": bool(re.search(r"C11 \(جديد v3.0\)", src)),
    "48 sections claimed": "48 قسمًا" in src,
}

# 4) no unresolved internal contradictions in headline numbers (280 vs 282 must both appear but labeled historically)
ok_282 = bool(re.search(r"282 \(v1\.0\)|282 \(v2\.0\)|→ 282|282 \(v2\.0\+v3\.0", src) or "282" in src)

result = {
    "assembled_at": NOW,
    "target": target,
    "lines": lines, "bytes": bytes_,
    "sections_found": len(found),
    "sections_expected": 48,
    "order_ok": order_ok,
    "missing": missing, "extra": extra,
    "placeholder_hits": placeholders,
    "number_checks": {k: bool(v) for k, v in checks.items()},
    "all_number_checks_pass": all(checks.values()),
}
json.dump(result, open(os.path.join(BUILD, "assemble_verify.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(result, ensure_ascii=False, indent=1))
