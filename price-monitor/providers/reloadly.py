"""Reloadly adapter — built strictly per the OFFICIAL OpenAPI 3.1.0 spec
archived at research/market_api/reloadly_giftcards_openapi.json (docs.reloadly.com,
fetched 2026-10-12). Read-only: catalog + discounts + balance. The /orders
endpoint is intentionally NOT implemented — ordering requires owner approval.

Verified API contract (from the spec):
  POST https://auth.reloadly.com/oauth/token
       {audience, client_id, client_secret, grant_type=client_credentials}
       -> {access_token, expires_in}
  GET  {base}/products?page&size&productName&countryCode&productCategoryId&global&includeRange&includeFixed
  GET  {base}/discounts?page&size  (per-product discountPercentage)
  GET  {base}/accounts/balance      (balance + currencyCode)
  base prod    = https://giftcards.reloadly.com
  base sandbox = https://giftcards-sandbox.reloadly.com
"""
from .base import ProviderAdapter, ProviderError

AUTH_URL = "https://auth.reloadly.com/oauth/token"


class ReloadlyAdapter(ProviderAdapter):
    code = "reloadly"

    def __init__(self, creds=None, use_sandbox=None):
        super().__init__(creds)
        # sandbox toggle: env RELOADLY_USE_SANDBOX=1 (for owner-approved test mode)
        if use_sandbox is None:
            use_sandbox = str(self.creds.get("RELOADLY_USE_SANDBOX", "")).lower() in ("1", "true", "yes")
        self.base = "https://giftcards-sandbox.reloadly.com" if use_sandbox \
            else "https://giftcards.reloadly.com"
        self.audience = "https://giftcards-sandbox.reloadly.com" if use_sandbox \
            else "https://giftcards.reloadly.com"

    # -- interface --
    def credentials_present(self):
        return bool(self.creds.get("RELOADLY_CLIENT_ID")) and bool(self.creds.get("RELOADLY_CLIENT_SECRET"))

    def authenticate(self):
        res = self.call("POST", AUTH_URL, payload={
            "audience": self.audience,
            "client_id": self.creds["RELOADLY_CLIENT_ID"],
            "client_secret": self.creds["RELOADLY_CLIENT_SECRET"],
            "grant_type": "client_credentials",
        }, timeout=self.AUTH_TIMEOUT)
        tok = (res.body or {}).get("access_token")
        if not tok:
            raise ProviderError("auth ok but no access_token in response")
        self.token = tok
        self.token_exp = (res.body or {}).get("expires_in", 3600)
        return True

    def _auth_headers(self):
        if not self.token:
            raise ProviderError("not authenticated")
        return {"Authorization": f"Bearer {self.token}"}

    def fetch_catalog(self, max_pages=50):
        """GET /products (paged) + GET /discounts -> normalized rows with computed cost."""
        products, page = [], 1
        while page <= max_pages:
            res = self.call("GET", f"{self.base}/products?page={page}&size=200",
                            headers=self._auth_headers())
            batch = res.body if isinstance(res.body, list) else []
            if not batch:
                break
            products.extend(batch)
            if len(batch) < 200:
                break
            page += 1

        discounts = {}
        dpage = 1
        while dpage <= max_pages:
            res = self.call("GET", f"{self.base}/discounts?page={dpage}&size=500",
                            headers=self._auth_headers())
            batch = res.body if isinstance(res.body, list) else []
            if not batch:
                break
            for d in batch:
                pid = d.get("productId")
                pct = d.get("discountPercentage")
                if pid is not None and pct is not None:
                    discounts[pid] = float(pct)
            if len(batch) < 500:
                break
            dpage += 1

        rows = []
        for p in products:
            pid = p.get("productId")
            unit = None
            disc = discounts.get(pid, p.get("discountPercentage"))
            # unit price: RANGE products -> minRecipientDenomination; FIXED -> senderFee-based face value not exposed;
            # the spec's /orders uses unitPrice; catalog carries denomination bounds instead.
            if p.get("denominationType") == "RANGE":
                unit = p.get("minRecipientDenomination")
            # discount is the reseller margin; cost is computed at order time in real flows.
            # For catalog economics we record face value + discount; unit_cost left null unless known.
            rows.append({
                "external_id": str(pid),
                "product_name": p.get("productName") or "",
                "brand": (p.get("brand") or {}).get("productName") if isinstance(p.get("brand"), dict)
                         else (p.get("brandName") or None),
                "region": ",".join(c.get("isoName", "") for c in (p.get("countries") or [])
                                   if isinstance(c, dict)) or p.get("recipientCountryCode"),
                "currency": p.get("recipientCurrencyCode") or p.get("senderCurrencyCode"),
                "unit_price": float(unit) if unit is not None else None,
                "discount_pct": float(disc) if disc is not None else None,
                "unit_cost": None,  # computed at order time in real flows (read-only platform)
                "stock": "IN_STOCK" if p.get("status") == "ACTIVE" else str(p.get("status")),
                "status": str(p.get("status")),
                "raw": {k: p.get(k) for k in ("productId", "productName", "denominationType",
                                              "senderFee", "senderFeePercentage", "global",
                                              "supportsPreOrder", "minRecipientDenomination",
                                              "maxrecipientDenomination")},
            })
        return rows

    def fetch_balance(self):
        res = self.call("GET", f"{self.base}/accounts/balance", headers=self._auth_headers())
        b = res.body or {}
        bal = b.get("balance")
        cur = b.get("currencyCode")
        if bal is None:
            return None
        return {"balance": bal, "currency": cur}
