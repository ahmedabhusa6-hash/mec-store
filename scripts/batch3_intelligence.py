#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.3 | Batch 3 intelligence builder (draft pass).
Evidence level = Advertised (snippet) per v4.1 §4.1 — direct page reads deferred.
Output: research/batch3_intelligence_draft.json — for manual curation pass.
NOTE: P3 SKUs already carrying Directly-Observed offers from the B3-DIRECT wave
(stackvault API / turgame / channel posts) are marked so curation preserves them.
"""
import json, re, os, time

RD = "/home/z/my-project/research"
OUT = "/home/z/my-project/download"
TODAY = "2026-09-27"

FX = {"USD": 1.0, "EUR": 1.137, "GBP": 1.3548, "RUB": 0.0126, "TRY": 0.0293,
      "AED": 0.2723, "SAR": 0.2666, "INR": 0.0115, "EGP": 0.0206, "ARS": 0.00104,
      "CAD": 0.73, "AUD": 0.66, "JPY": 0.0067, "KRW": 0.00073, "THB": 0.029,
      "QAR": 0.2747, "KWD": 3.26, "OMR": 2.60, "BHD": 2.65, "JOD": 1.41, "MAD": 0.10,
      "IQD": 0.00076, "YER": 0.004}
FX_NOTE = "EUR/GBP/RUB/TRY/AED/SAR = Wise 25/09 (batch-1 basis); others approx 27/09 (lower confidence); TRY basis flagged stale by Turgame implied rate 48.8/USD [to-verify]"

CUR_MAP = {"$": "USD", "€": "EUR", "£": "GBP", "₽": "RUB", "₹": "INR"}
CUR_WORDS = {"USD": "USD", "EUR": "EUR", "GBP": "GBP", "RUB": "RUB", "AED": "AED",
             "SAR": "SAR", "INR": "INR", "EGP": "EGP", "ARS": "ARS"}

CHANNEL_HOSTS = ["eneba.com","turgame.com","kinguin.net","kinguin.com","g2a.com","cdkeys.com",
    "allkeyshop.com","gg.deals","keys4us","gocdkeys.com","royalcdkeys.com","cjs-cdkeys.com",
    "ggsel.net","keyforsteam.de","z2u.com","plati.market","plati.ru","reloadly.com","ding.com",
    "dtone.com","megatec-center.com","almomaizcard.com","fazercards.com","seagm.com","unipin.com",
    "airalo.com","sms-activate","5sim","topuplive","gameboost","instant-gaming","instantgaming",
    "fanatical","greenmangaming","loaded.com","k4g.com","hrkgame","gamivo"]
OFFICIAL_HOSTS = ["openai.com","chatgpt.com","anthropic.com","claude.ai","google.com","spotify.com",
    "netflix.com","youtube.com","nordvpn.com","telegram.org","discord.com","microsoft.com","xbox.com",
    "apple.com","valve.com","steampowered.com","canva.com","disneyplus.com","hulu.com","max.com",
    "primevideo.com","amazon.com","expressvpn.com","surfshark.com","playstation.com","deepseek.com",
    "x.ai","midjourney.com","github.com","razer.com","roblox.com","help.openai.com","notion.so",
    "slack.com","zoom.us","atlassian.com","trello.com","miro.com","figma.com","monday.com",
    "clickup.com","asana.com","coursera.org","skillshare.com","duolingo.com","patreon.com",
    "medium.com","linkedin.com","vimeo.com","soundcloud.com","audible.com","paramountplus.com",
    "peacocktv.com","crunchyroll.com","deezer.com","iqiyi.com","youku.com","twitch.tv",
    "paramount.com","nbc.com","jetbrains.com","unity.com","adobe.com","envato.com",
    "shutterstock.com","kittl.com","framer.com","grammarly.com","quillbot.com","recraft.ai",
    "ideogram.ai","leonardo.ai","krea.ai","character.ai","gamma.app","mistral.ai","jasper.ai",
    "sider.com","poe.com","suno.com","elevenlabs.io","runwayml.com","perplexity.ai",
    "cursor.com","anysphere.co","blackhawknetwork.com","incomm.com"]

def host_class(h):
    h = (h or "").lower()
    if any(c in h for c in CHANNEL_HOSTS): return "channel"
    if any(o in h for o in OFFICIAL_HOSTS): return "official"
    return "other"

def usd(amount, cur):
    return round(amount * FX.get(cur, 1.0), 2)

cat = json.load(open(OUT + "/catalog_v42.json", encoding="utf-8"))
fi = json.load(open(RD + "/findings_index_b3.json", encoding="utf-8"))
by_sku = fi["by_sku"]
offers = json.load(open(OUT + "/offers_intelligence.json", encoding="utf-8"))

FAM_RANGE = {
    "AI/SaaS": (1, 400), "Gift Cards": (1, 130), "Game Top-up": (0.5, 100),
    "Game Keys": (2, 90), "Software/Licenses": (0.5, 400), "eSIM": (2, 70),
    "SMM Services": (0.01, 60), "Virtual Numbers": (0.05, 12),
    "Digital Subscriptions": (0.5, 400), "API Services": (1, 600),
}

def denom_of(s):
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
    seen, ded = set(), []
    for c in cands:
        k = (c["seller_host"], c["price"])
        if k in seen: continue
        seen.add(k); ded.append(c)
    ded.sort(key=lambda x: ({"channel": 0, "official": 1, "other": 2}[x["host_class"]], x["usd"]))
    return ded

draft = {}
for s in cat["skus"]:
    if s.get("priority") != "P3": continue
    sid = s["sku_id"]
    existing = offers["skus"].get(sid, {})
    has_direct = any(o.get("source_run") == "MEC2-20260927-B3-DIRECT" for o in existing.get("offers", []))
    rec = {
        "identity": " | ".join([x for x in [s.get("product"), s.get("plan_edition"),
             s.get("duration_denomination"), s.get("region"), s.get("activation_type")] if x]),
        "family": s["family"],
        "catalog_state": s.get("ledger_state"),
        "batch3_evidence_level": "Advertised (snippet) — direct page reads deferred (quota §19)",
        "has_direct_observed_offers": has_direct,
    }
    offers_list = extract_offers(s)
    ch = [o for o in offers_list if o["host_class"] == "channel"]
    off = [o for o in offers_list if o["host_class"] == "official"]
    rec["offers_raw"] = offers_list[:8]
    rec["cheapest_channel_advertised"] = ch[0] if ch else None
    rec["official_baseline_snippet"] = off[0] if off else None
    rec["n_candidates"] = len(offers_list)
    draft[sid] = rec

json.dump({"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "run_id": "MEC2-20260927-B3",
           "fx_note": FX_NOTE, "draft": draft},
          open(RD + "/batch3_intelligence_draft.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

n_off = len([1 for v in draft.values() if v["n_candidates"] > 0])
n_ch = len([1 for v in draft.values() if v.get("cheapest_channel_advertised")])
n_offbase = len([1 for v in draft.values() if v.get("official_baseline_snippet")])
n_direct = len([1 for v in draft.values() if v["has_direct_observed_offers"]])
print("DRAFT: %d P3 SKUs | with >=1 candidate: %d | channel-host candidate: %d | official snippet: %d | pre-seeded direct offers: %d"
      % (len(draft), n_off, n_ch, n_offbase, n_direct))
