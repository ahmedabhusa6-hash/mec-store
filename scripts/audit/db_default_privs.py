#!/usr/bin/env python3
"""MEC-20 DB FIX (P2, AUDIT-4): pg_default_acl still auto-grants anon/authenticated
full DML on FUTURE tables in public schema (the 18-19 REVOKE covered existing
tables only). This closes the default-privileges gap. Uses the same Railway
variables + pg8000 pattern as scripts/db_audit.py. Credentials NEVER printed."""
import json, re, urllib.request, os

API = "https://backboard.railway.com/graphql/v2"
TOKEN = ""
with open('/home/z/my-project/.env') as f:
    for line in f:
        if line.startswith('RAILWAY_TOKEN='):
            TOKEN = line.strip().split('=', 1)[1]
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
vars = json.loads(raw) if isinstance(raw, str) else raw
DB_URL = next((v for k, v in vars.items()
               if k.startswith("DIRECT") and isinstance(v, str) and v.startswith("postgresql")), vars["DATABASE_URL"])

m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/(\w+)", DB_URL)
user, password, host, port, dbname = m.groups()

import pg8000.native
con = pg8000.native.Connection(user=user, password=password, host=host, port=int(port), database=dbname)

# 1) BEFORE: show current default ACLs for anon/authenticated
before = con.run("""
  SELECT pg_get_userbyid(defaclrole) AS grantor, defaclnamespace::regnamespace AS schema, defaclobjtype, defaclacl
  FROM pg_default_acl
  WHERE defaclacl::text LIKE '%anon%' OR defaclacl::text LIKE '%authenticated%'
""")
print("BEFORE default ACL entries touching anon/authenticated:", len(before))
for row in before:
    print("  grantor=%s schema=%s type=%s" % (row[0], row[1], row[2]))

# 2) FIX: revoke future-table default privileges from anon/authenticated
#    for every granting role that currently grants to them (postgres + supabase_admin)
for role in [r[0] for r in before]:
    try:
        con.run(f"SET ROLE \"{role}\"")
    except Exception as e:
        print(f"  SKIP role={role}: cannot SET ROLE ({str(e)[:80]}) — manual action needed")
        continue
    try:
        con.run("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated")
        con.run("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated")
        con.run("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM anon, authenticated")
        print(f"  REVOKED future default privileges as role={role}")
    except Exception as e:
        print(f"  FAILED role={role}: {str(e)[:120]}")
    finally:
        con.run("RESET ROLE")

# 3) AFTER: verify
after = con.run("""
  SELECT pg_get_userbyid(defaclrole) AS grantor, defaclnamespace::regnamespace AS schema, defaclobjtype, defaclacl
  FROM pg_default_acl
  WHERE defaclacl::text LIKE '%anon%' OR defaclacl::text LIKE '%authenticated%'
""")
print("AFTER default ACL entries touching anon/authenticated:", len(after))

# 4) Also confirm existing tables still have RLS + no anon grants (regression check)
rls = con.run("""
  SELECT c.relname, c.relrowsecurity,
    count(p.policyname) AS policies
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  LEFT JOIN pg_policies p ON p.schemaname = n.nspname AND p.tablename = c.relname
  WHERE n.nspname = 'public' AND c.relkind = 'r'
  GROUP BY c.relname, c.relrowsecurity ORDER BY c.relname
""")
bad = [r for r in rls if not r[1]]
print("Tables:", len(rls), "| RLS-enabled:", len(rls) - len(bad), "| RLS-missing:", [r[0] for r in bad])
grants = con.run("""
  SELECT table_name, grantee FROM information_schema.role_table_grants
  WHERE table_schema = 'public' AND grantee IN ('anon', 'authenticated')
""")
print("anon/authenticated grants on existing tables:", len(grants), "(expect 0)")
con.close()
print("DONE")
