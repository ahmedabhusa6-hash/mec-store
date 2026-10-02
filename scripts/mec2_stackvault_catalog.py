#!/usr/bin/env python3
"""MEC-2.0: StackVault catalog deep extraction (product -> price mapping) + misc pages."""
import json, re, ssl, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
OUT = "/home/z/my-project/data/research/mec2_stackvault_catalog.json"

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            return r.getcode(), r.read().decode("utf-8", "replace")
    except Exception as e:
        return None, "EXC: %s" % e

def text_of(h):
    h = re.sub(r"<br\s*/?>", "\n", h); h = re.sub(r"</(p|div|li|h\d)>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    for a, b in [("&nbsp;"," "),("&amp;","&"),("&#036;","$"),("&#33;","!"),("&lt;","<"),("&gt;",">"),("&#39;","'"),("&quot;",'"')]:
        h = h.replace(a, b)
    return re.sub(r"[ \t]+", " ", h)

pages = {}
for path in ["", "/shop", "/products", "/catalog", "/all", "/category", "/sitemap.xml"]:
    code, html = fetch("https://stackvault.shop" + path)
    pages[path or "/"] = {"http": code, "len": len(html) if html else 0}
    print(path or "/", "->", code, len(html) if html else 0)
    if code == 200 and html:
        pages[path or "/"]["html_head"] = html[:200]
        if path:  # non-home pages: try to keep product blocks
            pages[path or "/"]["text"] = text_of(html)[:6000]
    time.sleep(1.2)

# main page: extract product-card blocks around prices
code, html = fetch("https://stackvault.shop")
cards = []
if code == 200:
    # product cards usually contain a title line + price with $ + "In Stock"
    blocks = re.split(r'(?=class="[^"]*(product|card|item)[^"]*")', html)
    # simpler robust approach: find all $-prices with 300 chars context, then clean
    for m in re.finditer(r"\$\s?\d+(?:\.\d{2})?", html):
        ctx = html[max(0, m.start()-700): m.end()+200]
        t = text_of(ctx)
        # keep last plausible product name lines before the price
        lines = [l.strip() for l in t.split("\n") if l.strip()]
        cards.append({"price": m.group(0), "context_tail": " | ".join(lines[-14:])[:400]})
    # dedupe by context
    seen, uniq = set(), []
    for c in cards:
        k = c["price"] + c["context_tail"][:80]
        if k not in seen:
            seen.add(k); uniq.append(c)
    pages["home_cards"] = uniq[:40]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=1)
print("cards extracted:", len(pages.get("home_cards", [])))
print("Saved:", OUT)
