#!/usr/bin/env python3
"""MEC DB AUDIT: connect to production Supabase Postgres (creds fetched from Railway API,
never printed) and audit schema/tables/constraints/indexes/RLS. READ-ONLY."""
import json, os, re, urllib.request

# --- 1. Get DB credentials from Railway variables API ---
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
raw = r.get("data", {}).get("variables")
if not raw:
    raise SystemExit("cannot read variables: " + json.dumps(r)[:300])
# variables returns a JSON-ish dict string
vars = json.loads(raw) if isinstance(raw, str) else raw
DIRECT = None
for k, v in vars.items():
    if k.startswith("DIRECT") and isinstance(v, str) and v.startswith("postgresql"):
        DIRECT = v
DB_URL = DIRECT or vars.get("DATABASE_URL")
print(f"using {'DIRECT' if DIRECT else 'POOLED'} connection (value hidden)")

# --- 2. Parse URL for pg8000 ---
m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/(\w+)", DB_URL)
user, password, host, port, dbname = m.groups()

import pg8000.native
con = pg8000.native.Connection(user=user, password=password, host=host, port=int(port),
                               database=dbname, timeout=30, ssl_context=True)
print("CONNECTED to Supabase Postgres\n")

out = {}

def run(label, sql):
    try:
        rows = con.run(sql)
        out[label] = [dict(zip([c['name'] for c in con.columns], row)) for row in rows]
        return out[label]
    except Exception as e:
        out[label] = [{"error": str(e)[:200]}]
        return out[label]

# A. tables + row counts
tbls = run("tables", """SELECT table_name, table_schema FROM information_schema.tables
  WHERE table_schema='public' ORDER BY table_name""")
print("== TABLES ==")
for t in tbls:
    name = t["table_name"]
    try:
        cnt = con.run(f'SELECT COUNT(*) AS c FROM "{name}"')[0][0]
    except Exception as e:
        cnt = f"ERR {str(e)[:60]}"
    print(f"  {name}: {cnt} rows")
    t["rowCount"] = cnt

# B. columns per table
print("\n== COLUMNS ==")
for t in tbls:
    name = t["table_name"]
    cols = run(f"cols_{name}", f"""SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns WHERE table_schema='public' AND table_name='{name}'
      ORDER BY ordinal_position""")
    print(f"  {name}: {', '.join(c['column_name'] for c in cols)}")

# C. constraints
cons = run("constraints", """SELECT tc.table_name, tc.constraint_type, tc.constraint_name,
  kcu.column_name, ccu.table_name AS foreign_table
  FROM information_schema.table_constraints tc
  LEFT JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
  LEFT JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name=ccu.constraint_name
  WHERE tc.table_schema='public' ORDER BY tc.table_name, tc.constraint_type""")
print("\n== CONSTRAINTS ==")
seen = set()
for c in cons:
    key = (c["table_name"], c["constraint_name"], c["constraint_type"])
    if key in seen: continue
    seen.add(key)
    print(f"  {c['table_name']}.{c['constraint_name']}: {c['constraint_type']}"
          + (f" -> {c['foreign_table']}" if c.get("foreign_table") else ""))

# D. indexes
idx = run("indexes", """SELECT tablename, indexname, indexdef FROM pg_indexes
  WHERE schemaname='public' ORDER BY tablename, indexname""")
print("\n== INDEXES ==")
for i in idx:
    print(f"  {i['indexname']}: {i['indexdef'][:100]}")

# E. RLS policies
rls = run("rls_tables", """SELECT relname, relrowsecurity FROM pg_class
  JOIN pg_namespace ON pg_class.relnamespace=pg_namespace.oid
  WHERE nspname='public' AND relkind='r'""")
print("\n== RLS per table ==")
for t in rls:
    print(f"  {t['relname']}: RLS={'ON' if t['relrowsecurity'] else 'OFF'}")
pol = run("rls_policies", """SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
  FROM pg_policies WHERE schemaname='public'""")
for p in pol:
    print(f"  policy {p['tablename']}.{p['policyname']}: {p['cmd']} roles={p['roles']}")

# F. roles/grants (am I superuser? what role is the app?)
who = run("current_user", "SELECT current_user, current_setting('role') as role, version() as v")
print("\n== CONNECTION ROLE ==")
for w in who: print(f"  user={w['current_user']} role={w['role']}")

con.run("COMMIT") if False else None
con.close()
json.dump(out, open("/home/z/my-project/research/live_capture/db_audit.json", "w"),
          ensure_ascii=False, indent=1, default=str)
print("\nSaved -> research/live_capture/db_audit.json")
