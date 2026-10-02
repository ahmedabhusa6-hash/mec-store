#!/usr/bin/env python3
"""MEC-2.0 G4b: fix select fields on committed Interaction Archive rows.
Notion API creates new select options when set on a page (select type only).
Status-type property (if any) falls back to nearest existing option."""
import json, ssl, urllib.request, urllib.error

import os as _os
def _load_token():
    tok = _os.environ.get('NOTION_TOKEN', '')
    if tok:
        return tok
    env_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '.env')
    try:
        for line in open(env_path, encoding='utf-8'):
            if line.strip().startswith('NOTION_TOKEN='):
                return line.strip().split('=', 1)[1].strip().strip(chr(34)).strip(chr(39))
    except FileNotFoundError:
        pass
    raise SystemExit('NOTION_TOKEN missing: set env var or add NOTION_TOKEN=... to .env')
TOKEN = _load_token()
BASE = "https://api.notion.com/v1"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
IA_DB = "e844ab12-d846-4974-9651-0892464966e5"

ROWS = {
    "3e858a07-79e8-812b-b58d-eb28bf42c7f0": {  # Cycle 6
        "Actor": ("z.ai Runtime (Super Z)", "System"),
        "Stage": ("Runtime Evidence + Analysis", "ChatGPT Analysis"),
        "Status": ("Committed", "Received"),
    },
    "3e858a07-79e8-8183-8513-ca9ff8642de7": {  # Cycle 7
        "Actor": ("z.ai Runtime (Super Z)", "System"),
        "Stage": ("Runtime Research + Knowledge Commit", "ChatGPT Analysis"),
        "Status": ("Committed", "Received"),
    },
}

def api(method, path, body=None, retries=3):
    headers = {"Authorization": "Bearer " + TOKEN, "Notion-Version": "2022-06-28",
               "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, method=method, headers=headers, data=data)
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                import time; time.sleep(3); continue
            try: detail = e.read().decode()[:250]
            except Exception: detail = ""
            return {"__error": e.code, "__detail": detail}
        except Exception:
            import time; time.sleep(1.5)
    return {"__error": "max_retries"}

db = api("GET", "/databases/" + IA_DB)
props = db.get("properties", {})
for row_id, fields in ROWS.items():
    payload = {}
    for prop_name, (desired, fallback) in fields.items():
        pk = None
        for k in props:
            if k.lower() == prop_name.lower():
                pk = k; break
        if not pk:
            print("!! prop not found:", prop_name); continue
        ptype = props[pk].get("type")
        if ptype == "select":
            payload[pk] = {"select": {"name": desired}}  # API creates new option
        elif ptype == "status":
            options = [o.get("name") for o in (props[pk].get("status") or {}).get("options", [])]
            pick = desired if desired in options else fallback
            payload[pk] = {"status": {"name": pick}}
        else:
            print("!! unexpected type for", pk, ptype); continue
    r = api("PATCH", "/pages/" + row_id, {"properties": payload})
    ok = "__error" not in r
    print(("OK " if ok else "!! ") + row_id[:8], "→", {k: v for k, v in payload.items()},
          "" if ok else r.get("__detail", ""))
