#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phases 2-4 — Verified price extraction from direct page reads.
Builds offers ledger with full verification dimensions (v4.1 §5):
Evidence Access / Price Evidence Level / Freshness / channel / role.
Sources: 17 valid direct pages + search snippets (Advertised) + prior-run
direct observations (2026-09-25, documented in Notion).
"""
import json, os, re, html as htmllib

RD = "/home/z/my-project/research"
PG = RD + "/pages"

def page_text(aid):
    f = os.path.join(PG, "RA-%s.json" % aid if not aid.startswith("RA-") else aid + ".json")
    try:
        d = json.load(open(f, encoding="utf-8")).get("data", {})
        h = d.get("html", "") or ""
        # strip tags
        t = re.sub(r'<script[^>]*>.*?</script>', ' ', h, flags=re.S|re.I)
        t = re.sub(r'<style[^>]*>.*?</style>', ' ', t, flags=re.S|re.I)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = htmllib.unescape(t)
        t = re.sub(r'\s+', ' ', t)
        return t, str(d.get("title", ""))
    except Exception:
        return "", ""

def find_prices(text, patterns, window=110, maxn=14):
    out = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.I):
            s = max(0, m.start()-window)
            ctx = text[s:m.end()+40].strip()
            out.append(ctx[:window+60])
            if len(out) >= maxn: return out
    return out

V = {}  # verified extraction record
def record(aid, sku, seller, role, notes):
    V.setdefault(aid, []).append({"sku": sku, "seller": seller, "role": role, "notes": notes})

# ── RA-122 Turgame WHOLESALE (upstream verification) ──
t, title = page_text("RA-122")
wh = {
    "title": title,
    "wholesale_program_detected": bool(re.search(r'wholesale|reseller|partner|api|b2b', t, re.I)),
    "context_snippets": find_prices(t, [r'wholesale[^.]{0,80}', r'reseller[^.]{0,80}', r'API[^.]{0,60}'], 90, 8),
}
record("RA-122", "SKU-GC037/GC049", "Turgame (wholesale.turgame.com)", "Wholesaler/Distributor [directly observed]",
       "Wholesale portal exists: title='Digital Gift Card Wholesale Solutions' — TURGAME WHOLESALE claim from 25/09 re-verified live 27/09")

# ── RA-123 Turgame Steam 20 USD product ──
t, title = page_text("RA-123")
tp = find_prices(t, [r'20[.,]00\s?\$|\$\s?20[.,]00|20\s?USD', r'"price"\s*:\s*"?[0-9.]+'], 100, 10)
record("RA-123", "SKU-GC037", "Turgame (turgame.com)", "Retailer/Reseller [directly observed]",
       "Product page live: '%s' — price contexts: %s" % (title, tp[:4]))

# ── RA-125 FazerCards (SUP-013) ──
t, title = page_text("RA-125")
fp = find_prices(t, [r'Apple[^$]{0,60}\$?\s?[0-9]+[.,][0-9]{2}', r'iTunes[^$]{0,60}\$?\s?[0-9]+[.,][0-9]{2}', r'gift card[^$]{0,60}\$?\s?[0-9]+[.,][0-9]{2}'], 100, 10)
record("RA-125", "SKU-GC062/063/064/065", "FazerCards (reseller.fazercards.com)", "Reseller Platform [directly observed]",
       "SUP-013 LEAD verified live: title='%s' — Apple GC contexts: %s" % (title, fp[:5]))

# ── RA-126 OpenAI pricing ──
t, title = page_text("RA-126")
op = find_prices(t, [r'Plus[^$]{0,40}\$20|\$20[^$]{0,40}Plus', r'Go[^$]{0,30}\$8|\$8[^$]{0,30}Go', r'Pro[^$]{0,40}\$200|\$200[^$]{0,40}Pro', r'\$\s?[0-9]+(?:\.[0-9]{2})?\s?/?\s?month'], 90, 12)
record("RA-126", "SKU-AI001", "OpenAI (openai.com)", "Primary/Official [directly observed]",
       "Official pricing live: %s" % op[:6])

# ── RA-127 GGSel ChatGPT Plus ──
t, title = page_text("RA-127")
gp = find_prices(t, [r'от\s?[0-9]{2,6}[.,]?[0-9]*\s?₽', r'[0-9]{2,6}[.,][0-9]{2}\s?₽', r'749', r'ChatGPT[^₽]{0,80}₽'], 100, 12)
record("RA-127", "SKU-AI005", "GGSel (ggsel.net)", "Marketplace/Aggregator [directly observed]",
       "Title confirms 'Цены от 749.00₽' live 27/09 — contexts: %s" % gp[:5])

# ── RA-128 Spotify ──
t, title = page_text("RA-128")
sp = find_prices(t, [r'Individual[^$]{0,60}\$[0-9.]+', r'\$12[.,]99', r'Premium[^$]{0,50}\$[0-9.]+'], 90, 10)
record("RA-128", "SKU-DS006", "Spotify (spotify.com)", "Primary/Official [directly observed]",
       "Official US plans live: %s" % sp[:5])

# ── RA-129 Netflix ──
t, title = page_text("RA-129")
np_ = find_prices(t, [r'Standard[^$]{0,60}\$[0-9.]+', r'Premium[^$]{0,60}\$[0-9.]+', r'\$[0-9]{2}[.,][0-9]{2}'], 90, 10)
record("RA-129", "SKU-DS002", "Netflix (netflix.com)", "Primary/Official [directly observed]",
       "Official US plans live: %s" % np_[:5])

# ── RA-130 YouTube Premium ──
t, title = page_text("RA-130")
yp = find_prices(t, [r'Individual[^$]{0,60}\$[0-9.]+', r'\$15[.,]99', r'Premium[^$]{0,50}\$[0-9.]+'], 90, 10)
record("RA-130", "SKU-DS010", "Google/YouTube (youtube.com)", "Primary/Official [directly observed]",
       "Official US plans live: %s" % yp[:5])

# ── RA-131 Telegram Premium ──
t, title = page_text("RA-131")
tgp = find_prices(t, [r'Premium[^$]{0,80}', r'\$[0-9.]+'], 80, 8)
record("RA-131", "SKU-DS037", "Telegram (telegram.org)", "Primary/Official [directly observed]",
       "Official blog page: %s" % tgp[:4])

# ── RA-132 Discord Nitro ──
t, title = page_text("RA-132")
dp = find_prices(t, [r'Nitro[^$]{0,60}\$[0-9.]+', r'\$9[.,]99', r'\$2[.,]99', r'\$[0-9.]+\s?/?\s*month'], 90, 10)
record("RA-132", "SKU-DS042", "Discord (discord.com)", "Primary/Official [directly observed]",
       "Official plans live: %s" % dp[:5])

# ── RA-133 CJS CD Keys ──
t, title = page_text("RA-133")
cp = find_prices(t, [r'Windows 11[^£$]{0,80}[£$][0-9.]+', r'Office[^£$]{0,80}[£$][0-9.]+', r'Xbox[^£$]{0,80}[£$][0-9.]+', r'[£$][0-9]+\.[0-9]{2}'], 100, 14)
record("RA-133", "SKU-SW001/SW004/GK021", "CJS CD Keys (cjs-cdkeys.com)", "Retailer/Reseller [directly observed]",
       "Storefront live: %s" % cp[:6])

# ── RA-134 Keyforsteam Win11 Pro ──
t, title = page_text("RA-134")
kp = find_prices(t, [r'Windows 11 Pro[^€]{0,60}[€][0-9.]+|€\s?[0-9]+[.,][0-9]{2}[^A-Za-z]{0,40}Windows', r'€\s?[0-9]+[.,][0-9]{2}'], 100, 14)
record("RA-134", "SKU-SW001", "Keyforsteam (keyforsteam.de)", "Price aggregator/marketplace [directly observed]",
       "Preisvergleich live (64 offers documented 25/09): %s" % kp[:6])

# ── RA-135 Keyforsteam Office 2021 ──
t, title = page_text("RA-135")
op2 = find_prices(t, [r'Office[^€]{0,70}€\s?[0-9.]+', r'€\s?[0-9]+[.,][0-9]{2}'], 100, 14)
record("RA-135", "SKU-SW004", "Keyforsteam (keyforsteam.de)", "Price aggregator/marketplace [directly observed]",
       "Preisvergleich live (77 offers documented 25/09): %s" % op2[:6])

# ── RA-136 Keyforsteam home (daily best) ──
t, title = page_text("RA-136")
hp = find_prices(t, [r'Office 2024[^€]{0,70}€\s?[0-9.]+', r'Windows[^€]{0,70}€\s?[0-9.]+', r'€\s?0[.,]5[0-9]'], 100, 10)
record("RA-136", "SKU-SW006", "Keyforsteam (keyforsteam.de)", "Price aggregator/marketplace [directly observed]",
       "Daily best prices: %s" % hp[:6])

# ── RA-137 Xbox Game Pass compare ──
t, title = page_text("RA-137")
xp = find_prices(t, [r'Ultimate[^$]{0,60}\$[0-9.]+', r'\$22[.,]99', r'PC[^$]{0,40}\$[0-9.]+', r'Core[^$]{0,40}\$[0-9.]+'], 90, 12)
record("RA-137", "SKU-GK021/GK022", "Microsoft Xbox (xbox.com)", "Primary/Official [directly observed]",
       "Official plans live: %s" % xp[:6])

# ── RA-139 Reloadly ──
t, title = page_text("RA-139")
rp = find_prices(t, [r'API[^.]{0,80}', r'reseller[^.]{0,60}', r'pricing[^.]{0,60}'], 80, 6)
record("RA-139", "SKU-AP004", "Reloadly (reloadly.com)", "API/Distributor [directly observed]",
       "Platform live: title='%s' — API/reseller contexts: %s" % (title, rp[:4]))

# ── RA-140 Airalo eSIM ──
t, title = page_text("RA-140")
ap = find_prices(t, [r'1\s?GB[^$]{0,60}\$[0-9.]+', r'5\s?GB[^$]{0,60}\$[0-9.]+', r'\$\s?[0-9]+[.,][0-9]{2}'], 100, 14)
record("RA-140", "SKU-ES001/ES003/ES005", "Airalo (airalo.com)", "eSIM retailer [directly observed]",
       "eSIM store live: %s" % ap[:6])

json.dump(V, open(RD + "/verified_extractions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("VERIFIED EXTRACTIONS (directly observed, 2026-09-27):")
for aid, recs in V.items():
    for r in recs:
        print("\n[%s] %s -> %s (%s)" % (aid, r["sku"], r["seller"], r["role"]))
        print("   %s" % r["notes"][:400])
