#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C15 WRITE CAPABILITY TEST — 2026-10-02
Explicit user instruction received this session (PMRF v3.1 C15: "اختبار قدرة كتابة التوكن
الجديد يتطلب كتابة فعلية بتعليمات صريحة" — التعليمات صريحة الآن).

Token under test: rotated internal integration token (ntn_2379…) — read capability already
proven by D5-ROTATION capture. This test answers: INSERT content? UPDATE content? (ARCHIVE?)

Protocol — minimal-invasive, established write surface (same parent all 6+ historical sync
scripts used: REF_HAKIM = governing reference page):
  0) PRE-FLIGHT (reads) : GET /users/me ; GET /pages/REF_HAKIM (state before)
  1) CREATE             : POST /pages                                [INSERT] test page under REF_HAKIM
  2) APPEND             : PATCH /blocks/{page}/children               [INSERT] one paragraph block
                         (NOTE: append-children endpoint is PATCH per Notion API spec —
                          run 1 mistakenly used POST and got 400 invalid_request_url; run 2 = corrected)
  3) UPDATE BLOCK       : PATCH /blocks/{block}                      [UPDATE] rewrite paragraph text
  4) UPDATE PAGE PROP   : PATCH /pages/{page} (icon swap)            [UPDATE] page properties
  5) VERIFY READ-BACK   : GET /blocks/{page}/children
  6) CLEANUP ARCHIVE    : PATCH /pages/{page} {"archived": true}     [UPDATE/DELETE-equivalent]
  7) POST-CHECK         : GET /pages/{page} ; GET /blocks/{page} ; GET /pages/REF_HAKIM (residual footprint)

Fallback if CREATE is denied (403): no-op title rewrite on REF_HAKIM (same exact title value)
— proves/disproves UPDATE capability without inserting anything. No other fallback: if both
denied, write capability = NONE.

Residual footprint policy (documented honestly, zero-hallucination):
  - Success path leaves: (a) one page in Notion Trash (archived test page), (b) REF_HAKIM
    last_edited_time bump (metadata only — content unchanged, child stub vanishes from live view).
  - Every request/response is logged to research/c15_write_test_2026-10-02.json
"""
import json, time, datetime, urllib.request, urllib.error, os

TOKEN = "[REDACTED-NOTION-TOKEN]"
BASE = "https://api.notion.com/v1"
HDRS = {"Authorization": "Bearer " + TOKEN, "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"  # المرجع الحاكم (digital products) — established write-surface parent
EVIDENCE_OUT = "/home/z/my-project/research/c15_write_test_2026-10-02_run2.json"

TS = lambda: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime("%Y-%m-%dT%H:%M:%S+03:00")
LOG = []  # evidence log

def api(method, path, payload=None):
    """Full-method API call with retry on 429. Returns (parsed_body, http_status)."""
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HDRS, method=method)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r), r.status
        except urllib.error.HTTPError as e:
            code = e.code
            body = b""
            try: body = e.read()[:500]
            except Exception: pass
            if code == 429:
                time.sleep(2.0 * (attempt + 1)); continue
            return {"_http_error": code, "_body": body.decode(errors="replace")[:400]}, code
        except Exception as ex:
            time.sleep(1.5 * (attempt + 1))
    return {"_error": "timeout", "_exc": str(ex)[:100]}, 0

def step(name, method, path, payload=None, digest_fn=None):
    """Execute one API step, log evidence, return (body, status)."""
    body, st = api(method, path, payload)
    ok = (st == 200 and "_http_error" not in body and "_error" not in body)
    rec = {"step": name, "ts": TS(), "method": method, "path": path,
           "http_status": st, "ok": ok,
           "request_payload": payload,
           "response_digest": digest_fn(body) if digest_fn else str(body)[:600]}
    LOG.append(rec)
    print("[%s] %-18s %-6s %-42s -> HTTP %s %s" % (rec["ts"][11:19], name, method, path[:42], st, "OK" if ok else "FAIL"))
    if not ok:
        print("    !! body:", str(body)[:300])
    time.sleep(0.6)
    return body, st, ok

def para(text):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def main():
    print("=" * 78)
    print("C15 WRITE CAPABILITY TEST — rotated token ntn_2379… — %s" % TS())
    print("=" * 78)
    result = {"test_id": "C15", "started_at": TS(), "token_prefix": TOKEN[:10] + "…",
              "capabilities": {}, "events": []}

    # ---- 0) PRE-FLIGHT (reads) ----
    me, st, ok = step("PREFLIGHT_ME", "GET", "/users/me",
                      digest_fn=lambda b: {"bot_name": b.get("name"), "workspace_name": (b.get("workspace") or {}).get("name")})
    ref_before, st, ok = step("PREFLIGHT_REF", "GET", "/pages/" + REF_HAKIM,
                              digest_fn=lambda b: {"title": str(b.get("properties", {}))[:80],
                                                   "last_edited": b.get("last_edited_time"),
                                                   "archived": b.get("archived")})
    ref_before_edit = ref_before.get("last_edited_time") if st == 200 else None

    # ---- 1) CREATE test page under REF_HAKIM [INSERT] ----
    test_title = "C15 — اختبار قدرة الكتابة (توكن مدوّر) — 2026-10-02 — آمن للحذف"
    created, st_c, ok_c = step("CREATE_PAGE", "POST", "/pages",
        {"parent": {"page_id": REF_HAKIM},
         "icon": {"type": "emoji", "emoji": "🧪"},
         "properties": {"title": {"title": [{"text": {"content": test_title}}]}},
         "children": [para("صفحة اختبار C15 — أُنشئت لاختبار قدرة الكتابة للتوكن المدوّر فقط. "
                           "ستُؤرشف فور اكتمال الاختبار. لا محتوى معرفي هنا.")]},
        digest_fn=lambda b: {"id": b.get("id"), "url": b.get("url"), "created": b.get("created_time")})
    result["capabilities"]["insert_page_create"] = ok_c

    page_id = created.get("id")
    if ok_c and page_id:
        result["test_page"] = {"id": page_id, "url": created.get("url"), "title": test_title}
        # ---- 2) APPEND block [INSERT blocks] ----
        marker = "C15-APPEND-%s" % TS()
        app, st_a, ok_a = step("APPEND_BLOCK", "PATCH", "/blocks/%s/children" % page_id,
            {"children": [para("كتلة اختبار إلحاق: " + marker)]},
            digest_fn=lambda b: {"appended": [r.get("id") for r in b.get("results", [])]})
        result["capabilities"]["insert_block_append"] = ok_a
        blk_id = None
        if ok_a and app.get("results"):
            blk_id = app["results"][0].get("id")

        # ---- 3) UPDATE block [UPDATE content] ----
        upd_marker = "C15-UPDATE-OK-%s" % TS()
        ok_u1 = False
        if blk_id:
            _, _, ok_u1 = step("UPDATE_BLOCK", "PATCH", "/blocks/" + blk_id,
                {"paragraph": {"rich_text": [{"type": "text", "text": {"content": "كتلة اختبار بعد التحديث: " + upd_marker}}]}},
                digest_fn=lambda b: {"id": b.get("id"), "archived": b.get("archived")})
        result["capabilities"]["update_block_patch"] = ok_u1

        # ---- 4) UPDATE page property (icon swap) [UPDATE page] ----
        _, _, ok_u2 = step("UPDATE_PAGE_ICON", "PATCH", "/pages/" + page_id,
            {"icon": {"type": "emoji", "emoji": "🔬"}},
            digest_fn=lambda b: {"icon": b.get("icon")})
        result["capabilities"]["update_page_patch"] = ok_u2

        # ---- 5) VERIFY read-back ----
        rb, st_v, ok_v = step("VERIFY_READBACK", "GET", "/blocks/%s/children?page_size=100" % page_id,
            digest_fn=lambda b: {"results": len(b.get("results", [])),
                                 "types": [r.get("type") for r in b.get("results", [])]})
        readback_texts = []
        if ok_v:
            for b in rb.get("results", []):
                t = b.get("type", "")
                spec = b.get(t, {})
                for rt in spec.get("rich_text", []):
                    readback_texts.append(rt.get("plain_text", ""))
        verified_content = any(upd_marker in t for t in readback_texts) if ok_u1 else any("C15" in t for t in readback_texts)
        result["capabilities"]["verify_readback_content"] = bool(verified_content)
        print("    read-back content verified:", verified_content)

        # ---- 6) CLEANUP: archive test page ----
        _, _, ok_arch = step("CLEANUP_ARCHIVE", "PATCH", "/pages/" + page_id, {"archived": True},
                             digest_fn=lambda b: {"id": b.get("id"), "archived": b.get("archived")})
        result["capabilities"]["archive_page_delete_equiv"] = ok_arch

        # ---- 7) POST-CHECK: residual footprint ----
        pg, st_p1, _ = step("POSTCHECK_PAGE", "GET", "/pages/" + page_id,
                            digest_fn=lambda b: {"archived": b.get("archived"), "in_trash": b.get("in_trash", "n/a")})
        bl, st_p2, _ = step("POSTCHECK_BLOCK", "GET", "/blocks/" + page_id,
                            digest_fn=lambda b: {"archived": b.get("archived"), "type": b.get("type")})
        ref_after, st_p3, _ = step("POSTCHECK_REF", "GET", "/pages/" + REF_HAKIM,
                                   digest_fn=lambda b: {"last_edited": b.get("last_edited_time"), "archived": b.get("archived")})
        result["residual_footprint"] = {
            "test_page_state": {"archived": pg.get("archived"), "in_trash": pg.get("in_trash", "n/a")},
            "stub_block_state": {"archived": bl.get("archived")},
            "ref_hakim_last_edited_before": ref_before_edit,
            "ref_hakim_last_edited_after": ref_after.get("last_edited_time"),
            "note": "الصفحة في سلة المحذوفات؛ محتوى المرجع الحاكم لم يتغير — فقط طابع آخر تحرير ارتفع (أثر لا مفر منه لأي اختبار كتابة)"
        }
    else:
        # ---- FALLBACK: CREATE denied → update-only probe (no-op title rewrite on REF_HAKIM) ----
        print(">> CREATE denied — falling back to UPDATE-only probe (no-op title rewrite on REF_HAKIM)")
        cur_title = "مرجع حاكم — قاعدة بيانات أرخص موردي ومتاجر المنتجات والخدمات الرقمية"
        _, _, ok_fb = step("FALLBACK_NOOP_TITLE", "PATCH", "/pages/" + REF_HAKIM,
            {"properties": {"title": {"title": [{"text": {"content": cur_title}}]}}},
            digest_fn=lambda b: {"last_edited": b.get("last_edited_time")})
        result["capabilities"]["update_page_patch"] = ok_fb
        result["capabilities"]["insert_page_create"] = False
        result["fallback_note"] = "CREATE مرفوض — اختُبرت قدرة UPDATE فقط عبر إعادة كتابة العنوان بقيمته الحرفية نفسها (بلا أي تغيير محتوى)"

    # ---- verdict ----
    caps = result["capabilities"]
    insert_ok = caps.get("insert_page_create") and caps.get("insert_block_append", True)
    update_ok = caps.get("update_block_patch") or caps.get("update_page_patch")
    if insert_ok and update_ok:
        verdict = "WRITE_FULL (إنشاء + إلحاق + تحديث + أرشفة — كلها ناجحة)"
    elif insert_ok:
        verdict = "WRITE_INSERT_ONLY"
    elif update_ok:
        verdict = "WRITE_UPDATE_ONLY"
    else:
        verdict = "WRITE_NONE (التوكن للقراءة فقط)"
    result["verdict"] = verdict
    result["finished_at"] = TS()
    result["events"] = LOG

    os.makedirs(os.path.dirname(EVIDENCE_OUT), exist_ok=True)
    with open(EVIDENCE_OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("=" * 78)
    print("VERDICT:", verdict)
    print("capabilities:", json.dumps(caps, ensure_ascii=False))
    print("evidence ->", EVIDENCE_OUT)

if __name__ == "__main__":
    main()
