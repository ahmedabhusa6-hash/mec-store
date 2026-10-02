#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.1 | Batch 2 intelligence builder (draft pass).
Evidence level = Advertised (snippet) per v4.1 §4.1 — direct page reads deferred
(remote-function quota exhausted mid-run; honest state, retry scheduled).
Output: research/batch2_intelligence_draft.json — for manual curation pass,
then merge into download/offers_intelligence.json (separate merge step).
"""
import json, re, os

RD = "/home/z/my-project/research"
OUT = "/home/z/my-project/download"
TODAY = "2026-09-27"

# FX basis: batch-1 documented (Wise 25/09) + new currencies approx 27/09 (lower confidence)
FX = {"USD": 1.0, "EUR": 1.137, "GBP": 1.3548, "RUB": 0.0126, "TRY": 0.0293,
      "AED": 0.2723, "SAR": 0.2666, "INR": 0.0115, "EGP": 0.0206, "ARS": 0.00104,
      "CAD": 0.73, "AUD": 0.66}
FX_NOTE = "EUR/GBP/RUB/TRY/AED/SAR = Wise 25/09 (batch-1 basis); INR/EGP/ARS/CAD/AUD = approx market 27/09 (lower confidence)"

CUR_MAP = {"$": "USD", "€": "EUR", "£": "GBP", "₽": "RUB", "₹": "INR"}
CUR_WORDS = {"USD": "USD", "EUR": "EUR", "GBP": "GBP", "RUB": "RUB", "AED": "AED",
             "SAR": "SAR", "INR": "INR", "EGP": "EGP", "ARS": "ARS"}

CHANNEL_HOSTS = ["eneba.com","turgame.com","kinguin.net","kinguin.com","g2a.com","cdkeys.com",
    "allkeyshop.com","gg.deals","keys4us","gocdkeys.com","royalcdkeys.com","cjs-cdkeys.com",
    "ggsel.net","keyforsteam.de","z2u.com","plati.market","plati.ru","reloadly.com","ding.com",
    "dtone.com","megatec-center.com","almomaizcard.com","fazercards.com","seagm.com","unipin.com",
    "airalo.com","sms-activate","5sim","topuplive","topuplive.com","gameboost","gameboost.com",
    "instant-gaming","instantgaming","fanatical","greenmangaming","loaded.com","k4g.com","hrkgame",
    "cdkeysdiscount","kinguin","eneba","gamivo","gamivo.com"]
OFFICIAL_HOSTS = ["openai.com","chatgpt.com","anthropic.com","claude.ai","google.com","spotify.com",
    "netflix.com","youtube.com","nordvpn.com","telegram.org","discord.com","microsoft.com","xbox.com",
    "apple.com","valve.com","steampowered.com","canva.com","disneyplus.com","hulu.com","max.com",
    "primevideo.com","amazon.com","expressvpn.com","surfshark.com","playstation.com","deepseek.com",
    "x.ai","midjourney.com","github.com","razer.com","roblox.com","help.openai.com"]

def host_class(h):
    h = (h or "").lower()
    if any(c in h for c in CHANNEL_HOSTS): return "channel"
    if any(o in h for o in OFFICIAL_HOSTS): return "official"
    return "other"

def usd(amount, cur):
    return round(amount * FX.get(cur, 1.0), 2)

cat = json.load(open(OUT + "/catalog_v42.json", encoding="utf-8"))
fi = json.load(open(RD + "/findings_index_b2.json", encoding="utf-8"))
by_sku = fi["by_sku"]

# family sanity ranges: (min_usd, max_usd) for a plausible unit price
FAM_RANGE = {
    "AI/SaaS": (1, 400), "Gift Cards": (1, 130), "Game Top-up": (0.5, 100),
    "Game Keys": (2, 90), "Software/Licenses": (0.5, 400), "eSIM": (2, 70),
    "SMM Services": (0.01, 60), "Virtual Numbers": (0.05, 12),
    "Digital Subscriptions": (0.5, 400), "API Services": (1, 600),
}

def denom_of(s):
    """numeric face value + currency for denomination-based SKUs (gift cards)."""
    d = (s.get("duration_denomination") or "")
    m = re.match(r'([0-9]{1,6}(?:\.[0-9]{1,2})?)\s*(EUR|USD|AED|SAR|GBP| TRY)?', d)
    if not m: return None
    try: val = float(m.group(1))
    except Exception: return None
    cur = m.group(2) or None
    if cur and val >= 5 and s.get("family") == "Gift Cards":
        return (val, cur)
    return None

PRICE_RE = re.compile(r'(\$|€|£|₽|₹|USD|EUR|GBP|RUB|AED|SAR|INR|EGP|ARS)\s?([0-9]{1,5}(?:[.,][0-9]{1,2})?)', re.I)

def extract_offers(s):
    sku_id = s["sku_id"]
    fam = s["family"]
    lo, hi = FAM_RANGE.get(fam, (0.01, 1000))
    denom = denom_of(s)
    cands = []
    for f in by_sku.get(sku_id, []):
        text = (f.get("title") or "") + " · " + (f.get("snippet") or "")
        tlow = text.lower()
        # denomination guard for gift cards: text must reference the denomination number
        if denom:
            dnum = ("%g" % denom[0])
            if dnum not in text and ("%.2f" % denom[0]) not in text:
                continue
        for m in PRICE_RE.finditer(text):
            sym = m.group(1).upper()
            cur = CUR_MAP.get(m.group(1)) or CUR_WORDS.get(sym, "USD")
            try: amt = float(m.group(2).replace(",", "."))
            except Exception: continue
            u = usd(amt, cur)
            if not (lo <= u <= hi): continue
            cands.append({
                "seller_host": f["host"], "url": f["url"], "title": (f["title"] or "")[:100],
                "price": amt, "cur": cur, "usd": u,
                "host_class": host_class(f["host"]),
                "context": (f["snippet"] or "")[:200], "result_date": f.get("date", ""),
            })
    # dedupe host+price
    seen, ded = set(), []
    for c in cands:
        k = (c["seller_host"], c["price"])
        if k in seen: continue
        seen.add(k); ded.append(c)
    # rank: channel first, then official, then other; then cheapest
    ded.sort(key=lambda x: ({"channel": 0, "official": 1, "other": 2}[x["host_class"]], x["usd"]))
    return ded

draft = {}
for s in cat["skus"]:
    if s.get("priority") != "P2": continue
    sid = s["sku_id"]
    rec = {
        "identity": " | ".join([x for x in [s.get("product"), s.get("plan_edition"),
             s.get("duration_denomination"), s.get("region"), s.get("activation_type")] if x]),
        "family": s["family"],
        "catalog_state": s.get("ledger_state"),
        "batch2_evidence_level": "Advertised (snippet) — direct page reads deferred (remote-function quota exhausted mid-run; §19 honest state)",
    }
    offers = extract_offers(s)
    ch = [o for o in offers if o["host_class"] == "channel"]
    off = [o for o in offers if o["host_class"] == "official"]
    if offers:
        rec["offers_raw"] = offers[:8]
        rec["cheapest_channel_advertised"] = ch[0] if ch else None
        rec["official_baseline_snippet"] = off[0] if off else None
        rec["n_candidates"] = len(offers)
    else:
        rec["offers_raw"] = []
        rec["n_candidates"] = 0
    draft[sid] = rec

# rate-limited SKUs (queries never executed): RB-116..130 targets
RL = ["SKU-DS038","SKU-DS040","SKU-DS041","SKU-DS043","SKU-DS049","SKU-DS050",
      "SKU-DS061","SKU-DS062","SKU-DS063","SKU-AP002","SKU-AP003","SKU-AP005",
      "SKU-AP006","SKU-AP007","SKU-AP008","SKU-AP009","SKU-AP010","SKU-AP016"]
for sid in RL:
    if sid in draft:
        draft[sid]["rate_limited"] = True
        draft[sid]["rate_limit_note"] = "Query planned (RB-116..RB-130) but remote-function quota exhausted before execution — deferred to retry; honest state = Not-Searched (this run)"

json.dump({"generated": TODAY, "run_id": "MEC2-20260927-B2", "fx_note": FX_NOTE,
           "draft": draft}, open(RD + "/batch2_intelligence_draft.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

n_off = len([1 for v in draft.values() if v["n_candidates"] > 0])
n_ch = len([1 for v in draft.values() if v.get("cheapest_channel_advertised")])
n_offbase = len([1 for v in draft.values() if v.get("official_baseline_snippet")])
print("DRAFT: %d P2 SKUs | with >=1 candidate: %d | with channel-host candidate: %d | with official-host snippet: %d | rate-limited: %d"
      % (len(draft), n_off, n_ch, n_offbase, len(RL)))
