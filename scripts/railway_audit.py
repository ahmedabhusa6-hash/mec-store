#!/usr/bin/env python3
"""MEC-18: Railway deployment audit — query project/service/deployment status via GraphQL API.
Read-only queries only. Token from env RAILWAY_TOKEN (never printed)."""
import json, os, sys, urllib.request

API = "https://backboard.railway.com/graphql"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
PROJECT_ID = "a574c5d0-f136-446b-b8c9-2ceba79e4210"
ENV_ID = "89138798-9412-4829-be22-3b913df05fe5"

def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=payload, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "mec-audit/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:500]}
    except Exception as e:
        return {"error": str(e)}

def main():
    if not TOKEN:
        print("NO_TOKEN: set RAILWAY_TOKEN env"); return 1
    # 1. Token validity
    me = gql("query { me { id name email } }")
    print("== ME =="); print(json.dumps(me, ensure_ascii=False)[:300])

    # 2. Project + services + deployments + domains
    q = """
    query($id: String!) {
      project(id: $id) {
        id name
        environments { edges { node { id name } } }
        services { edges { node {
          id name serviceType
          deployments { edges { node {
            id status createdAt
            staticUrl
            meta { source }
          } } }
          domains { edges { node { id domain } } }
        } } }
        infraSRID
      }
    }"""
    proj = gql(q, {"id": PROJECT_ID})
    print("\n== PROJECT ==")
    if "http_error" in proj or "error" in proj:
        print(json.dumps(proj, ensure_ascii=False)[:500]); return 1
    p = proj.get("data", {}).get("project")
    if not p:
        print("PROJECT_NOT_FOUND_OR_NO_ACCESS"); print(json.dumps(proj)[:500]); return 1
    print(f"name={p['name']} id={p['id']}")
    for env in p.get("environments", {}).get("edges", []):
        print(f"  env: {env['node']['name']} ({env['node']['id']})")
    for s in p.get("services", {}).get("edges", []):
        n = s["node"]
        print(f"\n  SERVICE: {n['name']} type={n.get('serviceType')} id={n['id']}")
        for d in n.get("domains", {}).get("edges", []):
            print(f"    domain: {d['node']['domain']}")
        for dep in n.get("deployments", {}).get("edges", []):
            dn = dep["node"]
            print(f"    deploy: status={dn['status']} created={dn['createdAt']} src={dn.get('meta',{}).get('source')} id={dn['id']}")
            if dn.get("staticUrl"):
                print(f"      staticUrl: {dn['staticUrl']}")
    # 3. Deployment detail (logs + build status)
    qd = """
    query($id: String!) {
      deployment(id: $id) {
        id status createdAt updatedAt
        meta { source commit }
        staticUrl
        service { id name }
        environment { id name }
        buildTriggers { buildCommand }
      }
    }"""
    dep = gql(qd, {"id": "87142d12-aa5e-4d5e-92b7-fc5b6f968294"})
    print("\n== DEPLOYMENT DETAIL ==")
    print(json.dumps(dep.get("data", dep), ensure_ascii=False, indent=1)[:900])
    return 0

if __name__ == "__main__":
    sys.exit(main())
