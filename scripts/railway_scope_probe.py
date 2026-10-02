#!/usr/bin/env python3
"""MEC-18e: what can this token see? projects list + token scope + deployment fixed query."""
import json, os, urllib.request, urllib.error

API = "https://backboard.railway.com/graphql/v2"
TOKEN = os.environ.get("RAILWAY_TOKEN", "")
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

print("== PROJECTS VISIBLE TO TOKEN ==")
r = gql('query { projects { edges { node { id name } } } }')
print(json.dumps(r, ensure_ascii=False, indent=1)[:1000])

print("\n== DEPLOYMENT (fixed) ==")
r2 = gql('query($id: String!) { deployment(id: $id) { id status createdAt updatedAt url staticUrl meta } }', {"id": DEPLOY_ID})
print(json.dumps(r2, ensure_ascii=False, indent=1)[:900])
