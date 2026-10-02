#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.3 | Batch 3 compile — parse all OK batch-3 search results into findings index.
Evidence level = Advertised/Lead (search snippets per v4.1 §4.1) until page reads.
Output: research/findings_index_b3.json grouped by SKU + ranked verify candidates.
"""
import json, os, re

RD = "/home/z/my-project/research"
AD = RD + "/actions"
ledger = json.load(open(RD + "/action_ledger.json", encoding="utf-8"))
b2 = [l for l in ledger if l.get("batch") == 3 and l["method"].startswith("web_search")]

PRICE_RE = re.compile(r'(\$|USD|€|EUR|£|GBP|₽|RUB|AED|SAR|TRY|₹|INR|EGP|ARS)\s?([0-9]{1,6}(?:[.,][0-9]{1,3})?)', re.I)
findings = []
for act in b2:
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
            "date": it.get("date", ""), "prices_seen": prices[:8],
        })

by_sku = {}
for fd in findings:
    for sku in fd["targets"]:
        by_sku.setdefault(sku, []).append(fd)

CHANNEL_HOSTS = ["eneba.com","turgame.com","kinguin.net","kinguin.com","g2a.com","cdkeys.com",
    "allkeyshop.com","gg.deals","keys4us","gocdkeys.com","royalcdkeys.com","cjs-cdkeys.com",
    "ggsel.net","keyforsteam.de","z2u.com","plati.market","plati.ru","reloadly.com","ding.com",
    "dtone.com","megatec-center.com","almomaizcard.com","fazercards.com","seagm.com","unipin.com",
    "airalo.com","sms-activate","5sim","smmpanel","justanotherpanel"]
OFFICIAL_HOSTS = ["openai.com","anthropic.com","google.com","spotify.com","netflix.com",
    "youtube.com","nordvpn.com","telegram.org","discord.com","microsoft.com","xbox.com",
    "apple.com","valve.com","steampowered.com","canva.com","disneyplus.com","hulu.com",
    "max.com","primevideo.com","expressvpn.com","surfshark.com","playstation.com",
    "deepseek.com","x.ai","midjourney.com","github.com","razer.com","roblox.com"]

verify_candidates = {}
for sku, fds in by_sku.items():
    ranked = sorted(fds, key=lambda x: (
        0 if any(h in x["host"] for h in CHANNEL_HOSTS) else (1 if any(h in x["host"] for h in OFFICIAL_HOSTS) else 2),
        -len(x["prices_seen"])))
    verify_candidates[sku] = [
        {"url": r["url"], "host": r["host"], "title": r["title"][:90],
         "prices_seen": r["prices_seen"], "rank_reason": "channel" if any(h in r["host"] for h in CHANNEL_HOSTS) else ("official" if any(h in r["host"] for h in OFFICIAL_HOSTS) else "other")}
        for r in ranked[:3]]

out = {
    "generated": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
    "run_id": "MEC2-20260927-B3",
    "actions_parsed": len(b2),
    "findings_total": len(findings),
    "skus_with_findings": len(by_sku),
    "by_sku": by_sku,
    "verify_candidates": verify_candidates,
}
json.dump(out, open(RD + "/findings_index_b3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# console summary
print("ACTIONS_PARSED: %d | FINDINGS: %d | SKUS_WITH_FINDINGS: %d / 218" % (len(b2), len(findings), len(by_sku)))
cat = json.load(open("/home/z/my-project/download/catalog_v42.json", encoding="utf-8"))
p2 = [s["sku_id"] for s in cat["skus"] if s.get("priority") == "P3"]
no_find = [s for s in p2 if s not in by_sku]
print("P3 SKUs with ZERO findings:", no_find)
with_price = [s for s in by_sku if any(fd["prices_seen"] for fd in by_sku[s])]
print("SKUs with >=1 price pattern: %d" % len(with_price))
# channel-host verify candidates count
n_ch = sum(1 for s in verify_candidates if verify_candidates[s] and verify_candidates[s][0]["rank_reason"] == "channel")
print("SKUs whose top verify candidate is a Notion-specified channel host: %d" % n_ch)
