#!/usr/bin/env python3
"""AUDIT-4: READ-ONLY database & Supabase audit (agent4).
Reuses the Railway-API credential pattern from scripts/db_audit.py (creds never printed).
GUARANTEE: every executed SQL statement must start with SELECT / EXPLAIN / WITH —
no writes, no locks, no DDL. EXPLAIN is used WITHOUT ANALYZE (no execution).
Output: console + /home/z/my-project/research/audit/agent4_db_audit.json
"""
import json, os, re, urllib.request

ROOT = "/home/z/my-project"
API = "https://backboard.railway.com/graphql/v2"
PROJECT = "a574c5d0-f136-446f-b8c9-2ceba79e4214"
ENV = "89138798-9412-4829-be22-3b913df05fe5"
SVC = "79f9401c-3598-4cbe-a5fe-d50c13191820"

# --- 0. Load RAILWAY_TOKEN from .env (never printed) ---
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
if not TOKEN and os.path.exists(f"{ROOT}/.env"):
    for line in open(f"{ROOT}/.env"):
        line = line.strip()
        if line.startswith("RAILWAY_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
if not TOKEN:
    raise SystemExit("RAILWAY_TOKEN not found in env or .env")
print("RAILWAY_TOKEN: loaded (value hidden)")

def gql(q, v=None):
    payload = json.dumps({"query": q, "variables": v or {}}).encode()
    req = urllib.request.Request(API, data=payload, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "User-Agent": "audit4/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

r = gql("""query($projectId: String!, $environmentId: String!, $serviceId: String!) {
  variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
}""", {"projectId": PROJECT, "environmentId": ENV, "serviceId": SVC})
raw = r.get("data", {}).get("variables")
if not raw:
    raise SystemExit("cannot read variables: " + json.dumps(r)[:300])
vars = json.loads(raw) if isinstance(raw, str) else raw
DIRECT = None
for k, v in vars.items():
    if k.startswith("DIRECT") and isinstance(v, str) and v.startswith("postgresql"):
        DIRECT = v
DB_URL = DIRECT or vars.get("DATABASE_URL")
print(f"using {'DIRECT' if DIRECT else 'POOLED'} connection (value hidden)")

m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/([^\s?/]+)", DB_URL)
user, password, host, port, dbname = m.groups()

import pg8000.native
con = pg8000.native.Connection(user=user, password=password, host=host, port=int(port),
                               database=dbname, timeout=30, ssl_context=True)
print("CONNECTED to Supabase Postgres\n")

OUT = {}
ALLOWED = re.compile(r"^\s*(SELECT|EXPLAIN|WITH)\b", re.IGNORECASE)

def run(label, sql):
    """Read-only guarded executor: SELECT/EXPLAIN/WITH only, single statement."""
    s = sql.strip().rstrip(";")
    if not ALLOWED.match(s):
        OUT[label] = [{"error": "BLOCKED (not SELECT/EXPLAIN/WITH)"}]
        print(f"  !! {label}: BLOCKED non-read statement")
        return OUT[label]
    if ";" in s:
        OUT[label] = [{"error": "BLOCKED (multi-statement)"}]
        print(f"  !! {label}: BLOCKED multi-statement")
        return OUT[label]
    try:
        rows = con.run(s)
        OUT[label] = [dict(zip([c["name"] for c in con.columns], row)) for row in rows]
    except Exception as e:
        OUT[label] = [{"error": str(e)[:300]}]
    return OUT[label]

def mask_phone(p):
    if not isinstance(p, str) or len(p) < 6: return p
    return p[:6] + "***" + p[-2:] if len(p) > 8 else p[:6] + "***"

def hdr(t):
    print(f"\n{'='*72}\n== {t}\n{'='*72}")

# ================= SECTION 1: server & connection role =================
hdr("1. SERVER & CONNECTION ROLE")
run("server", "SELECT current_user, current_setting('role') AS role, version() AS v, now() AT TIME ZONE 'utc' AS now_utc")
for w in OUT["server"]:
    print(f"  user={w.get('current_user')} role={w.get('role')}")
    print(f"  version={str(w.get('v'))[:70]} now_utc={w.get('now_utc')}")

# ================= SECTION 2: tables, row counts, sizes =================
hdr("2. TABLES / ROW COUNTS / SIZES")
tables = run("tables", """SELECT table_name FROM information_schema.tables
  WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name""")
for t in tables:
    n = t["table_name"]
    run(f"count_{n}", f'SELECT COUNT(*) AS c FROM "{n}"')
    run(f"size_{n}", f"""SELECT pg_size_pretty(pg_total_relation_size('"public"."{n}"'::regclass)) AS total_size,
      pg_total_relation_size('"public"."{n}"'::regclass) AS total_bytes FROM (SELECT 1) x""")
    cnt = OUT[f"count_{n}"][0].get("c", "?")
    sz = OUT[f"size_{n}"][0].get("total_size", "?")
    print(f"  {n}: rows={cnt} size={sz}")
expected_tables = {"Product","ChainLink","GeoPrice","Order","Attempt","Supplier",
                   "SyncLog","Waitlist","Wallet","WalletTx"}
found_tables = {t["table_name"] for t in tables}
print(f"  EXPECTED 10 tables; FOUND {len(found_tables)}")
print(f"  missing vs plan: {sorted(expected_tables-found_tables) or 'NONE'}")
print(f"  extra vs plan:   {sorted(found_tables-expected_tables) or 'NONE'}")

# ================= SECTION 3: columns vs prisma/schema.prisma (drift) =================
hdr("3. COLUMN DRIFT vs prisma/schema.prisma")
prisma_src = open(f"{ROOT}/prisma/schema.prisma").read()
prisma_models = {}
for mm in re.finditer(r"model (\w+) \{([^}]*)\}", prisma_src):
    name, body = mm.groups()
    cols = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("@@"): continue
        fm = re.match(r"(\w+)\s+([A-Za-z\[\]?]+)", line)
        if not fm: continue
        fld, typ = fm.groups()
        if typ.startswith("String") or typ.startswith("Int") or typ.startswith("Float") \
           or typ.startswith("Boolean") or typ.startswith("DateTime"):
            cols.append(fld)  # scalar only (relations excluded)
    prisma_models[name] = cols
drift_report = {}
for model, cols in sorted(prisma_models.items()):
    run(f"cols_{model}", f"""SELECT column_name, data_type, is_nullable FROM information_schema.columns
      WHERE table_schema='public' AND table_name='{model}' ORDER BY ordinal_position""")
    live = {c["column_name"]: c for c in OUT[f"cols_{model}"] if "error" not in c}
    expected = set(cols)
    missing_db = sorted(expected - set(live))
    extra_db = sorted(set(live) - expected)
    drift_report[model] = {"prisma_fields": len(expected), "live_columns": len(live),
                           "missing_in_db": missing_db, "extra_in_db": extra_db}
    status = "MATCH" if not missing_db and not extra_db else "DRIFT"
    print(f"  {model}: {status} (prisma={len(expected)} live={len(live)})" +
          (f" missing_db={missing_db}" if missing_db else "") +
          (f" extra_db={extra_db}" if extra_db else ""))
OUT["drift_report"] = drift_report

# ================= SECTION 4: constraints =================
hdr("4. PK / FK / UNIQUE CONSTRAINTS")
run("constraints", """SELECT tc.table_name, tc.constraint_type, tc.constraint_name,
  string_agg(kcu.column_name, ',' ORDER BY kcu.ordinal_position) AS cols,
  ccu.table_name AS fk_table
  FROM information_schema.table_constraints tc
  LEFT JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
    AND tc.table_schema=kcu.table_schema
  LEFT JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name=ccu.constraint_name
    AND tc.constraint_type='FOREIGN KEY'
  WHERE tc.table_schema='public'
  GROUP BY tc.table_name, tc.constraint_type, tc.constraint_name, ccu.table_name
  ORDER BY tc.table_name, tc.constraint_type""")
seen = set()
for c in OUT["constraints"]:
    key = (c["table_name"], c["constraint_name"], c["constraint_type"])
    if key in seen or "error" in c: continue
    seen.add(key)
    print(f"  {c['table_name']}: [{c['constraint_type']}] {c['constraint_name']}({c.get('cols')})"
          + (f" -> {c['fk_table']}" if c.get("fk_table") else ""))

# ================= SECTION 5: indexes (+ verify 7 hot-path) =================
hdr("5. INDEXES (verify hot-path set)")
run("indexes", """SELECT tablename, indexname, indexdef FROM pg_indexes
  WHERE schemaname='public' ORDER BY tablename, indexname""")
for i in OUT["indexes"]:
    if "error" in i: continue
    print(f"  {i['indexname']}: {i['indexdef'][:120]}")
HOTPATH = ["Order.phone", "Order.createdAt", "WalletTx.walletId", "Attempt.orderId",
           "ChainLink.productId", "GeoPrice.productId"]
idx_keys = set()
for i in OUT["indexes"]:
    if "error" in i: continue
    d = i["indexdef"]
    mm = re.search(r'\(([^)]+)\)', d)
    if mm and "CREATE" in d:
        idx_keys.add(f'{i["tablename"]}.{mm.group(1).split()[0].strip("\"")}')
print("\n  HOT-PATH CHECK (worklog 18-19 claims 7 indexes applied):")
for h in HOTPATH:
    ok = h in idx_keys
    print(f"    {h}: {'OK' if ok else 'MISSING'}")
non_pk = [i for i in OUT["indexes"] if "error" not in i and "pkey" not in i["indexname"]]
print(f"  total non-PK indexes: {len(non_pk)} (expect >= 7 hot-path + uniques + prisma idx)")

# ================= SECTION 6: RLS + policies =================
hdr("6. RLS & POLICIES (per table)")
run("rls", """SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity,
  (SELECT COUNT(*) FROM pg_policies p WHERE p.schemaname='public' AND p.tablename=c.relname) AS policy_count
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname""")
for t in OUT["rls"]:
    if "error" in t: continue
    print(f"  {t['relname']}: RLS={'ON' if t['relrowsecurity'] else 'OFF'} "
          f"FORCE={'ON' if t['relforcerowsecurity'] else 'off'} policies={t['policy_count']}")
run("policies", """SELECT tablename, policyname, cmd, roles, permissive FROM pg_policies
  WHERE schemaname='public' ORDER BY tablename""")
if OUT["policies"] and "error" not in OUT["policies"][0]:
    for p in OUT["policies"]:
        print(f"    policy {p['tablename']}.{p['policyname']}: {p['cmd']} roles={p['roles']}")
else:
    print("  (no policies / not visible)")

# ================= SECTION 7: roles & grants (PostgREST lock) =================
hdr("7. SUPABASE ROLES & TABLE GRANTS")
run("roles", """SELECT rolname, rolsuper, rolcanlogin FROM pg_roles
  WHERE rolname IN ('anon','authenticated','service_role','postgrest','supabase_admin',
                    'supabase_read_only_user','authenticator','postgres')
  ORDER BY rolname""")
for x in OUT["roles"]:
    if "error" in x: continue
    print(f"  role {x['rolname']}: super={x['rolsuper']} canlogin={x['rolcanlogin']}")
supa_roles = [x["rolname"] for x in OUT["roles"] if "error" not in x]
tbl_names = [t["table_name"] for t in tables]
privs = ["SELECT","INSERT","UPDATE","DELETE"]
matrix = []
for role in ["anon","authenticated","service_role"]:
    if role not in supa_roles:
        print(f"  !! role {role} DOES NOT EXIST (PostgREST roles absent?)"); continue
    for tn in tbl_names:
        run(f"priv_{role}_{tn}",
            f"""SELECT has_table_privilege('{role}', 'public."{tn}"', 'SELECT') AS sel,
                has_table_privilege('{role}', 'public."{tn}"', 'INSERT') AS ins,
                has_table_privilege('{role}', 'public."{tn}"', 'UPDATE') AS upd,
                has_table_privilege('{role}', 'public."{tn}"', 'DELETE') AS del""")
        row = OUT[f"priv_{role}_{tn}"][0]
        row.update({"role": role, "table": tn}); matrix.append(row)
        if any(row[k] for k in ("sel","ins","upd","del")):
            print(f"  !! GRANT ACTIVE: {role} ON {tn}: "
                  + ",".join(k for k in ("sel","ins","upd","del") if row[k]))
OUT["privilege_matrix"] = matrix
anon_any = any(any(r[k] for k in ("sel","ins","upd","del")) for r in matrix if r["role"]=="anon")
auth_any = any(any(r[k] for k in ("sel","ins","upd","del")) for r in matrix if r["role"]=="authenticated")
sr_any = any(any(r[k] for k in ("sel","ins","upd","del")) for r in matrix if r["role"]=="service_role")
print(f"\n  SUMMARY: anon has ANY privilege: {anon_any} | authenticated: {auth_any} | service_role: {sr_any}")
# raw relacl entries (source of truth)
run("relacl", """SELECT c.relname, r.rolname AS grantee, a.privilege_type
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl, ACLDEFAULT('r', c.relowner)::aclitem[])) a
  JOIN pg_roles r ON r.oid=a.grantee
  WHERE n.nspname='public' AND c.relkind='r' AND r.rolname IN ('anon','authenticated','service_role')
  ORDER BY 1,2,3""")
grants_pubrest = [g for g in OUT["relacl"] if "error" not in g]
print(f"  relacl entries granted to PostgREST roles (anon/authenticated/service_role): {len(grants_pubrest)}")

# ================= SECTION 8: DATA INTEGRITY =================
hdr("8A. WALLET LEDGER INTEGRITY (balance = SUM(WalletTx)?)")
run("wallet_cols", """SELECT column_name FROM information_schema.columns
  WHERE table_schema='public' AND table_name='Wallet'""")
wallet_cols = [c["column_name"] for c in OUT["wallet_cols"] if "error" not in c]
print(f"  Wallet columns: {wallet_cols} (stored balance column: {'balance' in wallet_cols})")
run("wallet_balances", """SELECT w.id, w.phone, COALESCE(SUM(t.amount),0) AS derived_balance,
  COUNT(t.id) AS tx_count
  FROM "Wallet" w LEFT JOIN "WalletTx" t ON t."walletId"=w.id
  GROUP BY w.id, w.phone ORDER BY derived_balance DESC""")
tot_drift = 0
for w in OUT["wallet_balances"]:
    if "error" in w: continue
    print(f"  wallet {mask_phone(w['phone'])}: balance={w['derived_balance']:.2f} txs={w['tx_count']}")
if "balance" in wallet_cols:
    run("wallet_drift", """SELECT w.id, w.phone, w.balance AS stored, COALESCE(SUM(t.amount),0) AS derived
      FROM "Wallet" w LEFT JOIN "WalletTx" t ON t."walletId"=w.id
      GROUP BY w.id, w.phone, w.balance HAVING ABS(w.balance - COALESCE(SUM(t.amount),0)) > 0.005""")
    tot_drift = len([d for d in OUT["wallet_drift"] if "error" not in d])
    print(f"  stored-vs-derived drift wallets: {tot_drift}")
else:
    print("  -> architecture is derived-balance only (no stored balance column) => drift impossible by construction")
run("tx_by_type", """SELECT type, COUNT(*) AS n, ROUND(SUM(amount)::numeric,2) AS total
  FROM "WalletTx" GROUP BY type ORDER BY type""")
print("  WalletTx by type:")
for t in OUT["tx_by_type"]:
    if "error" in t: continue
    print(f"    {t['type']}: n={t['n']} total={t['total']}")
run("total_float", """SELECT ROUND(COALESCE(SUM(s.b),0)::numeric,2) AS total_customer_liability_usd
  FROM (SELECT COALESCE(SUM(t.amount),0) AS b FROM "Wallet" w
        LEFT JOIN "WalletTx" t ON t."walletId"=w.id GROUP BY w.id) s""")
print(f"  total customer float (sum of wallet balances): {OUT['total_float'][0]}")

hdr("8B. ORPHANED FOREIGN KEYS (expect 0 — FKs enforced)")
orphans = [
  ("orders->product",    """SELECT COUNT(*) AS c FROM "Order" o LEFT JOIN "Product" p ON p.id=o."productId" WHERE p.id IS NULL"""),
  ("attempts->order",    """SELECT COUNT(*) AS c FROM "Attempt" a LEFT JOIN "Order" o ON o.id=a."orderId" WHERE o.id IS NULL"""),
  ("chainlinks->product","""SELECT COUNT(*) AS c FROM "ChainLink" cl LEFT JOIN "Product" p ON p.id=cl."productId" WHERE p.id IS NULL"""),
  ("chainlinks->supplier","""SELECT COUNT(*) AS c FROM "ChainLink" cl LEFT JOIN "Supplier" s ON s.id=cl."supplierId" WHERE s.id IS NULL"""),
  ("geoprices->product", """SELECT COUNT(*) AS c FROM "GeoPrice" g LEFT JOIN "Product" p ON p.id=g."productId" WHERE p.id IS NULL"""),
  ("wallettx->wallet",   """SELECT COUNT(*) AS c FROM "WalletTx" t LEFT JOIN "Wallet" w ON w.id=t."walletId" WHERE w.id IS NULL"""),
  ("waitlist->product",  """SELECT COUNT(*) AS c FROM "Waitlist" wl LEFT JOIN "Product" p ON p.id=wl."productId" WHERE p.id IS NULL"""),
]
for label, sql in orphans:
    run(f"orphan_{label.split('->')[0].replace('>','_')}", sql)
    print(f"  {label}: {OUT[f'orphan_{label.split(chr(45)+chr(62))[0].replace(chr(62),chr(95))}'][0].get('c', '?')} broken")

hdr("8C. GEOPRICE COVERAGE (missing SA +966 / YE +967)")
run("geo_regions", """SELECT region, currency, COUNT(*) AS n FROM "GeoPrice" GROUP BY region, currency ORDER BY region""")
for g in OUT["geo_regions"]:
    if "error" in g: continue
    print(f"  region {g['region']} ({g['currency']}): {g['n']} rows")
run("geo_coverage", """SELECT p.slug, p.active,
  MAX(CASE WHEN gp.region='SA' THEN 1 ELSE 0 END) AS has_sa,
  MAX(CASE WHEN gp.region='YE' THEN 1 ELSE 0 END) AS has_ye,
  MAX(CASE WHEN gp.region='WW' THEN 1 ELSE 0 END) AS has_ww
  FROM "Product" p LEFT JOIN "GeoPrice" gp ON gp."productId"=p.id
  GROUP BY p.slug, p.active ORDER BY p.slug""")
missing_sa, missing_ye, missing_both = [], [], []
tot = 0
for row in OUT["geo_coverage"]:
    if "error" in row: continue
    tot += 1
    if not row["has_sa"] and not row["has_ye"] and not row["has_ww"]:
        missing_both.append(row["slug"])
    elif not row["has_sa"]:
        missing_sa.append(row["slug"])
    elif not row["has_ye"]:
        missing_ye.append(row["slug"])
print(f"  products total: {tot}")
print(f"  missing SA(+966): {len(missing_sa)} {missing_sa[:10]}")
print(f"  missing YE(+967): {len(missing_ye)} {missing_ye[:10]}")
print(f"  missing ALL regions (unsellable): {len(missing_both)} {missing_both[:10]}")

hdr("8D. DUPLICATE SLUGS / PRODUCT ACTIVITY")
run("dup_slug", """SELECT slug, COUNT(*) AS c FROM "Product" GROUP BY slug HAVING COUNT(*)>1""")
print(f"  duplicate slugs: {len([d for d in OUT['dup_slug'] if 'error' not in d])}")
run("product_active", """SELECT active, COUNT(*) AS c FROM "Product" GROUP BY active""")
for a in OUT["product_active"]:
    if "error" in a: continue
    print(f"  active={a['active']}: {a['c']} products")
run("active_no_chain", """SELECT COUNT(*) AS c FROM "Product" p
  WHERE p.active=true AND NOT EXISTS (SELECT 1 FROM "ChainLink" cl
  WHERE cl."productId"=p.id AND cl.active=true)""")
print(f"  ACTIVE products with NO active chain (JIT-dead): {OUT['active_no_chain'][0].get('c','?')}")
run("active_no_price", """SELECT COUNT(*) AS c FROM "Product" p
  WHERE p.active=true AND NOT EXISTS (SELECT 1 FROM "GeoPrice" g WHERE g."productId"=p.id)""")
print(f"  ACTIVE products with NO price rows: {OUT['active_no_price'][0].get('c','?')}")

hdr("8E. ORDER ANALYSIS (sandbox / status / rail)")
run("order_cols", """SELECT column_name FROM information_schema.columns
  WHERE table_schema='public' AND table_name='Order'""")
print(f"  Order columns: {[c['column_name'] for c in OUT['order_cols'] if 'error' not in c]}")
run("order_status", """SELECT status, COUNT(*) AS c FROM "Order" GROUP BY status ORDER BY c DESC""")
for s in OUT["order_status"]:
    if "error" in s: continue
    print(f"  status={s['status']}: {s['c']}")
run("order_rail", """SELECT rail, COUNT(*) AS c FROM "Order" GROUP BY rail""")
for s in OUT["order_rail"]:
    if "error" in s: continue
    print(f"  rail={s['rail']}: {s['c']}")
run("sandbox_orders", """SELECT COUNT(*) AS sandbox_payload,
  COUNT(*) FILTER (WHERE "deliveredPayload" LIKE 'SANDBOX%') AS marked
  FROM "Order" WHERE "deliveredPayload" IS NOT NULL""")
sb = OUT["sandbox_orders"][0]
print(f"  deliveredPayload rows: {sb.get('sandbox_payload')} (SANDBOX-marked: {sb.get('marked')})")
run("order_totals", """SELECT COUNT(*) AS n, ROUND(COALESCE(SUM("amountUsd"),0)::numeric,2) AS gmv_usd,
  ROUND(COALESCE(SUM("cashbackAmount"),0)::numeric,2) AS cashback,
  ROUND(COALESCE(SUM("apologyAmount"),0)::numeric,2) AS apology,
  ROUND(COALESCE(SUM("costUsd"),0)::numeric,2) AS cogs FROM "Order" """)
print(f"  order totals: {OUT['order_totals'][0]}")
run("attempt_stats", """SELECT "supplierCode", status, COUNT(*) AS c, ROUND(AVG("latencyMs")::numeric,0) AS avg_ms
  FROM "Attempt" GROUP BY "supplierCode", status ORDER BY c DESC""")
print("  attempts:")
for a in OUT["attempt_stats"]:
    if "error" in a: continue
    print(f"    {a['supplierCode']}/{a['status']}: {a['c']} (avg {a['avg_ms']}ms)")

hdr("8F. SUPPLIER REGISTRY")
run("suppliers", """SELECT code, name, kind, active, score, "failCount", "openUntil"
  FROM "Supplier" ORDER BY code""")
for s in OUT["suppliers"]:
    if "error" in s: continue
    print(f"  {s['code']}: {s['name']} [{s['kind']}] active={s['active']} score={s['score']} fails={s['failCount']}")

hdr("8G. SYNCLOG RECENCY")
run("synclog_recent", """SELECT "supplierCode", ok, COUNT(*) AS n, MAX("createdAt") AS last_at
  FROM "SyncLog" GROUP BY "supplierCode", ok ORDER BY last_at DESC""")
for s in OUT["synclog_recent"]:
    if "error" in s: continue
    print(f"  {s['supplierCode']} ok={s['ok']}: {s['n']} runs, last={s['last_at']}")
run("synclog_last3", """SELECT "supplierCode", ok, "productsSeen", matched, changed, "inStockNow",
  "balanceUsd", "createdAt" FROM "SyncLog" ORDER BY "createdAt" DESC LIMIT 3""")
for s in OUT["synclog_last3"]:
    if "error" in s: continue
    print(f"  last: {s['createdAt']} {s['supplierCode']} ok={s['ok']} seen={s['productsSeen']} matched={s['matched']} changed={s['changed']} bal={s['balanceUsd']}")

# ================= SECTION 9: EXPLAIN (plan only, NO ANALYZE) =================
hdr("9. EXPLAIN PLANS (planning only — no execution)")
explain_queries = {
  "catalog_join": """EXPLAIN SELECT p.slug, gp.region, gp.price, cl.priority, cl."costUsd", s.code
    FROM "Product" p
    LEFT JOIN "GeoPrice" gp ON gp."productId" = p.id
    LEFT JOIN "ChainLink" cl ON cl."productId" = p.id AND cl.active = true
    LEFT JOIN "Supplier" s ON s.id = cl."supplierId"
    WHERE p.active = true ORDER BY p.name""",
  "wallet_balance_agg": """EXPLAIN SELECT COALESCE(SUM(amount),0) FROM "WalletTx" WHERE "walletId" = 'aaaaaaaaaaaaaaaaaaaaaaaa'""",
  "attempts_by_order": """EXPLAIN SELECT * FROM "Attempt" WHERE "orderId" = 'aaaaaaaaaaaaaaaaaaaaaaaa' ORDER BY "createdAt" ASC""",
  "orders_recent_12": """EXPLAIN SELECT * FROM "Order" ORDER BY "createdAt" DESC LIMIT 12""",
  "chains_by_product_active": """EXPLAIN SELECT * FROM "ChainLink" WHERE "productId" = 'aaaaaaaaaaaaaaaaaaaaaaaa' AND active = true ORDER BY priority ASC""",
  "wallettx_history": """EXPLAIN SELECT * FROM "WalletTx" WHERE "walletId" = 'aaaaaaaaaaaaaaaaaaaaaaaa' ORDER BY "createdAt" DESC LIMIT 50""",
}
for label, sql in explain_queries.items():
    run(f"explain_{label}", sql)
    print(f"\n  --- {label} ---")
    for row in OUT[f"explain_{label}"]:
        for k, v in row.items():
            if v is not None: print(f"    {v}")

# ================= SECTION 10: scan statistics =================
hdr("10. PG_STAT SCAN USAGE (seq vs idx since stats reset)")
run("scan_stats", """SELECT relname, n_live_tup, seq_scan, seq_tup_read, idx_scan,
  pg_size_pretty(pg_total_relation_size(relid)) AS size
  FROM pg_stat_user_tables WHERE schemaname='public' ORDER BY relname""")
for s in OUT["scan_stats"]:
    if "error" in s: continue
    print(f"  {s['relname']}: live={s['n_live_tup']} seq_scan={s['seq_scan']} idx_scan={s['idx_scan']} size={s['size']}")

# ================= SECTION 11: backup / recovery evidence =================
hdr("11. BACKUP / RECOVERY EVIDENCE (read-only catalog)")
run("replication_slots", "SELECT slot_name, slot_type, active, database FROM pg_replication_slots")
print("  replication slots (WAL consumers / PITR evidence):")
for s in OUT["replication_slots"]:
    if "error" in s: print(f"    {s}")
    else: print(f"    {s['slot_name']} ({s['slot_type']}, active={s['active']}, db={s['database']})")
if all("error" in s for s in OUT["replication_slots"]):
    print("    (not readable or none)")
run("archiver", """SELECT archived_count, failed_count, last_archived_wal, last_archived_time
  FROM pg_stat_archiver""")
print(f"  archiver: {OUT['archiver'][0]}")
run("schemas_list", """SELECT schema_name FROM information_schema.schemata
  WHERE schema_name NOT LIKE 'pg_%' AND schema_name <> 'information_schema' ORDER BY 1""")
print(f"  non-system schemas: {[s['schema_name'] for s in OUT['schemas_list'] if 'error' not in s]}")
run("extensions", "SELECT extname, extversion FROM pg_extension ORDER BY extname")
print(f"  extensions: {[e['extname'] for e in OUT['extensions'] if 'error' not in e]}")
run("wal_level", "SELECT setting AS wal_level FROM pg_settings WHERE name='wal_level'")
print(f"  wal_level: {OUT['wal_level'][0].get('wal_level','?')} (replica/logical needed for PITR)")

con.close()
outpath = f"{ROOT}/research/audit/agent4_db_audit.json"
json.dump(OUT, open(outpath, "w"), ensure_ascii=False, indent=1, default=str)
print(f"\nSaved -> {outpath}")
print("AUDIT-4 COMPLETE — read-only, no modifications made.")
