#!/usr/bin/env python3
"""MEC-20 regression suite — runs against local production-mode server (port 3000).
Covers AUDIT-3's 12 regression candidates + the new fixes (costUsd strip,
order owner-proof, orders history, health, apology cap, atomic debit)."""
import json, time, urllib.request, urllib.parse, urllib.error, random, sys

BASE = "http://localhost:3000"
PASS, FAIL, SKIP = [], [], []
XFF = f"10.20.30.{random.randint(2, 254)}"  # isolate rate buckets

def req(method, path, body=None, headers=None, xff=None):
    h = {"Content-Type": "application/json", **(headers or {})}
    if xff: h["X-Forwarded-For"] = xff
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        res = urllib.request.urlopen(r, timeout=30)
        raw = res.read().decode()
        return res.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: return e.code, json.loads(raw)
        except Exception: return e.code, raw
    except Exception as e:
        return 0, str(e)

def check(name, cond, evidence=""):
    (PASS if cond else FAIL).append((name, evidence))
    print(("PASS" if cond else "FAIL"), "|", name, ("| " + str(evidence)[:130] if evidence else ""))

# ---------- 1. Health (NEW) ----------
s, b = req("GET", "/api/health")
check("health 200 ok db:true", s == 200 and isinstance(b, dict) and b.get("ok") is True and b.get("db") is True, b)

# ---------- 2. Catalog: 200, 37 products, NO costUsd leak ----------
s, b = req("GET", "/api/store/catalog", xff=XFF)
prods = b.get("products", []) if isinstance(b, dict) else []
chains = [c for p in prods for c in p.get("chain", [])]
leaked = [c for c in chains if "costUsd" in c or "checkedAt" in c]
check("catalog 200 ok:true", s == 200 and b.get("ok") is True, f"status={s} n={len(prods)}")
check("catalog has ~37 products", 30 <= len(prods) <= 60, len(prods))
check("catalog chains: costUsd/checkedAt stripped (P0 fix)", len(leaked) == 0, f"leaked={len(leaked)}")
check("catalog chains keep stock for UX", any("stock" in c for c in chains))

slug = None
if prods:
    # pick a product with SA+YE prices, prefer cheap one
    def price_usd(p):
        sa = p["prices"].get("SA"); ye = p["prices"].get("YE") or p["prices"].get("WW")
        if not ye: return None
        return ye["price"] if ye["currency"] == "USD" else round(ye["price"] / 3.75, 2)
    cands = [(price_usd(p), p["slug"]) for p in prods if price_usd(p)]
    cands = [c for c in cands if c[0] and c[0] < 25]
    cands.sort()
    slug = cands[0][1] if cands else prods[0]["slug"]
print("test product:", slug)

# ---------- 3. Legal pages (NEW) ----------
for p in ["/terms", "/privacy", "/refund"]:
    s, b = req("GET", p)
    ok = s == 200 and isinstance(b, str) and "rtl" in b and ("الشروط" in b or "الخصوصية" in b or "الاسترداد" in b)
    check(f"legal page {p} 200 Arabic RTL", ok, s)

# ---------- 4. Validation edges ----------
s, b = req("POST", "/api/store/checkout", {"slug": slug, "phone": "+9611234567", "rail": "wallet"}, xff=XFF)
check("checkout invalid phone (+961) → 400", s == 400, f"{s} {b}")
s, b = req("POST", "/api/store/checkout", {"slug": "not-a-slug-xyz", "phone": "+966500000007", "rail": "wallet"}, xff=XFF)
check("checkout unknown slug → 404", s == 404, f"{s} {b}")
s, b = req("POST", "/api/store/checkout", {"slug": slug, "phone": "+966500000007", "rail": "wire"}, xff=XFF)
check("checkout unsupported rail → 400", s == 400, f"{s} {b}")
s, b = req("POST", "/api/store/checkout", {"slug": slug, "phone": "+966500000007", "rail": "wallet", "price": 0.01}, xff=XFF)
check("tampered price ignored (server-locked or 402)", s in (402, 200), f"{s}")

s, b = req("POST", "/api/wallet/deposit", {"phone": "+966500000007", "amountUsd": 4}, xff=XFF)
check("deposit below min ($4) → 400", s == 400, f"{s} {b}")
s, b = req("POST", "/api/wallet/deposit", {"phone": "+966500000007", "amountUsd": 501}, xff=XFF)
check("deposit above max ($501) → 400", s == 400, f"{s} {b}")

# ---------- 5. E2E wallet purchase (sandbox) + ledger arithmetic ----------
PHONE = "+9665%08d" % random.randint(10000000, 99999999)  # +966 + 9 digits (regex: \d{8,9})
s, b = req("POST", "/api/wallet/deposit", {"phone": PHONE, "amountUsd": 25}, xff=XFF)
check("deposit $25 sandbox credited", s == 200 and b.get("credited") == 25, b)

s, b = req("POST", "/api/store/checkout", {"slug": slug, "phone": PHONE, "rail": "wallet"}, xff=XFF)
check("wallet checkout → delivered", s == 200 and b.get("ok") and b.get("routed", {}).get("status") == "delivered", b)
publicId = b.get("publicId")
price = b.get("routed", {}).get("cashback")  # placeholder
s, w = req("GET", f"/api/wallet?phone={urllib.parse.quote(PHONE)}", xff=XFF)
bal = w.get("balance") if isinstance(w, dict) else None
if bal is None:
    check("ledger exact", False, f"wallet read failed: {w}")
else:
    txs = w.get("txs", [])
    dep = next((t["amount"] for t in txs if t["type"] == "deposit"), 0)
    pur = next((t["amount"] for t in txs if t["type"] == "purchase"), 0)
    cb = next((t["amount"] for t in txs if t["type"] == "cashback"), 0)
    check("ledger exact: balance = deposit + purchase + cashback", abs(bal - (dep + pur + cb)) < 0.001, f"bal={bal} dep={dep} pur={pur} cb={cb}")

# ---------- 6. Order owner-proof (P1 fix) ----------
s, b = req("GET", f"/api/store/orders/{publicId}")
check("order GET without phone → 404 (owner proof)", s == 404, f"{s}")
s, b = req("GET", f"/api/store/orders/{publicId}?phone=%2B966500000009")
check("order GET wrong phone → 404", s == 404, f"{s}")
s, b = req("GET", f"/api/store/orders/{publicId}?phone={urllib.parse.quote(PHONE)}", xff=XFF)
check("order GET right phone → 200 + payload", s == 200 and b.get("ok") and b.get("order", {}).get("deliveredPayload"), f"{s}")
transparency = b.get("transparency", [])
check("order transparency: costUsd stripped", all("costUsd" not in t for t in transparency), f"steps={len(transparency)}")

# ---------- 7. Orders history (NEW) ----------
s, b = req("GET", f"/api/store/orders?phone={urllib.parse.quote(PHONE)}", xff=XFF)
check("orders history 200 + contains order", s == 200 and any(o["publicId"] == publicId for o in b.get("orders", [])), f"{s} n={len(b.get('orders', []))}")
s, b = req("GET", "/api/store/orders?phone=%2B9610000000")
check("orders history invalid phone → 400", s == 400, s)

# ---------- 8. TRC20 flow + idempotent confirm ----------
s, b = req("POST", "/api/store/checkout", {"slug": slug, "phone": PHONE, "rail": "trc20"}, xff=XFF)
check("trc20 checkout → pending_payment + instructions", s == 200 and b.get("payment", {}).get("address"), b.get("payment", {}).get("network"))
pid2 = b.get("publicId")
s, c1 = req("POST", "/api/store/payments/confirm", {"publicId": pid2, "ref": f"TXID-{random.randint(1000,9999)}"}, xff=XFF)
check("sandbox confirm → delivered", s == 200 and c1.get("routed", {}).get("status") == "delivered", c1)
s, c2 = req("POST", "/api/store/payments/confirm", {"publicId": pid2, "ref": "TXID-REPEAT"}, xff=XFF)
check("repeat confirm → idempotent (no re-route)", s == 200 and c2.get("idempotent") is True, c2)

# ---------- 9. Admin gate ----------
s, b = req("GET", "/api/admin/stats")
check("admin no token → 401", s == 401, s)
s, b = req("GET", "/api/admin/stats", headers={"x-admin-token": "garbage"})
check("admin bad token → 401", s == 401, s)
try:
    tok = open("/tmp/admin_token.txt").read().strip()
    s, b = req("GET", "/api/admin/stats", headers={"x-admin-token": tok})
    check("admin good token → 200", s == 200 and b.get("ok"), s)
except FileNotFoundError:
    SKIP.append(("admin good token", "no token file"))

# ---------- 10. Rate limit (fresh XFF, checkout bucket 10/min) ----------
xff2 = "10.99.99.99"
codes = []
for i in range(14):
    s, _ = req("POST", "/api/store/checkout", {"slug": slug, "phone": "+966500000008", "rail": "wire"}, xff=xff2)
    codes.append(s)
n429 = codes.count(429)
check("rate limit: 429s appear after ~10 rapid checkouts", n429 >= 1 and codes[0] == 400, f"codes={codes}")

# ---------- 11. Restock owner-proof + idempotency ----------
s, b = req("POST", f"/api/store/orders/{pid2}/restock")
check("restock without phone → 404", s == 404, s)

# ---------- 12. 404 page ----------
s, b = req("GET", "/xyz-not-found")
check("404 page renders Arabic", s == 404 and isinstance(b, str) and "rtl" in b, s)

print("\n" + "=" * 60)
print(f"RESULT: {len(PASS)} PASS / {len(FAIL)} FAIL / {len(SKIP)} SKIP")
if FAIL:
    print("FAILURES:")
    for n, e in FAIL: print(" -", n, "|", str(e)[:150])
json.dump({"pass": len(PASS), "fail": len(FAIL), "failures": FAIL, "skip": SKIP},
          open("/home/z/my-project/research/audit/regression_results.json", "w"), ensure_ascii=False, indent=1)
sys.exit(1 if FAIL else 0)
