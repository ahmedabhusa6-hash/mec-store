#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1a R4 — Same-box confirmation + TLS SANs + decohomz front + full raw catalog
Passive/unauthenticated GETs + authorized reads. Output: research/g1a_r4_samebox_20261002.json
"""
import json, ssl, socket, re
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

OUT = "/home/z/my-project/research/g1a_r4_samebox_20261002.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def fetch(url, headers=None, timeout=25, limit=None):
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    try:
        r = urlopen(Request(url, headers=h), timeout=timeout, context=CTX)
        data = r.read(limit) if limit else r.read()
        return {"ok": True, "status": r.status, "headers": {k: v for k, v in r.headers.items()},
                "body": data.decode("utf-8", "replace")}
    except HTTPError as e:
        try: body = e.read(2000).decode("utf-8", "replace")
        except Exception: body = ""
        return {"ok": False, "status": e.code, "headers": dict(e.headers or {}), "body": body}
    except Exception as e:
        return {"ok": False, "status": 0, "error": repr(e)}

res = {"run": "G-1a R4 same-box", "ts": datetime.now(timezone.utc).isoformat()}

# ---------- 1. TLS certificate on 51.77.244.194 (SNI prodseller.com and none) ----------
certs = {}
for sni in ["prodseller.com", "decohomz.com", "stackvault.shop"]:
    try:
        s = socket.create_connection(("51.77.244.194", 443), timeout=15)
        w = CTX.wrap_socket(s, server_hostname=sni)
        der = w.getpeercert(binary_form=True)
        # decode via ssl.DER_cert_to_PEM + openssl-less parse: use _ssl _test_decode_cert
        import tempfile, os
        pem = ssl.DER_cert_to_PEM_cert(der)
        fd, path = tempfile.mkstemp(suffix=".pem")
        os.write(fd, pem.encode()); os.close(fd)
        dec = ssl._ssl._test_decode_cert(path)
        os.unlink(path)
        certs[sni] = {"subject": dec.get("subject"), "issuer": dec.get("issuer"),
                       "san": dec.get("subjectAltName"), "notBefore": dec.get("notBefore"),
                       "notAfter": dec.get("notAfter")}
        w.close()
    except Exception as e:
        certs[sni] = {"error": repr(e)}
res["tls_sni_test"] = certs
print("=== TLS on 51.77.244.194 ===")
for k, v in certs.items():
    print(f" SNI {k}:")
    print("   ", json.dumps(v, ensure_ascii=False)[:400])

# ---------- 2. Full raw catalog /api/products on OVH box ----------
r = fetch("https://prodseller.com/api/products", limit=3000000)
if r.get("ok"):
    try:
        arr = json.loads(r["body"])
        res["raw_catalog"] = {"n": len(arr),
                               "first_ids": [p.get("_id") for p in arr[:5]],
                               "names_sample": [p.get("name") for p in arr[:8]]}
        # save raw
        with open("/home/z/my-project/research/g1a_r4_raw_api_products.json", "w", encoding="utf-8") as f:
            json.dump(arr, f, ensure_ascii=False, indent=1)
        print(f"\n=== /api/products raw: {len(arr)} products ===")
        # check schema keys
        keys = set()
        for p in arr[:20]: keys.update(p.keys())
        print(" schema keys:", sorted(keys)[:25])
    except Exception as e:
        print("parse err", e)
        res["raw_catalog"] = {"parse_error": str(e), "len_body": len(r["body"])}
else:
    print("/api/products failed:", r.get("status"), r.get("error"))

# cross-check vs StackVault sv-api catalog (known cb_ ObjectIds)
try:
    sv = json.load(open("/home/z/my-project/research/g1_cb_live_catalog_20261002.json"))
    sv_oids = set()
    for p in sv.get("products", []):
        pid = str(p.get("id", ""))
        m = re.match(r"^[a-z]{2}_([0-9a-f]{24})$", pid)
        if m: sv_oids.add(m.group(1))
    raw_oids = {p.get("_id") for p in arr} if isinstance(arr, list) else set()
    inter = sv_oids & raw_oids
    res["catalog_cross_check"] = {"sv_oids": len(sv_oids), "raw_oids": len(raw_oids),
                                    "intersection": len(inter),
                                    "raw_minus_sv": len(raw_oids - sv_oids),
                                    "sv_minus_raw": len(sv_oids - raw_oids)}
    print(f"\nCROSS: sv={len(sv_oids)} raw={len(raw_oids)} shared={len(inter)} "
          f"raw-only={len(raw_oids-sv_oids)} sv-only={len(sv_oids-raw_oids)}")
    extras = [p for p in (arr if isinstance(arr, list) else []) if p.get("_id") in (raw_oids - sv_oids)][:10]
    for p in extras: print("  raw-only product:", p.get("_id"), str(p.get('name'))[:60])
except Exception as e:
    print("cross-check err", e)

# ---------- 3. Other paths on the box ----------
paths = ["/api/v1/products", "/api/orders", "/api/admin", "/api/config", "/api/health",
         "/v1/products", "/sv-api/config", "/api/me", "/api/user"]
res["path_probe"] = {}
for p in paths:
    r = fetch("https://prodseller.com" + p, limit=2000)
    res["path_probe"][p] = {"status": r.get("status"), "head": (r.get("body") or "")[:120]}
    print(f"{p:22} -> {r.get('status')} {(r.get('body') or '')[:90]!r}")

# ---------- 4. decohomz.com front ----------
r = fetch("https://decohomz.com/", limit=200000)
if r.get("ok"):
    body = r["body"]
    t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
    d = re.search(r'<meta name="description"[^>]*content="([^"]*)"', body)
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", body)
    phones = re.findall(r"\+\d{1,3}[\s\d.-]{7,15}", body)
    res["decohomz_front"] = {"title": t.group(1).strip() if t else None,
                              "meta_desc": d.group(1) if d else None,
                              "emails": list(set(emails))[:10], "phones": list(set(phones))[:10],
                              "len": len(body), "csrf": "csrf-token" in body,
                              "generator": re.search(r'<meta name="generator"[^>]*content="([^"]*)"', body).group(1) if re.search(r'<meta name="generator"[^>]*content="([^"]*)"', body) else None}
    print("\n=== decohomz.com front ===")
    print(json.dumps(res["decohomz_front"], ensure_ascii=False, indent=1)[:600])
    # visible text snippet
    txt = re.sub(r"<[^>]+>", " ", body)
    txt = re.sub(r"\s+", " ", txt)
    print(" text snippet:", txt[:500])

# ---------- 5. headers of sv-api on decohomz (cloudflare) ----------
r = fetch("https://decohomz.com/sv-api/products", limit=3000)
res["sv_api_headers"] = {k: v for k, v in (r.get("headers") or {}).items()
                          if k.lower() in ("server", "cf-ray", "cf-cache-status", "x-powered-by",
                                            "x-served-by", "via", "x-nf-request-id", "alt-svc")}
print("\nsv-api headers:", res["sv_api_headers"])

json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print("\nSaved:", OUT)
