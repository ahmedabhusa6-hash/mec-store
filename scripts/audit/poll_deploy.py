#!/usr/bin/env python3
"""Poll MEC-20 Railway deployment status until terminal state."""
import json, time, urllib.request, sys

TOKEN = ""
with open('/home/z/my-project/.env') as f:
    for line in f:
        if line.startswith('RAILWAY_TOKEN='):
            TOKEN = line.strip().split('=', 1)[1]
API = "https://backboard.railway.com/graphql/v2"
SVC = "79f9401c-3598-4cbe-a5fe-d50c13191820"

def gql(q, v=None):
    req = urllib.request.Request(API, data=json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "mec-audit/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

q = """query($id:String!){ service(id:$id){ deployments(first:3){ edges{ node{ id status createdAt } } } } }"""
for attempt in range(60):
    r = gql(q, {"id": SVC})
    edges = r["data"]["service"]["deployments"]["edges"]
    for e in edges:
        n = e["node"]
        print(f"[poll {attempt}] {n['id'][:8]} status={n['status']} createdAt={n['createdAt']}")
    top = edges[0]["node"] if edges else None
    if top and top["status"].upper() in ("SUCCESS", "FAILED", "CRASHED", "CANCELLED"):
        print("TERMINAL:", top["status"])
        sys.exit(0 if top["status"].upper() == "SUCCESS" else 1)
    time.sleep(20)
print("TIMEOUT waiting for deployment")
sys.exit(2)
