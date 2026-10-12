"""MEC Phase-5 — deterministic cross-provider product matching engine.

Master-prompt §8 (identity & matching) implemented as PURE RULES — no AI/ML on
provider data (compliance default), fully auditable, reproducible and testable.

Identity model (per §8): brand · product_core · tier · duration · credits_qty
  match_key = "brand|core|tier|duration" (+ "|qty" for credit products)

Hierarchical matching:
  L1 canonical alias table (brand+product+tier in one deterministic pattern)
  L2 duration normalization (12M / 18M / 1Y / 24H …)
  L3 category rules (e.g. netflix 4K→premium — Netflix plan structure)
  L4 leftovers stay UNMATCHED (honest default; never merge on name similarity)

Writes (additive, reversible):
  provider_products.match_key / match_status → MATCHED | UNMATCHED
  benchmark_products aggregates (offers, providers, min/avg/max, spread%,
  cheapest provider+offer) — effective price = unit_cost (post-discount) or
  unit_price fallback, per §7هـ (actual acquisition cost categories).

Everything degrades gracefully (DB down ⇒ engine returns error, never raises).
"""
import json, os, re, time, urllib.request

# ---------------- deterministic identity extraction ----------------
# Longest/most-specific patterns FIRST (first match wins).
ALIASES = [
    # --- AI subscriptions ---
    (r"gemini\s*(ai)?\s*pro", "google", "gemini", "pro"),
    (r"gemini\s*links?", "google", "gemini", "pro"),          # links = the Pro offer
    (r"gemini", "google", "gemini", None),
    (r"chatgpt\s*plus", "openai", "chatgpt", "plus"),
    (r"chatgpt", "openai", "chatgpt", None),
    (r"gpt-?4o?", "openai", "chatgpt", None),
    (r"codex", "openai", "codex_credits", None),
    (r"claude\s*pro", "anthropic", "claude", "pro"),
    (r"claude", "anthropic", "claude", None),
    (r"perplexity\s*max", "perplexity", "perplexity", "max"),
    (r"perplexity\s*pro", "perplexity", "perplexity", "pro"),
    (r"perplexity", "perplexity", "perplexity", None),
    (r"supergrok\s*heavy", "xai", "supergrok", "heavy"),
    (r"supergrok\s*plus", "xai", "supergrok", "plus"),
    (r"supergrok", "xai", "supergrok", None),
    (r"grok\s*heavy", "xai", "grok", "heavy"),
    (r"grok\s*plus", "xai", "grok", "plus"),
    (r"cursor\s*pro", "cursor", "cursor", "pro"),
    (r"cursor", "cursor", "cursor", None),
    (r"copilot", "microsoft", "copilot", None),
    # --- streaming / music ---
    (r"netflix\s*premium|netflix.*4k|4k.*netflix", "netflix", "netflix", "premium"),
    (r"netflix\s*standard", "netflix", "netflix", "standard"),
    (r"netflix\s*basic", "netflix", "netflix", "basic"),
    (r"netflix", "netflix", "netflix", None),
    (r"spotify\s*premium", "spotify", "spotify", "premium"),
    (r"spotify", "spotify", "spotify", "premium"),            # main retail product
    (r"youtube\s*premium|yt\s*premium", "google", "youtube", "premium"),
    (r"youtube\s*music", "google", "youtube_music", None),
    (r"youtube", "google", "youtube", "premium"),
    (r"apple\s+music", "apple", "music", None),
    (r"prime\s*video", "amazon", "prime_video", None),
    # --- productivity / SaaS ---
    (r"office\s*365\s*plus", "microsoft", "office365", "plus"),
    (r"office\s*365", "microsoft", "office365", None),
    (r"notion\s*business", "notion", "notion", "business"),
    (r"notion\s*plus", "notion", "notion", "plus"),
    (r"notion", "notion", "notion", None),
    (r"canva\s*pro", "canva", "canva", "pro"),
    (r"canva", "canva", "canva", None),
    (r"figma.*\bedu\b", "figma", "figma", "pro_edu"),
    (r"figma\s*pro", "figma", "figma", "pro"),
    (r"figma", "figma", "figma", None),
    (r"adobe\s*express", "adobe", "express", None),
    (r"adobe", "adobe", "adobe_other", None),
    (r"capcut\s*pro", "capcut", "capcut", "pro"),
    (r"capcut", "capcut", "capcut", None),
    (r"duolingo\s*super", "duolingo", "super", "super"),
    (r"duolingo", "duolingo", "super", "super"),
    (r"elevenlabs\s*creator", "elevenlabs", "elevenlabs", "creator"),
    (r"elevenlabs", "elevenlabs", "elevenlabs", None),
    (r"framer\s*pro", "framer", "framer", "pro"),
    (r"gamma\s*pro", "gamma", "gamma", "pro"),
    (r"lovable\s*pro\s*lite", "lovable", "lovable", "pro_lite"),
    (r"lovable\s*pro", "lovable", "lovable", "pro"),
    (r"manus\s*pro", "manus", "manus", "pro"),
    (r"replit\s*core", "replit", "replit", "core"),
    (r"warp\s*build", "warp", "warp", "build"),
    (r"warp", "warp", "warp", None),
    (r"wondercraft", "wondercraft", "wondercraft", None),
    (r"wispr\s*flow\s*pro", "wispr", "wispr_flow", "pro"),
    (r"granola\s*business", "granola", "granola", "business"),
    (r"gumloop\s*pro", "gumloop", "gumloop", "pro"),
    (r"miro", "miro", "miro", None),
    (r"jetbrains\s*edu", "jetbrains", "jetbrains_pack", "edu"),
    (r"jetbrains", "jetbrains", "jetbrains_pack", None),
    (r"coursera", "coursera", "coursera", None),
    (r"edx", "edx", "edx", None),
    (r"ilovepdf", "ilovepdf", "ilovepdf", None),
    # --- VPN / security ---
    (r"nord\s*vpn", "nordvpn", "nordvpn", None),
    (r"adguard", "adguard", "adguard", None),
    (r"avira\s*prime", "avira", "avira", "prime"),
    # --- social / gaming ---
    # NOTE: generic bare "discord" intentionally NOT aliased — decorations,
    # clone accounts and badges are different products that merely mention the
    # brand; merging them on name similarity violates the honesty rule (§8).
    (r"discord\s*nitro", "discord", "nitro", None),
    (r"x\s*premium|twitter\s*premium", "x", "x_premium", "premium"),
    (r"telegram\s*premium", "telegram", "premium", None),
    (r"twitch", "twitch", "twitch", None),
    # --- email accounts (anchored: product must BE the account, not merely mention it) ---
    (r"^\s*gmails?\b", "google", "gmail_account", None),
    (r"^\s*emails?\s+(outlook|hotmail)|(outlook|hotmail)\s+(emails?|accounts?)", "microsoft", "outlook_account", None),
]
ALIAS_COMPILED = [(re.compile(p), b, c, t) for p, b, c, t in ALIASES]

# marketing noise stripped before matching (never changes identity)
NOISE = re.compile(
    r"\(can be monetized\)|full warranty|full waranty|no warranty|cheap|new|"
    r"100%|🔥|⚡|✅|best price|hot deal|ready|activate now|fast", re.I)

DUR_RE = re.compile(
    r"(\d+)\s*(days?|d|weeks?|w|months?|mon|m|years?|yrs?|y)\b", re.I)
DUR_MAP = {"d": "D", "day": "D", "days": "D",
           "w": "W", "week": "W", "weeks": "W",
           "m": "M", "mon": "M", "month": "M", "months": "M",
           "y": "Y", "yr": "Y", "yrs": "Y", "year": "Y", "years": "Y"}
HOURS_RE = re.compile(r"(\d+)\s*(?:hours?|hrs?|h)\b", re.I)
CREDITS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*([km])\s*credit", re.I)
TRIAL_RE = re.compile(r"\btrial\b", re.I)


def extract_duration(text):
    m = DUR_RE.search(text)
    if m:
        n, unit = m.group(1), m.group(2).lower()
        u = DUR_MAP.get(unit.rstrip("s") if unit.endswith("s") and len(unit) > 1 else unit,
                        DUR_MAP.get(unit))
        if u is None:  # plural like "months"
            u = {"days": "D", "weeks": "W", "months": "M", "years": "Y",
                 "mon": "M", "yrs": "Y"}.get(unit)
        return f"{n}{u}" if u else None
    m = HOURS_RE.search(text)
    if m:
        h = int(m.group(1))
        return f"{h}H"
    return None


def extract_credits(text):
    m = CREDITS_RE.search(text)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).upper()
    qty = int(val * 1000) if unit == "K" else int(val * 1_000_000)
    return f"{qty}CR"


def normalize(name):
    """Return identity dict or None when no canonical product is recognized."""
    if not name:
        return None
    text = NOISE.sub(" ", str(name).lower())
    text = re.sub(r"[^\w\s\-\+\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    for rx, brand, core, tier in ALIAS_COMPILED:
        if rx.search(text):
            dur = extract_duration(text)
            qty = extract_credits(text)
            t = tier or "std"
            if TRIAL_RE.search(text):
                t = (tier or "std") + "_trial"
            key = f"{brand}|{core}|{t}|{dur or 'none'}"
            if qty:
                key += f"|{qty}"
            return {"match_key": key, "brand": brand, "product_core": core,
                    "tier": t, "duration": dur or None, "quantity": qty}
    return None


# ---------------- aggregation + persistence ----------------
def _effective_price(row):
    """Actual acquisition cost proxy: post-discount cost when provider
    publishes it, else list price (§7هـ — categories kept separate, never mixed)."""
    uc, up = row.get("unit_cost"), row.get("unit_price")
    try:
        if uc is not None:
            return float(uc)
        if up is not None:
            return float(up)
    except (TypeError, ValueError):
        return None
    return None


def run_matching(sb_url=None, sb_key=None):
    """One pass: read provider_products, classify, write back + benchmarks.
    Returns stats dict. Never raises (degrades on DB failure)."""
    t0 = time.time()
    SB_URL = sb_url or os.environ.get("SUPABASE_URL", "")
    SB_KEY = sb_key or os.environ.get("SUPABASE_KEY", "")

    def _req(path, payload=None, method="GET", prefer=None):
        headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                   "Content-Type": "application/json"}
        if prefer:
            headers["Prefer"] = prefer
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/{path}",
            data=json.dumps(payload).encode() if payload is not None else None,
            headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else None

    try:
        rows = _req("provider_products?select=id,provider_code,external_id,"
                    "product_name,brand,region,currency,unit_price,discount_pct,"
                    "unit_cost,stock,status&limit=5000")
    except Exception as e:
        return {"ok": False, "error": f"read provider_products failed: {e}"}

    groups = {}
    updates = []          # rows to upsert back with match fields
    matched = unmatched = 0
    for r in rows:
        ident = normalize(r.get("product_name"))
        key = ident["match_key"] if ident else None
        updates.append({**r, "match_key": key,
                        "match_status": "MATCHED" if ident else "UNMATCHED"})
        if ident:
            matched += 1
            g = groups.setdefault(key, {"identity": ident, "offers": []})
            g["offers"].append({
                "provider_code": r["provider_code"],
                "product_name": r["product_name"],
                "effective_price": _effective_price(r),
                "unit_price": r.get("unit_price"),
                "stock": r.get("stock"),
            })
        else:
            unmatched += 1

    # write back match fields (single batched upsert; product_name required —
    # PG checks NOT NULL on tuple formation BEFORE conflict arbitration)
    w_err = None
    try:
        payload = [{k: r[k] for k in ("provider_code", "external_id",
                                      "product_name", "match_key", "match_status")}
                   for r in updates]
        _req("provider_products?on_conflict=provider_code,external_id",
             payload=payload, method="POST",
             prefer="return=minimal,resolution=merge-duplicates")
    except Exception as e:
        w_err = str(e)

    # benchmark aggregates
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    bench = []
    for key, g in groups.items():
        ident = g["identity"]
        priced = [o for o in g["offers"] if o["effective_price"] is not None]
        prices = sorted(o["effective_price"] for o in priced)
        providers = sorted({o["provider_code"] for o in g["offers"]})
        if prices:
            lo, hi = prices[0], prices[-1]
            cheapest = next(o for o in priced if o["effective_price"] == lo)
            dearest = next(o for o in priced if o["effective_price"] == hi)
            bench.append({
                "match_key": key, "brand": ident["brand"],
                "product_core": ident["product_core"], "tier": ident["tier"],
                "duration": ident["duration"], "quantity": ident["quantity"],
                "offers": len(g["offers"]), "providers": len(providers),
                "min_price": lo, "max_price": hi,
                "avg_price": round(sum(prices) / len(prices), 4),
                "spread_pct": round((hi - lo) / lo * 100, 2) if lo > 0 else None,
                "cheapest_provider": cheapest["provider_code"],
                "cheapest_offer": cheapest["product_name"][:120],
                "dearest_provider": dearest["provider_code"],
                "last_matched_at": now,
            })
        else:
            bench.append({
                "match_key": key, "brand": ident["brand"],
                "product_core": ident["product_core"], "tier": ident["tier"],
                "duration": ident["duration"], "quantity": ident["quantity"],
                "offers": len(g["offers"]), "providers": len(providers),
                "min_price": None, "max_price": None, "avg_price": None,
                "spread_pct": None, "cheapest_provider": None,
                "cheapest_offer": None, "dearest_provider": None,
                "last_matched_at": now,
            })

    b_err = None
    try:
        if bench:
            _req("benchmark_products?on_conflict=match_key", payload=bench,
                 method="POST", prefer="return=minimal,resolution=merge-duplicates")
        # delete stale benchmarks (keys no longer present)
        if bench:
            keys = ",".join(f'"{b["match_key"]}"' for b in bench)
            _req(f"benchmark_products?match_key=not.in.({keys})",
                 method="DELETE", prefer="return=minimal")
        else:
            _req("benchmark_products?match_key=not.is.null", method="DELETE",
                 prefer="return=minimal")
    except Exception as e:
        b_err = str(e)

    multi = [b for b in bench if b["providers"] >= 2 and b["min_price"] is not None]
    return {
        "ok": not (w_err or b_err),
        "rows": len(rows), "matched": matched, "unmatched": unmatched,
        "benchmarks": len(bench), "comparable": len(multi),
        "write_back_error": w_err, "benchmark_error": b_err,
        "ms": int((time.time() - t0) * 1000),
    }
