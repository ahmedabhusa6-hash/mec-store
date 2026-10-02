#!/usr/bin/env python3
"""MEC-18f: full Railway project state — services, envs, deployment source, variables (names only), domains."""
import json, os, urllib.request, urllib.error

API = "https://backboard.railway.com/graphql/v2"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
PROJECT_ID = "a574c5d0-f136-446f-b8c9-2ceba79e4214"
ENV_ID = "89138798-9412-4829-be22-3b913df05fe5"
SERVICE_ID = "79f9401c-3598-4cbe-a5fe-d50c13191820"
DEPLOY_ID = "87142d12-aa5e-4d5e-92b7-fc5b6f968294"

def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=payload, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "User-Agent": "mec-audit/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:500]}

out = {}

# 1. Full project with environments + services
r = gql("""query($id: String!) { project(id: $id) {
  id name
  environments { edges { node { id name isEphemeral } } }
} }""", {"id": PROJECT_ID})
out["project"] = r.get("data", r)

# 2. Service instances for the environment
r2 = gql("""query($environmentId: String!) {
  serviceInstances(environmentId: $environmentId) { edges { node { id serviceName serviceId } } }
}""", {"environmentId": ENV_ID})
if "http_error" in r2 or r2.get("errors"):
    # try alternate: environment query
    r2 = gql("""query($id: String!) { environment(id: $id) { id name } }""", {"id": ENV_ID})
out["serviceInstances"] = r2.get("data", r2)

# 3. Deployment full meta
r3 = gql("""query($id: String!) { deployment(id: $id) {
  id status createdAt updatedAt url staticUrl meta
  service { id name }
  environment { id name }
} }""", {"id": DEPLOY_ID})
out["deployment"] = r3.get("data", r3)

# 4. Variables for service deployment (names only — never values)
r4 = gql("""query($environmentId: String!, $serviceId: String) {
  variables(environmentId: $environmentId, serviceId: $serviceId) {
    edges { node { name } }
  }
}""", {"environmentId": ENV_ID, "serviceId": SERVICE_ID})
out["variableNames"] = [e["node"]["name"] for e in r4.get("data", {}).get("variables", {}).get("edges", [])] if "data" in r4 else r4

# 5. Domains
r5 = gql("""query($environmentId: String!) {
  domains(environmentId: $environmentId) { edges { node { id domain serviceId } } }
}""", {"environmentId": ENV_ID})
out["domains"] = r5.get("data", r5)

print(json.dumps(out, ensure_ascii=False, indent=1)[:4000])
