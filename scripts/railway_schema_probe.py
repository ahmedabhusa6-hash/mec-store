#!/usr/bin/env python3
"""MEC-18c: discover Railway GraphQL v2 schema fields for Service/Deployment."""
import json, os, urllib.request, urllib.error

API = "https://backboard.railway.com/graphql/v2"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")

def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=payload, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "User-Agent": "mec-audit/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:600]}

INTROSPECT = """
query {
  __type(name: "Service") { fields { name } }
}
"""
r = gql(INTROSPECT)
print("== Service fields ==")
print(json.dumps(r, indent=0).replace("\\n","")[:1200])

INTROSPECT2 = """
query {
  __type(name: "Deployment") { fields { name } }
}
"""
r2 = gql(INTROSPECT2)
print("\n== Deployment fields ==")
print(json.dumps(r2, indent=0).replace("\\n","")[:800])
