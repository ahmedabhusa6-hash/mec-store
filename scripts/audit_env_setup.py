#!/usr/bin/env python3
"""MEC-20 audit prep: fetch Railway production env vars and build local .env.
Secret values are NEVER printed — only variable names."""
import json, urllib.request, sys

RT = None
with open('/home/z/my-project/.env') as f:
    for line in f:
        if line.startswith('RAILWAY_TOKEN='):
            RT = line.strip().split('=', 1)[1]
if not RT:
    sys.exit("RAILWAY_TOKEN missing")

ENV_ID = "89138798-9412-4829-be22-3b913df05fe5"
PROJECT_ID = "a574c5d0-f136-446f-b8c9-2ceba79e4214"
SERVICE_ID = "79f9401c-3598-4cbe-a5fe-d50c13191820"

q = """query($projectId: String!, $environmentId: String!, $serviceId: String!) {
  variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId)
}"""
req = urllib.request.Request(
    "https://backboard.railway.com/graphql/v2",
    data=json.dumps({"query": q, "variables": {
        "projectId": PROJECT_ID, "environmentId": ENV_ID, "serviceId": SERVICE_ID}}).encode(),
    headers={"Authorization": f"Bearer {RT}", "Content-Type": "application/json",
             "User-Agent": "mec-audit/1.0"},
)
resp = json.loads(urllib.request.urlopen(req, timeout=20).read())
raw = resp.get("data", {}).get("variables")
if not raw:
    sys.exit("cannot read variables: " + json.dumps(resp)[:300])
railway_vars = json.loads(raw) if isinstance(raw, str) else raw
print("Railway variable NAMES fetched:", sorted(railway_vars.keys()))

# Prefer DIRECT postgres URL for local prisma (avoids pgbouncer prepared-stmt issues)
direct = next((v for k, v in railway_vars.items()
               if k.startswith("DIRECT") and isinstance(v, str) and v.startswith("postgresql")), None)
if direct:
    railway_vars["DATABASE_URL"] = direct
    print("Using DIRECT postgres connection for local dev (value hidden)")

# Build local .env: Railway prod vars + local-only tokens (GITHUB/RAILWAY stay from existing .env)
local_tokens = {}
with open('/home/z/my-project/.env') as f:
    for line in f:
        if line.startswith(('GITHUB_TOKEN=', 'RAILWAY_TOKEN=')):
            local_tokens[line.strip().split('=', 1)[0]] = line.strip().split('=', 1)[1]

merged = dict(railway_vars)
merged.update(local_tokens)  # local tokens win

# Safety: ensure sandbox mode locally is whatever prod uses (report it, no value leak for mode is fine — it's not a secret)
mode = merged.get('STORE_MODE', '(unset)')
print("STORE_MODE =", mode)

with open('/home/z/my-project/.env', 'w') as f:
    for k in sorted(merged):
        f.write(f"{k}={merged[k]}\n")
print("Local .env written with", len(merged), "variables (values hidden)")
