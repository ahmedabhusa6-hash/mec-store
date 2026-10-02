#!/usr/bin/env python3
"""MEC-18d: full Railway v2 audit — project, services, deployments, domains, live URL test."""
import json, os, sys, urllib.request, urllib.error

API = "https://backboard.railway.com/graphql/v2"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
PROJECT_ID = "a574c5d0-f136-446b-b8c9-2ceba79e4210"
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
        return {"http_error": e.code, "body": e.read().decode()[:400]}

def main():
    # 0. Query type fields
    q0 = 'query { __schema { queryType { fields { name } } } }'
    r0 = gql(q0)
    names = [f["name"] for f in r0.get("data", {}).get("__schema", {}).get("queryType", {}).get("fields", [])]
    print("== QUERIES =="); print(", ".join(names)); print()

    # 1. Project (basic + environments)
    q1 = """query($id: String!) { project(id: $id) {
        id name createdAt updatedAt
        environments { edges { node { id name isEphemeral } } }
    } }"""
    r1 = gql(q1, {"id": PROJECT_ID})
    print("== PROJECT =="); print(json.dumps(r1.get("data", r1), ensure_ascii=False, indent=1)[:800]); print()

    # 2. Deployment detail
    q2 = """query($id: String!) { deployment(id: $id) {
        id status createdAt updatedAt url staticUrl
        meta { source commit }
        service { id name }
        environment { id name }
    } }"""
    r2 = gql(q2, {"id": DEPLOY_ID})
    print("== DEPLOYMENT =="); print(json.dumps(r2.get("data", r2), ensure_ascii=False, indent=1)[:800]); print()

    # 3. Try service + its deployments via common v2 patterns
    q3 = """query($serviceId: String!, $environmentId: String) {
      deployments(serviceId: $serviceId, environmentId: $environmentId) {
        edges { node { id status createdAt url staticUrl } }
      }
    }"""
    r3 = gql(q3, {"serviceId": SERVICE_ID, "environmentId": ENV_ID})
    print("== SERVICE DEPLOYMENTS =="); print(json.dumps(r3.get("data", r3), ensure_ascii=False, indent=1)[:1200])

if __name__ == "__main__":
    main()
