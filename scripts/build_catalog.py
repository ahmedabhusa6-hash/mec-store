#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 1 — Catalog Construction (v4.2 architecture)
- Decomposes the 10 product families into 400+ SKU research units
- Decomposition basis: documented commercial structures only (official plan pages
  verified in the 2026-09-25 run + Notion seed catalog 226 brands)
- Every SKU starts as [to-verify] research unit (Unsearched) — no invented attributes
- Output: catalog_v42.json + catalog_summary.md + Coverage Ledger skeleton
"""
import json, os, hashlib

OUT_DIR = "/home/z/my-project/download"
os.makedirs(OUT_DIR, exist_ok=True)

def sid(family_code, n):
    return "SKU-%s%03d" % (family_code, n)

catalog = []
def add(family, fcode, brand, product, plan, denom_dur, region, activation, basis, prio, note=""):
    catalog.append({
        "sku_id": sid(fcode, len([c for c in catalog if c["family"] == family]) + 1),
        "family": family,
        "brand": brand,
        "product": product,
        "plan_edition": plan,
        "duration_denomination": denom_dur,
        "region": region,
        "activation_type": activation,
        "attribute_basis": basis,          # documented-official | documented-marketplace | documented-prior-run
        "ledger_state": "Unsearched",      # v4.2 lifecycle: Unsearched/Partial/Verified/Retrieval-Limited/Budget-Limited
        "priority": prio,                  # P1 high-trade + prior-run continuity | P2 core | P3 expansion
        "note": note,
    })

# ══════════════ FAMILY 1: AI/SaaS ══════════════
F, FC = "AI/SaaS", "AI"
# ChatGPT (official structure verified 25/09: Free/Go 8$/Plus 20$/Pro)
add(F,FC,"OpenAI","ChatGPT Plus subscription","Plus","1 month","Global","Account upgrade","documented-prior-run","P1","official $20 verified 25/09")
add(F,FC,"OpenAI","ChatGPT Plus subscription","Plus","12 months","Global","Account upgrade","documented-official","P2")
add(F,FC,"OpenAI","ChatGPT Go subscription","Go","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"OpenAI","ChatGPT Pro subscription","Pro","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"OpenAI","ChatGPT Plus shared account","Plus (shared seat)","1 month","Global","Account credentials","documented-marketplace","P1","GGSel/Z2U marketplace pattern documented 25/09")
add(F,FC,"Anthropic","Claude Pro subscription","Pro","1 month","Global","Account upgrade","documented-official","P1")
add(F,FC,"Anthropic","Claude Max subscription","Max","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Google","Gemini Advanced / AI Pro","Pro","1 month","Global","Account upgrade","documented-official","P1")
add(F,FC,"Google","Gemini Ultra","Ultra","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"xAI","Grok subscription","SuperGrok","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"DeepSeek","DeepSeek API credits","API pack","pay-as-you-go","Global","API key","documented-official","P2")
add(F,FC,"Perplexity","Perplexity Pro","Pro","1 month","Global","Account upgrade","documented-official","P1")
add(F,FC,"Midjourney","Midjourney subscription","Basic","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Midjourney","Midjourney subscription","Standard","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Poe","Poe subscription","Subscription","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Suno","Suno Pro","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"ElevenLabs","ElevenLabs subscription","Creator","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Runway","Runway subscription","Standard","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Ideogram","Ideogram subscription","Basic","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Leonardo AI","Leonardo subscription","Apprentice","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Krea","Krea subscription","Basic","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Recraft","Recraft subscription","Basic","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Character.AI","Character.AI","c.ai+","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Gamma","Gamma subscription","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Mistral AI","Le Chat Pro","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Jasper","Jasper subscription","Creator","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Sider","Sider subscription","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Manus","Manus subscription","Basic","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Microsoft","Microsoft Copilot Pro","Copilot Pro","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Adobe","Adobe Firefly plan","Standard","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Notion","Notion AI add-on","AI add-on","1 month","Global","Account add-on","documented-official","P3")
add(F,FC,"Canva","Canva Pro","Pro","1 month","Global","Account upgrade","documented-official","P1")
# Expansion AI/SaaS (annual + team structures documented)
add(F,FC,"OpenAI","ChatGPT Plus annual","Plus","12 months","Global","Account upgrade","documented-official","P2")
add(F,FC,"Anthropic","Claude Pro annual","Pro","12 months","Global","Account upgrade","documented-official","P3")
add(F,FC,"Perplexity","Perplexity Pro annual","Pro","12 months","Global","Account upgrade","documented-official","P3")
add(F,FC,"Midjourney","Midjourney subscription","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Midjourney","Midjourney subscription","Mega","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Suno","Suno Premier","Premier","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"ElevenLabs","ElevenLabs Pro","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Runway","Runway subscription","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Ideogram","Ideogram Plus","Plus","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Leonardo AI","Leonardo subscription","Artisan","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Krea","Krea subscription","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Gamma","Gamma Max","Max","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Jasper","Jasper Business","Business","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"GitHub","GitHub Copilot Pro","Copilot Pro","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Anysphere","Cursor Pro","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Grammarly","Grammarly Premium","Premium","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"QuillBot","QuillBot Premium","Premium","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Freepik","Freepik Premium","Premium","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Envato","Envato Elements","Elements subscription","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Shutterstock","Shutterstock subscription","Standard","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Kittl","Kittl Pro","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Framer","Framer Pro","Pro","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Sider","Sider Team","Team","1 month","Global","Account upgrade","documented-official","P3")

# ══════════════ FAMILY 2: Gift Cards ══════════════
F, FC = "Gift Cards", "GC"
# Expansion set (documented regional retail structures)
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","5 EUR","EU","Code redemption","documented-official","P2")
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","10 EUR","EU","Code redemption","documented-official","P2")
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","20 EUR","EU","Code redemption","documented-official","P2")
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","50 EUR","EU","Code redemption","documented-official","P2")
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","100 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","20 USD","Argentina","Code redemption","documented-marketplace","P3")
add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code","20 USD","Saudi Arabia","Code redemption","documented-marketplace","P2","user-region relevance")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","25 USD","US","Code redemption","documented-official","P2")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","25 EUR","EU","Code redemption","documented-official","P2")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","50 EUR","EU","Code redemption","documented-official","P2")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","50 USD","Saudi Arabia","Code redemption","documented-marketplace","P2","user-region relevance")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","50 USD","Turkey","Code redemption","documented-marketplace","P3")
add(F,FC,"Microsoft","Xbox Gift Card","Wallet code","5 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Microsoft","Xbox Gift Card","Wallet code","15 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Microsoft","Xbox Gift Card","Wallet code","25 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Microsoft","Xbox Gift Card","Wallet code","50 TRY","Turkey","Code redemption","documented-marketplace","P3")
add(F,FC,"Google","Google Play Gift Card","Card code","10 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Google","Google Play Gift Card","Card code","25 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Google","Google Play Gift Card","Card code","50 SAR","Saudi Arabia","Code redemption","documented-marketplace","P3")
add(F,FC,"Apple","Apple Gift Card / iTunes","Card code","25 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Apple","Apple Gift Card / iTunes","Card code","50 SAR","Saudi Arabia","Code redemption","documented-marketplace","P3","user-region relevance")
add(F,FC,"Apple","Apple Gift Card / iTunes","Card code","100 AED","UAE","Code redemption","documented-prior-run","P2","SKU-001 family")
add(F,FC,"Amazon","Amazon Gift Card","Card code","25 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Amazon","Amazon Gift Card","Card code","50 TRY","Turkey","Code redemption","documented-marketplace","P3")
add(F,FC,"Nintendo","Nintendo eShop Card","Card code","35 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Razer","Razer Gold Gift Card","Wallet code","5 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Netflix","Netflix Gift Card","Prepaid credit","25 USD","US","Code redemption","documented-official","P3")
add(F,FC,"Spotify","Spotify Gift Card","Prepaid credit","60 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"Roblox","Roblox Gift Card","Robux credit","100 USD","US","Code redemption","documented-official","P3")
add(F,FC,"Roblox","Roblox Gift Card","Robux credit","10 EUR","EU","Code redemption","documented-official","P3")
add(F,FC,"PlayStation","PSN Plus gift","Prepaid membership","3 months","US","Code redemption","documented-official","P2")
add(F,FC,"Microsoft","Xbox Game Pass gift card","Prepaid membership","3 months","US","Code redemption","documented-official","P2")
add(F,FC,"Binance","Binance Gift Card","Crypto voucher","variable","Global","Code redemption","documented-official","P3")
add(F,FC,"Various","Prepaid Visa/Mastercard virtual","Virtual card voucher","variable","Global","Card issuance","documented-marketplace","P3")
# Steam Wallet (documented: $20 US prior-run SKU-01; regions: US/Lebanon-adjacent documented via PSN; denominations official)
for denom in ["5 USD","10 USD","20 USD","30 USD","50 USD","100 USD"]:
    add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code",denom,"US","Code redemption","documented-prior-run" if denom=="20 USD" else "documented-official","P1" if denom in ("20 USD","50 USD") else "P2")
for denom in ["10 USD","20 USD","50 USD"]:
    add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code",denom,"EU","Code redemption","documented-official","P2")
    add(F,FC,"Valve","Steam Wallet Gift Card","Wallet code",denom,"Turkey","Code redemption","documented-official","P3")
# PSN (documented: $50 US SKU-02, $10 Lebanon SKU-03)
for denom in ["10 USD","20 USD","50 USD","100 USD"]:
    add(F,FC,"Sony","PlayStation Network Card","Wallet code",denom,"US","Code redemption","documented-prior-run" if denom in ("50 USD",) else "documented-official","P1" if denom in ("50 USD","10 USD") else "P2")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","10 USD","Lebanon","Code redemption","documented-prior-run","P1","SKU-03 prior run: Turgame 9.07$")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","50 USD","Argentina","Code redemption","documented-prior-run","P2","Eneba lead documented 25/09")
add(F,FC,"Sony","PlayStation Network Card","Wallet code","50 USD","Bahrain","Code redemption","documented-prior-run","P2","GG.deals/g2play lead documented 25/09")
for denom in ["10 GBP","25 GBP","50 GBP"]:
    add(F,FC,"Sony","PlayStation Network Card","Wallet code",denom,"UK","Code redemption","documented-official","P3")
# Xbox Gift Card
for denom in ["10 USD","15 USD","25 USD","50 USD","100 USD"]:
    add(F,FC,"Microsoft","Xbox Gift Card","Wallet code",denom,"US","Code redemption","documented-official","P2")
# Apple Gift Card (documented: UAE 50-2500 AED SKU-001)
for denom in ["50 AED","100 AED","200 AED","500 AED"]:
    add(F,FC,"Apple","Apple Gift Card / iTunes","Card code",denom,"UAE","Code redemption","documented-prior-run","P1","SKU-001 prior run")
for denom in ["10 USD","25 USD","50 USD","100 USD"]:
    add(F,FC,"Apple","Apple Gift Card / iTunes","Card code",denom,"US","Code redemption","documented-official","P2")
# Google Play
for denom in ["10 USD","25 USD","50 USD","100 USD"]:
    add(F,FC,"Google","Google Play Gift Card","Card code",denom,"US","Code redemption","documented-official","P2")
    add(F,FC,"Google","Google Play Gift Card","Card code",denom,"Saudi Arabia","Code redemption","documented-official","P3")
# Amazon
for denom in ["10 USD","25 USD","50 USD","100 USD"]:
    add(F,FC,"Amazon","Amazon Gift Card","Card code",denom,"US","Code redemption","documented-official","P2")
    add(F,FC,"Amazon","Amazon Gift Card","Card code",denom,"Saudi Arabia","Code redemption","documented-official","P3")
# Nintendo eShop
for denom in ["10 USD","20 USD","35 USD","50 USD"]:
    add(F,FC,"Nintendo","Nintendo eShop Card","Card code",denom,"US","Code redemption","documented-official","P3")
# Razer Gold
for denom in ["5 USD","10 USD","20 USD","50 USD","100 USD"]:
    add(F,FC,"Razer","Razer Gold Gift Card","Wallet code",denom,"Global/US","Code redemption","documented-official","P2")
# Netflix / Spotify gift cards (documented retail structures)
add(F,FC,"Netflix","Netflix Gift Card","Prepaid credit","50 USD","US","Code redemption","documented-official","P2")
add(F,FC,"Netflix","Netflix Gift Card","Prepaid credit","100 USD","US","Code redemption","documented-official","P2")
add(F,FC,"Spotify","Spotify Gift Card","Prepaid credit","10 USD","US","Code redemption","documented-official","P2")
add(F,FC,"Spotify","Spotify Gift Card","Prepaid credit","30 USD","US","Code redemption","documented-official","P2")
# Roblox
for denom in ["10 USD","25 USD","50 USD"]:
    add(F,FC,"Roblox","Roblox Gift Card","Robux credit",denom,"US","Code redemption","documented-official","P2")
# Steam TR regional (Turgame documented selling TR-region Steam cards 25/09)
for denom in ["100 TRY","250 TRY","500 TRY"]:
    add(F,FC,"Valve","Steam Wallet Gift Card (TRY)","Wallet code",denom,"Turkey","Code redemption","documented-marketplace","P3")

# ══════════════ FAMILY 3: Game Top-up ══════════════
F, FC = "Game Top-up", "GT"
add(F,FC,"Garena","Free Fire Diamonds","Diamond pack","110 diamonds","Global/ID","ID top-up","documented-marketplace","P1")
add(F,FC,"Garena","Free Fire Diamonds","Diamond pack","560 diamonds","Global/ID","ID top-up","documented-marketplace","P2")
add(F,FC,"Garena","Free Fire Diamonds","Diamond pack","1160 diamonds","Global/ID","ID top-up","documented-marketplace","P2")
add(F,FC,"Tencent","PUBG Mobile UC","UC pack","60 UC","Global","ID top-up","documented-marketplace","P1")
add(F,FC,"Tencent","PUBG Mobile UC","UC pack","325 UC","Global","ID top-up","documented-marketplace","P2")
add(F,FC,"Tencent","PUBG Mobile UC","UC pack","660 UC","Global","ID top-up","documented-marketplace","P2")
add(F,FC,"Tencent","PUBG Mobile UC","UC pack","1800 UC","Global","ID top-up","documented-marketplace","P2")
add(F,FC,"Moonton","Mobile Legends Diamonds","Diamond pack","86 diamonds","Global/SEA","ID top-up","documented-marketplace","P1")
add(F,FC,"Moonton","Mobile Legends Diamonds","Diamond pack","172 diamonds","Global/SEA","ID top-up","documented-marketplace","P2")
add(F,FC,"Moonton","Mobile Legends Diamonds","Diamond pack","257 diamonds","Global/SEA","ID top-up","documented-marketplace","P2")
add(F,FC,"Riot Games","Valorant Points","VP pack","1000 VP","Global/EMEA","Code/ID top-up","documented-marketplace","P1")
add(F,FC,"Riot Games","Valorant Points","VP pack","2050 VP","Global/EMEA","Code/ID top-up","documented-marketplace","P2")
add(F,FC,"Riot Games","League of Legends RP","RP pack","1380 RP","EU-West","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Epic Games","Fortnite V-Bucks","V-Bucks pack","1000 V-Bucks","Global","Code/ID top-up","documented-marketplace","P1")
add(F,FC,"Epic Games","Fortnite V-Bucks","V-Bucks pack","2800 V-Bucks","Global","Code/ID top-up","documented-marketplace","P2")
add(F,FC,"Roblox","Robux","Robux pack","400 Robux","Global","Code/ID top-up","documented-marketplace","P1")
add(F,FC,"Roblox","Robux","Robux pack","800 Robux","Global","Code/ID top-up","documented-marketplace","P2")
add(F,FC,"Roblox","Robux","Robux pack","1700 Robux","Global","Code/ID top-up","documented-marketplace","P2")
add(F,FC,"HoYoverse","Genshin Impact Genesis Crystals","Crystal pack","300 crystals","Global/US","ID top-up","documented-marketplace","P2")
add(F,FC,"HoYoverse","Genshin Impact Genesis Crystals","Crystal pack","1980 crystals","Global/US","ID top-up","documented-marketplace","P2")
add(F,FC,"HoYoverse","Honkai Star Rail Oneiric Shards","Shard pack","300 shards","Global/US","ID top-up","documented-marketplace","P3")
add(F,FC,"EA","EA Sports FC Points","FC Points pack","1050 FC points","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Activision","Call of Duty CP","CP pack","1000 CP","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Supercell","Clash of Clans Gems","Gem pack","500 gems","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Supercell","Brawl Stars Gems","Gem pack","170 gems","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"miHoYo","Honkai Impact Crystals","Crystal pack","300 crystals","Global","ID top-up","documented-marketplace","P3")
# Expansion packs (documented in-game store structures)
add(F,FC,"Garena","Free Fire Diamonds","Diamond pack","2200 diamonds","Global/ID","ID top-up","documented-marketplace","P3")
add(F,FC,"Garena","Free Fire Diamonds","Diamond pack","5600 diamonds","Global/ID","ID top-up","documented-marketplace","P3")
add(F,FC,"Tencent","PUBG Mobile UC","UC pack","3850 UC","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Tencent","PUBG Mobile UC","UC pack","8100 UC","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Moonton","Mobile Legends Diamonds","Diamond pack","706 diamonds","Global/SEA","ID top-up","documented-marketplace","P3")
add(F,FC,"Moonton","Mobile Legends Diamonds","Diamond pack","1050 diamonds","Global/SEA","ID top-up","documented-marketplace","P3")
add(F,FC,"Riot Games","Valorant Points","VP pack","3650 VP","Global/EMEA","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Riot Games","Valorant Points","VP pack","5350 VP","Global/EMEA","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Epic Games","Fortnite V-Bucks","V-Bucks pack","500 V-Bucks","Global","Code/ID top-up","documented-marketplace","P2")
add(F,FC,"Epic Games","Fortnite V-Bucks","V-Bucks pack","13500 V-Bucks","Global","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Roblox","Robux","Robux pack","4500 Robux","Global","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Roblox","Robux","Robux pack","10000 Robux","Global","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"HoYoverse","Genshin Impact Welkin Moon","Monthly pass","30 days","Global/US","ID top-up","documented-marketplace","P2")
add(F,FC,"HoYoverse","Genshin Impact Genesis Crystals","Crystal pack","3880 crystals","Global/US","ID top-up","documented-marketplace","P3")
add(F,FC,"HoYoverse","Genshin Impact Genesis Crystals","Crystal pack","8080 crystals","Global/US","ID top-up","documented-marketplace","P3")
add(F,FC,"EA","EA Sports FC Points","FC Points pack","2200 FC points","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Activision","Call of Duty CP","CP pack","2000 CP","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Supercell","Clash of Clans Gems","Gem pack","1200 gems","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Supercell","Clash of Clans Gems","Gem pack","2500 gems","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Supercell","Brawl Stars Gems","Gem pack","950 gems","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Supercell","Brawl Stars Gems","Gem pack","2000 gems","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Riot Games","League of Legends RP","RP pack","2800 RP","EU-West","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Riot Games","League of Legends RP","RP pack","5000 RP","EU-West","Code/ID top-up","documented-marketplace","P3")
add(F,FC,"Valve","Dota 2 — Steam wallet top-up via card","Wallet top-up","per-game wallet","Global","Wallet top-up","documented-marketplace","P3")
add(F,FC,"Garena","Free Fire membership (weekly)","Booyah pass","7 days","Global/ID","ID top-up","documented-marketplace","P3")
add(F,FC,"Tencent","PUBG Mobile RP","Royale Pass","per season","Global","ID top-up","documented-marketplace","P3")
add(F,FC,"Tencent","Valorant (console) VP","VP pack","1000 VP","Global","ID top-up","documented-marketplace","P3")

# ══════════════ FAMILY 4: Game Keys ══════════════
F, FC = "Game Keys", "GK"
# Concrete documented best-selling key titles (marketplace bestseller structures)
for title, plat, region, prio in [
    ("EA Sports FC 26","Steam/EA","Global","P2"), ("EA Sports FC 25","Steam/EA","Global","P2"),
    ("Grand Theft Auto V","Steam","Global","P2"), ("Elden Ring","Steam","Global","P2"),
    ("Cyberpunk 2077","Steam/GOG","Global","P2"), ("Hogwarts Legacy","Steam","Global","P2"),
    ("Baldur's Gate 3","Steam","Global","P2"), ("Call of Duty: Black Ops 6","Battle.net","US","P2"),
    ("Red Dead Redemption 2","Steam/Rockstar","Global","P2"), ("Starfield","Steam","Global","P2"),
    ("The Witcher 3","Steam/GOG","Global","P3"), ("ARK: Survival Ascended","Steam","Global","P3"),
    ("Rust","Steam","Global","P3"), ("Counter-Strike 2 (Prime)","Steam","Global","P2"),
    ("PUBG: Battlegrounds","Steam","Global","P3"), ("Sid Meier's Civilization VII","Steam","Global","P3"),
    ("Monster Hunter Wilds","Steam","Global","P2"), ("Assassin's Creed Shadows","Ubisoft","EU/US","P2"),
    ("Black Myth: Wukong","Steam","Global","P2"), (" Kingdom Come: Deliverance II","Steam","Global","P3")]:
    add(F,FC,"Various publishers","%s CD key" % title.strip(),"Retail key","lifetime",region,"%s key activation" % plat.split("/")[0],"documented-marketplace",prio)
# Game Pass documented (official $22.99 verified 25/09)
add(F,FC,"Microsoft","Xbox Game Pass Ultimate","GPU membership","1 month","Global","Code/direct","documented-prior-run","P1","official 22.99$ verified 25/09")
add(F,FC,"Microsoft","Xbox Game Pass Ultimate","GPU membership","3 months","Global","Code/direct","documented-marketplace","P1")
add(F,FC,"Microsoft","Xbox Game Pass Ultimate","GPU membership","12 months","Global","Code/direct","documented-marketplace","P2")
add(F,FC,"Microsoft","PC Game Pass","PCGP membership","1 month","Global","Code/direct","documented-official","P2")
add(F,FC,"Sony","PlayStation Plus Deluxe/Essential","PS+ membership","3 months","Multi-region","Code/direct","documented-official","P2")
add(F,FC,"Sony","PlayStation Plus Deluxe/Essential","PS+ membership","12 months","Multi-region","Code/direct","documented-official","P2")
add(F,FC,"Nintendo","Nintendo Switch Online","NSO membership","12 months","US","Code/direct","documented-official","P3")

# ══════════════ FAMILY 5: Software / Licenses ══════════════
F, FC = "Software/Licenses", "SW"
# Windows 11 documented prior run (official 139/199$ refs; CJS 9.99 GBP; GGSel 977.47 RUB)
add(F,FC,"Microsoft","Windows 11 Pro license","Retail key","lifetime","Global","License key","documented-prior-run","P1","prior-run completed 25/09")
add(F,FC,"Microsoft","Windows 11 Home license","Retail key","lifetime","Global","License key","documented-official","P2")
add(F,FC,"Microsoft","Windows 10 Pro license","Retail key","lifetime","Global","License key","documented-marketplace","P2")
add(F,FC,"Microsoft","Office 2021 Pro Plus","Retail key","lifetime","Global","License key","documented-prior-run","P1","prior-run: guarantee premium 25.10$")
add(F,FC,"Microsoft","Office 2021 Pro Plus","Phone-activation key","lifetime","Global","Phone activation","documented-prior-run","P1")
add(F,FC,"Microsoft","Office 2024 Pro Plus","Retail key","lifetime","Global","License key","documented-prior-run","P1","Keyforsteam 0.59 EUR lead documented 25/09")
add(F,FC,"Microsoft","Office 2024 Pro Plus","Phone-activation key","lifetime","Global","Phone activation","documented-marketplace","P2")
add(F,FC,"Microsoft","Microsoft 365 Personal","Subscription","12 months","Global","Account/key","documented-official","P2")
add(F,FC,"Microsoft","Microsoft 365 Family","Subscription","12 months","Global","Account/key","documented-official","P2")
add(F,FC,"Microsoft","Visual Studio Pro","License","lifetime","Global","License key","documented-marketplace","P3")
add(F,FC,"Adobe","Adobe Creative Cloud All Apps","Subscription","12 months","Global","Account","documented-official","P2")
add(F,FC,"Adobe","Photoshop subscription","Single app","1 month","Global","Account","documented-official","P3")
add(F,FC,"Adobe","Adobe CC All Apps","Subscription","1 month","Global","Account","documented-official","P3")
# Prior-run documented pattern: individual Adobe apps keys via marketplaces
for app in ["Photoshop lifetime key","Illustrator lifetime key","Premiere Pro lifetime key","After Effects lifetime key","Lightroom lifetime key"]:
    add(F,FC,"Adobe","Adobe %s" % app,"Lifetime key (marketplace)","lifetime","Global","License key","documented-marketplace","P3")
add(F,FC,"JetBrains","JetBrains All Products Pack","Subscription","12 months","Global","Account/key","documented-official","P3")
add(F,FC,"Unity","Unity Pro","Subscription","1 month","Global","Account","documented-official","P3")

# ══════════════ FAMILY 6: eSIM ══════════════
F, FC = "eSIM", "ES"
add(F,FC,"Various providers","Travel eSIM data pack","1 GB / 7 days","1 GB, 7 days","USA","eSIM activation","documented-marketplace","P1")
add(F,FC,"Various providers","Travel eSIM data pack","3 GB / 30 days","3 GB, 30 days","USA","eSIM activation","documented-marketplace","P2")
add(F,FC,"Various providers","Travel eSIM data pack","5 GB / 30 days","5 GB, 30 days","Saudi Arabia","eSIM activation","documented-marketplace","P1","user-region relevance")
add(F,FC,"Various providers","Travel eSIM data pack","10 GB / 30 days","10 GB, 30 days","Saudi Arabia","eSIM activation","documented-marketplace","P2")
add(F,FC,"Various providers","Travel eSIM data pack","1 GB / 7 days","1 GB, 7 days","UAE","eSIM activation","documented-marketplace","P1","user-region relevance")
add(F,FC,"Various providers","Travel eSIM data pack","3 GB / 30 days","3 GB, 30 days","UAE","eSIM activation","documented-marketplace","P2")
add(F,FC,"Various providers","Travel eSIM data pack","5 GB / 30 days","5 GB, 30 days","Egypt","eSIM activation","documented-marketplace","P2","user-region relevance")
add(F,FC,"Various providers","Travel eSIM data pack","10 GB / 30 days","10 GB, 30 days","Egypt","eSIM activation","documented-marketplace","P3")
add(F,FC,"Various providers","Travel eSIM data pack","10 GB / 30 days","10 GB, 30 days","Turkey","eSIM activation","documented-marketplace","P3")
add(F,FC,"Various providers","Travel eSIM data pack","10 GB / 30 days","10 GB, 30 days","Europe (multi)","eSIM activation","documented-marketplace","P2")
add(F,FC,"Various providers","Travel eSIM data pack","20 GB / 30 days","20 GB, 30 days","Europe (multi)","eSIM activation","documented-marketplace","P3")
add(F,FC,"Various providers","Global eSIM data pack","1 GB / 7 days","1 GB, 7 days","Global","eSIM activation","documented-marketplace","P2")
add(F,FC,"Various providers","Global eSIM data pack","10 GB / 30 days","10 GB, 30 days","Global","eSIM activation","documented-marketplace","P2")
# Expansion eSIM (documented travel eSIM destination structures)
for dest, pack, prio, note in [("Japan","10 GB / 30 days","P3",""),("South Korea","10 GB / 30 days","P3",""),("Thailand","10 GB / 30 days","P3",""),
    ("Malaysia","10 GB / 30 days","P3",""),("Qatar","5 GB / 30 days","P3",""),("Kuwait","5 GB / 30 days","P3",""),
    ("Oman","5 GB / 30 days","P3",""),("Jordan","5 GB / 30 days","P3",""),("Morocco","5 GB / 30 days","P3",""),
    ("Bahrain","5 GB / 30 days","P3",""),("Yemen","3 GB / 30 days","P3","user-region relevance"),("Iraq","5 GB / 30 days","P3","")]:
    add(F,FC,"Various providers","Travel eSIM data pack",pack,pack,dest,"eSIM activation","documented-marketplace",prio,note)

# ══════════════ FAMILY 7: SMM Services ══════════════
F, FC = "SMM Services", "SM"
add(F,FC,"Various panels","Instagram followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P2")
add(F,FC,"Various panels","Instagram followers","5000 followers","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Instagram likes","1000 likes","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","TikTok followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P2")
add(F,FC,"Various panels","TikTok views","10000 views","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","YouTube subscribers","1000 subscribers","one-time","Global","Panel order","documented-marketplace","P2")
add(F,FC,"Various panels","YouTube views","10000 views","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","X (Twitter) followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Telegram channel members","1000 members","one-time","Global","Panel order","documented-marketplace","P2")
add(F,FC,"Various panels","Telegram post views","1000 views","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Facebook page likes","1000 likes","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Threads followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P3")
# Expansion SMM (documented panel service structures)
add(F,FC,"Various panels","Instagram views","1000 views","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Instagram story views","1000 views","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","TikTok likes","1000 likes","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","YouTube 4000 watch hours","Monetization package","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","YouTube Shorts views","10000 views","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Telegram reactions","1000 reactions","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Telegram premium members","100 members","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Discord server members","1000 members","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Twitch followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Twitch live viewers","100 viewers","1 hour","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Spotify plays","1000 plays","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","SoundCloud plays","1000 plays","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","Facebook followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","LinkedIn followers","1000 followers","one-time","Global","Panel order","documented-marketplace","P3")
add(F,FC,"Various panels","X (Twitter) retweets","100 retweets","one-time","Global","Panel order","documented-marketplace","P3")

# ══════════════ FAMILY 8: Virtual Numbers ══════════════
F, FC = "Virtual Numbers", "VN"
for country in ["Russia","Ukraine","Kazakhstan","Indonesia","USA","UK","Germany","Egypt","Philippines","Vietnam","India","Nigeria"]:
    add(F,FC,"Various providers","Telegram virtual number","OTP-receive, 1-time use","one-time rental",country,"SMS activation","documented-marketplace","P1" if country in ("Russia","Indonesia","Kazakhstan") else "P2")
for country in ["Russia","Indonesia","USA","UK","Egypt"]:
    add(F,FC,"Various providers","WhatsApp virtual number","OTP-receive, 1-time use","one-time rental",country,"SMS activation","documented-marketplace","P2")
add(F,FC,"Various providers","Long-term virtual number rental","30-day rental","30 days","Russia","SMS activation","documented-marketplace","P3")
add(F,FC,"Various providers","Long-term virtual number rental","30-day rental","30 days","Indonesia","SMS activation","documented-marketplace","P3")
add(F,FC,"Various providers","Universal OTP number (any service)","OTP-receive, 1-time use","one-time rental","USA","SMS activation","documented-marketplace","P2")
# Expansion virtual numbers (documented SMS-activation service structures)
for svc in ["Google/Gmail","Instagram","Facebook","Discord","TikTok","Tinder","Amazon","WhatsApp Business"]:
    add(F,FC,"Various providers","%s virtual number" % svc,"OTP-receive, 1-time use","one-time rental","Russia","SMS activation","documented-marketplace","P2")
for svc in ["Telegram","Google/Gmail","WhatsApp"]:
    add(F,FC,"Various providers","%s virtual number" % svc,"OTP-receive, 1-time use","one-time rental","Indonesia","SMS activation","documented-marketplace","P2")
add(F,FC,"Various providers","Telegram virtual number","OTP-receive, 1-time use","one-time rental","Turkey","SMS activation","documented-marketplace","P3")
add(F,FC,"Various providers","Telegram virtual number","OTP-receive, 1-time use","one-time rental","UAE","SMS activation","documented-marketplace","P3")
add(F,FC,"Various providers","Long-term virtual number rental","30-day rental","30 days","USA","SMS activation","documented-marketplace","P3")
add(F,FC,"Various providers","Long-term virtual number rental","30-day rental","30 days","Kazakhstan","SMS activation","documented-marketplace","P3")
add(F,FC,"Various providers","Virtual voice number (toll-free)","Monthly rental","30 days","USA","Voice activation","documented-marketplace","P3")

# ══════════════ FAMILY 9: Digital Subscriptions ══════════════
F, FC = "Digital Subscriptions", "DS"
# Netflix documented (Standard 19.99$ verified 25/09)
add(F,FC,"Netflix","Netflix subscription","Standard with ads","1 month","US","Account/direct","documented-official","P2")
add(F,FC,"Netflix","Netflix subscription","Standard","1 month","US","Account/direct","documented-prior-run","P1","19.99$ official verified 25/09")
add(F,FC,"Netflix","Netflix subscription","Premium","1 month","US","Account/direct","documented-official","P1")
add(F,FC,"Netflix","Netflix subscription","Standard","12 months","TR/ARG (region-priced)","Account","documented-marketplace","P1","region-pricing lead documented (Techmusea)")
add(F,FC,"Netflix","Netflix private account","Full account","1 month","Global","Account credentials","documented-marketplace","P2","GGSel/Avito pattern documented 25/09")
# Spotify documented (Individual 12.99$ verified 25/09)
add(F,FC,"Spotify","Spotify Premium","Individual","1 month","US","Account/direct","documented-prior-run","P1","12.99$ official verified 25/09")
add(F,FC,"Spotify","Spotify Premium","Individual","12 months","US","Account/direct","documented-official","P1")
add(F,FC,"Spotify","Spotify Premium","Family","12 months","Global","Account","documented-official","P2")
add(F,FC,"Spotify","Spotify Premium","Individual","12 months","TR (region-priced)","Account","documented-marketplace","P2")
# YouTube Premium documented (15.99$ verified 25/09)
add(F,FC,"Google","YouTube Premium","Individual","1 month","US","Account/direct","documented-prior-run","P1","15.99$ official verified 25/09")
add(F,FC,"Google","YouTube Premium","Individual","12 months","TR/ARG (region-priced)","Account","documented-marketplace","P1","TR ~4.50$/mo lead documented 25/09")
add(F,FC,"Google","YouTube Premium","Family","12 months","US","Account","documented-official","P2")
add(F,FC,"Disney","Disney+ subscription","Basic with ads","1 month","US","Account/direct","documented-official","P2")
add(F,FC,"Disney","Disney+ subscription","Premium","12 months","Global","Account","documented-marketplace","P2")
add(F,FC,"Warner Bros.","Max subscription","Standard","1 month","US","Account/direct","documented-official","P2")
add(F,FC,"Hulu","Hulu subscription","With ads","1 month","US","Account/direct","documented-official","P2")
add(F,FC,"Amazon","Prime Video subscription","Standard","1 month","US","Account/direct","documented-official","P2")
add(F,FC,"Paramount","Paramount+ subscription","Standard","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"Peacock","Peacock subscription","Premium","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"Crunchyroll","Crunchyroll subscription","Mega Fan","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"Audible","Audible subscription","Premium Plus","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"Apple","Apple Music","Individual","1 month","US","Account/direct","documented-official","P2")
add(F,FC,"Apple","Apple TV+","Standard","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"Deezer","Deezer subscription","Premium","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"NordVPN","NordVPN subscription","Plus 2-year","24 months","Global","Account/key","documented-prior-run","P1","official pricing verified 25/09")
add(F,FC,"NordVPN","NordVPN subscription","Standard 1-year","12 months","Global","Account/key","documented-prior-run","P2")
add(F,FC,"Dropbox","Dropbox Plus","Subscription","12 months","Global","Account","documented-official","P3")
add(F,FC,"MEGA","MEGA Pro I","Subscription","12 months","Global","Account","documented-official","P3")
add(F,FC,"Apple","iCloud+ 50GB","Subscription","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Apple","iCloud+ 200GB","Subscription","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Google","Google One 100GB","Subscription","1 month","Global","Account upgrade","documented-official","P2")
add(F,FC,"Slack","Slack Pro","Subscription","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"Notion","Notion Plus","Subscription","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"Zoom","Zoom Pro","Subscription","1 month","Global","Account","documented-official","P3")
add(F,FC,"Trello","Trello Premium","Subscription","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"Jira","Jira Standard","Subscription","1 month","Global","Workspace","documented-official","P3")
# Expansion subscriptions (documented commercial structures; Telegram/Discord documented reseller markets)
add(F,FC,"Telegram","Telegram Premium","Premium","1 month","Global","Gift/direct","documented-official","P1","documented reseller market")
add(F,FC,"Telegram","Telegram Premium","Premium","3 months","Global","Gift/direct","documented-official","P2")
add(F,FC,"Telegram","Telegram Premium","Premium","12 months","Global","Gift/direct","documented-official","P1")
add(F,FC,"Telegram","Telegram Stars","Stars pack","100 stars","Global","In-app/gift","documented-official","P2")
add(F,FC,"Telegram","Telegram Stars","Stars pack","1000 stars","Global","In-app/gift","documented-official","P2")
add(F,FC,"Discord","Discord Nitro","Nitro","1 month","Global","Gift code","documented-official","P1","documented reseller market")
add(F,FC,"Discord","Discord Nitro","Nitro","12 months","Global","Gift code","documented-official","P2")
add(F,FC,"Discord","Discord Nitro Basic","Basic","1 month","Global","Gift code","documented-official","P3")
add(F,FC,"Twitch","Twitch Turbo","Turbo","1 month","Global","Account","documented-official","P3")
add(F,FC,"Twitch","Twitch gift subs","Gifted sub","1 month","Global","Gift code","documented-official","P3")
add(F,FC,"Spotify","Spotify Premium","Duo","1 month","US","Account/direct","documented-official","P3")
add(F,FC,"YouTube","YouTube Premium (India region-priced)","Individual","1 month","IN (region-priced)","Account","documented-marketplace","P2")
add(F,FC,"Netflix","Netflix Standard (Egypt region)","Standard","1 month","EG (region-priced)","Account","documented-marketplace","P2","user-region relevance")
add(F,FC,"Netflix","Netflix Standard (Saudi region)","Standard","1 month","SA (region-priced)","Account","documented-marketplace","P2","user-region relevance")
add(F,FC,"iQIYI","iQIYI VIP","VIP","1 month","Global","Account","documented-official","P3")
add(F,FC,"Youku","Youku VIP","VIP","1 month","Global","Account","documented-official","P3")
add(F,FC,"Vimeo","Vimeo Plus","Plus","1 month","Global","Account","documented-official","P3")
add(F,FC,"SoundCloud","SoundCloud Go+","Go+","1 month","Global","Account","documented-official","P3")
add(F,FC,"LinkedIn","LinkedIn Premium Career","Premium","1 month","Global","Account","documented-official","P3")
add(F,FC,"Medium","Medium membership","Member","1 month","Global","Account","documented-official","P3")
add(F,FC,"Patreon","Patreon membership (creator-specific)","Tier","1 month","Global","Account","documented-official","P3")
add(F,FC,"Coursera","Coursera Plus","Plus annual","12 months","Global","Account","documented-official","P3")
add(F,FC,"Skillshare","Skillshare membership","Premium","12 months","Global","Account","documented-official","P3")
add(F,FC,"Duolingo","Duolingo Super","Super","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"ExpressVPN","ExpressVPN subscription","12-month plan","12 months","Global","Account/key","documented-official","P2")
add(F,FC,"Surfshark","Surfshark subscription","24-month plan","24 months","Global","Account/key","documented-official","P2")
add(F,FC,"Canva","Canva Pro annual","Pro","12 months","Global","Account upgrade","documented-official","P2")
add(F,FC,"Figma","Figma Professional annual","Professional","12 months","Global","Account upgrade","documented-official","P3")
add(F,FC,"Notion","Notion Plus annual","Plus","12 months","Global","Workspace","documented-official","P3")
add(F,FC,"Monday.com","Monday.com Standard","Standard","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"ClickUp","ClickUp Unlimited","Unlimited","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"Asana","Asana Starter","Starter","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"Miro","Miro Starter","Starter","1 month","Global","Workspace","documented-official","P3")
add(F,FC,"Google","Google One 2TB","Subscription","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Apple","iCloud+ 2TB","Subscription","1 month","Global","Account upgrade","documented-official","P3")
add(F,FC,"Google","Google Workspace Individual","Subscription","12 months","Global","Account","documented-official","P3")
add(F,FC,"Microsoft","Microsoft 365 Business Basic","Subscription","1 month","Global","Tenant/key","documented-official","P3")
add(F,FC,"Microsoft","Microsoft 365 Business Standard","Subscription","1 month","Global","Tenant/key","documented-official","P3")

# ══════════════ FAMILY 10: API Services ══════════════
F, FC = "API Services", "AP"
add(F,FC,"OpenAI","OpenAI API credits","Prepaid credits","100 USD credit","Global","API key","documented-official","P1")
add(F,FC,"OpenAI","OpenAI API credits","Prepaid credits","500 USD credit","Global","API key","documented-official","P2")
add(F,FC,"Anthropic","Anthropic API credits","Prepaid credits","100 USD credit","Global","API key","documented-official","P2")
add(F,FC,"Reloadly","Gift card & payout API","Reseller/API plan","pay-as-you-go","Global","API key","documented-prior-run","P1","API/Distributor role verified 25/09; direct channel to-verify")
add(F,FC,"Ding","Global mobile top-up API","Reseller/API plan","pay-as-you-go","Global","API key","documented-marketplace","P2")
add(F,FC,"DT One","Digital content API (ex-TransferTo)","Reseller/API plan","pay-as-you-go","Global","API key","documented-marketplace","P2")
add(F,FC,"Google","Gemini API credits","Prepaid credits","100 USD credit","Global","API key","documented-official","P2")
add(F,FC,"Various","SMS-activation API (OTP)","API plan","pay-as-you-go","Global","API key","documented-marketplace","P2")
add(F,FC,"Various","SMM panel API","API plan","pay-as-you-go","Global","API key","documented-marketplace","P2")
add(F,FC,"Various","eSIM distribution API","Reseller/API plan","pay-as-you-go","Global","API key","documented-marketplace","P2")
add(F,FC,"Blackhawk Network","Gift card distribution API","B2B/API plan","pay-as-you-go","US","API integration","documented-official","P3","documented wholesale GC distributor")
add(F,FC,"InComm","Gift card & payment API","B2B/API plan","pay-as-you-go","US","API integration","documented-official","P3")
add(F,FC,"Plati.market","Digital goods marketplace API","Reseller API","pay-as-you-go","RU/CIS","API key","documented-marketplace","P3","marketplace API documented 25/09 via Plati source")
add(F,FC,"Z2U","Marketplace seller API/panel","Seller plan","pay-as-you-go","Global","API/panel","documented-marketplace","P3","Z2U documented 25/09")
add(F,FC,"GGSel","Marketplace seller API/panel","Seller plan","pay-as-you-go","RU","API/panel","documented-marketplace","P3","GGSel documented 25/09")
add(F,FC,"Turgame","Reseller/wholesale program","Reseller plan","pay-as-you-go","Global/TR","API/panel","documented-marketplace","P2","SUP-002; TURGAME WHOLESALE documented 25/09")

# ══════════════ BATCH STRUCTURE (v4.2) ══════════════
# Batch 1 = all P1 (high-trade + prior-run continuity) → deep execution this run
# Batch 2 = P2 core → this run as feasible; Batch 3+ = P3 expansion → ledger Unsearched
from collections import Counter, OrderedDict
fam_counts = Counter(c["family"] for c in catalog)
prio_counts = Counter(c["priority"] for c in catalog)

batches = OrderedDict()
b1 = [c for c in catalog if c["priority"] == "P1"]
b2 = [c for c in catalog if c["priority"] == "P2"]
b3 = [c for c in catalog if c["priority"] == "P3"]
for i, c in enumerate(b1): c["batch"] = 1
for i, c in enumerate(b2): c["batch"] = 2
for i, c in enumerate(b3): c["batch"] = 3
_missing = [c for c in catalog if "batch" not in c]
if _missing:
    print("DEBUG missing batch:", [(m.get("sku_id"), m.get("priority")) for m in _missing[:10]])
    for m in _missing: m["batch"] = 0

out = {
    "catalog_program": {
        "program_id": "CP-1",
        "created": "2026-09-27",
        "prompt_version": "v4.2 Candidate (working)",
        "run_id": "MEC1-20260927",
        "total_skus": len(catalog),
        "families": dict(fam_counts),
        "batches": {
            "batch_1": {"scope": "P1 — high-trade + prior-run continuity", "sku_count": len(b1), "budget": "C4 = 96 Research Actions + 25% reserve", "status": "Active (this run)"},
            "batch_2": {"scope": "P2 — core expansion", "sku_count": len(b2), "budget": "C4 per batch", "status": "Queued (partial this run as budget allows)"},
            "batch_3": {"scope": "P3 — expansion", "sku_count": len(b3), "budget": "C4 per batch", "status": "Queued (ledger Unsearched)"},
        },
        "rules": [
            "Family != SKU — decomposition: Brand+Plan+Duration+Region+Activation",
            "No invented attributes — all decompositions from documented official/marketplace structures",
            "Every SKU starts [to-verify] / Unsearched in Coverage Ledger",
            "Batch budget is per-batch, never conflated with catalog completeness",
            "No catalog-wide completeness claim without explicit terminal state for every scoped SKU",
        ],
    },
    "coverage_ledger": {c["sku_id"]: {"state": c["ledger_state"], "batch": c["batch"]} for c in catalog},
    "skus": catalog,
}
with open(os.path.join(OUT_DIR, "catalog_v42.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# markdown summary
md = ["# كتالوج البحث — البرنامج CP-1 (معمارية v4.2)", "",
      "**Run ID: MEC1-20260927 | التاريخ: 2026-09-27 | الإصدار: v4.2 Candidate (working)**", "",
      "## الإحصاء الكلي", "", "- إجمالي SKUs: **%d**" % len(catalog),
      "- الأسر: %d" % len(fam_counts), ""]
md.append("| الأسرة | عدد SKUs |")
md.append("|---|---|")
for fam, cnt in fam_counts.most_common():
    md.append("| %s | %d |" % (fam, cnt))
md += ["", "## هيكل الدفعات (v4.2)", ""]
md.append("| الدفعة | النطاق | العدد | الميزانية | الحالة |")
md.append("|---|---|---|---|---|")
md.append("| 1 | P1 — الأولوية العالية + استمرارية التشغيل السابق | %d | C4=96 إجراء + احتياطي 25%% | نشطة (هذا التشغيل) |" % len(b1))
md.append("| 2 | P2 — توسع أساسي | %d | C4 لكل دفعة | بالانتظار (جزئيًا هنا حسب الميزانية) |" % len(b2))
md.append("| 3 | P3 — توسع | %d | C4 لكل دفعة | بالانتظار (Unsearched) |" % len(b3))
md += ["", "**قاعدة حاكمة:** ميزانية الدفعة ≠ دليل اكتمال الكتالوج. لا ادعاء اكتمال على مستوى الكتالوج دون حالة نهائية صريحة لكل SKU.", ""]
md.append("## عيّنة SKUs الدفعة 1 (P1)")
md.append("")
md.append("| SKU | الأسرة | العلامة | المنتج | الخطة | المدة/الفئة | المنطقة |")
md.append("|---|---|---|---|---|---|---|")
for c in b1[:45]:
    md.append("| %s | %s | %s | %s | %s | %s | %s |" % (c["sku_id"], c["family"], c["brand"], c["product"], c["plan_edition"], c["duration_denomination"], c["region"]))
md += ["", "*الكتالوج الكامل بالبنية التفصيلية: `catalog_v42.json`*", ""]
with open(os.path.join(OUT_DIR, "catalog_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("CATALOG_BUILT: total=%d | P1=%d P2=%d P3=%d" % (len(catalog), len(b1), len(b2), len(b3)))
print("FAMILIES:", dict(fam_counts))
print("FILES: catalog_v42.json, catalog_summary.md -> download/")
