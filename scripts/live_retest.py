#!/usr/bin/env python3
"""MEC LIVE RETEST — full verification suite after hardening deploy.
Every test maps to a BEFORE state captured in api_audit_results.json."""
import json, time, urllib.request, urllib.error

BASE = "https://mec-store-production.up.railway.app"
ADMIN_TOKEN = open("/tmp/admin_token.txt").read().strip()
PHONE = "+967771234567"

def call(method, path, body=None, headers=None, timeout=40):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", "User-Agent": "mec-audit/1.0"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            try: return r.status, json.loads(raw)
            except Exception: return r.status, raw[:300]
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: return e.code, json.loads(raw)
        except Exception: return e.code, raw[:300]
    except Exception as e:
        return 0, str(e)[:150]

results = []
def test(name, ok, detail):
    results.append({"test": name, "verdict": "PASS" if ok else "FAIL", "detail": detail[:200]})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail[:170]}")

print("=" * 72)
print("MEC LIVE RETEST — AFTER HARDENING DEPLOY (f2c88f49)")
print("=" * 72)

# 1. Pages
for path, want in [("/", 200), ("/intel", 200), ("/nope-404", 404), ("/api", 200)]:
    t0 = time.time()
    s, r = call("GET", path)
    ms = round((time.time() - t0) * 1000)
    test(f"GET {path}", s == want, f"HTTP {s} in {ms}ms (want {want})")

# 2. 404 page Arabic check
s, r = call("GET", "/nope-404")
if isinstance(r, str):
    test("404 Arabic page", "هذه الصفحة غير موجودة" in r, "custom Arabic 404 rendered" if "هذه الصفحة غير موجودة" in r else r[:80])
else:
    test("404 Arabic page", False, "non-text response")

# 3. Security headers
req = urllib.request.Request(BASE + "/", headers={"User-Agent": "mec-audit/1.0"})
with urllib.request.urlopen(req, timeout=20) as r:
    hdrs = dict(r.headers)
    missing = [h for h in ["x-frame-options", "content-security-policy", "strict-transport-security",
                           "x-content-type-options", "referrer-policy"] if not (hdrs.get(h) or hdrs.get(h.title()))]
    test("security headers (5)", len(missing) == 0, f"missing: {missing}" if missing else "ALL PRESENT (CSP/HSTS/XFO/XCTO/RP)")

# 4. Admin auth matrix (BEFORE: open 200 leak)
s, r = call("GET", "/api/admin/stats")
test("admin stats NO token", s == 401, f"HTTP {s} (BEFORE: 200 + leaked SaraShamari)")
s, r = call("GET", "/api/admin/stats", headers={"x-admin-token": "wrong"})
test("admin stats BAD token", s == 401, f"HTTP {s}")
s, r = call("GET", "/api/admin/stats", headers={"x-admin-token": ADMIN_TOKEN})
ok = s == 200 and isinstance(r, dict) and r.get("ok")
test("admin stats GOOD token", ok, f"HTTP {s} orders.total={r.get('orders',{}).get('total') if isinstance(r,dict) else '?'}")

# 5. Admin sync without token (BEFORE: ran a real 25s sync)
t0 = time.time()
s, r = call("POST", "/api/admin/sync", {})
test("admin sync NO token", s == 401, f"HTTP {s} in {round(time.time()-t0,1)}s (BEFORE: 200 after 25s real sync)")

# 6. Catalog + performance (BEFORE: 2.5-2.7s)
times = []
for _ in range(3):
    t0 = time.time()
    s, r = call("GET", "/api/store/catalog")
    times.append(round((time.time() - t0) * 1000))
ok = s == 200 and isinstance(r, dict) and len(r.get("products", [])) == 37
test("catalog 37 products", ok, f"HTTP {s} products={len(r.get('products',[])) if isinstance(r,dict) else '?'} | latencies: {times}ms (BEFORE: 2500-2700ms)")

# 7. Wallet
s, r = call("GET", f"/api/wallet?phone={PHONE.replace('+','%2B')}")
test("wallet state", s == 200 and isinstance(r, dict) and r.get("ok"), f"HTTP {s} balance={r.get('balance') if isinstance(r,dict) else '?'} txs={len(r.get('txs',[])) if isinstance(r,dict) else '?'}")

# 8. SANDBOX DELIVERY FIX (BEFORE: all sandbox orders FAILED + refund + apology)
s, r = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": PHONE, "rail": "wallet"})
routed = r.get("routed", {}) if isinstance(r, dict) else {}
delivered = routed.get("status") == "delivered" and routed.get("ok") is True
test("SANDBOX checkout DELIVERS", delivered, f"routed={json.dumps(routed, ensure_ascii=False)[:120]} (BEFORE: failed+refund)")

# 9. Order status + transparency + receipt marked SANDBOX
pid = r.get("publicId") if isinstance(r, dict) else None
if pid:
    s, r2 = call("GET", f"/api/store/orders/{pid}")
    o = r2.get("order", {}) if isinstance(r2, dict) else {}
    payload = o.get("deliveredPayload") or ""
    steps = r2.get("transparency", []) if isinstance(r2, dict) else []
    test("order delivered + SANDBOX receipt", o.get("status") == "delivered" and "SANDBOX" in payload,
         f"status={o.get('status')} winner={o.get('winner')} receipt={'SANDBOX-marked ✓' if 'SANDBOX' in payload else 'NOT MARKED'} steps={len(steps)}")
    test("cashback credited", o.get("cashback", 0) > 0, f"cashback=${o.get('cashback')}")

# 10. TRC20 + confirm + idempotency
s, r3 = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": "+967770001133", "rail": "trc20"})
pay = r3.get("payment", {}) if isinstance(r3, dict) else {}
pid2 = r3.get("publicId") if isinstance(r3, dict) else None
test("TRC20 checkout payment instructions", s == 200 and pay.get("address") and pay.get("centsCode"),
     f"addr={pay.get('address','?')} amount={pay.get('amount')} cents={pay.get('centsCode')}")
if pid2:
    s, c1 = call("POST", "/api/store/payments/confirm", {"publicId": pid2, "txid": "RETEST-1"})
    st1 = (c1.get("routed") or c1).get("status") if isinstance(c1, dict) else "?"
    test("TRC20 confirm delivers (sandbox)", st1 == "delivered", f"HTTP {s} status={st1}")
    s, c2 = call("POST", "/api/store/payments/confirm", {"publicId": pid2, "txid": "RETEST-1"})
    test("confirm idempotency", isinstance(c2, dict) and c2.get("idempotent") is True, f"HTTP {s} idempotent={c2.get('idempotent') if isinstance(c2,dict) else '?'}")

# 11. Rate limiting (BEFORE: 12/12 all 200)
codes = []
t0 = time.time()
for i in range(14):
    s, _ = call("POST", "/api/store/checkout", {"slug": "avira-prime-3-months", "phone": f"+96777888{i:02d}", "rail": "trc20"}, timeout=15)
    codes.append(s)
has429 = 429 in codes
test("rate limiting on checkout", has429, f"codes={codes} in {round(time.time()-t0,1)}s (BEFORE: all 200, no limit)")

# 12. Validation regression checks
s, r = call("POST", "/api/store/checkout", {"slug": "x", "phone": "bad", "rail": "wallet"})
test("invalid input still rejected", s == 400, f"HTTP {s} {r.get('error','') if isinstance(r,dict) else ''}")
s, r = call("POST", "/api/wallet/deposit", {"phone": PHONE, "amountUsd": -5})
test("negative deposit still rejected", s == 400, f"HTTP {s}")
s, r = call("POST", "/api/wallet/deposit", {"phone": PHONE, "amountUsd": 999999})
test("huge deposit still rejected", s == 400, f"HTTP {s}")

# 13. Tight phone regex (BEFORE: accepted quotes as phone)
s, r = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": "+96777123456' OR '1'='1", "rail": "wallet"})
rejected = s == 400 and isinstance(r, dict) and not r.get("ok", True)
test("SQLi-ish phone rejected (tight regex)", rejected, f"HTTP {s} (BEFORE: accepted as valid phone)")

# Summary
passed = sum(1 for x in results if x["verdict"] == "PASS")
print("\n" + "=" * 72)
print(f"RESULT: {passed}/{len(results)} PASS")
print("=" * 72)
json.dump(results, open("/home/z/my-project/research/live_capture/retest_results.json", "w"), ensure_ascii=False, indent=1)
print("saved -> research/live_capture/retest_results.json")
