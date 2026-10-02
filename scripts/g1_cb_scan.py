#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1 CLOSURE SCAN: cb_ supplier identification via template forensics.
Passive OSINT only — public GET endpoints, zero interaction.
Reference: PMRF v1.0 §18 G-1 (identity of cb_ supplier, 229/282 = 81.2% of StackVault catalog)
Tests:
  T1  cb_ names vs archived ps_ names (30/09)  -> re-encoding test (A8)
  T2  cb_ description templates vs ps_/mr_ archived templates
  T3  cb_ Mongo ObjectId timestamps vs ps_ hex timestamps (supplier DB creation windows)
  T4  cb_ names vs ProdSeller live catalog (29/09, 26 products)
  T5  family focus vs known entities
  T6  language/emoji/URL fingerprints in descriptions
  T7  price points vs known supplier prices (incl. archived costPrice of matching names)
Output: research/g1_cb_scan_20261002.json + console report
"""
import json, re, time, unicodedata, urllib.request, gzip
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
from difflib import SequenceMatcher

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))  # Asia/Aden
OUT = "/home/z/my-project/research/g1_cb_scan_20261002.json"
RAW = "/home/z/my-project/research/g1_cb_live_catalog_20261002.json"

def fetch(url, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)[:200]

# ---------- normalization helpers ----------
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B00-\U00002BFF"
    "\U0000FE0F\U0000200D\U00002700-\U000027bf\U0001f900-\U0001f9FF\U00002190-\U000021FF"
    "\U000025A0-\U000025FF\U0000200B\U0000FE0E\U00002764\U00002705\U0000274C\U00002757]+")
VN_CHARS = set("ăâêôơưđắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵĂÂÊÔƠƯĐ")
ID_TOKENS = {"garansi","gak","gaes","kalian","jangan","beli","akun","harga","stok","dana",
             "pulsa","gopay","ovo","rb","jt","wajib","min","kalau","udah","sama","yang",
             "buat","kak","bang","bosku","sis","gan","tok","bank","qris","shopee"}

def norm_title(t):
    t = EMOJI_RE.sub(" ", t or "")
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"\d+", "#", t)
    t = re.sub(r"[^a-z#\*\(\)\&\+\-\.,:/% ']", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def name_key(t):
    """aggressive key for matching: letters only, no digits"""
    t = EMOJI_RE.sub(" ", t or "")
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"[^a-z ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def desc_head(d, lines=3):
    d = d or ""
    parts = [l for l in d.split("\n") if l.strip()][:lines]
    out = []
    for l in parts:
        l = EMOJI_RE.sub(" ", l)
        l = re.sub(r"\d+", "#", l)
        l = re.sub(r"https?://\S+", "URL", l)
        out.append(re.sub(r"\s+", " ", l).strip().lower())
    return " | ".join(out)

def mongo_ts(hex24):
    """Mongo ObjectId: first 4 bytes = Unix seconds."""
    try:
        if not re.fullmatch(r"[0-9a-f]{24}", hex24 or ""):
            return None
        return datetime.fromtimestamp(int(hex24[:8], 16), tz=timezone.utc)
    except Exception:
        return None

def langs_markers(text):
    text = text or ""
    vn = sum(1 for c in text if c in VN_CHARS)
    words = set(re.findall(r"[a-z]+", text.lower()))
    idn = len(words & ID_TOKENS)
    return {"vn_diacritics": vn, "id_tokens": idn,
            "has_usdt": "usdt" in text.lower(), "has_rupee": "₹" in text,
            "has_dong_sym": "đ" in text.lower() or "₫" in text}

result = {"execution_timestamp": datetime.now(TZ).isoformat(),
          "reference": "PMRF v1.0 G-1", "tests": {}, "notes": []}

# ---------- A) live catalog ----------
print("[A] fetching live catalog ...")
st, body = fetch("https://decohomz.com/sv-api/products")
live_items = []
if st == 200 and body.lstrip()[:1] in "[{":
    j = json.loads(body)
    live_items = j if isinstance(j, list) else (j.get("products") or j.get("data") or [])
with open(RAW, "w") as f:
    f.write(body if st == 200 else "")
print(f"    http={st} n={len(live_items)}")
if st != 200:
    print("FATAL: catalog unreachable"); raise SystemExit(1)

def split(items):
    d = {"cb": [], "ps": [], "mr": [], "other": []}
    for it in items:
        pid = str(it.get("id") or it.get("_id") or "")
        k = pid.split("_")[0] if "_" in pid else "other"
        d[k if k in d else "other"].append(it)
    return d

live = split(live_items)
cb, ps_live, mr_live, other = live["cb"], live["ps"], live["mr"], live["other"]
print(f"    cb_={len(cb)} ps_={len(ps_live)} mr_={len(mr_live)} other={len(other)}")
result["counts"] = {"cb": len(cb), "ps": len(ps_live), "mr": len(mr_live), "other": len(other)}

# ---------- B) cb_ deep analysis ----------
print("\n[B] cb_ deep analysis ...")

# B1 — Mongo timestamps
ts = []
for it in cb:
    pid = str(it.get("id") or "")
    m = re.fullmatch(r"cb_([0-9a-f]{24})", pid)
    if m:
        t = mongo_ts(m.group(1))
        if t: ts.append((t, pid))
cb_hex_n = len(ts)
hours = Counter(t.strftime("%m-%d %H:00") for t, _ in ts)
if ts:
    tmin = min(t for t, _ in ts); tmax = max(t for t, _ in ts)
    span_h = (tmax - tmin).total_seconds() / 3600
    # clusters: gap > 6h starts new cluster
    srt = sorted(t for t, _ in ts)
    clusters, cur = [], [srt[0]]
    for t in srt[1:]:
        if (t - cur[-1]).total_seconds() > 6 * 3600: clusters.append(cur); cur = [t]
        else: cur.append(t)
    clusters.append(cur)
    cluster_sum = [{"from": c[0].astimezone(TZ).isoformat()[:16],
                    "to": c[-1].astimezone(TZ).isoformat()[:16], "n": len(c)} for c in clusters]
else:
    tmin = tmax = None; span_h = 0; cluster_sum = []; hours = {}
print(f"    mongo-hex cb_ IDs: {cb_hex_n}/{len(cb)} | window {tmin} -> {tmax} ({span_h:.1f}h) | clusters={len(cluster_sum)}")
for c in cluster_sum: print("      cluster:", c)
result["tests"]["T3_cb_mongo"] = {
    "n_hex_ids": cb_hex_n, "total_cb": len(cb),
    "window_utc": [tmin.isoformat() if tmin else None, tmax.isoformat() if tmax else None],
    "span_hours": round(span_h, 1), "clusters": cluster_sum,
    "hour_histogram": dict(sorted(hours.items()))}

# B2 — title templates
tpl = Counter(norm_title(it.get("name", "")) for it in cb)
result["cb_title_templates_top30"] = tpl.most_common(30)
print("    top cb_ title templates:")
for t, n in tpl.most_common(12): print(f"      [{n:3}] {t[:95]}")

# B3 — description fingerprints
dh = Counter(desc_head(it.get("description", "")) for it in cb if it.get("description"))
result["cb_desc_templates_top20"] = dh.most_common(20)
all_desc = "\n".join((it.get("description") or "") for it in cb)
mk = langs_markers(all_desc)
# URLs inside descriptions
doms = Counter()
for it in cb:
    for u in re.findall(r"https?://([A-Za-z0-9\.\-]+)", it.get("description") or ""):
        doms[u.lower()] += 1
result["cb_desc_markers"] = {**mk, "desc_present": sum(1 for it in cb if it.get("description", "").strip())}
result["cb_desc_url_domains"] = doms.most_common(15)
print("    desc markers:", mk, "| url domains:", doms.most_common(8))

# distinctive style markers per entity
def has_marker(items, pat):
    rx = re.compile(pat, re.I)
    return sum(1 for it in items if rx.search((it.get("description") or "") + " " + (it.get("name") or "")))
markers = {
    "hitmeow_style_price_line": has_marker(cb, r"Price:\s*\$"),
    "hitmeow_sold_accounts": has_marker(cb, r"Sold:\s*#?\+?\s*accounts?"),
    "hitmeow_stock_accounts": has_marker(cb, r"Stock:\s*#?\s*accounts?"),
    "evoera_items_available": has_marker(cb, r"#\s*items available"),
    "evoera_restocked": has_marker(cb, r"has been restocked"),
    "prodseller_check": has_marker(cb, r"✔"),
    "warranty_word": has_marker(cb, r"warranty|guarantee"),
    "reseller_word": has_marker(cb, r"reseller"),
    "activation_link": has_marker(cb, r"activation link|activate"),
    "k12_word": has_marker(cb, r"\bk12\b|edu\b"),
}
result["cb_style_markers"] = markers
print("    style markers:", markers)

# B4 — families & prices
def family(name):
    n = (name or "").lower()
    for k in ["chatgpt","gemini","claude","perplexity","duolingo","capcut","canva","office",
              "adobe","spotify","youtube","netflix","kling","wispr","mobbin","notion","x premium",
              "twitter","cursor","windsurf","gmail","apple","prime","discord","telegram","copilot"]:
        if k in n: return k
    return "other"
fam = Counter(family(it.get("name")) for it in cb)
fam_prices = defaultdict(list)
for it in cb:
    try: fam_prices[family(it.get("name"))].append(float(it.get("price") or 0))
    except Exception: pass
result["cb_families"] = fam.most_common(20)
result["cb_family_price_ranges"] = {k: {"min": min(v), "max": max(v), "n": len(v)}
                                    for k, v in sorted(fam_prices.items(), key=lambda x: -len(x[1]))}
print("    families:", fam.most_common(10))

# B5 — stock/category fingerprints
stocks = Counter()
for it in cb:
    try: stocks[int(it.get("stock") or 0)] += 1
    except Exception: pass
cats = Counter((it.get("category") or "?") + "/" + (it.get("categoryName") or "?") for it in cb)
result["cb_stock_top15"] = stocks.most_common(15)
result["cb_categories"] = cats.most_common(10)
result["cb_bulk"] = {"bulkEnabled_true": sum(1 for it in cb if str(it.get("bulkEnabled")).lower() == "true"),
                     "with_tiers": sum(1 for it in cb if it.get("bulkTiers") not in (None, "", "[]"))}
print("    stock top:", stocks.most_common(6), "| cats:", cats.most_common(4), "| bulk:", result["cb_bulk"])

# the 1 'other' product
result["other_products"] = [{k: str(v)[:120] for k, v in it.items()} for it in other]
for it in other: print("    OTHER:", str(it.get("id"))[:40], "|", str(it.get("name"))[:80])

# ---------- C) comparison vs archives ----------
print("\n[C] cross-matching ...")
arch = json.load(open("/home/z/my-project/research/stackvault_live/sv_products_current.json"))
arch_items = arch if isinstance(arch, list) else (arch.get("products") or arch.get("data") or [])
arch = split(arch_items)
ps_arch, mr_arch = arch["ps"], arch["mr"]

# T3b — ps_ hex timestamps (ProdSeller DB fingerprint)
ps_ts = []
for it in ps_arch + ps_live:
    m = re.fullmatch(r"ps_([0-9a-f]{24})", str(it.get("id") or ""))
    if m:
        t = mongo_ts(m.group(1))
        if t: ps_ts.append(t)
if ps_ts:
    pmin, pmax = min(ps_ts), max(ps_ts)
    ph = Counter(t.strftime("%m-%d") for t in ps_ts)
    result["tests"]["T3b_ps_mongo"] = {"n": len(ps_ts),
        "window_utc": [pmin.isoformat(), pmax.isoformat()],
        "span_days": round((pmax - pmin).total_seconds() / 86400, 1),
        "daily_histogram": dict(sorted(ph.items()))}
    print(f"    ps_ hex window: {pmin:%d/%m %H:%M} -> {pmax:%d/%m %H:%M} ({len(ps_ts)} ids)")

# T1 — name matching cb_ vs ps_ archived / mr_ archived
def name_match(cb_list, ref_list, label):
    ref_keys = {name_key(it.get("name")): it for it in ref_list}
    exact, fuzzy = [], []
    for it in cb_list:
        k = name_key(it.get("name"))
        if k in ref_keys:
            exact.append((it.get("name"), ref_keys[k].get("name"),
                          it.get("price"), ref_keys[k].get("price"), ref_keys[k].get("costPrice"),
                          str(it.get("id"))[:36], str(ref_keys[k].get("id"))[:36]))
        else:
            best, br = None, 0.0
            for rk, rit in ref_keys.items():
                r = SequenceMatcher(None, k, rk).ratio()
                if r > br: br, best = r, (rit.get("name"), rit.get("price"), rit.get("costPrice"))
            if best and br >= 0.82:
                fuzzy.append((it.get("name"), best[0], round(br, 3), it.get("price"), best[1], best[2]))
    out = {"exact_n": len(exact), "exact": exact[:40], "fuzzy_n": len(fuzzy), "fuzzy_top": sorted(fuzzy, key=lambda x: -x[2])[:25]}
    result["tests"][label] = out
    print(f"    {label}: exact={len(exact)} fuzzy(>=0.82)={len(fuzzy)}")
    for e in exact[:8]: print("      EXACT:", str(e[0])[:60], "| cbP:", e[2], "vs archP:", e[3], "archCost:", e[4])
    return out

t1 = name_match(cb, ps_arch, "T1_cb_vs_ps_archived")
t1b = name_match(cb, mr_arch, "T1b_cb_vs_mr_archived")

# T4 — vs ProdSeller live catalog 29/09
try:
    psf = json.load(open("/home/z/my-project/research/prodseller_live/products_fresh.json"))
    psf_items = psf.get("products") or []
    psf_names = [it.get("name") or it.get("title") or "" for it in psf_items]
    cb_keys = {name_key(n) for n in (it.get("name") for it in cb)}
    m4 = [n for n in psf_names if name_key(n) in cb_keys]
    # fuzzy
    fz = []
    for n in psf_names:
        nk = name_key(n)
        best = max((SequenceMatcher(None, nk, ck).ratio() for ck in cb_keys), default=0)
        if best >= 0.82: fz.append((n, round(best, 3)))
    result["tests"]["T4_cb_vs_prodseller_live"] = {"exact_n": len(m4), "exact": m4, "fuzzy": sorted(fz, key=lambda x: -x[1])[:15]}
    print(f"    T4 vs ProdSeller(29/09, {len(psf_names)} items): exact={len(m4)} fuzzy={len(fz)}")
    for n in m4[:6]: print("      MATCH-PS:", n[:80])
except Exception as e:
    print("    T4 skipped:", e)

# T2 — description template overlap
ps_dh = Counter(desc_head(it.get("description")) for it in ps_arch if it.get("description"))
mr_dh = Counter(desc_head(it.get("description")) for it in mr_arch if it.get("description"))
def tpl_overlap(a: Counter, b: Counter):
    inter = set(a) & set(b)
    return {"shared_templates": len(inter),
            "shared_top": [(t, a[t], b[t]) for t in sorted(inter, key=lambda x: -(a[x] + b[x]))[:10]],
            "a_total": sum(a.values()), "b_total": sum(b.values())}
result["tests"]["T2_cb_vs_ps_desc"] = tpl_overlap(dh, ps_dh)
result["tests"]["T2b_cb_vs_mr_desc"] = tpl_overlap(dh, mr_dh)
print(f"    T2 desc-template overlap: cb∩ps={result['tests']['T2_cb_vs_ps_desc']['shared_templates']} cb∩mr={result['tests']['T2b_cb_vs_mr_desc']['shared_templates']}")

# T7 — price ladder on matched exact products (cb_ price vs archived ps_ price & costPrice)
if t1["exact"]:
    rows = []
    for nm_cb, nm_arch, cb_p, arch_p, arch_c, cb_id, arch_id in t1["exact"]:
        try:
            cb_p = float(cb_p); arch_p = float(arch_p); arch_c = float(arch_c) if arch_c not in (None, "") else None
            rows.append({"name": nm_cb[:70], "cb_price": cb_p, "sv_price_archived": arch_p,
                         "sv_cost_archived": arch_c,
                         "cb_vs_sv_retail_pct": round((cb_p - arch_p) / arch_p * 100, 1) if arch_p else None,
                         "cb_vs_sv_cost_pct": round((cb_p - arch_c) / arch_c * 100, 1) if arch_c else None})
        except Exception: pass
    result["tests"]["T7_matched_price_ladder"] = rows
    print("    T7 matched price ladder (first 8):")
    for r in rows[:8]: print("      ", r)

# T6b — search all channel archives for 'cb' tokens
print("\n[D] archive token scan for 'cb' ...")
cb_mentions = []
for fn in ["sv_supply8_deep.json", "sv_supply9_deepen.json", "sv_supply7_map_expansion.json",
           "sv_supply6_upstream.json", "b3_channel_history.json", "sv_supply5_deepdive.json"]:
    try:
        j = json.load(open(f"/home/z/my-project/research/{fn}"))
        s = json.dumps(j, ensure_ascii=False)
        for m in re.finditer(r"[^\"']{0,60}\bcb[_\.\- ]?[a-z0-9]{0,12}[^\"']{0,60}", s, re.I):
            frag = m.group(0).strip()
            if re.search(r"\bcb[_\.\- ]", frag, re.I) and len(frag) > 8:
                cb_mentions.append({"file": fn, "frag": frag[:130]})
    except Exception:
        pass
uniq = {c["frag"]: c for c in cb_mentions}
result["tests"]["T6b_cb_token_mentions"] = list(uniq.values())[:30]
print(f"    cb token mentions in archives: {len(uniq)}")
for c in list(uniq.values())[:10]: print("      ", c["file"], "::", c["frag"][:100])

# ---------- verdict inputs ----------
result["notes"].append("Mongo hex in cb_ IDs = supplier-side or sync-side DB creation timestamps (same pattern as ps_ = ProdSeller IDs)")

with open(OUT, "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(f"\nSAVED {OUT}")
