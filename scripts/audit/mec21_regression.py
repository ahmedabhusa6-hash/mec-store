#!/usr/bin/env python3
# MEC-21 regression suite — verifies all session fixes + MEC-20 regression guard
# Run against freshly built local prod server (localhost:3000).
import json
import time
import urllib.request
import urllib.error
import sys

BASE = "http://localhost:3000"
PASS, FAIL, SKIP = [], [], []

def req(method, path, body=None, headers=None, timeout=20):
    h = {"Content-Type": "application/json", **(headers or {})}
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
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
    print(f"  {'✓ PASS' if cond else '✗ FAIL'} | {name}" + (f" | {evidence}" if evidence and not cond else ""))

TS = str(int(time.time()))[-6:]
PHONE = f"+96650{TS}"  # fresh phone for E2E

print("== 1. Catalog (aliases + stock tri-state + no cost leak + ETag) ==")
s, h, cat = req("GET", "/api/store/catalog")
check("catalog 200", s == 200, f"status={s}")
prods = cat.get("products", [])
check("37 products", len(prods) == 37, f"n={len(prods)}")
gpt = next((p for p in prods if p["slug"] == "chatgpt-plus-1-month"), None)
check("aliases present (chatgpt)", bool(gpt and "شات جي بي تي" in (gpt.get("aliases") or "")), str(gpt)[:80] if gpt else "missing")
nfx = next((p for p in prods if "netflix" in p["slug"]), None)
check("aliases present (netflix)", bool(nfx and "نتفلكس" in (nfx.get("aliases") or "")))
stock_vals = {c["stock"] for p in prods for c in p["chain"]}
check("stock tri-state only (0/1/null)", stock_vals <= {0, 1, None}, f"values={stock_vals}")
body_str = json.dumps(cat, ensure_ascii=False)
check("no costUsd leak", "costUsd" not in body_str and "cost_usd" not in body_str)
check("no checkedAt leak", "checkedAt" not in body_str)
etag = h.get("etag") or h.get("ETag")
check("catalog ETag present", bool(etag), f"headers={list(h.keys())}")
if etag:
    s2, h2, _ = req("GET", "/api/store/catalog", headers={"If-None-Match": etag})
    check("catalog 304 on If-None-Match", s2 == 304, f"status={s2}")

print("== 2. Wallet hardening (no row creation, no ref leak) ==")
s, h, w = req("GET", f"/api/wallet?phone=%2B96651119999")  # random never-used phone
check("unknown phone 200 empty-shape", s == 200 and w.get("balance") == 0 and w.get("txs") == [], f"{s} {w}")
check("no ref field in txs", all("ref" not in t for t in (w.get("txs") or [])))

s, h, dep = req("POST", "/api/wallet/deposit", {"phone": PHONE, "amountUsd": 10})
check("deposit $10 sandbox ok", s == 200 and dep.get("ok"), f"{s} {dep}")
s, h, w2 = req("GET", f"/api/wallet?phone={urllib.parse.quote(PHONE)}")
check("wallet balance 10.00", w2.get("balance") == 10.0, str(w2.get("balance")))
check("txs have no ref", all("ref" not in t for t in w2.get("txs", [])))

print("== 3. Waitlist endpoint (G12) ==")
oos = next((p for p in prods if all(c["stock"] == 0 for c in p["chain"])), None)
if oos:
    s, h, wl = req("POST", "/api/store/waitlist", {"phone": PHONE, "slug": oos["slug"]})
    check("waitlist join ok", s == 200 and wl.get("ok"), f"{s} {wl}")
    s, h, wl2 = req("POST", "/api/store/waitlist", {"phone": PHONE, "slug": oos["slug"]})
    check("waitlist idempotent (already:true)", wl2.get("already") is True, str(wl2))
else:
    SKIP.append(("waitlist", "no OOS product in catalog"))
    print("  - SKIP | waitlist (no OOS product available)")
s, h, wl3 = req("POST", "/api/store/waitlist", {"phone": "", "slug": "chatgpt-plus-1-month"})
check("waitlist without phone 400", s == 400, f"status={s}")

print("== 4. Order IDOR regression (MEC-20 fix intact) ==")
s, h, o = req("GET", "/api/store/orders/MEC-DOESNOTEXIST99?phone=%2B9665000000")
check("random publicId 404", s == 404, f"status={s}")

print("== 5. E2E purchase (engine.ts edits regression) ==")
cheap = sorted([p for p in prods if p["prices"].get("SA")], key=lambda p: p["prices"]["SA"]["price"])[0]
s, h, co = req("POST", "/api/store/checkout", {"slug": cheap["slug"], "phone": PHONE, "region": "SA", "rail": "wallet"})
check("checkout ok", s == 200 and co.get("ok"), f"{s} {str(co)[:120]}")
pid = co.get("publicId") or (co.get("order") or {}).get("publicId")
routed = co.get("routed") or {}
order_status = routed.get("status") or co.get("status")
check("order delivered (sandbox)", order_status == "delivered", f"status={order_status} keys={list(co.keys())}")
s, h, w3 = req("GET", f"/api/wallet?phone={urllib.parse.quote(PHONE)}")
bal = w3.get("balance")
price = cheap["prices"]["SA"]["price"]
usd = co.get("amountUsd") or routed.get("amountUsd") or (co.get("order") or {}).get("amountUsd")
cashback = routed.get("cashback") or co.get("cashback") or 0
if usd is not None:
    expected = round(10 - usd + (cashback if isinstance(cashback, (int, float)) else 0), 2)
    check(f"ledger exact ({10} - {usd} + {cashback} = {expected})", abs(bal - expected) < 0.011, f"actual={bal}")
else:
    SKIP.append(("ledger", "amountUsd not in response"))
    print(f"  - SKIP | ledger (checkout response keys: {list(co.keys())})")
s, h, od = req("GET", f"/api/store/orders/{pid}?phone={urllib.parse.quote(PHONE)}")
check("order detail owner ok", s == 200 and od.get("ok"))
s, h, od2 = req("GET", f"/api/store/orders/{pid}?phone=%2B96651119999")
check("order detail wrong-phone 404", s == 404, f"status={s}")

print("== 6. SEO surfaces ==")
r = urllib.request.Request(BASE + "/")
with urllib.request.urlopen(r, timeout=15) as resp:
    home_status = resp.status
    html = resp.read().decode("utf-8")
check("home 200", home_status == 200, f"status={home_status}")
check("canonical link", 'rel="canonical"' in html)
check("og:image", 'og-image.png' in html and 'property="og:image"' in html)
check("og:locale ar_SA", 'ar_SA' in html)
check("og:url", 'property="og:url"' in html)
check("twitter:card", 'twitter:card' in html)
check("h1 present", "<h1" in html)
check("no /intel link in header", 'href="/intel"' not in html)
s, h, sm = req("GET", "/sitemap.xml")
check("sitemap 200 w/ 4 urls", s == 200 and sm.count("<url>") >= 4 if isinstance(sm, str) else s == 200)
s, h, rb = req("GET", "/robots.txt")
rb_str = rb if isinstance(rb, str) else ""
check("robots disallow /intel", "Disallow: /intel" in rb_str)
check("robots sitemap line", "Sitemap:" in rb_str)
s, h, intel = req("GET", "/intel")
intel_str = intel if isinstance(intel, str) else ""
check("/intel noindex", "noindex" in intel_str)
s, h, ogimg = req("GET", "/og-image.png")
check("og-image served", s == 200)
s, h, ic = req("GET", "/icon.png")
check("icon served", s == 200)

print("== 7. Wallet rate limit (20/min) — LAST (exhausts bucket) ==")
codes = []
for i in range(24):
    s, _, _ = req("GET", f"/api/wallet?phone={urllib.parse.quote(PHONE)}")
    codes.append(s)
n429 = codes.count(429)
check("429 fires within 24 reqs (cap 20)", n429 >= 1, f"codes={codes}")
check("cap is ~20 (not 60)", n429 >= 3, f"n429={n429}")

print("== 8. Admin gate regression ==")
s, _, _ = req("GET", "/api/admin/stats")
check("admin no-token 401", s == 401, f"status={s}")

print()
total = len(PASS) + len(FAIL) + len(SKIP)
print(f"RESULT: {len(PASS)} PASS / {len(FAIL)} FAIL / {len(SKIP)} SKIP (of {total})")
if FAIL:
    print("FAILED:")
    for n, e in FAIL:
        print(f"  ✗ {n} | {e}")
sys.exit(1 if FAIL else 0)
