#!/usr/bin/env python3
"""MEC-AUDIT-2: Full happy path + deep security probes with real slugs."""
import json, urllib.request, urllib.error, time

BASE = "https://mec-store-production.up.railway.app"
PHONE = "+967771234567"  # audit wallet (has $10 sandbox balance)

def call(method, path, body=None, timeout=40):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json", "User-Agent": "mec-audit/1.0"})
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
        return 0, str(e)[:200]

def show(name, s, r):
    body = json.dumps(r, ensure_ascii=False)[:260] if isinstance(r, dict) else str(r)[:200]
    print(f"  [{s}] {name} -> {body}")

print("=== 1. WALLET RAIL (with $10 balance, product $0.69 YE) ===")
s, r = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": PHONE, "rail": "wallet"})
show("checkout wallet", s, r)
w_order = r.get("publicId") if isinstance(r, dict) else None

print("\n=== 2. TRC20 RAIL (payment instructions) ===")
s, r2 = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": PHONE, "rail": "trc20"})
show("checkout trc20", s, r2)
t_order = r2.get("publicId") if isinstance(r2, dict) else None
payment = r2.get("payment") if isinstance(r2, dict) else None
if payment: print("    payment details:", json.dumps(payment, ensure_ascii=False)[:300])

print("\n=== 3. ORDER STATUS ===")
if w_order:
    s, r = call("GET", f"/api/store/orders/{w_order}")
    show("wallet order status", s, r)
if t_order:
    s, r = call("GET", f"/api/store/orders/{t_order}")
    show("trc20 order status", s, r)

print("\n=== 4. PAYMENT CONFIRM (trc20 sandbox simulation) ===")
if t_order:
    s, rc1 = call("POST", "/api/store/payments/confirm", {"publicId": t_order, "txid": "AUDIT-CONFIRM-001"})
    show("confirm #1", s, rc1)
    s, rc2 = call("POST", "/api/store/payments/confirm", {"publicId": t_order, "txid": "AUDIT-CONFIRM-001"})
    show("confirm #2 (double-submit)", s, rc2)
    s, rc3 = call("POST", "/api/store/payments/confirm", {"publicId": t_order, "txid": "AUDIT-CONFIRM-DIFF"})
    show("confirm #3 (different txid)", s, rc3)

print("\n=== 5. CRITICAL: SQLi phone with VALID slug ===")
sqli_phones = [
    "+96777123456' OR '1'='1",
    "+96777123456\"; DROP TABLE orders;--",
    "+96777123456' UNION SELECT 1--",
    "' OR 1=1--",
]
for sp in sqli_phones:
    s, r = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": sp, "rail": "wallet"})
    ok = isinstance(r, dict) and r.get("ok")
    print(f"  [{s}] phone={sp[:32]!r:36} ok={ok} -> {json.dumps(r, ensure_ascii=False)[:140]}")

print("\n=== 6. PRICE TAMPERING attempts ===")
s, r = call("POST", "/api/store/checkout", {"slug": "adobe-express-12m", "phone": PHONE, "rail": "wallet",
    "price": 0.01, "amountUsd": 0.01, "prices": {"YE": {"price": 0.01}}})
show("tampered price fields", s, r)
if isinstance(r, dict) and r.get("ok"):
    print("    >>> PRICE TAMPERING CHECK: order created — need to verify server-side price lock")

print("\n=== 7. RATE LIMIT CHECK (12 rapid checkouts) ===")
codes = []
t0 = time.time()
for i in range(12):
    s, _ = call("POST", "/api/store/checkout", {"slug": "avira-prime-3-months", "phone": f"+96777000{i:02d}", "rail": "trc20"})
    codes.append(s)
print(f"  12 checkouts in {round(time.time()-t0,1)}s -> codes: {codes}")
print("  RATE LIMITING:", "PRESENT" if 429 in codes else "ABSENT (no rate limit on checkout!)")

print("\n=== 8. WALLET after spends ===")
s, r = call("GET", f"/api/wallet?phone={PHONE.replace('+','%2B')}")
show("wallet state", s, r)
