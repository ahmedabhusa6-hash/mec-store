#!/usr/bin/env python3
"""MEC matching-engine tests — REAL, isolated (no network, no DB writes).
Names below are verbatim from live provider catalogs (2026-10-13 dump).
Covers: alias recognition, duration/credits/trial extraction, noise removal,
cross-provider key unification, effective-price aggregation, idempotency of
the pure functions. Exit 0 only if ALL pass.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from providers.matching import (normalize, extract_duration, extract_credits,
                                _effective_price)

PASS, FAIL = [], []


def t(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"[PASS] {name}")
    except Exception as e:
        FAIL.append((name, str(e)[:200]))
        print(f"[FAIL] {name}: {e}")


# ---------- 1) duration extraction ----------
def d_dur():
    cases = {
        "Gemini Pro 18M": "18M", "Adobe Express 12 Months": "12M",
        "Notion Business 3 Months": "3M", "Office 365 Plus 1 year": "1Y",
        "Canva Pro 2 yrs FW": "2Y", "Spotify 3M Redeem Link": "3M",
        "ChatGPT Plus UPI (24H)": "24H", "Adguard VPN 7 Days full warranty": "7D",
        "Freepik Panel 30D": "30D", "Codex 1 Day": "1D",
    }
    for name, want in cases.items():
        got = extract_duration(name.lower())
        assert got == want, f"{name}: expected {want}, got {got}"


def d_dur_none():
    assert extract_duration("Gmails Accounts") is None


# ---------- 2) credits & trial ----------
def d_credits():
    assert extract_credits("20M Credit API Codex 1 Day") == "20000000CR"
    assert extract_credits("100M Credit API Codex 5 Days") == "100000000CR"
    assert extract_credits("Capcut Pro") is None


def d_trial():
    i = normalize("Adobe Express 4 Months Trial")
    assert i and i["tier"].endswith("_trial"), i
    assert i["duration"] == "4M", i


# ---------- 3) cross-provider unification (the core value) ----------
def d_gemini_7_providers():
    names = [
        "Gemini Pro 18M NEW",                              # acczone
        "Gemini Links 18m New Url",                        # aivaulthub
        "Gemini Pro 18M ( Reactivation URLs )",            # aiversex
        "Gemini Pro 18 Months",                            # digitalcore
        "Gemini Pro 18Months (link)",                      # prodseller
        "Gemini AI Pro 18 Months Activation Link",         # richai
        "Gemini Pro 18Months (link)",                      # stackvault
    ]
    keys = {normalize(n)["match_key"] for n in names}
    assert keys == {"google|gemini|pro|18M"}, keys


def d_netflix_tiers():
    a = normalize("Netflix 1M 4K HDR")["match_key"]
    b = normalize("Netflix 1M Premium 4K HDR")["match_key"]
    assert a == b == "netflix|netflix|premium|1M", (a, b)


def d_different_duration_not_merged():
    a = normalize("Adobe Express 12M")["match_key"]
    b = normalize("Adobe Express 4 Months Trial")["match_key"]
    assert a != b, (a, b)


def d_figma_edu():
    a = normalize("Figma Pro Edu 2yrs")["match_key"]
    b = normalize("Figma EDU (PRO) 1Y")["match_key"]
    assert a == "figma|figma|pro_edu|2Y" and b == "figma|figma|pro_edu|1Y", (a, b)


def d_noise_only():
    """Noise words must never change the identity."""
    a = normalize("Spotify Premium 3M Redeem Link")
    b = normalize("🎧 Spotify Premium 3M Redeem Link — full warranty, NEW")
    assert a["match_key"] == b["match_key"] == "spotify|spotify|premium|3M", (a, b)


# ---------- 4) honesty: unknown stays UNMATCHED ----------
def d_unmatched():
    for n in ("131K Decor Discord / Profile Effect Cheap (Login Type)",
              "Discord Clone Account 2017", "Apple ID 2FA Gmail"):
        assert normalize(n) is None, n


def d_codex_qty():
    a = normalize("20M Credit API Codex 1 Day - full warranty")
    b = normalize("50M Credit API Codex 2 Days - full warranty")
    assert a and a["quantity"] == "20000000CR", a
    assert b and b["quantity"] == "50000000CR", b
    assert a["match_key"] != b["match_key"], (a, b)


# ---------- 5) effective price (§7هـ categories) ----------
def d_effective_price():
    assert _effective_price({"unit_cost": 0.81, "unit_price": 0.90}) == 0.81
    assert _effective_price({"unit_cost": None, "unit_price": 0.90}) == 0.90
    assert _effective_price({"unit_cost": None, "unit_price": None}) is None
    assert _effective_price({"unit_cost": "0.81", "unit_price": None}) == 0.81


# ---------- 6) purity: same input → same output (determinism) ----------
def d_deterministic():
    n = "Gemini AI Pro 18 Months Activation Link"
    assert normalize(n) == normalize(n)


for fn in (d_dur, d_dur_none, d_credits, d_trial, d_gemini_7_providers,
           d_netflix_tiers, d_different_duration_not_merged, d_figma_edu,
           d_noise_only, d_unmatched, d_codex_qty, d_effective_price,
           d_deterministic):
    t(fn.__name__, fn)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
