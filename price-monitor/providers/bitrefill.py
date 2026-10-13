"""Bitrefill adapter — Personal API (Bearer key), READ-ONLY.

Sources of truth (docs archived under research/bitrefill_docs_20261013/, fetched
2026-10-13 as official .md mirrors of docs.bitrefill.com):
  https://api.bitrefill.com/v2   (Personal API — Authorization: Bearer <key>)
  GET /ping               -> {meta, message:"pong"} — LIVE shape 2026-10-13
                             (docs show data.message; both accepted)
  GET /accounts/balance   -> {meta, data:{balance, currency}}       (60 req/10min)
  GET /products?limit&start -> {meta:{limit,start,total,_next}, data:[...]}
                             (60 req/min + products quota 1000/hour)

Live-verified 2026-10-13 (owner-provided key, read-only probes only):
  /ping 200 · /accounts/balance 200 {balance:0, currency:"BTC"}
  /v2/products 200 — full pull: 145 pages, 7,242 products (meta.total 7,243),
  72,516 package rows. Server clamps page size to 50 regardless of requested
  limit (requested 500, effective 50) — pagination follows meta._next.

PRICE SEMANTICS (empirically determined from the 2026-10-13 full pull,
n=7,912 USD-priced package rows): packages[].price is denominated in
SATOSHIS — the USD price/value ratio clusters tightly at 1199–1203 sats/$
(p25–p75) and the account balance is BTC-denominated. Therefore:
  unit_price = price in sats (integer), currency = "BTC",
  raw.face_value / raw.face_currency preserve the card denomination.
No FX conversion happens inside the adapter — converting sats to USD is a
separate, explicit, timestamped concern (master prompt §7 honesty rule).

Product model: one provider_products row per package denomination
(external_id = official package id, e.g. "digicel-bonaire<&>5" — globally
unique, stable). Range-only products (no packages) get one row with
unit_price=None and raw.range (price is only known at invoice time).

Read-only policy: catalog + balance ONLY. POST /invoices and every order
endpoint are NEVER called by this platform (ordering requires explicit
owner approval per the policy layer).
"""
import os
import time

from .base import ProviderAdapter, ProviderError


class BitrefillAdapter(ProviderAdapter):
    code = "bitrefill"
    BASE = "https://api.bitrefill.com/v2"
    CRED_ENV = "BITREFILL_API_KEY"
    PAGE_LIMIT = 50     # server clamps to 50 (live-verified 2026-10-13)
    PAGE_PAUSE = 1.1    # seconds between pages — stays under 60 req/min
    MAX_PAGES = 400     # hard bound: 400×50 = 20,000 products (catalog ≈ 7,243)

    def credentials_present(self):
        return bool(self.creds.get(self.CRED_ENV))

    def _headers(self):
        return {"Authorization": f"Bearer {self.creds[self.CRED_ENV]}"}

    def authenticate(self):
        """Verify the key read-only via /ping. Live shape (2026-10-13):
        {meta:..., message:"pong"} — top level; docs show data.message.
        Both shapes accepted; anything else is an auth failure."""
        res = self.call("GET", self.BASE + "/ping", headers=self._headers(),
                        timeout=self.AUTH_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        pong = (body.get("message") == "pong"
                or (body.get("data") or {}).get("message") == "pong")
        if res.status != 200 or not pong:
            raise ProviderError(f"auth verify failed: HTTP {res.status} {str(body)[:120]}")
        self.token = self.creds[self.CRED_ENV]
        self.token_exp = 3600
        return True

    def fetch_catalog(self):
        """GET /products — start-based walk, drift-tolerant, truncation-guarded.

        LIVE EVIDENCE (2026-10-13): the /products listing is dynamically
        ordered and shifts CONTINUOUSLY — in one 4-minute walk, digicel-bonaire
        appeared at start=0 AND start=50 (an insert at the top slid every
        window down), so 1,737 of 7,242 records were drift duplicates with
        re-quoted sats prices. Countermeasures, in order:
          (a) walk explicit start windows to meta.total;
          (b) TRUNCATION GUARD: records fetched MUST reach meta.total else raise
              (a silent partial catalog is never reported as success);
          (c) DEDUP by product id (last record wins = freshest sats quote) —
              drift duplicates collapse;
          (d) convergence over cycles: each cycle sees a slightly different
              subset of the moving list; the DB union converges toward the
              full unique SKU set (stale-row retirement is a follow-up).
        """
        records, total = [], None
        start, pages = 0, 0
        _verbose = os.environ.get("MEC_SYNC_VERBOSE") == "1"
        _t0 = time.time()
        while pages < self.MAX_PAGES:
            res = self.call("GET",
                            f"{self.BASE}/products?limit={self.PAGE_LIMIT}&start={start}",
                            headers=self._headers(), timeout=self.CALL_TIMEOUT)
            body = res.body if isinstance(res.body, dict) else {}
            meta = body.get("meta") or {}
            total = meta.get("total") or total
            batch = body.get("data") or []
            if not batch and total is not None and len(records) < int(total):
                # empty window before reaching total = anomaly — retry once
                time.sleep(2.0)
                res = self.call("GET",
                                f"{self.BASE}/products?limit={self.PAGE_LIMIT}&start={start}",
                                headers=self._headers(), timeout=self.CALL_TIMEOUT)
                body = res.body if isinstance(res.body, dict) else {}
                batch = body.get("data") or []
            if not batch:
                break
            records.extend(batch)
            pages += 1
            if _verbose and pages % 10 == 0:
                print(f"[bitrefill] {pages} pages, {len(records)} records "
                      f"({time.time() - _t0:.0f}s)", flush=True)
            if total is not None and len(records) >= int(total):
                break
            if len(batch) < self.PAGE_LIMIT and total is None:
                break  # no total to validate against — legacy heuristic
            start += self.PAGE_LIMIT
            time.sleep(self.PAGE_PAUSE)  # honor the 60 req/min endpoint limit
        if total is not None and len(records) < int(total):
            raise ProviderError(
                f"catalog truncated: fetched {len(records)} of {total} records "
                "(pagination ended early) — refusing to report a partial catalog")
        # drift dedup: same product id listed twice -> keep LAST (freshest quote)
        seen = {}
        for p in records:
            seen[p.get("id")] = p
        products = list(seen.values())
        self.last_fetch_stats = {
            "records_fetched": len(records),
            "unique_products": len(products),
            "meta_total": total,
        }
        return self._normalize(products)

    def _normalize(self, products):
        rows = []
        for p in products:
            base = {
                "product_name": p.get("name") or "",
                "brand": p.get("base_name"),
                "region": p.get("country_code"),
                "currency": "BTC",  # unit_price denomination = satoshis
                "discount_pct": None,
                "unit_cost": None,
                "stock": "IN_STOCK" if p.get("in_stock") else "OUT_OF_STOCK",
                "status": "ACTIVE" if p.get("in_stock") else "INACTIVE",
            }
            common_raw = {
                "product_id": p.get("id"),
                "country_code": p.get("country_code"),
                "categories": (p.get("categories") or [])[:6],
                "recipient_type": p.get("recipient_type"),
                "face_currency": p.get("currency"),
                "price_unit": "sats",
            }
            pkgs = p.get("packages") or []
            if pkgs:
                for pkg in pkgs:
                    rows.append({
                        "external_id": str(pkg.get("id")),
                        **base,
                        "product_name": self._denominated_name(p, pkg),
                        "unit_price": self._f(pkg.get("price")),
                        "raw": {**common_raw,
                                "face_value": pkg.get("value"),
                                "amount": pkg.get("amount"),
                                "price_sats": pkg.get("price")},
                    })
            else:
                rows.append({
                    "external_id": f"{p.get('id')}<>range",
                    **base,
                    "unit_price": None,  # price known only at invoice time
                    "raw": {**common_raw, "range": p.get("range")},
                })
        return rows

    @staticmethod
    def _denominated_name(p, pkg):
        """'Amazon US — 25 USD' / 'Bitrefill eSIM Europe — 1GB, 7 Days EUR'."""
        name, val = p.get("name") or "", pkg.get("value")
        if val is None:
            return name
        s = str(val)
        try:
            s = f"{float(val):g}"
        except (TypeError, ValueError):
            pass
        return f"{name} — {s} {p.get('currency') or ''}".rstrip()

    @staticmethod
    def _f(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def fetch_balance(self):
        res = self.call("GET", self.BASE + "/accounts/balance", headers=self._headers(),
                        timeout=self.CALL_TIMEOUT)
        body = res.body if isinstance(res.body, dict) else {}
        b = body.get("data") if isinstance(body.get("data"), dict) else body
        if b.get("balance") is None:
            return None
        return {"balance": b.get("balance"), "currency": b.get("currency")}
