#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R2 — follow-up decisive tests (local):
  F1  live sv_ps (CapCut line) hex ObjectIds vs ProdSeller-fresh hex  -> same DB?
  F2  laha names vs ProdSeller-fresh names (retail storefront similarity)
  F3  cb_ description URL domains (fresh extraction, full)
  F4  decohomz.com root content analysis (SV API host)
  F5  gemini12pro last post proper extraction (per-message block parsing)
  F6  cb_ "other" family top names (146 unclassified -> what are they?)
"""
import json, re
from collections import Counter

def jload(p): return json.load(open(p))
raw1 = jload("/home/z/my-project/research/g1_rescan_raw_20261002.json")
raw3 = jload("/home/z/my-project/research/g1_rescan_raw3_20261002.json")
def body(name, src=raw1):
    return next((f["body"] for f in src["fetches"] if f["name"] == name), None)

sv = json.loads(body("sv_public"))["products"]
sv_cb = [it for it in sv if str(it.get("id", "")).startswith("cb_")]
sv_ps = [it for it in sv if str(it.get("id", "")).startswith("ps_")]
sv_mr = [it for it in sv if str(it.get("id", "")).startswith("mr_")]
ps_fresh = json.loads(body("ps_products"))["products"]
laha = json.loads(body("laha_products_xak"))["products"]

# ---------- F1: ps_live hex vs ps_fresh hex ----------
ps_live_hex = {str(it["id"])[3:]: it for it in sv_ps if re.fullmatch(r"ps_[0-9a-f]{24}", str(it.get("id")))}
ps_fresh_hex = {str(it.get("id")): it for it in ps_fresh if re.fullmatch(r"[0-9a-f]{24}", str(it.get("id")))}
inter = set(ps_live_hex) & set(ps_fresh_hex)
print(f"[F1] ps_live(20 CapCut) hex={len(ps_live_hex)} vs ps_fresh(26) hex={len(ps_fresh_hex)} -> ObjectId overlap={len(inter)}")
for o in sorted(inter):
    print(f"    SAME RECORD: ps_{o[:10]}.. | SV:'{ps_live_hex[o].get('name','?')[:45]}' ${ps_live_hex[o].get('price')} | PS-API:'{ps_fresh_hex[o].get('name','?')[:45]}' ${ps_fresh_hex[o].get('price')}")
if not inter:
    # name fallback
    def nk(t):
        t = re.sub(r"[^a-zA-Z ]", " ", (t or "").lower()); return re.sub(r"\s+", " ", t).strip()
    ps_live_names = {nk(it.get("name")) for it in sv_ps}
    ps_fresh_names = {nk(it.get("name")): it for it in ps_fresh}
    nm = ps_live_names & set(ps_fresh_names)
    print(f"    ObjectId=0 -> name fallback: {len(nm)} matches")
    for n in sorted(nm)[:10]: print(f"      ~ {n[:70]} | PS-API price=${ps_fresh_names[n].get('price')}")

# ---------- F2: laha vs prodseller-fresh ----------
def nk(t):
    t = re.sub(r"[^a-zA-Z ]", " ", (t or "").lower()); return re.sub(r"\s+", " ", t).strip()
laha_names = {nk(it.get("name")): it for it in laha}
ps_fresh_names = {nk(it.get("name")): it for it in ps_fresh}
inter2 = set(laha_names) & set(ps_fresh_names)
print(f"\n[F2] laha(15) vs ProdSeller-fresh(26) name overlap = {len(inter2)}")
for n in sorted(inter2)[:10]:
    print(f"    ~ {n[:60]} | laha=${laha_names[n].get('price')} ps=${ps_fresh_names[n].get('price')}")

# ---------- F3: cb_ desc URL domains ----------
doms = Counter()
urls_by_dom = {}
for it in sv_cb:
    for u in re.findall(r"https?://([A-Za-z0-9\.\-]+)(/\S*)?", it.get("description") or ""):
        d = u[0].lower(); doms[d] += 1
        urls_by_dom.setdefault(d, set()).add("https://" + d + (u[1] or "")[:60])
print(f"\n[F3] cb_ description URL domains:")
for d, n in doms.most_common(20):
    print(f"    {n:4}  {d}   e.g. {sorted(urls_by_dom[d])[:2]}")

# ---------- F4: decohomz root ----------
dec = body("decohomz_root") or ""
title = re.search(r"<title>(.*?)</title>", dec, re.S)
metas = re.findall(r'<meta[^>]*(?:name|property)="([^"]+)"[^>]*content="([^"]{0,120})"', dec)
print(f"\n[F4] decohomz.com root: title={title.group(1).strip()[:100] if title else None}")
for k, v in metas[:8]: print(f"    meta {k} = {v[:100]}")
h1s = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", dec, re.S)
for h in h1s[:6]: print("    h1/h2:", re.sub(r"<[^>]+>", "", h).strip()[:100])
links = sorted(set(re.findall(r'href="(https?://[^"]+)"', dec)))
for l in links[:15]: print("    link:", l[:100])

# ---------- F5: gemini12pro proper extraction ----------
g12 = body("g12_channel") or ""
blocks = re.split(r'class="tgme_widget_message ', g12)
msgs = []
for b in blocks[1:]:
    t = re.search(r'datetime="([\d\-T:+]+)"', b)
    x = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', b, re.S)
    if t:
        txt = re.sub(r"<br\s*/?>", "\n", x.group(1)) if x else ""
        txt = re.sub(r"<[^>]+>", "", txt)
        txt = txt.replace("&#036;", "$").replace("&#33;", "!").replace("&amp;", "&").replace("&#039;", "'")
        msgs.append((t.group(1), re.sub(r"\s+", " ", txt).strip()))
msgs.sort(key=lambda m: m[0])
print(f"\n[F5] gemini12pro: {len(msgs)} messages extracted (chronological):")
for dt, tx in msgs[-8:]:
    print(f"    {dt[:16]} :: {tx[:180]}")

# ---------- F6: cb_ "other" family ----------
def family(name):
    n = (name or "").lower()
    for k in ["chatgpt","gemini","claude","perplexity","duolingo","capcut","canva","office",
              "adobe","spotify","youtube","netflix","kling","gmail","apple","discord",
              "telegram","copilot","cursor","grok","codex","facebook","lovable","aws",
              "twitter","x premium","tiktok","linkedin","reddit","notion","windsurf","mobbin","wispr","prime","telegram premium"]:
        if k in n: return k
    return "other"
oth = [it.get("name") for it in sv_cb if family(it.get("name")) == "other"]
print(f"\n[F6] cb_ 'other' = {len(oth)} products; sample 40:")
for n in oth[:40]: print("    -", (n or "")[:85])
