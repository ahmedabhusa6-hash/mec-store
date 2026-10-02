#!/usr/bin/env python3
"""
LIVE PROBE WAVE — Other API-differential suppliers
==================================================
Targets (per user directive: بعد ProdSeller افحص الآخرين):
  1. StackVault backend API (live re-fetch with correct URL)
  2. GGSel (ggsel.com — ChatGPT Plus 749₽) — check API/public pricing
  3. BitTopUp (bittopup.com — has API program)
  4. K4G (k4g.com — API documented)
Gentle pacing, single-shot fetches, honest failures.
"""
import json
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone

OUT = "/home/z/my-project/research/prodseller_live"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9,ar;q=0.8,ru;q=0.7"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch(url, timeout=25, as_json=True):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read().decode("utf-8", errors="replace")
            if as_json:
                try:
                    return r.status, json.loads(raw), raw
                except json.JSONDecodeError:
                    return r.status, None, raw
            return r.status, raw, raw
    except urllib.error.HTTPError as e:
        return e.code, None, e.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return 0, None, f"{type(e).__name__}: {e}"


def probe(name, url, as_json=True):
    print(f"\n{'─'*70}\n[{name}] {url}")
    st, data, raw = fetch(url, as_json=as_json)
    print(f"  HTTP {st} | bytes: {len(raw) if raw else 0}")
    return st, data, raw


results = {}

# ---------- 1. StackVault backend live ----------
for u in ["https://decohomz.com/sv-api/products",
          "https://stackvault.shop/api/products",
          "https://decohomz.com/sv-api/products?page=1"]:
    st, data, raw = probe("StackVault", u)
    if st == 200 and data is not None:
        prods = data if isinstance(data, list) else data.get("products", data.get("data", []))
        print(f"  ✓ LIVE StackVault: {len(prods)} products")
        results["stackvault"] = {"url": u, "n": len(prods), "data": data}
        with open(f"{OUT}/stackvault_live.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        break
    elif st == 200:
        print(f"  200 but not JSON (len {len(raw)}). snippet: {raw[:200]}")
    else:
        print(f"  ✗ failed: {str(raw)[:150]}")
    time.sleep(2)

# ---------- 2. GGSel ----------
for u in ["https://ggsel.com/api/products?page=1",
          "https://ggsel.com/",
          "https://ggsel.com/en/"]:
    st, data, raw = probe("GGSel", u)
    if st == 200 and data is not None:
        print(f"  ✓ GGSel JSON OK ({len(raw)} bytes)")
        results["ggsel"] = {"url": u, "status": st, "sample": str(raw)[:300]}
        break
    elif st == 200:
        # HTML — save for parsing
        with open(f"{OUT}/ggsel_home.html", "w", encoding="utf-8") as f:
            f.write(raw)
        print(f"  ✓ GGSel HTML saved ({len(raw)} bytes)")
        results["ggsel"] = {"url": u, "status": st, "html_bytes": len(raw), "file": f"{OUT}/ggsel_home.html"}
        break
    else:
        print(f"  ✗ {str(raw)[:120]}")
    time.sleep(2)

# ---------- 3. BitTopUp ----------
for u in ["https://www.bittopup.com/api/v1/products",
          "https://www.bittopup.com/api/catalog",
          "https://www.bittopup.com/"]:
    st, data, raw = probe("BitTopUp", u)
    if st == 200 and data is not None:
        print(f"  ✓ BitTopUp JSON OK")
        results["bittopup"] = {"url": u, "status": st, "sample": str(raw)[:300]}
        with open(f"{OUT}/bittopup_api.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        break
    elif st == 200:
        with open(f"{OUT}/bittopup_home.html", "w", encoding="utf-8") as f:
            f.write(raw)
        print(f"  ✓ BitTopUp HTML saved ({len(raw)} bytes)")
        results["bittopup"] = {"url": u, "status": st, "html_bytes": len(raw)}
        break
    else:
        print(f"  ✗ {str(raw)[:120]}")
    time.sleep(2)

# ---------- 4. K4G API ----------
for u in ["https://api.k4g.com/products?pageSize=50",
          "https://www.k4g.com/api/products",
          "https://www.k4g.com/"]:
    st, data, raw = probe("K4G", u)
    if st == 200 and data is not None:
        print(f"  ✓ K4G JSON OK")
        results["k4g"] = {"url": u, "status": st, "sample": str(raw)[:300]}
        with open(f"{OUT}/k4g_api.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        break
    elif st == 200:
        print(f"  HTML {len(raw)} bytes — snippet: {raw[:150]}")
        results["k4g"] = {"url": u, "status": st, "html_bytes": len(raw)}
    else:
        print(f"  ✗ {str(raw)[:120]}")
    time.sleep(2)

print(f"\n{'='*70}\nPROBE SUMMARY:")
for k, v in results.items():
    print(f"  {k}: {json.dumps({kk: vv for kk, vv in v.items() if kk != 'data'}, ensure_ascii=False)[:150]}")

with open(f"{OUT}/live_probe_wave1.json", "w", encoding="utf-8") as f:
    json.dump({"ts": datetime.now(timezone.utc).isoformat(),
               "results": {k: {kk: vv for kk, vv in v.items() if kk != "data"} for k, v in results.items()}},
              f, ensure_ascii=False, indent=2)
