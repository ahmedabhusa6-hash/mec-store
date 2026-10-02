# Patch regression script: non-JSON handling + order status via routed
import re

PATH = "/home/z/my-project/scripts/audit/mec21_regression.py"
src = open(PATH, encoding="utf-8").read()
n = 0

# 1. non-JSON safe parsing in req()
anchor1 = "return resp.status, dict(resp.headers), json.loads(raw) if raw else None"
if anchor1 in src:
    src = src.replace(anchor1, 'try:\n                    parsed = json.loads(raw) if raw else None\n                except Exception:\n                    parsed = raw.decode("utf-8", errors="replace")\n                return resp.status, dict(resp.headers), parsed')
    n += 1

# 2. order status via routed
anchor2 = 'check("order delivered (sandbox)", co.get("status") == "delivered", f"status={co.get(\'status\')}")'
if anchor2 in src:
    src = src.replace(anchor2, 'routed = co.get("routed") or {}\norder_status = routed.get("status") or co.get("status")\ncheck("order delivered (sandbox)", order_status == "delivered", f"status={order_status} keys={list(co.keys())}")')
    n += 1

# 3. usd/cashback via routed
anchor3 = 'usd = co.get("amountUsd") or co.get("order", {}).get("amountUsd")'
if anchor3 in src:
    src = src.replace(anchor3, 'usd = co.get("amountUsd") or routed.get("amountUsd") or (co.get("order") or {}).get("amountUsd")')
    n += 1
anchor4 = 'cashback = co.get("cashback") or co.get("order", {}).get("cashback") or 0'
if anchor4 in src:
    src = src.replace(anchor4, 'cashback = routed.get("cashback") or co.get("cashback") or 0')
    n += 1

# 4. home fetch: drop req() call, use urllib with status
anchor5 = 's, h, home = req("GET", "/")\ncheck("home 200", s == 200)\nhome_str = home if isinstance(home, str) else json.dumps(home)\nr = urllib.request.Request(BASE + "/")\nwith urllib.request.urlopen(r, timeout=15) as resp:\n    html = resp.read().decode("utf-8")\ncheck("canonical link"'
if anchor5 in src:
    src = src.replace(anchor5, 'r = urllib.request.Request(BASE + "/")\nwith urllib.request.urlopen(r, timeout=15) as resp:\n    home_status = resp.status\n    html = resp.read().decode("utf-8")\ncheck("home 200", home_status == 200, f"status={home_status}")\ncheck("canonical link"')
    n += 1

open(PATH, "w", encoding="utf-8").write(src)
print(f"patched {n}/5 anchors")
