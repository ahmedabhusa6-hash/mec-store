#!/usr/bin/env python3
"""MEC-AUDIT: Live API security & flow tests against production (sandbox mode).
Read-mostly; checkout tests use sandbox rails only (marked SANDBOX receipts)."""
import json, urllib.request, urllib.error, time, sys

BASE = "https://mec-store-production.up.railway.app"

def call(method, path, body=None, timeout=30):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json",
        "User-Agent": "mec-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            try: return r.status, json.loads(raw)
            except Exception: return r.status, raw[:200]
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: return e.code, json.loads(raw)
        except Exception: return e.code, raw[:200]
    except Exception as e:
        return 0, str(e)[:150]

results = []
def test(name, method, path, body=None, expect=None, check=None):
    t0 = time.time()
    status, resp = call(method, path, body)
    dt = (time.time() - t0) * 1000
    ok = "?"
    if check: ok = "PASS" if check(status, resp) else "FAIL"
    elif expect: ok = "PASS" if status == expect else "FAIL"
    r = {"test": name, "status": status, "ms": round(dt), "verdict": ok}
    if isinstance(resp, dict):
        r["resp"] = {k: resp.get(k) for k in list(resp)[:6]}
    else:
        r["resp"] = str(resp)[:150]
    results.append(r)
    print(f"[{ok}] {name}: HTTP {status} {round(dt)}ms -> {json.dumps(r['resp'], ensure_ascii=False)[:180]}")
    return status, resp

print("=" * 70)
print("A. CHECKOUT FLOW (sandbox)")
print("=" * 70)
# A1: valid checkout, wallet rail (empty wallet -> should still create order with payment need OR fail gracefully)
s, r1 = test("checkout wallet (no balance)", "POST", "/api/store/checkout",
     {"slug": "gemini-pro-18m", "phone": "+967771234567", "rail": "wallet"})
# A2: checkout TRC20 (payment instructions expected)
s, r2 = test("checkout trc20", "POST", "/api/store/checkout",
     {"slug": "gemini-pro-18m", "phone": "+967771234567", "rail": "trc20"})
pid = None
if isinstance(r2, dict) and r2.get("ok"): pid = r2.get("publicId")
# A3: order status for created order
if pid:
    test("order status", "GET", f"/api/store/orders/{pid}")
# A4: payments/confirm (sandbox) — first confirm
if pid:
    s, rc1 = test("payments confirm #1 (sandbox)", "POST", "/api/store/payments/confirm",
        {"publicId": pid, "txid": "AUDIT-SANDBOX-TEST-1"})
# A5: payments/confirm AGAIN — idempotency check (double-spend test)
if pid:
    s, rc2 = test("payments confirm #2 (idempotency)", "POST", "/api/store/payments/confirm",
        {"publicId": pid, "txid": "AUDIT-SANDBOX-TEST-1"})

print()
print("=" * 70)
print("B. VALIDATION & ABUSE TESTS")
print("=" * 70)
# B1: invalid slug
test("checkout invalid slug", "POST", "/api/store/checkout",
     {"slug": "does-not-exist", "phone": "+967771234567", "rail": "wallet"},
     check=lambda s, r: s in (400, 404) and (not r.get("ok", True)))
# B2: invalid phone
test("checkout invalid phone", "POST", "/api/store/checkout",
     {"slug": "gemini-pro-18m", "phone": "not-a-phone", "rail": "wallet"},
     check=lambda s, r: s == 400 and not r.get("ok", True))
# B3: missing fields
test("checkout missing fields", "POST", "/api/store/checkout", {"slug": "gemini-pro-18m"},
     check=lambda s, r: s == 400 and not r.get("ok", True))
# B4: XSS in phone
test("checkout XSS phone", "POST", "/api/store/checkout",
     {"slug": "gemini-pro-18m", "phone": "<script>alert(1)</script>", "rail": "wallet"},
     check=lambda s, r: s == 400 and not r.get("ok", True))
# B5: SQLi in phone
test("checkout SQLi phone", "POST", "/api/store/checkout",
     {"slug": "gemini-pro-18m", "phone": "+96777123456' OR '1'='1", "rail": "wallet"},
     check=lambda s, r: not (isinstance(r, dict) and r.get("ok")))
# B6: invalid rail
test("checkout invalid rail", "POST", "/api/store/checkout",
     {"slug": "gemini-pro-18m", "phone": "+967771234567", "rail": "free_money"},
     check=lambda s, r: s == 400 and not r.get("ok", True))
# B7: non-existent order
test("order status nonexistent", "GET", "/api/store/orders/does-not-exist-xyz",
     check=lambda s, r: s in (404, 400) and not r.get("ok", True))
# B8: confirm non-existent order
test("confirm nonexistent order", "POST", "/api/store/payments/confirm",
     {"publicId": "does-not-exist-xyz", "txid": "X"},
     check=lambda s, r: s in (404, 400) and not r.get("ok", True))
# B9: wallet deposit (sandbox) — valid
test("wallet deposit sandbox", "POST", "/api/wallet/deposit",
     {"phone": "+967771234567", "amountUsd": 10},
     check=lambda s, r: r.get("ok") is True)
# B10: wallet deposit negative
test("wallet deposit negative", "POST", "/api/wallet/deposit",
     {"phone": "+967771234567", "amountUsd": -50},
     check=lambda s, r: not (isinstance(r, dict) and r.get("ok") and r.get("balance", 0) < 0))
# B11: wallet deposit huge
test("wallet deposit huge", "POST", "/api/wallet/deposit",
     {"phone": "+967771234567", "amountUsd": 99999999},
     check=lambda s, r: not (isinstance(r, dict) and r.get("ok") and r.get("balance", 1) > 100000))
# B12: wallet deposit string injection
test("wallet deposit type confusion", "POST", "/api/wallet/deposit",
     {"phone": "+967771234567", "amountUsd": {"$gt": 0}},
     check=lambda s, r: not (isinstance(r, dict) and r.get("ok") and isinstance(r.get("balance"), str)))

print()
print("=" * 70)
print("C. INFOSEC / HEADERS")
print("=" * 70)
req = urllib.request.Request(BASE + "/", headers={"User-Agent": "mec-audit/1.0"})
with urllib.request.urlopen(req, timeout=20) as r:
    hdrs = dict(r.headers)
    for h in ["x-frame-options", "content-security-policy", "strict-transport-security",
              "x-content-type-options", "referrer-policy", "permissions-policy"]:
        v = hdrs.get(h) or hdrs.get(h.title())
        print(f"  {h}: {v if v else 'MISSING'}")

json.dump(results, open("/home/z/my-project/research/live_capture/api_audit_results.json", "w"),
          ensure_ascii=False, indent=1)
print(f"\nSaved {len(results)} results.")
