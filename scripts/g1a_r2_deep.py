#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1a R2 — deep follow-up: crt.sh, og:image harvest, SPA JS bundle analysis, TG-ID grep
Passive only. Output: research/g1a_r2_deep_20261002.json + images/
"""
import json, ssl, re, time, os, glob
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

OUT = "/home/z/my-project/research/g1a_r2_deep_20261002.json"
IMGDIR = "/home/z/my-project/research/g1a_media"
os.makedirs(IMGDIR, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=30, raw=False, headers=None):
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    try:
        with urlopen(Request(url, headers=h), timeout=timeout, context=CTX) as r:
            data = r.read()
            return {"ok": True, "status": r.status, "final_url": r.url,
                    "body": data if raw else data.decode("utf-8", "replace")}
    except HTTPError as e:
        return {"ok": False, "status": e.code, "error": str(e)}
    except Exception as e:
        return {"ok": False, "status": 0, "error": repr(e)}

def jfetch(url, timeout=30):
    r = fetch(url, timeout)
    if r.get("ok"):
        try: return {"ok": True, "data": json.loads(r["body"])}
        except Exception as e: return {"ok": False, "error": f"json:{e}", "raw": r["body"][:400]}
    return r

res = {"run": "G-1a R2", "ts": datetime.now(timezone.utc).isoformat(), "sections": {}}
S = res["sections"]

# ---------- 1. crt.sh (retry, no exclude param) ----------
S["crtsh"] = jfetch("https://crt.sh/?q=%25.prodseller.com&output=json", timeout=60)
if not S["crtsh"].get("ok"):
    S["crtsh2"] = jfetch("https://crt.sh/?q=prodseller.com&output=json", timeout=60)

# ---------- 2. Telegram og:image harvest ----------
S["tg_images"] = {}
tg_pages = {}
for h in ["sookbit", "ProdsellerSupport", "prodsellerbot", "ProdSellerOfficial"]:
    r = fetch(f"https://t.me/{h}", timeout=20)
    tg_pages[h] = r
    if r.get("ok"):
        m = re.search(r'<meta property="og:image"[^>]*content="([^"]*)"', r["body"])
        m2 = re.search(r'<meta property="og:description"[^>]*content="([^"]*)"', r["body"])
        S["tg_images"][h] = {"image": m.group(1) if m else None,
                             "desc": m2.group(1) if m2 else None}
    time.sleep(0.6)

# download images
downloaded = {}
for h, info in S["tg_images"].items():
    if info.get("image"):
        r = fetch(info["image"], timeout=25, raw=True)
        if r.get("ok"):
            ext = ".jpg"
            path = f"{IMGDIR}/tg_{h}{ext}"
            with open(path, "wb") as f: f.write(r["body"])
            downloaded[h] = {"path": path, "bytes": len(r["body"])}
        time.sleep(0.6)
S["downloaded_images"] = downloaded

# ---------- 3. SPA JS bundle analysis ----------
S["spa"] = {}
root = fetch("https://prodseller.com/", timeout=25)
if root.get("ok"):
    scripts = re.findall(r'src="([^"]+\.js)"', root["body"])
    S["spa"]["scripts"] = scripts
    alljs = ""
    for sc in scripts[:8]:
        url = sc if sc.startswith("http") else "https://prodseller.com" + (sc if sc.startswith("/") else "/" + sc)
        jr = fetch(url, timeout=30)
        if jr.get("ok"):
            alljs += jr["body"]
            time.sleep(0.4)
    S["spa"]["js_total_chars"] = len(alljs)
    if alljs:
        emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}", alljs)))
        tgrefs = sorted(set(re.findall(r"t\.me/([A-Za-z0-9_]+)", alljs)))
        phones = sorted(set(re.findall(r"\+33[\s\d.-]{8,16}", alljs)))
        # interesting route names
        routes = sorted(set(re.findall(r"path:\s*[\"']([^\"']{1,40})[\"']", alljs)))[:80]
        titles = sorted(set(re.findall(r"title:\s*[\"']([^\"']{3,50})[\"']", alljs)))[:60]
        S["spa"].update({"emails": emails, "tg_refs": tgrefs, "phones_fr": phones,
                          "angular_routes": routes, "titles": titles})
        # search for VN indicators
        vn_words = [w for w in ["Vietnam", "vietnam", "Viet Nam", "Tieng", "Tiếng", "Nha Trang", "Ho Chi Minh", "Ha Noi"] if w in alljs]
        S["spa"]["vn_markers"] = vn_words
        # api endpoints
        eps = sorted(set(re.findall(r"[\"'](/api/[A-Za-z0-9/_-]{2,40})[\"']", alljs)))[:80]
        S["spa"]["api_paths"] = eps
        # save trimmed js for manual inspection
        with open(f"{IMGDIR}/prodseller_admin_bundle.txt", "w", encoding="utf-8") as f:
            f.write(alljs[:300000])

# ---------- 4. api-docs body ----------
ad = fetch("https://prodseller.com/api-docs/", timeout=25)
if ad.get("ok"):
    body = ad["body"]
    emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}", body)))
    contacts = sorted(set(re.findall(r"(?:contact|Contact)[^<>{}]{0,120}", body)))[:20]
    S["api_docs"] = {"emails": emails, "contact_strings": contacts[:20],
                      "len": len(body)}

# ---------- 5. Wayback retries (longer timeout) ----------
S["wayback"] = {}
try:
    S["wayback"]["cdx"] = jfetch("https://web.archive.org/cdx/search/cdx?url=prodseller.com&output=json&limit=60", timeout=60)
except Exception as e:
    S["wayback"]["cdx"] = {"error": repr(e)}
try:
    S["wayback"]["cdx_ip"] = jfetch("https://web.archive.org/cdx/search/cdx?url=51.77.244.194&output=json&limit=60", timeout=60)
except Exception as e:
    S["wayback"]["cdx_ip"] = {"error": repr(e)}

# ---------- 6. Grep archived research for TG IDs ----------
S["tg_id_grep"] = {}
ids = {"sookbit_id": "5574095571", "support_id": "8848514093"}
for label, tid in ids.items():
    hits = []
    for path in glob.glob("/home/z/my-project/research/**/*.json", recursive=True) + \
                glob.glob("/home/z/my-project/research/**/*.html", recursive=True):
        try:
            content = open(path, encoding="utf-8", errors="ignore").read()
            if tid in content:
                # capture context
                idxs = [m.start() for m in re.finditer(re.escape(tid), content)][:3]
                ctx = [content[max(0,i-120):i+120].replace("\n"," ") for i in idxs]
                hits.append({"file": path.replace("/home/z/my-project/", ""), "contexts": ctx})
        except Exception: pass
    S["tg_id_grep"][label] = hits

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1, default=str)

# ===== summary =====
print("=== crt.sh ===")
for key in ("crtsh", "crtsh2"):
    c = S.get(key, {})
    if c.get("ok") and isinstance(c.get("data"), list):
        names = set()
        for row in c["data"]:
            for n in str(row.get("name_value", "")).split("\n"):
                names.add(n.strip())
        print(f" {key}: {len(c['data'])} rows")
        for n in sorted(names): print("   -", n)
        break
    elif c:
        print(f" {key}:", str(c)[:150])

print("\n=== tg og:images ===")
for h, info in S.get("tg_images", {}).items():
    print(f" @{h}: {str(info.get('image'))[:90]} | desc: {str(info.get('desc'))[:100]}")
print(" downloaded:", S.get("downloaded_images"))

print("\n=== SPA ===")
spa = S.get("spa", {})
for k in ["scripts", "js_total_chars", "emails", "tg_refs", "phones_fr", "vn_markers", "api_paths"]:
    print(f" {k}: {str(spa.get(k))[:300]}")
print(" routes:", str(spa.get("angular_routes"))[:400])
print(" titles:", str(spa.get("titles"))[:300])

print("\n=== api-docs ===", str(S.get("api_docs"))[:400])
print("\n=== wayback ===", str(S.get("wayback"))[:400])
print("\n=== TG ID grep ===")
for label, hits in S.get("tg_id_grep", {}).items():
    print(f" {label}: {len(hits)} file hits")
    for h in hits[:5]:
        print("   file:", h["file"])
        for c in h["contexts"][:1]: print("    ctx:", c[:200])
print("\nSaved:", OUT)
