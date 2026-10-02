#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — RELEASE SEAL (توجيه §35)
1. Hash the assembled master (content before seal)
2. Append the Release Seal block at end of §48
3. Hash the final file (record for worklog/report)
"""
import hashlib, os, json
from datetime import datetime, timezone, timedelta

ROOT = "/home/z/my-project"
TARGET = os.path.join(ROOT, "download", "PROJECT MASTER REFERENCE FILE.md")
TZ = timezone(timedelta(hours=3))

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

pre_seal = sha(TARGET)
pre_bytes = os.path.getsize(TARGET)
seal_ts = datetime.now(TZ).isoformat(timespec="seconds")

seal_block = f"""
### 48.3 Release Seal

| الحقل | القيمة |
|---|---|
| Filename | PROJECT MASTER REFERENCE FILE.md |
| Release version | **PMRF v3.0** |
| Generation timestamp | 2026-10-02T07:47:03+03:00 (التجميع النهائي بعد التصحيحات) |
| Verification timestamp | {seal_ts} (بوابات التدقيق الأربع + إعادة البناء 19/19 + التتبع 50 مسارًا/0 مفقود) |
| SHA-256 (المحتوى قبل هذا الختم) | `{pre_seal}` |
| حجم المحتوى المختوم | {pre_bytes:,} bytes (1,175 سطرًا) |
| Canonical status | **CANONICAL PROJECT MASTER REFERENCE** (قرار §46.5 — الحدود العشرة مصرحة في §45) |
| الأرشيف المحفوظ | v1.5 (sha 486a2502e4ab4a3c…) + v2.0 (sha e58b326e00375dd9…) في PMRF_ARCHIVE/ |

**قاعدة الختم:** هذا الختم يغطي المحتوى السابق له حصرًا. أي تعديل لاحق يستوجب إصدارًا جديدًا وختمًا جديدًا — لا يُحدَّث هذا الختم.
"""

with open(TARGET, "a", encoding="utf-8") as f:
    f.write(seal_block)

final_hash = sha(TARGET)
final_bytes = os.path.getsize(TARGET)
final_lines = sum(1 for _ in open(TARGET, encoding="utf-8"))

record = {
    "seal_appended_at": seal_ts,
    "pre_seal_sha256": pre_seal,
    "pre_seal_bytes": pre_bytes,
    "final_sha256": final_hash,
    "final_bytes": final_bytes,
    "final_lines": final_lines,
    "canonical_status": "CANONICAL PROJECT MASTER REFERENCE",
}
json.dump(record, open(os.path.join(ROOT, "research", "pmrf_v3_build", "seal.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(record, ensure_ascii=False, indent=1))
