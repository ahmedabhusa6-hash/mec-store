#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 2 compile — parse all OK search results into a raw findings index.
Evidence level = Advertised/Lead (search snippets per v4.1 §4.1) until page reads.
Output: research/findings_index.json grouped by SKU + price-pattern extraction.
"""
import json, os, re, glob

RD = "/home/z/my-project/research"
AD = RD + "/actions"
ledger = json.load(open(RD + "/action_ledger.json", encoding="utf-8"))

PRICE_RE = re.compile(r'(\$|USD|€|EUR|£|GBP|₽|RUB|AED|SAR|TRY)\s?([0-9]{1,6}(?:[.,][0-9]{1,3})?)', re.I)
findings = []
for act in ledger:
    if act["retrieval_status"] != "OK":
        continue
    f = os.path.join(AD, act["action_id"] + ".json")
    if not os.path.exists(f):
        continue
    try:
        data = json.load(open(f, encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("results", [])
    except Exception:
        continue
    for it in items:
        if not isinstance(it, dict):
            continue
        snippet = (it.get("snippet") or "") + " " + (it.get("name") or "")
        prices = ["%s%s" % (m[0], m[1]) for m in PRICE_RE.findall(snippet)]
        findings.append({
            "action_id": act["action_id"], "query": act["query"],
            "discovery_family": act["discovery_family"],
            "targets": act["targets"],
            "url": it.get("url", ""), "host": it.get("host_name", ""),
            "title": it.get("name", ""), "snippet": (it.get("snippet") or "")[:400],
            "date": it.get("date", ""), "prices_seen": prices[:6],
        })

# group by SKU
by_sku = {}
for fd in findings:
    for sku in fd["targets"]:
        by_sku.setdefault(sku, []).append(fd)

# top candidate pages per P1 SKU for direct verification (prefer Notion-specified channel hosts)
CHANNEL_HOSTS = ["eneba.com","turgame.com","kinguin.net","kinguin.com","g2a.com","cdkeys.com",
    "allkeyshop.com","gg.deals","keys4us","gocdkeys.com","royalcdkeys.com","cjs-cdkeys.com",
    "ggsel.net","keyforsteam.de","z2u.com","plati.market","plati.ru","reloadly.com","ding.com",
    "dtone.com","megatec-center.com","almomaizcard.com","fazercards.com"]
OFFICIAL_HOSTS = ["openai.com","anthropic.com","google.com","spotify.com","netflix.com",
    "youtube.com","nordvpn.com","telegram.org","discord.com","microsoft.com","xbox.com",
    "apple.com","valve.com","steampowered.com","canva.com"]

verify_candidates = {}
for sku, fds in by_sku.items():
    ranked = sorted(fds, key=lambda x: (
        0 if any(h in x["host"] for h in CHANNEL_HOSTS) else (1 if any(h in x["host"] for h in OFFICIAL_HOSTS) else 2),
        -len(x["prices_seen"])))
    verify_candidates[sku] = [
        {"url": r["url"], "host": r["host"], "title": r["title"][:80],
         "prices_seen": r["prices_seen"], "channel_priority": ("notion-channel" if any(h in r["host"] for h in CHANNEL_HOSTS) else ("official" if any(h in r["host"] for h in OFFICIAL_HOSTS) else "other"))}
        for r in ranked[:4]]

summary = {
    "generated": "2026-09-27",
    "actions_ok": len([a for a in ledger if a["retrieval_status"] == "OK"]),
    "findings_total": len(findings),
    "unique_hosts": sorted({f["host"] for f in findings if f["host"]})[:80],
    "skus_with_findings": len(by_sku),
}
json.dump({"summary": summary, "findings": findings, "by_sku_count": {k: len(v) for k, v in by_sku.items()},
           "verify_candidates": verify_candidates},
          open(RD + "/findings_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("FINDINGS:", len(findings), "| SKUs covered:", len(by_sku), "| hosts:", len(summary["unique_hosts"]))
print("\n=== P1 SKU coverage ===")
cat = json.load(open("/home/z/my-project/download/catalog_v42.json", encoding="utf-8"))
p1 = [s for s in cat["skus"] if s["batch"] == 1]
for s in p1:
    n = len(by_sku.get(s["sku_id"], []))
    print("%s | %4d findings | %s %s %s" % (s["sku_id"], n, s["brand"], s["product"], s["duration_denomination"]))
