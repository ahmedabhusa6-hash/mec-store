#!/usr/bin/env python3
"""AUDIT-4 supplemental: PostgREST grants (role_table_grants), default ACLs,
_prisma_migrations presence, pg_stat_statements, STORE_MODE. READ-ONLY."""
import json, os, re, urllib.request

ROOT = "/home/z/my-project"
API = "https://backboard.railway.com/graphql/v2"

TOKEN = os.environ.get("RAILWAY_TOKEN", "")
if not TOKEN:
    for line in open(f"{ROOT}/.env"):
        line = line.strip()
        if line.startswith("RAILWAY_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
if not TOKEN:
    raise SystemExit("no token")

def gql(q, v=None):
    req = urllib.request.Request(API, data=json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "audit4/1.1"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

r = gql("""query($projectId: String!, $environmentId: String!, $serviceId: String!) {
  variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
}""", {"projectId": "a574c5d0-f136-446f-b8c9-2ceba79e4214",
       "environmentId": "89138798-9412-4829-be22-3b913df05fe5",
       "serviceId": "79f9401c-3598-4cbe-a5fe-d50c13191820"})
raw = r.get("data", {}).get("variables")
vars = json.loads(raw) if isinstance(raw, str) else raw
if not vars:
    raise SystemExit("no variables: " + json.dumps(r)[:200])
print("STORE_MODE =", vars.get("STORE_MODE", "(unset)"))
print("railway vars present:", len(vars), "(values hidden)")
DIRECT = None
for k, v in vars.items():
    if k.startswith("DIRECT") and isinstance(v, str) and v.startswith("postgresql"):
        DIRECT = v
DB_URL = DIRECT or vars.get("DATABASE_URL")
m = re.match(r"postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/([^\s?/]+)", DB_URL)

import pg8000.native
con = pg8000.native.Connection(user=m.group(1), password=m.group(2), host=m.group(3),
    port=int(m.group(4)), database=m.group(5), timeout=30, ssl_context=True)
print("CONNECTED (creds hidden)\n")

def run(sql):
    if not re.match(r"^\s*(SELECT|EXPLAIN|WITH)\b", sql, re.IGNORECASE):
        return [{"error": "BLOCKED"}]
    try:
        rows = con.run(sql)
        return [dict(zip([c["name"] for c in con.columns], row)) for row in rows]
    except Exception as e:
        return [{"error": str(e)[:200]}]

print("== information_schema.role_table_grants (anon/authenticated/service_role) ==")
rows = run("""SELECT grantee, table_name, privilege_type FROM information_schema.role_table_grants
  WHERE table_schema='public' AND grantee IN ('anon','authenticated','service_role')
  ORDER BY grantee, table_name, privilege_type""")
anon = [x for x in rows if x.get("grantee") == "anon"]
auth = [x for x in rows if x.get("grantee") == "authenticated"]
sr = [x for x in rows if x.get("grantee") == "service_role"]
print(f"  anon grants: {len(anon)} | authenticated grants: {len(auth)} | service_role grants: {len(sr)}")
for x in rows[:5]: print("   sample:", x)

print("\n== default ACLs on public schema (future tables) ==")
for x in run("""SELECT pg_get_userbyid(defaclrole) AS grantor_role, defaclobjtype, defaclacl
  FROM pg_default_acl WHERE defaclnamespace = 'public'::regnamespace::oid"""):
    print("  ", x)

print("\n== _prisma_migrations / prisma metadata tables ==")
rows = run("""SELECT table_name FROM information_schema.tables
  WHERE table_schema='public' AND table_name ILIKE '%prisma%'""")
print("  found:", rows if rows else "NONE (schema managed by db push, no migration history)")

print("\n== pg_stat_statements top 10 by calls ==")
for x in run("""SELECT calls, round(total_exec_time::numeric,1) AS total_ms,
  left(regexp_replace(query, E'[\\n\\r]+', ' ', 'g'), 110) AS q
  FROM pg_stat_statements WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
  ORDER BY calls DESC LIMIT 10"""):
    print(f"  calls={x['calls']} ms={x['total_ms']} :: {x['q']}")

print("\n== raw relacl grants to anon/authenticated (direct check) ==")
rows = run("""SELECT c.relname, r.rolname, a.privilege_type FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  CROSS JOIN LATERAL aclexplode(c.relacl) a JOIN pg_roles r ON r.oid = a.grantee
  WHERE n.nspname = 'public' AND c.relkind = 'r' AND r.rolname IN ('anon','authenticated')""")
print(f"  entries: {len(rows)} (0 = fully revoked)" if rows else "  entries: 0 (fully revoked)")
for x in rows: print("  ", x)

print("\n== policy count raw ==")
for x in run("SELECT COUNT(*) AS n FROM pg_policies WHERE schemaname='public'"):
    print("  total policies:", x["n"])

con.close()
print("\nSUPPLEMENTAL DONE (read-only)")
