#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1a R1 — Platform Operator Identity: passive domain & entity intelligence
Target: prodseller.com (ProdSeller platform), @sookbit, 51.77.244.194 (legacy IP)
Strictly passive: public RDAP/DNS/CT/Archive/GET only. No auth, no purchases, no interaction.
Output: research/g1a_r1_domain_intel_20261002.json
"""
import json, ssl, socket, time, re, sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError, URLError

OUT = "/home/z/my-project/research/g1a_r1_domain_intel_20261002.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=20, headers=None, raw=False):
    h = {"User-Agent": UA, "Accept-Language": "en;q=0.9"}
    if headers: h.update(headers)
    req = Request(url, headers=h)
    try:
        with urlopen(req, timeout=timeout, context=CTX) as r:
            data = r.read()
            return {"ok": True, "status": r.status, "final_url": r.url,
                    "headers": dict(r.headers), "body": data if raw else data.decode("utf-8", "replace")}
    except HTTPError as e:
        try: body = e.read().decode("utf-8", "replace")
        except Exception: body = ""
        return {"ok": False, "status": e.code, "error": str(e), "body": body[:2000]}
    except Exception as e:
        return {"ok": False, "status": 0, "error": repr(e)}

def jfetch(url, timeout=20):
    r = fetch(url, timeout)
    if r.get("ok"):
        try: return {"ok": True, "data": json.loads(r["body"])}
        except Exception as e: return {"ok": False, "error": f"json: {e}", "raw": r["body"][:500]}
    return r

res = {"run": "G-1a R1 domain/entity intel", "ts": datetime.now(timezone.utc).isoformat(),
       "passive_only": True, "sections": {}}
S = res["sections"]

# ============ 1. RDAP / WHOIS prodseller.com ============
S["rdap_prodseller"] = jfetch("https://rdap.verisign.com/com/v1/domain/prodseller.com")

# ============ 2. DNS via DoH ============
def doh(name, rtype):
    return jfetch(f"https://dns.google/resolve?name={name}&type={rtype}")

S["dns"] = {}
for rt in ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]:
    S["dns"][rt] = doh("prodseller.com", rt)
    time.sleep(0.4)

# ============ 3. Certificate Transparency (crt.sh) ============
S["crtsh"] = jfetch("https://crt.sh/?q=prodseller.com&output=json&exclude=expired", timeout=45)

# ============ 4. Legacy IP 51.77.244.194 ============
S["legacy_ip"] = {}
S["legacy_ip"]["http_root"] = fetch("http://51.77.244.194/", timeout=15)
S["legacy_ip"]["https_root"] = fetch("https://51.77.244.194/", timeout=15)
S["legacy_ip"]["rdap"] = jfetch("https://rdap.db.ripe.net/ip/51.77.244.194")
S["legacy_ip"]["reverse_dns"] = jfetch("https://api.hackertarget.com/reverseiplookup/?q=51.77.244.194")
S["legacy_ip"]["reverse_dns_prodseller"] = jfetch("https://api.hackertarget.com/reverseiplookup/?q=prodseller.com")

# ============ 5. Wayback Machine ============
S["wayback"] = {}
S["wayback"]["availability_prodseller"] = jfetch("http://archive.org/wayback/available?url=prodseller.com")
S["wayback"]["cdx_prodseller"] = jfetch(
    "http://web.archive.org/cdx/search/cdx?url=prodseller.com*&output=json&limit=200&collapse=urlkey", timeout=45)
S["wayback"]["cdx_legacy_ip"] = jfetch(
    "http://web.archive.org/cdx/search/cdx?url=51.77.244.194*&output=json&limit=100&collapse=urlkey", timeout=45)

# ============ 6. prodseller.com public surfaces ============
S["prodseller_web"] = {}
for path in ["/", "/robots.txt", "/sitemap.xml", "/api-docs/", "/terms", "/about", "/login"]:
    S["prodseller_web"][path] = fetch("https://prodseller.com" + path, timeout=20)
    time.sleep(0.5)

# ============ 7. Telegram public pages ============
S["telegram"] = {}
for handle in ["sookbit", "ProdsellerSupport", "prodsellerbot"]:
    S["telegram"][handle] = fetch(f"https://t.me/{handle}", timeout=15)
    time.sleep(0.6)
S["telegram"]["ProdSellerOfficial_preview"] = fetch("https://t.me/s/ProdSellerOfficial", timeout=20)

# ============ extract structured facts ============
facts = {"emails": set(), "phones": set(), "tg_handles": set(), "domains": set()}
def harvest(text):
    if not text: return
    for m in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        if not m.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")):
            facts["emails"].add(m)
    for m in re.findall(r"\+\d{1,3}[\s.-]?\d(?:[\s.-]?\d){6,14}", text):
        facts["phones"].add(m.strip())
    for m in re.findall(r"@([A-Za-z][A-Za-z0-9_]{3,30})", text):
        facts["tg_handles"].add(m)
    for m in re.findall(r"https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})", text):
        facts["domains"].add(m)

def walk(x):
    if isinstance(x, dict):
        for v in x.values(): walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
    elif isinstance(x, str):
        if len(x) < 400000: harvest(x)

walk(S)
# filter noise
stop = {"gmail.com","google.com","twitter.com","x.com","facebook.com","apple.com","microsoft.com",
        "w3.org","schema.org","googleapis.com","gstatic.com","telegram.org","cdn-telegram.org","t.me",
        "openssl.org","ietf.org","verisign.com","googleadservices.com","googletagmanager.com","archive.org","web.archive.org"}
facts["domains"] = {d for d in facts["domains"] if d.lower() not in stop and not d.lower().endswith(".w3.org")}
res["extracted"] = {k: sorted(v)[:80] for k, v in facts.items()}

# compact: strip huge HTML bodies from telegram pages but keep key excerpts
def compact_telegram(entry):
    if not isinstance(entry, dict): return entry
    body = entry.get("body", "") or ""
    keep = dict(entry)
    # og: meta + description block
    m = re.search(r'<meta property="og:description"[^>]*content="([^"]*)"', body)
    m2 = re.search(r'<meta property="og:title"[^>]*content="([^"]*)"', body)
    keep["og_description"] = m.group(1) if m else None
    keep["og_title"] = m2.group(1) if m2 else None
    keep.pop("body", None); keep.pop("headers", None)
    return keep

if "telegram" in S:
    for k, v in list(S["telegram"].items()):
        S["telegram"][k] = compact_telegram(v)

# compact prodseller_web: keep title/meta + first 3000 chars
for path, entry in list(S.get("prodseller_web", {}).items()):
    if isinstance(entry, dict) and "body" in entry:
        body = entry["body"]
        t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
        d = re.search(r'<meta name="description"[^>]*content="([^"]*)"', body)
        entry["title"] = t.group(1).strip() if t else None
        entry["meta_description"] = d.group(1) if d else None
        entry["body_head"] = body[:2500]
        entry.pop("body", None); entry.pop("headers", None)

# strip wayback bodies if any
for k, v in list(S.get("wayback", {}).items()):
    if isinstance(v, dict) and "data" in v and isinstance(v["data"], list):
        S["wayback"][k] = {"ok": True, "rows": len(v["data"]), "sample": v["data"][:60]}
    elif isinstance(v, dict) and "raw" in v:
        S["wayback"][k] = {"ok": False, "raw_head": v["raw"][:300]}

# legacy ip bodies compact
li = S.get("legacy_ip", {})
for k, v in list(li.items()):
    if isinstance(v, dict) and "body" in v:
        v["body_head"] = v["body"][:1200]; v.pop("body", None); v.pop("headers", None)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

# ===== console summary =====
def one(x):
    if isinstance(x, dict): return x
    return {"note": type(x).__name__}

r = S.get("rdap_prodseller", {})
if r.get("ok"):
    d = r["data"]
    print("=== RDAP prodseller.com ===")
    for ev in d.get("events", []): print(" event:", ev.get("eventAction"), ev.get("eventDate"))
    for ent in d.get("entities", []):
        print(" entity:", ent.get("roles"), json.dumps({k: v for k, v in ent.items() if k != "vcardArray"}, ensure_ascii=False)[:200])
        vc = ent.get("vcardArray")
        if isinstance(vc, list) and len(vc) > 1:
            for item in vc[1]:
                if item[0] in ("fn", "org", "adr", "email", "tel"):
                    print("   vcard:", item[0], item[3] if len(item) > 3 else None)
    print(" nameservers:", [ns.get("ldhName") for ns in d.get("nameservers", [])])
    print(" secureDNS:", bool(d.get("secureDNS", {}).get("delegationSigned")))
else:
    print("RDAP failed:", str(r)[:200])

print("\n=== DNS ===")
for rt, v in S["dns"].items():
    if v.get("ok"):
        answers = [a.get("data") for a in v["data"].get("Answer", [])]
        if answers: print(f" {rt}: {answers[:6]}")

print("\n=== crt.sh ===")
c = S.get("crtsh", {})
if c.get("ok") and isinstance(c.get("data"), list):
    names = set()
    for row in c["data"]:
        for n in (row.get("name_value") or "").split("\n"):
            names.add(n.strip())
    print(f" {len(c['data'])} certs; unique names:")
    for n in sorted(names)[:40]: print("  -", n)
else:
    print(" crt.sh:", str(c)[:200])

print("\n=== Legacy IP 51.77.244.194 ===")
print(" http:", li.get("http_root", {}).get("status"), "https:", li.get("https_root", {}).get("status"))
rd = li.get("rdap", {})
if rd.get("ok"):
    d = rd["data"]
    print(" netname:", d.get("name"), "| country:", d.get("country"), "| handle:", d.get("handle"))
    for ent in d.get("entities", [])[:3]:
        print(" entity:", ent.get("roles"), ent.get("handle"))
rv = li.get("reverse_dns_prodseller", {})
if rv.get("ok"): print(" reverse(prodseller.com):", str(rv.get("body", ""))[:200])
rv2 = li.get("reverse_dns", {})
if rv2.get("ok"): print(" reverse(51.77.244.194):", str(rv2.get("body", ""))[:300])

print("\n=== Telegram ===")
for h, v in S["telegram"].items():
    if isinstance(v, dict):
        print(f" @{h}: title={v.get('og_title')!r} desc={str(v.get('og_description'))[:160]!r}")

print("\n=== Extracted facts ===")
for k, v in res["extracted"].items():
    if v: print(f" {k}: {v[:25]}")

print("\nSaved:", OUT)
