#!/usr/bin/env python3
"""MEC-18b: Railway audit via GraphQL v2 endpoint (current). Read-only."""
import json, os, sys, urllib.request, urllib.error

API = "https://backboard.railway.com/graphql/v2"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
PROJECT_ID = "a574c5d0-f136-446b-b8c9-2ceba79e4210"

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
        try: body = e.read().decode()[:400]
        except Exception: body = ""
        return {"http_error": e.code, "body": body}
    except Exception as e:
        return {"error": str(e)}

def main():
    if not TOKEN:
        print("NO_TOKEN"); return 1
    # Project tokens cannot query 'me' — go straight to project
    q = """
    query($id: String!) {
      project(id: $id) {
        id name
        environments { edges { node { id name isEphemeral } } }
        services { edges { node {
          id name
          deployments { edges { node { id status createdAt staticUrl } } }
          domains { edges { node { id domain } } }
        } } }
      }
    }"""
    proj = gql(q, {"id": PROJECT_ID})
    print("== PROJECT =="); print(json.dumps(proj, ensure_ascii=False, indent=1)[:3000])
    return 0
    # project query (v2 shape)
    q = """
    query($id: String!) {
      project(id: $id) {
        id name
        environments { edges { node { id name isEphemeral } } }
        services { edges { node { id name } } }
      }
    }"""
    proj = gql(q, {"id": PROJECT_ID})
    print("\n== PROJECT ==")
    print(json.dumps(proj, ensure_ascii=False, indent=1)[:1500])
    return 0

if __name__ == "__main__":
    sys.exit(main())
