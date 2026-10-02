#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1a R5 — decohomz origin hunt + front-site identity + port-80 vhost test + subdomain sweep
Output: research/g1a_r5_decohomz_origin_20261002.json
"""
import json, ssl, re
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

OUT = "/home/z/my-project/research/g1a_r5_decohomz_origin_20261002.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def fetch(url, headers=None, timeout=25, limit=None):
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    try:
        r = urlopen(Request(url, headers=h), timeout=timeout, context=CTX)
        data = r.read(limit) if limit else r.read()
        return {"ok": True, "status": r.status, "final_url": r.url,
                "headers": {k: v for k, v in r.headers.items()},
                "body": data.decode("utf-8", "replace")}
    except HTTPError as e:
        try: body = e.read(3000).decode("utf-8", "replace")
        except Exception: body = ""
        return {"ok": False, "status": e.code, "headers": dict(e.headers or {}), "body": body}
    except Exception as e:
        return {"ok": False, "status": 0, "error": repr(e)}

res = {"run": "G-1a R5 decohomz origin hunt", "ts": datetime.now(timezone.utc).isoformat()}

# ---------- 1. Port 80 vhost test on OVH box ----------
res["port80_vhost"] = {}
for host in ["decohomz.com", "stackvault.shop", "www.stackvault.shop", "prodseller.com"]:
    r = fetch("http://51.77.244.194/sv-api/products", headers={"Host": host}, limit=4000)
    res["port80_vhost"][host] = {"status": r.get("status"), "head": (r.get("body") or "")[:180]}
    print(f"80 Host={host:20} -> {r.get('status')} :: {(r.get('body') or '')[:100]!r}")

# also test /api/products with decohomz host
r = fetch("http://51.77.244.194/api/products", headers={"Host": "decohomz.com"}, limit=600)
res["port80_vhost"]["decohomz@api"] = {"status": r.get("status"), "head": (r.get("body") or "")[:180]}
print(f"80 Host=decohomz /api/products -> {r.get('status')} :: {(r.get('body') or '')[:100]!r}")

# ---------- 2. decohomz front-site pages ----------
pages = ["/about", "/contact", "/shop", "/categories", "/robots.txt", "/sitemap.xml",
         "/become-a-vendor", "/pre-order", "/deals"]
res["decohomz_pages"] = {}
for p in pages:
    r = fetch("https://decohomz.com" + p, limit=100000)
    body = r.get("body") or ""
    info = {"status": r.get("status"), "len": len(body)}
    t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
    if t: info["title"] = t.group(1).strip()[:100]
    txt = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
    txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    info["text"] = txt[:900]
    emails = list(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", body)))[:8]
    phones = list(set(re.findall(r"(?:\+20|01)[0-9\s-]{8,13}", body)))[:8]
    if emails: info["emails"] = emails
    if phones: info["phones_eg"] = phones
    res["decohomz_pages"][p] = info
    print(f"\n[{p}] {r.get('status')} len={len(body)} title={info.get('title')}")
    print("  text:", txt[:280])
    if emails: print("  EMAILS:", emails)
    if phones: print("  PHONES:", phones)

# ---------- 3. Subdomain sweep for decohomz (direct-connect candidates) ----------
def doh(name, rt="A"):
    try:
        r = urlopen(Request(f"https://dns.google/resolve?name={name}&type={rt}",
                             headers={"User-Agent": UA}), timeout=15, context=CTX)
        d = json.loads(r.read().decode())
        return [a.get("data") for a in d.get("Answer", [])]
    except Exception as e:
        return {"err": repr(e)}

subs = ["mail", "cpanel", "webmail", "direct", "origin", "api", "dev", "staging",
        "admin", "app", "cdn", "ftp", "ssh", "sv", "shop", "store"]
res["decohomz_subdomains"] = {}
for s in subs:
    a = doh(f"{s}.decohomz.com")
    if a and not (isinstance(a, dict)):
        res["decohomz_subdomains"][s] = a
        print(f" {s}.decohomz.com -> {a}")

# ---------- 4. crt.sh for all three domains (retry) ----------
res["crtsh"] = {}
for dom in ["prodseller.com", "decohomz.com", "stackvault.shop"]:
    r = fetch(f"https://crt.sh/?q={dom}&output=json", limit=4000000, timeout=60)
    if r.get("ok"):
        try:
            arr = json.loads(r["body"])
            names = set()
            for row in arr:
                for n in str(row.get("name_value", "")).split("\n"):
                    names.add(n.strip())
            res["crtsh"][dom] = {"n_certs": len(arr), "names": sorted(names)}
            print(f"\ncrt.sh {dom}: {len(arr)} certs")
            for n in sorted(names)[:25]: print("   -", n)
        except Exception as e:
            res["crtsh"][dom] = {"parse_error": str(e)}
    else:
        res["crtsh"][dom] = {"status": r.get("status"), "error": r.get("error")}
        print(f"crt.sh {dom}: FAILED {r.get('status')} {str(r.get('error'))[:80]}")

json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
print("\nSaved:", OUT)
