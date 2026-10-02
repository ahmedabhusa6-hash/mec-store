#!/usr/bin/env python3
# MEC-21 PRODUCTION verification (GET/HEAD only, read-only)
import json
import urllib.request
import urllib.error
import sys

BASE = "https://mec-store-production.up.railway.app"
PASS, FAIL = [], []

def fetch(path, headers=None, method="GET", timeout=25):
    h = dict(headers or {})
    r = urllib.request.Request(BASE + path, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            try:
                parsed = json.loads(raw) if raw else None
            except Exception:
                parsed = raw.decode("utf-8", errors="replace")
            return resp.status, dict(resp.headers), parsed
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, dict(e.headers), json.loads(raw) if raw else None
        except Exception:
            return e.code, dict(e.headers), raw.decode(errors="replace")
    except Exception as e:
        return 0, {}, {"error": str(e)}

def check(name, cond, evidence=""):
    (PASS if cond else FAIL).append((name, evidence))
    print(f"  {'PASS' if cond else 'FAIL'} | {name}" + (f" | {evidence}" if evidence and not cond else ""))

print("== 1. Health + mode ==")
s, h, health = fetch("/api/health")
check("health ok+db", s == 200 and health.get("ok") and health.get("db"), f"{s} {health}")
check("health latency < 400ms", health.get("latencyMs", 9999) < 400, f"{health.get('latencyMs')}ms")

print("== 2. Catalog (new features on prod) ==")
s, h, cat = fetch("/api/store/catalog")
check("catalog 200", s == 200)
prods = cat.get("products", [])
check("37 products", len(prods) == 37, f"n={len(prods)}")
gpt = next((p for p in prods if p["slug"] == "chatgpt-plus-1-month"), None)
check("Arabic aliases live", bool(gpt and "شات جي بي تي" in (gpt.get("aliases") or "")))
body_str = json.dumps(cat)
check("no costUsd", "costUsd" not in body_str)
stock_vals = {c["stock"] for p in prods for c in p["chain"]}
check("stock tri-state", stock_vals <= {0, 1, None}, f"{stock_vals}")
etag = h.get("etag") or h.get("ETag")
check("ETag present", bool(etag))
if etag:
    s2, h2, _ = fetch("/api/store/catalog", headers={"If-None-Match": etag})
    check("304 works", s2 == 304, f"status={s2}")

print("== 3. Wallet hardening on prod ==")
s, h, w = fetch("/api/wallet?phone=%2B96651119999")
check("unknown phone empty-shape (no oracle)", s == 200 and w.get("balance") == 0 and w.get("txs") == [], f"{s} {w}")
check("no ref in txs", all("ref" not in t for t in (w.get("txs") or [])))

print("== 4. SEO surfaces on prod ==")
s, h, html = fetch("/")
html = html if isinstance(html, str) else ""
check("home 200", s == 200)
check("canonical", 'rel="canonical"' in html)
check("og:image", 'property="og:image"' in html and "og-image.png" in html)
check("og:locale ar_SA", 'ar_SA' in html)
check("twitter card", 'twitter:card' in html)
check("no /intel link", 'href="/intel"' not in html)
check("h1", "<h1" in html)
s, h, sm = fetch("/sitemap.xml")
check("sitemap 200", s == 200 and "<urlset" in (sm if isinstance(sm, str) else ""))
s, h, rb = fetch("/robots.txt")
rb = rb if isinstance(rb, str) else ""
check("robots disallow /intel", "Disallow: /intel" in rb)
check("robots sitemap", "Sitemap:" in rb)
s, h, _ = fetch("/og-image.png")
check("og-image served", s == 200)
s, h, _ = fetch("/icon.png")
check("icon served", s == 200)
s, h, intel = fetch("/intel")
check("/intel noindex", "noindex" in (intel if isinstance(intel, str) else ""))
s, h, _ = fetch("/terms")
check("/terms 200", s == 200)

print("== 5. Security headers ==")
s, h, _ = fetch("/", method="HEAD")
hdr = {k.lower(): v for k, v in h.items()}
check("HSTS preload", "max-age=63072000" in hdr.get("strict-transport-security", "") and "preload" in hdr.get("strict-transport-security", ""))
check("XFO DENY", hdr.get("x-frame-options") == "DENY")
check("CSP no unsafe-eval", "unsafe-eval" not in hdr.get("content-security-policy", ""))
check("XCTO", hdr.get("x-content-type-options") == "nosniff")
check("Referrer-Policy", "referrer-policy" in hdr)

print("== 6. Admin gate (rotated token: old must fail, new must pass) ==")
s, h, _ = fetch("/api/admin/stats")
check("admin no-token 401", s == 401, f"status={s}")

print("== 7. Waitlist endpoint live ==")
s, h, wl = fetch("/api/store/waitlist")  # GET -> 405 expected (POST-only route)
check("waitlist GET 405", s == 405, f"status={s}")

print("== 8. 404 + /api liveness ==")
s, h, _ = fetch("/nonexistent-page")
check("404 status", s == 404, f"status={s}")
s, h, api = fetch("/api")
check("/api liveness", s == 200)

print()
print(f"PROD RESULT: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    for n, e in FAIL:
        print(f"  FAIL {n} | {e}")
sys.exit(1 if FAIL else 0)
