#!/usr/bin/env python3
"""MEC DB FIXES: apply hot-path indexes + REVOKE anon/authenticated access
(kills Supabase PostgREST exposure — RLS was OFF on all 10 tables).
Read-only credentials fetched from Railway API; never printed."""
import json, os, re, urllib.request

API = "https://backboard.railway.com/graphql/v2"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
PROJECT = "a574c5d0-f136-446f-b8c9-2ceba79e4214"
ENV = "89138798-9412-4829-be22-3b913df05fe5"
SVC = "79f9401c-3598-4cbe-a5fe-d50c13191820"

def gql(q, v=None):
    payload = json.dumps({"query": q, "variables": v or {}}).encode()
    req = urllib.request.Request(API, data=payload, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "User-Agent": "mec-audit/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

r = gql("""query($projectId: String!, $environmentId: String!, $serviceId: String!) {
  variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
}""", {"projectId": PROJECT, "environmentId": ENV, "serviceId": SVC})
vars = json.loads(r["data"]["variables"]) if isinstance(r["data"]["variables"], str) else r["data"]["variables"]
DIRECT = next(v for k, v in vars.items() if k.startswith("DIRECT") and str(v).startswith("postgresql"))
m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/(\w+)", DIRECT)
user, password, host, port, dbname = m.groups()

import pg8000.native
con = pg8000.native.Connection(user=user, password=password, host=host, port=int(port),
                               database=dbname, timeout=30, ssl_context=True)
print("CONNECTED — applying fixes\n")

fixes = [
    # 1. Hot-path indexes (audit: Order.phone/createdAt, WalletTx.walletId, Attempt.orderId, ChainLink.productId, GeoPrice.productId missing)
    ('CREATE INDEX IF NOT EXISTS "Order_phone_idx" ON public."Order"(phone)', "index Order.phone"),
    ('CREATE INDEX IF NOT EXISTS "Order_createdAt_idx" ON public."Order"("createdAt" DESC)', "index Order.createdAt DESC"),
    ('CREATE INDEX IF NOT EXISTS "Order_status_idx" ON public."Order"(status)', "index Order.status"),
    ('CREATE INDEX IF NOT EXISTS "WalletTx_walletId_idx" ON public."WalletTx"("walletId")', "index WalletTx.walletId"),
    ('CREATE INDEX IF NOT EXISTS "Attempt_orderId_idx" ON public."Attempt"("orderId")', "index Attempt.orderId"),
    ('CREATE INDEX IF NOT EXISTS "ChainLink_productId_idx" ON public."ChainLink"("productId")', "index ChainLink.productId"),
    ('CREATE INDEX IF NOT EXISTS "GeoPrice_productId_idx" ON public."GeoPrice"("productId")', "index GeoPrice.productId"),
    # 2. PostgREST hardening: app connects as postgres (owner) — anon/authenticated roles get NOTHING
    ('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon', "revoke tables from anon"),
    ('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM authenticated', "revoke tables from authenticated"),
    ('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon', "revoke sequences from anon"),
    ('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM authenticated', "revoke sequences from authenticated"),
    ('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon', "revoke functions from anon"),
    ('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM authenticated', "revoke functions from authenticated"),
    # 3. Belt & suspenders: enable RLS too (owner bypasses it; PostgREST roles get blocked twice)
    ('ALTER TABLE public."Order" ENABLE ROW LEVEL SECURITY', "RLS Order"),
    ('ALTER TABLE public."Wallet" ENABLE ROW LEVEL SECURITY', "RLS Wallet"),
    ('ALTER TABLE public."WalletTx" ENABLE ROW LEVEL SECURITY', "RLS WalletTx"),
    ('ALTER TABLE public."Product" ENABLE ROW LEVEL SECURITY', "RLS Product"),
    ('ALTER TABLE public."ChainLink" ENABLE ROW LEVEL SECURITY', "RLS ChainLink"),
    ('ALTER TABLE public."GeoPrice" ENABLE ROW LEVEL SECURITY', "RLS GeoPrice"),
    ('ALTER TABLE public."Supplier" ENABLE ROW LEVEL SECURITY', "RLS Supplier"),
    ('ALTER TABLE public."Attempt" ENABLE ROW LEVEL SECURITY', "RLS Attempt"),
    ('ALTER TABLE public."SyncLog" ENABLE ROW LEVEL SECURITY', "RLS SyncLog"),
    ('ALTER TABLE public."Waitlist" ENABLE ROW LEVEL SECURITY', "RLS Waitlist"),
]

ok, fail = 0, 0
for sql, label in fixes:
    try:
        con.run(sql)
        print(f"  ✓ {label}")
        ok += 1
    except Exception as e:
        msg = str(e)[:120]
        if "already exists" in msg.lower():
            print(f"  = {label} (already)")
            ok += 1
        else:
            print(f"  ✗ {label}: {msg}")
            fail += 1

# verify: index count + grants
idx = con.run("SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public'")
print(f"\nPublic indexes now: {idx[0][0]}")
grants = con.run("""SELECT grantee, privilege_type FROM information_schema.role_table_grants
  WHERE table_schema='public' AND grantee IN ('anon','authenticated') LIMIT 10""")
print(f"anon/authenticated grants remaining: {len(grants)}")

con.close()
print(f"\nDONE: {ok} ok, {fail} failed")
